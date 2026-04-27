from __future__ import annotations

from io import BytesIO
from typing import Tuple

from pypdf import PdfReader


def extract_pdf_text(data: bytes, max_chars: int = 120_000) -> Tuple[str, int]:
    """Return (text, page_count). Truncates to max_chars keeping head+tail."""
    reader = PdfReader(BytesIO(data))
    parts = []
    for p in reader.pages:
        t = p.extract_text() or ""
        if t.strip():
            parts.append(t)
    text = "\n\n".join(parts)
    if len(text) > max_chars:
        half = max_chars // 2
        text = text[:half] + "\n\n... [truncated for extraction] ...\n\n" + text[-half:]
    return text, len(reader.pages)
