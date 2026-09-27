"""The public pitch is rounded, and its drift is reported rather than failed (I07).

The GitHub repository description is the one published sentence CI cannot
rewrite: editing it needs admin rights no workflow token has. It used to quote
the exact entry count, so every merged row turned `main` red until someone ran
`gh repo edit` by hand. It now states the count floored to the hundred, shared
with the site's og:description, and a separate push-only workflow files an
issue carrying the exact command instead of failing lint. No network here.
"""

from __future__ import annotations

import contextlib
import io
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats
import build_docs
import check_description


class PublicCountTest(unittest.TestCase):
    def test_floors_to_the_hundred_with_a_plus(self):
        for entries, shown in ((1207, "1,200+"), (1200, "1,200+"), (1199, "1,100+"), (805, "800+"), (100, "100+")):
            with self.subTest(entries=entries):
                self.assertEqual(_stats.public_count(entries), shown)

    def test_a_small_catalogue_is_stated_exactly(self):
        # Flooring 42 to "0+" would be true and useless.
        self.assertEqual(_stats.public_count(42), "42")

    def test_next_change_is_the_next_hundred(self):
        self.assertEqual(_stats.next_public_change(1207), 1300)
        self.assertEqual(_stats.next_public_change(1299), 1300)
        self.assertEqual(_stats.next_public_change(1300), 1400)
        self.assertEqual(_stats.next_public_change(42), 43)

    def test_pitch_changes_only_across_a_hundred(self):
        self.assertEqual(_stats.pitch_public({"entries": 1201}), _stats.pitch_public({"entries": 1299}))
        self.assertNotEqual(_stats.pitch_public({"entries": 1299}), _stats.pitch_public({"entries": 1300}))
        pitch = _stats.pitch_public({"entries": 1207})
        self.assertTrue(pitch.startswith("1,200+ public resources for Jev"), pitch)
        self.assertNotIn("1207", pitch)
        self.assertNotIn("verified examples", pitch)

    def test_site_meta_description_is_the_same_rounded_sentence(self):
        meta = build_docs.meta_block({"entries": 1207})
        pitch = _stats.pitch_public({"entries": 1207}).replace("'", "&#x27;")
        self.assertIn(f'<meta name="description" content="{pitch}" />', meta)
        self.assertIn(f'<meta property="og:description" content="{pitch}" />', meta)


class EditCommandTest(unittest.TestCase):
    def test_command_is_paste_ready(self):
        pitch = _stats.pitch_public({"entries": 1207})
        command = check_description.edit_command(pitch)
        self.assertTrue(command.startswith(f'gh repo edit {check_description.SELF} --description "'))
        self.assertIn("TypeSafe AI's", command)
        # Round-trips through a real shell to exactly the pitch.
        out = subprocess.run(
            ["bash", "-c", command.replace(f"gh repo edit {check_description.SELF} --description ", "printf %s ", 1)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertEqual(out, pitch)

    def test_shell_specials_are_escaped(self):
        command = check_description.edit_command('a "b" $HOME `x` \\')
        out = subprocess.run(
            ["bash", "-c", command.replace(f"gh repo edit {check_description.SELF} --description ", "printf %s ", 1)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertEqual(out, 'a "b" $HOME `x` \\')


class CheckDescriptionTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        self.output = self.dir / "output"
        self.summary = self.dir / "summary"
        self.report = self.dir / "report.md"
        self.expected = _stats.pitch_public({"entries": 1207})

    def run_check(self, published, argv=(), has_token=True):
        env = {"GITHUB_OUTPUT": str(self.output), "GITHUB_STEP_SUMMARY": str(self.summary)}
        out = io.StringIO()
        with patch.dict(os.environ, env), patch.object(
            check_description._stats, "compute", return_value={"entries": 1207}
        ), patch.object(check_description, "token", return_value="t" if has_token else ""), patch.object(
            check_description, "api_get", return_value=published
        ), patch.object(check_description, "report_social_preview"), contextlib.redirect_stdout(out):
            code = check_description.main(list(argv))
        return code, out.getvalue()

    def status(self):
        return self.output.read_text() if self.output.exists() else ""

    def test_match_passes_and_reports_match(self):
        code, out = self.run_check({"description": self.expected}, ["--report", str(self.report)])
        self.assertEqual(code, 0)
        self.assertIn("status=match", self.status())
        self.assertFalse(self.report.exists())
        self.assertIn("1,200+", out)

    def test_adding_a_row_within_the_hundred_is_not_drift(self):
        code, _ = self.run_check({"description": _stats.pitch_public({"entries": 1250})})
        self.assertEqual(code, 0)

    def test_drift_for_a_person_exits_non_zero_with_the_command(self):
        code, out = self.run_check({"description": "1207 public resources for Jev"})
        self.assertEqual(code, 1)
        self.assertIn(check_description.edit_command(self.expected), out)
        self.assertIn("status=drift", self.status())

    def test_drift_in_ci_warns_writes_the_issue_and_stays_green(self):
        code, out = self.run_check({"description": "1207 public resources for Jev"}, ["--report", str(self.report)])
        self.assertEqual(code, 0)
        self.assertIn("::warning", out)
        self.assertIn("status=drift", self.status())
        body = self.report.read_text()
        self.assertIn(check_description.edit_command(self.expected), body)
        self.assertIn("1207 public resources for Jev", body)
        self.assertIn(self.expected, body)
        self.assertIn(check_description.edit_command(self.expected), self.summary.read_text())

    def test_stale_report_from_an_earlier_run_is_removed(self):
        self.report.write_text("old")
        self.run_check({"description": self.expected}, ["--report", str(self.report)])
        self.assertFalse(self.report.exists())

    def test_no_token_or_no_answer_is_skipped_never_drift(self):
        code, out = self.run_check(None, ["--report", str(self.report)], has_token=False)
        self.assertEqual(code, 0)
        self.assertIn("skipped", out)
        self.assertIn(self.expected, out)
        self.assertIn("status=skipped", self.status())
        self.output.unlink()
        code, _ = self.run_check(None, ["--report", str(self.report)])
        self.assertEqual(code, 0)
        self.assertIn("status=skipped", self.status())
        self.assertFalse(self.report.exists())


class WorkflowWiringTest(unittest.TestCase):
    """Lint stays read-only and never checks what it cannot fix."""

    def test_lint_no_longer_checks_the_live_description(self):
        lint = (ROOT / ".github/workflows/lint.yml").read_text()
        self.assertNotIn("check_description", lint)
        self.assertNotIn("issues: write", lint)
        self.assertIn("permissions:\n  contents: read\n", lint)

    def test_description_workflow_is_push_only_and_may_file_issues(self):
        text = (ROOT / ".github/workflows/description.yml").read_text()
        self.assertIn("python3 scripts/check_description.py --report", text)
        self.assertIn("permissions:\n  contents: read\n  issues: write\n", text)
        self.assertIn("  push:\n    branches: [main]\n", text)
        self.assertIn("  workflow_dispatch:\n", text)
        self.assertNotIn("pull_request", text)
        self.assertIn("--label description", text)
        # No event payload reaches a shell.
        self.assertNotIn("github.event", text.split("\non:")[1])

    def test_counts_previews_the_rounded_description(self):
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "counts.py")], capture_output=True, text=True, check=True
        ).stdout
        entries = len(__import__("json").loads((ROOT / "catalog.json").read_text()))
        self.assertIn(_stats.pitch_public({"entries": entries}), out)
        self.assertIn(f"{_stats.next_public_change(entries):,}", out)


if __name__ == "__main__":
    unittest.main()
