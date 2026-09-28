"""A Jev release changes compat.json and nothing else (I23).

The model names verify_claims.py and discover_candidates.py look for come from
compat.json, with a pinned version it does not list still counted; a claim
that lost only its pinned version is `version-moved`, counted per version and
given a proposed rewrite that is never written; lint_docs.py holds versioned
vendor links, compat.json's own prose, the MCP server's source and the plugin
manifests to compat.json, and rehearses a release with --simulate-model. No
network: every read is replaced."""

from __future__ import annotations

import ast
import contextlib
import copy
import datetime as dt
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = pathlib.Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import _github  # noqa: E402
import _stats  # noqa: E402
import build_compat  # noqa: E402
import discover_candidates as dc  # noqa: E402
import lint_docs  # noqa: E402
import review_rows as rr  # noqa: E402
import verify_claims as vc  # noqa: E402
import verify_compat  # noqa: E402

# compat.json as it stood when the lists were typed in: the derived signals must
# reproduce the old list exactly, so no proposal changes for today's files.
TODAY = {"platforms": [{"model": "jev-latest · jev-1.13.0"}, {"model": "typesafe/jev-1.13 · ~typesafe/jev-latest"}]}
OLD_STRONG = [
    "api.typesafe.ai", "typesafe_sdk", "@typesafe-ai/sdk", "@ai-sdk/typesafe-ai", "typesafe-ai/jev",
    "typesafe/jev", "jev-latest", "jev-1.13", "/v1/systemone", "systemOne", "system_one",
    "langchain_typesafe", "TypeSafeClient", "AsyncTypeSafeClient",
]
RELEASED = {"platforms": [{"model": "jev-latest · jev-preview · jev-1.14.0"}, {"model": "typesafe/jev-1.14"}]}


def string_constants(path: pathlib.Path) -> list[str]:
    """Every string literal in a module's code, docstrings left out."""
    tree = ast.parse(path.read_text())
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
        and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)
    }
    return [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings
    ]


