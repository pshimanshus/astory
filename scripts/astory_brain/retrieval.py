from __future__ import annotations

import json
import re
from pathlib import Path

from .models import BrainChunk, RecallResult


def recall(
    index_dir: str | Path,
    query: str,
    role: str | None = None,
    run_id: str | None = None,
    limit: int = 10,
) -> list[RecallResult]:
    chunks = _load_chunks(Path(index_dir))
    links = _load_links(Path(index_dir))
    query_tokens = _tokens(query)
    scored: list[RecallResult] = []

    for chunk in chunks:
        if not _chunk_allowed(chunk, role, run_id):
            continue
        result = _score_chunk(chunk, query_tokens, query, role, run_id)
        if result.score > 0:
            scored.append(result)

    scored.sort(key=lambda item: (-item.score, item.chunk.path, item.chunk.chunk_id))
    expanded = _graph_expand(scored[:limit], chunks, links, role, run_id)
    merged = _merge_results(scored + expanded)
    return merged[:limit]


def _score_chunk(
    chunk: BrainChunk,
    query_tokens: set[str],
    raw_query: str,
    role: str | None,
    run_id: str | None,
) -> RecallResult:
    path_tokens = _tokens(chunk.path)
    text_tokens = _tokens(chunk.text)
    combined = path_tokens | text_tokens | set(chunk.tags)
    overlap = query_tokens & combined
    evidence: list[str] = []
    score = float(len(overlap))

    normalized_path = chunk.path.lower().replace("-", " ")
    if raw_query.lower() in normalized_path:
        score += 8
        evidence.append("path_match")
    if run_id and run_id in chunk.path:
        score += 10
        evidence.append("exact_run_match")
    elif any(token in path_tokens for token in query_tokens):
        score += 2
        evidence.append("path_match")
    if role and chunk.role == role:
        score += 10
        evidence.append("exact_role_match")
    if chunk.role and chunk.role in query_tokens:
        score += 10
        evidence.append("query_role_match")
    if {"identity", "face"} & query_tokens and "/identity/" in chunk.path:
        score += 7
        evidence.append("identity_path_match")
    if "style" in query_tokens and (
        chunk.role == "style" or "/style/" in chunk.path
    ):
        score += 9
        evidence.append("style_path_match")
    if overlap:
        score += min(len(overlap), 6)
        evidence.append("keyword_match")
    if "prompt" in query_tokens and (chunk.kind == "prompt" or "/prompts/" in chunk.path):
        score += 9
        evidence.append("prompt_kind_match")
    if "slide" in query_tokens and "/prompts/" in chunk.path:
        score += 4
        evidence.append("slide_prompt_match")
    if (
        {"slide", "prompt"} <= query_tokens
        and "/prompts/slide_" in chunk.path
        and chunk.path.endswith("_prompt.txt")
        and "_attempt_" not in chunk.path
        and "_final_" not in chunk.path
    ):
        score += 7
        evidence.append("canonical_slide_prompt_match")
    if "prompt" in query_tokens and chunk.path.endswith("prompt_generation_report.md"):
        score -= 5
    if chunk.kind == "compiled_truth":
        score += 3
        evidence.append("compiled_truth_match")
    if not evidence and score > 0:
        evidence.append("weak_match")

    if "exact_role_match" in evidence or "exact_run_match" in evidence or chunk.kind == "compiled_truth":
        safety = "exists"
    elif len(overlap) >= 2:
        safety = "probable"
    else:
        safety = "weak"

    return RecallResult(chunk=chunk, score=score, evidence=evidence, safety=safety)


def _graph_expand(
    seeds: list[RecallResult],
    chunks: list[BrainChunk],
    links: list[dict],
    role: str | None,
    run_id: str | None,
) -> list[RecallResult]:
    seed_paths = {result.chunk.path for result in seeds}
    linked_paths = {
        link.get("to_path")
        for link in links
        if link.get("from_path") in seed_paths and link.get("to_path")
    }
    if not linked_paths:
        return []
    chunks_by_path: dict[str, BrainChunk] = {}
    for chunk in chunks:
        chunks_by_path.setdefault(chunk.path, chunk)
    results: list[RecallResult] = []
    for path in sorted(linked_paths):
        chunk = chunks_by_path.get(path)
        if not chunk or not _chunk_allowed(chunk, role, run_id):
            continue
        results.append(
            RecallResult(
                chunk=chunk,
                score=1.5,
                evidence=["graph_neighbor"],
                safety="probable",
            )
        )
    return results


def _chunk_allowed(
    chunk: BrainChunk,
    role: str | None,
    run_id: str | None,
) -> bool:
    if run_id and run_id not in chunk.path:
        return False
    if not role:
        return True
    if chunk.role and chunk.role != role:
        return False
    if chunk.role is None and "references/identity/" in chunk.path:
        return False
    return True


def _merge_results(results: list[RecallResult]) -> list[RecallResult]:
    by_chunk: dict[str, RecallResult] = {}
    for result in results:
        current = by_chunk.get(result.chunk.chunk_id)
        if not current or result.score > current.score:
            by_chunk[result.chunk.chunk_id] = result
    merged = list(by_chunk.values())
    merged.sort(key=lambda item: (-item.score, item.chunk.path, item.chunk.chunk_id))
    return merged


def _load_chunks(index_dir: Path) -> list[BrainChunk]:
    rows = _read_jsonl(index_dir / "chunks.jsonl")
    return [
        BrainChunk(
            chunk_id=row["chunk_id"],
            source_id=row["source_id"],
            page_id=row.get("page_id"),
            path=row["path"],
            text=row["text"],
            kind=row["kind"],
            role=row.get("role"),
            tags=list(row.get("tags") or []),
        )
        for row in rows
    ]


def _load_links(index_dir: Path) -> list[dict]:
    path = index_dir / "links.jsonl"
    if not path.exists():
        return []
    return _read_jsonl(path)


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _tokens(text: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", text.lower()) if token}
