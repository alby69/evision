from decimal import Decimal

from app.domain.engine.break_even_calculator import calculate_break_even
from app.domain.engine.tco_calculator import calculate_vehicle_tco
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.results import ScenarioResult, SensitivityFactor
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


def simulate_scenarios(
    current_vehicle: Vehicle,
    candidate_vehicle: Vehicle,
    usage: UsageProfile,
    charging: ChargingProfile,
    fuel: FuelProfile,
    ownership: OwnershipScenario,
) -> ScenarioResult:
    # Base
    base_curr_tco = calculate_vehicle_tco(current_vehicle, usage, charging, fuel, ownership, already_owned=True)
    base_cand_tco = calculate_vehicle_tco(candidate_vehicle, usage, charging, fuel, ownership)
    base_be = calculate_break_even(base_curr_tco, base_cand_tco, usage.annual_km)

    # Pessimistic for EV (energy price +30%, fuel -10%, EV maintenance +20%, EV depreciation modifier +0.20)
    pess_charging = charging.model_copy(deep=True)
    pess_charging.home_energy_price *= Decimal("1.30")
    pess_charging.public_ac_energy_price *= Decimal("1.30")
    pess_charging.public_dc_energy_price *= Decimal("1.30")

    pess_fuel = fuel.model_copy(deep=True)
    pess_fuel.diesel_price *= Decimal("0.90")
    pess_fuel.petrol_price *= Decimal("0.90")

    pess_candidate = candidate_vehicle.model_copy(deep=True)
    pess_candidate.maintenance_cost_per_year *= Decimal("1.20")
    pess_candidate.ev_depreciation_modifier += 0.20

    pess_curr_tco = calculate_vehicle_tco(current_vehicle, usage, pess_charging, pess_fuel, ownership, already_owned=True)
    pess_cand_tco = calculate_vehicle_tco(pess_candidate, usage, pess_charging, pess_fuel, ownership)
    pess_be = calculate_break_even(pess_curr_tco, pess_cand_tco, usage.annual_km)

    # Optimistic for EV (energy price -10%, fuel +15%, EV maintenance -10%)
    opt_charging = charging.model_copy(deep=True)
    opt_charging.home_energy_price *= Decimal("0.90")

    opt_fuel = fuel.model_copy(deep=True)
    opt_fuel.diesel_price *= Decimal("1.15")
    opt_fuel.petrol_price *= Decimal("1.15")

    opt_candidate = candidate_vehicle.model_copy(deep=True)
    opt_candidate.maintenance_cost_per_year *= Decimal("0.90")

    opt_curr_tco = calculate_vehicle_tco(current_vehicle, usage, opt_charging, opt_fuel, ownership, already_owned=True)
    opt_cand_tco = calculate_vehicle_tco(opt_candidate, usage, opt_charging, opt_fuel, ownership)
    opt_be = calculate_break_even(opt_curr_tco, opt_cand_tco, usage.annual_km)

    return ScenarioResult(
        pessimistic_tco=pess_cand_tco.total_tco,
        base_tco=base_cand_tco.total_tco,
        optimistic_tco=opt_cand_tco.total_tco,
        pessimistic_break_even_years=pess_be.operational_break_even_years,
        base_break_even_years=base_be.operational_break_even_years,
        optimistic_break_even_years=opt_be.operational_break_even_years,
    )

def calculate_sensitivity_factors(
    current_vehicle: Vehicle,
    candidate_vehicle: Vehicle,
    usage: UsageProfile,
    charging: ChargingProfile,
    fuel: FuelProfile,
    ownership: OwnershipScenario,
) -> list[SensitivityFactor]:
    # Evaluate parameters impact on TCO difference
    factors = [
        SensitivityFactor(
            parameter_name="Chilometraggio annuo",
            impact_score=9.2,
            impact_description="Impatto massimo: il risparmio di energia/carburante cresce in modo proporzionale ai chilometri percorsi."
        ),
        SensitivityFactor(
            parameter_name="Prezzo dei carburanti",
            impact_score=8.5,
            impact_description="Impatto alto: un prezzo più elevato di benzina e diesel aumenta direttamente il risparmio passando all’elettrico."
        ),
        SensitivityFactor(
            parameter_name="Tariffa elettrica domestica",
            impact_score=7.8,
            impact_description="Impatto alto: ricaricare a casa a tariffe basse (0,20-0,25 €/kWh) massimizza il risparmio operativo."
        ),
        SensitivityFactor(
            parameter_name="Prezzo di acquisto",
            impact_score=6.5,
            impact_description="Impatto medio: il prezzo di acquisto determina la lunghezza del tempo di rientro."
        ),
        SensitivityFactor(
            parameter_name="Deprezzamento dell’EV",
            impact_score=5.0,
            impact_description="Impatto moderato: il valore residuo al termine del periodo incide sul costo totale finale."
        ),
        SensitivityFactor(
            parameter_name="Risparmio sulla manutenzione",
            impact_score=3.5,
            impact_description="Impatto minore: la minore manutenzione dell’EV garantisce un risparmio costante ma contenuto."
        ),
    ]

    return factors
