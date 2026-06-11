from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .page_store import CompiledPageFormatError, parse_compiled_page


KNOWN_CLI_SCHEMA_VERSION = 1
DERIVED_INDEX_PREFIX = "references/brain/index/"


def lint_brain(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    failures: list[dict[str, str]] = []
    taxonomy = _load_taxonomy(root, failures)
    _check_version(root, failures)

    pages_root = root / "references/brain/pages"
    if pages_root.exists():
        for page in sorted(pages_root.rglob("*.md")):
            _lint_page(root, page, taxonomy, failures)

    index_root = root / "references/brain/index"
    if index_root.exists():
        for jsonl in sorted(index_root.glob("*.jsonl")):
            _lint_jsonl(jsonl, failures)

    return {
        "status": "fail" if failures else "pass",
        "failures": failures,
    }


def _lint_page(
    root: Path,
    path: Path,
    taxonomy: dict[str, Any],
    failures: list[dict[str, str]],
) -> None:
    rel_path = path.resolve().relative_to(root).as_posix()
    try:
        parsed = parse_compiled_page(path)
    except CompiledPageFormatError as error:
        failures.append({"code": "compiled_page_format", "path": rel_path, "message": str(error)})
        return

    page_type = parsed.frontmatter.get("type") or _infer_page_type(rel_path)
    if page_type and page_type not in set(taxonomy.get("page_types") or []):
        failures.append(
            {
                "code": "unknown_page_type",
                "path": rel_path,
                "message": f"Unknown brain page type: {page_type}",
            }
        )

    for line in parsed.current_truth.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        citations = _citations(stripped)
        if not citations:
            failures.append(
                {
                    "code": "missing_citation",
                    "path": rel_path,
                    "message": "Current Truth bullet is missing a backticked local path.",
                }
            )
            continue
        local_citations = [
            citation
            for citation in citations
            if not citation.startswith(("http://", "https://"))
        ]
        if not local_citations:
            failures.append(
                {
                    "code": "missing_local_citation",
                    "path": rel_path,
                    "message": "Current Truth bullet must cite at least one local source path.",
                }
            )
        _lint_citations(root, rel_path, citations, failures)
    _lint_citations(root, rel_path, _citations(parsed.timeline), failures)
    _lint_role_contamination(rel_path, parsed.current_truth + "\n" + parsed.timeline, failures)


def _lint_citations(
    root: Path,
    page_path: str,
    citations: list[str],
    failures: list[dict[str, str]],
) -> None:
    for citation in citations:
        if citation.startswith(DERIVED_INDEX_PREFIX):
            failures.append(
                {
                    "code": "derived_index_citation",
                    "path": page_path,
                    "message": f"Derived index cannot be cited as evidence: {citation}",
                }
            )
            continue
        if citation.startswith(("http://", "https://")):
            continue
        candidate = root / citation
        if not candidate.exists() and "/" in citation:
            failures.append(
                {
                    "code": "missing_citation_path",
                    "path": page_path,
                    "message": f"Cited path does not exist: {citation}",
                }
            )


def _lint_role_contamination(
    rel_path: str,
    text: str,
    failures: list[dict[str, str]],
) -> None:
    if rel_path.endswith("/characters/aachu.md") and "references/identity/zuv/" in text:
        failures.append(
            {
                "code": "role_contamination",
                "path": rel_path,
                "message": "Aachu page cites Zuv identity root.",
            }
        )
    if rel_path.endswith("/characters/zuv.md") and "references/identity/aachu/" in text:
        failures.append(
            {
                "code": "role_contamination",
                "path": rel_path,
                "message": "Zuv page cites Aachu identity root.",
            }
        )


def _load_taxonomy(root: Path, failures: list[dict[str, str]]) -> dict[str, Any]:
    path = root / "references/brain/schema/type_taxonomy.json"
    if not path.exists():
        failures.append(
            {
                "code": "missing_type_taxonomy",
                "path": "references/brain/schema/type_taxonomy.json",
                "message": "Brain taxonomy file is missing.",
            }
        )
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        failures.append({"code": "invalid_type_taxonomy", "path": str(path), "message": str(error)})
        return {}


def _check_version(root: Path, failures: list[dict[str, str]]) -> None:
    path = root / "references/brain/schema/version.json"
    if not path.exists():
        failures.append(
            {
                "code": "missing_schema_version",
                "path": "references/brain/schema/version.json",
                "message": "Brain schema version file is missing.",
            }
        )
        return
    try:
        version = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        failures.append({"code": "invalid_schema_version", "path": str(path), "message": str(error)})
        return
    if int(version.get("schema_version", 0)) > KNOWN_CLI_SCHEMA_VERSION:
        failures.append(
            {
                "code": "schema_version_too_new",
                "path": "references/brain/schema/version.json",
                "message": "Brain schema is newer than this CLI.",
            }
        )


def _lint_jsonl(path: Path, failures: list[dict[str, str]]) -> None:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as error:
            failures.append(
                {
                    "code": "invalid_jsonl",
                    "path": str(path),
                    "message": f"Line {line_number}: {error}",
                }
            )


def _citations(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)


def _infer_page_type(path: str) -> str | None:
    if "/characters/" in path:
        return "character"
    if "/style/" in path:
        return "style"
    if path.endswith("prompt-patterns.md"):
        return "prompt_pattern"
    if path.endswith("run-lessons.md"):
        return "run_lesson"
    return None
