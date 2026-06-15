# A Story of Two — App Prototype Design

**Date:** 2026-06-15
**Status:** Approved (brainstorm) — ready for implementation plan
**Type:** Clickable, interactive prototype with faked AI generation

---

## 1. Goal

A consumer app that turns a stranger's real love story — their photos plus a spoken
story — into a hand-drawn *A Story of Two*–style illustrated carousel. The app doubles
as a growth funnel for `@a.storyof.two`: while the art "prints," the user falls into the
brand's world and is *gently, honestly* invited to follow/like, and the finished art is
released as a gift sent to their special one (which also invites that person to the app).

**This round** builds a **clickable, interactive prototype of the full flow** with the
AI generation, transcription, and uniqueness-judging **faked/stubbed** — so we can feel
and refine the experience fast, before committing to the hard generation backend.

## 2. The bigger picture (context, not in scope here)

The real product is three pieces, to be built in order:
1. **The client app / UX flow** — this prototype.
2. **The generation + judging engine** — the hard core (real model work, moderation,
   the "is this unique / on-brand?" gate, turnaround time). *Not built here.*
3. **The growth + business layer** — real consent/privacy for strangers' photos & voice,
   the real 3-carousel cap, real referral attribution, real engagement integration.
   *Not built here.*

This repo today is a **studio production pipeline** for one specific couple (Aachu & Zuv)
with locked identity references and human-in-the-loop gates. Generating on-brand
illustrations of *strangers*, fast, judged automatically, is a fundamentally different and
harder problem — it is the make-or-break of the real product and is deliberately faked in
this prototype.

## 3. Locked decisions

- **Fidelity:** clickable interactive prototype; AI faked. (Not a shippable app, not a
  spec-only deliverable.)
- **Identity:** no login. A silent **device-id** tracks the max-3-carousels cap. Instead of
  a form, a warm conversational capture: *"Are you here with your special one, or sending
  them something from afar?"* + first names (creator + partner). The whole app then speaks
  to them **by name**; identity becomes intimacy, not friction.
- **Faked output:** at the reveal, slides are **their story rendered in the house style** —
  a small set of pre-drawn generic-couple illustrations in the exact A Story of Two style
  (paper, line art), captioned live with the couple's names and their "recorded" story
  beats. Honest (not literally Aachu/Zuv's portraits) and convincing (real house craft).
- **The wait = a mixed journey:** Phase 1 the brand voice greets them by name → Phase 2 a
  short story/letter to read → Phase 3 opens into a swipeable feed of real carousels/reels
  they can like + follow from. The follow/like ask appears **once**, in the brand's honest
  "papi pet" voice, and is fully dismissable. Never nags.
- **Unlock = the gift (step 9):** sending the carousel to your special one **is** the
  referral. One primary act — *"Send it to [name]"* — releases the art and carries an
  A Story invite in the shared message. No separate "refer a friend" chore.
- **Send-only output (step 10):** no copy/download button anywhere. The send act opens a
  surface offering **WhatsApp send · WhatsApp status · Instagram story · set as wallpaper
  (mobile/desktop)**. All share, never save.

## 4. Build approach

**Phone-shaped web prototype** — React + Vite, deployable to a URL, rendered inside a
phone frame, runs in any browser.
- Real swipe/scroll gestures, CSS / Framer-Motion animations, real mic capture (Web Audio),
  a real share surface (Web Share API where available, simulated otherwise).
- **Why:** fastest path to "feel it working," instantly shareable by link, reuses the web
  competence already in `site/`.
- **Rejected alternatives:** Expo/React Native (more "real app" feel, but slower iteration
  and overkill while AI is faked); pure static HTML/CSS/JS (too unwieldy across ~10 stateful,
  animated screens).

## 5. The flow, screen by screen

1. **Landing — the paper page.** Blank, warm paper texture. A single `+` button (center)
   with a hand-drawn arrow + line: *"say your story, get it illustrated."* A small,
   tappable **disclaimer**: *"We may post your story on A Story of Two. If it's unique and
   our agent loves it, you'll get your illustrated carousel. Max 3 per person."*
2. **The warm hello.** *"Are you here with your special one — or sending them something from
   afar?"* + first names (you / them). Silent device-id begins tracking the 3-cap.
3. **Choose your photos.** Multi-select from a (simulated) gallery. No camera/photo
   *permission* screen, since the user is the one picking. Select several.
4. **Your photos, together.** Chosen photos sit in a **horizontal-scroll strip of
   rounded-rectangle cards.** Below: a **mic** with the same arrow + line: *"record your
   story — we draw from your voice."*
5. **Tell your story.** Large mic, real audio capture, animated waveform, a gentle prompt.
   (Transcription is faked.)
6. **While it prints — the mixed wait.** Hand-drawn "printing" animation. Phase 1: brand
   voice greets by name. Phase 2: a short story/letter to read. Phase 3: opens into a
   swipeable feed of real carousels/reels to like + follow from. Follow/like ask shown
   **once**, honest, dismissable. Believable simulated timing.
7. **The reveal.** Their carousel — real A Story house-style illustrations, captioned live
   with their names + story beats. Swipeable, soft entrance animation.
8. **Rate us.** A light, lovely rating moment.
9. **Unlock = the gift.** Single primary button *"Send it to [name]."* Firing it releases
   the art and carries an A Story invite in the shared message — the send is the referral.
10. **Send-only output.** No copy/download. The send surface offers **WhatsApp send ·
    WhatsApp status · Instagram story · set as wallpaper (mobile/desktop).** All share.

## 6. Cross-cutting decisions

- **Faked seams:** the "agent" always loves the story (happy path); transcription,
  uniqueness-check, and generation are simulated with believable timing/animation.
- **Brand / voice:** paper texture, hand-drawn line art, existing A Story illustration
  assets; copy in the A Story voice — intimate, honest, never corporate.
- **3-cap:** silent, device-local; a gentle *"you've made your three"* state.
- **Names everywhere:** captured names personalize prompts, the wait, the reveal captions,
  and the final "Send it to [name]."

## 7. Out of scope (deliberately, for now)

Real generation; real moderation / uniqueness judging; real accounts; payments; live
Instagram/WhatsApp APIs (the prototype uses the device share surface or simulates it); the
*"your story wasn't selected"* rejection path (noted for production — the prototype assumes
the happy path where the agent always loves the story).

## 8. Open questions for production (not blocking the prototype)

- How is "uniqueness" actually judged, and what does a rejection feel like with grace?
- Real consent/privacy handling for strangers' photos and voice recordings.
- Real cross-device 3-cap and referral attribution.
- Generation turnaround time and its effect on the wait experience.
