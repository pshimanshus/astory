from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CompiledPageFormatError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedCompiledPage:
    path: Path
    current_truth: str
    timeline: str
    frontmatter: dict[str, Any]
    body: str


def parse_compiled_page(path: Path) -> ParsedCompiledPage:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    marker = "\n---\n"
    if marker not in body:
        raise CompiledPageFormatError(f"{path} is missing compiled truth separator")
    current_truth, timeline = body.split(marker, 1)
    if "# Current Truth" not in current_truth:
        raise CompiledPageFormatError(f"{path} is missing # Current Truth")
    if "# Timeline / Evidence" not in timeline:
        raise CompiledPageFormatError(f"{path} is missing # Timeline / Evidence")
    return ParsedCompiledPage(
        path=path,
        current_truth=current_truth.strip(),
        timeline=timeline.strip(),
        frontmatter=frontmatter,
        body=body,
    )


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    return parse_simple_frontmatter(raw), text[end + len("\n---\n") :]


def parse_simple_frontmatter(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            value = line[4:].strip()
            data.setdefault(current_key, []).append(_unquote(value))
            continue
        if ":" not in line:
            current_key = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [
                _unquote(part.strip())
                for part in inner.split(",")
                if part.strip()
            ]
        else:
            data[key] = _unquote(value)
    return data


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
