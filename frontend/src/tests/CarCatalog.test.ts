import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchCarFacets, searchCars } from '../services/api';
import { CarCatalogItem, CarFacetMap } from '../types/api';

describe('Car Catalog Service', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('should fetch car facets with the requested dimensions', async () => {
    const mockFacets: CarFacetMap = {
      make: [{ value: 'Toyota', count: 6396 }],
      model: [{ value: 'Corolla', count: 512 }],
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockFacets,
    } as Response);

    const results = await fetchCarFacets(['make', 'model'], { make: 'Toyota' });
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/v1/vehicles/car-facets?facets=make%2Cmodel&make=Toyota',
    );
    expect(results.make[0].value).toBe('Toyota');
    expect(results.model[0].count).toBe(512);
  });

  it('should search conventional cars by make and model', async () => {
    const mockCars: CarCatalogItem[] = [
      { make: 'Toyota', model: 'Corolla', year: 2020, fuel_type: 'gas', drive: 'fwd', cylinders: 4 },
    ];

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCars,
    } as Response);

    const results = await searchCars({ make: 'Toyota', model: 'Corolla', year: 2020 });
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/v1/vehicles/cars?make=Toyota&model=Corolla&year=2020',
    );
    expect(results).toEqual(mockCars);
  });
});
