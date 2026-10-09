from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.models.enums import FuelType, ValueSource, VehicleType


class Vehicle(BaseModel):
    id: str | None = None
    brand: str
    model: str
    version: str | None = ""
    year: int
    registration_date: str | None = None

    vehicle_type: VehicleType
    fuel_type: FuelType

    purchase_price: Decimal = Field(gt=Decimal(0), description="Purchase or valuation price in EUR")
    current_value: Decimal = Field(default=Decimal(0), description="Current trade-in / market value in EUR")
    annual_tax: Decimal = Field(default=Decimal(0), description="Annual road tax (bollo) in EUR")

    # Consumption
    urban_consumption: float = Field(gt=0, description="Urban consumption (kWh/100km or l/100km)")
    extraurban_consumption: float = Field(gt=0, description="Extraurban consumption")
    highway_consumption: float = Field(gt=0, description="Highway consumption")

    # BEV / EV Specifics
    battery_capacity: float | None = Field(default=None, description="Gross battery capacity in kWh")
    usable_battery_capacity: float | None = Field(default=None, description="Usable battery capacity in kWh")
    wltp_range: float | None = Field(default=None, description="WLTP range in km")
    charging_ac_power: float | None = Field(default=None, description="AC charging power in kW")
    charging_dc_power: float | None = Field(default=None, description="DC fast charging power in kW")

    # Fixed annual maintenance & running costs
    maintenance_cost_per_year: Decimal = Field(default=Decimal(0), description="Expected annual routine maintenance cost")
    insurance_cost_per_year: Decimal = Field(default=Decimal(0), description="Expected annual insurance cost")
    tire_cost_per_year: Decimal = Field(default=Decimal(0), description="Expected annual tire cost")

    # Value retention / residual
    expected_residual_value_ratio: float = Field(default=0.45, description="Expected residual ratio after default horizon")
    ev_depreciation_modifier: float = Field(default=1.0, description="Modifier for EV depreciation rate")

    source_type: ValueSource = ValueSource.USER_INPUT

    @property
    def is_ev(self) -> bool:
        return self.vehicle_type in (VehicleType.BEV, VehicleType.PHEV)
