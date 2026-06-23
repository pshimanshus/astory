import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.astory_brain.outcomes import (
    compute_outcome_report,
    load_carousel_outcomes,
    write_outcome_artifacts,
)
from scripts.astory_brain.page_store import parse_compiled_page


NOW = datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc)


def _export(
    shortcode,
    *,
    timestamp,
    likes,
    reach,
    shares,
    saved,
    follows=0,
    views=0,
    comments=0,
):
    return {
        "schema_version": 1,
        "post": {
            "id": f"id-{shortcode}",
            "permalink": f"https://www.instagram.com/p/{shortcode}/",
            "timestamp": timestamp,
            "like_count": likes,
            "comments_count": comments,
        },
        "insights": {
            "available": {
                "likes": likes,
                "reach": reach,
                "shares": shares,
                "saved": saved,
                "follows": follows,
                "views": views,
                "comments": comments,
            },
            "denied": [],
            "errors": {},
        },
    }


def _write_export(root: Path, shortcode: str, payload: dict) -> Path:
    path = root / "data/instagram/carousel_posts" / shortcode / "carousel_export.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class AStoryBrainOutcomesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo_root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        _write_export(
            self.repo_root,
            "WINNER1",
            _export(
                "WINNER1",
                timestamp="2026-05-10T08:00:00+0000",
                likes=20418,
                reach=531805,
                shares=21351,
                saved=6988,
                follows=186,
            ),
        )
        _write_export(
            self.repo_root,
            "FLOP1",
            _export(
                "FLOP1",
                timestamp="2026-05-20T08:00:00+0000",
                likes=244,
                reach=20160,
                shares=91,
                saved=105,
                follows=6,
            ),
        )
        _write_export(
            self.repo_root,
            "FRESH1",
            _export(
                "FRESH1",
                timestamp="2026-06-11T16:49:49+0000",
                likes=81,
                reach=2307,
                shares=13,
                saved=14,
            ),
        )

    def test_load_carousel_outcomes_reads_exports(self):
        records = load_carousel_outcomes(self.repo_root)
        self.assertEqual(
            {record.shortcode for record in records},
            {"WINNER1", "FLOP1", "FRESH1"},
        )
        winner = next(r for r in records if r.shortcode == "WINNER1")
        self.assertEqual(winner.reach, 531805)
        self.assertAlmostEqual(winner.shares_per_1k, 40.15, places=2)
        self.assertEqual(
            winner.export_path,
            "data/instagram/carousel_posts/WINNER1/carousel_export.json",
        )

    def test_report_tiers_by_share_rate_not_likes(self):
        records = load_carousel_outcomes(self.repo_root)
        report = compute_outcome_report(records, now=NOW)
        by_code = {entry["shortcode"]: entry for entry in report["posts"]}
        self.assertEqual(by_code["WINNER1"]["tier"], "winner")
        self.assertEqual(by_code["FLOP1"]["tier"], "flop")
        # Posts younger than the maturity window stay unranked.
        self.assertEqual(by_code["FRESH1"]["tier"], "immature")
        self.assertEqual(report["ranking"][0], "WINNER1")
        self.assertNotIn("FRESH1", report["ranking"])

    def test_zero_reach_does_not_crash(self):
        _write_export(
            self.repo_root,
            "ZERO1",
            _export(
                "ZERO1",
                timestamp="2026-05-01T08:00:00+0000",
                likes=0,
                reach=0,
                shares=0,
                saved=0,
            ),
        )
        records = load_carousel_outcomes(self.repo_root)
        report = compute_outcome_report(records, now=NOW)
        by_code = {entry["shortcode"]: entry for entry in report["posts"]}
        self.assertEqual(by_code["ZERO1"]["shares_per_1k"], 0.0)

    def test_write_outcome_artifacts_emits_lintable_page(self):
        records = load_carousel_outcomes(self.repo_root)
        report = compute_outcome_report(records, now=NOW)
        artifacts = write_outcome_artifacts(self.repo_root, report)

        parsed = parse_compiled_page(self.repo_root / artifacts["page"])
        self.assertEqual(parsed.frontmatter["type"], "outcome_attribution")
        self.assertIn("# Current Truth", parsed.current_truth)
        # Every Current Truth bullet must carry a backticked local citation.
        for line in parsed.current_truth.splitlines():
            if line.strip().startswith("- "):
                self.assertTrue(
                    "`data/instagram/carousel_posts/" in line
                    or "`scripts/" in line,
                    msg=f"bullet missing local citation: {line}",
                )
        self.assertIn("WINNER1", parsed.current_truth)

        payload = json.loads(
            (self.repo_root / artifacts["report"]).read_text(encoding="utf-8")
        )
        self.assertEqual(payload["ranking"][0], "WINNER1")

    def test_missing_exports_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(load_carousel_outcomes(Path(empty)), [])


if __name__ == "__main__":
    unittest.main()
