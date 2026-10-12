import logging

import httpx

from app.core.config import settings
from app.schemas.api_schemas import CarCatalogItem, CarFacetValue
from app.services.numeric_utils import parse_int, parse_number

logger = logging.getLogger(__name__)

ALLOWED_FACETS = {
    "make",
    "model",
    "generation",
    "chassis_code",
    "body",
    "doors",
    "fuel",
    "transmission",
    "drive",
    "cylinders",
    "year",
    "badge",
}

# Fallback catalog used when the API key is missing or the external API is unavailable.
MOCK_CAR_CATALOG: list[CarCatalogItem] = [
    CarCatalogItem(
        make="Volkswagen", model="Golf", year=2019, fuel_type="diesel",
        transmission="manual", drive="fwd", cylinders=4, displacement=2.0, car_class="compact car",
    ),
    CarCatalogItem(
        make="Volkswagen", model="Polo", year=2018, fuel_type="gasoline",
        transmission="manual", drive="fwd", cylinders=3, displacement=1.0, car_class="subcompact car",
    ),
    CarCatalogItem(
        make="Fiat", model="Panda", year=2020, fuel_type="gasoline",
        transmission="manual", drive="fwd", cylinders=2, displacement=1.0, car_class="minicompact car",
    ),
    CarCatalogItem(
        make="Fiat", model="500", year=2017, fuel_type="diesel",
        transmission="manual", drive="fwd", cylinders=4, displacement=1.3, car_class="minicompact car",
    ),
    CarCatalogItem(
        make="Toyota", model="Corolla", year=2020, fuel_type="gasoline",
        transmission="automatic", drive="fwd", cylinders=4, displacement=2.0, car_class="compact car",
    ),
    CarCatalogItem(
        make="Toyota", model="Yaris", year=2019, fuel_type="hybrid",
        transmission="automatic", drive="fwd", cylinders=4, displacement=1.5, car_class="subcompact car",
    ),
    CarCatalogItem(
        make="Honda", model="CR-V", year=2016, fuel_type="diesel",
        transmission="automatic", drive="4wd", cylinders=4, displacement=1.6, car_class="suv",
    ),
    CarCatalogItem(
        make="Ford", model="Focus", year=2018, fuel_type="diesel",
        transmission="manual", drive="fwd", cylinders=4, displacement=1.5, car_class="compact car",
    ),
    CarCatalogItem(
        make="Renault", model="Clio", year=2019, fuel_type="diesel",
        transmission="manual", drive="fwd", cylinders=4, displacement=1.5, car_class="subcompact car",
    ),
    CarCatalogItem(
        make="BMW", model="3 Series", year=2018, fuel_type="diesel",
        transmission="automatic", drive="rwd", cylinders=4, displacement=2.0, car_class="compact car",
    ),
    CarCatalogItem(
        make="Mercedes-Benz", model="C-Class", year=2019, fuel_type="diesel",
        transmission="automatic", drive="rwd", cylinders=4, displacement=2.0, car_class="compact car",
    ),
    CarCatalogItem(
        make="Audi", model="A4", year=2018, fuel_type="diesel",
        transmission="automatic", drive="fwd", cylinders=4, displacement=2.0, car_class="compact car",
    ),
]


def _api_key() -> str:
    return (settings.CAR_CATALOG_API_KEY or settings.EV_CATALOG_API_KEY).strip()


def _mock_facets(
    facets: list[str],
    make: str | None = None,
    model: str | None = None,
) -> dict[str, list[CarFacetValue]]:
    results = list(MOCK_CAR_CATALOG)
    if make:
        results = [item for item in results if make.strip().lower() in item.make.lower()]
    if model:
        results = [item for item in results if model.strip().lower() in item.model.lower()]

    def counts(values: list[object]) -> list[CarFacetValue]:
        tally: dict[object, int] = {}
        for value in values:
            if value in (None, ""):
                continue
            tally[value] = tally.get(value, 0) + 1
        return [CarFacetValue(value=value, count=count) for value, count in sorted(tally.items(), key=lambda kv: str(kv[0]))]

    getters: dict[str, list[object]] = {
        "make": [item.make for item in results],
        "model": [item.model for item in results],
        "year": [item.year for item in results],
        "fuel": [item.fuel_type for item in results],
        "transmission": [item.transmission for item in results],
        "drive": [item.drive for item in results],
        "cylinders": [item.cylinders for item in results],
        "body": [item.car_class for item in results],
    }

    return {facet: counts(getters[facet]) for facet in facets if facet in getters}


