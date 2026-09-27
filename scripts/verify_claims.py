#!/usr/bin/env python3
"""Re-check that the primitive claims in catalog.json are still true upstream.

A row carrying `question_types` asserts which Jev primitives a project's code
actually calls. That assertion was true when a person read the call site, and
nothing stopped it going stale afterwards — an upstream refactor could remove
the integration entirely and this catalog would keep claiming it.

This script closes that gap. For every row with `evidence`, it fetches that file
from the repository's default branch and asserts every string in
`evidence.matched` still appears.

The file is read first at `HEAD` on raw.githubusercontent.com, which resolves
to the default branch without the API call per repository that asking for the
branch name costs. That resolution is observed behaviour, not documented, so
only a pass is taken from it: a file missing or changed at HEAD is read again at
the default branch the API names, and that read is what gets reported. A GitHub
rate limit leaves a claim unchecked (`skipped`), never failed.

Deliberately not pinned to a commit. Pinning would verify a historical snapshot
forever and never notice a removal, which defeats the purpose. The cost is that
an upstream rename reports `path-gone`; that is a false positive a person
resolves, not a reason to check the wrong thing.

Exit code is 0 when every claim holds and 1 when any fails, so the scheduled
workflow can open an issue.

A file whose claim holds is also searched for the primitives' request and
answer shapes — `"type": "choice"`, `Noul(`, `.noul` and the like
(PRIMITIVE_SHAPES), never the bare words. What it finds is a machine text
signal about that one file: it does not say the code calls the primitive, and
it is not `question_types`, which records what a person read the code calling.
`--write-signals` records it in each row's `primitives_seen`, the only field
this script ever writes; the weekly metadata run calls it and commits the
result with the other mechanical facts. Nothing reads `primitives_seen` in place
of `question_types`.

Usage:
  python3 scripts/verify_claims.py                  # check every row with evidence
  python3 scripts/verify_claims.py --only slug      # check one row
  python3 scripts/verify_claims.py --discover       # propose evidence for rows lacking it
  python3 scripts/verify_claims.py --json           # machine-readable report
  python3 scripts/verify_claims.py --write-signals  # record primitives_seen in catalog.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from _github import (
    CODE_EXT,
    RateLimited,
    api_get,
    default_branch,
    log_usage,
    raw_get,
    repo_of,
    step_summary,
    usage_lines,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"

# Signals that a file is a genuine Jev call site rather than a mention. The
# import and the endpoint are strong; a bare primitive name is not, because
# "choice" and "score" are ordinary English words.
STRONG = [
    "api.typesafe.ai",
    "typesafe_sdk",
    "@typesafe-ai/sdk",
    # The Vercel AI SDK provider: evaluate() calls, where noul is spelled boolean.
    "@ai-sdk/typesafe-ai",
    "typesafe-ai/jev",
    "typesafe/jev",
    "jev-latest",
    "jev-1.13",
    "/v1/systemone",
    "systemOne",
    "system_one",
    "langchain_typesafe",
    "TypeSafeClient",
    "AsyncTypeSafeClient",
]
# Only meaningful alongside a strong signal.
WEAK = ["noul", "Noul", "choice", "Choice", "score", "Score"]

# The Jev primitives, in the order schema/entry.schema.json lists them for
# question_types and primitives_seen.
PRIMITIVES = ("choice", "score", "noul")

# A primitive's request or answer shape written out, as opposed to its name.
# WEAK's bare words say nothing about a primitive ("choice" and "score" are
# English, and a README names all three); these are the forms Jev's request and
# answer take in code. Each pattern's one group is the primitive. Left out on
# purpose: `.choice` and `.score` (random.choice, model.score), `type="noul"`
# as a keyword argument (the test doubles that build fake answers), and
# Vercel's `boolean`, which is how its SDK spells noul and how everything else
# spells a boolean.
_QUOTE = r"""\\?["']"""  # also inside an escaped JSON string: {\"type\":\"noul\"}
PRIMITIVE_SHAPES = (
    # The request's `type` field: JSON, a Python dict, a JS object, a TS type.
    re.compile(rf"""(?<![\w$.])(?:{_QUOTE}type{_QUOTE}|type)\s*:\s*{_QUOTE}(choice|score|noul){_QUOTE}"""),
    # The same field in Ruby, PHP or Elixir.
    re.compile(rf"""(?:{_QUOTE}type{_QUOTE}|:type)\s*=>\s*{_QUOTE}(choice|score|noul){_QUOTE}"""),
    # The SDKs' question constructors. click.Choice( is a CLI option, not Jev.
    re.compile(r"""(?<!click\.)\b(Choice|Score|Noul)\("""),
    # Reading a noul answer.
    re.compile(r"""\.(noul)\b"""),
)

WORKERS = 6


def weak_words(body: str) -> list[str]:
    """The WEAK words the file contains as whole words, in WEAK's order."""
    return [w for w in WEAK if re.search(rf"\b{re.escape(w)}\b", body)]


def primitive_signals(body: str) -> list[str]:
    """The primitives whose shape (PRIMITIVE_SHAPES) the text contains, in
    PRIMITIVES order. A text signal about this one file, not a reading."""
    found = {match.group(1).lower() for pattern in PRIMITIVE_SHAPES for match in pattern.finditer(body)}
    return [name for name in PRIMITIVES if name in found]


def check(entry: dict) -> dict:
    slug = entry["slug"]
    repo = repo_of(entry)
    if not repo:
        return {
            "slug": slug,
            "status": "no-repo",
            "detail": "row has no GitHub repository",
        }
    try:
        return read_claim(slug, repo, entry["evidence"])
    except RateLimited as exc:
        return {"slug": slug, "status": "skipped", "detail": f"not checked: {exc}"}


def read_claim(slug: str, repo: str, evidence: dict) -> dict:
    # A pass at HEAD is a pass; anything else is judged at the named branch.
    body = raw_get(repo, "HEAD", evidence["path"])
    if body is not None and all(needle in body for needle in evidence["matched"]):
        return {
            "slug": slug,
            "status": "ok",
            "detail": f"{repo}@HEAD:{evidence['path']}",
            "primitive_signals": primitive_signals(body),
        }

    branch = default_branch(repo)
    if not branch:
        return {
            "slug": slug,
            "status": "repo-gone",
            "detail": f"{repo} did not resolve",
        }

    body = raw_get(repo, branch, evidence["path"])
    if body is None:
        return {
            "slug": slug,
            "status": "path-gone",
            "detail": f"{repo}@{branch}:{evidence['path']} not found — renamed, moved or deleted",
        }

    missing = [needle for needle in evidence["matched"] if needle not in body]
    if missing:
        return {
            "slug": slug,
            "status": "claim-gone",
            "detail": f"{repo}@{branch}:{evidence['path']} no longer contains {missing}",
        }
    return {
        "slug": slug,
        "status": "ok",
        "detail": f"{repo}@{branch}:{evidence['path']}",
        "primitive_signals": primitive_signals(body),
    }


def needs_discovery(entry: dict) -> bool:
    """A row lint requires evidence or evidence_none of, that carries neither.

    That is a row claiming primitives, and since 2026-09-27 every row with code
    in a GitHub repository; --discover can only help where there is a
    repository to read.
    """
    return (
        bool(entry.get("question_types") or entry.get("has_code"))
        and "evidence" not in entry
        and "evidence_none" not in entry
        and repo_of(entry) is not None
    )


def discover(entry: dict) -> dict:
    """Propose evidence for a row that has none, by reading the repository.

    Proposals are a starting point for a person, never written automatically —
    the whole point of this catalog is that a human read the call site. For an
    alternative the proposal says `wire-shape`, the only evidence.kind lint
    accepts there: whatever file it cites, the project is not built on Jev.
    """
    slug = entry["slug"]
    repo = repo_of(entry)
    if not repo:
        return {"slug": slug, "status": "no-repo"}
    branch = default_branch(repo)
    if not branch:
        return {"slug": slug, "status": "repo-gone"}

    tree = api_get(f"/repos/{repo}/git/trees/{branch}?recursive=1")
    if not isinstance(tree, dict) or "tree" not in tree:
        return {"slug": slug, "status": "tree-unavailable"}

    # Prefer paths whose name already hints at the integration; it keeps the
    # candidate list short on repositories with thousands of files.
    paths = [
        node["path"]
        for node in tree["tree"]
        if node.get("type") == "blob" and node["path"].endswith(CODE_EXT)
    ]
    hinted = [p for p in paths if re.search(r"jev|typesafe", p, re.I)]
    candidates = (hinted or paths)[:40]

    best = None
    for path in candidates:
        body = raw_get(repo, branch, path)
        if not body:
            continue
        strong = [s for s in STRONG if s in body]
        if not strong:
            continue
        weak = weak_words(body)
        score = len(strong) * 2 + len(weak)
        # A test file proves the integration exists, but the implementation is
        # the better witness: tests get deleted while features stay, and a
        # mocked string is weaker proof than a real call site.
        if re.search(r"(^|/)(tests?|spec|__tests__)/|\.(test|spec)\.[a-z]+$|_test\.[a-z]+$|test_[^/]*$", path, re.I):
            score -= 5
        # Config and fixture files mention endpoints without calling them.
        if re.search(r"(^|/)(fixtures?|config|constants|prefs)[./]", path, re.I):
            score -= 3
        if best is None or score > best["score"]:
            best = {
                "score": score,
                "path": path,
                "matched": (strong[:2] + weak[:2])[:4],
                "signals": primitive_signals(body),
            }
    if not best:
        return {"slug": slug, "status": "no-call-site", "repo": repo}
    proposal = {
        "slug": slug,
        "status": "proposed",
        "repo": repo,
        "path": best["path"],
        "matched": best["matched"],
        # A hint for the person reading the file, never a value for question_types.
        "primitive_signals": best["signals"],
    }
    if entry.get("kind") == "alternative":
        proposal["kind"] = "wire-shape"
    return proposal


# --- primitives_seen ---------------------------------------------------------

SEEN = "primitives_seen"
# A read that found the cited file without the claim, or no file or repository
# at all: that file shows nothing now, so the row carries no signal. A read the
# rate limit stopped is no read, and changes nothing.
UNSEEN = ("claim-gone", "path-gone", "repo-gone")


def seen_after(result: dict) -> list[str] | None:
    """What a row's primitives_seen should be after this read; None to leave it."""
    if result["status"] == "ok":
        return list(result.get("primitive_signals") or [])
    if result["status"] in UNSEEN:
        return []
    return None


def with_seen(entry: dict, seen: list[str]) -> dict:
    """A copy of the row carrying `seen` right after `evidence`, or none when
    `seen` is empty. Every other key keeps its place and value."""
    out: dict = {}
    for key, value in entry.items():
        if key == SEEN:
            continue
        out[key] = value
        if key == "evidence" and seen:
            out[SEEN] = list(seen)
    return out


def apply_signals(catalog: list[dict], results: list[dict]) -> tuple[list[dict], dict[str, list[str]]]:
    """The catalogue with each read row's primitives_seen brought up to date,
    and one log line per row by outcome. question_types is never read or written."""
    by_slug = {r["slug"]: r for r in results}
    outcome: dict[str, list[str]] = {"added": [], "changed": [], "removed": [], "unchanged": [], "unread": []}
    rows = []
    for entry in catalog:
        result = by_slug.get(entry.get("slug"))
        seen = seen_after(result) if result else None
        old = list(entry.get(SEEN) or [])
        if result is None:
            rows.append(entry)
            continue
        slug = entry["slug"]
        if seen is None:
            outcome["unread"].append(f"  ? {slug}: {result['status']}, left as it was")
        elif seen == old:
            outcome["unchanged"].append(slug)
        elif not old:
            outcome["added"].append(f"  + {slug}: {', '.join(seen)}")
        elif not seen:
            why = "no shape in the file" if result["status"] == "ok" else result["status"]
            outcome["removed"].append(f"  - {slug}: {', '.join(old)} ({why})")
        else:
            outcome["changed"].append(f"  ~ {slug}: {', '.join(old)} -> {', '.join(seen)}")
        rows.append(entry if seen is None or seen == old else with_seen(entry, seen))
    return rows, outcome


def write_signals(catalog: list[dict], todo: list[dict]) -> int:
    """--write-signals: read every cited file and record primitives_seen.

    Exit 0 whatever the claims show: a claim that stopped holding is the
    claims job's alarm, and this run only records what each file shows. The
    last line printed is always the counts, for the workflow log."""
    print(f"reading {len(todo)} cited file(s) for primitive text signals\n", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(check, todo))
    rows, outcome = apply_signals(catalog, results)
    for kind in ("added", "changed", "removed", "unread"):
        for line in outcome[kind]:
            print(line)
    counts = (
        f"primitive text signals: {len(results)} row(s) with evidence; "
        f"{len(outcome['added'])} added, {len(outcome['changed'])} changed, "
        f"{len(outcome['removed'])} removed, {len(outcome['unchanged'])} unchanged; "
        f"{len(outcome['unread'])} not read (GitHub rate limit or no repository)"
    )
    step_summary(
        "## Primitive text signals\n\n"
        "`primitives_seen`: primitives whose request or answer shape each row's cited file "
        "contains. A machine text signal, not a person's reading, and not `question_types`.\n\n"
        f"- {counts}\n"
        + "".join(f"- {line}\n" for line in usage_lines())
    )
    if rows != catalog:
        CATALOG.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {CATALOG.name}")
    else:
        print("nothing to write")
    log_usage()
    print(counts)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="", help="check a single slug")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--discover", action="store_true", help="propose evidence for rows lacking it"
    )
    mode.add_argument(
        "--write-signals",
        action="store_true",
        help="record in catalog.json the primitives whose shape each cited file contains (primitives_seen)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    catalog = json.loads(CATALOG.read_text())

    if args.write_signals:
        todo = [e for e in catalog if "evidence" in e and (not args.only or e["slug"] == args.only)]
        return write_signals(catalog, todo)

    if args.discover:
        todo = [e for e in catalog if needs_discovery(e) and (not args.only or e["slug"] == args.only)]
        print(f"discovering evidence for {len(todo)} row(s)\n", file=sys.stderr)
        if args.only and not todo:
            print(
                f"{args.only}: not a row that needs one: it already carries evidence or "
                "evidence_none, has no code, has no GitHub repository, or is not in catalog.json",
                file=sys.stderr,
            )
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            results = list(pool.map(discover, todo))
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            for r in results:
                if r["status"] == "proposed":
                    print(
                        f"  {r['slug']}\n    path: {r['path']}\n    matched: {r['matched']}"
                    )
                    if r.get("primitive_signals"):
                        print(
                            f"    primitive shapes in that file: {', '.join(r['primitive_signals'])} "
                            "(a text signal: read the call before setting question_types)"
                        )
                    if r.get("kind"):
                        print(f"    kind: {r['kind']} (the row is an alternative, so the file is not where it builds on Jev)")
                else:
                    print(f"  {r['slug']}  [{r['status']}]")
        return 0

    todo = [
        e
        for e in catalog
        if "evidence" in e and (not args.only or e["slug"] == args.only)
    ]
    if not todo:
        print("no rows carry evidence yet")
        return 0

    print(f"re-checking {len(todo)} claim(s)\n", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(check, todo))

    # A claim the rate limit kept us from reading is neither a pass nor a
    # failure. Counting it as either would be the false report this avoids.
    skipped = [r for r in results if r["status"] == "skipped"]
    failed = [r for r in results if r["status"] not in ("ok", "skipped")]
    step_summary(
        "## Cited call sites\n\n"
        + f"- checked {len(results) - len(skipped)} of {len(results)} claim(s): "
        + f"{len(failed)} failed, {len(skipped)} skipped (GitHub rate limit)\n"
        + "".join(f"- {line}\n" for line in usage_lines())
    )
    if skipped:
        print(
            f"::warning title=Claims not checked::{len(skipped)} of {len(results)} "
            "cited call sites were not read: GitHub rate limit. They are not failures.",
            file=sys.stderr,
        )
    if args.json:
        print(
            json.dumps(
                {
                    "checked": len(results),
                    "failed": failed,
                    "skipped": skipped,
                    # A text signal per file whose claim held; see --write-signals.
                    "primitive_signals": {
                        r["slug"]: r["primitive_signals"]
                        for r in results
                        if r["status"] == "ok" and r.get("primitive_signals")
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        for r in results:
            mark = "ok  " if r["status"] == "ok" else r["status"].upper()
            shapes = r.get("primitive_signals")
            tail = f"  · primitive shapes: {', '.join(shapes)}" if shapes else ""
            print(f"  {mark:<12} {r['slug']}  {r['detail']}{tail}")
        held = len(results) - len(failed) - len(skipped)
        tail = f"; {len(skipped)} not checked (GitHub rate limit)" if skipped else ""
        print(f"\n{held}/{len(results)} claims still hold{tail}")
        if failed:
            print("\nFailures need a person: an upstream rename is a false positive,")
            print("a removed integration means the row's question_types is now wrong.")
    log_usage()

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
