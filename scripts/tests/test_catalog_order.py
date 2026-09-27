"""File order of catalog.json must never decide what a reader sees.

Rows that tie on every display key (same official/has_code/stars and a title
that differs only in case, e.g. two forks both called "jev-mcp") used to fall
back to their position in catalog.json. Sorting the file, or two PRs inserting
rows in a different order, would then silently reshuffle the README.
"""

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import build_readme
import lint
import sort_catalog


def row(slug: str, title: str = "jev-mcp", stars: int = 2) -> dict:
    return {"slug": slug, "title": title, "stars": stars, "official": False, "has_code": False}


class DisplayOrderTest(unittest.TestCase):
    def test_full_tie_is_broken_by_slug_whatever_the_file_order(self):
        rows = [row("jev-mcp-freepik-company"), row("jev-mcp-byk"), row("jev-mcp-rajasekharponakala")]
        expected = ["jev-mcp-byk", "jev-mcp-freepik-company", "jev-mcp-rajasekharponakala"]
        for ordering in (rows, list(reversed(rows))):
            with self.subTest(first=ordering[0]["slug"]):
                got = [e["slug"] for e in sorted(ordering, key=build_readme.sort_key)]
                self.assertEqual(got, expected)

    def test_case_only_title_difference_still_breaks_by_slug(self):
        rows = [row("b-row", title="Jev"), row("a-row", title="jev")]
        got = [e["slug"] for e in sorted(rows, key=build_readme.sort_key)]
        self.assertEqual(got, ["a-row", "b-row"])

    def test_slug_is_only_the_last_resort(self):
        rows = [row("a-row", stars=1), row("z-row", stars=9)]
        got = [e["slug"] for e in sorted(rows, key=build_readme.sort_key)]
        self.assertEqual(got, ["z-row", "a-row"])


def quietly(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


class SortCatalogTest(unittest.TestCase):
    """The data files are kept in slug order so concurrent additions do not collide."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)

    def write(self, name: str, rows: list) -> pathlib.Path:
        path = self.dir / name
        path.write_text(sort_catalog.render(rows), encoding="utf-8")
        return path

    def test_sorts_by_slug_and_second_run_changes_nothing(self):
        rows = [
            {"slug": "zeta", "title": "Zeta", "summary_zh": "中文"},
            {"slug": "alpha", "title": "Alpha"},
            {"slug": "jev-mcp-byk", "title": "jev-mcp"},
        ]
        path = self.write("catalog.json", rows)
        self.assertEqual(quietly(sort_catalog.main, [], files=(path,)), 0)
        first = path.read_text(encoding="utf-8")
        self.assertEqual([r["slug"] for r in json.loads(first)], ["alpha", "jev-mcp-byk", "zeta"])
        # Written the way every other writer writes it: no escaped CJK, indent 2.
        self.assertIn("中文", first)
        self.assertEqual(first, json.dumps(json.loads(first), indent=2, ensure_ascii=False) + "\n")

        quietly(sort_catalog.main, [], files=(path,))
        self.assertEqual(path.read_text(encoding="utf-8"), first)
        self.assertEqual(quietly(sort_catalog.main, ["--check"], files=(path,)), 0)

    def test_check_reports_without_rewriting(self):
        path = self.write("catalog.json", [{"slug": "b"}, {"slug": "a"}])
        before = path.read_text(encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = sort_catalog.main(["--check"], files=(path,))
        self.assertEqual(status, 1)
        self.assertEqual(path.read_text(encoding="utf-8"), before)
        self.assertIn("'a' at [1] sorts before 'b'", out.getvalue())
        self.assertIn(sort_catalog.COMMAND, out.getvalue())

    def test_one_appended_row_counts_as_one_to_move(self):
        rows = [{"slug": f"row-{i:04d}"} for i in range(1, 500)] + [{"slug": "row-0000"}]
        self.assertEqual(sort_catalog.misplaced(rows), 1)
        self.assertIn("1 of 500 rows", sort_catalog.order_problem(rows))
        self.assertEqual(sort_catalog.misplaced(sort_catalog.sort_entries(rows)), 0)

    def test_sorting_preserves_every_row(self):
        rows = [{"slug": s, "n": i} for i, s in enumerate(["c", "a-b", "ab", "a", "a0"])]
        got = sort_catalog.sort_entries(rows)
        self.assertEqual([r["slug"] for r in got], ["a", "a-b", "a0", "ab", "c"])
        self.assertEqual(sorted(r["n"] for r in got), list(range(5)))
        self.assertEqual([r["slug"] for r in rows][0], "c", "input list must not be mutated")


class LintOrderTest(unittest.TestCase):
    """lint.py rejects a data file that is not in slug order, and says how to fix it."""

    def setUp(self):
        lint.errors.clear()
        self.addCleanup(lint.errors.clear)

    def test_appended_row_is_an_error_naming_the_script(self):
        lint.check_slug_order("catalog.json", [{"slug": "alpha"}, {"slug": "zeta"}, {"slug": "beta"}])
        self.assertEqual(len(lint.errors), 1)
        self.assertIn("catalog.json", lint.errors[0])
        self.assertIn("'beta'", lint.errors[0])
        self.assertIn("scripts/sort_catalog.py", lint.errors[0])

    def test_sorted_file_passes(self):
        lint.check_slug_order("retired.json", [{"slug": "a"}, {"slug": "b"}])
        self.assertEqual(lint.errors, [])


if __name__ == "__main__":
    unittest.main()
