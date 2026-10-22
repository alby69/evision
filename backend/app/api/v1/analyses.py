from datetime import datetime, timezone
from typing import Any, Union, cast
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.seed import DEMO_VEHICLES
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.models.db_models import SavedAnalysis, SavedVehicle
from app.schemas.api_schemas import (
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    FullAnalysisRequest,
    FullAnalysisResponse,
    SavedAnalysisSummary,
)
from app.services.analysis_service import run_comparative_analysis, run_full_analysis

router = APIRouter(prefix="/analyses", tags=["Analyses"])

_saved_analyses: dict[str, Any] = {}


@router.get("/demo", response_model=FullAnalysisResponse)
def get_demo_analysis() -> FullAnalysisResponse:
    """Generates a ready-to-use demo analysis (Honda CR-V 2016 vs. Renault Zoe 2022)."""
    honda_crv = DEMO_VEHICLES[0]
    renault_zoe = DEMO_VEHICLES[2]

    demo_usage = UsageProfile(
        annual_km=25000.0,
        city_percentage=0.40,
        extraurban_percentage=0.40,
        highway_percentage=0.20,
        winter_multiplier=1.20,
    )
    demo_charging = ChargingProfile(
        home_charging_percentage=0.80,
        public_ac_charging_percentage=0.10,
        public_dc_charging_percentage=0.10,
    )
    demo_fuel = FuelProfile()
    demo_ownership = OwnershipScenario(
        horizon_years=6,
        trade_in_value=honda_crv.current_value,
    )

    res_dict = run_full_analysis(
        current_vehicle=honda_crv,
        candidate_vehicle=renault_zoe,
        usage=demo_usage,
        charging=demo_charging,
        fuel=demo_fuel,
        ownership=demo_ownership,
    )

    return FullAnalysisResponse(
        id="demo-analysis-001",
        title="Demo Analysis: Honda CR-V vs. Renault Zoe R110",
        current_vehicle=honda_crv,
        candidate_vehicle=renault_zoe,
        usage=demo_usage,
        charging=demo_charging,
        fuel=demo_fuel,
        ownership=demo_ownership,
        **res_dict,
    )


@router.post("", response_model=FullAnalysisResponse, status_code=201)
async def create_analysis(
    req: FullAnalysisRequest, db: AsyncSession = Depends(get_db)
) -> FullAnalysisResponse:
    """Executes full decision engine analysis and persists response."""
    res_dict = run_full_analysis(
        current_vehicle=req.current_vehicle,
        candidate_vehicle=req.candidate_vehicle,
        usage=req.usage,
        charging=req.charging,
        fuel=req.fuel,
        ownership=req.ownership,
    )

    analysis_id = f"analysis-{uuid.uuid4().hex[:8]}"
    title = req.title or f"Confronto {req.current_vehicle.brand} vs {req.candidate_vehicle.brand}"

    response = FullAnalysisResponse(
        id=analysis_id,
        title=title,
        current_vehicle=req.current_vehicle,
        candidate_vehicle=req.candidate_vehicle,
        usage=req.usage,
        charging=req.charging,
        fuel=req.fuel,
        ownership=req.ownership,
        **res_dict,
    )

    _saved_analyses[analysis_id] = response.model_dump(mode="json")

    try:
        cand_ids = [req.candidate_vehicle.id] if req.candidate_vehicle.id else []
        saved_entry = SavedAnalysis(
            id=analysis_id,
            name=title,
            current_vehicle_id=req.current_vehicle.id,
            candidate_vehicle_ids=cand_ids,
            analysis_result=response.model_dump(mode="json"),
            created_at=datetime.now(timezone.utc),
        )
        db.add(saved_entry)
        await db.commit()
    except Exception:
        pass

    return response


@router.post("/compare", response_model=ComparativeAnalysisResponse, status_code=201)
async def create_comparative_analysis(
    req: ComparativeAnalysisRequest, db: AsyncSession = Depends(get_db)
) -> ComparativeAnalysisResponse:
    """Executes multi-car decision engine analysis comparing 1 reference vehicle against N candidate EVs."""
    curr_vehicle = req.current_vehicle
    if not curr_vehicle and req.current_vehicle_id:
        try:
            stmt = select(SavedVehicle).where(SavedVehicle.id == req.current_vehicle_id)
            res = await db.execute(stmt)
            sv = res.scalar_one_or_none()
            if sv:
                from app.domain.models.vehicle import Vehicle
                curr_vehicle = Vehicle(**sv.vehicle_data)
        except Exception:
            pass

    if not curr_vehicle:
        raise HTTPException(
            status_code=400,
            detail="È necessario fornire l'auto di riferimento (current_vehicle o current_vehicle_id valido).",
        )

    res_dict = run_comparative_analysis(
        current_vehicle=curr_vehicle,
        candidate_vehicles=req.candidate_vehicles,
        usage=req.usage,
        charging=req.charging,
        fuel=req.fuel,
        ownership=req.ownership,
    )

    analysis_id = f"analysis-{uuid.uuid4().hex[:8]}"
    cand_names = ", ".join([f"{c.brand} {c.model}" for c in req.candidate_vehicles[:3]])
    title = req.title or f"Confronto {curr_vehicle.brand} vs {cand_names}"
    created_str = datetime.now(timezone.utc).isoformat()

    response = ComparativeAnalysisResponse(
        id=analysis_id,
        title=title,
        current_vehicle=curr_vehicle,
        current_tco=res_dict["current_tco"],
        usage=req.usage,
        charging=req.charging,
        fuel=req.fuel,
        ownership=req.ownership,
        comparisons=res_dict["comparisons"],
        created_at=created_str,
    )

    _saved_analyses[analysis_id] = response.model_dump(mode="json")

    try:
        cand_ids = [c.id for c in req.candidate_vehicles if c.id]
        saved_entry = SavedAnalysis(
            id=analysis_id,
            name=title,
            current_vehicle_id=curr_vehicle.id if curr_vehicle else None,
            candidate_vehicle_ids=cand_ids,
            analysis_result=response.model_dump(mode="json"),
            created_at=datetime.now(timezone.utc),
        )
        db.add(saved_entry)
        await db.commit()
    except Exception:
        pass

    return response


