import {
  CarCatalogItem,
  CarFacetMap,
  EVCatalogItem,
  FullAnalysisResponse,
  Vehicle,
  VehicleValuation,
  VehicleValuationRequest,
} from '../types/api';

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
  if (!res.ok) throw new Error('Impossibile caricare il catalogo veicoli.');
  return res.json();
}

export async function fetchCarFacets(
  facets: string[],
  query?: {
    make?: string;
    model?: string;
    generation?: string;
    body?: string;
    fuel?: string;
    transmission?: string;
    drive?: string;
    year?: number;
  },
): Promise<CarFacetMap> {
  const params = new URLSearchParams();
  params.append('facets', facets.join(','));
  if (query?.make) params.append('make', query.make);
  if (query?.model) params.append('model', query.model);
  if (query?.generation) params.append('generation', query.generation);
  if (query?.body) params.append('body', query.body);
  if (query?.fuel) params.append('fuel', query.fuel);
  if (query?.transmission) params.append('transmission', query.transmission);
  if (query?.drive) params.append('drive', query.drive);
  if (query?.year) params.append('year', query.year.toString());

  const res = await fetch(`${API_BASE}/vehicles/car-facets?${params.toString()}`);
  if (!res.ok) throw new Error('Impossibile caricare i filtri del catalogo auto.');
  return res.json();
}

export async function searchCars(query: {
  make: string;
  model: string;
  year?: number;
  fuel_type?: string;
}): Promise<CarCatalogItem[]> {
  const params = new URLSearchParams();
  params.append('make', query.make);
  params.append('model', query.model);
  if (query.year) params.append('year', query.year.toString());
  if (query.fuel_type) params.append('fuel_type', query.fuel_type);

  const res = await fetch(`${API_BASE}/vehicles/cars?${params.toString()}`);
  if (!res.ok) throw new Error('Impossibile caricare il catalogo auto.');
  return res.json();
}

export async function estimateVehicleValue(
  payload: VehicleValuationRequest,
): Promise<VehicleValuation> {
  const res = await fetch(`${API_BASE}/vehicles/valuation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let detail = 'Stima non disponibile';
    try {
      const data = await res.json();
      if (data?.detail) detail = typeof data.detail === 'string' ? data.detail : detail;
    } catch {
      /* response had no JSON body */
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function fetchDemoVehicles(): Promise<Vehicle[]> {
  const res = await fetch(`${API_BASE}/vehicles`);
  if (!res.ok) throw new Error('Impossibile caricare i veicoli di esempio.');
  return res.json();
}

export async function fetchDemoAnalysis(): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyses/demo`);
  if (!res.ok) throw new Error('Impossibile caricare l’analisi dimostrativa.');
  return res.json();
}

export async function fetchAnalysisById(id: string): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyses/${id}`);
  if (!res.ok) throw new Error('Impossibile caricare l’analisi.');
  return res.json();
}

export async function createAnalysis(payload: unknown): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Impossibile calcolare l’analisi. Controlla i dati inseriti.');
  return res.json();
}
