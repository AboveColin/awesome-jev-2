#!/usr/bin/env python3
"""Discovery verdicts, kept in the repository: `.discover/seen.json`.

scripts/discover_candidates.py reads the code of cited repositories that are
not in the catalogue and records one verdict per repository, so the weekly run
does not read the same code again for RECHECK_DAYS and does not propose the same
candidate twice. Those verdicts used to live only in the Actions cache, which
GitHub evicts after seven days without access: exactly the weekly schedule, and
scheduled runs start hours late. One late or failed run lost them all, and the
next issue proposed every candidate again as new.

They now live in git. discover.yml reads strangers' repositories and holds no
write permission, so it leaves this file as an artifact; metadata.yml, which
already commits the weekly facts, merges the newest artifact into the file here
and commits it with the refresh. The Actions cache stays as the fast path
between those commits.

The file records what a script found, never what a person decided: a person's
decision is a row in catalog.json or a line in docs/declined.txt. Its `about`
lines say so to anyone who opens it.

Every entry is checked on the way in, from the repository or an artifact: a
lower-case owner/name, one of VERDICTS, a YYYY-MM-DD date no later than
tomorrow. Anything else is dropped with a message, so that shape is all an
artifact can put into git. The newest verdict for a repository wins. The file
is written one repository per line in name order, so a week's diff is the
repositories that week's run read.

Usage:
  python3 scripts/discover_seen.py .discover/seen.json SOURCE.json [...]
      merge each SOURCE's verdicts into the first file and rewrite it
  python3 scripts/discover_seen.py .discover/seen.json
      rewrite it in canonical form, dropping entries that are not verdicts
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATH = ROOT / ".discover" / "seen.json"
# A repository judged not to call Jev is re-read after this long: projects add
# integrations, and a verdict from two months ago is not a verdict about today.
RECHECK_DAYS = 60
# Everything discover_candidates.inspect() can conclude, in the order its
# console report lists them.
VERDICTS = ("calls-jev", "mentions-only", "no-signal", "repo-gone", "tree-unavailable")
PROPOSED = "calls-jev"
# discover_candidates.slug_of(): the owner and name GitHub links carry, lower-cased.
SLUG = re.compile(r"[a-z0-9][\w.-]*/[\w.-]+")
ABOUT = [
    "Script verdicts, not human conclusions. Nobody reviewed these entries.",
    "scripts/discover_candidates.py read each repository's code on the date given and recorded what it found:",
    "calls-jev: a file it read contains a Jev call-site string (a reason for a person to read it, not a catalog row);",
    "mentions-only: no file it read calls Jev, but the README names it; no-signal: neither;",
    "repo-gone: GitHub returned no repository; tree-unavailable: its file list could not be read.",
    "It reads some files, not all, so no-signal does not mean a repository never calls Jev.",
    f"A verdict older than {RECHECK_DAYS} days is read again.",
    "A person's decision is a row in catalog.json or a line in docs/declined.txt, never an entry here.",
    "Written by .github/workflows/discover.yml, committed by .github/workflows/metadata.yml; see scripts/discover_seen.py.",
]


def problem(slug: object, entry: object, latest: dt.date) -> str:
    """Why an entry is not a verdict, or "" when it is one."""
    if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug != slug.lower():
        return "not a lower-case owner/name"
    if not isinstance(entry, dict):
        return "not an object"
    if entry.get("verdict") not in VERDICTS:
        return "not one of " + ", ".join(VERDICTS)
    on = entry.get("on")
    try:
        day = dt.date.fromisoformat(on)
    except (TypeError, ValueError):
        return "date is not YYYY-MM-DD"
    if day.isoformat() != on:
        return "date is not YYYY-MM-DD"
    if day > latest:
        return "dated after tomorrow"
    return ""


def parse(data: object, *, today: dt.date) -> tuple[dict[str, dict], list[str]]:
    """The verdicts in a loaded file, and one message per entry left out.

    Takes this module's shape, {"about": [...], "verdicts": {...}}, and the bare
    {slug: {"on", "verdict"}} mapping the Actions cache held before 2026-09-27,
    which the first run after the change restores."""
    if isinstance(data, dict) and isinstance(data.get("verdicts"), dict):
        entries = data["verdicts"]
    elif isinstance(data, dict) and not ({"about", "verdicts"} & set(data)):
        entries = data
    else:
        return {}, ['not a verdict file: expected {"about": [...], "verdicts": {...}}']
    latest = today + dt.timedelta(days=1)
    kept: dict[str, dict] = {}
    dropped: list[str] = []
    for slug, entry in entries.items():
        why = problem(slug, entry, latest)
        if why:
            dropped.append(f"{str(slug)[:80]!r}: {why}")
        else:
            kept[slug] = {"on": entry["on"], "verdict": entry["verdict"]}
    return kept, dropped


def load(path: pathlib.Path | str, *, today: dt.date) -> tuple[dict[str, dict], list[str]]:
    """parse() of a file. A missing file is an empty one, not a problem: the
    first run, and a cache miss, start from nothing."""
    path = pathlib.Path(path)
    if not path.exists():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return {}, [f"unreadable: {exc}"]
    return parse(data, today=today)


def newer(a: dict, b: dict) -> dict:
    """The later of two verdicts about one repository. On the same day a
    proposal wins, so a candidate already put to people is not forgotten; then
    the verdict's name decides, so a merge never depends on argument order."""
    return max(a, b, key=lambda e: (e["on"], e["verdict"] == PROPOSED, e["verdict"]))


