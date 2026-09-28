"""Which pull requests run what, and how changes are meant to land (I06).

The repository settings behind this (fork-PR approval, auto-merge, a ruleset on
main) are the maintainer's to change and are not in git. What is in git: the
package build runs only for pull requests that touch the package, and the
contributor guide says how changes reach main.
"""

from __future__ import annotations

import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from test_mcp_caveats import load_server  # noqa: E402


class PublishTriggerTest(unittest.TestCase):
    def test_package_build_runs_only_for_package_changes(self):
        text = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        on = text.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
        paths = on.split("  pull_request:\n    paths:\n", 1)[1]
        listed = [line.strip().strip('- "') for line in paths.splitlines() if line.strip()]
        self.assertEqual(listed, ["src/**", "pyproject.toml", ".github/workflows/publish.yml"])
        # Releases are still tag-driven.
        self.assertIn('  push:\n    tags:\n      - "awesome-jev-mcp-v*"\n', on)


class ModelStringCheckTest(unittest.TestCase):
    """publish.yml's one data-dependent smoke assertion, made on every pull
    request. publish.yml no longer runs for a pull request that changes only
    compat.json, so without this a compat.json edit that let the fabricated
    `typesafe/jev-1` through would first be caught by a release tag."""

    def test_the_fabricated_model_string_is_rejected_and_real_ones_are_not(self):
        server = load_server()
        self.assertIs(server.check_model_string(model="typesafe/jev-1")["valid"], False)
        # A parenthetical is a remark about the string, not part of it
        # (`jev-latest (default)`), as lint_docs.py reads the cell too.
        real = [
            re.sub(r"\s*\(.*\)$", "", part.strip())
            for platform in server.COMPAT["platforms"]
            for part in platform["model"].split("·")
            if part.strip() not in ("—", "")
        ]
        self.assertTrue(real, "compat.json lists no model string")
        for model in real:
            with self.subTest(model=model):
                self.assertIs(server.check_model_string(model=model)["valid"], True)

    def test_publish_yml_still_makes_the_same_assertion(self):
        text = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        self.assertIn('server.check_model_string(model="typesafe/jev-1")["valid"] is False', text)


class LandingGuideTest(unittest.TestCase):
    def test_contributing_says_how_changes_reach_main(self):
        text = (ROOT / "CONTRIBUTING.md").read_text()
        section = text.split("## How changes reach `main`\n", 1)[1].split("\n## ", 1)[0]
        for phrase in ("`claude/*`", "`codex/*`", "pull request", "**Approve and run**", "force-push"):
            self.assertIn(phrase, section)


if __name__ == "__main__":
    unittest.main()
