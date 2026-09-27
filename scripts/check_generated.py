#!/usr/bin/env python3
"""Decide what a regenerated tree means for this event (I01).

Since 2026-09-27 a pull request only has to change the sources: catalog.json
and the other root JSON files. Every lint run regenerates all generated files
first (regenerate.py); this then compares the result with what is committed,
file by file, and decides by event:

  pr      A pull request. Each generated file must either be untouched by the
          pull request — the same at its head as at the merge base — or be
          byte-identical to what the generators produce from the tree CI
          checked out. Untouched and stale is fine: the bot regenerates it on
          main after the merge. Touched and different fails: that is a hand
          edit, or output generated from an older catalogue, and on main the
          bot would silently overwrite it. Every file's verdict goes to
          $GITHUB_STEP_SUMMARY.
  push    main, after a merge. Drift is expected and is not a failure. It is
          reported, and written to $GITHUB_OUTPUT as drift=true for lint.yml's
          regenerate job, which commits it.
  strict  Anything else: a workflow_dispatch (metadata.yml dispatches one after
          it lands), or a person before committing. Any drift fails.

Drift is read with `git status`, untracked files included, not `git diff`: the
pattern pages are created and deleted as patterns gain or lose entries, and a
diff cannot see a page that nobody committed.

Stdlib only, like the rest of scripts/.

Run: python3 scripts/regenerate.py && python3 scripts/check_generated.py strict
     python3 scripts/check_generated.py pr --base origin/main   # what CI will say about a branch
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from regenerate import OUTPUTS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX = "python3 scripts/regenerate.py"
DIFF_LINES = 40


def git(args: list[str], cwd: pathlib.Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


def touched(base: str, head: str, cwd: pathlib.Path) -> set[str]:
    """Generated paths the pull request changes: head against the merge base
    of base and head, so commits that reached main after the branch was cut
    are not counted as the pull request's."""
    merge_base = git(["merge-base", base, head], cwd).strip()
    out = git(["diff", "--name-only", "--no-renames", "-z", merge_base, head, "--", *OUTPUTS], cwd)
    return {path for path in out.split("\0") if path}


def drifted(cwd: pathlib.Path) -> dict[str, str]:
    """Generated paths whose regenerated content differs from HEAD, with why."""
    out = git(
        ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames", "--", *OUTPUTS],
        cwd,
    )
    reasons = {}
    for record in out.split("\0"):
        if not record:
            continue
        code, path = record[:2], record[3:]
        if code == "??":
            reasons[path] = "the generators produce this file, and it is not committed"
        elif "D" in code:
            reasons[path] = "the generators no longer produce this file, and it is committed"
        else:
            reasons[path] = "committed content differs from what the generators produce"
    return reasons


@dataclasses.dataclass(frozen=True)
class Verdict:
    matches: list[str]  # changed by the pull request, exactly as generated
    differs: list[str]  # changed by the pull request, not as generated
    stale: list[str]  # untouched by the pull request, regenerated on main after merge


def classify(changed: set[str], drift: set[str]) -> Verdict:
    return Verdict(
        matches=sorted(changed - drift),
        differs=sorted(changed & drift),
        stale=sorted(drift - changed),
    )


def excerpt(path: str, cwd: pathlib.Path) -> str:
    """The start of the difference, committed (-) against generated (+)."""
    try:
        diff = git(["diff", "--no-color", "-U1", "HEAD", "--", path], cwd)
    except subprocess.CalledProcessError:
        return ""
    lines = diff.splitlines()
    more = len(lines) - DIFF_LINES
    return "\n".join(lines[:DIFF_LINES] + ([f"... {more} more lines"] if more > 0 else []))


