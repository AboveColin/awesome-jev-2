#!/usr/bin/env python3
"""Keep catalog.json and retired.json in slug order.

The order of rows in the data files means nothing to any reader: every
generator, the site and the MCP server sort for themselves, with slug as the
final tie-break. A fixed order exists only for the people editing the file.
When every new row was appended at the end, any two pull requests adding rows
touched the same lines and conflicted with each other; in slug order they
insert at different places and merge cleanly.

Rows are written back exactly as the other writers do (refresh_metadata.py,
check_links.py): json.dumps(indent=2, ensure_ascii=False) plus a newline, so
sorting never reformats anything else. The sort is stable and slugs are
unique (lint.py checks both files together), so running it twice changes
nothing the second time.

Run: python3 scripts/sort_catalog.py            # rewrite files that are out of order
     python3 scripts/sort_catalog.py --check    # exit 1 if a file would change
"""

from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = (ROOT / "catalog.json", ROOT / "retired.json")
COMMAND = "python3 scripts/sort_catalog.py"


def slug_of(entry: object) -> str:
    """Sort key. A row without a string slug sorts first; lint reports it."""
    slug = entry.get("slug") if isinstance(entry, dict) else None
    return slug if isinstance(slug, str) else ""


def sort_entries(entries: list) -> list:
    """A new list in slug order. Stable, so equal keys keep their order."""
    return sorted(entries, key=slug_of)


def render(entries: list) -> str:
    return json.dumps(entries, indent=2, ensure_ascii=False) + "\n"


def first_out_of_order(entries: list) -> tuple[int, str, str] | None:
    """(index, previous slug, slug) of the first row that sorts before its predecessor."""
    for i in range(1, len(entries)):
        before, here = slug_of(entries[i - 1]), slug_of(entries[i])
        if here < before:
            return i, before, here
    return None


def misplaced(entries: list) -> int:
    """The fewest rows that must move to put the file in slug order.

    Rows minus the longest run already in order (not necessarily adjacent).
    Counting rows whose index changes would report one appended row as a
    thousand: every row after its slot shifts down by one.
    """
    tails: list[str] = []
    for entry in entries:
        slug = slug_of(entry)
        i = bisect.bisect_right(tails, slug)
        if i == len(tails):
            tails.append(slug)
        else:
            tails[i] = slug
    return len(entries) - len(tails)


def order_problem(entries: list) -> str | None:
    """One line describing why `entries` is not in slug order, or None."""
    found = first_out_of_order(entries)
    if found is None:
        return None
    i, before, here = found
    return (
        f"{misplaced(entries)} of {len(entries)} rows need to move into slug order "
        f"(first: {here!r} at [{i}] sorts before {before!r} at [{i - 1}])"
    )


def process(path: pathlib.Path, *, check: bool) -> bool:
    """Sort one file in place (or only report, with check). True if it was or would be changed."""
    name = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    text = path.read_text(encoding="utf-8")
    entries = json.loads(text)
    if not isinstance(entries, list):
        raise SystemExit(f"error: {name}: top level must be an array of entries")

    problem = order_problem(entries)
    fresh = render(sort_entries(entries))
    if fresh == text:
        print(f"  ok {name}: {len(entries)} rows in slug order")
        return False

    reason = problem or "rows are in order, but the file is not formatted as json.dumps(indent=2)"
    if check:
        print(f"  {name}: {reason}")
        return True
    path.write_text(fresh, encoding="utf-8")
    print(f"  sorted {name}: {reason}; rewrote {len(entries)} rows")
    return True


def main(argv: list[str] | None = None, files: tuple[pathlib.Path, ...] = FILES) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--check", action="store_true", help="report files that are out of order without rewriting them"
    )
    args = parser.parse_args(argv)

    changed = [path for path in files if process(path, check=args.check)]
    if args.check and changed:
        print(f"\n{len(changed)} file(s) not in slug order. Run `{COMMAND}` and commit the result.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
