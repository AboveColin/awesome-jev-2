"""discover.yml and the discovery half of metadata.yml (I05): the issue step,
and the hand-over of verdicts from discover (no write permission) to metadata
(which commits them). Shell steps run as GitHub runs them (`bash -e`, no
pipefail) with a stub `gh` on PATH that records every call. No network."""

from __future__ import annotations

import datetime as dt
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

import discover_seen  # noqa: E402
from test_weekly_jobs import run_block, step_lines  # noqa: E402

# Plays gh: logs each call, one per line; `issue list` prints $STUB_EXISTING,
# `issue view` prints $STUB_CURRENT (the open issue's description), `issue
# create` prints the new issue's URL, or fails when it is asked for a label
# named in $STUB_MISSING.
GH_STUB = """#!/bin/bash
printf '%s\\n' "$*" >> "$STUB_LOG"
if [ "$1 $2" = "issue list" ]; then
  echo "$STUB_EXISTING"
  exit 0
fi
if [ "$1 $2" = "issue view" ]; then
  printf '%s\\n' "$STUB_CURRENT"
  exit 0
fi
if [ "$1 $2" = "issue create" ]; then
  if [ -n "$STUB_MISSING" ]; then
    for arg in "$@"; do
      if [ "$arg" = "$STUB_MISSING" ]; then
        echo "could not add label: '$arg' not found" >&2
        exit 1
      fi
    done
  fi
  echo "https://github.com/kydlikebtc/awesome-jev/issues/99"
fi
exit 0
"""

QUEUE = "<!-- Written by scripts/queue_sync.py -->\n\nThe discovery queue.\n\n- [ ] [a/b](https://github.com/a/b)\n"
NEW = "### 2 new candidates with a call site\n"
NOTHING_NEW = "No new candidate with a call site this week.\n\n<details>\n"


class IssueStepTest(unittest.TestCase):
    """The description is the queue (queue_sync.py), rewritten when it changed;
    a week with something new also gets its report as a comment."""

    NAME = "Open or update the discovery issue"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        stub = self.dir / "bin" / "gh"
        stub.parent.mkdir()
        stub.write_text(GH_STUB)
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        self.log = self.dir / "gh.log"
        self.body = self.dir / "body.md"
        self.queue = self.dir / "queue.md"
        text = (WORKFLOWS / "discover.yml").read_text()
        self.script = run_block(step_lines(text, self.NAME)).replace("/tmp/", f"{self.dir}/")

    def run_step(self, body: str, existing: str = "", missing: str = "", current: str = "") -> list[str]:
        self.body.write_text(body)
        self.queue.write_text(QUEUE)
        self.log.write_text("")
        env = {
            **os.environ,
            "PATH": f"{self.dir / 'bin'}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(self.log),
            "STUB_EXISTING": existing,
            "STUB_MISSING": missing,
            "STUB_CURRENT": current,
        }
        done = subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-c", self.script],
            cwd=self.dir, env=env, capture_output=True, text=True,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        return [line for line in self.log.read_text().splitlines() if not line.startswith("label create")]

    def of(self, calls: list[str], verb: str) -> list[str]:
        return [call for call in calls if call.startswith(f"issue {verb}")]

    def test_nothing_new_and_no_issue_posts_nothing(self):
        # Earlier candidates alone never make a heading (test_discover_report).
        calls = self.run_step(NOTHING_NEW)
        self.assertEqual(calls, ["issue list --state open --label discovery --json number --jq .[0].number"])

    def test_the_queue_is_rewritten_every_week_it_changed(self):
        calls = self.run_step(NOTHING_NEW, existing="14", current="an older queue")
        self.assertIn("issue view 14 --json body --jq .body", calls)
        self.assertEqual(self.of(calls, "edit"), [f"issue edit 14 --body-file {self.queue}"])
        self.assertEqual(self.of(calls, "comment"), [], "nothing new, so no comment")
        self.assertEqual(self.of(calls, "create"), [])

    def test_an_unchanged_queue_is_left_alone(self):
        for current in (QUEUE, QUEUE.replace("\n", "\r\n")):
            with self.subTest(crlf="\r" in current):
                calls = self.run_step(NOTHING_NEW, existing="14", current=current.rstrip("\n"))
                self.assertEqual(self.of(calls, "edit"), [])

    def test_a_new_week_comments_on_the_open_issue(self):
        calls = self.run_step(NEW, existing="14", current=QUEUE.rstrip("\n"))
        self.assertEqual(calls[-1], f"issue comment 14 --body-file {self.body}")
        self.assertEqual(self.of(calls, "create") + self.of(calls, "edit"), [])

    def test_a_new_issue_holds_the_queue_and_the_report_is_its_first_comment(self):
        calls = self.run_step(NEW)
        self.assertEqual(
            self.of(calls, "create"),
            [f"issue create --title Discovery: candidates to read --label discovery --label help wanted "
             f"--body-file {self.queue}"],
        )
        self.assertEqual(
            calls[-1], f"issue comment https://github.com/kydlikebtc/awesome-jev/issues/99 --body-file {self.body}"
        )

    def test_without_help_wanted_it_keeps_the_label_next_week_looks_for(self):
        calls = self.run_step(NEW, missing="help wanted")
        self.assertEqual(len(self.of(calls, "create")), 2)
        self.assertEqual(
            self.of(calls, "create")[-1],
            f"issue create --title Discovery: candidates to read --label discovery --body-file {self.queue}",
        )
        self.assertTrue(calls[-1].startswith("issue comment https://"), calls[-1])

    def test_without_any_label_it_still_files_the_issue(self):
        calls = self.run_step(NEW, missing="discovery")
        self.assertEqual(self.of(calls, "create")[-1],
                         f"issue create --title Discovery: candidates to read --body-file {self.queue}")
        self.assertTrue(calls[-1].startswith("issue comment https://"), calls[-1])


