from decimal import Decimal

import pytest

from app.domain.engine.break_even_calculator import calculate_break_even
from app.domain.engine.range_calculator import (
    calculate_battery_degradation,
    calculate_real_world_range,
)
from app.domain.engine.recommendation_engine import generate_decision_recommendation
from app.domain.engine.scenarios_calculator import calculate_sensitivity_factors, simulate_scenarios
from app.domain.engine.tco_calculator import calculate_vehicle_tco
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.enums import FinancingType, FuelType, VehicleType
from app.domain.models.ownership import FinancingProfile, OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


@pytest.fixture
def current_diesel_car() -> Vehicle:
    return Vehicle(
        id="v-honda-crv",
        brand="Honda",
        model="CR-V",
        version="1.6 i-DTEC",
        year=2016,
        vehicle_type=VehicleType.DIESEL,
        fuel_type=FuelType.DIESEL,
        purchase_price=Decimal(12000),
        current_value=Decimal(5000),
        annual_tax=Decimal(250),
        urban_consumption=5.5,
        extraurban_consumption=4.5,
        highway_consumption=6.0,
        maintenance_cost_per_year=Decimal(700),
        insurance_cost_per_year=Decimal(600),
        tire_cost_per_year=Decimal(150),
    )

@pytest.fixture
def candidate_zoe_ev() -> Vehicle:
    return Vehicle(
        id="v-renault-zoe",
        brand="Renault",
        model="Zoe",
        version="R110 52kWh",
        year=2022,
        vehicle_type=VehicleType.BEV,
        fuel_type=FuelType.ELECTRICITY,
        purchase_price=Decimal(12900),
        annual_tax=Decimal(0),  # Exempt in many regions
        urban_consumption=13.0,
        extraurban_consumption=15.0,
        highway_consumption=20.0,
        battery_capacity=52.0,
        usable_battery_capacity=52.0,
        wltp_range=395.0,
        maintenance_cost_per_year=Decimal(250),
        insurance_cost_per_year=Decimal(500),
        tire_cost_per_year=Decimal(120),
    )

@pytest.fixture
def usage_25k() -> UsageProfile:
    return UsageProfile(
        annual_km=25000.0,
        city_percentage=0.40,
        extraurban_percentage=0.40,
        highway_percentage=0.20,
        winter_multiplier=1.20,
    )

@pytest.fixture
def standard_charging() -> ChargingProfile:
    return ChargingProfile(
        home_charging_percentage=0.80,
        public_ac_charging_percentage=0.10,
        public_dc_charging_percentage=0.10,
        home_energy_price=Decimal("0.25"),
        public_ac_energy_price=Decimal("0.45"),
        public_dc_energy_price=Decimal("0.75"),
        charging_losses_percentage=0.10,
    )

@pytest.fixture
def standard_fuel() -> FuelProfile:
    return FuelProfile(
        diesel_price=Decimal("1.80"),
        petrol_price=Decimal("1.85"),
        annual_fuel_price_growth=0.03,
    )

@pytest.fixture
def ownership_5yr() -> OwnershipScenario:
    return OwnershipScenario(
        horizon_years=5,
        trade_in_value=Decimal(5000),
        incentive_amount=Decimal(0),
        financing=FinancingProfile(
            financing_type=FinancingType.CASH
        ),
    )

def test_tco_calculation_diesel(current_diesel_car, usage_25k, standard_charging, standard_fuel, ownership_5yr):
    tco_res = calculate_vehicle_tco(current_diesel_car, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    assert tco_res.horizon_years == 5
    assert tco_res.total_tco > Decimal(0)
    assert tco_res.total_energy_fuel_cost > Decimal(0)
    assert tco_res.tco_per_km > Decimal(0)
    assert len(tco_res.yearly_breakdown) == 5

def test_tco_calculation_ev(candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr):
    tco_res = calculate_vehicle_tco(candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    assert tco_res.horizon_years == 5
    assert tco_res.total_tco > Decimal(0)
    assert tco_res.total_energy_fuel_cost > Decimal(0)
    assert tco_res.net_purchase_cost == Decimal(7900)  # 12900 - 5000 trade in

def test_tco_calculation_leasing(candidate_zoe_ev, usage_25k, standard_charging, standard_fuel):
    leasing_ownership = OwnershipScenario(
        horizon_years=3,
        trade_in_value=Decimal(2000),
        incentive_amount=Decimal(1000),
        financing=FinancingProfile(
            financing_type=FinancingType.LEASING,
            down_payment=Decimal(1500),
            lease_monthly_fee=Decimal(250),
            duration_months=36,
            residual_value_percentage=40.0,
        ),
    )
    tco_res = calculate_vehicle_tco(candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, leasing_ownership)
    assert tco_res.horizon_years == 3
    assert tco_res.total_tco > Decimal(0)
    assert tco_res.total_financing_interest >= Decimal(0)

def test_break_even_calculation(current_diesel_car, candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr):
    curr_tco = calculate_vehicle_tco(current_diesel_car, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    cand_tco = calculate_vehicle_tco(candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr)

    be = calculate_break_even(curr_tco, cand_tco, usage_25k.annual_km)
    assert be.annual_operational_savings > Decimal(0)
    assert be.operational_break_even_years is not None
    assert be.operational_break_even_years > 0.0

def test_range_and_battery_degradation(candidate_zoe_ev, usage_25k):
    range_res = calculate_real_world_range(candidate_zoe_ev, usage_25k)
    assert range_res.usable_battery_kwh == 52.0
    assert range_res.urban_range_km > range_res.highway_range_km
    assert range_res.winter_highway_range_km < range_res.highway_range_km

    deg_res = calculate_battery_degradation(candidate_zoe_ev, usage_25k, 5)
    assert deg_res.initial_capacity_kwh == 52.0
    assert deg_res.yearly_capacities_kwh[5] < deg_res.initial_capacity_kwh

def test_scenarios_and_recommendation(current_diesel_car, candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr):
    scenarios = simulate_scenarios(current_diesel_car, candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    assert scenarios.optimistic_tco < scenarios.pessimistic_tco

    factors = calculate_sensitivity_factors(current_diesel_car, candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    assert len(factors) > 0

    curr_tco = calculate_vehicle_tco(current_diesel_car, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    cand_tco = calculate_vehicle_tco(candidate_zoe_ev, usage_25k, standard_charging, standard_fuel, ownership_5yr)
    be = calculate_break_even(curr_tco, cand_tco, usage_25k.annual_km)

    rec = generate_decision_recommendation(
        current_diesel_car, candidate_zoe_ev, curr_tco, cand_tco, be, usage_25k, standard_charging, standard_fuel, ownership_5yr
    )
    assert rec.rating in ["STRONG_BUY", "BUY", "MAYBE", "KEEP_CURRENT", "AVOID"]
    assert 0 <= rec.risk_score <= 100
