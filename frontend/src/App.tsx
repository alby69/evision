import React, { useEffect, useRef, useState } from 'react';
import { FullAnalysisResponse, ValueExplanation } from './types/api';
import { fetchDemoAnalysis, createAnalysis, fetchAnalysisById } from './services/api';
import { RecommendationBadge } from './components/RecommendationBadge';
import { AnalysisCharts } from './components/AnalysisCharts';
import { ScenarioInsights } from './components/ScenarioInsights';
import { AnalysisWizard, AnalysisPayload } from './components/AnalysisWizard';
import { Card, StatCard, SectionHeader, Chip, ThemeToggle, InfoHint } from './components/ui';
import {
  Zap,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  SlidersHorizontal,
  Calculator,
  Share2,
  FileText,
  Check,
  X,
  TrendingUp,
  Timer,
  Fuel,
  AlertTriangle,
  Loader2,
  Calendar,
  Route,
  Plug,
} from 'lucide-react';
import { fmtEUR, fmtNum, fmtPct, fmtSignedEUR, fmtYears } from './utils/format';

type AnalysisSource = 'demo' | 'saved' | 'custom';

const riskTone: Record<'LOW' | 'MEDIUM' | 'HIGH', 'emerald' | 'amber' | 'rose'> = {
  LOW: 'emerald',
  MEDIUM: 'amber',
  HIGH: 'rose',
};

const sourceTone: Record<ValueExplanation['source'], 'emerald' | 'blue' | 'amber' | 'neutral'> = {
  FACT: 'emerald',
  USER_INPUT: 'blue',
  ESTIMATE: 'amber',
  ASSUMPTION: 'neutral',
};

const sourceLabels: Record<ValueExplanation['source'], string> = {
  FACT: 'Dato reale',
  USER_INPUT: 'Tuo dato',
  ESTIMATE: 'Stima',
  ASSUMPTION: 'Assunzione',
};

