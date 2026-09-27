"""review_pr.py: the review card a pull request's rows get in lint (I03).

The card's Markdown and annotations, the rows it picks from a real git history
(the merge base, not whatever main did since), that the base branch's copy of
the scripts judges the pull request's catalogue without importing anything
from it, and lint.yml's review job run as GitHub runs it. No network: the card
runs --offline or with a fake Net.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "tests"))

import check  # noqa: E402
import review_pr as rp  # noqa: E402
import review_rows as rr  # noqa: E402
from test_review_rows import FakeNet, row  # noqa: E402

LINT = ROOT / ".github" / "workflows" / "lint.yml"
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
IDENTITY = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]
STEP = "Review the rows with the base branch's scripts"


def git(cwd: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", *IDENTITY, *args], cwd=cwd, capture_output=True, text=True, check=True,
        env={**os.environ, **GIT_ENV},
    ).stdout


def dump(rows: list[dict]) -> str:
    return json.dumps(rows, indent=2, ensure_ascii=False) + "\n"


def finding(check_key: str, level: str, text: str = "words") -> rr.Finding:
    return rr.Finding(check_key, level, text)


def card(*rows: rr.RowReview, **extra) -> rp.Card:
    fields = {"base": "a" * 40, "author": "alice", "rows": rows, "removed": (), "retired": (),
              "notes": (), "ran_from": "the base commit's scripts", **extra}
    return rp.Card(**fields)


REVIEW = rr.RowReview("demo-row", "added", (), (
    finding("call-site", "ok", "Every string."),
    finding("repository", "warning", "`stars` is 1, GitHub counts 50."),
    finding("link", "ok", "The link answered 200."),
    finding("self-submission", "error", "`alice` owns it."),
    finding("classification", "info", "A hint."),
))


class CardTest(unittest.TestCase):
    def test_table_details_and_both_languages(self):
        text = rp.markdown(card(REVIEW))
        self.assertIn("| Row | | Call site | Repository | Link | Author | Flag notes | Kind / patterns |", text)
        self.assertIn("| `demo-row` | added | ✓ | ⚠ | ✓ | ✗ |  | ℹ |", text)
        self.assertIn("- ✗ **Author**: `alice` owns it.", text)
        self.assertIn("- ✓ Call site, Link", text)
        self.assertIn("1 added, 0 changed, 0 removed; 1 ✗, 1 ⚠, 0 not checked", text)
        self.assertIn("nothing on it fails this check", text)
        self.assertIn("a second gate, not a review", text)
        self.assertIn("a maintainer still reads the call site", text)
        self.assertIn("第二道门，不是审核", text)
        self.assertIn("维护者仍要亲自读调用点", text)
        self.assertIn("目前仅供参考", text)
        self.assertTrue(text.rstrip().split("\n")[-1].startswith("- GitHub"), "usage lines last")
        zh = next(line for line in text.splitlines() if "第二道门" in line)
        self.assertTrue(zh.endswith("<sub>(机翻)</sub>"))

    def test_blocking_says_so(self):
        text = rp.markdown(card(REVIEW, blocking=True))
        self.assertIn("**✗ fails this check**", text)
        self.assertNotIn("nothing on it fails", text)
        self.assertNotIn("目前仅供参考", text)

    def test_no_rows(self):
        self.assertIn("No row in `catalog.json` was added or changed.", rp.markdown(card()))

    def test_a_changed_row_names_its_fields_and_may_have_nothing_to_check(self):
        text = rp.markdown(card(rr.RowReview("demo-row", "changed", ("summary",), ())))
        self.assertIn("#### `demo-row` — changed: `summary`", text)
        self.assertIn("No field a check reads changed.", text)

    def test_removed_rows(self):
        text = rp.markdown(card(removed=("gone-row", "retired-row"), retired=("retired-row",)))
        self.assertIn("moved to `retired.json`: `retired-row`", text)
        self.assertIn("⚠ removed without moving to `retired.json`: `gone-row`", text)

    def test_a_long_card_is_cut_in_the_summary_not_in_the_log(self):
        many = [rr.RowReview(f"r{n:04}", "added", (), ()) for n in range(rp.TABLE_ROWS + 3)]
        text = rp.markdown(card(*many))
        self.assertIn("…and 3 more, in the log", text)
        self.assertNotIn(f"r{rp.TABLE_ROWS + 2:04}", text)
        self.assertIn(f"r{rp.TABLE_ROWS + 2:04}", rp.console(card(*many)))

    def test_hostile_slugs_and_fields_stay_in_their_span(self):
        evil = "x`|y\n::error::z"
        text = rp.markdown(card(rr.RowReview(evil, "changed", (evil,), (finding("link", "error"),))))
        self.assertNotIn("\n::error::", text)
        self.assertIn("| `x'\\|y ::error::z` | changed |", text)
        # A slug still starts a console line: in CI, main() prints the card
        # with workflow commands stopped (HistoryTest, test_ci_prints_…).
        log = rp.console(card(rr.RowReview(evil, "changed", (evil,), ())))
        self.assertFalse(any(line.startswith("::") for line in log.splitlines()), log)

    def test_annotations(self):
        lines = {"demo-row": 7}
        self.assertEqual(
            rp.annotations(card(REVIEW), lines),
            [
                "::notice file=catalog.json,line=7,title=Review card%3A demo-row (Repository)::"
                "`stars` is 1, GitHub counts 50.",
                "::warning file=catalog.json,line=7,title=Review card%3A demo-row (Author)::`alice` owns it.",
            ],
        )
        blocking = rp.annotations(card(REVIEW, blocking=True), {})
        self.assertTrue(blocking[1].startswith("::error title=Review card%3A demo-row (Author)::"))
        odd = rr.RowReview("demo-row", "added", (), (finding("link", "error", "100% down"),))
        self.assertTrue(rp.annotations(card(odd), {})[0].endswith("::100%25 down"))

    def test_slug_lines(self):
        text = dump([row(slug="a"), row(slug="b")])
        lines = rp.slug_lines(text)
        self.assertEqual(text.splitlines()[lines["b"] - 1].strip(), '"slug": "b",')
        self.assertEqual(set(lines), {"a", "b"})

    def test_json(self):
        data = json.loads(rp.as_json(card(REVIEW)))
        self.assertEqual((data["errors"], data["warnings"]), (1, 1))
        self.assertEqual(data["rows"][0]["findings"][3]["check"], "self-submission")

    def test_author(self):
        self.assertEqual(rp.author_from("liu-x27"), ("liu-x27", None))
        self.assertEqual(rp.author_from(""), (None, None))
        login, note = rp.author_from('x"; touch /tmp/pwned; echo "')
        self.assertIsNone(login)
        self.assertIn("not a GitHub login", note)


class GitCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        env = mock.patch.dict(os.environ, {**GIT_ENV, "PR_AUTHOR": ""})
        env.start()
        self.addCleanup(env.stop)

    def repo(self, name: str, files: dict[str, str]) -> pathlib.Path:
        repo = self.dir / name
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        self.commit(repo, files, "base")
        return repo

    def commit(self, repo: pathlib.Path, files: dict[str, str], message: str) -> None:
        for rel, text in files.items():
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    def run_card(self, *argv: str, net=None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if net is None:
                code = rp.main(list(argv))
            else:
                with mock.patch.object(rp, "default_net", lambda: net):
                    code = rp.main(list(argv))
        return code, out.getvalue(), err.getvalue()


class HistoryTest(GitCase):
    def setUp(self):
        super().setUp()
        self.tree = self.repo("tree", {"catalog.json": dump([row(slug="a"), row(slug="b")]), "retired.json": "[]\n"})
        git(self.tree, "checkout", "-q", "-b", "topic")
        self.commit(self.tree, {"catalog.json": dump([row(slug="a"), row(slug="b", summary="new"), row(slug="c")])}, "topic")
        # main moves on after the branch left it: not the branch's change.
        git(self.tree, "checkout", "-q", "main")
        self.commit(self.tree, {"catalog.json": dump([row(slug="a", stars=5), row(slug="b")])}, "main moves")
        git(self.tree, "checkout", "-q", "topic")

    def test_rows_are_compared_with_the_merge_base(self):
        code, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--offline", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual([(r["slug"], r["kind"], r["fields"]) for r in data["rows"]],
                         [("c", "added", []), ("b", "changed", ["summary"])])
        self.assertEqual(data["base"], git(self.tree, "merge-base", "main", "HEAD").strip())
        # This repository's scripts judged another checkout, which changed none.
        self.assertIn("not this pull request's", data["ran_from"])
        self.assertEqual(data["notes"], [])

    def test_uncommitted_edits_count(self):
        (self.tree / "catalog.json").write_text(dump([row(slug="a"), row(slug="b")]))
        _, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--offline", "--json")
        self.assertEqual(json.loads(out)["rows"], [])

    def test_an_unknown_base_is_reported_not_failed(self):
        code, out, err = self.run_card("--tree", str(self.tree), "--base", "nope", "--offline")
        self.assertEqual((code, out), (0, ""))
        self.assertIn("review card not run: nope is not a commit", err)
        code, _, _ = self.run_card("--tree", str(self.tree), "--base", "nope", "--offline", "--blocking")
        self.assertEqual(code, 2)

    def test_advisory_exits_0_whatever_it_finds_and_blocking_does_not(self):
        (self.tree / "catalog.json").write_text(dump([row(slug="a"), row(slug="b"), row(slug="c", flags=["ai-generated"])]))
        code, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--offline")
        self.assertEqual(code, 0)
        self.assertIn("✗", out)
        code, _, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--offline", "--blocking")
        self.assertEqual(code, 1)

    def test_an_unparsable_catalogue_is_a_note(self):
        (self.tree / "catalog.json").write_text("[{")
        code, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--offline", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("catalog.json could not be read", data["notes"][0])
        self.assertEqual(data["removed"], ["a", "b"])

    def test_ci_writes_the_summary_and_annotates_lines(self):
        summary = self.dir / "summary.md"
        net = FakeNet(link=(404, "Not Found")).net()
        with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary), "PR_AUTHOR": "Alice"}):
            code, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--ci", net=net)
        self.assertEqual(code, 0)
        text = summary.read_text()
        self.assertIn("## Review card", text)
        self.assertIn("opened by `Alice`", text)
        line = rp.slug_lines((self.tree / "catalog.json").read_text())["c"]
        self.assertIn(f"::warning file=catalog.json,line={line},title=Review card%3A c (Link)::", out)
        self.assertIn(f"::warning file=catalog.json,line={line},title=Review card%3A c (Author)::", out)

    def test_ci_prints_the_pull_requests_strings_with_workflow_commands_stopped(self):
        # The runner reads `::name::` after leading spaces, and a slug starts
        # a console line, so a row could forge or silence annotations (review
        # of I03). Only this script's own annotations may sit outside the stop.
        evil = "::error title=Spoofed::all clear"
        rows = [row(slug="a"), row(slug="b"),
                row(slug=evil, flags=["ai-generated"], evidence={"path": "##[error]forged", "matched": ["x"]})]
        (self.tree / "catalog.json").write_text(dump(rows))
        with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(self.dir / "summary.md"), "PR_AUTHOR": "bob"}):
            code, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--ci", "--offline")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        (stop,) = [i for i, line in enumerate(lines) if line.startswith("::stop-commands::")]
        token = lines[stop].removeprefix("::stop-commands::")
        self.assertRegex(token, r"^[0-9a-f]{32}$")
        resume = lines.index(f"::{token}::")
        self.assertTrue(any(line.strip().startswith(evil) for line in lines[stop + 1:resume]))
        outside = lines[:stop] + lines[resume + 1:]
        self.assertTrue(outside, "the annotations follow the card")
        for line in outside:
            with self.subTest(line=line):
                if line.lstrip().startswith("::"):
                    self.assertRegex(line, r"^::(warning|notice) file=catalog\.json,line=\d+,title=Review card%3A ")
                    self.assertNotIn("::error title=Spoofed", line)

    def test_pr_author_comes_from_the_environment_and_is_checked(self):
        with mock.patch.dict(os.environ, {"PR_AUTHOR": "not a login"}):
            _, out, _ = self.run_card("--tree", str(self.tree), "--base", "main", "--offline", "--json")
        data = json.loads(out)
        self.assertIsNone(data["author"])
        self.assertIn("not a GitHub login", data["notes"][-1])


class BaseScriptsTest(GitCase):
    """lint.yml runs the base branch's scripts against the pull request's tree.
    Nothing the pull request adds under scripts/ may be imported, even a module
    named after one the card imports, or after the standard library's json."""

    def test_the_pull_requests_scripts_are_data(self):
        base = self.dir / "base"
        shutil.copytree(ROOT / "scripts", base / "scripts", ignore=shutil.ignore_patterns("tests", "__pycache__"))
        tree = self.repo("tree", {"catalog.json": dump([row(slug="a")])})
        marker = self.dir / "imported"
        poison = f"open({str(marker)!r}, 'w').write(__name__)\nraise SystemExit('pull request code ran')\n"
        self.commit(tree, {
            "catalog.json": dump([row(slug="a"), row(slug="b", flags=["code-untested"])]),
            "scripts/review_rows.py": poison,
            "scripts/json.py": poison,
            "scripts/_github.py": poison,
        }, "pull request")
        done = subprocess.run(
            [sys.executable, str(base / "scripts" / "review_pr.py"), "--tree", str(tree), "--base", "HEAD~1", "--offline"],
            cwd=tree, capture_output=True, text=True, env={**os.environ, **GIT_ENV, "PR_AUTHOR": "bob"},
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertFalse(marker.exists(), done.stdout)
        self.assertIn("b — added", done.stdout)
        self.assertIn("Flag notes: Flagged `code-untested` with no `notes` line", done.stdout)
        self.assertIn("not this pull request's", done.stdout)
        self.assertIn("changes 3 file(s) under `scripts/` or `.github/`", done.stdout)


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        text = LINT.read_text()
        self.job = text.split("\n  review:\n", 1)[1]
        self.header = text.split("\nname: lint\n", 1)[0]

    def test_it_runs_on_pull_requests_only_with_a_read_only_token(self):
        self.assertIn("    if: github.event_name == 'pull_request'\n", self.job)
        self.assertNotIn("permissions", self.job)
        self.assertIn("\npermissions:\n  contents: read\n", LINT.read_text())
        self.assertIn("          fetch-depth: 0\n", self.job)
        self.assertIn("          persist-credentials: false\n", self.job)
        self.assertIn("    timeout-minutes: 10\n", self.job)

    def test_advisory_the_step_cannot_fail_the_job(self):
        self.assertIn("        continue-on-error: true\n", self.job)
        self.assertNotIn("--blocking", self.job.split("run: |", 1)[1])

    def test_the_author_arrives_through_the_environment_only(self):
        self.assertIn("          PR_AUTHOR: ${{ github.event.pull_request.user.login }}\n", self.job)
        self.assertIn("          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n", self.job)
        run = self.job.split("        run: |\n", 1)[1]
        self.assertNotIn("${{", run)
        self.assertNotIn("PR_AUTHOR", run)
        self.assertIn("PR_AUTHOR", self.header)
        self.assertIn("review_pr.py", self.header)

    def test_the_check_is_a_step_of_check_py_for_this_job(self):
        step = check.BY_NAME["review"]
        self.assertEqual((step.job, step.needs, step.argv), ("review", "network", ("python3", "scripts/review_pr.py")))
        self.assertIn("review", check.JOBS)


def step_script() -> str:
    lines = LINT.read_text().splitlines()
    start = lines.index(f"      - name: {STEP}")
    run = next(i for i in range(start, len(lines)) if lines[i] == "        run: |")
    body = []
    for line in lines[run + 1:]:
        if line.strip() and not line.startswith(" " * 10):
            break
        body.append(line[10:])
    return "\n".join(body)


class WorkflowStepTest(GitCase):
    """The step's shell, as GitHub runs a step without `shell:` (bash -e), in
    the merge-commit checkout a pull_request event gets. Each side's
    review_pr.py is a stub saying whose copy it is."""

    STUB = (
        "import json, os, pathlib, sys\n"
        "print(json.dumps({{'copy': {who!r}, 'argv': sys.argv[1:], 'author': os.environ.get('PR_AUTHOR'),\n"
        "                  'file': str(pathlib.Path(__file__).resolve())}}))\n"
    )

    def workspace(self, base_has_script: bool) -> pathlib.Path:
        files = {"catalog.json": dump([row(slug="a")])}
        if base_has_script:
            files["scripts/review_pr.py"] = self.STUB.format(who="base")
        repo = self.repo("workspace", files)
        git(repo, "checkout", "-q", "-b", "pr")
        self.commit(repo, {"catalog.json": dump([row(slug="a"), row(slug="b")]),
                           "scripts/review_pr.py": self.STUB.format(who="pull request")}, "pull request")
        git(repo, "checkout", "-q", "main")
        git(repo, "merge", "-q", "--no-ff", "-m", "merge", "pr")
        return repo

    def run_step(self, repo: pathlib.Path) -> subprocess.CompletedProcess:
        runner = self.dir / "runner"
        runner.mkdir()
        env = {**os.environ, **GIT_ENV, "RUNNER_TEMP": str(runner), "GITHUB_WORKSPACE": str(repo),
               "PR_AUTHOR": 'o"; touch pwned; echo "'}
        return subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", step_script()],
                              cwd=repo, env=env, capture_output=True, text=True)

    def test_the_base_copy_runs_on_the_pull_requests_tree(self):
        repo = self.workspace(base_has_script=True)
        done = self.run_step(repo)
        self.assertEqual(done.returncode, 0, done.stderr)
        said = json.loads(done.stdout)
        self.assertEqual(said["copy"], "base")
        self.assertEqual(said["argv"], ["--ci", "--tree", str(repo), "--base", "HEAD^1"])
        self.assertEqual(said["author"], 'o"; touch pwned; echo "')
        self.assertTrue(said["file"].startswith(str((self.dir / "runner" / "base").resolve())), said["file"])
        self.assertFalse((repo / "pwned").exists())

    def test_no_card_until_the_base_branch_has_the_script(self):
        repo = self.workspace(base_has_script=False)
        done = self.run_step(repo)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("The base branch has no scripts/review_pr.py yet", done.stdout)
        self.assertNotIn("pull request", done.stdout.replace("no scripts/review_pr.py", ""))


class DocsTest(unittest.TestCase):
    def test_contributing_explains_the_card(self):
        text = (ROOT / "CONTRIBUTING.md").read_text()
        section = " ".join(text.split("### The review card", 1)[1].split("\n## ", 1)[0].split())
        for words in ("second gate", "does not replace", "reads the call site", "base branch",
                      "python3 scripts/review_pr.py", "Approve and run", "advisory"):
            with self.subTest(words=words):
                self.assertIn(words, section)

    def test_the_template_points_at_it(self):
        self.assertIn("review card", (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text())


if __name__ == "__main__":
    unittest.main()
