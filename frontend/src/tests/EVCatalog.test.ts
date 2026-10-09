import { describe, it, expect, vi, beforeEach } from 'vitest';
import { searchEVCatalog } from '../services/api';
import { EVCatalogItem } from '../types/api';

describe('EV Catalog Service & Types', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('should fetch EV catalog items with query parameters', async () => {
    const mockItems: EVCatalogItem[] = [
      {
        make: 'Tesla',
        model: 'Model 3 Long Range',
        year: 2023,
        battery_useable_capacity: 75,
        electric_range: 576,
        vehicle_consumption: 14.7,
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockItems,
    } as Response);

    const results = await searchEVCatalog({ search: 'Tesla' });
    expect(globalThis.fetch).toHaveBeenCalledWith('/api/v1/vehicles/catalog?search=Tesla');
    expect(results).toEqual(mockItems);
    expect(results[0].make).toBe('Tesla');
    expect(results[0].battery_useable_capacity).toBe(75);
  });
});
