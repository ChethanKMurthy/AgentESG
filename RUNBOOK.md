# RUNBOOK

Quick operational reference for the esg.intel stack. Everything is run from the
repo root: `/Users/chethan356/projects/Capstone`.

---

## 0. Prerequisites on the host

- Docker Desktop running (or any Docker engine).
- `cloudflared` installed (only needed for the public tunnel).
  `brew install cloudflared`.

The local compose stack is three services on one network:

| Service | Container | Port | Purpose |
|---|---|---|---|
| `frontend` | `esg_frontend` | **5173** → 80 | React SPA + nginx reverse proxy to `/api` |
| `backend`  | `esg_backend`  | 8000        | FastAPI + agents + RAG + rule engine |
| `postgres` | `esg_postgres` | 5432        | Postgres 16 (companies, metrics, audit) |

Named Docker volumes hold persistent state:

| Volume | Holds |
|---|---|
| `postgres_data` | All DB rows (companies, esg_metrics, audit_logs) |
| `backend_data`  | `/app/data/hf_cache` (embedding model), `/app/data/faiss` (vector store), `/app/data/documents` (indexed regulatory corpus), `/app/data/seed` (CSVs) |

Nothing is stored on the host filesystem.

---

## 1. Start the stack

```bash
# Start Docker Desktop first if it's not running:
open -a Docker

# Bring containers back up (idempotent; recreates anything missing)
docker compose up -d

# Or, if you just stopped them and want a faster no-recreate restart:
docker compose start

# Verify
docker ps
curl -sS http://127.0.0.1:5173/api/health
```

Expected output of `docker ps`:

```
esg_frontend   Up ... seconds
esg_backend    Up ... seconds (healthy)
esg_postgres   Up ... seconds (healthy)
```

Open **http://localhost:5173** — home page should load.

First boot after a clean-slate may take up to ~90s while the backend downloads
the `sentence-transformers/all-MiniLM-L6-v2` model into the `backend_data`
volume. Subsequent boots start in under 10s because the model is cached.

---

## 2. Share it publicly (Cloudflare tunnel)

**Warning** — the tunnel is unauthenticated. Anyone with the URL can:

- Trigger Claude API calls that bill your Anthropic key.
- Upload PDFs and write to the DB.

Only share with people you trust.

```bash
cloudflared tunnel --url http://127.0.0.1:5173 --no-autoupdate
```

Copy the `https://<something>.trycloudflare.com` URL it prints. The URL
**changes every time** — if you need a stable hostname, log into Cloudflare
with `cloudflared tunnel login` and bind the tunnel to a domain you own.

Stop the tunnel: `Ctrl+C` in that terminal, or from any other terminal:

```bash
pkill -f "cloudflared tunnel"
```

---

## 3. Stop the stack

```bash
# Stops containers, keeps volumes AND images (recommended for a pause)
docker compose stop

# Fully removes containers (images + volumes kept)
docker compose down

# ⚠️ Destroys all DB rows and the FAISS / HF caches
docker compose down -v
```

After `stop` or `down`, you can quit Docker Desktop. Data is intact.

---

## 4. Daily operations

### Logs

```bash
docker logs esg_backend --tail 100 -f
docker logs esg_frontend --tail 50
docker logs esg_postgres --tail 50
```

### Shell into a container

```bash
docker exec -it esg_backend bash
docker exec -it esg_postgres psql -U esg -d esg
```

### Re-seed from the CSV datasets (clears and reloads companies + metrics)

```bash
docker exec esg_backend python scripts/seed.py
```

### Re-index the regulatory corpus (after adding new docs to the volume)

```bash
# Copy new docs in
docker exec -u 0 esg_backend mkdir -p /app/data/documents
docker cp path/to/new-reg-docs/. esg_backend:/app/data/documents/
docker exec -u 0 esg_backend chown -R app:app /app/data/documents

# Trigger ingestion
curl -sS -X POST http://127.0.0.1:5173/api/copilot/ingest \
  -H "Content-Type: application/json" -d '{}'
```

### Upload a disclosure PDF via the API (bypass the UI)

```bash
curl -sS -X POST http://127.0.0.1:5173/api/upload/disclosure \
  -F "file=@Datasets/KPIs/dumbledore_industries_fy2024.pdf"
```

Response includes the new `company_id`; visit
`http://localhost:5173/companies/<id>` for the dashboard.

### Regenerate the synthetic Harry-Potter KPI PDFs

```bash
python3 Datasets/KPIs/generate.py
```

(Needs `reportlab`: `pip3 install reportlab`.)

---

## 5. Configuration

### Changing the Anthropic key

