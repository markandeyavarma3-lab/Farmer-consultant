# 🌱 Multilevel Natural Farming Consultant (Voice Assistant)

A voice-first assistant that gives small and marginal farmers **chemical-free natural-farming
advice** (APCNF / Zero Budget Natural Farming) in **Telugu, Hindi, or English** — grounded in
trusted sources, honest about what it doesn't know, and built entirely on **free-tier tools**.

> Submission for Connecting Dreams Foundation — Option B. This is a **proof of concept**, not a
> production system. See `docs/DESIGN_RATIONALE.md` for the thinking behind every decision.

---

## Why this exists

Only about a third of Indian farmers have access to any agricultural extension service. The
Kisan Call Centre is human-bandwidth-limited, runs fixed hours, and gives generic advice. Most
agritech apps are text-heavy, English-biased, and ultimately sell chemical inputs — which is the
opposite of what a natural farmer needs. Meanwhile **Andhra Pradesh runs the world's largest
natural-farming programme (APCNF, 1.7M+ farmers)**, yet a farmer with a question at 9 PM has
nowhere specific to turn.

This assistant fills that gap: **voice in, voice out, in the farmer's own language, answering
only from a curated natural-farming knowledge base, and handing off to a human when unsure.**

## What "Multilevel" means here (three deliberate levels)

1. **Multi-layer cropping** — the *domain* meaning. The assistant knows Palekar's five-layer
   model and APCNF's A-Grade / ATM / 365-Days-Green-Cover models (`knowledge_base/05_*`).
2. **Multi-level support** — Tier 1 self-serve voice → Tier 2 RAG-grounded answer → Tier 3
   automatic **human escalation** to a CRP / Kisan Call Centre when confidence is low.
3. **Multi-level users** — a Beginner/Experienced toggle changes how deep the answer goes.
   Plus three **language levels** (Telugu / Hindi / English).

## How it works (pipeline)

```
🎙️ Voice  ─▶  STT            ─▶  RAG retrieval     ─▶  confident?
            (Sarvam: te/hi)      (ChromaDB over          │
            (Groq Whisper: en)    natural-farming KB)     ├─ no  ─▶ human escalation message
                                                          │
                                                          └─ yes ─▶ Groq Llama 3.1 8B Instant
                                                                    (answer ONLY from context)
                                                                         │
🔊 Spoken answer  ◀──  TTS (Sarvam / gTTS fallback)  ◀────────────────────┘
                                       + on-screen text + source citation
```

## Tech stack (100% free tier)

| Layer        | Choice                                   | Why |
|--------------|------------------------------------------|-----|
| UI + hosting | Streamlit + Community Cloud              | Native mic widget (`st.audio_input`), one-click deploy |
| LLM          | Groq — Llama 3.1 8B Instant (70B quality fallback) | Fast by default; 70B kicks in if 8B rate-limits |
| STT (te/hi)  | Sarvam AI saarika:v2.5 → Groq Whisper fallback | Best Indian-language accuracy; Whisper backup if Sarvam fails |
| STT (en)     | Groq Whisper large-v3                    | Free, accurate for English |
| TTS          | Sarvam Bulbul → gTTS fallback            | Natural Indic voices; gTTS needs no key |
| RAG          | ChromaDB + multilingual MiniLM embeddings| Local, free, cross-lingual retrieval |
| Knowledge    | Curated APCNF / NITI Aayog corpus        | Grounded, source-noted, anti-hallucination |

> **Deliberately NOT used:** vanilla OpenAI Whisper for Telugu — independent field benchmarks
> found it produces incoherent Telugu output. See the design rationale.

---

## Run it locally

```bash
# 1. Install
pip install -r requirements.txt

# 2. Add keys (both free)
cp .env.example .env        # then edit .env with your Groq + Sarvam keys

# 3. Build the vector index from the knowledge base
python scripts/build_index.py

# 4. Launch
streamlit run app.py
```

Open the local URL, allow microphone access, pick a language, and ask a question like
*"జీవామృతం ఎలా తయారు చేయాలి?"* ("How do I make Jeevamrutham?").

> No Sarvam key? The app still runs: use **English** voice (Groq Whisper) or type in any
> language, and spoken answers fall back to free gTTS.

## Deploy to Streamlit Community Cloud (free)

1. Push this repo to GitHub.
2. On share.streamlit.io, create a new app pointing at `app.py`.
3. In **App settings → Secrets**, paste your keys (see `.streamlit/secrets.toml.example`).
4. Deploy. The vector index builds automatically on first run.

## Project structure

```
natural-farming-consultant/
├── app.py                  # Streamlit voice UI + the 3 "multilevel" controls
├── config.py               # All models, languages, thresholds, contacts
├── requirements.txt
├── src/
│   ├── stt.py              # Sarvam (te/hi) + Groq Whisper (en) routing
│   ├── tts.py              # Sarvam Bulbul → gTTS fallback
│   ├── rag.py              # chunking, ChromaDB, confidence-scored retrieval
│   ├── llm.py              # Groq grounded answer generation + model fallback
│   ├── prompts.py          # anti-hallucination system prompt
│   └── escalation.py       # Tier-3 human handoff messages (te/hi/en)
├── knowledge_base/         # 7 curated, source-noted natural-farming docs
├── scripts/build_index.py  # build the vector store
└── docs/
    ├── DESIGN_RATIONALE.md  # why every decision was made (read this)
    └── DEMO_SCRIPT.md       # 3-minute demo walkthrough
```

## Honest limitations (disclosed on purpose)

- **Telugu STT is the hardest part** — even the best free models sit around 25–46% word-error-
  rate on real field audio, so the app **always shows the transcript for correction** before
  answering. For the most reliable live demo, Hindi STT is stronger.
- **Free-tier rate limits** are fine for a demo, not for scale (clear upgrade path exists).
- **Advice is advisory.** Recipe quantities follow NITI Aayog figures but vary by source; the
  assistant escalates to a human for anything needing local judgement or a field visit.
- Natural-farming **yield** evidence is genuinely mixed; the assistant is built to emphasise
  *cost/risk reduction*, not yield miracles.
