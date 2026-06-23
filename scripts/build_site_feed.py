"""Build the canonical site feed for the website from the first-party pulls.

Merges ``account_inventory.json`` (per-post insights) with
``account_inventory_list.json`` (cover URLs) by media id, downloads real reel
cover frames into ``site/assets/reels/real/<shortcode>.jpg`` (optimized via
``sips`` when available), and writes ``site/data/feed.json`` — the single source
the static pages read from (numbers are baked into markup at build time; this
file is the provenance + a convenience for regeneration).

Usage:
    python3 scripts/build_site_feed.py [--no-download]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
INSIGHTS = ROOT / "data/instagram/account_inventory.json"
COVERS = ROOT / "data/instagram/account_inventory_list.json"
REEL_COVER_DIR = ROOT / "site/assets/reels/real"
FEED_OUT = ROOT / "site/data/feed.json"
COVER_WIDTH = 640  # 9:16 web covers

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def _num(value: object) -> int:
    return value if isinstance(value, (int, float)) else 0


def download(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    try:
        request = Request(url, headers={"User-Agent": UA})
        with urlopen(request, timeout=30) as response:
            data = response.read()
        dest.write_bytes(data)
    except Exception as error:  # noqa: BLE001 - best effort, log and continue
        print(f"  ! cover failed {dest.name}: {error}")
        return False
    if shutil.which("sips"):
        subprocess.run(
            ["sips", "--resampleWidth", str(COVER_WIDTH), str(dest)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the site feed from first-party pulls.")
    parser.add_argument("--no-download", action="store_true", help="Skip cover downloads.")
    args = parser.parse_args(argv)

    insights = {m["id"]: m for m in json.loads(INSIGHTS.read_text())["media"]}
    covers = {m["id"]: m for m in json.loads(COVERS.read_text())["media"]}
    REEL_COVER_DIR.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    downloaded = 0
    for media_id, base in covers.items():
        ins = (insights.get(media_id) or {}).get("insights", {})
        shortcode = base.get("shortcode")
        is_reel = base.get("media_product_type") == "REELS"
        cover_path = None
        if is_reel and shortcode and base.get("thumbnail_url"):
            dest = REEL_COVER_DIR / f"{shortcode}.jpg"
            if not args.no_download and download(base["thumbnail_url"], dest):
                downloaded += 1
            if dest.exists():
                cover_path = f"assets/reels/real/{shortcode}.jpg"

        records.append(
            {
                "shortcode": shortcode,
                "permalink": base.get("permalink"),
                "kind": "reel" if is_reel else ("carousel" if base.get("media_type") == "CAROUSEL_ALBUM" else "photo"),
                "timestamp": base.get("timestamp"),
                "caption": (base.get("caption") or "").strip(),
                "likes": _num(base.get("like_count")),
                "comments": _num(base.get("comments_count")),
                "views": _num(ins.get("views")),
                "reach": _num(ins.get("reach")),
                "shares": _num(ins.get("shares")),
                "saves": _num(ins.get("saved")),
                "cover": cover_path,
            }
        )

    records.sort(key=lambda r: r["timestamp"] or "", reverse=True)
    totals = {
        "media": len(records),
        "views": sum(r["views"] for r in records),
        "reach": sum(r["reach"] for r in records),
        "shares": sum(r["shares"] for r in records),
        "saves": sum(r["saves"] for r in records),
        "reels": sum(1 for r in records if r["kind"] == "reel"),
        "carousels": sum(1 for r in records if r["kind"] == "carousel"),
    }
    FEED_OUT.parent.mkdir(parents=True, exist_ok=True)
    FEED_OUT.write_text(
        json.dumps({"totals": totals, "media": records}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"feed": str(FEED_OUT.relative_to(ROOT)), "covers_downloaded": downloaded, "totals": totals}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
