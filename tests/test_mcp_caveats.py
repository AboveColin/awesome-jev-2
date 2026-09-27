"""The MCP server reports self-submitted as a caveat and never filters on it.

`mcp` itself is not installed in CI (scripts/ and tests/ are standard-library
only), so the one class the server imports from it is stubbed. The catalogue is
read from this checkout through AWESOME_JEV_CATALOG, so nothing reaches the
network.
"""

from __future__ import annotations

import importlib
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


class _StubServer:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self):
        return lambda fn: fn


def load_server():
    mcp = types.ModuleType("mcp")
    mcp_server = types.ModuleType("mcp.server")
    mcp_server.MCPServer = _StubServer
    mcp.server = mcp_server
    stale = {name: None for name in sys.modules if name.startswith("awesome_jev_mcp")}
    with patch.dict(sys.modules, {"mcp": mcp, "mcp.server": mcp_server}), patch.dict(
        os.environ, {"AWESOME_JEV_CATALOG": str(ROOT)}
    ), patch.object(sys, "path", [str(ROOT / "src"), *sys.path]):
        for name in stale:
            sys.modules.pop(name, None)
        return importlib.import_module("awesome_jev_mcp.server")


class SelfSubmittedCaveatTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = load_server()
        cls.flagged = sorted(
            e["slug"] for e in cls.server.CATALOG if "self-submitted" in (e.get("flags") or [])
        )

    def test_the_flag_is_a_caveat_not_a_disqualifier(self):
        self.assertNotIn("self-submitted", self.server.DISQUALIFYING)

    def test_self_submitted_rows_are_returned_with_the_caveat(self):
        self.assertTrue(self.flagged, "expected at least one self-submitted row in the catalogue")
        for slug in self.flagged:
            with self.subTest(slug=slug):
                # Default filters, so a row dropped as "not an example" would be missing.
                result = self.server.search_examples(query=slug, limit=50)
                by_slug = {row["slug"]: row for row in result["results"]}
                self.assertIn(slug, by_slug, "a self-submitted row was filtered out")
                self.assertIn("self-submitted", by_slug[slug]["caveats"])

    def test_get_example_carries_the_flag(self):
        row = self.server.get_example(self.flagged[0])
        self.assertIn("self-submitted", row["flags"])


class EvidenceKindTest(unittest.TestCase):
    """evidence.kind reaches an agent untouched (I18): get_example returns the row."""

    @classmethod
    def setUpClass(cls):
        cls.server = load_server()

    def test_an_alternatives_citation_says_it_is_not_a_call_site(self):
        slug = next(e["slug"] for e in self.server.CATALOG if e["kind"] == "alternative" and e.get("evidence"))
        self.assertEqual(self.server.get_example(slug)["evidence"]["kind"], "wire-shape")

    def test_the_tool_description_explains_the_field(self):
        doc = self.server.get_example.__doc__
        for kind in ("call-site", "wire-shape", "example-only"):
            self.assertIn(f"`{kind}`", doc)


if __name__ == "__main__":
    unittest.main()
