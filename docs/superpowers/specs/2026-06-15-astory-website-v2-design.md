# A Story of Two — Website v2 Design Spec ("The World")

_Date: 2026-06-15 · Status: approved, building · Supersedes
[v1](2026-06-15-astory-website-design.md)._

## Purpose

The brand home and digital studio for **A Story of Two** (Aachu & Zuv) — a
story-world you *enter*, not a landing page. It answers the question Instagram
can't: _what is A Story of Two as a brand, a universe, a studio, and a future
platform?_ It houses everything now (reels, carousels, photos) and reserves
space for everything next (podcast, YouTube, store, app), and is the warm front
door for both **brands reaching out** and **fans reaching out**.

## Positioning (decided)

**Immersive fan-world first, proof felt not sold.** The brand is made to feel
bigger than Instagram by pulling people *deeper into the world*, not by pitching.
Brands are convinced the way a great film convinces — by the quality of the world
they're standing in. Reach/range/systems are present, woven into the experience,
never a deck.

## Audiences → Jobs (product POV)

- **Brand / agency / platform** — "Is this real, safe, effective? What can we
  build together? How do I reach you?" → needs proof, format range, recurring
  systems, brand-fit, an easy reach-out.
- **Fan / new visitor** — "I love this — more of this world, follow, future
  products, can I say hi?" → needs the world, follow, future-surface signups, a
  warm contact.
- **Collaborator / future buyer** — "What is this universe and where is it
  going?" → needs the studio vision + roadmap.

## The data study (first-party Graph API, pulled 2026-06-15)

The design is grounded in a full first-party pull of the account, not
assumptions. Apify was over its monthly hard limit; the owned-account Graph API
(token live) gave better data. Stored in `data/instagram/account_inventory.json`
(+ `scripts/instagram_pull_account.py`).

- **87 media** total (not the 61 v1 assumed), **reels-dominant**: 69 reels (79%)
  · 17 carousels · 1 photo. **Reels are the discovery engine.**
- **Young and exploding:** all from ~Mar 20 → Jun 15 2026, ramping 10 → 28 → 35
  posts/month. A rocket, not a back-catalog.
- **Proof (lifetime of pulled media, one quarter):** **33.1M views · 23.7M reach
  · ~993K shares · 194K saves.** 8 reels over 1M views (max ≈ 5.0M). 22 posts
  cleared 5K+ shares.
- **The killer stat — shares rival/beat likes** (content is *sendable*, the
  brand's whole thesis): reel "me threatening to leave" = 171K likes / **145K
  shares**; carousel "…didn't marry a calm girl" = 20K likes / **21K shares**.
- **Format–voice split (the creative spine):** reels = funny, Hinglish, chaotic,
  relatable (reach + virality, 28.5M views / 911K shares); carousels = tender,
  "be with someone who…" wisdom (highest save-rate; standout "explain the hard
  parts gently" = 1.6M reach / 18.8K shares / 14.8K saves).

## Structure (decided): a multi-room world you navigate

Not a single page and not a site-map. A **hub that opens into rooms**, each its
own **immersive long-scroll reveal** (NO full-bleed photo hero anywhere).
Connected by one design language and a hand-drawn **"world map" / index**
navigation; moving between rooms feels like turning to a new chapter. Built as
**multiple static HTML pages** sharing one design system, so it's fast,
deployable anywhere, and future rooms (store, app, YouTube) slot in as *states*,
not rebuilds.

### The entry (`index.html` — the hub)

No hero image. You land on warm paper; the brand **assembles** through motion —
the mark, the essence line building word by word, a handwritten margin note. As
you scroll, the world reveals in layers: a torn-paper edge slides back to a
single silently-playing reel in a small frame; the proof whisper counts up (33M
views · ~1M shares); then the **doorways draw themselves in** as an illustrated
index of the rooms. Photos appear as fragments/polaroids within the scroll,
never one big bleed.

### The rooms (each an immersive long-scroll)

1. **The Reels** — discovery engine. Real reel covers (first-party
   `thumbnail_url`) + **real view counts** + real per-reel links. The 8 reels
   over 1M featured big; all 69 as a browsable wall, sortable (most viewed / most
   shared / newest). Top few may use live Instagram embeds. Funny/Hinglish voice.
2. **The Stories** — the tender carousel archive. Real swipeable carousels (12
   with slides on hand), opening lines, reach/shares/**saves** shown quietly.
   The watercolor **illustration gallery** lives here as the emotional wrapper.
3. **The Memory** — the real-life photo layer: travel, home, the wedding, the
   ordinary (~47 real photos from `references/identity` + `references/places`).
   Album/paper feel — what stays, what travels.
4. **The Studio** — the universe + future. Live (Instagram, Spotify) +
   coming-soon (Podcast, YouTube, Prints/Merch, App), class-driven to light up at
   launch. A media brand in the making.
5. **For Brands** — partnership front door as **story, not deck**: the share-rate
   superpower, 33M views / ~1M shares, format range, recurring content systems &
   brand-fit rituals, why collabs live naturally inside the world. Press-kit
   substance, warm tone. Reach out.

_(Memory may fold into Home/Stories for a leaner 5-room first cut if needed.)_

## Reach-Out system (serves brands AND fans)

One warm door, **intent-routed**: Collaborate / Just say hi / Press. Default
implementation = smart prefilled contact (mailto with per-intent subject) to
`a.storyof.two.collab@gmail.com`, structured so a real captured form (and
store/app **"notify me"** waitlist) drops in later without redesign.

## Design system (the connective tissue)

- **Palette:** warm ivory paper base, ink-charcoal text; house accents — muted
  denim blue, faded sage, peach blush, dusty coral, warm camel. One dark
  "lamplight" mode for emotional beats.
- **Type:** Fraunces (editorial serif, emotional lines) + Hanken Grotesk
  (humanist sans, meta/UI) + Caveat (handwriting, signature moments).
- **Texture/motion:** paper grain, torn-paper layers, handwritten margin notes,
  illustrated motifs, choreographed scroll reveals ("line arrives, then image"),
  chapter-turn room transitions. Honors `prefers-reduced-motion`.
- **Aesthetic POV:** editorial paper-archive / storybook — distinctive, never
  templated. Reuse + elevate v1's `styles.css` / `main.js`.
- **Components (reusable):** room shell + map nav, doorway card, proof stat,
  reel cover card, carousel, polaroid/album frame, universe (live/soon) card,
  reach-out block. Content driven by the real data where possible.

## Build & delivery

- Static multi-page site in `site/`: `index.html` (hub) + `reels.html`,
  `stories.html`, `memory.html`, `studio.html`, `brands.html`. Shared
  `styles.css` + `main.js`. Framework-free, no build step. Deployable anywhere.
- **Mobile-first**, responsive, accessible (alt text, contrast, keyboard,
  reduced-motion), fast (lazy media, no heavy deps).
- Reel walls / stories / proof generated from `data/instagram/account_inventory
  .json` (numbers baked into static markup — real, no live fetch).
- **Asset plan:** pull reel cover frames first-party (`thumbnail_url`) →
  optimize into `site/assets/reels/`; carousel slides from `.carousel_research/`;
  Memory photos curated from `references/`; illustrations from
  `references/style/`. No Instagram CDN hot-linking (URLs expire).

## Out of scope (YAGNI)

Backend/CMS, live e-commerce, analytics, multi-language. Real form-capture and
store/app waitlist are *structured for* but not built now. Future rooms slot in
as class-driven states.
