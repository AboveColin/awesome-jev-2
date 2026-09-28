"""Evidence by decision pattern: one definition, printed everywhere (I47).

query.evidence_ladder() (the MCP package) counts what the catalogue records
about the rows filed under a pattern: TypeSafe AI's documentation pages, the
cited file by evidence.kind, independent reports, negative results and rows
citing no file. _stats reads it from there, so list_patterns, the Pages API
index, docs/shape.md and every docs/by-pattern/ page print the same numbers,
each saying they are reports counted, not a verdict. Everything renders in
memory: CI runs unit tests before it regenerates.
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
import assemble_site  # noqa: E402
import build_shape  # noqa: E402
import site_api  # noqa: E402
from platform_values import load_query  # noqa: E402
from readme import pages, rows, strings  # noqa: E402

QUERY = load_query()
CATALOG, RETIRED, PATTERNS, COMPAT, SCHEMA = _stats.load()
TAXONOMY = json.loads((ROOT / "taxonomy.json").read_text())
CASES = json.loads((ROOT / "scripts" / "tests" / "negative_cases.json").read_text())["cases"]


def row(slug: str, **fields) -> dict:
    return {"slug": slug, "title": slug, "kind": "project", "patterns": ["gate"], "flags": [], **fields}


FIXTURE = [
    row("docs", kind="official-docs", patterns=["gate", "route"]),
    row("call", evidence={"path": "a.py", "matched": ["x"]}),
    row("call2", evidence={"path": "b.py", "matched": ["x"], "kind": "call-site"}, patterns=["gate", "route"]),
    row("wire", kind="alternative", evidence={"path": "c.py", "matched": ["x"], "kind": "wire-shape"}),
    row("example", evidence={"path": "examples/d.py", "matched": ["x"], "kind": "example-only"}),
    row("bench", kind="benchmark", measurement={"task": "t", "direction": "unfavourable"}),
    row("vendor", kind="benchmark", flags=["vendor-reported"], evidence={"path": "e.py", "matched": ["x"]}),
    row("dropped", kind="plugin", flags=["negative-result"], patterns=["route"]),
]


class LadderTest(unittest.TestCase):
    def test_each_column_on_a_fixture(self):
        self.assertEqual(
            QUERY.evidence_ladder(FIXTURE, "gate"),
            {"total": 7, "official_docs": 1, "call_site": 3, "wire_shape": 1, "example_only": 1,
             "independent_reports": 1, "negative_results": 1, "no_file_cited": 2},
        )
        self.assertEqual(
            QUERY.evidence_ladder(FIXTURE, "route"),
            {"total": 3, "official_docs": 1, "call_site": 1, "wire_shape": 0, "example_only": 0,
             "independent_reports": 0, "negative_results": 1, "no_file_cited": 2},
        )
        self.assertEqual(QUERY.evidence_ladder(FIXTURE)["total"], len(FIXTURE))
        self.assertEqual(tuple(QUERY.evidence_ladder(FIXTURE)), QUERY.LADDER)

    def test_independent_and_negative_are_the_predicates_the_site_shares(self):
        # negative_cases.json holds query.is_independent_report / is_negative_result to
        # the site's isIndependentReport / isNegativeResult (both suites read it), so a
        # ladder over those cases counts exactly what they expect.
        cases = [{**case["entry"], "slug": str(i), "patterns": ["p"]} for i, case in enumerate(CASES)]
        ladder = QUERY.evidence_ladder(cases, "p")
        self.assertEqual(ladder["independent_reports"], sum(case["independent"] for case in CASES))
        self.assertEqual(ladder["negative_results"], sum(case["negative"] for case in CASES))

    def test_one_definition_of_the_cited_file_kind(self):
        edge = [{}, {"evidence": None}, {"evidence": {}}, {"evidence": {"path": "p"}},
                {"evidence": {"path": "p", "kind": "wire-shape"}}, {"evidence": {"path": "p", "kind": ""}}]
        for entry in [*CATALOG, *edge]:
            self.assertEqual(QUERY.evidence_kind(entry), _stats.evidence_kind(entry))
        self.assertEqual(QUERY.EVIDENCE_KINDS, _stats.EVIDENCE_KINDS)

    def test_stats_reads_the_packages_definition(self):
        for p in PATTERNS:
            with self.subTest(pattern=p["key"]):
                self.assertEqual(_stats.evidence_ladder(CATALOG, p["key"]), QUERY.evidence_ladder(CATALOG, p["key"]))
        self.assertEqual(
            _stats.ladder_by_pattern(CATALOG, PATTERNS)["overview"]["total"], _stats.compute()["by_pattern"]["overview"]
        )

    def test_the_note_says_what_the_counts_are(self):
        self.assertIn("Reports counted, not a verdict", QUERY.EVIDENCE_NOTE)
        self.assertIn("not reproduced by this repository", QUERY.EVIDENCE_NOTE)
        for key in QUERY.LADDER[1:]:
            self.assertIn(key, QUERY.EVIDENCE_NOTE)


class SurfacesTest(unittest.TestCase):
    def ladder(self, key: str) -> dict[str, int]:
        return _stats.evidence_ladder(CATALOG, key)

    def test_list_patterns_carries_the_same_numbers(self):
        answer = QUERY.pattern_counts(CATALOG, PATTERNS)
        self.assertIn("not a verdict", answer["evidence_note"])
        for item in answer["patterns"]:
            with self.subTest(pattern=item["key"]):
                ladder = self.ladder(item["key"])
                self.assertEqual(item["examples"], ladder["total"])
                self.assertEqual(item["negative_results"], ladder["negative_results"])
                self.assertEqual(item["evidence"], {k: v for k, v in ladder.items() if k != "total"})

    def test_the_pages_api_index_carries_them_too(self):
        stats = _stats.compute()
        files = site_api.api_files(
            CATALOG, PATTERNS, stats, site_url=assemble_site.SITE_URL, published=assemble_site.RUNTIME_FILES
        )
        index = json.loads(files[site_api.INDEX])
        for item in index["patterns"]:
            self.assertEqual(item["evidence"]["independent_reports"], self.ladder(item["key"])["independent_reports"])

    def test_every_pattern_page_prints_the_line(self):
        for key, under in rows.group_by_pattern(copy.deepcopy(CATALOG)).items():
            if not under:
                continue
            ladder = self.ladder(key)
            for pack, independent, no_file in (
                (strings.EN, "independent reports", "no file cited"), (strings.ZH, "独立报告", "未引用文件"),
            ):
                with self.subTest(pattern=key, lang=pack["lang_code"]):
                    text = pages.render_page(key, under, pack)
                    line = next(line for line in text.splitlines() if "shape" in line and "·" in line)
                    self.assertIn(f"{independent} {ladder['independent_reports']} ·", line)
                    self.assertIn(f"{no_file} {ladder['no_file_cited']}", line)
        zh = pages.render_page("overview", [e for e in CATALOG if "overview" in e["patterns"]], strings.ZH)
        self.assertIn("只是计数，不是结论", zh)
        self.assertIn("<sub>(机翻)</sub>", next(line for line in zh.splitlines() if "只是计数" in line))
        self.assertIn("pattern_evidence", strings.ZH_MACHINE)
        self.assertIn("reports counted, not a verdict", strings.EN["pattern_evidence"])

    def test_the_shape_page_matrix_has_every_pattern_with_its_counts(self):
        inputs = build_shape.Inputs(copy.deepcopy(CATALOG), PATTERNS, COMPAT, SCHEMA, TAXONOMY)
        for lang, heading in (("en", "## Evidence by decision pattern"), ("zh", "## 按决策模式看证据")):
            text = build_shape.render(inputs, lang)
            section = text.split(heading, 1)[1].split("\n## ", 1)[0]
            self.assertIn("not a verdict" if lang == "en" else "不是结论", section)
            for p in PATTERNS:
                with self.subTest(lang=lang, pattern=p["key"]):
                    cells = " | ".join(str(v) for v in self.ladder(p["key"]).values())
                    self.assertIn(f"(by-pattern/{rows.page_name(p['key'], lang)}) | {cells} |", section)
        overview_only = sum(
            1 for e in CATALOG if e["patterns"] == ["overview"] and QUERY.is_independent_report(e)
        )
        self.assertEqual(_stats.current_shape()["overview_only_reports"], overview_only)
        if overview_only:
            self.assertIn(f"{overview_only} independent reports are filed under `overview`",
                          build_shape.render(inputs, "en"))


if __name__ == "__main__":
    unittest.main()
