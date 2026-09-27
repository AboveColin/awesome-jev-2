"""Pull requests may leave generated files to a bot that regenerates main (I01).

check_generated.py judges a regenerated tree by event: in a pull request a
generated file must be untouched or exactly as generated; on main drift is
handed to lint.yml's regenerate job; anywhere else drift fails. These tests
build throwaway git repositories — plain ones, the merge-commit shape CI checks
out, a scratch copy of this repository run through the real generators, and a
bare origin the regenerate job's own shell pushes to. No network.
"""

from __future__ import annotations

import contextlib
import io
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check  # noqa: E402
import check_generated  # noqa: E402
import regenerate  # noqa: E402

LINT = ROOT / ".github" / "workflows" / "lint.yml"
# The catalog job runs `check.py --ci`; this is its generated-files step alone.
VERDICT = "python3 scripts/check.py --ci --only generated"
# No global or system git config: a signing key or hook on the machine running
# the tests must not change what a commit does.
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
IDENTITY = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]


def run_git(cwd: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", *IDENTITY, *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


def workflow_step(name: str) -> str:
    """The `run:` block of the named lint.yml step, dedented."""
    lines = LINT.read_text().splitlines()
    start = lines.index(f"      - name: {name}")
    run = next(i for i in range(start, len(lines)) if lines[i] == "        run: |")
    body = []
    for line in lines[run + 1 :]:
        if line.strip() and not line.startswith(" " * 10):
            break
        body.append(line[10:])
    return "\n".join(body)


class GitCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        env = patch.dict(os.environ, GIT_ENV)
        env.start()
        self.addCleanup(env.stop)
        self.summary = self.dir / "summary.md"
        self.output = self.dir / "output.txt"

    def init(self, name: str, files: dict[str, str]) -> pathlib.Path:
        repo = self.dir / name
        repo.mkdir()
        run_git(repo, "init", "-q", "-b", "main")
        for rel, text in files.items():
            self.write(repo, rel, text)
        self.commit(repo, "base")
        return repo

    def write(self, repo: pathlib.Path, rel: str, text: str) -> None:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, repo: pathlib.Path, message: str) -> None:
        run_git(repo, "add", "-A")
        run_git(repo, "commit", "-q", "-m", message)

    def check(self, repo: pathlib.Path, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        env = {"GITHUB_STEP_SUMMARY": str(self.summary), "GITHUB_OUTPUT": str(self.output)}
        with patch.dict(os.environ, env), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check_generated.main(list(argv), cwd=repo)
        return code, out.getvalue() + err.getvalue()

    def summary_text(self) -> str:
        return self.summary.read_text() if self.summary.exists() else ""


class ClassifyTest(unittest.TestCase):
    def test_three_verdicts(self):
        verdict = check_generated.classify({"a", "b"}, {"b", "c"})
        self.assertEqual(verdict.matches, ["a"])
        self.assertEqual(verdict.differs, ["b"])
        self.assertEqual(verdict.stale, ["c"])

    def test_outputs_are_what_regenerate_writes(self):
        self.assertIs(check_generated.OUTPUTS, regenerate.OUTPUTS)
        for path in ("README.md", "README.zh-CN.md", "docs/by-pattern", "docs/assets", "llms.txt"):
            self.assertIn(path, regenerate.OUTPUTS)
        self.assertNotIn("catalog.json", regenerate.OUTPUTS)
        self.assertNotIn("site/index.html", regenerate.OUTPUTS)

    def test_list_prints_only_outputs_present_in_the_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "README.md").write_text("x")
            (root / "docs" / "by-pattern").mkdir(parents=True)
            out = io.StringIO()
            with patch.object(regenerate, "ROOT", root), contextlib.redirect_stdout(out):
                self.assertEqual(regenerate.main(["--list"]), 0)
        self.assertEqual(out.getvalue().split(), ["README.md", "docs/by-pattern"])


