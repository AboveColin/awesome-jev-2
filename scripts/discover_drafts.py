#!/usr/bin/env python3
"""Draft catalog rows for discovery candidates: `discover_candidates.py --drafts DIR`.

A candidate the weekly discovery run found calling Jev still has to be read by
a person before it becomes a row. What that person should not have to do is
copy by hand what the script already knows: the URL, GitHub's star count and
licence, the file it found the call site in and the strings it matched there,
and the keyword rules' guess at kind and patterns. A draft is that row with
those fields filled in, written to DIR/<slug>.json as one object to complete
and then add to catalog.json.

A draft is not a row. Its first field, `_draft`, says what a script filled in
and what a person still has to do, and lint.py refuses any row that still has
it (lint.DRAFT_FIELD). That field is the only thing that keeps a draft out of
the catalogue as it is: the empty summary fails too, but a single word would
pass, and nothing requires `evidence.read_on`. The review card on the pull
request (scripts/review_rows.py) is a second gate. Neither reads the code for
anyone.

Nothing is written over an existing file, so running the command again never
loses a draft someone has started to complete. Drafts belong to the person
completing them: `drafts/` is ignored by git, and CI never writes one.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _github import LANG_EXT, SELF  # noqa: E402
from lint import DRAFT_FIELD  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROPOSED = "calls-jev"
# Where the weekly run's candidates come from, spelled as the rows it
# produced record it. A harvest knows a candidate was cited by a sibling list;
# a single `--only` read does not, so its draft leaves sources for the person.
SOURCE = {
    "catalog": "sibling-list aggregate (docs/sibling-lists.txt)",
    "url": f"https://github.com/{SELF}/blob/main/docs/sibling-lists.txt",
}
SLUG_MAX = 80  # schema/entry.schema.json, slug.maxLength


def kebab(text: str) -> str:
    """Lower-case letters and digits joined by single hyphens: the schema's slug alphabet."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def propose_slug(owner: str, name: str, taken: set[str]) -> str:
    """The repository's name as a slug; with its owner appended when that is
    taken (the catalogue's habit: jgrep-kyu1204), then numbered."""
    base = kebab(name)[:SLUG_MAX].strip("-")
    with_owner = kebab(f"{name}-{owner}")[:SLUG_MAX].strip("-")
    for slug in (base, with_owner):
        if len(slug) >= 2 and slug not in taken:
            return slug
    n = 2
    while True:
        slug = f"{with_owner[: SLUG_MAX - 1 - len(str(n))].strip('-')}-{n}"
        if slug not in taken:
            return slug
        n += 1


def languages_of(path: str) -> list[str]:
    """The catalogue language the call site's file extension names, if exactly one does."""
    suffix = pathlib.PurePosixPath(path).suffix.lower()
    found = [lang for lang, exts in LANG_EXT.items() if suffix in exts]
    return found if len(found) == 1 else []


def call_site_url(result: dict) -> str:
    # The link discover_candidates.blob_url() prints; a test holds them equal.
    return f"{result['url']}/blob/HEAD/{urllib.parse.quote(result['evidence_path'], safe='/')}"


def instructions(result: dict, *, sourced: bool, today: dt.date) -> list[str]:
    """The `_draft` field: what a script filled in, and what is left to a person."""
    matched = ", ".join(json.dumps(s, ensure_ascii=False) for s in result["matched"])
    lines = [
        f"Draft written by scripts/discover_candidates.py on {today.isoformat()}: what a script "
        "found, not a catalog row. lint.py refuses any row that still has this field.",
        f"Read the call site yourself: {call_site_url(result)}. The script found {matched} "
        "in that file; it did not read how the code uses them.",
    ]
    if result.get("evidence_is_test"):
        lines.append(
            "That file looks like a test. Find the call site in the implementation and cite "
            "that instead: a mocked string is weaker proof than a real call."
        )
    if languages_of(result["evidence_path"]):
        guesses = (
            "kind and patterns are keyword guesses from the repository's description, and "
            "languages comes from the call site's file extension: check all three."
        )
    else:
        guesses = (
            "kind and patterns are keyword guesses from the repository's description: check "
            "both. languages is left out, as the call site's file extension names no language "
            "the catalogue knows: add it from the code."
        )
    lines += [
        "Write summary and summary_zh from what the code does, not from its README (set "
        "zh_machine to true if a tool wrote the Chinese). Add question_types for the "
        "primitives the call site uses, platforms for how it reaches Jev, and evidence.read_on "
        "for the day you read the file.",
        guesses + " stars, repo_license and the archived and no-license flags are GitHub's "
        "answers on the draft's date. first_seen is the day the row enters the catalogue.",
        "Add any other flag a reader needs (CONTRIBUTING.md, 'Flags are the point'); "
        "self-submitted goes with an 'author submission' source if this is your own project.",
    ]
    if not sourced:
        lines.append(
            "sources is empty: name where you found this repository. A candidate from the "
            "weekly discovery issue was found by the sibling-list aggregate: "
            + json.dumps(SOURCE)
        )
    lines.append(
        "Then delete this field, add the row to catalog.json and run python3 scripts/check.py --fix."
    )
    return lines


