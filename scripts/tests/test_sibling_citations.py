"""Which sibling directories cite each row (I16).

1,053 rows named one and the same source, the sibling-list aggregate, and the
harvest that knew which lists cited a repository kept only the count. Now
sibling_lists.py harvests once for both discover_candidates.py and
attribute_sources.py, and the weekly run records one `sources` item per list
whose README links a row's repository, after the sources a person wrote,
sorted by URL. Here: the one shape of a citation, the harvest, the rules for
adding, keeping and dropping one, lint's rules, the counts and where they are
published, and that nothing of a list but its name and URL is taken.
No network: every README is a string handed to a fake fetch.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import pathlib
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _github  # noqa: E402
import _stats  # noqa: E402
import attribute_sources as attr  # noqa: E402
import build_docs  # noqa: E402
import discover_candidates as dc  # noqa: E402
import lint  # noqa: E402
import sibling_lists as sl  # noqa: E402

# The same cases as scripts/test_catalog_core.mjs: the Python and the site's
# rule must agree on what a citation is.
SHAPES = [
    ({"catalog": "heyjunpenn/awesome-jev", "url": "https://github.com/heyjunpenn/awesome-jev"}, True),
    ({"catalog": "Omrigotlieb/awesome-jev", "url": "https://github.com/Omrigotlieb/awesome-jev"}, True),
    ({"catalog": "a.b/c-d_e.f", "url": "https://github.com/a.b/c-d_e.f"}, True),
    ({"catalog": "heyjunpenn/awesome-jev", "url": "https://github.com/heyjunpenn/awesome-jev/"}, False),
    ({"catalog": "heyjunpenn/Awesome-Jev", "url": "https://github.com/heyjunpenn/awesome-jev"}, False),
    ({"catalog": "heyjunpenn's list", "url": "https://github.com/heyjunpenn/awesome-jev"}, False),
    ({"catalog": "maintainer submission", "url": "https://github.com/kydlikebtc/awesome-jev"}, False),
    (
        {
            "catalog": "sibling-list aggregate (docs/sibling-lists.txt)",
            "url": "https://github.com/kydlikebtc/awesome-jev/blob/main/docs/sibling-lists.txt",
        },
        False,
    ),
    ({"catalog": "a/b/c", "url": "https://github.com/a/b/c"}, False),
    ({"catalog": "a/..", "url": "https://github.com/a/.."}, False),
    ({"catalog": "a/b", "url": "http://github.com/a/b"}, False),
    ({"catalog": "a/b", "url": "https://github.com/a/b", "note": "x"}, False),
    ({"catalog": "a/b"}, False),
]

AGGREGATE = {
    "catalog": "sibling-list aggregate (docs/sibling-lists.txt)",
    "url": "https://github.com/kydlikebtc/awesome-jev/blob/main/docs/sibling-lists.txt",
}
A = "https://github.com/alpha/awesome-jev"
B = "https://github.com/Beta/jev-list"
C = "https://github.com/gamma/awesome-jev"
LISTED = [A, B, C]
# Words a notice or a surface must never attach to a citation count.
VERDICT = re.compile(r"\b(?:verified|confidence|trusted|quality)\b", re.I)


def row(slug: str, url: str, *sources: dict, **extra) -> dict:
    return {"slug": slug, "title": slug, "url": url, "sources": list(sources) or [AGGREGATE], "license": "CC0-1.0", **extra}


def harvest_of(readmes: dict[str, str]) -> sl.Harvest:
    """A harvest over LISTED where `readmes` gives each reached list's text."""
    return sl.harvest(LISTED, fetch=lambda url: (url, readmes.get(url, "")), workers=2)


