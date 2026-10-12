import asyncio
import logging
import re
import statistics
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.schemas.api_schemas import (
    ValuationComparable,
    VehicleValuationRequest,
    VehicleValuationResponse,
)
from app.services.numeric_utils import parse_int

logger = logging.getLogger(__name__)

# AutoScout24.it fuel-type codes (facet values) mapped to canonical names.
FUEL_CODES: dict[str, str] = {
    "b": "gasoline",
    "d": "diesel",
    "e": "electric",
    "h": "hybrid",
    "l": "lpg",
    "c": "cng",
}

# Canonical fuel names -> accepted AutoScout24 code(s). Unknown requests are ignored
# (no fuel filter applied) rather than failing.
FUEL_TO_CODES: dict[str, set[str]] = {
    "gasoline": {"b"},
    "petrol": {"b"},
    "gas": {"b"},
    "diesel": {"d"},
    "electric": {"e"},
    "electricity": {"e"},
    "hybrid": {"h"},
    "lpg": {"l"},
    "cng": {"c"},
    "metano": {"c"},
}

MILEAGE_BAND = 0.35  # +/- 35% of the estimated odometer
MIN_SAMPLE = 3
MAX_COMPARABLES = 5
TRADE_IN_RATIO = 0.85  # dealer trade-in vs. private-sale asking price
ROUNDING_STEP = 50

# The AutoScout24 scraper renders the page on demand and can take 40-60s on a
# cold run, so a short timeout would fail spuriously. We allow a generous read
# timeout and retry a couple of times before giving up.
REQUEST_TIMEOUT = httpx.Timeout(90.0, connect=10.0)
MAX_ATTEMPTS = 3

_ARTICLE_RE = re.compile(r'<article class="cldt-summary-full-item[^"]*"[^>]*>')


class ValuationUnavailable(Exception):
    """Raised when the valuation provider is not configured or returns no usable data."""


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or ""


def _build_search_url(make: str, model: str, year: int | None) -> str:
    params: list[tuple[str, str]] = [
        ("atype", "C"),  # used cars
        ("cy", "I"),  # country: Italy
        ("ustate", "N,U"),  # new & used
    ]
    if year:
        params.append(("fregfrom", str(year - 1)))
        params.append(("fregto", str(year + 1)))
    params.append(("sort", "standard"))
    params.append(("desc", "0"))
    query = urlencode(params)
    model_slug = _slug(model)
    path = f"/lst/{_slug(make)}/{model_slug}" if model_slug else f"/lst/{_slug(make)}"
    return f"{settings.AUTOSCOUT24_BASE_URL.rstrip('/')}{path}?{query}"


async def _fetch_page(client: httpx.AsyncClient, api_key: str, url: str) -> str:
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "autoscout24-scraper.p.rapidapi.com",
    }
    response = await client.post(settings.RAPIDAPI_AS24_URL, headers=headers, params={"url": url})
    if response.status_code in (401, 403):
        raise ValuationUnavailable("Chiave RapidAPI non valida o non autorizzata.")
    if response.status_code == 429:
        raise ValuationUnavailable("Limite di richieste RapidAPI raggiunto, riprova più tardi.")
    response.raise_for_status()
    if not response.text or '<article' not in response.text:
        raise ValuationUnavailable("Nessun annuncio AutoScout24 trovato nella pagina.")
    return response.text


def _parse_listings(html: str) -> list[dict]:
    listings: list[dict] = []
    for match in _ARTICLE_RE.finditer(html):
        tag = match.group(0)
        data: dict[str, object] = {}
        for name in ("price", "mileage", "first-registration", "fuel-type", "make", "model"):
            attr = re.search(rf'data-{re.escape(name)}="([^"]*)"', tag)
            data[name] = attr.group(1) if attr else None
        price = parse_int(data.get("price"))
        mileage = parse_int(data.get("mileage"))
        if price is None:
            continue
        first_reg = str(data.get("first-registration") or "")
        year = None
        m = re.search(r"(\d{4})", first_reg)
        if m:
            year = int(m.group(1))
        listings.append(
            {
                "make": str(data.get("make") or ""),
                "model": str(data.get("model") or ""),
                "year": year,
                "mileage": mileage,
                "price": price,
                "fuel": str(data.get("fuel-type") or ""),
            }
        )
    return listings


def _price_eur(price: object) -> float | None:
    value = parse_int(price)
    return float(value) if value is not None else None


