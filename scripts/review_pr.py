#!/usr/bin/env python3
"""The review card: check the rows a pull request adds or changes (I03).

A pull request's checkboxes said the summaries were read, the call site was
read, the stars and licence came from the API and whether it was the author's
own project; nothing in CI checked any of it until the weekly jobs ran after
the merge. This script compares catalog.json with the merge base, and runs the
checks in scripts/review_rows.py on each row added or changed: the cited file
still holds the matched strings, the licence and archive status agree with
GitHub, stars are close, the link answers, the pull request's author is not
the project's owner without the row saying so, flags that need a reason have
one, and a keyword classifier's guess. It writes a card: a table and a line
per finding, to stdout and, with --ci, to the job summary (a fork's pull
request shows it too) and as annotations on catalog.json's lines.

It is a second gate that matches text, not a review. Strings present in a file
say nothing about whether the code calls Jev the way the row claims; a
maintainer still reads the call site.

In CI it must not be the pull request's own copy that judges the pull request,
or a pull request could edit the checks it is judged by. lint.yml's `review`
job checks the base commit out into a separate directory and runs that copy
with --tree pointing at the pull request's checkout: everything this script
imports comes from its own directory, and the tree is only read as data.
lint.yml comes from the pull request and passes --ci, --tree and --base, so
keep those three options working.

Advisory while it is new: it exits 0 whatever the card says. --blocking makes
an `error` finding exit 1, for when a fortnight of cards has shown no
systematic false alarm.

Usage:
  python3 scripts/review_pr.py                          # this branch against origin/main
  python3 scripts/review_pr.py --author LOGIN           # also compare LOGIN with each row's owner
  python3 scripts/review_pr.py --base upstream/main --offline --json
  python3 scripts/review_pr.py --ci --tree DIR --base HEAD^1   # lint.yml's review job

GITHUB_TOKEN (locally `GITHUB_TOKEN=$(gh auth token)`) gives the GitHub reads
their own budget; without it GitHub allows 60 requests an hour.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import pathlib
import secrets
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from _github import log_usage, step_summary, usage_lines  # noqa: E402
from check import escape  # noqa: E402
from review_rows import (  # noqa: E402
    CHECKS,
    LABELS,
    LOGIN,
    MARKS,
    RowReview,
    code,
    default_net,
    diff_rows,
    review_rows,
)

DEFAULT_BASE = "origin/main"
CATALOG = "catalog.json"
RETIRED = "retired.json"
# Changes under these paths are tooling, which the card reports but did not run.
TOOLING = ("scripts/", ".github/")
TABLE_ROWS = 200
COMMAND = "python3 scripts/review_pr.py"

ADVISORY_EN = (
    "**Advisory while the card is new: nothing on it fails this check.** "
    "✗ is for the author to fix before merging (and will fail the check once the card counts), "
    "⚠ needs a person's eyes, ℹ is a hint, ✓ passed, and *not checked* is not a pass."
)
BLOCKING_EN = (
    "**✗ fails this check**: it is for the author to fix before merging. "
    "⚠ needs a person's eyes, ℹ is a hint, ✓ passed, and *not checked* is not a pass."
)
GATE_EN = (
    "This card matches text and compares facts with GitHub today. It is a second gate, not a review: "
    "strings present in a file do not show that the code calls Jev the way the row says, "
    "so a maintainer still reads the call site."
)
GATE_ZH = (
    "这张卡只做文本匹配，并把事实与 GitHub 当前数据比对；它是第二道门，不是审核。"
    "文件里有这些字符串，不等于代码按该行所说的方式调用 Jev，维护者仍要亲自读调用点。"
)
ADVISORY_ZH = "目前仅供参考，不会让检查失败。"
MACHINE_ZH = " <sub>(机翻)</sub>"


@dataclasses.dataclass(frozen=True)
class Card:
    base: str  # the merge base the rows were compared with
    author: str | None
    rows: tuple[RowReview, ...]
    removed: tuple[str, ...]
    retired: tuple[str, ...]  # removed rows that are now in retired.json
    notes: tuple[str, ...]
    ran_from: str  # whose scripts judged the rows
    blocking: bool = False  # an error fails the check (--blocking)

    def count(self, level: str) -> int:
        return sum(f.level == level for row in self.rows for f in row.findings)


# ---------------------------------------------------------------------------
# git
# ---------------------------------------------------------------------------


def git(tree: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(tree), *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def merge_base(tree: pathlib.Path, base: str) -> str | None:
    """Where this branch left `base`: rows `base` changed since are not the
    branch's. In CI, on the merge commit, that is the base commit itself."""
    if base.startswith("-"):
        return None  # an option, not a revision
    done = git(tree, "merge-base", base, "HEAD")
    return (done.stdout.strip() or None) if done.returncode == 0 else None


