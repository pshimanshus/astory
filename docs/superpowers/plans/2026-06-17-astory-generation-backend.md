# A Story of Two — Generation Backend v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an automated backend service that accepts a submission (photos + voice + choices), runs a headless studio pipeline (transcribe → winner-bank match → prompt build → render → vision-QA → assemble), and returns a finished A Story of Two–style illustrated carousel — no human in the loop.

**Architecture:** A Python **FastAPI** service with an in-process async worker. `POST /jobs` stores the submission and queues one job; the worker runs the six pipeline stages and writes results; `GET /jobs/{id}` reports status + slides. All model calls go through two injected interfaces — `LLMProvider` (Gemini, free) and `Renderer` (OpenAI `gpt-image-1`, paid) — so the pipeline logic is pure and unit-testable with fakes. The studio's winner bank + house-style/imagegen contracts are loaded as data/context; this is a focused headless pipeline, not a port of the 33-state HITL orchestrator.

**Tech Stack:** Python 3.13, FastAPI, uvicorn, `sqlite3` (stdlib) for jobs, local filesystem for blobs, `openai` SDK (rendering + nothing else), `google-genai` SDK (transcription + reasoning + vision QA). Tests: **`unittest`** (stdlib), run via `python3 -m unittest`. FastAPI endpoint tests use `fastapi.testclient.TestClient` (bundled, uses `httpx`).

## Global Constraints

- **Image rendering:** OpenAI `gpt-image-1` only. Native portrait size `1024x1536`.
- **All other model calls (transcription, reasoning, vision QA):** Gemini `gemini-2.5-flash` via free tier. **No Anthropic/Claude SDK or API anywhere in the project.**
- **Test framework:** `unittest` (match the repo). Never add `pytest`.
- **No network in unit/integration tests** — providers are injected and faked. Real API calls happen only in the env-gated live-smoke (Task 15).
- **Secrets** live in `.env.local` (gitignored): `OPENAI_API_KEY`, `GEMINI_API_KEY`. Never commit keys. Never print key values.
- **Brandmark:** every rendered slide prompt must request the tiny low-contrast handwritten `@a.storyof.two` top-right brandmark (from the imagegen contract).
- All new code lives under `backend/`. Do not modify `app/`, `scripts/`, or `references/` (read-only reuse of `references/` data is fine).
- `git add` only the files a task names — never `git add -A` (the working tree carries unrelated WIP).

---

## File structure (created across tasks)

```
backend/
  requirements.txt                 # Task 0
  README.md                        # Task 0 / 15
  .gitignore                       # Task 0  (.venv, data/, __pycache__)
  app/
    __init__.py                    # Task 0
    config.py                      # Task 0  — env + paths + model names + slide range
    main.py                        # Task 0 (skeleton) / Task 14 (job routes)
    models.py                      # Task 1  — JobStatus, JobInput, SlidePrompt, Slide, MatchResult, Job
    store.py                       # Task 2  — SQLite jobs + filesystem blobs
    data_refs.py                   # Task 3  — load winner bank, contracts text, house-style ref images
    providers/
      __init__.py                  # Task 4
      base.py                      # Task 4  — LLMProvider, Renderer protocols + QAResult
      gemini.py                    # Task 5  — GeminiProvider (transcribe, reason_json)
      openai_renderer.py           # Task 6  — OpenAIRenderer (render)
    pipeline/
      __init__.py                  # Task 7
      transcribe.py                # Task 9  — story_from_audio
      match.py                     # Task 7  — match_winner
      prompt_build.py              # Task 8  — build_slide_prompts
      render.py                    # Task 10 — render_slides
      qa.py                        # Task 11 — qa_slide, render_with_qa
      assemble.py                  # Task 12 — assemble_carousel
      run.py                       # Task 13 — run_job (orchestrates 1..6)
  tests/
    __init__.py                    # Task 1
    fakes.py                       # Task 4  — FakeLLM, FakeRenderer
    test_models.py                 # Task 1
    test_store.py                  # Task 2
    test_data_refs.py              # Task 3
    test_gemini.py                 # Task 5
    test_openai_renderer.py        # Task 6
    test_match.py                  # Task 7
    test_prompt_build.py           # Task 8
    test_transcribe.py             # Task 9
    test_render.py                 # Task 10
    test_qa.py                     # Task 11
    test_assemble.py               # Task 12
    test_run.py                    # Task 13
    test_api.py                    # Task 14
  scripts/
    live_smoke.py                  # Task 15 — manual, env-gated end-to-end
```

All tests are run from the `backend/` directory with `python3 -m unittest` (a `backend/.venv` is created in Task 0; activate it for every step).

---

## Task 0: Scaffold the backend service

**Files:**
- Create: `backend/requirements.txt`, `backend/.gitignore`, `backend/README.md`, `backend/app/__init__.py`, `backend/app/config.py`, `backend/app/main.py`

**Interfaces:**
- Produces: `app.config.settings` (a `Settings` instance with `openai_api_key`, `gemini_api_key`, `data_dir: Path`, `image_model="gpt-image-1"`, `gemini_model="gemini-2.5-flash"`, `image_size="1024x1536"`, `min_slides=3`, `max_slides=5`); `app.main.app` (FastAPI instance with `GET /health`).

- [ ] **Step 1: Create `backend/requirements.txt`**

```
fastapi==0.115.*
uvicorn[standard]==0.30.*
openai>=1.40
google-genai>=0.3
python-multipart==0.0.*
httpx>=0.27
```

- [ ] **Step 2: Create `backend/.gitignore`**

```
.venv/
data/
__pycache__/
*.pyc
.env.local
```

- [ ] **Step 3: Create the venv and install**

Run (from repo root):
```bash
cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```
Expected: installs with no errors; `python3 -c "import fastapi, openai, google.genai"` prints nothing (success).

- [ ] **Step 4: Create `backend/app/__init__.py`** (empty file).

- [ ] **Step 5: Create `backend/app/config.py`**

```python
import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_env_local() -> None:
    # Minimal .env.local loader (repo convention; no python-dotenv dependency).
    root = Path(__file__).resolve().parents[2]
    env = root / ".env.local"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    gemini_api_key: str
    data_dir: Path
    image_model: str = "gpt-image-1"
    gemini_model: str = "gemini-2.5-flash"
    image_size: str = "1024x1536"
    min_slides: int = 3
    max_slides: int = 5


def load_settings() -> Settings:
    _load_env_local()
    data_dir = Path(os.environ.get("ASTORY_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        data_dir=data_dir,
    )


settings = load_settings()
```

- [ ] **Step 6: Create `backend/app/main.py` (skeleton)**

```python
from fastapi import FastAPI

app = FastAPI(title="A Story of Two — Generation Backend")


@app.get("/health")
def health() -> dict:
    return {"ok": True}
```

- [ ] **Step 7: Verify the app imports and health works**

Run (in `backend/`, venv active):
```bash
python3 -c "from fastapi.testclient import TestClient; from app.main import app; print(TestClient(app).get('/health').json())"
```
Expected: `{'ok': True}`

- [ ] **Step 8: Create `backend/README.md`** with run instructions:

```markdown
# A Story of Two — Generation Backend

## Setup
    cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

Add to repo-root `.env.local`: `OPENAI_API_KEY=...` and `GEMINI_API_KEY=...`

## Run
    . .venv/bin/activate && uvicorn app.main:app --reload

## Test
    . .venv/bin/activate && python3 -m unittest
```

- [ ] **Step 9: Commit**

```bash
git add backend/requirements.txt backend/.gitignore backend/README.md backend/app/__init__.py backend/app/config.py backend/app/main.py
git commit -m "feat(backend): scaffold FastAPI service + config + health"
```

---

## Task 1: Domain models

**Files:**
- Create: `backend/app/models.py`, `backend/tests/__init__.py`, `backend/tests/test_models.py`

**Interfaces:**
- Produces: `JobStatus` (Enum: `QUEUED`,`RUNNING`,`READY`,`FAILED`), and dataclasses `JobInput`, `SlidePrompt`, `Slide`, `MatchResult`, `Job` with the fields below. `Job.new(input) -> Job` factory (uuid id, status QUEUED, utc timestamps, empty slides). `Job.touch()` updates `updated_at`.

- [ ] **Step 1: Write the failing test** `backend/tests/test_models.py`

