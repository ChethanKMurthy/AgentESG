from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(512), index=True)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float)
    user_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    client_ip: Mapped[Optional[str]] = mapped_column(String(64))
    user_agent: Mapped[Optional[str]] = mapped_column(String(512))
    event_type: Mapped[str] = mapped_column(String(64), default="http_request", index=True)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
