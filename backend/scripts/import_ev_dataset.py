#!/usr/bin/env python3
"""Advanced EV Dataset Import Script.

Imports and validates external EV dataset files (CSV or JSON), validates records
using a Pydantic v2 model (EVDatasetRecord), logs rejected rows, and safely merges/upserts
records into the target OpenEV Data CSV file.

Usage:
    python backend/scripts/import_ev_dataset.py --input-file path/to/data.json --target-file backend/data/open-ev-data.csv
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CSV_FIELDS = [
    "unique_code",
    "make_slug",
    "make_name",
    "model_slug",
    "model_name",
    "year",
    "trim_slug",
    "trim_name",
    "variant_slug",
    "variant_name",
    "vehicle_type",
    "drivetrain",
    "system_power_kw",
    "system_torque_nm",
    "battery_capacity_gross_kwh",
    "battery_capacity_net_kwh",
    "battery_chemistry",
    "dc_max_power_kw",
    "ac_max_power_kw",
    "range_wltp_km",
    "range_epa_km",
    "acceleration_0_100_s",
    "top_speed_kmh",
    "charge_connectors",
    "sources",
]


class EVDatasetRecord(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    unique_code: str = Field(..., min_length=1)
    make_slug: str = Field(..., min_length=1)
    make_name: str = Field(..., min_length=1)
    model_slug: str = Field(..., min_length=1)
    model_name: str = Field(..., min_length=1)
    year: int = Field(..., ge=1900, le=2100)

    trim_slug: str | None = ""
    trim_name: str | None = ""
    variant_slug: str | None = ""
    variant_name: str | None = ""
    vehicle_type: str | None = ""
    drivetrain: str | None = ""

    system_power_kw: float | None = None
    system_torque_nm: float | None = None
    battery_capacity_gross_kwh: float | None = None
    battery_capacity_net_kwh: float | None = None
    battery_chemistry: str | None = ""
    dc_max_power_kw: float | None = None
    ac_max_power_kw: float | None = None
    range_wltp_km: float | None = None
    range_epa_km: float | None = None
    acceleration_0_100_s: float | None = None
    top_speed_kmh: float | None = None
    charge_connectors: str | None = ""
    sources: str | None = ""

    @field_validator(
        "system_power_kw",
        "system_torque_nm",
        "battery_capacity_gross_kwh",
        "battery_capacity_net_kwh",
        "dc_max_power_kw",
        "ac_max_power_kw",
        "range_wltp_km",
        "range_epa_km",
        "acceleration_0_100_s",
        "top_speed_kmh",
        mode="before",
    )
    @classmethod
    def _coerce_optional_float(cls, v: Any) -> float | None:
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid numeric value: {v}")

    @field_validator("year", mode="before")
    @classmethod
    def _coerce_int(cls, v: Any) -> int:
        if isinstance(v, float):
            return int(v)
        if isinstance(v, str) and v.strip().isdigit():
            return int(v.strip())
        return v

    def to_csv_dict(self) -> dict[str, str]:
        dump = self.model_dump()
        result: dict[str, str] = {}
        for key in CSV_FIELDS:
            val = dump.get(key)
            result[key] = "" if val is None else str(val)
        return result


def load_raw_records(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".json":
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "records" in data and isinstance(data["records"], list):
                return data["records"]
            else:
                raise ValueError("JSON input must be a list of objects or a dict with a 'records' list.")
    elif suffix in (".csv", ".txt"):
        records: list[dict[str, Any]] = []
        with input_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported formats: .csv, .json")


def validate_and_parse(raw_records: list[dict[str, Any]]) -> tuple[list[EVDatasetRecord], list[dict[str, Any]]]:
    valid_records: list[EVDatasetRecord] = []
    rejected_records: list[dict[str, Any]] = []

    for idx, raw in enumerate(raw_records):
        try:
            rec = EVDatasetRecord.model_validate(raw)
            valid_records.append(rec)
        except ValidationError as err:
            logger.warning("Row %d rejected due to validation errors: %s | Raw data: %s", idx + 1, err.errors(), raw)
            rejected_records.append({"row_index": idx + 1, "data": raw, "errors": err.errors()})

    return valid_records, rejected_records


def import_ev_dataset(input_path: Path, target_path: Path, dry_run: bool = False) -> dict[str, int]:
    raw = load_raw_records(input_path)
    valid, rejected = validate_and_parse(raw)

    existing_map: dict[str, dict[str, str]] = {}
    if target_path.exists():
        with target_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get("unique_code", "").strip()
                if code:
                    existing_map[code] = dict(row)

    upsert_count = 0
    for rec in valid:
        code = rec.unique_code
        if code not in existing_map or existing_map[code] != rec.to_csv_dict():
            upsert_count += 1
        existing_map[code] = rec.to_csv_dict()

    if not dry_run:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for row_dict in existing_map.values():
                writer.writerow(row_dict)

    summary = {
        "processed": len(raw),
        "valid": len(valid),
        "rejected": len(rejected),
        "upserted": upsert_count,
        "total_target_records": len(existing_map),
    }

    logger.info("Import completed: %s", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Import and validate external EV dataset into OpenEV Data CSV.")
    parser.add_argument("--input-file", "-i", required=True, type=Path, help="Path to external CSV or JSON file")
    parser.add_argument(
        "--target-file",
        "-t",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "open-ev-data.csv",
        help="Path to target OpenEV CSV file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and simulate merge without writing")

    args = parser.parse_args()

    try:
        import_ev_dataset(args.input_file, args.target_file, dry_run=args.dry_run)
        return 0
    except Exception as e:
        logger.error("Failed to import EV dataset: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