class SignalsTest(unittest.TestCase):
    def test_model_names_come_from_compat_json(self):
        self.assertEqual(_github.version_signals(TODAY), ("jev-latest", "jev-1.13"))
        self.assertEqual(_github.version_signals(RELEASED), ("jev-latest", "jev-preview", "jev-1.14"))
        # Another product's versioned name in a gateway's id is not Jev's.
        self.assertEqual(_github.version_signals({"platforms": [{"model": "acme/other-jev-3.1 · jev-latest"}]}), ("jev-latest",))
        # The real file: every name is an alias or a major.minor, and every
        # jev-* name a cell records contains one of them.
        real = json.loads((ROOT / "compat.json").read_text())
        names = _github.version_signals()
        for name in names:
            self.assertRegex(name, r"^jev-(?:[a-z]+|\d+\.\d+)$")
        for platform in real["platforms"]:
            for name in _github.MODEL_NAME.findall(platform["model"]):
                self.assertTrue(any(n in name for n in names), name)

    def test_todays_compat_gives_the_list_both_scripts_typed_in(self):
        self.assertEqual(list(_github.strong(_github.version_signals(TODAY))), OLD_STRONG)

    def test_a_version_compat_json_does_not_list_still_counts(self):
        models = _github.version_signals(TODAY)
        body = 'client = TypeSafeClient(); model = "jev-1.14.0"; fallback = "jev-latest"'
        self.assertEqual(_github.strong_signals(body, models), ["jev-latest", "jev-1.14", "TypeSafeClient"])
        # A listed version is not counted twice; other projects' versions and names are not versions.
        self.assertEqual(_github.strong_signals("jev-1.13.0 typesafe/jev-1.13", models), ["typesafe/jev", "jev-1.13"])
        for text in ("my-jev-1.2", "jev-2048", "ajev-1.2", "v.jev-1.2", "jev-latest-ish"):
            with self.subTest(text=text):
                found = _github.strong_signals(text, models)
                self.assertFalse([s for s in found if s.startswith("jev-") and s != "jev-latest"], found)
        # After a release the old pin is still a signal, through the fallback.
        self.assertIn("jev-1.13", _github.strong_signals('"jev-1.13.0"', _github.version_signals(RELEASED)))

    def test_neither_script_keeps_its_own_list_or_a_typed_in_version(self):
        for module in (vc, dc):
            with self.subTest(module=module.__name__):
                self.assertFalse(hasattr(module, "STRONG"))
        for path in (SCRIPTS / "verify_claims.py", SCRIPTS / "discover_candidates.py", SCRIPTS / "_stats.py",
                     SCRIPTS / "_github.py", ROOT / "src" / "awesome_jev_mcp" / "server.py"):
            with self.subTest(path=path.name):
                typed = [s for s in string_constants(path) if _github.VERSION.search(s)]
                self.assertEqual(typed, [], "a model version typed into code goes stale with the next release")

    def test_discovery_judges_a_candidate_by_the_shared_signals(self):
        meta = {"html_url": "https://github.com/a/b", "stargazers_count": 3, "language": "Python"}
        tree = {"tree": [{"type": "blob", "path": "jev_client.py"}]}
        with mock.patch.object(dc, "api_get", side_effect=[meta, tree]), \
             mock.patch.object(dc, "default_branch", return_value="main"), \
             mock.patch.object(dc, "raw_get", return_value='payload = {"model": "jev-7.1.0"}'):
            result = dc.inspect("a/b")
        self.assertEqual(result["verdict"], "calls-jev")
        self.assertEqual(result["matched"], ["jev-7.1"])

    def test_evidence_proposals_quote_the_version_the_file_names(self):
        tree = {"tree": [{"type": "blob", "path": "jev.py"}]}
        with mock.patch.object(vc, "default_branch", return_value="main"), \
             mock.patch.object(vc, "api_get", return_value=tree), \
             mock.patch.object(vc, "raw_get", return_value='system_one(model="jev-7.1.0")'):
            proposal = vc.discover({"slug": "x", "url": "https://github.com/a/b", "has_code": True})
        self.assertEqual(proposal["matched"], ["jev-7.1", "system_one"])


ROW = {"slug": "pinned", "url": "https://github.com/a/b",
       "evidence": {"path": "src/x.py", "matched": ["jev-1.13", "system_one"], "read_on": "2026-09-01"}}


def read_as(body: str | None):
    """Patch verify_claims' reads so every file at every branch is `body`."""
    stack = contextlib.ExitStack()
    stack.enter_context(mock.patch.object(vc, "raw_get", return_value=body))
    stack.enter_context(mock.patch.object(vc, "default_branch", return_value="main"))
    return stack


