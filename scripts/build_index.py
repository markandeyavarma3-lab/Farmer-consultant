"""
build_index.py — One-time (or on-change) build of the Chroma vector store.

Run this once before launching the app, and again whenever you edit the
knowledge base:

    python scripts/build_index.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.rag import build_index  # noqa: E402


def main():
    print("Building vector index from knowledge_base/ ...")
    n = build_index(reset=True)
    print(f"Done. Indexed {n} chunks into the Chroma store.")


if __name__ == "__main__":
    main()
