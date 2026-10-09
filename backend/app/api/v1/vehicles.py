from fastapi import APIRouter, HTTPException, Query

from app.core.seed import DEMO_VEHICLES
from app.domain.models.vehicle import Vehicle
from app.schemas.api_schemas import EVCatalogItem
from app.services.ev_catalog_service import search_ev_catalog

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
