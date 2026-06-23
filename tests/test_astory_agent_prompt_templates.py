import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASTORY_ROOT = REPO_ROOT / ".agents" / "skills" / "astory"


class IdeaRoomPromptTemplateTests(unittest.TestCase):
    def test_idea_room_has_closed_agent_prompt_packet(self):
        template_path = ASTORY_ROOT / "templates" / "agents" / "idea_room_agent_prompt.md"

        self.assertTrue(template_path.exists(), "Idea Room must use a closed prompt packet")
        template = template_path.read_text()

        required_sections = [
            "# Idea Room Agent Prompt",
            "## Who You Are (Load This First)",
            "## Mission",
            "## Read Before Writing",
            "## Evidence Ledger",
            "## Discussion Protocol",
            "## Required Output Schema",
            "## Output Artifacts",
            "## Do Not Return",
            "## Bad Output Patterns",
        ]
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, template)

        required_contract_fragments = [
            "Worldview",
            "Method",
            "Memory",
            "Refusals",
            "persona file",
            "runs/{{run_id}}/input/creative_brief.json",
            "references/text-style/winner-bank/",
            "planning/source_winner_remix_contract.json",
            "runs/{{run_id}}/planning/creator_direction_notes.md",
            "agent_{{agent_number}}_candidates.json",
            "scene-landing preview",
            "do not force both Aachu and Zuv into every slide",
        ]
        for fragment in required_contract_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, template)

    def test_skill_requires_idea_room_prompt_packet_for_dispatch(self):
        skill = (ASTORY_ROOT / "SKILL.md").read_text()

        self.assertIn("templates/agents/idea_room_agent_prompt.md", skill)
        self.assertIn("Use `templates/agents/idea_room_agent_prompt.md`", skill)

    def test_agent_packets_require_source_winner_remix_contract(self):
        packet_paths = [
            ASTORY_ROOT / "templates" / "agents" / "idea_room_agent_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "story_room_agent_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "visual_scene_discussion_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "review_room_agent_prompt.md",
        ]

        for packet_path in packet_paths:
            with self.subTest(packet=packet_path.name):
                template = packet_path.read_text()
                self.assertIn("source winner", template)
                self.assertIn("permissioned", template)
                self.assertIn("planning/source_winner_remix_contract.json", template)
                self.assertIn("planning/source_winner_novelty_model.json", template)
                self.assertIn("source-preserving remix", template)

    def test_idea_and_review_packets_require_novelty_candidate_ledger(self):
        packet_paths = [
            ASTORY_ROOT / "templates" / "agents" / "idea_room_agent_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "review_room_agent_prompt.md",
        ]

        for packet_path in packet_paths:
            with self.subTest(packet=packet_path.name):
                template = packet_path.read_text()
                self.assertIn("planning/novelty_candidate_ledger.json", template)
                self.assertIn("source_engine", template)
                self.assertIn("a_story_wrappers", template)
                self.assertIn("selection_scores", template)

    def test_assignment_matrix_names_idea_room_prompt_packet(self):
        template = (
            ASTORY_ROOT / "templates" / "debates" / "agent_assignment_matrix.md"
        ).read_text()

        for agent in [
            "Relatability Ethnographer",
            "Shareability Strategist",
            "Visual Story Director",
        ]:
            with self.subTest(agent=agent):
                row = next(
                    line
                    for line in template.splitlines()
                    if line.startswith(f"| Idea Room | {agent} |")
                )
                self.assertIn("templates/agents/idea_room_agent_prompt.md", row)
                self.assertNotIn("{{prompt_packet_or_persona}}", row)


if __name__ == "__main__":
    unittest.main()
