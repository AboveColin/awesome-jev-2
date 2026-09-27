"""The MCP package's version is on PyPI, or the gap is reported (I32).

SKILL.md, llms.txt and the package README told readers outside Claude Code to
`pip install awesome-jev-mcp`, while PyPI answered 404: no release tag had ever
been pushed and nothing in CI looked. check_release.py compares
pyproject.toml's version with PyPI on every push to main (lint's `release`
job): pending is a warning, a version older than PyPI's newest fails, and the
files declaring the version must agree. publish.yml installs a release back
from PyPI after uploading it, retrying while the index catches up.

PyPI is played by a local HTTP server; a stub `python3`, `pip` and `sleep` play
the publish job's tools. Nothing leaves this machine.
"""

from __future__ import annotations

import contextlib
import http.server
import io
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_release  # noqa: E402

WORKFLOWS = ROOT / ".github" / "workflows"


class FakePyPI:
    """Answers /pypi/<package>/json with a status and body, counting hits."""

    def __init__(self, status: int = 200, body: bytes | None = None, length: int | None = None):
        self.status, self.body, self.hits = status, body or b"", 0
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802 - http.server's name
                outer.hits += 1
                outer.path = self.path
                self.send_response(outer.status)
                self.send_header("Content-Type", "application/json")
                if length is not None:
                    # Promise more than is sent, then hang up: a cut connection.
                    self.send_header("Content-Length", str(length))
                    self.close_connection = True
                self.end_headers()
                self.wfile.write(outer.body)

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/pypi"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def releases(*versions: str) -> bytes:
    return json.dumps({"info": {"name": "awesome-jev-mcp"}, "releases": {v: [] for v in versions}}).encode()


def closed_port_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}/pypi"


class VersionOrderTest(unittest.TestCase):
    def test_release_segments_compare_numerically(self):
        key = check_release.version_key
        self.assertLess(key("0.9.0"), key("0.10.0"))
        self.assertLess(key("0.1"), key("0.1.1"))
        self.assertEqual(key("1.0"), key("1.0.0"))

    def test_a_pre_release_comes_before_its_release(self):
        key = check_release.version_key
        self.assertLess(key("0.2.0a1"), key("0.2.0b1"))
        self.assertLess(key("0.2.0b1"), key("0.2.0rc1"))
        self.assertLess(key("0.2.0rc1"), key("0.2.0"))
        self.assertLess(key("0.1.9"), key("0.2.0rc1"))

    def test_anything_else_is_not_ordered_rather_than_guessed(self):
        for text in ("0.1.0.post1", "0.1.0.dev3", "1.0+local", "latest", ""):
            with self.subTest(text=text):
                self.assertIsNone(check_release.version_key(text))


class JudgeTest(unittest.TestCase):
    def status(self, version, published):
        return check_release.judge(version, published)[0]

    def test_never_published_is_pending(self):
        self.assertEqual(self.status("0.1.0", None), "pending")
        self.assertEqual(self.status("0.1.0", []), "pending")

    def test_the_version_on_pypi_is_published(self):
        self.assertEqual(self.status("0.1.0", ["0.1.0"]), "published")
        self.assertEqual(self.status("0.2.0", ["0.1.0", "0.2.0"]), "published")
        self.assertEqual(self.status("1.0", ["1.0.0"]), "published")

    def test_a_bump_not_yet_tagged_is_pending(self):
        self.assertEqual(self.status("0.2.0", ["0.1.0"]), "pending")
        self.assertEqual(self.status("0.2.0", ["0.1.0", "0.2.0rc1"]), "pending")

    def test_a_version_older_than_pypi_newest_is_behind(self):
        self.assertEqual(self.status("0.1.0", ["0.1.0", "0.2.0"]), "behind")
        self.assertEqual(self.status("0.1.5", ["0.2.0"]), "behind")
        self.assertIn("0.2.0", "\n".join(check_release.judge("0.1.5", ["0.2.0"])[1]))

    def test_unorderable_releases_never_make_it_behind(self):
        self.assertEqual(self.status("0.2.0", ["0.1.0", "0.3.0.post1"]), "pending")


