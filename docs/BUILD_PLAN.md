# 8-Day Build Plan (June 12 → June 20)

You are starting **June 12**; submission is **June 20** with subject line
`Markandeya Varma Gottumukkala | AI Assignment`. You're fully free, so this plan front-loads
the risky parts (voice + Telugu STT) so you discover problems early, not the night before.

> The codebase in this repo already gives you Days 1–3 done. This plan is how to take it from
> "runs on my laptop" to "deployed, tested, demoed, defensible."

---

## Day 1 (Thu, Jun 12) — Get it running locally
- [ ] Create free **Groq** key (console.groq.com) and **Sarvam** key (dashboard.sarvam.ai).
- [ ] `pip install -r requirements.txt`; copy `.env.example` → `.env`, add both keys.
- [ ] `python scripts/build_index.py` → confirm "Indexed 37 chunks".
- [ ] `streamlit run app.py`. Type a question in English → confirm grounded answer + sources.
- **Goal:** text-mode RAG answers working end-to-end. (Voice comes next.)

## Day 2 (Fri, Jun 13) — Voice loop + the Telugu risk, early
- [ ] Test `st.audio_input` mic capture in the browser.
- [ ] Record yourself asking a question in **English** → confirm Groq Whisper transcribes.
- [ ] Record in **Hindi** and **Telugu** → check Sarvam transcripts. **This is the critical
      experiment.** Note the word-error you see.
- [ ] Confirm TTS plays back (Sarvam, and force the gTTS fallback once to be sure it works).
- **Decision gate:** if Telugu STT is unusable on your voice/accent, make **Hindi** the primary
  demo language (English/Hindi STT are stronger) — Telugu stays supported, demoed via text.

## Day 3 (Sat, Jun 14) — Knowledge base polish + grounding quality
- [ ] Re-read all 7 KB docs; fix anything you can verify against naturalfarming.niti.gov.in.
- [ ] Add 1–2 more docs if you find gaps (e.g. specific crops common around Eluru: paddy, maize).
- [ ] Rebuild the index. Ask 15–20 varied questions; note any wrong or ungrounded answers.
- [ ] Tune `MAX_DISTANCE_FOR_CONFIDENCE` in `config.py` so good questions answer and junk
      questions escalate. **Test the escalation path explicitly.**

## Day 4 (Sun, Jun 15) — The three "multilevel" features, verified
- [ ] Beginner vs Experienced: confirm answer depth actually changes.
- [ ] All three languages answer in the right language.
- [ ] Five-layer / ATM model questions return the cropping-model content.
- [ ] Escalation message reads correctly in Telugu and Hindi (get a friend to sanity-check the
      Telugu, or read it aloud).

## Day 5 (Mon, Jun 16) — UX for real farmers + robustness
- [ ] Large, clear buttons; make sure transcript-confirmation step is obvious.
- [ ] Handle empty input, mic-denied, API-down gracefully (the code does — verify the messages).
- [ ] Force a Groq rate-limit / bad-key situation once → confirm fallback + friendly error.
- [ ] Make the sidebar caption about escalation and "advice is advisory" visible.

## Day 6 (Tue, Jun 17) — Deploy
- [ ] Push to a clean **public GitHub repo** (check `.gitignore` kept your `.env` out!).
- [ ] Deploy on **Streamlit Community Cloud**, add keys in Secrets.
- [ ] Confirm the index auto-builds on first load and voice works on the deployed URL
      (test on your phone — that's the real device).
- [ ] Fix any cloud-only issues (memory, cold start). If embeddings are too heavy, you're
      already on the small MiniLM model; that should fit.

## Day 7 (Wed, Jun 18) — Demo video + dry run
- [ ] Follow `docs/DEMO_SCRIPT.md`. Record a 3-minute screen capture: voice in → grounded
      answer → depth toggle → **escalation moment** → name the three multilevels.
- [ ] Re-record once if rushed. Keep it under 3.5 min.
- [ ] Read the evaluator-questions section aloud until you can answer each smoothly.

## Day 8 (Thu, Jun 19) — Polish & submit (one day early)
- [ ] Final README pass; make sure the live link + repo link are at the top.
- [ ] Skim `DESIGN_RATIONALE.md` — it's your written "product thinking" proof.
- [ ] Submit email: subject **`Markandeya Varma Gottumukkala | AI Assignment`**, include the
      **live demo link, GitHub link, and the 3-min video** (or video link).
- [ ] Keep Jun 20 as buffer for anything that breaks.

---

## What "done" looks like
A deployed, working voice assistant in 3 languages that answers natural-farming questions from a
cited knowledge base, changes depth by user level, knows the five-layer cropping model, and
escalates to a human when unsure — plus a GitHub repo, a 3-minute demo, and a design-rationale
doc that explains every choice. That is a top-decile submission for an 8-day NGO PoC.

## If you fall behind — cut in this order
1. Drop **Telugu voice**, keep Telugu **text** + Hindi/English voice. (Biggest risk, first to cut.)
2. Drop the Beginner/Experienced toggle (keep one good default depth).
3. Drop TTS, keep STT + on-screen answer. (Still "voice-enabled" via input.)
**Never cut:** grounded RAG + source citation + human escalation. Those are the whole point.
