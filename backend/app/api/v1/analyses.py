import uuid

from fastapi import APIRouter, HTTPException

from app.core.seed import DEMO_VEHICLES
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.schemas.api_schemas import FullAnalysisRequest, FullAnalysisResponse
from app.services.analysis_service import run_full_analysis

router = APIRouter(prefix="/analyses", tags=["Analyses"])

_saved_analyses: dict[str, FullAnalysisResponse] = {}

@router.post("", response_model=FullAnalysisResponse, status_code=201)
def create_analysis(req: FullAnalysisRequest):
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

    response = FullAnalysisResponse(
        id=analysis_id,
        title=req.title or "EV Replacement Decision Analysis",
        current_vehicle=req.current_vehicle,
        candidate_vehicle=req.candidate_vehicle,
        usage=req.usage,
        charging=req.charging,
        fuel=req.fuel,
        ownership=req.ownership,
        **res_dict
    )

    _saved_analyses[analysis_id] = response
    return response

@router.get("/demo", response_model=FullAnalysisResponse)
def get_demo_analysis():
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
        **res_dict
    )

@router.get("/{analysis_id}", response_model=FullAnalysisResponse)
def get_analysis(analysis_id: str):
    """Retrieves a saved analysis by ID."""
    if analysis_id in _saved_analyses:
        return _saved_analyses[analysis_id]
    if analysis_id == "demo-analysis-001":
        return get_demo_analysis()
    raise HTTPException(status_code=404, detail="Analysis not found")
