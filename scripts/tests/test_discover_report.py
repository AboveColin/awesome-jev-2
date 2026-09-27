"""The weekly discovery issue as a task list (I05, phase A).

Issue #14 held a 54-row table, no way to say "I am reading this one", and a
sentence counting the candidates from earlier weeks without naming any. Each
candidate is now a task-list box a person can claim, with the command that
re-reads that one repository, and the earlier candidates are listed by name.
No network: inspect() is replaced wherever the CLI would read GitHub.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import discover_candidates as dc  # noqa: E402


def hit(slug: str, cited: int = 3, stars: int = 5, **extra) -> dict:
    owner, name = slug.split("/")
    return {
        "slug": slug,
        "url": f"https://github.com/{owner}/{name}",
        "stars": stars,
        "cited_by": cited,
        "verdict": "calls-jev",
        "evidence_path": "src/jev_client.py",
        "matched": ["api.typesafe.ai"],
        "evidence_is_test": False,
        "suggested_kind": "sdk",
        "suggested_patterns": ["classification", "tool-selection"],
        "description": "",
        **extra,
    }


def report(new_hits=(), waiting=(), new_lists=(), results=None) -> str:
    results = list(new_hits) if results is None else results
    return dc.report_markdown(results, list(new_hits), list(waiting), list(new_lists), 52, 52)


class TaskListTest(unittest.TestCase):
    def test_each_new_candidate_is_a_box_with_its_command(self):
        body = report([hit("acme/jev-tool", cited=7, stars=12)])
        lines = body.splitlines()
        box = next(i for i, line in enumerate(lines) if line.startswith("- [ ] "))
        self.assertEqual(
            lines[box],
            "- [ ] [acme/jev-tool](https://github.com/acme/jev-tool) · cited by 7 · ★12"
            " · call site [`src/jev_client.py`](https://github.com/acme/jev-tool/blob/HEAD/src/jev_client.py)"
            " · suggested sdk / classification, tool-selection",
        )
        self.assertEqual(lines[box + 1], "  `python3 scripts/discover_candidates.py --only acme/jev-tool`")
        self.assertNotIn("| --- |", body, "the table is gone")

    def test_boxes_are_ordered_by_citations_then_stars_then_name(self):
        body = report([hit("b/two", cited=3, stars=1), hit("a/one", cited=3, stars=1), hit("c/top", cited=9, stars=0),
                       hit("d/starred", cited=3, stars=50)])
        order = re.findall(r"^- \[ \] \[([^\]]+)\]", body, re.M)
        self.assertEqual(order, ["c/top", "d/starred", "a/one", "b/two"])

    def test_a_test_file_call_site_is_flagged(self):
        body = report([hit("acme/x", evidence_path="tests/test_jev.py", evidence_is_test=True)])
        self.assertIn("/blob/HEAD/tests/test_jev.py) ⚠ test file · suggested", body)

    def test_a_strangers_path_cannot_break_out_of_its_code_span_or_link(self):
        path = "src/we`ird @here/(x) [id].ts"
        body = report([hit("acme/x", evidence_path=path)])
        line = next(line for line in body.splitlines() if line.startswith("- [ ] "))
        span = re.search(r"call site \[`([^`]*)`\]\((\S+)\)", line)
        self.assertIsNotNone(span, line)
        self.assertEqual(span.group(1), "src/we'ird @here/(x) [id].ts")
        self.assertEqual(span.group(2), "https://github.com/acme/x/blob/HEAD/src/we%60ird%20%40here/%28x%29%20%5Bid%5D.ts")

    def test_more_than_the_cap_says_where_the_rest_go(self):
        hits = [hit(f"o/r{i:03d}") for i in range(dc.NEW_SHOWN + 2)]
        body = report(hits)
        self.assertEqual(len(re.findall(r"^- \[ \] ", body, re.M)), dc.NEW_SHOWN)
        self.assertIn(f"### {dc.NEW_SHOWN + 2} new candidates with a call site", body)
        self.assertIn(f"Showing {dc.NEW_SHOWN} of {dc.NEW_SHOWN + 2}", body)

    def test_no_new_candidate_says_so(self):
        self.assertIn("No new candidate with a call site this week.", report())


class ClaimHeaderTest(unittest.TestCase):
    def test_says_how_to_claim_and_how_to_decline_in_both_languages(self):
        body = report([hit("acme/x")])
        self.assertEqual(body.count("comment `claim owner/name`"), 1)
        self.assertIn(f"https://github.com/{dc.SELF}/blob/main/CONTRIBUTING.md#adding-an-entry", body)
        self.assertIn(f"https://github.com/{dc.SELF}/blob/main/docs/declined.txt", body)
        zh = next(line for line in body.splitlines() if "认领" in line)
        self.assertIn("`claim owner/name`", zh)
        self.assertTrue(zh.endswith(" <sub>(机翻)</sub>"), "model-written Chinese is marked")
        self.assertLess(body.index("claim owner/name"), body.index("- [ ] "))

    def test_no_header_without_anything_to_claim(self):
        body = report(new_lists=[{"slug": "x/awesome-jev", "url": "https://github.com/x/awesome-jev",
                                  "stars": 0, "description": ""}])
        self.assertNotIn("claim owner/name", body)


class WaitingTest(unittest.TestCase):
    WAITING = [("zeta/late", {"on": "2026-09-24", "verdict": "calls-jev"}),
               ("alpha/early", {"on": "2026-09-17", "verdict": "calls-jev"})]

    def test_earlier_candidates_are_listed_by_name_with_their_command(self):
        body = report([hit("acme/x")], waiting=self.WAITING)
        self.assertIn("<summary>2 candidates from earlier weeks are still neither catalogued nor declined</summary>", body)
        lines = body.splitlines()
        self.assertIn(
            "- [ ] [alpha/early](https://github.com/alpha/early) · read 2026-09-17"
            " · `python3 scripts/discover_candidates.py --only alpha/early`",
            lines,
        )
        self.assertLess(body.index("alpha/early"), body.index("zeta/late"), "oldest first")
        details = body[body.index("<details>"):body.index("</details>")]
        self.assertIn("\n\n- [ ] [alpha/early]", details, "a blank line lets the list render inside <details>")
        self.assertNotIn("still neither catalogued nor declined. Add each", body, "no longer a bare count")

    def test_waiting_alone_does_not_make_the_workflow_post(self):
        # discover.yml posts only when the body has a `### ` heading.
        body = report(waiting=self.WAITING)
        self.assertIsNone(re.search(r"^### ", body, re.M))
        self.assertIn("alpha/early", body)
        self.assertIn("comment `claim owner/name`", body, "earlier candidates can be claimed too")

    def test_a_long_backlog_is_capped(self):
        waiting = [(f"o/w{i:03d}", {"on": "2026-09-24", "verdict": "calls-jev"}) for i in range(dc.WAITING_SHOWN + 5)]
        body = report(waiting=waiting)
        self.assertEqual(len(re.findall(r"^- \[ \] \[o/w", body, re.M)), dc.WAITING_SHOWN)
        self.assertIn("…and 5 more", body)


class OnlyCommandTest(unittest.TestCase):
    """The command printed under every box: re-reads one repository now."""

    def run_main(self, *argv: str, result: dict | None = None):
        out, err = io.StringIO(), io.StringIO()
        seen = []

        def fake_inspect(slug):
            seen.append(slug)
            read = dict(result or hit(slug), slug=slug)
            read.pop("cited_by")  # inspect() knows nothing of citations
            return read

        with mock.patch.object(dc, "inspect", fake_inspect), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dc.main(list(argv))
        return code, out.getvalue(), err.getvalue(), seen

    def test_reads_that_one_repository_and_prints_its_call_site(self):
        code, out, _, seen = self.run_main("--only", "Acme/Jev-Tool.git")
        self.assertEqual(code, 0)
        self.assertEqual(seen, ["acme/jev-tool"])
        self.assertIn("=== calls-jev (1) ===", out)
        self.assertIn("src/jev_client.py  -> ['api.typesafe.ai']", out)
        self.assertIn("https://github.com/acme/jev-tool/blob/HEAD/src/jev_client.py", out)
        self.assertNotIn(" lists ", out, "no citation count outside a harvest")

    def test_accepts_the_repository_url(self):
        _, _, _, seen = self.run_main("--only", "https://github.com/acme/jev-tool")
        self.assertEqual(seen, ["acme/jev-tool"])

    def test_json(self):
        code, out, _, _ = self.run_main("--only", "acme/x", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)[0]["slug"], "acme/x")

    def test_rejects_what_is_not_a_repository(self):
        for bad in ("acme", "acme/x/y", "../etc/passwd", "a b/c"):
            with self.subTest(bad=bad):
                code, _, err, seen = self.run_main("--only", bad)
                self.assertEqual(code, 2)
                self.assertIn("owner/name", err)
                self.assertEqual(seen, [])

    def test_says_when_the_repository_is_already_catalogued_or_declined(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        repo = next(dc.repo_of(e) for e in catalog if dc.repo_of(e))
        _, out, _, _ = self.run_main("--only", repo.lower())
        self.assertIn("already in catalog.json", out)
        declined = next(iter(dc.read_declined()))
        _, out, _, _ = self.run_main("--only", declined)
        self.assertIn("declined in docs/declined.txt", out)

    def test_every_printed_command_parses(self):
        body = report([hit("acme/jev-tool")], waiting=WaitingTest.WAITING)
        commands = re.findall(r"`python3 scripts/discover_candidates.py (--only \S+)`", body)
        self.assertEqual(len(commands), 3)
        for command in commands:
            with self.subTest(command=command):
                code, _, _, seen = self.run_main(*command.split())
                self.assertEqual(code, 0)
                self.assertEqual(seen, [command.split()[1]])

    def test_never_touches_a_verdict_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            seen = pathlib.Path(tmp) / "seen.json"
            code, _, _, _ = self.run_main("--only", "acme/x", "--seen", str(seen))
            self.assertEqual(code, 0)
            self.assertFalse(seen.exists(), "a person's --only run proposes nothing to anyone")


class SlugTest(unittest.TestCase):
    def test_slug_is_lower_case_without_dot_git(self):
        # The old f-string needed Python 3.12 (CONTRIBUTING says 3.11+), and its
        # raw r'\\.git$' asked for a literal backslash, so ".git" stayed on.
        self.assertEqual(dc.slug_of("Acme", "Jev-Tool.git"), "acme/jev-tool")
        self.assertEqual(dc.slug_of("acme", "x.github.io"), "acme/x.github.io")


if __name__ == "__main__":
    unittest.main()
