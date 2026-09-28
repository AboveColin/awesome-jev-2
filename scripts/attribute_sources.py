#!/usr/bin/env python3
"""Record in each row's `sources` which sibling directories cite its repository.

Until 2026-09-27, 1,053 rows named one and the same source: the sibling-list
aggregate, a link to docs/sibling-lists.txt. Which of the lists there cited a
row was counted by discover_candidates.py for its weekly issue and then thrown
away, so a reader could not tell which directories list a project, or how many.

This reads every list's README (sibling_lists.py) and gives each catalogued row
with a GitHub repository one `sources` item per list that links it:
`{"catalog": "owner/name", "url": "https://github.com/owner/name"}`, the list's
own name and URL and nothing else, since many of these lists ship no licence.
Those items come after the sources a person wrote, which stay as they are and
say where the row was found; they are sorted by URL (ignoring case), so the
same citations are always the same bytes.

A citation is a fact about a list, not about the project: that list's README
linked the repository when last read. The lists copy from each other, so a
count of them is how widely a project is mentioned, never a check of it
(docs/method.md). It is refreshed weekly by the metadata workflow, like stars.

What changes, and what does not:
- A list read this time: its citations follow its README, added and removed.
- A list in docs/sibling-lists.txt that could not be read: its citations are
  kept as last read, so a host having a bad day moves nothing.
- A list no longer in docs/sibling-lists.txt: its citations are dropped (lint
  fails a citation of a list the file does not name).
- A list never cites its own row, and a row of this repository's own (the
  examples) is cited by none: a list linking this repository links the list.
- retired.json is not touched.
catalog.json is written only when some row's citations changed.

Usage:
  python3 scripts/attribute_sources.py                      # report what would change
  python3 scripts/attribute_sources.py --write              # ...and write it
  python3 scripts/attribute_sources.py --offline --write    # read nothing: drop the
      citations of lists docs/sibling-lists.txt no longer names, and sort the rest
  python3 scripts/attribute_sources.py --only jev --json
  python3 scripts/attribute_sources.py --write --digest /tmp/digest.md
      # appends one paragraph for the weekly refresh's issue body: counted, never listed

The last line printed is always the counts, so a CI log's tail explains a run.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _github import step_summary  # noqa: E402
from sibling_lists import (  # noqa: E402
    SIBLINGS,
    Harvest,
    citation,
    fetch_readme,
    harvest,
    in_citation_order,
    is_citation,
    list_repository,
    list_url,
    listed_urls,
    own_repository,
    read_lists,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"


def cited_urls(entry: dict, found: Harvest | None, listed: list[str]) -> list[str]:
    """The lists that should now be recorded citing the row, in citation order.

    `found` is this run's harvest (None when nothing was read); `listed` is
    every list docs/sibling-lists.txt names, as list_url() spells it.
    """
    repo = own_repository(entry)
    if repo is None:
        return []
    names = set(listed)
    reached = set(found.reached) if found else set()
    had = {s["url"] for s in entry.get("sources") or [] if is_citation(s)}
    # A list that was not read keeps what it cited when it last was.
    urls = {url for url in had if url in names and url not in reached}
    if found:
        urls |= {url for url in found.cited.get(repo, ()) if url in names}
    # A list's own row: its README linking itself is not another directory citing it.
    return in_citation_order(url for url in urls if list_repository(url) != repo)


def attributed(entry: dict, found: Harvest | None, listed: list[str]) -> dict:
    """A new row: the same keys in the same order, `sources` holding the
    person-written items as they were, then the citations (cited_urls)."""
    sources = entry.get("sources") or []
    kept = [source for source in sources if not is_citation(source)]
    return {**entry, "sources": kept + [citation(url) for url in cited_urls(entry, found, listed)]}


def compare(before: dict, after: dict) -> dict | None:
    """What changed in one row's citations, or None when nothing did."""
    if before.get("sources") == after.get("sources"):
        return None
    old = [s["url"] for s in before.get("sources") or [] if is_citation(s)]
    new = [s["url"] for s in after["sources"] if is_citation(s)]
    return {
        "slug": after["slug"],
        "added": [url for url in new if url not in old],
        "removed": [url for url in old if url not in new],
    }


def attribute(
    catalog: list[dict], found: Harvest | None, listed: list[str], only: str = ""
) -> tuple[list[dict], list[dict]]:
    """(the new catalogue, one change record per row whose sources changed)."""
    rows, changes = [], []
    for entry in catalog:
        if only not in entry.get("slug", ""):
            rows.append(entry)
            continue
        new = attributed(entry, found, listed)
        change = compare(entry, new)
        if change:
            changes.append(change)
        rows.append(new if change else entry)
    return rows, changes


def name_of(url: str) -> str:
    return url.removeprefix("https://github.com/")


