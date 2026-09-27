"""Draft rows for discovery candidates (I05, phase C): `--drafts DIR`.

A draft is a catalog row with what the script knows filled in, and a `_draft`
field lint refuses, so the only way into the catalogue is through a person
who completes it. These tests pin both halves: what is filled in (and that a
completed draft passes lint), and that the marker alone keeps an untouched or
half-done draft out. No network: inspect() is replaced wherever the CLI would
read GitHub.
"""

from __future__ import annotations

import contextlib
import copy
import datetime as dt
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import discover_candidates as dc  # noqa: E402
import discover_drafts as dd  # noqa: E402
import lint  # noqa: E402

SCHEMA = json.loads(lint.SCHEMA.read_text(encoding="utf-8"))
SLUG = re.compile(SCHEMA["properties"]["slug"]["pattern"])
TODAY = dt.date(2026, 9, 28)


def found(slug: str = "acme/jev-tool", **extra) -> dict:
    """What inspect() returns for a repository calling Jev."""
    owner, name = slug.split("/")
    return {
        "slug": slug.lower(),
        "url": f"https://github.com/{owner}/{name}",
        "stars": 12,
        "license": "MIT",
        "language": "Python",
        "archived": False,
        "created": "2026-09-01",
        "pushed": "2026-09-20",
        "description": "A tool that routes things",
        "verdict": "calls-jev",
        "suggested_kind": "project",
        "suggested_patterns": ["tool-selection"],
        "evidence_path": "src/jev_client.py",
        "matched": ["api.typesafe.ai", "jev-latest"],
        "evidence_is_test": False,
        **extra,
    }


def lint_row(entry: dict) -> lint.Findings:
    schema = lint.validate(entry, SCHEMA, "catalog.json[0]")
    rules = lint.check_entry_invariants(entry, "catalog.json[0]", retired=False, today=TODAY)
    return lint.Findings(schema.errors + rules.errors, schema.warnings + rules.warnings)


def completed(draft: dict) -> dict:
    """What a person does: read the code, write the summaries, date the reading,
    name the source if the draft could not, and delete the marker."""
    row = copy.deepcopy(draft)
    del row[dd.DRAFT_FIELD]
    row["summary"] = "Routes each request to a tool with a choice question."
    row["summary_zh"] = "用 choice 问题为每个请求选择工具。"
    row["zh_machine"] = True
    row["evidence"]["read_on"] = "2026-09-28"
    row["sources"] = row["sources"] or [dict(dd.SOURCE)]
    return row


class SlugTest(unittest.TestCase):
    def test_the_repository_name_as_a_slug(self):
        self.assertEqual(dd.propose_slug("BennyKok", "omg.dev", set()), "omg-dev")
        self.assertEqual(dd.propose_slug("a", "Jev__Router--X", set()), "jev-router-x")

    def test_a_taken_name_gets_its_owner_then_a_number(self):
        self.assertEqual(dd.propose_slug("kyu1204", "jgrep", {"jgrep"}), "jgrep-kyu1204")
        self.assertEqual(dd.propose_slug("kyu1204", "jgrep", {"jgrep", "jgrep-kyu1204"}), "jgrep-kyu1204-2")
        self.assertEqual(
            dd.propose_slug("kyu1204", "jgrep", {"jgrep", "jgrep-kyu1204", "jgrep-kyu1204-2"}), "jgrep-kyu1204-3"
        )

    def test_every_proposal_is_a_slug_the_schema_accepts(self):
        taken = {"x", "jev", "jev-o"}
        for owner, name in [("o", "."), ("o", "-"), ("o", "j"), ("O", "Jev"), ("o-o", "日本語"),
                            ("o", "a" * 120), ("o", "---a---"), ("0", "0")]:
            with self.subTest(name=name):
                slug = dd.propose_slug(owner, name, taken)
                self.assertRegex(slug, SLUG)
                self.assertTrue(2 <= len(slug) <= dd.SLUG_MAX, slug)
                self.assertNotIn(slug, taken)

    def test_a_long_numbered_slug_stays_within_the_limit(self):
        name = "b" * 90
        first = dd.propose_slug("o", name, set())
        slug = dd.propose_slug("o", name, {first, dd.kebab(f"{name}-o")[:80]})
        self.assertLessEqual(len(slug), dd.SLUG_MAX)
        self.assertTrue(slug.endswith("-2"), slug)