def merge(*sources: dict[str, dict]) -> dict[str, dict]:
    """Every repository any source has a verdict for, with its newest verdict."""
    out: dict[str, dict] = {}
    for source in sources:
        for slug, entry in source.items():
            out[slug] = newer(out[slug], entry) if slug in out else dict(entry)
    return out


def render(verdicts: dict[str, dict]) -> str:
    """The file's text: `about` first, then one repository per line in name
    order, each entry's keys sorted. Same verdicts, same bytes."""
    about = ",\n".join(f"    {json.dumps(line, ensure_ascii=False)}" for line in ABOUT)
    rows = ",\n".join(
        f"    {json.dumps(slug, ensure_ascii=False)}: "
        + json.dumps(verdicts[slug], sort_keys=True, ensure_ascii=False)
        for slug in sorted(verdicts)
    )
    lines = ["{", '  "about": [', about, "  ],"]
    lines += ['  "verdicts": {', rows, "  }"] if rows else ['  "verdicts": {}']
    return "\n".join(lines + ["}"]) + "\n"


def write(path: pathlib.Path | str, verdicts: dict[str, dict]) -> None:
    """render() to path, replacing it in one step so a crash mid-write never
    leaves half a file for the next run or the next commit."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(render(verdicts))
        os.replace(tmp, path)
    except BaseException:
        pathlib.Path(tmp).unlink(missing_ok=True)
        raise


def report_dropped(where: str, dropped: list[str]) -> None:
    """A GitHub warning naming how many entries of a file were left out, then
    the first few; the rest of the file is still used."""
    if not dropped:
        return
    n = len(dropped)
    print(
        f"::warning title=Discovery verdicts left out::{where}: "
        f"{n} entr{'ies' if n != 1 else 'y'} not shaped like a verdict, left out",
        file=sys.stderr,
    )
    for line in dropped[:10]:
        print(f"  {where}: {line}", file=sys.stderr)


def main(argv: list[str] | None = None, *, today: dt.date | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or any(a.startswith("-") for a in args):
        print(__doc__.split("Usage:")[1].rstrip(), file=sys.stderr)
        return 2
    today = today or dt.date.today()
    target, sources = pathlib.Path(args[0]), args[1:]
    kept, dropped = load(target, today=today)
    report_dropped(str(target), dropped)
    loaded = []
    for source in sources:
        if not pathlib.Path(source).exists():
            print(f"error: {source} does not exist; {target} left as it was", file=sys.stderr)
            return 1
        verdicts, dropped = load(source, today=today)
        if dropped and not verdicts:
            report_dropped(source, dropped)
            print(f"error: {source} holds no verdicts; {target} left as it was", file=sys.stderr)
            return 1
        report_dropped(source, dropped)
        loaded.append(verdicts)
    merged = merge(kept, *loaded)
    added = sum(1 for slug in merged if slug not in kept)
    changed = sum(1 for slug in merged if slug in kept and merged[slug] != kept[slug])
    write(target, merged)
    proposed = sum(1 for entry in merged.values() if entry["verdict"] == PROPOSED)
    print(
        f"discovery verdicts: {len(merged)} in {target} ({proposed} {PROPOSED}); "
        f"{added} added and {changed} updated from {len(sources)} source(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
