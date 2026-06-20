"""
rag.py — Retrieval-Augmented Generation over the natural-farming knowledge base.

Uses sentence-transformers + numpy for vector search. No ChromaDB, no
opentelemetry, no protobuf — works on any Python version including 3.14,
and deploys cleanly on Streamlit Community Cloud.

37 chunks at 384 dimensions = ~57 KB index. Numpy cosine search over that
is sub-millisecond; ChromaDB would be overkill and broke on Python 3.14.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    KB_DIR, EMBED_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_K, MAX_DISTANCE_FOR_CONFIDENCE,
)

INDEX_FILE = Path(__file__).resolve().parent.parent / "vector_index.npz"

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


# ---------------------------------------------------------------------------
# Chunking (unchanged logic)
# ---------------------------------------------------------------------------
def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            tail = current[-overlap:] if current else ""
            current = (tail + "\n\n" + para).strip() if tail else para
    if current:
        chunks.append(current)
    return chunks


def _load_kb_chunks() -> list[dict]:
    records = []
    for md_path in sorted(KB_DIR.glob("*.md")):
        raw = md_path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else md_path.stem
        for i, chunk in enumerate(_chunk_text(raw)):
            records.append({
                "id": f"{md_path.stem}-{i}",
                "text": chunk,
                "source": title,
                "file": md_path.name,
            })
    return records


# ---------------------------------------------------------------------------
# Index build / load
# ---------------------------------------------------------------------------
def build_index(reset: bool = True) -> int:
    """Build a numpy vector index from the knowledge base. Returns chunk count."""
    records = _load_kb_chunks()
    texts = [r["text"] for r in records]
    sources = [r["source"] for r in records]

    embeddings = _get_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )

    np.savez_compressed(
        str(INDEX_FILE),
        embeddings=embeddings.astype(np.float32),
        sources=np.array(sources),
        texts=np.array(texts),
    )
    return len(records)


class _Index:
    """Thin wrapper so app.py can call collection.count() unchanged."""
    def count(self) -> int:
        if not INDEX_FILE.exists():
            return 0
        try:
            data = np.load(str(INDEX_FILE), allow_pickle=False)
            return int(len(data["texts"]))
        except Exception:
            return 0


def get_collection() -> _Index:
    """Return an object with a .count() method (mirrors the old ChromaDB API)."""
    return _Index()


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def retrieve(query: str, k: int = RETRIEVAL_K) -> dict:
    """
    Return retrieved context plus a confidence flag.
    confident == False triggers Tier-3 human escalation.
    """
    if not INDEX_FILE.exists():
        build_index()

    data = np.load(str(INDEX_FILE), allow_pickle=False)
    embeddings = data["embeddings"]        # (n, d) float32, already L2-normalised
    sources = data["sources"].tolist()
    texts = data["texts"].tolist()

    query_emb = _get_model().encode(
        [query], normalize_embeddings=True
    ).astype(np.float32)                   # (1, d)

    # Cosine similarity = dot product when both sides are L2-normalised
    scores = np.dot(embeddings, query_emb.T).flatten()
    distances = 1.0 - scores              # cosine distance in [0, 2]

    top_k = min(k, len(texts))
    top_idx = np.argsort(distances)[:top_k]

    best_distance = float(distances[top_idx[0]])
    confident = best_distance <= MAX_DISTANCE_FOR_CONFIDENCE

    context = "\n\n---\n\n".join(texts[i] for i in top_idx)
    retrieved_sources = [sources[i] for i in top_idx]

    return {
        "context": context,
        "sources": retrieved_sources,
        "confident": confident,
        "best_distance": best_distance,
    }
