
from app.domain.models.results import BatteryDegradationResult, RealWorldRangeResult
from app.domain.models.usage import UsageProfile
from app.domain.models.vehicle import Vehicle


def calculate_real_world_range(vehicle: Vehicle, usage: UsageProfile) -> RealWorldRangeResult:
    usable_kwh = vehicle.usable_battery_capacity or vehicle.battery_capacity or 50.0

    urban_cons = vehicle.urban_consumption
    extraurban_cons = vehicle.extraurban_consumption
    highway_cons = vehicle.highway_consumption

    mixed_cons = (
        usage.city_percentage * urban_cons +
        usage.extraurban_percentage * extraurban_cons +
        usage.highway_percentage * highway_cons
    )

    urban_range = (usable_kwh / urban_cons) * 100.0 if urban_cons > 0 else 0.0
    extraurban_range = (usable_kwh / extraurban_cons) * 100.0 if extraurban_cons > 0 else 0.0
    highway_range = (usable_kwh / highway_cons) * 100.0 if highway_cons > 0 else 0.0
    mixed_range = (usable_kwh / mixed_cons) * 100.0 if mixed_cons > 0 else 0.0

    winter_highway_cons = highway_cons * usage.winter_multiplier
    winter_highway_range = (usable_kwh / winter_highway_cons) * 100.0 if winter_highway_cons > 0 else 0.0

    return RealWorldRangeResult(
        usable_battery_kwh=usable_kwh,
        urban_range_km=round(urban_range, 1),
        extraurban_range_km=round(extraurban_range, 1),
        highway_range_km=round(highway_range, 1),
        mixed_range_km=round(mixed_range, 1),
        winter_highway_range_km=round(winter_highway_range, 1),
    )

def calculate_battery_degradation(
    vehicle: Vehicle,
    usage: UsageProfile,
    horizon_years: int,
    yearly_degradation_rate: float = 0.015,
    km_degradation_per_10k: float = 0.005,
) -> BatteryDegradationResult:
    initial_cap = vehicle.usable_battery_capacity or vehicle.battery_capacity or 50.0
    real_range = calculate_real_world_range(vehicle, usage)

    capacities: dict[int, float] = {0: initial_cap}
    ranges: dict[int, float] = {0: real_range.mixed_range_km}

    current_cap = initial_cap
    for y in range(1, horizon_years + 1):
        time_loss = current_cap * yearly_degradation_rate
        use_loss = current_cap * (usage.annual_km / 10000.0) * km_degradation_per_10k
        current_cap = max(current_cap - (time_loss + use_loss), initial_cap * 0.60)

        capacities[y] = round(current_cap, 2)
        ratio = current_cap / initial_cap
        ranges[y] = round(real_range.mixed_range_km * ratio, 1)

    return BatteryDegradationResult(
        initial_capacity_kwh=initial_cap,
        yearly_capacities_kwh=capacities,
        yearly_ranges_km=ranges,
    )
