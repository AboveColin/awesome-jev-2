#!/usr/bin/env python3
"""Write the "What to watch" table in docs/status.md from watch.json.

The status page's dated snapshot ends with the questions it left open. They
used to be five hand-written bullets that never said where anything stood.
watch.json now holds each question and how it is tracked; scripts/watch.py
counts what catalog.json can say, shows a dated, attributed reading for the
rest, and states each recent change against the snapshot before the newest in
history/ (or the newest week of first_seen dates until history/ holds two),
with the dates printed. This writes that table between the page's
`<!-- watch:start -->` and `<!-- watch:end -->` markers; the prose around
them stays hand-written.

Stdlib only, like the rest of scripts/.

Run: python3 scripts/build_watch.py
     python3 scripts/build_watch.py --check    # exit 1 if the table is stale
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import snapshot_stats  # noqa: E402
import watch  # noqa: E402
from _markers import replace_block  # noqa: E402

ROOT = watch.ROOT
STATUS = ROOT / "docs" / "status.md"


def render_status(text: str, spec: dict, catalog: list[dict], history) -> str:
    """docs/status.md with its watch block refilled."""
    return replace_block(text, "watch", watch.render(spec, catalog, history), where="docs/status.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 instead of writing a stale table")
    args = parser.parse_args(argv)
    spec = watch.load()
    catalog = json.loads((ROOT / "catalog.json").read_text())
    found = watch.problems(spec, catalog)
    if found:
        print("error: watch.json cannot be rendered:\n  " + "\n  ".join(found), file=sys.stderr)
        return 1
    history = snapshot_stats.load_history()
    counted = watch.values(spec, catalog)
    summary = (
        f"{len(spec['items'])} questions, counted now: "
        + ", ".join(f"{key} {value}" for key, value in counted.items())
        + f"; {len(history)} snapshot(s) in history/"
    )
    current = STATUS.read_text()
    rendered = render_status(current, spec, catalog, history)
    if rendered == current:
        print(f"docs/status.md's watch table is current ({summary})")
        return 0
    if args.check:
        print(f"error: docs/status.md's watch table is stale; run python3 scripts/build_watch.py ({summary})",
              file=sys.stderr)
        return 1
    STATUS.write_text(rendered)
    print(f"rewrote docs/status.md's watch table ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
