from datetime import datetime, timezone
from typing import Any, cast
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db_models import SavedVehicle
from app.schemas.api_schemas import (
    SavedVehicleCreate,
    SavedVehicleResponse,
    SavedVehicleUpdate,
)

router = APIRouter(prefix="/garage", tags=["Garage"])

_in_memory_garage: dict[str, dict[str, Any]] = {}


def _to_response(sv: Any) -> SavedVehicleResponse:
    if isinstance(sv, dict):
        return SavedVehicleResponse(**sv)
    created_str = sv.created_at.isoformat() if isinstance(sv.created_at, datetime) else str(sv.created_at)
    updated_str = sv.updated_at.isoformat() if isinstance(sv.updated_at, datetime) else str(sv.updated_at)
    return SavedVehicleResponse(
        id=sv.id,
        name=sv.name,
        is_default=sv.is_default,
        vehicle_data=sv.vehicle_data,
        created_at=created_str,
        updated_at=updated_str,
    )


@router.get("", response_model=list[SavedVehicleResponse])
async def list_garage_vehicles(db: AsyncSession = Depends(get_db)) -> list[SavedVehicleResponse]:
    """Retrieves all saved vehicles from the user's garage."""
    db_vehicles: list[SavedVehicleResponse] = []
    try:
        stmt = select(SavedVehicle).order_by(SavedVehicle.is_default.desc(), SavedVehicle.created_at.desc())
        result = await db.execute(stmt)
        vehicles = result.scalars().all()
        db_vehicles = [_to_response(v) for v in vehicles]
    except Exception:
        pass

    db_ids = {v.id for v in db_vehicles}
    memory_vehicles = [
        _to_response(v) for v in _in_memory_garage.values() if v["id"] not in db_ids
    ]
    all_vehicles = db_vehicles + memory_vehicles
    all_vehicles.sort(key=lambda x: (x.is_default, x.created_at), reverse=True)
    return all_vehicles


@router.post("", response_model=SavedVehicleResponse, status_code=201)
async def create_garage_vehicle(
    payload: SavedVehicleCreate, db: AsyncSession = Depends(get_db)
) -> SavedVehicleResponse:
    """Saves a new vehicle into the user's garage."""
    v_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    v_data = payload.vehicle_data.model_dump(mode="json")
    if not v_data.get("id"):
        v_data["id"] = v_id

    try:
        if payload.is_default:
            await db.execute(update(SavedVehicle).values(is_default=False))

        new_vehicle = SavedVehicle(
            id=v_id,
            name=payload.name,
            is_default=payload.is_default,
            vehicle_data=v_data,
            created_at=now,
            updated_at=now,
        )
        db.add(new_vehicle)
        await db.commit()
        await db.refresh(new_vehicle)
        return _to_response(new_vehicle)
    except Exception:
        if payload.is_default:
            for item in _in_memory_garage.values():
                item["is_default"] = False

        res = {
            "id": v_id,
            "name": payload.name,
            "is_default": payload.is_default,
            "vehicle_data": v_data,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        _in_memory_garage[v_id] = res
        return _to_response(res)


@router.get("/{vehicle_id}", response_model=SavedVehicleResponse)
async def get_garage_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)) -> SavedVehicleResponse:
    """Retrieves a specific vehicle from the garage by ID."""
    try:
        stmt = select(SavedVehicle).where(SavedVehicle.id == vehicle_id)
        result = await db.execute(stmt)
        vehicle = result.scalar_one_or_none()
        if vehicle:
            return _to_response(vehicle)
    except Exception:
        if vehicle_id in _in_memory_garage:
            return _to_response(_in_memory_garage[vehicle_id])

    if vehicle_id in _in_memory_garage:
        return _to_response(_in_memory_garage[vehicle_id])
    raise HTTPException(status_code=404, detail="Vehicle not found in garage")


@router.put("/{vehicle_id}", response_model=SavedVehicleResponse)
async def update_garage_vehicle(
    vehicle_id: str, payload: SavedVehicleUpdate, db: AsyncSession = Depends(get_db)
) -> SavedVehicleResponse:
    """Updates a saved vehicle in the garage."""
    now = datetime.now(timezone.utc)
    try:
        stmt = select(SavedVehicle).where(SavedVehicle.id == vehicle_id)
        result = await db.execute(stmt)
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found in garage")

        vehicle_obj = cast(Any, vehicle)
        if payload.name is not None:
            vehicle_obj.name = payload.name
        if payload.vehicle_data is not None:
            v_data = payload.vehicle_data.model_dump(mode="json")
            if not v_data.get("id"):
                v_data["id"] = vehicle_id
            vehicle_obj.vehicle_data = v_data
        if payload.is_default is not None:
            if payload.is_default:
                await db.execute(update(SavedVehicle).values(is_default=False))
            vehicle_obj.is_default = payload.is_default

        vehicle_obj.updated_at = now
        await db.commit()
        await db.refresh(vehicle)
        return _to_response(vehicle)
    except HTTPException:
        raise
    except Exception:
        if vehicle_id not in _in_memory_garage:
            raise HTTPException(status_code=404, detail="Vehicle not found in garage")
        item = _in_memory_garage[vehicle_id]
        if payload.name is not None:
            item["name"] = payload.name
        if payload.vehicle_data is not None:
            v_data = payload.vehicle_data.model_dump(mode="json")
            if not v_data.get("id"):
                v_data["id"] = vehicle_id
            item["vehicle_data"] = v_data
        if payload.is_default is not None:
            if payload.is_default:
                for other in _in_memory_garage.values():
                    other["is_default"] = False
            item["is_default"] = payload.is_default
        item["updated_at"] = now.isoformat()
        return _to_response(item)


@router.delete("/{vehicle_id}", status_code=204)
async def delete_garage_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Removes a vehicle from the garage."""
    deleted = False
    try:
        stmt = select(SavedVehicle).where(SavedVehicle.id == vehicle_id)
        result = await db.execute(stmt)
        vehicle = result.scalar_one_or_none()
        if vehicle:
            await db.delete(vehicle)
            await db.commit()
            deleted = True
    except Exception:
        pass

    if vehicle_id in _in_memory_garage:
        del _in_memory_garage[vehicle_id]
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle not found in garage")
