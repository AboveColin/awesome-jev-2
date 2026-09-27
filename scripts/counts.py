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
    # The headline numbers are _stats' published ones; only the breakdowns
    # below, which nothing else publishes, are counted here.
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