def _parse_facets(data: object) -> dict[str, list[CarFacetValue]]:
    result: dict[str, list[CarFacetValue]] = {}
    if not isinstance(data, dict):
        return result
    for name, values in data.items():
        if not isinstance(values, list):
            continue
        items: list[CarFacetValue] = []
        for raw in values:
            if not isinstance(raw, dict) or "value" not in raw:
                continue
            value = raw["value"]
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            items.append(CarFacetValue(value=value, count=int(raw.get("count") or 0)))
        result[name] = items
    return result


def _parse_cars(data: object) -> list[CarCatalogItem]:
    items: list[CarCatalogItem] = []
    if not isinstance(data, list):
        return items
    for raw in data:
        if not isinstance(raw, dict):
            continue
        items.append(
            CarCatalogItem(
                make=str(raw.get("make") or "Unknown"),
                model=str(raw.get("model") or ""),
                year=parse_int(raw.get("year")),
                fuel_type=str(raw["fuel_type"]) if raw.get("fuel_type") else None,
                transmission=str(raw["transmission"]) if raw.get("transmission") else None,
                drive=str(raw["drive"]) if raw.get("drive") else None,
                cylinders=parse_int(raw.get("cylinders")),
                displacement=parse_number(raw.get("displacement")),
                car_class=str(raw["class"]) if raw.get("class") else None,
            )
        )
    return items


async def get_car_facets(
    facets: list[str],
    make: str | None = None,
    model: str | None = None,
    generation: str | None = None,
    body: str | None = None,
    fuel: str | None = None,
    transmission: str | None = None,
    drive: str | None = None,
    year: int | None = None,
) -> dict[str, list[CarFacetValue]]:
    """Returns available values and counts for the requested catalog dimensions.

    Uses the API Ninjas /v2/carfacets endpoint (available on the free tier) and
    falls back to a small local dataset when no API key is configured.
    """
    selected = [facet for facet in facets if facet in ALLOWED_FACETS][:6]
    if not selected:
        return {}

    api_key = _api_key()
    if not api_key:
        return _mock_facets(selected, make=make, model=model)

    params: dict[str, str | int] = {"facets": ",".join(selected)}
    for name, value in (
        ("make", make),
        ("model", model),
        ("generation", generation),
        ("body", body),
        ("fuel", fuel),
        ("transmission", transmission),
        ("drive", drive),
        ("year", year),
    ):
        if value not in (None, ""):
            params[name] = value

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                settings.CAR_FACETS_API_URL,
                headers={"X-Api-Key": api_key},
                params=params,
            )
            response.raise_for_status()
            return _parse_facets(response.json())
    except Exception as exc:  # noqa: BLE001
        logger.warning("Car facets API request failed, using mock data fallback: %s", exc)
        return _mock_facets(selected, make=make, model=model)


def _mock_cars(
    make: str,
    model: str,
    year: int | None = None,
    fuel_type: str | None = None,
) -> list[CarCatalogItem]:
    results = list(MOCK_CAR_CATALOG)
    if make:
        results = [item for item in results if make.strip().lower() in item.make.lower()]
    if model:
        results = [item for item in results if model.strip().lower() in item.model.lower()]
    if year:
        results = [item for item in results if item.year == year]
    if fuel_type:
        results = [item for item in results if (item.fuel_type or "").lower() == fuel_type.strip().lower()]
    return results


async def search_cars(
    make: str,
    model: str,
    year: int | None = None,
    fuel_type: str | None = None,
) -> list[CarCatalogItem]:
    """Searches conventional cars by make/model (and optional year/fuel).

    Uses the API Ninjas /v1/cars endpoint, which is available on the free tier,
    and falls back to a small local dataset when no API key is configured.
    """
    if not make or not model:
        return []

    api_key = _api_key()
    if not api_key:
        return _mock_cars(make, model, year=year, fuel_type=fuel_type)

    params: dict[str, str | int] = {"make": make, "model": model}
    if year:
        params["year"] = year
    if fuel_type:
        params["fuel_type"] = fuel_type

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                settings.CAR_CATALOG_API_URL,
                headers={"X-Api-Key": api_key},
                params=params,
            )
            response.raise_for_status()
            items = _parse_cars(response.json())
            if items:
                return items
            return _mock_cars(make, model, year=year, fuel_type=fuel_type)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Car catalog API request failed, using mock data fallback: %s", exc)
        return _mock_cars(make, model, year=year, fuel_type=fuel_type)
