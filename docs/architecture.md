# EV Purchase Advisor Architecture

## Overview

EV Purchase Advisor is built with strict separation of concerns following Domain-Driven Design (DDD) principles:

```text
Calculation Engine (Pure Python Domain)
        ↓
Application Services / Repositories
        ↓
FastAPI REST API / CLI Interface
        ↓
Frontend Application (React + Vite + Tailwind CSS)
```

The core calculation engine is completely pure and decoupled from HTTP frameworks, ORMs, and user interfaces.

---

## Domain Model Architecture

1. **Vehicles (`backend/app/domain/models/vehicle.py`)**:
   - Generic vehicle representation supporting BEV, PHEV, HEV, PETROL, DIESEL, LPG, CNG.
   - Contains consumption parameters, battery capacities, range specs, purchase prices, residual values, and fixed costs (taxes, insurance, tires, maintenance).

2. **Usage Profile (`backend/app/domain/models/usage.py`)**:
   - Annual mileage, road distribution percentages (urban/city, extraurban, highway), seasonal multipliers, and long trip allocations.

3. **Charging & Fuel Profiles (`backend/app/domain/models/charging.py`)**:
   - `ChargingProfile`: energy prices (€/kWh), charging split (home, public AC, public DC fast charging), and charging loss percentages.
   - `FuelProfile`: fuel prices (€/l for petrol/diesel/LPG, €/kg for CNG) and expected annual growth rates.

4. **Ownership Scenario & Financing (`backend/app/domain/models/ownership.py`)**:
   - Ownership horizon in years, payment structure (cash, loan, balloon payment, interest rates, leasing: monthly fee and residual/balloon).

5. **Calculation Engine (`backend/app/domain/engine/`)**:
   - `tco_calculator.py`: Multi-year cumulative Total Cost of Ownership calculation (incl. leasing cash flow).
   - `break_even_calculator.py`: Operational and total ownership break-even timeline and mileage.
   - `range_calculator.py`: Real-world range per road type, winter highway range, and battery degradation curves.
   - `scenarios_calculator.py`: Pessimistic/Base/Optimistic scenario generation and parameter sensitivity factors.
   - `recommendation_engine.py`: Decision support engine producing ratings (`STRONG_BUY`, `BUY`, `MAYBE`, `KEEP_CURRENT`, `AVOID`), risk scores, confidence factors, and explanations.

---

## Backend Layers (`backend/app/`)

- **API** (`api/v1/`): FastAPI routers — `garage`, `vehicles`, `calculations`, `analyses`, `prices`. Request/response contracts live in `schemas/api_schemas.py`; the OpenAPI spec is served at `/openapi.json`.
- **Services** (`services/`):
  - `analysis_service.py`: orchestrates single and multi-car comparative analyses (`run_full_analysis`, `run_comparative_analysis`).
  - `energy_price_service.py`: fetches regional fuel (petrol, diesel, LPG, CNG) and electricity prices from MIMIT (Osservaprezzi Carburanti).
  - `ev_catalog_service.py`: EV catalog search. Primary source is the bundled OpenEV Data dataset (`ev_dataset.py`), topped up with a curated demo catalog; the external API Ninjas endpoint is only a last-resort fallback.
  - `car_catalog_service.py`: conventional (ICE) car lookup and cascading facet dropdowns via the API Ninjas free-tier endpoints.
  - `valuation_service.py`: used-car value estimate from comparable AutoScout24.it listings (RapidAPI "AutoScout24 Scraper").
- **Core** (`core/`): settings (`config.py`, env-driven), SQLAlchemy/PostgreSQL setup (`database.py`), demo seeds (`seed.py`).
- **Database Models** (`models/db_models.py`):
  - `SavedVehicle`: `saved_vehicles` table storing user's garage vehicles, names, default flags, and serialized specs.
  - `SavedAnalysis`: `saved_analyses` table storing persistent single and multi-car comparative analysis results.

---

## Frontend Architecture (`frontend/`)

- **Shell** (`src/App.tsx`): header (theme toggle, garage, history, share, PDF, new analysis), hero verdict, KPI cards, comparative side-by-side view, charts, footer; shareable state via `?id=...`.
- **Garage Manager** (`src/components/GarageManager.tsx`): modal drawer for CRUD operations on saved garage vehicles and selecting reference cars.
- **Multi-Car Selector** (`src/components/MultiCarSelector.tsx`): component allowing selection and specification of up to 5 EV candidate cars for simultaneous comparison.
- **Comparative Analysis View** (`src/components/ComparativeAnalysisView.tsx`): side-by-side KPI comparison table and multi-line Recharts TCO cumulative curves.
- **Wizard** (`components/AnalysisWizard.tsx`): 5-step modal dialog with fuel price inputs, MIMIT price auto-fetch, multi-car EV selection, and validation.
- **Charts** (`components/AnalysisCharts.tsx`): Recharts cumulative TCO, expense donut, real-world range, battery degradation.
- **Data layer**: `services/api.ts` (REST client), `types/api.ts` (shared contracts), `utils/format.ts` (it-IT formatters).
