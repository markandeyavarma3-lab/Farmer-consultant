"""
llm.py — Grounded answer generation via Groq (free tier).

Takes the retrieved context and produces a farmer-facing answer that obeys the
strict anti-hallucination system prompt. Falls back to the smaller, higher-rate-
limit model if the primary is rate-limited (important for a live demo).
"""

from __future__ import annotations

import os
from pathlib import Path

from groq import Groq

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import GROQ_MODEL, GROQ_MODEL_FALLBACK, GROQ_MODEL_EMERGENCY
from src.prompts import SYSTEM_PROMPT, build_answer_prompt, sources_footer


def _client() -> Groq:
    key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your environment or secrets.")
    return Groq(api_key=key)


def generate_answer(
    query: str,
    context: str,
    sources: list[str],
    language_code: str,
    expertise: str,
) -> str:
    """Generate a grounded answer. Returns the answer text with a source footer."""
    client = _client()
    user_prompt = build_answer_prompt(query, context, language_code, expertise)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for model in (GROQ_MODEL, GROQ_MODEL_FALLBACK, GROQ_MODEL_EMERGENCY):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,        # low — we want faithful, not creative
                max_tokens=700,
            )
            answer = completion.choices[0].message.content.strip()
            return answer + sources_footer(sources, language_code)
        except Exception as exc:  # rate limit, transient error -> try fallback
            last_error = exc
            continue

    raise RuntimeError(f"Both Groq models failed. Last error: {last_error}")
