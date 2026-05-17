# HF Spaces Docker SDK image for AgentESG backend.
# Build context: the root of the Space repo (which mirrors the AgentESG repo).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_ENV=production \
    DEMO_MODE=true \
    DATABASE_URL=sqlite+aiosqlite:////app/data/app.db \
    DOCUMENTS_PATH=/app/data/documents \
    VECTOR_STORE_PATH=/app/data/faiss \
    HF_HOME=/app/data/hf_cache \
    HF_HUB_CACHE=/app/data/hf_cache \
    TRANSFORMERS_CACHE=/app/data/hf_cache \
    SENTENCE_TRANSFORMERS_HOME=/app/data/hf_cache \
    TOKENIZERS_PARALLELISM=false \
    PORT=7860

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

COPY backend /app/backend
COPY Datasets /app/Datasets
COPY deploy/hfspace/prebuild.py /app/prebuild.py

# HF Spaces enforces UID 1000 — make the writable areas owned by that user.
RUN useradd -m -u 1000 -s /bin/bash user \
 && mkdir -p /app/data/hf_cache /app/data/faiss /app/data/documents /app/data/seed \
 && chown -R user:user /app

USER user
WORKDIR /app/backend

# Pre-download the embedding model + pre-build FAISS + seed SQLite during build.
# Failure here is fatal — better to surface it at build time than first request.
RUN cd /app/backend && python /app/prebuild.py

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS http://localhost:7860/api/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
