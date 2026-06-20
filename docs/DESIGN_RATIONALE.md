# Design Rationale

*Why this assistant is built the way it is. Written for the evaluators at Connecting Dreams
Foundation — this is the "show your thinking" document.*

---

## 1. The problem I chose to solve (and the one I refused to)

The easy version of this assignment is "connect an LLM to a microphone and let it answer
farming questions." I deliberately did not build that, for one reason: **a general LLM
confidently inventing fertiliser quantities or pesticide recipes is actively dangerous to a
farmer.** A wrong Jeevamrutham ratio wastes a week of fermentation; a wrong pesticide call can
lose a crop. So the real problem isn't "can the AI talk" — it's **"can the AI be trusted, in
the farmer's language, and know when to shut up and fetch a human."**

Everything below follows from that.

## 2. Why grounded RAG, not raw LLM knowledge

The assistant answers **only** from a curated knowledge base of seven source-noted documents
built from NITI Aayog (naturalfarming.niti.gov.in) and APCNF/RySS material — the nine
principles, the four ZBNF pillars, exact Jeevamrutham/Beejamrutham recipes, the three pest
"astras," the five-layer cropping model, the seasonal/PMDS calendar, and a transition FAQ.

The system prompt (`src/prompts.py`) hard-forbids using outside knowledge or inventing
quantities, runs at low temperature (0.2), and every answer carries a **source citation**.
This is what makes it "a thoughtful engineer's tool," not a ChatGPT wrapper.

## 3. The three meanings of "Multilevel" — answered, not dodged

The brief says "Multilevel" without defining it. Rather than pick one reading and hope, I built
for all three, because each maps to a real farmer need:

| Level | Meaning | Where it lives |
|-------|---------|----------------|
| **Cropping layers** | Palekar five-layer / APCNF A-Grade, ATM, 365-DGC models | `knowledge_base/05_five_layer_model.md` |
| **Support tiers** | self-serve → RAG answer → **human escalation** | `src/escalation.py`, confidence threshold in `config.py` |
| **User levels** | Beginner vs Experienced depth + Telugu/Hindi/English | sidebar toggles in `app.py`, `build_answer_prompt()` |

If an evaluator asks "what does multilevel mean?", I can defend a complete, layered answer.

## 4. Why these specific free-tier technology choices

- **Sarvam for Telugu/Hindi STT, NOT vanilla Whisper.** An independent Feb-2026 field
  benchmark on real FarmerChat recordings found OpenAI Whisper produced *incoherent* Telugu
  output. Sarvam has the best agriculture-term accuracy among free options. I route English to
  **Groq Whisper** (where it's excellent) and Indic languages to Sarvam. This single routing
  decision is the difference between a demo that works and one that embarrasses you on stage.
- **Groq Llama 3.3 70B with an 8B fallback.** 70B for answer quality; the code automatically
  drops to `llama-3.1-8b-instant` if the 70B daily limit is hit mid-demo — a small robustness
  detail that matters when you have one shot in front of judges.
- **ChromaDB + multilingual MiniLM embeddings.** Local, free, and cross-lingual: a Telugu query
  can match an English knowledge base, so I maintain one clean English corpus instead of three.
- **Streamlit Community Cloud.** Its native `st.audio_input()` mic widget is the single biggest
  reason a *voice* app is feasible in 8 days with zero front-end plumbing.
- **gTTS fallback.** If Sarvam credits run dry, spoken output still works with no key. The demo
  never goes fully silent.

## 5. Trust & safety design (the part NGOs care about most)

1. **Show the transcript before answering.** STT on low-resource languages is imperfect, so the
   recognised text is always displayed and editable — the farmer (or demo operator) confirms it
   before the assistant commits to an answer. No silent misunderstandings.
2. **Confidence-gated human escalation.** If no knowledge-base chunk matches closely enough
   (cosine distance threshold in `config.py`), the assistant does **not** generate — it returns
   a localised message pointing to the village RySS CRP or Kisan Call Centre (1800-180-1551).
   This mirrors Digital Green's Farmer.Chat, which deliberately kept a human in the loop.
3. **Source citation on every answer.** The farmer can see *where* advice came from.
4. **Honest benefit framing.** The knowledge base and prompt steer toward natural farming's
   well-evidenced benefit — **lower cost and risk** — and away from contested yield claims.
5. **No off-topic answers.** The prompt redirects anything unrelated to farming.

## 6. What I consciously left out of scope (and why)

- **Image-based pest diagnosis** — high value, but adds a vision model and a whole new failure
  mode; out of scope for an 8-day voice PoC. Noted as a future step.
- **User accounts / history / farm profiles** — real product needs them; a PoC doesn't, and
  they'd eat days better spent on the voice loop and grounding quality.
- **Self-hosted IndicConformer STT** — zero ongoing cost and fine-tunable, but heavier to host;
  Sarvam's managed free tier is the faster path for a demo. The architecture can swap to it.
- **Production scale** — free-tier rate limits are accepted, disclosed, and have a clear upgrade
  path (Groq developer tier, Sarvam startup program).

## 7. How I'd take this to production (the honest roadmap)

1. Replace Sarvam free tier with a fine-tuned self-hosted IndicConformer for cost-free scale.
2. Expand and **agronomically validate** the knowledge base with RySS/KVK experts; version it.
3. Add a real escalation *routing* layer that connects to actual CRPs (WhatsApp/IVR), not just a
   phone number — deployed as an assistant *to extension workers* first, as Farmer.Chat did.
4. Add offline/IVR access for farmers without smartphones (the genuinely hard last-mile problem).
5. Log queries (with consent) to find knowledge gaps and improve retrieval.

## 8. One-line summary for the evaluator

> A voice assistant that knows real natural-farming practice, speaks the farmer's language,
> cites its sources, and is honest enough to hand off to a human when it isn't sure — built on
> free tools, in eight days, as a faithful proof of concept.
