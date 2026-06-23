"""Generate the static room pages for the A Story of Two site from the real feed.

The deployed site stays fully static — this is a one-time authoring step that
bakes the real numbers / covers into HTML. Shared chrome (head, nav, footer) is
defined once here so every room stays consistent. Run:

    python3 scripts/build_pages.py            # build all data-driven rooms
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Our isolated dir (Codex agents own `site/`); override with ASTORY_SITE_DIR.
SITE = ROOT / os.environ.get("ASTORY_SITE_DIR", "site-studio")
FEED = json.loads((SITE / "data/feed.json").read_text())
# Cache-bust token so CSS/JS refetch after every regeneration.
BUILD = str(int(time.time()))

ROOMS = [
    ("reels", "Reels"),
    ("stories", "Stories"),
    ("memory", "Memory"),
    ("studio", "Studio"),
    ("brands", "For Brands"),
]


def human(n: int) -> str:
    if n >= 10_000_000:
        return f"{round(n / 1_000_000)}M"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 10_000:
        return f"{round(n / 1000)}K"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def first_line(caption: str) -> str:
    """First meaningful line of a caption — skip pure hashtag/emoji tails."""
    for raw in (caption or "").split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or re.fullmatch(r"[\W_]+", line):
            continue
        # drop trailing hashtags on the same line
        line = re.split(r"\s+#", line)[0].strip()
        if line:
            return line
    return ""


def head(title: str, desc: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <meta name="theme-color" content="#F3ECE0" />
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23F3ECE0'/%3E%3Cpath d='M16 24s-7-4.5-7-9.2C9 12 10.8 10.5 13 10.5c1.4 0 2.4.7 3 1.6.6-.9 1.6-1.6 3-1.6 2.2 0 4 1.5 4 4.3C23 19.5 16 24 16 24z' fill='%23C2785F'/%3E%3C/svg%3E" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..500&family=Hanken+Grotesk:wght@300;400;500;600&family=Caveat:wght@500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css?v={BUILD}" />
  <link rel="stylesheet" href="assets/illustrations/frames.css?v={BUILD}" />
  <link rel="stylesheet" href="assets/illustrations/paper.css?v={BUILD}" />
  <noscript><style>.reveal,.rise{{opacity:1 !important;transform:none !important;animation:none !important}}</style></noscript>
</head>
<body>
  <a class="skip" href="#room">Skip to content</a>
  <div class="grain" aria-hidden="true"></div>
"""


def nav(current: str) -> str:
    items = []
    for i, (slug, label) in enumerate(ROOMS, start=1):
        here = ' nav__here' if slug == current else ""
        items.append(
            f'      <a class="{here.strip()}" href="{slug}.html"><span class="n">{i:02d}</span>{label.replace(" ", "&nbsp;")}</a>'
        )
    links = "\n".join(items)
    return f"""  <header class="nav" id="nav">
    <a class="nav__mark" href="index.html">a&nbsp;story&nbsp;of&nbsp;two</a>
    <nav class="nav__links" id="navlinks" aria-label="The rooms">
{links}
    </nav>
    <div class="nav__right">
      <a class="nav__follow" href="brands.html#reach">Reach&nbsp;out</a>
      <button class="nav__toggle" id="navtoggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="navlinks">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
"""


