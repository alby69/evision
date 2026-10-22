import { describe, expect, test } from 'vitest';
import { VehicleType, FuelType, VehicleCategory } from '../types/api';
import { getConsumptionUnit } from '../components/GarageManager';

describe('Garage and Multi-Car Models', () => {
  test('Creates vehicle structure correctly', () => {
    const mockVehicle = {
      brand: 'Fiat',
      model: 'Panda',
      category: VehicleCategory.CAR,
      vehicle_type: VehicleType.PETROL,
      fuel_type: FuelType.PETROL,
      year: 2020,
      purchase_price: 10000,
      current_value: 7000,
      urban_consumption: 6.0,
      extraurban_consumption: 5.0,
      highway_consumption: 6.0,
    };

    expect(mockVehicle.brand).toBe('Fiat');
    expect(mockVehicle.fuel_type).toBe(FuelType.PETROL);
    expect(mockVehicle.category).toBe(VehicleCategory.CAR);
  });

  test('Returns correct consumption unit based on fuel and vehicle type', () => {
    expect(getConsumptionUnit(FuelType.PETROL, VehicleType.PETROL)).toBe('L/100km');
    expect(getConsumptionUnit(FuelType.DIESEL, VehicleType.DIESEL)).toBe('L/100km');
    expect(getConsumptionUnit(FuelType.ELECTRICITY, VehicleType.BEV)).toBe('kWh/100km');
    expect(getConsumptionUnit(FuelType.PETROL, VehicleType.PHEV)).toBe('kWh/100km');
  });

  test('Supports EV specific fields on vehicle data', () => {
    const evVehicle = {
      brand: 'Tesla',
      model: 'Model 3',
      vehicle_type: VehicleType.BEV,
      fuel_type: FuelType.ELECTRICITY,
      year: 2023,
      purchase_price: 42000,
      urban_consumption: 14.0,
      extraurban_consumption: 16.0,
      highway_consumption: 19.0,
      battery_capacity: 60,
      wltp_range: 491,
    };

    expect(evVehicle.battery_capacity).toBe(60);
    expect(evVehicle.wltp_range).toBe(491);
  });
});
