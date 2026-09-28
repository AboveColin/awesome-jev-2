"""Negative results through the MCP server (I34).

search_examples(outcome="negative") returns the rows whose own author measured
Jev for the use and concluded against it, even those flagged shadow-mode-only
or not-jev, which a default search leaves out; every such row says
`negative_result: true`, and list_patterns counts them per pattern. The rule is
query.is_negative_result(), the one the generated pages and (by shared cases)
the site use.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from awesome_jev_mcp import query  # noqa: E402

PATTERNS = [
    {"key": "context-compaction", "en": "Context compaction", "blurb_en": "What to keep."},
    {"key": "classification", "en": "Classification", "blurb_en": "Which label."},
]


def row(slug: str, **fields) -> dict:
    base = {"slug": slug, "title": slug, "url": f"https://github.com/o/{slug}", "summary": "s",
            "kind": "project", "patterns": ["context-compaction"], "has_code": True}
    return {**base, **fields}


ROWS = [
    row("lost-bench", kind="benchmark", stars=900, measurement={"task": "t", "direction": "unfavourable"}),
    row("shadow-bench", kind="benchmark", stars=800, patterns=["classification"], flags=["shadow-mode-only"],
        measurement={"task": "t", "direction": "unfavourable"}),
    row("dropped-plugin", kind="plugin", stars=700, flags=["negative-result"], notes="Recall fell; removed."),
    row("won-bench", kind="benchmark", stars=600, measurement={"task": "t", "direction": "favourable"}),
    row("vendor-bench", kind="benchmark", stars=500, flags=["vendor-reported"]),
    row("plain", stars=400),
]
FLAGS = [{"key": "shadow-mode-only", "blurb_en": "Inert."}, {"key": "negative-result", "blurb_en": "Measured, not adopted."}]


def slugs(answer: dict) -> list[str]:
    return [r["slug"] for r in answer["results"]]


class OutcomeTest(unittest.TestCase):
    def search(self, **filters) -> dict:
        return query.search(ROWS, PATTERNS, FLAGS, **filters)

    def test_negative_keeps_the_shadow_row_a_default_search_leaves_out(self):
        self.assertNotIn("shadow-bench", slugs(self.search()))
        answer = self.search(outcome="negative")
        self.assertEqual(slugs(answer), ["lost-bench", "shadow-bench", "dropped-plugin"])
        self.assertEqual(answer["outcome_note"], query.OUTCOME_NOTES["negative"])
        self.assertIn("not reproduced here", answer["outcome_note"])
        # The shadow caveat still travels, and is explained.
        shadow = next(r for r in answer["results"] if r["slug"] == "shadow-bench")
        self.assertEqual(shadow["caveats"], ["shadow-mode-only"])
        self.assertIn("shadow-mode-only", answer["caveat_glossary"])

    def test_every_negative_row_says_so_and_no_other_does(self):
        for result in self.search(include_non_jev=True, limit=50)["results"]:
            with self.subTest(slug=result["slug"]):
                expected = result["slug"] in {"lost-bench", "shadow-bench", "dropped-plugin"}
                self.assertIs(result.get("negative_result", False), expected)

    def test_independent_is_a_benchmark_not_flagged_vendor_reported(self):
        self.assertEqual(slugs(self.search(outcome="independent")), ["lost-bench", "won-bench"])
        self.assertEqual(slugs(self.search(outcome="independent", include_non_jev=True)),
                         ["lost-bench", "shadow-bench", "won-bench"])

    def test_it_combines_with_the_other_filters(self):
        self.assertEqual(slugs(self.search(outcome="negative", pattern="classification")), ["shadow-bench"])
        self.assertEqual(slugs(self.search(outcome="negative", kind="plugin")), ["dropped-plugin"])

    def test_an_unknown_outcome_lists_the_valid_ones(self):
        answer = self.search(outcome="failed")
        self.assertEqual(answer["valid_outcomes"], ["negative", "independent"])
        self.assertNotIn("results", answer)

    def test_get_example_marks_a_negative_result(self):
        self.assertIs(query.find_example(ROWS, "dropped-plugin", FLAGS)["negative_result"], True)
        self.assertNotIn("negative_result", query.find_example(ROWS, "won-bench", FLAGS))

    def test_list_patterns_counts_them(self):
        counts = {p["key"]: p for p in query.pattern_counts(ROWS, PATTERNS)["patterns"]}
        self.assertEqual(counts["context-compaction"]["negative_results"], 2)
        self.assertEqual(counts["classification"]["negative_results"], 1)
        self.assertEqual(counts["context-compaction"]["examples"], 5)


if __name__ == "__main__":
    unittest.main()
