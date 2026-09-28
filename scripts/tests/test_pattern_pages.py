"""Each pattern page says where its design notes are and lists, ahead of every
row, the official material and this repository's own examples (I24).

docs/by-pattern/<key>.md used to be one blurb and a list of links, while how
to model the decision lived in docs/patterns.md, which linked no pattern page:
neither knew the other existed. Now a page links its `## key` section of the
patterns page and opens with two short lists: what TypeSafe AI publishes
(`official`) and the examples under examples/ (the rows examples/index.json
indexes), each row with its caveats. The patterns page closes every section
with a line build_docs.py writes: how many rows the catalogue files there,
their page and the site's filter. lint_docs holds each section to its markers.

Everything renders in memory: CI runs unit tests before it regenerates.
"""

from __future__ import annotations

import copy
import json
import pathlib
import re
import sys
import unittest
import unittest.mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_examples_index  # noqa: E402
import lint_docs  # noqa: E402
from readme import pages, rows, strings  # noqa: E402

CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
PATTERN_KEYS = [p["key"] for p in json.loads((ROOT / "patterns.json").read_text())["patterns"]]
CJK = re.compile(r"[㐀-鿿]")
PACKS = (strings.EN, strings.ZH)


def grouped(catalog=None) -> dict[str, list[dict]]:
    return {k: v for k, v in rows.group_by_pattern(copy.deepcopy(catalog or CATALOG)).items() if v}