BASE = {
    "catalog.json": "rows v1\n",
    "README.md": "generated from v1\n",
    "docs/by-pattern/a.md": "page a from v1\n",
    "CONTRIBUTING.md": "hand-written\n",
}


class PullRequestTest(GitCase):
    """A branch `pr` off `main`, checked out; the test plays the generators."""

    def setUp(self):
        super().setUp()
        self.repo = self.init("repo", BASE)
        run_git(self.repo, "checkout", "-q", "-b", "pr")

    def generate(self, version: str) -> None:
        self.write(self.repo, "README.md", f"generated from {version}\n")
        self.write(self.repo, "docs/by-pattern/a.md", f"page a from {version}\n")

    def test_a_catalog_only_pull_request_passes(self):
        self.write(self.repo, "catalog.json", "rows v2\n")
        self.commit(self.repo, "add a row")
        self.generate("v2")
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 0, out)
        summary = self.summary_text()
        self.assertIn("changes no generated file", summary)
        self.assertIn("regenerated on `main` by the bot after the merge (2)", summary)
        self.assertIn("- `README.md`", summary)

    def test_output_committed_exactly_as_generated_passes(self):
        self.write(self.repo, "catalog.json", "rows v2\n")
        self.generate("v2")
        self.commit(self.repo, "add a row and regenerate")
        self.generate("v2")
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 0, out)
        self.assertIn("exactly what the generators produce", self.summary_text())
        self.assertIn("2 as generated, 0 not", out)

    def test_a_hand_edited_output_fails_and_shows_the_difference(self):
        self.write(self.repo, "README.md", "generated from v1\nmy project, added by hand\n")
        self.commit(self.repo, "edit the README")
        self.generate("v1")
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("::error file=README.md,", out)
        summary = self.summary_text()
        self.assertIn("not what the generators produce", summary)
        self.assertIn("-my project, added by hand", summary)
        self.assertIn(check_generated.FIX, summary)
        # The untouched page is not blamed on the pull request.
        self.assertNotIn("docs/by-pattern/a.md", summary)

    def test_output_generated_from_an_older_catalogue_fails(self):
        self.write(self.repo, "catalog.json", "rows v2\n")
        self.write(self.repo, "README.md", "generated from v1, edited\n")
        self.commit(self.repo, "row plus a stale README")
        self.generate("v2")
        code, _ = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 1)

    def test_deleting_a_page_the_generators_still_write_fails(self):
        (self.repo / "docs/by-pattern/a.md").unlink()
        self.commit(self.repo, "delete a page")
        self.generate("v1")
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("docs/by-pattern/a.md: the generators produce this file, and it is not committed", out)

    def test_a_new_page_exactly_as_generated_passes(self):
        self.write(self.repo, "docs/by-pattern/b.md", "page b\n")
        self.commit(self.repo, "new pattern page")
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 0, out)
        self.assertIn("- `docs/by-pattern/b.md`", self.summary_text())

    def test_commits_that_reached_main_after_the_branch_point_are_not_the_pull_requests(self):
        self.write(self.repo, "catalog.json", "rows v2\n")
        self.commit(self.repo, "add a row")
        run_git(self.repo, "checkout", "-q", "main")
        self.write(self.repo, "README.md", "regenerated on main by the bot\n")
        self.commit(self.repo, "chore: regenerate from catalog.json")
        run_git(self.repo, "checkout", "-q", "pr")
        self.assertEqual(check_generated.touched("main", "pr", self.repo), set())

    def test_files_that_are_not_generated_are_ignored(self):
        self.write(self.repo, "CONTRIBUTING.md", "edited\n")
        self.commit(self.repo, "docs")
        self.write(self.repo, "CONTRIBUTING.md", "edited again, uncommitted\n")
        code, _ = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 0)
        self.assertNotIn("CONTRIBUTING", self.summary_text())

    def test_not_a_merge_commit_is_an_error_not_a_verdict(self):
        code, out = self.check(self.repo, "pr", "--base", "HEAD^1", "--head", "HEAD^2")
        self.assertEqual(code, 2)
        self.assertIn("error: git", out)


