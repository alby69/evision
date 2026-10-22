import React, { useEffect, useState } from 'react';
import { SavedVehicleResponse, Vehicle, VehicleCategory, VehicleType, FuelType } from '../types/api';
import { listGarageVehicles, createGarageVehicle, updateGarageVehicle, deleteGarageVehicle } from '../services/api';
import { X, Trash2, Edit, Plus, Car } from 'lucide-react';
import { Field, TextInput, NumberInput, SelectInput } from './ui';

interface GarageManagerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectVehicle?: (vehicle: Vehicle) => void;
  currentVehicle?: Vehicle;
}

const FUEL_OPTIONS = [
  { value: FuelType.PETROL, label: 'Benzina' },
  { value: FuelType.DIESEL, label: 'Diesel' },
  { value: FuelType.LPG, label: 'GPL' },
  { value: FuelType.CNG, label: 'Metano' },
  { value: FuelType.ELECTRICITY, label: 'Elettrico' },
];

const CATEGORY_OPTIONS = [
  { value: VehicleCategory.CAR, label: 'Autovettura' },
  { value: VehicleCategory.SUV, label: 'SUV / Crossover' },
  { value: VehicleCategory.VAN, label: 'Furgone / Commerciale' },
  { value: VehicleCategory.MOTORCYCLE, label: 'Motociclo' },
];

const getConsumptionUnit = (fuelType: FuelType, vehicleType: VehicleType) => {
  if (fuelType === FuelType.ELECTRICITY || vehicleType === VehicleType.BEV) {
    return 'kWh/100km';
  }
  return 'L/100km';
};

const emptyVehicle: Vehicle = {
  brand: '',
  model: '',
  version: '',
  year: new Date().getFullYear(),
  category: VehicleCategory.CAR,
  vehicle_type: VehicleType.PETROL,
  fuel_type: FuelType.PETROL,
  purchase_price: 15000,
  current_value: 12000,
  annual_tax: 150,
  urban_consumption: 6.5,
  extraurban_consumption: 5.0,
  highway_consumption: 6.0,
  maintenance_cost_per_year: 300,
  insurance_cost_per_year: 500,
  tire_cost_per_year: 150,
};

