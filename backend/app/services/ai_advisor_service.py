import os
from decimal import Decimal
from typing import Any
import httpx

from app.core.config import settings


def _format_eur_str(val: float | int | Decimal) -> str:
    fval = float(val)
    sign = "-" if fval < 0 else ""
    abs_val = abs(fval)
    return f"{sign}€{abs_val:,.2f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Safely retrieves a value/attribute from either a dict or an object/Pydantic model."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        val = obj.get(key)
        return default if val is None else val
    if hasattr(obj, key):
        val = getattr(obj, key)
        return default if val is None else val
    return default


def _extract_analysis_metrics(data: dict[str, Any]) -> dict[str, Any]:
    """Extracts standardized metrics from either single or comparative analysis structures."""
    comps = _get(data, "comparisons")
    is_comparative = isinstance(comps, list) and len(comps) > 0

    curr_v = _get(data, "current_vehicle")
    curr_tco = _get(data, "current_tco")

    curr_brand = _get(curr_v, "brand", "")
    curr_model = _get(curr_v, "model", "")
    curr_name_from_v = f"{curr_brand} {curr_model}".strip() if (curr_brand or curr_model) else ""
    curr_name = curr_name_from_v or _get(curr_tco, "vehicle_name") or "l'auto attuale"

    usage = _get(data, "usage")
    annual_km = float(_get(usage, "annual_km", 20000))

    charging = _get(data, "charging")
    home_pct = float(_get(charging, "home_charging_percentage", 0.8)) * 100

    ownership = _get(data, "ownership")
    horizon = int(_get(ownership, "horizon_years", 5))

    if is_comparative and comps:
        # Find candidate with highest cumulative savings
        best_cand = None
        best_savings = -float("inf")
        for c in comps:
            be_tmp = _get(c, "break_even")
            sav_tmp = float(_get(be_tmp, "cumulative_savings_over_horizon", 0))
            if sav_tmp > best_savings:
                best_savings = sav_tmp
                best_cand = c
        if not best_cand:
            best_cand = comps[0]

        cand_v = _get(best_cand, "candidate_vehicle")
        cand_tco = _get(best_cand, "candidate_tco")
        be = _get(best_cand, "break_even")
        cand_range = _get(best_cand, "candidate_range")
        rec = _get(best_cand, "recommendation")
        all_candidates = [_get(c, "candidate_vehicle") for c in comps if _get(c, "candidate_vehicle")]
    else:
        cand_v = _get(data, "candidate_vehicle")
        cand_tco = _get(data, "candidate_tco")
        be = _get(data, "break_even")
        cand_range = _get(data, "candidate_range")
        rec = _get(data, "recommendation")
        all_candidates = [cand_v] if cand_v else []

    cand_brand = _get(cand_v, "brand", "")
    cand_model = _get(cand_v, "model", "")
    cand_name_from_v = f"{cand_brand} {cand_model}".strip() if (cand_brand or cand_model) else ""
    cand_name = cand_name_from_v or _get(cand_tco, "vehicle_name") or "l'auto elettrica"

    savings = float(_get(be, "cumulative_savings_over_horizon", 0))
    monthly_op_savings = float(_get(be, "monthly_operational_savings", 0))
    annual_op_savings = float(_get(be, "annual_operational_savings", monthly_op_savings * 12))
    be_years = _get(be, "operational_break_even_years")

    cand_energy_total = float(_get(cand_tco, "total_energy_fuel_cost", 0)) if cand_tco else 0.0
    curr_fuel_total = float(_get(curr_tco, "total_energy_fuel_cost", 0)) if curr_tco else 0.0

    cand_annual_energy = cand_energy_total / horizon if horizon > 0 else 0.0
    curr_annual_fuel = curr_fuel_total / horizon if horizon > 0 else 0.0

    mixed_range = float(_get(cand_range, "mixed_range_km", 300))
    extraurban_range = float(_get(cand_range, "extraurban_range_km", mixed_range))
    highway_range = float(_get(cand_range, "highway_range_km", 250))
    winter_range = float(_get(cand_range, "winter_highway_range_km", 200))
    urban_range = float(_get(cand_range, "urban_range_km", 350))

    return {
        "curr_v": curr_v,
        "curr_name": curr_name,
        "curr_tco": curr_tco,
        "cand_v": cand_v,
        "cand_name": cand_name,
        "cand_tco": cand_tco,
        "all_candidates": all_candidates,
        "is_comparative": is_comparative,
        "usage": usage,
        "annual_km": annual_km,
        "charging": charging,
        "home_pct": home_pct,
        "ownership": ownership,
        "horizon": horizon,
        "be": be,
        "be_years": be_years,
        "savings": savings,
        "monthly_op_savings": monthly_op_savings,
        "annual_op_savings": annual_op_savings,
        "cand_energy_total": cand_energy_total,
        "curr_fuel_total": curr_fuel_total,
        "cand_annual_energy": cand_annual_energy,
        "curr_annual_fuel": curr_annual_fuel,
        "mixed_range": mixed_range,
        "extraurban_range": extraurban_range,
        "highway_range": highway_range,
        "winter_range": winter_range,
        "urban_range": urban_range,
        "rec": rec,
    }