def footer() -> str:
    return """  <footer class="footer" id="footer">
    <p class="footer__quote reveal">“maybe love isn’t finding someone calm.<br />maybe it’s finding someone patient enough<br /><em>to hold your chaos gently.”</em></p>
    <div class="footer__links reveal">
      <a href="https://www.instagram.com/a.storyof.two/" target="_blank" rel="noopener">Instagram</a>
      <a href="https://open.spotify.com/playlist/6enjAPU2P9U7MeOQPhVsCp" target="_blank" rel="noopener">Our Spotify</a>
      <a href="brands.html#reach">Collab</a>
    </div>
    <p class="footer__mark">@a.storyof.two</p>
    <p class="footer__colophon">Aachu &amp; Zuv · a story, kept gently.</p>
  </footer>
  <script src="main.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- reels room
def build_reels() -> str:
    reels = [m for m in FEED["media"] if m["kind"] == "reel" and m.get("cover")]
    by_views = sorted(reels, key=lambda r: r["views"], reverse=True)
    headliners = by_views[:8]
    total_reel_views = sum(r["views"] for r in reels)
    over_million = sum(1 for r in reels if r["views"] >= 1_000_000)

    hcards = []
    for r in headliners:
        cap = esc(first_line(r["caption"]))[:90]
        hcards.append(
            f"""        <a class="hframe reveal" href="{r['permalink']}" target="_blank" rel="noopener" aria-label="Reel — {human(r['views'])} views">
          <figure class="ill-reel">
            <span class="ill-reel__media"><img src="{r['cover']}" alt="Reel still" loading="lazy" /></span>
            <span class="ill-reel__play" aria-hidden="true"></span>
            <span class="ill-reel__ledge" aria-hidden="true"></span>
          </figure>
          <span class="hframe__cap">{human(r['views'])} views <em>{cap}</em></span>
        </a>"""
        )

    cards = []
    for r in by_views:
        cards.append(
            f"""      <a class="rcard" href="{r['permalink']}" target="_blank" rel="noopener" data-views="{r['views']}" data-shares="{r['shares']}" data-ts="{r['timestamp']}" aria-label="Reel — {human(r['views'])} views">
        <img src="{r['cover']}" alt="Reel still" loading="lazy" />
        <span class="rcard__play" aria-hidden="true"></span>
        <span class="rcard__views">{human(r['views'])}</span>
      </a>"""
        )

    return (
        head(
            "The Reels — A Story of Two",
            "The discovery engine: 69 reels, 28M+ views, 8 of them past a million. The everyday couple chaos the internet couldn't scroll past.",
        )
        + nav("reels")
        + f"""  <main id="room">
    <section class="room">
      <div class="room__intro">
        <p class="kicker reveal"><span>01</span> The Reels</p>
        <h1 class="lead lead--big reveal">The ones the internet<br /><em>couldn’t scroll past.</em></h1>
        <p class="body reveal">Funny, Hinglish, a little unhinged — the reels are how people find us. Real moments, hand-captioned, filmed between two people who actually live them. <em>“romance aur bakchodi, dono unlimited.”</em></p>
        <div class="room__stats reveal">
          <span class="room__stat"><b>{human(total_reel_views)}</b><em>views, all reels</em></span>
          <span class="room__stat"><b>{len(reels)}</b><em>reels &amp; counting</em></span>
          <span class="room__stat"><b>{over_million}</b><em>past a million</em></span>
        </div>
      </div>

      <div class="strip" aria-label="The biggest reels">
{chr(10).join(hcards)}
      </div>

      <div class="sortbar" role="group" aria-label="Sort the reels">
        <span class="sortbar__label">The full wall · {len(reels)} reels</span>
        <button type="button" data-sort="views" aria-pressed="true">Most viewed</button>
        <button type="button" data-sort="shares" aria-pressed="false">Most shared</button>
        <button type="button" data-sort="ts" aria-pressed="false">Newest</button>
      </div>
      <div class="rgrid" id="rgrid">
{chr(10).join(cards)}
      </div>
    </section>

    <div class="room__close reveal">
      <p class="body body--center">This is a slice. The whole thing keeps moving —
        <a href="https://www.instagram.com/a.storyof.two/reels/" target="_blank" rel="noopener">see every reel on Instagram&nbsp;↗</a></p>
    </div>
  </main>
