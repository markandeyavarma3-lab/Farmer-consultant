"""
rag.py — Retrieval-Augmented Generation over the natural-farming knowledge base.

Uses ChromaDB (local, persistent, free) with a small multilingual sentence-
transformer so a Telugu/Hindi query can match the English knowledge base.

The knowledge base is the heart of "not a ChatGPT wrapper": every answer is
grounded in curated, source-noted documents, not the model's open memory.
"""

from __future__ import annotations

import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    KB_DIR, CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_K, MAX_DISTANCE_FOR_CONFIDENCE,
)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split on paragraph boundaries, then pack into ~size-char chunks with overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            # carry a little overlap for context continuity
            tail = current[-overlap:] if current else ""
            current = (tail + "\n\n" + para).strip() if tail else para
    if current:
        chunks.append(current)
    return chunks


def _load_kb_chunks() -> list[dict]:
    """Read every markdown file in the KB and return chunk dicts with metadata."""
    records = []
    for md_path in sorted(KB_DIR.glob("*.md")):
        raw = md_path.read_text(encoding="utf-8")
        # Use the first H1 as a human-readable source title.
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
def _embedding_fn():
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)


def build_index(reset: bool = True) -> int:
    """(Re)build the Chroma collection from the knowledge base. Returns chunk count."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )
    records = _load_kb_chunks()
    collection.add(
        ids=[r["id"] for r in records],
        documents=[r["text"] for r in records],
        metadatas=[{"source": r["source"], "file": r["file"]} for r in records],
    )
    return len(records)


def get_collection():
    """Open the persistent collection (assumes build_index has been run)."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def retrieve(query: str, k: int = RETRIEVAL_K) -> dict:
    """
    Return retrieved context plus a confidence flag.

    confident == False signals the support-tier escalation logic that the query
    is likely out of scope and a human should be suggested.
    """
    collection = get_collection()
    res = collection.query(query_texts=[query], n_results=k)

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    if not docs:
        return {"context": "", "sources": [], "confident": False, "best_distance": None}

    best_distance = min(dists) if dists else None
    confident = best_distance is not None and best_distance <= MAX_DISTANCE_FOR_CONFIDENCE

    context = "\n\n---\n\n".join(docs)
    sources = [m.get("source", "") for m in metas]
    return {
        "context": context,
        "sources": sources,
        "confident": confident,
        "best_distance": best_distance,
    }
