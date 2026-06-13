import unittest

from scripts.astory_orchestrator import validate

# Real-run shape (runs/2026-06-10_22-22_heart-rent/debates/idea_room/final_scoreboard.json)
REAL_SCOREBOARD = {
    "selected": "Heart Rent Notice",
    "minimum_required_overall_score": 4.0,
    "candidates": [
        {"title": "Heart Rent Notice", "overall_score": 4.7, "selection_status": "selected"},
        {"title": "Security Deposit", "overall_score": 4.0, "selection_status": "rejected"},
        {"title": "Receipt At The Door", "overall_score": 3.7, "selection_status": "rejected"},
    ],
}

# Template shape (.agents/skills/astory/templates/debates/final_scoreboard.json)
TEMPLATE_SCOREBOARD = {
    "threshold": 4.0,
    "selected_idea_id": "idea_001",
    "survivors": [
        {
            "idea_id": "idea_001",
            "title": "A",
            "scores": {"overall": 4.5},
            "selection_status": "selected",
        },
        {
            "idea_id": "idea_002",
            "title": "B",
            "scores": {"overall": 3.2},
            "selection_status": "rejected",
        },
    ],
}

REAL_SELECTED_IDEA = {
    "id": "idea_01",
    "title": "Heart Rent Notice",
    "one_line_concept": "Aachu playfully asks Zuv to pay rent for living in her heart.",
}

TEMPLATE_SELECTED_IDEA = {
    "selected_idea_id": "idea_001",
    "final_title": "A",
    "final_concept": "concept text",
}


class ScoreExtractionTests(unittest.TestCase):
    def test_best_overall_score_real_shape(self):
        self.assertEqual(validate.best_overall_score(REAL_SCOREBOARD), 4.7)

    def test_best_overall_score_template_shape(self):
        self.assertEqual(validate.best_overall_score(TEMPLATE_SCOREBOARD), 4.5)

    def test_selected_score_prefers_selected_entry(self):
        self.assertEqual(validate.selected_score(REAL_SCOREBOARD), 4.7)
        self.assertEqual(validate.selected_score(TEMPLATE_SCOREBOARD), 4.5)

    def test_threshold_reads_either_key(self):
        self.assertEqual(validate.threshold(REAL_SCOREBOARD), 4.0)
        self.assertEqual(validate.threshold(TEMPLATE_SCOREBOARD), 4.0)
        self.assertEqual(validate.threshold({}), validate.MIN_IDEA_SCORE)

    def test_meets_threshold(self):
        self.assertTrue(validate.meets_threshold(REAL_SCOREBOARD))
        below = {
            "minimum_required_overall_score": 4.0,
            "candidates": [
                {"title": "X", "overall_score": 3.5, "selection_status": "selected"}
            ],
        }
        self.assertFalse(validate.meets_threshold(below))


class ScoreboardValidationTests(unittest.TestCase):
    def test_real_and_template_scoreboards_are_valid(self):
        self.assertEqual(validate.validate_final_scoreboard(REAL_SCOREBOARD), [])
        self.assertEqual(validate.validate_final_scoreboard(TEMPLATE_SCOREBOARD), [])

    def test_non_dict_scoreboard_reports_problem(self):
        self.assertTrue(validate.validate_final_scoreboard(None))
        self.assertTrue(validate.validate_final_scoreboard([]))

    def test_empty_entries_reports_problem(self):
        self.assertIn(
            "no_idea_entries",
            validate.validate_final_scoreboard({"candidates": []}),
        )

    def test_no_parseable_score_reports_problem(self):
        bad = {"candidates": [{"title": "X", "selection_status": "selected"}]}
        self.assertIn("no_parseable_overall_score", validate.validate_final_scoreboard(bad))


class SelectedIdeaValidationTests(unittest.TestCase):
    def test_real_and_template_selected_ideas_are_valid(self):
        self.assertEqual(validate.validate_selected_idea(REAL_SELECTED_IDEA), [])
        self.assertEqual(validate.validate_selected_idea(TEMPLATE_SELECTED_IDEA), [])

    def test_missing_id_title_concept_reported(self):
        problems = validate.validate_selected_idea({})
        self.assertIn("missing_id", problems)
        self.assertIn("missing_title", problems)
        self.assertIn("missing_concept", problems)


