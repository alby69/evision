# EV Purchase Advisor Roadmap

Questo documento traccia l'evoluzione del progetto, con dettagli tecnici e criteri di accettazione per ogni release.

## ✅ MVP (v0.1) - Initial Release (COMPLETATO)
- [x] Pure Python Calculation Engine (TCO, break-even, real-world range, battery degradation).
- [x] Recommendation Engine with Decision Ratings, Risk Scores (0-100), and Explanation text.
- [x] FastAPI REST API with interactive Swagger documentation.
- [x] PostgreSQL persistence with SQLAlchemy 2 and Alembic.
- [x] Demo data seeds (Honda CR-V, Dacia Duster, Renault Zoe, MG4, Smart EQ).
- [x] Guided 5-step React frontend wizard with Recharts visualizations.
- [x] Docker & Docker Compose setup.

## ✅ v0.2 - Enhanced Analytics & Saved Comparisons (COMPLETATO)
*Obiettivo: Permettere agli utenti di salvare, condividere e esportare le proprie analisi, introducendo modelli di finanziamento reali.*
- [x] **Saved & Shareable Analyses**:
  - *Backend*: `POST /api/v1/analyses` restituisce un `id` (`analysis-XXXXXXXX`); `GET /api/v1/analyses/{id}` recupera l'analisi (persistenza in-memory).
  - *Frontend*: Pulsante "Condividi" che copia l'URL univoco (`?id=...`) nella clipboard, con fallback manuale e feedback visivo.
- [x] **PDF Report Export**:
  - *Frontend*: Esportazione via print stylesheet dedicato (`@media print` in `index.css`): solo contenuto dell'analisi, colori ottimizzati per stampa A4, grafici inclusi.
- [x] **Advanced Financing Models (Leasing)**:
  - *Backend*: `FinancingInput` esteso con `financing_type` (`CASH` | `LOAN` | `FINANCING` | `LEASING`), `residual_value_percentage`, `lease_monthly_fee`, `balloon_payment`; motore TCO con cash flow del leasing.
  - *Frontend*: Toggle nel wizard tra acquisto/finanziamento e leasing/noleggio con campi dinamici.

## ✅ v0.2.1 - UI/UX Overhaul (COMPLETATO)
*Obiettivo: Trasformare l'interfaccia da prototipo funzionale a prodotto curato, accessibile e coerente.*
- [x] **Design system**: token tema light/dark (HSL + `<alpha-value>`), componenti riutilizzabili (`ui.tsx`: Card, StatCard, Chip, Field, RangeSlider, ThemeToggle), ombre/animazioni, focus-visible, reduced-motion.
- [x] **Pipeline CSS critica**: aggiunto `frontend/postcss.config.js` (Tailwind + Autoprefixer non venivano mai applicati senza di esso).
- [x] **Tema dark**: toggle con persistenza (`localStorage`) e script anti-flash in `index.html`.
- [x] **Wizard modale accessibile**: focus-trap, Escape/backdrop, stepper cliccabile con stato, validazione per passo, percentuali 0-100 con controllo somma = 100%, auto-scroll, label/ARIA corretti.
- [x] **Risultati arricchiti**: hero con verdetto + confidenza, KPI con barre, sezione Scenari + Sensibilità (prima non mostrata), 4 grafici ridisegnati (tooltip, asse € compatte, donut con totale, nuovo grafico degrado batteria), tabella trasparenza con legenda fonti, footer disclaimer.
- [x] **Accessibilità & responsive**: contrasto WCAG AA verificato in entrambi i temi (0 failure), navigazione da tastiera, ARIA live, skip-link, target touch ≥ 40 px, nessun overflow orizzontale 360→1920 px.

## 🚧 v0.3 - Vehicle Catalog & Live Data Integration (IN SVILUPPO)
*Obiettivo: Ridurre l'attrito nell'inserimento dati e aumentare la precisione con dati reali.*
- [x] **Vehicle Catalog Search**: `GET /api/v1/vehicles/catalog` (proxy su API Ninjas, parametri `make`/`model`/`search`/`min_year`/`max_year`/`limit`) con combobox accessibile nel wizard e fallback ai dati demo senza API key. Chiave configurabile via `EV_CATALOG_API_KEY`.
- [ ] **Vehicle Catalog Import**: Script di seeding avanzato per importare dataset pubblici di veicoli EV (es. formato CSV/JSON con specifiche tecniche standardizzate) direttamente in locale.
- [ ] **Live Price Feeds**: Integrazione con API pubbliche o feed RSS per i prezzi medi di carburante ed elettricità per regione/nazione.
- [ ] **Listing Auto-Parser**: Endpoint backend (`POST /api/v1/parse-listing`) che accetta un URL (es. AutoScout24, Subito) ed estrae tramite scraping strutturato (o API se disponibile) marca, modello, prezzo, km e anno, popolando automaticamente il wizard.

## 🔜 v0.4 - AI Advisor Integration
*Obiettivo: Trasformare i dati numerici in consigli narrativi personalizzati.*
- [ ] **LLM-Assisted Explanation**: Integrazione con un provider LLM (es. OpenAI, Anthropic, o modelli locali via Ollama) per generare una spiegazione in linguaggio naturale ("Perché ha senso", "A cosa fare attenzione") basata sull'output strutturato JSON del motore di calcolo.
- [ ] **Chat-like Q&A**: Interfaccia chat opzionale per porre domande specifiche sull'analisi generata (es. "Cosa succede se aumento i km annui del 20%?").

## 🛡️ Cross-Cutting Concerns (Tutte le versioni)
- [ ] Coverage dei test pytest > 85% per il motore di dominio.
- [ ] Validazione strict dei tipi Pydantic v2.
- [x] Accessibilità (a11y) e responsive design nel frontend (audit WCAG/contrast/touch/layout superato, vedere v0.2.1).
- [ ] ESLint configurato e script `npm run lint` funzionante.
- [ ] Code splitting del bundle frontend (> 500 kB gzip 177 kB, candidato: Recharts via dynamic import).
