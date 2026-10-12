from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ev_catalog_endpoint():
    response = client.get("/api/v1/vehicles/catalog")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Search specifically for Tesla
    tesla_res = client.get("/api/v1/vehicles/catalog?search=Tesla")
    assert tesla_res.status_code == 200
    tesla_data = tesla_res.json()
    assert len(tesla_data) > 0
    assert any("Tesla" in item["make"] for item in tesla_data)

    # Filter specifically by make=Renault
    renault_res = client.get("/api/v1/vehicles/catalog?make=Renault")
    assert renault_res.status_code == 200
    renault_data = renault_res.json()
    assert len(renault_data) > 0
    assert all("Renault" in item["make"] for item in renault_data)

def test_list_vehicles():
    response = client.get("/api/v1/vehicles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_car_facets_endpoint():
    response = client.get("/api/v1/vehicles/car-facets?facets=make")
    assert response.status_code == 200
    data = response.json()
    assert "make" in data
    assert isinstance(data["make"], list)
    assert len(data["make"]) > 0
    assert {"value", "count"} <= set(data["make"][0].keys())

    models_res = client.get("/api/v1/vehicles/car-facets?facets=model&make=Toyota")
    assert models_res.status_code == 200
    models = models_res.json()
    assert "model" in models
    assert len(models["model"]) > 0


def test_car_catalog_endpoint():
    response = client.get("/api/v1/vehicles/cars?make=Toyota&model=Corolla")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("make" in item and "model" in item for item in data)


def test_valuation_endpoint_unavailable_without_key(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "RAPIDAPI_API_KEY", "")
    response = client.post(
        "/api/v1/vehicles/valuation",
        json={"make": "Fiat", "model": "Panda", "year": 2019, "mileage": 80000},
    )
    assert response.status_code == 503
    assert "RAPIDAPI_API_KEY" in response.json()["detail"]


def test_valuation_endpoint_validation():
    response = client.post("/api/v1/vehicles/valuation", json={"make": "", "model": ""})
    assert response.status_code == 422

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