def generate_rule_based_explanation(data: dict[str, Any]) -> str:
    """Generates a rich, natural language Italian summary from structured analysis data."""
    m = _extract_analysis_metrics(data)

    if m["is_comparative"]:
        be_years = m["be_years"]
        if be_years is not None:
            be_m = round(be_years * 12)
            y = int(be_m // 12)
            rem_m = int(be_m % 12)
            be_text = f"circa {be_years:.1f} anni ({y} anni e {rem_m} mesi)" if y > 0 else f"circa {rem_m} mesi"
        else:
            be_text = "oltre la durata dell'orizzonte impostato"

        risk_score = _get(m["rec"], "risk_score", 0)

        summary = (
            f"Dall'analisi comparativa su un orizzonte di {m['horizon']} anni ({int(m['annual_km']):,} km/anno), "
            f"il modello evidenzia come la scelta migliore sia la **{m['cand_name']}**. "
            f"Rispetto a mantenere l'attuale {m['curr_name']}, passare a {m['cand_name']} genera un risparmio netto cumulato "
            f"stimato in **{_format_eur_str(m['savings'])}**, riducendo i costi operativi mensili di {_format_eur_str(m['monthly_op_savings'])}/mese "
            f"({_format_eur_str(m['annual_op_savings'])}/anno). "
            f"Il tempo di rientro operativo del capitale è stimato in {be_text}. "
            f"Il punteggio di rischio calcolato è di {risk_score}/100."
        )
        return summary

    be_years = m["be_years"]
    if be_years is not None:
        be_m = round(be_years * 12)
        y = int(be_m // 12)
        rem_m = int(be_m % 12)
        be_text = f"circa {be_years:.1f} anni ({y} anni e {rem_m} mesi)" if y > 0 else f"circa {rem_m} mesi"
    else:
        be_text = "non raggiunto entro l'orizzonte di analisi"

    rating = _get(m["rec"], "rating", "MAYBE")
    risk_score = _get(m["rec"], "risk_score", 20)

    if m["savings"] > 0:
        tone_text = f"un'opportunità finanziariamente molto conveniente, con un risparmio stimato di **{_format_eur_str(m['savings'])}** in {m['horizon']} anni"
    elif m["savings"] < 0:
        tone_text = f"un costo complessivo superiore di **{_format_eur_str(abs(m['savings']))}** rispetto al mantenimento dell'attuale {m['curr_name']}"
    else:
        tone_text = f"un impatto finanziario sostanzialmente neutro (differenza stimata {_format_eur_str(0)})"

    explanation = (
        f"L'analisi di sostituzione da {m['curr_name']} a **{m['cand_name']}** indica {tone_text}. "
        f"I costi operativi si riducono di circa **{_format_eur_str(m['monthly_op_savings'])} al mese** ({_format_eur_str(m['annual_op_savings'])}/anno), "
        f"portando il punto di pareggio (break-even) a {be_text}. "
        f"La valutazione complessiva è **{rating}** con un punteggio di rischio del **{risk_score}/100**."
    )
    return explanation


def generate_rule_based_qna(data: dict[str, Any], question: str) -> str:
    """Generates an informative, contextual response in Italian for user queries."""
    q_lower = question.lower().strip()
    m = _extract_analysis_metrics(data)

    # 1. Annual Energy / Fuel / Operating Costs Intent
    cost_keywords = ["spendo", "spesa", "costo anno", "costo annuo", "all'anno", "bolletta", "consumo di energia", "euro all'anno", "€/anno"]
    has_cost_kw = any(k in q_lower for k in cost_keywords)
    has_fuel_energy = any(k in q_lower for k in ["carburante", "diesel", "benzina", "elettrico", "elettrica", "energia"])
    has_question_cost = any(k in q_lower for k in ["quanto", "euro", "€", "costa", "spendo", "risparmio"])

    if has_cost_kw or (has_fuel_energy and has_question_cost and "tco" not in q_lower) or ("quanto" in q_lower and "risparmio" in q_lower and ("anno" in q_lower or "carburante" in q_lower)):
        if "risparmio" in q_lower and "spendo" not in q_lower:
            return (
                f"Con **{m['cand_name']}**, il risparmio stimato sui soli costi di energia e carburante è di circa "
                f"**{_format_eur_str(m['annual_op_savings'])}/anno** (pari a **{_format_eur_str(m['monthly_op_savings'])}/mese**). "
                f"Nel dettaglio, per percorrere {m['annual_km']:,.0f} km/anno, la spesa in carburante per la tua attuale **{m['curr_name']}** "
                f"è stimata in circa **{_format_eur_str(m['curr_annual_fuel'])}/anno**, mentre la spesa in ricarica elettrica per **{m['cand_name']}** "
                f"si attesta a circa **{_format_eur_str(m['cand_annual_energy'])}/anno** (assumendo il {m['home_pct']:.0f}% di ricarica domestica)."
            )
        else:
            monthly_energy = m['cand_annual_energy'] / 12.0
            return (
                f"Per percorrere {m['annual_km']:,.0f} km/anno con **{m['cand_name']}**, la spesa stimata in energia elettrica "
                f"è di circa **{_format_eur_str(m['cand_annual_energy'])}/anno** (pari a circa **{_format_eur_str(monthly_energy)}/mese**), "
                f"con una quota del {m['home_pct']:.0f}% di ricarica domestica. Rispetto ai circa **{_format_eur_str(m['curr_annual_fuel'])}/anno** "
                f"di carburante per la tua **{m['curr_name']}**, il risparmio in carburante/energia è di circa **{_format_eur_str(m['annual_op_savings'])}/anno**."
            )

    # 2. Break-Even Intent
    if any(k in q_lower for k in ["break even", "break-even", "rientro", "pareggio", "tempo", "in quanti anni", "quanti anni", "quando recupero", "ammortamento"]):
        be_years = m["be_years"]
        if be_years is not None:
            be_m = round(be_years * 12)
            y = int(be_m // 12)
            rem_m = int(be_m % 12)
            be_str = f"circa **{be_years:.1f} anni** ({y} anni e {rem_m} mesi)" if y > 0 else f"circa **{rem_m} mesi**"
        else:
            be_str = "non viene raggiunto entro l'orizzonte temporale selezionato"

        return (
            f"Il punto di pareggio operativo tra costi del carburante/manutenzione e costo dell'energia per **{m['cand_name']}** "
            f"viene raggiunto in {be_str}. Ogni mese risparmi circa **{_format_eur_str(m['monthly_op_savings'])}** sui soli costi di esercizio "
            f"(pari a **{_format_eur_str(m['annual_op_savings'])}/anno**)."
        )

    # 3. Model Recommendation / SUV / Selection Intent
    if any(k in q_lower for k in ["modello", "quale auto", "quale veicolo", "suv", "permuta", "budget", "sostituire", "trova", "scelta", "consigliami"]):
        if m["is_comparative"] and m["all_candidates"]:
            cand_names = ", ".join([f"**{_get(c, 'brand', '')} {_get(c, 'model', '')}**".strip() for c in m["all_candidates"] if _get(c, "brand") or _get(c, "model")])
            return (
                f"Dall'analisi comparativa effettuata per sostituire la tua **{m['curr_name']}**, i modelli valutati sono: {cand_names}. "
                f"La scelta migliore evidenziata dal motore è la **{m['cand_name']}**, che garantisce un risparmio netto cumulato di "
                f"**{_format_eur_str(m['savings'])}** in {m['horizon']} anni e un'autonomia reale mista di **{m['mixed_range']:.0f} km**."
            )
        else:
            return (
                f"Per la tua percorrenza di {m['annual_km']:,.0f} km/anno, la **{m['cand_name']}** è il modello analizzato per la sostituzione della tua **{m['curr_name']}**. "
                f"Offre un'autonomia reale nel ciclo misto di **{m['mixed_range']:.0f} km** (extraurbano: **{m['extraurban_range']:.0f} km**, autostrada invernale: **{m['winter_range']:.0f} km**) "
                f"e ti permette di risparmiare **{_format_eur_str(m['annual_op_savings'])}/anno** sui costi operativi."
            )

    # 4. Range & Driving Profile Intent
    if any(k in q_lower for k in ["autonomia", "inverno", "invernale", "autostrada", "viaggi", "km con un pieno", "carica", "extraurbano", "urbano", "velocità", "batteria"]):
        return (
            f"Per **{m['cand_name']}**, l'autonomia reale stimata nel profilo misto è di circa **{m['mixed_range']:.0f} km** (extraurbano: **{m['extraurban_range']:.0f} km**). "
            f"In condizioni invernali e a velocità autostradale (130 km/h), l'autonomia si attesta a circa **{m['winter_range']:.0f} km** (urbano: **{m['urban_range']:.0f} km**). "
            f"Per spostamenti extraurbani quotidiani, l'autonomia reale risponde ampiamente alle tue esigenze."
        )

    # 5. Charging & Tariff Intent
    if any(k in q_lower for k in ["ricarica", "casa", "domestica", "colonnina", "colonnine", "prezzo energia", "kw", "kwh", "caricare", "tariffa"]):
        return (
            f"Con la configurazione attuale, ricarichi al **{m['home_pct']:.0f}% a casa**. "
            f"La ricarica domestica è il fattore chiave che abbatte la spesa energetica a **{_format_eur_str(m['cand_annual_energy'])}/anno**. "
            f"Se la quota di ricarica alle colonnine pubbliche aumenta, il risparmio annuo diminuisce a causa delle tariffe superiori delle colonnine AC/DC."
        )

    # 6. Why / Rationale Intent
    if any(k in q_lower for k in ["perché", "perche", "consigli", "valutazione", "motivo", "giudizio", "conviene"]):
        if m["savings"] > 0:
            return (
                f"Consigliamo il passaggio a **{m['cand_name']}** principalement per il risparmio sui costi d'uso "
                f"(**{_format_eur_str(m['monthly_op_savings'])}/mese**, circa **{_format_eur_str(m['annual_op_savings'])}/anno**) ed un risparmio netto cumulato di "
                f"**{_format_eur_str(m['savings'])}** in {m['horizon']} anni. La quota di ricarica domestica ({m['home_pct']:.0f}%) "
                f"abbatte significativamente il costo per chilometro."
            )
        else:
            return (
                f"Attualmente mantenere **{m['curr_name']}** risulta più conveniente di **{_format_eur_str(abs(m['savings']))}** rispetto al passaggio a **{m['cand_name']}**. "
                f"Ciò è dovuto principalmente al prezzo d'acquisto o ammortamento del veicolo elettrico rispetto alla tua percorrenza di {m['annual_km']:,.0f} km/anno."
            )

    # 7. Generic Contextual Fallback
    return (
        f"Relativamente alla tua analisi per **{m['cand_name']}** vs **{m['curr_name']}**: "
        f"la spesa stimata in energia elettrica per l'EV è di **{_format_eur_str(m['cand_annual_energy'])}/anno** per {m['annual_km']:,.0f} km/anno "
        f"(risparmio netto cumulato di **{_format_eur_str(m['savings'])}** in {m['horizon']} anni). "
        f"L'autonomia reale mista è di **{m['mixed_range']:.0f} km** (invernale autostradale: **{m['winter_range']:.0f} km**)."
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