# --- Story leg fixtures (template + real-run shapes) ---

REAL_STORY_CONCEPT = {
    "title": "Heart Rent Notice",
    "one_line_summary": "Aachu jokingly asks Zuv to pay rent for living in her heart.",
    "emotional_hook": "Love has become permanent.",
    "setup": "A cozy interior with negative space.",
    "escalation": "Aachu holds a tiny rent note toward Zuv.",
    "payoff": "Zuv offers a paper heart as payment.",
    "relationship_truth": "Love becomes a home.",
    "risks": ["Do not make Aachu look stern."],
}
TEMPLATE_STORY_CONCEPT = {
    "title": "T",
    "one_line_summary": "summary",
    "emotional_hook": "hook",
    "setup": "setup",
    "escalation": "escalation",
    "payoff": "payoff",
    "relationship_truth": "truth",
    "risk_of_being_generic": "risk",
}

REAL_BEAT_MAP = {
    "slide_count": 1,
    "slides": [
        {"slide": 1, "exact_on_image_text": "pay rent for living in my heart", "beat": "ask"}
    ],
}
TEMPLATE_BEAT_MAP = {
    "slide_count": 1,
    "slides": [
        {"slide_number": 1, "exact_on_image_text": "x", "visual_scene": "scene"}
    ],
}

REAL_SELECTED_SCENES = {
    "slides": [
        {
            "slide": 1,
            "selected_scene_id": "scene_01",
            "exact_on_image_text": "pay rent for living in my heart",
            "scene": "Aachu extends a rent note.",
        }
    ],
}
TEMPLATE_SELECTED_SCENES = {
    "slides": [
        {
            "slide_number": 1,
            "selected_scene_option_id": "1A",
            "exact_on_image_text": "x",
        }
    ],
}


class StoryConceptValidationTests(unittest.TestCase):
    def test_real_and_template_are_valid(self):
        self.assertEqual(validate.validate_story_concept(REAL_STORY_CONCEPT), [])
        self.assertEqual(validate.validate_story_concept(TEMPLATE_STORY_CONCEPT), [])

    def test_non_dict_reports_problem(self):
        self.assertEqual(validate.validate_story_concept(None), ["story_concept_not_object"])

    def test_missing_arc_and_title_reported(self):
        problems = validate.validate_story_concept({"setup": "s"})
        self.assertIn("missing_title", problems)
        self.assertIn("missing_summary", problems)
        self.assertIn("missing_escalation", problems)
        self.assertIn("missing_payoff", problems)


class SlideBeatMapValidationTests(unittest.TestCase):
    def test_real_and_template_are_valid(self):
        self.assertEqual(validate.validate_slide_beat_map(REAL_BEAT_MAP), [])
        self.assertEqual(validate.validate_slide_beat_map(TEMPLATE_BEAT_MAP), [])

    def test_empty_slides_reports_problem(self):
        self.assertIn("no_slides", validate.validate_slide_beat_map({"slides": []}))

    def test_slide_count_mismatch_reported(self):
        bad = {"slide_count": 3, "slides": [{"exact_on_image_text": "x"}]}
        self.assertIn("slide_count_mismatch", validate.validate_slide_beat_map(bad))

    def test_slide_missing_text_reported(self):
        bad = {"slide_count": 1, "slides": [{"slide": 1}]}
        self.assertIn("slide_0_missing_exact_on_image_text",
                      validate.validate_slide_beat_map(bad))


class SelectedScenesValidationTests(unittest.TestCase):
    def test_real_and_template_are_valid(self):
        self.assertEqual(validate.validate_selected_scenes(REAL_SELECTED_SCENES), [])
        self.assertEqual(validate.validate_selected_scenes(TEMPLATE_SELECTED_SCENES), [])

    def test_empty_slides_reports_problem(self):
        self.assertIn("no_slides", validate.validate_selected_scenes({"slides": []}))

    def test_slide_missing_scene_and_text_reported(self):
        bad = {"slides": [{"slide": 1}]}
        problems = validate.validate_selected_scenes(bad)
        self.assertIn("slide_0_missing_selected_scene", problems)
        self.assertIn("slide_0_missing_exact_on_image_text", problems)


if __name__ == "__main__":
    unittest.main()
