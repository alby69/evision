from pydantic import BaseModel, Field


class UsageProfile(BaseModel):
    annual_km: float = Field(default=20000.0, gt=0, description="Total annual kilometers driven")

    city_percentage: float = Field(default=0.40, ge=0, le=1.0)
    extraurban_percentage: float = Field(default=0.40, ge=0, le=1.0)
    highway_percentage: float = Field(default=0.20, ge=0, le=1.0)

    winter_multiplier: float = Field(default=1.20, ge=1.0, description="Winter consumption multiplier for EV (e.g., 1.20 = +20%)")
    summer_multiplier: float = Field(default=1.05, ge=1.0, description="Summer consumption multiplier (AC)")

    def validate_percentages(self) -> bool:
        total = self.city_percentage + self.extraurban_percentage + self.highway_percentage
        return abs(total - 1.0) < 0.001
