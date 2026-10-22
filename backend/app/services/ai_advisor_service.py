import os
from typing import Any
import httpx

from app.core.config import settings


def _format_eur_str(val: float | int) -> str:
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    return f"{sign}€{abs_val:,.2f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def generate_rule_based_explanation(data: dict[str, Any]) -> str:
    """Generates a rich, natural language Italian summary from structured analysis data."""
    if "comparisons" in data and isinstance(data["comparisons"], list):
        # Comparative 1 vs N analysis
        curr = data.get("current_vehicle", {})
        curr_name = f"{curr.get('brand', 'Auto')} {curr.get('model', '')}".strip()
        comps = data["comparisons"]
        horizon = data.get("ownership", {}).get("horizon_years", 5)
        annual_km = data.get("usage", {}).get("annual_km", 20000)

        # Find best candidate
        best_cand = None
        best_savings = -float("inf")
        for c in comps:
          be = c.get("break_even", {})
          savings = float(be.get("cumulative_savings_over_horizon", 0))
          if savings > best_savings:
            best_savings = savings
            best_cand = c

        if not best_cand:
            return f"Analisi comparativa completata per l'auto attuale {curr_name}."

        cand_v = best_cand.get("candidate_vehicle", {})
        cand_name = f"{cand_v.get('brand', 'EV')} {cand_v.get('model', '')}".strip()
        be_obj = best_cand.get("break_even", {})
        be_years = be_obj.get("operational_break_even_years")
        op_savings = float(be_obj.get("monthly_operational_savings", 0))
        risk_score = best_cand.get("recommendation", {}).get("risk_score", 0)

        be_text = f"circa {be_years:.1f} anni" if be_years is not None else "oltre la durata dell'orizzonte impostato"

        summary = (
            f"Dall'analisi comparativa su un orizzonte di {horizon} anni ({int(annual_km):,} km/anno), "
            f"il modello evidenzia come la scelta migliore sia la **{cand_name}**. "
            f"Rispetto a mantenere l'attuale {curr_name}, passare a {cand_name} genera un risparmio netto cumulato "
            f"stimato in **{_format_eur_str(best_savings)}**, riducendo i costi operativi mensili di {_format_eur_str(op_savings)}/mese. "
            f"Il tempo di rientro operativo del capitale è stimato in {be_text}. "
            f"Il punteggio di rischio calcolato è di {risk_score}/100."
        )
        return summary.replace(",", ".")

    # Single analysis
    curr_v = data.get("current_vehicle", {})
    cand_v = data.get("candidate_vehicle", {})
    curr_name = f"{curr_v.get('brand', 'Auto')} {curr_v.get('model', '')}".strip()
    cand_name = f"{cand_v.get('brand', 'EV')} {cand_v.get('model', '')}".strip()

    horizon = data.get("ownership", {}).get("horizon_years", 5)
    be = data.get("break_even", {})
    savings = float(be.get("cumulative_savings_over_horizon", 0))
    op_savings = float(be.get("monthly_operational_savings", 0))
    be_years = be.get("operational_break_even_years")
    rec = data.get("recommendation", {})
    rating = rec.get("rating", "MAYBE")
    risk_score = rec.get("risk_score", 20)

    be_text = f"circa {be_years:.1f} anni" if be_years is not None else "non raggiunto entro l'orizzonte di analisi"

    if savings > 0:
        tone_text = f"un'opportunità finanziariamente molto conveniente, con un risparmio stimato di **{_format_eur_str(savings)}** in {horizon} anni"
    elif savings < 0:
        tone_text = f"un costo complessivo superiore di **{_format_eur_str(abs(savings))}** rispetto al mantenimento dell'attuale {curr_name}"
    else:
        tone_text = f"un impatto finanziario sostanzialmente neutro (differenza stimata {_format_eur_str(0)})"

    explanation = (
        f"L'analisi di sostituzione da {curr_name} a **{cand_name}** indica {tone_text}. "
        f"I costi operativi si riducono di circa **{_format_eur_str(op_savings)} al mese**, "
        f"portando il punto di pareggio (break-even) a {be_text}. "
        f"La valutazione complessiva è **{rating}** con un punteggio di rischio del **{risk_score}/100**."
    )
    return explanation


