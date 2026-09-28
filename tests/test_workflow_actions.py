"""Every action the workflows use runs on Node 24, and stays current (I12).

GitHub deprecated the Node 20 runtime for actions (github.blog, 2025-09-19):
every run of lint, pages and publish ended in a warning that it was forcing
checkout@v4, setup-python@v5 and the rest onto Node 24, the step before
refusing to run them. The workflows now reference each action's first major
that declares `runs.using: node24` (or is a composite whose steps do) or a
later one, and .github/dependabot.yml proposes each new major as a weekly pull
request that a person merges.

The floors below were read from each action's own action.yml at that tag
(`gh api repos/<action>/contents/action.yml?ref=<tag>`) on 2026-09-27; the
major before each floor declares node20. An action not in the table fails the
test, so a new one gets looked up before it lands rather than after its
runtime is retired. No network here.
"""

from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

# First major whose action.yml runs on Node 24. upload-pages-artifact is a
# composite; its v4 wraps upload-artifact v4.6.2 (node20), its v5 wraps v7.
# pypa/gh-action-pypi-publish is a composite (its setup-python step is v6.2.0,
# node24) published under the moving `release/v1` branch its README's examples use.
NODE24_FLOOR = {
    "actions/checkout": 5,
    "actions/setup-python": 6,
    "actions/setup-node": 5,
    "actions/cache": 5,
    "actions/upload-artifact": 6,
    "actions/download-artifact": 7,
    "actions/configure-pages": 6,
    "actions/upload-pages-artifact": 5,
    "actions/deploy-pages": 5,
    "pypa/gh-action-pypi-publish": 1,
}

USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)", re.MULTILINE)
# The repository's style: a major tag (or pypa's release/vN branch), which
# Dependabot moves forward. Not a commit SHA, not a minor, not a branch name.
MAJOR_REF = re.compile(r"^([\w.-]+/[\w.-]+)@(?:release/)?v(\d+)$")


def uses() -> list[tuple[str, str]]:
    found = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for ref in USES.findall(path.read_text()):
            found.append((path.name, ref))
    return found


class ActionRuntimeTest(unittest.TestCase):
    def test_workflows_use_actions(self):
        self.assertGreater(len(uses()), 10)

    def test_every_action_is_referenced_by_its_major_tag(self):
        for workflow, ref in uses():
            with self.subTest(workflow=workflow, ref=ref):
                self.assertRegex(ref, MAJOR_REF)

    def test_no_action_runs_on_node_20(self):
        for workflow, ref in uses():
            match = MAJOR_REF.match(ref)
            if not match:
                continue  # reported by the test above
            action, major = match.group(1), int(match.group(2))
            with self.subTest(workflow=workflow, ref=ref):
                self.assertIn(
                    action, NODE24_FLOOR,
                    f"{action} is new: read its action.yml at the tag you use and add "
                    "its first node24 (or composite) major to NODE24_FLOOR",
                )
                self.assertGreaterEqual(major, NODE24_FLOOR[action], f"{ref} runs on Node 20")


class DependabotTest(unittest.TestCase):
    def test_actions_are_proposed_weekly_as_pull_requests(self):
        path = ROOT / ".github" / "dependabot.yml"
        self.assertTrue(path.exists(), "no .github/dependabot.yml")
        text = path.read_text()
        self.assertIn("version: 2\n", text)
        self.assertRegex(text, r'package-ecosystem:\s*"github-actions"')
        self.assertRegex(text, r'directory:\s*"/"')
        self.assertRegex(text, r'interval:\s*"weekly"')
        # Pull requests only: nothing here merges them.
        self.assertNotIn("auto-merge", text)
        for workflow in WORKFLOWS.glob("*.yml"):
            self.assertNotIn("dependabot/fetch-metadata", workflow.read_text())


class ArtifactHandoffTest(unittest.TestCase):
    """What a major bump of an artifact action could silently break."""

    def step_with(self, text: str, action: str) -> dict[str, str]:
        block = text.split(f"uses: {action}@", 1)[1].split("\n      - ", 1)[0]
        return dict(re.findall(r"^\s{10}([\w-]+):\s*(.+?)\s*$", block, re.MULTILINE))

    def test_publish_downloads_the_artifact_build_uploaded(self):
        text = (WORKFLOWS / "publish.yml").read_text()
        up = self.step_with(text, "actions/upload-artifact")
        down = self.step_with(text, "actions/download-artifact")
        self.assertEqual(up["name"], down["name"])
        self.assertEqual(up["path"], "dist/")
        self.assertEqual(down["path"], "dist/")

    def test_pages_keeps_the_dotfile_assemble_site_writes(self):
        # upload-pages-artifact v4 and later drop dotfiles unless told not to,
        # and assemble_site.py writes site/.nojekyll. The deploy is from an
        # artifact, so Jekyll never runs either way; keeping it keeps the
        # artifact what it was under v3.
        self.assertIn('".nojekyll"', (ROOT / "scripts" / "assemble_site.py").read_text())
        text = (WORKFLOWS / "pages.yml").read_text()
        step = self.step_with(text, "actions/upload-pages-artifact")
        self.assertEqual(step.get("path"), "site")
        self.assertEqual(step.get("include-hidden-files"), "true")
        # The deploy job reads the artifact under upload-pages-artifact's
        # default name, and needs these two permissions to publish it.
        self.assertNotIn("artifact_name", text)
        self.assertIn("  pages: write\n  id-token: write\n", text)


if __name__ == "__main__":
    unittest.main()
