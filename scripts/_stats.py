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

ROOT = pathlib.Path(__file__).resolve().parent.parent

# A pattern holding less than this share of the catalogue is reported as thin.
# A share rather than a count: ten rows was a signal at 148 entries and is
# noise at 800.
THIN_SHARE = 0.025

# What the file an `evidence` record cites shows, as `evidence.kind` records it:
# a place the project calls Jev; a file showing a project speaking Jev's request
# shape rather than using Jev (every `kind: alternative` row, and adapters); or
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
MODEL_NAMES_AND_HOST = ("jev-latest", "jev-1.13", "typesafe-ai/jev", "typesafe/jev", "api.typesafe.ai")


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
    return len(matched) == 1 and matched[0] in MODEL_NAMES_AND_HOST


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
        # Machine signals listed in docs/review-queue.md, for a person to read.
        "review_examples_dir": sum(1 for e in catalog if examples_unjudged(e)),
        "review_single_model_name": sum(1 for e in catalog if single_model_name(e)),
        # A row with question_types additionally asserts *which* primitives.
        # Different claims; publishing one number for both would overstate it.
        "primitive_rows": sum(1 for e in catalog if e.get("question_types")),
        "primitive_rows_cited": sum(
            1 for e in catalog if e.get("question_types") and e.get("evidence")
        ),
        "no_licence": sum(1 for e in catalog if e.get("repo_license") == "unknown"),
        "zh_hand": sum(1 for e in catalog if not e.get("zh_machine")),
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
