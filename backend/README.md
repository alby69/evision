# EV Purchase Advisor — Backend

FastAPI backend for the EV Purchase Advisor decision engine.

## Structure

```text
app/
├── main.py                # FastAPI app entrypoint, CORS, /api/v1 router
├── cli.py                 # Standalone CLI around the domain engine
├── api/v1/                # Routers: vehicles, calculations, analyses
├── core/                  # config (env), database (SQLAlchemy/PostgreSQL), demo seeds
├── domain/
│   ├── models/            # Pydantic domain models (vehicle, usage, charging, ownership, results)
│   └── engine/            # Pure calculation engine (TCO, break-even, range, scenarios, recommendation)
├── schemas/               # API request/response contracts
└── services/              # analysis_service (full analysis), ev_catalog_service (catalog), ev_dataset (OpenEV dataset)
tests/                     # pytest suite (engine + API)
```

## Quick Start

```bash
# Install (uv) or: pip install -r requirements.txt
uv sync

# Run API (reload) — serves Swagger at http://localhost:8000/docs
uv run uvicorn app.main:app --reload

# Run tests
uv run python -m pytest
```

## Configuration

Environment variables are read via `app/core/config.py` (see repo-root `.env.example`):

* `DATABASE_URL` — PostgreSQL connection string.
* `EV_DATASET_PATH` — path to the bundled OpenEV Data CSV (primary, offline EV catalog; default `data/open-ev-data.csv`). Refresh it with `python backend/scripts/update_ev_dataset.py` (dataset © OpenEV Data contributors, CDLA-Permissive-2.0).
* `EV_CATALOG_API_KEY` — API Ninjas key for `GET /api/v1/vehicles/catalog` (optional last-resort fallback; dataset + demo catalog are used first).
* `EV_CATALOG_API_URL` — catalog endpoint override.
* `CAR_CATALOG_API_KEY` — API Ninjas key for the conventional (ICE) car selector; falls back to `EV_CATALOG_API_KEY` when empty.
* `CAR_FACETS_API_URL` — free-tier cascading dropdown endpoint (`/v2/carfacets`).
* `CAR_CATALOG_API_URL` — free-tier conventional car lookup endpoint (`/v1/cars`).
* `RAPIDAPI_API_KEY` — RapidAPI key for `POST /api/v1/vehicles/valuation` (used-car value estimate from comparable AutoScout24.it listings, via the "AutoScout24 Scraper"). Optional; the endpoint answers `503` when unset.
* `RAPIDAPI_AS24_URL` — RapidAPI scraper endpoint (default `https://autoscout24-scraper.p.rapidapi.com/get_page_source`).
* `AUTOSCOUT24_BASE_URL` — marketplace used to build the search page (default `https://www.autoscout24.it`).

Settings read `.env` from the **working directory**: place the key in `backend/.env` for local runs; Docker Compose passes it from the repo-root `.env`.

> Never commit real keys — both `.env` files are gitignored; `.env.example` keeps a placeholder.

## API

Full specification: [docs/api.md](../docs/api.md). Live docs at `/docs` when running.
