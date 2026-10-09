from fastapi import APIRouter

from app.domain.engine.break_even_calculator import calculate_break_even
from app.domain.engine.scenarios_calculator import calculate_sensitivity_factors, simulate_scenarios
from app.domain.engine.tco_calculator import calculate_vehicle_tco
from app.domain.models.results import (
    BreakEvenResult,
    ScenarioResult,
    VehicleTCOResult,
)
from app.schemas.api_schemas import BreakEvenRequest, TCORequest

router = APIRouter(prefix="/calculations", tags=["Calculations"])

@router.post("/tco", response_model=VehicleTCOResult)
def compute_tco(req: TCORequest):
    """Calculates multi-year TCO for a given vehicle."""
    return calculate_vehicle_tco(req.vehicle, req.usage, req.charging, req.fuel, req.ownership)

@router.post("/break-even", response_model=BreakEvenResult)
def compute_break_even(req: BreakEvenRequest):
    """Calculates operational and total break-even metrics between two vehicles."""
    curr_tco = calculate_vehicle_tco(req.current_vehicle, req.usage, req.charging, req.fuel, req.ownership)
    cand_tco = calculate_vehicle_tco(req.candidate_vehicle, req.usage, req.charging, req.fuel, req.ownership)
    return calculate_break_even(curr_tco, cand_tco, req.usage.annual_km)

@router.post("/scenarios", response_model=ScenarioResult)
def compute_scenarios(req: BreakEvenRequest):
    """Simulates pessimistic, base, and optimistic scenarios."""
    return simulate_scenarios(
        req.current_vehicle, req.candidate_vehicle, req.usage, req.charging, req.fuel, req.ownership
    )

@router.post("/sensitivity")
def compute_sensitivity(req: BreakEvenRequest):
    """Computes parameter sensitivity factors."""
    return calculate_sensitivity_factors(
        req.current_vehicle, req.candidate_vehicle, req.usage, req.charging, req.fuel, req.ownership
    )
