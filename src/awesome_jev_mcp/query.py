"""What the MCP server's tools answer, as plain functions over the data they
are handed.

server.py registers the tools and stamps every result with where the data came
from; everything a tool decides is here — which rows count as examples, which
caveats travel with a row, the order results come in, whether a model string is
real. Standard library only and no module state: each function takes the
catalogue, the taxonomy or compat.json as an argument. That is what lets the
repository's CI, which installs nothing, test the answers on a handful of rows
(tests/test_mcp_query.py) without `mcp` and without the network.
"""

from __future__ import annotations

import re
from typing import Any

# Flags that change whether a row is an example at all, as opposed to a caveat
# about its quality. An agent looking for "how do I do X" should not be handed
# a reimplementation that never calls the API. `self-submitted` is deliberately
# not here: it discloses who proposed a row, says nothing about whether the row
# is an example, and reaches the agent in `caveats` like every other flag.
DISQUALIFYING = {"not-jev", "shadow-mode-only"}

# The most rows one search returns, whatever `limit` asks for: an agent pays
# for every token of a tool result.
MAX_LIMIT = 50

SEARCH_NOTE = (
    "Rows report what a person read at the source. Nothing here has been "
    "executed; performance figures in this space are mostly vendor-reported."
)

PATTERNS_NOTE = (
    "docs/patterns.md gives each pattern an explicit 'when NOT to use this'. "
    "For safety-gating in particular: a probabilistic gate is defence in depth, "
    "never a security boundary."
)

NOUL_WARNING = (
    "`noul` answers carry no confidence field on any surface — the probability "
    "is the answer. A helper reading .confidence uniformly returns nothing for "
    "a third of your questions."
)


def compact(entry: dict) -> dict[str, Any]:
    """The fields worth spending tokens on in a list of results."""
    out: dict[str, Any] = {
        "slug": entry["slug"],
        "title": entry["title"],
        "url": entry["url"],
        "summary": entry["summary"],
        "kind": entry["kind"],
        "patterns": entry["patterns"],
    }
    # Whose words the summary is travels with it, like the caveats: an agent
    # quoting an `upstream-description` summary is quoting the project itself.
    if entry.get("summary_source"):
        out["summary_source"] = entry["summary_source"]
    # How far to trust `patterns`: the date a person read the row against them.
    # Absent means no reading is recorded, and an `overview` project or plugin
    # with code then means "not yet indexed by pattern", not "surveys the space".
    if entry.get("patterns_reviewed"):
        out["patterns_reviewed"] = entry["patterns_reviewed"]
    # GitHub's facts about the repository, as the weekly refresh last read
    # them: an agent judging upkeep gets the dates, not a verdict.
    for key in (
        "question_types", "languages", "platforms", "stars", "repo_license",
        "repo_created_at", "repo_pushed_at", "repo_commits",
    ):
        if entry.get(key) is not None:
            out[key] = entry[key]
    if entry.get("official"):
        out["official"] = True
    # Always: caveats are never optional (see server.py's docstring).
    if entry.get("flags"):
        out["caveats"] = entry["flags"]
    if entry.get("notes"):
        out["note"] = entry["notes"]
    return out


def _haystack(entry: dict) -> str:
    """What a free-text query is matched against."""
    return " ".join(
        str(x)
        for x in (
            entry["title"],
            entry["summary"],
            entry.get("notes", ""),
            entry["slug"],
            " ".join(entry.get("platforms") or []),
        )
    ).lower()


def sort_key(entry: dict) -> tuple:
    """Official first, then rows with code, then popularity — the README's
    order, so a reader and an agent see much the same thing first. The README
    compares stars by band (★10+, ★100+, …) and then goes by title; here the
    exact count decides, as on the site. Slug last, as in the README, so rows
    that tie on everything else (forks sharing a title and star count) do not
    fall back to their position in the file."""
    return (
        not entry.get("official", False),
        not entry.get("has_code", False),
        -(entry.get("stars") or 0),
        entry["title"].lower(),
        entry["slug"],
    )