```python
import unittest
from app.models import Job, JobInput, JobStatus, Slide, SlidePrompt, MatchResult


def make_input(**kw):
    base = dict(
        device_id="dev_1", delivery_contact="a@b.com", creator_name="Aarav",
        partner_name="Mira", relationship="together", setting_choice="keep",
        quote_mode="agent", quote_copy=None, photo_paths=["p1.jpg"], audio_path="a.webm",
    )
    base.update(kw)
    return JobInput(**base)


class ModelTests(unittest.TestCase):
    def test_job_new_defaults(self):
        job = Job.new(make_input())
        self.assertEqual(job.status, JobStatus.QUEUED)
        self.assertTrue(job.id)
        self.assertEqual(job.slides, [])
        self.assertIsNone(job.story_text)
        self.assertIsNone(job.error)
        self.assertEqual(job.created_at, job.updated_at)

    def test_touch_changes_updated_at(self):
        job = Job.new(make_input())
        first = job.updated_at
        job.status = JobStatus.RUNNING
        job.touch()
        self.assertGreaterEqual(job.updated_at, first)

    def test_quote_mode_values(self):
        for mode in ("own", "agent", "none"):
            self.assertEqual(make_input(quote_mode=mode).quote_mode, mode)

    def test_slide_and_prompt_and_match(self):
        sp = SlidePrompt(index=0, image_prompt="x", on_image_text="hi", use_setting_ref=True)
        sl = Slide(index=0, image_path="out/0.png", caption="hi")
        mr = MatchResult(pattern_id="p1", slide_count=4, beats=["a", "b", "c", "d"])
        self.assertEqual((sp.index, sl.index, mr.slide_count), (0, 0, 4))
```

- [ ] **Step 2: Run it — expect failure**

Run: `cd backend && python3 -m unittest tests.test_models -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'app.models'`).

- [ ] **Step 3: Implement** `backend/app/models.py`

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"


@dataclass
class JobInput:
    device_id: str
    delivery_contact: str
    creator_name: str
    partner_name: str
    relationship: str          # 'together' | 'sending'
    setting_choice: str        # 'keep' | 'fresh'
    quote_mode: str            # 'own' | 'agent' | 'none'
    quote_copy: str | None
    photo_paths: list[str]
    audio_path: str


@dataclass
class SlidePrompt:
    index: int
    image_prompt: str
    on_image_text: str | None
    use_setting_ref: bool


@dataclass
class Slide:
    index: int
    image_path: str
    caption: str | None


@dataclass
class MatchResult:
    pattern_id: str
    slide_count: int
    beats: list[str]


@dataclass
class Job:
    id: str
    status: JobStatus
    input: JobInput
    story_text: str | None = None
    match: MatchResult | None = None
    slides: list[Slide] = field(default_factory=list)
    error: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def new(cls, job_input: JobInput) -> "Job":
        ts = _now()
        return cls(id=uuid.uuid4().hex, status=JobStatus.QUEUED, input=job_input,
                   created_at=ts, updated_at=ts)

    def touch(self) -> None:
        self.updated_at = _now()
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_models -v`
Expected: PASS (4 tests). Create an empty `backend/tests/__init__.py` so discovery works.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models.py backend/tests/__init__.py backend/tests/test_models.py
git commit -m "feat(backend): domain models with tests"
```

---

## Task 2: Job store (SQLite + blob filesystem)

**Files:**
- Create: `backend/app/store.py`, `backend/tests/test_store.py`

**Interfaces:**
- Consumes: `app.models` (`Job`, `JobInput`, `JobStatus`, `Slide`, `MatchResult`).
- Produces: `JobStore(db_path: Path, blob_root: Path)` with: `create(job: Job) -> None`, `get(job_id: str) -> Job | None`, `save(job: Job) -> None` (upsert), `save_blob(job_id, name, data: bytes) -> str` (returns absolute path), `read_blob(path: str) -> bytes`. Job (de)serialized to/from JSON in one TEXT column.

- [ ] **Step 1: Write the failing test** `backend/tests/test_store.py`

```python
import tempfile
import unittest
from pathlib import Path

from app.models import Job, JobInput, JobStatus, Slide, MatchResult
from app.store import JobStore


def make_job():
    ji = JobInput(device_id="d", delivery_contact="c", creator_name="A", partner_name="B",
                  relationship="together", setting_choice="keep", quote_mode="none",
                  quote_copy=None, photo_paths=["p.jpg"], audio_path="a.webm")
    return Job.new(ji)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.store = JobStore(db_path=root / "jobs.db", blob_root=root / "blobs")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_and_get_roundtrip(self):
        job = make_job()
        self.store.create(job)
        got = self.store.get(job.id)
        self.assertEqual(got.id, job.id)
        self.assertEqual(got.status, JobStatus.QUEUED)
        self.assertEqual(got.input.creator_name, "A")

    def test_save_persists_status_match_and_slides(self):
        job = make_job()
        self.store.create(job)
        job.status = JobStatus.READY
        job.story_text = "we met in the rain"
        job.match = MatchResult(pattern_id="p1", slide_count=2, beats=["x", "y"])
        job.slides = [Slide(index=0, image_path="0.png", caption="hi")]
        self.store.save(job)
        got = self.store.get(job.id)
        self.assertEqual(got.status, JobStatus.READY)
        self.assertEqual(got.story_text, "we met in the rain")
        self.assertEqual(got.match.slide_count, 2)
        self.assertEqual(got.slides[0].caption, "hi")

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.store.get("nope"))

    def test_blob_roundtrip(self):
        job = make_job()
        self.store.create(job)
        path = self.store.save_blob(job.id, "photo0.jpg", b"\x89PNGdata")
        self.assertTrue(Path(path).exists())
        self.assertEqual(self.store.read_blob(path), b"\x89PNGdata")
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_store -v`
Expected: FAIL (`No module named 'app.store'`).

- [ ] **Step 3: Implement** `backend/app/store.py`

```python
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from app.models import Job, JobInput, JobStatus, MatchResult, Slide


class JobStore:
    def __init__(self, db_path: Path, blob_root: Path):
        self.db_path = Path(db_path)
        self.blob_root = Path(blob_root)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.blob_root.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, data TEXT NOT NULL)")

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create(self, job: Job) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO jobs (id, data) VALUES (?, ?)", (job.id, _dumps(job)))

    def save(self, job: Job) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO jobs (id, data) VALUES (?, ?) "
                      "ON CONFLICT(id) DO UPDATE SET data=excluded.data", (job.id, _dumps(job)))

    def get(self, job_id: str) -> Job | None:
        with self._conn() as c:
            row = c.execute("SELECT data FROM jobs WHERE id=?", (job_id,)).fetchone()
        return _loads(row[0]) if row else None

    def save_blob(self, job_id: str, name: str, data: bytes) -> str:
        d = self.blob_root / job_id
        d.mkdir(parents=True, exist_ok=True)
        path = d / name
        path.write_bytes(data)
        return str(path)

    def read_blob(self, path: str) -> bytes:
        return Path(path).read_bytes()


def _dumps(job: Job) -> str:
    return json.dumps(asdict(job), default=lambda o: o.value if isinstance(o, JobStatus) else o)


def _loads(data: str) -> Job:
    d = json.loads(data)
    d["status"] = JobStatus(d["status"])
    d["input"] = JobInput(**d["input"])
    d["match"] = MatchResult(**d["match"]) if d.get("match") else None
    d["slides"] = [Slide(**s) for s in d.get("slides", [])]
    return Job(**d)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_store -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/store.py backend/tests/test_store.py
git commit -m "feat(backend): SQLite job store + blob filesystem with tests"
```

---

## Task 3: Reference data loaders

**Files:**
- Create: `backend/app/data_refs.py`, `backend/tests/test_data_refs.py`

**Interfaces:**
- Produces: `load_winner_bank(path=None) -> list[dict]` (defaults to `references/text-style/winner-bank/winner_bank.json`); `bank_summary(records, limit=40) -> list[dict]` (each `{caption, slide_count, comments, send_proxy}` — trimmed fields the matcher needs); `load_contract(name) -> str` (reads `.agents/skills/astory/references/<name>.md`); `house_style_ref_paths() -> list[Path]` (configurable list of brand reference images; default empty list if none configured, never raises).

- [ ] **Step 1: Write the failing test** `backend/tests/test_data_refs.py`

