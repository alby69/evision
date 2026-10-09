import React, { useState, useEffect, useCallback } from 'react';
import { EVCatalogItem } from '../types/api';
import { searchEVCatalog } from '../services/api';

interface EVSearchSelectProps {
  onSelectVehicle: (item: EVCatalogItem) => void;
}

export const EVSearchSelect: React.FC<EVSearchSelectProps> = ({ onSelectVehicle }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<EVCatalogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const fetchCatalog = useCallback(async (searchTerm: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchEVCatalog({ search: searchTerm, limit: 8 });
      setResults(data);
    } catch (err) {
      console.error('Failed to search EV catalog:', err);
      setError('Impossibile caricare il catalogo EV');
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

  const handleSelect = (item: EVCatalogItem) => {
    onSelectVehicle(item);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full mb-4">
      <label className="block text-sm font-semibold mb-1 text-primary">
        🔍 Cerca nel Catalogo EV Pubblico (OpenEV / API Ninjas)
      </label>
      <div className="relative flex items-center">
        <input
          type="text"
          className="w-full p-2.5 rounded-lg border border-input bg-background pr-10 focus:ring-2 focus:ring-primary focus:outline-none"
          placeholder="Digita marca o modello (es. Tesla, Zoe, MG4, Ioniq)..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
        />
        {loading && (
          <div className="absolute right-3 text-xs text-muted-foreground animate-pulse">
            Ricerca...
          </div>
        )}
      </div>

      {isOpen && (
        <div className="absolute z-20 w-full mt-1 bg-card border border-border rounded-xl shadow-xl max-h-72 overflow-y-auto p-1">
          {error && <div className="p-3 text-sm text-destructive">{error}</div>}
          {!loading && !error && results.length === 0 && (
            <div className="p-3 text-sm text-muted-foreground text-center">
              Nessun veicolo elettrico trovato per "{query}"
            </div>
          )}
          {results.map((item, idx) => (
            <div
              key={`${item.make}-${item.model}-${idx}`}
              onClick={() => handleSelect(item)}
              className="p-3 hover:bg-muted/70 rounded-lg cursor-pointer transition-colors border-b border-border/40 last:border-none flex justify-between items-center"
            >
              <div>
                <div className="font-bold text-foreground text-sm">
                  {item.make} {item.model}
                  {item.year && <span className="text-xs font-normal text-muted-foreground ml-2">({item.year})</span>}
                </div>
                <div className="text-xs text-muted-foreground flex gap-3 mt-1">
                  {item.battery_useable_capacity && (
                    <span>Batteria: <strong>{item.battery_useable_capacity} kWh</strong></span>
                  )}
                  {item.electric_range && (
                    <span>Autonomia: <strong>{item.electric_range} km</strong></span>
                  )}
                  {item.vehicle_consumption && (
                    <span>Consumo: <strong>{item.vehicle_consumption} kWh/100km</strong></span>
                  )}
                </div>
              </div>
              <button
                type="button"
                className="text-xs font-semibold px-3 py-1.5 rounded bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground transition-all shrink-0 ml-2"
              >
                Seleziona
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