class ShapeTest(unittest.TestCase):
    def test_a_citation_is_exactly_one_shape(self):
        for source, cited in SHAPES:
            with self.subTest(source=source):
                self.assertIs(sl.is_citation(source), cited)

    def test_no_source_a_person_wrote_looks_like_one(self):
        # Before the backfill no row had a source of this shape; after it,
        # every row's person-written sources are still not of it.
        for name in ("catalog.json", "retired.json"):
            for entry in json.loads((ROOT / name).read_text(encoding="utf-8")):
                kept = [s for s in entry["sources"] if not sl.is_citation(s)]
                self.assertTrue(kept, entry["slug"])

    def test_list_lines_become_citation_urls(self):
        self.assertEqual(sl.list_url("https://github.com/Beta/jev-list/"), B)
        self.assertEqual(sl.list_url("  https://github.com/Beta/jev-list  "), B)
        self.assertIsNone(sl.list_url("https://github.com/Beta/jev-list/tree/main"))
        self.assertIsNone(sl.list_url("https://gitlab.com/a/b"))
        self.assertEqual(sl.listed_urls([A, A + "/", "# c", B, "https://example.com/x"]), [A, B])
        self.assertEqual(sl.citation(B), {"catalog": "Beta/jev-list", "url": B})
        self.assertTrue(sl.is_citation(sl.citation(B)))

    def test_read_lists_skips_comments_and_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "lists.txt"
            path.write_text(f"# header\n\n{A}\n  # indented comment\n{B}\n")
            self.assertEqual(sl.read_lists(path), [A, B])

    def test_the_real_lists_are_all_repository_roots(self):
        lines = sl.read_lists()
        self.assertEqual(len(sl.listed_urls(lines)), len(lines))

    def test_this_repository_is_the_one_github_knows(self):
        self.assertEqual(sl.SELF, _github.SELF)

    def test_own_repository(self):
        self.assertEqual(sl.own_repository({"url": "https://github.com/Acme/Tool.git"}), "acme/tool")
        self.assertEqual(
            sl.own_repository({"url": "https://acme.dev", "repo": "https://github.com/acme/tool/tree/main/x"}),
            "acme/tool",
        )
        self.assertIsNone(sl.own_repository({"url": "https://github.com/kydlikebtc/awesome-jev/tree/main/examples/x"}))
        self.assertIsNone(sl.own_repository({"url": "https://docs.typesafe.ai/"}))


class HarvestTest(unittest.TestCase):
    def test_which_lists_cite_which_repository(self):
        found = harvest_of({
            A: "see https://github.com/Acme/Tool and https://github.com/acme/tool.git and "
               "https://github.com/sponsors/acme and https://github.com/other/thing",
            B: "https://github.com/ACME/tool",
        })
        self.assertEqual(found.reached, (A, B))
        self.assertEqual(found.unreached, (C,))
        self.assertEqual(found.cited["acme/tool"], frozenset({A, B}))
        self.assertEqual(found.cited["other/thing"], frozenset({A}))
        self.assertNotIn("sponsors/acme", found.cited)
        # A list naming a repository twice still cites it once.
        self.assertEqual(found.counts()["acme/tool"], 2)

    def test_a_list_returning_an_earlier_lists_readme_is_counted_once(self):
        # GitHub serves a renamed repository's README under its old name too,
        # so one directory listed under both names must not cite a row twice.
        text = "https://github.com/acme/tool https://github.com/acme/other"
        found = harvest_of({A: text, B: "https://github.com/acme/tool", C: text})
        self.assertEqual(found.reached, (A, B, C))
        self.assertEqual(found.same, ((C, A),))
        self.assertEqual(found.cited["acme/tool"], frozenset({A, B}))
        self.assertEqual(found.cited["acme/other"], frozenset({A}))
        self.assertEqual(harvest_of({A: "x", B: "y"}).same, ())

    def test_ties_break_by_name_not_by_chance(self):
        found = harvest_of({A: "https://github.com/zz/b https://github.com/aa/b https://github.com/mm/b"})
        self.assertEqual([slug for slug, _ in found.counts().most_common()], ["aa/b", "mm/b", "zz/b"])

    def test_discover_keeps_which_lists_cited_each_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            lists = pathlib.Path(tmp) / "sibling-lists.txt"
            lists.write_text(f"{A}\n{B}\n")
            # Two lists' READMEs, each its own text (one identical to another would count once).
            readmes = {A: "https://github.com/zz-new/hit", B: "- https://github.com/zz-new/hit"}
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(dc, "SIBLINGS", lists), \
                    mock.patch.object(dc, "fetch_readme", lambda url: (url, readmes.get(url, ""))), \
                    mock.patch.object(dc, "inspect", lambda slug: {"slug": slug, "verdict": "no-signal"}), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(dc.main(["--top", "5", "--json"]), 0, err.getvalue())
        results = json.loads(out.getvalue())
        self.assertEqual(results, [{"slug": "zz-new/hit", "verdict": "no-signal", "cited_by": 2, "cited_lists": [B, A]}])
        self.assertIn("reached 2/2 lists", err.getvalue())


