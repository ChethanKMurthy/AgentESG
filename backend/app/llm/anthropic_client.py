from __future__ import annotations

from threading import Lock
from typing import List, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnthropicClient:
    _instance: Optional["AnthropicClient"] = None
    _lock = Lock()

    def __init__(self) -> None:
        from anthropic import AsyncAnthropic

        settings = get_settings()
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens
        self.enabled = bool(settings.anthropic_api_key)
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key) if self.enabled else None

    @classmethod
    def instance(cls) -> "AnthropicClient":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def stream(
        self,
        system: str,
        user: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        if not self.enabled or self.client is None:
            yield "LLM disabled (no ANTHROPIC_API_KEY). Returning retrieved context only."
            return
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        async with self.client.messages.stream(**kwargs) as s:
            async for chunk in s.text_stream:
                yield chunk

    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        if not self.enabled or self.client is None:
            logger.warning("llm_disabled_returning_stub")
            return (
                "LLM disabled (no ANTHROPIC_API_KEY). "
                "Returning retrieved context only."
            )
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            resp = await self.client.messages.create(**kwargs)
            parts: List[str] = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
            return "".join(parts).strip()
        except Exception as exc:
            logger.error("llm_call_failed", error=str(exc))
            raise


def get_llm_client() -> AnthropicClient:
    return AnthropicClient.instance()
