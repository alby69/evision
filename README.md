# EV Purchase Advisor

> **"If I buy this electric car instead of keeping my current car, how much does it really cost me, when do I break even, and what is the most economically sound decision?"**

An open-source decision support web application for evaluating the total financial impact and replacement economics of purchasing an electric vehicle (EV) compared to keeping a current internal combustion engine (ICE) vehicle or buying alternative vehicles.

---

## 🌟 Key Features

* **Authoritative Calculation Engine**: Pure Python domain engine calculating Total Cost of Ownership (TCO), incremental cost, operational vs. total break-even, battery degradation, and real-world range.
* **Smart Recommendation Engine**: Produces actionable, interpretable guidance (`STRONG_BUY`, `BUY`, `MAYBE`, `KEEP_CURRENT`, `AVOID`) with confidence levels, risk scores (0-100), and "Why it makes sense" / "Cautions" explanations.
* **Facts vs. Assumptions Transparency**: Explicit source tagging (`FACT`, `USER_INPUT`, `ESTIMATE`, `ASSUMPTION`) for every parameter and math breakdown.
* **Interactive Guided Wizard**: 7-step progressive wizard to enter current car, usage profile, candidate EV, energy costs, maintenance/insurance/taxes/depreciation, financing, and horizon.
* **Scenario & Sensitivity Simulator**: Multi-scenario comparison (Base, Optimistic, Pessimistic) and interactive parameter sliders.
* **Modern Visualization**: Recharts charts for cumulative TCO curves, annual cash flow, cost breakdown donuts, and real-world range comparisons.
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

## 🚀 Quick Start

### Prerequisites
* [Docker](https://www.docker.com/) & Docker Compose
* Python 3.12+ (for local backend development)
* Node.js 22+ (for local frontend development)

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/example/ev-purchase-advisor.git
cd ev-purchase-advisor

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
python -m pytest
```

### Frontend Tests
```bash
cd frontend
npm test
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
