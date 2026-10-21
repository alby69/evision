from typing import Any
from pydantic import BaseModel, Field

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


class FullAnalysisResult(BaseModel):
    id: str | None = None
    title: str = "EV Replacement Decision Analysis"
    current_vehicle: Vehicle
    candidate_vehicle: Vehicle
    usage: UsageProfile
    charging: ChargingProfile
    fuel: FuelProfile
    ownership: OwnershipScenario
    current_tco: VehicleTCOResult
    candidate_tco: VehicleTCOResult
    break_even: BreakEvenResult
    candidate_range: RealWorldRangeResult
    candidate_battery_degradation: BatteryDegradationResult
    scenarios: ScenarioResult
    sensitivity: list[SensitivityFactor] = Field(default_factory=list)
    recommendation: DecisionRecommendation

    def to_llm_context(self) -> dict[str, Any]:
        """Generates a clean, structured, semantic JSON representation tailored for LLM system prompts.

        Transforms raw mathematical outputs into structured decision intelligence for AI advisory.
        """
        savings_val = float(self.break_even.cumulative_savings_over_horizon)
        current_tco_val = float(self.current_tco.total_tco)
        candidate_tco_val = float(self.candidate_tco.total_tco)

        return {
            "title": self.title,
            "comparison_pair": {
                "current_vehicle": f"{self.current_vehicle.brand} {self.current_vehicle.model} ({self.current_vehicle.year})",
                "candidate_vehicle": f"{self.candidate_vehicle.brand} {self.candidate_vehicle.model} ({self.candidate_vehicle.year})",
            },
            "horizon_years": self.ownership.horizon_years,
            "usage_profile": {
                "annual_km": self.usage.annual_km,
                "city_percentage": self.usage.city_percentage,
                "highway_percentage": self.usage.highway_percentage,
            },
            "main_recommendation": {
                "rating": self.recommendation.rating,
                "confidence": self.recommendation.confidence,
                "risk_score": self.recommendation.risk_score,
                "risk_level": self.recommendation.risk_level,
                "summary": self.recommendation.summary_text,
            },
            "financial_summary": {
                "current_vehicle_tco_eur": round(current_tco_val, 2),
                "candidate_vehicle_tco_eur": round(candidate_tco_val, 2),
                "cumulative_savings_eur": round(savings_val, 2),
                "net_tco_difference_pct": round(((candidate_tco_val - current_tco_val) / current_tco_val) * 100, 1) if current_tco_val > 0 else 0.0,
                "candidate_cost_per_km_eur": float(self.candidate_tco.tco_per_km),
                "current_cost_per_km_eur": float(self.current_tco.tco_per_km),
            },
            "break_even_timeline": {
                "operational_break_even_years": self.break_even.operational_break_even_years,
                "operational_break_even_km": self.break_even.operational_break_even_km,
                "monthly_operational_savings_eur": float(self.break_even.monthly_operational_savings),
            },
            "real_world_range": {
                "mixed_range_km": self.candidate_range.mixed_range_km,
                "winter_highway_range_km": self.candidate_range.winter_highway_range_km,
                "usable_battery_kwh": self.candidate_range.usable_battery_kwh,
            },
            "key_advantages": self.recommendation.key_advantages,
            "cautions_and_risks": self.recommendation.cautions_and_risks,
            "scenario_sensitivity": {
                "pessimistic_tco_eur": float(self.scenarios.pessimistic_tco),
                "base_tco_eur": float(self.scenarios.base_tco),
                "optimistic_tco_eur": float(self.scenarios.optimistic_tco),
                "top_sensitive_parameters": [
                    {"parameter": s.parameter_name, "impact_score": s.impact_score, "description": s.impact_description}
                    for s in self.sensitivity[:3]
                ],
            },
        }
