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
server is worse than a dependency, and the catalogue's own CI imports this
module only in tests that stub `mcp` out — the dependency-free build pipeline
is untouched.

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


# Flags that change whether a row is an example at all, as opposed to a caveat
# about its quality. An agent looking for "how do I do X" should not be handed
# a reimplementation that never calls the API. `self-submitted` is deliberately
# not here: it discloses who proposed a row, says nothing about whether the row
# is an example, and reaches the agent in `caveats` like every other flag.
DISQUALIFYING = {"not-jev", "shadow-mode-only"}


def _compact(entry: dict) -> dict[str, Any]:
    """The fields worth spending tokens on in a list of results."""
    out: dict[str, Any] = {
        "slug": entry["slug"],
        "title": entry["title"],
        "url": entry["url"],
        "summary": entry["summary"],
        "kind": entry["kind"],
        "patterns": entry["patterns"],
    }
    for key in ("question_types", "languages", "platforms", "stars", "repo_license"):
        if entry.get(key) is not None:
            out[key] = entry[key]
    if entry.get("official"):
        out["official"] = True
    # Always. See the module docstring.
    if entry.get("flags"):
        out["caveats"] = entry["flags"]
    if entry.get("notes"):
        out["note"] = entry["notes"]
    return out


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
        question_type: restrict to examples calling this primitive
        platform: e.g. "cloudflare-workers-ai", "langchain", "typesafe-api"
        query: free text matched against title, summary, notes and platforms
        official_only: only material published by TypeSafe AI
        with_code_only: only rows whose link contains adaptable code
        include_non_jev: include reimplementations and shadow-mode rows
        limit: maximum rows to return, 1-50
    """
    limit = max(1, min(int(limit), 50))
    rows = CATALOG

    if pattern:
        keys = {p["key"] for p in PATTERNS}
        if pattern not in keys:
            return {
                "error": f"unknown pattern {pattern!r}",
                "valid_patterns": sorted(keys),
                "hint": "call list_patterns() for what each one means",
            }
        rows = [e for e in rows if pattern in e["patterns"]]
    if kind:
        rows = [e for e in rows if e["kind"] == kind]
    if language:
        rows = [e for e in rows if language in (e.get("languages") or [])]
    if question_type:
        rows = [e for e in rows if question_type in (e.get("question_types") or [])]
    if platform:
        rows = [
            e
            for e in rows
            if any(platform.lower() in p.lower() for p in (e.get("platforms") or []))
        ]
    if official_only:
        rows = [e for e in rows if e.get("official")]
    if with_code_only:
        rows = [e for e in rows if e.get("has_code")]
    if not include_non_jev:
        rows = [e for e in rows if not DISQUALIFYING & set(e.get("flags") or [])]
    if query:
        terms = query.lower().split()

        def hay(e: dict) -> str:
            return " ".join(
                str(x)
                for x in (
                    e["title"],
                    e["summary"],
                    e.get("notes", ""),
                    e["slug"],
                    " ".join(e.get("platforms") or []),
                )
            ).lower()

        rows = [e for e in rows if all(t in hay(e) for t in terms)]

    # Official first, then rows with code, then popularity — the README's order,
    # so a reader and an agent see much the same thing first. The README compares
    # stars by band (★10+, ★100+, …) and then goes by title; here the exact count
    # decides, as on the site. Slug last, as in the README, so rows that tie on
    # everything else (forks sharing a title and star count) do not fall back to
    # their position in the file.
    rows = sorted(
        rows,
        key=lambda e: (
            not e.get("official", False),
            not e.get("has_code", False),
            -(e.get("stars") or 0),
            e["title"].lower(),
            e["slug"],
        ),
    )
    return {
        "total_matching": len(rows),
        "returned": min(len(rows), limit),
        "results": [_compact(e) for e in rows[:limit]],
        "note": (
            "Rows report what a person read at the source. Nothing here has been "
            "executed; performance figures in this space are mostly vendor-reported."
        ),
    }


@tool
def get_example(slug: str) -> dict[str, Any]:
    """Return one catalogue row in full, including its sources and evidence.

    `evidence` names the file a primitive claim was read in; a scheduled job
    re-reads it weekly, so the claim is checkable rather than asserted.

    Args:
        slug: the row's stable id, as returned by search_examples
    """
    for entry in CATALOG:
        if entry["slug"] == slug:
            return entry
    # Sorted rather than taken in file order: the copy that answered may be a
    # checkout mid-edit or an AWESOME_JEV_CATALOG directory, not the sorted file.
    close = sorted(e["slug"] for e in CATALOG if slug.lower() in e["slug"].lower())[:5]
    return {
        "error": f"no entry with slug {slug!r}",
        "did_you_mean": close or None,
        "hint": "use search_examples() to find a slug",
    }


@tool
def list_patterns() -> dict[str, Any]:
    """The decision-pattern taxonomy, with how many examples exist for each.

    A pattern with zero examples is a genuine gap in the ecosystem, not a
    missing row — worth knowing before concluding nobody does something.
    """
    counts: dict[str, int] = {}
    for entry in CATALOG:
        for key in entry["patterns"]:
            counts[key] = counts.get(key, 0) + 1
    return {
        "patterns": [
            {
                "key": p["key"],
                "name": p["en"],
                "description": p["blurb_en"],
                "examples": counts.get(p["key"], 0),
            }
            for p in PATTERNS
        ],
        "note": (
            "docs/patterns.md gives each pattern an explicit 'when NOT to use this'. "
            "For safety-gating in particular: a probabilistic gate is defence in depth, "
            "never a security boundary."
        ),
    }


@tool
def compatibility(surface: str = "") -> dict[str, Any]:
    """How reaching Jev differs per platform: model string, field names, endpoint.

    There is no portable model string, and the yes/no primitive is spelled
    `noul` everywhere except one SDK that calls it `boolean`. Check this before
    porting code between gateways — it is not a URL swap.

    Args:
        surface: filter to one platform by name fragment, e.g. "cloudflare"
    """
    rows = COMPAT["platforms"]
    if surface:
        rows = [p for p in rows if surface.lower() in p["name"].lower()]
        if not rows:
            return {
                "error": f"no surface matching {surface!r}",
                "known_surfaces": [p["name"] for p in COMPAT["platforms"]],
            }
    return {
        "as_of": COMPAT["as_of"],
        "surfaces": rows,
        "limits": COMPAT["limits"],
        "warning": (
            "`noul` answers carry no confidence field on any surface — the probability "
            "is the answer. A helper reading .confidence uniformly returns nothing for "
            "a third of your questions."
        ),
    }


@tool
def check_model_string(model: str) -> dict[str, Any]:
    """Check whether a Jev model string is real, and which surface it belongs to.

    Exists because `typesafe/jev-1` is the most repeated fabrication about this
    model — it appears in no documentation, and an agent about to write it into
    someone's code should be told before the request fails.

    Args:
        model: the string you are about to send, e.g. "typesafe-ai/jev"
    """
    needle = model.strip()

    def accepted(platform: dict) -> list[str]:
        """The individual strings a surface accepts, from its `·`-joined cell."""
        return [
            part.strip()
            for part in platform["model"].split("·")
            if part.strip() not in ("—", "")
        ]

    # Exact match, deliberately. A substring test reports `typesafe/jev-1` as
    # valid because it is a prefix of `typesafe/jev-1.13` — and catching that
    # exact fabrication is the only reason this tool exists.
    hits = [
        {
            "surface": p["name"],
            "accepts": accepted(p),
            "endpoint": p["endpoint"],
            "env": p["env"],
        }
        for p in COMPAT["platforms"]
        if needle and needle in accepted(p)
    ]
    if hits:
        return {"model": needle, "valid": True, "surfaces": hits}

    every = sorted({m for p in COMPAT["platforms"] for m in accepted(p)})
    # A near miss is the common case, so name it rather than just saying no.
    near = [
        m for m in every if needle and (m.startswith(needle) or needle.startswith(m))
    ]
    return {
        "model": needle,
        "valid": False,
        "reason": "matches no model string on any documented surface",
        "close_but_wrong": near or None,
        "valid_strings": every,
        "hint": (
            "The versioned id is jev-1.13.0, with aliases jev-latest and jev-preview. "
            "Gateways rename it: typesafe-ai/jev on Vercel, typesafe/jev on Cloudflare, "
            "typesafe/jev-1.13 on OpenRouter. `typesafe/jev-1` exists nowhere and is the "
            "most repeated fabrication about this model. Pin a version rather than an "
            "alias once you have tuned any threshold."
        ),
    }


if __name__ == "__main__":
    mcp.run()