class QueueStepTest(unittest.TestCase):
    NAME = "Write the discovery queue"

    def test_writes_the_queue_after_the_verdicts_and_before_the_issue(self):
        text = workflow("discover.yml")
        self.assertIn("        run: python3 scripts/queue_sync.py --out /tmp/queue.md", step_lines(text, self.NAME))
        order = [step_index(text, name) for name in (
            "Discover", "Leave the verdicts for the weekly refresh to commit", self.NAME,
            "Open or update the discovery issue",
        )]
        self.assertEqual(order, sorted(order))

    def test_the_queue_script_reads_the_file_discover_writes(self):
        # discover.yml's Discover step writes this run's verdicts here; the
        # queue must be built from them, not from the committed copy alone.
        run = run_block(step_lines(workflow("discover.yml"), "Discover"))
        self.assertIn("--seen .discover/seen.json", run)
        self.assertIn('".discover" / "seen.json"', (ROOT / "scripts" / "queue_sync.py").read_text())


def workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text()


def step_index(text: str, name: str) -> int:
    return text.index(f"      - name: {name}")


class DiscoverVerdictsTest(unittest.TestCase):
    """discover.yml keeps the verdicts in both places and hands them over."""

    def test_reads_and_writes_the_committed_file_and_the_cache(self):
        text = workflow("discover.yml")
        run = run_block(step_lines(text, "Discover"))
        self.assertIn("--seen .discover/seen.json --seen .cache/discover-seen.json", run)
        self.assertIn("          path: .cache/discover-seen.json\n", text, "the cache stays as the fast path")
        self.assertIn("          key: discover-seen-${{ github.run_id }}\n", text)

    def test_leaves_the_verdicts_as_an_artifact_before_touching_the_issue(self):
        text = workflow("discover.yml")
        lines = step_lines(text, "Leave the verdicts for the weekly refresh to commit")
        for line in (
            "        uses: actions/upload-artifact@v7",
            "          name: discover-seen",
            "          path: .discover/seen.json",
            "          include-hidden-files: true",
            "          if-no-files-found: error",
            "          retention-days: 90",
        ):
            self.assertIn(line, lines)
        order = [step_index(text, name) for name in (
            "Discover", "Leave the verdicts for the weekly refresh to commit", "Open or update the discovery issue",
        )]
        self.assertEqual(order, sorted(order))

    def test_still_holds_no_write_permission_to_the_repository(self):
        text = workflow("discover.yml")
        self.assertIn("permissions:\n  contents: read\n  issues: write\n", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("git push", text)


GH_RUN_STUB = """#!/bin/bash
printf '%s\\n' "$*" >> "$STUB_LOG"
if [ "$1 $2" = "run list" ]; then
  echo "$STUB_RUN"
  exit 0
fi
if [ "$1 $2" = "run download" ]; then
  [ -n "$STUB_ARTIFACT" ] || { echo "no valid artifacts found to download" >&2; exit 1; }
  while [ $# -gt 0 ]; do
    if [ "$1" = "--dir" ]; then dir="$2"; fi
    shift
  done
  mkdir -p "$dir"
  cp "$STUB_ARTIFACT" "$dir/seen.json"
  exit 0
fi
exit 1
"""


class MetadataTakesInVerdictsTest(unittest.TestCase):
    NAME = "Take in the latest discovery verdicts"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        self.work = self.dir / "work"
        (self.work / "scripts").mkdir(parents=True)
        (self.work / "scripts" / "discover_seen.py").write_bytes((ROOT / "scripts" / "discover_seen.py").read_bytes())
        self.ds = discover_seen
        self.target = self.work / ".discover" / "seen.json"
        self.ds.write(self.target, {"a/x": {"on": "2026-09-17", "verdict": "no-signal"}})
        stub = self.dir / "bin" / "gh"
        stub.parent.mkdir()
        stub.write_text(GH_RUN_STUB)
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        self.log = self.dir / "gh.log"
        self.lines = step_lines(workflow("metadata.yml"), self.NAME)
        self.script = run_block(self.lines).replace("/tmp/", f"{self.dir}/tmp/")

    def run_step(self, run: str = "42", artifact: object = None) -> subprocess.CompletedProcess:
        self.log.write_text("")
        path = ""
        if artifact is not None:
            source = self.dir / "artifact.json"
            source.write_text(artifact if isinstance(artifact, str) else self.ds.render(artifact))
            path = str(source)
        env = {
            **os.environ,
            "PATH": f"{self.dir / 'bin'}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(self.log),
            "STUB_RUN": run,
            "STUB_ARTIFACT": path,
        }
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-c", self.script],
            cwd=self.work, env=env, capture_output=True, text=True,
        )

    def test_merges_the_newest_successful_run_on_main(self):
        before = self.target.read_text()
        done = self.run_step(artifact={"a/x": {"on": "2026-09-24", "verdict": "calls-jev"},
                                       "b/y": {"on": "2026-09-24", "verdict": "no-signal"}})
        self.assertEqual(done.returncode, 0, done.stderr)
        calls = self.log.read_text().splitlines()
        self.assertEqual(calls[0], "run list --workflow discover.yml --branch main --status success "
                                   "--limit 1 --json databaseId --jq .[0].databaseId // empty")
        self.assertTrue(calls[1].startswith("run download 42 --name discover-seen --dir "), calls[1])
        self.assertNotEqual(self.target.read_text(), before)
        self.assertEqual(self.ds.load(self.target, today=dt.date(2026, 9, 28))[0], {
            "a/x": {"on": "2026-09-24", "verdict": "calls-jev"}, "b/y": {"on": "2026-09-24", "verdict": "no-signal"},
        })
        self.assertIn("2 in .discover/seen.json", done.stdout)

    def test_no_run_yet_changes_nothing(self):
        before = self.target.read_bytes()
        done = self.run_step(run="")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("no successful discovery run on main", done.stdout)
        self.assertEqual(self.target.read_bytes(), before)
        self.assertEqual(len(self.log.read_text().splitlines()), 1, "nothing downloaded")

    def test_an_expired_artifact_is_a_warning(self):
        before = self.target.read_bytes()
        done = self.run_step(artifact=None)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("::warning title=Discovery verdicts not taken in::run 42", done.stdout)
        self.assertEqual(self.target.read_bytes(), before)

    def test_a_broken_artifact_fails_this_step_only_and_changes_nothing(self):
        before = self.target.read_bytes()
        done = self.run_step(artifact='["not", "verdicts"]')
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(self.target.read_bytes(), before)
        self.assertIn("        continue-on-error: true", self.lines, "the refresh goes on without them")

    def test_sits_before_the_commit_which_stages_the_file(self):
        text = workflow("metadata.yml")
        order = [step_index(text, name) for name in (
            "Keep the sweep and refresh logs", self.NAME,
            "Rebuild everything generated from those facts, and commit it here",
        )]
        self.assertEqual(order, sorted(order))
        add = next(line for line in text.splitlines() if "git add" in line)
        self.assertIn(".discover", add.split())


if __name__ == "__main__":
    unittest.main()