class VersionMovedTest(unittest.TestCase):
    def test_only_a_lost_version_with_another_in_the_file_is_a_move(self):
        cases = (
            (["jev-1.13"], 'model="jev-1.14.0"', ["jev-1.14"]),
            (["jev-1.13.0"], 'model="jev-1.14.0" or "jev-1.12"', ["jev-1.12", "jev-1.14"]),
            (["typesafe/jev-1.13"], "typesafe/jev-1.14", ["jev-1.14"]),
            (["jev-1.13"], 'model="jev-latest"', []),  # moved to an alias: not a pin
            (["jev-1.13", "system_one"], 'model="jev-1.14.0"', []),  # more than the version went
            (["typesafe/jev-1.13"], "jev-1.13.0", []),  # same version, another spelling
            ([], "jev-1.14", []),
        )
        for missing, body, pins in cases:
            with self.subTest(missing=missing, body=body):
                self.assertEqual(vc.moved_to(missing, body), pins)

    def test_the_rewrite_keeps_how_precisely_the_version_was_written(self):
        body = 'client.system_one(model="jev-1.14.2", route="typesafe/jev-1.14")'
        self.assertEqual(vc.rewrite(["jev-1.13", "system_one"], body, "jev-1.14"), ["jev-1.14", "system_one"])
        self.assertEqual(vc.rewrite(["jev-1.13.0"], body, "jev-1.14"), ["jev-1.14.2"])
        self.assertEqual(vc.rewrite(["typesafe/jev-1.13"], body, "jev-1.14"), ["typesafe/jev-1.14"])
        # Nothing in the file reads like the rewritten string: a person reads it.
        self.assertIsNone(vc.rewrite(['model="jev-1.13"'], body, "jev-1.14"))

    def test_the_check_says_version_moved_with_a_proposal(self):
        with read_as('client.system_one(model="jev-1.14.0")'):
            result = vc.check(ROW)
        self.assertEqual(result["status"], "version-moved")
        self.assertEqual(result["pins"], ["jev-1.14"])
        self.assertEqual(result["proposed"], ["jev-1.14", "system_one"])
        self.assertIn("no longer contains ['jev-1.13']; it names jev-1.14 instead", result["detail"])
        for body, status in (('client.system_one(model="jev-latest")', "claim-gone"),
                             ('client.other(model="jev-1.14.0")', "claim-gone"),
                             ('client.system_one(model="jev-1.13.0")', "ok")):
            with self.subTest(body=body), read_as(body):
                self.assertEqual(vc.check(ROW)["status"], status)

    def test_a_moved_file_still_gives_its_text_signals(self):
        result = {"slug": "pinned", "status": "version-moved", "primitive_signals": ["noul"]}
        self.assertEqual(vc.seen_after(result), ["noul"])

    def run_main(self, rows, body, *argv):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = pathlib.Path(tmp) / "catalog.json"
            catalog.write_text(json.dumps(rows))
            before = catalog.read_bytes()
            summary = pathlib.Path(tmp) / "summary.md"
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(vc, "CATALOG", catalog), \
                 mock.patch.object(sys, "argv", ["verify_claims.py", *argv]), \
                 mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}), \
                 read_as(body), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = vc.main()
            self.assertEqual(catalog.read_bytes(), before, "nothing is ever written")
            return code, out.getvalue(), err.getvalue(), summary.read_text() if summary.exists() else ""

    def rows(self):
        moved = [dict(ROW, slug=f"moved-{i}", url=f"https://github.com/a/m{i}") for i in range(2)]
        gone = dict(ROW, slug="gone", evidence={"path": "x.py", "matched": ["TypeSafeClient"]})
        return moved + [gone]

    def test_the_report_counts_moved_rows_per_version_and_still_fails(self):
        code, out, _, summary = self.run_main(self.rows(), 'system_one(model="jev-1.14.0")')
        self.assertEqual(code, 1)
        self.assertEqual(out.count("  VERSION-MOVED"), 2)
        self.assertIn("  CLAIM-GONE   gone", out)
        self.assertIn("version-moved: 2 row(s) now pin jev-1.14 — ", out)
        self.assertIn("--propose-version-rewrite", out)
        self.assertIn("checked 3 of 3 claim(s): 3 failed, 0 skipped", summary)
        self.assertIn("2 of the failures only moved to another model version", summary)

    def test_json_groups_the_moves(self):
        _, out, _, _ = self.run_main(self.rows(), 'system_one(model="jev-1.14.0")', "--json")
        data = json.loads(out)
        self.assertEqual(data["version_moved"], {"jev-1.14": ["moved-0", "moved-1"]})
        self.assertEqual(len(data["failed"]), 3)

    def test_the_rewrite_dry_run_prints_and_writes_nothing(self):
        code, out, _, _ = self.run_main(self.rows(), 'system_one(model="jev-1.14.0")', "--propose-version-rewrite")
        self.assertEqual(code, 0)
        self.assertIn('    matched:  ["jev-1.13", "system_one"]\n    proposed: ["jev-1.14", "system_one"]', out)
        self.assertNotIn("gone", out.replace("claim-gone", ""))
        self.assertNotIn("read_on", out.replace("leave read_on as it is", "").replace("read_on stays", ""))
        self.assertIn("version rewrites: 2 of 3 cited row(s) version-moved, 2 with a proposed evidence.matched", out)
        _, out, err, _ = self.run_main(self.rows(), 'system_one(model="jev-1.14.0")', "--propose-version-rewrite", "--json")
        self.assertEqual([r["proposed"] for r in json.loads(out)], [["jev-1.14", "system_one"]] * 2)
        self.assertEqual({key for r in json.loads(out) for key in r}, {"slug", "path", "matched", "proposed", "pins"})
        self.assertIn("Nothing written", err)

    def test_the_dry_run_is_its_own_mode(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.run_main(self.rows(), "", "--propose-version-rewrite", "--discover")

    def test_the_review_card_names_the_version_and_the_fix(self):
        answer = {"slug": "pinned", "status": "version-moved", "pins": ["jev-1.14"],
                  "proposed": ["jev-1.14", "system_one"], "detail": "x"}
        net = rr.Net(claim=lambda row: answer, facts=None, commits=None, link=None)
        (finding,) = rr.check_call_site(dict(ROW, has_code=True), net, "")
        self.assertEqual(finding.level, "error")
        self.assertIn("names `jev-1.14` where `evidence.matched` quotes another model version", finding.text)
        self.assertIn("As the file reads now: `jev-1.14`, `system_one`.", finding.text)


class StatsSignalTest(unittest.TestCase):
    def test_a_single_pinned_version_is_thin_whichever_it_is(self):
        def row(matched):
            return {"evidence": {"path": "a.py", "matched": matched}}

        for matched, thin in ((["jev-1.13"], True), (["jev-9.4.1"], True), (["jev-latest"], True),
                              (["jev-2048"], False), (["jev-1.13", "noul"], False)):
            with self.subTest(matched=matched):
                self.assertEqual(_stats.single_model_name(row(matched)), thin)


class LintDocsTest(unittest.TestCase):
    ALLOWED = {"https://docs.example/model-notes/jev-1.13"}

    def test_the_mcp_server_the_plugin_and_the_issue_forms_are_read(self):
        files = lint_docs.fact_file_list(lint_docs.hand_written_files())
        for rel in ("src/awesome_jev_mcp/server.py", ".claude-plugin/plugin.json", ".github/ISSUE_TEMPLATE/config.yml"):
            self.assertIn(rel, files)

    def test_a_versioned_vendor_link_must_be_recorded(self):
        text = ("See [notes](https://docs.example/model-notes/jev-1.13).\n"
                "Old: https://docs.example/model-notes/jev-1.12, and https://docs.example/jev-1.13/x.\n"
                "Not versions: https://github.com/a/jev-2048 https://x.example/my-jev-1.2\n")
        found = lint_docs.check_versioned_urls("d.md", text, self.ALLOWED)
        self.assertEqual(len(found), 2, found)
        self.assertTrue(found[0].startswith("d.md:2: links 'https://docs.example/model-notes/jev-1.12'"))
        self.assertIn("'https://docs.example/jev-1.13/x'", found[1])

    def test_generated_pages_keep_their_catalogue_links(self):
        compat = {"platforms": [{"model": "jev-1.13.0", "docs_url": sorted(self.ALLOWED)}], "limits": [
            {"k": "choice options", "n": {"max": 255}}, {"k": "score levels", "n": {"min": 2, "max": 10}},
            {"k": "context", "n": {"request_k": 64, "state_k": 32}}]}
        text = "a row about https://docs.example/model-notes/jev-1.12\n"
        texts = {"README.md": text, "docs/vetting.md": text}
        with mock.patch.object(lint_docs, "check_compat_prose", return_value=[]):
            found = lint_docs.vendor_problems(compat, ["README.md", "docs/vetting.md"], texts)
        self.assertEqual([p.split(":", 1)[0] for p in found], ["docs/vetting.md"])

    def test_every_run_reads_compat_json_prose(self):
        compat = {"platforms": [{"model": "jev-1.13.0"}], "limits": [
            {"k": "choice options", "n": {"max": 255}}, {"k": "score levels", "n": {"min": 2, "max": 10}},
            {"k": "context", "n": {"request_k": 64, "state_k": 32}}],
            "not_model_strings": [{"s": "x", "why": "Send jev-9.9.9 instead."}]}
        found = lint_docs.vendor_problems(compat, [])
        self.assertEqual(len(found), 1)
        self.assertRegex(found[0], r"^compat\.json:\d+: not_model_strings 'x' why: model string 'jev-9\.9\.9'")

    def test_compat_json_prose_is_held_to_its_own_model_cells(self):
        compat = copy.deepcopy(json.loads((ROOT / "compat.json").read_text()))
        raw = (ROOT / "compat.json").read_text()
        self.assertEqual(lint_docs.check_compat_prose(compat, lint_docs.vendor_facts(compat), raw), [])
        released, _ = lint_docs.simulated_compat(compat, "jev-99.0.0")
        found = lint_docs.check_compat_prose(released, lint_docs.vendor_facts(released), raw)
        self.assertTrue(found)
        for problem in found:
            self.assertRegex(problem, r"^compat\.json:\d+: \w+ '[^']+' \w+: model string ")

    def test_a_blockquoted_inline_value_starts_a_line_too(self):
        self.assertTrue(lint_docs.check_leading_markers("d.md", "> <!--n:x-->1<!--/n--> rows\n"))
        self.assertEqual(lint_docs.check_leading_markers("d.md", "> on <!--n:x-->1<!--/n--> rows\n"), [])


class RehearsalTest(unittest.TestCase):
    COMPAT = {
        "platforms": [
            {"id": "native", "model": "jev-latest · jev-1.13.0", "docs_url": "https://d.example/limits/jev-1.13"},
            {"id": "gateway", "model": "acme/jev-1.13 · acme/jev-1.12"},
        ]
    }

    def test_the_newest_version_moves_everywhere_at_its_precision(self):
        then, old = lint_docs.simulated_compat(self.COMPAT, "jev-1.14.0")
        self.assertEqual(old, "jev-1.13")
        self.assertEqual([p["model"] for p in then["platforms"]], ["jev-latest · jev-1.14.0", "acme/jev-1.14 · acme/jev-1.12"])
        self.assertEqual(then["platforms"][0]["docs_url"], "https://d.example/limits/jev-1.14")
        self.assertEqual(self.COMPAT["platforms"][0]["model"], "jev-latest · jev-1.13.0", "the input is left alone")
        then, _ = lint_docs.simulated_compat(self.COMPAT, "jev-2.0")
        self.assertEqual(then["platforms"][0]["model"], "jev-latest · jev-2.0.0")

    def test_only_a_newer_versioned_id_is_rehearsed(self):
        for model in ("jev-latest", "1.14.0", "jev-1.13.5", "jev-1.12"):
            with self.subTest(model=model), self.assertRaises(SystemExit) as caught:
                lint_docs.simulated_compat(self.COMPAT, model)
            self.assertIn("error:", str(caught.exception.code))

    def test_the_rehearsal_on_this_tree_writes_nothing_and_lists_what_to_edit(self):
        watched = [ROOT / name for name in ("compat.json", "catalog.json", "docs/compatibility.md")]
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in watched]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(lint_docs.main(["--simulate-model", "jev-99.0.0"]), 0)
        self.assertEqual([(p.read_bytes(), p.stat().st_mtime_ns) for p in watched], before)
        text = out.getvalue()
        self.assertIn("Release rehearsal: compat.json with jev-99.0.0 in place of ", text)
        self.assertIn("Would fail lint_docs: ", text)
        entries = [line.strip() for line in text.split("Each is a copy to edit:\n", 1)[1].split("\n\n", 1)[0].splitlines()
                   if line.startswith("  ") and not line.startswith("    ")]
        listed = [entry.split()[0] for entry in entries]
        for rel, entry in zip(listed, entries):
            self.assertTrue((ROOT / rel).exists(), rel)
            # A generated page is fixed through its source, never by hand.
            self.assertEqual("(generated: fix its source, not this file)" in entry, lint_docs.generated(rel), entry)
        # Derived from compat.json, so never among the copies to edit.
        self.assertNotIn("src/awesome_jev_mcp/server.py", listed)
        self.assertIn("--propose-version-rewrite", text)


