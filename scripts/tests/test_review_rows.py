"""review_rows.py: which rows a pull request adds or changes, and each check's
verdict on them (I03). No network: the three checks that read GitHub or a link
are given a fake Net, and every test says which answers it gets."""

from __future__ import annotations

import contextlib
import copy
import io
import pathlib
import re
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import review_rows as rr  # noqa: E402
from _github import SELF, RateLimited  # noqa: E402

ROW = {
    "slug": "demo-row",
    "title": "Demo",
    "summary": "Reranks retrieved passages with one Jev noul each",
    "summary_zh": "演示",
    "url": "https://github.com/alice/demo",
    "kind": "project",
    "patterns": ["search-ranking"],
    "question_types": ["noul"],
    "languages": ["python"],
    "has_code": True,
    "stars": 100,
    "repo_license": "MIT",
    "evidence": {"path": "src/demo.py", "matched": ["system_one"], "read_on": "2026-09-20"},
    "sources": [{"catalog": "maintainer submission", "url": "https://github.com/kydlikebtc/awesome-jev"}],
    "license": "CC0-1.0",
}
DROP = object()


def row(**changes: object) -> dict:
    out = copy.deepcopy(ROW)
    for key, value in changes.items():
        if value is DROP:
            out.pop(key, None)
        else:
            out[key] = value
    return out


class FakeNet:
    """Answers as told, and remembers what it was asked."""

    def __init__(self, claim="ok", commits=2, link=(200, ""), **facts):
        self.claim_status = claim
        self.facts_answer = {
            "state": "ok", "stars": 100, "repo_license": "MIT", "archived": False,
            "full_name": "alice/demo", "html_url": "https://github.com/alice/demo", **facts,
        }
        self.commits_answer = commits
        self.link_answer = link
        self.asked: list[str] = []

    def claim(self, entry):
        self.asked.append("claim")
        return {"slug": entry["slug"], "status": self.claim_status, "detail": "x"}

    def facts(self, entry):
        self.asked.append("facts")
        answer = {"slug": entry["slug"], "repo": "alice/demo", **self.facts_answer}
        # `facts_commits=N` plays refresh_metadata.fetch() carrying the count itself.
        if "facts_commits" in answer:
            answer["commits"] = answer.pop("facts_commits")
        return answer

    def commits(self, repo):
        self.asked.append("commits")
        if isinstance(self.commits_answer, BaseException):
            raise self.commits_answer
        return self.commits_answer

    def link(self, url):
        self.asked.append("link")
        return self.link_answer

    def net(self) -> rr.Net:
        return rr.Net(claim=self.claim, facts=self.facts, commits=self.commits, link=self.link)


def levels(findings, check=None):
    return [f.level for f in findings if check is None or f.check == check]


def added(entry: dict) -> rr.Change:
    return rr.Change(entry["slug"], "added", entry, frozenset(entry))


def changed(entry: dict, *fields: str) -> rr.Change:
    return rr.Change(entry["slug"], "changed", entry, frozenset(fields))


class DiffTest(unittest.TestCase):
    def test_moving_rows_changes_nothing(self):
        a, b = row(slug="a"), row(slug="b")
        self.assertEqual(rr.diff_rows([a, b], [b, a]), ([], [], []))

    def test_added_rows_first_then_changed_then_removed(self):
        old = [row(slug="a"), row(slug="b"), row(slug="c")]
        new = [row(slug="z"), row(slug="b"), row(slug="a", summary="new words"), row(slug="d")]
        changes, removed, problems = rr.diff_rows(old, new)
        self.assertEqual([(c.slug, c.kind) for c in changes], [("d", "added"), ("z", "added"), ("a", "changed")])
        self.assertEqual(changes[2].fields, frozenset({"summary"}))
        self.assertEqual(changes[0].fields, frozenset(ROW))
        self.assertEqual(removed, ["c"])
        self.assertEqual(problems, [])

    def test_a_key_added_or_dropped_is_a_changed_field(self):
        changes, _, _ = rr.diff_rows([row(slug="a")], [row(slug="a", stars=DROP, notes="why")])
        self.assertEqual(changes[0].fields, frozenset({"stars", "notes"}))

    def test_rows_that_cannot_be_keyed_are_noted_not_fatal(self):
        changes, _, problems = rr.diff_rows([], [row(slug="a"), "junk", {"title": "x"}, row(slug="a", stars=1)])
        self.assertEqual([c.slug for c in changes], ["a"])
        self.assertEqual(changes[0].row["stars"], 1)
        self.assertEqual(len(problems), 3)
        self.assertTrue(any("twice" in p for p in problems))

    def test_a_catalogue_that_is_not_an_array(self):
        changes, removed, problems = rr.diff_rows([row(slug="a")], {"slug": "a"})
        self.assertEqual((changes, removed), ([], ["a"]))
        self.assertIn("not a JSON array", problems[0])


