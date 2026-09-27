"""Overview rows with code are listed as not yet indexed by pattern, and a
person's reading is recorded in `patterns_reviewed` (I13).

`overview` is for a row that surveys the model or the space. It is also what
the keyword rules suggest when nothing matches, and the bulk passes took their
suggestion, so the label filled with projects nobody placed: langchain's row is
"The agent engineering platform.", filed under overview. Nothing inferred about
that is written into catalog.json. What is derived at build time:

* which rows are not yet indexed by pattern: a project or plugin with code
  whose only pattern is overview and whose row records no `patterns_reviewed`.
  The READMEs, the Overview page and the site list them last, under their own
  heading, and docs/review-queue.md lists them with the rules' suggestion;
* how many rows' patterns equal the rules' suggestion, published as agreement
  with the rules and nothing more: any review of them was not recorded.

`patterns_reviewed` is the one recorded fact, and only a person writes it.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_review_queue as queue  # noqa: E402
import classify  # noqa: E402
import lint  # noqa: E402
from readme import pages, rows, strings  # noqa: E402

SCHEMA = json.loads((ROOT / "schema" / "entry.schema.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
CJK = re.compile(r"[㐀-鿿]")


def entry(slug: str, **fields) -> dict:
    out = {
        "slug": slug, "title": slug, "summary": "The agent engineering platform.", "summary_zh": "平台",
        "url": f"https://github.com/someone/{slug}", "kind": "project", "patterns": ["overview"],
        "has_code": True, "sources": [], "license": "CC0-1.0",
    }
    out.update(fields)
    return out


class RuleTest(unittest.TestCase):
    def test_which_rows_are_not_yet_indexed(self):
        self.assertTrue(_stats.not_indexed_by_pattern(entry("a")))
        self.assertTrue(_stats.not_indexed_by_pattern(entry("a", kind="plugin")))
        for why, row in (
            ("a person recorded reading it", entry("a", patterns_reviewed="2026-09-27")),
            ("it has a real pattern", entry("a", patterns=["tool-selection"])),
            ("an SDK", entry("a", kind="sdk")),
            ("official docs are what overview is for", entry("a", kind="official-docs")),
            ("an alternative", entry("a", kind="alternative")),
            ("no code to place", entry("a", has_code=False)),
        ):
            with self.subTest(why=why):
                self.assertFalse(_stats.not_indexed_by_pattern(row))

    def test_the_site_holds_the_same_rule(self):
        core = (ROOT / "site" / "catalog-core.mjs").read_text()
        kinds = re.search(r"export const UNINDEXED_KINDS = \[([^\]]*)\]", core).group(1)
        self.assertEqual(tuple(re.findall(r'"([^"]+)"', kinds)), _stats.UNINDEXED_KINDS)
        self.assertIn('entry.patterns[0] === "overview"', core)
        self.assertIn("!entry.patterns_reviewed", core)
        page = (ROOT / "site" / "index.html").read_text()
        self.assertIn("notIndexedByPattern", page.split("const STR")[0])
        for lang in ("en", "zh"):
            block = page.split(f"        {lang}: {{", 1)[1]
            self.assertIn("unindexed_h:", block.split("\n        }", 1)[0])

    def test_agreement_with_the_rules_is_not_counted_once_a_reading_is_recorded(self):
        row = entry("a")
        self.assertEqual(classify.suggest(row)[1], ["overview"])
        self.assertTrue(_stats.patterns_match_rules(row))
        self.assertFalse(_stats.patterns_match_rules(entry("a", patterns_reviewed="2026-09-27")))
        self.assertFalse(_stats.patterns_match_rules(entry("a", patterns=["search-ranking"])))

    def test_the_real_counts(self):
        s = _stats.compute()
        self.assertEqual(s["patterns_reviewed"], sum(1 for e in CATALOG if e.get("patterns_reviewed")))
        self.assertEqual(s["overview_unindexed"], sum(1 for e in CATALOG if _stats.not_indexed_by_pattern(e)))
        self.assertEqual(s["patterns_rule_identical"], sum(1 for e in CATALOG if _stats.patterns_match_rules(e)))
        self.assertGreater(s["overview_unindexed"], 0)


class SchemaAndLintTest(unittest.TestCase):
    def test_a_date_only_a_person_writes(self):
        field = SCHEMA["properties"]["patterns_reviewed"]
        self.assertEqual(field["type"], "string")
        self.assertEqual(field["pattern"], "^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
        self.assertIn("Only that person writes it", field["description"])
        props = list(SCHEMA["properties"])
        self.assertEqual(props.index("patterns_reviewed"), props.index("patterns") + 1)

    def test_lint_accepts_a_past_reading_and_refuses_a_future_one(self):
        row = entry("demo-row", sources=[{"catalog": "x", "url": "https://example.com"}],
                    evidence_none="not-yet-backfilled", patterns_reviewed="2026-09-20")
        errors, _ = lint.check_entries(SCHEMA, [row], [])
        self.assertEqual(errors, ())
        errors, _ = lint.check_entry_invariants(
            dict(row, patterns_reviewed="2026-09-21"), "catalog.json[0]", retired=False, today=dt.date(2026, 9, 20)
        )
        self.assertEqual(errors, ("catalog.json[0]: demo-row: patterns_reviewed 2026-09-21 is in the future",))

    def test_nothing_writes_it_but_a_person(self):
        # No script sets it: a reading is not something a build can infer.
        for path in sorted((ROOT / "scripts").glob("*.py")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(script=path.name):
                self.assertNotRegex(text, r"""\[["']patterns_reviewed["']\]\s*=""")
        self.assertEqual(sum(1 for e in CATALOG if e.get("patterns_reviewed")), _stats.compute()["patterns_reviewed"])


def overview_readme(text: str, heading: str) -> str:
    """The README's Overview section, up to the next top-level section."""
    return text.split(f"\n### {heading}\n", 1)[1].split("\n## ", 1)[0]


class ListingTest(unittest.TestCase):
    def setUp(self):
        self.unindexed = [e for e in CATALOG if _stats.not_indexed_by_pattern(e)]
        self.overview = [e for e in CATALOG if e["patterns"] == ["overview"]]

    def test_readmes_list_none_inline_and_say_how_many_are_apart(self):
        for name, pack in (("README.md", strings.EN), ("README.zh-CN.md", strings.ZH)):
            lang = pack["lang_code"]
            heading = f"#### {pack['unindexed_h']}"
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                section = overview_readme(text, rows.label(rows.PATTERN_LABELS, "overview", lang))
                listed, note = section.split(heading, 1)
                for row in self.unindexed:
                    self.assertNotIn(f"]({row['url']})", listed)
                self.assertIn(f"**{len(self.unindexed)}**", note)
                self.assertIn("#unindexed)", note)
                self.assertIn("docs/review-queue.md#unsorted-overview", note)
                self.assertEqual("<sub>(机翻)</sub>" in note.split("\n\n")[1], pack is strings.ZH)

    def test_the_overview_page_lists_them_last_under_their_heading(self):
        for lang, heading in (("en", "## Not yet indexed by pattern"), ("zh", "## 尚未按模式索引")):
            with self.subTest(lang=lang):
                text = (ROOT / "docs" / "by-pattern" / rows.page_name("overview", lang)).read_text(encoding="utf-8")
                before, after = text.split('<a name="unindexed"></a>', 1)
                self.assertTrue(after.lstrip().startswith(heading))
                for row in self.overview:
                    link = f"**[{rows.esc(row['title'])}]({row['url']})**"
                    self.assertIn(link, after if row in self.unindexed else before, row["slug"])

    def test_no_other_page_has_the_heading(self):
        for path in sorted((ROOT / "docs" / "by-pattern").glob("*.md")):
            if path.name.startswith("overview."):
                continue
            with self.subTest(page=path.name):
                self.assertNotIn('<a name="unindexed"></a>', path.read_text(encoding="utf-8"))

    def test_a_recorded_reading_moves_a_row_back_into_the_list(self):
        rows_ = [entry("unplaced"), entry("placed", patterns_reviewed="2026-09-27"), entry("docs", kind="official-docs")]
        text = pages.render_page("overview", rows_, strings.EN)
        before, after = text.split('<a name="unindexed"></a>', 1)
        self.assertIn("/placed)", before)
        self.assertIn("/docs)", before)
        self.assertIn("/unplaced)", after)
        self.assertIn("Projects and plugins with code, 1 of them", after)
        # With none left, the heading goes too.
        text = pages.render_page("overview", [entry("placed", patterns_reviewed="2026-09-27")], strings.ZH)
        self.assertNotIn("unindexed", text)

    def test_the_strings_exist_in_both_languages_and_the_chinese_is_marked(self):
        for key in ("unindexed_h", "unindexed_readme", "unindexed_page"):
            with self.subTest(key=key):
                self.assertTrue(strings.EN[key])
                self.assertRegex(strings.ZH[key], CJK)
        self.assertLessEqual({"unindexed_readme", "unindexed_page"}, strings.ZH_MACHINE)


class QueueAndDocsTest(unittest.TestCase):
    def test_the_queue_section_is_every_unindexed_row_by_band_then_title(self):
        section = queue.unsorted_overview(CATALOG)
        expected = sorted(
            (e for e in CATALOG if _stats.not_indexed_by_pattern(e)),
            key=lambda e: (-rows.star_band(e.get("stars")), e["title"].lower(), e["slug"]),
        )
        self.assertEqual([cells[0] for cells in section.rows], [queue.row_link(e) for e in expected])
        self.assertIn("a suggestion", section.columns[-1][0])

    def test_the_suggestion_is_the_rules_and_a_dash_when_none_matches(self):
        section = queue.unsorted_overview([entry("plain"), entry("ranker", summary="Reranks passages", stars=150)])
        self.assertEqual([cells[-1] for cells in section.rows], ["`search-ranking`", "—"])
        self.assertEqual(section.rows[0][2], "★100+")

    def test_a_recorded_reading_takes_a_row_off_both_pattern_sections(self):
        remote = entry("remote", summary="Remote control for coding agents", patterns=["tool-selection"])
        for build, row in ((queue.unsorted_overview, entry("a")), (queue.tool_selection_broad_words, remote)):
            with self.subTest(section=build.__name__):
                self.assertEqual(len(build([row]).rows), 1)
                self.assertEqual(build([dict(row, patterns_reviewed="2026-09-27")]).rows, ())

    def test_published_where_the_docs_say(self):
        s = _stats.compute()
        status = (ROOT / "docs" / "status.md").read_text(encoding="utf-8")
        self.assertIn(f"review-queue.md#unsorted-overview)) | {s['overview_unindexed']} |", status)
        self.assertIn(f"any review of these rows was not recorded) | {s['patterns_rule_identical']} of {s['entries']} |", status)
        page = (ROOT / "docs" / "review-queue.md").read_text(encoding="utf-8")
        self.assertIn(f"](#unsorted-overview) | {s['overview_unindexed']} |", page)
        for rel in ("docs/patterns.md", "llms.txt"):
            with self.subTest(doc=rel):
                self.assertIn(f"<!--n:overview_unindexed-->{s['overview_unindexed']}<!--/n-->", (ROOT / rel).read_text())
        self.assertIn("docs/patterns.md", [str(path.relative_to(ROOT)) for path in build_docs.render()])


if __name__ == "__main__":
    unittest.main()
