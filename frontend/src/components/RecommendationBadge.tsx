import React from 'react';
import { RecommendationRating } from '../types/api';
import { Zap } from 'lucide-react';

interface RecommendationBadgeProps {
  rating: RecommendationRating;
}

export const RecommendationBadge: React.FC<RecommendationBadgeProps> = ({ rating }) => {
  const badgeConfig = {
    [RecommendationRating.STRONG_BUY]: {
      label: 'CONVENIENTE (STRONG BUY)',
      color: 'bg-emerald-600 text-white border-emerald-500',
      description: 'Risparmio finanziario significativo e tempi di rientro rapidi.',
    },
    [RecommendationRating.BUY]: {
      label: 'CONVENIENTE (BUY)',
      color: 'bg-green-600 text-white border-green-500',
      description: 'Convenienza economica confermata nel periodo di possesso.',
    },
    [RecommendationRating.MAYBE]: {
      label: 'NEUTRO (MAYBE)',
      color: 'bg-amber-500 text-white border-amber-400',
      description: 'Costi totali equivalenti. La scelta dipende da preferenze personali.',
    },
    [RecommendationRating.KEEP_CURRENT]: {
      label: 'TIENI AUTO ATTUALE',
      color: 'bg-orange-600 text-white border-orange-500',
      description: 'In termini economici puri conviene mantenere l’auto attuale.',
    },
    [RecommendationRating.AVOID]: {
      label: 'NON CONVIENE (AVOID)',
      color: 'bg-rose-600 text-white border-rose-500',
      description: 'L’acquisto dell’auto candidata comporta costi totali maggiori.',
    },
  };

  const config = badgeConfig[rating] || badgeConfig[RecommendationRating.MAYBE];

  return (
    <div className={`p-4 rounded-xl shadow-md border ${config.color} transition-all`}>
      <div className="flex items-center gap-2">
        <Zap className="w-6 h-6 animate-pulse" />
        <span className="font-bold text-lg uppercase tracking-wider">{config.label}</span>
      </div>
      <p className="mt-1 text-sm opacity-90">{config.description}</p>
    </div>
  );
};
