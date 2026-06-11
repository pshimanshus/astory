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


if __name__ == "__main__":
    unittest.main()
