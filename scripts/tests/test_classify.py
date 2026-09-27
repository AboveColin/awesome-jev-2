"""scripts/classify.py: the keyword rules behind every suggested kind and pattern (I20).

The rules had no test while they filed 230 rows under tool-selection, many for
"control", "harness" or "screen" in a description ("Remote control for
claude…", "The harness for your harness"). Since 2026-09-27 those words no
longer count on their own, and a robot, an autonomous system, a vehicle or a
screen counts only beside a word for deciding or acting, so a robot arm or a
game agent choosing its next move keeps the suggestion.

The samples below are catalogue rows' titles and summaries, copied here so the
tests do not move when a row is edited. Rows are never re-classified by this
change: the rows the old rule filed there and the new one would not are listed
in docs/review-queue.md for a person, which the last tests check.
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_review_queue as queue  # noqa: E402
import classify  # noqa: E402
import discover_candidates  # noqa: E402
import review_rows  # noqa: E402
from readme.rows import star_band  # noqa: E402

TS = "tool-selection"

# (title, summary): projects that decide which action comes next.
KEEP = {
    "typesafe-mario": (
        "typesafe-mario",
        "Plays Super Mario Bros. from structured emulator RAM rather than screenshots, deciding run, jump and dodge.",
    ),
    "embodied-jev": (
        "embodied-jev",
        "EmbodiedJev: MuJoCo robot decision workbench with MiniCPM5-2B, Jev and compatible model APIs",
    ),
    "jev-drone": (
        "jev-drone",
        "Camera-only simulated drone where Jev makes tactical judgements at a low rate while stabilisation "
        "and safety reflexes stay in ordinary fast code.",
    ),
    "quackd": (
        "quackd",
        "One CLI for all your robots. Connect them, command them, and let them work together, each with an "
        "LLM for a brain, Jev for cheaper steps.",
    ),
}
# (title, summary): the old rule filed these under tool-selection for a word
# that names no decision.
DROP = {
    "omg-dev": (
        "omg.dev",
        "omg.dev — Remote control for claude, codex, cursor, opencode, pi, grok, jcocde with mobile client",
    ),
    "interlinked-cli": (
        "interlinked-cli",
        "The harness for your harness. Local hooks, taste enforcement, and developer observability for AI "
        "coding agents (Claude Code, Codex, Cursor, Copilot CLI).",
    ),
    "agentiloop": (
        "agent",
        "AgentiLoop Agent! An Autonomous Agentic Agent for Mac, and exclusive Apple only harnesss. Supports "
        "automation, scripting, coding, build anything and more. Powered by 21 LLM providers across local "
        "and cloud platforms. Dark or Light Mode UI.",
    ),
}


def patterns(summary: str, title: str = "x", rules=classify.classify) -> list[str]:
    return rules(summary, title)[1]


class ToolSelectionTest(unittest.TestCase):
    def test_projects_that_decide_their_next_action_keep_it(self):
        for slug, (title, summary) in KEEP.items():
            with self.subTest(slug=slug):
                self.assertIn(TS, patterns(summary, title))
                self.assertIn(TS, patterns(summary, title, classify.classify_broad))

    def test_a_word_that_names_no_decision_no_longer_files_a_row_there(self):
        for slug, (title, summary) in DROP.items():
            with self.subTest(slug=slug):
                self.assertNotIn(TS, patterns(summary, title))
                # What changed: the rule until 2026-09-27 took every one of them.
                self.assertIn(TS, patterns(summary, title, classify.classify_broad))

    def test_harness_alone_adds_no_pattern(self):
        self.assertEqual(classify.classify("The harness for your harness", "x"), ("project", ["overview"]))
        self.assertEqual(patterns("A remote control for coding agents"), ["overview"])

    def test_a_setting_counts_only_beside_a_word_for_deciding_or_acting(self):
        for setting in ("robot", "autonomous", "drive", "drives", "screen", "screenshots"):
            with self.subTest(setting=setting):
                self.assertNotIn(TS, patterns(f"A {setting} toolkit"))
                self.assertIn(TS, patterns(f"A {setting} toolkit", rules=classify.classify_broad))
                for action in ("decides", "a decision", "action", "each step", "command", "moves", "which", "next"):
                    with self.subTest(action=action):
                        self.assertIn(TS, patterns(f"A {setting} toolkit: {action}"))

    def test_words_that_name_the_decision_count_on_their_own(self):
        for text in (
            "Drives a browser",
            "Computer use on macOS",
            "Clicks through forms",
            "A GUI agent",
            "Classifies the next action",
            "Gates each tool call",
            "Scores every agent step",
            "Navigates a site",
            "Tool routing for agents",
            "Chains the three primitives",
            "Reflexes for an agent",
            "Asks which tool to use",
            "Picks each action",
        ):
            with self.subTest(text=text):
                self.assertIn(TS, patterns(text))

    def test_every_word_starts_at_a_word_boundary(self):
        # The old rule had a boundary on its first words only.
        for text in (
            "A subnavigation menu",
            "Flags unscreened uploads for the next reviewer",
            "Uncontrolled drift detection",
            "A robotics kit that can remove parts",
        ):
            with self.subTest(text=text):
                self.assertNotIn(TS, patterns(text))
        self.assertIn(TS, patterns("A subnavigation menu", rules=classify.classify_broad))
        self.assertIn(TS, patterns("Flags unscreened uploads for the next reviewer", rules=classify.classify_broad))


class RulesTest(unittest.TestCase):
    """The rest of the rules, pinned as they are: nothing but tool-selection changed."""

    def test_kinds(self):
        for text, kind in (
            ("An open-source reimplementation of the Jev API", "alternative"),
            ("A reproducible benchmark of calibration", "benchmark"),
            ("A Python SDK for the API", "sdk"),
            ("An MCP server exposing Jev", "plugin"),
            ("A LangChain integration", "integration"),
            ("Sorts my photos", "project"),
        ):
            with self.subTest(text=text):
                self.assertEqual(classify.classify(text, "x")[0], kind)

    def test_patterns_in_rule_order_at_most_three(self):
        self.assertEqual(
            patterns("Retries, reranks, routes to the cheapest model and classifies tickets"),
            ["retry-control", "search-ranking", "model-routing"],
        )
        self.assertEqual(patterns("Nothing a rule knows"), ["overview"])

    def test_the_name_is_read_too_and_the_language_is_not(self):
        self.assertEqual(patterns("", "jev-rerank"), ["search-ranking"])
        self.assertEqual(classify.classify("Reranks passages", "x", "python"), classify.classify("Reranks passages", "x"))

    def test_only_tool_selection_differs_between_the_two_rule_sets(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        changed = 0
        for entry in catalog:
            old, new = classify.suggest(entry, classify.classify_broad), classify.suggest(entry)
            with self.subTest(slug=entry["slug"]):
                self.assertEqual(old[0], new[0])
                self.assertFalse(TS in new[1] and TS not in old[1], "the new rule only ever drops tool-selection")
                if old != new:
                    changed += 1
                    self.assertIn(TS, old[1])
                    self.assertNotIn(TS, new[1])
        self.assertGreater(changed, 0)

    def test_suggest_reads_summary_and_title(self):
        entry = {"slug": "s", "title": "jev-rerank", "summary": "Retries on failure"}
        self.assertEqual(classify.suggest(entry), classify.classify("Retries on failure", "jev-rerank"))
        self.assertEqual(classify.suggest({"slug": "s"}), ("project", ["overview"]))

    def test_old_imports_still_work(self):
        self.assertIs(discover_candidates.classify, classify.classify)
        self.assertIs(review_rows.classify, classify.classify)


def row(slug: str, summary: str, patterns_: list[str], *, stars: int | None = None, title: str | None = None) -> dict:
    out = {
        "slug": slug, "title": title or slug, "summary": summary, "summary_zh": "摘要",
        "url": f"https://github.com/someone/{slug}", "kind": "project", "patterns": patterns_,
        "sources": [], "license": "CC0-1.0",
    }
    if stars is not None:
        out["stars"] = stars
    return out


class ReplayQueueTest(unittest.TestCase):
    """The rows the old rule put in tool-selection and the new one would not, for a person."""

    ROWS = [
        row("remote", "Remote control for coding agents", [TS], stars=537),
        row("harness", "A harness for agents", [TS, "safety-gating"], stars=12, title="Zed harness"),
        row("robot-arm", "Robot arm that decides its next move", [TS], stars=3000),
        row("already-moved", "Remote control for coding agents", ["overview"], stars=900),
        row("hand-filed", "Plays chess", [TS], stars=40),
        row("few-stars", "An autonomous agent", [TS], stars=3, title="Alpha"),
    ]

    def listed(self, rows: list[dict]) -> list[str]:
        return [cells[0].split("]")[0].lstrip("[") for cells in queue.tool_selection_broad_words(rows).rows]

    def test_only_rows_carrying_it_on_dropped_words_are_listed_most_starred_band_first(self):
        # robot-arm keeps the suggestion; already-moved no longer carries the pattern;
        # hand-filed never matched a keyword, so a person chose it.
        self.assertEqual(self.listed(self.ROWS), ["remote", "harness", "few-stars"])

    def test_each_row_shows_both_suggestions_and_its_band(self):
        (cells,) = [c for c in queue.tool_selection_broad_words(self.ROWS).rows if "#remote)" in c[0]]
        self.assertEqual(cells[1:], ("★100+", "`tool-selection`", "`tool-selection`", "`overview`"))

    def test_counted_where_status_publishes_it(self):
        # Rendered here rather than read from the committed files: a pull
        # request that re-files a row leaves those to the bot, and CI runs the
        # unit tests before it regenerates anything (scripts/check.py).
        catalog = json.loads((ROOT / "catalog.json").read_text())
        count = _stats.compute()["review_tool_selection_broad"]
        self.assertEqual(len(queue.tool_selection_broad_words(catalog).rows), count)
        self.assertIn(f"](#tool-selection-broad-words) | {count} |", queue.render(catalog))
        status = build_docs.render()[ROOT / "docs" / "status.md"]
        self.assertIn(f"(review-queue.md#tool-selection-broad-words)) | {count} |", status)

    def test_stars_move_a_row_only_across_a_band_floor(self):
        rows = copy.deepcopy(self.ROWS)
        before = queue.render(rows)
        for entry in rows:
            band = star_band(entry["stars"])
            entry["stars"] = {0: 9, 1: 99, 2: 999, 3: 9999}[band]
        self.assertEqual(queue.render(rows), before)
        rows[0]["stars"] = 5
        self.assertNotEqual(queue.render(rows), before)

    def test_changing_the_pattern_takes_a_row_off(self):
        rows = copy.deepcopy(self.ROWS)
        rows[0]["patterns"] = ["overview"]
        self.assertNotIn("remote", self.listed(rows))


if __name__ == "__main__":
    unittest.main()
