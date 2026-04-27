# esg.intel — Platform Summary

A production-style ESG/CSRD compliance platform: FastAPI backend, React/Vite frontend, hybrid RAG, data-driven rule engine, peer benchmarking, roadmap generator, multi-agent orchestrator, and end-to-end audit logging.

## What is built (by stage)

### 1. Backend foundation — `backend/app`
- `main.py` — FastAPI app, CORS, lifespan that auto-creates tables on startup, request-ID middleware, audit middleware, all routers under `/api`.
- `core/config.py` — pydantic-settings `Settings` (DB URL, Anthropic model/key, embedding model, vector store path, RAG weights/chunk sizes). All knobs env-driven.
- `db/session.py` + `db/base.py` — async SQLAlchemy engine, `SessionLocal`, declarative `Base`.
- `models/` — `Company`, `ESGMetric` (composite PK `(company_id, year)`), `AuditLog` (request_id, method, path, status_code, latency, user_id, IP, UA, event_type, JSON payload, timestamp).
- `middleware/audit.py` — wraps every non-health request: assigns `request_id`, measures latency, writes one `AuditLog` row per HTTP request.

### 2. Data layer
- `Datasets/company_master.csv` and `Datasets/esg_metrics.csv` — seeded via `backend/scripts/seed.py` into Postgres/SQLite.
- `services/company_service.py` — list/get/create/update/delete with filters (country, sector, csrd_applicable, name search).
- `api/routes/company.py` — CRUD endpoints (`/api/companies`).

### 3. RAG pipeline — `backend/app/rag`
- `loader.py` — reads `.txt/.md/.pdf/.docx`, hashes path → `doc_id`.
- `chunker.py` — sentence-aware splitter with overlap (`rag_chunk_size=800`, `rag_chunk_overlap=120`).
- `embeddings.py` — `sentence-transformers/all-MiniLM-L6-v2`, normalized, singleton, runs on CPU.
- `store.py` — FAISS `IndexFlatIP` (cosine via normalized vectors) + JSON chunk dump + pickled BM25 + meta.
- `retriever.py` — `HybridRetriever` fuses dense (FAISS) + sparse (BM25) using **Reciprocal Rank Fusion** with weighted contribution: `weight / (rrf_k + rank + 1)`. Default 0.6 dense / 0.4 sparse.
- `reranker.py` — MMR-style diversification with Jaccard overlap penalty (λ=0.7).
- `service.py` — `RAGService` singleton, async ingest under a lock, `query()` pulls a 3× pool then reranks down to `top_k`.

### 4. Rule engine — `backend/app/rule_engine`
- `types.py` — `Rule` (id, category, severity, `when` lambda, `message` lambda, citations) and `RuleResult`.
- `csrd_rules.py` — 10 data-driven rules covering CSRD applicability (EU large-undertaking, EU listed, non-EU >€150M turnover) and ESRS findings (E1 renewable share, E1 Scope-3 dominance, G1 board independence, S1 gender ratio, G1 incidents, E5 waste recycled, E3 water intensity).
- `evaluator.py` — runs every rule against `(company, metrics)`, produces `RuleResult` list and a severity-bucketed summary.

### 5. Analytics — `backend/app/analytics`
- `percentile.py` — `percentile_rank` (mid-rank) and `summary_stats` (n, min, mean, median, p25, p75, max, stdev).
- `benchmark.py` — `BenchmarkService.compare(company_id, year, peer_scope)`. Peer scopes: sector, country, sector_country, industry, industry_country. For each metric in `METRIC_DIRECTION`, returns value, peer stats, percentile rank, delta-vs-median, and status (`leader|peer|laggard`) — direction-aware (e.g. lower emissions = better).
- `scoring.py` — `compute_composite` aggregates direction-normalized percentiles into Environment / Social / Governance pillar scores (40/30/30) and a weighted composite.

### 6. Roadmap — `backend/app/roadmap`
- `gap_analysis.py` — converts triggered rules + benchmark laggards into a unified `Gap` list (severity, current, target, evidence, citations).
- `generator.py` — groups gaps by metric/category, orders by severity, picks horizon (`critical/high → 0–3m`, `medium → 3–6m`, `low → 6–12m`, `info → 12m+`), pulls actions from a category playbook and KPIs from a metric→KPIs map. Each item ships an `Explanation` with drivers, weights, methodology text, and confidence (high if both rule+benchmark drivers).
- `explainer.py` — `narrate_items` calls Claude per item to add a 2–3 sentence narrative, gated on the LLM key.

### 7. Multi-agent orchestrator — `backend/app/agents`
Five agents on a shared `AgentContext` dataclass; each subclass of `BaseAgent` runs through `run()`, which times the call, captures errors, and appends a structured `trace` entry. The `Orchestrator` runs them in fixed order:

