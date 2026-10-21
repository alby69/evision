import csv
import json
from pathlib import Path
import pytest
from scripts.import_ev_dataset import import_ev_dataset, EVDatasetRecord


def test_ev_dataset_record_validation():
    valid_data = {
        "unique_code": "test:ev_one:2024:base",
        "make_slug": "test",
        "make_name": "Test Brand",
        "model_slug": "ev_one",
        "model_name": "EV One",
        "year": "2024",
        "battery_capacity_gross_kwh": "75.5",
        "range_wltp_km": "450",
    }
    record = EVDatasetRecord.model_validate(valid_data)
    assert record.unique_code == "test:ev_one:2024:base"
    assert record.year == 2024
    assert record.battery_capacity_gross_kwh == 75.5
    assert record.range_wltp_km == 450.0

    csv_dict = record.to_csv_dict()
    assert csv_dict["unique_code"] == "test:ev_one:2024:base"
    assert csv_dict["battery_capacity_gross_kwh"] == "75.5"


def test_import_json_and_csv_upsert(tmp_path: Path):
    target_csv = tmp_path / "target_open_ev.csv"
    input_json = tmp_path / "new_evs.json"

    records = [
        {
            "unique_code": "brand:model1:2025:base",
            "make_slug": "brand",
            "make_name": "Brand",
            "model_slug": "model1",
            "model_name": "Model 1",
            "year": 2025,
            "battery_capacity_gross_kwh": 80.0,
            "range_wltp_km": 500.0,
        },
        {
            "unique_code": "invalid_record_missing_fields",
        },
    ]

    with input_json.open("w", encoding="utf-8") as f:
        json.dump(records, f)

    summary = import_ev_dataset(input_json, target_csv, dry_run=False)
    assert summary["processed"] == 2
    assert summary["valid"] == 1
    assert summary["rejected"] == 1
    assert summary["upserted"] == 1

    assert target_csv.exists()
    with target_csv.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert reader[0]["unique_code"] == "brand:model1:2025:base"
        assert reader[0]["battery_capacity_gross_kwh"] == "80.0"

    input_csv = tmp_path / "more_evs.csv"
    with input_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["unique_code", "make_slug", "make_name", "model_slug", "model_name", "year", "range_wltp_km"])
        writer.writerow(["brand:model1:2025:base", "brand", "Brand", "model1", "Model 1", "2025", "520.0"])
        writer.writerow(["brand:model2:2025:base", "brand", "Brand", "model2", "Model 2", "2025", "400.0"])

    summary2 = import_ev_dataset(input_csv, target_csv, dry_run=False)
    assert summary2["processed"] == 2
    assert summary2["valid"] == 2
    assert summary2["total_target_records"] == 2

    with target_csv.open("r", encoding="utf-8") as f:
        rows = {r["unique_code"]: r for r in csv.DictReader(f)}
        assert rows["brand:model1:2025:base"]["range_wltp_km"] == "520.0"
        assert "brand:model2:2025:base" in rows


def test_dry_run(tmp_path: Path):
    target_csv = tmp_path / "target_open_ev.csv"
    input_json = tmp_path / "new_evs.json"

    records = [
        {
            "unique_code": "brand:model1:2025:base",
            "make_slug": "brand",
            "make_name": "Brand",
            "model_slug": "model1",
            "model_name": "Model 1",
            "year": 2025,
        }
    ]

    with input_json.open("w", encoding="utf-8") as f:
        json.dump(records, f)

    summary = import_ev_dataset(input_json, target_csv, dry_run=True)
    assert summary["valid"] == 1
    assert not target_csv.exists()
