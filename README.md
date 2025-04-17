# arc

A command‑line application for aggregating financial and economic data, caching it locally, and producing quick tabular or visual outputs. This README aims to give another developer a **self‑contained view of the project**—what already works, why it was built the way it is, and exactly what’s left to do.

---
## 1  Project snapshot (Apr 2025)

| Layer | What works today | What’s still missing |
|-------|------------------|-----------------------|
| **API wrappers** | FRED and Yahoo Finance wrappers fully operational. | Stats Canada JSON wrapper and EDGAR filings fetcher are stub files. |
| **Persistence** | • SQLAlchemy + SQLite engine scaffolding (`database/core.py`).<br>• ORM models for stock metadata/prices and initial economic tables.<br>• TinyDB document store (`database/document_store.py`) used by EDGAR stub. | ORM **write‑helpers** are incomplete → caches are *read‑only*; first run will hit remote APIs. |
| **CLI** | Typer CLI with two sub‑commands: `fred` and `stock`.<br>Global `--no-cache` flag wired. | When caches are enabled, command will raise if underlying write‑helpers are unfinished. |
| **Tests / CI** | Basic unit tests for FRED and YF wrappers. | No integration tests yet; no GitHub Actions pipeline. |
| **Packaging** | Single `arc` namespace; editable install via `uv pip install -e .`; global install via `uv tool install -e`. | None. |

---
## 2  Design decisions so far

* **Namespacing** – All code lives under a single `arc` package to avoid clashes (`import arc.api …`).
* **Dual‑store strategy**  
  * Structured, numeric, versioned → **SQLite** (fast local queries, ACID, zero server).  
  * Heterogeneous JSON / text blobs → **TinyDB** (single JSON file, no schema friction).
* **SQLAlchemy ORM ≥ raw SQL** – Easier migrations if we someday promote the DB to Postgres; type‑annotated models help IDE navigation.
* **Typer** – Minimal boilerplate for a multi‑command CLI, auto‑generates `--help`, supports PowerShell completion.
* **uv (Python launcher)** – Fast dependency solves; `uv tool …` provides globally‑shimmed CLI without polluting the dev venv.

---
## 3  Open tasks (expanded)

Below is the *live* backlog excerpted from our private planning doc. Checked items are complete; unchecked items are upcoming.

### 3.1  Persistence & caching

- [ ] **Implement insert helpers** in `database/models.py`  
   - [ ] `StockMetadata` → upsert by `ticker`.  
  - [ ] `StockPrice` → bulk insert with `ON CONFLICT` handling.  
  - [ ] `EconomicSeries` + `EconomicData` → link via foreign key.
- [ ] **Wire `FredWrapper` write‑path**  
  Call insert helpers after network fetch.
- [ ] **Add `cache` param to `YFWrapper.get_data()`**  
  If `cache=True`, attempt DB read before calling yfinance; write results back afterward.

### 3.2  API coverage

- [ ] **Stats Canada wrapper**  
  - Map dataset discovery endpoint.  
  - Parse CSV/JSON into pandas DataFrame.  
  - Respect cache flag.
- [ ] **EDGAR wrapper**  
  - Already fetches submissions JSON → next step is caching filings list to TinyDB.  
  - Long‑term: parse 10‑K sections into the relational DB.

### 3.3  Automation / scheduler

- [ ] Introduce **APScheduler** job runner (`arc/schedule.py`).
- [ ] Nightly task reads `conf/watchlist.yml` and refreshes:  
  - tickers prices (daily interval)  
  - macro series (monthly releases)
- [ ] CLI command `arc schedule run` to launch the scheduler loop.

### 3.4  Visualization layer

- [ ] Finish `visualization/basic_chart.py`  
  - [ ] Candlestick plot for OHLCV.  
  - [ ] Line plot for economic time‑series.  
  Return `matplotlib.Figure` so CLI can display or save.

### 3.5  Testing & CI

- [ ] **Integration test** spins up temporary SQLite DB, runs `arc fred CPIAUCSL`, asserts rows added.
- [ ] **GitHub Actions** workflow installs deps and runs pytest matrix (Linux, Windows).

---
## 4  Usage quick‑start

```powershell
# 1  Create / activate venv
uv venv .venv;  . .venv/Scripts/Activate.ps1

# 2  Install in editable mode (adds arc package + CLI)
uv pip install -e .

# 3  Pull headline CPI series (cached)
arc fred CPIAUCSL

# 4  Force bypass caches (API hit)
arc --no-cache fred CPIAUCSL

# 5  Grab weekly prices for AAPL and MSFT
arc stock AAPL MSFT -p 1y -i 1wk -o chart
```

Environment variables expected: `FRED_API_KEY`, `STATS_CANADA_API_KEY`, `EDGAR_API_KEY`. Load them via `.env` or export in the shell.

---
## 5  Roadmap (summary)

1. **Finish relational write‑path**  → project becomes usable offline after first run.  
2. **Add Stats Canada & EDGAR ingestion**  → broadens dataset breadth.  
3. **Nightly scheduler + Streamlit prototype**  → automated refresh and basic dashboard.  
4. **CI + docs polish**  → stabilize for sharing or open‑sourcing.

*(A more granular checklist lives outside the repository for now and is mirrored here under §3 Open tasks.)*

---
## 6  License

Undecided; will likely adopt MIT once core functionality stabilises.

