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
