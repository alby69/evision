import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Cell,
  LabelList,
  PieChart,
  Pie,
} from 'recharts';
import { FullAnalysisResponse } from '../types/api';
import { Card, SectionHeader } from './ui';
import { LineChart as LineChartIcon, PieChart as PieChartIcon, Gauge, BatteryCharging } from 'lucide-react';
import { fmtEUR, fmtEURCompact, fmtNum } from '../utils/format';

interface ChartsProps {
  analysis: FullAnalysisResponse;
}

interface TooltipEntry {
  name?: string;
  value?: number;
  color?: string;
  stroke?: string;
  payload?: Record<string, unknown>;
}

const ChartTooltip: React.FC<{
  active?: boolean;
  payload?: TooltipEntry[];
  label?: string | number;
  formatter?: (value: number, name?: string) => string;
}> = ({ active, payload, label, formatter }) => {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-xl border border-border bg-card px-3 py-2 shadow-lift">
      {label !== undefined && (
        <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">{label}</div>
      )}
      <div className="space-y-1">
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-xs">
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{
                background:
                  entry.color ||
                  entry.stroke ||
                  (entry.payload && (entry.payload as { fill?: string }).fill) ||
                  '#64748b',
              }}
              aria-hidden="true"
            />
            <span className="text-muted-foreground">{entry.name}</span>
            <span className="ml-auto pl-3 font-bold tabular-nums text-foreground">
              {entry.value !== undefined
                ? formatter
                  ? formatter(entry.value, entry.name)
                  : fmtNum(entry.value)
                : '—'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

const chartAxisProps = {
  tick: { fontSize: 11, fill: 'hsl(var(--muted-foreground))' },
  axisLine: { stroke: 'hsl(var(--border))' },
  tickLine: false,
} as const;

export const AnalysisCharts: React.FC<ChartsProps> = ({ analysis }) => {
  const currentBreakdown = analysis.current_tco.yearly_breakdown;
  const candidateBreakdown = analysis.candidate_tco.yearly_breakdown;
  const currentName = `${analysis.current_vehicle.brand} ${analysis.current_vehicle.model}`;
  const candidateName = `${analysis.candidate_vehicle.brand} ${analysis.candidate_vehicle.model}`;

  const tcoCurveData = currentBreakdown.map((item, index) => {
    const cand = candidateBreakdown[index];
    return {
      year: `Anno ${item.year}`,
      [currentName]: Number(item.cumulative_cost),
      [candidateName]: cand ? Number(cand.cumulative_cost) : 0,
    };
  });

  const lastCurrent = currentBreakdown[currentBreakdown.length - 1];
  const lastCandidate = candidateBreakdown[candidateBreakdown.length - 1];
  const finalDelta =
    lastCurrent && lastCandidate
      ? Number(lastCurrent.cumulative_cost) - Number(lastCandidate.cumulative_cost)
      : 0;

  const costBreakdownData = [
    { name: 'Energia / Carburante', value: Number(analysis.candidate_tco.total_energy_fuel_cost), color: '#10B981' },
    { name: 'Manutenzione', value: Number(analysis.candidate_tco.total_maintenance_cost), color: '#3B82F6' },
    { name: 'Assicurazione', value: Number(analysis.candidate_tco.total_insurance_cost), color: '#8B5CF6' },
    { name: 'Bollo / Tasse', value: Number(analysis.candidate_tco.total_taxes), color: '#F59E0B' },
    { name: 'Interessi finanziamento', value: Number(analysis.candidate_tco.total_financing_interest), color: '#EF4444' },
  ].filter((item) => item.value > 0);

  const costTotal = costBreakdownData.reduce((acc, item) => acc + item.value, 0);

  const rangeData = [
    { type: 'Misto reale', range: Number(analysis.candidate_range.mixed_range_km), color: '#10B981' },
    { type: 'Urbano', range: Number(analysis.candidate_range.urban_range_km), color: '#3B82F6' },
    { type: 'Autostrada', range: Number(analysis.candidate_range.highway_range_km), color: '#8B5CF6' },
    { type: 'Inverno autostrada', range: Number(analysis.candidate_range.winter_highway_range_km), color: '#F59E0B' },
  ];

  const degradationData = Object.entries(analysis.candidate_battery_degradation.yearly_ranges_km).map(
    ([year, range]) => ({ year: Number(year), range: Number(range) }),
  );

  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
      {/* Cumulative TCO */}
      <Card className="p-5">
        <SectionHeader
          icon={<LineChartIcon className="h-4 w-4" />}
          title="TCO cumulativo"
          subtitle={
            Math.abs(finalDelta) < 1
              ? 'Costi totali sostanzialmente equivalenti al termine del periodo.'
              : finalDelta > 0
                ? `Al termine del periodo: ${fmtEUR(finalDelta)} in meno con l’elettrico.`
                : `Al termine del periodo: ${fmtEUR(-finalDelta)} in più con l’elettrico.`
          }
        />
        <div className="h-64" role="img" aria-label="Grafico dell'andamento del costo totale di possesso cumulativo">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={tcoCurveData} margin={{ top: 4, right: 8, left: 4, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="year" {...chartAxisProps} />
              <YAxis {...chartAxisProps} width={58} tickFormatter={(v) => fmtEURCompact(v)} />
              <Tooltip content={<ChartTooltip formatter={(value) => fmtEUR(value)} />} />
              <Line
                type="monotone"
                dataKey={currentName}
                stroke="#EF4444"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey={candidateName}
                stroke="#10B981"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3 flex flex-wrap gap-4 text-xs font-semibold">
          <span className="inline-flex items-center gap-1.5 text-muted-foreground">
            <span className="h-2.5 w-2.5 rounded-full bg-[#EF4444]" aria-hidden="true" />
            {currentName} (attuale)
          </span>
          <span className="inline-flex items-center gap-1.5 text-muted-foreground">
            <span className="h-2.5 w-2.5 rounded-full bg-[#10B981]" aria-hidden="true" />
            {candidateName} (elettrico)
          </span>
        </div>
      </Card>

      {/* Cost breakdown */}
      <Card className="p-5">
        <SectionHeader
          icon={<PieChartIcon className="h-4 w-4" />}
          title="Da cosa è composto il costo"
          subtitle={`Ripartizione del TCO per ${candidateName}.`}
        />
        <div className="relative h-56" role="img" aria-label="Grafico a ciambella della ripartizione dei costi">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={costBreakdownData}
                cx="50%"
                cy="50%"
                innerRadius={62}
                outerRadius={88}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {costBreakdownData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip formatter={(value) => fmtEUR(value)} />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="overline">Totale TCO</span>
            <span className="text-lg font-black tabular-nums">{fmtEUR(costTotal)}</span>
          </div>
        </div>
        <ul className="mt-3 space-y-1.5">
          {costBreakdownData.map((item) => {
            const pct = costTotal > 0 ? (item.value / costTotal) * 100 : 0;
            return (
              <li key={item.name} className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: item.color }} aria-hidden="true" />
                <span className="text-muted-foreground">{item.name}</span>
                <span className="ml-auto tabular-nums font-semibold text-foreground">{fmtEUR(item.value)}</span>
                <span className="w-10 text-right tabular-nums text-muted-foreground">{pct.toFixed(0)}%</span>
              </li>
            );
          })}
        </ul>
      </Card>

      {/* Real-world range */}
      <Card className="p-5">
        <SectionHeader
          icon={<Gauge className="h-4 w-4" />}
          title="Autonomia reale stimata"
          subtitle={`Chilometri percorribili con un pieno di batteria, per ${candidateName}.`}
        />
        <div className="h-56" role="img" aria-label="Grafico a barre dell'autonomia reale stimata">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rangeData} layout="vertical" margin={{ top: 4, right: 48, left: 4, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
              <XAxis type="number" {...chartAxisProps} unit=" km" />
              <YAxis dataKey="type" type="category" width={128} {...chartAxisProps} />
              <Tooltip cursor={{ fill: 'hsl(var(--muted) / 0.5)' }} content={<ChartTooltip formatter={(value) => `${fmtNum(value)} km`} />} />
              <Bar dataKey="range" radius={[0, 6, 6, 0]} barSize={22}>
                {rangeData.map((entry) => (
                  <Cell key={entry.type} fill={entry.color} />
                ))}
                <LabelList
                  dataKey="range"
                  position="right"
                  formatter={(value: number) => fmtNum(value)}
                  style={{ fontSize: 11, fontWeight: 700, fill: 'hsl(var(--foreground))' }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Battery degradation */}
      <Card className="p-5">
        <SectionHeader
          icon={<BatteryCharging className="h-4 w-4" />}
          title="Degrado della batteria"
          subtitle={`Autonomia residua stimata negli anni (capacità iniziale ${fmtNum(
            analysis.candidate_battery_degradation.initial_capacity_kwh,
            1,
          )} kWh).`}
        />
        <div className="h-56" role="img" aria-label="Grafico del degrado della batteria nel tempo">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={degradationData} margin={{ top: 4, right: 12, left: 4, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="year" {...chartAxisProps} tickFormatter={(v) => (v === 0 ? 'Nuova' : `Anno ${v}`)} />
              <YAxis {...chartAxisProps} width={52} domain={['dataMin - 20', 'dataMax + 10']} tickFormatter={(v) => `${fmtNum(v)}`} />
              <Tooltip content={<ChartTooltip formatter={(value) => `${fmtNum(value)} km`} />} />
              <Line
                type="monotone"
                dataKey="range"
                name="Autonomia reale"
                stroke="#0EA5E9"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#0EA5E9' }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
};

export default AnalysisCharts;
