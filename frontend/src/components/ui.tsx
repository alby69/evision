import React, { useEffect, useState } from 'react';
import { Moon, Sun, Info } from 'lucide-react';

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className = '',
  children,
  ...rest
}) => (
  <div className={`card-panel ${className}`} {...rest}>
    {children}
  </div>
);

interface SectionHeaderProps {
  icon?: React.ReactNode;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  icon,
  title,
  subtitle,
  action,
}) => (
  <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
    <div className="flex items-start gap-3">
      {icon && (
        <span className="mt-0.5 rounded-lg bg-primary/10 p-2 text-primary">{icon}</span>
      )}
      <div>
        <h3 className="text-base font-bold text-foreground sm:text-lg">{title}</h3>
        {subtitle && <p className="mt-0.5 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
    </div>
    {action}
  </div>
);

interface FieldProps {
  label: string;
  hint?: string;
  error?: string | null;
  htmlFor?: string;
  children: React.ReactNode;
}

export const Field: React.FC<FieldProps> = ({ label, hint, error, htmlFor, children }) => (
  <div>
    <label className="field-label" htmlFor={htmlFor}>
      {label}
    </label>
    {children}
    {error ? (
      <p className="mt-1.5 text-xs font-medium text-destructive" role="alert">
        {error}
      </p>
    ) : hint ? (
      <p className="field-hint">{hint}</p>
    ) : null}
  </div>
);

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const TextInput: React.FC<InputProps> = ({ className = '', ...rest }) => (
  <input type="text" className={`field-input ${className}`} {...rest} />
);

export const NumberInput: React.FC<InputProps> = ({ className = '', ...rest }) => (
  <input type="number" inputMode="decimal" className={`field-input ${className}`} {...rest} />
);

export const SelectInput: React.FC<React.SelectHTMLAttributes<HTMLSelectElement>> = ({
  className = '',
  children,
  ...rest
}) => (
  <select className={`field-input ${className}`} {...rest}>
    {children}
  </select>
);

interface RangeSliderProps {
  id?: string;
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (value: number) => void;
  ariaLabel?: string;
}

export const RangeSlider: React.FC<RangeSliderProps> = ({
  id,
  min,
  max,
  step = 1,
  value,
  onChange,
  ariaLabel,
}) => {
  const pct = max > min ? ((value - min) / (max - min)) * 100 : 0;
  return (
    <input
      id={id}
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      aria-label={ariaLabel}
      style={{ ['--range-fill' as string]: `${pct}%` }}
      onChange={(e) => onChange(Number(e.target.value))}
    />
  );
};

interface ChipProps {
  children: React.ReactNode;
  tone?: 'neutral' | 'primary' | 'amber' | 'emerald' | 'rose' | 'blue';
  title?: string;
  className?: string;
}

const chipTones: Record<NonNullable<ChipProps['tone']>, string> = {
  neutral: 'bg-muted text-muted-foreground border-border',
  primary: 'bg-primary/10 text-primary border-primary/20',
  amber: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/25',
  emerald: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/25',
  rose: 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/25',
  blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/25',
};

export const Chip: React.FC<ChipProps> = ({ children, tone = 'neutral', title, className = '' }) => (
  <span
    title={title}
    className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide ${chipTones[tone]} ${className}`}
  >
    {children}
  </span>
);

export const InfoHint: React.FC<{ text: string; label?: string }> = ({
  text,
  label = 'Informazione',
}) => (
  <span title={text} className="inline-flex cursor-help align-middle text-muted-foreground">
    <Info className="h-3.5 w-3.5" aria-hidden="true" />
    <span className="sr-only">{label}: {text}</span>
  </span>
);

interface StatCardProps {
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  icon?: React.ReactNode;
  tone?: 'emerald' | 'primary' | 'blue' | 'amber' | 'rose' | 'neutral';
  progress?: { value: number; label: string };
  className?: string;
}

const statTones: Record<NonNullable<StatCardProps['tone']>, { wrap: string; icon: string; bar: string }> = {
  emerald: {
    wrap: 'hover:border-emerald-500/30',
    icon: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
    bar: 'bg-emerald-500',
  },
  primary: {
    wrap: 'hover:border-primary/30',
    icon: 'bg-primary/10 text-primary',
    bar: 'bg-primary',
  },
  blue: {
    wrap: 'hover:border-blue-500/30',
    icon: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    bar: 'bg-blue-500',
  },
  amber: {
    wrap: 'hover:border-amber-500/30',
    icon: 'bg-amber-500/10 text-amber-700 dark:text-amber-400',
    bar: 'bg-amber-500',
  },
  rose: {
    wrap: 'hover:border-rose-500/30',
    icon: 'bg-rose-500/10 text-rose-700 dark:text-rose-400',
    bar: 'bg-rose-500',
  },
  neutral: {
    wrap: 'hover:border-border',
    icon: 'bg-muted text-muted-foreground',
    bar: 'bg-muted-foreground',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  sub,
  icon,
  tone = 'neutral',
  progress,
  className = '',
}) => {
  const t = statTones[tone];
  return (
    <Card className={`group p-5 transition-colors duration-200 ${t.wrap} ${className}`}>
      <div className="flex items-start justify-between gap-3">
        <span className="overline">{label}</span>
        {icon && (
          <span className={`rounded-lg p-1.5 transition-transform duration-200 group-hover:scale-110 ${t.icon}`}>
            {icon}
          </span>
        )}
      </div>
      <div className="mt-2 text-2xl font-black tabular-nums tracking-tight text-foreground">
        {value}
      </div>
      {sub && <div className="mt-1 text-xs leading-relaxed text-muted-foreground">{sub}</div>}
      {progress && (
        <div className="mt-3">
          <div
            className="h-1.5 w-full overflow-hidden rounded-full bg-muted"
            role="progressbar"
            aria-valuenow={Math.round(progress.value * 100)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={progress.label}
          >
            <div
              className={`h-full rounded-full transition-all duration-700 ${t.bar}`}
              style={{ width: `${Math.min(100, Math.max(0, progress.value * 100))}%` }}
            />
          </div>
        </div>
      )}
    </Card>
  );
};

export const ThemeToggle: React.FC = () => {
  const [dark, setDark] = useState<boolean>(
    () => typeof document !== 'undefined' && document.documentElement.classList.contains('dark'),
  );

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    try {
      localStorage.setItem('ev-theme', dark ? 'dark' : 'light');
    } catch {
      /* storage unavailable */
    }
  }, [dark]);

  return (
    <button
      type="button"
      onClick={() => setDark((d) => !d)}
      className="btn-outline h-10 w-10 p-0"
      aria-label={dark ? 'Passa al tema chiaro' : 'Passa al tema scuro'}
      title={dark ? 'Tema chiaro' : 'Tema scuro'}
    >
      {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
};
