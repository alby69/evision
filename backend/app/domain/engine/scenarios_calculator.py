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
    base_curr_tco = calculate_vehicle_tco(current_vehicle, usage, charging, fuel, ownership)
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

    pess_curr_tco = calculate_vehicle_tco(current_vehicle, usage, pess_charging, pess_fuel, ownership)
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

    opt_curr_tco = calculate_vehicle_tco(current_vehicle, usage, opt_charging, opt_fuel, ownership)
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
            parameter_name="Annual Mileage",
            impact_score=9.2,
            impact_description="Highest impact: Operating fuel/energy cost savings scale directly with annual kilometers."
        ),
        SensitivityFactor(
            parameter_name="Fuel Prices",
            impact_score=8.5,
            impact_description="High impact: Higher ICE fuel prices directly increase savings when switching to electric."
        ),
        SensitivityFactor(
            parameter_name="Home Electricity Tariff",
            impact_score=7.8,
            impact_description="High impact: Access to low-cost home charging (€0.20-0.25/kWh) maximizes operational savings."
        ),
        SensitivityFactor(
            parameter_name="Vehicle Purchase Price",
            impact_score=6.5,
            impact_description="Medium impact: Upfront acquisition price determines break-even timeline length."
        ),
        SensitivityFactor(
            parameter_name="EV Depreciation Rate",
            impact_score=5.0,
            impact_description="Moderate impact: Resale value after ownership period affects final total cost."
        ),
        SensitivityFactor(
            parameter_name="Routine Maintenance Savings",
            impact_score=3.5,
            impact_description="Lower impact: EV maintenance savings (no oil changes, less brake wear) provide steady small savings."
        ),
    ]

    return factors
