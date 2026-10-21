import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache store: { key: (timestamp, data) }
_PRICE_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 24 * 3600  # 24 hours

REGION_MAP = {
    "IT-21": "Piemonte",
    "IT-23": "Valle d'Aosta",
    "IT-25": "Lombardia",
    "IT-32": "Trentino-Alto Adige",
    "IT-34": "Veneto",
    "IT-36": "Friuli-Venezia Giulia",
    "IT-42": "Liguria",
    "IT-45": "Emilia-Romagna",
    "IT-52": "Toscana",
    "IT-55": "Umbria",
    "IT-57": "Marche",
    "IT-62": "Lazio",
    "IT-65": "Abruzzo",
    "IT-67": "Molise",
    "IT-72": "Campania",
    "IT-75": "Puglia",
    "IT-77": "Basilicata",
    "IT-78": "Calabria",
    "IT-82": "Sicilia",
    "IT-88": "Sardegna",
}


def _get_fallback_prices(region: str) -> dict[str, Any]:
    return {
        "region": region,
        "region_name": REGION_MAP.get(region, "Italia"),
        "petrol_eur_l": round(settings.DEFAULT_PETROL_PRICE, 3),
        "diesel_eur_l": round(settings.DEFAULT_DIESEL_PRICE, 3),
        "lpg_eur_l": round(settings.DEFAULT_LPG_PRICE, 3),
        "cng_eur_kg": round(settings.DEFAULT_CNG_PRICE, 3),
        "electricity_home_eur_kwh": round(settings.DEFAULT_ELECTRICITY_HOME_PRICE, 3),
        "source": "DEFAULT_FALLBACK",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


async def fetch_regional_prices(region: str = "IT-25") -> dict[str, Any]:
    cache_key = f"fuel_price_{region.upper()}"
    now = time.time()

    if cache_key in _PRICE_CACHE:
        ts, cached_data = _PRICE_CACHE[cache_key]
        if now - ts < CACHE_TTL_SECONDS:
            logger.debug("Returning cached regional energy prices for %s", region)
            return cached_data

    url = settings.MISE_FUEL_PRICES_API_URL
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200 and resp.text:
                lines = resp.text.splitlines()
                petrol_vals, diesel_vals, lpg_vals, cng_vals = [], [], [], []

                for line in lines[1:]:  # skip header
                    parts = line.split(";")
                    if len(parts) >= 4:
                        fuel_desc = parts[1].strip().lower()
                        try:
                            price_val = float(parts[2].replace(",", "."))
                        except ValueError:
                            continue

                        if "benzina" in fuel_desc:
                            petrol_vals.append(price_val)
                        elif "gasolio" in fuel_desc:
                            diesel_vals.append(price_val)
                        elif "gpl" in fuel_desc:
                            lpg_vals.append(price_val)
                        elif "metano" in fuel_desc:
                            cng_vals.append(price_val)

                data = {
                    "region": region,
                    "region_name": REGION_MAP.get(region, "Italia"),
                    "petrol_eur_l": round(sum(petrol_vals) / len(petrol_vals), 3) if petrol_vals else settings.DEFAULT_PETROL_PRICE,
                    "diesel_eur_l": round(sum(diesel_vals) / len(diesel_vals), 3) if diesel_vals else settings.DEFAULT_DIESEL_PRICE,
                    "lpg_eur_l": round(sum(lpg_vals) / len(lpg_vals), 3) if lpg_vals else settings.DEFAULT_LPG_PRICE,
                    "cng_eur_kg": round(sum(cng_vals) / len(cng_vals), 3) if cng_vals else settings.DEFAULT_CNG_PRICE,
                    "electricity_home_eur_kwh": round(settings.DEFAULT_ELECTRICITY_HOME_PRICE, 3),
                    "source": "MISE_API",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                _PRICE_CACHE[cache_key] = (now, data)
                return data
    except Exception as e:
        logger.warning("Failed to fetch MISE fuel prices from %s: %s. Using default fallback.", url, e)

    fallback = _get_fallback_prices(region)
    _PRICE_CACHE[cache_key] = (now, fallback)
    return fallback
