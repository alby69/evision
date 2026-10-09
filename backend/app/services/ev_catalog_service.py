import logging

import httpx

from app.core.config import settings
from app.schemas.api_schemas import EVCatalogItem

logger = logging.getLogger(__name__)

# Fallback catalog data when API key is missing or external API is unavailable
MOCK_EV_CATALOG: list[EVCatalogItem] = [
    EVCatalogItem(
        make="Tesla",
        model="Model 3 Long Range",
        year_start=2021,
        year=2023,
        battery_capacity=82.0,
        battery_useable_capacity=75.0,
        electric_range=576.0,
        charge_power_max=250.0,
        vehicle_consumption=14.7,
        estimated_price_eur=49990.0,
    ),
    EVCatalogItem(
        make="Tesla",
        model="Model Y Long Range",
        year_start=2021,
        year=2023,
        battery_capacity=82.0,
        battery_useable_capacity=75.0,
        electric_range=533.0,
        charge_power_max=250.0,
        vehicle_consumption=15.7,
        estimated_price_eur=52990.0,
    ),
    EVCatalogItem(
        make="Renault",
        model="Zoe R110 52kWh",
        year_start=2019,
        year=2022,
        battery_capacity=55.0,
        battery_useable_capacity=52.0,
        electric_range=395.0,
        charge_power_max=50.0,
        vehicle_consumption=15.0,
        estimated_price_eur=33500.0,
    ),
    EVCatalogItem(
        make="Renault",
        model="5 E-Tech 52kWh",
        year_start=2024,
        year=2024,
        battery_capacity=52.0,
        battery_useable_capacity=52.0,
        electric_range=400.0,
        charge_power_max=100.0,
        vehicle_consumption=14.5,
        estimated_price_eur=25000.0,
    ),
    EVCatalogItem(
        make="MG",
        model="MG4 Electric Standard",
        year_start=2022,
        year=2023,
        battery_capacity=51.0,
        battery_useable_capacity=50.8,
        electric_range=350.0,
        charge_power_max=88.0,
        vehicle_consumption=16.0,
        estimated_price_eur=30790.0,
    ),
    EVCatalogItem(
        make="Fiat",
        model="500e 42kWh",
        year_start=2020,
        year=2023,
        battery_capacity=42.0,
        battery_useable_capacity=37.3,
        electric_range=320.0,
        charge_power_max=85.0,
        vehicle_consumption=14.0,
        estimated_price_eur=28950.0,
    ),
    EVCatalogItem(
        make="Volkswagen",
        model="ID.3 Pro 58kWh",
        year_start=2020,
        year=2023,
        battery_capacity=62.0,
        battery_useable_capacity=58.0,
        electric_range=425.0,
        charge_power_max=120.0,
        vehicle_consumption=15.5,
        estimated_price_eur=39990.0,
    ),
    EVCatalogItem(
        make="Hyundai",
        model="Ioniq 5 Long Range RWD",
        year_start=2021,
        year=2023,
        battery_capacity=77.4,
        battery_useable_capacity=74.0,
        electric_range=507.0,
        charge_power_max=233.0,
        vehicle_consumption=17.0,
        estimated_price_eur=48350.0,
    ),
    EVCatalogItem(
        make="Kia",
        model="EV6 Long Range RWD",
        year_start=2021,
        year=2023,
        battery_capacity=77.4,
        battery_useable_capacity=74.0,
        electric_range=528.0,
        charge_power_max=233.0,
        vehicle_consumption=16.5,
        estimated_price_eur=49950.0,
    ),
    EVCatalogItem(
        make="Smart",
        model="EQ Fortwo",
        year_start=2018,
        year=2022,
        battery_capacity=17.6,
        battery_useable_capacity=16.7,
        electric_range=135.0,
        charge_power_max=22.0,
        vehicle_consumption=16.0,
        estimated_price_eur=25000.0,
    ),
    EVCatalogItem(
        make="BMW",
        model="i4 eDrive40",
        year_start=2021,
        year=2023,
        battery_capacity=83.9,
        battery_useable_capacity=80.7,
        electric_range=590.0,
        charge_power_max=205.0,
        vehicle_consumption=16.1,
        estimated_price_eur=60900.0,
    ),
    EVCatalogItem(
        make="Nissan",
        model="Leaf 39kWh",
        year_start=2018,
        year=2022,
        battery_capacity=40.0,
        battery_useable_capacity=39.0,
        electric_range=270.0,
        charge_power_max=50.0,
        vehicle_consumption=17.1,
        estimated_price_eur=34200.0,
    ),
]


def _filter_mock_catalog(
    make: str | None = None,
    model: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    search: str | None = None,
    limit: int = 10,
) -> list[EVCatalogItem]:
    results = list(MOCK_EV_CATALOG)

    if search:
        s = search.strip().lower()
        results = [
            item for item in results
            if s in item.make.lower() or s in item.model.lower()
        ]

    if make:
        m = make.strip().lower()
        results = [item for item in results if m in item.make.lower()]

    if model:
        md = model.strip().lower()
        results = [item for item in results if md in item.model.lower()]

    if min_year:
        results = [
            item for item in results
            if (item.year and item.year >= min_year) or (item.year_start and item.year_start >= min_year)
        ]

    if max_year:
        results = [
            item for item in results
            if (item.year and item.year <= max_year) or (item.year_start and item.year_start <= max_year)
        ]

    return results[:limit]


async def search_ev_catalog(
    make: str | None = None,
    model: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    search: str | None = None,
    limit: int = 10,
) -> list[EVCatalogItem]:
    """
    Searches EV specifications catalog.
    Uses API Ninjas if EV_CATALOG_API_KEY is configured, falling back gracefully to mock catalog data.
    """
    api_key = settings.EV_CATALOG_API_KEY.strip()

    if not api_key:
        return _filter_mock_catalog(make, model, min_year, max_year, search, limit)

    params: dict[str, str | int] = {}
    if make:
        params["make"] = make
    if model:
        params["model"] = model
    if search and not make and not model:
        params["model"] = search
    if min_year:
        params["min_year"] = min_year
    if max_year:
        params["max_year"] = max_year

    headers = {"X-Api-Key": api_key}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.EV_CATALOG_API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            items: list[EVCatalogItem] = []
            if isinstance(data, list):
                for raw in data:
                    if isinstance(raw, dict):
                        item = EVCatalogItem(
                            make=str(raw.get("make") or "Unknown"),
                            model=str(raw.get("model") or "EV Model"),
                            year_start=raw.get("year_start") or raw.get("year"),
                            year=raw.get("year"),
                            battery_capacity=raw.get("battery_capacity"),
                            battery_useable_capacity=raw.get("battery_useable_capacity") or raw.get("battery_capacity"),
                            electric_range=raw.get("electric_range") or raw.get("range"),
                            charge_power_max=raw.get("charge_power_max"),
                            vehicle_consumption=raw.get("vehicle_consumption"),
                            estimated_price_eur=raw.get("estimated_price_eur"),
                        )
                        items.append(item)

            if items:
                return items[:limit]
            # If API returned empty results, fallback to local search
            return _filter_mock_catalog(make, model, min_year, max_year, search, limit)

    except Exception as exc:  # noqa: BLE001
        logger.warning("EV catalog API request failed, using mock data fallback: %s", exc)
        return _filter_mock_catalog(make, model, min_year, max_year, search, limit)
