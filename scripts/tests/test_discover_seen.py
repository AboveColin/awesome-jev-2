"""Discovery verdicts kept in git, .discover/seen.json (I05, phase B).

The verdicts lived only in the Actions cache, which GitHub evicts after seven
days without access, on a weekly schedule whose runs start hours late. These
pin the file's shape (a header saying they are a script's verdicts, one
repository per line, same verdicts same bytes), the merge (newest verdict per
repository, independent of order), what an artifact can and cannot put into
git, and discover_candidates.py reading and writing it. No network.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import itertools
import json
import pathlib
import random
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import discover_candidates as dc  # noqa: E402
import discover_seen as ds  # noqa: E402

TODAY = dt.date(2026, 9, 28)


def v(on: str, verdict: str = "no-signal") -> dict:
    return {"on": on, "verdict": verdict}


class ParseTest(unittest.TestCase):
    def test_reads_the_file_shape_and_the_old_cache_shape(self):
        entries = {"acme/x": v("2026-09-24", "calls-jev"), "b/y": v("2026-09-17")}
        for shape in ({"about": ["…"], "verdicts": entries}, entries):
            with self.subTest(shape=list(shape)):
                self.assertEqual(ds.parse(shape, today=TODAY), (entries, []))

    def test_what_is_not_a_verdict_file_yields_nothing(self):
        for data in ([], "x", None, {"about": ["…"]}, {"verdicts": []}, {"about": 1, "acme/x": v("2026-09-24")}):
            with self.subTest(data=data):
                verdicts, dropped = ds.parse(data, today=TODAY)
                self.assertEqual(verdicts, {})
                self.assertEqual(len(dropped), 1)
                self.assertIn("not a verdict file", dropped[0])

    def test_each_bad_entry_is_left_out_with_a_reason_and_the_rest_kept(self):
        bad = {
            "Acme/X": (v("2026-09-24"), "lower-case"),
            "acme/Jev": (v("2026-09-24"), "lower-case"),
            "acme": (v("2026-09-24"), "owner/name"),
            "../../etc/x": (v("2026-09-24"), "owner/name"),
            "a/b\n$(touch pwned)": (v("2026-09-24"), "owner/name"),
            "a/b c": (v("2026-09-24"), "owner/name"),
            "a/verdict": (v("2026-09-24", "looks-fine"), "not one of"),
            "a/date": (v("2026-9-4"), "YYYY-MM-DD"),
            "a/compact": (v("20260924"), "YYYY-MM-DD"),
            "a/nodate": ({"verdict": "no-signal"}, "YYYY-MM-DD"),
            "a/future": (v("2026-10-01"), "after tomorrow"),
            "a/list": (["no-signal"], "not an object"),
        }
        data = {"verdicts": {**{slug: entry for slug, (entry, _) in bad.items()}, "ok/one": v("2026-09-29")}}
        verdicts, dropped = ds.parse(data, today=TODAY)
        self.assertEqual(verdicts, {"ok/one": v("2026-09-29")}, "tomorrow is allowed: runners are on UTC")
        self.assertEqual(len(dropped), len(bad))
        for (slug, (_, why)), line in zip(bad.items(), dropped):
            with self.subTest(slug=slug):
                self.assertIn(why, line)

    def test_only_the_two_fields_are_kept(self):
        verdicts, _ = ds.parse({"acme/x": {**v("2026-09-24"), "note": "hello @everyone"}}, today=TODAY)
        self.assertEqual(verdicts, {"acme/x": v("2026-09-24")})


class MergeTest(unittest.TestCase):
    def test_the_newest_verdict_wins(self):
        old, new = {"a/x": v("2026-07-01", "calls-jev")}, {"a/x": v("2026-09-24", "no-signal")}
        self.assertEqual(ds.merge(old, new), new)
        self.assertEqual(ds.merge(new, old), new)

    def test_on_the_same_day_a_proposal_is_not_forgotten(self):
        a, b = {"a/x": v("2026-09-24", "calls-jev")}, {"a/x": v("2026-09-24", "mentions-only")}
        self.assertEqual(ds.merge(a, b), a)
        self.assertEqual(ds.merge(b, a), a)

    def test_keeps_every_repository_either_side_has(self):
        self.assertEqual(ds.merge({"a/x": v("2026-09-24")}, {}, {"b/y": v("2026-09-17")}),
                         {"a/x": v("2026-09-24"), "b/y": v("2026-09-17")})

    def test_order_never_matters(self):
        rng = random.Random(5)
        days = ["2026-09-17", "2026-09-24", "2026-07-30"]
        sources = [
            {f"o/r{rng.randrange(8)}": v(rng.choice(days), rng.choice(ds.VERDICTS)) for _ in range(6)}
            for _ in range(4)
        ]
        results = {json.dumps(ds.merge(*order), sort_keys=True) for order in itertools.permutations(sources)}
        self.assertEqual(len(results), 1)

    def test_merge_does_not_change_its_inputs(self):
        a = {"a/x": v("2026-09-17")}
        ds.merge(a, {"a/x": v("2026-09-24")})
        self.assertEqual(a, {"a/x": v("2026-09-17")})


class RenderTest(unittest.TestCase):
    VERDICTS = {"zeta/z": v("2026-09-24", "calls-jev"), "alpha/a": v("2026-09-17"), "mid/m": v("2026-09-24", "repo-gone")}

    def test_round_trips(self):
        for verdicts in (self.VERDICTS, {}):
            with self.subTest(n=len(verdicts)):
                self.assertEqual(ds.parse(json.loads(ds.render(verdicts)), today=TODAY), (verdicts, []))

    def test_same_verdicts_same_bytes_one_line_each_in_name_order(self):
        shuffled = dict(reversed(list(self.VERDICTS.items())))
        text = ds.render(self.VERDICTS)
        self.assertEqual(text, ds.render(shuffled))
        rows = [line for line in text.splitlines() if line.startswith('    "') and '": {' in line]
        self.assertEqual(rows, [
            '    "alpha/a": {"on": "2026-09-17", "verdict": "no-signal"},',
            '    "mid/m": {"on": "2026-09-24", "verdict": "repo-gone"},',
            '    "zeta/z": {"on": "2026-09-24", "verdict": "calls-jev"}',
        ])
        self.assertTrue(text.endswith("}\n"))

    def test_one_changed_verdict_is_a_one_line_diff(self):
        before = ds.render(self.VERDICTS).splitlines()
        after = ds.render({**self.VERDICTS, "mid/m": v("2026-09-28", "calls-jev")}).splitlines()
        self.assertEqual(sum(1 for a, b in zip(before, after) if a != b), 1)
        self.assertEqual(len(before), len(after))

    def test_the_header_says_these_are_a_scripts_verdicts(self):
        about = json.loads(ds.render({}))["about"]
        self.assertEqual(about[0], "Script verdicts, not human conclusions. Nobody reviewed these entries.")
        text = " ".join(about)
        for verdict in ds.VERDICTS:
            self.assertIn(f"{verdict}:", text)
        self.assertIn(f"{ds.RECHECK_DAYS} days", text)
        self.assertIn("catalog.json", text)
        self.assertIn("docs/declined.txt", text)

    def test_write_replaces_in_one_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "new" / "seen.json"
            ds.write(path, self.VERDICTS)
            self.assertEqual(path.read_text(encoding="utf-8"), ds.render(self.VERDICTS))
            self.assertEqual(sorted(p.name for p in path.parent.iterdir()), ["seen.json"], "no temp file left")


class CommittedFileTest(unittest.TestCase):
    def test_the_committed_file_is_valid_and_canonical(self):
        text = ds.PATH.read_text(encoding="utf-8")
        verdicts, dropped = ds.parse(json.loads(text), today=dt.date.today())
        self.assertEqual(dropped, [], "rewrite it: python3 scripts/discover_seen.py .discover/seen.json")
        self.assertEqual(text, ds.render(verdicts), "rewrite it: python3 scripts/discover_seen.py .discover/seen.json")

    def test_one_definition_of_the_recheck_period_and_the_verdicts(self):
        self.assertIs(dc.RECHECK_DAYS, ds.RECHECK_DAYS)
        self.assertIs(dc.VERDICTS, ds.VERDICTS)


class CliTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        self.target = self.dir / ".discover" / "seen.json"

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ds.main(list(args), today=TODAY)
        return code, out.getvalue(), err.getvalue()

    def source(self, name: str, data: object) -> str:
        path = self.dir / name
        path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
        return str(path)

    def test_merges_an_artifact_into_the_committed_file(self):
        ds.write(self.target, {"a/x": v("2026-09-17"), "b/y": v("2026-09-17", "calls-jev")})
        src = self.source("art.json", {"about": [], "verdicts": {"a/x": v("2026-09-24", "calls-jev"), "c/z": v("2026-09-24")}})
        code, out, err = self.run_cli(str(self.target), src)
        self.assertEqual(code, 0, err)
        self.assertEqual(ds.load(self.target, today=TODAY)[0], {
            "a/x": v("2026-09-24", "calls-jev"), "b/y": v("2026-09-17", "calls-jev"), "c/z": v("2026-09-24"),
        })
        self.assertIn("3 in", out)
        self.assertIn("(2 calls-jev); 1 added and 1 updated from 1 source(s)", out)

    def test_creates_the_file_and_takes_the_old_cache_shape(self):
        src = self.source("cache.json", {"a/x": v("2026-09-24", "calls-jev")})
        code, _, err = self.run_cli(str(self.target), src)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.target.read_text(encoding="utf-8"), ds.render({"a/x": v("2026-09-24", "calls-jev")}))

    def test_a_bad_entry_is_warned_about_and_never_written(self):
        src = self.source("art.json", {"verdicts": {"a/x": v("2026-09-24"), "a/b\n$(touch pwned)": v("2026-09-24")}})
        code, _, err = self.run_cli(str(self.target), src)
        self.assertEqual(code, 0)
        self.assertIn(f"::warning title=Discovery verdicts left out::{src}: 1 entry not shaped like a verdict", err)
        self.assertNotIn("pwned", self.target.read_text(encoding="utf-8"))

    def test_a_source_that_is_not_verdicts_changes_nothing(self):
        ds.write(self.target, {"a/x": v("2026-09-17")})
        before = self.target.read_bytes()
        for data in ("{not json", ["a/x"], {"verdicts": {"Bad/Slug": v("2026-09-24")}}):
            with self.subTest(data=data):
                code, _, err = self.run_cli(str(self.target), self.source("bad.json", data))
                self.assertEqual(code, 1)
                self.assertIn("left as it was", err)
                self.assertEqual(self.target.read_bytes(), before)
        code, _, err = self.run_cli(str(self.target), str(self.dir / "missing.json"))
        self.assertEqual(code, 1)
        self.assertIn("does not exist", err)

    def test_no_source_rewrites_in_canonical_form(self):
        self.target.parent.mkdir()
        self.target.write_text(json.dumps({"verdicts": {"b/y": v("2026-09-17"), "a/x": v("2026-09-24")}}, indent=4))
        code, _, _ = self.run_cli(str(self.target))
        self.assertEqual(code, 0)
        self.assertEqual(self.target.read_text(encoding="utf-8"),
                         ds.render({"a/x": v("2026-09-24"), "b/y": v("2026-09-17")}))

    def test_usage(self):
        for args in ((), ("--help",)):
            with self.subTest(args=args):
                code, _, err = self.run_cli(*args)
                self.assertEqual(code, 2)
                self.assertIn("discover_seen.py", err)


class DiscoverRunTest(unittest.TestCase):
    """discover_candidates.main() over two verdict files, as discover.yml runs
    it: the committed one and the Actions cache copy, which may be newer."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        self.lists = self.dir / "sibling-lists.txt"
        self.lists.write_text("https://github.com/lister/awesome-jev\n")
        self.committed = self.dir / "repo" / ".discover" / "seen.json"
        self.cache = self.dir / ".cache" / "discover-seen.json"
        self.body = self.dir / "body.md"
        self.inspected: list[str] = []
        today = dt.date.today()
        self.today = today.isoformat()
        self.recent = (today - dt.timedelta(days=3)).isoformat()
        self.stale = (today - dt.timedelta(days=ds.RECHECK_DAYS + 1)).isoformat()

    def fake_inspect(self, slug: str) -> dict:
        self.inspected.append(slug)
        verdict = {"new/hit": "calls-jev", "old/proposal": "calls-jev", "old/gone-quiet": "no-signal"}.get(slug, "no-signal")
        owner, name = slug.split("/")
        out = {"slug": slug, "url": f"https://github.com/{owner}/{name}", "stars": 1, "verdict": verdict}
        if verdict == "calls-jev":
            out.update(evidence_path="jev.py", matched=["api.typesafe.ai"], evidence_is_test=False,
                       suggested_kind="project", suggested_patterns=["overview"])
        return out

    def run_discover(self) -> tuple[int, str]:
        # odd/.git is a link a sibling list could carry: its slug is "odd/".
        cited = ["new/hit", "old/proposal", "old/gone-quiet", "fresh/quiet", "waiting/one", "odd/.git"]
        readme = " ".join(f"https://github.com/{slug}" for slug in cited)
        err = io.StringIO()
        with mock.patch.object(dc, "SIBLINGS", self.lists), \
                mock.patch.object(dc, "fetch_readme", lambda url: (url, readme)), \
                mock.patch.object(dc, "inspect", self.fake_inspect), \
                mock.patch.object(dc, "find_new_lists", lambda lists: []), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = dc.main(["--top", "10", "--seen", str(self.committed), "--seen", str(self.cache),
                            "--markdown", str(self.body)])
        return code, err.getvalue()

    def test_reads_both_files_writes_both_the_same_and_lists_the_earlier_ones_by_name(self):
        # Committed on the Wednesday; the cache is the newer Thursday run's.
        ds.write(self.committed, {
            "old/proposal": v(self.stale, "calls-jev"),     # due a re-read, still calls Jev
            "old/gone-quiet": v(self.stale, "calls-jev"),   # due a re-read, no longer does
            "waiting/one": v(self.stale, "mentions-only"),  # older than the cache's verdict
        })
        self.cache.parent.mkdir(parents=True)
        self.cache.write_text(json.dumps({
            "fresh/quiet": v(self.recent, "no-signal"),
            "waiting/one": v(self.recent, "calls-jev"),
            "Bad Slug/x": v(self.recent, "calls-jev"),
        }))
        code, err = self.run_discover()
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(self.inspected), ["new/hit", "odd/", "old/gone-quiet", "old/proposal"],
                         "fresh verdicts from either file are not read again")
        self.assertIn(f"{self.cache}: 1 entry not shaped like a verdict", err, "the bad cache entry is reported")
        self.assertIn("this run's verdicts: 1 entry not shaped like a verdict", err, "odd/ is reported, not written")
        self.assertIn("2 read in the last", err)

        committed = self.committed.read_text(encoding="utf-8")
        self.assertEqual(committed, self.cache.read_text(encoding="utf-8"), "both copies hold the same verdicts")
        verdicts, dropped = ds.parse(json.loads(committed), today=dt.date.today())
        self.assertEqual(dropped, [])
        self.assertEqual(verdicts, {
            "new/hit": v(self.today, "calls-jev"),
            "old/proposal": v(self.today, "calls-jev"),
            "old/gone-quiet": v(self.today, "no-signal"),
            "fresh/quiet": v(self.recent, "no-signal"),
            "waiting/one": v(self.recent, "calls-jev"),
        })

        body = self.body.read_text(encoding="utf-8")
        self.assertIn("### 1 new candidate with a call site", body)
        self.assertIn("- [ ] [new/hit]", body)
        self.assertIn("2 candidates from earlier weeks are still neither catalogued nor declined", body)
        self.assertIn("- [ ] [waiting/one](https://github.com/waiting/one)", body)
        self.assertIn("- [ ] [old/proposal](https://github.com/old/proposal)", body)
        self.assertNotIn("old/gone-quiet", body, "a re-read that found no call site drops out")

    def body_parts(self) -> tuple[str, str]:
        """The issue body split into the new boxes and the earlier candidates."""
        body = self.body.read_text(encoding="utf-8")
        new, _, earlier = body.partition("<details>")
        return new, earlier

    def test_a_quiet_repository_that_now_calls_jev_is_a_new_candidate(self):
        # Read once and found quiet, read again after RECHECK_DAYS and found
        # calling Jev: the case the re-read exists for. It was never proposed,
        # so it gets a box under the heading the workflow posts on (review of I05).
        ds.write(self.committed, {"new/hit": v(self.stale, "no-signal"),
                                  "waiting/one": v(self.recent, "calls-jev")})
        code, err = self.run_discover()
        self.assertEqual(code, 0, err)
        self.assertIn("new/hit", self.inspected)
        new, earlier = self.body_parts()
        self.assertRegex(new, r"(?m)^### \d+ new candidates? with a call site$")
        self.assertIn("- [ ] [new/hit]", new)
        self.assertNotIn("new/hit", earlier)
        self.assertIn("- [ ] [waiting/one]", earlier, "a candidate proposed before is still an earlier one")

    def test_an_earlier_candidate_since_catalogued_or_declined_is_not_listed(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        catalogued = next(repo.lower() for repo in map(dc.repo_of, catalog) if repo)
        declined = next(iter(dc.read_declined()))
        ds.write(self.committed, {slug: v(self.recent, "calls-jev")
                                  for slug in (catalogued, declined, "waiting/one")})
        code, err = self.run_discover()
        self.assertEqual(code, 0, err)
        _, earlier = self.body_parts()
        self.assertIn("1 candidate from earlier weeks is still neither catalogued nor declined", earlier)
        self.assertIn("- [ ] [waiting/one]", earlier)
        self.assertNotIn(catalogued, earlier)
        self.assertNotIn(declined, earlier)

    def test_a_first_run_starts_from_nothing(self):
        code, err = self.run_discover()
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.inspected), 6)
        self.assertTrue(self.committed.exists() and self.cache.exists())
        self.assertNotIn("from earlier weeks", self.body.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