def search(
    rows: list[dict],
    patterns: list[dict],
    *,
    pattern: str = "",
    kind: str = "",
    language: str = "",
    question_type: str = "",
    platform: str = "",
    query: str = "",
    official_only: bool = False,
    with_code_only: bool = False,
    include_non_jev: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """search_examples' answer: `rows` filtered, ordered by sort_key() and cut
    to `limit` (clamped to 1..MAX_LIMIT), each as compact() shapes it. An
    unknown `pattern` answers with the valid keys instead."""
    limit = max(1, min(int(limit), MAX_LIMIT))

    if pattern:
        keys = {p["key"] for p in patterns}
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
        # question_types is what a person read the code calling; the weekly
        # script's text signal (primitives_seen) never matches here.
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
        rows = [e for e in rows if all(t in _haystack(e) for t in terms)]

    rows = sorted(rows, key=sort_key)
    return {
        "total_matching": len(rows),
        "returned": min(len(rows), limit),
        "results": [compact(e) for e in rows[:limit]],
        "note": SEARCH_NOTE,
    }


def find_example(rows: list[dict], slug: str) -> dict[str, Any]:
    """get_example's answer: the row itself, or up to five slugs containing
    the one asked for."""
    for entry in rows:
        if entry["slug"] == slug:
            return entry
    # Sorted rather than taken in file order: the copy that answered may be a
    # checkout mid-edit or an AWESOME_JEV_CATALOG directory, not the sorted file.
    close = sorted(e["slug"] for e in rows if slug.lower() in e["slug"].lower())[:5]
    return {
        "error": f"no entry with slug {slug!r}",
        "did_you_mean": close or None,
        "hint": "use search_examples() to find a slug",
    }


def pattern_counts(rows: list[dict], patterns: list[dict]) -> dict[str, Any]:
    """list_patterns' answer: the taxonomy in its own order, each pattern with
    how many rows file under it (every row, caveats or not)."""
    counts: dict[str, int] = {}
    for entry in rows:
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
            for p in patterns
        ],
        "note": PATTERNS_NOTE,
    }


def compat_lookup(compat: dict, surface: str = "") -> dict[str, Any]:
    """compatibility's answer: compat.json's platforms, or those whose name
    contains `surface` (ignoring case)."""
    rows = compat["platforms"]
    if surface:
        rows = [p for p in rows if surface.lower() in p["name"].lower()]
        if not rows:
            return {
                "error": f"no surface matching {surface!r}",
                "known_surfaces": [p["name"] for p in compat["platforms"]],
            }
    return {
        "as_of": compat["as_of"],
        "surfaces": rows,
        "limits": compat["limits"],
        "warning": NOUL_WARNING,
    }


def accepted(platform: dict) -> list[str]:
    """The individual strings a surface accepts, from its `·`-joined cell. A
    parenthetical is a remark about the string (`jev-latest (default)`), not
    part of it; scripts/lint_docs.py reads the cell the same way."""
    return [
        re.sub(r"\s*\(.*\)$", "", part.strip())
        for part in platform["model"].split("·")
        if part.strip() not in ("—", "")
    ]


def model_hint(compat: dict) -> str:
    """What to send instead, built from compat.json and nothing else, so a
    release changes compat.json alone. Until 2026-09-27 this was a sentence
    with the versioned ids typed in, which nothing checked."""
    official = [p for p in compat["platforms"] if p.get("official")]
    own = [m for p in official for m in accepted(p)]
    versioned = [m for m in own if re.search(r"\d\.\d", m)]
    aliases = [m for m in own if m not in versioned]
    parts = []
    if versioned:
        tail = f", with aliases {' and '.join(aliases)}" if aliases else ""
        parts.append(f"The versioned id is {' and '.join(versioned)}{tail}.")
    # Surfaces that take the same strings are named together, in compat.json's order.
    renamed: dict[tuple[str, ...], list[str]] = {}
    for platform in compat["platforms"]:
        theirs = tuple(m for m in accepted(platform) if m not in own)
        if theirs:
            renamed.setdefault(theirs, []).append(platform["name"])
    if renamed:
        parts.append(
            "Gateways and SDKs rename it: "
            + "; ".join(f"{' or '.join(ms)} on {' and '.join(names)}" for ms, names in renamed.items())
            + "."
        )
    parts += [f"`{item['s']}`: {item['why']}" for item in compat.get("not_model_strings", [])]
    parts.append("Pin a version rather than an alias once you have tuned any threshold.")
    return " ".join(parts)


def model_string_check(compat: dict, model: str) -> dict[str, Any]:
    """check_model_string's answer: the surfaces that accept `model` exactly,
    or why it is not valid, what it nearly matches and what to send instead."""
    needle = model.strip()

    # Exact match, deliberately. A substring test reports `typesafe/jev-1` as
    # valid because it is a prefix of OpenRouter's versioned string — and
    # catching that exact fabrication is the only reason this tool exists.
    hits = [
        {
            "surface": p["name"],
            "accepts": accepted(p),
            "endpoint": p["endpoint"],
            "env": p["env"],
        }
        for p in compat["platforms"]
        if needle and needle in accepted(p)
    ]
    if hits:
        return {"model": needle, "valid": True, "surfaces": hits}

    every = sorted({m for p in compat["platforms"] for m in accepted(p)})
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
        "hint": model_hint(compat),
    }