class AttributeTest(unittest.TestCase):
    def test_citations_follow_the_sources_a_person_wrote_sorted_by_url(self):
        entry = row("tool", "https://github.com/acme/tool", AGGREGATE, {"catalog": "web search", "url": "https://x.example"})
        before = copy.deepcopy(entry)
        new = attr.attributed(entry, harvest_of({C: "- https://github.com/acme/tool", A: "https://github.com/acme/tool"}), LISTED)
        self.assertEqual(entry, before, "the row passed in is not changed")
        self.assertEqual(list(new), list(entry), "same keys, same order")
        self.assertEqual(new["sources"], [*before["sources"], sl.citation(A), sl.citation(C)])

    def test_a_list_read_follows_its_readme_and_one_not_read_keeps_what_it_had(self):
        entry = row("tool", "https://github.com/acme/tool", AGGREGATE, sl.citation(A), sl.citation(C))
        # A read, no longer links it; C not read; B read and links it now.
        found = sl.harvest(LISTED, fetch=lambda url: (url, {A: "nothing", B: "https://github.com/acme/tool"}.get(url, "")))
        new = attr.attributed(entry, found, LISTED)
        self.assertEqual(new["sources"], [AGGREGATE, sl.citation(B), sl.citation(C)])
        self.assertEqual(attr.compare(entry, new), {"slug": "tool", "added": [B], "removed": [A]})

    def test_a_list_no_longer_listed_loses_its_citations_even_offline(self):
        entry = row("tool", "https://github.com/acme/tool", AGGREGATE, sl.citation(C), sl.citation(A))
        new = attr.attributed(entry, None, [A, B])
        self.assertEqual(new["sources"], [AGGREGATE, sl.citation(A)], "C dropped, the rest sorted")

    def test_offline_adds_nothing(self):
        entry = row("tool", "https://github.com/acme/tool")
        self.assertEqual(attr.attributed(entry, None, LISTED), entry)

    def test_a_list_never_cites_its_own_row(self):
        entry = row("alpha-list", A)
        found = harvest_of({A: f"{A} https://github.com/x/y", B: A})
        self.assertEqual(attr.attributed(entry, found, LISTED)["sources"], [AGGREGATE, sl.citation(B)])

    def test_rows_without_a_repository_of_their_own_are_cited_by_none(self):
        found = harvest_of({A: "https://github.com/kydlikebtc/awesome-jev https://github.com/acme/tool"})
        example = row("example-x", "https://github.com/kydlikebtc/awesome-jev/tree/main/examples/x")
        # C was not read this time, and still a row with no repository keeps none of it.
        docs = row("docs", "https://docs.example.com", AGGREGATE, sl.citation(A), sl.citation(C))
        self.assertEqual(attr.attributed(example, found, LISTED), example)
        self.assertEqual(attr.attributed(docs, found, LISTED)["sources"], [AGGREGATE])
        self.assertEqual(attr.attributed(docs, None, LISTED)["sources"], [AGGREGATE])

    def test_a_second_run_changes_nothing(self):
        catalog = [row("tool", "https://github.com/acme/tool"), row("other", "https://github.com/acme/other")]
        found = harvest_of({A: "https://github.com/acme/tool", B: "https://github.com/acme/tool https://github.com/acme/other"})
        once, changes = attr.attribute(catalog, found, LISTED)
        self.assertEqual(len(changes), 2)
        twice, again = attr.attribute(once, found, LISTED)
        self.assertEqual((twice, again), (once, []))

    def test_only_limits_the_rows(self):
        catalog = [row("tool", "https://github.com/acme/tool"), row("other", "https://github.com/acme/other")]
        found = harvest_of({A: "https://github.com/acme/tool https://github.com/acme/other"})
        rows, changes = attr.attribute(catalog, found, LISTED, "oth")
        self.assertEqual([c["slug"] for c in changes], ["other"])
        self.assertIs(rows[0], catalog[0])


class MainTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        self.lists = self.dir / "sibling-lists.txt"
        self.lists.write_text("# lists\n" + "\n".join(LISTED) + "\n")
        self.catalog = self.dir / "catalog.json"
        self.rows = [row("tool", "https://github.com/acme/tool"), row("docs", "https://docs.example.com")]
        self.catalog.write_text(json.dumps(self.rows, indent=2) + "\n")
        self.readmes = {A: "https://github.com/acme/tool", B: "- https://github.com/acme/tool"}
        for name, value in (("SIBLINGS", self.lists), ("CATALOG", self.catalog)):
            patcher = mock.patch.object(attr, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(attr, "fetch_readme", lambda url: (url, self.readmes.get(url, "")))
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = attr.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_write_records_the_citations_and_ends_on_the_counts(self):
        code, out, _ = self.run_main("--write")
        self.assertEqual(code, 0)
        written = json.loads(self.catalog.read_text())
        self.assertEqual(written[0]["sources"], [AGGREGATE, sl.citation(A), sl.citation(B)])
        self.assertEqual(written[1], self.rows[1])
        self.assertEqual(
            out.splitlines()[-1],
            "sibling-list citations: 1 of 2 row(s) changed (2 added, 0 removed); read 2 of 3 list(s); "
            "1 not read, their citations kept as last read",
        )
        self.assertIn("  ~ tool: +alpha/awesome-jev +Beta/jev-list", out)

    def test_a_directory_listed_under_two_names_is_recorded_once(self):
        # C answers with A's README (a renamed list): its citation goes, A's stays.
        self.rows[0]["sources"] = [AGGREGATE, sl.citation(A), sl.citation(C)]
        self.catalog.write_text(json.dumps(self.rows, indent=2) + "\n")
        self.readmes = {A: "https://github.com/acme/tool", B: "nothing", C: "https://github.com/acme/tool"}
        code, out, _ = self.run_main("--write")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(self.catalog.read_text())[0]["sources"], [AGGREGATE, sl.citation(A)])
        self.assertIn(f"      {C} = {A}", out)
        self.assertTrue(out.splitlines()[-1].endswith("; 1 returned an earlier list's README, counted once"), out)

    def test_the_real_file_lists_a_current_name_before_its_old_one(self):
        # The two renamed directories: the old name follows the current one,
        # so the citations are recorded under the name GitHub answers to now.
        lines = sl.listed_urls(sl.read_lists())
        for current, old in (
            ("https://github.com/AbdelStark/awesome-typesafe-jev", "https://github.com/AbdelStark/awesome-typesafe"),
            ("https://github.com/OmniJev/awesome-jev-gallery", "https://github.com/OmniJev/awesome-jev"),
        ):
            with self.subTest(current=current):
                self.assertLess(lines.index(current), lines.index(old))
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        cited = {url for entry in catalog for url in sl.citations_of(entry)}
        self.assertNotIn("https://github.com/AbdelStark/awesome-typesafe", cited)
        self.assertNotIn("https://github.com/OmniJev/awesome-jev", cited)

    def test_nothing_is_written_without_write_or_without_a_change(self):
        before = self.catalog.read_bytes()
        self.run_main()
        self.assertEqual(self.catalog.read_bytes(), before)
        self.run_main("--write")
        written = self.catalog.read_bytes()
        self.catalog.write_bytes(written)
        stamp = self.catalog.stat().st_mtime_ns
        code, out, _ = self.run_main("--write")
        self.assertEqual((code, self.catalog.stat().st_mtime_ns), (0, stamp))
        self.assertIn("0 of 2 row(s) changed", out.splitlines()[-1])

    def test_when_no_list_answers_nothing_is_written(self):
        self.readmes = {}
        before = self.catalog.read_bytes()
        code, out, err = self.run_main("--write")
        self.assertEqual(code, 1)
        self.assertEqual(self.catalog.read_bytes(), before)
        self.assertIn("::warning title=Sibling lists not read::", err)
        self.assertTrue(out.splitlines()[-1].startswith("sibling-list citations: "))

    def test_offline_reads_nothing(self):
        with mock.patch.object(attr, "fetch_readme", side_effect=AssertionError("read a list")):
            code, out, _ = self.run_main("--offline", "--write")
        self.assertEqual(code, 0)
        self.assertIn("(offline)", out.splitlines()[-1])

    def test_the_digest_counts_and_opens_no_notice(self):
        digest = self.dir / "digest.md"
        digest.write_text("Re-read 2 repositories: 0 rows changed, 0 of them stars only.\n")
        self.run_main("--write", "--digest", str(digest))
        text = digest.read_text()
        self.assertTrue(text.startswith("Re-read 2 repositories"), "appended, the refresh's first line kept")
        self.assertIn("1 rows gained or lost a sibling directory", text)
        self.assertIn("`gamma/awesome-jev`", text, "a list not read is named")
        self.assertNotIn("tool", text, "no row is named")
        workflow = (ROOT / ".github" / "workflows" / "metadata.yml").read_text()
        grep = next(line for line in workflow.splitlines() if "grep -qE" in line and "digest.md" in line)
        self.assertIsNone(re.search(grep.split('"')[1], text), "citations alone land silently")
        self.assertIsNone(VERDICT.search(text))

    def test_a_row_only_put_back_in_order_is_not_counted_as_a_change_of_citations(self):
        changes = [{"slug": "a", "added": [], "removed": []}, {"slug": "b", "added": [A], "removed": []}]
        found = harvest_of({A: "", B: "x", C: "y"})
        text = attr.digest(changes, found, LISTED)
        self.assertIn("1 rows gained or lost a sibling directory citing their repository (1 citations added, 0 removed)", text)
        self.assertIn("1 rows had their citations put back in URL order.", text)
        self.assertEqual(attr.digest([], harvest_of({A: "x", B: "x", C: "x"}), LISTED), "", "a quiet week adds nothing")

    def test_json(self):
        code, out, err = self.run_main("--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["changed"], [{"slug": "tool", "added": [A, B], "removed": []}])
        self.assertEqual((data["unreached"], data["listed"]), ([C], 3))
        self.assertIn("sibling-list citations: ", err)


class LintTest(unittest.TestCase):
    GOOD = row("tool", "https://github.com/acme/tool", AGGREGATE, sl.citation(A), sl.citation(B))

    def errors(self, entry: dict) -> tuple[str, ...]:
        return lint.check_sibling_citations(entry, "catalog.json[0]").errors

    def test_the_weekly_shape_passes(self):
        self.assertEqual(self.errors(self.GOOD), ())
        self.assertEqual(lint.check_citation_lists([self.GOOD], LISTED), lint.Findings())

    def test_each_rule_names_what_is_wrong(self):
        cases = {
            "out of order": (row("t", "https://github.com/acme/tool", AGGREGATE, sl.citation(B), sl.citation(A)), "sorted by url"),
            "twice": (row("t", "https://github.com/acme/tool", AGGREGATE, sl.citation(A), sl.citation(A)), "each once"),
            "before a person's source": (row("t", "https://github.com/acme/tool", sl.citation(A), AGGREGATE), "after every other"),
            "only citations": (row("t", "https://github.com/acme/tool", sl.citation(A)), "keep the source saying where"),
            "no repository": (row("t", "https://docs.example.com", AGGREGATE, sl.citation(A)), "no GitHub repository"),
            "this repository": (row("t", "https://github.com/kydlikebtc/awesome-jev/tree/main/examples/x", AGGREGATE, sl.citation(A)), "no GitHub repository"),
            "itself": (row("t", A, AGGREGATE, sl.citation(A)), "cannot cite its own row"),
        }
        for name, (entry, words) in cases.items():
            with self.subTest(case=name):
                errors = self.errors(entry)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(words, errors[0])

    def test_every_row_is_held_to_them_in_both_files(self):
        broken = row("t", "https://github.com/acme/tool", AGGREGATE, sl.citation(B), sl.citation(A))
        for retired in (False, True):
            with self.subTest(retired=retired):
                errors = lint.check_entry_invariants(broken, "x[0]", retired=retired).errors
                self.assertTrue(any("sorted by url" in error for error in errors), errors)

    def test_a_list_the_file_does_not_name_is_one_error_however_many_rows(self):
        rows = [self.GOOD, row("t2", "https://github.com/acme/t2", AGGREGATE, sl.citation(A))]
        errors = lint.check_citation_lists(rows, [B, C]).errors
        self.assertEqual(errors, (
            f"catalog.json: 2 row(s) cite {A} in sources, a list docs/sibling-lists.txt does not name; "
            f"run {lint.CITATION_FIX} to drop them",
        ))

    def test_lint_main_reads_the_list_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            for name in ("CATALOG", "RETIRED", "SIBLINGS"):
                self.addCleanup(setattr, lint, name, getattr(lint, name))
            lint.CATALOG, lint.RETIRED, lint.SIBLINGS = folder / "c.json", folder / "r.json", folder / "l.txt"
            entry = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))[0]
            entry = {**entry, "sources": [*[s for s in entry["sources"] if not sl.is_citation(s)], sl.citation(A)]}
            lint.CATALOG.write_text(json.dumps([entry]))
            lint.RETIRED.write_text("[]")
            for listed, status in ((f"{B}\n", 1), (f"{A}\n", 0)):
                with self.subTest(listed=listed):
                    lint.SIBLINGS.write_text(listed)
                    err = io.StringIO()
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                        self.assertEqual(lint.main(), status, err.getvalue())
                    self.assertEqual("docs/sibling-lists.txt does not name" in err.getvalue(), bool(status))

    def test_the_real_catalogue_keeps_the_rules(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        for entry in catalog:
            self.assertEqual(self.errors(entry), (), entry["slug"])
        self.assertEqual(lint.check_citation_lists(catalog, sl.listed_urls(sl.read_lists())).errors, ())

    def test_only_the_weekly_script_writes_citations(self):
        # Every other script leaves sources alone; a draft carries the aggregate only.
        for path in sorted((ROOT / "scripts").glob("*.py")):
            if path.name in ("attribute_sources.py", "sibling_lists.py"):
                continue
            with self.subTest(script=path.name):
                self.assertNotIn("citation(", path.read_text(encoding="utf-8").replace("is_citation(", ""))


class PublishedTest(unittest.TestCase):
    CATALOG = [
        row("a", "https://github.com/acme/a", AGGREGATE, sl.citation(A), sl.citation(B)),
        row("b", "https://github.com/acme/b", AGGREGATE, sl.citation(A)),
        row("c", "https://github.com/acme/c"),
        row("d", "https://docs.example.com", {"catalog": "web search", "url": "https://x.example"}),
        row("e", "https://github.com/kydlikebtc/awesome-jev/tree/main/examples/e"),
    ]

    def test_cited_by_counts_rows_with_a_repository_only(self):
        self.assertEqual(_stats.cited_by(self.CATALOG), {"0": 1, "1": 1, "2": 1})
        self.assertEqual(json.loads(json.dumps(_stats.cited_by(self.CATALOG))), _stats.cited_by(self.CATALOG))

    def test_the_status_table_groups_counts_into_ranges_that_add_up(self):
        stats = {"cited_by": {"0": 7, "1": 18, "2": 89, "3": 100, "5": 50, "6": 10, "20": 3, "21": 2, "45": 1}}
        text = build_docs.cited_by_block(stats)
        self.assertIn("| 3–5 | 150 |", text)
        self.assertIn("| 11–20 | 3 |", text)
        self.assertIn("| 21 or more | 3 |", text)
        total = sum(int(line.rsplit("|", 2)[1]) for line in text.splitlines()[2:])
        self.assertEqual(total, sum(stats["cited_by"].values()))
        self.assertIsNone(VERDICT.search(text))

    def test_sources_md_gives_the_lists_one_line_and_a_table_of_their_own(self):
        table = build_docs.sources_block(self.CATALOG)
        self.assertIn(f"| {build_docs.CITATIONS_ROW} | {build_docs.CITATIONS_ANCHOR} | 2 |", table)
        self.assertIn("| sibling-list aggregate (docs/sibling-lists.txt) |", table)
        self.assertNotIn("alpha/awesome-jev", table)
        lists = build_docs.citations_block(self.CATALOG, LISTED)
        self.assertEqual(
            lists.splitlines()[2:],
            [f"| [alpha/awesome-jev]({A}) | 2 |", f"| [Beta/jev-list]({B}) | 1 |", f"| [gamma/awesome-jev]({C}) | 0 |"],
        )
        # The anchor points at the heading the table sits under.
        sources_md = (ROOT / "docs" / "sources.md").read_text(encoding="utf-8")
        self.assertIn("### Sibling directories linking catalogued repositories\n", sources_md)
        self.assertIn("(#sibling-directories-linking-catalogued-repositories)", build_docs.CITATIONS_ANCHOR)

    def test_the_real_counts_agree_with_the_rows(self):
        stats = _stats.compute()
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(stats["cited_rows"], sum(1 for e in catalog if sl.citations_of(e)))
        self.assertEqual(sum(stats["cited_by"].values()), stats["citable_rows"])
        rendered = build_docs.render()
        status = rendered[ROOT / "docs" / "status.md"]
        self.assertIn(f"| {stats['cited_rows']} of {stats['citable_rows']} |", status)
        self.assertIn("<!-- cited-by:start -->\n| Sibling directories linking the repository | Rows |", status)
        llms = rendered[ROOT / "llms.txt"]
        self.assertIn(f"re-read weekly (<!--n:cited_rows-->{stats['cited_rows']}<!--/n--> rows", llms)

    def test_the_site_counts_and_lists_them_in_both_languages(self):
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        for key in ("cited_one", "cited_n", "cited_h", "cited_about"):
            self.assertEqual(html.count(f"{key}: "), 2, key)
        self.assertIn("siblingCitations(e)", html)
        self.assertIn("The Chinese of the four sibling-citation strings below is model-written", html)
        about = re.findall(r'cited_about: "([^"]+)"', html)
        self.assertTrue(all("not a check" in text or "不是对项目的核查" in text for text in about), about)


if __name__ == "__main__":
    unittest.main()
