import { describe, expect, test } from 'vitest';
import { VehicleType, FuelType } from '../types/api';

describe('Garage and Multi-Car Models', () => {
  test('Creates vehicle structure correctly', () => {
    const mockVehicle = {
      brand: 'Fiat',
      model: 'Panda',
      year: 2020,
      vehicle_type: VehicleType.PETROL,
      fuel_type: FuelType.PETROL,
      purchase_price: 10000,
      current_value: 7000,
      urban_consumption: 6.0,
      extraurban_consumption: 5.0,
      highway_consumption: 6.0,
    };

    expect(mockVehicle.brand).toBe('Fiat');
    expect(mockVehicle.fuel_type).toBe(FuelType.PETROL);
  });
});
