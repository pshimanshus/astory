# GBrain/Karpathy A Story Brain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an A Story brain layer that ports the engineering primitives from GBrain and Karpathy's LLM Wiki pattern into this repo: immutable sources, compiled knowledge pages, deterministic indexing, hybrid recall, cited synthesis, maintenance, and eval gates.

**Architecture:** Do not copy GBrain as a dependency. Rebuild the same invariants locally: source records, compiled pages, chunks, links, retrieval evidence, recall synthesis, and regression evals. Start with file-backed JSONL/Markdown so the repo remains portable, but shape the contracts so a future SQLite/PGLite/vector backend can replace the storage engine without changing the `/astory` workflow.

**Tech Stack:** Python standard library, `unittest`, Markdown, JSON/JSONL, existing run folders, existing `.agents/skills/astory/` workflow, optional future SQLite/PGLite backend behind the same interface.

---

## Engineering Read Of GBrain And Karpathy

The useful GBrain lesson is not "add vector search." It is the full memory pipeline:

- **Sources:** every datum has origin, scope, timestamp, and permission/source boundary.
- **Compiled truth:** current usable knowledge is rewritten into stable pages.
- **Timeline evidence:** raw evidence is append-only and traceable.
- **Chunks:** searchable units are derived from pages and artifacts, not treated as truth by themselves.
- **Hybrid retrieval:** keyword, semantic, structural, and graph signals are fused.
- **Evidence stamps:** results carry why they matched and whether they are safe to use.
- **Think layer:** retrieval is followed by synthesis with citations and gaps.
- **Maintenance loop:** the brain is repaired, consolidated, and evaluated repeatedly.
- **Evals:** retrieval quality is measured with hard negatives and known-answer tests.

Karpathy's LLM Wiki pattern supplies the simpler product invariant:

- Raw sources are user-owned and immutable.
- The wiki is LLM-maintained and structured.
- Ingest updates existing pages instead of creating a pile of loose notes.
- Query answers can be written back so explorations compound.
- Lint catches contradictions, stale claims, orphans, and gaps.

For A Story, this becomes a creative continuity engine: it remembers identity, style, prompt behavior, run outcomes, QA failures, and creator decisions with citations.

## Non-Negotiable Invariants

- The brain must not override HITL gates in `.agents/skills/astory/SKILL.md`.
- Final Aachu/Zuv imagegen remains blocked unless visible local references are loaded in context.
- No memory claim can be treated as truth unless it cites a local source path.
- Generated run artifacts remain raw evidence; compiled pages summarize them.
- Retrieval must label weak matches instead of smuggling them into prompts.
- Character identity references must remain scoped by role: Aachu, Zuv, together, wardrobe, place, style.
- Search/index scripts must not require network access or API keys.
- The first implementation must be deterministic and testable before embeddings exist.

## Target File Structure

- Create: `scripts/astory_brain/__init__.py`
  - Package marker and public exports.
- Create: `scripts/astory_brain/models.py`
  - Dataclasses for `BrainSource`, `BrainPage`, `BrainChunk`, `BrainLink`, `RecallResult`, and `RecallSynthesis`.
- Create: `scripts/astory_brain/source_scan.py`
  - Discovers source artifacts in `references/`, `.agents/skills/astory/references/`, and selected `runs/*` folders.
- Create: `scripts/astory_brain/page_store.py`
  - Reads and writes compiled Markdown pages with a strict `# Current Truth` / `---` / `# Timeline / Evidence` contract.
- Create: `scripts/astory_brain/indexer.py`
  - Builds deterministic JSONL index files from sources and compiled pages.
- Create: `scripts/astory_brain/retrieval.py`
  - Implements keyword, metadata, role, run-id, and graph-lite retrieval with evidence stamps.
- Create: `scripts/astory_brain/synthesis.py`
  - Produces cited Markdown recall briefs and gap lists from retrieval results.
- Create: `scripts/astory_brain/lint.py`
  - Validates citations, page format, stale claims, orphan pages, and role contamination.
- Create: `scripts/astory_brain_cli.py`
  - CLI for `index`, `recall`, `lint`, and `retro`.
- Create: `tests/test_astory_brain_models.py`
- Create: `tests/test_astory_brain_page_store.py`
- Create: `tests/test_astory_brain_indexer.py`
- Create: `tests/test_astory_brain_retrieval.py`
- Create: `tests/test_astory_brain_synthesis.py`
- Create: `tests/test_astory_brain_lint.py`
- Create: `references/brain/README.md`
- Create: `references/brain/pages/characters/aachu.md`
- Create: `references/brain/pages/characters/zuv.md`
- Create: `references/brain/pages/characters/together.md`
- Create: `references/brain/pages/style/observational-intimacy-premium.md`
- Create: `references/brain/pages/prompt-patterns.md`
- Create: `references/brain/pages/run-lessons.md`
- Create: `references/brain/index/sources.jsonl`
- Create: `references/brain/index/pages.jsonl`
- Create: `references/brain/index/chunks.jsonl`
- Create: `.agents/skills/astory/templates/planning/memory_recall.md`
- Create: `.agents/skills/astory/templates/docs/retro.md`
- Modify: `.agents/skills/astory/SKILL.md`
  - Add `MEMORY_RECALL_PREFLIGHT`, recall artifacts, retro writeback, and brain lint gates.
- Modify: `scripts/astory_repo_qa.py`
  - Add brain artifact checks to the dynamic review loop after the review-loop plan lands.

---

