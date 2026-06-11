import re
import unittest
from pathlib import Path

from scripts.astory_orchestrator import spine

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".agents/skills/astory/SKILL.md"


class SpineStructureTests(unittest.TestCase):
    def test_spine_has_thirty_two_states(self):
        self.assertEqual(len(spine.STATES), 32)

    def test_first_state_is_init_run(self):
        self.assertEqual(spine.first_state(), "INIT_RUN")

    def test_indices_are_contiguous_and_ordered(self):
        self.assertEqual([s.index for s in spine.STATES], list(range(1, 33)))

    def test_by_name_round_trips_and_raises_on_unknown(self):
        self.assertEqual(spine.by_name("SELECT_BEST_IDEA").name, "SELECT_BEST_IDEA")
        with self.assertRaises(KeyError):
            spine.by_name("NOT_A_STATE")

    def test_select_best_idea_produces_selected_idea(self):
        self.assertIn(
            "planning/selected_idea.json",
            spine.by_name("SELECT_BEST_IDEA").produces,
        )


class SpineIntegrityTests(unittest.TestCase):
    def test_validate_spine_reports_no_problems(self):
        self.assertEqual(spine.validate_spine(), [])

    def test_single_linear_chain_visits_every_state_once(self):
        visited = []
        cursor = spine.first_state()
        while cursor is not None:
            self.assertNotIn(cursor, visited, "cycle in spine chain")
            visited.append(cursor)
            cursor = spine.next_state(cursor)
        self.assertEqual(set(visited), set(spine.STATE_NAMES))
        self.assertEqual(visited[-1], "COMPLETE_OR_BLOCKED")

    def test_required_hitl_states(self):
        self.assertEqual(
            spine.HITL_STATES,
            ("HITL_IDEA_LOCK", "HITL_STORY_LOCK", "HITL_PROMPT_LOCK"),
        )

    def test_hard_gate_states_present(self):
        for gate in (
            "DISCOVER_AND_ASSIGN_AGENTS",
            "REVIEW_ROOM_QA",
            "REVIEW_ROOM_IMAGEGEN_BLOCKER_CHECK",
            "REVIEW_ROOM_FINAL_BLOCKER_CHECK",
        ):
            self.assertIn(gate, spine.GATE_STATES)

    def test_produces_paths_use_known_run_subdirs(self):
        for spec in spine.STATES:
            for path in spec.produces:
                self.assertTrue(
                    path.startswith(spine.RUN_SUBDIRS),
                    f"{spec.name} produces path outside run dirs: {path}",
                )


class SpineMatchesSkillTests(unittest.TestCase):
    def test_spine_names_match_skill_state_machine(self):
        text = SKILL_PATH.read_text()
        section = text.split("## State Machine", 1)[1].split("\n## ", 1)[0]
        names = re.findall(r"^\d+\.\s+`([A-Z_]+)`", section, flags=re.MULTILINE)
        self.assertEqual(tuple(names), spine.STATE_NAMES)


if __name__ == "__main__":
    unittest.main()
