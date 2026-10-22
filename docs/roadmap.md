# EV Purchase Advisor Roadmap

Questo documento traccia l'evoluzione del progetto, con dettagli tecnici e criteri di accettazione per ogni release.

## 🚧 v0.4 - My Garage, Persistenza Analisi, Confronto Multi-Auto & Gestione Carburanti (COMPLETATO)
*Obiettivo: Trasformare eVision da strumento di analisi singola a piattaforma completa di gestione e confronto del parco auto personale.*
- [x] **My Garage (Persistenza Auto)**:
  - Backend: Modello SQLAlchemy `SavedVehicle` (`saved_vehicles`) e router `/api/v1/garage` (CRUD completo, auto predefinita).
  - Frontend: Componente `GarageManager` modale per salvare, modificare e impostare l'auto predefinita.
- [x] **Persistenza Analisi su Database**:
  - Backend: Migrazione da persistenza in-memory a PostgreSQL per le analisi (`SavedAnalysis`), salvando sia analisi singole che comparative.
  - Frontend: Vista "Storico Analisi" per ricaricare o eliminare analisi salvate.
- [x] **Confronto Multi-Auto Simultaneo (1 vs N)**:
  - Backend: Motore `run_comparative_analysis` ed endpoint `POST /api/v1/analyses/compare` per confrontare 1 auto di riferimento vs fino a 5 candidati EV contemporaneamente.
  - Frontend:
    - Componente `MultiCarSelector` per selezionare fino a 5 EV candidate nel wizard.
    - Vista `ComparativeAnalysisView` con tabella KPI side-by-side e grafico TCO cumulativo multi-linea Recharts.
- [x] **Gestione e Feed Prezzi Carburanti**:
  - Backend: Endpoint `/api/v1/prices/fuel` per il recupero dei prezzi medi regionali di benzina, diesel, GPL, metano ed elettricità dal feed MIMIT.
  - Frontend: Controlli per i prezzi dei carburanti (benzina, diesel, GPL, metano) nel wizard con pulsante di aggiornamento automatico MIMIT.

## ✅ v0.3 - Vehicle Catalog & Live Data Integration (COMPLETATO)
*Obiettivo: Ridurre l'attrito nell'inserimento dati e aumentare la precisione con dati reali.*
- [x] **Vehicle Catalog Search**: `GET /api/v1/vehicles/catalog` e combobox accessibile nel wizard. Dataset aperto **OpenEV Data** (`backend/data/open-ev-data.csv`, ~490 varianti).
- [x] **Used-Car Valuation**: `POST /api/v1/vehicles/valuation` — stima del valore di mercato e di permuta da annunci AutoScout24.it comparabili via RapidAPI "AutoScout24 Scraper".
- [x] **Live Price Feeds**: Integrazione con API MIMIT per i prezzi medi di carburante ed elettricità per regione.

## ✅ v0.2.1 - UI/UX Overhaul (COMPLETATO)
- [x] **Design system**: token tema light/dark (HSL + `<alpha-value>`), componenti riutilizzabili.
- [x] **Wizard modale accessibile**: focus-trap, Escape/backdrop, stepper cliccabile con stato.
- [x] **Accessibilità & responsive**: contrasto WCAG AA verificato in entrambi i temi.

## ✅ v0.2 - Enhanced Analytics & Saved Comparisons (COMPLETATO)
- [x] **Saved & Shareable Analyses**: Link univoci (`?id=...`).
- [x] **PDF Report Export**: Esportazione via print stylesheet.
- [x] **Advanced Financing Models (Leasing)**: Modelli di finanziamento e leasing.

## ✅ MVP (v0.1) - Initial Release (COMPLETATO)
- [x] Pure Python Calculation Engine, Recommendation Engine, FastAPI, React frontend.

## 🔄 Roadmap Modulo Garage - eVision

| ID | Feature / Task | Descrizione | Priorità | Stato |
|----|----------------|-------------|----------|-------|
| **R1** | **Fix Semantico Garage** | Corretto `TYPE_OPTIONS` per usare "Categoria Veicolo" (Auto, SUV, Furgone, Motociclo) invece di duplicare l'alimentazione. | 🔴 Alta | ✅ Completato |
| **R2** | **Validazione Consumi** | Aggiunto `min={0.1}` e validazione required sui campi di consumo per prevenire errori di divisione per zero nel motore TCO. | 🔴 Alta | ✅ Completato |
| **R3** | **UI Dinamica Consumi** | Le etichette dei consumi mostrano dinamicamente "L/100km" o "kWh/100km" in base all'alimentazione. | 🟡 Media | ✅ Completato |
| **R4** | **Campi EV nel Garage** | Aggiunti campi condizionali "Capacità batteria (kWh)" e "Autonomia WLTP (km)" nel form di inserimento. | 🟡 Media | ✅ Completato |
| **R5** | **Matrice Punteggio Ponderato** | Permettere all'utente di personalizzare i pesi (Risparmio, Autonomia, Sostenibilità) per il calcolo del "Winner Score". | 🟡 Media | 🗺️ In Backlog (v0.5) |
| **R6** | **Export PDF Comparativo** | Report PDF dedicato a più colonne per il confronto 1 vs N, con grafici sovrapposti e tabella KPI. | 🟢 Bassa | 🗺️ In Backlog (v0.5) |

## 🔜 v0.5 - AI Advisor & Reportistica Avanzata

_Periodo stimato: Q1 2027_
_Obiettivo: Trasformare i dati grezzi in narrazioni decisionali chiare e automatizzare la reportistica._

- [ ] **LLM-Assisted Comparative Summary**: Generazione di un paragrafo in linguaggio naturale che spiega *perché* l'auto X è migliore dell'auto Y per lo specifico utente (`ai_summary_placeholder` predisposto nello schema API).
- [ ] **Export PDF Comparativo**: Layout PDF ottimizzato per la stampa a due colonne con grafici Recharts esportati in SVG.
- [ ] **Alert di Soglia (Red Flags)**: Evidenziazione visiva automatica nei risultati di parametri fuori dagli intervalli di sicurezza (es. break-even > 5 anni).
- [ ] **Chat-like Q&A**: Interfaccia chat per porre domande sull'analisi generata.