def rows_at(tree: pathlib.Path, rev: str, path: str) -> object:
    done = git(tree, "show", f"{rev}:{path}")
    if done.returncode != 0:
        return []
    return json.loads(done.stdout)


def scripts_commit(base: str) -> str:
    """Which commit the running scripts were checked out from, in words."""
    done = git(SCRIPTS.parent, "rev-parse", "HEAD")
    head = done.stdout.strip() if done.returncode == 0 else ""
    if not head:
        return "a copy outside git"
    if head == base:
        return f"the base commit `{head[:12]}`"
    return f"`{head[:12]}`"


def tooling_changes(tree: pathlib.Path, rev: str) -> list[str]:
    done = git(tree, "diff", "--name-only", rev, "--")
    return [p for p in done.stdout.splitlines() if p.startswith(TOOLING)]


def read_rows(path: pathlib.Path) -> tuple[object, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return [], f"{path.name} could not be read ({type(exc).__name__}); lint says why"


def slug_lines(text: str) -> dict[str, int]:
    """1-based line of each row's `"slug": …` in catalog.json, for annotations."""
    lines = {}
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('"slug": "'):
            try:
                lines.setdefault(json.loads("{" + stripped.rstrip(",") + "}")["slug"], number)
            except ValueError:
                continue
    return lines


# ---------------------------------------------------------------------------
# The card
# ---------------------------------------------------------------------------


def cell_text(text: str) -> str:
    """An outside string in a table cell: a code span, with its bars escaped."""
    return code(text).replace("|", "\\|")


def cell(row: RowReview, check: str) -> str:
    worst = row.worst(check)
    return MARKS[worst] if worst else ""


def heading(row: RowReview) -> str:
    if row.kind == "added":
        return f"{code(row.slug)} — added"
    return f"{code(row.slug)} — changed: " + ", ".join(code(field) for field in row.fields)


def tally(card: Card) -> str:
    added = sum(row.kind == "added" for row in card.rows)
    return (
        f"{added} added, {len(card.rows) - added} changed, {len(card.removed)} removed; "
        f"{card.count('error')} ✗, {card.count('warning')} ⚠, {card.count('skipped')} not checked"
    )


def markdown(card: Card) -> str:
    lines = ["## Review card", ""]
    who = f", opened by {code(card.author)}" if card.author else ""
    lines += [
        f"Rows this pull request adds or changes in `catalog.json`, compared with `{card.base[:12]}`{who}: "
        f"{tally(card)}.",
        "",
        BLOCKING_EN if card.blocking else ADVISORY_EN,
        "",
    ]
    if not card.rows:
        lines += ["No row in `catalog.json` was added or changed.", ""]
    else:
        lines += [
            "| Row | | " + " | ".join(label for _, label in CHECKS) + " |",
            "| --- | --- | " + " | ".join("---" for _ in CHECKS) + " |",
        ]
        for row in card.rows[:TABLE_ROWS]:
            lines.append(f"| {cell_text(row.slug)} | {row.kind} | " + " | ".join(cell(row, key) for key, _ in CHECKS) + " |")
        if len(card.rows) > TABLE_ROWS:
            lines.append(f"| …and {len(card.rows) - TABLE_ROWS} more, in the log | | " + " | ".join("" for _ in CHECKS) + " |")
        lines.append("")
        for row in card.rows[:TABLE_ROWS]:
            lines += details(row)
    lines += [f"- ⚠ {note}" for note in card.notes] + ([""] if card.notes else [])
    if card.removed:
        lines += [removed_line(card), ""]
    lines += [
        "---",
        "",
        f"Checked by {card.ran_from}. {GATE_EN}",
        "",
        GATE_ZH + ("" if card.blocking else ADVISORY_ZH) + MACHINE_ZH,
        "",
        f"Run it yourself: `{COMMAND} --base origin/main"
        + (f" --author {card.author}`" if card.author else " --author <login>`")
        + " (with `GITHUB_TOKEN` set).",
        "",
    ]
    lines += [f"- {line}" for line in usage_lines()]
    return "\n".join(lines) + "\n"


def details(row: RowReview) -> list[str]:
    problems = [f for f in row.findings if f.level != "ok"]
    passed = sorted({LABELS[f.check] for f in row.findings if f.level == "ok"}, key=list(LABELS.values()).index)
    if not row.findings:
        return [f"#### {heading(row)}", "", "No field a check reads changed.", ""]
    lines = [f"#### {heading(row)}", ""]
    lines += [f"- {MARKS[f.level] if f.level != 'skipped' else '–'} **{LABELS[f.check]}**: {f.text}" for f in problems]
    if passed:
        lines.append(f"- ✓ {', '.join(passed)}")
    return lines + [""]


def removed_line(card: Card) -> str:
    retired = [slug for slug in card.removed if slug in card.retired]
    gone = [slug for slug in card.removed if slug not in card.retired]
    parts = []
    if retired:
        parts.append("moved to `retired.json`: " + ", ".join(code(s) for s in retired))
    if gone:
        parts.append(
            "⚠ removed without moving to `retired.json`: " + ", ".join(code(s) for s in gone)
            + " (a dead or wrong row is retired with a `notes` line, not deleted)"
        )
    return "- Removed from `catalog.json`: " + "; ".join(parts) + "."


def console(card: Card) -> str:
    who = f", author {card.author}" if card.author else ""
    lines = [f"review card: compared with {card.base[:12]}{who} ({'blocking' if card.blocking else 'advisory'})"]
    for row in card.rows:
        lines.append(f"  {heading(row).replace('`', '')}")
        if not row.findings:
            lines.append("    (no field a check reads changed)")
        for f in row.findings:
            lines.append(f"    {MARKS[f.level]:<11} {LABELS[f.check]}: {f.text}")
    for note in card.notes:
        lines.append(f"  note: {note}")
    if card.removed:
        lines.append("  " + removed_line(card)[2:])
    lines.append(f"{tally(card)}")
    lines.append(f"checked by {card.ran_from}")
    return "\n".join(lines)


def annotations(card: Card, lines: dict[str, int]) -> list[str]:
    """Workflow commands putting each ✗ and ⚠ on its row's line in catalog.json.
    While advisory, a ✗ is a warning annotation, not an error."""
    out = []
    for row in card.rows:
        for f in row.findings:
            if f.level not in ("error", "warning"):
                continue
            command = {"error": "error" if card.blocking else "warning", "warning": "notice"}[f.level]
            place = f"file={CATALOG},line={lines[row.slug]}," if row.slug in lines else ""
            title = escape(f"Review card: {code(row.slug)[1:-1]} ({LABELS[f.check]})", prop=True)
            out.append(f"::{command} {place}title={title}::{escape(f.text)}")
    return out


def as_json(card: Card) -> str:
    data = dataclasses.asdict(card)
    data["errors"], data["warnings"] = card.count("error"), card.count("warning")
    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------


def author_from(value: str) -> tuple[str | None, str | None]:
    value = (value or "").strip()
    if not value:
        return None, None
    if not LOGIN.match(value):
        return None, "the pull-request author given is not a GitHub login, so it was not compared"
    return value, None


def build(tree: pathlib.Path, base: str, author: str | None, net, offline: str) -> Card | None:
    rev = merge_base(tree, base)
    if rev is None:
        return None
    notes: list[str] = []
    try:
        old = rows_at(tree, rev, CATALOG)
    except ValueError:
        old = []
        notes.append(f"the base's {CATALOG} does not parse, so every row counts as added")
    new, problem = read_rows(tree / CATALOG)
    if problem:
        notes.append(problem)
    retired, _ = read_rows(tree / RETIRED)
    changes, removed, problems = diff_rows(old, new)
    notes += problems
    reviews, more = review_rows(changes, author=author, net=net, offline=offline)
    notes += more
    ran_from = "this checkout's own `scripts/` (a local run)"
    if SCRIPTS.parent != tree.resolve():
        ran_from = f"the `scripts/` of {scripts_commit(rev)}, not this pull request's"
        tooling = tooling_changes(tree, rev)
        if tooling:
            shown = ", ".join(code(path) for path in tooling[:10]) + (" …" if len(tooling) > 10 else "")
            notes.append(
                f"This pull request also changes {len(tooling)} file(s) under `scripts/` or `.github/` ({shown}). "
                "They did not judge its rows; the `catalog` job runs them, so a person reads them."
            )
    retired_slugs = {r.get("slug") for r in retired if isinstance(r, dict)} if isinstance(retired, list) else set()
    return Card(
        base=rev, author=author, rows=tuple(reviews), removed=tuple(removed),
        retired=tuple(s for s in removed if s in retired_slugs), notes=tuple(notes), ran_from=ran_from,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default=DEFAULT_BASE, metavar="REV", help=f"compare with the merge base of REV and HEAD (default {DEFAULT_BASE})")
    parser.add_argument("--tree", default=str(SCRIPTS.parent), metavar="DIR", help="the checkout whose catalog.json is reviewed (default: this one)")
    parser.add_argument("--author", default=None, metavar="LOGIN", help="the pull request's author (default: $PR_AUTHOR)")
    parser.add_argument("--offline", action="store_true", help="skip the checks that read GitHub or the link")
    parser.add_argument("--json", action="store_true", help="print the card as JSON")
    parser.add_argument("--ci", action="store_true", help="also write the card to $GITHUB_STEP_SUMMARY and annotate catalog.json")
    parser.add_argument("--blocking", action="store_true", help="exit 1 when any finding is an error (the card is advisory without it)")
    args = parser.parse_args(argv)

    tree = pathlib.Path(args.tree).resolve()
    author, author_note = author_from(args.author if args.author is not None else os.environ.get("PR_AUTHOR", ""))
    net = None if args.offline else default_net()
    card = build(tree, args.base, author, net, "--offline")
    if card is None:
        message = f"review card not run: {args.base} is not a commit in {tree}; fetch it, or pass --base <remote>/main"
        print(message, file=sys.stderr)
        if args.ci:
            step_summary(f"## Review card\n\nNot run: `{args.base}` is not a commit in this checkout.\n")
        return 2 if args.blocking else 0
    card = dataclasses.replace(
        card, blocking=args.blocking, notes=card.notes + ((author_note,) if author_note else ())
    )

    report = as_json(card) if args.json else console(card)
    if args.ci:
        # The log quotes the pull request's own strings (a slug starts a line),
        # and the runner takes a line starting with `::` once its leading
        # spaces are dropped (or holding the older `##[` form) for a workflow
        # command. Commands stay off while the card prints; the token that
        # turns them back on is random, so no row can name it. The annotations
        # below come after it.
        token = secrets.token_hex(16)
        print(f"::stop-commands::{token}")
        print(report)
        print(f"::{token}::", flush=True)
    else:
        print(report)
    if args.ci:
        step_summary(markdown(card))
        text = (tree / CATALOG).read_text(encoding="utf-8", errors="replace") if (tree / CATALOG).exists() else ""
        for line in annotations(card, slug_lines(text)):
            print(line, file=sys.stderr if args.json else sys.stdout)
    if net is not None:
        log_usage()
    return 1 if args.blocking and card.count("error") else 0


if __name__ == "__main__":
    sys.exit(main())
