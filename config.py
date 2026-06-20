"""
config.py — Central configuration for the Natural Farming Consultant.

All tunable constants live here so the rest of the code reads cleanly and the
free-tier model/provider choices are easy to see and swap.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
KB_DIR = ROOT_DIR / "knowledge_base"
CHROMA_DIR = ROOT_DIR / "chroma_store"          # persistent local vector store
COLLECTION_NAME = "natural_farming"

# ---------------------------------------------------------------------------
# Languages  (the "multilingual" level of "multilevel")
# Telugu is primary (Andhra Pradesh); Hindi is the most reliable for live STT
# demos; English is the fallback / developer language.
# ---------------------------------------------------------------------------
LANGUAGES = {
    "te": {"name": "తెలుగు (Telugu)", "sarvam_code": "te-IN", "tts_lang": "te"},
    "hi": {"name": "हिंदी (Hindi)",   "sarvam_code": "hi-IN", "tts_lang": "hi"},
    "en": {"name": "English",         "sarvam_code": "en-IN", "tts_lang": "en"},
}
DEFAULT_LANG = "te"

# ---------------------------------------------------------------------------
# Expertise levels  (the "user-expertise" level of "multilevel")
# Changes how deep / how simple the generated answer is.
# ---------------------------------------------------------------------------
EXPERTISE_LEVELS = {
    "beginner": "New to natural farming — explain simply, define terms, give one clear next step.",
    "experienced": "Already practises natural farming — be concise, use exact quantities and technical terms.",
}
DEFAULT_EXPERTISE = "beginner"

# ---------------------------------------------------------------------------
# Models (all free tier)
# ---------------------------------------------------------------------------
# Groq LLM — the reasoning "brain".
# llama-3.1-8b-instant: very fast, handles most farming Q&A well (primary)
# llama-3.3-70b-versatile: better quality for complex advice (quality fallback)
# llama-3.2-3b-preview: emergency fallback if rate limits hit during live demo
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_MODEL_FALLBACK = "llama-3.3-70b-versatile"
GROQ_MODEL_EMERGENCY = "llama-3.2-3b-preview"
GROQ_WHISPER_MODEL = "whisper-large-v3"          # used ONLY for English STT

# Embeddings — small multilingual model so it fits Streamlit Cloud RAM limits
# and can match a Telugu/Hindi query against an English knowledge base.
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Sarvam — Indian-language STT/TTS (best agri-term accuracy on free credits).
SARVAM_STT_MODEL = "saarika:v2.5"
SARVAM_TTS_MODEL = "bulbul:v2"

# ---------------------------------------------------------------------------
# Retrieval / escalation tuning  (the "support-tier" level of "multilevel")
# ---------------------------------------------------------------------------
RETRIEVAL_K = 4                      # chunks pulled per query
# Chroma returns cosine *distance* (0 = identical, 2 = opposite). If the best
# chunk is farther than this, we treat the query as out-of-scope and escalate.
MAX_DISTANCE_FOR_CONFIDENCE = 1.15
CHUNK_SIZE = 900                     # characters per chunk
CHUNK_OVERLAP = 150

# ---------------------------------------------------------------------------
# Human escalation contacts (Tier 3)
# ---------------------------------------------------------------------------
CONTACTS = {
    "kisan_call_centre": "1800-180-1551",
    "kcc_hours": "6:00 AM – 10:00 PM, all days",
    "apcnf_note": "Ask for your village/mandal RySS Community Resource Person (CRP).",
}
