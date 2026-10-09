
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
