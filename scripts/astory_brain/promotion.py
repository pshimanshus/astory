from __future__ import annotations

from pathlib import Path

from .models import MemoryClaim


def promote_claim_to_page(repo_root: str | Path, claim: MemoryClaim, target_page: str) -> None:
    root = Path(repo_root).resolve()
    page_path = root / target_page
    if not page_path.exists():
        raise ValueError(f"Target page does not exist: {target_page}")
    text = page_path.read_text(encoding="utf-8")
    if claim.claim_id in text:
        return
    frontmatter, body = _split_frontmatter_raw(text)
    promoted = _insert_current_truth_bullet(body, claim)
    promoted = _insert_timeline_bullet(promoted, claim)
    page_path.write_text((frontmatter + promoted).rstrip() + "\n", encoding="utf-8")


def _insert_current_truth_bullet(body: str, claim: MemoryClaim) -> str:
    if "# Current Truth" not in body or "\n---\n" not in body:
        raise ValueError("Target page must be a compiled brain page.")
    current, timeline = body.split("\n---\n", 1)
    evidence = ", ".join(f"`{path}`" for path in claim.evidence_paths)
    bullet = f"- `{claim.claim_id}`: {claim.text} Evidence: {evidence}."
    return current.rstrip() + "\n" + bullet + "\n\n---\n" + timeline.lstrip()


def _insert_timeline_bullet(body: str, claim: MemoryClaim) -> str:
    current, timeline = body.split("\n---\n", 1)
    evidence = claim.evidence_paths[0] if claim.evidence_paths else f"runs/{claim.run_id}/memory/claim_candidates.json"
    date = claim.run_id[:10]
    bullet = f"- {date} | `{evidence}` | Promoted memory claim `{claim.claim_id}`."
    return current.rstrip() + "\n\n---\n\n" + timeline.rstrip() + "\n" + bullet + "\n"


def _split_frontmatter_raw(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    split_at = end + len("\n---\n")
    return text[:split_at], text[split_at:]
