import React from 'react';
import { FullAnalysisResponse } from '../types/api';
import { Card, SectionHeader } from './ui';
import { TrendingUp, TrendingDown, Minus, Crosshair } from 'lucide-react';
import { fmtEUR, fmtSignedEUR, fmtYears } from '../utils/format';

interface ScenarioInsightsProps {
  analysis: FullAnalysisResponse;
}

const sensitivityLabels: Record<string, string> = {
  'Annual Mileage': 'Chilometraggio annuo',
  'Fuel Prices': 'Prezzo dei carburanti',
  'Home Electricity Tariff': 'Tariffa elettrica domestica',
  'Vehicle Purchase Price': 'Prezzo di acquisto',
  'EV Depreciation Rate': 'Deprezzamento dell’EV',
  'Routine Maintenance Savings': 'Risparmio sulla manutenzione',
};

const sensitivityDescriptions: Record<string, string> = {
  'Annual Mileage':
    'Impatto massimo: il risparmio di energia/carburante cresce in modo proporzionale ai chilometri percorsi.',
  'Fuel Prices':
    'Impatto alto: un prezzo più elevato di benzina e diesel aumenta direttamente il risparmio passando all’elettrico.',
  'Home Electricity Tariff':
    'Impatto alto: ricaricare a casa a tariffe basse (0,20-0,25 €/kWh) massimizza il risparmio operativo.',
  'Vehicle Purchase Price':
    'Impatto medio: il prezzo di acquisto determina la lunghezza del tempo di rientro.',
  'EV Depreciation Rate':
    'Impatto moderato: il valore residuo al termine del periodo incide sul costo totale finale.',
  'Routine Maintenance Savings':
    'Impatto minore: la minore manutenzione dell’EV garantisce un risparmio costante ma contenuto.',
};

interface ScenarioCardConfig {
  label: string;
  caption: string;
  tco: number;
  breakEven?: number | null;
  icon: React.ReactNode;
  wrap: string;
  value: string;
}

export const ScenarioInsights: React.FC<ScenarioInsightsProps> = ({ analysis }) => {
  const currentTotal = Number(analysis.current_tco.total_tco);

  const scenarios: ScenarioCardConfig[] = [
    {
      label: 'Pessimistico',
      caption: 'Energia +30%, manutenzione EV +20%, carburanti −10%.',
      tco: Number(analysis.scenarios.pessimistic_tco),
      breakEven: analysis.scenarios.pessimistic_break_even_years,
      icon: <TrendingDown className="h-4 w-4 text-rose-500" />,
      wrap: 'border-rose-500/30 bg-rose-500/5',
      value: 'text-rose-700 dark:text-rose-400',
    },
    {
      label: 'Base',
      caption: 'Prezzi, tariffe e costi correnti come inseriti.',
      tco: Number(analysis.scenarios.base_tco),
      breakEven: analysis.scenarios.base_break_even_years,
      icon: <Minus className="h-4 w-4 text-primary" />,
      wrap: 'border-primary/30 bg-primary/5',
      value: 'text-foreground',
    },
    {
      label: 'Ottimistico',
      caption: 'Energia −10%, carburanti +15%, manutenzione EV −10%.',
      tco: Number(analysis.scenarios.optimistic_tco),
      breakEven: analysis.scenarios.optimistic_break_even_years,
      icon: <TrendingUp className="h-4 w-4 text-emerald-500" />,
      wrap: 'border-emerald-500/30 bg-emerald-500/5',
      value: 'text-emerald-700 dark:text-emerald-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-5">
      <Card className="p-5 lg:col-span-3">
        <SectionHeader
          icon={<TrendingUp className="h-4 w-4" />}
          title="Scenari economici"
          subtitle="Quanto costa l’elettrico se energia, carburanti e manutenzione evolvono diversamente."
        />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {scenarios.map((scenario) => {
            const savings = currentTotal - scenario.tco;
            return (
              <div key={scenario.label} className={`rounded-xl border p-4 ${scenario.wrap}`}>
                <div className="flex items-center justify-between">
                  <span className="overline">{scenario.label}</span>
                  {scenario.icon}
                </div>
                <div className={`mt-2 text-xl font-black tabular-nums tracking-tight ${scenario.value}`}>
                  {fmtEUR(scenario.tco)}
                </div>
                <div className="text-[11px] text-muted-foreground">TCO del veicolo elettrico</div>
                <div className="mt-3 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-muted-foreground">Break-even</span>
                    <span className="font-bold tabular-nums text-foreground">
                      {scenario.breakEven != null ? fmtYears(scenario.breakEven) : 'Mai'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-muted-foreground">vs auto attuale</span>
                    <span
                      className={`font-bold tabular-nums ${
                        savings > 0
                          ? 'text-emerald-700 dark:text-emerald-400'
                          : savings < 0
                            ? 'text-rose-700 dark:text-rose-400'
                            : 'text-muted-foreground'
                      }`}
                    >
                      {fmtSignedEUR(savings)}
                    </span>
                  </div>
                </div>
                <p className="mt-3 text-[11px] leading-relaxed text-muted-foreground">{scenario.caption}</p>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="p-5 lg:col-span-2">
        <SectionHeader
          icon={<Crosshair className="h-4 w-4" />}
          title="Cosa pesa di più"
          subtitle="Fattori ordinati per impatto sul costo totale."
        />
        <ul className="space-y-3.5">
          {analysis.sensitivity.map((factor) => {
            const score = Math.max(0, Math.min(10, Number(factor.impact_score)));
            return (
              <li key={factor.parameter_name}>
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="font-semibold text-foreground">
                    {sensitivityLabels[factor.parameter_name] ?? factor.parameter_name}
                  </span>
                  <span className="shrink-0 text-xs font-bold tabular-nums text-muted-foreground">
                    {score.toFixed(1)}/10
                  </span>
                </div>
                <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-primary to-emerald-400 transition-all duration-700"
                    style={{ width: `${score * 10}%` }}
                  />
                </div>
                <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                  {sensitivityDescriptions[factor.parameter_name] ?? factor.impact_description}
                </p>
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
};

export default ScenarioInsights;
