from app.services.ev_dataset import load_ev_dataset, search_ev_dataset


def test_dataset_loads_and_is_rich():
    items = load_ev_dataset()
    assert len(items) > 400

    makes = {item.make for item in items}
    assert {"Tesla", "Volkswagen", "Peugeot", "Renault", "BYD"} <= makes

    with_specs = [item for item in items if item.battery_useable_capacity and item.electric_range]
    assert len(with_specs) > 300


def test_search_is_case_insensitive_and_by_make():
    results = search_ev_dataset(search="volkswagen", limit=20)
    assert results
    assert all(item.make == "Volkswagen" for item in results)
    assert any(item.electric_range for item in results)
    assert any(item.vehicle_consumption for item in results)


def test_search_by_model_substring():
    results = search_ev_dataset(search="hyundai ioniq", limit=20)
    assert results
    assert all("Hyundai" == item.make for item in results)
    assert all("IONIQ" in item.model for item in results)
