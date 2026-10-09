from decimal import Decimal

from pydantic import BaseModel

from app.domain.models.enums import ValueSource


class ValueExplanation(BaseModel):
    value: str
    formula: str
    source: ValueSource
    notes: str | None = None

class YearlyCostBreakdown(BaseModel):
    year: int
    energy_or_fuel_cost: Decimal
    financing_cost: Decimal
    maintenance_cost: Decimal
    insurance_cost: Decimal
    tax_cost: Decimal
    tire_cost: Decimal
    depreciation: Decimal
    total_year_cost: Decimal
    cumulative_cost: Decimal
    residual_value: Decimal

class VehicleTCOResult(BaseModel):
    vehicle_id: str | None = None
    vehicle_name: str
    horizon_years: int
    net_purchase_cost: Decimal
    total_tco: Decimal
    tco_per_year: Decimal
    tco_per_month: Decimal
    tco_per_km: Decimal
    yearly_breakdown: list[YearlyCostBreakdown]
    residual_value_end: Decimal
    total_energy_fuel_cost: Decimal
    total_maintenance_cost: Decimal
    total_insurance_cost: Decimal
    total_taxes: Decimal
    total_financing_interest: Decimal

class RealWorldRangeResult(BaseModel):
    usable_battery_kwh: float
    urban_range_km: float
    extraurban_range_km: float
    highway_range_km: float
    mixed_range_km: float
    winter_highway_range_km: float

class BatteryDegradationResult(BaseModel):
    initial_capacity_kwh: float
    yearly_capacities_kwh: dict[int, float]
    yearly_ranges_km: dict[int, float]

class BreakEvenResult(BaseModel):
    operational_break_even_years: float | None = None
    operational_break_even_months: float | None = None
    operational_break_even_km: float | None = None

    total_ownership_break_even_years: float | None = None
    total_ownership_break_even_months: float | None = None
    total_ownership_break_even_km: float | None = None

    cumulative_savings_over_horizon: Decimal = Decimal(0)
    annual_operational_savings: Decimal = Decimal(0)
    monthly_operational_savings: Decimal = Decimal(0)
    cost_per_km_diff: Decimal = Decimal(0)

class ScenarioResult(BaseModel):
    pessimistic_tco: Decimal
    base_tco: Decimal
    optimistic_tco: Decimal
    pessimistic_break_even_years: float | None
    base_break_even_years: float | None
    optimistic_break_even_years: float | None

class SensitivityFactor(BaseModel):
    parameter_name: str
    impact_score: float  # 0.0 to 10.0
    impact_description: str

class DecisionRecommendation(BaseModel):
    rating: str  # STRONG_BUY, BUY, MAYBE, KEEP_CURRENT, AVOID
    confidence: float  # 0.0 to 1.0
    risk_score: int  # 0 to 100
    risk_level: str  # LOW, MEDIUM, HIGH
    summary_text: str
    key_advantages: list[str]
    cautions_and_risks: list[str]
    explanations: list[ValueExplanation]