def draft_row(result: dict, *, slug: str, today: dt.date, sourced: bool) -> dict:
    """One candidate as a catalog row with everything a script knows filled in,
    `_draft` first, in the field order the catalogue's rows use."""
    owner, name = result["url"].rstrip("/").split("/")[-2:]
    licence = result.get("license") or "unknown"
    flags = (["archived"] if result.get("archived") else []) + (
        ["no-license"] if licence == "unknown" else []
    )
    row: dict = {
        DRAFT_FIELD: instructions(result, sourced=sourced, today=today),
        "slug": slug,
        "title": name,
        "summary": "",
        "summary_zh": "",
        "url": result["url"],
        "kind": result["suggested_kind"],
        "patterns": list(result["suggested_patterns"]),
    }
    languages = languages_of(result["evidence_path"])
    if languages:
        row["languages"] = languages
    row["author"] = {"name": owner, "url": f"https://github.com/{owner}"}
    row["has_code"] = True
    row["stars"] = int(result.get("stars") or 0)
    row["repo_license"] = licence
    row["evidence"] = {"path": result["evidence_path"], "matched": list(result["matched"])}
    row["first_seen"] = today.isoformat()
    if flags:
        row["flags"] = flags
    row["sources"] = [dict(SOURCE)] if sourced else []
    row["license"] = "CC0-1.0"
    return row


def catalogue_slugs(root: pathlib.Path = ROOT) -> set[str]:
    """Every slug in catalog.json and retired.json: a slug is never reused."""
    taken: set[str] = set()
    for name in ("catalog.json", "retired.json"):
        path = root / name
        if path.exists():
            taken |= {e["slug"] for e in json.loads(path.read_text(encoding="utf-8")) if "slug" in e}
    return taken


def drafts_in(directory: pathlib.Path) -> dict[str, str]:
    """slug -> url of the drafts already in the directory (unreadable ones by slug only)."""
    found: dict[str, str] = {}
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            url = json.loads(path.read_text(encoding="utf-8")).get("url", "")
        except (OSError, ValueError, AttributeError):
            url = ""
        found[path.stem] = str(url).rstrip("/").lower()
    return found


def write_drafts(
    results: list[dict],
    directory: pathlib.Path | str,
    *,
    sourced: bool,
    today: dt.date | None = None,
    taken: set[str] | None = None,
) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    """A draft for each result that found a call site, in owner/name order.
    Returns (written, kept): a draft already there for the same repository is
    kept as it is, and a slug another repository's draft holds is not reused."""
    directory = pathlib.Path(directory)
    today = today or dt.date.today()
    taken = set(catalogue_slugs() if taken is None else taken)
    existing = drafts_in(directory)
    written: list[pathlib.Path] = []
    kept: list[pathlib.Path] = []
    for result in sorted(results, key=lambda r: r["slug"]):
        if result.get("verdict") != PROPOSED:
            continue
        url = result["url"].rstrip("/").lower()
        mine = next((slug for slug, u in existing.items() if u == url), None)
        if mine:
            kept.append(directory / f"{mine}.json")
            taken.add(mine)
            continue
        owner, name = result["url"].rstrip("/").split("/")[-2:]
        slug = propose_slug(owner, name, taken | set(existing))
        taken.add(slug)
        path = directory / f"{slug}.json"
        directory.mkdir(parents=True, exist_ok=True)
        row = draft_row(result, slug=slug, today=today, sourced=sourced)
        path.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return written, kept


def report(results: list[dict], directory: str, *, sourced: bool, skip: str = "") -> int:
    """write_drafts() with a line on stderr for every candidate: the draft
    written or kept, or why there is none. Returns how many were written."""
    if skip:
        for result in results:
            print(f"no draft for {result['slug']}: it is {skip}", file=sys.stderr)
        return 0
    for result in results:
        if result.get("verdict") != PROPOSED:
            print(
                f"no draft for {result['slug']}: its verdict is {result.get('verdict')}, "
                "and a draft needs a call site",
                file=sys.stderr,
            )
    written, kept = write_drafts(results, directory, sourced=sourced)
    for path in written:
        print(f"wrote draft {path}", file=sys.stderr)
    for path in kept:
        print(f"kept draft {path}: it is already there, delete it for a new one", file=sys.stderr)
    if written or kept:
        print(
            f"{len(written)} draft(s) written, {len(kept)} kept. Each is refused by lint.py "
            f"until a person completes it and deletes its {DRAFT_FIELD} field.",
            file=sys.stderr,
        )
    return len(written)
