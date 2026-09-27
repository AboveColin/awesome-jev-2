"""discover.yml's issue step, run as GitHub runs it (`bash -e`, no pipefail)
with a stub `gh` on PATH that records every call. No network (I05)."""

from __future__ import annotations

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

from test_weekly_jobs import run_block, step_lines  # noqa: E402

# Plays gh: logs each call, one per line; `issue list` prints $STUB_EXISTING;
# `issue create` fails when it is asked for a label named in $STUB_MISSING.
GH_STUB = """#!/bin/bash
printf '%s\\n' "$*" >> "$STUB_LOG"
if [ "$1 $2" = "issue list" ]; then
  echo "$STUB_EXISTING"
  exit 0
fi
if [ "$1 $2" = "issue create" ] && [ -n "$STUB_MISSING" ]; then
  for arg in "$@"; do
    if [ "$arg" = "$STUB_MISSING" ]; then
      echo "could not add label: '$arg' not found" >&2
      exit 1
    fi
  done
fi
exit 0
"""


class IssueStepTest(unittest.TestCase):
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
        text = (WORKFLOWS / "discover.yml").read_text()
        self.script = run_block(step_lines(text, self.NAME)).replace("/tmp/", f"{self.dir}/")

    def run_step(self, body: str, existing: str = "", missing: str = "") -> list[str]:
        self.body.write_text(body)
        self.log.write_text("")
        env = {
            **os.environ,
            "PATH": f"{self.dir / 'bin'}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(self.log),
            "STUB_EXISTING": existing,
            "STUB_MISSING": missing,
        }
        done = subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-c", self.script],
            cwd=self.dir, env=env, capture_output=True, text=True,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        return [line for line in self.log.read_text().splitlines() if not line.startswith("label create")]

    def creates(self, calls: list[str]) -> list[str]:
        return [call for call in calls if call.startswith("issue create")]

    def test_nothing_new_posts_nothing(self):
        # Earlier candidates alone never make a heading (test_discover_report).
        self.assertEqual(self.run_step("No new candidate with a call site this week.\n\n<details>\n"), [])

    def test_a_new_week_comments_on_the_open_issue(self):
        calls = self.run_step("### 2 new candidates with a call site\n", existing="14")
        self.assertEqual(calls[-1], f"issue comment 14 --body-file {self.body}")
        self.assertEqual(self.creates(calls), [])

    def test_a_new_issue_asks_for_help(self):
        calls = self.run_step("### 1 new candidate with a call site\n")
        self.assertEqual(
            self.creates(calls),
            [f"issue create --title Discovery: candidates to read --label discovery --label help wanted --body-file {self.body}"],
        )

    def test_without_help_wanted_it_keeps_the_label_next_week_looks_for(self):
        calls = self.run_step("### 1 new candidate with a call site\n", missing="help wanted")
        self.assertEqual(len(self.creates(calls)), 2)
        self.assertEqual(
            self.creates(calls)[-1],
            f"issue create --title Discovery: candidates to read --label discovery --body-file {self.body}",
        )

    def test_without_any_label_it_still_files_the_issue(self):
        calls = self.run_step("### 1 new candidate with a call site\n", missing="discovery")
        self.assertEqual(self.creates(calls)[-1], f"issue create --title Discovery: candidates to read --body-file {self.body}")


if __name__ == "__main__":
    unittest.main()
