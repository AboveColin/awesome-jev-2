"""counts.py prints _stats' numbers instead of counting them again (I11).

_stats.compute() is the one definition of every published number. counts.py
used to recount "with code", "official" and hand-written Chinese itself; the
two agreed only by coincidence of identical expressions.
"""

from __future__ import annotations

import contextlib
import io
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import counts  # noqa: E402


def run_counts() -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = counts.main()
    assert code == 0, code
    return out.getvalue()


class CountsTest(unittest.TestCase):
    def test_importing_prints_nothing(self):
        done = subprocess.run(
            [sys.executable, "-c", "import counts"],
            cwd=ROOT / "scripts", capture_output=True, text=True, check=True,
        )
        self.assertEqual(done.stdout, "")

    def test_headline_numbers_are_the_stats_snapshot(self):
        fake = {
            **_stats.compute(),
            "entries": 7004,
            "retired": 7005,
            "with_code": 7001,
            "official": 7002,
            "zh_hand": 7003,
            "call_site_rows": 7006,
            "wire_shape_rows": 7007,
            "example_only_rows": 7008,
            "review_examples_dir": 7009,
            "review_single_model_name": 7010,
            "review_tool_selection_broad": 7016,
            "patterns_rule_identical": 7017,
            "patterns_reviewed": 7018,
            "overview_unindexed": 7019,
            "has_code_unbacked": 7011,
            "summary_upstream": 7012,
            "summary_upstream_stale": 7013,
            "summary_curated": 7014,
            "summary_unlabelled": 7015,
        }
        with patch.object(_stats, "compute", return_value=fake):
            text = run_counts()
        for line in (
            "catalog.json   7004 entries",
            "retired.json   7005 entries",
            "with code      7001",
            "official       7002",
            "zh hand-written 7003/7004",
            "evidence       7006 call-site, 7007 wire-shape, 7008 example-only",
            "review queue   7009 under examples/, 7010 on one model name or host, "
            "7016 tool-selection on dropped keywords (docs/review-queue.md)",
            "code, no cite  7011 (neither evidence nor evidence_none)",
            "patterns       7017 equal the keyword rules' suggestion (no review recorded), 7018 patterns_reviewed, "
            "7019 overview rows with code not yet indexed by pattern",
            "summaries      7012 upstream-description, 7013 upstream-description-stale, 7014 curated, 7015 unlabelled",
            "next changes at 7,100 entries",
            "  7,000+ public resources for Jev",
        ):
            self.assertIn(line, text)

    def test_real_numbers_match_stats(self):
        stats = _stats.compute()
        text = run_counts()
        self.assertIn(f"with code      {stats['with_code']}\n", text)
        self.assertIn(f"official       {stats['official']}\n", text)
        self.assertIn(f"zh hand-written {stats['zh_hand']}/{stats['entries']}\n", text)


if __name__ == "__main__":
    unittest.main()
