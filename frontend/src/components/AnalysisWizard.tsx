import React, { useState } from 'react';
import { Vehicle, UsageProfile, ChargingProfile, OwnershipScenario, VehicleType, FuelType } from '../types/api';

interface AnalysisWizardProps {
  onRunAnalysis: (payload: {
    current_vehicle: Vehicle;
    candidate_vehicle: Vehicle;
    usage: UsageProfile;
    charging: ChargingProfile;
    ownership: OwnershipScenario;
  }) => void;
  isLoading: boolean;
}

export const AnalysisWizard: React.FC<AnalysisWizardProps> = ({ onRunAnalysis, isLoading }) => {
  const [step, setStep] = useState(1);

  const [currentVehicle, setCurrentVehicle] = useState<Vehicle>({
    brand: 'Honda',
    model: 'CR-V',
    version: '1.6 i-DTEC',
    year: 2016,
    vehicle_type: VehicleType.DIESEL,
    fuel_type: FuelType.DIESEL,
    purchase_price: 12000,
    current_value: 5000,
    annual_tax: 250,
    urban_consumption: 5.5,
    extraurban_consumption: 4.5,
    highway_consumption: 6.0,
    maintenance_cost_per_year: 700,
    insurance_cost_per_year: 600,
    tire_cost_per_year: 150,
  });

  const [candidateVehicle, setCandidateVehicle] = useState<Vehicle>({
    brand: 'Renault',
    model: 'Zoe',
    version: 'R110 52kWh',
    year: 2022,
    vehicle_type: VehicleType.BEV,
    fuel_type: FuelType.ELECTRICITY,
    purchase_price: 12900,
    annual_tax: 0,
    urban_consumption: 13.0,
    extraurban_consumption: 15.0,
    highway_consumption: 20.0,
    battery_capacity: 52,
    usable_battery_capacity: 52,
    wltp_range: 395,
    maintenance_cost_per_year: 250,
    insurance_cost_per_year: 500,
    tire_cost_per_year: 120,
  });

  const [usage, setUsage] = useState<UsageProfile>({
    annual_km: 25000,
    city_percentage: 0.4,
    extraurban_percentage: 0.4,
    highway_percentage: 0.2,
    winter_multiplier: 1.2,
  });

  const [charging, setCharging] = useState<ChargingProfile>({
    home_charging_percentage: 0.8,
    public_ac_charging_percentage: 0.1,
    public_dc_charging_percentage: 0.1,
    home_energy_price: 0.25,
    public_ac_energy_price: 0.45,
    public_dc_energy_price: 0.75,
    charging_losses_percentage: 0.1,
  });

  const [ownership, setOwnership] = useState<OwnershipScenario>({
    horizon_years: 5,
    trade_in_value: 5000,
    incentive_amount: 0,
    financing: {
      financing_type: 'CASH',
      down_payment: 0,
      financed_amount: 0,
      interest_rate_annual: 0.05,
      duration_months: 36,
      final_balloon_payment: 0,
    },
  });

  const handleFinish = () => {
    onRunAnalysis({
      current_vehicle: currentVehicle,
      candidate_vehicle: candidateVehicle,
      usage,
      charging,
      ownership,
    });
  };

  return (
    <div className="bg-card p-6 rounded-2xl border border-border shadow-md max-w-3xl mx-auto my-6">
      <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
        <h2 className="text-xl font-bold">Wizard Configurazione Analisi (Step {step} di 5)</h2>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              className={`w-8 h-2 rounded-full ${s <= step ? 'bg-primary' : 'bg-muted'}`}
            />
          ))}
        </div>
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg text-primary">Step 1 — Auto Attuale</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Marca</label>
              <input
                type="text"
                className="w-full p-2 rounded border border-input bg-background"
                value={currentVehicle.brand}
                onChange={(e) => setCurrentVehicle({ ...currentVehicle, brand: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Modello</label>
              <input
                type="text"
                className="w-full p-2 rounded border border-input bg-background"
                value={currentVehicle.model}
                onChange={(e) => setCurrentVehicle({ ...currentVehicle, model: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Valore Attuale Stimato (€)</label>
              <input
                type="number"
                className="w-full p-2 rounded border border-input bg-background"
                value={currentVehicle.current_value}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setCurrentVehicle({ ...currentVehicle, current_value: val });
                  setOwnership({ ...ownership, trade_in_value: val });
                }}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Alimentazione</label>
              <select
                className="w-full p-2 rounded border border-input bg-background"
                value={currentVehicle.fuel_type}
                onChange={(e) => setCurrentVehicle({ ...currentVehicle, fuel_type: e.target.value as FuelType })}
              >
                <option value={FuelType.DIESEL}>Diesel</option>
                <option value={FuelType.PETROL}>Benzina</option>
                <option value={FuelType.LPG}>GPL</option>
                <option value={FuelType.CNG}>Metano</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg text-primary">Step 2 — Profilo di Utilizzo</h3>
          <div>
            <label className="block text-sm font-medium mb-1">Chilometri Annui Driven ({usage.annual_km.toLocaleString()} km)</label>
            <input
              type="range"
              min={5000}
              max={60000}
              step={1000}
              className="w-full"
              value={usage.annual_km}
              onChange={(e) => setUsage({ ...usage, annual_km: Number(e.target.value) })}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">Urbano / Città (%)</label>
              <input
                type="number"
                step="0.05"
                className="w-full p-2 rounded border border-input bg-background"
                value={usage.city_percentage}
                onChange={(e) => setUsage({ ...usage, city_percentage: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Extraurbano (%)</label>
              <input
                type="number"
                step="0.05"
                className="w-full p-2 rounded border border-input bg-background"
                value={usage.extraurban_percentage}
                onChange={(e) => setUsage({ ...usage, extraurban_percentage: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Autostrada (%)</label>
              <input
                type="number"
                step="0.05"
                className="w-full p-2 rounded border border-input bg-background"
                value={usage.highway_percentage}
                onChange={(e) => setUsage({ ...usage, highway_percentage: Number(e.target.value) })}
              />
            </div>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg text-primary">Step 3 — Auto Elettrica Candidata</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Marca Candidate</label>
              <input
                type="text"
                className="w-full p-2 rounded border border-input bg-background"
                value={candidateVehicle.brand}
                onChange={(e) => setCandidateVehicle({ ...candidateVehicle, brand: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Modello</label>
              <input
                type="text"
                className="w-full p-2 rounded border border-input bg-background"
                value={candidateVehicle.model}
                onChange={(e) => setCandidateVehicle({ ...candidateVehicle, model: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Prezzo Acquisto (€)</label>
              <input
                type="number"
                className="w-full p-2 rounded border border-input bg-background"
                value={candidateVehicle.purchase_price}
                onChange={(e) => setCandidateVehicle({ ...candidateVehicle, purchase_price: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Capacità Batteria (kWh)</label>
              <input
                type="number"
                className="w-full p-2 rounded border border-input bg-background"
                value={candidateVehicle.usable_battery_capacity}
                onChange={(e) =>
                  setCandidateVehicle({
                    ...candidateVehicle,
                    battery_capacity: Number(e.target.value),
                    usable_battery_capacity: Number(e.target.value),
                  })
                }
              />
            </div>
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg text-primary">Step 4 — Ricarica ed Energia</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Ricarica a Casa (%)</label>
              <input
                type="number"
                step="0.05"
                className="w-full p-2 rounded border border-input bg-background"
                value={charging.home_charging_percentage}
                onChange={(e) => setCharging({ ...charging, home_charging_percentage: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Prezzo Energia Casa (€/kWh)</label>
              <input
                type="number"
                step="0.01"
                className="w-full p-2 rounded border border-input bg-background"
                value={charging.home_energy_price}
                onChange={(e) => setCharging({ ...charging, home_energy_price: Number(e.target.value) })}
              />
            </div>
          </div>
        </div>
      )}

      {step === 5 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg text-primary">Step 5 — Orizzonte e Finanziamento</h3>
          <div>
            <label className="block text-sm font-medium mb-1">Orizzonte di possesso ({ownership.horizon_years} Anni)</label>
            <input
              type="range"
              min={1}
              max={10}
              className="w-full"
              value={ownership.horizon_years}
              onChange={(e) => setOwnership({ ...ownership, horizon_years: Number(e.target.value) })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Valore Permuta Usato (€)</label>
              <input
                type="number"
                className="w-full p-2 rounded border border-input bg-background"
                value={ownership.trade_in_value}
                onChange={(e) => setOwnership({ ...ownership, trade_in_value: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Modalità Acquisto / Finanziamento</label>
              <select
                className="w-full p-2 rounded border border-input bg-background font-medium"
                value={ownership.financing.financing_type}
                onChange={(e) =>
                  setOwnership({
                    ...ownership,
                    financing: {
                      ...ownership.financing,
                      financing_type: e.target.value as 'CASH' | 'LOAN' | 'FINANCING' | 'LEASING',
                    },
                  })
                }
              >
                <option value="CASH">Acquisto Diretto (Cash)</option>
                <option value="LOAN">Finanziamento / Prestito Tradizionale</option>
                <option value="LEASING">Leasing / Noleggio con Maxi-Rata Finale</option>
              </select>
            </div>
          </div>

          {ownership.financing.financing_type !== 'CASH' && (
            <div className="p-4 rounded-xl bg-muted/40 border border-border space-y-3">
              <h4 className="text-sm font-semibold text-foreground">Dettagli Finanziamento / Leasing</h4>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium mb-1">Anticipo (€)</label>
                  <input
                    type="number"
                    className="w-full p-2 rounded border border-input bg-background"
                    value={ownership.financing.down_payment}
                    onChange={(e) =>
                      setOwnership({
                        ...ownership,
                        financing: { ...ownership.financing, down_payment: Number(e.target.value) },
                      })
                    }
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">Durata (Mesi)</label>
                  <input
                    type="number"
                    className="w-full p-2 rounded border border-input bg-background"
                    value={ownership.financing.duration_months}
                    onChange={(e) =>
                      setOwnership({
                        ...ownership,
                        financing: { ...ownership.financing, duration_months: Number(e.target.value) },
                      })
                    }
                  />
                </div>
                {ownership.financing.financing_type === 'LEASING' ? (
                  <>
                    <div>
                      <label className="block text-xs font-medium mb-1">Canone Mensile Leasing (€)</label>
                      <input
                        type="number"
                        className="w-full p-2 rounded border border-input bg-background"
                        value={ownership.financing.lease_monthly_fee ?? 0}
                        onChange={(e) =>
                          setOwnership({
                            ...ownership,
                            financing: { ...ownership.financing, lease_monthly_fee: Number(e.target.value) },
                          })
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium mb-1">Valore Residuo (%) Balloon Payment</label>
                      <input
                        type="number"
                        step="1"
                        className="w-full p-2 rounded border border-input bg-background"
                        value={ownership.financing.residual_value_percentage ?? 40}
                        onChange={(e) =>
                          setOwnership({
                            ...ownership,
                            financing: { ...ownership.financing, residual_value_percentage: Number(e.target.value) },
                          })
                        }
                      />
                    </div>
                  </>
                ) : (
                  <div>
                    <label className="block text-xs font-medium mb-1">Tasso Annuo (es. 0.05 per 5%)</label>
                    <input
                      type="number"
                      step="0.01"
                      className="w-full p-2 rounded border border-input bg-background"
                      value={ownership.financing.interest_rate_annual}
                      onChange={(e) =>
                        setOwnership({
                          ...ownership,
                          financing: { ...ownership.financing, interest_rate_annual: Number(e.target.value) },
                        })
                      }
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex justify-between mt-8 pt-4 border-t border-border">
        {step > 1 ? (
          <button
            onClick={() => setStep(step - 1)}
            className="px-4 py-2 rounded-lg border border-border hover:bg-muted font-medium text-sm"
          >
            Indietro
          </button>
        ) : <div />}

        {step < 5 ? (
          <button
            onClick={() => setStep(step + 1)}
            className="px-5 py-2 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:opacity-90"
          >
            Avanti
          </button>
        ) : (
          <button
            onClick={handleFinish}
            disabled={isLoading}
            className="px-6 py-2.5 rounded-lg bg-emerald-600 text-white font-bold text-sm hover:bg-emerald-700 shadow-md transition-all"
          >
            {isLoading ? 'Calcolo in corso...' : 'Calcola Analisi Decisionale'}
          </button>
        )}
      </div>
    </div>
  );
};
