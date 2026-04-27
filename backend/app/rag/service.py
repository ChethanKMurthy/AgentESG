from __future__ import annotations

import asyncio
from threading import Lock
from typing import List, Optional

from rank_bm25 import BM25Okapi

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.chunker import Chunk, chunk_documents
from app.rag.embeddings import EmbeddingModel, get_embedding_model
from app.rag.loader import load_documents
from app.rag.reranker import Reranker
from app.rag.retriever import HybridRetriever, RetrievedChunk, tokenize
from app.rag.store import VectorStore

logger = get_logger(__name__)


class RAGService:
    _instance: Optional["RAGService"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedder: EmbeddingModel = get_embedding_model()
        self.store = VectorStore(self.settings.vector_store_path, self.embedder.dim)
        self.retriever = HybridRetriever(
            store=self.store,
            embedder=self.embedder,
            dense_weight=self.settings.rag_dense_weight,
            sparse_weight=self.settings.rag_sparse_weight,
            rrf_k=self.settings.rag_rrf_k,
        )
        self.reranker = Reranker()
        self._ingest_lock = asyncio.Lock()
        if self.store.exists():
            try:
                self.retriever.load()
            except Exception as exc:
                logger.warning("rag_load_failed", error=str(exc))

    @classmethod
    def instance(cls) -> "RAGService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _build_sync(self, root: str) -> dict:
        docs = load_documents(root)
        if not docs:
            return {"documents": 0, "chunks": 0}
        chunks: List[Chunk] = chunk_documents(
            docs,
            chunk_size=self.settings.rag_chunk_size,
            overlap=self.settings.rag_chunk_overlap,
        )
        texts = [c.text for c in chunks]
        vectors = self.embedder.encode(texts)

        self.store.reset()
        self.store.add_vectors(vectors)
        self.store.save_index()
        self.store.save_chunks(chunks)

        tokens = [tokenize(t) for t in texts]
        bm25 = BM25Okapi(tokens)
        self.store.save_bm25(bm25, tokens)

        self.store.save_meta(
            {
                "documents": len(docs),
                "chunks": len(chunks),
                "embedding_model": self.embedder.model_name,
                "dim": self.embedder.dim,
            }
        )
        self.retriever.load()
        return {"documents": len(docs), "chunks": len(chunks)}

    async def ingest(self, root: Optional[str] = None) -> dict:
        target = root or self.settings.documents_path
        async with self._ingest_lock:
            logger.info("rag_ingest_start", root=target)
            result = await asyncio.to_thread(self._build_sync, target)
            logger.info("rag_ingest_done", **result)
            return result

    async def query(
        self,
        text: str,
        top_k: Optional[int] = None,
        rerank: bool = True,
    ) -> List[RetrievedChunk]:
        if not self.retriever.is_ready():
            return []
        k = top_k or self.settings.rag_top_k
        pool = max(k * 3, 15)
        candidates = await asyncio.to_thread(self.retriever.search, text, pool)
        if rerank:
            candidates = self.reranker.rerank(text, candidates, k)
        return candidates[:k]

    def stats(self) -> dict:
        meta = self.store.load_meta()
        meta["ready"] = self.retriever.is_ready()
        return meta


def get_rag_service() -> RAGService:
    return RAGService.instance()
