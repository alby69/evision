const eur0 = new Intl.NumberFormat('it-IT', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
});

const eur2 = new Intl.NumberFormat('it-IT', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const eur3 = new Intl.NumberFormat('it-IT', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 3,
  maximumFractionDigits: 3,
});

const num0 = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 0 });
const num1 = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 1 });

const toNumber = (v: unknown): number => {
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : 0;
};

export const fmtEUR = (v: unknown, decimals: 0 | 2 | 3 = 0): string => {
  const n = toNumber(v);
  if (decimals === 3) return eur3.format(n);
  if (decimals === 2) return eur2.format(n);
  return eur0.format(n);
};

export const fmtSignedEUR = (v: unknown): string => {
  const n = toNumber(v);
  const formatted = eur0.format(Math.abs(n));
  if (n > 0) return `+${formatted}`;
  if (n < 0) return `−${formatted}`;
  return formatted;
};

export const fmtNum = (v: unknown, decimals: 0 | 1 = 0): string => {
  const n = toNumber(v);
  return decimals === 1 ? num1.format(n) : num0.format(n);
};

export const fmtKm = (v: unknown): string => `${fmtNum(v)} km`;

/** Formats a 0..1 fraction as a percentage, e.g. 0.42 -> "42%". */
export const fmtPct = (v: unknown, decimals = 0): string =>
  `${(toNumber(v) * 100).toFixed(decimals)}%`;

/** Compact euro for chart axes: 12500 -> "12,5k €". */
export const fmtEURCompact = (v: unknown): string => {
  const n = toNumber(v);
  const abs = Math.abs(n);
  if (abs >= 1_000_000) return `${num1.format(n / 1_000_000)} mln €`;
  if (abs >= 1_000) return `${num1.format(n / 1_000)}k €`;
  return `${num0.format(n)} €`;
};

export const fmtYears = (v: unknown): string => {
  const n = toNumber(v);
  return `${num1.format(n)} ${n === 1 ? 'anno' : 'anni'}`;
};