class MergeCommitTest(GitCase):
    """The shape actions/checkout gives a pull_request run: a merge commit whose
    first parent is the base branch and second the pull request's head."""

    def merged(self, pr_files: dict[str, str]) -> pathlib.Path:
        repo = self.init("repo", BASE)
        run_git(repo, "checkout", "-q", "-b", "pr")
        for rel, text in pr_files.items():
            self.write(repo, rel, text)
        self.commit(repo, "pull request")
        run_git(repo, "checkout", "-q", "main")
        # main moves on after the branch point, as it does.
        self.write(repo, "CONTRIBUTING.md", "edited on main\n")
        self.commit(repo, "meanwhile on main")
        run_git(repo, "checkout", "-q", "--detach", "main")
        run_git(repo, "merge", "-q", "--no-ff", "pr", "-m", "Merge pr into main")
        return repo

    def test_catalog_only(self):
        repo = self.merged({"catalog.json": "rows v2\n"})
        self.write(repo, "README.md", "generated from v2\n")
        code, out = self.check(repo, "pr", "--base", "HEAD^1", "--head", "HEAD^2")
        self.assertEqual(code, 0, out)

    def test_hand_edit(self):
        repo = self.merged({"README.md": "edited by hand\n"})
        self.write(repo, "README.md", "generated from v1\n")
        code, _ = self.check(repo, "pr", "--base", "HEAD^1", "--head", "HEAD^2")
        self.assertEqual(code, 1)


class PushAndStrictTest(GitCase):
    def setUp(self):
        super().setUp()
        self.repo = self.init("repo", BASE)

    def test_drift_on_main_is_handed_to_the_regenerate_job(self):
        self.write(self.repo, "README.md", "generated from v2\n")
        code, out = self.check(self.repo, "push")
        self.assertEqual(code, 0)
        self.assertEqual(self.output.read_text(), "drift=true\n")
        self.assertIn("the `regenerate` job commits them", self.summary_text())
        self.assertIn("README.md", out)

    def test_no_drift_on_main(self):
        code, _ = self.check(self.repo, "push")
        self.assertEqual(code, 0)
        self.assertEqual(self.output.read_text(), "drift=false\n")

    def test_strict_fails_on_drift_including_an_uncommitted_new_page(self):
        # The case `git diff --quiet` cannot see.
        self.write(self.repo, "docs/by-pattern/b.md", "page b\n")
        code, out = self.check(self.repo, "strict")
        self.assertEqual(code, 1)
        self.assertIn("docs/by-pattern/b.md: the generators produce this file, and it is not committed", out)
        self.assertIn(check_generated.FIX, out)

    def test_strict_passes_when_current(self):
        self.write(self.repo, "CONTRIBUTING.md", "not generated\n")
        code, _ = self.check(self.repo, "strict")
        self.assertEqual(code, 0)


def copy_tree(dest: pathlib.Path) -> None:
    """This repository's working files, tracked or new, without .git."""
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    for rel in filter(None, listed.split("\0")):
        source = ROOT / rel
        if source.is_file():
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


