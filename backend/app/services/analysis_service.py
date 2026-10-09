from typing import Any

from app.domain.engine.break_even_calculator import calculate_break_even
from app.domain.engine.range_calculator import (
    calculate_battery_degradation,
    calculate_real_world_range,
)
from app.domain.engine.recommendation_engine import generate_decision_recommendation
from app.domain.engine.scenarios_calculator import calculate_sensitivity_factors, simulate_scenarios
from app.domain.engine.tco_calculator import calculate_vehicle_tco
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.results import (
    BatteryDegradationResult,
    BreakEvenResult,
    DecisionRecommendation,
    RealWorldRangeResult,
    ScenarioResult,
    SensitivityFactor,
    VehicleTCOResult,
)
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


class AnalysisRequest(Vehicle):
    pass

class FullAnalysisPayload:
    pass

def run_full_analysis(
    current_vehicle: Vehicle,
    candidate_vehicle: Vehicle,
    usage: UsageProfile,
    charging: ChargingProfile,
    fuel: FuelProfile,
    ownership: OwnershipScenario,
) -> dict[str, Any]:
    curr_tco: VehicleTCOResult = calculate_vehicle_tco(current_vehicle, usage, charging, fuel, ownership)
    cand_tco: VehicleTCOResult = calculate_vehicle_tco(candidate_vehicle, usage, charging, fuel, ownership)

    be: BreakEvenResult = calculate_break_even(curr_tco, cand_tco, usage.annual_km)
    cand_range: RealWorldRangeResult = calculate_real_world_range(candidate_vehicle, usage)
    cand_batt: BatteryDegradationResult = calculate_battery_degradation(
        candidate_vehicle, usage, ownership.horizon_years
    )
    scenarios: ScenarioResult = simulate_scenarios(
        current_vehicle, candidate_vehicle, usage, charging, fuel, ownership
    )
    sensitivity: list[SensitivityFactor] = calculate_sensitivity_factors(
        current_vehicle, candidate_vehicle, usage, charging, fuel, ownership
    )
    rec: DecisionRecommendation = generate_decision_recommendation(
        current_vehicle, candidate_vehicle, curr_tco, cand_tco, be, usage, charging, fuel, ownership
    )

    return {
        "current_tco": curr_tco,
        "candidate_tco": cand_tco,
        "break_even": be,
        "candidate_range": cand_range,
        "candidate_battery_degradation": cand_batt,
        "scenarios": scenarios,
        "sensitivity": sensitivity,
        "recommendation": rec,
    }
