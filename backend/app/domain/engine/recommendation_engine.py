from decimal import Decimal

from app.domain.engine.range_calculator import calculate_real_world_range
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.enums import RecommendationRating, RiskLevel, ValueSource
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.results import (
    BreakEvenResult,
    DecisionRecommendation,
    RealWorldRangeResult,
    ValueExplanation,
    VehicleTCOResult,
)
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


def generate_decision_recommendation(
    current_vehicle: Vehicle,
    candidate_vehicle: Vehicle,
    current_tco: VehicleTCOResult,
    candidate_tco: VehicleTCOResult,
    break_even: BreakEvenResult,
    usage: UsageProfile,
    charging: ChargingProfile,
    fuel: FuelProfile,
    ownership: OwnershipScenario,
) -> DecisionRecommendation:
    savings = break_even.cumulative_savings_over_horizon
    horizon = ownership.horizon_years
    op_be_years = break_even.operational_break_even_years
    range_res: RealWorldRangeResult = calculate_real_world_range(candidate_vehicle, usage)

    key_advantages: list[str] = []
    cautions: list[str] = []
    explanations: list[ValueExplanation] = []

    # Risk Score Calculation (0 to 100)
    risk_score = 15  # Base low risk

    # 1. Financial Investment Risk
    if candidate_tco.net_purchase_cost > Decimal(30000):
        risk_score += 20
        cautions.append("Significant upfront initial capital required.")
    elif candidate_tco.net_purchase_cost > Decimal(18000):
        risk_score += 10

    # 2. Charging Access Risk
    if charging.home_charging_percentage < 0.50:
        risk_score += 25
        cautions.append("High reliance on public AC/DC fast charging increases energy cost.")
    else:
        key_advantages.append(f"High home charging ratio ({int(charging.home_charging_percentage * 100)}%) drastically reduces cost per km.")

    # 3. Mileage Advantage
    if usage.annual_km >= 20000:
        key_advantages.append(f"High annual mileage ({int(usage.annual_km):,} km/year) accelerates financial break-even.".replace(",", "."))
    elif usage.annual_km < 10000:
        cautions.append("Low annual mileage delays financial break-even.")

    # 4. Highway Range Risk
    if range_res.winter_highway_range_km < 200:
        risk_score += 15
        cautions.append(f"Limited winter highway range ({range_res.winter_highway_range_km:.0f} km) requires planning on long trips.")

    # Determine Rating
    confidence = 0.85
    if savings > Decimal(4000) and (op_be_years is not None and op_be_years <= horizon * 0.75):
        rating = RecommendationRating.STRONG_BUY
        summary = (
            f"Strongly recommended! Replacing {current_vehicle.brand} {current_vehicle.model} with "
            f"{candidate_vehicle.brand} {candidate_vehicle.model} is projected to save €{savings:,.2f} over {horizon} years. "
            f"Break-even occurs in approx {op_be_years:.1f} years."
        )
    elif savings > Decimal(1000) and (op_be_years is not None and op_be_years <= horizon):
        rating = RecommendationRating.BUY
        summary = (
            f"Financially advantageous decision. Switching saves approx €{savings:,.2f} over {horizon} years, "
            f"with break-even reached in {op_be_years:.1f} years."
        )
    elif savings >= Decimal(-1000) and savings <= Decimal(1000):
        rating = RecommendationRating.MAYBE
        summary = (
            f"Economically neutral decision. Total costs over {horizon} years are nearly equivalent "
            f"(difference of €{savings:,.2f}). Decision depends on personal preference for EV driving experience."
        )
    elif savings < Decimal(-1000) and candidate_tco.net_purchase_cost > current_tco.net_purchase_cost:
        rating = RecommendationRating.KEEP_CURRENT
        summary = (
            f"Financially better to keep current {current_vehicle.brand} {current_vehicle.model}. "
            f"The candidate EV incurs €{abs(savings):,.2f} higher total costs over the {horizon}-year period."
        )
    else:
        rating = RecommendationRating.AVOID
        summary = "Switching to this candidate vehicle is economically disadvantageous under current usage profile."

    risk_score = min(100, max(0, risk_score))
    risk_lvl = RiskLevel.LOW if risk_score < 30 else (RiskLevel.MEDIUM if risk_score < 60 else RiskLevel.HIGH)

    # Explanations
    explanations.append(
        ValueExplanation(
            value=f"€{candidate_tco.tco_per_km:.4f} / km",
            formula="Candidate Total TCO / Total Kilometers driven",
            source=ValueSource.FACT,
            notes=f"Compared to €{current_tco.tco_per_km:.4f} / km for current car."
        )
    )
    explanations.append(
        ValueExplanation(
            value=f"{range_res.mixed_range_km:.0f} km",
            formula="Usable battery kWh / Weighted consumption * 100",
            source=ValueSource.ESTIMATE,
            notes="Real world estimated range under mixed usage profile."
        )
    )

    return DecisionRecommendation(
        rating=rating.value,
        confidence=confidence,
        risk_score=risk_score,
        risk_level=risk_lvl.value,
        summary_text=summary,
        key_advantages=key_advantages,
        cautions_and_risks=cautions,
        explanations=explanations,
    )
