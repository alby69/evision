import React from 'react';
import { RecommendationRating } from '../types/api';
import { TrendingUp, ThumbsUp, Minus, RotateCcw, TrendingDown } from 'lucide-react';
import { fmtPct } from '../utils/format';

interface RecommendationBadgeProps {
  rating: RecommendationRating;
  confidence?: number;
}

interface BadgeConfig {
  label: string;
  tag: string;
  description: string;
  icon: React.ReactNode;
  tone: string;
  iconTone: string;
}

const badgeConfig: Record<RecommendationRating, BadgeConfig> = {
  [RecommendationRating.STRONG_BUY]: {
    label: 'Conviene molto',
    tag: 'Strong buy',
    description:
      'Risparmio finanziario significativo e break-even rapido: l’upgrade all’elettrico è solido su quasi tutti gli scenari.',
    icon: <TrendingUp className="h-5 w-5" />,
    tone: 'border-emerald-500/30 bg-gradient-to-br from-emerald-50 to-white dark:from-emerald-950/50 dark:to-card',
    iconTone: 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30',
  },
  [RecommendationRating.BUY]: {
    label: 'Conviene',
    tag: 'Buy',
    description:
      'Convenienza economica confermata nell’orizzonte di possesso considerato, con margine positivo attendibile.',
    icon: <ThumbsUp className="h-5 w-5" />,
    tone: 'border-emerald-500/25 bg-gradient-to-br from-emerald-50/80 to-white dark:from-emerald-950/40 dark:to-card',
    iconTone: 'bg-emerald-500 text-white shadow-md shadow-emerald-500/30',
  },
  [RecommendationRating.MAYBE]: {
    label: 'Neutro',
    tag: 'Maybe',
    description:
      'I costi totali sono sostanzialmente equivalenti: la scelta dipende da priorità personali non monetarie.',
    icon: <Minus className="h-5 w-5" />,
    tone: 'border-amber-500/30 bg-gradient-to-br from-amber-50 to-white dark:from-amber-950/40 dark:to-card',
    iconTone: 'bg-amber-500 text-white shadow-md shadow-amber-500/30',
  },
  [RecommendationRating.KEEP_CURRENT]: {
    label: 'Tieni l’auto attuale',
    tag: 'Keep current',
    description:
      'In termini economici puri conviene continuare a usare il veicolo attuale per ora.',
    icon: <RotateCcw className="h-5 w-5" />,
    tone: 'border-orange-500/30 bg-gradient-to-br from-orange-50 to-white dark:from-orange-950/40 dark:to-card',
    iconTone: 'bg-orange-500 text-white shadow-md shadow-orange-500/30',
  },
  [RecommendationRating.AVOID]: {
    label: 'Non conviene',
    tag: 'Avoid',
    description:
      'L’acquisto del veicolo candidato comporta costi totali nettamente superiori rispetto all’alternativa.',
    icon: <TrendingDown className="h-5 w-5" />,
    tone: 'border-rose-500/30 bg-gradient-to-br from-rose-50 to-white dark:from-rose-950/40 dark:to-card',
    iconTone: 'bg-rose-600 text-white shadow-md shadow-rose-600/30',
  },
};

export const RecommendationBadge: React.FC<RecommendationBadgeProps> = ({
  rating,
  confidence,
}) => {
  const config = badgeConfig[rating] || badgeConfig[RecommendationRating.MAYBE];
  const confidencePct = confidence !== undefined ? Math.round(confidence * 100) : null;

  return (
    <div
      className={`animate-fade-up rounded-2xl border p-5 shadow-card ${config.tone}`}
      role="status"
      aria-label={`Verdetto: ${config.label}`}
    >
      <div className="flex items-start gap-3.5">
        <span className={`shrink-0 rounded-xl p-2.5 ${config.iconTone}`}>{config.icon}</span>
        <div className="min-w-0">
          <div className="overline">Verdetto del motore</div>
          <div className="mt-0.5 text-xl font-black leading-tight tracking-tight">
            {config.label}
          </div>
          <div className="mt-0.5 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
            {config.tag}
          </div>
          <p className="mt-2 text-[13px] leading-relaxed text-muted-foreground">
            {config.description}
          </p>
        </div>
      </div>

      {confidencePct !== null && (
        <div className="mt-4 rounded-xl border border-border/70 bg-card/70 p-3">
          <div className="flex items-baseline justify-between text-xs font-semibold">
            <span className="text-muted-foreground">Confidenza del modello</span>
            <span className="tabular-nums text-foreground">{fmtPct(confidence)}</span>
          </div>
          <div
            className="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted"
            role="progressbar"
            aria-valuenow={confidencePct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Confidenza del modello"
          >
            <div
              className="h-full rounded-full bg-primary transition-all duration-700"
              style={{ width: `${confidencePct}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationBadge;
