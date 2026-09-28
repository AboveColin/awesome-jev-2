"""The one definition of every number this project publishes about itself.

build_readme, build_docs, check_description and counts.py each used to count
"with code" or "dated 2xx records" on their own. They happened to agree. A number
that appears in the README badge, the status page, llms.txt, the site meta tags
and the repository description has to be computed once, or sooner or later two
of those surfaces will disagree and a reader will reasonably trust neither.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import json
import pathlib
import re
from collections import Counter

from classify import classify_broad, suggest
from measurements import directions as measurement_directions
from measurements import measured, negative, unread
from sibling_lists import citations_of, own_repository

ROOT = pathlib.Path(__file__).resolve().parent.parent

# A pattern holding less than this share of the catalogue is reported as thin.
# A share rather than a count: ten rows was a signal at 148 entries and is
# noise at 800.
THIN_SHARE = 0.025

# What the file an `evidence` record cites shows, as `evidence.kind` records it:
# a place the project calls Jev; a file showing a project speaking Jev's request
# shape rather than building on Jev (every `kind: alternative` row, and adapters); or
# an example the project ships rather than its own integration. A record without the field is
# a call site: that is what every citation meant before the field existed.
EVIDENCE_KINDS = ("call-site", "wire-shape", "example-only")

# Machine signals for docs/review-queue.md. Each marks a citation a person
# should re-read, never a verdict, and neither is written into catalog.json.
#
# A path under an examples directory: an SDK's examples are often its best call
# site, and a project's are often all it has, so only a person can say which.
# Recording `evidence.kind` either way is that decision, and ends the signal.
EXAMPLES_DIR = re.compile(r"(^|/)examples?/")
# One model name or the API host as the only matched string: any file that
# configures Jev contains one (a settings file, a pricing table, a model list)
# whether or not it calls the API, so on its own it is the thinnest witness a
# citation can have. A second matched string from the call itself ends it.
# A pinned model version counts whichever it is (PINNED_MODEL_VERSION): the
# version typed in here would have gone stale with the next release, and a
# citation resting on the next version is as thin as one resting on this one.
MODEL_NAMES_AND_HOST = ("jev-latest", "typesafe-ai/jev", "typesafe/jev", "api.typesafe.ai")
PINNED_MODEL_VERSION = re.compile(r"jev-\d+(?:\.\d+)+")

# A row with code whose English summary names nothing about Jev, and no note
# that does: a reader of the list cannot tell what the project asks Jev to
# decide. Most are the project's own GitHub description (summary_source),
# which has no reason to mention Jev. The words are a floor, not a test: they
# match inside longer words, a summary without them may still say it, and one
# with them may say little. TypeSafe AI's own rows (`official`, which lint
# holds to the vendor's hosts) are about Jev by construction and left out.
# Over a hundred rows match, so they are listed in docs/review-queue.md rather
# than warned about on every lint run.
JEV_WORDS = re.compile(r"jev|typesafe|system[\s-]?one|choice|score|noul|decision|confidence", re.IGNORECASE)
# A cited file whose path names a shadow or dry run, on a row without the
# shadow-mode-only flag: the call may be wired in on purpose so that nothing it
# returns reaches a decision, which is what the flag tells a reader. Only a
# person reading the call can say. One row matched when the rule was added, so
# lint warns about it (lint.py) instead of listing it in the review queue.
SHADOW_PATH = re.compile(r"shadow|dry.?run", re.IGNORECASE)
SHADOW_FLAG = "shadow-mode-only"

# A row filed under tool-selection that only the keyword rules' broad words
# suggest: "control", "harness" or "screen" on their own, or a robot, an
# autonomous system or "drive" with no word for deciding or acting. Those words
# counted until 2026-09-27 (classify.py), and the bulk passes took the rules'
# patterns, so such a row may never have been read against the pattern.
TOOL_SELECTION = "tool-selection"

# `overview` is for a row that surveys the model or the space (docs/patterns.md).
# It is also what the keyword rules suggest when nothing matches, and the bulk
# passes took their suggestion, so it filled with projects nobody placed. A
# project or plugin with code whose only pattern is overview is therefore
# listed apart, as not yet indexed by pattern, until a person records reading
# it against the patterns (`patterns_reviewed`) or gives it one. site/
# catalog-core.mjs holds the same rule for the site.
OVERVIEW = "overview"
UNINDEXED_KINDS = ("project", "plugin")

# Where a summary's words come from, as summary_source records it
# (schema/entry.schema.json). The two upstream values are the project's own
# text, which is why docs/sources.md counts them apart from the rest.
SUMMARY_SOURCES = ("curated", "upstream-description", "upstream-description-stale")

# The Jev primitives, in the schema's order. Two layers of evidence about them,
# never merged: `question_types` is a person's reading of the code calling a
# primitive; `primitives_seen` is a script's text signal that the one file a
# row's evidence cites contains the primitive's request or answer shape
# (scripts/verify_claims.py). A count of primitive claims reads the first only.
PRIMITIVES = ("choice", "score", "noul")

# GitHub's own facts about a row's repository, recorded by the weekly refresh
# (scripts/refresh_metadata.py) as GitHub states them: creation and last push
# as UTC timestamps, and the default branch's commit count. Published as counts
# per calendar month, never as an age: "N days since" is true for one day.
REPO_FACTS = ("repo_created_at", "repo_pushed_at", "repo_commits")


def load() -> tuple[list[dict], list[dict], list[dict], dict, dict]:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    retired = json.loads((ROOT / "retired.json").read_text())
    patterns = json.loads((ROOT / "patterns.json").read_text())["patterns"]
    compat = json.loads((ROOT / "compat.json").read_text())
    schema = json.loads((ROOT / "schema" / "entry.schema.json").read_text())
    return catalog, retired, patterns, compat, schema


def link_ok(entry: dict) -> bool:
    """A dated successful HTTP response, not a current availability guarantee."""
    return bool(entry.get("checked")) and 200 <= (entry.get("link_status") or 0) < 300


def evidence_kind(entry: dict) -> str | None:
    """What the cited file shows (EVIDENCE_KINDS), or None for a row citing none."""
    evidence = entry.get("evidence")
    if not evidence:
        return None
    return evidence.get("kind") or "call-site"


def examples_unjudged(entry: dict) -> bool:
    """Machine signal: the cited file sits in an examples directory, and nobody
    has recorded whether it is the project's call site or only an example."""
    evidence = entry.get("evidence")
    return bool(evidence) and "kind" not in evidence and bool(EXAMPLES_DIR.search(evidence.get("path", "")))


