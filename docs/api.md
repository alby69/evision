# API Specification Overview

The backend exposes a REST API compliant with OpenAPI 3.0 at `/api/v1`.

## Endpoints Summary

### Vehicles (`/api/v1/vehicles`)
* `GET /api/v1/vehicles`: List demo and saved vehicles.
* `POST /api/v1/vehicles`: Create custom vehicle.
* `GET /api/v1/vehicles/{id}`: Get vehicle details.

### Calculations (`/api/v1/calculations`)
* `POST /api/v1/calculations/tco`: Calculate multi-year TCO for a vehicle.
* `POST /api/v1/calculations/break-even`: Calculate break-even comparing current car vs candidate car.
* `POST /api/v1/calculations/sensitivity`: Compute parameter sensitivity analysis.

### Recommendations (`/api/v1/recommendation`)
* `POST /api/v1/recommendation`: Run complete decision support analysis and generate advice card.

### Scenarios & Comparison (`/api/v1/analyses`)
* `POST /api/v1/analyses`: Create full saved analysis.
* `GET /api/v1/analyses/demo`: Fetch ready-to-run demo analysis scenario (Honda CR-V vs. Renault Zoe).
