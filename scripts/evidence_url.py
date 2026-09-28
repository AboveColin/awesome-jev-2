"""The link to the file a row's `evidence` cites: the rule in
src/awesome_jev_mcp/evidence_url.py, loaded by its path.

The rule moved into the MCP package on 2026-09-28 (I35): the server's
wire_pattern prompt links cited files too, and an installed server has no
scripts/ to import from. Loaded by path rather than imported, as site_api.py
loads query.py, so scripts/ never imports the package itself. The generated
pages, the review queue and the tests import `evidence_url` from here as
before; that file documents the rule.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

SOURCE = pathlib.Path(__file__).resolve().parent.parent / "src" / "awesome_jev_mcp" / "evidence_url.py"


def _load():
    name = "awesome_jev_evidence_url"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, SOURCE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


_rule = _load()
GITHUB_HOST = _rule.GITHUB_HOST
repository = _rule.repository
evidence_url = _rule.evidence_url