def generate_rule_based_qna(data: dict[str, Any], question: str) -> str:
    """Generates an informative, contextual response in Italian for user queries."""
    q_lower = question.lower()

    # Extract relevant details from data
    curr_v = data.get("current_vehicle", {})
    cand_v = data.get("candidate_vehicle", {})
    curr_name = f"{curr_v.get('brand', '')} {curr_v.get('model', '')}".strip() or "l'auto attuale"
    cand_name = f"{cand_v.get('brand', '')} {cand_v.get('model', '')}".strip() or "l'auto candidata"

    be = data.get("break_even", {})
    savings = float(be.get("cumulative_savings_over_horizon", 0))
    be_years = be.get("operational_break_even_years")
    op_savings = float(be.get("monthly_operational_savings", 0))

    range_data = data.get("candidate_range", {}) or data.get("comparisons", [{}])[0].get("candidate_range", {})
    mixed_range = range_data.get("mixed_range_km", 300)
    winter_range = range_data.get("winter_highway_range_km", 200)

    charging = data.get("charging", {})
    home_pct = float(charging.get("home_charging_percentage", 0.8)) * 100

    usage = data.get("usage", {})
    annual_km = usage.get("annual_km", 20000)

    if any(k in q_lower for k in ["perché", "perche", "consigli", "valutazione", "motivo", "giudizio"]):
        if savings > 0:
            return (
                f"Consigliamo il passaggio a **{cand_name}** principalmente per il risparmio sui costi d'uso "
                f"({_format_eur_str(op_savings)}/mese) ed un risparmio netto cumulato di {_format_eur_str(savings)} in "
                f"{data.get('ownership', {}).get('horizon_years', 5)} anni. La quota di ricarica domestica "
                f"({home_pct:.0f}%) abbatte significativamente il costo per chilometro."
            )
        else:
            return (
                f"Attualmente mantenere **{curr_name}** risulta più conveniente di {_format_eur_str(abs(savings))}. "
                f"Ciò è dovuto principalmente al prezzo d'acquisto o ammortamento del veicolo elettrico rispetto alla tua "
                f"percorrenza di {annual_km:,.0f} km/anno."
            )

    if any(k in q_lower for k in ["autonomia", "inverno", "autostrada", "viaggi", "km"]):
        return (
            f"Per **{cand_name}**, l'autonomia reale stimata nel profilo misto è di circa **{mixed_range:.0f} km**. "
            f"In condizioni invernali e a velocità autostradale (130 km/h), l'autonomia si attesta a circa **{winter_range:.0f} km**. "
            f"Per viaggi superiori a questa soglia sarà necessario programmare una sosta di ricarica fast DC."
        )

    if any(k in q_lower for k in ["ricarica", "casa", "colonnina", "prezzo", "costo energia", "bolletta"]):
        return (
            f"Con la configurazione attuale, ricarichi al **{home_pct:.0f}% a casa**. "
            f"La ricarica domestica è il principale fattore di risparmio dell'EV. Se la quota di ricarica alle colonnine "
            f"pubbliche aumenta, il risparmio mensile diminuisce a causa delle tariffe più elevate delle colonnine AC/DC."
        )

    if any(k in q_lower for k in ["break even", "rientro", "pareggio", "tempo", "anni"]):
        be_str = f"circa **{be_years:.1f} anni**" if be_years else "non viene raggiunto nell'orizzonte temporale selezionato"
        return (
            f"Il punto di pareggio operativo tra costi del carburante/manutenzione e costo dell'energia viene raggiunto in {be_str}. "
            f"Ogni mese risparmi circa {_format_eur_str(op_savings)} sui soli costi di esercizio."
        )

    # Generic contextual response
    return (
        f"Relativamente alla tua analisi per **{cand_name}** vs **{curr_name}**: "
        f"il risparmio totale stimato è di {_format_eur_str(savings)} su {data.get('ownership', {}).get('horizon_years', 5)} anni. "
        f"I principali fattori che influenzano l'analisi sono la percorrenza annua ({annual_km:,.0f} km), "
        f"la quota di ricarica domestica ({home_pct:.0f}%) e l'autonomia invernale autostradale ({winter_range:.0f} km)."
    )


async def generate_ai_explanation(analysis_data: dict[str, Any]) -> str:
    """Generates an AI narrative explanation for an analysis.

    Uses OpenAI API if OPENAI_API_KEY is configured, else falls back to rule-based engine.
    """
    api_key = getattr(settings, "OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return generate_rule_based_explanation(analysis_data)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Sei il Consulente EV di EV Purchase Advisor. Genera una sintesi chiara, "
                                "empatica ed esplicativa in lingua italiana spiegando le ragioni finanziarie, "
                                "l'autonomia e i fattori di rischio dell'analisi fornita in JSON."
                            ),
                        },
                        {"role": "user", "content": f"Analisi JSON:\n{analysis_data}"},
                    ],
                    "temperature": 0.5,
                    "max_tokens": 300,
                },
            )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json["choices"][0]["message"]["content"]
                return str(content).strip()
    except Exception:
        pass

    return generate_rule_based_explanation(analysis_data)


async def answer_qna(analysis_data: dict[str, Any], question: str) -> str:
    """Answers a user question about their analysis using OpenAI or rule-based fallback."""
    api_key = getattr(settings, "OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return generate_rule_based_qna(analysis_data, question)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Sei il Consulente EV di EV Purchase Advisor. Rispondi alla domanda dell'utente in modo preciso "
                                "e sintetico in italiano, basandoti esclusivamente sui dati dell'analisi fornita."
                            ),
                        },
                        {"role": "user", "content": f"Dati Analisi: {analysis_data}\n\nDomanda utente: {question}"},
                    ],
                    "temperature": 0.5,
                    "max_tokens": 300,
                },
            )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json["choices"][0]["message"]["content"]
                return str(content).strip()
    except Exception:
        pass

    return generate_rule_based_qna(analysis_data, question)
