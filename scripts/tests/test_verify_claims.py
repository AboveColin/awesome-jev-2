"""verify_claims.py: a cited file is read at HEAD on the raw host, and only a pass
is taken from there; a rate limit leaves a claim unchecked, never failed.
No network: the _github calls are replaced."""

from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import _github  # noqa: E402
import verify_claims as vc  # noqa: E402

ROW = {
    "slug": "demo",
    "url": "https://github.com/a/b",
    "evidence": {"path": "src/x.py", "matched": ["system_one"], "read_on": "2026-09-01"},
}


class Files:
    """A fake raw host: {(branch, path): body}; a missing key is a 404."""

    def __init__(self, files: dict, *, branch: str | None = "main"):
        self.files = files
        self.branch = branch
        self.reads: list[str] = []
        self.branch_lookups = 0

    def raw_get(self, repo, branch, path, **_):
        self.reads.append(branch)
        value = self.files.get((branch, path))
        if isinstance(value, BaseException):
            raise value
        return value

    def default_branch(self, repo):
        self.branch_lookups += 1
        return self.branch

    def patch(self, test: unittest.TestCase) -> None:
        for name in ("raw_get", "default_branch"):
            patcher = mock.patch.object(vc, name, getattr(self, name))
            patcher.start()
            test.addCleanup(patcher.stop)


class CheckTest(unittest.TestCase):
    def test_a_pass_at_head_costs_no_api_call(self):
        files = Files({("HEAD", "src/x.py"): "client.system_one()"})
        files.patch(self)
        result = vc.check(ROW)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["detail"], "a/b@HEAD:src/x.py")
        self.assertEqual(files.branch_lookups, 0)

    def test_a_miss_at_head_is_read_again_at_the_named_default_branch(self):
        files = Files({("main", "src/x.py"): "client.system_one()"})
        files.patch(self)
        self.assertEqual(vc.check(ROW)["status"], "ok")
        self.assertEqual(files.reads, ["HEAD", "main"])

    def test_failures_are_reported_at_the_named_branch_only(self):
        cases = [
            ({}, "main", "path-gone", "a/b@main:src/x.py not found"),
            ({("HEAD", "src/x.py"): "nothing", ("main", "src/x.py"): "nothing"}, "main", "claim-gone",
             "a/b@main:src/x.py no longer contains ['system_one']"),
            ({}, None, "repo-gone", "a/b did not resolve"),
        ]
        for files, branch, status, detail in cases:
            with self.subTest(status=status):
                fake = Files(files, branch=branch)
                with mock.patch.object(vc, "raw_get", fake.raw_get), \
                     mock.patch.object(vc, "default_branch", fake.default_branch):
                    result = vc.check(ROW)
                self.assertEqual(result["status"], status)
                self.assertTrue(result["detail"].startswith(detail), result["detail"])
                self.assertEqual(fake.branch_lookups, 1)

    def test_a_rate_limit_leaves_the_claim_unchecked(self):
        Files({("HEAD", "src/x.py"): _github.RateLimited("raw", "HTTP 429 again after the wait")}).patch(self)
        result = vc.check(ROW)
        self.assertEqual(result["status"], "skipped")
        self.assertIn("HTTP 429", result["detail"])


