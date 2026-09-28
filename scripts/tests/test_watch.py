"""docs/status.md's "What to watch" as a table from watch.json (I45).

Counted signals come from catalog.json through scripts/watch.py; a reading
carries its date and whether a person or a model made it; a recent change is
stated against the snapshot before the newest in history/, or the newest week
of first_seen dates until there are two, always with absolute dates. The table
renders in memory here: CI runs unit tests before it regenerates.
"""

from __future__ import annotations

import contextlib
import copy
import datetime as dt
import io
import json
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_watch  # noqa: E402
import regenerate  # noqa: E402
import snapshot_stats  # noqa: E402
import watch  # noqa: E402
from platform_values import load_query  # noqa: E402

CATALOG = json.loads((ROOT / "catalog.json").read_text())
SPEC = watch.load()
CASES = json.loads((ROOT / "scripts" / "tests" / "negative_cases.json").read_text())["cases"]
TODAY = dt.date(2026, 9, 28)

COUNTED = {"id": "reports", "signal": "independent-reports", "question_en": "Q?", "question_zh": "问？",
           "definition_en": "D.", "definition_zh": "定义。"}
PROXY = {"id": "wire", "signal": "alternatives-matching", "matched_contains": "/v1/x", "question_en": "Q2?",
         "question_zh": "问二？", "definition_en": "A proxy.", "definition_zh": "代理。"}
READ = {"id": "paper", "signal": "manual", "question_en": "Paper?", "question_zh": "论文？",
        "definition_en": "A reading.", "definition_zh": "核读。", "status_en": "None yet.", "status_zh": "还没有。",
        "url": "https://docs.example/p", "as_of": "2026-09-20", "checked_by": "person"}
LISTED = {**READ, "id": "listed", "signal": "listed-rows", "rows": ["a"], "checked_by": "model"}
del LISTED["url"]


def row(slug: str, **fields) -> dict:
    return {"slug": slug, "title": slug.upper(), "kind": "project", "patterns": ["gate"], "first_seen": "2026-09-01",
            **fields}


ROWS = [
    row("a", kind="benchmark", first_seen="2026-09-24", measurement={"task": "t", "direction": "mixed"}),
    row("b", kind="benchmark", first_seen="2026-09-10"),
    row("c", kind="benchmark", flags=["vendor-reported"], first_seen="2026-09-24"),
    row("d", kind="alternative", evidence={"path": "s.py", "matched": ["/v1/x/choice"]}, first_seen="2026-09-18"),
    row("e", kind="alternative", evidence={"path": "s.py", "matched": ["jev-latest"]}),
    row("f", kind="alternative"),
    row("g", evidence={"path": "s.py", "matched": ["/v1/x"]}),
]
MINI = {"items": [COUNTED, PROXY, READ, LISTED]}


def snap(date: str, values: dict) -> tuple[str, dict]:
    return date, {"date": date, "watch": values}


class ProblemsTest(unittest.TestCase):
    def test_the_committed_file_renders(self):
        self.assertEqual(watch.problems(SPEC, CATALOG, TODAY + dt.timedelta(days=1)), [])
        self.assertEqual(watch.problems(MINI, ROWS, TODAY), [])

    def test_each_rule(self):
        cases = {
            "signal must be one of": {**COUNTED, "signal": "vibes"},
            "question_zh has no Chinese": {**COUNTED, "question_zh": "no chinese"},
            "definition_en is missing": {k: v for k, v in COUNTED.items() if k != "definition_en"},
            "checked_by must be one of": {**READ, "checked_by": "someone"},
            "as_of must be a YYYY-MM-DD date": {**READ, "as_of": "2026-10-01"},
            "needs the url": {k: v for k, v in READ.items() if k != "url"},
            "url must be https": {**READ, "url": "http://docs.example/p"},
            "status_zh is missing": {**READ, "status_zh": ""},
            "which is not in catalog.json": {**LISTED, "rows": ["a", "nope"]},
            "rows must be a list of distinct slugs": {**LISTED, "rows": ["a", "a"]},
            "matched_contains must name": {**PROXY, "matched_contains": " "},
        }
        for needle, item in cases.items():
            with self.subTest(needle):
                found = watch.problems({"items": [item]}, ROWS, TODAY)
                self.assertTrue(any(needle in f for f in found), found)
        self.assertTrue(watch.problems({"items": []}, ROWS, TODAY))
        self.assertIn("watch.json: ids must be distinct", watch.problems({"items": [COUNTED, COUNTED]}, ROWS, TODAY))
        self.assertTrue(watch.problems({"items": [{**COUNTED, "id": "Not An Id"}]}, ROWS, TODAY))

    def test_a_retired_row_stops_the_generator_with_a_message(self):
        broken = copy.deepcopy(SPEC)
        listed = next(i for i in broken["items"] if i["signal"] == "listed-rows")
        listed["rows"].append("no-such-row")
        found = watch.problems(broken, CATALOG, TODAY + dt.timedelta(days=1))
        self.assertEqual(found, [f"watch.json: {listed['id']!r}: lists 'no-such-row', which is not in catalog.json"])


