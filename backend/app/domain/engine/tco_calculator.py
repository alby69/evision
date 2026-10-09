from decimal import ROUND_HALF_UP, Decimal

from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.enums import FinancingType, FuelType
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.results import VehicleTCOResult, YearlyCostBreakdown
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


def _round_dec(val: Decimal, places: int = 2) -> Decimal:
    fmt = "0." + "0" * places if places > 0 else "0"
    return val.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)


def calculate_vehicle_tco(
    vehicle: Vehicle,
    usage: UsageProfile,
    charging: ChargingProfile,
    fuel: FuelProfile,
    ownership: OwnershipScenario,
) -> VehicleTCOResult:
    # 1. Net Purchase Price
    gross_price = vehicle.purchase_price
    incentive = ownership.incentive_amount
    trade_in = ownership.trade_in_value

    net_purchase_cost = max(Decimal(0), gross_price - incentive - trade_in)

    # 2. Financing Calculation
    financing = ownership.financing
    annual_interest_payment = Decimal(0)

    if financing.financing_type in (FinancingType.LOAN, FinancingType.FINANCING, FinancingType.LEASING):
        principal = financing.financed_amount if financing.financed_amount > 0 else net_purchase_cost - financing.down_payment
        if principal > 0 and financing.duration_months > 0:
            rate = Decimal(str(financing.interest_rate_annual)) / Decimal(12)
            n_months = financing.duration_months
            if rate > 0:
                monthly = (principal * rate * ((1 + rate) ** n_months)) / (((1 + rate) ** n_months) - 1)
                total_financed_payments = monthly * n_months + financing.final_balloon_payment
                total_interest = total_financed_payments - principal
                annual_interest_payment = total_interest / Decimal(ownership.horizon_years)
            else:
                total_interest = Decimal(0)
                annual_interest_payment = Decimal(0)

    # 3. Energy / Fuel Cost per year calculation
    weighted_consumption = (
        usage.city_percentage * vehicle.urban_consumption +
        usage.extraurban_percentage * vehicle.extraurban_consumption +
        usage.highway_percentage * vehicle.highway_consumption
    )

    yearly_breakdowns: list[YearlyCostBreakdown] = []
    cumulative_running = Decimal(0)

    total_energy_fuel = Decimal(0)
    total_maintenance = Decimal(0)
    total_insurance = Decimal(0)
    total_taxes = Decimal(0)
    total_tires = Decimal(0)
    total_financing_interest = annual_interest_payment * Decimal(ownership.horizon_years)

    yearly_depreciation_rates = [0.20, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04]

    current_market_val = vehicle.purchase_price

    for y in range(1, ownership.horizon_years + 1):
        if vehicle.is_ev:
            weighted_kwh_per_100km = weighted_consumption * usage.winter_multiplier
            total_kwh_needed = (usage.annual_km / 100.0) * weighted_kwh_per_100km
            total_kwh_purchased = total_kwh_needed * (1.0 + charging.charging_losses_percentage)

            avg_energy_rate = (
                Decimal(str(charging.home_charging_percentage)) * charging.home_energy_price +
                Decimal(str(charging.public_ac_charging_percentage)) * charging.public_ac_energy_price +
                Decimal(str(charging.public_dc_charging_percentage)) * charging.public_dc_energy_price
            )

            year_energy_fuel = Decimal(str(total_kwh_purchased)) * avg_energy_rate
        else:
            growth_factor = (1.0 + fuel.annual_fuel_price_growth) ** (y - 1)
            if vehicle.fuel_type == FuelType.DIESEL:
                unit_price = fuel.diesel_price * Decimal(str(growth_factor))
            elif vehicle.fuel_type == FuelType.LPG:
                unit_price = fuel.lpg_price * Decimal(str(growth_factor))
            elif vehicle.fuel_type == FuelType.CNG:
                unit_price = fuel.cng_price * Decimal(str(growth_factor))
            else:
                unit_price = fuel.petrol_price * Decimal(str(growth_factor))

            liters_needed = (usage.annual_km / 100.0) * weighted_consumption
            year_energy_fuel = Decimal(str(liters_needed)) * unit_price

        year_maint = vehicle.maintenance_cost_per_year
        year_ins = vehicle.insurance_cost_per_year
        year_tax = vehicle.annual_tax
        year_tires = vehicle.tire_cost_per_year

        dep_idx = min(y - 1, len(yearly_depreciation_rates) - 1)
        base_dep_rate = yearly_depreciation_rates[dep_idx]
        if vehicle.is_ev:
            base_dep_rate *= vehicle.ev_depreciation_modifier

        year_depreciation = current_market_val * Decimal(str(base_dep_rate))
        current_market_val = max(Decimal(0), current_market_val - year_depreciation)

        year_running_total = (
            year_energy_fuel +
            annual_interest_payment +
            year_maint +
            year_ins +
            year_tax +
            year_tires
        )

        cumulative_running += year_running_total

        total_energy_fuel += year_energy_fuel
        total_maintenance += year_maint
        total_insurance += year_ins
        total_taxes += year_tax
        total_tires += year_tires

        yearly_breakdowns.append(
            YearlyCostBreakdown(
                year=y,
                energy_or_fuel_cost=_round_dec(year_energy_fuel, 2),
                financing_cost=_round_dec(annual_interest_payment, 2),
                maintenance_cost=_round_dec(year_maint, 2),
                insurance_cost=_round_dec(year_ins, 2),
                tax_cost=_round_dec(year_tax, 2),
                tire_cost=_round_dec(year_tires, 2),
                depreciation=_round_dec(year_depreciation, 2),
                total_year_cost=_round_dec(year_running_total + year_depreciation, 2),
                cumulative_cost=_round_dec(cumulative_running, 2),
                residual_value=_round_dec(current_market_val, 2),
            )
        )

    final_residual = current_market_val
    total_tco = net_purchase_cost + cumulative_running - final_residual

    total_km = usage.annual_km * ownership.horizon_years
    tco_per_year = total_tco / Decimal(ownership.horizon_years)
    tco_per_month = total_tco / Decimal(ownership.horizon_years * 12)
    tco_per_km = total_tco / Decimal(str(total_km)) if total_km > 0 else Decimal(0)

    vehicle_name = f"{vehicle.brand} {vehicle.model}"
    if vehicle.version:
        vehicle_name += f" ({vehicle.version})"

    return VehicleTCOResult(
        vehicle_id=vehicle.id,
        vehicle_name=vehicle_name,
        horizon_years=ownership.horizon_years,
        net_purchase_cost=_round_dec(net_purchase_cost, 2),
        total_tco=_round_dec(total_tco, 2),
        tco_per_year=_round_dec(tco_per_year, 2),
        tco_per_month=_round_dec(tco_per_month, 2),
        tco_per_km=_round_dec(tco_per_km, 4),
        yearly_breakdown=yearly_breakdowns,
        residual_value_end=_round_dec(final_residual, 2),
        total_energy_fuel_cost=_round_dec(total_energy_fuel, 2),
        total_maintenance_cost=_round_dec(total_maintenance, 2),
        total_insurance_cost=_round_dec(total_insurance, 2),
        total_taxes=_round_dec(total_taxes, 2),
        total_financing_interest=_round_dec(total_financing_interest, 2),
    )
