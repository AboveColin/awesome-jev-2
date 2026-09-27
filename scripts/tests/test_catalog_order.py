"""File order of catalog.json must never decide what a reader sees.

Rows that tie on every display key (same official/has_code/stars and a title
that differs only in case, e.g. two forks both called "jev-mcp") used to fall
back to their position in catalog.json. Sorting the file, or two PRs inserting
rows in a different order, would then silently reshuffle the README.
"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import build_readme


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


if __name__ == "__main__":
    unittest.main()
