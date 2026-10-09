import json
import sys
from decimal import Decimal
from typing import Any

from app.domain.engine.break_even_calculator import calculate_break_even
from app.domain.engine.recommendation_engine import generate_decision_recommendation
from app.domain.engine.tco_calculator import calculate_vehicle_tco
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


def decimal_default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def run_analysis(filepath: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    current_car = Vehicle(**data["current_vehicle"])
    candidate_car = Vehicle(**data["candidate_vehicle"])
    usage = UsageProfile(**data.get("usage", {}))
    charging = ChargingProfile(**data.get("charging", {}))
    fuel = FuelProfile(**data.get("fuel", {}))
    ownership = OwnershipScenario(**data.get("ownership", {}))

    curr_tco = calculate_vehicle_tco(current_car, usage, charging, fuel, ownership)
    cand_tco = calculate_vehicle_tco(candidate_car, usage, charging, fuel, ownership)
    be = calculate_break_even(curr_tco, cand_tco, usage.annual_km)
    rec = generate_decision_recommendation(
        current_car, candidate_car, curr_tco, cand_tco, be, usage, charging, fuel, ownership
    )

    print("\n==========================================")
    print("        EV PURCHASE ADVISOR REPORT        ")
    print("==========================================")
    print(f"Current Vehicle:   {curr_tco.vehicle_name} (TCO: €{curr_tco.total_tco:,.2f})")
    print(f"Candidate Vehicle: {cand_tco.vehicle_name} (TCO: €{cand_tco.total_tco:,.2f})")
    print("------------------------------------------")
    print(f"Cost / km (Current):   €{curr_tco.tco_per_km:.3f} / km")
    print(f"Cost / km (Candidate): €{cand_tco.tco_per_km:.3f} / km")
    print(f"Cumulative Savings:    €{be.cumulative_savings_over_horizon:,.2f}")
    if be.operational_break_even_years is not None:
        print(f"Break-Even:            {be.operational_break_even_years:.1f} years ({be.operational_break_even_months:.0f} months)")
    print("------------------------------------------")
    print(f"RECOMMENDATION: {rec.rating}")
    print(f"Risk Score:     {rec.risk_score}/100 ({rec.risk_level})")
    print(f"\n{rec.summary_text}")
    print("\nKey Advantages:")
    for adv in rec.key_advantages:
        print(f"  ✓ {adv}")
    print("\nCautions & Risks:")
    for c in rec.cautions_and_risks:
        print(f"  ! {c}")
    print("==========================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "analyze":
        run_analysis(sys.argv[2])
    else:
        print("Usage: python -m app.cli analyze <path-to-analysis.json>")
