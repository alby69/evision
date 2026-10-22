from datetime import datetime, timezone
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, Numeric, String

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    version = Column(String, nullable=True, default="")
    year = Column(Integer, nullable=False)

    vehicle_type = Column(String, nullable=False)
    fuel_type = Column(String, nullable=False)

    purchase_price = Column(Numeric(12, 2), nullable=False)
    current_value = Column(Numeric(12, 2), nullable=True, default=0.0)
    annual_tax = Column(Numeric(12, 2), nullable=True, default=0.0)

    urban_consumption = Column(Float, nullable=False)
    extraurban_consumption = Column(Float, nullable=False)
    highway_consumption = Column(Float, nullable=False)

    battery_capacity = Column(Float, nullable=True)
    usable_battery_capacity = Column(Float, nullable=True)
    wltp_range = Column(Float, nullable=True)

    maintenance_cost_per_year = Column(Numeric(10, 2), default=0.0)
    insurance_cost_per_year = Column(Numeric(10, 2), default=0.0)
    tire_cost_per_year = Column(Numeric(10, 2), default=0.0)

    is_demo = Column(Boolean, default=False)


class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    current_vehicle_data = Column(JSON, nullable=False)
    candidate_vehicle_data = Column(JSON, nullable=False)
    usage_profile_data = Column(JSON, nullable=False)
    charging_profile_data = Column(JSON, nullable=False)
    fuel_profile_data = Column(JSON, nullable=False)
    ownership_scenario_data = Column(JSON, nullable=False)
    analysis_result_data = Column(JSON, nullable=True)


class SavedVehicle(Base):
    __tablename__ = "saved_vehicles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    vehicle_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class SavedAnalysis(Base):
    __tablename__ = "saved_analyses"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    current_vehicle_id = Column(String, ForeignKey("saved_vehicles.id"), nullable=True)
    candidate_vehicle_ids = Column(JSON, nullable=False)
    analysis_result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now)
