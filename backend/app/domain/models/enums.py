from enum import Enum


class VehicleType(str, Enum):
    BEV = "BEV"
    PHEV = "PHEV"
    HEV = "HEV"
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    LPG = "LPG"
    CNG = "CNG"

class FuelType(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    DIESEL = "DIESEL"
    PETROL = "PETROL"
    LPG = "LPG"
    CNG = "CNG"

class ValueSource(str, Enum):
    FACT = "FACT"
    USER_INPUT = "USER_INPUT"
    ESTIMATE = "ESTIMATE"
    ASSUMPTION = "ASSUMPTION"

class RecommendationRating(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    MAYBE = "MAYBE"
    KEEP_CURRENT = "KEEP_CURRENT"
    AVOID = "AVOID"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class FinancingType(str, Enum):
    CASH = "CASH"
    LOAN = "LOAN"
    FINANCING = "FINANCING"
    LEASING = "LEASING"
