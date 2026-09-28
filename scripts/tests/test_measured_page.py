"""The README's "Measured, not claimed" shows a few rows; docs/measured.md has them all (I29).

Printed whole, the section held every independent measurement report with its
note: 350 of the README's lines, ahead of the pattern index the README calls
its primary index, while each pattern shows its first rows and links a page
with the rest. The section now works the same way. It prints INLINE_MEASURED
rows: first the picks of the curated `measured` path in collections.json, in
that path's order, then the first of the others in list order (sort_key: the
star band, never the exact count). docs/measured.md and docs/measured.zh-CN.md
list every report with every note, and caveat tags travel with every row on both.

Since 2026-09-28 (I34) the negative results come first on both, under their own
heading: a benchmark whose author's direction is unfavourable, or any other row
flagged negative-result (so a plugin can be one). They count towards the
section's ten, and their order is the band's, never the file's.

Everything here renders in memory: CI runs the unit tests before it
regenerates, so the committed files need not be current.
"""

from __future__ import annotations

import copy
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "tests"))

import build_readme  # noqa: E402
import lint_docs  # noqa: E402
import regenerate  # noqa: E402
from evidence_url import evidence_url  # noqa: E402
from readme import pages, rows, sections, strings  # noqa: E402
from test_star_bands import copy_tree, moved_within_bands  # noqa: E402

CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
RETIRED = json.loads((ROOT / "retired.json").read_text(encoding="utf-8"))
MEASURED = [entry for entry in CATALOG if rows.is_measured(entry)]
# The catalogue without its negative results, for the picks-and-fill rules alone.
POSITIVE = [entry for entry in CATALOG if not rows.is_negative(entry)]
MEASURED_POSITIVE = [entry for entry in POSITIVE if rows.is_measured(entry)]
PICKED = rows.collection_slugs("measured")
PACKS = (strings.EN, strings.ZH)
ROW_HEAD = re.compile(r"^- \*\*\[(.+?)\]\((.+?)\)\*\*", re.M)


def report(slug: str, stars: int | None = None, **fields) -> dict:
    base = {
        "slug": slug, "title": slug, "summary": f"{slug} measured something.", "summary_zh": f"{slug} 测了一些东西。",
        "url": f"https://example.org/{slug}", "kind": "benchmark", "patterns": ["classification"],
        "has_code": False, "stars": stars,
    }
    return {**base, **fields}


def section(readme: str, pack: dict) -> str:
    """The Measured section of a rendered README, up to the next ## heading."""
    start = readme.index(f"\n## {pack['measured_h']}\n")
    return readme[start: readme.index("\n## ", start + 1)]


def titles(text: str) -> list[str]:
    return [match.group(1) for match in ROW_HEAD.finditer(text)]


class SelectionTest(unittest.TestCase):
    def test_the_curated_picks_come_first_in_their_order_then_the_list_order(self):
        measured = [report(f"r{i}", stars=10 ** (i % 5)) for i in range(15)]
        picked, others = sections.inline_measured(measured, ["r3", "r0", "r9"])
        self.assertEqual([e["slug"] for e in picked], ["r3", "r0", "r9"])
        rest = [e for e in sorted(measured, key=rows.sort_key) if e["slug"] not in {"r3", "r0", "r9"}]
        self.assertEqual(others, rest[: sections.INLINE_MEASURED - 3])
        self.assertEqual(len(picked) + len(others), sections.INLINE_MEASURED)

    def test_a_pick_that_is_not_an_independent_report_here_is_skipped(self):
        measured = [report(f"r{i}") for i in range(12)]
        picked, others = sections.inline_measured(measured, ["gone", "r5", "r5", "vendor"])
        self.assertEqual([e["slug"] for e in picked], ["r5"])
        self.assertNotIn("r5", [e["slug"] for e in others])
        self.assertEqual(len(others), sections.INLINE_MEASURED - 1)

    def test_fewer_reports_than_the_limit_are_all_shown(self):
        measured = [report(f"r{i}") for i in range(4)]
        picked, others = sections.inline_measured(measured, ["r2"])
        self.assertEqual(len(picked) + len(others), 4)

    def test_more_picks_than_the_limit_are_cut_at_the_limit(self):
        measured = [report(f"r{i:02d}") for i in range(20)]
        wanted = [f"r{i:02d}" for i in range(19, 5, -1)]
        picked, others = sections.inline_measured(measured, wanted)
        self.assertEqual([e["slug"] for e in picked], wanted[: sections.INLINE_MEASURED])
        self.assertEqual(others, [])

    def test_file_order_changes_nothing(self):
        a = sections.inline_measured(copy.deepcopy(MEASURED), PICKED)
        b = sections.inline_measured(copy.deepcopy(MEASURED[::-1]), PICKED)
        self.assertEqual(a, b)

    def test_the_fill_compares_star_bands_not_counts(self):
        # Two rows in the same band: the title decides, whatever the counts.
        measured = [report("zeta", stars=900), report("alpha", stars=101)]
        _, others = sections.inline_measured(measured, [])
        self.assertEqual([e["slug"] for e in others], ["alpha", "zeta"])

    def test_the_limit_sits_beside_the_per_pattern_one(self):
        self.assertEqual(sections.INLINE_MEASURED, 10)
        self.assertIs(build_readme.INLINE_MEASURED, sections.INLINE_MEASURED)

    def test_the_picks_are_read_from_collections_json(self):
        data = json.loads((ROOT / "collections.json").read_text(encoding="utf-8"))
        group = next(g for g in data["collections"] if g["id"] == "measured")
        self.assertEqual(PICKED, [item["slug"] for item in group["entries"]])
        self.assertEqual(rows.collection_slugs("no-such-path"), [])