class CompatibilityDocTest(unittest.TestCase):
    def test_the_page_states_the_reading_date_not_an_age(self):
        data = json.loads((ROOT / "compat.json").read_text())
        data["as_of"] = "2031-02-03"
        text = build_compat.build(data)
        self.assertIn("checked by a person, against every platform's page,\n> on <!--n:as_of-->2031-02-03<!--/n-->", text)
        self.assertEqual(text.count("<!--n:as_of-->"), 1)
        self.assertNotRegex(text, r"(?i)\bdays? ago\b|\btoday\b")


class CompatAgeTest(unittest.TestCase):
    def test_the_age_is_reported_and_stale_past_the_limit(self):
        today = dt.date(2026, 11, 20)
        days, lines = verify_compat.age_lines("2026-09-22", today)
        self.assertEqual(days, 59)
        self.assertIn("a person last read every platform page 59 day(s) ago", lines[0])
        self.assertIn(f"more than {verify_compat.STALE_DAYS} days", lines[1])
        days, lines = verify_compat.age_lines("2026-11-01", today)
        self.assertEqual((days, len(lines)), (19, 1))
        # The limit itself is still fresh; a day past it is not.
        limit = today - dt.timedelta(days=verify_compat.STALE_DAYS)
        self.assertEqual(len(verify_compat.age_lines(limit.isoformat(), today)[1]), 1)
        self.assertEqual(len(verify_compat.age_lines((limit - dt.timedelta(days=1)).isoformat(), today)[1]), 2)
        self.assertEqual(verify_compat.age_lines("soon", today)[0], None)

    def test_a_newer_version_on_a_page_is_its_own_verdict(self):
        newest = verify_compat.newest_recorded(TODAY)
        self.assertEqual(newest, (1, 13))
        self.assertEqual(verify_compat.newer_versions("jev-1.12 jev-1.13.0 jev-1.14.0 jev-2.0", newest), ["jev-1.14.0", "jev-2.0"])
        platform = {"id": "native", "url": "https://d.example", "model": "jev-latest · jev-1.13.0"}
        for page, verdict in (("jev-latest jev-1.13.0", "ok"),
                              ("jev-latest jev-1.13.0 jev-1.14.0", "newer-version"),
                              ("jev-latest jev-1.14.0", "string-gone")):
            with self.subTest(page=page), mock.patch.object(verify_compat, "fetch", return_value=(page, "")):
                self.assertEqual(verify_compat.check(platform, newest)[0], verdict)

    def run_main(self, page: str, as_of: str):
        compat = {"as_of": as_of, "platforms": [{"id": "native", "url": "https://d.example", "model": "jev-1.13.0"}]}
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "compat.json").write_text(json.dumps(compat))
            outputs = root / "outputs"
            out = io.StringIO()
            with mock.patch.object(verify_compat, "ROOT", root), \
                 mock.patch.object(verify_compat, "fetch", return_value=(page, "")), \
                 mock.patch.object(verify_compat, "_today", return_value=dt.date(2026, 11, 20)), \
                 mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(outputs)}), \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = verify_compat.main()
            return code, out.getvalue(), outputs.read_text()

    def test_main_writes_the_age_to_the_outputs_only(self):
        code, out, outputs = self.run_main("jev-1.13.0", "2026-09-22")
        self.assertEqual(code, 0, "an old reading asks for a person but is not a failed string")
        self.assertEqual(outputs, "stale=true\nage=59\n")
        code, out, outputs = self.run_main("jev-1.13.0 jev-1.14.0", "2026-11-19")
        self.assertEqual((code, outputs), (1, "stale=false\nage=1\n"))
        self.assertIn("python3 scripts/lint_docs.py --simulate-model jev-1.14.0", out)


if __name__ == "__main__":
    unittest.main()
