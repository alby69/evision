import React, { useState } from 'react';
import { ComparativeAnalysisResponse, RecommendationRating } from '../types/api';
import { Card, Chip, SectionHeader } from './ui';
import { Trophy, Check, AlertTriangle, TrendingUp, Route, Plug, Calendar, Sliders, ShieldAlert } from 'lucide-react';
import { AIAssistantWidget } from './AIAssistantWidget';
import { fmtDuration, fmtEUR, fmtNum, fmtPct, fmtSignedEUR } from '../utils/format';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

interface ComparativeAnalysisViewProps {
  analysis: ComparativeAnalysisResponse;
}

const CANDIDATE_COLORS = [
  '#059669', // Emerald
  '#2563eb', // Blue
  '#d97706', // Amber
  '#7c3aed', // Violet
  '#e11d48', // Rose
];

const CURRENT_CAR_COLOR = '#64748b'; // Slate

const RATING_LABELS: Record<RecommendationRating, { label: string; tone: 'emerald' | 'blue' | 'amber' | 'rose' }> = {
  [RecommendationRating.STRONG_BUY]: { label: 'Fortemente consigliato', tone: 'emerald' },
  [RecommendationRating.BUY]: { label: 'Consigliato', tone: 'emerald' },
  [RecommendationRating.MAYBE]: { label: 'Neutro / Da valutare', tone: 'amber' },
  [RecommendationRating.KEEP_CURRENT]: { label: 'Tieni auto attuale', tone: 'rose' },
  [RecommendationRating.AVOID]: { label: 'Sconsigliato', tone: 'rose' },
};

