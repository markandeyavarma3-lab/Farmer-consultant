"""
tts.py — Text-to-Speech.

Primary: Sarvam Bulbul (natural Telugu/Hindi voices, free credits).
Fallback: gTTS (Google Translate TTS) — free, no API key, supports te/hi/en —
so spoken output still works even with zero Sarvam credits during a demo.

Returns MP3/WAV bytes that Streamlit can play with st.audio(...).
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

import requests

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import LANGUAGES, SARVAM_TTS_MODEL

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


def synthesize(text: str, language_code: str) -> tuple[bytes, str]:
    """Return (audio_bytes, mime_type). Tries Sarvam, falls back to gTTS."""
    # Strip the markdown source footer so it is not read aloud.
    spoken = text.split("\n\n_")[0].strip()
    try:
        return _synth_sarvam(spoken, language_code), "audio/wav"
    except Exception:
        return _synth_gtts(spoken, language_code), "audio/mp3"


def _synth_sarvam(text: str, language_code: str) -> bytes:
    key = (os.environ.get("SARVAM_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("No Sarvam key")
    sarvam_lang = LANGUAGES[language_code]["sarvam_code"]

    headers = {"api-subscription-key": key, "Content-Type": "application/json"}
    body = {
        "inputs": [text[:1500]],            # keep request small
        "target_language_code": sarvam_lang,
        "model": SARVAM_TTS_MODEL,
        "speaker": "meera",
    }
    resp = requests.post(SARVAM_TTS_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    audios = resp.json().get("audios", [])
    if not audios:
        raise RuntimeError("Sarvam returned no audio")
    return base64.b64decode(audios[0])


def _synth_gtts(text: str, language_code: str) -> bytes:
    from gtts import gTTS

    lang = LANGUAGES[language_code]["tts_lang"]
    buf = io.BytesIO()
    gTTS(text=text[:1500], lang=lang).write_to_fp(buf)
    return buf.getvalue()