class CallSiteTest(unittest.TestCase):
    def check(self, entry, status="ok", net=True):
        fake = FakeNet(claim=status)
        return rr.check_call_site(entry, fake.net() if net else None, "offline"), fake

    def test_every_string_present(self):
        (finding,), _ = self.check(row())
        self.assertEqual(finding.level, "ok")
        self.assertIn("`alice/demo:src/demo.py`", finding.text)

    def test_what_the_weekly_job_would_fail_is_an_error(self):
        for status, words in (
            ("claim-gone", "does not contain every"),
            ("path-gone", "a typo, or the file moved upstream"),
            ("repo-gone", "GitHub has no repository"),
            ("no-repo", "needs a GitHub repository"),
        ):
            with self.subTest(status=status):
                (finding,), _ = self.check(row(), status)
                self.assertEqual(finding.level, "error")
                self.assertIn(words, finding.text)

    def test_a_rate_limit_or_offline_is_not_a_pass(self):
        self.assertEqual(levels(self.check(row(), "skipped")[0]), ["skipped"])
        findings, fake = self.check(row(), net=False)
        self.assertEqual(levels(findings), ["skipped"])
        self.assertEqual(fake.asked, [])

    def test_a_claim_without_a_citation_is_an_error_naming_the_command(self):
        (finding,), fake = self.check(row(evidence=DROP))
        self.assertEqual(finding.level, "error")
        self.assertIn("python3 scripts/verify_claims.py --discover --only demo-row", finding.text)
        self.assertEqual(fake.asked, [])

    def test_evidence_none_is_read_as_declared(self):
        (finding,), fake = self.check(row(evidence=DROP, evidence_none="docs-page"))
        self.assertEqual((finding.level, fake.asked), ("info", []))
        self.assertIn("`docs-page`", finding.text)

    def test_a_row_without_claims_has_nothing_to_check(self):
        # Since I17 a row with code on GitHub is a claim too (next test).
        self.assertEqual(self.check(row(evidence=DROP, question_types=DROP, has_code=False))[0], [])
        self.assertEqual(
            self.check(row(evidence=DROP, question_types=DROP, url="https://example.com/demo"))[0], []
        )

    def test_code_on_github_without_a_citation_is_an_error_naming_the_way_out(self):
        (finding,), fake = self.check(row(evidence=DROP, question_types=DROP))
        self.assertEqual((finding.level, fake.asked), ("error", []))
        for words in ("python3 scripts/verify_claims.py --discover --only demo-row", "`evidence_none`", "`has_code: false`"):
            self.assertIn(words, finding.text)
        (finding,), _ = self.check(row(evidence=DROP, question_types=DROP, evidence_none="no-jev-call-site"))
        self.assertEqual(finding.level, "info")

    def test_a_changed_has_code_triggers_the_call_site_check(self):
        self.assertIn("has_code", rr.READS["call-site"])


