"""Shape-tolerant validators for idea-room artifacts.

The template and real-run schemas diverge (survivors/candidates,
scores.overall/overall_score, threshold/minimum_required_overall_score). These
helpers accept either shape and answer the two questions the runner needs:
what is the selected idea's score, and is each artifact well-formed.
"""

from __future__ import annotations

from typing import Any

MIN_IDEA_SCORE = 4.0


def _entries(scoreboard: Any) -> list[dict[str, Any]]:
    if not isinstance(scoreboard, dict):
        return []
    raw = scoreboard.get("survivors")
    if not isinstance(raw, list):
        raw = scoreboard.get("candidates")
    if not isinstance(raw, list):
        return []
    return [entry for entry in raw if isinstance(entry, dict)]


def _entry_score(entry: dict[str, Any]) -> float | None:
    value = entry.get("overall_score")
    if isinstance(value, (int, float)):
        return float(value)
    scores = entry.get("scores")
    if isinstance(scores, dict) and isinstance(scores.get("overall"), (int, float)):
        return float(scores["overall"])
    return None


def best_overall_score(scoreboard: Any) -> float | None:
    parsed = [s for s in (_entry_score(e) for e in _entries(scoreboard)) if s is not None]
    return max(parsed) if parsed else None


def selected_entry(scoreboard: Any) -> dict[str, Any] | None:
    entries = _entries(scoreboard)
    if not entries:
        return None
    for entry in entries:
        if entry.get("selection_status") == "selected":
            return entry
    if isinstance(scoreboard, dict):
        marker = scoreboard.get("selected") or scoreboard.get("selected_idea_id")
        if marker is not None:
            for entry in entries:
                if marker in (entry.get("title"), entry.get("idea_id"), entry.get("id")):
                    return entry
    scored = [(e, _entry_score(e)) for e in entries]
    scored = [(e, s) for e, s in scored if s is not None]
    if scored:
        return max(scored, key=lambda pair: pair[1])[0]
    return None


def selected_score(scoreboard: Any) -> float | None:
    entry = selected_entry(scoreboard)
    if entry is not None:
        score = _entry_score(entry)
        if score is not None:
            return score
    return best_overall_score(scoreboard)


def threshold(scoreboard: Any) -> float:
    if isinstance(scoreboard, dict):
        for key in ("threshold", "minimum_required_overall_score"):
            value = scoreboard.get(key)
            if isinstance(value, (int, float)):
                return float(value)
    return MIN_IDEA_SCORE


def meets_threshold(scoreboard: Any) -> bool:
    score = selected_score(scoreboard)
    return score is not None and score >= threshold(scoreboard)


def validate_final_scoreboard(data: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["scoreboard_not_object"]
    entries = _entries(data)
    if not entries:
        problems.append("no_idea_entries")
        return problems
    if best_overall_score(data) is None:
        problems.append("no_parseable_overall_score")
    if selected_entry(data) is None:
        problems.append("no_selected_idea")
    return problems


def validate_selected_idea(data: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["selected_idea_not_object"]
    if not (data.get("id") or data.get("selected_idea_id")):
        problems.append("missing_id")
    if not (data.get("title") or data.get("final_title")):
        problems.append("missing_title")
    if not (data.get("one_line_concept") or data.get("final_concept")):
        problems.append("missing_concept")
    return problems


def validate_story_concept(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["story_concept_not_object"]
    problems: list[str] = []
    if not data.get("title"):
        problems.append("missing_title")
    if not (data.get("one_line_summary") or data.get("emotional_hook")):
        problems.append("missing_summary")
    for beat in ("setup", "escalation", "payoff"):
        if not data.get(beat):
            problems.append(f"missing_{beat}")
    return problems


def validate_slide_beat_map(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["slide_beat_map_not_object"]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["no_slides"]
    problems: list[str] = []
    count = data.get("slide_count")
    if isinstance(count, int) and count != len(slides):
        problems.append("slide_count_mismatch")
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict) or not slide.get("exact_on_image_text"):
            problems.append(f"slide_{index}_missing_exact_on_image_text")
    return problems


def validate_selected_scenes(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["selected_scenes_not_object"]
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["no_slides"]
    problems: list[str] = []
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            problems.append(f"slide_{index}_not_object")
            continue
        if not (slide.get("selected_scene_id") or slide.get("selected_scene_option_id")):
            problems.append(f"slide_{index}_missing_selected_scene")
        if not slide.get("exact_on_image_text"):
            problems.append(f"slide_{index}_missing_exact_on_image_text")
    return problems