class RealGeneratorsTest(GitCase):
    """The real generators on a scratch copy of this repository. Nothing here
    assumes the committed generated files are current: on a pull request CI
    they need not be."""

    def setUp(self):
        super().setUp()
        self.repo = self.dir / "copy"
        self.repo.mkdir()
        copy_tree(self.repo)
        run_git(self.repo, "init", "-q", "-b", "main")
        self.commit(self.repo, "copy")

    def regenerate(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/regenerate.py"], cwd=self.repo, check=True, capture_output=True, text=True
        )

    def edit_a_summary(self) -> None:
        catalog = self.repo / "catalog.json"
        text = catalog.read_text()
        marker = '"summary": "'
        self.assertIn(marker, text)
        catalog.write_text(text.replace(marker, marker + "Edited in a test. ", 1))

    def changed(self) -> set[str]:
        out = run_git(self.repo, "status", "--porcelain", "--untracked-files=all")
        return {line[3:] for line in out.splitlines()}

    def test_generators_write_nothing_outside_outputs(self):
        self.edit_a_summary()
        self.regenerate()
        written = self.changed() - {"catalog.json"}
        self.assertTrue(written, "editing a summary changed no generated file")
        outside = [p for p in written if not p.startswith(regenerate.OUTPUTS)]
        self.assertEqual(outside, [])

    def test_the_pull_request_flow(self):
        run_git(self.repo, "checkout", "-q", "-b", "pr")
        self.edit_a_summary()
        self.commit(self.repo, "edit a row")
        self.regenerate()
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 0, out)

        run_git(self.repo, "checkout", "-q", "--", ".")
        with (self.repo / "README.md").open("a") as handle:
            handle.write("\n- [my project](https://example.invalid), added by hand\n")
        self.commit(self.repo, "hand edit")
        self.regenerate()
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("::error file=README.md,", out)

        self.commit(self.repo, "regenerate")
        self.regenerate()
        code, out = self.check(self.repo, "pr", "--base", "main")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.changed(), set())


class LintWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = LINT.read_text()
        # The workflow without its comments, so prose cannot satisfy a test.
        self.code = "\n".join(line for line in self.text.splitlines() if not line.lstrip().startswith("#"))

    def job(self, name: str) -> str:
        return self.text.split(f"\n  {name}:\n", 1)[1].split("\n\n  # ", 1)[0]

    def test_the_required_check_keeps_its_name(self):
        self.assertIn("    name: Validate catalog and generated READMEs\n", self.text)

    def test_only_the_regenerate_job_can_write(self):
        self.assertIn("\npermissions:\n  contents: read\n", self.code)
        self.assertEqual(self.code.count("contents: write"), 1)
        self.assertIn("    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n", self.job("regenerate"))
        self.assertNotIn("permissions", self.job("catalog"))
        for scope in ("actions: write", "issues: write", "pull-requests: write"):
            self.assertNotIn(scope, self.code)

    def test_regenerate_runs_only_for_a_push_to_main_with_drift(self):
        self.assertIn(
            "    if: github.event_name == 'push' && github.ref == 'refs/heads/main' "
            "&& needs.catalog.outputs.drift == 'true'\n",
            self.job("regenerate"),
        )
        self.assertIn("    needs: catalog\n", self.job("regenerate"))
        self.assertIn("      drift: ${{ steps.generated.outputs.drift }}\n", self.text)
        self.assertIn("      group: regenerate\n      cancel-in-progress: false\n", self.text)

    def test_regenerate_builds_from_the_tip_and_lints_before_committing(self):
        job = self.job("regenerate")
        self.assertIn("        with:\n          ref: main\n", job)
        self.assertLess(job.index("run: python3 scripts/check.py --ci --quick\n"), job.index("git commit"))
        # That one command regenerates, then runs lint and every other check.
        opts = check.Options(ci=True, quick=True)
        runs = [s.name for s in check.STEPS if check.excluded(s, opts) is None and check.skipped(s, opts) is None]
        self.assertLess(runs.index("regenerate"), runs.index("lint-docs"))
        self.assertTrue({"lint", "compat", "docs", "lint-docs", "covers", "generated"} <= set(runs), runs)
        self.assertIn('git config user.name "github-actions[bot]"', job)
        self.assertIn('git commit -q -m "chore: regenerate from catalog.json"', job)
        self.assertNotIn("push -q origin HEAD:main --force", job)

    def test_the_catalog_job_regenerates_before_judging(self):
        # Since I08 the event split lives in check.py, which the job runs; the
        # step keeps the id its `drift` output is read from.
        self.assertIn("          fetch-depth: 0\n", self.text)
        self.assertTrue(
            self.job("catalog").endswith("        id: generated\n        run: python3 scripts/check.py --ci"),
            self.job("catalog")[-300:],
        )
        names = [step.name for step in check.STEPS]
        self.assertLess(names.index("regenerate"), names.index("generated"))
        ci = check.Options(ci=True)
        self.assertEqual(check.generated_args(ci, "pull_request")[0], ["pr", "--base", "HEAD^1", "--head", "HEAD^2"])
        self.assertEqual(check.generated_args(ci, "push")[0], ["push"])
        self.assertEqual(check.generated_args(ci, "workflow_dispatch")[0], ["strict"])
        self.assertEqual(check.generated_args(ci, "")[0], ["strict"])

    def test_no_expression_reaches_a_shell(self):
        lines = self.text.splitlines()
        in_run, indent = False, 0
        for line in lines:
            stripped = line.lstrip()
            if in_run and stripped and len(line) - len(stripped) <= indent:
                in_run = False
            if stripped.startswith("run:"):
                in_run, indent = True, len(line) - len(stripped)
                self.assertNotIn("${{", line)
            elif in_run:
                self.assertNotIn("${{", line)
        self.assertNotIn("github.event.", self.text.split("\non:", 1)[1])