@router.get("", response_model=list[SavedAnalysisSummary])
async def list_analyses(db: AsyncSession = Depends(get_db)) -> list[SavedAnalysisSummary]:
    """Lists saved analyses with lightweight metadata."""
    summaries: list[SavedAnalysisSummary] = []
    try:
        stmt = select(SavedAnalysis).order_by(SavedAnalysis.created_at.desc())
        result = await db.execute(stmt)
        entries = result.scalars().all()
        for e in entries:
            data = e.analysis_result
            curr_name = "Auto"
            cand_count = 1
            if isinstance(data, dict):
                if "current_vehicle" in data and isinstance(data["current_vehicle"], dict):
                    curr_name = f"{data['current_vehicle'].get('brand', '')} {data['current_vehicle'].get('model', '')}".strip()
                if "comparisons" in data and isinstance(data["comparisons"], list):
                    cand_count = len(data["comparisons"])

            created_str = e.created_at.isoformat() if isinstance(e.created_at, datetime) else str(e.created_at)
            summaries.append(
                SavedAnalysisSummary(
                    id=e.id,
                    title=e.name or "Analisi salvata",
                    current_vehicle_name=curr_name or "Auto",
                    candidate_count=cand_count,
                    created_at=created_str,
                )
            )
        if summaries:
            return summaries
    except Exception:
        pass

    # Fallback to in-memory analyses
    for aid, data in _saved_analyses.items():
        curr_name = "Auto"
        cand_count = 1
        if isinstance(data, dict):
            if "current_vehicle" in data and isinstance(data["current_vehicle"], dict):
                curr_name = f"{data['current_vehicle'].get('brand', '')} {data['current_vehicle'].get('model', '')}".strip()
            if "comparisons" in data and isinstance(data["comparisons"], list):
                cand_count = len(data["comparisons"])
            title = data.get("title", "Analisi salvata")
            created_str = data.get("created_at", datetime.now(timezone.utc).isoformat())
            summaries.append(
                SavedAnalysisSummary(
                    id=aid,
                    title=title,
                    current_vehicle_name=curr_name or "Auto",
                    candidate_count=cand_count,
                    created_at=created_str,
                )
            )

    return summaries


@router.get("/{analysis_id}", response_model=Union[FullAnalysisResponse, ComparativeAnalysisResponse])
async def get_analysis(
    analysis_id: str, db: AsyncSession = Depends(get_db)
) -> Union[FullAnalysisResponse, ComparativeAnalysisResponse]:
    """Retrieves a saved analysis by ID."""
    if analysis_id == "demo-analysis-001":
        return get_demo_analysis()

    try:
        stmt = select(SavedAnalysis).where(SavedAnalysis.id == analysis_id)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry and isinstance(entry.analysis_result, dict):
            data = entry.analysis_result
            if "comparisons" in data:
                return cast(ComparativeAnalysisResponse, ComparativeAnalysisResponse(**data))
            return cast(FullAnalysisResponse, FullAnalysisResponse(**data))
    except Exception:
        pass

    if analysis_id in _saved_analyses:
        data = _saved_analyses[analysis_id]
        if isinstance(data, dict):
            if "comparisons" in data:
                return cast(ComparativeAnalysisResponse, ComparativeAnalysisResponse(**data))
            return cast(FullAnalysisResponse, FullAnalysisResponse(**data))

    raise HTTPException(status_code=404, detail="Analysis not found")


@router.put("/{analysis_id}")
async def update_analysis(
    analysis_id: str, title_payload: dict[str, str], db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Updates/renames a saved analysis."""
    new_title = title_payload.get("title")
    if not new_title:
        raise HTTPException(status_code=400, detail="Il campo 'title' è obbligatorio.")

    updated = False
    try:
        stmt = select(SavedAnalysis).where(SavedAnalysis.id == analysis_id)
        res = await db.execute(stmt)
        entry = res.scalar_one_or_none()
        if entry:
            entry_obj = cast(Any, entry)
            entry_obj.name = new_title
            if isinstance(entry_obj.analysis_result, dict):
                entry_obj.analysis_result["title"] = new_title
            await db.commit()
            updated = True
    except Exception:
        pass

    if analysis_id in _saved_analyses and isinstance(_saved_analyses[analysis_id], dict):
        _saved_analyses[analysis_id]["title"] = new_title
        updated = True

    if not updated:
        raise HTTPException(status_code=404, detail="Analisi non trovata")

    return {"message": "Analisi aggiornata con successo", "title": new_title}


@router.delete("/{analysis_id}", status_code=204)
async def delete_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Deletes a saved analysis."""
    deleted = False
    try:
        stmt = select(SavedAnalysis).where(SavedAnalysis.id == analysis_id)
        res = await db.execute(stmt)
        entry = res.scalar_one_or_none()
        if entry:
            await db.delete(entry)
            await db.commit()
            deleted = True
    except Exception:
        pass

    if analysis_id in _saved_analyses:
        del _saved_analyses[analysis_id]
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail="Analisi non trovata")