export const GarageManager: React.FC<GarageManagerProps> = ({
  isOpen,
  onClose,
  onSelectVehicle,
  currentVehicle,
}) => {
  const [vehicles, setVehicles] = useState<SavedVehicleResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<{
    name: string;
    is_default: boolean;
    vehicle: Vehicle;
  }>({ name: '', is_default: false, vehicle: { ...emptyVehicle } });

  const loadVehicles = async () => {
    setLoading(true);
    try {
      const data = await listGarageVehicles();
      setVehicles(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadVehicles();
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editingId) {
        await updateGarageVehicle(editingId, {
          name: formData.name,
          is_default: formData.is_default,
          vehicle_data: formData.vehicle,
        });
      } else {
        await createGarageVehicle({
          name: formData.name,
          is_default: formData.is_default,
          vehicle_data: formData.vehicle,
        });
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({ name: '', is_default: false, vehicle: { ...emptyVehicle } });
      await loadVehicles();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (vehicle: SavedVehicleResponse) => {
    setEditingId(vehicle.id);
    setFormData({
      name: vehicle.name,
      is_default: vehicle.is_default,
      vehicle: vehicle.vehicle_data,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Eliminare questo veicolo dal garage?')) return;
    try {
      await deleteGarageVehicle(id);
      await loadVehicles();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelect = (vehicle: SavedVehicleResponse) => {
    if (onSelectVehicle) {
      onSelectVehicle(vehicle.vehicle_data);
    }
    onClose();
  };

  const handleNewVehicle = () => {
    setEditingId(null);
    setFormData({
      name: '',
      is_default: false,
      vehicle: currentVehicle ? { ...currentVehicle } : { ...emptyVehicle },
    });
    setShowForm(true);
  };

  const handleInputChange = (field: keyof Vehicle, value: string | number) => {
    setFormData((prev) => ({
      ...prev,
      vehicle: { ...prev.vehicle, [field]: value },
    }));
  };

  const handleSelectChange = (field: keyof Vehicle, value: string) => {
    setFormData((prev) => {
      const updatedVehicle = { ...prev.vehicle, [field]: value as Vehicle[keyof Vehicle] };
      if (field === 'fuel_type') {
        if (value === FuelType.ELECTRICITY && updatedVehicle.vehicle_type !== VehicleType.PHEV) {
          updatedVehicle.vehicle_type = VehicleType.BEV;
        } else if (value === FuelType.PETROL && updatedVehicle.vehicle_type === VehicleType.BEV) {
          updatedVehicle.vehicle_type = VehicleType.PETROL;
        } else if (value === FuelType.DIESEL && updatedVehicle.vehicle_type === VehicleType.BEV) {
          updatedVehicle.vehicle_type = VehicleType.DIESEL;
        } else if (value === FuelType.LPG && updatedVehicle.vehicle_type === VehicleType.BEV) {
          updatedVehicle.vehicle_type = VehicleType.LPG;
        } else if (value === FuelType.CNG && updatedVehicle.vehicle_type === VehicleType.BEV) {
          updatedVehicle.vehicle_type = VehicleType.CNG;
        }
      }
      return {
        ...prev,
        vehicle: updatedVehicle,
      };
    });
  };

  const consumptionUnit = getConsumptionUnit(
    formData.vehicle.fuel_type,
    formData.vehicle.vehicle_type
  );

  const isEV =
    formData.vehicle.fuel_type === FuelType.ELECTRICITY ||
    formData.vehicle.vehicle_type === VehicleType.BEV ||
    formData.vehicle.vehicle_type === VehicleType.PHEV;

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-foreground/60 p-3 backdrop-blur-sm sm:p-6"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="garage-title"
        className="mx-auto my-2 w-full max-w-4xl animate-scale-in rounded-2xl border border-border bg-card shadow-lift sm:my-6"
      >
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4 sm:px-6">
          <div>
            <div className="flex items-center gap-2">
              <Car className="h-5 w-5 text-primary" />
              <h2 id="garage-title" className="text-lg font-extrabold">Il mio garage</h2>
            </div>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Salva e gestisci i tuoi veicoli per analisi future.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="btn-ghost h-10 w-10 shrink-0 p-0"
            aria-label="Chiudi garage"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-5 sm:p-6">
          {showForm ? (
            <form onSubmit={handleSubmit} className="space-y-4 max-h-[60vh] overflow-y-auto">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-base font-bold">
                  {editingId ? 'Modifica veicolo' : 'Nuovo veicolo'}
                </h3>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingId(null);
                    setFormData({ name: '', is_default: false, vehicle: { ...emptyVehicle } });
                  }}
                  className="btn-ghost h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <Field label="Nome veicolo *" htmlFor="garage-name">
                <TextInput
                  id="garage-name"
                  value={formData.name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                  placeholder="Es. Mia auto, Auto di Paolo, ecc."
                  required
                />
              </Field>

              <Field label="Imposta come predefinita" htmlFor="garage-default">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    id="garage-default"
                    type="checkbox"
                    checked={formData.is_default}
                    onChange={(e) => setFormData((prev) => ({ ...prev, is_default: e.target.checked }))}
                    className="rounded border-input bg-background text-primary focus:ring-primary/20"
                  />
                  <span className="text-sm">Usa questo veicolo come predefinito nelle nuove analisi</span>
                </label>
              </Field>

              <div className="border-t border-border pt-4">
                <h4 className="text-sm font-semibold mb-3">Dati veicolo</h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <Field label="Marca *" htmlFor="gv-brand">
                    <TextInput
                      id="gv-brand"
                      value={formData.vehicle.brand}
                      onChange={(e) => handleInputChange('brand', e.target.value)}
                      required
                    />
                  </Field>
                  <Field label="Modello *" htmlFor="gv-model">
                    <TextInput
                      id="gv-model"
                      value={formData.vehicle.model}
                      onChange={(e) => handleInputChange('model', e.target.value)}
                      required
                    />
                  </Field>
                  <Field label="Versione" htmlFor="gv-version">
                    <TextInput
                      id="gv-version"
                      value={formData.vehicle.version ?? ''}
                      onChange={(e) => handleInputChange('version', e.target.value)}
                    />
                  </Field>
                  <Field label="Anno" htmlFor="gv-year">
                    <NumberInput
                      id="gv-year"
                      min={1990}
                      max={2030}
                      value={formData.vehicle.year}
                      onChange={(e) => handleInputChange('year', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label="Alimentazione" htmlFor="gv-fuel">
                    <SelectInput
                      id="gv-fuel"
                      value={formData.vehicle.fuel_type}
                      onChange={(e) => handleSelectChange('fuel_type', e.target.value)}
                    >
                      {FUEL_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </SelectInput>
                  </Field>
                  <Field label="Categoria veicolo" htmlFor="gv-category">
                    <SelectInput
                      id="gv-category"
                      value={formData.vehicle.category ?? VehicleCategory.CAR}
                      onChange={(e) => handleSelectChange('category', e.target.value)}
                    >
                      {CATEGORY_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </SelectInput>
                  </Field>
                  <Field
                    label="Prezzo acquisto (€) *"
                    htmlFor="gv-price"
                    hint="Prezzo effettivamente pagato all'acquisto (o valore di mercato al momento dell'acquisto/permuta)."
                  >
                    <NumberInput
                      id="gv-price"
                      min={0.1}
                      step={100}
                      value={formData.vehicle.purchase_price}
                      onChange={(e) => handleInputChange('purchase_price', Number(e.target.value) || 0)}
                      required
                    />
                  </Field>
                  <Field label="Valore attuale (€)" htmlFor="gv-value">
                    <NumberInput
                      id="gv-value"
                      min={0}
                      value={formData.vehicle.current_value ?? 0}
                      onChange={(e) => handleInputChange('current_value', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label="Bollo annuo (€)" htmlFor="gv-tax">
                    <NumberInput
                      id="gv-tax"
                      min={0}
                      value={formData.vehicle.annual_tax ?? 0}
                      onChange={(e) => handleInputChange('annual_tax', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label={`Consumo urbano (${consumptionUnit})`} htmlFor="gv-urban">
                    <NumberInput
                      id="gv-urban"
                      min={0.1}
                      step={0.1}
                      value={formData.vehicle.urban_consumption}
                      onChange={(e) => handleInputChange('urban_consumption', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label={`Consumo extraurbano (${consumptionUnit})`} htmlFor="gv-extra">
                    <NumberInput
                      id="gv-extra"
                      min={0.1}
                      step={0.1}
                      value={formData.vehicle.extraurban_consumption}
                      onChange={(e) => handleInputChange('extraurban_consumption', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label={`Consumo autostrada (${consumptionUnit})`} htmlFor="gv-highway">
                    <NumberInput
                      id="gv-highway"
                      min={0.1}
                      step={0.1}
                      value={formData.vehicle.highway_consumption}
                      onChange={(e) => handleInputChange('highway_consumption', Number(e.target.value) || 0)}
                    />
                  </Field>
                  {isEV && (
                    <>
                      <Field label="Capacità batteria lorda (kWh)" htmlFor="gv-battery">
                        <NumberInput
                          id="gv-battery"
                          min={0}
                          step={0.1}
                          value={formData.vehicle.battery_capacity ?? 0}
                          onChange={(e) => handleInputChange('battery_capacity', Number(e.target.value) || 0)}
                        />
                      </Field>
                      <Field label="Autonomia WLTP dichiarata (km)" htmlFor="gv-wltp">
                        <NumberInput
                          id="gv-wltp"
                          min={0}
                          step={1}
                          value={formData.vehicle.wltp_range ?? 0}
                          onChange={(e) => handleInputChange('wltp_range', Number(e.target.value) || 0)}
                        />
                      </Field>
                    </>
                  )}
                  <Field label="Manutenzione annua (€)" htmlFor="gv-maint">
                    <NumberInput
                      id="gv-maint"
                      min={0}
                      value={formData.vehicle.maintenance_cost_per_year ?? 0}
                      onChange={(e) => handleInputChange('maintenance_cost_per_year', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label="Assicurazione annua (€)" htmlFor="gv-ins">
                    <NumberInput
                      id="gv-ins"
                      min={0}
                      value={formData.vehicle.insurance_cost_per_year ?? 0}
                      onChange={(e) => handleInputChange('insurance_cost_per_year', Number(e.target.value) || 0)}
                    />
                  </Field>
                  <Field label="Pneumatici annui (€)" htmlFor="gv-tires">
                    <NumberInput
                      id="gv-tires"
                      min={0}
                      value={formData.vehicle.tire_cost_per_year ?? 0}
                      onChange={(e) => handleInputChange('tire_cost_per_year', Number(e.target.value) || 0)}
                    />
                  </Field>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-border">
                <button type="button" onClick={() => setShowForm(false)} className="btn-outline">
                  Annulla
                </button>
                <button type="submit" disabled={loading} className="btn-primary">
                  {loading ? 'Salvataggio...' : editingId ? 'Salva modifiche' : 'Aggiungi al garage'}
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold">Veicoli salvati ({vehicles.length})</h3>
                <button onClick={handleNewVehicle} className="btn-primary h-10 px-4">
                  <Plus className="h-4 w-4" />
                  Aggiungi veicolo
                </button>
              </div>

              {loading ? (
                <div className="flex justify-center py-8">
                  <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                </div>
              ) : vehicles.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Car className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">Nessun veicolo salvato. Aggiungi il tuo primo veicolo!</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[60vh] overflow-y-auto">
                  {vehicles.map((v) => (
                    <div
                      key={v.id}
                      className={`rounded-xl border p-4 transition-colors ${
                        v.is_default ? 'border-primary/50 bg-primary/5' : 'border-border hover:border-primary/30'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold truncate">{v.name}</h4>
                            {v.is_default && (
                              <span className="rounded-full bg-primary/10 text-primary text-[10px] font-bold px-2 py-0.5">
                                Predefinito
                              </span>
                            )}
                          </div>
                          <p className="mt-1 text-sm text-muted-foreground">
                            {v.vehicle_data.brand} {v.vehicle_data.model}
                            {v.vehicle_data.version && ` — ${v.vehicle_data.version}`}
                            {v.vehicle_data.year && ` (${v.vehicle_data.year})`}
                            {' — '}
                            {v.vehicle_data.fuel_type === FuelType.ELECTRICITY ? 'Elettrica' : v.vehicle_data.fuel_type}
                          </p>
                          <p className="mt-0.5 text-xs text-muted-foreground">
                            Valore: {v.vehicle_data.current_value ? `€${v.vehicle_data.current_value.toLocaleString()}` : 'N/D'} ·{' '}
                            Consumo: {v.vehicle_data.extraurban_consumption || 0}{' '}
                            {getConsumptionUnit(v.vehicle_data.fuel_type, v.vehicle_data.vehicle_type)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          {onSelectVehicle && (
                            <button
                              onClick={() => handleSelect(v)}
                              className="btn-outline h-9 px-3 text-sm"
                            >
                              Usa in analisi
                            </button>
                          )}
                          <button
                            onClick={() => handleEdit(v)}
                            className="btn-ghost h-9 w-9 p-0"
                            aria-label="Modifica veicolo"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(v.id)}
                            className="btn-ghost h-9 w-9 p-0 text-destructive hover:bg-destructive/10"
                            aria-label="Elimina veicolo"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GarageManager;