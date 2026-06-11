from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path

from .models import BrainLink
from .page_store import split_frontmatter


EDGE_KEYS = {
    "uses_reference",
    "approved_by",
    "failed_for",
    "inspired_by",
    "revises",
    "depicts",
    "mentions",
}


def extract_links_from_page(path: Path, repo_root: Path) -> list[BrainLink]:
    text = path.read_text(encoding="utf-8")
    rel_path = path.resolve().relative_to(repo_root.resolve()).as_posix()
    frontmatter, body = split_frontmatter(text)
    links: list[BrainLink] = []

    for key in sorted(EDGE_KEYS):
        values = frontmatter.get(key)
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            continue
        for value in values:
            target = str(value)
            links.append(_make_link(rel_path, key, target))

    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", body):
        target = match.group(1).strip()
        if target and not target.startswith(("http://", "https://", "#")):
            links.append(_make_link(rel_path, "mentions", target))

    for match in re.finditer(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", body):
        target = match.group(1).strip()
        if target:
            links.append(_make_link(rel_path, "mentions", target))

    return _dedupe_links(links)


def links_to_dicts(links: list[BrainLink]) -> list[dict[str, str | None]]:
    return [asdict(link) for link in links]


def _make_link(from_path: str, relation: str, target: str) -> BrainLink:
    to_path: str | None = target
    to_id: str | None = None
    if relation == "failed_for" and "/" not in target:
        to_path = None
        to_id = f"failure:{target}"
    return BrainLink(
        from_page_id=f"page:{from_path}",
        to_page_id=f"page:{target}" if to_path else to_id,
        relation=relation,
        evidence_path=from_path,
        from_path=from_path,
        to_path=to_path,
        to_id=to_id,
    )


def _dedupe_links(links: list[BrainLink]) -> list[BrainLink]:
    seen: set[tuple[str | None, str | None, str]] = set()
    deduped: list[BrainLink] = []
    for link in links:
        key = (link.to_path, link.to_id, link.relation)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(link)
    return deduped
