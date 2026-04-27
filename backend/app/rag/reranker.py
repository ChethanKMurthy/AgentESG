from __future__ import annotations

from typing import List

from app.rag.retriever import RetrievedChunk


class Reranker:
    """MMR-like diversification; keeps top-scoring but penalizes duplicates."""

    def __init__(self, lambda_mult: float = 0.7) -> None:
        self.lambda_mult = lambda_mult

    def rerank(self, query: str, candidates: List[RetrievedChunk], top_k: int) -> List[RetrievedChunk]:
        if not candidates:
            return []
        selected: List[RetrievedChunk] = []
        remaining = list(candidates)
        while remaining and len(selected) < top_k:
            best_i, best_score = 0, float("-inf")
            for i, c in enumerate(remaining):
                rel = c.score
                div = 0.0
                for s in selected:
                    div = max(div, _jaccard(c.chunk.text, s.chunk.text))
                score = self.lambda_mult * rel - (1 - self.lambda_mult) * div
                if score > best_score:
                    best_score, best_i = score, i
            selected.append(remaining.pop(best_i))
        return selected


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
