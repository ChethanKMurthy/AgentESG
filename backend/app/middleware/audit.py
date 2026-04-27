import time
import uuid
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.audit import AuditLog

logger = get_logger(__name__)

_SKIP_PATHS = {"/health", "/health/db", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        request.state.request_id = request_id
        start = time.perf_counter()

        status_code: Optional[int] = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            path = request.url.path
            if path not in _SKIP_PATHS:
                try:
                    async with SessionLocal() as session:
                        session.add(
                            AuditLog(
                                request_id=request_id,
                                method=request.method,
                                path=path,
                                status_code=status_code,
                                latency_ms=latency_ms,
                                user_id=request.headers.get("x-user-id"),
                                client_ip=request.client.host if request.client else None,
                                user_agent=request.headers.get("user-agent"),
                                event_type="http_request",
                                payload={"query": dict(request.query_params)},
                            )
                        )
                        await session.commit()
                except Exception as exc:
                    logger.warning("audit_write_failed", error=str(exc), path=path)