def tally(changes: list[dict], rows: int, found: Harvest | None, listed: list[str]) -> str:
    """The counts line: always the last line printed."""
    added = sum(len(c["added"]) for c in changes)
    removed = sum(len(c["removed"]) for c in changes)
    read = (
        f"read {len(found.reached)} of {len(listed)} list(s)"
        if found
        else f"read 0 of {len(listed)} list(s) (offline)"
    )
    kept = f"; {len(found.unreached)} not read, their citations kept as last read" if found and found.unreached else ""
    return (
        f"sibling-list citations: {len(changes)} of {rows} row(s) changed "
        f"({added} added, {removed} removed); {read}{kept}"
    )


def digest(changes: list[dict], found: Harvest | None, listed: list[str]) -> str:
    """A paragraph for the weekly refresh's digest. Counted, never listed, and
    free of the phrases the metadata workflow files a notice for: which lists
    link a project changes most weeks and needs nobody."""
    if not changes and not (found and found.unreached):
        return ""
    moved = [c for c in changes if c["added"] or c["removed"]]
    added = sum(len(c["added"]) for c in moved)
    removed = sum(len(c["removed"]) for c in moved)
    lines = [
        f"Sibling-list citations (`sources`): {len(moved)} rows gained or lost a sibling "
        f"directory citing their repository ({added} citations added, {removed} removed), "
        f"as the READMEs of {len(found.reached) if found else 0} of {len(listed)} lists link them."
    ]
    if len(changes) > len(moved):
        lines.append(f"{len(changes) - len(moved)} rows had their citations put back in URL order.")
    if found and found.unreached:
        lines.append(
            f"{len(found.unreached)} lists could not be read and keep their earlier citations: "
            + ", ".join(f"`{name_of(url)}`" for url in found.unreached)
            + "."
        )
    return " ".join(lines) + "\n"


def report(changes: list[dict], found: Harvest | None, listed: list[str], rows: int, *, write: bool) -> None:
    for change in changes:
        parts = [f"+{name_of(u)}" for u in change["added"]] + [f"-{name_of(u)}" for u in change["removed"]]
        print(f"  ~ {change['slug']}: {' '.join(parts) or 'reordered'}")
    if found and found.unreached:
        print(f"\n  {len(found.unreached)} list(s) not read; their citations are kept as last read:")
        for url in found.unreached:
            print(f"      {url}")
    line = tally(changes, rows, found, listed)
    step_summary(
        "## Sibling-list citations\n\n"
        + f"- {line.removeprefix('sibling-list citations: ')}\n"
        + f"- {'written to' if write and changes else 'would change'} catalog.json\n"
        + "".join(f"- not read: {url}\n" for url in (found.unreached if found else ()))
    )
    print(f"\n{line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true", help="write catalog.json when a row's citations changed")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="read no list: only drop citations of lists sibling-lists.txt no longer names, and sort",
    )
    parser.add_argument("--only", default="", help="only rows whose slug contains this substring")
    parser.add_argument("--json", action="store_true", help="machine-readable changes on stdout")
    parser.add_argument("--digest", default="", metavar="FILE", help="append a paragraph for the weekly digest")
    args = parser.parse_args(argv)

    if not SIBLINGS.exists():
        print(f"error: {SIBLINGS} is missing", file=sys.stderr)
        return 1
    lines = read_lists(SIBLINGS)
    listed = listed_urls(lines)
    for line in lines:
        if list_url(line) is None:
            print(f"left out: {line!r} is not a GitHub repository URL", file=sys.stderr)

    found = None
    if not args.offline:
        print(f"reading {len(listed)} sibling list(s)", file=sys.stderr)
        found = harvest(listed, fetch=fetch_readme)
        if not found.reached:
            print(
                f"::warning title=Sibling lists not read::none of {len(listed)} lists answered; "
                "catalog.json left as it was",
                file=sys.stderr,
            )
            print(tally([], 0, found, listed))
            return 1

    catalog = json.loads(CATALOG.read_text())
    rows, changes = attribute(catalog, found, listed, args.only)
    considered = sum(1 for e in catalog if args.only in e.get("slug", ""))
    if args.write and changes:
        CATALOG.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    if args.digest:
        text = digest(changes, found, listed)
        if text:
            with open(args.digest, "a", encoding="utf-8") as handle:
                handle.write("\n" + text)

    if args.json:
        print(
            json.dumps(
                {
                    "changed": changes,
                    "reached": list(found.reached) if found else [],
                    "unreached": list(found.unreached) if found else [],
                    "listed": len(listed),
                },
                indent=2,
            )
        )
        print(tally(changes, considered, found, listed), file=sys.stderr)
        return 0
    report(changes, found, listed, considered, write=args.write)
    if changes and not args.write:
        print("Run with --write to apply.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
