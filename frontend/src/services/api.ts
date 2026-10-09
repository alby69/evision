import { FullAnalysisResponse, Vehicle } from '../types/api';

const API_BASE = '/api/v1';

export async function fetchDemoVehicles(): Promise<Vehicle[]> {
  const res = await fetch(`${API_BASE}/vehicles`);
  if (!res.ok) throw new Error('Failed to fetch vehicles');
  return res.json();
}

export async function fetchDemoAnalysis(): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyses/demo`);
  if (!res.ok) throw new Error('Failed to fetch demo analysis');
  return res.json();
}

export async function fetchAnalysisById(id: string): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyses/${id}`);
  if (!res.ok) throw new Error('Failed to fetch analysis');
  return res.json();
}

export async function createAnalysis(payload: unknown): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to compute analysis');
  return res.json();
}
