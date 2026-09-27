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
        }
        with patch.object(_stats, "compute", return_value=fake):
            text = run_counts()
        for line in (
            "catalog.json   7004 entries",
            "retired.json   7005 entries",
            "with code      7001",
            "official       7002",
            "zh hand-written 7003/7004",
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