class RepositoryTest(unittest.TestCase):
    def check(self, entry, *, fields=frozenset(), is_added=True, **answers):
        fake = FakeNet(**answers)
        return rr.check_repository(entry, fields, is_added, fake.net(), "offline"), fake

    def test_agreement_is_one_line_naming_what_was_compared(self):
        (finding,), fake = self.check(row())
        self.assertEqual(finding.level, "ok")
        self.assertIn("licence, archive status, stars, commit count", finding.text)
        self.assertEqual(fake.asked, ["facts", "commits"])

    def test_licence(self):
        (finding,), _ = self.check(row(), repo_license="Apache-2.0")
        self.assertEqual(finding.level, "error")
        self.assertIn("`repo_license` is `MIT`, GitHub says `Apache-2.0`", finding.text)
        (finding,), _ = self.check(row(), repo_license="unknown")
        self.assertIn("no LICENSE file", finding.text)
        (finding,), _ = self.check(row(repo_license=DROP))
        self.assertEqual(finding.level, "warning")

    def test_archived_both_ways(self):
        (finding,), _ = self.check(row(), archived=True)
        self.assertEqual(finding.level, "error")
        self.assertIn("needs the `archived` flag", finding.text)
        (finding,), _ = self.check(row(flags=["archived"]))
        self.assertEqual(finding.level, "error")
        self.assertIn("does not mark", finding.text)
        self.assertEqual(levels(self.check(row(flags=["archived"]), archived=True)[0]), ["ok"])

    def test_stars_drift_is_only_a_warning_past_the_slack(self):
        # max(5, 10% of GitHub's count): 10 at 100, 5 at 20.
        for have, now, level in ((110, 100, "ok"), (89, 100, "warning"), (111, 100, "warning"),
                                 (25, 20, "ok"), (26, 20, "warning"), (1, 0, "ok"), (6, 0, "warning")):
            with self.subTest(have=have, now=now):
                findings, _ = self.check(row(stars=have), stars=now)
                self.assertEqual(levels(findings), [level])
        (finding,), _ = self.check(row(stars=DROP))
        self.assertEqual(finding.level, "warning")

    def test_a_rename_says_where_to(self):
        findings, _ = self.check(row(), full_name="alice/renamed")
        self.assertEqual(levels(findings), ["warning"])
        self.assertIn("`alice/renamed`", findings[0].text)
        # GitHub's capitals are not a rename.
        self.assertEqual(levels(self.check(row(), full_name="Alice/Demo")[0]), ["ok"])

    def test_gone_blocked_and_rate_limited(self):
        self.assertEqual(levels(self.check(row(), state="gone")[0]), ["error"])
        findings, _ = self.check(row(), state="blocked", detail="HTTP 451: @someone | <b>")
        self.assertEqual(levels(findings), ["warning"])
        self.assertNotIn("@someone", findings[0].text)
        self.assertNotIn("<b>", findings[0].text)
        findings, fake = self.check(row(), state="skipped")
        self.assertEqual((levels(findings), fake.asked), (["skipped"], ["facts"]))

    def test_a_count_the_facts_already_carry_is_not_asked_for_again(self):
        # refresh_metadata.fetch() counts commits since I15; the card reuses it.
        findings, fake = self.check(row(), **{"commits": 99, "facts_commits": 1})
        self.assertEqual(levels(findings), ["warning"])
        self.assertEqual(fake.asked, ["facts"])
        (finding,), fake = self.check(row(flags=["single-commit"]), facts_commits=1)
        self.assertEqual((finding.level, fake.asked), ("ok", ["facts"]))
        self.assertIn("commit count", finding.text)
        findings, fake = self.check(row(flags=["single-commit"]), facts_commits=40)
        self.assertEqual((levels(findings), fake.asked), (["info", "ok"], ["facts"]))

    def test_single_commit(self):
        findings, _ = self.check(row(), commits=1)
        self.assertEqual(levels(findings), ["warning"])
        self.assertIn("`single-commit`", findings[0].text)
        self.assertEqual(levels(self.check(row(flags=["single-commit"]), commits=1)[0]), ["ok"])
        self.assertEqual(levels(self.check(row(flags=["single-commit"]), commits=2)[0]), ["info", "ok"])
        # Not counted (an empty repository, a rate limit): the rest can agree,
        # but the commit count is not said to.
        (finding,) = self.check(row(), commits=None)[0]
        self.assertEqual(finding.level, "ok")
        self.assertIn("on licence, archive status, stars.", finding.text)
        findings, _ = self.check(row(), commits=RateLimited("core", "spent"))
        self.assertEqual(levels(findings), ["skipped", "ok"])
        self.assertNotIn("commit count", findings[1].text)

    def test_not_a_github_repository_or_this_one(self):
        for entry in (row(url="https://example.com/x"), row(url=f"https://github.com/{SELF}/tree/main/examples/x")):
            with self.subTest(url=entry["url"]):
                findings, fake = self.check(entry)
                self.assertEqual((findings, fake.asked), ([], []))

    def test_a_changed_url_compares_everything_again(self):
        # A row pointed at another repository: its old facts are not the new one's.
        findings, fake = self.check(row(), fields=frozenset({"url"}), is_added=False, repo_license="GPL-3.0")
        self.assertEqual(levels(findings), ["error"])
        self.assertIn("GitHub says `GPL-3.0`", findings[0].text)
        self.assertEqual(fake.asked, ["facts", "commits"])

    def test_a_changed_row_is_compared_only_on_what_changed(self):
        # The licence disagrees, but the pull request only moved the stars.
        findings, fake = self.check(row(stars=100), fields=frozenset({"stars"}), is_added=False, repo_license="GPL-3.0")
        self.assertEqual(levels(findings), ["ok"])
        self.assertIn("on stars.", findings[0].text)
        self.assertEqual(fake.asked, ["facts"])


