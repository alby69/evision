# EV Purchase Advisor

> **"If I buy this electric car instead of keeping my current car, how much does it really cost me, when do I break even, and what is the most economically sound decision?"**

An open-source decision support web application for evaluating the total financial impact and replacement economics of purchasing an electric vehicle (EV) compared to keeping a current internal combustion engine (ICE) vehicle or buying alternative vehicles.

---

## 🌟 Key Features

* **Authoritative Calculation Engine**: Pure Python domain engine calculating Total Cost of Ownership (TCO), incremental cost, operational vs. total break-even, battery degradation, and real-world range.
* **My Garage & Persistent History**: Save your reference vehicles permanently in PostgreSQL ("My Garage"), set default vehicles, and retrieve, rename, or delete past saved analyses.
* **Multi-Car Simultaneous Comparison (1 vs N)**: Compare 1 owned/reference vehicle against up to 5 candidate EVs simultaneously with side-by-side KPI tables with automatic best value highlighting, multi-line Recharts TCO cumulative curves, and a recommendation Winner Badge.
* **Live Fuel & Energy Price Integration**: Fetch current regional fuel prices (Petrol, Diesel, LPG, CNG) and home electricity tariffs directly from the MIMIT (Osservaprezzi Carburanti) Open Data feed or configure them manually.
* **Smart Recommendation Engine**: Produces actionable, interpretable guidance (`STRONG_BUY`, `BUY`, `MAYBE`, `KEEP_CURRENT`, `AVOID`) with confidence levels, risk scores (0-100), and "Why it makes sense" / "Cautions" explanations.
* **Facts vs. Assumptions Transparency**: Explicit source tagging (`FACT`, `USER_INPUT`, `ESTIMATE`, `ASSUMPTION`) for every parameter and math breakdown.
* **Interactive Guided Wizard**: Accessible 5-step modal wizard (focus trap, Escape, clickable stepper, per-step validation) to enter current car, usage profile, candidate EVs (with live catalog search), energy/fuel costs, maintenance/insurance/taxes, financing, and horizon.
* **Live Vehicle Catalogs**: Candidate EVs are searched against the bundled **OpenEV Data** dataset (offline, ~490 variants) topped up with a curated demo catalog and API Ninjas as a last resort; conventional (ICE) cars use the API Ninjas free-tier lookup and cascading facets.
* **Used-Car Valuation**: Optional on-demand market/trade-in estimate for the current car from comparable **AutoScout24.it** listings (RapidAPI "AutoScout24 Scraper"), auto-filled when a car is selected or triggered manually with `POST /api/v1/vehicles/valuation`.
* **Scenario & Sensitivity Simulator**: Pessimistic / Base / Optimistic scenario comparison (TCO, break-even, savings) plus a parameter sensitivity ranking with impact bars.
* **Modern Visualization**: Recharts charts for multi-car cumulative TCO curves, cost breakdown donut, real-world range vs. WLTP, and battery degradation over time.
* **Polished UI/UX**: Reusable design system (cards, chips, stats, form fields), light & dark theme with persistence, entrance animations, loading/error states with retry, progress bar, and shareable analysis links (`?id=...`) with PDF export via print stylesheet.
* **Accessible & Responsive**: WCAG AA color contrast verified in both themes, keyboard navigation, ARIA labelling, touch targets ≥ 40 px, and no horizontal overflow from 360 px to 1920 px.
* **API-First & CLI Ready**: REST API built with FastAPI and OpenAPI auto-generated documentation, plus a standalone CLI tool.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       Browser       │
                    │   React + Vite      │
                    └──────────┬──────────┘
                               │
                             REST
                               │
                    ┌──────────▼──────────┐
                    │      FastAPI        │
                    │       API           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Domain / Engine   │
                    │                     │
                    │  TCO Calculator     │
                    │  EV & ICE Models    │
                    │  Break-Even Engine  │
                    │  Recommendation     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Database       │
                    │  PostgreSQL / DB    │
                    └─────────────────────┘
```

---

## 🧩 Frontend Structure

```text
frontend/
├── index.html                  # Anti-flash theme init, meta, favicon
├── postcss.config.js           # Tailwind + Autoprefixer pipeline (required!)
├── tailwind.config.js          # Design tokens (HSL), animations, shadows
├── public/favicon.svg
└── src/
    ├── App.tsx                 # Shell: header, garage manager, history modal, verdict hero, KPIs
    ├── index.css               # Theme tokens, `.btn`/`.field-*`/`.card-panel` components, print styles
    ├── components/
    │   ├── ui.tsx              # Primitives: Card, StatCard, Chip, Field, RangeSlider, ThemeToggle…
    │   ├── AnalysisWizard.tsx  # 5-step accessible modal wizard with fuel price controls
    │   ├── GarageManager.tsx   # My Garage modal drawer (CRUD, default vehicle selection)
    │   ├── MultiCarSelector.tsx# Multi-car EV selection component (1-5 candidates)
    │   ├── ComparativeAnalysisView.tsx # Side-by-side KPI table and multi-line Recharts TCO chart
    │   ├── AnalysisCharts.tsx  # TCO, donut, range, battery degradation charts
    │   ├── ScenarioInsights.tsx# Pessimistic/Base/Optimistic scenarios + sensitivity bars
    │   ├── RecommendationBadge.tsx
    │   └── EVSearchSelect.tsx  # Accessible combobox for catalog search
    ├── utils/format.ts         # it-IT formatters (currency, km, %)
    ├── services/api.ts         # REST client (`/api/v1`)
    └── types/api.ts            # Shared TypeScript contracts
```

---

## 🚀 Quick Start

### Prerequisites
* [Docker](https://www.docker.com/) & Docker Compose
* Python 3.12+ (for local backend development)
* Node.js 22+ (for local frontend development)

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/alby69/evision.git
cd evision

# Start backend, frontend, and PostgreSQL database
docker compose up --build
```

Access the services:
* **Frontend Application**: `http://localhost:5173`
* **FastAPI Backend & Interactive API Docs**: `http://localhost:8000/docs`

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Tests
```bash
cd frontend
npm test            # unit tests (Vitest)
npm run build       # production build
```

---

## 📄 Documentation

* [Architecture Overview](docs/architecture.md)
* [Financial & Math Calculations](docs/calculations.md)
* [API Specification](docs/api.md)
* [Project Roadmap](docs/roadmap.md)

---

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for details.