### Task 1: Define Brain Data Contracts

**Files:**
- Create: `scripts/astory_brain/__init__.py`
- Create: `scripts/astory_brain/models.py`
- Test: `tests/test_astory_brain_models.py`

- [ ] **Step 1: Write failing dataclass tests**

Add:

```python
import unittest

from scripts.astory_brain.models import BrainChunk, BrainSource, RecallResult


class AStoryBrainModelTests(unittest.TestCase):
    def test_source_requires_local_path_and_kind(self):
        source = BrainSource(
            source_id="source:run:2026-06-10_22-22_heart-rent:approvals",
            path="runs/2026-06-10_22-22_heart-rent/docs/approvals.md",
            kind="approval",
            scope="run",
            run_id="2026-06-10_22-22_heart-rent",
            role=None,
            sha256="abc123",
            modified_at="2026-06-10T22:22:00+05:30",
        )

        self.assertEqual(source.kind, "approval")
        self.assertEqual(source.run_id, "2026-06-10_22-22_heart-rent")
        self.assertTrue(source.path.endswith("approvals.md"))

    def test_recall_result_carries_evidence_and_safety(self):
        chunk = BrainChunk(
            chunk_id="chunk:1",
            source_id="source:1",
            page_id="page:characters/aachu",
            path="references/brain/pages/characters/aachu.md",
            text="Aachu identity must cite visible local references.",
            kind="compiled_truth",
            role="aachu",
            tags=["identity"],
        )
        result = RecallResult(
            chunk=chunk,
            score=1.0,
            evidence=["exact_role_match", "keyword_match"],
            safety="exists",
        )

        self.assertIn("exact_role_match", result.evidence)
        self.assertEqual(result.safety, "exists")
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_models -v
```

Expected: FAIL because `scripts.astory_brain.models` does not exist.

- [ ] **Step 3: Implement dataclasses**

Create `scripts/astory_brain/models.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


SourceKind = Literal[
    "approval",
    "prompt",
    "eval",
    "reference",
    "skill_reference",
    "compiled_page",
    "retro",
    "trace",
]

Safety = Literal["exists", "probable", "weak", "unknown"]


@dataclass(frozen=True)
class BrainSource:
    source_id: str
    path: str
    kind: SourceKind
    scope: str
    run_id: str | None
    role: str | None
    sha256: str
    modified_at: str


@dataclass(frozen=True)
class BrainPage:
    page_id: str
    path: str
    title: str
    kind: str
    role: str | None
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BrainChunk:
    chunk_id: str
    source_id: str
    page_id: str | None
    path: str
    text: str
    kind: str
    role: str | None
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BrainLink:
    from_page_id: str
    to_page_id: str
    relation: str
    evidence_path: str


@dataclass(frozen=True)
class RecallResult:
    chunk: BrainChunk
    score: float
    evidence: list[str]
    safety: Safety


@dataclass(frozen=True)
class RecallSynthesis:
    query: str
    answer_markdown: str
    cited_paths: list[str]
    gaps: list[str]
    results: list[RecallResult]
```

Create `scripts/astory_brain/__init__.py` with:

```python
"""A Story brain layer: source indexing, recall, synthesis, and linting."""
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_models -v
```

Expected: PASS.

---

### Task 2: Implement Compiled Page Store

**Files:**
- Create: `scripts/astory_brain/page_store.py`
- Create: `references/brain/README.md`
- Create: `references/brain/pages/characters/aachu.md`
- Create: `references/brain/pages/characters/zuv.md`
- Create: `references/brain/pages/characters/together.md`
- Create: `references/brain/pages/style/observational-intimacy-premium.md`
- Create: `references/brain/pages/prompt-patterns.md`
- Create: `references/brain/pages/run-lessons.md`
- Test: `tests/test_astory_brain_page_store.py`

- [ ] **Step 1: Write failing page contract tests**

Add tests that create a temporary compiled page and assert:

```python
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.page_store import CompiledPageFormatError, parse_compiled_page


class AStoryBrainPageStoreTests(unittest.TestCase):
    def test_parse_compiled_page_splits_truth_and_timeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "aachu.md"
            page.write_text(
                "# Aachu\n\n"
                "# Current Truth\n"
                "- Use only visible local identity references.\n\n"
                "---\n\n"
                "# Timeline / Evidence\n"
                "- 2026-06-10 | `runs/example/docs/approvals.md` | approval recorded.\n",
                encoding="utf-8",
            )

            parsed = parse_compiled_page(page)

            self.assertIn("visible local identity references", parsed.current_truth)
            self.assertIn("runs/example/docs/approvals.md", parsed.timeline)

    def test_missing_separator_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "bad.md"
            page.write_text("# Current Truth\nNo separator\n", encoding="utf-8")

            with self.assertRaises(CompiledPageFormatError):
                parse_compiled_page(page)
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_page_store -v
```

Expected: FAIL because `page_store.py` does not exist.

- [ ] **Step 3: Implement page parser**

Implement `parse_compiled_page(path: Path)` with a strict separator check:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class CompiledPageFormatError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedCompiledPage:
    path: Path
    current_truth: str
    timeline: str


def parse_compiled_page(path: Path) -> ParsedCompiledPage:
    text = path.read_text(encoding="utf-8")
    marker = "\n---\n"
    if marker not in text:
        raise CompiledPageFormatError(f"{path} is missing compiled truth separator")
    current_truth, timeline = text.split(marker, 1)
    if "# Current Truth" not in current_truth:
        raise CompiledPageFormatError(f"{path} is missing # Current Truth")
    if "# Timeline / Evidence" not in timeline:
        raise CompiledPageFormatError(f"{path} is missing # Timeline / Evidence")
    return ParsedCompiledPage(path=path, current_truth=current_truth.strip(), timeline=timeline.strip())