```python
import unittest
from app import data_refs


class DataRefsTests(unittest.TestCase):
    def test_winner_bank_loads_list(self):
        bank = data_refs.load_winner_bank()
        self.assertIsInstance(bank, list)
        self.assertGreater(len(bank), 0)
        self.assertIn("caption", bank[0])

    def test_bank_summary_trims_fields(self):
        bank = data_refs.load_winner_bank()
        summ = data_refs.bank_summary(bank, limit=5)
        self.assertEqual(len(summ), 5)
        self.assertEqual(set(summ[0].keys()), {"caption", "slide_count", "comments", "send_proxy"})

    def test_load_contract_imagegen(self):
        text = data_refs.load_contract("imagegen-contract")
        self.assertIn("1080x1350", text)  # known string from the contract

    def test_house_style_ref_paths_returns_list(self):
        self.assertIsInstance(data_refs.house_style_ref_paths(), list)
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_data_refs -v`
Expected: FAIL (`No module named 'app.data_refs'`).

- [ ] **Step 3: Implement** `backend/app/data_refs.py`

```python
from __future__ import annotations

import json
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_WINNER_BANK = _REPO / "references/text-style/winner-bank/winner_bank.json"
_CONTRACTS = _REPO / ".agents/skills/astory/references"


def load_winner_bank(path: Path | None = None) -> list[dict]:
    return json.loads(Path(path or _WINNER_BANK).read_text())


def bank_summary(records: list[dict], limit: int = 40) -> list[dict]:
    out = []
    for r in records[:limit]:
        out.append({
            "caption": (r.get("caption") or "")[:600],
            "slide_count": r.get("childCount") or len(r.get("childTypes") or []),
            "comments": r.get("commentsCount") or 0,
            "send_proxy": r.get("commentSendProxy") or 0,
        })
    return out


def load_contract(name: str) -> str:
    return (_CONTRACTS / f"{name}.md").read_text()


def house_style_ref_paths() -> list[Path]:
    # Configurable via ASTORY_STYLE_REFS (os.pathsep-separated). Empty + non-raising by default.
    raw = os.environ.get("ASTORY_STYLE_REFS", "").strip()
    if not raw:
        return []
    return [Path(p) for p in raw.split(os.pathsep) if Path(p).exists()]
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_data_refs -v`
Expected: PASS (4 tests). If `test_load_contract_imagegen` fails on the `1080x1350` assertion, open `.agents/skills/astory/references/imagegen-contract.md`, pick another guaranteed substring (e.g. `"brandmark"`), and update the test to match the real file.

- [ ] **Step 5: Commit**

```bash
git add backend/app/data_refs.py backend/tests/test_data_refs.py
git commit -m "feat(backend): winner-bank + contract + style-ref loaders with tests"
```

---

## Task 4: Provider interfaces + test fakes

**Files:**
- Create: `backend/app/providers/__init__.py`, `backend/app/providers/base.py`, `backend/tests/fakes.py`

**Interfaces:**
- Produces: `LLMProvider` (Protocol): `transcribe(self, audio_bytes: bytes, mime_type: str) -> str`; `reason_json(self, system: str, prompt: str, image_bytes: list[bytes] | None = None) -> dict`. `Renderer` (Protocol): `render(self, prompt: str, ref_images: list[bytes], size: str) -> bytes`. `QAResult` dataclass: `passed: bool`, `reason: str`. Fakes: `FakeLLM(transcript="...", responses=[dict, ...])` (pops queued dicts from `reason_json`, records calls in `.calls`); `FakeRenderer(image=b"PNG")` (returns fixed bytes, records prompts in `.prompts`).

- [ ] **Step 1: Write the failing test** (fakes are test infra; assert their contract) `backend/tests/test_fakes.py`

```python
import unittest
from tests.fakes import FakeLLM, FakeRenderer


class FakeTests(unittest.TestCase):
    def test_fake_llm_transcribe_and_reason(self):
        llm = FakeLLM(transcript="hello", responses=[{"a": 1}, {"b": 2}])
        self.assertEqual(llm.transcribe(b"x", "audio/webm"), "hello")
        self.assertEqual(llm.reason_json("sys", "p1"), {"a": 1})
        self.assertEqual(llm.reason_json("sys", "p2"), {"b": 2})
        self.assertEqual(len(llm.calls), 2)

    def test_fake_renderer_records_prompts(self):
        r = FakeRenderer(image=b"IMG")
        self.assertEqual(r.render("draw", [], "1024x1536"), b"IMG")
        self.assertEqual(r.prompts, ["draw"])
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_fakes -v`
Expected: FAIL (`No module named 'tests.fakes'`).

- [ ] **Step 3: Implement** `backend/app/providers/__init__.py` (empty), `backend/app/providers/base.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class QAResult:
    passed: bool
    reason: str


@runtime_checkable
class LLMProvider(Protocol):
    def transcribe(self, audio_bytes: bytes, mime_type: str) -> str: ...
    def reason_json(self, system: str, prompt: str,
                    image_bytes: list[bytes] | None = None) -> dict: ...


@runtime_checkable
class Renderer(Protocol):
    def render(self, prompt: str, ref_images: list[bytes], size: str) -> bytes: ...
```

And `backend/tests/fakes.py`:

```python
from __future__ import annotations


class FakeLLM:
    def __init__(self, transcript: str = "", responses: list[dict] | None = None):
        self._transcript = transcript
        self._responses = list(responses or [])
        self.calls: list[tuple[str, str, int]] = []

    def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        return self._transcript

    def reason_json(self, system: str, prompt: str, image_bytes=None) -> dict:
        self.calls.append((system, prompt, len(image_bytes or [])))
        return self._responses.pop(0) if self._responses else {}


class FakeRenderer:
    def __init__(self, image: bytes = b"PNG"):
        self._image = image
        self.prompts: list[str] = []

    def render(self, prompt: str, ref_images, size: str) -> bytes:
        self.prompts.append(prompt)
        return self._image
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_fakes -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/__init__.py backend/app/providers/base.py backend/tests/fakes.py backend/tests/test_fakes.py
git commit -m "feat(backend): provider interfaces + test fakes"
```

---

## Task 5: Gemini provider (transcription + reasoning + vision)

**Files:**
- Create: `backend/app/providers/gemini.py`, `backend/tests/test_gemini.py`

**Interfaces:**
- Consumes: `app.config.settings` (gemini_api_key, gemini_model).
- Produces: `GeminiProvider(api_key, model, client=None)` implementing `LLMProvider`. `reason_json` requests `response_mime_type="application/json"` and returns the parsed dict; `transcribe` sends audio bytes + an instruction and returns text; vision is `reason_json(..., image_bytes=[...])`. A `client` may be injected for testing (any object exposing `.models.generate_content(...)`).

- [ ] **Step 1: Write the failing test** `backend/tests/test_gemini.py` (inject a mock client; assert request construction + parsing — no network)

```python
import json
import unittest
from unittest.mock import MagicMock

from app.providers.gemini import GeminiProvider


class GeminiTests(unittest.TestCase):
    def _provider(self, text):
        client = MagicMock()
        resp = MagicMock()
        resp.text = text
        client.models.generate_content.return_value = resp
        return GeminiProvider(api_key="k", model="gemini-2.5-flash", client=client), client

    def test_reason_json_parses_object(self):
        p, client = self._provider('{"pattern_id": "p1", "slide_count": 3}')
        out = p.reason_json("sys", "match this")
        self.assertEqual(out["slide_count"], 3)
        client.models.generate_content.assert_called_once()
        kwargs = client.models.generate_content.call_args.kwargs
        self.assertEqual(kwargs["model"], "gemini-2.5-flash")

    def test_reason_json_strips_code_fence(self):
        p, _ = self._provider('```json\n{"ok": true}\n```')
        self.assertEqual(p.reason_json("s", "p"), {"ok": True})

    def test_transcribe_returns_text(self):
        p, client = self._provider("we met in the rain")
        self.assertEqual(p.transcribe(b"audiobytes", "audio/webm"), "we met in the rain")
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_gemini -v`
Expected: FAIL (`No module named 'app.providers.gemini'`).

- [ ] **Step 3: Implement** `backend/app/providers/gemini.py`

