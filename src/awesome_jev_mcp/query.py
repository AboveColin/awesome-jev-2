"""What the MCP server's tools and resources answer, as plain functions over
the data they are handed.

server.py registers the tools and resources and stamps every result with where
the data came from; everything they decide is here — which rows count as
examples, which caveats travel with a row and what each one means, the order
results come in, whether a model string is real. Standard library only and no
module state: each function takes the catalogue, the taxonomy, the curated
collections or compat.json as an argument. That is what lets the
repository's CI, which installs nothing, test the answers on a handful of rows
(tests/test_mcp_query.py, tests/test_mcp_resources.py) without `mcp` and
without the network.
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

FLAGS_NOTE = (
    "What each caveat flag means. A row carries the keys (`caveats` in search results and "
    "resources, `flags` in get_example), and every answer holding flagged rows adds "
    "caveat_glossary: the English description of each flag among them. A row flagged with "
    "one of not_examples is not an example of deciding with Jev, and search_examples leaves "
    "it out by default. zh_machine marks Chinese a model wrote."
)

COLLECTIONS_NOTE = (
    "Curated entry points: editorial paths through the catalogue, each pick with why it is "
    "there (reason) and what to watch for (caution). A pick is editorial relevance, not a "
    "runtime certification; nothing here was executed."
)

# Where each pattern's "when NOT to use this" lives: docs/patterns.md, one
# `## <key>` section per pattern (scripts/lint_docs.py makes sure of it), so
# `#<key>` is the section's anchor on GitHub.
PATTERNS_DOC = "https://github.com/kydlikebtc/awesome-jev/blob/main/docs/patterns.md"

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


def caveat_glossary(flags: list[dict], seen) -> dict[str, str]:
    """{flag: its English description} for each flag in `seen` (an iterable of
    rows' flag lists), in taxonomy.json's order. `flags` is taxonomy.json's
    `flags`. The rows keep their bare keys; this says once what they mean."""
    present = {flag for group in seen for flag in group}
    return {f["key"]: f["blurb_en"] for f in flags if f["key"] in present}


def _with_glossary(answer: dict, flags: list[dict], seen) -> dict:
    """`answer` with caveat_glossary last, or unchanged when no flag is present."""
    glossary = caveat_glossary(flags, seen)
    return {**answer, "caveat_glossary": glossary} if glossary else answer


def when_not_to_use(key: str) -> str:
    """The docs/patterns.md section for pattern `key`, with its "when NOT to use"."""
    return f"{PATTERNS_DOC}#{key}"


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
    flags: list[dict] = (),
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
    to `limit` (clamped to 1..MAX_LIMIT), each as compact() shapes it, then the
    caveat_glossary of the flags those rows carry (`flags` is taxonomy.json's).
    An unknown `pattern` answers with the valid keys instead."""
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
    shown = rows[:limit]
    answer = {
        "total_matching": len(rows),
        "returned": len(shown),
        "results": [compact(e) for e in shown],
        "note": SEARCH_NOTE,
    }
    return _with_glossary(answer, flags, (e.get("flags") or [] for e in shown))


def find_example(rows: list[dict], slug: str, flags: list[dict] = ()) -> dict[str, Any]:
    """get_example's answer: the row itself, with the caveat_glossary of its
    flags after its own fields, or up to five slugs containing the one asked
    for."""
    for entry in rows:
        if entry["slug"] == slug:
            return _with_glossary(entry, flags, [entry.get("flags") or []])
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


def flag_list(taxonomy: dict) -> dict[str, Any]:
    """The awesome-jev://flags resource: taxonomy.json's flags as written there
    (key, English and Chinese label and description), in its order."""
    return {"flags": taxonomy["flags"], "not_examples": sorted(DISQUALIFYING), "note": FLAGS_NOTE}


def collection_uri(collection_id: str) -> str:
    return f"awesome-jev://collections/{collection_id}"


def collection_list(collections: list[dict]) -> dict[str, Any]:
    """The awesome-jev://collections resource: each curated path, how many rows
    it picks and the resource that lists them."""
    return {
        "collections": [
            {
                **{k: v for k, v in c.items() if k != "entries"},
                "entries": len(c["entries"]),
                "uri": collection_uri(c["id"]),
            }
            for c in collections
        ],
        "note": COLLECTIONS_NOTE,
    }


def collection_detail(
    collections: list[dict], rows: list[dict], flags: list[dict], collection_id: str
) -> dict[str, Any]:
    """The awesome-jev://collections/{id} resource: one curated path in its own
    order, each pick's reason and caution beside its row as compact() shapes
    it (None if the catalogue served lacks the row), then the caveat_glossary."""
    for c in collections:
        if c["id"] == collection_id:
            by_slug = {e["slug"]: e for e in rows}
            picked = [by_slug.get(item["slug"]) for item in c["entries"]]
            answer = {
                **{k: v for k, v in c.items() if k != "entries"},
                "entries": [
                    {**item, "row": compact(row) if row else None} for item, row in zip(c["entries"], picked)
                ],
                "note": COLLECTIONS_NOTE,
            }
            return _with_glossary(answer, flags, (row.get("flags") or [] for row in picked if row))
    return {
        "error": f"no collection {collection_id!r}",
        "valid_collections": [c["id"] for c in collections],
        "hint": "read awesome-jev://collections",
    }


def pattern_rows(rows: list[dict], key: str) -> list[dict]:
    """Every row filed under pattern `key`, caveated ones included, in sort_key()
    order and shaped by compact(): the rows of awesome-jev://patterns/{key} and
    of the site's api/v1/patterns/<key>.json alike."""
    return [compact(e) for e in sorted((e for e in rows if key in e["patterns"]), key=sort_key)]


def pattern_listing(rows: list[dict], patterns: list[dict], flags: list[dict], key: str) -> dict[str, Any]:
    """The awesome-jev://patterns/{key} resource: the pattern, where its "when
    NOT to use" is, and every row filed under it (pattern_rows()), then the
    caveat_glossary. Nothing is filtered, so the count is the catalogue's; rows
    whose caveats include one of not_examples are not examples of deciding
    with Jev. An unknown key answers with the valid ones."""
    for p in patterns:
        if p["key"] == key:
            entries = pattern_rows(rows, key)
            answer = {
                "pattern": key,
                "name": p["en"],
                "description": p["blurb_en"],
                "when_not_to_use": when_not_to_use(key),
                "examples": len(entries),
                "not_examples": sorted(DISQUALIFYING),
                "note": SEARCH_NOTE,
                "entries": entries,
            }
            return _with_glossary(answer, flags, (e.get("caveats") or [] for e in entries))
    return {
        "error": f"unknown pattern {key!r}",
        "valid_patterns": sorted(p["key"] for p in patterns),
        "hint": "call list_patterns() for what each one means",
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