class ReadmeSectionTest(unittest.TestCase):
    """The real catalogue, both READMEs."""

    @classmethod
    def setUpClass(cls):
        cls.readmes = {p["lang_code"]: build_readme.render(copy.deepcopy(CATALOG), copy.deepcopy(RETIRED), p) for p in PACKS}

    def test_the_section_prints_the_picks_first_then_fills_to_the_limit(self):
        self.assertGreater(len(MEASURED), sections.INLINE_MEASURED, "the catalogue should need a page")
        negatives, picked, others = sections.measured_selection(MEASURED, PICKED)
        self.assertTrue(negatives and picked)
        for pack in PACKS:
            with self.subTest(lang=pack["lang_code"]):
                text = section(self.readmes[pack["lang_code"]], pack)
                self.assertEqual(titles(text), [rows.esc(e["title"]) for e in negatives + picked + others])
                self.assertEqual(len(titles(text)), sections.INLINE_MEASURED)

    def test_it_says_how_the_rows_were_chosen_and_links_the_rest(self):
        # The real catalogue has negative results, so the line says they come first.
        for pack, page in ((strings.EN, "docs/measured.md"), (strings.ZH, "docs/measured.zh-CN.md")):
            lang = pack["lang_code"]
            with self.subTest(lang=lang):
                text = section(self.readmes[lang], pack)
                line = rows.marked(
                    pack, "measured_more_negative", shown=sections.INLINE_MEASURED, n=len(MEASURED),
                    path=rows.collection_link("measured", lang), page=page, site=rows.reports_link(lang),
                )
                self.assertIn("\n" + line + "\n", text)
                self.assertIn(f"]({page})", line)
                self.assertIn("?indep=1&lang=" + lang, line)
                self.assertIn("?collection=measured&lang=" + lang, line)
        self.assertIn("measured_more", strings.ZH_MACHINE)
        self.assertIn("measured_more_negative", strings.ZH_MACHINE)
        self.assertTrue(rows.marked(strings.ZH, "measured_more", shown=1, n=2, path="", page="", site="").endswith(" <sub>(机翻)</sub>"))

    def test_caveats_and_notes_travel_with_every_inline_row(self):
        negatives, picked, others = sections.measured_selection(MEASURED, PICKED)
        flagged = [e for e in negatives + picked + others if e.get("flags")]
        self.assertTrue(flagged, "worldmonitor is a negative result flagged shadow mode")
        for pack in PACKS:
            lang = pack["lang_code"]
            text = section(self.readmes[lang], pack)
            for entry in negatives + picked + others:
                with self.subTest(lang=lang, row=entry["slug"]):
                    for flag in entry.get("flags", []):
                        self.assertIn(f"`{rows.label(rows.FLAG_LABELS, flag, lang)}`", text)
                    note = entry.get("notes_zh" if lang == "zh" else "notes")
                    if note:
                        self.assertIn(f"  > {rows.esc(note)}", text)

    def test_the_other_reports_are_not_in_the_readme_section(self):
        shown = {e["slug"] for part in sections.measured_selection(MEASURED, PICKED) for e in part}
        text = section(self.readmes["en"], strings.EN)
        for entry in MEASURED:
            if entry["slug"] not in shown:
                with self.subTest(row=entry["slug"]):
                    self.assertNotIn(f"**[{rows.esc(entry['title'])}]({entry['url']})**", text)

    # START_HERE names a report (hermes-agent-jev-evaluation), which these catalogues drop.
    @mock.patch.object(sections, "START_HERE", [])
    def test_a_short_list_is_shown_whole_and_still_links_its_page(self):
        catalog = [e for e in CATALOG if not rows.is_measured(e)] + MEASURED[:3]
        text = section(build_readme.render(catalog, RETIRED, strings.EN), strings.EN)
        self.assertEqual(len(titles(text)), 3)
        self.assertIn(strings.EN["pattern_all"].format(n=3, page="docs/measured.md", site=rows.reports_link("en")), text)

    # These two catalogues leave the negative results out (START_HERE names one).
    @mock.patch.object(sections, "START_HERE", [])
    def test_without_picks_the_plain_more_line_is_used(self):
        with mock.patch.object(sections, "collection_slugs", return_value=[]):
            text = section(build_readme.render(copy.deepcopy(POSITIVE), RETIRED, strings.EN), strings.EN)
        self.assertIn(
            strings.EN["pattern_more"].format(
                shown=sections.INLINE_MEASURED, n=len(MEASURED_POSITIVE), page="docs/measured.md",
                site=rows.reports_link("en"),
            ),
            text,
        )

    @mock.patch.object(sections, "START_HERE", [])
    def test_when_the_picks_fill_the_section_it_does_not_speak_of_others(self):
        many = [e["slug"] for e in sorted(MEASURED_POSITIVE, key=rows.sort_key)][::-1][: sections.INLINE_MEASURED + 2]
        with mock.patch.object(sections, "collection_slugs", return_value=many):
            text = section(build_readme.render(copy.deepcopy(POSITIVE), RETIRED, strings.EN), strings.EN)
        by_slug = {e["slug"]: e for e in MEASURED_POSITIVE}
        self.assertEqual(titles(text), [rows.esc(by_slug[s]["title"]) for s in many[: sections.INLINE_MEASURED]])
        self.assertIn(
            strings.EN["pattern_more"].format(
                shown=sections.INLINE_MEASURED, n=len(MEASURED_POSITIVE), page="docs/measured.md",
                site=rows.reports_link("en"),
            ),
            text,
        )

    # START_HERE names a report (hermes-agent-jev-evaluation), which this catalogue may drop.
    @mock.patch.object(sections, "START_HERE", [])
    def test_one_report_past_the_limit_is_not_called_all(self):
        n = sections.INLINE_MEASURED + 1
        catalog = [e for e in CATALOG if not rows.is_measured(e)] + MEASURED_POSITIVE[:n]
        with mock.patch.object(sections, "collection_slugs", return_value=[]):
            text = section(build_readme.render(catalog, RETIRED, strings.EN), strings.EN)
        self.assertEqual(len(titles(text)), sections.INLINE_MEASURED)
        self.assertIn(
            strings.EN["pattern_more"].format(
                shown=sections.INLINE_MEASURED, n=n, page="docs/measured.md", site=rows.reports_link("en")
            ),
            text,
        )

    @mock.patch.object(sections, "START_HERE", [])
    def test_no_reports_no_section(self):
        catalog = [e for e in CATALOG if not rows.is_measured(e)]
        readme = build_readme.render(catalog, RETIRED, strings.EN)
        self.assertNotIn(f"## {strings.EN['measured_h']}", readme)
        self.assertNotIn("docs/measured.md", readme)


