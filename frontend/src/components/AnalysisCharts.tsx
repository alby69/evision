import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { FullAnalysisResponse } from '../types/api';

interface ChartsProps {
  analysis: FullAnalysisResponse;
}

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];

export const AnalysisCharts: React.FC<ChartsProps> = ({ analysis }) => {
  const currentBreakdown = analysis.current_tco.yearly_breakdown;
  const candidateBreakdown = analysis.candidate_tco.yearly_breakdown;

  // TCO Cumulative Chart Data
  const tcoCurveData = currentBreakdown.map((item, index) => {
    const cand = candidateBreakdown[index];
    return {
      year: `Anno ${item.year}`,
      [analysis.current_vehicle.model]: item.cumulative_cost,
      [analysis.candidate_vehicle.model]: cand ? cand.cumulative_cost : 0,
    };
  });

  // Cost Breakdown Donut Data for Candidate
  const costBreakdownData = [
    { name: 'Energia / Carburante', value: analysis.candidate_tco.total_energy_fuel_cost },
    { name: 'Manutenzione', value: analysis.candidate_tco.total_maintenance_cost },
    { name: 'Assicurazione', value: analysis.candidate_tco.total_insurance_cost },
    { name: 'Bollo / Tasse', value: analysis.candidate_tco.total_taxes },
    { name: 'Interessi Finanziamento', value: analysis.candidate_tco.total_financing_interest },
  ].filter((item) => item.value > 0);

  // Range Comparison
  const rangeData = [
    { type: 'Misto Reale', range: analysis.candidate_range.mixed_range_km },
    { type: 'Urbano', range: analysis.candidate_range.urban_range_km },
    { type: 'Autostrada', range: analysis.candidate_range.highway_range_km },
    { type: 'Inverno Autostrada', range: analysis.candidate_range.winter_highway_range_km },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      {/* Cumulative TCO Line Chart */}
      <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
        <h3 className="text-base font-semibold mb-3">Confronto TCO Cumulativo (€)</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={tcoCurveData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => [`€ ${value}`, 'TCO Cumulativo']} />
              <Legend />
              <Line
                type="monotone"
                dataKey={analysis.current_vehicle.model}
                stroke="#EF4444"
                strokeWidth={3}
              />
              <Line
                type="monotone"
                dataKey={analysis.candidate_vehicle.model}
                stroke="#10B981"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cost Breakdown Donut Chart */}
      <div className="bg-card p-5 rounded-xl border border-border shadow-sm">
        <h3 className="text-base font-semibold mb-3">Ripartizione Costi: {analysis.candidate_vehicle.model}</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={costBreakdownData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={5}
                dataKey="value"
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
              >
                {costBreakdownData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`€ ${value}`, 'Costo Totale']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Real-World Range Bar Chart */}
      <div className="bg-card p-5 rounded-xl border border-border shadow-sm md:col-span-2">
        <h3 className="text-base font-semibold mb-3">Autonomia Reale Stimata (km) - {analysis.candidate_vehicle.model}</h3>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rangeData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis type="number" unit=" km" />
              <YAxis dataKey="type" type="category" width={130} />
              <Tooltip formatter={(value) => [`${value} km`, 'Autonomia Reale']} />
              <Bar dataKey="range" fill="#3B82F6" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
