# A Story of Two — Website Design Spec

_Date: 2026-06-15 · Status: approved, building_

## Purpose

The flagship home of **A Story of Two** as a creative studio — a single
cinematic-scroll page that reads like a story and acts as the hub for the brand's
whole universe (Instagram now; podcast, YouTube, a prints/merch store, and the
app as they launch), and the front door for brand partnerships.

It is a brand/studio home, not a visitor-conversion funnel. Two audiences,
without reading like a cold media kit:

1. **Fans** — an immersive "this is us" world.
2. **Brands** — credibility at a glance (reach, shares, range, contact).

Not a generic portfolio grid. It should feel like the quiet pause between two
people who already know each other — and like a studio with a future.

## What the brand actually is (from data)

- `@a.storyof.two` — Aachu & Zuv. 11.7k followers, 61 posts.
- Bio essence: _"Relatable couple stories & everyday chaos ✨"_ · "16M+ views in 30 days."
- **Format mix:** carousels (5–9 slides), reels, photo posts. Reels are the
  reach engine — many in the millions (4.9M, 4M, 3.2M, 2.4M, 2.3M, 1.6M…).
- **Two visual languages, one soul:** real intimate photography of the couple in
  scenic places + hand-drawn watercolor-and-ink illustrations.
- **Throughline:** warm tones, generous negative space, delicate hand-set text
  floating over the image, tender _observational intimacy_, Hinglish voice.
- **Outcome signal:** shares + saves, not just likes. 12 recent carousels =
  ~3.6M reach, ~68K shares, ~36K saves; one carousel at 1.2M reach.
- **Collab funnel:** `a.storyof.two.collab@gmail.com` + Spotify playlist.

## Art direction (design system)

- **Palette:** warm ivory paper base, ink-charcoal text; accents from the house
  style — muted denim blue, faded sage, peach blush, dusty coral, warm camel.
  One dark "lamplight" section for contrast.
- **Type:** editorial serif (emotional lines) + clean humanist sans (meta/UI) +
  handwritten accent (signature moments, the `@a.storyof.two` mark).
- **Texture/motion:** subtle paper grain, soft vignettes, generous negative
  space, slow scroll reveals ("line arrives, then image"). Respect
  `prefers-reduced-motion`.
- **Signature motif:** floating hand-set text over breathing space — the brand's
  own layout idea, reused as the site's core pattern.

## Structure (one page, distinct sections)

1. **Hero** — near full-bleed warm couple photo + essence line; minimal floating nav.
2. **Aachu & Zuv** — typographic breath; 2–3 in-voice intro lines.
3. **Seen by millions — Reels** — cinematic 9:16 cards with real view badges +
   hand-typed lines, each linking to the actual reel. (Headline beat for both audiences.)
4. **The stories — Carousels** — 3–4 hero carousels with real opening lines; 1–2
   actually swipeable.
5. **The art — Illustrations** — quieter gallery wall of the watercolor work.
6. **The Studio — the universe hub** — live surfaces (Instagram, Spotify
   soundtrack) + coming-soon surfaces (Prints/Merch, Podcast, YouTube, App),
   class-driven so each lights up at launch. Signals "media brand in the making."
7. **The numbers, quietly** — followers · 16M+ views/30d · shares · saves, set
   like editorial stats, not a dashboard. (No email capture — "follow" only.)
8. **For brands** — warm confident invitation + `a.storyof.two.collab@gmail.com`.
9. **Follow / footer** — Instagram + Spotify + email + closing line + hand-set mark.

## Build & delivery

- Self-contained **static site** in `site/`: clean HTML + CSS + minimal vanilla
  JS (scroll reveals, carousel). No framework. Deployable anywhere / openable as a file.
- **Mobile-first**, responsive. Accessible: alt text, contrast, reduced-motion.
- **Copy** written in-brand (Hinglish-aware, tender, specific) via the writing skill.
- **Assets:** real local images copied + optimized into `site/assets/` from
  `references/identity`, `references/places`, `.carousel_research/`,
  `runs/*/exports/`, `references/style/best-illustration/`.

## Known constraint

No exact reel cover frame + live URL per view count yet (Apify over monthly
limit). Use real couple photos/stills as reel covers with the **real numbers**;
make covers + reel links trivial to swap later. Stat numbers are sourced from the
profile screenshot and `data/instagram/` insights as of 2026-06-15.

## Out of scope (YAGNI)

Backend, CMS, e-commerce/shop, email capture, analytics, multi-language toggle.
Structured so a shop/press-kit can slot in later without redesign.
