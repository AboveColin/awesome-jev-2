#!/usr/bin/env python3
"""Verify site/catalog.json matches the catalog at the repo root.

The Pages job copies catalog.json into site/ at build time. This guards against
publishing a site that reads a stale or truncated copy — the failure mode where
the README says 40 entries and the site quietly shows 12.

It also holds site/index.html's link-preview block to one of two states. In git
(and after a plain assemble) it must be the placeholder, so a catalogue number
can never be committed there again; after `assemble_site.py --deploy` it must be
exactly the tags the current stats produce, so Pages cannot publish a page whose
link preview is missing or stale.

Run: python3 scripts/check_site_data.py
     python3 scripts/check_site_data.py --deploy    # pages.yml, after assemble --deploy
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from assemble_site import META_PLACEHOLDER, ROOT, RUNTIME_FILES, meta_block, meta_body, stats_payload  # noqa: E402
from check_collections import validate_collections  # noqa: E402

# The site renders these fields unconditionally; a missing one is a blank cell.
REQUIRED = ("slug", "title", "summary", "summary_zh", "url", "kind", "patterns")


def meta_problem(index_html: str, stats: dict, *, deploy: bool) -> str | None:
    """Why site/index.html's `meta` block is wrong for this stage, or None."""
    body = meta_body(index_html)
    if deploy:
        if body != " ".join(meta_block(stats).split()):
            return (
                "site/index.html's link-preview tags are missing or stale for a deploy; "
                "run 'python3 scripts/assemble_site.py --deploy' first"
            )
        return None
    if body != META_PLACEHOLDER:
        return (
            "site/index.html's meta block must hold only the placeholder "
            f"{META_PLACEHOLDER!r}: the link-preview tags are written at deploy, never "
            "committed. If you ran 'assemble_site.py --deploy' locally, restore it with "
            "'git checkout -- site/index.html'"
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="require the link-preview tags written by assemble_site.py --deploy",
    )
    args = parser.parse_args(argv)

    for name in RUNTIME_FILES:
        copy = ROOT / "site" / name
        if not copy.exists():
            print(f"error: site/{name} is missing; the Pages job should copy it in", file=sys.stderr)
            return 1
        if json.loads((ROOT / name).read_text()) != json.loads(copy.read_text()):
            print(f"error: site/{name} differs from {name}", file=sys.stderr)
            return 1
        print(f"site/{name} matches {name}")

    # stats.json is derived, not copied, so it is compared with a recompute.
    stats = ROOT / "site" / "stats.json"
    if not stats.exists() or json.loads(stats.read_text()) != stats_payload():
        print("error: site/stats.json is missing or stale; run assemble_site.py", file=sys.stderr)
        return 1
    print("site/stats.json matches _stats.compute()")

    problem = meta_problem((ROOT / "site" / "index.html").read_text(), stats_payload(), deploy=args.deploy)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    print(
        "site/index.html carries the current link-preview tags"
        if args.deploy
        else "site/index.html carries the link-preview placeholder, as committed"
    )

    catalog = json.loads((ROOT / "site" / "catalog.json").read_text())
    collections = json.loads((ROOT / "site" / "collections.json").read_text())
    errors = validate_collections(collections, catalog)
    if errors:
        for error in errors:
            print(f"error: site/{error}", file=sys.stderr)
        return 1
    print("site/collections.json references valid catalog entries")

    for entry in catalog:
        missing = [field for field in REQUIRED if field not in entry]
        if missing:
            print(
                f"error: entry {entry.get('slug', '?')!r} is missing {missing} "
                "which the site needs to render",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