class LinkTest(unittest.TestCase):
    def check(self, entry, answer=(200, ""), net=True):
        fake = FakeNet(link=answer)
        return rr.check_link(entry, fake.net() if net else None, "offline"), fake

    def test_answers(self):
        for answer, level in (((200, ""), "ok"), ((204, ""), "ok"), ((403, "Forbidden"), "warning"),
                              ((429, ""), "warning"), ((300, ""), "warning"), ((301, ""), "warning"),
                              ((404, "Not Found"), "error"),
                              ((0, "timed out"), "error"), ((429, "not checked: GitHub core rate limit"), "skipped")):
            with self.subTest(answer=answer):
                self.assertEqual(levels(self.check(row(), answer)[0]), [level])

    def test_only_https_is_requested(self):
        for url in ("http://example.com", "file:///etc/passwd", None):
            with self.subTest(url=url):
                findings, fake = self.check(row(url=url))
                self.assertEqual((levels(findings), fake.asked), (["error"], []))

    def test_offline(self):
        findings, fake = self.check(row(), net=False)
        self.assertEqual((levels(findings), fake.asked), (["skipped"], []))


class SelfSubmissionTest(unittest.TestCase):
    OWN = {"sources": [{"catalog": "author submission", "url": "https://github.com/kydlikebtc/awesome-jev/pull/1"}],
           "flags": ["self-submitted"]}

    def test_the_owner_without_the_disclosure_is_an_error(self):
        (finding,), = [rr.check_self_submission(row(), True, "Alice")]
        self.assertEqual(finding.level, "error")
        self.assertIn("the owner of `alice/demo`", finding.text)
        self.assertIn('"catalog": "author submission"', finding.text)
        self.assertIn("`self-submitted`", finding.text)

    def test_the_owner_with_it(self):
        self.assertEqual(levels(rr.check_self_submission(row(**self.OWN), True, "alice")), ["ok"])

    def test_the_owner_who_named_the_source_but_not_the_flag_is_told_only_the_flag(self):
        # Open pull requests #21 and #23 are shaped like this (review of I03).
        (finding,) = rr.check_self_submission(row(sources=self.OWN["sources"]), True, "alice")
        self.assertEqual(finding.level, "error")
        self.assertIn("the row's sources say `author submission`", finding.text)
        self.assertIn("`flags` lacks `self-submitted`", finding.text)
        self.assertNotIn("add the source", finding.text)

    def test_the_recorded_author_counts_too(self):
        org = "https://github.com/some-org/demo"
        for author in ({"name": "A", "url": "https://github.com/Alice"}, {"name": "A", "handle": "@alice"}):
            with self.subTest(author=author):
                (finding,) = rr.check_self_submission(row(url=org, author=author), True, "alice")
                self.assertEqual(finding.level, "error")
                self.assertIn("the row's `author.", finding.text)

    def test_someone_else(self):
        self.assertEqual(levels(rr.check_self_submission(row(), True, "bob")), ["ok"])
        self.assertEqual(levels(rr.check_self_submission(row(**self.OWN), True, "bob")), ["info"])
        (finding,) = rr.check_self_submission(row(url="https://arxiv.org/abs/1", repo=DROP), True, "bob")
        self.assertEqual(finding.level, "info")
        self.assertIn("names no GitHub account", finding.text)

    def test_without_an_author(self):
        self.assertEqual(levels(rr.check_self_submission(row(), True, None)), ["skipped"])
        self.assertEqual(rr.check_self_submission(row(), False, None), [])

    def test_a_changed_row(self):
        self.assertEqual(levels(rr.check_self_submission(row(), False, "alice")), ["info"])
        self.assertEqual(rr.check_self_submission(row(**self.OWN), False, "alice"), [])
        self.assertEqual(rr.check_self_submission(row(), False, "bob"), [])

    def test_login_of(self):
        for value, login in (("Alice", "alice"), ("@alice", "alice"), ("https://github.com/Alice/", "alice"),
                             ("dependabot[bot]", "dependabot[bot]"), ("https://example.com/alice", None),
                             ("a b", None), ("-x", None), ("", None), ("x" * 40, None)):
            with self.subTest(value=value):
                self.assertEqual(rr.login_of(value), login)


