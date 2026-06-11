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

ClaimType = Literal[
    "identity_rule",
    "style_rule",
    "prompt_pattern",
    "failure_mode",
    "creator_preference",
    "production_constraint",
    "operational_fact",
]
RiskLevel = Literal["low", "medium", "high"]
PromotionPolicy = Literal["auto_apply", "human_review", "quarantine"]
ClaimStatus = Literal["candidate", "quarantined", "promoted", "deferred"]


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
    to_page_id: str | None
    relation: str
    evidence_path: str
    from_path: str | None = None
    to_path: str | None = None
    to_id: str | None = None


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


@dataclass(frozen=True)
class MemoryClaim:
    claim_id: str
    run_id: str
    claim_type: ClaimType
    text: str
    evidence_paths: list[str]
    confidence: float
    scope: str
    risk_level: RiskLevel
    promotion_policy: PromotionPolicy
    status: ClaimStatus
    applies_to: list[str] = field(default_factory=list)
    rationale: str = ""


@dataclass(frozen=True)
class MemoryLedgerEvent:
    event_id: str
    claim_id: str
    run_id: str
    action: str
    from_status: str | None
    to_status: str
    promotion_policy: PromotionPolicy
    evidence_paths: list[str]
    rationale: str


@dataclass(frozen=True)
class LearningReport:
    run_id: str
    claims: list[MemoryClaim]
    summary: dict[str, int]
