from decimal import ROUND_HALF_UP, Decimal

from app.domain.models.results import BreakEvenResult, VehicleTCOResult


def _round_dec(val: Decimal, places: int = 2) -> Decimal:
    fmt = "0." + "0" * places if places > 0 else "0"
    return val.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)

def calculate_break_even(
    current_tco: VehicleTCOResult,
    candidate_tco: VehicleTCOResult,
    annual_km: float,
) -> BreakEvenResult:
    horizon = current_tco.horizon_years

    current_annual_ops = (
        current_tco.total_energy_fuel_cost +
        current_tco.total_maintenance_cost +
        current_tco.total_insurance_cost +
        current_tco.total_taxes
    ) / Decimal(horizon)

    candidate_annual_ops = (
        candidate_tco.total_energy_fuel_cost +
        candidate_tco.total_maintenance_cost +
        candidate_tco.total_insurance_cost +
        candidate_tco.total_taxes
    ) / Decimal(horizon)

    annual_ops_savings = current_annual_ops - candidate_annual_ops
    monthly_ops_savings = annual_ops_savings / Decimal(12)

    upfront_cost_difference = candidate_tco.net_purchase_cost - current_tco.net_purchase_cost

    op_break_even_years: float | None = None
    op_break_even_months: float | None = None
    op_break_even_km: float | None = None

    if upfront_cost_difference <= Decimal(0):
        op_break_even_years = 0.0
        op_break_even_months = 0.0
        op_break_even_km = 0.0
    elif annual_ops_savings > Decimal(0):
        op_break_even_years = float(upfront_cost_difference / annual_ops_savings)
        op_break_even_months = op_break_even_years * 12.0
        op_break_even_km = op_break_even_years * annual_km

    tot_break_even_years: float | None = None
    tot_break_even_months: float | None = None
    tot_break_even_km: float | None = None

    for y in range(1, horizon + 1):
        curr_cum = current_tco.yearly_breakdown[y - 1].cumulative_cost
        cand_cum = candidate_tco.yearly_breakdown[y - 1].cumulative_cost

        curr_total = current_tco.net_purchase_cost + curr_cum - current_tco.yearly_breakdown[y - 1].residual_value
        cand_total = candidate_tco.net_purchase_cost + cand_cum - candidate_tco.yearly_breakdown[y - 1].residual_value

        if cand_total <= curr_total:
            tot_break_even_years = float(y)
            tot_break_even_months = float(y * 12)
            tot_break_even_km = float(y * annual_km)
            break

    cum_savings = current_tco.total_tco - candidate_tco.total_tco
    cost_per_km_diff = current_tco.tco_per_km - candidate_tco.tco_per_km

    return BreakEvenResult(
        operational_break_even_years=round(op_break_even_years, 2) if op_break_even_years is not None else None,
        operational_break_even_months=round(op_break_even_months, 1) if op_break_even_months is not None else None,
        operational_break_even_km=round(op_break_even_km, 0) if op_break_even_km is not None else None,

        total_ownership_break_even_years=round(tot_break_even_years, 2) if tot_break_even_years is not None else None,
        total_ownership_break_even_months=round(tot_break_even_months, 1) if tot_break_even_months is not None else None,
        total_ownership_break_even_km=round(tot_break_even_km, 0) if tot_break_even_km is not None else None,

        cumulative_savings_over_horizon=_round_dec(cum_savings, 2),
        annual_operational_savings=_round_dec(annual_ops_savings, 2),
        monthly_operational_savings=_round_dec(monthly_ops_savings, 2),
        cost_per_km_diff=_round_dec(cost_per_km_diff, 4),
    )