"""
        + footer()
    )


# -------------------------------------------------------------- stories room
FEAT = "DZNl2zxiRD4"  # the standout: 1.6M reach, 18.8K shares, 14.8K saves
ART = [
    ("your-yellow.jpg", "Watercolor — a couple holding each other in the rain"),
    ("observational-intimacy.jpg", "Watercolor — a couple at a coastal sunset"),
    ("art-4.jpg", "Watercolor — a couple on a rooftop under stars"),
    ("art-2.jpg", "Watercolor — morning light, making tea"),
    ("art-3.jpg", "Watercolor — eating together at the table"),
    ("art-5.jpg", "Illustration — a groom smiling on the wedding day"),
]


def build_stories() -> str:
    covered = {p.stem for p in (SITE / "assets/carousels/real").glob("*.jpg")}
    cars = [m for m in FEED["media"] if m["kind"] == "carousel"]
    by_id = {m["shortcode"]: m for m in cars}
    feat = by_id[FEAT]
    feat_slides = sorted((SITE / "assets/carousels/feat").glob(f"{FEAT}_*.jpg"))
    total_saves = sum(c["saves"] for c in cars)
    total_shares = sum(c["shares"] for c in cars)

    slides = "\n".join(
        f'            <div class="carousel__slide"><img src="assets/carousels/feat/{p.name}" alt="Carousel slide {i + 1}" loading="lazy" /></div>'
        for i, p in enumerate(feat_slides)
    )

    grid_cars = [
        c for c in sorted(cars, key=lambda r: r["shares"], reverse=True)
        if c["shortcode"] in covered and c["shortcode"] != FEAT
    ][:8]
    cards = []
    for c in grid_cars:
        line = esc(first_line(c["caption"]))
        if len(line) > 64:
            line = line[:63].rstrip() + "…"
        cards.append(
            f"""        <a class="story reveal" href="{c['permalink']}" target="_blank" rel="noopener">
          <img src="assets/carousels/real/{c['shortcode']}.jpg" alt="Carousel: {line}" loading="lazy" />
          <span class="story__line">{line}</span>
          <span class="story__tag">{human(c['shares'])} shares · {human(c['saves'])} saved</span>
        </a>"""
        )

    gallery = "\n".join(
        f'        <figure class="frame reveal"><img src="assets/art/{f}" alt="{esc(alt)}" loading="lazy" /></figure>'
        for f, alt in ART
    )

    return (
        head(
            "The Stories — A Story of Two",
            "The tender carousel archive — the 'be with someone who…' lines people save and send. 17 carousels, 82K shares, 44K saves.",
        )
        + nav("stories")
        + f"""  <main id="room">
    <section class="room">
      <div class="room__intro">
        <p class="kicker reveal"><span>02</span> The Stories</p>
        <h1 class="lead lead--big reveal">Swipe-through stories<br /><em>about being loved gently.</em></h1>
        <p class="body reveal">Where the reels are loud, the carousels are quiet. Hand-drawn and hand-written, they’re the “be with someone who…” lines people don’t just like — they <strong>save them, and send them to the person they mean them about.</strong></p>
        <div class="room__stats reveal">
          <span class="room__stat"><b>{len(cars)}</b><em>carousels</em></span>
          <span class="room__stat"><b>{human(total_shares)}</b><em>shares</em></span>
          <span class="room__stat"><b>{human(total_saves)}</b><em>saves · kept, not scrolled</em></span>
        </div>
      </div>
    </section>

    <section class="sect stories" style="padding-top:clamp(48px,7vw,90px)">
      <div class="feature reveal">
        <div class="carousel" id="carousel" tabindex="0" role="group" aria-roledescription="carousel" aria-label="Featured story: Be with someone who can explain the hard parts gently. Use left and right arrow keys to navigate slides.">
          <div class="carousel__track" id="track">
{slides}
          </div>
          <button class="carousel__btn carousel__btn--prev" id="prev" aria-label="Previous slide">‹</button>
          <button class="carousel__btn carousel__btn--next" id="next" aria-label="Next slide">›</button>
          <div class="carousel__dots" id="dots" aria-hidden="true"></div>
        </div>
        <div class="feature__meta">
          <p class="feature__open">“Can I ask you<br />a question?”<span class="feature__reply">~ sure!</span></p>
          <p class="feature__say">The most-sent one we’ve made — <em>“be with someone who can explain the hard parts gently.”</em></p>
          <p class="feature__stat"><b>{human(feat['reach'])}</b> reached · <b>{human(feat['shares'])}</b> shares · <b>{human(feat['saves'])}</b> saves</p>
          <a class="feature__link" href="{feat['permalink']}" target="_blank" rel="noopener">read it on Instagram&nbsp;↗</a>
        </div>
      </div>

      <div class="storygrid">
{chr(10).join(cards)}
      </div>
    </section>

    <section class="sect art" id="art">
      <div class="sect__head">
        <p class="kicker reveal"><span>※</span> Illustrations</p>
        <h2 class="lead reveal">Hand-drawn, because some<br /><em>feelings deserve paper.</em></h2>
        <p class="sect__note reveal">The watercolor language the stories are wrapped in — and the first things headed for prints.</p>
      </div>
      <div class="gallery">
{gallery}
      </div>
    </section>

    <div class="room__close reveal">
      <p class="body body--center">There are more, every week —
        <a href="https://www.instagram.com/a.storyof.two/" target="_blank" rel="noopener">follow the stories on Instagram&nbsp;↗</a></p>
    </div>
  </main>