def pr_report(verdict: Verdict, reasons: dict[str, str], cwd: pathlib.Path) -> str:
    out = ["## Generated files in this pull request", ""]
    if not (verdict.matches or verdict.differs):
        out.append("This pull request changes no generated file. Nothing to check.")
    if verdict.matches:
        out += ["Changed, and exactly what the generators produce:", ""]
        out += [f"- `{path}`" for path in verdict.matches]
    if verdict.differs:
        out += [
            "",
            "**Changed, but not what the generators produce** — these fail the check:",
            "",
        ]
        for path in verdict.differs:
            out.append(f"- `{path}`: {reasons[path]}")
        out += [
            "",
            "Generated files are optional in a pull request. Either drop your changes to them",
            "(`git checkout origin/main -- <file>`, or delete a page you added) and let the bot",
            f"regenerate them on `main` after the merge, or run `{FIX}` and commit",
            "exactly what it writes. To change what they say, edit `catalog.json` or the",
            "generator in `scripts/`, never the output.",
        ]
        for path in verdict.differs:
            diff = excerpt(path, cwd)
            if diff:
                out += ["", f"<details><summary><code>{path}</code>: committed (-) against generated (+)</summary>", ""]
                out += ["```diff", diff, "```", "", "</details>"]
    if verdict.stale:
        out += [
            "",
            f"Left untouched, and regenerated on `main` by the bot after the merge ({len(verdict.stale)}):",
            "",
        ]
        out += [f"- `{path}`" for path in verdict.stale]
    return "\n".join(out) + "\n"


def append(env: str, text: str) -> None:
    path = os.environ.get(env)
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(text)


def run_pr(base: str, head: str, cwd: pathlib.Path) -> int:
    reasons = drifted(cwd)
    verdict = classify(touched(base, head, cwd), set(reasons))
    report = pr_report(verdict, reasons, cwd)
    append("GITHUB_STEP_SUMMARY", report)
    print(report)
    print(
        f"pull request changes {len(verdict.matches) + len(verdict.differs)} generated files: "
        f"{len(verdict.matches)} as generated, {len(verdict.differs)} not; "
        f"{len(verdict.stale)} untouched files will be regenerated on main after the merge"
    )
    for path in verdict.differs:
        print(f"::error file={path},title=Generated file edited::{path}: {reasons[path]}. Drop the change, or run {FIX}.")
    return 1 if verdict.differs else 0


def run_push(cwd: pathlib.Path) -> int:
    reasons = drifted(cwd)
    append("GITHUB_OUTPUT", f"drift={'true' if reasons else 'false'}\n")
    if not reasons:
        print("every generated file on main is current")
        return 0
    lines = [f"- `{path}`: {why}" for path, why in sorted(reasons.items())]
    append(
        "GITHUB_STEP_SUMMARY",
        "## Generated files to regenerate on main\n\n"
        f"{len(reasons)} generated files differ from what this commit's sources produce. "
        "That is expected after a merge; the `regenerate` job commits them.\n\n" + "\n".join(lines) + "\n",
    )
    print(f"{len(reasons)} generated files differ from this commit's sources; the regenerate job commits them:")
    print("\n".join(lines))
    return 0


def run_strict(cwd: pathlib.Path) -> int:
    reasons = drifted(cwd)
    if not reasons:
        print("every generated file is current")
        return 0
    lines = [f"  {path}: {why}" for path, why in sorted(reasons.items())]
    print(f"::error::{len(reasons)} generated files are out of date with the sources.")
    print("\n".join(lines))
    print(
        f"Run '{FIX}' and commit everything it rewrote, including pattern pages it created or "
        "deleted. On main, the regenerate job does this after every push."
    )
    return 1


def main(argv: list[str] | None = None, cwd: pathlib.Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    modes = parser.add_subparsers(dest="mode", required=True)
    pr = modes.add_parser("pr", help="a pull request: touched generated files must be exactly as generated")
    pr.add_argument("--base", required=True, help="the branch the pull request targets (CI: HEAD^1)")
    pr.add_argument("--head", default="HEAD", help="the pull request's head (CI: HEAD^2; default HEAD)")
    modes.add_parser("push", help="main after a merge: report drift for the regenerate job")
    modes.add_parser("strict", help="fail on any drift")
    args = parser.parse_args(argv)

    try:
        if args.mode == "pr":
            return run_pr(args.base, args.head, cwd)
        if args.mode == "push":
            return run_push(cwd)
        return run_strict(cwd)
    except subprocess.CalledProcessError as exc:
        print(f"error: git {' '.join(exc.cmd[1:])} failed: {exc.stderr.strip()}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
