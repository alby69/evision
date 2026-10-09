# Calculation Engine Formulas & Financial Models

## 1. Energy & Fuel Cost Calculations

### Electric Vehicles (BEV)
$$\text{Annual Energy (kWh)} = \frac{\text{Annual km}}{100} \times \text{Weighted Consumption} \times (1 + \text{Charging Loss Ratio})$$

$$\text{Weighted Consumption} = (\% \text{City} \times C_{\text{city}} + \% \text{Extraurban} \times C_{\text{extraurban}} + \% \text{Highway} \times C_{\text{highway}}) \times \text{Seasonal Multiplier}$$

$$\text{Annual Energy Cost (€)} = \text{Annual Energy (kWh)} \times (\% \text{Home} \times P_{\text{home}} + \% \text{Public AC} \times P_{\text{AC}} + \% \text{Public DC} \times P_{\text{DC}})$$

### Combustion Engine Vehicles (ICE)
$$\text{Annual Fuel Cost (€)} = \frac{\text{Annual km}}{100} \times \text{Weighted Fuel Consumption} \times P_{\text{fuel}} \times (1 + \text{Fuel Growth Rate})^y$$

---

## 2. Total Cost of Ownership (TCO)

$$\text{TCO}(y) = \text{Net Purchase Cost} + \sum_{i=1}^{y} (\text{Energy/Fuel Cost}_i + \text{Financing}_i + \text{Maintenance}_i + \text{Insurance}_i + \text{Taxes}_i + \text{Tires}_i) - \text{Residual Value}(y)$$

Where:
* $\text{Net Purchase Cost} = \text{Gross Purchase Price} - \text{Incentives} - \text{Trade-in Value}$
* $\text{Residual Value}(y) = \text{Purchase Price} \times \text{Depreciation Curve}(y)$

---

## 3. Incremental Cost & Break-Even Analysis

$$\text{Incremental Cost}(y) = \text{TCO}_{\text{candidate}}(y) - \text{TCO}_{\text{current}}(y)$$

* **Operational Break-Even**: The point in time/mileage where cumulative operating savings (fuel/energy, maintenance, taxes) equal the difference in upfront cost.
* **Total Ownership Break-Even**: The exact point where $\text{Incremental Cost}(y) \le 0$.

---

## 4. Scenario Simulation

Each scenario re-runs the full TCO and break-even engines with multipliers applied to the candidate EV and price assumptions (`scenarios_calculator.simulate_scenarios`):

| Scenario | Energy (EV) | Fuel (ICE) | EV Maintenance | EV Depreciation |
|---|---|---|---|---|
| **Pessimistic** | ×1.30 (home & public) | ×0.90 | ×1.20 | modifier +0.20 |
| **Base** | — | — | — | — |
| **Optimistic** | ×0.90 (home) | ×1.15 | ×0.90 | — |

Outputs: `pessimistic_tco`, `base_tco`, `optimistic_tco`, and the corresponding operational break-even years/mileage per scenario.

---

## 5. Parameter Sensitivity

A static ranking of parameter impact on the TCO delta (`calculate_sensitivity_factors`), displayed as bars in the UI:

| Parameter | Impact score |
|---|---|
| Annual Mileage | 9.2 |
| Fuel Prices | 8.5 |
| Home Electricity Tariff | 7.8 |
| Vehicle Purchase Price | 6.5 |
| EV Depreciation Rate | 5.0 |
| Routine Maintenance Savings | 3.5 |

---

## 6. Recommendation Ratings & Risk

Rating thresholds over the ownership horizon ($\text{savings} = \text{TCO}_{\text{current}} - \text{TCO}_{\text{candidate}}$):

| Rating | Condition |
|---|---|
| `STRONG_BUY` | savings > €4 000 and operational break-even ≤ 75% of horizon |
| `BUY` | savings > €1 000 and operational break-even ≤ horizon |
| `MAYBE` | −€1 000 ≤ savings ≤ €1 000 |
| `KEEP_CURRENT` | savings < −€1 000 and EV upfront cost is higher |
| `AVOID` | otherwise |

**Risk score** accumulates weighted factors (e.g. winter highway range < 200 km → +15) and is clamped to 0–100:
`LOW` < 30, `MEDIUM` < 60, `HIGH` ≥ 60. **Confidence** starts at 0.85.

---

## 7. Battery Degradation & Real-World Range

* **Real-world range** per road type: $R = \frac{C_{\text{usable}}}{\text{consumption (kWh/100 km)}} \times 100$, computed for urban/extraurban/highway plus a mixed range weighted by the usage road split; winter highway range applies `winter_multiplier` to highway consumption.
* **Battery degradation** (iterative, per year):
  $\Delta C_y = C_{y-1} \times \left(d_{\text{year}} + \frac{\text{annual km}}{10\,000} \times d_{\text{km}}\right)$
  with $d_{\text{year}} = 1.5\%$ and $d_{\text{km}} = 0.5\%$ per 10 000 km, floored at 60% of the initial capacity ($C_y \ge 0.60 \times C_0$).
* Degraded ranges are reported as the mixed range scaled by the capacity ratio $C_y / C_0$.
