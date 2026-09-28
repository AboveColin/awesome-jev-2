#!/usr/bin/env python3
"""Print catalog statistics.

Runs in CI so every build logs the shape of the catalog, which makes coverage
gaps visible over time: a pattern with zero entries is a research to-do, not a
rendering bug.

Run: python3 scripts/counts.py
"""

from __future__ import annotations

import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _stats  # noqa: E402


def block(title: str, counter: Counter, universe: list[str] | None = None) -> None:
    print(f"\n{title}")
    if universe is not None:
        for key in universe:
            count = counter.get(key, 0)
            bar = "#" * count
            mark = " " if count else "!"
            print(f"  {mark} {key:<24} {count:>3} {bar}")
        missing = [key for key in universe if not counter.get(key)]
        if missing:
            print(f"    no entries yet: {', '.join(missing)}")
    else:
        for key, count in counter.most_common():
            print(f"    {key:<24} {count:>3} {'#' * count}")
        if not counter:
            print("    (none)")


def main() -> int:
    # The headline numbers are _stats' published ones. The breakdowns below
    # are tallied here from the rows, for this log only.
    catalog, _retired, _patterns, _compat, schema = _stats.load()
    stats = _stats.compute()

    all_patterns = schema["properties"]["patterns"]["items"]["enum"]
    all_kinds = schema["properties"]["kind"]["enum"]

    patterns = Counter(pattern for entry in catalog for pattern in entry["patterns"])
    kinds = Counter(entry["kind"] for entry in catalog)
    languages = Counter(lang for entry in catalog for lang in entry.get("languages", []))
    platforms = Counter(item for entry in catalog for item in entry.get("platforms", []))
    qtypes = Counter(item for entry in catalog for item in entry.get("question_types", []))
    flags = Counter(flag for entry in catalog for flag in entry.get("flags", []))

    print(f"catalog.json   {stats['entries']} entries")
    print(f"retired.json   {stats['retired']} entries")
    print(f"with code      {stats['with_code']}")
    print(f"official       {stats['official']}")
    print(
        f"evidence       {stats['call_site_rows']} call-site, {stats['wire_shape_rows']} wire-shape, "
        f"{stats['example_only_rows']} example-only"
    )
    print(f"code, no cite  {stats['has_code_unbacked']} (neither evidence nor evidence_none)")
    print(
        f"primitives     {stats['primitive_rows']} read by a person (question_types), "
        f"{stats['primitive_signal_rows']} with a text signal in the cited file (primitives_seen), "
        f"{stats['primitive_signal_only_rows']} of them with no question_types"
    )
    print(
        f"review queue   {stats['review_examples_dir']} under examples/, "
        f"{stats['review_single_model_name']} on one model name or host, "
        f"{stats['review_tool_selection_broad']} tool-selection on dropped keywords, "
        f"{stats['review_generic_summary']} summaries naming nothing about Jev (docs/review-queue.md)"
    )
    print(
        f"patterns       {stats['patterns_rule_identical']} equal the keyword rules' suggestion (no review recorded), "
        f"{stats['patterns_reviewed']} patterns_reviewed, {stats['overview_unindexed']} overview rows with code "
        "not yet indexed by pattern"
    )
    print(
        f"summaries      {stats['summary_upstream']} upstream-description, "
        f"{stats['summary_upstream_stale']} upstream-description-stale, {stats['summary_curated']} curated, "
        f"{stats['summary_unlabelled']} unlabelled (summary_source)"
    )
    last_pushes = ", ".join(f"{month} {count}" for month, count in stats["pushed_by_month"].items()) or "none"
    print(
        f"repositories   {stats['repo_facts_rows']} with GitHub's creation date, last push and commit count, "
        f"{stats['single_commit_rows']} single-commit; last push by month (UTC): {last_pushes}"
    )
    directions = ", ".join(f"{key} {count}" for key, count in stats["measurement_directions"].items())
    print(
        f"measurements   {stats['measured_rows']} benchmark rows index their author's measurement "
        f"(author-stated directions: {directions}), {stats['review_measurement_unread']} not read by a person"
    )
    print(
        f"citations      {stats['cited_rows']} of {stats['citable_rows']} rows with a GitHub repository "
        "linked by at least one sibling directory (sources; a count of mentions, not a review)"
    )
    if stats["entries"]:
        print(f"zh hand-written {stats['zh_hand']}/{stats['entries']}")

    # The repository description is the one published sentence CI cannot rewrite
    # (description.yml files an issue when it drifts), so every run, a pull
    # request's included, shows what it should say once this tree is on main. It
    # changes only when the count crosses a hundred or pitch_public() is reworded.
    print(
        "\nrepository description once merged (count floored to the hundred; "
        f"next changes at {_stats.next_public_change(stats['entries']):,} entries):"
    )
    print(f"  {_stats.pitch_public(stats)}")

    block("by pattern (! = gap)", patterns, all_patterns)
    block("by kind (! = gap)", kinds, all_kinds)
    block("by language", languages)
    block("by platform", platforms)
    block("by question type", qtypes)
    block("flags", flags)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
