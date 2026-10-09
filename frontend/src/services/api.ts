import { EVCatalogItem, FullAnalysisResponse, Vehicle } from '../types/api';

const API_BASE = '/api/v1';

export async function searchEVCatalog(query?: {
  make?: string;
  model?: string;
  search?: string;
  min_year?: number;
  max_year?: number;
  limit?: number;
}): Promise<EVCatalogItem[]> {
  const params = new URLSearchParams();
  if (query?.make) params.append('make', query.make);
  if (query?.model) params.append('model', query.model);
  if (query?.search) params.append('search', query.search);
  if (query?.min_year) params.append('min_year', query.min_year.toString());
  if (query?.max_year) params.append('max_year', query.max_year.toString());
  if (query?.limit) params.append('limit', query.limit.toString());

  const queryString = params.toString();
  const url = `${API_BASE}/vehicles/catalog${queryString ? `?${queryString}` : ''}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch vehicle catalog');
  return res.json();
}

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