1. **DataAgent** (`data_agent.py`)
   - Loads `Company` by `company_id`; raises `LookupError` if missing.
   - Pulls the latest `ESGMetric` row (highest year).
   - Hydrates `ctx.company`, `ctx.latest_metrics`. Output summary: name, has_metrics flag, year.

2. **RetrievalAgent** (`retrieval_agent.py`)
   - Skipped if `include_rag=False`.
   - If no user query, synthesizes a default: `"ESG compliance and CSRD applicability sector {sector} country {country}"`.
   - Calls `RAGService.query()` → hybrid RRF + MMR rerank.
   - Stores top-k as `ctx.retrieved` with index, chunk_id, source, score, text.

3. **AnalysisAgent** (`analysis_agent.py`)
   - Wraps `RuleEvaluator`. Evaluates all rules against `ctx.company` + `ctx.latest_metrics`.
   - Writes `ctx.rule_results` (full list incl. non-triggered) and `ctx.rule_summary` (counts by severity).

4. **ReportAgent** (`report_agent.py`)
   - Skipped if `include_report=False`.
   - Builds prompt from `REPORT_SYSTEM_PROMPT` + `REPORT_USER_TEMPLATE`: company JSON, metrics JSON, **only triggered** rule findings, formatted RAG context block (`[1] (source)\n…`).
   - Calls Claude (`AnthropicClient.complete`); falls back to a stub if `ANTHROPIC_API_KEY` is unset. Sets `ctx.report`.

5. **AuditAgent** (`audit_agent.py`)
   - Final stage. Persists one `AuditLog` per agent step (with timing + error) and one summary row (`event_type=analysis_full`) containing rule_summary, retrieved count, and any errors. Always commits before returning.

`Orchestrator.run` short-circuits to `AuditAgent` if `DataAgent` could not load the company, so the failed run is still auditable.

### 8. Copilot ("Verdant" / "V") — `backend/app/api/routes/copilot.py`
Three RAG-grounded endpoints, all sharing the same retrieve→prompt→audit shape:
- `POST /api/copilot/ingest` — rebuild the FAISS+BM25 index from `documents_path`.
- `GET /api/copilot/stats` — vector store meta + `ready` flag.
- `POST /api/copilot/query` — JSON answer with numeric `[n]` citations; uses `COPILOT_SYSTEM_PROMPT` (Verdant persona). Optionally attaches a `format_company_context` block when `company_id` is given.
- `POST /api/copilot/stream` — SSE stream: `meta`, `citations`, `token` deltas, `done`.
- `POST /api/copilot/brief` — strict-JSON briefing card (headline, verdict, summary, findings[], confidence). Robust JSON extraction from fenced/loose output.

### 9. Disclosure ingestion — `backend/app/api/routes/upload.py` + `ingestion/`
- `POST /api/upload/kpi` — structured KPI upsert (idempotent on `(company_id, year)`).
- `POST /api/upload/disclosure` — PDF (≤25 MB): `pypdf` extraction → `EXTRACTION_SYSTEM_PROMPT` to Claude → strict-JSON company+metrics → sanitization (type coercion, allowed-field whitelisting, fallback name from filename, fallback year = last year) → upsert by case-insensitive name. Returns extracted snapshot, `missing_metrics` list, and notes.

### 10. Frontend — `frontend/src` (React + Vite + TS + Tailwind + react-query + react-router)
- Public shell: `Home`, `About`.
- App shell with sidebar/topbar/command-palette: `Dashboard`, `Upload` (PDF disclosure), `Companies` (list + filters), `CompanyDetail` (rule findings, percentile bars, radar score, roadmap, full report), `Copilot` (chat with citations, RAG stats).
- `hooks/api.ts` wraps every backend endpoint with react-query.
- `components/charts/PercentileBar.tsx`, `RadarScore.tsx` for benchmark visualization.
- `components/copilot/VerdantWidget.tsx` for the persona-styled chat shell.

### 11. Infra
- `Dockerfile` + `Dockerfile.prod` + `gunicorn_conf.py` for backend; `Dockerfile` + `nginx.conf` for frontend.
- `docker-compose.yml` (dev) and `docker-compose.prod.yml`.
- `alembic/` migrations, `RUNBOOK.md`.

---

## End-to-end flow diagram

