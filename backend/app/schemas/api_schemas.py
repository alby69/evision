
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


class EVCatalogItem(BaseModel):
    make: str
    model: str
    year_start: int | None = None
    year: int | None = None
    battery_capacity: float | None = Field(default=None, description="Gross battery capacity in kWh")
    battery_useable_capacity: float | None = Field(default=None, description="Usable battery capacity in kWh")
    electric_range: float | None = Field(default=None, description="Electric range in km (WLTP or estimated)")
    charge_power_max: float | None = Field(default=None, description="Max charging power in kW")
    vehicle_consumption: float | None = Field(default=None, description="Average consumption in kWh/100km")
    estimated_price_eur: float | None = Field(default=None, description="Estimated purchase price in EUR")

class TCORequest(BaseModel):
    vehicle: Vehicle
    usage: UsageProfile
    charging: ChargingProfile
    fuel: FuelProfile
    ownership: OwnershipScenario

class BreakEvenRequest(BaseModel):
    current_vehicle: Vehicle
    candidate_vehicle: Vehicle
    usage: UsageProfile
    charging: ChargingProfile
    fuel: FuelProfile
    ownership: OwnershipScenario

class FullAnalysisRequest(BaseModel):
    title: str | None = "EV Replacement Decision Analysis"
    current_vehicle: Vehicle
    candidate_vehicle: Vehicle
    usage: UsageProfile = Field(default_factory=UsageProfile)
    charging: ChargingProfile = Field(default_factory=ChargingProfile)
    fuel: FuelProfile = Field(default_factory=FuelProfile)
    ownership: OwnershipScenario = Field(default_factory=OwnershipScenario)

class FullAnalysisResponse(BaseModel):
    id: str | None = None
    title: str
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
    sensitivity: list[SensitivityFactor]
    recommendation: DecisionRecommendation