class SignalTest(unittest.TestCase):
    def test_values_count_each_signal(self):
        self.assertEqual(watch.values(MINI, ROWS), {"reports": 2, "wire": 1})

    def test_independent_is_the_rule_every_surface_shares(self):
        rows = [{**case["entry"], "slug": str(i)} for i, case in enumerate(CASES)]
        self.assertEqual(watch.values({"items": [COUNTED]}, rows)["reports"], sum(c["independent"] for c in CASES))
        self.assertEqual(
            watch.values({"items": [COUNTED]}, CATALOG)["reports"],
            sum(1 for e in CATALOG if load_query().is_independent_report(e)),
        )
        self.assertEqual(watch.values({"items": [COUNTED]}, CATALOG)["reports"], _stats.compute()["independent_reports"])

    def test_before_two_snapshots_the_newest_first_seen_week(self):
        self.assertEqual(watch.newest_week(ROWS), ("2026-09-18", "2026-09-24"))
        for history in ((), (snap("2026-10-07", {"reports": 1}),), (snap("2026-10-07", {}), snap("2026-10-14", {}))):
            with self.subTest(snapshots=len(history)):
                text = watch.change(COUNTED, ROWS, history, 2)
                self.assertEqual(text, "+1 first seen 2026-09-18 to 2026-09-24 (history/ does not yet hold two snapshots)")

    def test_then_the_snapshot_before_the_newest(self):
        history = (snap("2026-10-07", {"reports": 5}), snap("2026-10-14", {"reports": 6}),
                   snap("2026-10-21", {"reports": 9}))
        # The newest (2026-10-21) is the refresh's own state; the change is counted from the one before it.
        self.assertEqual(watch.change(COUNTED, ROWS, history, 11), "+5 since the 2026-10-14 snapshot (then 6)")
        self.assertEqual(watch.baseline(history, "wire"), None)
        self.assertEqual(watch.change(COUNTED, ROWS, history[:2], 4), "-1 since the 2026-10-07 snapshot (then 5)")


class RenderTest(unittest.TestCase):
    def test_every_question_with_its_signal(self):
        text = watch.render(MINI, ROWS)
        lines = text.splitlines()
        self.assertEqual(lines[0], "| Question | Now | Recent change | How it is tracked |")
        self.assertEqual(len(lines), 2 + len(MINI["items"]))
        self.assertIn("**2** independent reports", text)
        self.assertIn("mixed 1, none recorded 1", text)
        self.assertIn("**1** of the 2 alternatives citing a file", text)
        self.assertIn("None yet. (read by a person, 2026-09-20; [source](https://docs.example/p))", text)
        self.assertIn("[A](https://kydlikebtc.github.io/awesome-jev/?lang=en#a). None yet. (read by a model, not yet by a "
                      "person, 2026-09-20)", text)

    def test_readings_are_never_presented_as_counts_and_dates_are_absolute(self):
        text = watch.render(SPEC, CATALOG)
        for item in SPEC["items"]:
            self.assertIn(item["question_en"], text)
            if item["signal"] in ("manual", "listed-rows"):
                self.assertIn(item["as_of"], text)
        self.assertNotRegex(text, r"\b(ago|today|yesterday|this week|last week|recently)\b")
        self.assertIn("not reproduced here", text)

    def test_independent_of_file_order(self):
        self.assertEqual(watch.render(SPEC, list(reversed(CATALOG))), watch.render(SPEC, CATALOG))

    def test_the_block_is_refilled_and_the_prose_around_it_kept(self):
        text = "Hand-written.\n\n<!-- watch:start -->\nold\n<!-- watch:end -->\n\nMore prose.\n"
        out = build_watch.render_status(text, MINI, ROWS, ())
        self.assertTrue(out.startswith("Hand-written.\n\n<!-- watch:start -->\n| Question |"))
        self.assertTrue(out.endswith("<!-- watch:end -->\n\nMore prose.\n"))
        self.assertNotIn("\nold\n", out)


class WiringTest(unittest.TestCase):
    def test_registered_and_the_status_page_has_the_markers(self):
        self.assertIn("build_watch.py", [script for script, _ in regenerate.GENERATORS])
        status = (ROOT / "docs" / "status.md").read_text()
        self.assertEqual(status.count("<!-- watch:start -->"), 1)
        self.assertIn("## What to watch\n", status)

    def test_a_snapshot_records_the_counted_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(snapshot_stats.main(["--history", str(folder), "--date", "2026-10-07"]), 0)
            payload = json.loads((folder / "2026-10-07.json").read_text())
        self.assertEqual(payload["watch"], watch.values(SPEC, CATALOG))
        self.assertEqual(snapshot_stats.problems("2026-10-07.json", payload), [])
        bad = {**payload, "watch": {"x": "many"}}
        self.assertTrue(any("watch must map" in f for f in snapshot_stats.problems("2026-10-07.json", bad)))

    def test_model_written_chinese_is_marked(self):
        for item in SPEC["items"]:
            self.assertIs(item.get("zh_machine"), True, item["id"])
        self.assertTrue(re.search(r"written by a model", SPEC["_comment"]))


if __name__ == "__main__":
    unittest.main()