```
                        ┌─────────────────────────────────────────────┐
                        │                  REACT SPA                  │
                        │  Home/About | Dashboard | Upload | Companies│
                        │  CompanyDetail | Copilot (Verdant)          │
                        └──────────────┬──────────────────────────────┘
                                       │ react-query / fetch / SSE
                                       ▼
                ┌──────────────────────────────────────────────┐
                │            FastAPI  (app.main)               │
                │  CORS  →  AuditMiddleware (request_id+log)   │
                └──┬──────────┬──────────┬──────────┬──────────┘
                   │          │          │          │
        /companies │  /upload │  /rules  │ /copilot │ /analysis/{full,compare,roadmap}
                   ▼          ▼          ▼          ▼          ▼
        ┌────────────┐ ┌─────────────┐ ┌────────┐ ┌──────────────────────────────┐
        │CompanyServ.│ │  Disclosure │ │  Rule  │ │       Orchestrator           │
        │ CRUD       │ │  PDF→LLM→   │ │ /eval  │ │  (multi-agent pipeline)      │
        │            │ │  upsert     │ │        │ │                              │
        └─────┬──────┘ └──────┬──────┘ └───┬────┘ │  1. DataAgent ────┐          │
              │               │            │      │  2. RetrievalAgent│          │
              │               │            │      │  3. AnalysisAgent │          │
              │               │            │      │  4. ReportAgent   │          │
              │               │            │      │  5. AuditAgent ◄──┘          │
              ▼               ▼            ▼      └──┬─────┬─────┬─────┬─────┬───┘
        ┌──────────────────────────────────────────┐ │     │     │     │     │
        │            Postgres / SQLite             │◄┘     │     │     │     │
        │  companies | esg_metrics | audit_logs    │       │     │     │     │
        └──────────────────────────────────────────┘       │     │     │     │
                                                           │     │     │     │
                                          ┌────────────────┘     │     │     │
                                          ▼                      ▼     ▼     ▼
                                   ┌─────────────┐        ┌────────────────────┐
                                   │ RAG Service │        │  Rule Engine       │
                                   │ (singleton) │        │  CSRD_RULES (data) │
                                   │             │        │  → RuleResult      │
                                   │ ┌─────────┐ │        └─────────┬──────────┘
                                   │ │ Loader  │ │                  │
                                   │ │ Chunker │ │                  ▼
                                   │ │ Embed.  │ │         ┌─────────────────┐
                                   │ │ FAISS   │◄┼─dense──►│ BenchmarkService│
                                   │ │ BM25    │◄┼─sparse─►│  percentile +   │
                                   │ │ RRF     │ │         │  pillar scoring │
                                   │ │ MMR     │ │         └─────────┬───────┘
                                   │ └─────────┘ │                   │
                                   └──────┬──────┘                   ▼
                                          │                ┌────────────────────┐
                                          │                │  Roadmap           │
                                          │                │  gap_analysis →    │
                                          │                │  generator →       │
                                          ▼                │  explainer (LLM)   │
                                   ┌─────────────┐         └─────────┬──────────┘
                                   │  Anthropic  │◄──────────────────┘
                                   │  Claude API │   (Copilot/Report/Brief/Narrate/Extract)
                                   └─────────────┘
```

## How a single `/api/analysis/full` request flows

1. **Browser** (CompanyDetail page) → `POST /api/analysis/full {company_id, query, top_k, include_rag, include_report}`.
2. **AuditMiddleware** stamps `request_id`, starts timer.
3. **Orchestrator** instantiates `AgentContext` and runs agents in order, each appending to `ctx.trace`:
   - DataAgent loads company + latest metrics from SQL.
   - RetrievalAgent runs hybrid RAG (FAISS dense + BM25 sparse → RRF fuse → MMR rerank) → top-k chunks.
   - AnalysisAgent runs all CSRD rules over `(company, metrics)` → triggered findings + summary.
   - ReportAgent stitches a Claude prompt with company JSON + metrics JSON + triggered findings + numbered context block, returns the executive brief.
   - AuditAgent persists per-agent steps and a final `analysis_full` summary row.
4. Response payload returns the company snapshot, metrics, full rule results, citations (with snippets), the LLM report, the per-agent trace (with durations and errors), and the request_id. The middleware writes the outer HTTP request log on the way out.

## How agents stay decoupled

- Agents only mutate the `AgentContext`; they never call each other.
- Business rules live as data in `csrd_rules.py`, not in agents — adding a CSRD update is a list edit.
- RAG hides dense/sparse/rerank behind one `query()` call; weights/strategy are env-tunable.
- Audit is cross-cutting via two layers: HTTP middleware (every request) + AuditAgent (every agent step) — both share the `audit_logs` table keyed by `request_id`, so a single ID stitches the full trace together.
- LLM access is a singleton with a hard `enabled` flag; absence of `ANTHROPIC_API_KEY` cleanly degrades to deterministic stubs (Copilot returns retrieved context, Report returns a stub, Roadmap skips narratives, Disclosure upload returns 503).
