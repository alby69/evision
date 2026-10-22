import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domain.engine.recommendation_engine import generate_decision_recommendation
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.core.seed import DEMO_VEHICLES
from app.services.analysis_service import run_full_analysis

client = TestClient(app)


def test_ai_explain_demo_endpoint():
    response = client.post("/api/v1/analyses/demo-analysis-001/ai-explain")
    assert response.status_code == 200
    data = response.json()
    assert "ai_summary" in data
    assert len(data["ai_summary"]) > 20


def test_qna_demo_endpoint():
    response = client.post(
        "/api/v1/analyses/demo-analysis-001/qna",
        json={"question": "Perché mi consigli la Zoe rispetto alla Honda CR-V?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 20


def test_red_flags_and_weighted_score():
    honda_crv = DEMO_VEHICLES[0]
    renault_zoe = DEMO_VEHICLES[2]

    demo_usage = UsageProfile(annual_km=25000.0)
    demo_charging = ChargingProfile(home_charging_percentage=0.20)  # Low home charging trigger
    demo_fuel = FuelProfile()
    demo_ownership = OwnershipScenario(horizon_years=5)

    res = run_full_analysis(
        current_vehicle=honda_crv,
        candidate_vehicle=renault_zoe,
        usage=demo_usage,
        charging=demo_charging,
        fuel=demo_fuel,
        ownership=demo_ownership,
    )

    rec = res["recommendation"]
    assert rec.weighted_score is not None
    assert isinstance(rec.red_flags, list)

    # Should trigger LOW_HOME_CHARGING flag
    codes = [rf.code for rf in rec.red_flags]
    assert "LOW_HOME_CHARGING" in codes
