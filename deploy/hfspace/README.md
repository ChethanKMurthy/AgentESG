---
title: AgentESG Backend
emoji: 🌱
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
short_description: Multi-agent ESG / CSRD compliance backend (FastAPI + hybrid RAG).
---

# AgentESG — backend (HF Space)

This Space runs the FastAPI backend for [AgentESG](https://github.com/ChethanKMurthy/AgentESG): a multi-agent ESG/CSRD compliance platform with hybrid RAG (FAISS + BM25 + RRF), a data-driven rule engine, peer benchmarking, and an explainable roadmap generator.

The frontend lives separately on Vercel and talks to this Space over HTTPS.

## Demo limits

This Space runs in `DEMO_MODE=true` to bound Anthropic API spend:

- 5 LLM-using requests per IP per day
- 200 LLM-using requests per day across all users
- Per-call `max_tokens` clamped to 512
- Default model: Claude Haiku 4.5

When a limit is hit, the API returns HTTP 429 with a clear message. Non-LLM endpoints (companies list, rule evaluation, RAG retrieval, benchmarks) are unrestricted.

For unlimited local use, clone the repo and `docker compose up`.

## Endpoints

- `GET  /api/health` — liveness
- `GET  /api/companies` — list
- `GET  /api/companies/{id}` — detail + latest metrics
- `POST /api/rules/evaluate` — rule engine
- `POST /api/upload` — disclosure PDF ingest (LLM)
- `POST /api/copilot/chat` — Verdant copilot (LLM, streaming)
- `POST /api/analysis/full` — orchestrated 5-agent run (LLM)
- `GET  /api/docs` — OpenAPI / Swagger UI
