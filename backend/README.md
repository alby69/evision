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
└── services/              # analysis_service (full analysis), ev_catalog_service (catalog proxy)
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
* `EV_CATALOG_API_KEY` — API Ninjas key for `GET /api/v1/vehicles/catalog` (optional; demo data used when empty).
* `EV_CATALOG_API_URL` — catalog endpoint override.

Settings read `.env` from the **working directory**: place the key in `backend/.env` for local runs; Docker Compose passes it from the repo-root `.env`.

> Never commit real keys — both `.env` files are gitignored; `.env.example` keeps a placeholder.

## API

Full specification: [docs/api.md](../docs/api.md). Live docs at `/docs` when running.
