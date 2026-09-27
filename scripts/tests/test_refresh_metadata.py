"""refresh_metadata.py: GraphQL batches agree with REST, a blocked repository or
a spent budget costs one row rather than the run, and what was read is written.
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
import refresh_metadata as rm  # noqa: E402


def row(slug: str, repo: str, **extra: object) -> dict:
    return {"slug": slug, "url": f"https://github.com/{repo}", **extra}


# The same four repositories as REST and GraphQL describe them.
REST = {
    "a/mit": {"stargazers_count": 10, "license": {"spdx_id": "MIT"}, "archived": False,
              "full_name": "a/mit", "html_url": "https://github.com/a/mit"},
    "a/none": {"stargazers_count": 0, "license": None, "archived": False,
               "full_name": "a/none", "html_url": "https://github.com/a/none"},
    "a/other": {"stargazers_count": 5, "license": {"spdx_id": "NOASSERTION"}, "archived": True,
                "full_name": "a/other", "html_url": "https://github.com/a/other"},
    "a/old": {"stargazers_count": 7, "license": {"spdx_id": "Apache-2.0"}, "archived": False,
              "full_name": "b/new", "html_url": "https://github.com/b/new"},
}
GRAPHQL = {
    "a/mit": {"nameWithOwner": "a/mit", "url": "https://github.com/a/mit", "stargazerCount": 10,
              "isArchived": False, "licenseInfo": {"spdxId": "MIT"}},
    "a/none": {"nameWithOwner": "a/none", "url": "https://github.com/a/none", "stargazerCount": 0,
               "isArchived": False, "licenseInfo": None},
    "a/other": {"nameWithOwner": "a/other", "url": "https://github.com/a/other", "stargazerCount": 5,
                "isArchived": True, "licenseInfo": {"spdxId": "NOASSERTION"}},
    "a/old": {"nameWithOwner": "b/new", "url": "https://github.com/b/new", "stargazerCount": 7,
              "isArchived": False, "licenseInfo": {"spdxId": "Apache-2.0"}},
}


class Quiet(unittest.TestCase):
    def setUp(self):
        _github.reset_usage()
        self.addCleanup(_github.reset_usage)
        self.env = mock.patch.dict(os.environ, {"GITHUB_TOKEN": "t"})
        self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        self.err = io.StringIO()
        redirect = contextlib.redirect_stderr(self.err)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)


class FactsTest(Quiet):
    def test_graphql_and_rest_give_the_same_facts(self):
        for repo in REST:
            with self.subTest(repo=repo):
                entry = row("x", repo)
                self.assertEqual(
                    rm.from_graphql(entry, repo, GRAPHQL[repo]), rm.from_rest(entry, repo, REST[repo])
                )

    def test_licence_mapping(self):
        self.assertEqual(rm.from_rest(row("x", "a/none"), "a/none", REST["a/none"])["repo_license"], "unknown")
        self.assertEqual(rm.from_graphql(row("x", "a/other"), "a/other", GRAPHQL["a/other"])["repo_license"], "NOASSERTION")


class RestTest(Quiet):
    def test_blocked_is_its_own_state(self):
        blocked = {"blocked": True, "status": 403, "message": "Repository access blocked"}
        with mock.patch.object(rm, "api_get", return_value=blocked):
            fresh = rm.fetch(row("x", "a/b"))
        self.assertEqual(fresh["state"], "blocked")
        self.assertEqual(fresh["detail"], "HTTP 403: Repository access blocked")

    def test_a_rate_limit_skips_the_row_instead_of_ending_the_run(self):
        with mock.patch.object(rm, "api_get", side_effect=_github.RateLimited("core", "spent")):
            self.assertEqual(rm.fetch(row("x", "a/b"))["state"], "skipped")

    def test_missing_is_gone(self):
        with mock.patch.object(rm, "api_get", return_value=None):
            self.assertEqual(rm.fetch(row("x", "a/b"))["state"], "gone")


class GraphqlBatchTest(Quiet):
    def answer(self, found: dict[str, dict]):
        """A fake graphql_request answering each alias from `found`."""
        calls = []

        def fake(query, variables):
            calls.append(variables)
            data = {"rateLimit": {"cost": 1, "remaining": 4999}}
            errors = []
            for key, owner in variables.items():
                if not key.startswith("o"):
                    continue
                alias = "r" + key[1:]
                repo = f"{owner}/{variables['n' + key[1:]]}"
                data[alias] = found.get(repo)
                if repo not in found:
                    errors.append({"type": "NOT_FOUND", "path": [alias]})
            return {"data": data, "errors": errors}

        return fake, calls

    def test_batches_of_a_hundred_with_variables_not_interpolation(self):
        rows = [row(f"r{i}", f"o/n{i}") for i in range(250)]
        found = {f"o/n{i}": {**GRAPHQL["a/mit"], "nameWithOwner": f"o/n{i}"} for i in range(250)}
        fake, calls = self.answer(found)
        with mock.patch.object(rm, "graphql_request", side_effect=fake), \
             mock.patch.object(rm, "api_get") as rest:
            results = rm.fetch_all(rows, via="graphql")
        self.assertEqual([len(c) // 2 for c in calls], [100, 100, 50])
        self.assertEqual(rest.call_count, 0)
        self.assertTrue(all(r["state"] == "ok" for r in results))
        query = rm.query_for([("o/n0", 0)])[0]
        self.assertIn("repository(owner: $o0, name: $n0)", query)
        self.assertNotIn('"o"', query)

    def test_an_alias_graphql_could_not_answer_is_read_over_rest(self):
        rows = [row("mit", "a/mit"), row("gone", "a/gone"), row("blocked", "a/blocked")]
        fake, _ = self.answer({"a/mit": GRAPHQL["a/mit"]})
        rest = {"a/gone": None, "a/blocked": {"blocked": True, "status": 451, "message": "DMCA"}}
        with mock.patch.object(rm, "graphql_request", side_effect=fake), \
             mock.patch.object(rm, "api_get", side_effect=lambda path: rest[path.removeprefix("/repos/")]):
            results = rm.fetch_all(rows, via="graphql")
        self.assertEqual([r["state"] for r in results], ["ok", "gone", "blocked"])

    def test_a_failed_or_rate_limited_query_falls_back_to_rest(self):
        rows = [row("mit", "a/mit"), row("other", "a/other")]
        for failure in (None, _github.RateLimited("graphql", "spent")):
            with self.subTest(failure=failure):
                side = [failure] if isinstance(failure, BaseException) else None
                with mock.patch.object(rm, "graphql_request", return_value=failure, side_effect=side), \
                     mock.patch.object(rm, "api_get", side_effect=lambda path: REST[path.removeprefix("/repos/")]):
                    results = rm.fetch_all(rows, via="graphql")
                self.assertEqual(results, [rm.from_rest(rows[0], "a/mit", REST["a/mit"]),
                                           rm.from_rest(rows[1], "a/other", REST["a/other"])])

    def test_rest_only_when_asked(self):
        with mock.patch.object(rm, "graphql_request") as gql, \
             mock.patch.object(rm, "api_get", side_effect=lambda path: REST[path.removeprefix("/repos/")]):
            rm.fetch_all([row("mit", "a/mit")], via="rest")
        gql.assert_not_called()

    def test_compare_reports_any_field_that_differs(self):
        rows = [row("mit", "a/mit"), row("other", "a/other")]
        fake, _ = self.answer({"a/mit": GRAPHQL["a/mit"], "a/other": {**GRAPHQL["a/other"], "stargazerCount": 6}})
        with mock.patch.object(rm, "graphql_request", side_effect=fake), \
             mock.patch.object(rm, "api_get", side_effect=lambda path: REST[path.removeprefix("/repos/")]):
            differences = rm.compare(rows)
        self.assertEqual(differences, ["other (a/other): stars rest=5 graphql=6"])


class MainTest(Quiet):
    """The whole script against a temporary catalogue."""

    def run_main(self, catalog: list[dict], answers: dict, *argv: str) -> tuple[int, str, list[dict], str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "catalog.json"
            path.write_text(json.dumps(catalog, indent=2) + "\n")
            digest = pathlib.Path(tmp) / "digest.md"

            def api(path_: str):
                value = answers[path_.removeprefix("/repos/")]
                if isinstance(value, BaseException):
                    raise value
                return value

            out = io.StringIO()
            with mock.patch.object(rm, "CATALOG", path), mock.patch.object(rm, "api_get", side_effect=api), \
                 mock.patch.object(sys, "argv", ["refresh_metadata.py", "--via", "rest", "--digest", str(digest), *argv]), \
                 contextlib.redirect_stdout(out):
                code = rm.main()
            return code, out.getvalue(), json.loads(path.read_text()), digest.read_text()

    def test_a_spent_budget_still_writes_what_was_read(self):
        catalog = [
            row("a-mit", "a/mit", stars=1, repo_license="MIT"),
            row("b-late", "a/late", stars=3, repo_license="MIT"),
            row("c-blocked", "a/blocked", stars=4, repo_license="MIT"),
        ]
        answers = {
            "a/mit": REST["a/mit"],
            "a/late": _github.RateLimited("core", "0 of 1000 left"),
            "a/blocked": {"blocked": True, "status": 403, "message": "Repository access blocked"},
        }
        code, out, written, digest = self.run_main(catalog, answers, "--write")
        self.assertEqual(code, 0)
        self.assertEqual(written[0]["stars"], 10, "the row that was read is written")
        self.assertEqual(written[1]["stars"], 3, "the skipped row keeps its facts")
        self.assertEqual(written[2]["stars"], 4)
        self.assertIn("checked 2 of 3 row(s): 1 skipped (GitHub API budget), 1 blocked, 0 did not resolve", out)
        self.assertIn("Re-read 2 of 3 repositories", digest.splitlines()[0])
        self.assertIn("**Worth a look before merging:**", digest)
        self.assertIn("`c-blocked` (a/blocked): GitHub refuses to serve it (HTTP 403: Repository access blocked)", digest)
        self.assertIn("**1 repositories were not re-read**", digest)
        self.assertNotIn("Nothing but star counts moved", digest)

    def test_writes_the_counts_to_the_job_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = pathlib.Path(tmp) / "summary.md"
            with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}):
                self.run_main([row("a-mit", "a/mit", stars=10, repo_license="MIT")], {"a/mit": REST["a/mit"]})
            text = summary.read_text()
        self.assertIn("## Repository facts", text)
        self.assertIn("checked 1 of 1 row(s): 0 skipped (GitHub API budget), 0 blocked, 0 did not resolve", text)
        self.assertIn("GitHub", text)

    def test_a_quiet_week_digest_is_unchanged(self):
        code, out, _, digest = self.run_main(
            [row("a-mit", "a/mit", stars=9, repo_license="MIT")], {"a/mit": REST["a/mit"]}
        )
        self.assertEqual(digest.splitlines()[0], "Re-read 1 repositories: 1 rows changed, 1 of them stars only.")
        self.assertIn("Nothing but star counts moved.", digest)


if __name__ == "__main__":
    unittest.main()