def _filter_outliers(values: list[float]) -> list[float]:
    if len(values) < 4:
        return values
    ordered = sorted(values)
    q1, _, q3 = statistics.quantiles(ordered, n=4)
    iqr = q3 - q1
    if iqr <= 0:
        return ordered
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    filtered = [value for value in ordered if low <= value <= high]
    return filtered or ordered


def _confidence(sample_size: int) -> str:
    if sample_size >= 8:
        return "high"
    if sample_size >= 4:
        return "medium"
    return "low"


def _round_value(value: float) -> float:
    return float(round(value / ROUNDING_STEP) * ROUNDING_STEP)


def _match_fuel(listing_fuel: str, requested_fuel: str | None) -> bool:
    if not requested_fuel:
        return True
    codes = FUEL_TO_CODES.get(requested_fuel.strip().lower())
    if not codes:
        return True
    if not listing_fuel:
        return False
    return listing_fuel in codes


async def estimate_vehicle_value(request: VehicleValuationRequest) -> VehicleValuationResponse:
    """Estimates a used-car value from comparable AutoScout24.it listings via RapidAPI.

    Fetches the AutoScout24 search page (scrapeunblocker scraper) and computes the robust
    median of asking prices for the same make/model/year, pre-filtered by mileage
    proximity when the odometer is known.
    """
    api_key = settings.RAPIDAPI_API_KEY.strip()
    if not api_key:
        raise ValuationUnavailable("Stima non disponibile: configurare RAPIDAPI_API_KEY.")

    url = _build_search_url(request.make, request.model, request.year)
    logger.debug("AutoScout24 search URL: %s", url)

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                html = await _fetch_page(client, api_key, url)
                break
            except ValuationUnavailable:
                raise
            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning(
                    "AutoScout24 scraper timeout (tentativo %d/%d)", attempt, MAX_ATTEMPTS
                )
                if attempt < MAX_ATTEMPTS:
                    await asyncio.sleep(1.5 * attempt)
            except httpx.HTTPStatusError as exc:
                logger.warning("AutoScout24 scraper failed: %s", exc)
                raise ValuationUnavailable("Scraper AutoScout24 non disponibile.") from exc
            except Exception as exc:
                logger.warning("AutoScout24 scraper request failed: %s", exc)
                raise ValuationUnavailable("Servizio di stima non disponibile.") from exc
        else:
            raise ValuationUnavailable(
                "Il servizio di stima è momentaneamente lento. Riprova tra poco."
            ) from last_error

    listings = _parse_listings(html)
    if not listings:
        raise ValuationUnavailable("Nessun annuncio comparabile trovato.")

    if request.year:
        listings = [item for item in listings if item["year"] in (None, request.year - 1, request.year, request.year + 1)]
    listings = [item for item in listings if _match_fuel(str(item["fuel"]), request.fuel_type)]

    priced: list[tuple[float, dict]] = []
    for listing in listings:
        price = _price_eur(listing.get("price"))
        if price is not None:
            priced.append((price, listing))

    if not priced:
        raise ValuationUnavailable("Nessun annuncio comparabile trovato.")

    if request.mileage:
        band = max(request.mileage * MILEAGE_BAND, 15000)
        close = [
            (price, listing)
            for price, listing in priced
            if listing.get("mileage") is not None
            and abs(int(listing["mileage"]) - request.mileage) <= band
        ]
        if len(close) >= MIN_SAMPLE:
            priced = close

    values = _filter_outliers([price for price, _ in priced])
    if not values:
        raise ValuationUnavailable("Nessun annuncio comparabile trovato.")

    estimated = statistics.median(values)
    ordered = sorted(values)
    if len(ordered) >= 4:
        low, _, high = statistics.quantiles(ordered, n=4)
    else:
        low, high = ordered[0], ordered[-1]

    default_title = f"{request.make} {request.model}".strip()
    closest = sorted(priced, key=lambda item: abs(item[0] - estimated))[:MAX_COMPARABLES]
    comparables: list[ValuationComparable] = []
    for price, listing in closest:
        make = str(listing.get("make") or request.make)
        model = str(listing.get("model") or request.model)
        comparables.append(
            ValuationComparable(
                title=f"{make} {model}".strip() or default_title,
                year=listing.get("year"),
                mileage=listing.get("mileage"),
                price_eur=round(price, 2),
                location="Italy",
            )
        )

    return VehicleValuationResponse(
        estimated_value=_round_value(estimated),
        trade_in_value=_round_value(estimated * TRADE_IN_RATIO),
        low_estimate=_round_value(low),
        high_estimate=_round_value(high),
        sample_size=len(values),
        source="AutoScout24 (RapidAPI)",
        confidence=_confidence(len(values)),
        comparables=comparables,
    )