export const App: React.FC = () => {
  const [analysis, setAnalysis] = useState<FullAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showWizard, setShowWizard] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [source, setSource] = useState<AnalysisSource>('demo');
  const [savedId, setSavedId] = useState<string | null>(null);

  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const analysisId = params.get('id');
    if (analysisId) {
      loadSavedAnalysis(analysisId);
    } else {
      loadDemoAnalysis();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDemoAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDemoAnalysis();
      setAnalysis(data);
      setSource('demo');
      setSavedId(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Impossibile caricare l’analisi dimostrativa.');
    } finally {
      setLoading(false);
    }
  };

  const loadSavedAnalysis = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAnalysisById(id);
      setAnalysis(data);
      setSource('saved');
      setSavedId(id);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : 'Impossibile caricare l’analisi condivisa. Il link potrebbe essere scaduto.',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (source === 'saved' && savedId) loadSavedAnalysis(savedId);
    else loadDemoAnalysis();
  };

  const handleCustomAnalysis = async (payload: AnalysisPayload) => {
    setLoading(true);
    setError(null);
    try {
      const data = await createAnalysis(payload);
      setAnalysis(data);
      setSource('custom');
      setSavedId(data.id ?? null);
      setShowWizard(false);
      if (data.id) {
        window.history.pushState({}, '', `?id=${data.id}`);
      }
      requestAnimationFrame(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Errore nel calcolo dell’analisi. Controlla i dati e riprova.');
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    if (!analysis?.id) return;
    const shareUrl = `${window.location.origin}${window.location.pathname}?id=${analysis.id}`;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch {
      window.prompt('Copia il link per condividere l’analisi:', shareUrl);
    }
  };

  const handleExportPdf = () => {
    window.print();
  };

  const sourceChip = () => {
    if (source === 'demo')
      return (
        <Chip
          tone="amber"
          title="Dati di esempio precaricati: avvia una nuova analisi per usare i tuoi numeri."
        >
          Esempio dimostrativo
        </Chip>
      );
    if (source === 'saved') return <Chip tone="blue">Analisi condivisa</Chip>;
    return <Chip tone="emerald">La tua analisi</Chip>;
  };

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70] focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-primary-foreground"
      >
        Vai al contenuto
      </a>

      {loading && (
        <div className="fixed left-0 top-0 z-[60] h-1 w-full overflow-hidden bg-primary/15 print:hidden" aria-hidden="true">
          <div className="h-full w-1/3 animate-indeterminate rounded-full bg-primary" />
        </div>
      )}

      {/* Top navigation */}
      <header className="sticky top-0 z-40 border-b border-border/70 bg-card/85 backdrop-blur-xl print:hidden">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-2.5">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm">
              <Zap className="h-5 w-5" />
            </span>
            <div className="leading-tight">
              <h1 className="text-sm font-extrabold tracking-tight sm:text-base">EV Purchase Advisor</h1>
              <p className="hidden text-[11px] text-muted-foreground sm:block">
                Conviene davvero passare all’elettrico?
              </p>
            </div>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <ThemeToggle />

            {analysis && (
              <>
                <button
                  onClick={handleShare}
                  className="btn-outline h-10 px-3 sm:px-3.5"
                  aria-label="Copia il link per condividere l’analisi"
                  title="Copia link di condivisione"
                >
                  {copied ? <Check className="h-4 w-4 text-emerald-700" /> : <Share2 className="h-4 w-4" />}
                  <span className="hidden sm:inline">{copied ? 'Copiato!' : 'Condividi'}</span>
                </button>

                <button
                  onClick={handleExportPdf}
                  className="btn-outline h-10 px-3 sm:px-3.5"
                  aria-label="Esporta il report in PDF"
                  title="Esporta report PDF"
                >
                  <FileText className="h-4 w-4" />
                  <span className="hidden sm:inline">PDF</span>
                </button>
              </>
            )}

            <button
              onClick={() => setShowWizard(true)}
              className="btn-primary h-10 px-3.5 sm:px-4"
              aria-label="Avvia una nuova analisi"
            >
              <SlidersHorizontal className="h-4 w-4" />
              <span className="hidden sm:inline">Nuova analisi</span>
            </button>
          </div>
        </div>
      </header>

      <main id="main" className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
        {error && (
          <div
            role="alert"
            className="mb-6 flex flex-wrap items-center gap-3 rounded-xl border border-destructive/50 bg-destructive/10 p-4 text-destructive"
          >
            <AlertTriangle className="h-5 w-5 shrink-0" aria-hidden="true" />
            <span className="min-w-0 flex-1 text-sm font-medium">{error}</span>
            <button onClick={handleRetry} className="btn-outline h-10 px-3.5 text-destructive">
              <RefreshCw className="h-3.5 w-3.5" />
              Riprova
            </button>
            <button
              onClick={() => setError(null)}
              className="rounded-lg p-2.5 transition hover:bg-destructive/20"
              aria-label="Chiudi il messaggio di errore"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        <div aria-live="polite" className="sr-only">
          {loading ? 'Calcolo in corso' : analysis ? 'Analisi aggiornata' : ''}
        </div>

        {loading && !analysis ? (
          <div className="flex flex-col items-center justify-center gap-3 py-28">
            <Loader2 className="h-9 w-9 animate-spin text-primary" aria-hidden="true" />
            <p className="text-sm font-medium text-muted-foreground">
              Calcolo del costo totale di possesso e dei tempi di rientro…
            </p>
          </div>
        ) : analysis ? (
          <div ref={resultsRef} className="scroll-mt-20 space-y-6 animate-fade-up">
            {/* Verdict hero */}
            <Card className="overflow-hidden">
              <div className="grid gap-6 p-6 lg:grid-cols-[1fr_21rem]">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="overline">Sintesi decisionale</span>
                    {sourceChip()}
                  </div>
                  <h2 className="mt-2 text-xl font-black tracking-tight sm:text-2xl">
                    {analysis.candidate_vehicle.brand} {analysis.candidate_vehicle.model}{' '}
                    <span className="font-medium text-muted-foreground">vs</span>{' '}
                    {analysis.current_vehicle.brand} {analysis.current_vehicle.model}
                  </h2>
                  <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                    {analysis.recommendation.summary_text}
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Chip tone="neutral">
                      <Calendar className="h-3 w-3" aria-hidden="true" />
                      {analysis.ownership.horizon_years} anni
                    </Chip>
                    <Chip tone="neutral">
                      <Route className="h-3 w-3" aria-hidden="true" />
                      {fmtNum(analysis.usage.annual_km)} km/anno
                    </Chip>
                    <Chip tone="neutral">
                      <Plug className="h-3 w-3" aria-hidden="true" />
                      {fmtPct(analysis.charging.home_charging_percentage)} ricarica a casa
                    </Chip>
                  </div>
                </div>

                <RecommendationBadge
                  rating={analysis.recommendation.rating}
                  confidence={analysis.recommendation.confidence}
                />
              </div>
            </Card>

            {/* Key metrics */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                label="Risparmio cumulativo"
                tone={Number(analysis.break_even.cumulative_savings_over_horizon) >= 0 ? 'emerald' : 'rose'}
                icon={<TrendingUp className="h-4 w-4" />}
                value={
                  <span
                    className={
                      Number(analysis.break_even.cumulative_savings_over_horizon) >= 0
                        ? 'text-emerald-700 dark:text-emerald-400'
                        : 'text-rose-700 dark:text-rose-400'
                    }
                  >
                    {fmtSignedEUR(analysis.break_even.cumulative_savings_over_horizon)}
                  </span>
                }
                sub={`Rispetto a tenere l’auto attuale per ${analysis.ownership.horizon_years} anni`}
              />

              <StatCard
                label="Break-even operativo"
                tone="primary"
                icon={<Timer className="h-4 w-4" />}
                value={
                  analysis.break_even.operational_break_even_years != null
                    ? fmtYears(analysis.break_even.operational_break_even_years)
                    : 'Non raggiunto'
                }
                sub={
                  analysis.break_even.operational_break_even_km
                    ? `≈ ${fmtNum(analysis.break_even.operational_break_even_km)} km percorsi · risparmio ${fmtEUR(
                        analysis.break_even.monthly_operational_savings,
                      )}/mese`
                    : `Risparmio operativo ${fmtEUR(analysis.break_even.monthly_operational_savings)}/mese`
                }
              />

              <StatCard
                label="Costo al chilometro"
                tone="blue"
                icon={<Fuel className="h-4 w-4" />}
                value={
                  <span className="flex items-baseline gap-2">
                    <span className="text-emerald-700 dark:text-emerald-400">
                      {fmtEUR(analysis.candidate_tco.tco_per_km, 3)}
                    </span>
                    <span className="text-sm font-medium text-muted-foreground line-through">
                      {fmtEUR(analysis.current_tco.tco_per_km, 3)}
                    </span>
                  </span>
                }
                sub={
                  Number(analysis.break_even.cost_per_km_diff) > 0
                    ? `Risparmio di ${fmtEUR(analysis.break_even.cost_per_km_diff, 3)}/km con l’elettrico`
                    : 'Nessun risparmio chilometrico'
                }
              />

              <StatCard
                label="Punteggio di rischio"
                tone={riskTone[analysis.recommendation.risk_level]}
                icon={<ShieldAlert className="h-4 w-4" />}
                value={
                  <span className="flex items-baseline gap-2">
                    {analysis.recommendation.risk_score}
                    <span className="text-sm font-medium text-muted-foreground">
                      /100 · {analysis.recommendation.risk_level}
                    </span>
                  </span>
                }
                sub={`Confidenza del modello ${fmtPct(analysis.recommendation.confidence)}`}
                progress={{ value: analysis.recommendation.risk_score / 100, label: 'Punteggio di rischio' }}
              />
            </div>

            {/* Scenarios & sensitivity */}
            <ScenarioInsights analysis={analysis} />

            {/* Pros & cautions */}
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <Card className="p-5">
                <SectionHeader icon={<Sparkles className="h-4 w-4" />} title="Perché ha senso" />
                {analysis.recommendation.key_advantages.length > 0 ? (
                  <ul className="space-y-2.5">
                    {analysis.recommendation.key_advantages.map((adv, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed">
                        <span className="mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400">
                          <Check className="h-3 w-3" />
                        </span>
                        <span>{adv}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Nessun vantaggio economico rilevante.</p>
                )}
              </Card>

              <Card className="p-5">
                <SectionHeader icon={<ShieldAlert className="h-4 w-4" />} title="Punti di attenzione" />
                {analysis.recommendation.cautions_and_risks.length > 0 ? (
                  <ul className="space-y-2.5">
                    {analysis.recommendation.cautions_and_risks.map((c, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed">
                        <span className="mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400">
                          <AlertTriangle className="h-3 w-3" />
                        </span>
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Nessun rischio critico evidenziato.</p>
                )}
              </Card>
            </div>

            {/* Charts */}
            <AnalysisCharts analysis={analysis} />

            {/* Data transparency */}
            <Card className="p-5">
              <SectionHeader
                icon={<Calculator className="h-4 w-4" />}
                title="Dati, stime e assunzioni"
                subtitle="Origine e formula di calcolo di ogni valore usato dal motore di analisi."
              />
              <div className="mb-4 flex flex-wrap items-center gap-2">
                {(Object.keys(sourceLabels) as ValueExplanation['source'][]).map((key) => (
                  <Chip key={key} tone={sourceTone[key]}>
                    {sourceLabels[key]}
                    <span className="hidden font-mono text-[10px] sm:inline">
                      · {key.replace('_', ' ')}
                    </span>
                  </Chip>
                ))}
              </div>
              <div className="overflow-x-auto rounded-xl border border-border">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-border bg-muted/40 text-[11px] uppercase tracking-wide text-muted-foreground">
                      <th className="px-3 py-2.5 font-bold">Metrica / Parametro</th>
                      <th className="px-3 py-2.5 font-bold">Valore</th>
                      <th className="px-3 py-2.5 font-bold">Sorgente</th>
                      <th className="px-3 py-2.5 font-bold">Formula del motore</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {analysis.recommendation.explanations.length > 0 ? (
                      analysis.recommendation.explanations.map((exp, idx) => (
                        <tr key={idx} className="transition-colors odd:bg-muted/20 hover:bg-muted/50">
                          <td className="px-3 py-2.5 font-medium">{exp.notes || 'Calcolo interno'}</td>
                          <td className="px-3 py-2.5 font-bold tabular-nums text-primary">{exp.value}</td>
                          <td className="px-3 py-2.5">
                            <Chip tone={sourceTone[exp.source]}>{sourceLabels[exp.source]}</Chip>
                          </td>
                          <td className="px-3 py-2.5 font-mono text-xs text-muted-foreground">{exp.formula}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="px-3 py-6 text-center text-sm text-muted-foreground">
                          Nessuna spiegazione di calcolo disponibile per questa analisi.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Card>

            <footer className="border-t border-border/70 py-8 text-center text-xs leading-relaxed text-muted-foreground print:hidden">
              <p className="flex items-center justify-center gap-1.5 font-semibold text-foreground">
                <Zap className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                EV Purchase Advisor
                <InfoHint text="Motore di calcolo open source: i valori dipendono da costi, prezzi e percorrenze che inserisci." />
              </p>
              <p className="mx-auto mt-1.5 max-w-2xl">
                Gli output sono stime a scopo informativo e non costituiscono consulenza finanziaria. Verifica sempre
                prezzi, incentivi e condizioni reali prima di decidere.
              </p>
            </footer>
          </div>
        ) : null}
      </main>

      {showWizard && (
        <AnalysisWizard
          onRunAnalysis={handleCustomAnalysis}
          isLoading={loading}
          onClose={() => setShowWizard(false)}
        />
      )}
    </div>
  );
};

export default App;