class PageTest(unittest.TestCase):
    def test_the_page_lists_every_report_once_in_list_order(self):
        # The negative results first, then the rest, each part in list order.
        negatives = sorted((e for e in MEASURED if rows.is_negative(e)), key=rows.sort_key)
        rest = sorted((e for e in MEASURED if not rows.is_negative(e)), key=rows.sort_key)
        self.assertTrue(negatives)
        for pack in PACKS:
            with self.subTest(lang=pack["lang_code"]):
                text = pages.render_measured_page(MEASURED, pack)
                self.assertEqual(titles(text), [rows.esc(e["title"]) for e in negatives + rest])
                head, tail = text.split(f"\n## {pack['others_h']}\n")
                self.assertIn(f"\n## {pack['negative_h']}\n", head)
                self.assertEqual(titles(head), [rows.esc(e["title"]) for e in negatives])

    def test_every_row_keeps_its_caveats_note_and_cited_file(self):
        for pack in PACKS:
            lang = pack["lang_code"]
            text = pages.render_measured_page(MEASURED, pack)
            for entry in MEASURED:
                with self.subTest(lang=lang, row=entry["slug"]):
                    for flag in entry.get("flags", []):
                        self.assertIn(f"`{rows.label(rows.FLAG_LABELS, flag, lang)}`", text)
                    note = entry.get("notes_zh" if lang == "zh" else "notes")
                    if note:
                        self.assertIn(f"  > {rows.esc(note)}", text)
                    url = evidence_url(entry)
                    if url:
                        self.assertIn(f"({rows.md_url(url)})", text)

    def test_the_page_says_what_it_is(self):
        for pack, readme, other in ((strings.EN, "../README.md", "measured.zh-CN.md"), (strings.ZH, "../README.zh-CN.md", "measured.md")):
            lang = pack["lang_code"]
            with self.subTest(lang=lang):
                text = pages.render_measured_page(MEASURED, pack)
                self.assertTrue(text.startswith(f"# {pack['measured_h']}\n"))
                self.assertIn(pack["page_other_lang"].format(other=other), text)
                # The measurements are their authors': the caveat the README gives, given here too.
                self.assertIn(pack["measured_intro"], text)
                self.assertIn(
                    rows.marked(
                        pack, "measured_page_intro", n=len(MEASURED),
                        readme=f"{readme}#{rows.anchor(pack['measured_h'])}",
                        path=rows.collection_link("measured", lang), site=rows.reports_link(lang),
                    ),
                    text,
                )
                self.assertIn(rows.stars_note(pack, catalog="../catalog.json"), text)
                self.assertIn(rows.marked(pack, "call_site_note"), text)
                self.assertTrue(text.endswith(pack["page_footer"] + "\n"))
        self.assertIn("measured_page_intro", strings.ZH_MACHINE)

    def test_it_promises_every_note_not_one_per_report(self):
        # Not every report has a note; the page carries every note there is.
        self.assertTrue([e for e in MEASURED if not e.get("notes")], "some report has no note")
        for key in ("measured_more", "measured_page_intro"):
            with self.subTest(key=key):
                self.assertNotIn("each with its note", strings.EN[key])
                self.assertIn("with every note", strings.EN[key])
                self.assertNotIn("各自的备注", strings.ZH[key])
                self.assertNotIn("每条附备注", strings.ZH[key])
                self.assertIn("全部备注", strings.ZH[key])

    def test_file_order_and_star_counts_inside_a_band_change_nothing(self):
        for pack in PACKS:
            expected = pages.render_measured_page(MEASURED, pack)
            with self.subTest(lang=pack["lang_code"], how="reversed"):
                self.assertEqual(pages.render_measured_page(copy.deepcopy(MEASURED[::-1]), pack), expected)
            for how in ("low", "high"):
                moved = [e for e in moved_within_bands(CATALOG, how) if rows.is_measured(e)]
                with self.subTest(lang=pack["lang_code"], how=how):
                    self.assertEqual(pages.render_measured_page(moved, pack), expected)

    def test_pages_are_written_and_removed_with_the_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = pathlib.Path(tmp)
            with mock.patch.object(pages, "DOCS_DIR", docs):
                written = pages.write_measured_pages(CATALOG)
                self.assertEqual(sorted(p.name for p in written), ["measured.md", "measured.zh-CN.md"])
                self.assertEqual((docs / "measured.md").read_text(), pages.render_measured_page(MEASURED, strings.EN))
                with mock.patch("builtins.print"):
                    self.assertEqual(pages.write_measured_pages([e for e in CATALOG if not rows.is_measured(e)]), [])
                self.assertEqual(sorted(docs.iterdir()), [])


