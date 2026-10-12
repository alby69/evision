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


def _format_duration(years: float) -> str:
    """Formats a duration in years as years + months, e.g.
    1.6 -> "1 anno e 7 mesi"; 0.5 -> "6 mesi"; 2.0 -> "2 anni".
    """
    total_months = round(years * 12)
    if total_months < 12:
        return f"{total_months} {'mese' if total_months == 1 else 'mesi'}"
    whole_years, months = divmod(total_months, 12)
    years_part = f"{whole_years} {'anno' if whole_years == 1 else 'anni'}"
    if months == 0:
        return years_part
    return f"{years_part} e {months} {'mese' if months == 1 else 'mesi'}"


def _format_eur(value, decimals: int = 2) -> str:
    """Formats a euro amount with Italian conventions: 7941.95 -> '€7.941,95'."""
    sign = "-" if value < 0 else ""
    body = f"{abs(value):,.{decimals}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return f"{sign}€{body}"


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
        cautions.append("Richiede un esborso iniziale significativo.")
    elif candidate_tco.net_purchase_cost > Decimal(18000):
        risk_score += 10

    # 2. Charging Access Risk
    if charging.home_charging_percentage < 0.50:
        risk_score += 25
        cautions.append("Molto ricorso alla ricarica pubblica AC/DC: il costo dell’energia sale.")
    else:
        key_advantages.append(
            f"Alta quota di ricarica a casa ({int(charging.home_charging_percentage * 100)}%): "
            f"riduce drasticamente il costo per km."
        )

    # 3. Mileage Advantage
    if usage.annual_km >= 20000:
        key_advantages.append(
            f"Percorrenza annua elevata ({int(usage.annual_km):,} km/anno): accorcia il tempo di rientro.".replace(",", ".")
        )
    elif usage.annual_km < 10000:
        cautions.append("Percorrenza annua bassa: allunga il tempo di rientro.")

    # 4. Highway Range Risk
    if range_res.winter_highway_range_km < 200:
        risk_score += 15
        cautions.append(
            f"Autonomia invernale in autostrada limitata ({range_res.winter_highway_range_km:.0f} km): "
            f"richiede pianificazione nei viaggi lunghi."
        )

    # Determine Rating
    confidence = 0.85
    if savings > Decimal(4000) and (op_be_years is not None and op_be_years <= horizon * 0.75):
        rating = RecommendationRating.STRONG_BUY
        summary = (
            f"Fortemente consigliato! Sostituire {current_vehicle.brand} {current_vehicle.model} con "
            f"{candidate_vehicle.brand} {candidate_vehicle.model} dovrebbe far risparmiare {_format_eur(savings)} "
            f"in {horizon} anni. Il break-even si raggiunge in circa {_format_duration(op_be_years)}."
        )
    elif savings > Decimal(1000) and (op_be_years is not None and op_be_years <= horizon):
        rating = RecommendationRating.BUY
        summary = (
            f"Decisione finanziariamente vantaggiosa. Il passaggio fa risparmiare circa {_format_eur(savings)} "
            f"in {horizon} anni, con break-even raggiunto in circa {_format_duration(op_be_years)}."
        )
    elif savings >= Decimal(-1000) and savings <= Decimal(1000):
        rating = RecommendationRating.MAYBE
        summary = (
            f"Decisione economicamente neutra. I costi totali in {horizon} anni sono quasi equivalenti "
            f"(differenza di {_format_eur(savings)}). La scelta dipende dalle preferenze personali di guida."
        )
    elif savings < Decimal(-1000) and candidate_tco.net_purchase_cost > current_tco.net_purchase_cost:
        rating = RecommendationRating.KEEP_CURRENT
        summary = (
            f"Dal punto di vista finanziario conviene mantenere l’attuale {current_vehicle.brand} {current_vehicle.model}. "
            f"L’EV candidata comporta costi totali superiori di {_format_eur(abs(savings))} nel periodo di {horizon} anni."
        )
    else:
        rating = RecommendationRating.AVOID
        summary = "Passare a questo veicolo candidato è economicamente svantaggioso con l’attuale profilo di utilizzo."

    risk_score = min(100, max(0, risk_score))
    risk_lvl = RiskLevel.LOW if risk_score < 30 else (RiskLevel.MEDIUM if risk_score < 60 else RiskLevel.HIGH)

    # Explanations
    explanations.append(
        ValueExplanation(
            value=f"{_format_eur(candidate_tco.tco_per_km, 4)} / km",
            formula="TCO totale candidato / Km totali percorsi",
            source=ValueSource.FACT,
            notes=f"Costo al chilometro · rispetto a {_format_eur(current_tco.tco_per_km, 4)} / km dell’auto attuale.",
        )
    )
    explanations.append(
        ValueExplanation(
            value=f"{range_res.mixed_range_km:.0f} km",
            formula="Batteria utile kWh / Consumo ponderato * 100",
            source=ValueSource.ESTIMATE,
            notes="Autonomia reale stimata · profilo di guida misto.",
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
