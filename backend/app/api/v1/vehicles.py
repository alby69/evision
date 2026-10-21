from fastapi import APIRouter, HTTPException, Query

from app.core.seed import DEMO_VEHICLES
from app.domain.models.vehicle import Vehicle
from app.schemas.api_schemas import (
    CarCatalogItem,
    CarFacetValue,
    EVCatalogItem,
    ParsedListingRequest,
    ParsedListingResponse,
    VehicleValuationRequest,
    VehicleValuationResponse,
)
from app.services.car_catalog_service import get_car_facets as get_car_facets_data
from app.services.car_catalog_service import search_cars
from app.services.ev_catalog_service import search_ev_catalog
from app.services.listing_parser_service import parse_listing_url
from app.services.valuation_service import ValuationUnavailable, estimate_vehicle_value

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

_in_memory_vehicles: list[Vehicle] = list(DEMO_VEHICLES)


@router.get("", response_model=list[Vehicle])
def list_vehicles() -> list[Vehicle]:
    """Returns list of demo and user saved vehicles."""
    return _in_memory_vehicles


@router.get("/catalog", response_model=list[EVCatalogItem])
async def get_ev_catalog(
    make: str | None = Query(None, description="Filter by vehicle make/brand (e.g. Tesla)"),
    model: str | None = Query(None, description="Filter by model name (e.g. Model 3)"),
    search: str | None = Query(None, description="Free text search on make and model"),
    min_year: int | None = Query(None, description="Filter by minimum release year"),
    max_year: int | None = Query(None, description="Filter by maximum release year"),
    limit: int = Query(10, ge=1, le=50, description="Max number of items to return"),
) -> list[EVCatalogItem]:
    """
    Search and retrieve electric vehicle technical specifications from catalog dataset/API.
    """
    return await search_ev_catalog(
        make=make,
        model=model,
        min_year=min_year,
        max_year=max_year,
        search=search,
        limit=limit,
    )


@router.get("/car-facets", response_model=dict[str, list[CarFacetValue]])
async def get_car_facets(
    facets: str = Query(..., description="Comma-separated dimensions, e.g. make,model,fuel (max 6)"),
    make: str | None = Query(None, description="Narrow to a vehicle make"),
    model: str | None = Query(None, description="Narrow to a vehicle model"),
    generation: str | None = Query(None, description="Narrow to a generation"),
    body: str | None = Query(None, description="Narrow to a body style"),
    fuel: str | None = Query(None, description="Narrow to a fuel type"),
    transmission: str | None = Query(None, description="Narrow to a transmission"),
    drive: str | None = Query(None, description="Narrow to a drive type"),
    year: int | None = Query(None, description="Narrow to a production year"),
) -> dict[str, list[CarFacetValue]]:
    """
    Cascading dropdown values for the conventional (ICE) car catalog (API Ninjas /v2/carfacets).

    Available on the API Ninjas free tier; falls back to a local dataset when no key is set.
    """
    facet_list = [facet.strip() for facet in facets.split(",") if facet.strip()]
    return await get_car_facets_data(
        facet_list,
        make=make,
        model=model,
        generation=generation,
        body=body,
        fuel=fuel,
        transmission=transmission,
        drive=drive,
        year=year,
    )


@router.get("/cars", response_model=list[CarCatalogItem])
async def list_cars(
    make: str = Query(..., description="Vehicle make, e.g. Volkswagen"),
    model: str = Query(..., description="Vehicle model, e.g. Golf"),
    year: int | None = Query(None, description="Filter by production year"),
    fuel_type: str | None = Query(None, description="Filter by fuel type (gasoline, diesel, hybrid, ...)"),
) -> list[CarCatalogItem]:
    """
    Searches conventional cars by make/model (API Ninjas /v1/cars, available on the free tier).
    """
    return await search_cars(make=make, model=model, year=year, fuel_type=fuel_type)


@router.post("/parse-listing", response_model=ParsedListingResponse)
async def parse_vehicle_listing(request: ParsedListingRequest) -> ParsedListingResponse:
    """
    Parses a vehicle listing URL (AutoScout24, Subito, etc.) and extracts make, model, year, price, and mileage.
    """
    try:
        return await parse_listing_url(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/valuation", response_model=VehicleValuationResponse)
async def estimate_value(request: VehicleValuationRequest) -> VehicleValuationResponse:
    """
    Estimates the current market/trade-in value of a used car from comparable listings.

    Derives the estimate from AutoScout24.it listings (RapidAPI "AutoScout24 Scraper"),
    filtered by make/model/year and mileage when known.
    """
    try:
        return await estimate_vehicle_value(request)
    except ValuationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("", response_model=Vehicle, status_code=201)
def create_vehicle(vehicle: Vehicle) -> Vehicle:
    """Creates a custom vehicle record."""
    if not vehicle.id:
        import uuid
        vehicle.id = f"custom-{uuid.uuid4().hex[:8]}"
    _in_memory_vehicles.append(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=Vehicle)
def get_vehicle(vehicle_id: str) -> Vehicle:
    """Fetches vehicle by ID."""
    for v in _in_memory_vehicles:
        if v.id == vehicle_id:
            return v
    raise HTTPException(status_code=404, detail="Vehicle not found")