"""
        + footer()
    )


# --------------------------------------------------------------- memory room
MEMORY = [
    ("memory/m-01.jpg", "a hug that lasts a little too long"),
    ("memory/m-02.jpg", "chai, before the hard conversations"),
    ("memory/m-03.jpg", "the balcony we kept coming back to"),
    ("memory/m-04.jpg", "ice cream, no reason"),
    ("memory/m-05.jpg", "lost on purpose"),
    ("memory/m-06.jpg", "us, mid-laugh"),
    ("memory/m-07.jpg", "two hands, one plate"),
    ("memory/m-08.jpg", "how small the world feels up there"),
    ("photos/wedding.jpg", "the day it became official"),
    ("memory/m-09.jpg", "a quiet one"),
    ("memory/m-10.jpg", "the long talks"),
    ("memory/m-11.jpg", "still choosing each other"),
    ("photos/rocks.jpg", "somewhere along the way"),
    ("memory/m-12.jpg", "home, on an ordinary evening"),
]


def build_memory() -> str:
    snaps = "\n".join(
        f"""        <figure class="snap reveal" style="--d:{(i % 4) * 0.05:.2f}s">
          <img src="assets/{src}" alt="{esc(cap)}" loading="lazy" />
          <figcaption>{esc(cap)}</figcaption>
        </figure>"""
        for i, (src, cap) in enumerate(MEMORY)
    )
    return (
        head(
            "The Memory — A Story of Two",
            "The real-life layer: travel, home, the wedding, the ordinary days we kept. The photos behind the posts.",
        )
        + nav("memory")
        + f"""  <main id="room">
    <section class="room">
      <div class="room__intro">
        <p class="kicker reveal"><span>03</span> The Memory</p>
        <h1 class="lead lead--big reveal">The small things<br /><em>we kept.</em></h1>
        <p class="body reveal">Before any of it was content, it was just our life — the mountains we got lost in, the kitchen where the chai happens, the ordinary evenings nobody was filming. This is the layer underneath everything else: <strong>what stays, and what travels.</strong></p>
      </div>
      <div class="album" style="margin-top:clamp(44px,7vw,80px)">
{snaps}
      </div>
    </section>
    <div class="room__close reveal">
      <p class="body body--center">A life, kept gently —
        <a href="https://www.instagram.com/a.storyof.two/" target="_blank" rel="noopener">more of it on Instagram&nbsp;↗</a></p>
    </div>
  </main>
