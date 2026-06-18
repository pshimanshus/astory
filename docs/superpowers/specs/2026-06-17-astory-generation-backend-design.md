# A Story of Two — Generation Backend v1 (Automated) — Design Spec

**Date:** 2026-06-17
**Status:** Design for review → implementation plan
**Branch:** `astory-gen-backend`

---

## 1. Goal

When the app sends a submission (photos + voice + the user's choices), a **real backend automatically fires the studio's agent + image-generation pipeline** and delivers a finished A Story of Two–style illustrated carousel back to the app. **Fully automated — no human in the loop, no concierge/man-in-the-middle step.** This is the engine that replaces the prototype's faked generation.

## 2. Hard constraints (from the product owner)

- **OpenAI API is approved for go-live** (account exists) — used for the one piece worth paying for: **image rendering**.
- **Everything else must use FREE models.**
- **No Anthropic/Claude API anywhere.**

## 3. Model stack (locked)

| Job | Provider | Notes |
|-----|----------|-------|
| Image rendering | **OpenAI `gpt-image-1`** | Paid (their account). Closest to the validated "imagegen" look; native portrait output. |
| Voice → text | **Gemini 2.5 Flash (free tier)** | Multimodal audio input; free. |
| Agent reasoning (winner-bank match, prompt + caption build) | **Gemini 2.5 Flash (free tier)** | Free; strong enough for structured creative reasoning with the winner-bank as context. |
| Vision QA (house-style / brandmark / text checks) | **Gemini 2.5 Flash (free tier)** | Multimodal vision; free. |

All non-image model calls go through a single **`LLMProvider` interface** and the renderer through a **`Renderer` interface**, so any provider can be swapped without touching pipeline logic. No Anthropic SDK is added to the project.

## 4. Architecture

```
 App (React)                Backend (FastAPI + worker)                 External
 ───────────                ──────────────────────────                 ────────
 submit ───────POST /jobs──▶ job store (queued)
   │                          │
   │                          ▼  async worker picks up job
   │                       ┌─ 1. transcribe (Gemini) ◀──────────────── voice clip
   │                       ├─ 2. understand + winner-bank match (Gemini, winner_bank.json + dumps)
   │                       ├─ 3. build slide prompts + on-image text (Gemini, house-style/imagegen contracts)
   │                       ├─ 4. render N slides (OpenAI gpt-image-1) ◀ style refs (+ optional setting photo)
   │                       ├─ 5. vision QA + bounded retry (Gemini)
   │                       └─ 6. assemble carousel + brandmark → store outputs
   │                          │
   ◀──poll GET /jobs/{id}─────┘ status: queued→running→ready|failed
 reveal + send (existing UI)
```

- **Service:** Python **FastAPI** + an async **worker** (in-process background task for v1; queue-backed later). One job = one carousel.
- **Store:** a job table + object storage for inputs (photos, audio) and outputs (slides). v1 default: local Postgres/SQLite + local/object filesystem; swappable to a managed store. *(Hosting target is an open assumption — see §13.)*
- **App contract:** `POST /jobs` (multipart: photos[], audio, names, relationship, setting-choice, quote-choice/copy, device-id, delivery-contact) → `{jobId}`. `GET /jobs/{id}` → `{status, slides?[], error?}`. The existing **printing screen becomes the poller**: animate while `running`, reveal on `ready`. Jobs target ~1–3 min so it stays in-session; if a job runs long, fall back to notifying the delivery contact.

## 5. Pipeline stages (the worker job)

1. **Transcribe** the voice clip → story text (Gemini audio).
2. **Understand + match** — Gemini reads the story + names + relationship, classifies it against **`references/text-style/winner-bank/winner_bank.json`** + the content dumps + real winner posts in `data/instagram/carousel_posts/`, and selects the winning pattern + slide-beat structure.
3. **Build prompts** — Gemini produces, per slide: the `gpt-image-1` prompt (grounded in the house-style + imagegen contracts), and the on-image text — **the user's own quote copy if they supplied it, agent-written if they asked, or none for a text-free illustration**. Honors the **setting choice**: if the user wants their setting retained, their photo is passed to the renderer as a composition/setting reference; otherwise the setting is generated.
4. **Render** — for each slide, call **OpenAI `gpt-image-1`** with the prompt + brand house-style reference image(s) + optional setting photo + the `@a.storyof.two` brandmark instruction, at native portrait size.
5. **Vision QA + retry** — Gemini vision checks each slide against the QA rubric (house-style fidelity, brandmark present, on-image text correct, no obvious artifacts). On failure, targeted prompt repair and retry (bounded, mirroring the studio retry rule); if it can't pass after the cap, the slide/job is marked `failed` with a reason rather than shipping something off-brand.
6. **Assemble** — order the slides into the carousel, persist outputs, set job `ready`.

This v1 pipeline **reuses the studio's assets and rules** — the winner bank, the house-style contract, the imagegen contract, the QA rubric — fed as context/system-instructions into the Gemini agent calls. It is a focused **headless pipeline**, not a literal runtime port of the 33-state human-in-the-loop orchestrator (that machine is interactive-shaped; porting it wholesale is deferred). For strangers we use **house-style rendering with optional setting reference, not face-identity anchors** — the studio's Aachu/Zuv identity-lock path does not apply.

## 6. Reuse vs. build

- **Reuse:** `winner_bank.json` + content dumps + real winner posts; house-style + imagegen contracts (as prompt context); the QA rubric; the entire React app UI.
- **Build new:** the FastAPI service + worker; the `LLMProvider` (Gemini) and `Renderer` (OpenAI) adapters; the matcher, prompt-builder, QA-checker modules; the job store + storage; app↔backend wiring + the polling printing screen; the delivery-contact capture; config/secrets handling.

## 7. App changes (frontend)

- Replace faked generation with a real `POST /jobs` (uploads photos + audio + choices).
- Add a **delivery contact** capture (email or WhatsApp) — needed for the long-job fallback.
- Add **setting** ("keep your setting?") and **quote** ("your words / we'll write it / no text") choices to the flow.
- Printing screen polls `GET /jobs/{id}` and reveals the real carousel on `ready`; rate + send-only flow unchanged.
- Surface a graceful `failed` state ("our agent couldn't quite draw this one — try another story").

## 8. Data model

`jobs`: `id`, `device_id`, `delivery_contact`, `creator_name`, `partner_name`, `relationship`, `setting_choice`, `quote_mode` (`own`|`agent`|`none`), `quote_copy?`, `status` (`queued`|`running`|`ready`|`failed`), `story_text?`, `matched_pattern?`, `slides?` (ordered list of stored image refs + captions), `error?`, `created_at`, `updated_at`. Inputs (photos, audio) and outputs (slides) live in object storage keyed by `job_id`.

## 9. Error handling

- Transcription failure → retry once → `failed("could not hear the story")`.
- Render failure / rate-limit (OpenAI) → exponential backoff, bounded retries.
- **Gemini free-tier rate limits** → backoff + a small concurrency cap on the worker; surface `running` longer rather than erroring.
- QA can't pass after retry cap → `failed` with reason (never ship off-brand).
- Job exceeds time budget → notify delivery contact; deliver async.

## 10. Testing strategy

- **Unit:** matcher (story → winning pattern, against a fixture bank), prompt-builder (choices → prompt + on-image text, incl. own/agent/none quote modes and setting on/off), `LLMProvider` + `Renderer` adapters (HTTP mocked), QA-result parser, job state machine.
- **Integration:** a full job end-to-end with **mocked** providers (deterministic), asserting `queued→running→ready` and a well-formed carousel.
- **Live smoke (manual, gated):** one real job through real OpenAI + Gemini, behind an env flag, not in CI.

## 11. Honest caveats

- **House-style fidelity without a fine-tune:** prompt + reference conditioning on `gpt-image-1` plus the QA-retry loop gets *close*, not necessarily pixel-identical to the hand-drawn studio look on day one. If fidelity falls short, v2 adds a fine-tuned model (the GPU/training step deferred earlier).
- **Gemini free tier:** has rate limits and data-usage terms (free-tier inputs may be used by Google to improve products) — relevant because submissions are personal. Mitigation: it's swappable behind `LLMProvider`; we can move agent reasoning to a paid/private tier or local model if limits or privacy bite.

## 12. Out of scope (v2)

Fine-tuned house-style model; hardened uniqueness-judge + automated moderation as coded gates (v1 does light inline LLM checks); horizontal scale / managed queue; payments; the website work.

## 13. Resolved decisions (confirmed 2026-06-17)

- **Hosting:** backend runs on the owner's machine / a small VPS for the soft launch (FastAPI + local store); migrate to managed hosting once proven. Affects deploy + secrets, not the core code.
- **Gemini free tier:** accepted for launch over users' personal stories; it stays swappable behind `LLMProvider`, and the agent-reasoning piece moves to local/paid if rate limits or data-usage terms become a problem.
- **Slides per carousel:** 3–5, decided per story by the matcher.
- **Turnaround:** target ~1–3 min so the reveal stays in-session; longer jobs fall back to notifying the delivery contact.