class MainTest(unittest.TestCase):
    def run_main(self, rows: list[dict], files: Files) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = pathlib.Path(tmp) / "catalog.json"
            catalog.write_text(json.dumps(rows))
            summary = pathlib.Path(tmp) / "summary.md"
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(vc, "CATALOG", catalog), \
                 mock.patch.object(sys, "argv", ["verify_claims.py"]), \
                 mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}), \
                 mock.patch.object(vc, "raw_get", files.raw_get), \
                 mock.patch.object(vc, "default_branch", files.default_branch), \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = vc.main()
            return code, out.getvalue(), summary.read_text()

    def rows(self) -> list[dict]:
        return [dict(ROW, slug=f"row-{i}", url=f"https://github.com/a/r{i}") for i in range(3)]

    def test_skipped_claims_are_counted_apart_and_do_not_fail_the_run(self):
        limited = _github.RateLimited("raw", "HTTP 429 again after the wait")
        answers = iter(["system_one", limited, limited])

        def raw_get(repo, branch, path, **_):
            answer = next(answers)
            if isinstance(answer, BaseException):
                raise answer
            return answer

        files = Files({})
        files.raw_get = raw_get
        code, out, summary = self.run_main(self.rows(), files)
        self.assertEqual(code, 0)
        self.assertIn("1/3 claims still hold; 2 not checked (GitHub rate limit)", out)
        self.assertIn("checked 1 of 3 claim(s): 0 failed, 2 skipped (GitHub rate limit)", summary)

    def test_a_failure_still_fails(self):
        code, out, summary = self.run_main(self.rows(), Files({}))
        self.assertEqual(code, 1)
        self.assertIn("0/3 claims still hold", out)
        self.assertIn("checked 3 of 3 claim(s): 3 failed, 0 skipped", summary)



class DiscoverTest(unittest.TestCase):
    """--discover serves every row lint now requires evidence of (I17), not only primitive claims."""

    CODE = {"slug": "code", "url": "https://github.com/a/code", "kind": "project", "has_code": True}

    def test_which_rows_need_a_proposal(self):
        cases = (
            (self.CODE, True),
            (dict(self.CODE, has_code=False, question_types=["noul"]), True),
            (dict(self.CODE, has_code=False), False),
            (dict(self.CODE, evidence_none="docs-page"), False),
            (dict(self.CODE, evidence=ROW["evidence"]), False),
            (dict(self.CODE, url="https://example.com/code"), False),
        )
        for row, needs in cases:
            with self.subTest(row=row):
                self.assertEqual(vc.needs_discovery(row), needs)

    def run_discover(self, rows: list[dict], only: str) -> tuple[str, str, list[str]]:
        asked: list[str] = []

        def discover(entry):
            asked.append(entry["slug"])
            proposal = {"slug": entry["slug"], "status": "proposed", "path": "srv.py", "matched": ["/v1/systemone"]}
            if entry.get("kind") == "alternative":
                proposal["kind"] = "wire-shape"
            return proposal

        with tempfile.TemporaryDirectory() as tmp:
            catalog = pathlib.Path(tmp) / "catalog.json"
            catalog.write_text(json.dumps(rows))
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(vc, "CATALOG", catalog), \
                 mock.patch.object(sys, "argv", ["verify_claims.py", "--discover", "--only", only]), \
                 mock.patch.object(vc, "discover", discover), \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(vc.main(), 0)
            return out.getvalue(), err.getvalue(), asked

    def test_a_row_with_code_and_no_primitive_claim_gets_a_proposal(self):
        out, _, asked = self.run_discover([self.CODE], "code")
        self.assertEqual(asked, ["code"])
        self.assertIn("path: srv.py", out)
        self.assertNotIn("kind:", out)

    def test_an_alternative_is_told_its_evidence_is_wire_shape(self):
        out, _, _ = self.run_discover([dict(self.CODE, kind="alternative")], "code")
        self.assertIn("kind: wire-shape", out)

    def test_a_row_that_needs_nothing_says_why_nothing_ran(self):
        _, err, asked = self.run_discover([dict(self.CODE, evidence_none="docs-page")], "code")
        self.assertEqual(asked, [])
        self.assertIn("code: not a row that needs one", err)

    def test_the_real_discover_labels_an_alternative(self):
        tree = {"tree": [{"type": "blob", "path": "jev_server.py"}]}
        with mock.patch.object(vc, "default_branch", return_value="main"), \
             mock.patch.object(vc, "api_get", return_value=tree), \
             mock.patch.object(vc, "raw_get", return_value="@app.post('/v1/systemone')"):
            self.assertEqual(vc.discover(dict(self.CODE, kind="alternative"))["kind"], "wire-shape")
            self.assertNotIn("kind", vc.discover(self.CODE))


if __name__ == "__main__":
    unittest.main()
