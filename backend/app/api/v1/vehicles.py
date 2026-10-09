
from fastapi import APIRouter, HTTPException

from app.core.seed import DEMO_VEHICLES
from app.domain.models.vehicle import Vehicle

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

_in_memory_vehicles: list[Vehicle] = list(DEMO_VEHICLES)

@router.get("", response_model=list[Vehicle])
def list_vehicles():
    """Returns list of demo and user saved vehicles."""
    return _in_memory_vehicles

@router.post("", response_model=Vehicle, status_code=201)
def create_vehicle(vehicle: Vehicle):
    """Creates a custom vehicle record."""
    if not vehicle.id:
        import uuid
        vehicle.id = f"custom-{uuid.uuid4().hex[:8]}"
    _in_memory_vehicles.append(vehicle)
    return vehicle

@router.get("/{vehicle_id}", response_model=Vehicle)
def get_vehicle(vehicle_id: str):
    """Fetches vehicle by ID."""
    for v in _in_memory_vehicles:
        if v.id == vehicle_id:
            return v
    raise HTTPException(status_code=404, detail="Vehicle not found")