export const ComparativeAnalysisView: React.FC<ComparativeAnalysisViewProps> = ({ analysis }) => {
  const { current_vehicle, current_tco, comparisons, ownership, usage, charging } = analysis;

  // Weighted Scoring State (R5: Matrice Punteggio Ponderato)
  const [wSavings, setWSavings] = useState<number>(50);
  const [wRange, setWRange] = useState<number>(30);
  const [wRisk, setWRisk] = useState<number>(20);

  // Dynamic Weighted Score Calculator
  const getCandidateWeightedScore = (comp: typeof comparisons[0]): number => {
    const totalW = (wSavings + wRange + wRisk) || 100;
    const savings = Number(comp.break_even.cumulative_savings_over_horizon);
    const mixedRange = Number(comp.candidate_range.mixed_range_km);
    const riskScore = Number(comp.recommendation.risk_score);

    const normSavings = Math.max(0, Math.min(100, 50 + (savings / 200)));
    const normRange = Math.min(100, (mixedRange / 500) * 100);
    const normRisk = Math.max(0, 100 - riskScore);

    const score = (normSavings * wSavings + normRange * wRange + normRisk * wRisk) / totalW;
    return Math.round(score * 10) / 10;
  };

  // Determine overall winner based on custom Weighted Score (or rating fallback)
  let bestCandidateIndex = 0;
  let bestWeightedScore = -1;

  comparisons.forEach((comp, idx) => {
    const score = getCandidateWeightedScore(comp);
    if (score > bestWeightedScore) {
      bestWeightedScore = score;
      bestCandidateIndex = idx;
    }
  });

  const bestCandidate = comparisons[bestCandidateIndex];

  // Helper to identify best values across candidates for each KPI row
  const lowestCostPerKm = Math.min(...comparisons.map((c) => Number(c.candidate_tco.tco_per_km)));
  const highestSavings = Math.max(...comparisons.map((c) => Number(c.break_even.cumulative_savings_over_horizon)));
  const lowestBeYears = Math.min(
    ...comparisons
      .map((c) => c.break_even.operational_break_even_years)
      .filter((y): y is number => y != null)
  );
  const highestMixedRange = Math.max(...comparisons.map((c) => Number(c.candidate_range.mixed_range_km)));
  const lowestTotalTco = Math.min(...comparisons.map((c) => Number(c.candidate_tco.total_tco)));
  const lowestRiskScore = Math.min(...comparisons.map((c) => Number(c.recommendation.risk_score)));

  // Prepare chart data for multi-line Recharts cumulative TCO
  const yearsCount = ownership.horizon_years;
  const chartData = Array.from({ length: yearsCount }, (_, i) => {
    const yearNum = i + 1;
    const currentYearData = current_tco.yearly_breakdown.find((y) => y.year === yearNum);
    const row: Record<string, number | string> = {
      yearLabel: `Anno ${yearNum}`,
      Current: currentYearData ? Math.round(Number(currentYearData.cumulative_cost)) : 0,
    };

    comparisons.forEach((comp) => {
      const candYearData = comp.candidate_tco.yearly_breakdown.find((y) => y.year === yearNum);
      const candName = `${comp.candidate_vehicle.brand} ${comp.candidate_vehicle.model}`;
      row[candName] = candYearData ? Math.round(Number(candYearData.cumulative_cost)) : 0;
    });

    return row;
  });

  return (
    <div className="space-y-6 animate-fade-up">
      {/* Top Banner & Winner Highlight */}
      <Card className="overflow-hidden border-primary/30">
        <div className="p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="overline">Confronto Multiplo (1 vs {comparisons.length})</span>
                <Chip tone="emerald">
                  {comparisons.length} {comparisons.length === 1 ? 'Candidata' : 'Candidate'} EV
                </Chip>
              </div>
              <h2 className="mt-2 text-xl font-black tracking-tight sm:text-2xl">
                {current_vehicle.brand} {current_vehicle.model}{' '}
                <span className="font-normal text-muted-foreground">vs</span>{' '}
                {comparisons.map((c) => `${c.candidate_vehicle.brand} ${c.candidate_vehicle.model}`).join(' / ')}
              </h2>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <Chip tone="neutral">
                  <Calendar className="h-3 w-3" />
                  {ownership.horizon_years} anni
                </Chip>
                <Chip tone="neutral">
                  <Route className="h-3 w-3" />
                  {fmtNum(usage.annual_km)} km/anno
                </Chip>
                <Chip tone="neutral">
                  <Plug className="h-3 w-3" />
                  {fmtPct(charging.home_charging_percentage)} ricarica casa
                </Chip>
              </div>
            </div>

            {bestCandidate && (
              <div className="flex flex-col items-end rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-right">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-400">
                  <Trophy className="h-4 w-4" />
                  <span>Scelta Consigliata (Best Pick)</span>
                </div>
                <div className="mt-1 text-base font-extrabold text-foreground">
                  {bestCandidate.candidate_vehicle.brand} {bestCandidate.candidate_vehicle.model}
                </div>
                <div className="mt-0.5 text-xs text-muted-foreground">
                  Risparmio: {fmtSignedEUR(bestCandidate.break_even.cumulative_savings_over_horizon)} in {ownership.horizon_years} anni
                </div>
              </div>
            )}
          </div>

          {analysis.ai_summary_placeholder && (
            <div className="mt-4 rounded-xl border border-border bg-muted/30 p-4 text-xs leading-relaxed text-muted-foreground">
              {analysis.ai_summary_placeholder}
            </div>
          )}
        </div>
      </Card>

      {/* AI Assistant Q&A Widget (v0.5) */}
      <AIAssistantWidget analysisId={analysis.id} initialSummary={analysis.ai_summary_placeholder} />

      {/* Matrice Punteggio Ponderato (Weighted Scoring Matrix - R5) */}
      <Card className="p-5">
        <SectionHeader
          icon={<Sliders className="h-4 w-4" />}
          title="Matrice Punteggio Ponderato (Winner Score)"
          subtitle="Personalizza i pesi per rispecchiare le tue priorità (Risparmio, Autonomia e Sicurezza/Rischio) e ricalcolare il vincitore."
        />

        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-border bg-muted/20 p-3 space-y-1.5">
            <div className="flex justify-between text-xs font-bold">
              <span>Peso Risparmio TCO</span>
              <span className="text-primary">{wSavings}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={wSavings}
              onChange={(e) => setWSavings(Number(e.target.value))}
              className="w-full accent-primary cursor-pointer"
            />
          </div>

          <div className="rounded-xl border border-border bg-muted/20 p-3 space-y-1.5">
            <div className="flex justify-between text-xs font-bold">
              <span>Peso Autonomia</span>
              <span className="text-primary">{wRange}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={wRange}
              onChange={(e) => setWRange(Number(e.target.value))}
              className="w-full accent-primary cursor-pointer"
            />
          </div>

          <div className="rounded-xl border border-border bg-muted/20 p-3 space-y-1.5">
            <div className="flex justify-between text-xs font-bold">
              <span>Peso Sicurezza / Rischio</span>
              <span className="text-primary">{wRisk}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={wRisk}
              onChange={(e) => setWRisk(Number(e.target.value))}
              className="w-full accent-primary cursor-pointer"
            />
          </div>
        </div>
      </Card>

      {/* Side-by-Side KPI Table */}
      <Card className="p-5 overflow-hidden">
        <SectionHeader
          icon={<TrendingUp className="h-4 w-4" />}
          title="Tabella Comparativa KPI Side-by-Side"
          subtitle="Valori chiave a confronto diretto. I migliori KPI per ogni metrica sono evidenziati in verde."
        />

        <div className="mt-4 overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[700px] text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-border bg-muted/40 text-[11px] uppercase tracking-wide text-muted-foreground">
                <th className="p-3 font-bold">Parametro / Metrica</th>
                <th className="p-3 font-bold border-l border-border bg-muted/20">
                  {current_vehicle.brand} {current_vehicle.model}
                  <span className="block text-[10px] font-normal text-muted-foreground">Auto Attuale</span>
                </th>
                {comparisons.map((comp, idx) => {
                  const isWinner = idx === bestCandidateIndex;
                  return (
                    <th
                      key={idx}
                      className={`p-3 font-bold border-l border-border ${
                        isWinner ? 'bg-emerald-500/10 text-emerald-800 dark:text-emerald-300' : ''
                      }`}
                    >
                      <div className="flex items-center gap-1.5">
                        <span>
                          {comp.candidate_vehicle.brand} {comp.candidate_vehicle.model}
                        </span>
                        {isWinner && (
                          <span className="inline-flex items-center gap-0.5 rounded-full bg-emerald-600 px-1.5 py-0.5 text-[9px] font-bold text-white">
                            <Trophy className="h-2.5 w-2.5" /> Best
                          </span>
                        )}
                      </div>
                      <span className="block text-[10px] font-normal text-muted-foreground">Candidata {idx + 1}</span>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {/* Prezzo Acquisto / Valore */}
              <tr>
                <td className="p-3 font-semibold text-muted-foreground">Prezzo / Valore Acquisto</td>
                <td className="p-3 border-l border-border tabular-nums">
                  {fmtEUR(current_vehicle.current_value ?? current_vehicle.purchase_price)}
                </td>
                {comparisons.map((comp, idx) => (
                  <td key={idx} className="p-3 border-l border-border tabular-nums">
                    {fmtEUR(comp.candidate_vehicle.purchase_price)}
                  </td>
                ))}
              </tr>

              {/* Costo TCO Totale */}
              <tr className="bg-muted/10">
                <td className="p-3 font-semibold text-muted-foreground">TCO Totale ({ownership.horizon_years} anni)</td>
                <td className="p-3 border-l border-border tabular-nums font-semibold">
                  {fmtEUR(current_tco.total_tco)}
                </td>
                {comparisons.map((comp, idx) => {
                  const val = Number(comp.candidate_tco.total_tco);
                  const isBest = Math.abs(val - lowestTotalTco) < 0.01;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums font-semibold ${
                        isBest ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-extrabold' : ''
                      }`}
                    >
                      {fmtEUR(val)}
                    </td>
                  );
                })}
              </tr>

              {/* Costo al km */}
              <tr>
                <td className="p-3 font-semibold text-muted-foreground">Costo al Chilometro</td>
                <td className="p-3 border-l border-border tabular-nums">
                  {fmtEUR(current_tco.tco_per_km, 3)}/km
                </td>
                {comparisons.map((comp, idx) => {
                  const val = Number(comp.candidate_tco.tco_per_km);
                  const isBest = Math.abs(val - lowestCostPerKm) < 0.001;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums ${
                        isBest ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-extrabold' : ''
                      }`}
                    >
                      {fmtEUR(val, 3)}/km
                    </td>
                  );
                })}
              </tr>

              {/* Risparmio Cumulativo */}
              <tr className="bg-muted/10">
                <td className="p-3 font-semibold text-muted-foreground">Risparmio Cumulativo TCO</td>
                <td className="p-3 border-l border-border text-muted-foreground">—</td>
                {comparisons.map((comp, idx) => {
                  const val = Number(comp.break_even.cumulative_savings_over_horizon);
                  const isBest = Math.abs(val - highestSavings) < 0.01;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums font-bold ${
                        val >= 0 ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-700 dark:text-rose-400'
                      } ${isBest ? 'bg-emerald-500/15 font-extrabold' : ''}`}
                    >
                      {fmtSignedEUR(val)}
                    </td>
                  );
                })}
              </tr>

              {/* Break-even Operativo */}
              <tr>
                <td className="p-3 font-semibold text-muted-foreground">Break-Even Operativo</td>
                <td className="p-3 border-l border-border text-muted-foreground">—</td>
                {comparisons.map((comp, idx) => {
                  const years = comp.break_even.operational_break_even_years;
                  const isBest = years != null && Math.abs(years - lowestBeYears) < 0.05;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums ${
                        isBest ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-extrabold' : ''
                      }`}
                    >
                      {years != null ? fmtDuration(years) : 'Non raggiunto'}
                    </td>
                  );
                })}
              </tr>

              {/* Autonomia Reale Mista */}
              <tr className="bg-muted/10">
                <td className="p-3 font-semibold text-muted-foreground">Autonomia Mista Reale</td>
                <td className="p-3 border-l border-border text-muted-foreground">—</td>
                {comparisons.map((comp, idx) => {
                  const val = comp.candidate_range.mixed_range_km;
                  const isBest = Math.abs(val - highestMixedRange) < 1;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums ${
                        isBest ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-extrabold' : ''
                      }`}
                    >
                      {val.toFixed(0)} km
                    </td>
                  );
                })}
              </tr>

              {/* Autonomia Invernale Autostrada */}
              <tr>
                <td className="p-3 font-semibold text-muted-foreground">Autonomia Invernale Autostrada</td>
                <td className="p-3 border-l border-border text-muted-foreground">—</td>
                {comparisons.map((comp, idx) => {
                  const val = comp.candidate_range.winter_highway_range_km;
                  return (
                    <td key={idx} className="p-3 border-l border-border tabular-nums">
                      {val.toFixed(0)} km
                    </td>
                  );
                })}
              </tr>

              {/* Punteggio Ponderato / Winner Score (R5) */}
              <tr className="bg-muted/10 font-bold">
                <td className="p-3 font-extrabold text-foreground">Winner Score (0-100)</td>
                <td className="p-3 border-l border-border text-muted-foreground">—</td>
                {comparisons.map((comp, idx) => {
                  const score = getCandidateWeightedScore(comp);
                  const isBest = idx === bestCandidateIndex;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums text-base ${
                        isBest ? 'bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 font-black' : ''
                      }`}
                    >
                      {score}/100 {isBest && '🏆'}
                    </td>
                  );
                })}
              </tr>

              {/* Punteggio di Rischio */}
              <tr>
                <td className="p-3 font-semibold text-muted-foreground">Punteggio Rischio (0-100)</td>
                <td className="p-3 border-l border-border text-muted-foreground">—</td>
                {comparisons.map((comp, idx) => {
                  const score = comp.recommendation.risk_score;
                  const isBest = score === lowestRiskScore;
                  return (
                    <td
                      key={idx}
                      className={`p-3 border-l border-border tabular-nums ${
                        isBest ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-extrabold' : ''
                      }`}
                    >
                      {score}/100 ({comp.recommendation.risk_level})
                    </td>
                  );
                })}
              </tr>

              {/* Giudizio Finale */}
              <tr>
                <td className="p-3 font-semibold text-muted-foreground">Valutazione Motore</td>
                <td className="p-3 border-l border-border text-muted-foreground">Riferimento</td>
                {comparisons.map((comp, idx) => {
                  const r = RATING_LABELS[comp.recommendation.rating] || { label: 'N/D', tone: 'neutral' };
                  return (
                    <td key={idx} className="p-3 border-l border-border">
                      <Chip tone={r.tone}>{r.label}</Chip>
                    </td>
                  );
                })}
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Multi-Line Recharts TCO Chart */}
      <Card className="p-5">
        <SectionHeader
          icon={<TrendingUp className="h-4 w-4" />}
          title="Curve TCO Cumulate nel Tempo"
          subtitle="Confronto dell'evoluzione dei costi totali sostenuti anno dopo anno."
        />

        <div className="mt-4 h-72 sm:h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="yearLabel" stroke="currentColor" opacity={0.7} fontSize={12} />
              <YAxis
                stroke="currentColor"
                opacity={0.7}
                fontSize={12}
                tickFormatter={(v) => `€${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(value: number) => [fmtEUR(value), '']}
                labelStyle={{ fontWeight: 'bold' }}
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  borderColor: 'var(--border)',
                  borderRadius: '0.75rem',
                  fontSize: '0.75rem',
                }}
              />
              <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />

              {/* Current Car Line */}
              <Line
                type="monotone"
                dataKey="Current"
                name={`${current_vehicle.brand} ${current_vehicle.model} (Attuale)`}
                stroke={CURRENT_CAR_COLOR}
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 3 }}
              />

              {/* Candidate Lines */}
              {comparisons.map((comp, idx) => {
                const name = `${comp.candidate_vehicle.brand} ${comp.candidate_vehicle.model}`;
                const color = CANDIDATE_COLORS[idx % CANDIDATE_COLORS.length];
                const isWinner = idx === bestCandidateIndex;
                return (
                  <Line
                    key={idx}
                    type="monotone"
                    dataKey={name}
                    name={isWinner ? `${name} 🏆` : name}
                    stroke={color}
                    strokeWidth={isWinner ? 3 : 2}
                    dot={{ r: isWinner ? 5 : 3 }}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Candidate Detail Cards */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {comparisons.map((comp, idx) => {
          const isWinner = idx === bestCandidateIndex;
          const r = RATING_LABELS[comp.recommendation.rating];
          const redFlags = comp.recommendation.red_flags || [];
          const weightedScore = getCandidateWeightedScore(comp);

          return (
            <Card
              key={idx}
              className={`p-5 transition-colors ${
                isWinner ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-border'
              }`}
            >
              <div className="flex items-start justify-between gap-3 border-b border-border/60 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold">
                      {comp.candidate_vehicle.brand} {comp.candidate_vehicle.model}
                    </h3>
                    {isWinner && (
                      <Chip tone="emerald">
                        <Trophy className="h-3 w-3" /> Winner ({weightedScore}/100)
                      </Chip>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    Prezzo: {fmtEUR(comp.candidate_vehicle.purchase_price)} · Batteria: {comp.candidate_vehicle.usable_battery_capacity ?? comp.candidate_vehicle.battery_capacity ?? 'N/D'} kWh
                  </p>
                </div>
                <Chip tone={r.tone}>{r.label}</Chip>
              </div>

              <div className="mt-4 space-y-3">
                <p className="text-xs leading-relaxed text-muted-foreground">
                  {comp.recommendation.summary_text}
                </p>

                {/* Red Flags / Avvisi di Soglia */}
                {redFlags.length > 0 && (
                  <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-3 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-destructive">
                      <ShieldAlert className="h-4 w-4" />
                      <span>Alert di Soglia (Red Flags)</span>
                    </div>
                    {redFlags.map((rf, i) => (
                      <div key={i} className="text-xs">
                        <span className="font-bold">{rf.title}: </span>
                        <span className="text-muted-foreground">{rf.description}</span>
                      </div>
                    ))}
                  </div>
                )}

                {comp.recommendation.key_advantages.length > 0 && (
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                      Vantaggi principali
                    </span>
                    <ul className="mt-1 space-y-1">
                      {comp.recommendation.key_advantages.slice(0, 3).map((adv, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs">
                          <Check className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          <span>{adv}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {comp.recommendation.cautions_and_risks.length > 0 && (
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
                      Punti di attenzione
                    </span>
                    <ul className="mt-1 space-y-1">
                      {comp.recommendation.cautions_and_risks.slice(0, 2).map((c, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs">
                          <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0 mt-0.5" />
                          <span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default ComparativeAnalysisView;
