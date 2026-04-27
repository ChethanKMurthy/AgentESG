from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env,
    }


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(db_session)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception as exc:
        return {"status": "error", "db": "down", "detail": str(exc)}
