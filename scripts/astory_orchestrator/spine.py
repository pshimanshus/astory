"""The A Story workflow spine: the 33-state machine encoded as data.

This mirrors the State Machine in `.agents/skills/astory/SKILL.md`. A test
(`tests/test_astory_orchestrator_spine.py`) asserts the two stay in sync. This
module is pure data + read helpers; it does not execute a run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

StateKind = Literal[
    "control",
    "deterministic",
    "creative",
    "gate",
    "hitl",
    "terminal",
]

# Run-relative directories any `produces` path must live under.
RUN_SUBDIRS = (
    "input/",
    "planning/",
    "debates/",
    "prompts/",
    "references-used/",
    "images/",
    "exports/",
    "evals/",
    "logs/",
    "docs/",
    "reports/",
    "state/",
)


@dataclass(frozen=True)
class StateSpec:
    name: str
    index: int
    kind: StateKind
    next: str | None
    produces: tuple[str, ...] = ()


STATES: tuple[StateSpec, ...] = (
    StateSpec("INIT_RUN", 1, "control", "PARSE_CREATIVE_INPUT"),
    StateSpec(
        "PARSE_CREATIVE_INPUT", 2, "control", "DETERMINE_IDEA_MODE",
        ("input/creative_brief.json",),
    ),
    StateSpec("DETERMINE_IDEA_MODE", 3, "control", "REFERENCE_PREFLIGHT"),
    StateSpec(
        "REFERENCE_PREFLIGHT", 4, "deterministic", "MEMORY_RECALL_PREFLIGHT",
        ("planning/identity_preflight.md", "planning/style_preflight.md"),
    ),
    StateSpec(
        "MEMORY_RECALL_PREFLIGHT", 5, "deterministic", "DISCOVER_AND_ASSIGN_AGENTS",
        ("planning/memory_recall.md",),
    ),
    StateSpec(
        "DISCOVER_AND_ASSIGN_AGENTS", 6, "gate", "GENERATE_OR_REFINE_IDEAS",
        ("debates/agent_assignment_matrix.md",),
    ),
    StateSpec(
        "GENERATE_OR_REFINE_IDEAS", 7, "creative", "SCORE_IDEAS",
        (
            "debates/idea_room/agent_01_candidates.json",
            "debates/idea_room/agent_02_candidates.json",
            "debates/idea_room/agent_03_candidates.json",
            "planning/idea_candidates.json",
        ),
    ),
    StateSpec(
        "SCORE_IDEAS", 8, "creative", "SELECT_BEST_IDEA",
        (
            "debates/idea_room/cross_critique.md",
            "debates/idea_room/repair_round.md",
            "debates/idea_room/final_scoreboard.json",
            "planning/novelty_candidate_ledger.json",
            "evals/idea_engagement_eval.json",
            "evals/idea_engagement_report.md",
        ),
    ),
    StateSpec(
        "SELECT_BEST_IDEA", 9, "creative", "CREATE_SCENE_LANDING_PREVIEW",
        (
            "planning/selected_idea.json",
            "planning/source_winner_remix_contract.json",
            "planning/rejected_ideas.md",
        ),
    ),
    StateSpec(
        "CREATE_SCENE_LANDING_PREVIEW", 10, "creative", "HITL_IDEA_LOCK",
        (
            "planning/scene_landing_preview.md",
            "planning/source_winner_novelty_model.json",
            "planning/winner_landing_comparison.md",
        ),
    ),
    StateSpec(
        "HITL_IDEA_LOCK", 11, "hitl", "GENERATE_STORY_CONCEPT",
        ("docs/approvals.md",),
    ),
    StateSpec(
        "GENERATE_STORY_CONCEPT", 12, "creative", "DECIDE_SLIDE_COUNT",
        ("planning/story_concept.json",),
    ),
    StateSpec(
        "DECIDE_SLIDE_COUNT", 13, "creative", "GENERATE_SLIDE_BEATS",
        ("planning/slide_count_decision.md",),
    ),
    StateSpec(
        "GENERATE_SLIDE_BEATS", 14, "creative", "GENERATE_SCENE_OPTIONS",
        ("planning/slide_beat_map.json",),
    ),
    StateSpec(
        "GENERATE_SCENE_OPTIONS", 15, "creative", "SELECT_AND_ORDER_SLIDES",
        ("planning/scene_options.json",),
    ),
    StateSpec(
        "SELECT_AND_ORDER_SLIDES", 16, "creative", "HITL_STORY_LOCK",
        ("planning/selected_scenes.json", "debates/story_room/story_debate.md"),
    ),
    StateSpec(
        "HITL_STORY_LOCK", 17, "hitl", "CREATE_CHARACTER_BIBLE",
        ("docs/approvals.md",),
    ),
    StateSpec(
        "CREATE_CHARACTER_BIBLE", 18, "creative", "CREATE_STYLE_BIBLE",
        ("planning/character_bible.json",),
    ),
    StateSpec(
        "CREATE_STYLE_BIBLE", 19, "creative", "CREATE_PROMPT_PACK",
        ("planning/style_bible.json",),
    ),
    StateSpec(
        "CREATE_PROMPT_PACK", 20, "creative", "PRE_GENERATION_EVAL",
        (
            "prompts/slide_01_4x5_prompt.txt",
            "prompts/negative_prompt.txt",
            "prompts/prompt_generation_report.md",
        ),
    ),
    StateSpec(
        "PRE_GENERATION_EVAL", 21, "gate", "REVIEW_ROOM_QA",
        (
            "evals/pre_generation_eval.json",
            "evals/pre_generation_eval_report.md",
            "evals/source_winner_alignment_eval.json",
            "debates/prompt_room/prompt_review.md",
        ),
    ),
    StateSpec(
        "REVIEW_ROOM_QA", 22, "gate", "HITL_PROMPT_LOCK",
        ("evals/repo_qa_review.json", "evals/repo_qa_review.md"),
    ),
    StateSpec(
        "HITL_PROMPT_LOCK", 23, "hitl", "LOAD_REFERENCE_IMAGES_IN_CONTEXT",
        ("docs/approvals.md",),
    ),
    StateSpec(
        "LOAD_REFERENCE_IMAGES_IN_CONTEXT", 24, "deterministic",
        "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK",
        (
            "references-used/selected_references.json",
            "evals/imagegen_reference_load_plan.json",
            "evals/imagegen_reference_visibility_proof.json",
        ),
    ),
    StateSpec(
        "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK", 25, "gate",
        "GENERATE_IMAGES_WITH_IMAGEGEN",
        ("evals/repo_qa_review_loop.json",),
    ),
    StateSpec(
        "GENERATE_IMAGES_WITH_IMAGEGEN", 26, "creative", "IMAGE_QUALITY_EVAL",
        ("images/slide_01_4x5_attempt_01_candidate.png",),
    ),
    StateSpec(
        "IMAGE_QUALITY_EVAL", 27, "gate", "REVIEW_ROOM_FINAL_BLOCKER_CHECK",
        (
            "evals/image_quality_eval.json",
            "evals/image_quality_report.md",
            "evals/source_winner_image_alignment.json",
            "debates/image_qa_room/image_qa_debate.md",
        ),
    ),
    StateSpec(
        "REVIEW_ROOM_FINAL_BLOCKER_CHECK", 28, "gate", "RETRY_OR_REVISE_IF_NEEDED",
        ("evals/repo_qa_review.json",),
    ),
    StateSpec("RETRY_OR_REVISE_IF_NEEDED", 29, "control", "FINAL_QA"),
    StateSpec(
        "FINAL_QA", 30, "gate", "EXPORT_AND_PACKAGE",
        ("evals/final_winner_landing_check.json",),
    ),
    StateSpec(
        "EXPORT_AND_PACKAGE", 31, "deterministic", "WRITE_REPORTS",
        ("exports/slide_01_post_4x5.png",),
    ),
    StateSpec(
        "WRITE_REPORTS", 32, "deterministic", "COMPLETE_OR_BLOCKED",
        ("docs/retro.md",),
    ),
    StateSpec("COMPLETE_OR_BLOCKED", 33, "terminal", None),
)

STATE_NAMES: tuple[str, ...] = tuple(s.name for s in STATES)
_BY_NAME: dict[str, StateSpec] = {s.name: s for s in STATES}
HITL_STATES: tuple[str, ...] = tuple(s.name for s in STATES if s.kind == "hitl")
GATE_STATES: tuple[str, ...] = tuple(s.name for s in STATES if s.kind == "gate")


def by_name(name: str) -> StateSpec:
    try:
        return _BY_NAME[name]
    except KeyError:
        raise KeyError(f"unknown spine state: {name!r}")


def is_state(name: str) -> bool:
    return name in _BY_NAME


def next_state(name: str) -> str | None:
    return by_name(name).next


def is_terminal(name: str) -> bool:
    return by_name(name).next is None


def first_state() -> str:
    return STATES[0].name


def validate_spine() -> list[str]:
    """Return a list of structural problems; empty means the spine is valid."""

    problems: list[str] = []

    for position, spec in enumerate(STATES, start=1):
        if spec.index != position:
            problems.append(
                f"index_out_of_order: {spec.name} has index {spec.index}, "
                f"expected {position}"
            )

    if len(STATE_NAMES) != len(set(STATE_NAMES)):
        problems.append("duplicate_state_names")

    for spec in STATES:
        if spec.next is not None and spec.next not in _BY_NAME:
            problems.append(f"unknown_next: {spec.name} -> {spec.next}")

    terminals = [s.name for s in STATES if s.next is None]
    if terminals != [STATES[-1].name]:
        problems.append(f"terminal_set_invalid: {terminals}")

    visited: list[str] = []
    seen: set[str] = set()
    cursor: str | None = STATES[0].name
    while cursor is not None:
        if cursor in seen:
            problems.append(f"cycle_detected_at: {cursor}")
            break
        seen.add(cursor)
        visited.append(cursor)
        cursor = _BY_NAME[cursor].next if cursor in _BY_NAME else None
    if set(visited) != set(STATE_NAMES):
        missing = sorted(set(STATE_NAMES) - set(visited))
        problems.append(f"chain_does_not_cover_all_states: missing={missing}")

    for required in ("HITL_IDEA_LOCK", "HITL_STORY_LOCK", "HITL_PROMPT_LOCK"):
        if required not in _BY_NAME or _BY_NAME[required].kind != "hitl":
            problems.append(f"missing_hitl_state: {required}")

    for spec in STATES:
        for path in spec.produces:
            if not path.startswith(RUN_SUBDIRS):
                problems.append(
                    f"produces_path_outside_run_dirs: {spec.name} -> {path}"
                )

    return problems
