"""Dated snapshots of the catalogue's counts in history/ (I46).

scripts/snapshot_stats.py writes history/<UTC date>.json from metadata.yml
only: compute()'s numbers, rows per kind/pattern/flag/language/licence, and
each row's slug, stars, licence and flags, under a header saying it is
generated. These tests hold the file's shape, that a rerun is byte-identical,
that no snapshot is dated before the newest one (no backfill), and how
docs/shape.md's trend section reads the files: a sentence until there are
three, then a table, absolute dates only. Temp directories throughout; the one
test of committed files checks only that whatever the bot committed is shaped
like a snapshot.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_shape  # noqa: E402
import snapshot_stats  # noqa: E402

CATALOG, RETIRED, PATTERNS, COMPAT, SCHEMA = _stats.load()
TAXONOMY = json.loads((ROOT / "taxonomy.json").read_text())
METADATA = ROOT / ".github" / "workflows" / "metadata.yml"


def fresh(date: str = "2026-10-07", rows=None) -> dict:
    rows = CATALOG if rows is None else rows
    stats = {**_stats.compute(), "entries": len(rows)}
    return snapshot_stats.snapshot(rows, PATTERNS, COMPAT, SCHEMA, date=date, stats=stats)


def run(folder: pathlib.Path, *args: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = snapshot_stats.main(["--history", str(folder), *args])
    return code, out.getvalue(), err.getvalue()


class ShapeOfASnapshotTest(unittest.TestCase):
    def test_header_counts_and_rows(self):
        payload = fresh()
        self.assertIs(payload["generated"], True)
        self.assertEqual(payload["source"], snapshot_stats.SOURCE)
        self.assertIn("not a source of truth", payload["about"][0])
        self.assertEqual(payload["date"], "2026-10-07")
        self.assertEqual(set(payload["counts"]), {"kinds", "patterns", "flags", "languages", "licences"})
        shape = _stats.current_shape()
        self.assertEqual(payload["counts"]["languages"], shape["languages"])
        self.assertEqual(payload["counts"]["patterns"], shape["by_pattern"])
        self.assertEqual(len(payload["rows"]), len(CATALOG))
        self.assertEqual(snapshot_stats.problems("2026-10-07.json", payload), [])

    def test_a_row_keeps_only_the_facts_the_refresh_moves(self):
        self.assertEqual(snapshot_stats.row_facts({"slug": "a", "stars": None, "flags": [], "title": "t"}), {"slug": "a"})
        self.assertEqual(
            snapshot_stats.row_facts({"slug": "a", "stars": 0, "repo_license": "MIT", "flags": ["archived"]}),
            {"slug": "a", "stars": 0, "repo_license": "MIT", "flags": ["archived"]},
        )

    def test_rows_are_in_slug_order_whatever_the_file_order(self):
        self.assertEqual(fresh(rows=list(reversed(CATALOG))), fresh())

    def test_render_is_json_with_one_line_per_row(self):
        payload = fresh()
        text = snapshot_stats.render(payload)
        self.assertEqual(json.loads(text), payload)
        self.assertTrue(text.endswith("\n  ]\n}\n"))
        row_lines = [line for line in text.splitlines() if line.startswith('    {"slug":')]
        self.assertEqual(len(row_lines), len(CATALOG))
        empty = {**payload, "rows": [], "stats": {**payload["stats"], "entries": 0}}
        self.assertEqual(json.loads(snapshot_stats.render(empty)), empty)

    def test_problems_name_each_way_a_file_is_not_a_snapshot(self):
        good = fresh()
        cases = {
            "not named YYYY-MM-DD.json": ("latest.json", good),
            "date '2026-10-07' is not the file's": ("2026-10-08.json", good),
            "generated: true": ("2026-10-07.json", {**good, "generated": False}),
            "counts must map": ("2026-10-07.json", {**good, "counts": {"kinds": {}}}),
            "stats must be": ("2026-10-07.json", {**good, "stats": {}}),
            "slug order": ("2026-10-07.json", {**good, "rows": list(reversed(good["rows"]))}),
            "each slug once": ("2026-10-07.json", {**good, "rows": good["rows"][:1] * 2}),
            "rows must be": ("2026-10-07.json", {**good, "rows": [{"slug": "a", "title": "x"}]}),
            "but stats.entries is": ("2026-10-07.json", {**good, "rows": good["rows"][:3]}),
            "not a JSON object": ("2026-10-07.json", []),
        }
        for needle, (name, payload) in cases.items():
            with self.subTest(needle):
                found = snapshot_stats.problems(name, payload)
                self.assertTrue(any(needle in f for f in found), found)


class WriteTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name) / "history"

    def test_a_rerun_on_the_same_day_is_byte_identical(self):
        code, out, _ = run(self.dir, "--date", "2026-10-07")
        self.assertEqual(code, 0)
        self.assertIn("written", out)
        first = (self.dir / "2026-10-07.json").read_bytes()
        code, out, _ = run(self.dir, "--date", "2026-10-07")
        self.assertEqual(code, 0)
        self.assertIn("unchanged", out)
        self.assertEqual((self.dir / "2026-10-07.json").read_bytes(), first)
        self.assertEqual([p.name for p in self.dir.iterdir()], ["2026-10-07.json"], "no temp file left behind")

    def test_later_dates_add_a_file_and_an_earlier_one_is_refused(self):
        run(self.dir, "--date", "2026-10-07")
        code, out, _ = run(self.dir, "--date", "2026-10-14")
        self.assertEqual(code, 0)
        self.assertIn("2 snapshot(s) since 2026-10-07", out)
        code, _, err = run(self.dir, "--date", "2026-10-01")
        self.assertEqual(code, 1)
        self.assertIn("never dated before the newest one", err)
        self.assertFalse((self.dir / "2026-10-01.json").exists())
        self.assertEqual(run(self.dir, "--date", "October")[0], 2)

    def test_load_history_skips_the_readme_and_stops_on_a_broken_snapshot(self):
        run(self.dir, "--date", "2026-10-14")
        (self.dir / "README.md").write_text("# history/\n")
        payload = json.loads((self.dir / "2026-10-14.json").read_text())
        (self.dir / "2026-10-07.json").write_text(snapshot_stats.render({**payload, "date": "2026-10-07"}))
        self.assertEqual([d for d, _ in snapshot_stats.load_history(self.dir)], ["2026-10-07", "2026-10-14"])
        (self.dir / "2026-10-21.json").write_text("{not json")
        with self.assertRaisesRegex(ValueError, "2026-10-21.json: unreadable"):
            snapshot_stats.load_history(self.dir)
        self.assertEqual(snapshot_stats.load_history(self.dir.parent / "nowhere"), [])

    def test_the_committed_history_is_shaped_like_snapshots(self):
        folder = ROOT / "history"
        self.assertTrue((folder / "README.md").exists(), "metadata.yml stages history/, which must exist")
        for path in sorted(folder.glob("*.json")):
            with self.subTest(path.name):
                self.assertEqual(snapshot_stats.problems(path.name, json.loads(path.read_text())), [])


def history(*dates: str, drop: str = "") -> tuple:
    base = fresh()
    out = []
    for i, date in enumerate(dates):
        stats = {**base["stats"], "entries": 1000 + i}
        stats.pop(drop, None)
        out.append((date, {**base, "date": date, "stats": stats}))
    return tuple(out)


class TrendTest(unittest.TestCase):
    def section(self, snapshots: tuple, lang: str = "en") -> str:
        return "\n".join(build_shape.trend_section(snapshots, lang))

    def test_no_snapshot_yet(self):
        self.assertIn("No snapshot yet", self.section(()))
        self.assertIn("还没有快照", self.section((), "zh"))

    def test_fewer_than_three_says_since_when_and_how_many(self):
        one = self.section(history("2026-10-07"))
        self.assertIn("Collecting since 2026-10-07: 1 snapshot in `history/`", one)
        self.assertIn("2 snapshots", self.section(history("2026-10-07", "2026-10-14")))
        self.assertIn("2 份快照", self.section(history("2026-10-07", "2026-10-14"), "zh"))
        self.assertNotIn("|", one)

    def test_three_or_more_make_a_table_of_the_newest(self):
        dates = [f"2026-{m:02d}-{d:02d}" for m, d in [(10, 7), (10, 14), (10, 21)]]
        text = self.section(history(*dates))
        self.assertIn("| 2026-10-21 | 1002 |", text)
        self.assertIn("3 since 2026-10-07, the newest 3 shown", text)
        many = [f"2026-{10 + i // 4:02d}-{1 + (i % 4) * 7:02d}" for i in range(14)]
        text = self.section(history(*many))
        self.assertNotIn(f"| {many[1]} |", text)
        self.assertIn(f"| {many[2]} |", text)
        self.assertEqual(sum(1 for line in text.splitlines() if re.match(r"\| \d{4}-", line)), build_shape.TREND_SHOWN)

    def test_a_count_an_old_snapshot_lacks_is_a_dash(self):
        text = self.section(history("2026-10-07", "2026-10-14", "2026-10-21", drop="independent_reports"))
        self.assertRegex(text, r"\| 2026-10-07 \| 1000 \| \d+ \| \d+ \| — \|")

    def test_only_absolute_dates(self):
        for snapshots in ((), history("2026-10-07"), history("2026-10-07", "2026-10-14", "2026-10-21")):
            for lang in ("en", "zh"):
                text = self.section(snapshots, lang)
                self.assertNotRegex(text, r"\bago\b|\btoday\b|\blast week\b|天前|今天|上周")

    def test_the_page_reads_history_when_it_loads(self):
        inputs = build_shape.load()
        self.assertEqual(list(inputs.history), snapshot_stats.load_history())
        page = build_shape.render(
            build_shape.Inputs(copy.deepcopy(CATALOG), PATTERNS, COMPAT, SCHEMA, TAXONOMY,
                               history("2026-10-07", "2026-10-14", "2026-10-21")), "en")
        self.assertIn("## Over time", page)
        self.assertIn("| 2026-10-14 | 1001 |", page)


class WiringTest(unittest.TestCase):
    def test_only_the_weekly_refresh_writes_snapshots_before_its_commit(self):
        text = METADATA.read_text()
        order = [text.index(f"      - name: {name}") for name in (
            "Record which sibling directories link each repository",
            "Take in the latest discovery verdicts",
            "Keep a dated snapshot of the catalogue's counts",
            "Rebuild everything generated from those facts, and commit it here",
        )]
        self.assertEqual(order, sorted(order))
        step = text[order[2]:order[3]]
        self.assertIn("continue-on-error: true", step)
        self.assertIn("run: python3 scripts/snapshot_stats.py\n", step)
        add = next(line for line in text.splitlines() if "git add -A" in line)
        self.assertIn("history", add.split())
        for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
            if workflow.name != "metadata.yml":
                self.assertNotIn("snapshot_stats", workflow.read_text(), workflow.name)

    def test_the_files_are_marked_generated_and_the_readme_is_not(self):
        out = subprocess.run(
            ["git", "check-attr", "linguist-generated", "--", "history/2026-10-07.json", "history/README.md"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
        self.assertIn("history/2026-10-07.json: linguist-generated: set", out)
        self.assertIn("history/README.md: linguist-generated: unspecified", out)


if __name__ == "__main__":
    unittest.main()
