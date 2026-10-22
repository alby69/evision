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


class CarFacetValue(BaseModel):
    value: int | str
    count: int


class ParsedListingRequest(BaseModel):
    url: str = Field(min_length=1, description="URL of the vehicle listing (AutoScout24, Subito, etc.)")


class ParsedListingResponse(BaseModel):
    url: str
    make: str
    model: str
    year: int | None = None
    price_eur: float | None = None
    mileage_km: int | None = None
    fuel_type: str | None = None
    raw_title: str | None = None


class CarCatalogItem(BaseModel):
    make: str
    model: str
    year: int | None = None
    fuel_type: str | None = Field(default=None, description="Raw fuel type from the catalog (gas, diesel, ...)")
    transmission: str | None = None
    drive: str | None = None
    cylinders: int | None = None
    displacement: float | None = Field(default=None, description="Engine displacement in liters")
    car_class: str | None = None


class VehicleValuationRequest(BaseModel):
    make: str = Field(min_length=1, description="Vehicle make/brand")
    model: str = Field(min_length=1, description="Vehicle model")
    year: int | None = Field(default=None, ge=1950, le=2100, description="Registration year")
    mileage: int | None = Field(default=None, ge=0, description="Current odometer in km (optional)")
    fuel_type: str | None = Field(default=None, description="Fuel type, when known")
    source: str | None = Field(default=None, description="Override the marketplace slug to query")


class ValuationComparable(BaseModel):
    title: str
    year: int | None = None
    mileage: int | None = None
    price_eur: float
    location: str | None = None
    url: str | None = None


class VehicleValuationResponse(BaseModel):
    estimated_value: float = Field(description="Estimated market value in EUR")
    trade_in_value: float = Field(description="Estimated dealer trade-in value in EUR")
    low_estimate: float
    high_estimate: float
    currency: str = "EUR"
    sample_size: int
    source: str
    confidence: str = Field(description="low | medium | high")
    comparables: list[ValuationComparable] = Field(default_factory=list)


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


# My Garage Schemas
class SavedVehicleCreate(BaseModel):
    name: str = Field(min_length=1, description="Name for vehicle in garage")
    is_default: bool = False
    vehicle_data: Vehicle


class SavedVehicleUpdate(BaseModel):
    name: str | None = None
    is_default: bool | None = None
    vehicle_data: Vehicle | None = None


class SavedVehicleResponse(BaseModel):
    id: str
    name: str
    is_default: bool
    vehicle_data: Vehicle
    created_at: str
    updated_at: str


# Multi-Car Comparison Schemas
class CandidateComparison(BaseModel):
    candidate_vehicle: Vehicle
    candidate_tco: VehicleTCOResult
    break_even: BreakEvenResult
    candidate_range: RealWorldRangeResult
    candidate_battery_degradation: BatteryDegradationResult
    scenarios: ScenarioResult
    sensitivity: list[SensitivityFactor]
    recommendation: DecisionRecommendation


class ComparativeAnalysisRequest(BaseModel):
    title: str | None = "Confronto Multi-Auto EV"
    current_vehicle_id: str | None = None
    current_vehicle: Vehicle | None = None
    candidate_vehicles: list[Vehicle] = Field(min_length=1)
    usage: UsageProfile = Field(default_factory=UsageProfile)
    charging: ChargingProfile = Field(default_factory=ChargingProfile)
    fuel: FuelProfile = Field(default_factory=FuelProfile)
    ownership: OwnershipScenario = Field(default_factory=OwnershipScenario)


class ComparativeAnalysisResponse(BaseModel):
    id: str | None = None
    title: str
    current_vehicle: Vehicle
    current_tco: VehicleTCOResult
    usage: UsageProfile
    charging: ChargingProfile
    fuel: FuelProfile
    ownership: OwnershipScenario
    comparisons: list[CandidateComparison]
    created_at: str | None = None
    ai_summary_placeholder: str | None = Field(default=None, description="Placeholder for future LLM-generated comparative summary")


class SavedAnalysisSummary(BaseModel):
    id: str
    title: str
    current_vehicle_name: str
    candidate_count: int
    created_at: str


# AI Advisor Schemas
class AIExplainResponse(BaseModel):
    ai_summary: str


class QnAnessRequest(BaseModel):
    question: str = Field(min_length=1, description="Question asked by the user regarding their analysis")


class QnAnessResponse(BaseModel):
    answer: str
