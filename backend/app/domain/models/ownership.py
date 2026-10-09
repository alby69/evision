from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.models.enums import FinancingType


class FinancingProfile(BaseModel):
    financing_type: FinancingType = FinancingType.CASH
    down_payment: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    financed_amount: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    interest_rate_annual: float = Field(default=0.05, ge=0, description="Annual interest rate (e.g., 0.05 = 5%)")
    duration_months: int = Field(default=36, ge=0)
    final_balloon_payment: Decimal = Field(default=Decimal(0), ge=Decimal(0))

class OwnershipScenario(BaseModel):
    horizon_years: int = Field(default=5, ge=1, le=15)
    trade_in_value: Decimal = Field(default=Decimal(0), ge=Decimal(0), description="Value of current vehicle given as trade-in")
    incentive_amount: Decimal = Field(default=Decimal(0), ge=Decimal(0), description="Government / eco incentives applied")
    financing: FinancingProfile = Field(default_factory=FinancingProfile)
