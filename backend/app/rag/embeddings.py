from __future__ import annotations

import asyncio
from threading import Lock
from typing import List, Optional

import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    _instance: Optional["EmbeddingModel"] = None
    _lock = Lock()

    def __init__(self, model_name: str, device: str = "cpu") -> None:
        from sentence_transformers import SentenceTransformer

        logger.info("embedding_model_loading", model=model_name, device=device)
        self.model = SentenceTransformer(model_name, device=device)
        self.model_name = model_name
        self.dim = self.model.get_sentence_embedding_dimension()

    @classmethod
    def instance(cls) -> "EmbeddingModel":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    settings = get_settings()
                    cls._instance = cls(
                        model_name=settings.embedding_model,
                        device=settings.embedding_device,
                    )
        return cls._instance

    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        vecs = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vecs.astype(np.float32)

    async def aencode(self, texts: List[str]) -> np.ndarray:
        return await asyncio.to_thread(self.encode, texts)


def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel.instance()