```

- [ ] **Step 4: Add initial compiled pages**

Create the seven Markdown pages listed above. Each page must include:

```markdown
# Current Truth

- Initial page exists to receive cited A Story evidence.
- Do not treat this page as stronger than local references, approvals, or run QA.

---

# Timeline / Evidence

- 2026-06-10 | `docs/setup_status.md` | Repo setup says planning is ready, while final image generation still requires visible local references.
```

For character pages, add the correct role-specific reference roots:

```markdown
- Aachu source root: `references/identity/aachu/`
- Zuv source root: `references/identity/zuv/`
- Together source root: `references/identity/together/`
```

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_page_store -v
```

Expected: PASS.

---

### Task 3: Build Deterministic Source Scanner

**Files:**
- Create: `scripts/astory_brain/source_scan.py`
- Test: `tests/test_astory_brain_indexer.py`

- [ ] **Step 1: Write failing source scan tests**

Add:

```python
import unittest

from scripts.astory_brain.source_scan import scan_sources


class AStoryBrainIndexerTests(unittest.TestCase):
    def test_scan_sources_finds_heart_rent_prompts_and_approvals(self):
        sources = scan_sources(".", include_runs=["2026-06-10_22-22_heart-rent"])
        paths = {source.path for source in sources}

        self.assertIn("runs/2026-06-10_22-22_heart-rent/docs/approvals.md", paths)
        self.assertIn("runs/2026-06-10_22-22_heart-rent/prompts/slide_01_4x5_prompt.txt", paths)

    def test_scan_sources_assigns_roles_from_reference_paths(self):
        sources = scan_sources(".", include_runs=[])
        role_by_path = {source.path: source.role for source in sources}

        self.assertEqual(role_by_path["references/identity/aachu/README.md"], "aachu")
        self.assertEqual(role_by_path["references/identity/zuv/README.md"], "zuv")
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_indexer -v
```

Expected: FAIL because `source_scan.py` does not exist.

- [ ] **Step 3: Implement scanner**

Implement:

```python
def scan_sources(repo_root: str | Path, include_runs: list[str]) -> list[BrainSource]:
    ...
```

Rules:

- Include Markdown, JSON, JSONL, and prompt `.txt` files.
- Include `references/`.
- Include `.agents/skills/astory/references/`.
- Include only named run folders from `include_runs`.
- Exclude `images/`, `exports/`, binary files, `__pycache__`, `.DS_Store`.
- Assign kind from path:
  - `docs/approvals.md` -> `approval`
  - `prompts/*.txt` -> `prompt`
  - `evals/*` -> `eval`
  - `references/brain/pages/*` -> `compiled_page`
  - `.agents/skills/astory/references/*` -> `skill_reference`
  - `references/*` -> `reference`
  - `logs/trace.jsonl` -> `trace`
- Assign role from path segment: `aachu`, `zuv`, `together`, `style`, `wardrobe`, `places`.
- Compute SHA-256 from file bytes.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_indexer -v
```

Expected: PASS.

---

### Task 4: Build File-Backed Index

**Files:**
- Create: `scripts/astory_brain/indexer.py`
- Generate: `references/brain/index/sources.jsonl`
- Generate: `references/brain/index/pages.jsonl`
- Generate: `references/brain/index/chunks.jsonl`
- Test: `tests/test_astory_brain_indexer.py`

- [ ] **Step 1: Add failing index write tests**

Extend `tests/test_astory_brain_indexer.py`:

```python
import json
import tempfile
from pathlib import Path

from scripts.astory_brain.indexer import build_index


