# EV Purchase Advisor Roadmap

Questo documento traccia l'evoluzione del progetto, con dettagli tecnici e criteri di accettazione per ogni release.

## ✅ MVP (v0.1) - Initial Release (COMPLETATO)
- [x] Pure Python Calculation Engine (TCO, break-even, real-world range, battery degradation).
- [x] Recommendation Engine with Decision Ratings, Risk Scores (0-100), and Explanation text.
- [x] FastAPI REST API with interactive Swagger documentation.
- [x] PostgreSQL persistence with SQLAlchemy 2 and Alembic.
- [x] Demo data seeds (Honda CR-V, Dacia Duster, Renault Zoe, MG4, Smart EQ).
- [x] Guided 7-step React frontend wizard with Recharts visualizations.
- [x] Docker & Docker Compose setup.

## 🚧 v0.2 - Enhanced Analytics & Saved Comparisons (IN SVILUPPO)
*Obiettivo: Permettere agli utenti di salvare, condividere e esportare le proprie analisi, introducendo modelli di finanziamento reali.*
- [ ] **Saved & Shareable Analyses**:
  - *Backend*: Nuovo modello `SavedAnalysis` con `share_token` (UUID). Endpoint `POST /api/v1/analyses` e `GET /api/v1/analyses/{token}`.
  - *Frontend*: Pulsante "Condividi" che copia l'URL univoco nella clipboard.
- [ ] **PDF Report Export**:
  - *Frontend*: Integrazione di esportazione PDF per il riepilogo dell'analisi (grafici inclusi) in un formato A4 pulito.
- [ ] **Advanced Financing Models (Leasing)**:
  - *Backend*: Estensione di `FinancingInput` per supportare `financing_type` (`CASH` | `LOAN` | `FINANCING` | `LEASING`). Aggiunta di `residual_value_percentage`, `lease_monthly_fee`, e `balloon_payment`. Aggiornamento del motore TCO per calcolare il cash flow del leasing.
  - *Frontend*: Toggle nel wizard per scegliere tra "Acquisto/Finanziamento" e "Leasing/Noleggio", con campi dinamici.

## 🔜 v0.3 - Vehicle Catalog & Live Data Integration
*Obiettivo: Ridurre l'attrito nell'inserimento dati e aumentare la precisione con dati reali.*
- [ ] **Vehicle Catalog Import**: Script di seeding avanzato o endpoint per importare dataset pubblici di veicoli EV (es. formato CSV/JSON con specifiche tecniche standardizzate).
- [ ] **Live Price Feeds**: Integrazione con API pubbliche o feed RSS per i prezzi medi di carburante ed elettricità per regione/nazione.
- [ ] **Listing Auto-Parser**: Endpoint backend (`POST /api/v1/parse-listing`) che accetta un URL (es. AutoScout24, Subito) ed estrae tramite scraping strutturato (o API se disponibile) marca, modello, prezzo, km e anno, popolando automaticamente il wizard.

## 🤖 v0.4 - AI Advisor Integration
*Obiettivo: Trasformare i dati numerici in consigli narrativi personalizzati.*
- [ ] **LLM-Assisted Explanation**: Integrazione con un provider LLM (es. OpenAI, Anthropic, o modelli locali via Ollama) per generare una spiegazione in linguaggio naturale ("Perché ha senso", "A cosa fare attenzione") basata sull'output strutturato JSON del motore di calcolo.
- [ ] **Chat-like Q&A**: Interfaccia chat opzionale per porre domande specifiche sull'analisi generata (es. "Cosa succede se aumento i km annui del 20%?").

## 🛡️ Cross-Cutting Concerns (Tutte le versioni)
- [ ] Coverage dei test pytest > 85% per il motore di dominio.
- [ ] Validazione strict dei tipi Pydantic v2.
- [ ] Accessibilità (a11y) e responsive design nel frontend.