Edit `.env` at repo root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Then restart just the backend:

```bash
docker compose up -d backend      # picks up new env on recreate
```

### Switching models

Same `.env`:

```
ANTHROPIC_MODEL=claude-opus-4-7
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Changing `EMBEDDING_MODEL` requires re-ingesting the corpus (step above) — the
FAISS index is tied to the model's dimensionality.

### CORS / public origin

```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your.domain
```

Restart backend after changes.

---

## 6. Common endpoints

| Method | Path | Use |
|---|---|---|
| GET  | `/api/health` | Liveness |
| GET  | `/api/health/db` | DB liveness |
| GET  | `/api/companies?limit=50` | List companies |
| GET  | `/api/companies/{id}` | One company |
| POST | `/api/upload/disclosure` | Upload a PDF (multipart) |
| POST | `/api/upload/kpi` | Structured JSON upload |
| POST | `/api/rules/evaluate` | Run rules on an ad-hoc payload |
| POST | `/api/analysis/full` | Full multi-agent analysis |
| POST | `/api/analysis/compare` | Peer benchmark (sector / industry / country) |
| POST | `/api/analysis/roadmap` | XAI roadmap with narratives |
| POST | `/api/copilot/query` | Verdant — chat (blocking) |
| POST | `/api/copilot/stream` | Verdant — SSE token stream |
| POST | `/api/copilot/brief` | Verdant — structured briefing JSON |
| GET  | `/api/copilot/stats` | RAG index state |
| POST | `/api/copilot/ingest` | Re-index regulatory corpus |

OpenAPI schema at `http://127.0.0.1:5173/api/docs` (served by FastAPI when you
hit `/api/openapi.json`; Swagger UI is at `/docs` on the backend port 8000 if
you expose it directly).

---

## 7. Troubleshooting

### Frontend shows old routes / stale build

Frontend image is baked at build time. After code changes:

```bash
docker compose up -d --build frontend
```

### Backend has old code

Same reason:

```bash
docker compose up -d --build backend
```

If `__pycache__` ever misbehaves inside the container:

```bash
docker exec -u 0 esg_backend find /app -name __pycache__ -type d -exec rm -rf {} +
docker compose restart backend
```

### `/api/copilot/*` returns 404

Something other than the Docker container is bound to `:5173` (e.g., a stray
local `uvicorn` or `vite dev`). Check and kill:

```bash
lsof -iTCP:5173 -sTCP:LISTEN -n -P
lsof -iTCP:8000 -sTCP:LISTEN -n -P
```

### Disclosure upload returns 503 "LLM disabled"

The backend has no `ANTHROPIC_API_KEY`. Set it in `.env` and run
`docker compose up -d backend`.

### Disclosure upload returns 422 "Could not extract enough text"

PDF is a scanned image — the extractor needs selectable text. OCR the PDF
first (e.g., `ocrmypdf in.pdf out.pdf`) and retry.

### Cloudflare tunnel URL doesn't load

- Confirm the local stack is healthy: `curl -sS http://127.0.0.1:5173/api/health`.
- Tunnels take ~10s to reach the global edge after the process starts.
- If the tunnel process died, start it again — URL will be different.

### Postgres complains the DB is empty after `down -v`

That's expected — `-v` wipes the volumes. Re-seed:

```bash
docker exec -u 0 esg_backend mkdir -p /app/data/seed
docker cp Datasets/company_master.csv esg_backend:/app/data/seed/
docker cp Datasets/esg_metrics.csv   esg_backend:/app/data/seed/
docker exec -u 0 esg_backend chown -R app:app /app/data/seed
docker exec esg_backend python scripts/seed.py
```

---

## 8. "Presentation day" fast path

Shortest possible checklist before demo:

```bash
# 1. Docker Desktop up
open -a Docker
# wait until whale icon steady

# 2. Bring stack back
cd /Users/chethan356/projects/Capstone
docker compose start

# 3. Sanity
curl -sS http://127.0.0.1:5173/api/health
docker ps

# 4. Public URL (new each time)
cloudflared tunnel --url http://127.0.0.1:5173 --no-autoupdate
#   → copy the https://*.trycloudflare.com URL to a safe clipboard

# 5. (Optional) Warm caches — hit the home page and upload one PDF so
#    the embedding model + FAISS index are hot before you start talking.
curl -sS http://127.0.0.1:5173/ > /dev/null
curl -sS http://127.0.0.1:5173/api/copilot/stats
```

Then open the tunnel URL in the browser, pop the Verdant widget, and go.

After the demo:

```bash
pkill -f "cloudflared tunnel"
docker compose stop
# optionally: quit Docker Desktop
```