```python
from __future__ import annotations

import json


class GeminiProvider:
    def __init__(self, api_key: str, model: str, client=None):
        self.model = model
        if client is not None:
            self._client = client
            self._types = None
        else:
            from google import genai
            from google.genai import types
            self._client = genai.Client(api_key=api_key)
            self._types = types

    def _part_from_bytes(self, data: bytes, mime: str):
        if self._types is not None:
            return self._types.Part.from_bytes(data=data, mime_type=mime)
        return {"inline_data": {"mime_type": mime, "data": data}}

    def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        contents = [
            self._part_from_bytes(audio_bytes, mime_type),
            "Transcribe this voice note into plain text. Return only the words spoken.",
        ]
        resp = self._client.models.generate_content(model=self.model, contents=contents)
        return (resp.text or "").strip()

    def reason_json(self, system: str, prompt: str, image_bytes: list[bytes] | None = None) -> dict:
        contents: list = [f"{system}\n\n{prompt}"]
        for img in image_bytes or []:
            contents.append(self._part_from_bytes(img, "image/png"))
        config = None
        if self._types is not None:
            config = self._types.GenerateContentConfig(response_mime_type="application/json")
        resp = self._client.models.generate_content(model=self.model, contents=contents, config=config)
        return _parse_json(resp.text or "{}")


def _parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
        t = t.strip().rstrip("`").strip()
    return json.loads(t)
```

(Note: the test injects a `client`, so `config=None` is passed to the mock — fine. The real path sets `_types` and builds a real config.)

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_gemini -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/gemini.py backend/tests/test_gemini.py
git commit -m "feat(backend): Gemini provider (transcribe/reason/vision) with tests"
```

---

## Task 6: OpenAI renderer (gpt-image-1)

**Files:**
- Create: `backend/app/providers/openai_renderer.py`, `backend/tests/test_openai_renderer.py`

**Interfaces:**
- Consumes: `app.config.settings` (openai_api_key, image_model, image_size).
- Produces: `OpenAIRenderer(api_key, model, client=None)` implementing `Renderer`. `render(prompt, ref_images, size)` → PNG bytes. With no `ref_images`, calls `client.images.generate(...)`; with `ref_images`, calls `client.images.edit(...)` passing the references. Decodes `data[0].b64_json` → bytes. `client` injectable for tests.

- [ ] **Step 1: Write the failing test** `backend/tests/test_openai_renderer.py`

```python
import base64
import unittest
from unittest.mock import MagicMock

from app.providers.openai_renderer import OpenAIRenderer


def _resp(png: bytes):
    r = MagicMock()
    item = MagicMock()
    item.b64_json = base64.b64encode(png).decode()
    r.data = [item]
    return r


class RendererTests(unittest.TestCase):
    def test_generate_when_no_refs(self):
        client = MagicMock()
        client.images.generate.return_value = _resp(b"PNGBYTES")
        r = OpenAIRenderer(api_key="k", model="gpt-image-1", client=client)
        out = r.render("draw them", [], "1024x1536")
        self.assertEqual(out, b"PNGBYTES")
        client.images.generate.assert_called_once()
        self.assertFalse(client.images.edit.called)
        self.assertEqual(client.images.generate.call_args.kwargs["model"], "gpt-image-1")
        self.assertEqual(client.images.generate.call_args.kwargs["size"], "1024x1536")

    def test_edit_when_refs_present(self):
        client = MagicMock()
        client.images.edit.return_value = _resp(b"EDITED")
        r = OpenAIRenderer(api_key="k", model="gpt-image-1", client=client)
        out = r.render("restyle", [b"refimg"], "1024x1536")
        self.assertEqual(out, b"EDITED")
        client.images.edit.assert_called_once()
        self.assertFalse(client.images.generate.called)
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_openai_renderer -v`
Expected: FAIL (`No module named 'app.providers.openai_renderer'`).

- [ ] **Step 3: Implement** `backend/app/providers/openai_renderer.py`

```python
from __future__ import annotations

import base64
import io


class OpenAIRenderer:
    def __init__(self, api_key: str, model: str, client=None):
        self.model = model
        if client is not None:
            self._client = client
        else:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)

    def render(self, prompt: str, ref_images: list[bytes], size: str) -> bytes:
        if ref_images:
            resp = self._client.images.edit(
                model=self.model, prompt=prompt, size=size,
                image=[io.BytesIO(b) for b in ref_images],
            )
        else:
            resp = self._client.images.generate(
                model=self.model, prompt=prompt, size=size, n=1,
            )
        return base64.b64decode(resp.data[0].b64_json)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_openai_renderer -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/openai_renderer.py backend/tests/test_openai_renderer.py
git commit -m "feat(backend): OpenAI gpt-image-1 renderer with tests"
```

---

## Task 7: Winner-bank matcher

**Files:**
- Create: `backend/app/pipeline/__init__.py`, `backend/app/pipeline/match.py`, `backend/tests/test_match.py`

**Interfaces:**
- Consumes: `LLMProvider`, `app.models.MatchResult`, `app.data_refs.bank_summary`.
- Produces: `match_winner(story: str, creator: str, partner: str, relationship: str, bank: list[dict], llm: LLMProvider, min_slides=3, max_slides=5) -> MatchResult`. Builds a system prompt embedding the bank summary, asks the LLM for `{pattern_id, slide_count, beats}`, clamps `slide_count` into `[min_slides, max_slides]`, and ensures `beats` length equals `slide_count` (truncate or pad with `""`).

- [ ] **Step 1: Write the failing test** `backend/tests/test_match.py`

