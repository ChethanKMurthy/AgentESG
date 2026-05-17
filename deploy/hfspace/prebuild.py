"""Run at image-build time so the first HTTP request doesn't pay model-download
and FAISS-build cost. Also seeds SQLite from the bundled CSVs.

Expects to be invoked with CWD=/app/backend.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import sys
from pathlib import Path


def _stage_documents() -> None:
    src = Path("/app/Datasets")
    dst = Path(os.environ["DOCUMENTS_PATH"])
    dst.mkdir(parents=True, exist_ok=True)

    for sub in ("Case studies", "Guidelines"):
        sub_src = src / sub
        if not sub_src.exists():
            continue
        for pdf in sub_src.glob("*.pdf"):
            target = dst / pdf.name
            if not target.exists():
                shutil.copy2(pdf, target)


def _stage_seed_csvs() -> None:
    src = Path("/app/Datasets")
    dst = Path("/app/data/seed")
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("company_master.csv", "esg_metrics.csv"):
        s = src / name
        d = dst / name
        if s.exists() and not d.exists():
            shutil.copy2(s, d)


async def _build_faiss() -> None:
    from app.rag.service import get_rag_service

    rag = get_rag_service()
    result = await rag.ingest()
    print(f"[prebuild] rag ingest: {result}", flush=True)


async def _seed_db() -> None:
    from scripts.seed import seed

    result = await seed(
        companies_csv="/app/data/seed/company_master.csv",
        metrics_csv="/app/data/seed/esg_metrics.csv",
        replace=True,
    )
    print(f"[prebuild] db seed: {result}", flush=True)


def main() -> None:
    _stage_documents()
    _stage_seed_csvs()
    asyncio.run(_build_faiss())
    asyncio.run(_seed_db())
    print("[prebuild] done", flush=True)


if __name__ == "__main__":
    sys.path.insert(0, "/app/backend")
    main()
