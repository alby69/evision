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
   - `FuelProfile`: fuel prices (€/l or €/kg) and expected annual growth rates.

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

- **API** (`api/v1/`): FastAPI routers — `vehicles`, `calculations`, `analyses`. Request/response contracts live in `schemas/api_schemas.py`; the OpenAPI spec is served at `/openapi.json`.
- **Services** (`services/`):
  - `analysis_service.py`: orchestrates the full analysis (TCO, break-even, scenarios, sensitivity, recommendation) in one call.
  - `ev_catalog_service.py`: EV catalog search. Primary source is the bundled OpenEV Data dataset (`ev_dataset.py`), topped up with a curated demo catalog; the external API Ninjas endpoint is only a last-resort fallback.
  - `car_catalog_service.py`: conventional (ICE) car lookup and cascading facet dropdowns via the API Ninjas free-tier endpoints, with a built-in fallback when no key is configured.
  - `valuation_service.py`: used-car value estimate from comparable AutoScout24.it listings (RapidAPI "AutoScout24 Scraper"); scrapes the search page, parses listing attributes and returns a robust median plus a trade-in estimate.
- **Core** (`core/`): settings (`config.py`, env-driven), SQLAlchemy/PostgreSQL setup (`database.py`), demo seeds (`seed.py`).
- **CLI** (`cli.py`): standalone command-line interface to the engine.
- **Persistence note**: vehicle records and saved analyses are currently kept in-memory per process; PostgreSQL models/Alembic remain for the persistent domain data.

---

## Frontend Architecture (`frontend/`)

- **Shell** (`src/App.tsx`): header (theme toggle, share, PDF, new analysis), hero verdict, KPI cards, scenarios, transparency table, charts, footer; shareable state via `?id=...`.
- **Design system** (`src/components/ui.tsx` + `src/index.css` + `tailwind.config.js`):
  - Design tokens as HSL variables with `<alpha-value>` (light + `.dark` class).
  - Shared primitives: `Card`, `SectionHeader`, `StatCard`, `Chip`, `Field`/inputs, `RangeSlider`, `InfoHint`, `ThemeToggle`, plus `.btn-*` / `.field-input` / `.card-panel` utility components.
  - `postcss.config.js` wires Tailwind + Autoprefixer — **without it Tailwind is never processed**.
- **Wizard** (`components/AnalysisWizard.tsx`): 5-step modal dialog with focus trap, per-step validation, clickable stepper, percent-sum checks (values stored as 0–1 decimals, displayed 0–100).
- **Charts** (`components/AnalysisCharts.tsx`): Recharts cumulative TCO, expense donut, real-world range, battery degradation.
- **Insights** (`components/ScenarioInsights.tsx`): pessimistic/base/optimistic scenarios and sensitivity ranking.
- **Data layer**: `services/api.ts` (REST client), `types/api.ts` (shared contracts), `utils/format.ts` (it-IT formatters).
- **Accessibility**: skip link, `aria-live` feedback, labelled controls, accessible combobox (`EVSearchSelect`), WCAG AA contrast verified in both themes, touch targets ≥ 40 px.
