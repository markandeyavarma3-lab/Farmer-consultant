"""
stt.py — Speech-to-Text routing.

Routing:
  Telugu / Hindi  -> Sarvam saarika:v2 (best Indian-language + agriculture-term accuracy)
                     Falls back to Groq Whisper-large-v3 if Sarvam fails for any reason.
  English         -> Groq Whisper whisper-large-v3 directly (fast, accurate)

Audio format note: browsers record in WebM (Chrome/Edge), OGG (Firefox), or MP4 (Safari).
We detect the actual format from magic bytes so neither API rejects a mislabelled file.
"""

from __future__ import annotations

import io
import os
from pathlib import Path

import requests

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import LANGUAGES, GROQ_WHISPER_MODEL, SARVAM_STT_MODEL

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

# Whisper language codes for Indian languages (ISO 639-1)
_WHISPER_LANG = {"te": "te", "hi": "hi", "en": "en"}


def _detect_audio_fmt(audio_bytes: bytes) -> tuple[str, str]:
    """Return (filename_ext, mime_type) based on magic bytes."""
    if audio_bytes[:4] == b"RIFF":
        return "wav", "audio/wav"
    if audio_bytes[:4] == b"\x1aE\xdf\xa3":
        return "webm", "audio/webm"
    if audio_bytes[:3] == b"OggS":
        return "ogg", "audio/ogg"
    if len(audio_bytes) > 8 and audio_bytes[4:8] == b"ftyp":
        return "mp4", "audio/mp4"
    if audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb":
        return "mp3", "audio/mp3"
    return "webm", "audio/webm"  # Chrome/Edge default


def transcribe(audio_bytes: bytes, language_code: str) -> str:
    """Transcribe audio. Returns recognised text (shown to user for correction)."""
    if language_code == "en":
        return _transcribe_groq(audio_bytes, "en")

    # Telugu / Hindi: try Sarvam first, fall back to Groq Whisper
    try:
        return _transcribe_sarvam(audio_bytes, language_code)
    except Exception as sarvam_err:
        # Groq Whisper supports Telugu and Hindi — quality is lower than Sarvam
        # but far better than no voice input at all.
        try:
            return _transcribe_groq(audio_bytes, language_code)
        except Exception:
            raise sarvam_err  # surface the original Sarvam error if both fail


def _transcribe_sarvam(audio_bytes: bytes, language_code: str) -> str:
    key = (os.environ.get("SARVAM_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("SARVAM_API_KEY not set — needed for Telugu/Hindi speech.")
    sarvam_lang = LANGUAGES[language_code]["sarvam_code"]

    ext, mime = _detect_audio_fmt(audio_bytes)
    files = {"file": (f"audio.{ext}", io.BytesIO(audio_bytes), mime)}
    data = {"model": SARVAM_STT_MODEL, "language_code": sarvam_lang}
    headers = {"api-subscription-key": key}

    resp = requests.post(SARVAM_STT_URL, headers=headers, files=files, data=data, timeout=60)
    if not resp.ok:
        raise RuntimeError(
            f"Sarvam API error {resp.status_code}: {resp.text[:300]}"
        )
    payload = resp.json()
    transcript = (payload.get("transcript") or payload.get("text") or "").strip()
    if not transcript:
        raise RuntimeError(f"Sarvam returned empty transcript. Response: {payload}")
    return transcript


def _transcribe_groq(audio_bytes: bytes, language_code: str) -> str:
    """Use Groq Whisper-large-v3 for any language (en/hi/te)."""
    from groq import Groq

    key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY not set — needed for speech recognition.")
    client = Groq(api_key=key)

    ext, _ = _detect_audio_fmt(audio_bytes)
    whisper_lang = _WHISPER_LANG.get(language_code, language_code)

    result = client.audio.transcriptions.create(
        file=(f"audio.{ext}", audio_bytes),
        model=GROQ_WHISPER_MODEL,
        language=whisper_lang,
        response_format="text",
    )
    return result if isinstance(result, str) else getattr(result, "text", "").strip()