def between(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def official_part(text: str, pack: dict) -> str:
    return between(text, f"## {pack['official_h']}\n", f"## {pack['examples_h']}\n")


def examples_part(text: str, pack: dict) -> str:
    return between(text, f"## {pack['examples_h']}\n", f"## {pack['list_h']}\n")


def short_links(part: str) -> list[str]:
    """The link of each one-line row in a short list, in order."""
    return re.findall(r"^- \[[^\n]*?\]\(([^)\s]+)\) <sub>", part, re.M)


class DesignLinkTest(unittest.TestCase):
    def test_every_page_links_its_section_of_the_patterns_page(self):
        headings = {
            rel: set(lint_docs.pattern_sections((ROOT / rel).read_text()))
            for rel in {f"docs/{doc.removeprefix('../')}" for doc in pages.PATTERNS_DOC.values()}
        }
        for key, members in grouped().items():
            for pack in PACKS:
                with self.subTest(page=rows.page_name(key, pack["lang_code"])):
                    doc = pages.PATTERNS_DOC[pack["lang_code"]]
                    text = pages.render_page(key, members, pack)
                    self.assertIn(f"]({doc}#{key})", text)
                    self.assertIn(key, headings[f"docs/{doc.removeprefix('../')}"])
        self.assertEqual(pages.PATTERNS_DOC["en"], "../patterns.md")

    def test_overview_says_what_the_label_means(self):
        members = grouped()["overview"]
        self.assertIn("What `overview` means", pages.render_page("overview", members, strings.EN))
        self.assertNotIn("What `overview` means", pages.render_page("tool-selection", grouped()["tool-selection"], strings.EN))

    def test_the_page_reads_intro_design_evidence_short_lists_then_the_full_list(self):
        members = grouped()["fan-out"]
        for pack in PACKS:
            with self.subTest(lang=pack["lang_code"]):
                text = pages.render_page("fan-out", members, pack)
                marks = [
                    pack["page_intro"].split("{", 1)[0],
                    "#fan-out)",
                    rows.marked(pack, "pattern_evidence", **_stats.evidence_ladder(members, "fan-out"),
                                shape=pages.SHAPE_EVIDENCE[pack["lang_code"]]),
                    f"## {pack['official_h']}\n",
                    f"## {pack['examples_h']}\n",
                    f"## {pack['list_h']}\n",
                    rows.stars_note(pack, catalog="../../catalog.json"),
                    f"- **[{rows.esc(members[0]['title'])}]",
                ]
                places = [text.index(mark) for mark in marks]
                self.assertEqual(places, sorted(places))


class ShortListsTest(unittest.TestCase):
    def test_official_material_is_exactly_the_official_rows_in_list_order(self):
        for key, members in grouped().items():
            official = [e for e in members if e.get("official")]
            for pack in PACKS:
                with self.subTest(page=rows.page_name(key, pack["lang_code"])):
                    # Whatever order the rows arrive in, as the full list.
                    part = official_part(pages.render_page(key, list(reversed(members)), pack), pack)
                    self.assertEqual(short_links(part), [e["url"] for e in sorted(official, key=rows.sort_key)])
                    self.assertEqual(rows.marked(pack, "official_none") in part, not official)

    def test_examples_are_the_rows_examples_index_json_indexes(self):
        indexed, _ = build_examples_index.build(copy.deepcopy(CATALOG))
        by_slug = {item["slug"]: item["path"] for item in indexed["examples"]}
        self.assertTrue(by_slug)
        seen = set()
        for key, members in grouped().items():
            own = sorted((e for e in members if e["slug"] in by_slug), key=rows.sort_key)
            for pack in PACKS:
                with self.subTest(page=rows.page_name(key, pack["lang_code"])):
                    part = examples_part(pages.render_page(key, members, pack), pack)
                    links = short_links(part)
                    self.assertEqual(links, [f"../../{by_slug[e['slug']]}" for e in own])
                    for link in links:
                        self.assertTrue((ROOT / "docs" / "by-pattern" / link).resolve().is_file(), link)
                    self.assertEqual(rows.marked(pack, "examples_none", dir="../../examples/") in part, not own)
            seen.update(e["slug"] for e in own)
        self.assertEqual(seen, set(by_slug))

    def test_each_short_list_row_carries_its_caveats_and_the_authors_direction(self):
        with_direction = next(e for e in CATALOG if rows.direction_bit(e, strings.EN))
        flagged = {**copy.deepcopy(with_direction), "slug": "zz-official", "official": True,
                   "flags": ["vendor-reported", "no-license"]}
        example = next(e for e in CATALOG if build_examples_index.own_example(e))
        members = [flagged, copy.deepcopy(example)]
        for pack in PACKS:
            with self.subTest(lang=pack["lang_code"]):
                text = pages.render_page("fan-out", members, pack)
                official = official_part(text, pack)
                for flag in ("vendor-reported", "no-license"):
                    self.assertIn(f"`{rows.label(rows.FLAG_LABELS, flag, pack['lang_code'])}`", official)
                self.assertIn(rows.direction_bit(flagged, pack), official)
                examples = examples_part(text, pack)
                for flag in example["flags"]:
                    self.assertIn(f"`{rows.label(rows.FLAG_LABELS, flag, pack['lang_code'])}`", examples)

    def test_the_short_lists_link_no_file_at_head_and_ignore_file_order(self):
        forward, backward = grouped(), grouped(list(reversed(CATALOG)))
        for key, members in forward.items():
            for pack in PACKS:
                with self.subTest(page=rows.page_name(key, pack["lang_code"])):
                    text = pages.render_page(key, members, pack)
                    head = text.split(f"## {pack['list_h']}\n", 1)[0]
                    self.assertNotIn("/blob/HEAD/", head)
                    self.assertEqual(head, pages.render_page(key, backward[key], pack).split(f"## {pack['list_h']}\n", 1)[0])

    def test_the_strings_exist_in_both_languages_and_the_models_chinese_is_marked(self):
        paragraphs = ("design_link", "design_link_overview", "official_intro", "official_none", "examples_intro",
                      "examples_none")
        for key in (*paragraphs, "official_h", "examples_h", "list_h"):
            with self.subTest(key=key):
                self.assertTrue(strings.EN[key])
                self.assertRegex(strings.ZH[key], CJK)
        self.assertLessEqual(set(paragraphs), strings.ZH_MACHINE)
        text = pages.render_page("fan-out", grouped()["fan-out"], strings.ZH)
        for line in (pages.design_line("fan-out", strings.ZH), rows.marked(strings.ZH, "official_intro")):
            self.assertIn(line + "\n", text)
            self.assertTrue(line.endswith(" <sub>(机翻)</sub>"))


class PatternsDocTest(unittest.TestCase):
    """docs/patterns.md as build_docs.py writes it, from the catalogue as it is now."""

    @classmethod
    def setUpClass(cls):
        docs = {str(path.relative_to(ROOT)): text for path, text in build_docs.render().items()}
        cls.text = docs["docs/patterns.md"]
        cls.stats = _stats.compute()

    def test_each_section_ends_with_its_count_its_page_and_the_site(self):
        sections = lint_docs.pattern_sections(self.text)
        pages_ = grouped()
        self.assertEqual(set(sections), set(PATTERN_KEYS))
        for key in PATTERN_KEYS:
            with self.subTest(key=key):
                body = sections[key].split("\n---\n", 1)[0].rstrip()
                self.assertTrue(body.endswith(f"<!-- catalogued-{key}:end -->"))
                line = between(body, f"<!-- catalogued-{key}:start -->\n", f"\n<!-- catalogued-{key}:end -->")
                n = self.stats["by_pattern"][key]
                self.assertEqual(n, len(pages_.get(key, [])))
                self.assertIn(f"**{rows.label(rows.PATTERN_LABELS, key, 'en')}** in the catalogue:", line)
                self.assertIn(f"({rows.site_link(key, 'en')})", line)
                self.assertEqual(f"(by-pattern/{key}.md)" in line, bool(n))
                if n:
                    self.assertIn(f"{n} row", line)

    def test_no_rows_one_row_and_many(self):
        self.assertNotIn("by-pattern/", build_docs.catalogued_block("recommendation", 0, "en"))
        self.assertNotIn("by-pattern/", build_docs.catalogued_block("recommendation", 0, "zh"))
        self.assertIn("1 row, [listed with its caveats]", build_docs.catalogued_block("recommendation", 1, "en"))
        self.assertIn("12 rows, [each listed", build_docs.catalogued_block("recommendation", 12, "en"))
        zh = build_docs.catalogued_block("recommendation", 12, "zh")
        self.assertIn("共 12 条", zh)
        self.assertIn("(by-pattern/recommendation.zh-CN.md)", zh)
        self.assertIn("lang=zh", zh)

    def test_the_count_is_generated_not_typed(self):
        # The line sits inside a block, so lint_docs' bare-count rule never sees it.
        self.assertEqual([p for p in lint_docs.check_bare_counts("docs/patterns.md", self.text)], [])
        self.assertEqual(len(re.findall(r"<!-- catalogued-[a-z-]+:start -->", self.text)), len(PATTERN_KEYS))


class CheckPatternDocsTest(unittest.TestCase):
    KEYS = ["tool-selection", "intent-routing"]

    def page(self, *sections: str) -> str:
        return "# Decision patterns\n\n" + "\n---\n\n".join(sections) + "\n---\n\n## Adding a pattern\n\nText.\n"

    @staticmethod
    def section(key: str, *, markers: str | None = None) -> str:
        markers = key if markers is None else markers
        block = f"<!-- catalogued-{markers}:start -->\nline\n<!-- catalogued-{markers}:end -->\n" if markers else ""
        return f"## {key}\n\n**The decision:** something.\n\n{block}"

    def check(self, text: str) -> list[str]:
        # The English page alone; test_patterns_zh.py holds the Chinese one to the same rules.
        with unittest.mock.patch.object(lint_docs, "PATTERN_DOCS", ("docs/patterns.md",)):
            return lint_docs.check_pattern_docs({"docs/patterns.md": text}, self.KEYS)

    def test_the_real_pages_pass(self):
        self.assertEqual(lint_docs.check_pattern_docs(), [])

    def test_a_complete_page_passes(self):
        self.assertEqual(self.check(self.page(self.section("tool-selection"), self.section("intent-routing"))), [])

    def test_a_missing_section_is_named(self):
        self.assertEqual(
            self.check(self.page(self.section("tool-selection"))),
            ["docs/patterns.md: no `## intent-routing` section for a pattern in patterns.json"],
        )

    def test_a_section_for_no_pattern_is_named(self):
        page = self.page(self.section("tool-selection"), self.section("intent-routing"), self.section("mind-reading"))
        self.assertEqual(self.check(page), ["docs/patterns.md: `## mind-reading` is not a pattern in patterns.json"])

    def test_a_section_without_its_markers_is_named(self):
        page = self.page(self.section("tool-selection", markers=""), self.section("intent-routing"))
        (problem,) = self.check(page)
        self.assertIn("the `## tool-selection` section has no <!-- catalogued-tool-selection:start -->", problem)

    def test_a_section_with_half_its_markers_is_named(self):
        half = self.section("tool-selection").replace("<!-- catalogued-tool-selection:end -->\n", "")
        self.assertEqual(len(self.check(self.page(half, self.section("intent-routing")))), 1)

    def test_markers_under_another_heading_do_not_count(self):
        swapped = self.page(
            self.section("tool-selection", markers="intent-routing"), self.section("intent-routing", markers="tool-selection")
        )
        self.assertEqual(len(self.check(swapped)), 2)

    def test_a_missing_page_is_named(self):
        with unittest.mock.patch.object(lint_docs, "PATTERN_DOCS", ("docs/no-such-page.md",)):
            self.assertEqual(
                lint_docs.check_pattern_docs(keys=self.KEYS),
                ["docs/no-such-page.md: missing; it defines every pattern in patterns.json"],
            )


if __name__ == "__main__":
    unittest.main()
