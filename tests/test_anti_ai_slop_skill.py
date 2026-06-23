import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "anti-ai-slop-human-copy-filter"
ASTORY_ROOT = REPO_ROOT / ".agents" / "skills" / "astory"


class AntiAISlopHumanCopyFilterSkillTests(unittest.TestCase):
    def test_skill_exists_with_non_negotiable_copy_filter_contract(self):
        skill_path = SKILL_ROOT / "SKILL.md"

        self.assertTrue(skill_path.exists(), "Anti-slop skill must exist")
        skill = skill_path.read_text()

        required_fragments = [
            "name: anti-ai-slop-human-copy-filter",
            "Use when",
            "captions",
            "on-screen text",
            "carousel copy",
            "reel hooks",
            "prompts for creative content",
            "creative thought",
            "The output should not sound written. It should sound felt.",
            "Context Lock",
            "What exact words/setup must not be moved away from?",
            "Emotional Jobs",
            "AI Slop Detection",
            "Banned Directions",
            "Viral Research Layer",
            "Default First Layer",
            "Viral Research Layer is not optional for creative jamming",
            "copy, visuals, storyboards, prompts, captions, hooks, scenes, or creative direction",
            "Research -> Pattern Hypothesis -> Human Draft -> Slop Audit -> Rewrite -> Output",
            "If live research is unavailable",
            "permissioned source-preserving remix",
            "exact copy, premise, caption, and slide structure",
            "Never print, expose, store, or log the token",
            "Would a real person send this to their partner?",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, skill)

    def test_skill_bans_preachy_generic_relationship_language(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text()

        banned_fragments = [
            "Love is not about",
            "True love means",
            "At the end of the day",
            "Sometimes the smallest things",
            "Real love is when",
            "Choose someone who",
            "generic life lessons",
            "moral of the story",
            "therapy page",
            "Instagram quote page from 2018",
        ]
        for fragment in banned_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, skill)

    def test_viral_research_reference_is_default_and_self_enforcing(self):
        research = (SKILL_ROOT / "references" / "viral-research.md").read_text()

        self.assertNotIn("Use this only when", research)

        required_fragments = [
            "Default First Layer",
            "Start with evidence before taste",
            "Viral Research Layer is not optional for creative jamming",
            "Dynamic Loop",
            "Research -> Pattern Hypothesis -> Human Draft -> Slop Audit -> Rewrite -> Output",
            "If live Apify research is unavailable",
            "return an evidence gap note",
            "Never print, expose, store, or log token values",
            "Do not reduce permissioned source winners to vague mechanics",
            "Preserve the winning engine",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, research)

    def test_permissioned_source_remix_is_not_blocked_as_copying(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        research = (SKILL_ROOT / "references" / "viral-research.md").read_text()

        self.assertNotIn("Do not copy creators.", skill)
        self.assertNotIn("Do not copy captions or phrasing", research)

        for text in (skill, research):
            with self.subTest(source=text[:40]):
                self.assertIn("source winner", text)
                self.assertIn("permissioned", text)
                self.assertIn("A Story wrapper", text)

    def test_astory_routes_written_artifacts_through_anti_slop_skill(self):
        skill = (ASTORY_ROOT / "SKILL.md").read_text()

        required_fragments = [
            "anti-ai-slop-human-copy-filter",
            "Before any written creative artifact",
            "storyboard",
            "caption",
            "on-image text",
            "prompt",
            "creative thought",
            "AI_SLOP_COPY_DRIFT",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, skill)

    def test_agent_packets_require_anti_slop_before_creative_copy(self):
        packet_paths = [
            ASTORY_ROOT / "templates" / "agents" / "idea_room_agent_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "story_room_agent_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "visual_scene_discussion_prompt.md",
            ASTORY_ROOT / "templates" / "agents" / "review_room_agent_prompt.md",
        ]

        for packet_path in packet_paths:
            with self.subTest(packet=packet_path.name):
                packet = packet_path.read_text()
                self.assertIn("anti-ai-slop-human-copy-filter", packet)
                self.assertIn("AI_SLOP_COPY_DRIFT", packet)
                self.assertIn("source winner", packet)
                self.assertIn("permissioned", packet)


if __name__ == "__main__":
    unittest.main()
