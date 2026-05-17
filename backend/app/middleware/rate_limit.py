from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.audit import LlmQuota

logger = get_logger(__name__)

_LLM_PREFIXES: Tuple[str, ...] = (
    "/api/upload",
    "/api/copilot",
    "/api/analysis",
)


def _is_llm_route(path: str) -> bool:
    return any(path.startswith(p) for p in _LLM_PREFIXES)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _increment(scope: str, key: str, day: str, cap: int) -> Tuple[int, bool]:
    """Atomic-enough check + increment. Returns (count_after, allowed)."""
    async with SessionLocal() as session:
        row: Optional[LlmQuota] = (
            await session.execute(
                select(LlmQuota).where(
                    LlmQuota.scope == scope,
                    LlmQuota.key == key,
                    LlmQuota.day == day,
                )
            )
        ).scalar_one_or_none()

        if row is None:
            session.add(LlmQuota(scope=scope, key=key, day=day, count=1))
            await session.commit()
            return 1, True

        if row.count >= cap:
            return row.count, False

        row.count = row.count + 1
        await session.commit()
        return row.count, True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP and global daily cap on LLM-routed endpoints when DEMO_MODE=true."""

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        if not settings.demo_mode or not _is_llm_route(request.url.path):
            return await call_next(request)

        today = date.today().isoformat()
        ip = _client_ip(request)

        try:
            ip_count, ip_ok = await _increment(
                scope="ip",
                key=ip,
                day=today,
                cap=settings.demo_daily_llm_calls_per_ip,
            )
            if not ip_ok:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Demo quota reached for your IP today. "
                        "Clone the repo and run locally for unlimited use: "
                        "https://github.com/ChethanKMurthy/AgentESG",
                        "scope": "per_ip",
                        "limit": settings.demo_daily_llm_calls_per_ip,
                        "used": ip_count,
                    },
                )

            global_count, global_ok = await _increment(
                scope="global",
                key="all",
                day=today,
                cap=settings.demo_total_daily_llm_calls,
            )
            if not global_ok:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Demo's global daily LLM quota reached. "
                        "Try again tomorrow, or clone the repo to run locally.",
                        "scope": "global",
                        "limit": settings.demo_total_daily_llm_calls,
                        "used": global_count,
                    },
                )
        except Exception as exc:
            logger.warning("rate_limit_check_failed", error=str(exc))
            return await call_next(request)

        return await call_next(request)
