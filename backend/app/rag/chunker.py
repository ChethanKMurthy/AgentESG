from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from app.rag.loader import RawDocument


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    source: str
    text: str
    position: int
    metadata: dict = field(default_factory=dict)


_SPLIT_RE = re.compile(r"(?<=[\.\?\!\n])\s+")


def _sentence_split(text: str) -> List[str]:
    parts = [p.strip() for p in _SPLIT_RE.split(text) if p.strip()]
    return parts or [text]


def chunk_document(
    doc: RawDocument,
    chunk_size: int,
    overlap: int,
) -> List[Chunk]:
    sentences = _sentence_split(doc.text)
    chunks: List[Chunk] = []
    buf: List[str] = []
    size = 0
    pos = 0

    def flush():
        nonlocal buf, size, pos
        if not buf:
            return
        text = " ".join(buf).strip()
        if text:
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}:{pos}",
                    doc_id=doc.doc_id,
                    source=doc.source,
                    text=text,
                    position=pos,
                    metadata=dict(doc.metadata),
                )
            )
            pos += 1
        buf = []
        size = 0

    for sent in sentences:
        if size + len(sent) + 1 > chunk_size and buf:
            flush()
            if overlap > 0 and chunks:
                tail = chunks[-1].text[-overlap:]
                buf = [tail]
                size = len(tail)
        buf.append(sent)
        size += len(sent) + 1
    flush()
    return chunks


def chunk_documents(
    docs: List[RawDocument],
    chunk_size: int,
    overlap: int,
) -> List[Chunk]:
    out: List[Chunk] = []
    for d in docs:
        out.extend(chunk_document(d, chunk_size, overlap))
    return out
