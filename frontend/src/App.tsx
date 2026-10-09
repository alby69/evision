import React, { useEffect, useState } from 'react';
import { FullAnalysisResponse } from './types/api';
import { fetchDemoAnalysis, createAnalysis } from './services/api';
import { RecommendationBadge } from './components/RecommendationBadge';
import { AnalysisCharts } from './components/AnalysisCharts';
import { AnalysisWizard } from './components/AnalysisWizard';
import { Zap, ShieldAlert, Sparkles, RefreshCw, SlidersHorizontal, Calculator, Share2, FileText, Check } from 'lucide-react';
import { fetchAnalysisById } from './services/api';

export const App: React.FC = () => {
  const [analysis, setAnalysis] = useState<FullAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showWizard, setShowWizard] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const analysisId = params.get('id');
    if (analysisId) {
      loadSavedAnalysis(analysisId);
    } else {
      loadDemoAnalysis();
    }
  }, []);

  const loadDemoAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDemoAnalysis();
      setAnalysis(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Impossibile caricare la demo.');
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
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Impossibile caricare l’analisi salvata.');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomAnalysis = async (payload: any) => {
    setLoading(true);
    setError(null);
    try {
      const data = await createAnalysis(payload);
      setAnalysis(data);
      setShowWizard(false);
      if (data.id) {
        window.history.pushState({}, '', `?id=${data.id}`);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Errore nel calcolo dell’analisi.');
    } finally {
      setLoading(false);
    }
  };

  const handleShare = () => {
    if (!analysis?.id) return;
    const shareUrl = `${window.location.origin}${window.location.pathname}?id=${analysis.id}`;
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const handleExportPdf = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="border-b border-border bg-card/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary text-primary-foreground shadow-sm">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-extrabold text-lg tracking-tight">EV Purchase Advisor</h1>
              <p className="text-xs text-muted-foreground">Decision Support Engine per Sostituzione Auto Elettrica</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {analysis && (
              <>
                <button
                  onClick={handleShare}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border bg-card text-foreground font-medium text-xs hover:bg-muted transition-all"
                  title="Copia link per condividere l'analisi"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Share2 className="w-4 h-4" />}
                  <span>{copied ? 'Copiato!' : 'Condividi'}</span>
                </button>

                <button
                  onClick={handleExportPdf}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border bg-card text-foreground font-medium text-xs hover:bg-muted transition-all print:hidden"
                  title="Esporta Report PDF"
                >
                  <FileText className="w-4 h-4" />
                  <span>Esporta PDF</span>
                </button>
              </>
            )}

            <button
              onClick={() => setShowWizard(!showWizard)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:opacity-90 shadow-sm transition-all print:hidden"
            >
              <SlidersHorizontal className="w-4 h-4" />
              {showWizard ? 'Chiudi Wizard' : 'Nuova Analisi'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive text-destructive flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm font-medium">{error}</span>
          </div>
        )}

        {showWizard && (
          <div className="mb-8">
            <AnalysisWizard onRunAnalysis={handleCustomAnalysis} isLoading={loading} />
          </div>
        )}

        {loading && !analysis ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <RefreshCw className="w-8 h-8 text-primary animate-spin" />
            <p className="text-sm text-muted-foreground">Elaborazione calcolo finanziario TCO e analisi di rischio in corso...</p>
          </div>
        ) : analysis ? (
          <div className="space-y-6">
            {/* Header Recommendation Card */}
            <div className="bg-card p-6 rounded-2xl border border-border shadow-sm flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="space-y-3 max-w-2xl">
                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-widest">
                  <span>Sintesi Decisionale</span>
                  <span>•</span>
                  <span>Orizzonte {analysis.ownership.horizon_years} Anni</span>
                </div>
                <h2 className="text-2xl font-extrabold tracking-tight">
                  {analysis.candidate_vehicle.brand} {analysis.candidate_vehicle.model} vs {analysis.current_vehicle.brand} {analysis.current_vehicle.model}
                </h2>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {analysis.recommendation.summary_text}
                </p>
              </div>

              <div className="w-full lg:w-80 flex-shrink-0">
                <RecommendationBadge rating={analysis.recommendation.rating} />
              </div>
            </div>

            {/* Key Decision Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
                <span className="text-xs font-medium text-muted-foreground">Risparmio Cumulativo</span>
                <div className="text-2xl font-black text-emerald-600 mt-1">
                  € {analysis.break_even.cumulative_savings_over_horizon.toLocaleString()}
                </div>
                <span className="text-xs text-muted-foreground mt-1 block">Rispetto a mantenere l’auto attuale</span>
              </div>

              <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
                <span className="text-xs font-medium text-muted-foreground">Break-Even Operativo</span>
                <div className="text-2xl font-black text-primary mt-1">
                  {analysis.break_even.operational_break_even_years !== null
                    ? `${analysis.break_even.operational_break_even_years} Anni`
                    : 'Non Raggiunto'}
                </div>
                <span className="text-xs text-muted-foreground mt-1 block">
                  {analysis.break_even.operational_break_even_km
                    ? `~ ${analysis.break_even.operational_break_even_km.toLocaleString()} km guidati`
                    : 'N/A'}
                </span>
              </div>

              <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
                <span className="text-xs font-medium text-muted-foreground">Costo al Chilometro</span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-xl font-bold text-emerald-600">€ {Number(analysis.candidate_tco.tco_per_km).toFixed(3)}</span>
                  <span className="text-xs text-muted-foreground line-through">€ {Number(analysis.current_tco.tco_per_km).toFixed(3)}</span>
                </div>
                <span className="text-xs text-muted-foreground mt-1 block">Risparmio {analysis.break_even.cost_per_km_diff > 0 ? `€ ${Number(analysis.break_even.cost_per_km_diff).toFixed(3)}/km` : 'nessuno'}</span>
              </div>

              <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
                <span className="text-xs font-medium text-muted-foreground">Punteggio di Rischio</span>
                <div className="text-2xl font-black mt-1">
                  {analysis.recommendation.risk_score} <span className="text-xs text-muted-foreground font-normal">/ 100 ({analysis.recommendation.risk_level})</span>
                </div>
                <span className="text-xs text-muted-foreground mt-1 block">Confidenza algoritmo: {(analysis.recommendation.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            {/* Explanations & Risks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
                <div className="flex items-center gap-2 mb-3 text-emerald-600 font-semibold text-base">
                  <Sparkles className="w-5 h-5" />
                  <h3>Perché la scelta ha senso</h3>
                </div>
                <ul className="space-y-2">
                  {analysis.recommendation.key_advantages.map((adv, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <span className="text-emerald-500 font-bold">✓</span>
                      <span>{adv}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
                <div className="flex items-center gap-2 mb-3 text-amber-500 font-semibold text-base">
                  <ShieldAlert className="w-5 h-5" />
                  <h3>Punti di Attenzione & Rischi</h3>
                </div>
                <ul className="space-y-2">
                  {analysis.recommendation.cautions_and_risks.length > 0 ? (
                    analysis.recommendation.cautions_and_risks.map((c, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-amber-500 font-bold">!</span>
                        <span>{c}</span>
                      </li>
                    ))
                  ) : (
                    <li className="text-sm text-muted-foreground">Nessun rischio critico evidenziato.</li>
                  )}
                </ul>
              </div>
            </div>

            {/* Charts Section */}
            <AnalysisCharts analysis={analysis} />

            {/* Facts vs Assumptions Transparency Section */}
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
              <div className="flex items-center gap-2 mb-4 font-semibold text-base">
                <Calculator className="w-5 h-5 text-primary" />
                <h3>Trasparenza Tracciabilità (Facts vs. Assumptions)</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-border text-xs text-muted-foreground uppercase">
                    <tr>
                      <th className="py-2 px-3">Metrica / Parametro</th>
                      <th className="py-2 px-3">Valore Estrapolato</th>
                      <th className="py-2 px-3">Sorgente</th>
                      <th className="py-2 px-3">Formula Matematica Engine</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {analysis.recommendation.explanations.map((exp, idx) => (
                      <tr key={idx} className="hover:bg-muted/50">
                        <td className="py-2.5 px-3 font-medium">{exp.notes || 'Calcolo Interno'}</td>
                        <td className="py-2.5 px-3 font-bold text-primary">{exp.value}</td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded text-xs font-semibold bg-primary/10 text-primary">
                            {exp.source}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-mono text-xs text-muted-foreground">{exp.formula}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
};

export default App;
