import csv
import logging
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.schemas.api_schemas import EVCatalogItem

logger = logging.getLogger(__name__)

_INSIGNIFICANT_TRIMS = {"", "base", "standard", "standard range"}


def _backend_root() -> Path:
    # app/services/ev_dataset.py -> app/services -> app -> backend
    return Path(__file__).resolve().parents[2]


def dataset_path() -> Path:
    configured = Path(settings.EV_DATASET_PATH)
    return configured if configured.is_absolute() else _backend_root() / configured


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _to_int(value: object) -> int | None:
    number = _to_float(value)
    return int(number) if number is not None else None


def _model_label(model_name: str, trim_name: str, variant_name: str) -> str:
    base = model_name.strip()
    extra = variant_name.strip() or trim_name.strip()
    if extra.lower() in _INSIGNIFICANT_TRIMS or extra.lower() in base.lower():
        return base
    return f"{base} {extra}"


def _derive_consumption(usable_kwh: float | None, range_km: float | None) -> float | None:
    if usable_kwh and range_km and range_km > 0:
        return round(usable_kwh / range_km * 100, 1)
    return None


@lru_cache(maxsize=1)
def load_ev_dataset() -> tuple[EVCatalogItem, ...]:
    """Loads the OpenEV Data dataset (see backend/data/open-ev-data.csv).

    Returns an empty tuple when the file is missing so callers can fall back
    gracefully to the online API or the built-in mock catalog.
    """
    path = dataset_path()
    if not path.exists():
        logger.warning("OpenEV dataset not found at %s", path)
        return ()

    items: dict[tuple[str, str], EVCatalogItem] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            make = (row.get("make_name") or "").strip()
            model_name = (row.get("model_name") or "").strip()
            if not make or not model_name:
                continue

            gross = _to_float(row.get("battery_capacity_gross_kwh"))
            net = _to_float(row.get("battery_capacity_net_kwh"))
            wltp = _to_float(row.get("range_wltp_km"))
            epa = _to_float(row.get("range_epa_km"))
            range_km = wltp or epa
            usable = net or gross
            year = _to_int(row.get("year"))

            item = EVCatalogItem(
                make=make,
                model=_model_label(model_name, row.get("trim_name") or "", row.get("variant_name") or ""),
                year_start=year,
                year=year,
                battery_capacity=gross,
                battery_useable_capacity=usable,
                electric_range=range_km,
                charge_power_max=_to_float(row.get("dc_max_power_kw")),
                vehicle_consumption=_derive_consumption(usable, range_km),
                estimated_price_eur=None,
            )

            key = (item.make.lower(), item.model.lower())
            existing = items.get(key)
            if existing is None or (item.year or 0) > (existing.year or 0):
                items[key] = item

    logger.info("OpenEV dataset loaded: %d vehicle variants", len(items))
    return tuple(items.values())


def _relevance(item: EVCatalogItem, query: str, make_q: str, model_q: str) -> tuple:
    make = item.make.lower()
    model = item.model.lower()
    score = 3
    if make_q:
        score = 2 if make.startswith(make_q) else (1 if make_q in make else 3)
    elif model_q:
        score = 2 if model.startswith(model_q) else (1 if model_q in model else 3)
    elif query:
        if make.startswith(query) or model.startswith(query):
            score = 0
        elif query in make or query in model:
            score = 1
    return (score, make, model, -(item.year or 0))


def search_ev_dataset(
    make: str | None = None,
    model: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    search: str | None = None,
    limit: int = 10,
) -> list[EVCatalogItem]:
    """Filters the OpenEV dataset in memory (case-insensitive substring match)."""
    items = load_ev_dataset()
    if not items:
        return []

    query = (search or "").strip().lower()
    make_q = (make or "").strip().lower()
    model_q = (model or "").strip().lower()

    results: list[EVCatalogItem] = []
    for item in items:
        if make_q and make_q not in item.make.lower():
            continue
        if model_q and model_q not in item.model.lower():
            continue
        if query and query not in f"{item.make} {item.model}".lower():
            continue
        year = item.year or item.year_start or 0
        if min_year and year < min_year:
            continue
        if max_year and year > max_year:
            continue
        results.append(item)

    results.sort(key=lambda item: _relevance(item, query, make_q, model_q))
    return results[:limit]
