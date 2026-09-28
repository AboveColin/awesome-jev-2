"""The catalogue's shape: one definition in _stats.shape(), printed by counts.py
and published on docs/shape.md (I49).

Every test renders in memory: pull-request CI runs the unit tests before it
regenerates anything, so a committed page need not be current.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "tests"))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_readme  # noqa: E402
import build_shape  # noqa: E402
import counts  # noqa: E402
import lint_docs  # noqa: E402
import regenerate  # noqa: E402
from readme import strings  # noqa: E402
from test_star_bands import moved_within_bands  # noqa: E402

CATALOG, RETIRED, PATTERNS, COMPAT, SCHEMA = _stats.load()
TAXONOMY = json.loads((ROOT / "taxonomy.json").read_text())

MINI_PATTERNS = [{"key": k, "en": k.title(), "zh": k} for k in ("gate", "route", "rank", "overview")]
MINI_COMPAT = {
    "platforms": [
        {"id": "native", "catalog_platforms": ["typesafe-api"]},
        {"id": "gw", "catalog_platforms": ["gateway-x"]},
    ]
}
MINI_SCHEMA = {"properties": {"kind": {"enum": ["project", "benchmark", "article", "case-study"]}}}


def row(slug: str, **fields) -> dict:
    base = {"slug": slug, "title": slug, "kind": "project", "patterns": ["gate"], "flags": []}
    return {**base, **fields}


MINI = [
    row("a", languages=["python", "go"], platforms=["typesafe-api"], stars=5, patterns=["gate", "route"],
        author={"name": "Ann"}, repo_license="MIT"),
    row("b", languages=["python"], platforms=["gateway-x", "typesafe-api"], stars=50, patterns=["gate", "route"],
        author={"name": " ann "}, repo_license="MIT"),
    row("c", languages=["typescript"], platforms=["claude-code", "typesafe-api"], stars=500, patterns=["route", "rank"],
        author={"name": "ANN"}, repo_license="unknown"),
    row("d", languages=["typescript"], platforms=["self-hosted", "gateway-x"], stars=None, kind="benchmark",
        author={"name": "Bo"}),
    row("e", platforms=[], kind="article", question_types=["choice", "noul"], flags=["paywalled"]),
    row("f", languages=["go"], platforms=["claude-code"], stars=9, patterns=["overview"],
        author={"name": "Bo"}, repo_license="Apache-2.0", flags=["no-license", "paywalled"]),
]


def mini_shape(rows=MINI) -> dict:
    return _stats.shape(rows, MINI_PATTERNS, MINI_COMPAT, MINI_SCHEMA)


class ShapeTest(unittest.TestCase):
    def test_tallies_are_most_first_then_by_name(self):
        shape = mini_shape()
        self.assertEqual(list(shape["languages"].items()), [("go", 2), ("python", 2), ("typescript", 2)])
        self.assertEqual(shape["rows_without_language"], 1)
        self.assertEqual(shape["flags"], {"paywalled": 2, "no-license": 1})
        self.assertEqual(shape["licences"], {"MIT": 2, "Apache-2.0": 1, "unknown": 1})
        self.assertEqual(shape["question_types"], {"choice": 1, "score": 0, "noul": 1})

    def test_patterns_and_kinds_keep_their_own_order_with_zeros(self):
        shape = mini_shape()
        self.assertEqual(list(shape["by_pattern"].items()), [("gate", 4), ("route", 3), ("rank", 1), ("overview", 1)])
        self.assertEqual(
            list(shape["kinds"].items()), [("project", 4), ("benchmark", 1), ("article", 1), ("case-study", 0)]
        )

    def test_every_row_falls_in_exactly_one_platform_group(self):
        shape = mini_shape()
        self.assertEqual(
            shape["platform_tiers"],
            {"typesafe-api-only": 1, "compat-surface": 1, "no-surface": 2, "self-hosted": 1, "none": 1},
        )
        self.assertEqual(list(shape["platform_tiers"]), list(_stats.PLATFORM_TIERS))
        surfaces = _stats.surface_values(MINI_COMPAT)
        self.assertEqual(surfaces, {"gateway-x"})
        cases = {
            (): "none",
            ("typesafe-api",): "typesafe-api-only",
            ("gateway-x",): "compat-surface",
            ("gateway-x", "claude-code"): "compat-surface",
            ("claude-code",): "no-surface",
            ("claude-code", "typesafe-api"): "no-surface",
            ("self-hosted", "gateway-x", "typesafe-api"): "self-hosted",
        }
        for values, tier in cases.items():
            with self.subTest(values=values):
                self.assertEqual(_stats.platform_tier({"platforms": list(values)}, surfaces), tier)

    def test_real_platform_groups_add_up_to_the_catalogue(self):
        shape = _stats.current_shape()
        self.assertEqual(sum(shape["platform_tiers"].values()), len(CATALOG))
        # The default value is not a surface of its own in this count.
        self.assertNotIn(_stats.DEFAULT_PLATFORM, _stats.surface_values(COMPAT))

    def test_stars_are_counted_in_bands_with_the_lower_median(self):
        shape = mini_shape()
        project = shape["stars_by_kind"]["project"]
        # a 5 (band 0), b 50 (band 1), c 500 (band 2), f 9 (band 0): lower median of 0,0,1,2 is 0.
        self.assertEqual(project, {"rows": 4, "with_stars": 4, "bands": [2, 1, 1, 0, 0, 0], "median_band": 0})
        self.assertEqual(shape["stars_by_kind"]["benchmark"]["median_band"], None)
        self.assertEqual(shape["stars_by_kind"]["case-study"]["rows"], 0)
        three = _stats.stars_by_kind([row("x", stars=10), row("y", stars=5000), row("z", stars=1)], ["project"])
        self.assertEqual(three["project"]["median_band"], 1)

    def test_languages_by_pattern_and_pairs(self):
        shape = mini_shape()
        self.assertEqual(shape["languages_by_pattern"]["route"], {"python": 2, "typescript": 1, "go": 1})
        self.assertEqual(shape["top_languages"], ["go", "python", "typescript"])
        self.assertEqual(shape["multi_pattern_rows"], 3)
        self.assertEqual(shape["pattern_pairs"], [["gate", "route", 2], ["route", "rank", 1]])
        # Ties go by patterns.json's order, and only `top` pairs are listed.
        rows = [row("p", patterns=["rank", "gate"]), row("q", patterns=["route", "gate"])]
        self.assertEqual(_stats.pattern_pairs(rows, MINI_PATTERNS, top=1), [["gate", "route", 1]])

    def test_authors_are_aggregates_keyed_by_name_without_case(self):
        self.assertEqual(
            mini_shape()["authors"],
            {"rows_naming_an_author": 5, "authors": 2, "one_row": 0, "two_rows": 1, "three_or_more_rows": 1,
             "most_rows_by_one_author": 3},
        )
        self.assertIsNone(_stats.author_key({"author": {"name": "  "}}))
        self.assertIsNone(_stats.author_key({"author": None}))

    def test_real_shape_is_independent_of_file_order(self):
        self.assertEqual(
            _stats.shape(list(reversed(CATALOG)), PATTERNS, COMPAT, SCHEMA),
            _stats.shape(CATALOG, PATTERNS, COMPAT, SCHEMA),
        )

    def test_a_star_count_moving_inside_its_band_changes_nothing(self):
        moved = moved_within_bands(CATALOG, "random", seed=3)
        self.assertEqual(_stats.shape(moved, PATTERNS, COMPAT, SCHEMA), _stats.shape(CATALOG, PATTERNS, COMPAT, SCHEMA))

    def test_one_definition_of_the_pattern_counts(self):
        self.assertEqual(_stats.compute()["by_pattern"], _stats.current_shape()["by_pattern"])


def page(rows=None, lang="en") -> str:
    inputs = build_shape.Inputs(
        copy.deepcopy(CATALOG if rows is None else rows), PATTERNS, COMPAT, SCHEMA, TAXONOMY
    )
    return build_shape.render(inputs, lang)


class PageTest(unittest.TestCase):
    def test_every_section_in_both_languages(self):
        for lang, headings in (
            ("en", ["## Languages", "## How rows reach Jev", "## Licences", "## Stars by kind",
                    "## Languages by decision pattern", "## Patterns filed together", "## Authors"]),
            ("zh", ["## 语言", "## 各行如何接入 Jev", "## 许可证", "## 按类型看 star", "## 按决策模式看语言",
                    "## 一起归档的模式", "## 作者"]),
        ):
            text = page(lang=lang)
            for heading in headings:
                with self.subTest(lang=lang, heading=heading):
                    self.assertIn(f"\n{heading}\n", text)

    def test_the_page_says_what_it_is_and_is_not(self):
        en, zh = page(lang="en"), page(lang="zh")
        self.assertIn("popularity signal, not a quality verdict", en)
        self.assertIn("not the ecosystem at large", en)
        self.assertIn(f"**{_stats.newest_check(CATALOG)}**", en)
        self.assertIn("Discovery does not tag it", en)
        self.assertIn("发现流程不会标注它", zh)
        self.assertIn("模型撰写（机翻）", zh.splitlines()[6])
        self.assertIn("(sources.md#licences)", en)

    def test_no_author_is_named_and_no_exact_star_count_is_printed(self):
        rows = [row(f"r{i}", stars=123_457 + i, author={"name": f"Zyzzyva{i}"}, languages=["python"],
                    platforms=["typesafe-api"], patterns=["safety-gating"]) for i in range(4)]
        for lang in ("en", "zh"):
            text = page(rows, lang)
            self.assertNotIn("Zyzzyva", text)
            self.assertNotIn("zyzzyva", text)
            self.assertNotIn("12345", text)
            self.assertNotIn("123,45", text)

    def test_the_page_is_independent_of_file_order_and_band_moves(self):
        base = page()
        self.assertEqual(page(list(reversed(CATALOG))), base)
        self.assertEqual(page(moved_within_bands(CATALOG, "high")), base)

    def test_it_prints_the_shape_it_computes(self):
        shape = _stats.current_shape()
        text = page()
        self.assertIn(f"| `python` | {shape['languages']['python']} |", text)
        self.assertIn(f"| `typesafe-api` and nothing else | {shape['platform_tiers']['typesafe-api-only']} |", text)
        self.assertIn(f"{shape['authors']['authors']} different ones", text)

    def test_registered_as_a_generator_and_as_generated(self):
        self.assertIn("build_shape.py", [script for script, _ in regenerate.GENERATORS])
        for rel in ("docs/shape.md", "docs/shape.zh-CN.md"):
            self.assertIn(rel, regenerate.OUTPUTS)
            self.assertTrue(lint_docs.generated(rel))

    def test_the_readmes_link_the_page_in_their_own_language(self):
        en = build_readme.render(copy.deepcopy(CATALOG), copy.deepcopy(RETIRED), strings.EN)
        zh = build_readme.render(copy.deepcopy(CATALOG), copy.deepcopy(RETIRED), strings.ZH)
        self.assertIn("| [`docs/shape.md`](docs/shape.md) |", en)
        self.assertIn("| [`docs/shape.zh-CN.md`](docs/shape.zh-CN.md) |", zh)
        self.assertIn("<sub>(机翻)</sub>", next(line for line in zh.splitlines() if "docs/shape.zh-CN.md" in line))


class CountsTest(unittest.TestCase):
    def test_counts_prints_the_shape_and_counts_nothing_itself(self):
        source = (ROOT / "scripts" / "counts.py").read_text()
        self.assertNotIn("Counter(", source)
        fake = _stats.current_shape()
        fake["languages"] = {"cobol": 9001}
        fake["platform_tiers"] = dict.fromkeys(_stats.PLATFORM_TIERS, 9002)
        fake["authors"] = {**fake["authors"], "authors": 9003}
        fake["licences"] = {"WTFPL": 9004}
        out = io.StringIO()
        with patch.object(_stats, "current_shape", return_value=fake), contextlib.redirect_stdout(out):
            self.assertEqual(counts.main(), 0)
        text = out.getvalue()
        for needle in ("cobol", "9001", "typesafe-api-only", "9002", "authors        9003", "WTFPL", "9004"):
            self.assertIn(needle, text)

    def test_sources_licence_table_is_the_shape_count(self):
        shape = mini_shape()
        self.assertEqual(
            build_docs.licences_block(shape).splitlines()[2:],
            ["| MIT | 2 |", "| Apache-2.0 | 1 |", "| None declared | 1 |"],
        )


if __name__ == "__main__":
    unittest.main()
