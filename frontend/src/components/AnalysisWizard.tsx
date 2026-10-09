import React, { useEffect, useRef, useState } from 'react';
import {
  Vehicle,
  UsageProfile,
  ChargingProfile,
  OwnershipScenario,
  VehicleType,
  FuelType,
  EVCatalogItem,
} from '../types/api';
import { EVSearchSelect } from './EVSearchSelect';
import { Field, NumberInput, SelectInput, RangeSlider, TextInput } from './ui';
import {
  X,
  Car,
  Route,
  Zap,
  Plug,
  Wallet,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Check,
} from 'lucide-react';
import { fmtEUR, fmtNum } from '../utils/format';

export interface AnalysisPayload {
  current_vehicle: Vehicle;
  candidate_vehicle: Vehicle;
  usage: UsageProfile;
  charging: ChargingProfile;
  ownership: OwnershipScenario;
}

interface AnalysisWizardProps {
  onRunAnalysis: (payload: AnalysisPayload) => void;
  isLoading: boolean;
  onClose: () => void;
}

const STEPS = [
  { label: 'Auto attuale', icon: Car },
  { label: 'Utilizzo', icon: Route },
  { label: 'EV candidata', icon: Zap },
  { label: 'Ricarica', icon: Plug },
  { label: 'Orizzonte', icon: Wallet },
] as const;

const clamp = (n: number, min: number, max: number) => Math.min(max, Math.max(min, n));
const toPercent = (dec: number) => Math.round(dec * 100);
const fromPercent = (pct: number) => clamp(pct, 0, 100) / 100;
const splitSum = (...values: number[]) => values.reduce((acc, v) => acc + v, 0);
const isFull = (sumDec: number) => Math.abs(sumDec - 1) < 0.005;

const PercentInput: React.FC<{
  label: string;
  value: number;
  onChange: (dec: number) => void;
  hint?: string;
}> = ({ label, value, onChange, hint }) => {
  const id = `pct-${label.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`;
  return (
    <div>
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <div className="relative">
        <NumberInput
          id={id}
          min={0}
          max={100}
          step={1}
          className="pr-9"
          value={toPercent(value)}
          onChange={(e) => onChange(fromPercent(Number(e.target.value)))}
          aria-label={label}
        />
        <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs font-bold text-muted-foreground">
          %
        </span>
      </div>
      {hint && <p className="field-hint">{hint}</p>}
    </div>
  );
};

