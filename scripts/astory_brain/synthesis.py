from __future__ import annotations

from .models import RecallResult, RecallSynthesis


def synthesize_recall(query: str, results: list[RecallResult]) -> RecallSynthesis:
    cited_paths: list[str] = []
    finding_lines: list[str] = []
    evidence_lines: list[str] = []
    gaps: list[str] = []

    for result in results:
        path = result.chunk.path
        if path not in cited_paths:
            cited_paths.append(path)
        excerpt = _excerpt(result.chunk.text)
        finding_lines.append(f"- `{path}`: {excerpt}")
        evidence_lines.append(
            f"- `{path}` score={result.score:.2f} safety={result.safety} evidence={', '.join(result.evidence)}"
        )

    if not results:
        gaps.append("No memory results found; use current references and approvals only.")
    elif all(result.safety == "weak" for result in results):
        gaps.append(
            "Only weak matches found; require fresh human-visible references or approvals before using this as truth."
        )
    lowered = query.lower()
    if any(term in lowered for term in ("aachu", "zuv", "identity", "face")):
        role_paths = [path for path in cited_paths if "/identity/" in path or "/characters/" in path]
        if not role_paths:
            gaps.append("Role-specific identity evidence missing.")

    if not gaps:
        gaps.append("No blocking memory gaps detected by deterministic recall.")

    answer = "\n".join(
        [
            "# Memory Recall",
            "",
            "## Query",
            "",
            query,
            "",
            "## Cited Findings",
            "",
            "\n".join(finding_lines) if finding_lines else "- No cited findings.",
            "",
            "## Retrieval Evidence",
            "",
            "\n".join(evidence_lines) if evidence_lines else "- No retrieval evidence.",
            "",
            "## Gaps",
            "",
            "\n".join(f"- {gap}" for gap in gaps),
            "",
            "## Usability For This Run",
            "",
            _usability(results),
            "",
        ]
    )
    return RecallSynthesis(
        query=query,
        answer_markdown=answer,
        cited_paths=cited_paths,
        gaps=gaps,
        results=results,
    )


def _excerpt(text: str) -> str:
    collapsed = " ".join(text.replace("`", "'").split())
    if len(collapsed) <= 180:
        return collapsed
    return collapsed[:177].rstrip() + "..."


def _usability(results: list[RecallResult]) -> str:
    if not results:
        return "Do not use memory as truth for this run; no cited results were found."
    if any(result.safety in {"exists", "probable"} for result in results):
        return "Usable as supporting context only. HITL gates and visible-reference requirements still control production."
    return "Weak context only. Do not place these claims into prompts without fresh evidence."
