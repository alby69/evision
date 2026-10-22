import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import app
from app.domain.engine.recommendation_engine import generate_decision_recommendation
from app.domain.models.charging import ChargingProfile, FuelProfile
from app.domain.models.ownership import OwnershipScenario
from app.domain.models.usage import UsageProfile
from app.domain.models.enums import FuelType, VehicleType
from app.domain.models.vehicle import Vehicle
from app.core.seed import DEMO_VEHICLES
from app.services.analysis_service import run_full_analysis
from app.services.ai_advisor_service import generate_rule_based_qna, generate_rule_based_explanation

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


def test_qna_annual_energy_cost():
    dacia_duster = DEMO_VEHICLES[1]
    leapmotor_b10 = Vehicle(
        id="leapmotor-b10",
        brand="Leapmotor",
        model="B10 160 kW",
        year=2024,
        vehicle_type=VehicleType.BEV,
        fuel_type=FuelType.ELECTRICITY,
        purchase_price=Decimal("29900.00"),
        urban_consumption=14.0,
        extraurban_consumption=16.0,
        highway_consumption=21.0,
        battery_capacity=68.7,
        usable_battery_capacity=68.7,
    )

    usage = UsageProfile(annual_km=30000.0)
    charging = ChargingProfile(home_charging_percentage=0.80)
    fuel = FuelProfile()
    ownership = OwnershipScenario(horizon_years=10, trade_in_value=8000.0)

    analysis_res = run_full_analysis(
        current_vehicle=dacia_duster,
        candidate_vehicle=leapmotor_b10,
        usage=usage,
        charging=charging,
        fuel=fuel,
        ownership=ownership,
    )

    # 1. Ask about annual energy expenditure in euros
    q1 = "io attualmente spendo quasi 3200€ anno per il carburante diesel per fare i 30.000km. Quanto spendo all'anno con l'elettrico?"
    ans1 = generate_rule_based_qna(analysis_res, q1)
    assert "Leapmotor B10" in ans1
    assert "spesa stimata in energia elettrica" in ans1
    assert "€" in ans1
    assert "/anno" in ans1

    # 2. Ask about annual savings
    q2 = "quanto risparmio ogni anno in carburante?"
    ans2 = generate_rule_based_qna(analysis_res, q2)
    assert "risparmio" in ans2
    assert "€" in ans2
    assert "Dacia Duster" in ans2

    # 3. Ask about break-even timeline
    q3 = "In quanti anni raggiungo il break-even?"
    ans3 = generate_rule_based_qna(analysis_res, q3)
    assert "punto di pareggio" in ans3 or "break-even" in ans3
    assert "anni" in ans3

    # 4. Ask about SUV recommendation
    q4 = "Consigliami qualche modello di auto elettrica SUV per sostituire la Duster"
    ans4 = generate_rule_based_qna(analysis_res, q4)
    assert "Leapmotor B10" in ans4
    assert "Zoe" not in ans4


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
