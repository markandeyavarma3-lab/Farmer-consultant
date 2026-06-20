"""
app.py — Natural Farming Consultant (voice-first, multilevel).

Run locally:   streamlit run app.py
Deploy:        Streamlit Community Cloud (set GROQ_API_KEY and SARVAM_API_KEY in Secrets)

The "multilevel" design is visible right in the sidebar controls:
  1. Language level     — Telugu / Hindi / English
  2. Expertise level    — Beginner / Experienced (changes answer depth)
  3. Support level/tier — RAG-grounded answer, else automatic human escalation
And in the knowledge base, the *cropping* multi-layer (five-layer) model.
"""

from __future__ import annotations

import os
import streamlit as st


def _load_secrets():
    """Bridge Streamlit Cloud secrets into os.environ so the API modules
    (which read os.environ) work both locally (.env) and on Streamlit Cloud."""
    # Local development: load a .env file if present.
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    # Streamlit Cloud: copy secrets into the environment.
    try:
        for key in ("GROQ_API_KEY", "SARVAM_API_KEY"):
            if key in st.secrets and not os.environ.get(key):
                os.environ[key] = st.secrets[key]
    except Exception:
        pass  # no secrets.toml locally is fine; .env / shell env will be used


_load_secrets()

from config import (
    LANGUAGES, DEFAULT_LANG, EXPERTISE_LEVELS, DEFAULT_EXPERTISE, CONTACTS,
)
from src.rag import retrieve, get_collection
from src.llm import generate_answer
from src.escalation import should_escalate, escalation_message

# ---------------------------------------------------------------------------
# UI strings per language (kept tiny and inline for a PoC)
# ---------------------------------------------------------------------------
UI = {
    "te": {
        "title": "🌱 సహజ వ్యవసాయ సలహాదారు",
        "tagline": "మీ ప్రశ్నను మాట్లాడండి లేదా టైప్ చేయండి",
        "speak": "🎙️ మీ ప్రశ్నను రికార్డ్ చేయండి",
        "type": "లేదా ఇక్కడ టైప్ చేయండి",
        "heard": "మీరు అడిగింది",
        "thinking": "ఆలోచిస్తున్నాను...",
        "ask_btn": "సలహా అడగండి",
    },
    "hi": {
        "title": "🌱 प्राकृतिक खेती सलाहकार",
        "tagline": "अपना सवाल बोलें या टाइप करें",
        "speak": "🎙️ अपना सवाल रिकॉर्ड करें",
        "type": "या यहाँ टाइप करें",
        "heard": "आपने पूछा",
        "thinking": "सोच रहा हूँ...",
        "ask_btn": "सलाह पूछें",
    },
    "en": {
        "title": "🌱 Natural Farming Consultant",
        "tagline": "Speak or type your question",
        "speak": "🎙️ Record your question",
        "type": "Or type here",
        "heard": "You asked",
        "thinking": "Thinking...",
        "ask_btn": "Ask",
    },
}


@st.cache_resource(show_spinner="Loading knowledge base...")
def _warm_collection():
    """Load the Chroma collection once per session (cached across reruns).

    On a fresh deploy the vector store is empty, so build it from the
    knowledge base on first run.
    """
    from src.rag import build_index
    collection = get_collection()
    if collection.count() == 0:
        build_index(reset=True)
        collection = get_collection()
    return collection


def _answer_flow(query: str, lang: str, expertise: str):
    """Shared pipeline: retrieve -> (escalate | generate) -> display + speak."""
    if not query.strip():
        st.warning("Please ask a question first.")
        return

    st.markdown(f"**{UI[lang]['heard']}:** {query}")

    with st.spinner(UI[lang]["thinking"]):
        retrieval = retrieve(query)

        if should_escalate(retrieval):
            answer = escalation_message(lang)
            st.info(answer)
            _speak(answer, lang)
            with st.expander("Why was this escalated?"):
                st.caption(
                    f"No knowledge-base section matched closely enough "
                    f"(best distance = {retrieval['best_distance']}). "
                    "The assistant escalates instead of guessing."
                )
            return

        answer = generate_answer(
            query=query,
            context=retrieval["context"],
            sources=retrieval["sources"],
            language_code=lang,
            expertise=expertise,
        )

    st.success(answer)
    _speak(answer, lang)
    with st.expander("📚 Sources used (retrieved context)"):
        for s in dict.fromkeys(retrieval["sources"]):
            st.caption(f"• {s}")


def _speak(text: str, lang: str):
    """Synthesize and play the answer. Silently skip audio if TTS fails."""
    try:
        from src.tts import synthesize
        audio_bytes, mime = synthesize(text, lang)
        st.audio(audio_bytes, format=mime)
    except Exception:
        st.caption("🔇 (Voice output unavailable right now — text shown above.)")


def main():
    st.set_page_config(page_title="Natural Farming Consultant", page_icon="🌱")

    # ---- Sidebar: the three "multilevel" controls -------------------------
    with st.sidebar:
        st.header("Settings")
        lang = st.radio(
            "1. Language",
            options=list(LANGUAGES.keys()),
            format_func=lambda c: LANGUAGES[c]["name"],
            index=list(LANGUAGES.keys()).index(DEFAULT_LANG),
        )
        expertise = st.radio(
            "2. Your experience",
            options=list(EXPERTISE_LEVELS.keys()),
            format_func=lambda e: e.capitalize(),
            index=list(EXPERTISE_LEVELS.keys()).index(DEFAULT_EXPERTISE),
        )
        st.divider()
        st.caption(
            "If the assistant is unsure, it will not guess — it points you to a "
            f"human expert (Kisan Call Centre {CONTACTS['kisan_call_centre']} or your "
            "local RySS CRP)."
        )
        st.caption("Proof of concept • free-tier stack • advice is advisory.")

    _warm_collection()

    st.title(UI[lang]["title"])
    st.write(UI[lang]["tagline"])

    # ---- Voice input ------------------------------------------------------
    audio = st.audio_input(UI[lang]["speak"])
    transcript = ""
    if audio is not None:
        try:
            from src.stt import transcribe
            with st.spinner("..."):
                transcript = transcribe(audio.getvalue(), lang)
        except Exception as exc:
            st.error(f"Speech recognition unavailable ({exc}). Please type your question.")

    # Show transcript for correction BEFORE answering (trust + STT-error safety).
    typed_default = transcript if transcript else ""
    query = st.text_input(UI[lang]["type"], value=typed_default)

    if st.button(UI[lang]["ask_btn"], type="primary"):
        _answer_flow(query, lang, expertise)


if __name__ == "__main__":
    main()
