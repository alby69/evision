export enum VehicleType {
  BEV = 'BEV',
  PHEV = 'PHEV',
  HEV = 'HEV',
  PETROL = 'PETROL',
  DIESEL = 'DIESEL',
  LPG = 'LPG',
  CNG = 'CNG',
}

export enum FuelType {
  ELECTRICITY = 'ELECTRICITY',
  DIESEL = 'DIESEL',
  PETROL = 'PETROL',
  LPG = 'LPG',
  CNG = 'CNG',
}

export enum RecommendationRating {
  STRONG_BUY = 'STRONG_BUY',
  BUY = 'BUY',
  MAYBE = 'MAYBE',
  KEEP_CURRENT = 'KEEP_CURRENT',
  AVOID = 'AVOID',
}

export interface Vehicle {
  id?: string;
  brand: string;
  model: string;
  version?: string;
  year: number;
  vehicle_type: VehicleType;
  fuel_type: FuelType;
  purchase_price: number;
  current_value?: number;
  annual_tax?: number;
  urban_consumption: number;
  extraurban_consumption: number;
  highway_consumption: number;
  battery_capacity?: number;
  usable_battery_capacity?: number;
  wltp_range?: number;
  charging_ac_power?: number;
  charging_dc_power?: number;
  maintenance_cost_per_year?: number;
  insurance_cost_per_year?: number;
  tire_cost_per_year?: number;
}

export interface UsageProfile {
  annual_km: number;
  city_percentage: number;
  extraurban_percentage: number;
  highway_percentage: number;
  winter_multiplier: number;
}

export interface ChargingProfile {
  home_charging_percentage: number;
  public_ac_charging_percentage: number;
  public_dc_charging_percentage: number;
  home_energy_price: number;
  public_ac_energy_price: number;
  public_dc_energy_price: number;
  charging_losses_percentage: number;
}

export interface FuelProfile {
  diesel_price: number;
  petrol_price: number;
  lpg_price: number;
  cng_price: number;
  annual_fuel_price_growth: number;
}

export interface FinancingProfile {
  financing_type: 'CASH' | 'LOAN' | 'FINANCING' | 'LEASING';
  down_payment: number;
  financed_amount: number;
  interest_rate_annual: number;
  duration_months: number;
  final_balloon_payment: number;
  residual_value_percentage?: number;
  lease_monthly_fee?: number;
}

export interface OwnershipScenario {
  horizon_years: number;
  trade_in_value: number;
  incentive_amount: number;
  financing: FinancingProfile;
}

export interface YearlyCostBreakdown {
  year: number;
  energy_or_fuel_cost: number;
  financing_cost: number;
  maintenance_cost: number;
  insurance_cost: number;
  tax_cost: number;
  tire_cost: number;
  depreciation: number;
  total_year_cost: number;
  cumulative_cost: number;
  residual_value: number;
}

export interface VehicleTCOResult {
  vehicle_id?: string;
  vehicle_name: string;
  horizon_years: number;
  net_purchase_cost: number;
  total_tco: number;
  tco_per_year: number;
  tco_per_month: number;
  tco_per_km: number;
  yearly_breakdown: YearlyCostBreakdown[];
  residual_value_end: number;
  total_energy_fuel_cost: number;
  total_maintenance_cost: number;
  total_insurance_cost: number;
  total_taxes: number;
  total_financing_interest: number;
}

export interface BreakEvenResult {
  operational_break_even_years?: number;
  operational_break_even_months?: number;
  operational_break_even_km?: number;
  total_ownership_break_even_years?: number;
  total_ownership_break_even_months?: number;
  total_ownership_break_even_km?: number;
  cumulative_savings_over_horizon: number;
  annual_operational_savings: number;
  monthly_operational_savings: number;
  cost_per_km_diff: number;
}

export interface RealWorldRangeResult {
  usable_battery_kwh: number;
  urban_range_km: number;
  extraurban_range_km: number;
  highway_range_km: number;
  mixed_range_km: number;
  winter_highway_range_km: number;
}

export interface BatteryDegradationResult {
  initial_capacity_kwh: number;
  yearly_capacities_kwh: Record<number, number>;
  yearly_ranges_km: Record<number, number>;
}

export interface ScenarioResult {
  pessimistic_tco: number;
  base_tco: number;
  optimistic_tco: number;
  pessimistic_break_even_years?: number;
  base_break_even_years?: number;
  optimistic_break_even_years?: number;
}

export interface SensitivityFactor {
  parameter_name: string;
  impact_score: number;
  impact_description: string;
}

export interface ValueExplanation {
  value: string;
  formula: string;
  source: 'FACT' | 'USER_INPUT' | 'ESTIMATE' | 'ASSUMPTION';
  notes?: string;
}

export interface DecisionRecommendation {
  rating: RecommendationRating;
  confidence: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  summary_text: string;
  key_advantages: string[];
  cautions_and_risks: string[];
  explanations: ValueExplanation[];
}

export interface FullAnalysisResponse {
  id?: string;
  title: string;
  current_vehicle: Vehicle;
  candidate_vehicle: Vehicle;
  usage: UsageProfile;
  charging: ChargingProfile;
  fuel: FuelProfile;
  ownership: OwnershipScenario;
  current_tco: VehicleTCOResult;
  candidate_tco: VehicleTCOResult;
  break_even: BreakEvenResult;
  candidate_range: RealWorldRangeResult;
  candidate_battery_degradation: BatteryDegradationResult;
  scenarios: ScenarioResult;
  sensitivity: SensitivityFactor[];
  recommendation: DecisionRecommendation;
}
