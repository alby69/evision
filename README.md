# EV Purchase Advisor

> **"If I buy this electric car instead of keeping my current car, how much does it really cost me, when do I break even, and what is the most economically sound decision?"**

An open-source decision support web application for evaluating the total financial impact and replacement economics of purchasing an electric vehicle (EV) compared to keeping a current internal combustion engine (ICE) vehicle or buying alternative vehicles.

---

## 🌟 Key Features

* **Authoritative Calculation Engine**: Pure Python domain engine calculating Total Cost of Ownership (TCO), incremental cost, operational vs. total break-even, battery degradation, and real-world range.
* **Smart Recommendation Engine**: Produces actionable, interpretable guidance (`STRONG_BUY`, `BUY`, `MAYBE`, `KEEP_CURRENT`, `AVOID`) with confidence levels, risk scores (0-100), and "Why it makes sense" / "Cautions" explanations.
* **Facts vs. Assumptions Transparency**: Explicit source tagging (`FACT`, `USER_INPUT`, `ESTIMATE`, `ASSUMPTION`) for every parameter and math breakdown.
* **Interactive Guided Wizard**: Accessible 5-step modal wizard (focus trap, Escape, clickable stepper, per-step validation) to enter current car, usage profile, candidate EV (with live catalog search), energy costs, maintenance/insurance/taxes, financing, and horizon.
* **Scenario & Sensitivity Simulator**: Pessimistic / Base / Optimistic scenario comparison (TCO, break-even, savings) plus a parameter sensitivity ranking with impact bars.
* **Modern Visualization**: Recharts charts for cumulative TCO curves, cost breakdown donut, real-world range vs. WLTP, and battery degradation over time.
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
                    │    PostgreSQL       │
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
    ├── App.tsx                 # Shell: header, hero verdict, KPIs, transparency, footer
    ├── index.css               # Theme tokens, `.btn`/`.field-*`/`.card-panel` components, print styles
    ├── components/
    │   ├── ui.tsx              # Primitives: Card, StatCard, Chip, Field, RangeSlider, ThemeToggle…
    │   ├── AnalysisWizard.tsx  # 5-step accessible modal wizard
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

### Configuration

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string. |
| `EV_CATALOG_API_KEY` | API key for the external EV catalog search (API Ninjas). Leave empty to fall back to built-in demo data. |
| `EV_CATALOG_API_URL` | Catalog endpoint URL (default: `https://api.api-ninjas.com/v1/electricvehicle`). |

Where to put the key (both files are **gitignored**):
* **Docker Compose**: root `.env` — compose interpolates it and passes `EV_CATALOG_API_KEY` to the backend container. Recreate the container after changing it: `docker compose up -d backend`.
* **Local backend** (`cd backend && uv run uvicorn ...`): `backend/.env` (pydantic-settings reads `.env` from the working directory).

> ⚠️ Never commit real API keys: `.env` / `backend/.env` are ignored; `.env.example` must keep the `your_api_key_here` placeholder.

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend
npm test            # unit tests (Vitest)
npx tsc --noEmit    # type check
npm run build       # production build (includes Tailwind/PostCSS pipeline)
```

> Note: `npm run lint` requires ESLint, which is not yet configured in this repository.

---

## 📄 Documentation

* [Architecture Overview](docs/architecture.md)
* [Financial & Math Calculations](docs/calculations.md)
* [API Specification](docs/api.md)
* [Project Roadmap](docs/roadmap.md)

---

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for details.
