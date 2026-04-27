from __future__ import annotations

import json
import os
import pickle
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

import numpy as np

from app.rag.chunker import Chunk


class VectorStore:
    def __init__(self, path: str, dim: int) -> None:
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.dim = dim
        self.index_file = self.path / "index.faiss"
        self.chunks_file = self.path / "chunks.json"
        self.bm25_file = self.path / "bm25.pkl"
        self.meta_file = self.path / "meta.json"
        self._index = None

    # ---------- FAISS ----------
    def _new_index(self):
        import faiss

        return faiss.IndexFlatIP(self.dim)

    def load_index(self):
        import faiss

        if self._index is not None:
            return self._index
        if self.index_file.exists():
            self._index = faiss.read_index(str(self.index_file))
        else:
            self._index = self._new_index()
        return self._index

    def save_index(self) -> None:
        import faiss

        if self._index is None:
            return
        faiss.write_index(self._index, str(self.index_file))

    def add_vectors(self, vectors: np.ndarray) -> None:
        idx = self.load_index()
        idx.add(vectors)

    def search(self, query_vec: np.ndarray, top_k: int):
        idx = self.load_index()
        if idx.ntotal == 0:
            return np.zeros((1, 0), dtype=np.float32), np.full((1, 0), -1, dtype=np.int64)
        return idx.search(query_vec, min(top_k, idx.ntotal))

    # ---------- chunks ----------
    def save_chunks(self, chunks: List[Chunk]) -> None:
        data = [asdict(c) for c in chunks]
        self.chunks_file.write_text(json.dumps(data, ensure_ascii=False))

    def load_chunks(self) -> List[Chunk]:
        if not self.chunks_file.exists():
            return []
        data = json.loads(self.chunks_file.read_text())
        return [Chunk(**d) for d in data]

    # ---------- BM25 ----------
    def save_bm25(self, bm25_obj, tokens: List[List[str]]) -> None:
        with open(self.bm25_file, "wb") as f:
            pickle.dump({"bm25": bm25_obj, "tokens": tokens}, f)

    def load_bm25(self):
        if not self.bm25_file.exists():
            return None, None
        with open(self.bm25_file, "rb") as f:
            d = pickle.load(f)
        return d.get("bm25"), d.get("tokens")

    # ---------- meta ----------
    def save_meta(self, meta: dict) -> None:
        self.meta_file.write_text(json.dumps(meta))

    def load_meta(self) -> dict:
        if not self.meta_file.exists():
            return {}
        return json.loads(self.meta_file.read_text())

    def exists(self) -> bool:
        return self.index_file.exists() and self.chunks_file.exists()

    def reset(self) -> None:
        for f in [self.index_file, self.chunks_file, self.bm25_file, self.meta_file]:
            if f.exists():
                os.remove(f)
        self._index = None