class DraftRowTest(unittest.TestCase):
    def draft(self, sourced: bool = True, **extra) -> dict:
        return dd.draft_row(found(**extra), slug="jev-tool", today=TODAY, sourced=sourced)

    def test_the_marker_comes_first_and_says_it_is_not_a_row(self):
        row = self.draft()
        self.assertEqual(next(iter(row)), dd.DRAFT_FIELD)
        text = " ".join(row[dd.DRAFT_FIELD])
        self.assertIn("not a catalog row", text)
        self.assertIn("lint.py refuses any row that still has this field", text)
        self.assertIn("2026-09-28", text)
        self.assertIn("https://github.com/acme/jev-tool/blob/HEAD/src/jev_client.py", text)
        self.assertIn("keyword guesses", text, "a guess is labelled as one")
        self.assertIn("delete this field", text)

    def test_what_the_script_knows_is_filled_in(self):
        row = self.draft()
        self.assertEqual(row["slug"], "jev-tool")
        self.assertEqual(row["title"], "jev-tool")
        self.assertEqual(row["url"], "https://github.com/acme/jev-tool")
        self.assertEqual((row["kind"], row["patterns"]), ("project", ["tool-selection"]))
        self.assertEqual(row["languages"], ["python"])
        self.assertEqual(row["author"], {"name": "acme", "url": "https://github.com/acme"})
        self.assertEqual((row["has_code"], row["stars"], row["repo_license"]), (True, 12, "MIT"))
        self.assertEqual(row["evidence"], {"path": "src/jev_client.py", "matched": ["api.typesafe.ai", "jev-latest"]})
        self.assertEqual(row["first_seen"], "2026-09-28")
        self.assertEqual(row["sources"], [dd.SOURCE])
        self.assertEqual(row["license"], "CC0-1.0")
        self.assertNotIn("flags", row)

    def test_what_only_a_person_can_say_is_left_empty(self):
        row = self.draft()
        self.assertEqual((row["summary"], row["summary_zh"]), ("", ""))
        for field in ("question_types", "platforms", "zh_machine", "notes", "checked", "link_status"):
            self.assertNotIn(field, row)
        self.assertNotIn("read_on", row["evidence"], "the day a person read it is theirs to write")

    def test_github_facts_bring_their_flags(self):
        row = self.draft(license="unknown", archived=True)
        self.assertEqual(row["flags"], ["archived", "no-license"])
        self.assertEqual(self.draft(license="NOASSERTION").get("flags"), None,
                         "a licence GitHub cannot name is still a licence file")

    def test_languages_only_from_an_extension_the_catalogue_knows(self):
        self.assertEqual(self.draft(evidence_path="lib/jev.TSX")["languages"], ["typescript"])
        self.assertNotIn("languages", self.draft(evidence_path="bin/jev"))
        self.assertNotIn("languages", self.draft(evidence_path="queries/jev.sql"))

    def test_a_missing_language_is_named_as_a_thing_to_add(self):
        # lint only warns about has_code without languages, so the draft says it.
        text = " ".join(self.draft(evidence_path="bin/jev")[dd.DRAFT_FIELD])
        self.assertIn("languages is left out", text)
        self.assertNotIn("check all three", text)
        text = " ".join(self.draft()[dd.DRAFT_FIELD])
        self.assertIn("check all three", text)
        self.assertNotIn("languages is left out", text)

    def test_a_test_file_is_called_out(self):
        text = " ".join(self.draft(evidence_is_test=True)[dd.DRAFT_FIELD])
        self.assertIn("looks like a test", text)
        self.assertNotIn("looks like a test", " ".join(self.draft()[dd.DRAFT_FIELD]))

    def test_without_a_harvest_sources_is_left_to_the_person(self):
        row = self.draft(sourced=False)
        self.assertEqual(row["sources"], [])
        self.assertIn(json.dumps(dd.SOURCE), " ".join(row[dd.DRAFT_FIELD]))

    def test_the_source_is_spelled_as_the_catalogue_spells_it(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        self.assertIn(dd.SOURCE, [s for e in catalog for s in e["sources"]])

    def test_the_call_site_link_is_the_one_the_issue_prints(self):
        path = "src/we`ird @here/(x) [id].ts"
        self.assertEqual(dd.call_site_url(found(evidence_path=path)),
                         dc.blob_url("https://github.com/acme/jev-tool", path))


class LintRefusesDraftsTest(unittest.TestCase):
    """The marker is the one thing that keeps a draft out; nothing else is relied on."""

    def test_an_untouched_draft_is_refused_with_the_reason(self):
        errors, _ = lint_row(dd.draft_row(found(), slug="jev-tool", today=TODAY, sourced=True))
        self.assertTrue(any("is a discovery draft, not a row" in e for e in errors), errors)

    def test_a_draft_completed_but_for_the_marker_is_still_refused(self):
        row = completed(dd.draft_row(found(), slug="jev-tool", today=TODAY, sourced=True))
        row = {dd.DRAFT_FIELD: ["left in"], **row}
        errors, _ = lint_row(row)
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("unknown field '_draft'", errors[0])
        self.assertIn("jev-tool: is a discovery draft, not a row", errors[1])

    def test_a_completed_draft_passes(self):
        for sourced in (True, False):
            for extra in ({}, {"license": "unknown", "archived": True}, {"evidence_path": "src/x.go"}):
                with self.subTest(sourced=sourced, extra=extra):
                    row = completed(dd.draft_row(found(**extra), slug="jev-tool", today=TODAY, sourced=sourced))
                    self.assertEqual(lint_row(row), lint.Findings(), row)

    def test_the_marker_is_the_one_lint_knows(self):
        self.assertIs(dd.DRAFT_FIELD, lint.DRAFT_FIELD)
        self.assertNotIn(lint.DRAFT_FIELD, SCHEMA["properties"], "the schema must keep refusing it too")

    def test_lint_fails_a_catalogue_holding_a_draft(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        draft = dd.draft_row(found("acme/zz-demo-draft"), slug="zz-demo-draft", today=TODAY, sourced=True)
        catalog = sorted(catalog + [completed(draft) | {dd.DRAFT_FIELD: ["left in"]}], key=lambda e: e["slug"])
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "catalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            err = io.StringIO()
            with mock.patch.object(lint, "CATALOG", path), contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(err):
                self.assertEqual(lint.main(), 1)
        self.assertIn("zz-demo-draft: is a discovery draft, not a row", err.getvalue())


class WriteDraftsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name) / "drafts"

    def write(self, results, taken=frozenset()):
        return dd.write_drafts(results, self.dir, sourced=True, today=TODAY, taken=set(taken))

    def test_one_file_per_candidate_that_calls_jev(self):
        written, kept = self.write([found("b/two"), found("a/one"), found("c/quiet", verdict="no-signal")])
        self.assertEqual([p.name for p in written], ["one.json", "two.json"])
        self.assertEqual(kept, [])
        text = written[0].read_text(encoding="utf-8")
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(text, json.dumps(json.loads(text), indent=2, ensure_ascii=False) + "\n")

    def test_never_over_a_draft_someone_started(self):
        (written,), _ = self.write([found("a/one")])
        written.write_text(written.read_text().replace('"summary": ""', '"summary": "mine"'))
        again, kept = self.write([found("A/One")])
        self.assertEqual((again, kept), ([], [written]))
        self.assertIn('"summary": "mine"', written.read_text())

    def test_another_repository_with_the_same_name_gets_its_own_slug(self):
        self.write([found("a/tool")])
        written, _ = self.write([found("b/tool")])
        self.assertEqual([p.name for p in written], ["tool-b.json"])

    def test_catalogue_slugs_are_not_reused(self):
        written, _ = self.write([found("x/tool")], taken={"tool"})
        self.assertEqual(written[0].name, "tool-x.json")
        real = dd.catalogue_slugs()
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        retired = json.loads((ROOT / "retired.json").read_text(encoding="utf-8"))
        self.assertEqual(real, {e["slug"] for e in catalog + retired})

    def test_drafts_are_ignored_by_git(self):
        done = subprocess.run(["git", "check-ignore", "-q", "drafts/some-row.json"], cwd=ROOT)
        self.assertEqual(done.returncode, 0, ".gitignore must keep /drafts/ out of commits")


class CommandTest(unittest.TestCase):
    """`--drafts DIR` on the two ways discover_candidates.py runs."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.drafts = self.tmp / "drafts"

    def only(self, repo: str, *extra: str, result: dict | None = None):
        out, err = io.StringIO(), io.StringIO()

        def fake_inspect(slug):
            return dict(result or found(slug), slug=slug)

        with mock.patch.object(dc, "inspect", fake_inspect), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dc.main(["--only", repo, "--drafts", str(self.drafts), *extra])
        return code, out.getvalue(), err.getvalue()

    def files(self) -> list[str]:
        return sorted(p.name for p in self.drafts.glob("*.json")) if self.drafts.exists() else []

    def test_only_writes_the_draft_and_leaves_sources_to_the_person(self):
        code, out, err = self.only("Acme/Zz-Demo-Tool")
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), ["zz-demo-tool.json"])
        row = json.loads((self.drafts / "zz-demo-tool.json").read_text(encoding="utf-8"))
        self.assertEqual(row["sources"], [])
        self.assertIn("wrote draft", err)
        self.assertIn("=== calls-jev (1) ===", out, "the verdict is still printed")

    def test_only_with_json_keeps_stdout_one_document(self):
        code, out, err = self.only("acme/zz-demo-tool", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)[0]["slug"], "acme/zz-demo-tool")
        self.assertIn("wrote draft", err)

    def test_no_draft_without_a_call_site(self):
        code, _, err = self.only("acme/zz-quiet", result=found("acme/zz-quiet", verdict="no-signal"))
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), [])
        self.assertIn("no draft for acme/zz-quiet: its verdict is no-signal", err)

    def test_no_draft_for_what_people_already_decided(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        listed = next(dc.repo_of(e) for e in catalog if dc.repo_of(e)).lower()
        declined = next(iter(dc.read_declined()))
        for repo, why in ((listed, "already in catalog.json"), (declined, "declined in docs/declined.txt")):
            with self.subTest(repo=repo):
                code, _, err = self.only(repo)
                self.assertEqual(code, 0)
                self.assertEqual(self.files(), [])
                self.assertIn(f"no draft for {repo}: it is {why}", err)

    def test_without_the_flag_nothing_is_written(self):
        out = io.StringIO()
        with mock.patch.object(dc, "inspect", lambda slug: found(slug)), \
                mock.patch.object(dd, "write_drafts", side_effect=AssertionError("wrote a draft")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(dc.main(["--only", "acme/zz-demo-tool"]), 0)

    def test_a_harvest_drafts_every_candidate_it_found_with_the_sibling_list_source(self):
        lists = self.tmp / "sibling-lists.txt"
        lists.write_text("https://github.com/lister/awesome-jev\n")
        cited = ["zz-new/hit", "zz-quiet/one"]
        readme = " ".join(f"https://github.com/{slug}" for slug in cited)

        def fake_inspect(slug):
            return found(slug) if slug == "zz-new/hit" else found(slug, verdict="no-signal")

        err = io.StringIO()
        with mock.patch.object(dc, "SIBLINGS", lists), \
                mock.patch.object(dc, "fetch_readme", lambda url: (url, readme)), \
                mock.patch.object(dc, "inspect", fake_inspect), \
                mock.patch.object(dc, "find_new_lists", lambda lists: []), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = dc.main(["--top", "10", "--drafts", str(self.drafts)])
        self.assertEqual(code, 0, err.getvalue())
        self.assertEqual(self.files(), ["hit.json"])
        row = json.loads((self.drafts / "hit.json").read_text(encoding="utf-8"))
        self.assertEqual(row["sources"], [dd.SOURCE])
        self.assertNotIn("zz-quiet/one", err.getvalue(), "a harvest names no draft it did not write")

    def test_the_issue_tells_a_claimer_about_drafts(self):
        for text in (dc.CLAIM_EN, dc.CLAIM_ZH):
            self.assertIn("`--drafts drafts`", text)
            self.assertIn("`_draft`", text)


if __name__ == "__main__":
    unittest.main()
