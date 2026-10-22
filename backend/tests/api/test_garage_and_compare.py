from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_garage_crud():
    # 1. Create a vehicle in garage
    vehicle_payload = {
        "name": "Fiat Panda 2020",
        "is_default": True,
        "vehicle_data": {
            "brand": "Fiat",
            "model": "Panda",
            "year": 2020,
            "vehicle_type": "PETROL",
            "fuel_type": "PETROL",
            "purchase_price": 9000,
            "current_value": 7000,
            "annual_tax": 150,
            "urban_consumption": 6.5,
            "extraurban_consumption": 5.0,
            "highway_consumption": 6.0,
        },
    }
    create_res = client.post("/api/v1/garage", json=vehicle_payload)
    assert create_res.status_code == 201
    v_data = create_res.json()
    v_id = v_data["id"]
    assert v_data["name"] == "Fiat Panda 2020"
    assert v_data["is_default"] is True

    # 2. List vehicles in garage
    list_res = client.get("/api/v1/garage")
    assert list_res.status_code == 200
    vehicles = list_res.json()
    assert len(vehicles) >= 1
    assert any(v["id"] == v_id for v in vehicles)

    # 3. Get specific vehicle
    get_res = client.get(f"/api/v1/garage/{v_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Fiat Panda 2020"

    # 4. Update vehicle
    update_res = client.put(f"/api/v1/garage/{v_id}", json={"name": "Fiat Panda Easy"})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Fiat Panda Easy"

    # 5. Delete vehicle
    del_res = client.delete(f"/api/v1/garage/{v_id}")
    assert del_res.status_code == 204


def test_comparative_analysis_endpoint():
    demo_res = client.get("/api/v1/analyses/demo").json()
    current = demo_res["current_vehicle"]
    candidate1 = demo_res["candidate_vehicle"]

    candidate2 = dict(candidate1)
    candidate2["model"] = "Zoe R135"
    candidate2["purchase_price"] = 15000

    compare_payload = {
        "title": "Confronto Multi-Auto Test",
        "current_vehicle": current,
        "candidate_vehicles": [candidate1, candidate2],
        "usage": demo_res["usage"],
        "charging": demo_res["charging"],
        "fuel": demo_res["fuel"],
        "ownership": demo_res["ownership"],
    }

    res = client.post("/api/v1/analyses/compare", json=compare_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Confronto Multi-Auto Test"
    assert len(data["comparisons"]) == 2
    assert data["comparisons"][0]["candidate_vehicle"]["model"] == candidate1["model"]
    assert data["comparisons"][1]["candidate_vehicle"]["model"] == "Zoe R135"

    analysis_id = data["id"]
    # Verify retrieving comparative analysis by ID
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert len(get_data["comparisons"]) == 2

    # Verify listing analyses summaries
    list_res = client.get("/api/v1/analyses")
    assert list_res.status_code == 200
    summaries = list_res.json()
    assert any(s["id"] == analysis_id for s in summaries)
