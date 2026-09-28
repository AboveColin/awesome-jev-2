#!/usr/bin/env python3
"""An MCP server over the awesome-jev catalogue.

A catalogue about how agents make decisions that only humans can read is a
strange artefact. This exposes it to the agents themselves: an assistant about
to wire Jev into something can ask for examples of the exact decision it is
making, on the platform it is using, in the language it is writing.

Three design choices worth knowing:

* **Caveats are never optional.** Every result carries its flags. The point of
  this catalogue is that `not-jev`, `shadow-mode-only` and `vendor-reported`
  travel with the row; an agent that got a recommendation without them would be
  worse informed than one that read the README.
* **Results are trimmed by default.** An agent pays for every token of a tool
  result, so `search_examples` returns compact rows and `get_example` returns
  the whole thing when one row actually matters.
* **The data's own provenance is a caveat too.** Installed as a package there is
  no repository around this file, so the catalogue is fetched and cached. Every
  result therefore carries a `data` line naming which layer answered and how
  current it is, and anything stale says so in capitals. See `data.py` for the
  ladder; the short version is that a checkout beats the network, the network
  beats the cache, and the snapshot in the wheel is the last resort rather than
  the default.

Unlike the rest of this repository, this file has a dependency. Hand-rolling
stdio JSON-RPC would keep the zero-dependency streak, but a subtly broken MCP
server is worse than a dependency. The dependency stops at this file: it
registers the tools and stamps where the data came from, and what each tool
answers is `query.py`, standard library only like `data.py`. The catalogue's
own CI tests those two directly and imports this module only in tests that
stub `mcp` out — the dependency-free build pipeline is untouched.

Run:
    pip install awesome-jev-mcp
    awesome-jev-mcp

If pip finds no such package, install the same server from the repository:
    pip install git+https://github.com/kydlikebtc/awesome-jev

From a checkout, `python3 -m awesome_jev_mcp` does the same thing and serves the
working tree rather than the published catalogue.
"""

from __future__ import annotations

import functools
import importlib.metadata

from typing import Any, Literal

from mcp.server import MCPServer

from .data import load
from .query import (
    compat_lookup,
    find_example,
    model_string_check,
    pattern_counts,
    search,
)

# Also read on this module by name (tests, and anyone who imported them from
# here before they moved to query.py).
from .query import DISQUALIFYING, accepted as _accepted, compact as _compact  # noqa: F401

CATALOG, COMPAT, PATTERNS, PROVENANCE = load()


def _version() -> str:
    """The installed version, reported to clients in serverInfo.

    Empty by default, which leaves anyone debugging a client unable to tell
    which build answered. Running straight from source has no installed
    metadata, and says so rather than guessing.
    """
    try:
        return importlib.metadata.version("awesome-jev-mcp")
    except importlib.metadata.PackageNotFoundError:
        return "0+source"


mcp = MCPServer(
    "awesome-jev",
    version=_version(),
    website_url="https://github.com/kydlikebtc/awesome-jev",
)


