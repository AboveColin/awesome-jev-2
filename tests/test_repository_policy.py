"""Which pull requests run what, and how changes are meant to land (I06).

The repository settings behind this (fork-PR approval, auto-merge, a ruleset on
main) are the maintainer's to change and are not in git. What is in git: the
package build runs only for pull requests that touch the package, and the
contributor guide says how changes reach main.
"""

from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PublishTriggerTest(unittest.TestCase):
    def test_package_build_runs_only_for_package_changes(self):
        text = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        on = text.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
        paths = on.split("  pull_request:\n    paths:\n", 1)[1]
        listed = [line.strip().strip('- "') for line in paths.splitlines() if line.strip()]
        self.assertEqual(listed, ["src/**", "pyproject.toml", ".github/workflows/publish.yml"])
        # Releases are still tag-driven.
        self.assertIn('  push:\n    tags:\n      - "awesome-jev-mcp-v*"\n', on)


class LandingGuideTest(unittest.TestCase):
    def test_contributing_says_how_changes_reach_main(self):
        text = (ROOT / "CONTRIBUTING.md").read_text()
        section = text.split("## How changes reach `main`\n", 1)[1].split("\n## ", 1)[0]
        for phrase in ("`claude/*`", "`codex/*`", "pull request", "**Approve and run**", "force-push"):
            self.assertIn(phrase, section)


if __name__ == "__main__":
    unittest.main()
