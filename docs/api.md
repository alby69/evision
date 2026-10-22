# API Specification Overview

The backend exposes a REST API compliant with OpenAPI 3.0 at `/api/v1`.
Interactive documentation is available at `http://localhost:8000/docs`.

## Endpoints Summary

### Garage (`/api/v1/garage`)
* `GET /api/v1/garage`: List all saved vehicles in the user's garage, ordered by default status and creation date.
* `POST /api/v1/garage`: Save a new vehicle into the garage (payload: `{ name, is_default, vehicle_data }`). Setting `is_default: true` automatically unsets default status on other saved vehicles.
* `GET /api/v1/garage/{vehicle_id}`: Retrieve details of a specific saved vehicle by ID.
* `PUT /api/v1/garage/{vehicle_id}`: Update a saved vehicle (name, default flag, or specs).
* `DELETE /api/v1/garage/{vehicle_id}`: Remove a vehicle from the garage.

### Vehicles (`/api/v1/vehicles`)
* `GET /api/v1/vehicles`: List demo and saved vehicles.
* `GET /api/v1/vehicles/catalog`: Search the EV catalog. Query params: `make`, `model`, `search`, `min_year`, `max_year`, `limit` (1–50, default 10). Results come primarily from the bundled **OpenEV Data** dataset (offline, ~490 variants across 65 makes), topped up with a curated demo catalog; the API Ninjas endpoint is queried only as a last resort when nothing matches.
* `GET /api/v1/vehicles/car-facets`: Cascading dropdown values for the conventional (ICE) car catalog.
* `GET /api/v1/vehicles/cars`: Look up conventional cars by `make` and `model` (optional `year`, `fuel_type`).
* `POST /api/v1/vehicles/valuation`: Estimate the current market value of a used car from comparable AutoScout24.it listings (RapidAPI "AutoScout24 Scraper"). Body: `{ make, model, year?, mileage?, fuel_type?, source? }`.

### Prices (`/api/v1/prices`)
* `GET /api/v1/prices/fuel`: Get current regional average fuel (petrol, diesel, LPG, CNG) and electricity prices (MIMIT Osservaprezzi Carburanti feed, NUTS-2 region parameter e.g. `IT-25` for Lombardia).

### Calculations & Analyses (`/api/v1/analyses`)
* `POST /api/v1/analyses`: Execute single-car decision analysis and persist it to PostgreSQL (`SavedAnalysis`), returning a `FullAnalysisResponse` with ID `analysis-XXXXXXXX`.
* `POST /api/v1/analyses/compare`: **Multi-Car Simultaneous Comparison (1 vs N)**: Execute decision analysis comparing 1 reference vehicle against up to 5 EV candidates simultaneously. Returns `ComparativeAnalysisResponse` containing parallel TCO, break-even, range, degradation, scenarios, and recommendation breakdowns for each candidate.
* `GET /api/v1/analyses`: List saved analyses summaries (`id`, `title`, `current_vehicle_name`, `candidate_count`, `created_at`).
* `GET /api/v1/analyses/demo`: Fetch ready-to-run demo analysis scenario (Honda CR-V vs. Renault Zoe).
* `GET /api/v1/analyses/{analysis_id}`: Retrieve a saved analysis by ID (single or comparative).
* `PUT /api/v1/analyses/{analysis_id}`: Rename/update a saved analysis title.
* `DELETE /api/v1/analyses/{analysis_id}`: Delete a saved analysis.

## Sharing & Persistence Flow

1. The frontend calls `POST /api/v1/analyses` or `POST /api/v1/analyses/compare` and persists the result to PostgreSQL.
2. The URL updates to `?id=<analysis_id>`; the "Condividi" button copies the link to the clipboard.
3. Opening a URL with `?id=...` replays the saved analysis directly via `GET /api/v1/analyses/{id}`.
