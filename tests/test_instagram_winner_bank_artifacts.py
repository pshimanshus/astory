import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WINNER_BANK_ROOT = REPO_ROOT / "references" / "text-style" / "winner-bank"


class InstagramWinnerBankArtifactTests(unittest.TestCase):
    def test_scraped_winner_bank_is_visible_in_repo(self):
        required_files = [
            WINNER_BANK_ROOT / "winner_bank.json",
            WINNER_BANK_ROOT / "posts_merged.json",
            WINNER_BANK_ROOT / "chunk_results.json",
            WINNER_BANK_ROOT / "winner_contact_sheet.jpg",
            REPO_ROOT / "references" / "text-style" / "winner-bank-index-2026-06-14.json",
        ]

        for path in required_files:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"missing winner-bank artifact: {path}")
                self.assertGreater(path.stat().st_size, 0)

    def test_winner_bank_keeps_source_attached_full_scrape(self):
        winner_bank = json.loads((WINNER_BANK_ROOT / "winner_bank.json").read_text())
        posts_merged = json.loads((WINNER_BANK_ROOT / "posts_merged.json").read_text())
        index = json.loads(
            (
                REPO_ROOT
                / "references"
                / "text-style"
                / "winner-bank-index-2026-06-14.json"
            ).read_text()
        )

        self.assertGreaterEqual(len(posts_merged), 700)
        self.assertGreaterEqual(len(winner_bank), 170)
        self.assertEqual(len(index), len(winner_bank))

        first = index[0]
        for key in [
            "source_account",
            "source_url",
            "format",
            "likes",
            "comments",
            "caption_preview_max_24_words",
            "remix_mode",
        ]:
            with self.subTest(key=key):
                self.assertIn(key, first)
                self.assertNotEqual(first[key], "")

        self.assertEqual(
            first["remix_mode"],
            "permissioned_source_preserve_then_astory_wrapper",
        )


if __name__ == "__main__":
    unittest.main()