def single_model_name(entry: dict) -> bool:
    """Machine signal: the citation rests on one model name or the API host."""
    matched = (entry.get("evidence") or {}).get("matched") or []
    return len(matched) == 1 and (
        matched[0] in MODEL_NAMES_AND_HOST or PINNED_MODEL_VERSION.fullmatch(matched[0]) is not None
    )


def generic_summary(entry: dict) -> bool:
    """Machine signal: a row with code, not TypeSafe AI's own, with no notes and
    an English summary that names none of JEV_WORDS."""
    return (
        bool(entry.get("has_code"))
        and not entry.get("official")
        and not entry.get("notes")
        and not JEV_WORDS.search(entry.get("summary") or "")
    )


def shadow_path_unflagged(entry: dict) -> bool:
    """Machine signal: the cited file's path names a shadow or dry run and the
    row does not carry the shadow-mode-only flag."""
    evidence = entry.get("evidence")
    path = evidence.get("path") if isinstance(evidence, dict) else None
    return isinstance(path, str) and bool(SHADOW_PATH.search(path)) and SHADOW_FLAG not in (entry.get("flags") or [])


def signal_only(entry: dict) -> list[str]:
    """The primitives the cited file's text shows (primitives_seen) that no
    person recorded reading (question_types), in PRIMITIVES order."""
    read = set(entry.get("question_types") or [])
    seen = set(entry.get("primitives_seen") or [])
    return [name for name in PRIMITIVES if name in seen and name not in read]


def primitive_layers(catalog: list[dict]) -> dict[str, dict[str, int]]:
    """Per primitive: rows a person read calling it, and rows where only the
    text signal shows it. The two never overlap, so they may be shown side by
    side; neither is a count of the other."""
    return {
        name: {
            "read": sum(1 for e in catalog if name in (e.get("question_types") or [])),
            "signal_only": sum(1 for e in catalog if name in signal_only(e)),
        }
        for name in PRIMITIVES
    }


def pushed_by_month(catalog: list[dict]) -> dict[str, int]:
    """Rows per calendar month (UTC, `YYYY-MM`) of their repository's last push,
    newest month first. Only rows that record one; a month nobody pushed in is
    left out rather than shown as zero."""
    months = Counter(e["repo_pushed_at"][:7] for e in catalog if isinstance(e.get("repo_pushed_at"), str))
    return dict(sorted(months.items(), reverse=True))


def cited_by(catalog: list[dict]) -> dict[str, int]:
    """Rows per number of sibling directories whose README links their
    repository, fewest first, over the rows that have such a repository (a
    row nobody links counts under "0"). A count of mentions, not of reviews:
    the lists copy from each other. Keys are strings, as JSON keeps them, so
    site/stats.json reads back equal to this."""
    counts = Counter(len(citations_of(e)) for e in catalog if own_repository(e))
    return {str(n): rows for n, rows in sorted(counts.items())}