class FlagNotesTest(unittest.TestCase):
    def test_flags_that_need_a_reason(self):
        for flag in rr.FLAGS_NEEDING_NOTES:
            with self.subTest(flag=flag):
                (finding,) = rr.check_flag_notes(row(flags=[flag]))
                self.assertEqual(finding.level, "error")
                self.assertEqual(levels(rr.check_flag_notes(row(flags=[flag], notes="why"))), ["ok"])
        self.assertEqual(rr.check_flag_notes(row(flags=["archived", "marketing"])), [])


class ClassificationTest(unittest.TestCase):
    def test_a_hint_never_more(self):
        self.assertEqual(levels(rr.check_classification(row())), ["ok"])
        (finding,) = rr.check_classification(row(kind="video", patterns=["overview"]))
        self.assertEqual(finding.level, "info")
        self.assertIn("suggest `project` / search-ranking", finding.text)
        self.assertIn("not a verdict", finding.text)


class ReviewRowTest(unittest.TestCase):
    def test_an_added_row_gets_every_check_in_order(self):
        fake = FakeNet()
        review = rr.review_row(added(row(flags=["ai-generated"], notes="why")), "bob", fake.net(), "")
        self.assertEqual([f.check for f in review.findings], [key for key, _ in rr.CHECKS])
        self.assertEqual(review.worst(), "ok")
        self.assertEqual(review.fields, ())

    def test_a_changed_row_gets_only_the_checks_reading_what_changed(self):
        fake = FakeNet()
        review = rr.review_row(changed(row(), "summary", "summary_zh"), "bob", fake.net(), "")
        self.assertEqual((review.findings, fake.asked), ((), []))
        self.assertEqual(review.fields, ("summary", "summary_zh"))
        review = rr.review_row(changed(row(), "url"), "bob", fake.net(), "")
        self.assertEqual({f.check for f in review.findings}, {"call-site", "repository", "link"})

    def test_changed_flags_are_compared_with_github(self):
        # Adding or dropping `archived` / `single-commit` is a claim about the
        # repository, so a flags-only change still asks GitHub.
        fake = FakeNet(commits=1)
        review = rr.review_row(changed(row(flags=["archived"]), "flags"), "bob", fake.net(), "")
        texts = [f.text for f in review.findings if f.check == "repository"]
        self.assertEqual(review.worst("repository"), "error")
        self.assertTrue(any("does not mark" in t for t in texts), texts)
        self.assertTrue(any("one commit" in t for t in texts), texts)
        self.assertEqual(fake.asked, ["facts", "commits"])

    def test_a_check_that_breaks_is_not_a_pass(self):
        fake = FakeNet()
        fake.claim = lambda entry: {}["boom"]
        with contextlib.redirect_stderr(io.StringIO()) as err:
            review = rr.review_row(added(row()), "bob", fake.net(), "")
        (finding,) = [f for f in review.findings if f.check == "call-site"]
        self.assertEqual(finding.level, "skipped")
        self.assertIn("Could not run", finding.text)
        self.assertIn("KeyError", err.getvalue())
        self.assertIn("link", {f.check for f in review.findings})

    def test_a_rate_limit_inside_a_check(self):
        fake = FakeNet()

        def limited(url):
            raise RateLimited("core", "spent")

        fake.link = limited
        review = rr.review_row(added(row()), "bob", fake.net(), "")
        self.assertEqual(review.worst("link"), "skipped")