def tool(fn):
    """Register an MCP tool whose result always names where the data came from.

    Stamping at the decorator rather than at each `return` is deliberate: these
    functions have a dozen exits between them, several of them error paths, and
    the error paths are exactly where a reader most needs to know whether they
    are looking at a stale catalogue. One forgotten return would be invisible.

    The stamp goes on every result, not only degraded ones. A field that appears
    only when something is wrong trains readers to skim past it, and it leaves
    "nothing is wrong" indistinguishable from "the warning got lost".
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = fn(*args, **kwargs)
        return (
            {**result, "data": PROVENANCE.line()}
            if isinstance(result, dict)
            else result
        )

    return mcp.tool()(wrapper)


@tool
def search_examples(
    pattern: str = "",
    kind: str = "",
    language: str = "",
    question_type: Literal["", "choice", "score", "noul"] = "",
    platform: str = "",
    query: str = "",
    official_only: bool = False,
    with_code_only: bool = False,
    include_non_jev: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """Find catalogued examples of using Jev, filtered by what they do.

    The primary axis is `pattern` — the decision being made, such as
    tool-selection or safety-gating. Call list_patterns() for the taxonomy.

    By default this excludes rows flagged `not-jev` (independent
    reimplementations that never call the API) and `shadow-mode-only` (wired in
    but deliberately inert), because neither answers "how do I do this". Pass
    include_non_jev=True to see them.

    Args:
        pattern: a decision pattern key, e.g. "safety-gating"
        kind: resource form, e.g. "project", "official-docs", "benchmark"
        language: e.g. "python", "typescript", "rust"
        question_type: restrict to examples a person read calling this
            primitive (question_types); a script's text signal
            (primitives_seen) never matches
        platform: e.g. "cloudflare-workers-ai", "langchain", "typesafe-api"
        query: free text matched against title, summary, notes and platforms
        official_only: only material published by TypeSafe AI
        with_code_only: only rows whose link contains adaptable code
        include_non_jev: include reimplementations and shadow-mode rows
        limit: maximum rows to return, 1-50
    """
    return search(
        CATALOG,
        PATTERNS,
        pattern=pattern,
        kind=kind,
        language=language,
        question_type=question_type,
        platform=platform,
        query=query,
        official_only=official_only,
        with_code_only=with_code_only,
        include_non_jev=include_non_jev,
        limit=limit,
    )


@tool
def get_example(slug: str) -> dict[str, Any]:
    """Return one catalogue row in full, including its sources and evidence.

    `evidence` names the file the row's code was read in; a scheduled job
    re-reads it weekly, so the claim is checkable rather than asserted.
    `evidence.kind` says what that file shows: `call-site` (the default when
    absent) is where the project calls Jev; `wire-shape` is a file that speaks
    Jev's request shape rather than building on Jev (every `alternative` row,
    whether it serves that shape or sends Jev the same request to compare, and
    adapters backed by other models); and `example-only` is an example the
    project ships, not its own integration.

    `summary_source` says whose words `summary` is: `upstream-description` is
    the project's own GitHub description, word for word when the weekly
    refresh last compared them; `upstream-description-stale` was taken from it
    and no longer matches; `curated` was written for this catalogue. Absent
    means it is not recorded. search_examples() carries it too.

    `sources` says where the row came from. After the sources a person wrote,
    each item shaped `{"catalog": "owner/name", "url":
    "https://github.com/owner/name"}` is a sibling-list citation: that other
    Jev directory's README linked the row's repository when the weekly refresh
    last read it. The directories copy from each other, so how many cite a row
    says how widely it is mentioned, not that anyone checked it.

    `patterns_reviewed` is the date a person read the row against the decision
    patterns; search_examples() carries it too. Absent means no such reading
    is recorded: many rows' patterns are what keyword rules suggested from the
    project's description, and `overview` is what those rules give when nothing
    matches, so a project or plugin with code filed only under `overview` and
    no `patterns_reviewed` is not yet indexed by pattern rather than a survey.

    `repo_created_at`, `repo_pushed_at` and `repo_commits` are GitHub's own
    facts about the linked repository as the weekly refresh last read them:
    when it was created and last pushed to (UTC) and how many commits its
    default branch has; search_examples() carries them too. They are not a
    judgement: an old push does not mean abandoned, and nothing here says
    whether a project is maintained. Wherever `repo_commits` is recorded, the
    `single-commit` caveat is set exactly when it is 1. Absent on rows without
    a GitHub repository.

    `question_types` lists the primitives a person read the code calling.
    `primitives_seen` is something else: a weekly script's text signal that the
    one file `evidence` cites contains those primitives' request or answer
    shape (`"type": "choice"`, `Noul(`, `.noul`). A shape in a file is not a
    call, nobody read it, and search_examples(question_type=...) never matches
    on it.

    Args:
        slug: the row's stable id, as returned by search_examples
    """
    return find_example(CATALOG, slug)


@tool
def list_patterns() -> dict[str, Any]:
    """The decision-pattern taxonomy, with how many examples exist for each.

    A pattern with zero examples is a genuine gap in the ecosystem, not a
    missing row — worth knowing before concluding nobody does something.
    """
    return pattern_counts(CATALOG, PATTERNS)


@tool
def compatibility(surface: str = "") -> dict[str, Any]:
    """How reaching Jev differs per platform: model string, field names, endpoint.

    There is no portable model string, and the yes/no primitive is spelled
    `noul` everywhere except one SDK that calls it `boolean`. Check this before
    porting code between gateways — it is not a URL swap.

    Args:
        surface: filter to one platform by name fragment, e.g. "cloudflare"
    """
    return compat_lookup(COMPAT, surface)


@tool
def check_model_string(model: str) -> dict[str, Any]:
    """Check whether a Jev model string is real, and which surface it belongs to.

    Exists because `typesafe/jev-1` is the most repeated fabrication about this
    model — it appears in no documentation, and an agent about to write it into
    someone's code should be told before the request fails.

    Args:
        model: the string you are about to send, e.g. "typesafe-ai/jev"
    """
    return model_string_check(COMPAT, model)


if __name__ == "__main__":
    mcp.run()
