from decimal import Decimal
import pytest

from app.domain.engine.break_even_calculator import calculate_break_even
from app.domain.engine.recommendation_engine import (
    _format_duration,
    _format_eur,
    generate_decision_recommendation,
)
from app.domain.engine.tco_calculator import calculate_vehicle_tco
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.enums import FuelType, RecommendationRating, VehicleType
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


def test_format_duration_and_eur():
    assert _format_duration(1.0) == "1 anno"
    assert _format_duration(2.0) == "2 anni"
    assert _format_duration(0.5) == "6 mesi"
    assert _format_duration(0.08) == "1 mese"
    assert _format_duration(1.5) == "1 anno e 6 mesi"

    assert _format_eur(1234.56) == "€1.234,56"
    assert _format_eur(-500.0) == "-€500,00"


@pytest.mark.parametrize(
    "annual_km, home_charging_pct, purchase_price",
    [
        (25000, 0.90, 20000),
        (15000, 0.80, 25000),
        (10000, 0.50, 30000),
        (5000, 0.20, 45000),
        (2000, 0.10, 60000),
    ],
)
def test_recommendation_ratings(annual_km, home_charging_pct, purchase_price):
    curr_car = Vehicle(
        brand="Fiat",
        model="Panda",
        year=2018,
        vehicle_type=VehicleType.PETROL,
        fuel_type=FuelType.PETROL,
        purchase_price=Decimal("12000"),
        current_value=Decimal("4000"),
        urban_consumption=7.0,
        extraurban_consumption=5.0,
        highway_consumption=6.0,
    )
    cand_car = Vehicle(
        brand="MG",
        model="MG4",
        year=2024,
        vehicle_type=VehicleType.BEV,
        fuel_type=FuelType.ELECTRICITY,
        purchase_price=Decimal(str(purchase_price)),
        usable_battery_capacity=64.0,
        wltp_range=450.0,
        urban_consumption=14.0,
        extraurban_consumption=16.0,
        highway_consumption=20.0,
    )

    usage = UsageProfile(annual_km=annual_km)
    charging = ChargingProfile(
        home_charging_percentage=home_charging_pct,
        public_ac_charging_percentage=(1.0 - home_charging_pct) / 2,
        public_dc_charging_percentage=(1.0 - home_charging_pct) / 2,
    )
    fuel = FuelProfile(petrol_price=Decimal("1.85"), diesel_price=Decimal("1.80"))
    ownership = OwnershipScenario(horizon_years=5)

    curr_tco = calculate_vehicle_tco(curr_car, usage, charging, fuel, ownership, already_owned=True)
    cand_tco = calculate_vehicle_tco(cand_car, usage, charging, fuel, ownership)
    be = calculate_break_even(curr_tco, cand_tco, usage.annual_km)

    rec = generate_decision_recommendation(
        curr_car, cand_car, curr_tco, cand_tco, be, usage, charging, fuel, ownership
    )
    assert rec.rating in [r.value for r in RecommendationRating]


def test_zero_interest_rate_tco():
    car = Vehicle(
        brand="Tesla",
        model="Model 3",
        year=2024,
        vehicle_type=VehicleType.BEV,
        fuel_type=FuelType.ELECTRICITY,
        purchase_price=Decimal("40000"),
        usable_battery_capacity=60.0,
        wltp_range=500.0,
        urban_consumption=13.0,
        extraurban_consumption=15.0,
        highway_consumption=18.0,
    )
    usage = UsageProfile(annual_km=15000)
    charging = ChargingProfile()
    fuel = FuelProfile()
    ownership = OwnershipScenario(horizon_years=5, is_financed=True, interest_rate=0.0)

    tco = calculate_vehicle_tco(car, usage, charging, fuel, ownership)
    assert tco.total_financing_interest == Decimal("0.00")
    assert tco.total_tco > Decimal("0")


def test_tco_alternative_fuel_types():
    for fuel_enum, vtype in [
        (FuelType.DIESEL, VehicleType.DIESEL),
        (FuelType.LPG, VehicleType.LPG),
        (FuelType.CNG, VehicleType.CNG),
    ]:
        car = Vehicle(
            brand="Test",
            model="AltFuel",
            year=2020,
            vehicle_type=vtype,
            fuel_type=fuel_enum,
            purchase_price=Decimal("20000"),
            urban_consumption=6.0,
            extraurban_consumption=4.5,
            highway_consumption=5.5,
        )
        usage = UsageProfile(annual_km=10000)
        charging = ChargingProfile()
        fuel = FuelProfile()
        ownership = OwnershipScenario(horizon_years=3)

        tco = calculate_vehicle_tco(car, usage, charging, fuel, ownership)
        assert tco.total_energy_fuel_cost > Decimal("0")
