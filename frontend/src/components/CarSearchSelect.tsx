import React, { useEffect, useMemo, useRef, useState } from 'react';
import { CarFacetMap, CarFacetValue, CarSelection } from '../types/api';
import { fetchCarFacets } from '../services/api';
import { Field, SelectInput } from './ui';
import { Car, Check, ChevronDown, Loader2, Search, X } from 'lucide-react';

interface CarSearchSelectProps {
  onSelectVehicle: (selection: CarSelection) => void;
}

interface FacetComboboxProps {
  id: string;
  label: string;
  options: CarFacetValue[];
  value: string;
  disabled?: boolean;
  loading?: boolean;
  placeholder: string;
  onSelect: (value: string) => void;
}

const FacetCombobox: React.FC<FacetComboboxProps> = ({
  id,
  label,
  options,
  value,
  disabled,
  loading,
  placeholder,
  onSelect,
}) => {
  const [query, setQuery] = useState(value);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setQuery(value);
  }, [value]);

  useEffect(() => {
    const handleMouseDown = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setQuery(value);
      }
    };
    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [value]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const effective = q === value.trim().toLowerCase() ? '' : q;
    const list = effective
      ? options.filter((option) => String(option.value).toLowerCase().includes(effective))
      : options;
    return list.slice(0, 60);
  }, [options, query, value]);

  useEffect(() => {
    setActiveIndex(-1);
  }, [filtered.length]);

  const handleSelect = (optionValue: string) => {
    onSelect(optionValue);
    setQuery(optionValue);
    setIsOpen(false);
    setActiveIndex(-1);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setIsOpen(true);
      setActiveIndex((i) => (filtered.length === 0 ? -1 : (i + 1) % filtered.length));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((i) => (filtered.length === 0 ? -1 : (i - 1 + filtered.length) % filtered.length));
    } else if (event.key === 'Enter') {
      if (isOpen && activeIndex >= 0 && filtered[activeIndex]) {
        event.preventDefault();
        handleSelect(String(filtered[activeIndex].value));
      }
    } else if (event.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <Field label={label} htmlFor={id}>
      <div ref={containerRef} className="relative">
        <input
          id={id}
          type="text"
          role="combobox"
          aria-expanded={isOpen}
          aria-autocomplete="list"
          autoComplete="off"
          disabled={disabled}
          className="field-input pr-10 disabled:cursor-not-allowed disabled:opacity-60"
          placeholder={placeholder}
          value={query}
          onFocus={(e) => {
            setIsOpen(true);
            e.target.select();
          }}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
        />
        <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center">
          {loading ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary/30 border-t-primary" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          )}
        </div>

        {isOpen && !disabled && (
          <div className="absolute z-40 mt-1 max-h-60 w-full overflow-y-auto rounded-xl border border-border bg-card p-1.5 shadow-lift">
            {filtered.length === 0 ? (
              <p className="px-3 py-4 text-center text-xs text-muted-foreground">Nessun risultato</p>
            ) : (
              <ul role="listbox" aria-label={label}>
                {filtered.map((option, idx) => {
                  const optionValue = String(option.value);
                  return (
                    <li
                      key={optionValue}
                      role="option"
                      aria-selected={activeIndex === idx}
                      tabIndex={-1}
                      onClick={() => handleSelect(optionValue)}
                      onMouseEnter={() => setActiveIndex(idx)}
                      className={`flex cursor-pointer items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                        activeIndex === idx ? 'bg-primary/10' : 'hover:bg-muted/70'
                      }`}
                    >
                      <span className="truncate font-medium text-foreground">{optionValue}</span>
                      <span className="shrink-0 text-[11px] tabular-nums text-muted-foreground">{option.count}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}
      </div>
    </Field>
  );
};

export const CarSearchSelect: React.FC<CarSearchSelectProps> = ({ onSelectVehicle }) => {
  const [makes, setMakes] = useState<CarFacetValue[]>([]);
  const [make, setMake] = useState('');
  const [models, setModels] = useState<CarFacetValue[]>([]);
  const [model, setModel] = useState('');
  const [details, setDetails] = useState<CarFacetMap>({});
  const [generation, setGeneration] = useState('');
  const [year, setYear] = useState('');
  const [fuel, setFuel] = useState('');
  const [body, setBody] = useState('');

  const [loadingMakes, setLoadingMakes] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<CarSelection | null>(null);

  useEffect(() => {
    let alive = true;
    setLoadingMakes(true);
    fetchCarFacets(['make'])
      .then((data) => {
        if (alive) setMakes(data.make ?? []);
      })
      .catch(() => {
        if (alive) setError('Impossibile caricare il catalogo auto.');
      })
      .finally(() => {
        if (alive) setLoadingMakes(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    if (!make) {
      setModels([]);
      setModel('');
      setDetails({});
      return;
    }
    let alive = true;
    setLoadingModels(true);
    setModel('');
    setDetails({});
    fetchCarFacets(['model'], { make })
      .then((data) => {
        if (alive) setModels(data.model ?? []);
      })
      .catch(() => {
        if (alive) setError('Impossibile caricare i modelli.');
      })
      .finally(() => {
        if (alive) setLoadingModels(false);
      });
    return () => {
      alive = false;
    };
  }, [make]);

  useEffect(() => {
    if (!make || !model) {
      setDetails({});
      return;
    }
    let alive = true;
    setLoadingDetails(true);
    setGeneration('');
    setYear('');
    setFuel('');
    setBody('');
    fetchCarFacets(['generation', 'year', 'fuel', 'body'], { make, model })
      .then((data) => {
        if (alive) setDetails(data);
      })
      .catch(() => {
        if (alive) setError('Impossibile caricare le versioni del modello.');
      })
      .finally(() => {
        if (alive) setLoadingDetails(false);
      });
    return () => {
      alive = false;
    };
  }, [make, model]);

  const years = useMemo(
    () =>
      (details.year ?? [])
        .map((entry) => Number(entry.value))
        .filter((value) => Number.isFinite(value))
        .sort((a, b) => b - a),
    [details.year],
  );

  const canConfirm = Boolean(make && model);

  const handleConfirm = () => {
    if (!canConfirm) return;
    const selection: CarSelection = {
      make,
      model,
      generation: generation || undefined,
      year: year ? Number(year) : undefined,
      fuel: fuel || undefined,
      body: body || undefined,
    };
    setSelected(selection);
    onSelectVehicle(selection);
  };

  const handleReset = () => {
    setSelected(null);
    setMake('');
    setModel('');
    setGeneration('');
    setYear('');
    setFuel('');
    setBody('');
  };

  return (
    <div className="rounded-xl border border-border bg-background p-4">
      <div className="flex items-center justify-between gap-2">
        <span className="field-label mb-0 inline-flex items-center gap-1.5">
          <Car className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
          Cerca la tua auto nel catalogo
        </span>
        {selected && (
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center gap-1 text-xs font-semibold text-muted-foreground transition hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
            Reimposta
          </button>
        )}
      </div>

      {selected && (
        <div className="mt-2 flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 animate-fade-in">
          <Check className="h-4 w-4 shrink-0 text-emerald-700 dark:text-emerald-400" aria-hidden="true" />
          <span className="truncate text-sm font-semibold text-foreground">
            {[
              `${selected.make} ${selected.model}`,
              selected.generation,
              selected.year,
              selected.fuel,
            ]
              .filter(Boolean)
              .join(' · ')}
          </span>
        </div>
      )}

      {error && (
        <p className="mt-2 text-xs font-medium text-destructive" role="alert">
          {error}
        </p>
      )}

      <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FacetCombobox
          id="car-make"
          label="Marca *"
          options={makes}
          value={make}
          loading={loadingMakes}
          placeholder="Es. Volkswagen, Toyota, Fiat..."
          onSelect={setMake}
        />
        <FacetCombobox
          id="car-model"
          label="Modello *"
          options={models}
          value={model}
          disabled={!make}
          loading={loadingModels}
          placeholder={make ? 'Es. Golf, Corolla, Panda...' : 'Scegli prima la marca'}
          onSelect={setModel}
        />
      </div>

      {model && (
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Generazione / versione" htmlFor="car-generation">
            <SelectInput
              id="car-generation"
              value={generation}
              disabled={loadingDetails}
              onChange={(e) => setGeneration(e.target.value)}
            >
              <option value="">{loadingDetails ? 'Caricamento…' : 'Non specificata'}</option>
              {(details.generation ?? []).map((entry) => (
                <option key={String(entry.value)} value={String(entry.value)}>
                  {String(entry.value)}
                </option>
              ))}
            </SelectInput>
          </Field>
          <Field label="Anno" htmlFor="car-year">
            <SelectInput
              id="car-year"
              value={year}
              disabled={loadingDetails}
              onChange={(e) => setYear(e.target.value)}
            >
              <option value="">{loadingDetails ? 'Caricamento…' : 'Non specificato'}</option>
              {years.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </SelectInput>
          </Field>
          <Field label="Alimentazione" htmlFor="car-fuel">
            <SelectInput
              id="car-fuel"
              value={fuel}
              disabled={loadingDetails}
              onChange={(e) => setFuel(e.target.value)}
            >
              <option value="">{loadingDetails ? 'Caricamento…' : 'Non specificata'}</option>
              {(details.fuel ?? []).map((entry) => (
                <option key={String(entry.value)} value={String(entry.value)}>
                  {String(entry.value)}
                </option>
              ))}
            </SelectInput>
          </Field>
          <Field label="Carrozzeria" htmlFor="car-body">
            <SelectInput
              id="car-body"
              value={body}
              disabled={loadingDetails}
              onChange={(e) => setBody(e.target.value)}
            >
              <option value="">{loadingDetails ? 'Caricamento…' : 'Non specificata'}</option>
              {(details.body ?? []).map((entry) => (
                <option key={String(entry.value)} value={String(entry.value)}>
                  {String(entry.value)}
                </option>
              ))}
            </SelectInput>
          </Field>
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <p className="field-hint mb-0 inline-flex items-center gap-1.5">
          <Search className="h-3 w-3" aria-hidden="true" />
          Dati API Ninjas (piano gratuito). I campi sotto restano modificabili.
        </p>
        <button type="button" onClick={handleConfirm} disabled={!canConfirm} className="btn-primary px-4">
          {loadingDetails ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
          Usa questo veicolo
        </button>
      </div>
    </div>
  );
};

export default CarSearchSelect;