class WorkflowStepsTest(GitCase):
    """lint.yml's own shell, run as GitHub runs a step that names no `shell:`:
    `bash -e`, without pipefail, so a failure inside a pipeline is not fatal."""

    def bash(self, script: str, cwd: pathlib.Path, **env: str) -> subprocess.CompletedProcess:
        full = {**os.environ, "GITHUB_OUTPUT": str(self.output), "GITHUB_STEP_SUMMARY": str(self.summary), **env}
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-c", script],
            cwd=cwd, env=full, capture_output=True, text=True,
        )

    def with_scripts(self, files: dict[str, str]) -> dict[str, str]:
        scripts = {
            f"scripts/{name}": (ROOT / "scripts" / name).read_text()
            for name in ("regenerate.py", "check_generated.py", "check.py")
        }
        return {**files, **scripts}

    # ---- the catalog job's verdict step ------------------------------------

    def merged_with_hand_edit(self) -> pathlib.Path:
        repo = self.init("repo", self.with_scripts(BASE))
        run_git(repo, "checkout", "-q", "-b", "pr")
        self.write(repo, "README.md", "edited by hand\n")
        self.commit(repo, "pull request")
        run_git(repo, "checkout", "-q", "--detach", "main")
        run_git(repo, "merge", "-q", "--no-ff", "pr", "-m", "merge")
        self.write(repo, "README.md", "generated from v1\n")
        return repo

    def test_each_event_gets_its_own_verdict(self):
        step = VERDICT
        repo = self.merged_with_hand_edit()
        done = self.bash(step, repo, GITHUB_EVENT_NAME="pull_request")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("::error file=README.md,", done.stdout)

        done = self.bash(step, repo, GITHUB_EVENT_NAME="push")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("drift=true", self.output.read_text())

        done = self.bash(step, repo, GITHUB_EVENT_NAME="workflow_dispatch")
        self.assertEqual(done.returncode, 1)

    # ---- the regenerate job's landing step ---------------------------------

    LAND = "Commit to main, or fall back to a branch if main moved"

    def origin_and_clone(self) -> tuple[pathlib.Path, pathlib.Path]:
        seed = self.init("seed", self.with_scripts(BASE))
        origin = self.dir / "origin.git"
        run_git(self.dir, "clone", "-q", "--bare", str(seed), str(origin))
        work = self.dir / "work"
        run_git(self.dir, "clone", "-q", str(origin), str(work))
        return origin, work

    def someone_pushes(self, origin: pathlib.Path, rel: str, text: str) -> None:
        other = self.dir / "other"
        if not other.exists():
            run_git(self.dir, "clone", "-q", str(origin), str(other))
        run_git(other, "pull", "-q", "--ff-only")
        self.write(other, rel, text)
        self.commit(other, f"edit {rel}")
        run_git(other, "push", "-q", "origin", "HEAD:main")

    def origin_log(self, origin: pathlib.Path, ref: str = "main") -> list[str]:
        return run_git(origin, "log", "--format=%an|%s", ref).splitlines()

    def test_nothing_to_commit(self):
        origin, work = self.origin_and_clone()
        done = self.bash(workflow_step(self.LAND), work)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("landed=none", self.output.read_text())
        self.assertEqual(len(self.origin_log(origin)), 1)

    def test_lands_on_main_as_the_bot_and_stages_only_outputs(self):
        origin, work = self.origin_and_clone()
        self.write(work, "README.md", "generated from v2\n")
        self.write(work, "docs/by-pattern/b.md", "a new page\n")
        self.write(work, "catalog.json", "must never be committed by the bot\n")
        done = self.bash(workflow_step(self.LAND), work)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("landed=main", self.output.read_text())
        self.assertEqual(self.origin_log(origin)[0], "github-actions[bot]|chore: regenerate from catalog.json")
        committed = run_git(origin, "show", "--name-only", "--format=", "main").split()
        self.assertEqual(sorted(committed), ["README.md", "docs/by-pattern/b.md"])
        self.assertIn("(2 files)", run_git(origin, "log", "-1", "--format=%b", "main"))
        self.assertIn("## Regenerated on main", self.summary_text())

    def test_a_failing_output_list_stops_the_step_and_stages_nothing(self):
        # Piped straight into `git add -A`, a failed `--list` is an empty
        # pathspec list, which stages the whole tree: the bot would commit
        # catalog.json and whatever else the run left behind.
        origin, work = self.origin_and_clone()
        self.write(work, "README.md", "generated from v2\n")
        self.write(work, "catalog.json", "must never be committed by the bot\n")
        self.write(work, "scripts/regenerate.py", "import sys\nsys.exit(3)\n")
        done = self.bash(workflow_step(self.LAND), work)
        self.assertNotEqual(done.returncode, 0, done.stdout)
        self.assertEqual(run_git(work, "diff", "--cached", "--name-only"), "")
        self.assertEqual(len(self.origin_log(origin)), 1)

    def test_rebases_onto_an_unrelated_push(self):
        origin, work = self.origin_and_clone()
        self.write(work, "README.md", "generated from v2\n")
        self.someone_pushes(origin, "CONTRIBUTING.md", "edited meanwhile\n")
        done = self.bash(workflow_step(self.LAND), work)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("landed=main", self.output.read_text())
        self.assertEqual(
            [line.split("|")[1] for line in self.origin_log(origin)][:2],
            ["chore: regenerate from catalog.json", "edit CONTRIBUTING.md"],
        )

    def test_falls_back_to_a_branch_rather_than_forcing(self):
        origin, work = self.origin_and_clone()
        self.write(work, "README.md", "generated from v2\n")
        self.someone_pushes(origin, "README.md", "a conflicting README\n")
        before = self.origin_log(origin)
        done = self.bash(workflow_step(self.LAND), work)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.origin_log(origin), before)
        landed = self.output.read_text().strip().split("=", 1)[1]
        self.assertTrue(landed.startswith("regenerate/"), landed)
        self.assertEqual(self.origin_log(origin, landed)[0].split("|")[1], "chore: regenerate from catalog.json")
        self.assertIn("::warning title=Regenerated files are not on main::", done.stdout)
        self.assertIn("## Regenerated files are on a branch", self.summary_text())


if __name__ == "__main__":
    unittest.main()
