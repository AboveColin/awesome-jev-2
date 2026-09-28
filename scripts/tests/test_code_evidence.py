"""Every row with code cites a file or says why it cannot (I17).

lint.py used to ask for `evidence` or `evidence_none` only when a row set
`question_types`, which 100 of 1,207 rows did; 34 rows with code carried
neither and nothing noticed. Since 2026-09-27 a row with code in a GitHub
repository is held to the same rule. These tests pin the backfill that made
it true, the count _stats publishes, and the places that explain the fields.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import lint  # noqa: E402

SCHEMA = json.loads((ROOT / "schema" / "entry.schema.json").read_text())
CATALOG = json.loads((ROOT / "catalog.json").read_text())


def compute(rows: list[dict]) -> dict:
    patterns = [{"key": "tool-selection"}]
    schema = {"properties": {"kind": {"enum": ["project"]}}}
    with patch.object(_stats, "load", return_value=(rows, [], patterns, {"platforms": []}, schema)):
        return _stats.compute()


def row(slug: str, **fields) -> dict:
    return {"slug": slug, "title": slug, "url": f"https://github.com/o/{slug}", "kind": "project",
            "patterns": ["tool-selection"], **fields}


class CountTest(unittest.TestCase):
    def test_rows_with_code_and_neither_field_are_counted_on_any_host(self):
        rows = [
            row("bare", has_code=True),
            row("docs", has_code=True, url="https://docs.example.com/page"),
            row("cited", has_code=True, evidence={"path": "a.py", "matched": ["system_one"]}),
            row("reason", has_code=True, evidence_none="docs-page"),
            row("prose", has_code=False),
        ]
        self.assertEqual(compute(rows)["has_code_unbacked"], 2)


class BackfillTest(unittest.TestCase):
    def test_no_row_with_code_is_left_without_either_field(self):
        left = [e["slug"] for e in CATALOG if e.get("has_code") and not (e.get("evidence") or e.get("evidence_none"))]
        self.assertEqual(left, [])
        self.assertEqual(_stats.compute()["has_code_unbacked"], 0)

    def test_lint_holds_every_current_row_to_the_rule(self):
        found = []
        for i, entry in enumerate(CATALOG):
            errors, _ = lint.check_entry_invariants(entry, f"catalog.json[{i}]", retired=False)
            found += [e for e in errors if "carries neither evidence nor evidence_none" in e]
        self.assertEqual(found, [])

    def test_a_row_marked_without_code_lists_no_languages(self):
        # The backfill turned four rows' has_code off; a language on such a row
        # would describe code the row now says it does not have.
        self.assertEqual([e["slug"] for e in CATALOG if not e.get("has_code") and e.get("languages")], [])


class ExplanationTest(unittest.TestCase):
    def test_the_schema_no_longer_ties_evidence_to_question_types_alone(self):
        props = SCHEMA["properties"]
        for field in ("evidence", "evidence_none"):
            with self.subTest(field=field):
                text = props[field]["description"]
                self.assertNotIn("primitive claim in question_types", text)
                self.assertIn("has_code", text)
                self.assertIn("GitHub", text)

    def test_every_evidence_none_value_lint_suggests_exists(self):
        enum = set(SCHEMA["properties"]["evidence_none"]["enum"])
        self.assertIn("no-jev-call-site", enum)
        errors, _ = lint.check_entry_invariants(row("x", has_code=True, languages=["python"]), "p", retired=False)
        (message,) = errors
        suggested = set(re.findall(r"[a-z]+(?:-[a-z]+)+", message.split("(")[-1]))
        self.assertTrue(suggested)
        self.assertLessEqual(suggested, enum)

    def test_the_site_explains_every_evidence_none_a_row_uses(self):
        page = (ROOT / "site" / "index.html").read_text()
        block = page[page.index("const evidenceContext"):]
        block = block[: block.index("}[key]")]
        explained = set(re.findall(r'^\s*"([a-z-]+)":', block, re.M))
        used = {e["evidence_none"] for e in CATALOG if e.get("evidence_none")}
        self.assertLessEqual(used, explained)


if __name__ == "__main__":
    unittest.main()
