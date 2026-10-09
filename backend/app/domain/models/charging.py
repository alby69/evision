from decimal import Decimal

from pydantic import BaseModel, Field


class ChargingProfile(BaseModel):
    home_charging_percentage: float = Field(default=0.80, ge=0, le=1.0)
    public_ac_charging_percentage: float = Field(default=0.10, ge=0, le=1.0)
    public_dc_charging_percentage: float = Field(default=0.10, ge=0, le=1.0)

    home_energy_price: Decimal = Field(default=Decimal("0.25"), ge=Decimal(0), description="EUR per kWh home tariff")
    public_ac_energy_price: Decimal = Field(default=Decimal("0.50"), ge=Decimal(0), description="EUR per kWh public AC")
    public_dc_energy_price: Decimal = Field(default=Decimal("0.75"), ge=Decimal(0), description="EUR per kWh public DC fast")

    charging_losses_percentage: float = Field(default=0.10, ge=0, le=0.5, description="Charging losses (10% = 0.10)")

    def validate_percentages(self) -> bool:
        total = self.home_charging_percentage + self.public_ac_charging_percentage + self.public_dc_charging_percentage
        return abs(total - 1.0) < 0.001

class FuelProfile(BaseModel):
    diesel_price: Decimal = Field(default=Decimal("1.80"), ge=Decimal(0))
    petrol_price: Decimal = Field(default=Decimal("1.85"), ge=Decimal(0))
    lpg_price: Decimal = Field(default=Decimal("0.75"), ge=Decimal(0))
    cng_price: Decimal = Field(default=Decimal("1.35"), ge=Decimal(0))

    annual_fuel_price_growth: float = Field(default=0.03, description="Expected annual fuel price inflation rate (e.g., 0.03 = +3%/year)")
