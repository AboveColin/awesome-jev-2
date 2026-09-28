"""compat.json's surfaces and the catalogue's `platforms` values, joined (I30).

A row records how it reaches Jev in the catalogue's own words; compat.json
names surfaces under ids of its own. Each surface now lists the values that
stand for it (`catalog_platforms`), marked coarse when a value does not tell
it apart from another route, and taxonomy.json lists the values no surface
claims. These tests hold lint's rules (scripts/platform_values.py), the
generated "Catalogued examples" column (scripts/build_compat.py) and the one
definition they share with the MCP server (src/awesome_jev_mcp/query.py).
Nothing here reads a committed generated file.
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_compat  # noqa: E402
import lint  # noqa: E402
import platform_values as pv  # noqa: E402

COMPAT = json.loads((ROOT / "compat.json").read_text())
TAXONOMY = json.loads((ROOT / "taxonomy.json").read_text())
CATALOG = json.loads((ROOT / "catalog.json").read_text())
RETIRED = json.loads((ROOT / "retired.json").read_text())

# A made-up compat.json and list: ids and values are fixtures.
SMALL = {"platforms": [
    {"id": "native", "name": "Native", "catalog_platforms": ["api"], "granularity": "coarse"},
    {"id": "gw-a", "name": "Gateway A", "catalog_platforms": ["gw"], "granularity": "coarse"},
    {"id": "gw-b", "name": "Gateway B", "catalog_platforms": ["gw"], "granularity": "coarse"},
    {"id": "edge", "name": "Edge", "catalog_platforms": ["edge-ai"]},
    {"id": "docs", "name": "Docs", "catalog_platforms": []},
]}
WITHOUT = ["github", "self-hosted"]


def rows(*values_per_row: list[str]) -> list[dict]:
    return [{"slug": f"r{i}", "platforms": list(v)} for i, v in enumerate(values_per_row)]


class CompatRulesTest(unittest.TestCase):
    def problems(self, compat=SMALL, without=WITHOUT) -> list[tuple[str, str]]:
        return pv.compat_problems(compat, without)

    def changed(self, index: int, **fields) -> dict:
        compat = copy.deepcopy(SMALL)
        for key, value in fields.items():
            if value is None:
                compat["platforms"][index].pop(key, None)
            else:
                compat["platforms"][index][key] = value
        return compat

    def test_the_fixture_and_the_real_files_keep_every_rule(self):
        self.assertEqual(self.problems(), [])
        self.assertEqual(pv.problems(CATALOG, RETIRED, COMPAT, TAXONOMY), [])

    def test_every_surface_lists_its_values(self):
        self.assertEqual(self.problems(self.changed(4, catalog_platforms=None)), [(
            "compat.json", "surface 'docs' has no catalog_platforms: list the values rows record in `platforms` "
            "for it, or [] when none stands for it")])
        for bad in ("edge-ai", ["edge-ai", "edge-ai"], [""], [" edge-ai"], [3]):
            with self.subTest(catalog_platforms=bad):
                found = self.problems(self.changed(3, catalog_platforms=bad))
                self.assertEqual(len(found), 1, found)
                self.assertIn("surface 'edge': catalog_platforms must be a list of distinct", found[0][1])

    def test_granularity_is_coarse_or_absent(self):
        found = self.problems(self.changed(3, granularity="fine"))
        self.assertEqual(found, [("compat.json", "surface 'edge': granularity is 'fine'; it is 'coarse' or absent")])

    def test_a_value_two_surfaces_list_is_coarse_on_both(self):
        found = self.problems(self.changed(2, granularity=None))
        self.assertEqual(found, [("compat.json", "'gw' is in the catalog_platforms of 'gw-a', 'gw-b', so it does "
                                  "not tell them apart: set granularity 'coarse' on 'gw-b'")])
        # One surface may still call its own value coarse (typesafe-api covers
        # rows reaching the native API through a pass-through too).
        self.assertEqual(self.problems(self.changed(0, catalog_platforms=["api"])), [])

    def test_the_list_without_a_surface_is_sorted_distinct_and_claims_nothing(self):
        for bad in (["self-hosted", "github"], ["github", "github"], "github", ["github", ""]):
            with self.subTest(without=bad):
                self.assertEqual(self.problems(without=bad), [
                    ("taxonomy.json", "platforms_without_surface must be a sorted list of distinct, non-empty strings")])
        self.assertEqual(self.problems(without=["edge-ai", "github"]), [(
            "taxonomy.json", "platforms_without_surface lists 'edge-ai', which compat.json surface 'edge' claims: "
            "keep it in one place")])


class RowRulesTest(unittest.TestCase):
    def test_every_recorded_value_is_claimed_or_listed(self):
        data = rows(["api", "github"], ["gw"], [], ["self-hosted", "edge-ai"])
        self.assertEqual(pv.row_problems("catalog.json", data, SMALL, WITHOUT), [])
        found = pv.row_problems("retired.json", rows(["api"], ["Edge-AI", "vercel"]), SMALL, WITHOUT)
        self.assertEqual([where for where, _ in found], ["retired.json[1]", "retired.json[1]"])
        self.assertEqual(found[0][1], (
            "r1: platforms value 'Edge-AI' is in no compat.json surface's catalog_platforms and not in "
            "taxonomy.json platforms_without_surface: fix the spelling, add it to the catalog_platforms of the "
            "surface it reaches Jev through, or list it there"))

    def test_both_files_are_read(self):
        found = pv.problems(rows(["nope"]), rows(["gone"]), SMALL, {"platforms_without_surface": WITHOUT})
        self.assertEqual([where for where, _ in found], ["catalog.json[0]", "retired.json[0]"])

    def test_a_row_without_platforms_or_a_malformed_one_is_the_schemas_business(self):
        data = [{"slug": "a"}, {"slug": "b", "platforms": "api"}, "not a row", {"slug": "c", "platforms": [3]}]
        self.assertEqual(pv.row_problems("catalog.json", data, SMALL, WITHOUT), [])

    def test_every_value_the_real_catalogue_records_is_joined(self):
        claimed = {v for p in COMPAT["platforms"] for v in p["catalog_platforms"]}
        without = set(TAXONOMY[pv.WITHOUT_SURFACE])
        recorded = {v for e in CATALOG + RETIRED for v in e.get("platforms", [])}
        self.assertEqual(recorded - claimed - without, set())
        self.assertEqual(claimed & without, set())


class RealMappingTest(unittest.TestCase):
    """The judgements the mapping makes, pinned so a change to them is deliberate."""

    def surface(self, key: str) -> dict:
        return next(p for p in COMPAT["platforms"] if p["id"] == key)

    def test_the_vercel_routes_and_the_native_api_are_coarse(self):
        coarse = {p["id"] for p in COMPAT["platforms"] if p.get("granularity") == "coarse"}
        self.assertEqual(coarse, {"typesafe-native", "vercel-eval", "vercel-compat", "ai-sdk-direct"})
        # The provider package itself (the ai-sdk-typesafe-provider row) records vercel-ai-sdk.
        self.assertEqual(self.surface("ai-sdk-direct")["catalog_platforms"], ["vercel-ai-sdk"])
        self.assertEqual(self.surface("vercel-compat")["catalog_platforms"], ["vercel-ai-gateway"])
        self.assertEqual(self.surface("vercel-eval")["catalog_platforms"], ["vercel-ai-gateway", "vercel-ai-sdk"])
        self.assertEqual(self.surface("typesafe-native")["catalog_platforms"], ["typesafe-api"])

    def test_typesafe_api_is_recorded_beside_a_gateways_value(self):
        # Why typesafe-native is coarse: rows reaching the API through another
        # surface record typesafe-api too.
        others = {v for p in COMPAT["platforms"] if p["id"] != "typesafe-native" for v in p["catalog_platforms"]}
        beside = [e["slug"] for e in CATALOG if "typesafe-api" in e.get("platforms", []) and others & set(e["platforms"])]
        self.assertIn("bifrost-typesafe-gateway", beside)
        self.assertIn("vercel-typesafe-compatible-api", beside)

    def test_no_row_was_given_a_finer_value(self):
        # The mapping joined vocabularies; it made no row's value finer than
        # its evidence. compat ids that are not also catalogue values stay
        # out of every row.
        ids_only = {p["id"] for p in COMPAT["platforms"]} - {v for p in COMPAT["platforms"] for v in p["catalog_platforms"]}
        self.assertEqual(ids_only, {"typesafe-native", "vercel-eval", "vercel-compat", "ai-sdk-direct", "cloudflare"})
        self.assertEqual([e["slug"] for e in CATALOG + RETIRED if ids_only & set(e.get("platforms", []))], [])


class OneDefinitionTest(unittest.TestCase):
    def test_scripts_use_the_mcp_packages_rule(self):
        query = pv.load_query()
        self.assertEqual(pathlib.Path(query.__file__).resolve(), (ROOT / "src/awesome_jev_mcp/query.py").resolve())
        self.assertIs(sys.modules["awesome_jev_query"], query)
        import site_api  # noqa: PLC0415 - loads the same file under the same name

        self.assertIs(site_api.load_query(), query)

    def test_lint_imports_no_package_code_until_it_checks(self):
        # review_pr.py imports lint.py from a copy of scripts/ alone.
        source = (ROOT / "scripts" / "platform_values.py").read_text()
        module_level = [line for line in source.splitlines() if line.startswith(("query =", "_query ="))]
        self.assertEqual(module_level, [])

    def test_counts_agree_with_search_examples(self):
        query = pv.load_query()
        counts = pv.surface_counts(COMPAT, CATALOG)
        self.assertEqual(list(counts), [p["id"] for p in COMPAT["platforms"]])
        for key, n in counts.items():
            with self.subTest(surface=key):
                found = query.search(CATALOG, [], (), COMPAT, platform=key, include_non_jev=True)
                self.assertEqual(found["total_matching"], n)


class LintWiringTest(unittest.TestCase):
    def test_check_all_holds_the_real_files_to_the_rules(self):
        schema = json.loads((ROOT / "schema" / "entry.schema.json").read_text())
        errors = lint.check_all(schema, CATALOG, RETIRED).errors
        self.assertEqual([e for e in errors if "platforms" in e or "catalog_platforms" in e], [])
        bad = copy.deepcopy(CATALOG)
        bad[0] = {**bad[0], "platforms": ["vercel"]}
        errors = lint.check_all(schema, bad, RETIRED).errors
        self.assertEqual(len([e for e in errors if "platforms value 'vercel'" in e]), 1, errors)

    def test_the_schema_says_where_the_values_come_from(self):
        about = json.loads((ROOT / "schema" / "entry.schema.json").read_text())["properties"]["platforms"]["description"]
        self.assertIn("catalog_platforms", about)
        self.assertIn("platforms_without_surface", about)


class ExamplesColumnTest(unittest.TestCase):
    TEXT = "".join(f"<!-- {name}:start -->\n<!-- {name}:end -->\n" for name in build_compat.BLOCKS)
    CELLS = ("model", "yesno", "answer_field", "confidence", "envelope", "endpoint", "env")

    def rendered(self, compat, catalog) -> str:
        data = {"as_of": "2031-01-01", "limits": [], **compat}
        for p in data["platforms"]:
            p.setdefault("url", f"https://d.example/{p['id']}")
            p.setdefault("notes", f"About {p['name']}.")
            for cell in self.CELLS:
                p.setdefault(cell, "—")
        text = build_compat.build(data, self.TEXT, catalog)
        return text.split("<!-- notes:start -->\n", 1)[1].split("\n<!-- notes:end -->", 1)[0]

    def test_the_last_table_counts_links_and_says_coarse(self):
        body = self.rendered(copy.deepcopy(SMALL), rows(["api", "gw"], ["gw"], ["edge-ai"], ["github"]))
        lines = body.splitlines()
        self.assertEqual(lines[0], "| Surface | Worth knowing | Catalogued examples |")
        site = "https://kydlikebtc.github.io/awesome-jev/"
        self.assertEqual(lines[2], f"| [Native](https://d.example/native) | About Native. | "
                                   f"[1]({site}?platform=native&lang=en) · `api` (coarse) |")
        self.assertIn(f"| [2]({site}?platform=gw-a&lang=en) · `gw` (coarse) |", lines[3])
        self.assertIn(f"| [1]({site}?platform=edge&lang=en) · `edge-ai` |", lines[5])
        self.assertTrue(lines[6].endswith("| About Docs. | — |"), lines[6])

    def test_the_count_follows_the_rows_not_their_order(self):
        catalog = rows(["api"], ["gw"], ["edge-ai"], ["api", "gw"])
        self.assertEqual(self.rendered(copy.deepcopy(SMALL), catalog),
                         self.rendered(copy.deepcopy(SMALL), catalog[::-1]))
        more = self.rendered(copy.deepcopy(SMALL), catalog + rows(["edge-ai"]))
        self.assertIn("[2](https://kydlikebtc.github.io/awesome-jev/?platform=edge&lang=en)", more)

    def test_the_real_page_carries_a_count_for_every_surface(self):
        text = build_compat.build()
        counts = pv.surface_counts(COMPAT, CATALOG)
        for key, n in counts.items():
            with self.subTest(surface=key):
                self.assertIn(f"[{n}](https://kydlikebtc.github.io/awesome-jev/?platform={key}&lang=en)", text)
        # Only the notes table has the column; the other five are unchanged.
        self.assertEqual(text.count("| Catalogued examples |"), 1)
        # The hand-written prose explains it and states no count itself.
        self.assertIn("The *Catalogued examples* column counts", text)


if __name__ == "__main__":
    unittest.main()