class RegistrationTest(unittest.TestCase):
    PATHS = ("docs/measured.md", "docs/measured.zh-CN.md")

    def test_the_pages_are_generated_outputs(self):
        for path in self.PATHS:
            with self.subTest(path=path):
                self.assertIn(path, regenerate.OUTPUTS)
                self.assertTrue(lint_docs.generated(path))
        self.assertIn("docs/measured.md", dict(regenerate.GENERATORS)["build_readme.py"])

    def test_the_command_writes_them(self):
        self.assertIn("write_measured_pages", build_readme.__all__)
        self.assertIs(build_readme.write_measured_pages, pages.write_measured_pages)

    def test_build_readme_writes_both_pages_from_the_catalogue(self):
        # On a scratch copy with the committed pages gone: build_readme.py itself
        # must write them, or a new report never reaches the page and nothing
        # drifts for the generated-files check to see.
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            copy_tree(tree)
            for path in self.PATHS:
                (tree / path).unlink(missing_ok=True)
            run = subprocess.run(
                [sys.executable, "scripts/build_readme.py"], cwd=tree, check=True, capture_output=True, text=True
            )
            catalog = json.loads((tree / "catalog.json").read_text(encoding="utf-8"))
            measured = [e for e in catalog if rows.is_measured(e)]
            for path, pack in zip(self.PATHS, PACKS):
                with self.subTest(path=path):
                    self.assertEqual((tree / path).read_text(encoding="utf-8"), pages.render_measured_page(measured, pack))
        self.assertIn(f"{len(measured)} independent measurement reports", run.stdout)


if __name__ == "__main__":
    unittest.main()