def not_indexed_by_pattern(entry: dict) -> bool:
    """A project or plugin with code filed only under overview, and no record
    of anyone reading it against the patterns. Derived, never stored."""
    return (
        entry.get("patterns") == [OVERVIEW]
        and bool(entry.get("has_code"))
        and entry.get("kind") in UNINDEXED_KINDS
        and not entry.get("patterns_reviewed")
    )


def patterns_match_rules(entry: dict) -> bool:
    """Machine signal, not a verdict: the row's patterns are exactly what the
    keyword rules suggest for its summary and title, and no reading is
    recorded. A person may have reviewed and agreed; that was not recorded."""
    return not entry.get("patterns_reviewed") and entry.get("patterns") == suggest(entry)[1]


def tool_selection_broad_only(entry: dict) -> bool:
    """Machine signal: the row carries tool-selection, the keyword rules as
    they stood until 2026-09-27 suggest it for the row's summary and title,
    the current rules do not, and no reading is recorded."""
    return (
        not entry.get("patterns_reviewed")
        and TOOL_SELECTION in entry.get("patterns", [])
        and TOOL_SELECTION in suggest(entry, classify_broad)[1]
        and TOOL_SELECTION not in suggest(entry)[1]
    )


def compute() -> dict:
    catalog, retired, patterns, compat, schema = load()
    by_pattern = Counter(p for e in catalog for p in e["patterns"])
    swept = [e["checked"] for e in catalog if link_ok(e)]
    last_sweep = max(swept) if swept else "never"
    siblings = [
        line
        for line in (ROOT / "docs" / "sibling-lists.txt").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return {
        "entries": len(catalog),
        "with_code": sum(1 for e in catalog if e.get("has_code")),
        "official": sum(1 for e in catalog if e.get("official")),
        "link_ok": sum(1 for e in catalog if link_ok(e)),
        "link_unstamped": sum(1 for e in catalog if not link_ok(e)),
        "last_sweep": last_sweep,
        # The newest date alone reads as "everything was checked then" once a
        # single row is stamped; this is how many rows it actually covers.
        "sweep_coverage": swept.count(last_sweep),
        "retired": len(retired),
        # Evidence counts recorded citations, not successful CI checks or
        # executed integrations. CI results do not live in catalog.json. One
        # count per evidence.kind: a file speaking Jev's request shape, or an
        # example, is not where a project uses Jev, and one total calling all
        # three "call sites" overstated the claim readers care about.
        "call_site_rows": sum(1 for e in catalog if evidence_kind(e) == "call-site"),
        "wire_shape_rows": sum(1 for e in catalog if evidence_kind(e) == "wire-shape"),
        "example_only_rows": sum(1 for e in catalog if evidence_kind(e) == "example-only"),
        # Rows with code that neither cite a file nor say why none can be
        # cited. lint.py fails those in a GitHub repository; a row elsewhere
        # (a docs page, a blog) is counted here without failing anything.
        "has_code_unbacked": sum(
            1 for e in catalog if e.get("has_code") and not (e.get("evidence") or e.get("evidence_none"))
        ),
        # Machine signals listed in docs/review-queue.md, for a person to read.
        "review_examples_dir": sum(1 for e in catalog if examples_unjudged(e)),
        "review_single_model_name": sum(1 for e in catalog if single_model_name(e)),
        "review_tool_selection_broad": sum(1 for e in catalog if tool_selection_broad_only(e)),
        "review_generic_summary": sum(1 for e in catalog if generic_summary(e)),
        # A benchmark's own report, indexed (`measurement`): how many rows carry
        # one, the directions their authors state (author-stated, not
        # reproduced here), and how many no person has read against the report
        # yet (docs/review-queue.md#measurement-unread).
        "measured_rows": len(measured(catalog)),
        "measurement_directions": measurement_directions(catalog),
        "review_measurement_unread": len(unread(catalog)),
        # Rows whose own author measured Jev for the use and concluded
        # against it: a benchmark whose measurement's direction is
        # unfavourable, or the negative-result flag on any other row.
        "negative_results": len(negative(catalog)),
        # How patterns were chosen is recorded only by patterns_reviewed. A row
        # whose patterns equal the keyword rules' suggestion shows agreement
        # with the rules and nothing more: the review, if any, was not recorded.
        "patterns_reviewed": sum(1 for e in catalog if e.get("patterns_reviewed")),
        "patterns_rule_identical": sum(1 for e in catalog if patterns_match_rules(e)),
        "overview_unindexed": sum(1 for e in catalog if not_indexed_by_pattern(e)),
        # A row with question_types additionally asserts *which* primitives.
        # Different claims; publishing one number for both would overstate it.
        "primitive_rows": sum(1 for e in catalog if e.get("question_types")),
        "primitive_rows_cited": sum(
            1 for e in catalog if e.get("question_types") and e.get("evidence")
        ),
        # A script's text signal, counted apart and never added to the above:
        # rows whose cited file contains a primitive's request or answer
        # shape, and of those, rows where no person recorded any primitive.
        "primitive_signal_rows": sum(1 for e in catalog if e.get("primitives_seen")),
        "primitive_signal_only_rows": sum(
            1 for e in catalog if e.get("primitives_seen") and not e.get("question_types")
        ),
        "primitive_layers": primitive_layers(catalog),
        "no_licence": sum(1 for e in catalog if e.get("repo_license") == "unknown"),
        # GitHub's dates and commit count, as the weekly refresh last read
        # them: how many rows record them, how many default branches had a
        # single commit (the `single-commit` flag, which follows the count on
        # every row the refresh reads), and last pushes per calendar month.
        "repo_facts_rows": sum(1 for e in catalog if all(key in e for key in REPO_FACTS)),
        "single_commit_rows": sum(1 for e in catalog if "single-commit" in (e.get("flags") or [])),
        "pushed_by_month": pushed_by_month(catalog),
        # Which sibling directories link each row's repository, as the weekly
        # run last read their READMEs: rows with a GitHub repository, how many
        # of them at least one list links, and rows per number of lists.
        "citable_rows": sum(1 for e in catalog if own_repository(e)),
        "cited_rows": sum(1 for e in catalog if citations_of(e)),
        "cited_by": cited_by(catalog),
        # summary_source: the project's own description word for word; taken
        # from it and no longer matching; written for this catalogue; not
        # recorded. The refresh writes the first two, only a person the third.
        "summary_upstream": sum(1 for e in catalog if e.get("summary_source") == "upstream-description"),
        "summary_upstream_stale": sum(
            1 for e in catalog if e.get("summary_source") == "upstream-description-stale"
        ),
        "summary_curated": sum(1 for e in catalog if e.get("summary_source") == "curated"),
        "summary_unlabelled": sum(1 for e in catalog if e.get("summary_source") not in SUMMARY_SOURCES),
        # Of the project-worded summaries, how many Chinese counterparts are a
        # machine translation of them.
        "summary_upstream_zh_machine": sum(
            1
            for e in catalog
            if e.get("summary_source") in SUMMARY_SOURCES[1:] and e.get("zh_machine")
        ),
        # Who wrote each Chinese summary: a person, or a model (zh_machine).
        # scripts/zh_audit.py compares the machine translations with their English.
        "zh_hand": sum(1 for e in catalog if not e.get("zh_machine")),
        "zh_machine": sum(1 for e in catalog if e.get("zh_machine")),
        "patterns_total": len(patterns),
        "patterns_covered": sum(1 for p in patterns if by_pattern[p["key"]]),
        "empty_kinds": [
            k
            for k in schema["properties"]["kind"]["enum"]
            if not any(e["kind"] == k for e in catalog)
        ],
        "platforms": len(compat["platforms"]),
        "sibling_lists": len(siblings),
        "by_pattern": {p["key"]: by_pattern[p["key"]] for p in patterns},
        "kinds": schema["properties"]["kind"]["enum"],
        "fields": list(schema["properties"]),
        "pattern_keys": [p["key"] for p in patterns],
    }


def public_count(entries: int) -> str:
    """The catalogue size as the public pitch states it: floored to the hundred.

    The repository description quotes this, and CI cannot edit that description
    (it needs admin rights no workflow token holds), so an exact count went
    stale with every merged row. A floor stays true as the catalogue grows and
    changes once per hundred, like the social preview's "800+". Below a hundred
    the floor would say nothing, so the count is exact there.
    """
    if entries < 100:
        return str(entries)
    return f"{entries // 100 * 100:,}+"


def next_public_change(entries: int) -> int:
    """The catalogue size at which public_count() next reads differently."""
    if entries < 100:
        return entries + 1
    return (entries // 100 + 1) * 100


def pitch_public(stats: dict) -> str:
    """The one-line description used by the GitHub repository and the site's
    meta tags. One function, so the two cannot drift into different sentences.
    The count is public_count()'s floor; README, status.md and llms.txt carry
    the exact figure."""
    return (
        f"{public_count(stats['entries'])} public resources for Jev, TypeSafe AI's System One "
        "decision model, indexed by decision pattern. Source citations, dated link "
        "checks and scheduled call-site text checks; runtime and performance are "
        "not independently tested here. EN/中文, JSON schema and platform compatibility."
    )
