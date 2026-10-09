# API Specification Overview

The backend exposes a REST API compliant with OpenAPI 3.0 at `/api/v1`.
Interactive documentation is available at `http://localhost:8000/docs`.

## Endpoints Summary

### Vehicles (`/api/v1/vehicles`)
* `GET /api/v1/vehicles`: List demo and saved vehicles.
* `GET /api/v1/vehicles/catalog`: Search the external EV catalog. Query params: `make`, `model`, `search`, `min_year`, `max_year`, `limit` (1–50, default 10). Falls back to built-in demo data when `EV_CATALOG_API_KEY` is not configured.
* `POST /api/v1/vehicles`: Create custom vehicle.
* `GET /api/v1/vehicles/{vehicle_id}`: Get vehicle details.

### Calculations (`/api/v1/calculations`)
* `POST /api/v1/calculations/tco`: Calculate multi-year TCO for a vehicle.
* `POST /api/v1/calculations/break-even`: Calculate break-even comparing current car vs candidate car.
* `POST /api/v1/calculations/scenarios`: Pessimistic / Base / Optimistic scenario simulation.
* `POST /api/v1/calculations/sensitivity`: Compute parameter sensitivity analysis.

### Recommendations (`/api/v1/recommendation`)
* `POST /api/v1/recommendation`: Run complete decision support analysis and generate advice card.

### Scenarios & Comparison (`/api/v1/analyses`)
* `POST /api/v1/analyses`: Execute full analysis, persist it in-memory and return it with an `id` (`analysis-XXXXXXXX`).
* `GET /api/v1/analyses/demo`: Fetch ready-to-run demo analysis scenario (Honda CR-V vs. Renault Zoe).
* `GET /api/v1/analyses/{analysis_id}`: Retrieve a previously created analysis.

## Sharing Flow

1. The frontend calls `POST /api/v1/analyses` and receives an `id`.
2. The URL is updated to `?id=<analysis_id>`; the "Condividi" button copies it to the clipboard.
3. Opening a URL with `?id=...` replays the shared analysis via `GET /api/v1/analyses/{id}`.
