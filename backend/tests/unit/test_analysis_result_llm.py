from decimal import Decimal
import pytest

from app.domain.models.analysis_result import FullAnalysisResult
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.enums import FuelType, RecommendationRating, RiskLevel, VehicleType
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


def test_full_analysis_result_to_llm_context():
    curr_v = Vehicle(
        brand="Honda",
        model="CR-V",
        year=2016,
        vehicle_type=VehicleType.DIESEL,
        fuel_type=FuelType.DIESEL,
        purchase_price=Decimal("12000"),
        urban_consumption=6.0,
        extraurban_consumption=5.0,
        highway_consumption=6.5,
    )
    cand_v = Vehicle(
        brand="Renault",
        model="Zoe",
        year=2022,
        vehicle_type=VehicleType.BEV,
        fuel_type=FuelType.ELECTRICITY,
        purchase_price=Decimal("15000"),
        urban_consumption=13.0,
        extraurban_consumption=15.0,
        highway_consumption=20.0,
        usable_battery_capacity=52.0,
        wltp_range=395.0,
    )

    usage = UsageProfile(annual_km=25000)
    charging = ChargingProfile()
    fuel = FuelProfile()
    ownership = OwnershipScenario(horizon_years=5)

    curr_tco = VehicleTCOResult(
        vehicle_name="Honda CR-V",
        horizon_years=5,
        net_purchase_cost=Decimal("0"),
        total_tco=Decimal("18000"),
        tco_per_year=Decimal("3600"),
        tco_per_month=Decimal("300"),
        tco_per_km=Decimal("0.144"),
        yearly_breakdown=[],
        residual_value_end=Decimal("2000"),
        total_energy_fuel_cost=Decimal("10000"),
        total_maintenance_cost=Decimal("3000"),
        total_insurance_cost=Decimal("3000"),
        total_taxes=Decimal("1000"),
        total_financing_interest=Decimal("0"),
    )

    cand_tco = VehicleTCOResult(
        vehicle_name="Renault Zoe",
        horizon_years=5,
        net_purchase_cost=Decimal("15000"),
        total_tco=Decimal("10000"),
        tco_per_year=Decimal("2000"),
        tco_per_month=Decimal("166.67"),
        tco_per_km=Decimal("0.080"),
        yearly_breakdown=[],
        residual_value_end=Decimal("6000"),
        total_energy_fuel_cost=Decimal("3000"),
        total_maintenance_cost=Decimal("1000"),
        total_insurance_cost=Decimal("2000"),
        total_taxes=Decimal("0"),
        total_financing_interest=Decimal("0"),
    )

    be = BreakEvenResult(
        operational_break_even_years=2.5,
        operational_break_even_km=62500.0,
        cumulative_savings_over_horizon=Decimal("8000"),
        annual_operational_savings=Decimal("1400"),
        monthly_operational_savings=Decimal("116.67"),
    )

    range_res = RealWorldRangeResult(
        usable_battery_kwh=52.0,
        urban_range_km=380.0,
        extraurban_range_km=320.0,
        highway_range_km=250.0,
        mixed_range_km=315.0,
        winter_highway_range_km=200.0,
    )

    batt_res = BatteryDegradationResult(
        initial_capacity_kwh=52.0,
        yearly_capacities_kwh={1: 51.0, 5: 47.0},
        yearly_ranges_km={1: 310.0, 5: 285.0},
    )

    scenarios = ScenarioResult(
        pessimistic_tco=Decimal("12000"),
        base_tco=Decimal("10000"),
        optimistic_tco=Decimal("9000"),
        pessimistic_break_even_years=3.2,
        base_break_even_years=2.5,
        optimistic_break_even_years=2.0,
    )

    sensitivity = [
        SensitivityFactor(
            parameter_name="Home Electricity Rate",
            impact_score=8.5,
            impact_description="High impact on overall TCO",
        )
    ]

    rec = DecisionRecommendation(
        rating=RecommendationRating.STRONG_BUY.value,
        confidence=0.85,
        risk_score=20,
        risk_level=RiskLevel.LOW.value,
        summary_text="Great EV investment!",
        key_advantages=["Low running cost"],
        cautions_and_risks=[],
        explanations=[],
    )

    result = FullAnalysisResult(
        current_vehicle=curr_v,
        candidate_vehicle=cand_v,
        usage=usage,
        charging=charging,
        fuel=fuel,
        ownership=ownership,
        current_tco=curr_tco,
        candidate_tco=cand_tco,
        break_even=be,
        candidate_range=range_res,
        candidate_battery_degradation=batt_res,
        scenarios=scenarios,
        sensitivity=sensitivity,
        recommendation=rec,
    )

    context = result.to_llm_context()

    assert context["comparison_pair"]["current_vehicle"] == "Honda CR-V (2016)"
    assert context["comparison_pair"]["candidate_vehicle"] == "Renault Zoe (2022)"
    assert context["main_recommendation"]["rating"] == "STRONG_BUY"
    assert context["financial_summary"]["cumulative_savings_eur"] == 8000.0
    assert context["real_world_range"]["winter_highway_range_km"] == 200.0
    assert len(context["scenario_sensitivity"]["top_sensitive_parameters"]) == 1