class Tree:
    """A scratch copy of the files that declare the version."""

    def __init__(self, test: unittest.TestCase, pyproject="0.1.0", plugin="0.1.0", marketplace=None):
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        (self.root / ".claude-plugin").mkdir()
        text = (ROOT / "pyproject.toml").read_text()
        real = check_release.pyproject_version(ROOT)
        (self.root / "pyproject.toml").write_text(text.replace(f'version = "{real}"', f'version = "{pyproject}"', 1))
        plugin_json = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        (self.root / ".claude-plugin" / "plugin.json").write_text(json.dumps({**plugin_json, "version": plugin}))
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        if marketplace is not None:
            market["plugins"] = [{**p, "version": marketplace} for p in market["plugins"]]
        (self.root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market))


class MainTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.output = pathlib.Path(tmp.name) / "output"
        self.summary = pathlib.Path(tmp.name) / "summary"
        env = {"GITHUB_OUTPUT": str(self.output), "GITHUB_STEP_SUMMARY": str(self.summary), "GITHUB_SHA": "abc1234def"}
        patcher = patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        retry = patch.object(check_release, "RETRY_DELAY", 0)
        retry.start()
        self.addCleanup(retry.stop)

    def run_check(self, *argv, root=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_release.main([*argv, *(["--root", str(root)] if root else [])])
        return code, out.getvalue()

    def pypi(self, status=200, body=None, length=None) -> FakePyPI:
        server = FakePyPI(status, body, length)
        self.addCleanup(server.close)
        return server

    def status(self):
        return self.output.read_text().strip().splitlines()[-1]

    def test_published_passes(self):
        server = self.pypi(body=releases("0.1.0"))
        code, out = self.run_check("--pypi", server.url, root=Tree(self).root)
        self.assertEqual((code, self.status()), (0, "status=published"))
        self.assertEqual(server.path, "/pypi/awesome-jev-mcp/json")
        self.assertIn("0.1.0", out)

    def test_never_published_warns_with_the_tag_command_and_passes(self):
        server = self.pypi(status=404, body=b'{"message": "Not Found"}')
        code, out = self.run_check("--pypi", server.url, root=Tree(self).root)
        self.assertEqual((code, self.status()), (0, "status=pending"))
        self.assertIn("::warning title=MCP package release pending::", out)
        summary = self.summary.read_text()
        self.assertIn("git tag awesome-jev-mcp-v0.1.0 abc1234def", summary)
        self.assertIn("git push origin awesome-jev-mcp-v0.1.0", summary)
        self.assertIn("trusted publisher", summary.lower())
        self.assertEqual(server.hits, 1, "a 404 is an answer, not a hiccup to retry")

    def test_a_bump_awaiting_its_tag_warns_and_passes(self):
        server = self.pypi(body=releases("0.1.0"))
        code, out = self.run_check("--pypi", server.url, root=Tree(self, "0.2.0", "0.2.0").root)
        self.assertEqual((code, self.status()), (0, "status=pending"))
        self.assertIn("::warning", out)
        self.assertNotIn("trusted publisher", self.summary.read_text().lower())

    def test_going_backwards_fails(self):
        server = self.pypi(body=releases("0.1.0", "0.2.0"))
        code, out = self.run_check("--pypi", server.url, root=Tree(self, "0.1.0", "0.1.0").root)
        self.assertEqual((code, self.status()), (1, "status=behind"))
        self.assertIn("::error", out)

    def test_server_errors_are_skipped_after_one_retry(self):
        server = self.pypi(status=503, body=b"unavailable")
        code, out = self.run_check("--pypi", server.url, root=Tree(self).root)
        self.assertEqual((code, self.status()), (0, "status=skipped"))
        self.assertEqual(server.hits, 2)
        self.assertIn("HTTP 503", out)
        self.assertNotIn("::warning", out)
        self.assertNotIn("::error", out)

    def test_garbage_and_unreachable_are_skipped(self):
        server = self.pypi(body=b"<html>captive portal</html>")
        self.assertEqual(self.run_check("--pypi", server.url, root=Tree(self).root)[0], 0)
        self.assertEqual(self.status(), "status=skipped")
        self.assertEqual(self.run_check("--pypi", closed_port_url(), root=Tree(self).root)[0], 0)
        self.assertEqual(self.status(), "status=skipped")

    def test_an_answer_cut_off_midway_is_skipped_not_a_crash(self):
        # http.client raises IncompleteRead, which is not an OSError.
        server = self.pypi(body=releases("0.1.0")[:20], length=4096)
        code, out = self.run_check("--pypi", server.url, root=Tree(self).root)
        self.assertEqual((code, self.status()), (0, "status=skipped"))
        self.assertEqual(server.hits, 2)
        self.assertIn("IncompleteRead", out)

    def test_disagreeing_declarations_fail_before_any_network(self):
        for tree in (Tree(self, "0.2.0", "0.1.0"), Tree(self, marketplace="0.3.0")):
            with self.subTest(root=tree.root):
                code, out = self.run_check("--pypi", closed_port_url(), root=tree.root)
                self.assertEqual((code, self.status()), (1, "status=mismatch"))
                self.assertIn("::error", out)

    def test_offline_checks_only_the_files(self):
        code, out = self.run_check("--offline", "--pypi", closed_port_url(), root=Tree(self).root)
        self.assertEqual((code, self.status()), (0, "status=offline"))
        self.assertEqual(self.run_check("--offline", root=Tree(self, "0.2.0", "0.1.0").root)[0], 1)


class RepositoryTest(unittest.TestCase):
    """The pull-request half: no network, so it runs in lint's unit tests."""

    def test_this_tree_declares_one_version(self):
        declared = check_release.declared_versions(ROOT)
        self.assertIn("pyproject.toml", declared)
        self.assertIn(".claude-plugin/plugin.json", declared)
        self.assertEqual(len(set(declared.values())), 1, declared)


class InstallRouteTest(unittest.TestCase):
    """Wherever a reader is told to install from PyPI, the repository route is
    given beside it, for whenever pip finds no release."""

    PYPI_ROUTE = "pip install awesome-jev-mcp"
    GIT_ROUTE = "pip install git+https://github.com/kydlikebtc/awesome-jev"

    def test_every_pypi_instruction_has_the_git_fallback(self):
        listed = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
        readers = [
            path for path in listed.stdout.splitlines()
            if path.endswith((".md", ".txt")) or path == "src/awesome_jev_mcp/server.py"
        ]
        found = [path for path in readers if self.PYPI_ROUTE in (ROOT / path).read_text(encoding="utf-8")]
        self.assertTrue(
            {"llms.txt", "skills/awesome-jev/SKILL.md", "src/awesome_jev_mcp/README.md"} <= set(found), found
        )
        for path in found:
            with self.subTest(path=path):
                self.assertIn(self.GIT_ROUTE, (ROOT / path).read_text(encoding="utf-8"))


class WorkflowWiringTest(unittest.TestCase):
    def test_lint_checks_pypi_only_for_a_push_to_main(self):
        text = (WORKFLOWS / "lint.yml").read_text()
        jobs = text.split("\njobs:\n", 1)[1]
        release = jobs.split("\n  release:\n", 1)[1].split("\n  # ", 1)[0]
        self.assertIn("    if: github.event_name == 'push' && github.ref == 'refs/heads/main'\n", release)
        self.assertIn("run: python3 scripts/check_release.py\n", release)
        self.assertNotIn("needs:", release)
        catalog = jobs.split("  catalog:\n", 1)[1].split("\n  regenerate:\n", 1)[0]
        self.assertNotIn("check_release", catalog)

    def test_publish_installs_the_release_back_after_uploading(self):
        text = (WORKFLOWS / "publish.yml").read_text()
        smoke = text.split("\n  smoke:\n", 1)[1]
        self.assertIn("    needs: publish\n", smoke)
        self.assertIn("    if: startsWith(github.ref, 'refs/tags/awesome-jev-mcp-v')\n", smoke)
        self.assertNotIn("actions/checkout", smoke, "it must install from PyPI, not the tree")


class SmokeStepTest(unittest.TestCase):
    """publish.yml's post-upload install, run under bash -e with stubs."""

    STEP = "Install the release from PyPI, retrying while the index catches up"
    PYTHON3 = "\n".join(
        [
            "#!/usr/bin/env bash",
            'if [ "$1 $2" = "-m venv" ]; then',
            '  mkdir -p "$3/bin"',
            '  cp "$STUBS/pip.tmpl" "$3/bin/pip"; cp "$STUBS/python.tmpl" "$3/bin/python"',
            '  chmod +x "$3/bin/pip" "$3/bin/python"; exit 0',
            "fi",
            "exit 97",
            "",
        ]
    )
    PIP = "\n".join(
        [
            "#!/usr/bin/env bash",
            'echo "pip $*" >> "$LOG"',
            'n=$(grep -c "^pip " "$LOG")',
            '[ "$n" -gt "$FAIL_TIMES" ]',
            "",
        ]
    )
    PYTHON = "\n".join(["#!/usr/bin/env bash", 'cat > /dev/null; echo "python $*" >> "$LOG"', 'exit "$PY_EXIT"', ""])
    SLEEP = "\n".join(["#!/usr/bin/env bash", 'echo "sleep $*" >> "$LOG"', ""])

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        self.stubs = self.dir / "stubs"
        self.stubs.mkdir()
        for name, body in (("python3", self.PYTHON3), ("sleep", self.SLEEP), ("pip.tmpl", self.PIP), ("python.tmpl", self.PYTHON)):
            (self.stubs / name).write_text(body)
            (self.stubs / name).chmod(0o755)
        self.log = self.dir / "log"
        self.runner_temp = self.dir / "runner"
        self.runner_temp.mkdir()

    def step(self) -> str:
        lines = (WORKFLOWS / "publish.yml").read_text().splitlines()
        start = lines.index(f"      - name: {self.STEP}")
        run = next(i for i in range(start, len(lines)) if lines[i] == "        run: |")
        body = []
        for line in lines[run + 1 :]:
            if line.strip() and not line.startswith(" " * 10):
                break
            body.append(line[10:])
        return "\n".join(body)

    def run_step(self, fail_times: int, py_exit: int = 0):
        env = {
            **os.environ,
            "PATH": f"{self.stubs}{os.pathsep}{os.environ['PATH']}",
            "STUBS": str(self.stubs),
            "LOG": str(self.log),
            "FAIL_TIMES": str(fail_times),
            "PY_EXIT": str(py_exit),
            "RUNNER_TEMP": str(self.runner_temp),
            "TAG": "awesome-jev-mcp-v0.1.0",
        }
        # GitHub's default shell for a run: block is bash -e, without pipefail.
        done = subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-c", self.step()],
            env=env, capture_output=True, text=True, cwd=self.dir,
        )
        calls = self.log.read_text().splitlines() if self.log.exists() else []
        return done, calls

    def kinds(self, calls):
        return [c.split()[0] for c in calls]

    def test_installs_the_tagged_version_first_time(self):
        done, calls = self.run_step(fail_times=0)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.kinds(calls), ["pip", "python"])
        self.assertIn("awesome-jev-mcp==0.1.0", calls[0])
        self.assertIn("--no-cache-dir", calls[0])
        self.assertEqual(calls[1], "python - 0.1.0")

    def test_retries_while_the_index_catches_up(self):
        done, calls = self.run_step(fail_times=2)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.kinds(calls), ["pip", "sleep", "pip", "sleep", "pip", "python"])
        self.assertIn("sleep 30", calls)

    def test_gives_up_after_five_attempts(self):
        done, calls = self.run_step(fail_times=99)
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(self.kinds(calls).count("pip"), 5)
        self.assertEqual(self.kinds(calls).count("sleep"), 4)
        self.assertIn("::error", done.stdout)

    def test_a_broken_release_fails_at_once_rather_than_retrying(self):
        done, calls = self.run_step(fail_times=0, py_exit=1)
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(self.kinds(calls), ["pip", "python"])

    def test_the_check_it_runs_reads_the_installed_version(self):
        step = self.step()
        self.assertIn("from awesome_jev_mcp import data", step)
        self.assertIn("data._read_dir(data.BUNDLED)", step)
        self.assertIn('importlib.metadata.version("awesome-jev-mcp")', step)


if __name__ == "__main__":
    unittest.main()
