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

3. **Charging Profile (`backend/app/domain/models/charging.py`)**:
   - Energy prices (€/kWh), charging split (home, public AC, public DC fast charging), and charging loss percentages.

4. **Fuel Profile (`backend/app/domain/models/fuel.py`)**:
   - Fuel prices (€/l or €/kg) and expected annual growth rates.

5. **Ownership Scenario & Financing (`backend/app/domain/models/ownership.py`)**:
   - Ownership horizon in years, payment structure (cash, loan, balloon payment, interest rates).

6. **Calculation Engine (`backend/app/domain/engine/`)**:
   - `tco.py`: Multi-year cumulative Total Cost of Ownership calculation.
   - `break_even.py`: Operational and total ownership break-even timeline and mileage.
   - `battery.py`: Battery degradation curves and usable range over time.
   - `scenarios.py`: Pessimistic, Base, and Optimistic scenario generation.
   - `sensitivity.py`: Parameter sensitivity analysis.
   - `recommendation.py`: Decision support engine producing ratings (`STRONG_BUY`, `BUY`, `MAYBE`, `KEEP_CURRENT`, `AVOID`), risk scores, confidence factors, and explanations.