const SumBadge: React.FC<{ sumDec: number; label: string }> = ({ sumDec, label }) => {
  const sum = toPercent(sumDec);
  const ok = isFull(sumDec);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold tabular-nums transition-colors ${
        ok
          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
          : 'border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-400'
      }`}
      role="status"
    >
      {ok && <Check className="h-3.5 w-3.5" aria-hidden="true" />}
      {label}: {sum}% {ok ? '' : '— deve essere 100%'}
    </span>
  );
};

export const AnalysisWizard: React.FC<AnalysisWizardProps> = ({
  onRunAnalysis,
  isLoading,
  onClose,
}) => {
  const [step, setStep] = useState(1);
  const [maxStep, setMaxStep] = useState(1);

  const panelRef = useRef<HTMLDivElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);

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

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    titleRef.current?.focus();
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, []);

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: 0 });
  }, [step]);

  const usageSum = splitSum(usage.city_percentage, usage.extraurban_percentage, usage.highway_percentage);
  const chargingSum = splitSum(
    charging.home_charging_percentage,
    charging.public_ac_charging_percentage,
    charging.public_dc_charging_percentage,
  );

  const stepErrors: Record<number, string | null> = {
    1: !currentVehicle.brand.trim() || !currentVehicle.model.trim()
      ? 'Marca e modello dell’auto attuale sono obbligatori.'
      : null,
    2: !isFull(usageSum) ? 'La ripartizione del profilo di guida deve totalizzare 100%.' : null,
    3: !candidateVehicle.brand.trim() || !candidateVehicle.model.trim()
      ? 'Marca e modello del veicolo candidato sono obbligatori.'
      : candidateVehicle.purchase_price <= 0
        ? 'Il prezzo di acquisto deve essere maggiore di zero.'
        : null,
    4: !isFull(chargingSum)
      ? 'La ripartizione delle modalità di ricarica deve totalizzare 100%.'
      : charging.home_energy_price <= 0
        ? 'Il prezzo dell’energia a casa deve essere maggiore di zero.'
        : null,
    5: null,
  };

  const canProceed = stepErrors[step] === null;

  const goNext = () => {
    if (!canProceed || step >= STEPS.length) return;
    const next = step + 1;
    setStep(next);
    setMaxStep((m) => Math.max(m, next));
  };

  const goBack = () => {
    if (step > 1) setStep(step - 1);
    else onClose();
  };

  const handlePanelKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key !== 'Tab') return;
    const focusable = Array.from(
      panelRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), select:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])',
      ) ?? [],
    ).filter((el) => el.offsetParent !== null);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  const handleFinish = () => {
    if (!stepErrors[5]) {
      onRunAnalysis({
        current_vehicle: currentVehicle,
        candidate_vehicle: candidateVehicle,
        usage,
        charging,
        ownership,
      });
    }
  };

  const handleCatalogVehicleSelect = (item: EVCatalogItem) => {
    const usableBatt =
      item.battery_useable_capacity || item.battery_capacity || candidateVehicle.usable_battery_capacity || 50;
    const grossBatt = item.battery_capacity || usableBatt;
    const cons = item.vehicle_consumption || candidateVehicle.extraurban_consumption;

    setCandidateVehicle({
      ...candidateVehicle,
      brand: item.make,
      model: item.model,
      year: item.year || item.year_start || candidateVehicle.year,
      purchase_price: item.estimated_price_eur || candidateVehicle.purchase_price,
      battery_capacity: grossBatt,
      usable_battery_capacity: usableBatt,
      wltp_range: item.electric_range || candidateVehicle.wltp_range,
      charging_dc_power: item.charge_power_max || candidateVehicle.charging_dc_power,
      urban_consumption: Math.round(cons * 0.9 * 10) / 10,
      extraurban_consumption: cons,
      highway_consumption: Math.round(cons * 1.3 * 10) / 10,
    });
  };

  const financingType = ownership.financing.financing_type;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-foreground/60 p-3 backdrop-blur-sm sm:p-6 print:hidden"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="wizard-title"
        onKeyDown={handlePanelKeyDown}
        className="mx-auto my-2 w-full max-w-3xl animate-scale-in rounded-2xl border border-border bg-card shadow-lift sm:my-6"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4 sm:px-6">
          <div>
            <div className="overline">Nuova analisi</div>
            <h2 id="wizard-title" ref={titleRef} tabIndex={-1} className="mt-0.5 text-lg font-extrabold outline-none">
              Configura il confronto
            </h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Passo {step} di {STEPS.length} · {STEPS[step - 1].label}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="btn-ghost h-10 w-10 shrink-0 p-0"
            aria-label="Chiudi wizard"
            title="Chiudi (Esc)"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Stepper */}
        <nav aria-label="Progresso wizard" className="overflow-x-auto border-b border-border px-3 py-3 sm:px-5">
          <ol className="flex min-w-max items-center">
            {STEPS.map((s, index) => {
              const number = index + 1;
              const state = number < step ? 'done' : number === step ? 'current' : 'todo';
              const reachable = number <= maxStep && number !== step;
              return (
                <li key={s.label} className="flex items-center">
                  <button
                    type="button"
                    onClick={() => reachable && setStep(number)}
                    disabled={!reachable}
                    aria-current={state === 'current' ? 'step' : undefined}
                    aria-label={`Passo ${number}: ${s.label}`}
                    className={`flex items-center gap-2 rounded-full px-2.5 py-2 transition ${
                      reachable ? 'hover:bg-muted' : 'cursor-default'
                    }`}
                  >
                    <span
                      className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 text-[11px] font-bold transition-colors ${
                        state === 'done'
                          ? 'border-primary bg-primary text-primary-foreground'
                          : state === 'current'
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border text-muted-foreground'
                      }`}
                    >
                      {state === 'done' ? <Check className="h-3.5 w-3.5" /> : number}
                    </span>
                    <span
                      className={`hidden text-xs font-semibold sm:inline ${
                        state === 'current' ? 'text-foreground' : 'text-muted-foreground'
                      }`}
                    >
                      {s.label}
                    </span>
                  </button>
                  {index < STEPS.length - 1 && (
                    <span
                      aria-hidden="true"
                      className={`mx-1 hidden h-px w-8 sm:block ${number < step ? 'bg-primary' : 'bg-border'}`}
                    />
                  )}
                </li>
              );
            })}
          </ol>
        </nav>

        {/* Body */}
        <div ref={bodyRef} className="max-h-[58vh] overflow-y-auto px-5 py-5 sm:px-6">
          <div key={step} className="animate-fade-up space-y-5">
            {step === 1 && (
              <section aria-label="Dati del veicolo attuale">
                <h3 className="text-base font-bold">Il tuo veicolo attuale</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  È la base di confronto: il motore calcola quanto continua a costarti se lo tieni.
                </p>
                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <Field label="Marca *" htmlFor="cv-brand">
                    <TextInput
                      id="cv-brand"
                      value={currentVehicle.brand}
                      aria-invalid={!currentVehicle.brand.trim()}
                      onChange={(e) => setCurrentVehicle({ ...currentVehicle, brand: e.target.value })}
                    />
                  </Field>
                  <Field label="Modello *" htmlFor="cv-model">
                    <TextInput
                      id="cv-model"
                      value={currentVehicle.model}
                      aria-invalid={!currentVehicle.model.trim()}
                      onChange={(e) => setCurrentVehicle({ ...currentVehicle, model: e.target.value })}
                    />
                  </Field>
                  <Field label="Versione" htmlFor="cv-version">
                    <TextInput
                      id="cv-version"
                      value={currentVehicle.version ?? ''}
                      onChange={(e) => setCurrentVehicle({ ...currentVehicle, version: e.target.value })}
                    />
                  </Field>
                  <Field label="Anno di immatricolazione" htmlFor="cv-year">
                    <NumberInput
                      id="cv-year"
                      min={1990}
                      max={2030}
                      value={currentVehicle.year}
                      onChange={(e) => setCurrentVehicle({ ...currentVehicle, year: Number(e.target.value) })}
                    />
                  </Field>
                  <Field label="Alimentazione" htmlFor="cv-fuel">
                    <SelectInput
                      id="cv-fuel"
                      value={currentVehicle.fuel_type}
                      onChange={(e) =>
                        setCurrentVehicle({ ...currentVehicle, fuel_type: e.target.value as FuelType })
                      }
                    >
                      <option value={FuelType.DIESEL}>Diesel</option>
                      <option value={FuelType.PETROL}>Benzina</option>
                      <option value={FuelType.LPG}>GPL</option>
                      <option value={FuelType.CNG}>Metano</option>
                    </SelectInput>
                  </Field>
                  <Field
                    label="Valore di mercato attuale (€)"
                    htmlFor="cv-value"
                    hint="Serve anche come valore di permuta: è ciò che “incassi” vendendolo."
                  >
                    <NumberInput
                      id="cv-value"
                      min={0}
                      value={currentVehicle.current_value ?? 0}
                      onChange={(e) => {
                        const val = Number(e.target.value);
                        setCurrentVehicle({ ...currentVehicle, current_value: val });
                        setOwnership({ ...ownership, trade_in_value: val });
                      }}
                    />
                  </Field>
                  <Field label="Manutenzione stimata (€/anno)" htmlFor="cv-maint">
                    <NumberInput
                      id="cv-maint"
                      min={0}
                      value={currentVehicle.maintenance_cost_per_year ?? 0}
                      onChange={(e) =>
                        setCurrentVehicle({ ...currentVehicle, maintenance_cost_per_year: Number(e.target.value) })
                      }
                    />
                  </Field>
                  <Field label="Assicurazione (€/anno)" htmlFor="cv-ins">
                    <NumberInput
                      id="cv-ins"
                      min={0}
                      value={currentVehicle.insurance_cost_per_year ?? 0}
                      onChange={(e) =>
                        setCurrentVehicle({ ...currentVehicle, insurance_cost_per_year: Number(e.target.value) })
                      }
                    />
                  </Field>
                </div>
              </section>
            )}

            {step === 2 && (
              <section aria-label="Profilo di utilizzo">
                <h3 className="text-base font-bold">Come guidi, quanto guidi</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Più chilometri fai e più il risparmio operativo dell’elettrico pesa sul conto.
                </p>

                <div className="mt-4 rounded-xl border border-border bg-background p-4">
                  <div className="flex items-baseline justify-between">
                    <label htmlFor="usage-km" className="field-label mb-0">
                      Chilometri annuali
                    </label>
                    <span className="text-xl font-black tabular-nums text-primary">
                      {fmtNum(usage.annual_km)} km
                    </span>
                  </div>
                  <div className="mt-3">
                    <RangeSlider
                      id="usage-km"
                      min={5000}
                      max={60000}
                      step={1000}
                      value={usage.annual_km}
                      onChange={(v) => setUsage({ ...usage, annual_km: v })}
                      ariaLabel="Chilometri annuali percorsi"
                    />
                  </div>
                  <div className="mt-2 flex justify-between text-[11px] font-medium text-muted-foreground tabular-nums">
                    <span>5.000 km</span>
                    <span>60.000 km</span>
                  </div>
                </div>

                <div className="rounded-xl border border-border bg-background p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="field-label mb-0">Ripartizione del profilo di guida</span>
                    <SumBadge sumDec={usageSum} label="Totale" />
                  </div>
                  <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <PercentInput
                      label="Urbano"
                      value={usage.city_percentage}
                      onChange={(v) => setUsage({ ...usage, city_percentage: v })}
                    />
                    <PercentInput
                      label="Extraurbano"
                      value={usage.extraurban_percentage}
                      onChange={(v) => setUsage({ ...usage, extraurban_percentage: v })}
                    />
                    <PercentInput
                      label="Autostrada"
                      value={usage.highway_percentage}
                      onChange={(v) => setUsage({ ...usage, highway_percentage: v })}
                    />
                  </div>
                </div>

                <Field
                  label={`Moltiplicatore inverno: ×${usage.winter_multiplier.toFixed(2)}`}
                  htmlFor="usage-winter"
                  hint="Quanto cala l’autonomia in condizioni invernali (1,00 = nessuna penalizzazione)."
                >
                  <RangeSlider
                    id="usage-winter"
                    min={1}
                    max={1.5}
                    step={0.05}
                    value={usage.winter_multiplier}
                    onChange={(v) => setUsage({ ...usage, winter_multiplier: v })}
                    ariaLabel="Moltiplicatore di penalizzazione invernale"
                  />
                </Field>
              </section>
            )}

            {step === 3 && (
              <section aria-label="Veicolo elettrico candidato">
                <h3 className="text-base font-bold">Il veicolo elettrico che valuti</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Cerca nel catalogo per importare le specifiche, oppure inseriscile a mano.
                </p>

                <div className="mt-4">
                  <EVSearchSelect onSelectVehicle={handleCatalogVehicleSelect} />
                </div>

                <div className="mt-4 border-t border-border pt-4">
                  <p className="overline mb-3">Specifiche — modificabili</p>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <Field label="Marca *" htmlFor="ev-brand">
                      <TextInput
                        id="ev-brand"
                        value={candidateVehicle.brand}
                        aria-invalid={!candidateVehicle.brand.trim()}
                        onChange={(e) => setCandidateVehicle({ ...candidateVehicle, brand: e.target.value })}
                      />
                    </Field>
                    <Field label="Modello *" htmlFor="ev-model">
                      <TextInput
                        id="ev-model"
                        value={candidateVehicle.model}
                        aria-invalid={!candidateVehicle.model.trim()}
                        onChange={(e) => setCandidateVehicle({ ...candidateVehicle, model: e.target.value })}
                      />
                    </Field>
                    <Field label="Prezzo di acquisto (€) *" htmlFor="ev-price">
                      <NumberInput
                        id="ev-price"
                        min={0}
                        value={candidateVehicle.purchase_price}
                        aria-invalid={candidateVehicle.purchase_price <= 0}
                        onChange={(e) =>
                          setCandidateVehicle({ ...candidateVehicle, purchase_price: Number(e.target.value) })
                        }
                      />
                    </Field>
                    <Field label="Batteria utile (kWh)" htmlFor="ev-battery">
                      <NumberInput
                        id="ev-battery"
                        min={1}
                        value={candidateVehicle.usable_battery_capacity ?? 0}
                        onChange={(e) =>
                          setCandidateVehicle({
                            ...candidateVehicle,
                            battery_capacity: Number(e.target.value),
                            usable_battery_capacity: Number(e.target.value),
                          })
                        }
                      />
                    </Field>
                    <Field label="Autonomia WLTP (km)" htmlFor="ev-range">
                      <NumberInput
                        id="ev-range"
                        min={0}
                        value={candidateVehicle.wltp_range ?? ''}
                        onChange={(e) =>
                          setCandidateVehicle({ ...candidateVehicle, wltp_range: Number(e.target.value) })
                        }
                      />
                    </Field>
                    <Field label="Consumo extraurbano (kWh/100km)" htmlFor="ev-consumption">
                      <NumberInput
                        id="ev-consumption"
                        min={0}
                        step={0.1}
                        value={candidateVehicle.extraurban_consumption}
                        onChange={(e) =>
                          setCandidateVehicle({
                            ...candidateVehicle,
                            extraurban_consumption: Number(e.target.value),
                          })
                        }
                      />
                    </Field>
                  </div>
                </div>
              </section>
            )}

            {step === 4 && (
              <section aria-label="Ricarica ed energia">
                <h3 className="text-base font-bold">Come e a che prezzo ricarichi</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  La quota di ricarica a casa è il principale leva sul costo chilometrico dell’elettrico.
                </p>

                <div className="mt-4 rounded-xl border border-border bg-background p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="field-label mb-0">Ripartizione delle ricariche</span>
                    <SumBadge sumDec={chargingSum} label="Totale" />
                  </div>
                  <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <PercentInput
                      label="A casa"
                      value={charging.home_charging_percentage}
                      onChange={(v) => setCharging({ ...charging, home_charging_percentage: v })}
                      hint="Wallbox / presa domestica"
                    />
                    <PercentInput
                      label="AC pubblica"
                      value={charging.public_ac_charging_percentage}
                      onChange={(v) => setCharging({ ...charging, public_ac_charging_percentage: v })}
                      hint="Colonnine lente"
                    />
                    <PercentInput
                      label="DC pubblica"
                      value={charging.public_dc_charging_percentage}
                      onChange={(v) => setCharging({ ...charging, public_dc_charging_percentage: v })}
                      hint="Ricarica rapida"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <Field label="Energia a casa (€/kWh)" htmlFor="ch-home">
                    <NumberInput
                      id="ch-home"
                      min={0}
                      step={0.01}
                      value={charging.home_energy_price}
                      aria-invalid={charging.home_energy_price <= 0}
                      onChange={(e) => setCharging({ ...charging, home_energy_price: Number(e.target.value) })}
                    />
                  </Field>
                  <Field label="Colonnina AC (€/kWh)" htmlFor="ch-ac">
                    <NumberInput
                      id="ch-ac"
                      min={0}
                      step={0.01}
                      value={charging.public_ac_energy_price}
                      onChange={(e) => setCharging({ ...charging, public_ac_energy_price: Number(e.target.value) })}
                    />
                  </Field>
                  <Field label="Colonnina DC (€/kWh)" htmlFor="ch-dc">
                    <NumberInput
                      id="ch-dc"
                      min={0}
                      step={0.01}
                      value={charging.public_dc_energy_price}
                      onChange={(e) => setCharging({ ...charging, public_dc_energy_price: Number(e.target.value) })}
                    />
                  </Field>
                  <Field
                    label={`Perdite di ricarica: ${toPercent(charging.charging_losses_percentage)}%`}
                    htmlFor="ch-losses"
                    hint="Energia persa durante la ricarica (cavi, convertitore)."
                  >
                    <RangeSlider
                      id="ch-losses"
                      min={0}
                      max={30}
                      step={1}
                      value={toPercent(charging.charging_losses_percentage)}
                      onChange={(v) => setCharging({ ...charging, charging_losses_percentage: fromPercent(v) })}
                      ariaLabel="Perdite di ricarica in percentuale"
                    />
                  </Field>
                </div>
              </section>
            )}

            {step === 5 && (
              <section aria-label="Orizzonte e finanziamento">
                <h3 className="text-base font-bold">Per quanto la tieni e come la paghi</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  L’orizzonte di possesso determina quanto tempo hai per recuperare l’investimento.
                </p>

                <div className="mt-4 rounded-xl border border-border bg-background p-4">
                  <div className="flex items-baseline justify-between">
                    <label className="field-label mb-0" htmlFor="own-horizon">
                      Orizzonte di possesso
                    </label>
                    <span className="text-xl font-black tabular-nums text-primary">
                      {ownership.horizon_years} {ownership.horizon_years === 1 ? 'anno' : 'anni'}
                    </span>
                  </div>
                  <div className="mt-3">
                    <RangeSlider
                      id="own-horizon"
                      min={1}
                      max={10}
                      value={ownership.horizon_years}
                      onChange={(v) => setOwnership({ ...ownership, horizon_years: v })}
                      ariaLabel="Anni di possesso previsti"
                    />
                  </div>
                  <div className="mt-2 flex justify-between text-[11px] font-medium text-muted-foreground tabular-nums">
                    <span>1 anno</span>
                    <span>10 anni</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <Field label="Valore di permuta del usato (€)" htmlFor="own-tradein">
                    <NumberInput
                      id="own-tradein"
                      min={0}
                      value={ownership.trade_in_value}
                      onChange={(e) => setOwnership({ ...ownership, trade_in_value: Number(e.target.value) })}
                    />
                  </Field>
                  <Field
                    label="Incentivi / eco-bonus (€)"
                    htmlFor="own-incentive"
                    hint="Contributi statali o regionali sull’acquisto."
                  >
                    <NumberInput
                      id="own-incentive"
                      min={0}
                      value={ownership.incentive_amount}
                      onChange={(e) => setOwnership({ ...ownership, incentive_amount: Number(e.target.value) })}
                    />
                  </Field>
                  <Field label="Modalità di acquisto" htmlFor="own-finance">
                    <SelectInput
                      id="own-finance"
                      value={financingType}
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
                      <option value="CASH">Acquisto diretto (contanti)</option>
                      <option value="LOAN">Prestito / finanziamento</option>
                      <option value="LEASING">Leasing con maxi-rata finale</option>
                    </SelectInput>
                  </Field>
                </div>

                {financingType !== 'CASH' && (
                  <div className="rounded-xl border border-border bg-background p-4">
                    <p className="overline mb-3">Dettagli finanziamento</p>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <Field label="Anticipo (€)" htmlFor="fin-down">
                        <NumberInput
                          id="fin-down"
                          min={0}
                          value={ownership.financing.down_payment}
                          onChange={(e) =>
                            setOwnership({
                              ...ownership,
                              financing: { ...ownership.financing, down_payment: Number(e.target.value) },
                            })
                          }
                        />
                      </Field>
                      <Field label="Durata (mesi)" htmlFor="fin-duration">
                        <NumberInput
                          id="fin-duration"
                          min={1}
                          max={120}
                          value={ownership.financing.duration_months}
                          onChange={(e) =>
                            setOwnership({
                              ...ownership,
                              financing: { ...ownership.financing, duration_months: Number(e.target.value) },
                            })
                          }
                        />
                      </Field>
                      {financingType === 'LEASING' ? (
                        <>
                          <Field label="Canone mensile (€)" htmlFor="fin-lease">
                            <NumberInput
                              id="fin-lease"
                              min={0}
                              value={ownership.financing.lease_monthly_fee ?? 0}
                              onChange={(e) =>
                                setOwnership({
                                  ...ownership,
                                  financing: { ...ownership.financing, lease_monthly_fee: Number(e.target.value) },
                                })
                              }
                            />
                          </Field>
                          <Field
                            label="Valore residuo / maxi-rata (%)"
                            htmlFor="fin-residual"
                            hint="Es. 40 = maxi-rata finale pari al 40% del prezzo."
                          >
                            <NumberInput
                              id="fin-residual"
                              min={0}
                              max={100}
                              step={1}
                              value={ownership.financing.residual_value_percentage ?? 40}
                              onChange={(e) =>
                                setOwnership({
                                  ...ownership,
                                  financing: {
                                    ...ownership.financing,
                                    residual_value_percentage: Number(e.target.value),
                                  },
                                })
                              }
                            />
                          </Field>
                        </>
                      ) : (
                        <Field
                          label="Tasso annuo (es. 0,05 = 5%)"
                          htmlFor="fin-rate"
                        >
                          <NumberInput
                            id="fin-rate"
                            min={0}
                            max={1}
                            step={0.005}
                            value={ownership.financing.interest_rate_annual}
                            onChange={(e) =>
                              setOwnership({
                                ...ownership,
                                financing: { ...ownership.financing, interest_rate_annual: Number(e.target.value) },
                              })
                            }
                          />
                        </Field>
                      )}
                    </div>
                  </div>
                )}

                <div className="rounded-xl border border-primary/20 bg-primary/5 p-4">
                  <p className="overline mb-2 text-primary">Riepilogo del confronto</p>
                  <div className="flex flex-wrap gap-2 text-xs font-semibold">
                    <span className="rounded-full border border-border bg-card px-3 py-1">
                      {currentVehicle.brand} {currentVehicle.model} → {candidateVehicle.brand} {candidateVehicle.model}
                    </span>
                    <span className="rounded-full border border-border bg-card px-3 py-1 tabular-nums">
                      {fmtNum(usage.annual_km)} km/anno
                    </span>
                    <span className="rounded-full border border-border bg-card px-3 py-1 tabular-nums">
                      {toPercent(charging.home_charging_percentage)}% ricarica a casa
                    </span>
                    <span className="rounded-full border border-border bg-card px-3 py-1 tabular-nums">
                      {ownership.horizon_years} anni
                    </span>
                    <span className="rounded-full border border-border bg-card px-3 py-1">
                      {financingType === 'CASH' ? 'Contanti' : financingType === 'LEASING' ? 'Leasing' : 'Finanziamento'}
                    </span>
                    {ownership.trade_in_value > 0 && (
                      <span className="rounded-full border border-border bg-card px-3 py-1 tabular-nums">
                        Permuta {fmtEUR(ownership.trade_in_value)}
                      </span>
                    )}
                  </div>
                </div>
              </section>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border px-5 py-4 sm:px-6">
          <button type="button" onClick={goBack} className={step > 1 ? 'btn-outline px-4' : 'btn-ghost px-4'}>
            {step > 1 ? (
              <>
                <ChevronLeft className="h-4 w-4" />
                Indietro
              </>
            ) : (
              'Annulla'
            )}
          </button>

          <div className="flex items-center gap-3">
            {stepErrors[step] && (
              <p className="hidden max-w-xs text-right text-xs font-medium text-destructive sm:block" role="alert">
                {stepErrors[step]}
              </p>
            )}
            {step < STEPS.length ? (
              <button type="button" onClick={goNext} disabled={!canProceed} className="btn-primary px-5">
                Avanti
                <ChevronRight className="h-4 w-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinish}
                disabled={isLoading}
                className="btn-success px-6 py-3"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Calcolo in corso…
                  </>
                ) : (
                  'Calcola l’analisi'
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisWizard;