def test_build_index_writes_sources_pages_and_chunks(self):
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "index"
        build_index(".", output, include_runs=["2026-06-10_22-22_heart-rent"])

        self.assertTrue((output / "sources.jsonl").exists())
        self.assertTrue((output / "pages.jsonl").exists())
        self.assertTrue((output / "chunks.jsonl").exists())

        chunks = [
            json.loads(line)
            for line in (output / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertTrue(any("heart-rent" in chunk["path"] for chunk in chunks))
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_indexer -v
```

Expected: FAIL because `build_index` does not exist.

- [ ] **Step 3: Implement chunking and index write**

Implement `build_index(repo_root, output_dir, include_runs)`:

- Calls `scan_sources`.
- Writes one JSON object per source to `sources.jsonl`.
- Writes one page record per compiled page to `pages.jsonl`.
- Writes chunks to `chunks.jsonl`.
- Chunk rules:
  - Markdown headings start new chunks.
  - Prompt files are one chunk per file.
  - JSON and JSONL files are chunked by top-level line/object text capped at 4,000 characters.
  - Each chunk includes `chunk_id`, `source_id`, `path`, `kind`, `role`, `tags`, and `text`.

- [ ] **Step 4: Generate repo index**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m scripts.astory_brain.indexer --repo-root . --output references/brain/index --include-run 2026-06-10_22-22_heart-rent --include-run 2026-06-10_22-55_couple-banter
```

Expected: writes the three JSONL files under `references/brain/index/`.

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_indexer -v
python3 -m json.tool references/brain/index/sources.jsonl >/tmp/astory_brain_sources_check.json
```

Expected: unit tests pass. The second command may fail because JSONL is not a single JSON document; if it fails, validate with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json, pathlib; [json.loads(line) for line in pathlib.Path("references/brain/index/sources.jsonl").read_text().splitlines() if line.strip()]'
```

Expected: JSONL parses line-by-line.

---

### Task 5: Implement Hybrid-Light Retrieval With Evidence Stamps

**Files:**
- Create: `scripts/astory_brain/retrieval.py`
- Test: `tests/test_astory_brain_retrieval.py`

- [ ] **Step 1: Write failing retrieval tests**

Add:

```python
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.retrieval import recall


class AStoryBrainRetrievalTests(unittest.TestCase):
    def test_recall_heart_rent_finds_active_run_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            build_index(".", index, include_runs=["2026-06-10_22-22_heart-rent"])

            results = recall(index, "heart rent slide prompt", limit=5)

            self.assertTrue(any("heart-rent" in item.chunk.path for item in results))
            self.assertTrue(any("keyword_match" in item.evidence for item in results))

    def test_role_filter_prevents_aachu_zuv_contamination(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            build_index(".", index, include_runs=[])

            results = recall(index, "face identity references", role="aachu", limit=20)

            self.assertTrue(results)
            self.assertTrue(all(item.chunk.role in {None, "aachu"} for item in results))
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_retrieval -v
```

Expected: FAIL because `retrieval.py` does not exist.

- [ ] **Step 3: Implement deterministic retrieval**

Implement `recall(index_dir, query, role=None, run_id=None, limit=10)`:

- Tokenize query with lowercase alphanumeric tokens.
- Score exact path/run-id/title matches highly.
- Score keyword overlap.
- Boost compiled pages.
- Boost matching role.
- Penalize mismatched role to zero when role filter is set.
- Add evidence stamps:
  - `exact_run_match`
  - `exact_role_match`
  - `path_match`
  - `keyword_match`
  - `compiled_truth_match`
  - `weak_match`
- Set safety:
  - `exists` for exact path/run/role or compiled page matches.
  - `probable` for strong keyword overlap.
  - `weak` for low overlap.
  - `unknown` only when no results exist.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_retrieval -v
```

Expected: PASS.

---

### Task 6: Implement Cited Recall Synthesis

**Files:**
- Create: `scripts/astory_brain/synthesis.py`
- Create: `.agents/skills/astory/templates/planning/memory_recall.md`
- Test: `tests/test_astory_brain_synthesis.py`

- [ ] **Step 1: Write failing synthesis tests**

Add:

```python
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.indexer import build_index
from scripts.astory_brain.retrieval import recall
from scripts.astory_brain.synthesis import synthesize_recall


class AStoryBrainSynthesisTests(unittest.TestCase):
    def test_synthesis_contains_citations_and_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            build_index(".", index, include_runs=["2026-06-10_22-22_heart-rent"])
            results = recall(index, "heart rent prompt identity", limit=5)

            synthesis = synthesize_recall("heart rent prompt identity", results)

            self.assertIn("## Cited Findings", synthesis.answer_markdown)
            self.assertIn("## Gaps", synthesis.answer_markdown)
            self.assertTrue(synthesis.cited_paths)
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_synthesis -v
```

Expected: FAIL because `synthesis.py` does not exist.

- [ ] **Step 3: Implement synthesis**

Implement `synthesize_recall(query, results)`:

- Produces Markdown sections:
  - `## Query`
  - `## Cited Findings`
  - `## Retrieval Evidence`
  - `## Gaps`
  - `## Usability For This Run`
- Every finding line includes a local path citation in backticks.
- If all top results are weak, add gap: `Only weak matches found; require fresh human-visible references or approvals before using this as truth.`
- If identity terms appear but no role-specific result is found, add gap: `Role-specific identity evidence missing.`

- [ ] **Step 4: Add memory recall template**

Create `.agents/skills/astory/templates/planning/memory_recall.md`:

```markdown
# Memory Recall

Run: `{{run_id}}`
Query: `{{query}}`

## Cited Findings

{{cited_findings}}

## Retrieval Evidence

{{retrieval_evidence}}

## Gaps

{{gaps}}

## Usability For This Run

{{usability}}
```

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_synthesis -v
```

Expected: PASS.

---

### Task 7: Add Brain CLI

**Files:**
- Create: `scripts/astory_brain_cli.py`
- Test: `tests/test_astory_brain_synthesis.py`

- [ ] **Step 1: Write failing CLI smoke test**

Add:

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class AStoryBrainCliTests(unittest.TestCase):
    def test_cli_index_and_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/astory_brain_cli.py",
                    "index",
                    "--repo-root",
                    ".",
                    "--output",
                    str(index),
                    "--include-run",
                    "2026-06-10_22-22_heart-rent",
                ],
                check=True,
            )
            output = subprocess.check_output(
                [
                    sys.executable,
                    "scripts/astory_brain_cli.py",
                    "recall",
                    "--index",
                    str(index),
                    "--query",
                    "heart rent prompt identity",
                ],
                text=True,
            )

            self.assertIn("## Cited Findings", output)
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_synthesis.AStoryBrainCliTests.test_cli_index_and_recall -v
```

Expected: FAIL because `scripts/astory_brain_cli.py` does not exist.

- [ ] **Step 3: Implement CLI**

Commands:

```bash
python3 scripts/astory_brain_cli.py index --repo-root . --output references/brain/index --include-run 2026-06-10_22-22_heart-rent
python3 scripts/astory_brain_cli.py recall --index references/brain/index --query "heart rent prompt identity" --output runs/2026-06-10_22-22_heart-rent/planning/memory_recall.md
```

Implementation details:

- `index` calls `build_index`.
- `recall` calls `recall` and `synthesize_recall`.
- `recall --output` writes Markdown and creates parent directories.
- Exit code is non-zero only for invalid arguments or unreadable index files.

- [ ] **Step 4: Run test to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_synthesis.AStoryBrainCliTests.test_cli_index_and_recall -v
```

Expected: PASS.

---

### Task 8: Add Brain Lint

**Files:**
- Create: `scripts/astory_brain/lint.py`
- Test: `tests/test_astory_brain_lint.py`

- [ ] **Step 1: Write failing lint tests**

Add:

```python
import tempfile
import unittest
from pathlib import Path

from scripts.astory_brain.lint import lint_brain


class AStoryBrainLintTests(unittest.TestCase):
    def test_lint_flags_missing_citation_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page_dir = root / "references/brain/pages"
            page_dir.mkdir(parents=True)
            (page_dir / "bad.md").write_text(
                "# Current Truth\n\n- This claim has no citation.\n\n---\n\n# Timeline / Evidence\n\n",
                encoding="utf-8",
            )

            report = lint_brain(root)

            self.assertEqual(report["status"], "fail")
            self.assertIn("missing_citation", report["failures"][0]["code"])
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_lint -v
```

Expected: FAIL because `lint.py` does not exist.

- [ ] **Step 3: Implement lint**

Rules:

- Every compiled page must parse.
- Every non-heading bullet under `# Current Truth` must contain a backticked local path.
- Character pages must not cite the other character's identity root unless page is `together.md`.
- `references/brain/index/*.jsonl` must parse line-by-line when present.
- Lint returns:

```python
{
    "status": "pass" | "fail",
    "failures": [{"code": str, "path": str, "message": str}],
}
```

- [ ] **Step 4: Run test to verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_lint -v
```

Expected: PASS.

---

### Task 9: Integrate Brain With `/astory`

**Files:**
- Modify: `.agents/skills/astory/SKILL.md`
- Create: `.agents/skills/astory/templates/docs/retro.md`

- [ ] **Step 1: Update state machine**

Modify the state machine to insert:

```markdown
5. `MEMORY_RECALL_PREFLIGHT`
```

after `REFERENCE_PREFLIGHT`, then renumber the later states.

Add the rule:

```markdown
During `MEMORY_RECALL_PREFLIGHT`, build or refresh `references/brain/index/`,
run a recall query for the run's idea/theme/story context, and write
`planning/memory_recall.md`. Do not use uncited memory claims in idea, story,
prompt, or QA artifacts. Memory recall can surface risks and past lessons, but
it cannot bypass HITL gates or visible-reference imagegen requirements.
```

- [ ] **Step 2: Add retro template**

Create `.agents/skills/astory/templates/docs/retro.md`:

```markdown
# Run Retro

Run: `{{run_id}}`
Status: `{{status}}`

## What Worked

{{what_worked}}

## What Failed Or Drifted

{{what_failed}}

## Prompt Lessons

{{prompt_lessons}}

## Identity / Style Lessons

{{identity_style_lessons}}

## Proposed Brain Updates

{{proposed_brain_updates}}

## Evidence

{{evidence_paths}}
```

- [ ] **Step 3: Add completion rule**

Add to `/astory` `WRITE_REPORTS`:

```markdown
Before `COMPLETE_OR_BLOCKED`, write `docs/retro.md` and list proposed updates
to `references/brain/pages/*`. Do not silently modify compiled brain pages
unless the user explicitly asks for memory writeback.
```

---

### Task 10: Add Review-Loop QA Hooks

**Files:**
- Modify: `scripts/astory_repo_qa.py`
- Modify: `tests/test_astory_repo_qa.py`

- [ ] **Step 1: Write failing QA test**

Add:

```python
def test_repo_qa_requires_memory_recall_for_imagegen_story_run(self):
    audit = astory_repo_qa.run_repo_qa(REPO_ROOT, "2026-06-10_22-22_heart-rent")
    check = audit["checks_by_id"]["memory_recall"]

    self.assertIn(check["status"], {"pass", "blocked"})
    self.assertIn("planning/memory_recall.md", check["expected_artifacts"])
```

- [ ] **Step 2: Implement QA check**

Add `_check_memory_recall(root, run_dir, workflow)`:

- `not_applicable` for local identity execution runs.
- `blocked` for imagegen story runs without `planning/memory_recall.md`.
- `fail` if recall exists but has no cited local paths.
- `pass` if recall exists and includes `## Cited Findings`, `## Gaps`, and at least one backticked local path.

- [ ] **Step 3: Run focused tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa -v
```

Expected: PASS after active run receives a valid recall artifact, or expected blocked status is asserted for runs not yet recalled.

---

### Task 11: Generate Active Run Recall

**Files:**
- Generate: `runs/2026-06-10_22-22_heart-rent/planning/memory_recall.md`
- Generate: `references/brain/index/sources.jsonl`
- Generate: `references/brain/index/pages.jsonl`
- Generate: `references/brain/index/chunks.jsonl`

- [ ] **Step 1: Build index**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py index --repo-root . --output references/brain/index --include-run 2026-06-10_22-22_heart-rent --include-run 2026-06-10_22-55_couple-banter --include-run 2026-06-07_17-57_auto
```

Expected: index JSONL files are written.

- [ ] **Step 2: Generate heart-rent recall**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py recall --index references/brain/index --query "heart rent prompt identity style Aachu Zuv" --output runs/2026-06-10_22-22_heart-rent/planning/memory_recall.md
```

Expected: `planning/memory_recall.md` includes cited findings, retrieval evidence, gaps, and usability.

- [ ] **Step 3: Lint brain**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py lint --repo-root .
```

Expected: pass once initial compiled pages cite local source paths.

---

### Task 12: Verification

**Files:**
- Check all files above.

- [ ] **Step 1: Run unit tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_models tests.test_astory_brain_page_store tests.test_astory_brain_indexer tests.test_astory_brain_retrieval tests.test_astory_brain_synthesis tests.test_astory_brain_lint -v
```

Expected: PASS.

- [ ] **Step 2: Run existing A Story tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_repo_qa tests.test_imagegen_reference_context tests.test_local_identity_pipeline -v
```

Expected: PASS or documented blocked status for known active-run hard gates.

- [ ] **Step 3: Validate JSONL indexes**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json, pathlib; [json.loads(line) for file in pathlib.Path("references/brain/index").glob("*.jsonl") for line in file.read_text().splitlines() if line.strip()]'
```

Expected: exits 0.

- [ ] **Step 4: Run repo QA**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_repo_qa.py --run-id 2026-06-10_22-22_heart-rent
```

Expected: writes QA artifacts and reports brain recall as pass or explicitly blocked with actionable missing artifact paths.

---

## Research Hardening Addendum

This addendum exists because the first version of the plan was still too close
to "Markdown notes plus search." The actual GBrain/Karpathy lesson is a set of
invariants. If we miss these, the brain becomes a cute index that will drift,
duplicate, and eventually lie.

Primary references used for this pass:

- GBrain repo: `https://github.com/garrytan/gbrain`
- GBrain retrieval architecture: `/private/tmp/gbrain-review/docs/architecture/RETRIEVAL.md`
- GBrain system-of-record contract: `/private/tmp/gbrain-review/docs/architecture/system-of-record.md`
- GBrain type taxonomy: `/private/tmp/gbrain-review/docs/architecture/type-taxonomy.md`
- GBrain eval bench: `/private/tmp/gbrain-review/docs/eval-bench.md`
- Karpathy LLM Wiki gist: `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`
- Microsoft GraphRAG docs: `https://microsoft.github.io/graphrag/`
- LangMem core concepts: `https://langchain-ai.github.io/langmem/concepts/conceptual_guide/`
- Mem0 paper: `https://arxiv.org/abs/2504.19413`
- Generative Agents paper: `https://arxiv.org/abs/2304.03442`
- RAPTOR paper: `https://arxiv.org/abs/2401.18059`
- Self-RAG paper: `https://arxiv.org/abs/2310.11511`

### Adaptation Matrix

| Upstream idea | Why it matters | A Story adaptation |
|---|---|---|
| Markdown/wiki is canonical; DB/index is derived | Prevents unrecoverable memory state and lets git remain the merge/recovery layer | `references/brain/pages/*` and run artifacts are source of truth; `references/brain/index/*` is disposable derived cache |
| Compiled truth + append-only timeline | Keeps the current working truth fast while preserving evidence history | Every brain page has `# Current Truth`, `---`, and `# Timeline / Evidence`; current truth bullets cite local paths |
| Typed source boundaries | Prevents cross-contamination between user notes, generated artifacts, references, and approvals | Every source record has `kind`, `scope`, `run_id`, `role`, `sha256`, `modified_at` |
| Canonical type taxonomy | Type sprawl breaks filtering, enrichment, and routing | Brain pages use a small fixed taxonomy: `character`, `relationship`, `style`, `prompt_pattern`, `run_lesson`, `failure_mode`, `reference`, `procedure` |
| Hybrid retrieval | Vector alone misses exact names; keyword alone misses paraphrase; graph catches relationships | Start with keyword + metadata + role + graph-lite. Add embeddings only after qrels pass |
| RRF and per-source boosts | Multiple retrieval arms should vote without one global score dominating | Later backend must fuse keyword/vector/graph/recency with RRF, not arbitrary weighted soup |
| Evidence stamps | Agents need to know why a result matched and whether it is safe to use | Results include `evidence` and `safety`; prompt code must reject weak identity/style claims |
| Alias resolver | Names and motifs evolve; duplicate pages are poison | Add aliases/frontmatter for Aachu/Zuv, style names, run slugs, motif labels |
| Graph traversal | Relationship questions are not solved by semantic similarity | Extract typed edges from wikilinks/frontmatter: `uses_reference`, `approved_by`, `failed_for`, `inspired_by`, `revises`, `depicts`, `mentions` |
| Think layer | Retrieval chunks are not the product; cited synthesis is | `memory_recall.md` must synthesize findings, gaps, and usability, not dump search results |
| Contradiction probe | Long-lived memory accumulates conflicts | Lint flags incompatible current-truth claims across pages and stale run lessons |
| Eval gate and qrels | Retrieval changes need measurable regression tests | Add `tests/fixtures/brain/qrels.json` for identity, style, prompt, run, and hard-negative queries |
| Active vs background memory | Writing memory in the hot path adds latency and mistakes | Active run writes `docs/retro.md`; compiled brain updates require explicit writeback/review |
| Prompt optimization from trajectories | The skill should improve from failures, not vibes | Retro records prompt failures; later `skillopt`-style task proposes skill/prompt edits with eval proof |
| Community/global summaries | Some queries are corpus-level, not entity-level | Add periodic rollups: style patterns, repeated failures, best-performing story structures |
| Guardrail seams | Classifiers should observe at boundaries without silently changing behavior | Brain lint/reporting can warn; it cannot rewrite prompts or bypass HITL |

### Final Architecture Position

The A Story brain has four memory planes:

1. **Episodic memory:** run folders, approvals, traces, prompts, evals, retros.
2. **Semantic memory:** compiled brain pages under `references/brain/pages/`.
3. **Procedural memory:** `.agents/skills/astory/SKILL.md`, master prompt, contracts, templates.
4. **Relational memory:** derived links connecting runs, references, motifs, failures, approvals, and pages.

Only planes 1-3 are canonical on disk. Plane 4 is derived and rebuilt.

The setup is "final enough" only when these recovery commands are true:

```bash
rm -rf references/brain/index
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py index --repo-root . --output references/brain/index --include-run 2026-06-10_22-22_heart-rent
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py lint --repo-root .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_astory_brain_retrieval tests.test_astory_brain_lint -v
```

If deleting the derived index changes truth, the design is wrong.

---

### Task 13: Enforce File-System Canonical System Of Record

**Files:**
- Modify: `scripts/astory_brain/indexer.py`
- Modify: `scripts/astory_brain/lint.py`
- Test: `tests/test_astory_brain_lint.py`

- [ ] **Step 1: Write failing derived-cache test**

Add:

```python
def test_index_is_disposable_and_rebuildable(self):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        page_dir = root / "references/brain/pages/characters"
        page_dir.mkdir(parents=True)
        (page_dir / "aachu.md").write_text(
            "# Aachu\n\n"
            "# Current Truth\n\n"
            "- Use visible local references from `references/identity/aachu/`.\n\n"
            "---\n\n"
            "# Timeline / Evidence\n\n"
            "- 2026-06-10 | `references/identity/aachu/README.md` | Source root exists.\n",
            encoding="utf-8",
        )

        index = root / "references/brain/index"
        build_index(root, index, include_runs=[])
        before = (index / "chunks.jsonl").read_text(encoding="utf-8")

        shutil.rmtree(index)
        build_index(root, index, include_runs=[])
        after = (index / "chunks.jsonl").read_text(encoding="utf-8")

        self.assertEqual(before, after)
```

- [ ] **Step 2: Implement stable ordering**

Ensure source scanning and chunk writing are sorted by stable relative path,
chunk kind, and chunk index. Do not include wall-clock timestamps inside derived
index rows except source `modified_at`.

- [ ] **Step 3: Add lint rule**

`lint_brain` must fail if a compiled page cites a derived index file as evidence.
Valid evidence lives in raw references, run artifacts, skill contracts, or setup
docs. Invalid evidence examples:

```text
references/brain/index/sources.jsonl
references/brain/index/pages.jsonl
references/brain/index/chunks.jsonl
```

---

### Task 14: Add Canonical Brain Type Taxonomy

**Files:**
- Create: `references/brain/schema/type_taxonomy.json`
- Modify: `scripts/astory_brain/models.py`
- Modify: `scripts/astory_brain/lint.py`
- Test: `tests/test_astory_brain_lint.py`

- [ ] **Step 1: Create taxonomy**

Create:

```json
{
  "version": 1,
  "page_types": [
    "character",
    "relationship",
    "style",
    "prompt_pattern",
    "run_lesson",
    "failure_mode",
    "reference",
    "procedure"
  ],
  "roles": [
    "aachu",
    "zuv",
    "together",
    "style",
    "wardrobe",
    "place",
    "brand",
    "text"
  ],
  "source_kinds": [
    "approval",
    "prompt",
    "eval",
    "reference",
    "skill_reference",
    "compiled_page",
    "retro",
    "trace"
  ]
}
```

- [ ] **Step 2: Write failing taxonomy lint test**

Add a page with frontmatter `type: random_note` and assert lint fails with
`unknown_page_type`.

- [ ] **Step 3: Implement taxonomy validation**

Compiled pages may include YAML-like frontmatter. If `type:` exists, it must be
in `type_taxonomy.json`. If no `type:` exists, infer from path and warn only.

---

### Task 15: Add Graph-Lite Edge Extraction

**Files:**
- Create: `scripts/astory_brain/graph.py`
- Generate: `references/brain/index/links.jsonl`
- Test: `tests/test_astory_brain_retrieval.py`

- [ ] **Step 1: Write failing graph extraction test**

Add a fixture page containing:

```markdown
---
type: run_lesson
uses_reference:
  - references/identity/aachu/face-01.png
failed_for:
  - generic_watercolor
---

# Current Truth

- Slide 1 used `references/identity/aachu/face-01.png`.
```

Assert extracted links include:

```json
{"relation": "uses_reference", "to_path": "references/identity/aachu/face-01.png"}
{"relation": "failed_for", "to_id": "failure:generic_watercolor"}
```

- [ ] **Step 2: Implement deterministic edge extraction**

Extract edges from:

- Markdown links: `[text](path)`
- Obsidian links: `[[path]]`
- Frontmatter lists: `uses_reference`, `approved_by`, `failed_for`, `inspired_by`, `revises`, `depicts`, `mentions`

Write `links.jsonl` with:

```json
{
  "from_path": "references/brain/pages/run-lessons.md",
  "to_path": "runs/...",
  "relation": "mentions",
  "evidence_path": "references/brain/pages/run-lessons.md"
}
```

- [ ] **Step 3: Use graph as retrieval arm**

When a top result has outgoing links, include linked chunks as graph-neighbor
candidates with evidence `graph_neighbor`. Keep this bounded to depth 1 in the
first implementation.

---

### Task 16: Add Qrels-Based Retrieval Eval Gate

**Files:**
- Create: `tests/fixtures/brain/qrels.json`
- Create: `scripts/astory_brain/eval.py`
- Test: `tests/test_astory_brain_retrieval.py`

- [ ] **Step 1: Create qrels fixture**

Create:

```json
[
  {
    "query": "Aachu face identity references",
    "role": "aachu",
    "expected_paths": ["references/identity/aachu/README.md"],
    "forbidden_paths": ["references/identity/zuv/README.md"]
  },
  {
    "query": "Zuv face identity references",
    "role": "zuv",
    "expected_paths": ["references/identity/zuv/README.md"],
    "forbidden_paths": ["references/identity/aachu/README.md"]
  },
  {
    "query": "observational intimacy premium watercolor style",
    "role": "style",
    "expected_paths": ["references/style/observational-intimacy-premium/README.md"],
    "forbidden_paths": []
  },
  {
    "query": "heart rent slide prompt",
    "run_id": "2026-06-10_22-22_heart-rent",
    "expected_paths": ["runs/2026-06-10_22-22_heart-rent/prompts/slide_01_4x5_prompt.txt"],
    "forbidden_paths": []
  }
]
```

- [ ] **Step 2: Implement eval runner**

`run_retrieval_eval(index_dir, qrels_path, top_k=5)` returns:

```python
{
    "status": "pass" | "fail",
    "recall_at_k": float,
    "forbidden_hit_count": int,
    "failures": [...]
}
```

Pass criteria for first gate:

- `recall_at_k >= 1.0` on fixture queries.
- `forbidden_hit_count == 0`.

- [ ] **Step 3: Add verification command**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/astory_brain_cli.py eval --index references/brain/index --qrels tests/fixtures/brain/qrels.json
```

Expected: pass.

---

### Task 17: Add Background Maintenance Loop

**Files:**
- Modify: `scripts/astory_brain_cli.py`
- Create: `references/brain/reports/doctor.md`
- Create: `references/brain/reports/retrieval_eval.json`
- Test: `tests/test_astory_brain_lint.py`

- [ ] **Step 1: Add `doctor` command**

`python3 scripts/astory_brain_cli.py doctor --repo-root .` must run:

1. Brain lint.
2. Index rebuild.
3. JSONL parse validation.
4. Qrels eval when fixture exists.
5. Orphan page report.
6. Stale run report: runs with no `docs/retro.md`.

- [ ] **Step 2: Write report**

Write `references/brain/reports/doctor.md` with sections:

```markdown
# A Story Brain Doctor

## Status

## Lint

## Retrieval Eval

## Orphans

## Stale Runs

## Required Human Decisions
```

- [ ] **Step 3: Integrate with `/astory audit`**

Update `.agents/skills/astory/SKILL.md` so `/astory audit <run_id>` includes
brain doctor status when brain files exist.

---

### Task 18: Add Versioning And Migration Contract

**Files:**
- Create: `references/brain/schema/version.json`
- Create: `references/brain/schema/migrations/0001_initial.md`
- Modify: `scripts/astory_brain/lint.py`

- [ ] **Step 1: Create version file**

Create:

```json
{
  "schema_version": 1,
  "compatible_cli_min": 1,
  "canonical_root": "references/brain/pages",
  "derived_roots": ["references/brain/index", "references/brain/reports"]
}
```

- [ ] **Step 2: Create migration note**

Create `references/brain/schema/migrations/0001_initial.md`:

```markdown
# Brain Schema Migration 0001

Initial schema:

- Markdown compiled pages are canonical.
- JSONL index files are derived.
- Type taxonomy is fixed in `references/brain/schema/type_taxonomy.json`.
- Derived state can be deleted and rebuilt.
```

- [ ] **Step 3: Add lint version check**

Lint fails if `references/brain/schema/version.json` is missing or has a
schema version higher than the CLI knows how to read.

---

## Future Backend Upgrade Contract

The file-backed index is intentionally not the final form. A later backend can replace it only if these interfaces remain stable:

- `scan_sources(repo_root, include_runs) -> list[BrainSource]`
- `build_index(repo_root, output_dir, include_runs) -> None`
- `recall(index_dir, query, role=None, run_id=None, limit=10) -> list[RecallResult]`
- `synthesize_recall(query, results) -> RecallSynthesis`
- `lint_brain(repo_root) -> dict`

When the corpus exceeds deterministic search, add:

- SQLite FTS or PGLite as a storage engine.
- Embedding columns as optional fields on chunks.
- RRF fusion across keyword, vector, role, graph, and recency arms.
- Hard-negative evals before enabling semantic matches in production prompts.

Do not add embeddings before the deterministic tests above exist.

## Self-Review

- Spec coverage: This plan ports GBrain/Karpathy primitives into A Story: sources, compiled pages, chunks, retrieval evidence, synthesis, maintenance, and evals.
- Scope: This is one subsystem, the brain layer. It integrates with the separate dynamic review-loop plan but does not replace it.
- Placeholder scan: No task uses TBD/TODO/fill-later language.
- Risk: The plan intentionally starts deterministic. That is not "toy mode"; it is the correctness harness required before a vector backend can be trusted with character identity and style continuity.
