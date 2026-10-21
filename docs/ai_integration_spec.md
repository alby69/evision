# 🤖 EV Purchase Advisor - AI Advisor Integration Specification (v0.4 Roadmap)

## 📌 Executive Summary
This document defines the architectural specification and Knowledge Management schema for integrating an **AI Advisor (LLM)** into the EV Purchase Advisor decision support system.

To ensure pure Python domain logic and prevent LLM hallucinations or calculation drift, the calculation engine remains authoritative for all financial, TCO, break-even, and range computations. The AI Advisor acts as an **interpretable narrative layer**, transforming structured calculation outputs into personalized, human-centric guidance and interactive Q&A.

---

## 🏗️ Architectural Flow

```text
┌───────────────────────────┐     Structured Inputs     ┌───────────────────────────┐
│     User Decision Data    ├──────────────────────────►│   Authoritative Engine    │
│  (Car, Usage, Costs, ...) │                           │  (TCO, Break-Even, Range) │
└───────────────────────────┘                           └─────────────┬─────────────┘
                                                                      │
                                                           FullAnalysisResult
                                                                      │
                                                            to_llm_context()
                                                                      │
                                                                      ▼
┌───────────────────────────┐     System Prompt +      ┌───────────────────────────┐
│     User AI Interface     │◄─────────────────────────┤        LLM Service        │
│    (Explanations & Q&A)   │     Markdown Guidance    │    (OpenAI / Claude / v0.4)│
└───────────────────────────┘                          └───────────────────────────┘
```

---

## 📄 LLM Context Schema (`to_llm_context()`)

The `FullAnalysisResult` domain model exposes `to_llm_context(self) -> dict` in `backend/app/domain/models/analysis_result.py`. This method extracts semantic decision factors into a clean, LLM-ready JSON payload:

```json
{
  "title": "EV Replacement Decision Analysis",
  "comparison_pair": {
    "current_vehicle": "Honda CR-V (2016)",
    "candidate_vehicle": "Renault Zoe (2022)"
  },
  "horizon_years": 5,
  "usage_profile": {
    "annual_km": 25000.0,
    "city_percentage": 0.4,
    "highway_percentage": 0.2
  },
  "main_recommendation": {
    "rating": "STRONG_BUY",
    "confidence": 0.85,
    "risk_score": 25,
    "risk_level": "LOW",
    "summary": "Fortemente consigliato! Sostituire Honda CR-V con Renault Zoe dovrebbe far risparmiare €7.941,95 in 5 anni..."
  },
  "financial_summary": {
    "current_vehicle_tco_eur": 18450.0,
    "candidate_vehicle_tco_eur": 10508.05,
    "cumulative_savings_eur": 7941.95,
    "net_tco_difference_pct": -43.0,
    "candidate_cost_per_km_eur": 0.0841,
    "current_cost_per_km_eur": 0.1476
  },
  "break_even_timeline": {
    "operational_break_even_years": 2.4,
    "operational_break_even_km": 60000.0,
    "monthly_operational_savings_eur": 185.50
  },
  "real_world_range": {
    "mixed_range_km": 320.0,
    "winter_highway_range_km": 210.0,
    "usable_battery_kwh": 52.0
  },
  "key_advantages": [
    "Alta quota di ricarica a casa (80%): riduce drasticamente il costo per km.",
    "Percorrenza annua elevata (25.000 km/anno): accorcia il tempo di rientro."
  ],
  "cautions_and_risks": [],
  "scenario_sensitivity": {
    "pessimistic_tco_eur": 12100.0,
    "base_tco_eur": 10508.05,
    "optimistic_tco_eur": 9200.0,
    "top_sensitive_parameters": [
      {
        "parameter": "Costo dell'energia a casa",
        "impact_score": 8.5,
        "description": "Un aumento del +20% sulla tariffa di casa aumenta il TCO di €850."
      }
    ]
  }
}
```

---

## 🎯 System Prompt Strategy

When invoking the LLM in v0.4, the system prompt will follow this structure:

```text
Sei il Consulente EV di EV Purchase Advisor. Il tuo obiettivo è spiegare in modo chiaro,
empatico e rigoroso il risultato dell'analisi finanziaria a un guidatore che valuta di
passare all'auto elettrica.

LINEE GUIDA:
1. Basati ESCLUSIVAMENTE sui dati numerici e sulle metriche fornite nel contesto JSON.
2. Non inventare o alterare numeri, prezzi, risparmi o tempi di rientro.
3. Rispondi con un tono professionale ma accessibile, mettendo in evidenza i punti di forza e i rischi.
4. Se l'utente pone domande aggiuntive ("E se faccio più autostrada?"), rispondi spiegando la sensibilità dei parametri senza modificare i dati certificati dal motore.

CONTESTO DELL'ANALISI:
{llm_context_json}
```

---

## 🛣️ v0.4 Planned Endpoints

- `POST /api/v1/analyses/{id}/ai-explain`: Returns an AI-generated natural language report explaining the verdict, break-even timeline, and risk factors.
- `POST /api/v1/analyses/{id}/qna`: Interactive Q&A conversational endpoint where users can ask specific questions about their analysis.
