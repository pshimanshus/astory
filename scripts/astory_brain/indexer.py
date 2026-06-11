from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .graph import extract_links_from_page, links_to_dicts
from .models import BrainChunk, BrainPage
from .page_store import CompiledPageFormatError, parse_compiled_page, split_frontmatter
from .source_scan import scan_sources


MAX_JSON_CHUNK_CHARS = 4000


def build_index(
    repo_root: str | Path,
    output_dir: str | Path,
    include_runs: list[str],
) -> None:
    root = Path(repo_root).resolve()
    output = Path(output_dir)
    if not output.is_absolute():
        output = root / output
    output.mkdir(parents=True, exist_ok=True)

    sources = scan_sources(root, include_runs=include_runs)
    pages: list[BrainPage] = []
    chunks: list[BrainChunk] = []
    links: list[dict[str, str | None]] = []

    for source in sources:
        abs_path = root / source.path
        page_id: str | None = None
        if source.kind == "compiled_page":
            page = _page_from_compiled_source(abs_path, source.path, source.role)
            pages.append(page)
            page_id = page.page_id
            try:
                links.extend(links_to_dicts(extract_links_from_page(abs_path, root)))
            except (OSError, ValueError):
                pass
        chunks.extend(_chunks_for_source(root, source, page_id))

    _write_jsonl(output / "sources.jsonl", [asdict(source) for source in sources])
    _write_jsonl(output / "pages.jsonl", [asdict(page) for page in pages])
    _write_jsonl(output / "chunks.jsonl", [asdict(chunk) for chunk in chunks])
    _write_jsonl(output / "links.jsonl", links)


def _page_from_compiled_source(path: Path, rel_path: str, role: str | None) -> BrainPage:
    title = path.stem.replace("-", " ").title()
    kind = _infer_page_kind(rel_path)
    try:
        parsed = parse_compiled_page(path)
        title = _first_heading(parsed.body) or title
        kind = str(parsed.frontmatter.get("type") or kind)
        role = str(parsed.frontmatter.get("role") or role) if parsed.frontmatter.get("role") else role
    except CompiledPageFormatError:
        pass
    return BrainPage(
        page_id=f"page:{rel_path}",
        path=rel_path,
        title=title,
        kind=kind,
        role=role,
        tags=_tags_for_path(rel_path),
    )


def _chunks_for_source(root: Path, source, page_id: str | None) -> list[BrainChunk]:
    path = root / source.path
    text = path.read_text(encoding="utf-8", errors="replace")
    if source.kind == "compiled_page":
        try:
            parsed = parse_compiled_page(path)
            raw_chunks = [
                ("compiled_truth", parsed.current_truth),
                ("timeline", parsed.timeline),
            ]
        except CompiledPageFormatError:
            raw_chunks = _markdown_chunks(text)
    elif source.kind == "prompt":
        raw_chunks = [("prompt", text)]
    elif path.suffix.lower() in {".json", ".jsonl"}:
        raw_chunks = _json_chunks(text)
    else:
        raw_chunks = _markdown_chunks(text)

    chunks: list[BrainChunk] = []
    for index, (kind, chunk_text) in enumerate(raw_chunks):
        cleaned = chunk_text.strip()
        if not cleaned:
            continue
        chunks.append(
            BrainChunk(
                chunk_id=f"chunk:{source.source_id}:{index:04d}",
                source_id=source.source_id,
                page_id=page_id,
                path=source.path,
                text=cleaned,
                kind=kind,
                role=source.role,
                tags=_tags_for_path(source.path),
            )
        )
    return chunks


def _markdown_chunks(text: str) -> list[tuple[str, str]]:
    _frontmatter, body = split_frontmatter(text)
    chunks: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        if line.startswith("# ") and current:
            chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current))
    return [("markdown", chunk) for chunk in chunks]


def _json_chunks(text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for key in sorted(data):
                chunks.append(("json", json.dumps({key: data[key]}, sort_keys=True)[:MAX_JSON_CHUNK_CHARS]))
        elif isinstance(data, list):
            for item in data:
                chunks.append(("json", json.dumps(item, sort_keys=True)[:MAX_JSON_CHUNK_CHARS]))
        else:
            chunks.append(("json", json.dumps(data, sort_keys=True)[:MAX_JSON_CHUNK_CHARS]))
    except json.JSONDecodeError:
        for line in text.splitlines():
            if line.strip():
                chunks.append(("jsonl", line[:MAX_JSON_CHUNK_CHARS]))
    return chunks


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _infer_page_kind(path: str) -> str:
    if "/characters/" in path:
        return "character"
    if "/style/" in path:
        return "style"
    if path.endswith("prompt-patterns.md"):
        return "prompt_pattern"
    if path.endswith("run-lessons.md"):
        return "run_lesson"
    return "reference"


def _tags_for_path(path: str) -> list[str]:
    tags: list[str] = []
    for marker in ("identity", "style", "prompt", "approval", "eval", "run", "reference"):
        if marker in path:
            tags.append(marker)
    return tags


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--include-run", action="append", default=[])
    args = parser.parse_args(argv)
    build_index(args.repo_root, args.output, args.include_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
