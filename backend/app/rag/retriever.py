from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

from app.rag.chunker import Chunk
from app.rag.embeddings import EmbeddingModel
from app.rag.store import VectorStore

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None


class HybridRetriever:
    def __init__(
        self,
        store: VectorStore,
        embedder: EmbeddingModel,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        rrf_k: int = 60,
    ) -> None:
        self.store = store
        self.embedder = embedder
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.rrf_k = rrf_k
        self._chunks: List[Chunk] = []
        self._bm25 = None
        self._tokens: List[List[str]] = []

    def load(self) -> None:
        self._chunks = self.store.load_chunks()
        self._bm25, self._tokens = self.store.load_bm25()
        self.store.load_index()

    def is_ready(self) -> bool:
        return bool(self._chunks) and self._bm25 is not None and self.store.exists()

    def _dense_rank(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        q = self.embedder.encode([query])
        scores, ids = self.store.search(q, top_k)
        if ids.size == 0:
            return []
        return [(int(i), float(s)) for s, i in zip(scores[0], ids[0]) if i >= 0]

    def _sparse_rank(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        if self._bm25 is None:
            return []
        tokens = tokenize(query)
        scores = self._bm25.get_scores(tokens)
        if len(scores) == 0:
            return []
        top = np.argsort(scores)[::-1][:top_k]
        return [(int(i), float(scores[i])) for i in top if scores[i] > 0]

    def search(self, query: str, top_k: int) -> List[RetrievedChunk]:
        if not self._chunks:
            self.load()
        if not self._chunks:
            return []

        pool = max(top_k * 3, 20)
        dense = self._dense_rank(query, pool)
        sparse = self._sparse_rank(query, pool)

        rrf: dict[int, float] = {}
        dense_rank_map: dict[int, int] = {}
        sparse_rank_map: dict[int, int] = {}
        for rank, (idx, _) in enumerate(dense):
            rrf[idx] = rrf.get(idx, 0.0) + self.dense_weight / (self.rrf_k + rank + 1)
            dense_rank_map[idx] = rank
        for rank, (idx, _) in enumerate(sparse):
            rrf[idx] = rrf.get(idx, 0.0) + self.sparse_weight / (self.rrf_k + rank + 1)
            sparse_rank_map[idx] = rank

        fused = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        out: List[RetrievedChunk] = []
        for idx, score in fused:
            if idx < 0 or idx >= len(self._chunks):
                continue
            out.append(
                RetrievedChunk(
                    chunk=self._chunks[idx],
                    score=float(score),
                    dense_rank=dense_rank_map.get(idx),
                    sparse_rank=sparse_rank_map.get(idx),
                )
            )
        return out