```python
import unittest
from app.pipeline.match import match_winner
from tests.fakes import FakeLLM


BANK = [{"caption": "love in small moments", "childCount": 4, "commentsCount": 10, "commentSendProxy": 3}]


class MatchTests(unittest.TestCase):
    def test_returns_matchresult_with_clamped_slides(self):
        llm = FakeLLM(responses=[{"pattern_id": "p1", "slide_count": 9, "beats": ["a", "b"]}])
        mr = match_winner("we argue then laugh", "A", "B", "together", BANK, llm,
                          min_slides=3, max_slides=5)
        self.assertEqual(mr.pattern_id, "p1")
        self.assertEqual(mr.slide_count, 5)          # 9 clamped to max 5
        self.assertEqual(len(mr.beats), 5)           # padded to slide_count

    def test_truncates_extra_beats(self):
        llm = FakeLLM(responses=[{"pattern_id": "p2", "slide_count": 3,
                                  "beats": ["a", "b", "c", "d", "e"]}])
        mr = match_winner("s", "A", "B", "sending", BANK, llm)
        self.assertEqual(len(mr.beats), 3)

    def test_passes_story_and_bank_to_llm(self):
        llm = FakeLLM(responses=[{"pattern_id": "p", "slide_count": 3, "beats": ["a", "b", "c"]}])
        match_winner("the rooftop night", "A", "B", "together", BANK, llm)
        _system, prompt, _imgs = llm.calls[0]
        self.assertIn("rooftop night", prompt)
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_match -v`
Expected: FAIL (`No module named 'app.pipeline.match'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/__init__.py` (empty) and `backend/app/pipeline/match.py`

```python
from __future__ import annotations

import json

from app.data_refs import bank_summary
from app.models import MatchResult
from app.providers.base import LLMProvider

_SYSTEM = (
    "You are the Story Director for A Story of Two, a hand-drawn romantic illustration brand. "
    "Given a couple's story and a bank of high-performing carousel patterns, pick the single "
    "pattern that best fits this story and design the slide beats. Respond ONLY as JSON: "
    '{"pattern_id": str, "slide_count": int, "beats": [str, ...]} where beats has exactly '
    "slide_count entries, each a one-line description of that slide's emotional beat."
)


def match_winner(story: str, creator: str, partner: str, relationship: str,
                 bank: list[dict], llm: LLMProvider, min_slides: int = 3,
                 max_slides: int = 5) -> MatchResult:
    summary = bank_summary(bank, limit=40)
    prompt = (
        f"Couple: {creator} & {partner} ({relationship}).\n"
        f"Their story: {story}\n\n"
        f"Winning patterns (JSON):\n{json.dumps(summary)}\n\n"
        f"Choose slide_count between {min_slides} and {max_slides}."
    )
    data = llm.reason_json(_SYSTEM, prompt)
    count = max(min_slides, min(max_slides, int(data.get("slide_count", min_slides))))
    beats = list(data.get("beats", []))[:count]
    beats += [""] * (count - len(beats))
    return MatchResult(pattern_id=str(data.get("pattern_id", "unknown")),
                       slide_count=count, beats=beats)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_match -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/__init__.py backend/app/pipeline/match.py backend/tests/test_match.py
git commit -m "feat(backend): winner-bank matcher with tests"
```

---

## Task 8: Slide prompt builder

**Files:**
- Create: `backend/app/pipeline/prompt_build.py`, `backend/tests/test_prompt_build.py`

**Interfaces:**
- Consumes: `LLMProvider`, `app.models.MatchResult`, `app.models.JobInput`, `app.models.SlidePrompt`, `app.data_refs.load_contract`.
- Produces: `build_slide_prompts(match: MatchResult, job_input: JobInput, llm: LLMProvider, brandmark: str = "@a.storyof.two") -> list[SlidePrompt]`. Asks the LLM for one prompt per beat; each `image_prompt` must include house-style + "native 1024x1536 portrait" + the brandmark instruction. `on_image_text` honors `quote_mode`: `own` → spread `job_input.quote_copy` across slides; `agent` → LLM-written; `none` → all `None`. `use_setting_ref = (job_input.setting_choice == "keep")` for every slide.

- [ ] **Step 1: Write the failing test** `backend/tests/test_prompt_build.py`

```python
import unittest
from app.models import JobInput, MatchResult
from app.pipeline.prompt_build import build_slide_prompts
from tests.fakes import FakeLLM


def ji(**kw):
    base = dict(device_id="d", delivery_contact="c", creator_name="A", partner_name="B",
                relationship="together", setting_choice="keep", quote_mode="agent",
                quote_copy=None, photo_paths=["p.jpg"], audio_path="a.webm")
    base.update(kw); return JobInput(**base)


MATCH = MatchResult(pattern_id="p1", slide_count=2, beats=["first glance", "still here"])


class PromptBuildTests(unittest.TestCase):
    def test_agent_mode_uses_llm_text_and_brandmark(self):
        llm = FakeLLM(responses=[{"slides": [
            {"image_prompt": "two people, rain", "on_image_text": "the first glance"},
            {"image_prompt": "two people, older", "on_image_text": "still here"},
        ]}])
        prompts = build_slide_prompts(MATCH, ji(quote_mode="agent"), llm)
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0].on_image_text, "the first glance")
        self.assertIn("@a.storyof.two", prompts[0].image_prompt)
        self.assertTrue(prompts[0].use_setting_ref)

    def test_none_mode_has_no_text(self):
        llm = FakeLLM(responses=[{"slides": [
            {"image_prompt": "a", "on_image_text": "x"},
            {"image_prompt": "b", "on_image_text": "y"},
        ]}])
        prompts = build_slide_prompts(MATCH, ji(quote_mode="none"), llm)
        self.assertTrue(all(p.on_image_text is None for p in prompts))

    def test_own_mode_uses_user_copy(self):
        llm = FakeLLM(responses=[{"slides": [{"image_prompt": "a", "on_image_text": "ignored"},
                                             {"image_prompt": "b", "on_image_text": "ignored"}]}])
        prompts = build_slide_prompts(MATCH, ji(quote_mode="own", quote_copy="our forever | and a day"), llm)
        self.assertEqual(prompts[0].on_image_text, "our forever")
        self.assertEqual(prompts[1].on_image_text, "and a day")

    def test_fresh_setting_disables_ref(self):
        llm = FakeLLM(responses=[{"slides": [{"image_prompt": "a", "on_image_text": None},
                                             {"image_prompt": "b", "on_image_text": None}]}])
        prompts = build_slide_prompts(MATCH, ji(setting_choice="fresh", quote_mode="none"), llm)
        self.assertFalse(any(p.use_setting_ref for p in prompts))
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_prompt_build -v`
Expected: FAIL (`No module named 'app.pipeline.prompt_build'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/prompt_build.py`

```python
from __future__ import annotations

from app.models import JobInput, MatchResult, SlidePrompt
from app.providers.base import LLMProvider

_SYSTEM = (
    "You are the Prompt Room for A Story of Two. For each emotional beat, write an image-generation "
    "prompt for a hand-drawn, warm, paper-textured romantic illustration in the A Story of Two house "
    "style. Respond ONLY as JSON: {\"slides\": [{\"image_prompt\": str, \"on_image_text\": str}]} "
    "with one entry per beat, in order."
)


def _style_suffix(brandmark: str) -> str:
    return (f" Hand-drawn A Story of Two house style, warm paper texture, soft line art. "
            f"Native 1024x1536 portrait. Include a tiny low-contrast handwritten "
            f"'{brandmark}' brandmark in the top-right corner.")


def build_slide_prompts(match: MatchResult, job_input: JobInput, llm: LLMProvider,
                        brandmark: str = "@a.storyof.two") -> list[SlidePrompt]:
    prompt = (
        f"Couple: {job_input.creator_name} & {job_input.partner_name}.\n"
        f"Beats (in order): {match.beats}\n"
        f"Write {match.slide_count} slides."
    )
    data = llm.reason_json(_SYSTEM, prompt)
    slides = list(data.get("slides", []))[:match.slide_count]
    while len(slides) < match.slide_count:
        slides.append({"image_prompt": "", "on_image_text": None})

    own_lines = []
    if job_input.quote_mode == "own" and job_input.quote_copy:
        own_lines = [s.strip() for s in job_input.quote_copy.split("|")]

    use_ref = job_input.setting_choice == "keep"
    out: list[SlidePrompt] = []
    for i, s in enumerate(slides):
        if job_input.quote_mode == "none":
            text = None
        elif job_input.quote_mode == "own":
            text = own_lines[i] if i < len(own_lines) else None
        else:  # agent
            text = s.get("on_image_text")
        out.append(SlidePrompt(
            index=i,
            image_prompt=(s.get("image_prompt", "") + _style_suffix(brandmark)),
            on_image_text=text,
            use_setting_ref=use_ref,
        ))
    return out
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_prompt_build -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/prompt_build.py backend/tests/test_prompt_build.py
git commit -m "feat(backend): slide prompt builder (quote modes + setting + brandmark) with tests"
```

---

## Task 9: Transcription stage

**Files:**
- Create: `backend/app/pipeline/transcribe.py`, `backend/tests/test_transcribe.py`

**Interfaces:**
- Consumes: `LLMProvider`.
- Produces: `story_from_audio(audio_bytes: bytes, mime_type: str, llm: LLMProvider) -> str`. Returns the transcript; raises `ValueError("empty transcript")` if the provider returns blank (so the pipeline can mark the job failed with a clear reason).

- [ ] **Step 1: Write the failing test** `backend/tests/test_transcribe.py`

```python
import unittest
from app.pipeline.transcribe import story_from_audio
from tests.fakes import FakeLLM


class TranscribeTests(unittest.TestCase):
    def test_returns_transcript(self):
        self.assertEqual(story_from_audio(b"x", "audio/webm", FakeLLM(transcript="we met")), "we met")

    def test_blank_raises(self):
        with self.assertRaises(ValueError):
            story_from_audio(b"x", "audio/webm", FakeLLM(transcript="   "))
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_transcribe -v`
Expected: FAIL (`No module named 'app.pipeline.transcribe'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/transcribe.py`

```python
from __future__ import annotations

from app.providers.base import LLMProvider


def story_from_audio(audio_bytes: bytes, mime_type: str, llm: LLMProvider) -> str:
    text = (llm.transcribe(audio_bytes, mime_type) or "").strip()
    if not text:
        raise ValueError("empty transcript")
    return text
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_transcribe -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/transcribe.py backend/tests/test_transcribe.py
git commit -m "feat(backend): transcription stage with tests"
```

---

## Task 10: Render stage

**Files:**
- Create: `backend/app/pipeline/render.py`, `backend/tests/test_render.py`

**Interfaces:**
- Consumes: `Renderer`, `app.models.SlidePrompt`.
- Produces: `render_slide(prompt: SlidePrompt, renderer: Renderer, size: str, style_refs: list[bytes], setting_ref: bytes | None) -> bytes`. Assembles the reference list (style refs always; the setting photo only when `prompt.use_setting_ref` and `setting_ref` is provided) and calls `renderer.render`.

- [ ] **Step 1: Write the failing test** `backend/tests/test_render.py`

```python
import unittest
from app.models import SlidePrompt
from app.pipeline.render import render_slide
from tests.fakes import FakeRenderer


class RenderTests(unittest.TestCase):
    def test_render_returns_bytes_and_passes_prompt(self):
        r = FakeRenderer(image=b"IMG")
        sp = SlidePrompt(index=0, image_prompt="draw", on_image_text=None, use_setting_ref=False)
        out = render_slide(sp, r, "1024x1536", style_refs=[], setting_ref=None)
        self.assertEqual(out, b"IMG")
        self.assertEqual(r.prompts, ["draw"])

    def test_setting_ref_included_only_when_requested(self):
        captured = {}

        class RefSpy(FakeRenderer):
            def render(self, prompt, ref_images, size):
                captured["refs"] = list(ref_images)
                return super().render(prompt, ref_images, size)

        sp_keep = SlidePrompt(index=0, image_prompt="x", on_image_text=None, use_setting_ref=True)
        render_slide(sp_keep, RefSpy(), "1024x1536", style_refs=[b"style"], setting_ref=b"photo")
        self.assertEqual(captured["refs"], [b"style", b"photo"])

        sp_fresh = SlidePrompt(index=0, image_prompt="x", on_image_text=None, use_setting_ref=False)
        render_slide(sp_fresh, RefSpy(), "1024x1536", style_refs=[b"style"], setting_ref=b"photo")
        self.assertEqual(captured["refs"], [b"style"])
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_render -v`
Expected: FAIL (`No module named 'app.pipeline.render'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/render.py`

```python
from __future__ import annotations

from app.models import SlidePrompt
from app.providers.base import Renderer


def render_slide(prompt: SlidePrompt, renderer: Renderer, size: str,
                 style_refs: list[bytes], setting_ref: bytes | None) -> bytes:
    refs = list(style_refs)
    if prompt.use_setting_ref and setting_ref is not None:
        refs.append(setting_ref)
    return renderer.render(prompt.image_prompt, refs, size)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_render -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/render.py backend/tests/test_render.py
git commit -m "feat(backend): render stage with tests"
```

---

## Task 11: Vision QA + bounded retry

**Files:**
- Create: `backend/app/pipeline/qa.py`, `backend/tests/test_qa.py`

**Interfaces:**
- Consumes: `LLMProvider`, `Renderer`, `app.models.SlidePrompt`, `app.providers.base.QAResult`, `app.pipeline.render.render_slide`.
- Produces: `qa_slide(image: bytes, prompt: SlidePrompt, llm: LLMProvider) -> QAResult` (LLM vision check → `{passed: bool, reason: str}`); `render_with_qa(prompt, renderer, llm, size, style_refs, setting_ref, max_retries=2) -> bytes` — renders, QA-checks, retries up to `max_retries` on failure, raises `RuntimeError(reason)` if it still fails (never returns off-brand art).

- [ ] **Step 1: Write the failing test** `backend/tests/test_qa.py`

```python
import unittest
from app.models import SlidePrompt
from app.providers.base import QAResult
from app.pipeline.qa import qa_slide, render_with_qa
from tests.fakes import FakeLLM, FakeRenderer


SP = SlidePrompt(index=0, image_prompt="draw", on_image_text="hi", use_setting_ref=False)


class QATests(unittest.TestCase):
    def test_qa_slide_parses_pass(self):
        llm = FakeLLM(responses=[{"passed": True, "reason": "on style"}])
        res = qa_slide(b"img", SP, llm)
        self.assertIsInstance(res, QAResult)
        self.assertTrue(res.passed)

    def test_render_with_qa_returns_on_first_pass(self):
        llm = FakeLLM(responses=[{"passed": True, "reason": "ok"}])
        r = FakeRenderer(image=b"GOOD")
        out = render_with_qa(SP, r, llm, "1024x1536", [], None, max_retries=2)
        self.assertEqual(out, b"GOOD")
        self.assertEqual(len(r.prompts), 1)            # no retry

    def test_render_with_qa_retries_then_succeeds(self):
        llm = FakeLLM(responses=[{"passed": False, "reason": "yellow cast"},
                                 {"passed": True, "reason": "fixed"}])
        r = FakeRenderer(image=b"IMG")
        out = render_with_qa(SP, r, llm, "1024x1536", [], None, max_retries=2)
        self.assertEqual(out, b"IMG")
        self.assertEqual(len(r.prompts), 2)            # one retry

    def test_render_with_qa_raises_after_cap(self):
        llm = FakeLLM(responses=[{"passed": False, "reason": "bad"}] * 5)
        with self.assertRaises(RuntimeError):
            render_with_qa(SP, FakeRenderer(), llm, "1024x1536", [], None, max_retries=2)
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_qa -v`
Expected: FAIL (`No module named 'app.pipeline.qa'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/qa.py`

```python
from __future__ import annotations

from app.models import SlidePrompt
from app.pipeline.render import render_slide
from app.providers.base import LLMProvider, QAResult, Renderer

_SYSTEM = (
    "You are Image QA for A Story of Two. Check whether the image is on-brand: hand-drawn warm "
    "house style, the @a.storyof.two brandmark present top-right, any on-image text correct and "
    "legible, no obvious artifacts. Respond ONLY as JSON: {\"passed\": bool, \"reason\": str}."
)


def qa_slide(image: bytes, prompt: SlidePrompt, llm: LLMProvider) -> QAResult:
    ask = f"Intended on-image text: {prompt.on_image_text!r}. Prompt: {prompt.image_prompt}"
    data = llm.reason_json(_SYSTEM, ask, image_bytes=[image])
    return QAResult(passed=bool(data.get("passed", False)), reason=str(data.get("reason", "")))


def render_with_qa(prompt: SlidePrompt, renderer: Renderer, llm: LLMProvider, size: str,
                   style_refs: list[bytes], setting_ref: bytes | None, max_retries: int = 2) -> bytes:
    last = "no attempt"
    for _ in range(max_retries + 1):
        image = render_slide(prompt, renderer, size, style_refs, setting_ref)
        result = qa_slide(image, prompt, llm)
        if result.passed:
            return image
        last = result.reason
    raise RuntimeError(f"QA failed after retries: {last}")
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_qa -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/qa.py backend/tests/test_qa.py
git commit -m "feat(backend): vision QA + bounded retry with tests"
```

---

## Task 12: Carousel assembly

**Files:**
- Create: `backend/app/pipeline/assemble.py`, `backend/tests/test_assemble.py`

**Interfaces:**
- Consumes: `app.models.Slide`, `app.models.SlidePrompt`.
- Produces: `assemble_slides(prompts: list[SlidePrompt], images: list[bytes], save_blob) -> list[Slide]` where `save_blob(name: str, data: bytes) -> str` persists a slide image and returns its path; output `Slide`s are ordered by `index`, captioned from each prompt's `on_image_text`.

- [ ] **Step 1: Write the failing test** `backend/tests/test_assemble.py`

```python
import unittest
from app.models import SlidePrompt
from app.pipeline.assemble import assemble_slides


class AssembleTests(unittest.TestCase):
    def test_assembles_ordered_captioned_slides(self):
        saved = {}

        def save_blob(name, data):
            saved[name] = data
            return f"/blobs/{name}"

        prompts = [
            SlidePrompt(index=0, image_prompt="a", on_image_text="one", use_setting_ref=False),
            SlidePrompt(index=1, image_prompt="b", on_image_text=None, use_setting_ref=False),
        ]
        images = [b"IMG0", b"IMG1"]
        slides = assemble_slides(prompts, images, save_blob)
        self.assertEqual([s.index for s in slides], [0, 1])
        self.assertEqual(slides[0].caption, "one")
        self.assertIsNone(slides[1].caption)
        self.assertEqual(slides[0].image_path, "/blobs/slide_0.png")
        self.assertEqual(saved["slide_1.png"], b"IMG1")
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_assemble -v`
Expected: FAIL (`No module named 'app.pipeline.assemble'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/assemble.py`

```python
from __future__ import annotations

from typing import Callable

from app.models import Slide, SlidePrompt


def assemble_slides(prompts: list[SlidePrompt], images: list[bytes],
                    save_blob: Callable[[str, bytes], str]) -> list[Slide]:
    slides: list[Slide] = []
    for prompt, image in zip(sorted(prompts, key=lambda p: p.index), images):
        path = save_blob(f"slide_{prompt.index}.png", image)
        slides.append(Slide(index=prompt.index, image_path=path, caption=prompt.on_image_text))
    return slides
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_assemble -v`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/assemble.py backend/tests/test_assemble.py
git commit -m "feat(backend): carousel assembly with tests"
```

---

## Task 13: Pipeline orchestration (`run_job`)

**Files:**
- Create: `backend/app/pipeline/run.py`, `backend/tests/test_run.py`

**Interfaces:**
- Consumes: everything above — `JobStore`, `LLMProvider`, `Renderer`, `match_winner`, `build_slide_prompts`, `story_from_audio`, `render_with_qa`, `assemble_slides`, `load_winner_bank`, `house_style_ref_paths`.
- Produces: `run_job(job_id: str, store: JobStore, llm: LLMProvider, renderer: Renderer, *, bank=None, size="1024x1536", min_slides=3, max_slides=5, max_retries=2) -> None`. Loads the job, sets `RUNNING`, runs stages 1–6 reading inputs via `store.read_blob` and saving outputs via `store.save_blob`, sets `READY` with `slides`; on any exception sets `FAILED` with `error` and never raises.

- [ ] **Step 1: Write the failing test** `backend/tests/test_run.py`

```python
import tempfile
import unittest
from pathlib import Path

from app.models import Job, JobInput, JobStatus
from app.store import JobStore
from app.pipeline.run import run_job
from tests.fakes import FakeLLM, FakeRenderer


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.store = JobStore(db_path=root / "j.db", blob_root=root / "b")

    def tearDown(self):
        self.tmp.cleanup()

    def _job(self, **kw):
        ji = JobInput(device_id="d", delivery_contact="c", creator_name="A", partner_name="B",
                      relationship="together", setting_choice="fresh", quote_mode="agent",
                      quote_copy=None, photo_paths=[], audio_path="", **kw)
        job = Job.new(ji)
        audio = self.store.save_blob(job.id, "voice.webm", b"AUDIO")
        job.input.audio_path = audio
        self.store.create(job)
        return job

    def _llm(self):
        return FakeLLM(transcript="we met in the rain", responses=[
            {"pattern_id": "p1", "slide_count": 2, "beats": ["glance", "stay"]},          # match
            {"slides": [{"image_prompt": "a", "on_image_text": "t0"},
                        {"image_prompt": "b", "on_image_text": "t1"}]},                    # prompt build
            {"passed": True, "reason": "ok"},                                              # qa slide 0
            {"passed": True, "reason": "ok"},                                              # qa slide 1
        ])

    def test_happy_path_reaches_ready(self):
        job = self._job()
        run_job(job.id, self.store, self._llm(), FakeRenderer(image=b"IMG"),
                bank=[{"caption": "x", "childCount": 2, "commentsCount": 1, "commentSendProxy": 1}])
        got = self.store.get(job.id)
        self.assertEqual(got.status, JobStatus.READY)
        self.assertEqual(len(got.slides), 2)
        self.assertEqual(got.story_text, "we met in the rain")

    def test_transcription_failure_marks_failed(self):
        job = self._job()
        run_job(job.id, self.store, FakeLLM(transcript="  "), FakeRenderer(),
                bank=[{"caption": "x", "childCount": 2}])
        got = self.store.get(job.id)
        self.assertEqual(got.status, JobStatus.FAILED)
        self.assertIn("transcript", (got.error or "").lower())
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_run -v`
Expected: FAIL (`No module named 'app.pipeline.run'`).

- [ ] **Step 3: Implement** `backend/app/pipeline/run.py`

```python
from __future__ import annotations

from app.data_refs import house_style_ref_paths, load_winner_bank
from app.models import JobStatus
from app.pipeline.assemble import assemble_slides
from app.pipeline.match import match_winner
from app.pipeline.prompt_build import build_slide_prompts
from app.pipeline.qa import render_with_qa
from app.pipeline.transcribe import story_from_audio
from app.providers.base import LLMProvider, Renderer
from app.store import JobStore


def run_job(job_id: str, store: JobStore, llm: LLMProvider, renderer: Renderer, *,
            bank=None, size: str = "1024x1536", min_slides: int = 3, max_slides: int = 5,
            max_retries: int = 2) -> None:
    job = store.get(job_id)
    if job is None:
        return
    try:
        job.status = JobStatus.RUNNING
        job.touch()
        store.save(job)

        ji = job.input
        audio = store.read_blob(ji.audio_path)
        story = story_from_audio(audio, "audio/webm", llm)
        job.story_text = story
        store.save(job)

        bank = bank if bank is not None else load_winner_bank()
        match = match_winner(story, ji.creator_name, ji.partner_name, ji.relationship,
                             bank, llm, min_slides=min_slides, max_slides=max_slides)
        job.match = match
        store.save(job)

        prompts = build_slide_prompts(match, ji, llm)

        style_refs = [p.read_bytes() for p in house_style_ref_paths()]
        setting_ref = store.read_blob(ji.photo_paths[0]) if ji.photo_paths else None

        images = [render_with_qa(p, renderer, llm, size, style_refs, setting_ref, max_retries)
                  for p in prompts]

        job.slides = assemble_slides(prompts, images,
                                     lambda name, data: store.save_blob(job_id, name, data))
        job.status = JobStatus.READY
        job.touch()
        store.save(job)
    except Exception as exc:  # never raise out of the worker
        job.status = JobStatus.FAILED
        job.error = str(exc)
        job.touch()
        store.save(job)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_run -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/pipeline/run.py backend/tests/test_run.py
git commit -m "feat(backend): pipeline orchestration run_job with tests"
```

---

## Task 14: HTTP API (submit + poll) with background worker

**Files:**
- Modify: `backend/app/main.py`
- Create: `backend/app/deps.py`, `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `JobStore`, `Job`, `JobInput`, `run_job`, providers.
- Produces: `POST /jobs` (multipart form: `photos` files[], `audio` file, plus form fields `device_id, delivery_contact, creator_name, partner_name, relationship, setting_choice, quote_mode, quote_copy`) → `{"job_id": str}` (creates job QUEUED, saves blobs, schedules `run_job` via `BackgroundTasks`). `GET /jobs/{id}` → `{"status": str, "slides": [{"index","caption","url"}], "error": str|None}` where `url` is `/jobs/{id}/slides/{index}.png`. `GET /jobs/{id}/slides/{index}.png` streams the PNG. `app.deps.get_store()`, `get_llm()`, `get_renderer()` are FastAPI dependency providers, overridable in tests.

- [ ] **Step 1: Write the failing test** `backend/tests/test_api.py` (override deps with fakes + a worker that runs synchronously)

```python
import io
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import deps
from app.main import app
from app.store import JobStore
from tests.fakes import FakeLLM, FakeRenderer


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.store = JobStore(db_path=root / "j.db", blob_root=root / "b")
        self.llm = FakeLLM(transcript="we met", responses=[
            {"pattern_id": "p", "slide_count": 2, "beats": ["x", "y"]},
            {"slides": [{"image_prompt": "a", "on_image_text": "t0"},
                        {"image_prompt": "b", "on_image_text": "t1"}]},
            {"passed": True, "reason": "ok"}, {"passed": True, "reason": "ok"},
        ])
        app.dependency_overrides[deps.get_store] = lambda: self.store
        app.dependency_overrides[deps.get_llm] = lambda: self.llm
        app.dependency_overrides[deps.get_renderer] = lambda: FakeRenderer(image=b"IMG")
        app.dependency_overrides[deps.get_bank] = lambda: [{"caption": "x", "childCount": 2}]
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.tmp.cleanup()

    def _submit(self):
        files = [("photos", ("p.jpg", io.BytesIO(b"PHOTO"), "image/jpeg")),
                 ("audio", ("v.webm", io.BytesIO(b"AUDIO"), "audio/webm"))]
        data = dict(device_id="d", delivery_contact="c", creator_name="A", partner_name="B",
                    relationship="together", setting_choice="fresh", quote_mode="agent", quote_copy="")
        return self.client.post("/jobs", files=files, data=data)

    def test_submit_returns_job_id(self):
        r = self._submit()
        self.assertEqual(r.status_code, 200)
        self.assertIn("job_id", r.json())

    def test_poll_reaches_ready_with_slides(self):
        job_id = self._submit().json()["job_id"]
        # BackgroundTasks run synchronously after the response in TestClient.
        r = self.client.get(f"/jobs/{job_id}")
        body = r.json()
        self.assertEqual(body["status"], "ready")
        self.assertEqual(len(body["slides"]), 2)
        self.assertTrue(body["slides"][0]["url"].endswith("/slides/0.png"))

    def test_slide_image_streams(self):
        job_id = self._submit().json()["job_id"]
        r = self.client.get(f"/jobs/{job_id}/slides/0.png")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, b"IMG")

    def test_unknown_job_404(self):
        self.assertEqual(self.client.get("/jobs/nope").status_code, 404)
```

- [ ] **Step 2: Run — expect failure**

Run: `cd backend && python3 -m unittest tests.test_api -v`
Expected: FAIL (`No module named 'app.deps'` / route missing).

- [ ] **Step 3: Implement** `backend/app/deps.py`

```python
from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.data_refs import load_winner_bank
from app.providers.gemini import GeminiProvider
from app.providers.openai_renderer import OpenAIRenderer
from app.store import JobStore


@lru_cache
def get_store() -> JobStore:
    return JobStore(db_path=settings.data_dir / "jobs.db", blob_root=settings.data_dir / "blobs")


def get_llm():
    return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)


def get_renderer():
    return OpenAIRenderer(api_key=settings.openai_api_key, model=settings.image_model)


@lru_cache
def get_bank() -> list[dict]:
    return load_winner_bank()
```

- [ ] **Step 4: Implement the routes** — replace `backend/app/main.py`

```python
from __future__ import annotations

import io

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app import deps
from app.config import settings
from app.models import Job, JobInput
from app.pipeline.run import run_job

app = FastAPI(title="A Story of Two — Generation Backend")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/jobs")
async def submit_job(
    background: BackgroundTasks,
    device_id: str = Form(...),
    delivery_contact: str = Form(...),
    creator_name: str = Form(...),
    partner_name: str = Form(...),
    relationship: str = Form(...),
    setting_choice: str = Form(...),
    quote_mode: str = Form(...),
    quote_copy: str = Form(""),
    photos: list[UploadFile] = File(default=[]),
    audio: UploadFile = File(...),
    store=Depends(deps.get_store),
    llm=Depends(deps.get_llm),
    renderer=Depends(deps.get_renderer),
    bank=Depends(deps.get_bank),
) -> dict:
    job = Job.new(JobInput(
        device_id=device_id, delivery_contact=delivery_contact, creator_name=creator_name,
        partner_name=partner_name, relationship=relationship, setting_choice=setting_choice,
        quote_mode=quote_mode, quote_copy=(quote_copy or None), photo_paths=[], audio_path="",
    ))
    store.create(job)
    photo_paths = []
    for i, up in enumerate(photos):
        photo_paths.append(store.save_blob(job.id, f"photo_{i}.jpg", await up.read()))
    job.input.photo_paths = photo_paths
    job.input.audio_path = store.save_blob(job.id, "voice.webm", await audio.read())
    store.save(job)

    background.add_task(run_job, job.id, store, llm, renderer,
                        bank=bank, size=settings.image_size,
                        min_slides=settings.min_slides, max_slides=settings.max_slides)
    return {"job_id": job.id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str, store=Depends(deps.get_store)) -> dict:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "status": job.status.value,
        "error": job.error,
        "slides": [{"index": s.index, "caption": s.caption,
                    "url": f"/jobs/{job_id}/slides/{s.index}.png"} for s in job.slides],
    }


@app.get("/jobs/{job_id}/slides/{index}.png")
def get_slide(job_id: str, index: int, store=Depends(deps.get_store)):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    match = [s for s in job.slides if s.index == index]
    if not match:
        raise HTTPException(status_code=404, detail="slide not found")
    return StreamingResponse(io.BytesIO(store.read_blob(match[0].image_path)), media_type="image/png")
```

- [ ] **Step 5: Run — expect pass**

Run: `cd backend && python3 -m unittest tests.test_api -v`
Expected: PASS (4 tests). If `test_poll_reaches_ready_with_slides` sees `queued`/`running` instead of `ready`, it means BackgroundTasks didn't run inline — wrap the client in a `with TestClient(app) as client:` context in the test so tasks flush, and re-run.

- [ ] **Step 6: Commit**

```bash
git add backend/app/deps.py backend/app/main.py backend/tests/test_api.py
git commit -m "feat(backend): /jobs submit+poll API with background worker and tests"
```

---

## Task 15: Config validation, live-smoke, full suite

**Files:**
- Create: `backend/scripts/live_smoke.py`
- Modify: `backend/README.md`

**Interfaces:**
- Produces: `backend/scripts/live_smoke.py` — a manual, env-gated end-to-end run against REAL OpenAI + Gemini (requires `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ASTORY_LIVE_SMOKE=1`); prints the job status + writes slides to `backend/data/smoke/`. Not imported by any test.

- [ ] **Step 1: Run the full unit/integration suite**

Run: `cd backend && python3 -m unittest -v`
Expected: every test from Tasks 1–14 passes, no network used.

- [ ] **Step 2: Create** `backend/scripts/live_smoke.py`

```python
"""Manual end-to-end smoke against real providers. Run:
    ASTORY_LIVE_SMOKE=1 python3 scripts/live_smoke.py path/to/voice.webm
Requires OPENAI_API_KEY and GEMINI_API_KEY in .env.local.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from app.config import settings
from app.deps import get_bank
from app.models import Job, JobInput
from app.pipeline.run import run_job
from app.providers.gemini import GeminiProvider
from app.providers.openai_renderer import OpenAIRenderer
from app.store import JobStore


def main() -> int:
    if os.environ.get("ASTORY_LIVE_SMOKE") != "1":
        print("Refusing to run: set ASTORY_LIVE_SMOKE=1 to call real paid/free APIs.")
        return 2
    if not settings.openai_api_key or not settings.gemini_api_key:
        print("Missing OPENAI_API_KEY or GEMINI_API_KEY in .env.local.")
        return 2
    audio_path = Path(sys.argv[1])
    store = JobStore(db_path=settings.data_dir / "smoke/jobs.db", blob_root=settings.data_dir / "smoke")
    job = Job.new(JobInput(device_id="smoke", delivery_contact="me", creator_name="Aarav",
                           partner_name="Mira", relationship="together", setting_choice="fresh",
                           quote_mode="agent", quote_copy=None, photo_paths=[], audio_path=""))
    store.create(job)
    job.input.audio_path = store.save_blob(job.id, "voice.webm", audio_path.read_bytes())
    store.save(job)
    run_job(job.id, store, GeminiProvider(settings.gemini_api_key, settings.gemini_model),
            OpenAIRenderer(settings.openai_api_key, settings.image_model),
            bank=get_bank(), size=settings.image_size)
    done = store.get(job.id)
    print("status:", done.status.value, "| error:", done.error, "| slides:", len(done.slides))
    return 0 if done.status.value == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Append run/smoke docs to `backend/README.md`**

```markdown
## Live smoke (manual, costs OpenAI credits)
    . .venv/bin/activate
    ASTORY_LIVE_SMOKE=1 python3 scripts/live_smoke.py path/to/voice.webm
Outputs to backend/data/smoke/. Requires OPENAI_API_KEY + GEMINI_API_KEY in .env.local.
```

- [ ] **Step 4: Commit**

```bash
git add backend/scripts/live_smoke.py backend/README.md
git commit -m "feat(backend): env-gated live-smoke script + docs"
```

---

## Self-review notes (author check vs. spec)

- **Spec coverage:** §3 stack → Tasks 5 (Gemini), 6 (OpenAI), Global Constraints (no Claude). §4 architecture → Tasks 0/14 (FastAPI + background worker + store). §5 stages 1–6 → Tasks 9,7,8,10/11,12,13. §7 app changes → **separate next plan** (see below). §8 data model → Tasks 1,2. §9 error handling → Tasks 9,11,13 (transcript fail, QA cap, never-raise worker). §10 testing → unittest throughout + Task 15 live-smoke. §11 caveats → carried (QA-retry, swappable providers).
- **No Claude:** only `google-genai` + `openai` SDKs are added (Task 0 requirements). Verified.
- **Type consistency:** `LLMProvider.reason_json`/`transcribe`, `Renderer.render`, `MatchResult`, `SlidePrompt`, `Slide`, `Job(status, slides, story_text, match, error)` used identically across Tasks 1→14.
- **Test framework:** `unittest` everywhere; `python3 -m unittest` runner; no pytest. Verified vs. repo convention.

## Out of scope here → the immediate NEXT plan (app integration)

A separate plan wires the React app (`app/`) to this backend:
1. `app/src/services/api.ts` — `submitJob(formData)` → `POST /jobs`; `getJob(id)` → poll.
2. Replace `services/fakeGeneration.ts` usage: `PrintingScreen` submits on entry, polls `GET /jobs/{id}`, reveals real slides on `ready`, shows a graceful `failed` state.
3. Add **delivery-contact** capture + **setting** ("keep your setting?") and **quote** ("your words / we'll write it / no text") choices to the flow + session.
4. Point `RevealScreen`/`Carousel` at the returned slide URLs; keep rate + send-only unchanged.
5. CORS config on the backend for the app origin; env-based backend base URL in the app.
