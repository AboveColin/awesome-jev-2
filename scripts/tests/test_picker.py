"""picker.json, the primitive picker, and its rules (I25).

picker.json arranges TypeSafe's own guidance on choosing a primitive as a
decision list. scripts/picker.py holds the rules lint.py applies to it; the
walk it shares with the site (site/catalog-core.mjs pickerSteps) is held to the
cases in picker_cases.json, which scripts/test_catalog_core.mjs reads too. The
counts beside a leaf come from _stats.primitive_layers_by_pattern. The figure
and the README are tests/test_primitive_picker.py's. Nothing here reads a
committed generated file.
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

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import lint  # noqa: E402
import picker  # noqa: E402

SCHEMA = json.loads((ROOT / "schema" / "entry.schema.json").read_text())
PATTERN_KEYS = [p["key"] for p in json.loads((ROOT / "patterns.json").read_text())["patterns"]]
PRIMITIVES = SCHEMA["properties"]["question_types"]["items"]["enum"]
REAL = picker.load()
CASES = json.loads((ROOT / "scripts" / "tests" / "picker_cases.json").read_text())["cases"]


def node(i: str, yes: str, *, no_node: str = "", no_leaf: str = "", **extra) -> dict:
    no = {"answer": "no", "node": no_node} if no_node else {"answer": "no", "leaf": no_leaf}
    return {
        "id": i,
        "question_en": f"Is it {i}?",
        "question_zh": "是这样吗？",
        "source_url": "https://docs.typesafe.ai/primitives#choose-a-question-type",
        "branches": [{"answer": "yes", "leaf": yes}, no],
        **extra,
    }


def leaf(i: str, **extra) -> dict:
    return {
        "id": i,
        "label_en": f"leaf {i}",
        "label_zh": "一个叶子",
        "note_en": "Say what to do.",
        "note_zh": "说明怎么做。",
        "source_url": "https://docs.typesafe.ai/primitives",
        **extra,
    }


# A made-up list that keeps every rule: two questions, three leaves.
SMALL = {
    "zh_machine": True,
    "start": "first",
    "nodes": [node("first", "code", no_node="second"), node("second", "yes-no", no_leaf="rethink")],
    "leaves": [
        leaf("code"),
        leaf("yes-no", primitive="noul", pattern_key="safety-gating", label_en="noul", label_zh="noul"),
        leaf("rethink"),
    ],
}


def problems(data) -> list[tuple[str, str]]:
    return picker.problems(data, PATTERN_KEYS, PRIMITIVES)


def changed(path: tuple, value) -> dict:
    """SMALL with the value at `path` replaced (None deletes it)."""
    data = copy.deepcopy(SMALL)
    *head, last = path
    target = data
    for key in head:
        target = target[key]
    if value is None:
        del target[last]
    else:
        target[last] = value
    return data


class RealFileTest(unittest.TestCase):
    def test_the_committed_list_keeps_every_rule(self):
        self.assertEqual(problems(REAL), [])

    def test_every_step_and_leaf_cites_a_docs_typesafe_ai_page(self):
        steps, last = picker.walk(REAL)
        for item in [*(n for n, _ in steps), *(l for _, l in steps), last]:
            with self.subTest(item=item["id"]):
                self.assertTrue(item["source_url"].startswith(picker.SOURCE_PREFIX))

    def test_it_reaches_each_primitive_and_names_a_pattern_whose_shape_uses_it(self):
        steps, last = picker.walk(REAL)
        leaves = [l for _, l in steps] + [last]
        self.assertEqual({l["primitive"] for l in leaves if l.get("primitive")}, set(PRIMITIVES))
        patterns_doc = (ROOT / "docs" / "patterns.md").read_text()
        for l in leaves:
            if not l.get("primitive"):
                continue
            with self.subTest(leaf=l["id"]):
                section = patterns_doc.split(f"\n## {l['pattern_key']}\n", 1)[1].split("\n## ", 1)[0]
                shape = re.search(r"\*\*Shape:\*\*(.+?)\n\n", section, re.S).group(1)
                self.assertIn(f"`{l['primitive']}`", shape)

    def test_the_chinese_is_disclosed_as_a_models(self):
        self.assertIs(REAL["zh_machine"], True)

    def test_it_states_no_limit_or_answer_field(self):
        # Limits live in compat.json and answer fields in the primitives
        # figure (build_assets.PRIMS); a copy here would drift from them.
        steps, last = picker.walk(REAL)
        texts = [n[k] for n, _ in steps for k in picker.NODE_TEXT]
        texts += [l[k] for l in [*(l for _, l in steps), last] for k in picker.LEAF_TEXT]
        for text in texts:
            self.assertIsNone(re.search(r"\d|probabilities|confidence|legend|置信度", text), text)

    def test_it_never_calls_itself_a_recommendation(self):
        comment = " ".join(REAL["_comment"])
        self.assertIn("not a recommendation", comment)


class RulesTest(unittest.TestCase):
    """One mutation per rule, each reported exactly once, with its wording."""

    def assert_one(self, data, where: str, words: str):
        found = problems(data)
        self.assertEqual(len(found), 1, found)
        self.assertEqual(found[0][0], where)
        self.assertIn(words, found[0][1])

    def test_the_made_up_list_passes(self):
        self.assertEqual(problems(SMALL), [])

    def test_the_top_level(self):
        self.assertEqual(problems([]), [("picker.json", "must be an object")])
        self.assert_one(changed(("extra",), 1), "picker.json", "unknown field 'extra'")
        self.assert_one(changed(("zh_machine",), "yes"), "picker.json.zh_machine", "must be true")
        found = problems(changed(("zh_machine",), None))
        self.assertIn(("picker.json", "lacks 'zh_machine'"), found)

    def test_ids(self):
        # The branch still names "rethink", so the walk reports it too.
        self.assertIn(("picker.json leaves[Rethink]", "id must be lower-case letters, digits and hyphens"),
                      problems(changed(("leaves", 2, "id"), "Rethink")))
        data = changed(("leaves",), SMALL["leaves"] + [leaf("code")])
        self.assertIn(("picker.json leaves[code]", "repeats an id"), problems(data))

    def test_fields(self):
        self.assert_one(changed(("nodes", 0, "question_zh"), None), "picker.json nodes[first]", "lacks 'question_zh'")
        self.assert_one(changed(("leaves", 0, "colour"), "red"), "picker.json leaves[code]", "unknown field 'colour'")
        self.assert_one(changed(("leaves", 0, "note_en"), " "), "picker.json leaves[code].note_en", "non-empty string")

    def test_chinese_fields_are_chinese_except_a_primitives_own_name(self):
        self.assert_one(changed(("nodes", 1, "question_zh"), "Is it?"), "picker.json nodes[second].question_zh", "not Chinese")
        self.assert_one(changed(("leaves", 0, "label_zh"), "code"), "picker.json leaves[code].label_zh", "not Chinese")
        self.assertEqual(problems(changed(("leaves", 1, "label_zh"), "noul")), [])

    def test_no_number_or_answer_field_in_any_text(self):
        for key, value, fact in (
            ("note_en", "Up to 255 options.", "2"),
            ("label_en", "read the confidence", "confidence"),
            ("note_zh", "读取置信度。", "置信度"),
        ):
            with self.subTest(value=value):
                self.assert_one(changed(("leaves", 0, key), value), f"picker.json leaves[code].{key}", repr(fact))

    def test_every_node_and_leaf_names_its_docs_typesafe_ai_source(self):
        self.assert_one(changed(("nodes", 0, "source_url"), None), "picker.json nodes[first]", "lacks 'source_url'")
        for bad in ("", 7, "https://example.com/primitives", "http://docs.typesafe.ai/primitives",
                    "https://docs.typesafe.ai/", "https://docs.typesafe.ai/a b"):
            with self.subTest(bad=bad):
                found = problems(changed(("nodes", 0, "source_url"), bad))
                self.assertIn(("picker.json nodes[first].source_url", "must name the https://docs.typesafe.ai/ page (and heading) this step follows"), found)
        self.assert_one(changed(("leaves", 2, "source_url"), "https://typesafe.ai/blog"),
                        "picker.json leaves[rethink].source_url", "docs.typesafe.ai")

    def test_a_leaf_names_a_known_primitive_and_pattern_and_never_a_primitive_alone(self):
        self.assert_one(changed(("leaves", 1, "primitive"), "binary"), "picker.json leaves[yes-no].primitive", "'binary'")
        self.assert_one(changed(("leaves", 1, "pattern_key"), "gating"), "picker.json leaves[yes-no].pattern_key", "patterns.json")
        self.assert_one(changed(("leaves", 1, "pattern_key"), None), "picker.json leaves[yes-no]", "no pattern_key")
        # A pattern alone is allowed: the leaf links it and counts nothing.
        self.assertEqual(problems(changed(("leaves", 0, "pattern_key"), "fan-out")), [])

    def test_the_shape_the_figure_draws(self):
        self.assert_one(changed(("start",), "nowhere"), "picker.json start", "not a node id")
        loop = changed(("nodes", 1, "branches", 1), {"answer": "no", "node": "first"})
        found = problems(loop)
        self.assertIn(("picker.json nodes[second]", "no leads back to 'first'; the list must not loop"), found)
        yes_to_node = changed(("nodes", 0, "branches", 0), {"answer": "yes", "node": "second"})
        self.assertEqual(problems(yes_to_node)[0][0], "picker.json nodes[first]")

    def test_every_node_and_leaf_is_reached_once(self):
        stray = changed(("nodes",), SMALL["nodes"] + [node("third", "code", no_leaf="rethink")])
        self.assertEqual(problems(stray), [("picker.json nodes[third]", "is never reached from start")])
        unused = changed(("leaves",), SMALL["leaves"] + [leaf("spare")])
        self.assertEqual(problems(unused), [("picker.json leaves[spare]", "is never reached")])
        twice = changed(("nodes", 1, "branches", 0), {"answer": "yes", "leaf": "code"})
        found = problems(twice)
        self.assertIn(("picker.json leaves[code]", "is reached from more than one node"), found)
        self.assertIn(("picker.json leaves[yes-no]", "is never reached"), found)


class WalkTest(unittest.TestCase):
    def test_the_shared_cases(self):
        self.assertGreaterEqual(len(CASES), 12)
        for case in CASES:
            with self.subTest(case=case["name"]):
                if case["walk"] is None:
                    with self.assertRaises(picker.NotADecisionList):
                        picker.walk(case["picker"])
                    continue
                steps, last = picker.walk(case["picker"])
                self.assertEqual([[n["id"], l["id"]] for n, l in steps], case["walk"]["steps"])
                self.assertEqual(last["id"], case["walk"]["last"])

    def test_sources_are_numbered_once_in_reading_order(self):
        data = copy.deepcopy(SMALL)
        data["nodes"][1]["source_url"] = "https://docs.typesafe.ai/primitives/noul"
        self.assertEqual(
            picker.sources(data),
            ["https://docs.typesafe.ai/primitives#choose-a-question-type", "https://docs.typesafe.ai/primitives",
             "https://docs.typesafe.ai/primitives/noul"],
        )

    def test_counts_only_beside_a_leaf_with_a_primitive_and_a_pattern(self):
        by_pattern = {"safety-gating": {"noul": {"read": 3, "signal_only": 4}}}
        self.assertEqual(picker.layers(SMALL["leaves"][1], by_pattern), {"read": 3, "signal_only": 4})
        self.assertIsNone(picker.layers(SMALL["leaves"][0], by_pattern))
        self.assertIsNone(picker.layers(leaf("x", pattern_key="fan-out"), by_pattern))
        self.assertEqual(picker.layers(leaf("x", primitive="choice", pattern_key="fan-out"), by_pattern),
                         {"read": 0, "signal_only": 0})


class StatsTest(unittest.TestCase):
    ROWS = [
        {"slug": "a", "patterns": ["safety-gating"], "question_types": ["noul"], "primitives_seen": ["noul", "choice"]},
        {"slug": "b", "patterns": ["safety-gating", "fan-out"], "primitives_seen": ["noul"]},
        {"slug": "c", "patterns": ["fan-out"], "question_types": ["score"]},
    ]
    PATTERNS = [{"key": "fan-out"}, {"key": "safety-gating"}, {"key": "recommendation"}]

    def test_the_layers_per_pattern_are_primitive_layers_over_its_rows(self):
        found = _stats.primitive_layers_by_pattern(self.ROWS, self.PATTERNS)
        self.assertEqual(list(found), ["fan-out", "safety-gating", "recommendation"])
        self.assertEqual(found["safety-gating"]["noul"], {"read": 1, "signal_only": 1})
        self.assertEqual(found["safety-gating"]["choice"], {"read": 0, "signal_only": 1})
        self.assertEqual(found["fan-out"]["score"], {"read": 1, "signal_only": 0})
        self.assertEqual(found["recommendation"], _stats.primitive_layers([]))

    def test_stats_json_carries_them_for_the_site(self):
        stats = _stats.compute()
        catalog, _, patterns, _, _ = _stats.load()
        self.assertEqual(stats["primitive_layers_by_pattern"], _stats.primitive_layers_by_pattern(catalog, patterns))


class LintWiringTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        for name in ("CATALOG", "RETIRED", "PICKER_FILE"):
            self.addCleanup(setattr, lint, name, getattr(lint, name))
        lint.CATALOG, lint.RETIRED = self.dir / "catalog.json", self.dir / "retired.json"
        lint.CATALOG.write_text("[]")
        lint.RETIRED.write_text("[]")

    def run_main(self, data) -> tuple[int, str]:
        lint.PICKER_FILE = self.dir / "picker.json"
        lint.PICKER_FILE.write_text(json.dumps(data, ensure_ascii=False))
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            status = lint.main()
        return status, err.getvalue()

    def test_lint_reads_picker_json(self):
        self.assertEqual(self.run_main(REAL), (0, ""))
        broken = copy.deepcopy(REAL)
        broken["leaves"][0]["source_url"] = "https://example.com/"
        status, err = self.run_main(broken)
        self.assertEqual(status, 1)
        self.assertIn(f"error: picker.json leaves[{broken['leaves'][0]['id']}].source_url: must name", err)

    def test_the_primitives_are_the_schemas(self):
        found = lint.check_picker(SCHEMA, [{"key": k} for k in PATTERN_KEYS], changed(("leaves", 1, "primitive"), "boolean"))
        self.assertEqual(len(found.errors), 1)
        self.assertIn("'boolean' is not one of: choice, score, noul", found.errors[0])


if __name__ == "__main__":
    unittest.main()
