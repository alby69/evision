from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_vehicles():
    response = client.get("/api/v1/vehicles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_demo_analysis_endpoint():
    response = client.get("/api/v1/analyses/demo")
    assert response.status_code == 200
    data = response.json()
    assert "current_tco" in data
    assert "candidate_tco" in data
    assert "break_even" in data
    assert "recommendation" in data
    assert data["recommendation"]["rating"] in ["STRONG_BUY", "BUY", "MAYBE", "KEEP_CURRENT", "AVOID"]

def test_full_analysis_creation():
    demo_res = client.get("/api/v1/analyses/demo").json()
    payload = {
        "title": "Custom Test Analysis",
        "current_vehicle": demo_res["current_vehicle"],
        "candidate_vehicle": demo_res["candidate_vehicle"],
        "usage": demo_res["usage"],
        "charging": demo_res["charging"],
        "fuel": demo_res["fuel"],
        "ownership": demo_res["ownership"],
    }
    response = client.post("/api/v1/analyses", json=payload)
    assert response.status_code == 201
    data = response.json()
    analysis_id = data["id"]
    assert analysis_id.startswith("analysis-")
    assert data["title"] == "Custom Test Analysis"

    # Test retrieval of saved analysis
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Custom Test Analysis"