class ReviewRowsTest(unittest.TestCase):
    def test_only_the_first_rows_are_read_from_the_network(self):
        fake = FakeNet()
        changes = [added(row(slug=f"r{n}")) for n in range(3)]
        reviews, notes = rr.review_rows(changes, author="bob", net=fake.net(), cap=2)
        self.assertEqual([r.slug for r in reviews], ["r0", "r1", "r2"])
        self.assertEqual(reviews[1].worst("link"), "ok")
        self.assertEqual(reviews[2].worst("link"), "skipped")
        self.assertIn("only the first 2 rows", [f.text for f in reviews[2].findings if f.check == "link"][0])
        self.assertEqual(reviews[2].worst("flag-notes"), None)
        self.assertEqual(len(notes), 1)
        self.assertEqual(fake.asked.count("link"), 2)

    def test_offline(self):
        reviews, notes = rr.review_rows([added(row())], author=None, net=None, offline="--offline")
        self.assertEqual(notes, [])
        for check in rr.NETWORK:
            self.assertEqual(reviews[0].worst(check), "skipped")
        self.assertIn("--offline", reviews[0].findings[0].text)


class NetTest(unittest.TestCase):
    def test_the_real_net_is_the_weekly_jobs_functions(self):
        import check_links
        import refresh_metadata
        import verify_claims

        net = rr.default_net()
        self.assertIs(net.claim, verify_claims.check)
        self.assertIs(net.facts, refresh_metadata.fetch)
        self.assertIs(net.commits, rr.commit_count)
        self.assertIs(net.link, check_links.fetch_status)

    def test_commits_are_counted_to_two(self):
        asked = []
        for answer, count in (([{}], 1), ([{}, {}], 2), ([], 0), (None, None), ({"message": "Git Repository is empty."}, None)):
            with self.subTest(answer=answer), mock.patch.object(rr, "api_get", lambda path: asked.append(path) or answer):
                self.assertEqual(rr.commit_count("alice/demo"), count)
        self.assertEqual(set(asked), {"/repos/alice/demo/commits?per_page=2"})


class InertTextTest(unittest.TestCase):
    def test_outside_strings_cannot_break_out(self):
        hostile = "a`b|c\n::error::x @someone <img>"
        entry = row(evidence={"path": hostile, "matched": ["x"]}, url=f"https://github.com/alice/demo?{hostile}")
        fake = FakeNet(claim="claim-gone", state="blocked", detail=hostile, link=(404, hostile))
        findings = rr.review_row(added(entry), "bob", fake.net(), "").findings
        self.assertTrue(findings)
        for finding in findings:
            with self.subTest(check=finding.check):
                self.assertNotIn("\n", finding.text)
                # Every backtick opens or closes one of the finding's own code
                # spans; outside them no @-mention, table bar or tag survives.
                self.assertEqual(finding.text.count("`") % 2, 0, finding.text)
                prose = re.sub(r"`[^`]*`", "", finding.text)
                self.assertNotIn("@someone", prose)
                self.assertNotIn("<img>", prose)
                self.assertNotRegex(prose, r"(?<!\\)\|")


if __name__ == "__main__":
    unittest.main()
