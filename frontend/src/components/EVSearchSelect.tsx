import React, { useState, useEffect, useCallback, useRef } from 'react';
import { EVCatalogItem } from '../types/api';
import { searchEVCatalog } from '../services/api';
import { Search, Check, X, ChevronDown, BatteryCharging, Gauge, Zap } from 'lucide-react';

interface EVSearchSelectProps {
  onSelectVehicle: (item: EVCatalogItem) => void;
}

export const EVSearchSelect: React.FC<EVSearchSelectProps> = ({ onSelectVehicle }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<EVCatalogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [selected, setSelected] = useState<EVCatalogItem | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const listboxId = 'ev-catalog-listbox';

  const fetchCatalog = useCallback(async (searchTerm: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchEVCatalog({ search: searchTerm, limit: 8 });
      setResults(data);
    } catch (err) {
      console.error('Failed to search EV catalog:', err);
      setError('Impossibile caricare il catalogo EV. Riprova tra istante.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCatalog(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, fetchCatalog]);

  useEffect(() => {
    setActiveIndex(-1);
  }, [results]);

  useEffect(() => {
    const handleMouseDown = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleMouseDown);
    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  const handleSelect = (item: EVCatalogItem) => {
    onSelectVehicle(item);
    setSelected(item);
    setIsOpen(false);
    setActiveIndex(-1);
  };

  const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setIsOpen(true);
      setActiveIndex((i) => (results.length === 0 ? -1 : (i + 1) % results.length));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((i) => (results.length === 0 ? -1 : (i - 1 + results.length) % results.length));
    } else if (event.key === 'Enter') {
      if (isOpen && activeIndex >= 0 && results[activeIndex]) {
        event.preventDefault();
        handleSelect(results[activeIndex]);
      }
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full"
      onKeyDown={(event) => {
        if (event.key === 'Escape' && isOpen) {
          event.stopPropagation();
          event.preventDefault();
          setIsOpen(false);
        }
      }}
    >
      <label className="field-label" htmlFor="ev-catalog-search">
        <Search className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
        Cerca nel catalogo EV pubblico
      </label>

      {selected && (
        <div className="mb-2 flex items-center justify-between gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 animate-fade-in">
          <div className="flex min-w-0 items-center gap-2 text-sm">
            <Check className="h-4 w-4 shrink-0 text-emerald-700 dark:text-emerald-400" aria-hidden="true" />
            <span className="truncate font-semibold text-foreground">
              {selected.make} {selected.model}
            </span>
            <span className="hidden shrink-0 text-xs text-muted-foreground sm:inline">
              {[
                selected.battery_useable_capacity ? `${selected.battery_useable_capacity} kWh` : null,
                selected.electric_range ? `${selected.electric_range} km WLTP` : null,
                selected.estimated_price_eur ? `~ ${selected.estimated_price_eur.toLocaleString('it-IT')} €` : null,
              ]
                .filter(Boolean)
                .join(' · ')}
            </span>
          </div>
          <button
            type="button"
            onClick={() => setSelected(null)}
            className="shrink-0 rounded-md p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
            aria-label="Rimuovi veicolo selezionato"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      <div className="relative">
        <input
          id="ev-catalog-search"
          type="text"
          role="combobox"
          aria-expanded={isOpen}
          aria-controls={listboxId}
          aria-autocomplete="list"
          aria-activedescendant={activeIndex >= 0 ? `ev-option-${activeIndex}` : undefined}
          autoComplete="off"
          className="field-input pr-10"
          placeholder="Digita marca o modello (es. Tesla, Zoe, MG4, Ioniq)..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleInputKeyDown}
        />
        <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center">
          {loading ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary/30 border-t-primary" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          )}
        </div>
      </div>

      {isOpen && (
        <div className="absolute z-30 mt-2 w-full animate-scale-in overflow-hidden rounded-xl border border-border bg-card shadow-lift">
          {error && (
            <div className="px-4 py-3 text-sm font-medium text-destructive" role="alert">
              {error}
            </div>
          )}

          {!loading && !error && results.length === 0 && (
            <div className="flex flex-col items-center gap-1 px-4 py-6 text-center">
              <Search className="h-5 w-5 text-muted-foreground/60" aria-hidden="true" />
              <p className="text-sm font-medium text-foreground">Nessun risultato</p>
              <p className="text-xs text-muted-foreground">
                Nessun veicolo elettrico trovato per “{query}”.
              </p>
            </div>
          )}

          {loading && results.length === 0 && (
            <div className="space-y-2 p-2" aria-hidden="true">
              {[0, 1, 2].map((i) => (
                <div key={i} className="skeleton h-14 rounded-lg" />
              ))}
            </div>
          )}

          {!loading && !error && results.length > 0 && (
            <ul id={listboxId} role="listbox" aria-label="Risultati catalogo EV" className="max-h-72 overflow-y-auto p-1.5">
              {results.map((item, idx) => (
                <li
                  key={`${item.make}-${item.model}-${idx}`}
                  id={`ev-option-${idx}`}
                  role="option"
                  aria-selected={activeIndex === idx}
                  tabIndex={-1}
                  onClick={() => handleSelect(item)}
                  onMouseEnter={() => setActiveIndex(idx)}
                  className={`flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-transparent px-3 py-2.5 transition-colors ${
                    activeIndex === idx ? 'border-primary/25 bg-primary/10' : 'hover:bg-muted/70'
                  }`}
                >
                  <div className="min-w-0">
                    <div className="truncate text-sm font-bold text-foreground">
                      {item.make} {item.model}
                      {item.year && (
                        <span className="ml-1.5 text-xs font-normal text-muted-foreground">
                          ({item.year})
                        </span>
                      )}
                    </div>
                    <div className="mt-1 flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-muted-foreground">
                      {item.battery_useable_capacity && (
                        <span className="inline-flex items-center gap-1">
                          <BatteryCharging className="h-3 w-3" aria-hidden="true" />
                          {item.battery_useable_capacity} kWh
                        </span>
                      )}
                      {item.electric_range && (
                        <span className="inline-flex items-center gap-1">
                          <Gauge className="h-3 w-3" aria-hidden="true" />
                          {item.electric_range} km
                        </span>
                      )}
                      {item.vehicle_consumption && (
                        <span className="inline-flex items-center gap-1">
                          <Zap className="h-3 w-3" aria-hidden="true" />
                          {item.vehicle_consumption} kWh/100km
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="shrink-0 rounded-md bg-primary/10 px-2.5 py-1 text-[11px] font-bold text-primary transition group-hover:bg-primary group-hover:text-primary-foreground">
                    Seleziona
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <p className="field-hint">
        Dati da catalogo pubblico (OpenEV / API Ninjas). I campi sotto si aggiornano automaticamente e restano modificabili.
      </p>
    </div>
  );
};

export default EVSearchSelect;
