# API Specification Overview

The backend exposes a REST API compliant with OpenAPI 3.0 at `/api/v1`.
Interactive documentation is available at `http://localhost:8000/docs`.

## Endpoints Summary

### Vehicles (`/api/v1/vehicles`)
* `GET /api/v1/vehicles`: List demo and saved vehicles.
* `GET /api/v1/vehicles/catalog`: Search the EV catalog. Query params: `make`, `model`, `search`, `min_year`, `max_year`, `limit` (1–50, default 10). Results come primarily from the bundled **OpenEV Data** dataset (offline, ~490 variants across 65 makes), topped up with a curated demo catalog; the API Ninjas endpoint is queried only as a last resort when nothing matches. Range/consumption are taken from WLTP (EPA fallback) and consumption is derived from usable battery ÷ range when needed.
* `GET /api/v1/vehicles/car-facets`: Cascading dropdown values for the conventional (ICE) car catalog. Query param `facets` (comma-separated, max 6) among `make`, `model`, `generation`, `chassis_code`, `body`, `doors`, `fuel`, `transmission`, `drive`, `cylinders`, `year`, `badge`; optional narrowing params `make`, `model`, `generation`, `body`, `fuel`, `transmission`, `drive`, `year`. Uses the API Ninjas free-tier `/v2/carfacets`; falls back to built-in data when no key is configured.
* `GET /api/v1/vehicles/cars`: Look up conventional cars by `make` and `model` (optional `year`, `fuel_type`). Uses the API Ninjas free-tier `/v1/cars`; falls back to built-in data when no key is configured.
* `POST /api/v1/vehicles/valuation`: Estimate the current market value of a used car from comparable AutoScout24.it listings (RapidAPI "AutoScout24 Scraper"). Body: `{ make, model, year?, mileage?, fuel_type?, source? }`. Returns `{ estimated_value, trade_in_value, low_estimate, high_estimate, currency, sample_size, source, confidence, comparables }` with all values in EUR. The estimate is the robust median of asking prices for the same make/model/year, pre-filtered by mileage proximity when the odometer is known. Requires `RAPIDAPI_API_KEY`; answers `503` with a human-readable detail when unconfigured or no comparables are found.
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
