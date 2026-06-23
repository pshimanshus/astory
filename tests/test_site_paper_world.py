import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def read_site_file(name: str) -> str:
    return (SITE / name).read_text(encoding="utf-8")


class SitePaperWorldTests(unittest.TestCase):
    def test_homepage_uses_continuous_paper_world_chapters(self):
        html = read_site_file("index.html")

        self.assertIn('class="paper-world"', html)
        for chapter_id in ["hero", "our-story", "work", "stories", "reach-collab"]:
            self.assertIn(f'id="{chapter_id}"', html)

        forbidden = ["The Studio", 'id="studio"', "Coming soon", "Prints &amp; Merch", "The App"]
        for phrase in forbidden:
            self.assertNotIn(phrase, html)

    def test_reel_proof_does_not_show_unsourced_card_level_metrics(self):
        html = read_site_file("index.html")

        for unsourced_badge in ["4.9M", "4.0M", "3.2M", "2.4M", "2.3M", "1.6M"]:
            self.assertNotIn(unsourced_badge, html)

        self.assertIn("top reels watched in the millions", html)
        self.assertIn("Watch real reels", html)

    def test_generated_concepts_are_project_bound_assets(self):
        html = read_site_file("index.html")

        expected_assets = [
            "assets/generated/concepts/hero-no-studio.png",
            "assets/generated/concepts/our-story-continuation.png",
            "assets/generated/concepts/reels-stories-continuation.png",
            "assets/generated/concepts/brand-reach-collab-fold.png",
        ]

        for asset in expected_assets:
            self.assertIn(asset, html)
            self.assertTrue((SITE / asset).exists(), asset)

        self.assertNotIn("assets/generated/concepts/hero-locked.png", html)

    def test_motion_supports_paper_world_and_page_stack(self):
        css = read_site_file("styles.css")
        js = read_site_file("main.js")

        for selector in [".paper-world", ".paper-chapter", ".concept-art", ".story-stack"]:
            self.assertIn(selector, css)

        for behavior in ["IntersectionObserver", "pointerdown", "prefers-reduced-motion", "data-parallax"]:
            self.assertIn(behavior, js)

    def test_deep_links_land_on_sections_without_initial_smooth_scroll(self):
        css = read_site_file("styles.css")
        js = read_site_file("main.js")

        self.assertNotIn("scroll-behavior: smooth", css)
        self.assertIn("alignHashTarget", js)
        self.assertIn("scrollIntoView", js)


if __name__ == "__main__":
    unittest.main()