"""
        + footer()
    )


# --------------------------------------------------------------- studio room
def build_studio() -> str:
    return (
        head(
            "The Studio — A Story of Two",
            "One love story, told in every format. Instagram and a Spotify soundtrack are live; the podcast, YouTube, prints & merch, and the app are coming.",
        )
        + nav("studio")
        + """  <main id="room">
    <section class="room">
      <div class="room__intro">
        <p class="kicker reveal"><span>04</span> The Studio</p>
        <h1 class="lead lead--big reveal">One love story,<br /><em>told in every format.</em></h1>
        <p class="body reveal">A Story of Two began on Instagram. It isn’t staying there. We’re building a small studio around one idea — that <strong>ordinary love deserves to be made beautiful</strong> — across everything we make next.</p>
      </div>

      <div class="universe" style="margin-top:clamp(44px,7vw,80px)">
        <a class="uni uni--live reveal" href="https://www.instagram.com/a.storyof.two/" target="_blank" rel="noopener">
          <span class="uni__status">Live</span>
          <h3 class="uni__title">Instagram</h3>
          <p class="uni__desc">Where it all began — reels, carousels, and the everyday chaos. 33M+ views a quarter.</p>
          <span class="uni__go">Follow&nbsp;↗</span>
        </a>
        <a class="uni uni--live reveal" style="--d:.06s" href="https://open.spotify.com/playlist/6enjAPU2P9U7MeOQPhVsCp" target="_blank" rel="noopener">
          <span class="uni__status">Live</span>
          <h3 class="uni__title">The Soundtrack</h3>
          <p class="uni__desc">The songs our story is set to — a playlist on Spotify.</p>
          <span class="uni__go">Listen&nbsp;↗</span>
        </a>
        <div class="uni uni--soon reveal" style="--d:.12s">
          <span class="uni__status">Coming soon</span>
          <h3 class="uni__title">The Podcast</h3>
          <p class="uni__desc">The conversations behind the captions.</p>
          <span class="uni__go">Soon</span>
        </div>
        <div class="uni uni--soon reveal">
          <span class="uni__status">Coming soon</span>
          <h3 class="uni__title">YouTube</h3>
          <p class="uni__desc">Longer stories, in motion.</p>
          <span class="uni__go">Soon</span>
        </div>
        <div class="uni uni--soon reveal" style="--d:.06s">
          <span class="uni__status">Coming soon</span>
          <h3 class="uni__title">Prints &amp; Merch</h3>
          <p class="uni__desc">The watercolor moments — on paper you can keep, and things you can wear.</p>
          <span class="uni__go">Soon</span>
        </div>
        <div class="uni uni--soon reveal" style="--d:.12s">
          <span class="uni__status">Coming soon</span>
          <h3 class="uni__title">The App</h3>
          <p class="uni__desc">A place to keep your own story, made beautiful.</p>
          <span class="uni__go">Soon</span>
        </div>
      </div>
    </section>
    <div class="room__close reveal">
      <p class="body body--center">Want to build one of these <em>with</em> us?
        <a href="brands.html#reach">say hello&nbsp;↗</a></p>
    </div>
  </main>
