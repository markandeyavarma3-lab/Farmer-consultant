# Demo Script (≈ 3 minutes)

A tight walkthrough for your demo video / live presentation. Goal: show product thinking and
trust design, not just "the AI talks." Rehearse once; keep it under 3.5 minutes.

---

## Before you record (checklist)

- [ ] App deployed on Streamlit Cloud (have the live link ready) **and** running locally as backup.
- [ ] `GROQ_API_KEY` and `SARVAM_API_KEY` set in Secrets.
- [ ] Test all three demo questions once so retrieval/voice are warm.
- [ ] Quiet room, decent mic. For the *live voice* moment, **use Hindi or English** (most
      reliable STT); mention Telugu is supported and show it as text if the room is noisy.
- [ ] Have `docs/DESIGN_RATIONALE.md` open in case of questions.

## The 30-second framing (say this first)

> "Only about a third of Indian farmers get any extension advice. The Kisan Call Centre is
> human-limited and fixed-hours; most farming apps are text-heavy and English-first, and they
> sell chemicals — useless to a natural farmer. Andhra Pradesh runs the world's largest natural-
> farming programme, but a farmer with a question at night has nowhere specific to turn. So I
> built a voice assistant that gives natural-farming advice in the farmer's own language, only
> from trusted sources, and hands off to a human when it isn't sure."

## Demo beat 1 — Voice in, grounded answer out (60s)

1. Pick **Beginner + Telugu** (or Hindi). Say or type: *"How do I make Jeevamrutham?"*
2. Point out the **transcript appearing for confirmation** — "notice it shows what it heard
   before answering, because speech recognition in Indian languages isn't perfect."
3. Let it answer + **play the spoken audio**.
4. Open the **"Sources used"** expander: "every answer cites the knowledge base — it's not
   pulling this from the model's imagination."

## Demo beat 2 — The "multilevel" depth toggle (30s)

1. Switch to **Experienced**, ask the same question.
2. Point out the answer is now terse, with exact quantities — "same engine, different farmer.
   That's one of the three levels of 'multilevel' — user expertise."

## Demo beat 3 — The trust moment: escalation (45s)  ← the most important beat

1. Ask something deliberately out of scope: *"What's the market price of tomatoes today?"* or
   *"My buffalo is sick, what medicine?"*
2. Show it **refuses to guess** and returns the **human-escalation message** (CRP / Kisan Call
   Centre 1800-180-1551).
3. Say: *"This is the part I'm proudest of. A general chatbot would have made up an answer. This
   one knows the edge of its own knowledge and sends the farmer to a real person. That's the
   difference between a demo and something you could actually put in front of a farmer."*

## Demo beat 4 — Name the three "multilevels" (15s)

> "'Multilevel' here means three things: the multi-layer crop model it can teach, the multiple
> support tiers ending in human escalation, and multiple user/language levels."

## Close (15s)

> "It's a proof of concept on entirely free tools, deployed and working. It's honest about its
> limits — Telugu speech recognition and rate limits — and the design rationale doc explains
> every decision. Thank you."

---

## Likely evaluator questions — and how to answer

**"Isn't this just a ChatGPT wrapper?"**
> No — it answers only from a curated, source-cited natural-farming knowledge base via RAG, at
> low temperature, with a prompt that forbids outside knowledge and inventing quantities. A raw
> wrapper would happily hallucinate a recipe; mine escalates instead.

**"Why Sarvam and not Whisper for Telugu?"**
> An independent 2026 field benchmark on real farmer recordings found vanilla Whisper produces
> incoherent Telugu. I route English to Groq Whisper, Indic languages to Sarvam — best tool per
> language. It's a deliberate, evidence-based choice, not a default.

**"How do you stop it giving dangerous advice?"**
> Three guards: grounding (answers only from vetted context), confidence-gated escalation (no
> match → human handoff, never a guess), and honest framing (cost/risk benefits, not yield
> hype). For anything needing a field visit or pest ID it isn't sure of, it defers to a CRP.

**"What about farmers without smartphones / who can't read?"**
> Voice-first already removes the literacy barrier for *using* it. True last-mile (feature
> phones / IVR) is the honest next step in the production roadmap — I scoped it out of an
> 8-day PoC deliberately rather than fake it.

**"Does it scale?"**
> Not on free tier, and I disclose that. The upgrade path is concrete: Groq developer tier,
> Sarvam startup program, or self-hosted IndicConformer for zero-cost STT at scale.

**"Where did the farming content come from — is it correct?"**
> Curated from NITI Aayog and APCNF/RySS material, with source notes. Recipe quantities vary
> across sources, so I treat NITI Aayog figures as canonical and keep ranges where they exist —
> and the assistant always tells the farmer to confirm with a local CRP. It's advisory, by design.

**"What would you do with two more weeks?"**
> Agronomic validation of the knowledge base with RySS experts, image-based pest diagnosis, real
> CRP routing over WhatsApp/IVR, and query logging to find and fill knowledge gaps.