"""
        + footer()
    )


# ---------------------------------------------------------------- brands room
def reachout_block() -> str:
    return """    <section class="reachout" id="reach" aria-label="Reach out">
      <div class="reachout__in">
        <p class="kicker reveal" style="justify-content:center"><span>✎</span> Let’s talk</p>
        <h2 class="lead lead--big reveal">Let’s make something that feels<br />like <em>us</em> — and like <em>you.</em></h2>
        <div class="reachout__opts">
          <a class="opt reveal" href="mailto:a.storyof.two.collab@gmail.com?subject=Collaboration%20%E2%80%94%20A%20Story%20of%20Two">
            <span class="opt__tag">brands</span>
            <h3 class="opt__title">Collaborate</h3>
            <p class="opt__desc">Sponsored reels, carousel campaigns, photo &amp; travel stories, long-term ambassadorships.</p>
            <span class="opt__go">Start a conversation&nbsp;→</span>
          </a>
          <a class="opt reveal" style="--d:.08s" href="mailto:a.storyof.two.collab@gmail.com?subject=Press%20%2F%20feature%20%E2%80%94%20A%20Story%20of%20Two">
            <span class="opt__tag">press</span>
            <h3 class="opt__title">Press &amp; features</h3>
            <p class="opt__desc">Writing about creators, couples, or new-media studios? Happy to talk.</p>
            <span class="opt__go">Get in touch&nbsp;→</span>
          </a>
          <a class="opt reveal" style="--d:.16s" href="mailto:a.storyof.two.collab@gmail.com?subject=Just%20saying%20hi%20%F0%9F%91%8B">
            <span class="opt__tag">everyone</span>
            <h3 class="opt__title">Just say hi</h3>
            <p class="opt__desc">A line about a reel that felt like you, a question, a hello. We read them.</p>
            <span class="opt__go">Say something&nbsp;→</span>
          </a>
        </div>
      </div>
    </section>"""


def build_brands() -> str:
    t = FEED["totals"]
    return (
        head(
            "For Brands — A Story of Two",
            "Proof, format range, and the recurring systems a partnership can live inside. 33M views, ~1M shares in a quarter — content that doesn't just get seen, it gets sent.",
        )
        + nav("brands")
        + f"""  <main id="room">
    <section class="room">
      <div class="room__intro">
        <p class="kicker reveal"><span>05</span> For Brands</p>
        <h1 class="lead lead--big reveal">Marketing that feels<br /><em>like real life.</em></h1>
        <p class="body reveal">We partner with a few brands we’d actually use, and build around real moments instead of a script. Here’s the honest case — not a deck, just what the work does.</p>
      </div>

      <div class="superpower ill-wash ill-wash--coral reveal">
        <p>Our content doesn’t just get <em>seen.</em><br />It gets <em>sent.</em></p>
        <span>on the biggest posts, shares rival — or beat — likes</span>
      </div>
    </section>

    <section class="reach" aria-label="The numbers">
      <div class="reach__head">
        <p class="kicker kicker--light reveal"><span>※</span> One quarter, two people</p>
        <h2 class="lead lead--light reveal">When the work is honest,<br /><em>it travels.</em></h2>
      </div>
      <div class="stats">
        <div class="stat reveal"><b data-count="{t['views'] // 1_000_000}">0</b><span>M</span><p>views</p></div>
        <div class="stat reveal" style="--d:.1s"><b data-count="{t['reach'] // 1_000_000}">0</b><span>M</span><p>accounts reached</p></div>
        <div class="stat reveal" style="--d:.2s"><b data-count="{round(t['shares'] / 1000)}">0</b><span>K</span><p>shares — it gets sent</p></div>
        <div class="stat reveal" style="--d:.3s"><b data-count="{round(t['saves'] / 1000)}">0</b><span>K</span><p>saves — it gets kept</p></div>
      </div>
      <p class="reach__foot reveal">Real numbers, pulled from the account — not estimates. <em>Updated each quarter.</em></p>
    </section>

    <section class="room" style="padding-top:clamp(80px,12vh,150px)">
      <div class="sect__head">
        <p class="kicker reveal"><span>↳</span> The range</p>
        <h2 class="lead reveal">Three formats,<br /><em>one voice.</em></h2>
      </div>
      <div class="fmts">
        <div class="fmt reveal">
          <b>28M</b>
          <h3>Reels</h3>
          <p>The reach engine. Funny, Hinglish, scroll-stopping — eight have passed a million views. Built for discovery.</p>
        </div>
        <div class="fmt reveal" style="--d:.08s">
          <b>82K</b>
          <h3>Carousels</h3>
          <p>The emotional archive. Tender, saveable, sendable — the format people forward to someone they love.</p>
        </div>
        <div class="fmt reveal" style="--d:.16s">
          <b>∞</b>
          <h3>Photo &amp; travel</h3>
          <p>The real-life layer. Warm, lived-in placement for a product, a place, or a stay — never posed, never an ad-read.</p>
        </div>
      </div>

      <div class="sect__head" style="margin-top:clamp(80px,11vw,140px)">
        <p class="kicker reveal"><span>↻</span> Recurring systems</p>
        <h2 class="lead reveal">Rituals a brand<br /><em>can live inside.</em></h2>
        <p class="sect__note reveal">Not one-off posts — repeatable formats with built-in audience expectation, so a partnership compounds instead of interrupting.</p>
      </div>
      <div class="rituals">
        <div class="ritual reveal">
          <h3>The everyday bit</h3>
          <p>One true couple moment, told in Hinglish. <em>The format that does the millions</em> — a natural home for a product that’s already part of the scene.</p>
        </div>
        <div class="ritual reveal" style="--d:.08s">
          <h3>The carousel line</h3>
          <p>A tender, illustrated “be with someone who…” story. <em>The most-saved, most-sent thing we make</em> — sentiment a brand can sit gently beside.</p>
        </div>
        <div class="ritual reveal" style="--d:.04s">
          <h3>Travel &amp; home diaries</h3>
          <p>A place, lived in — not posed in. <em>Destinations, stays, and home goods</em> woven into a real trip people actually want to take.</p>
        </div>
        <div class="ritual reveal" style="--d:.12s">
          <h3>The running joke</h3>
          <p>Chai, the 7-minute wait, “main kar lungi.” <em>Ownable rituals</em> a brand can become part of over a season — not a single placement.</p>
        </div>
      </div>
    </section>

{reachout_block()}

  </main>
"""
        + footer()
    )


BUILDERS = {
    "reels": build_reels,
    "stories": build_stories,
    "memory": build_memory,
    "studio": build_studio,
    "brands": build_brands,
}


def main() -> int:
    built = []
    for slug, builder in BUILDERS.items():
        out = SITE / f"{slug}.html"
        out.write_text(builder(), encoding="utf-8")
        built.append(str(out.relative_to(ROOT)))
    print("built:\n  " + "\n  ".join(built))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
