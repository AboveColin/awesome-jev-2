#!/usr/bin/env python3
"""The discovery issue's description: every candidate, and where it stands.

The weekly `discover` run posts what it found each week as a comment on one
open issue labelled `discovery`. Comments pile up, nothing in them changes
when a candidate is catalogued or declined, and ticking a box in a bot's
comment needs write access to this repository. So the issue's description is
this queue instead, rewritten by the same run from files in the repository:

  .discover/seen.json  which repositories a script found calling Jev (calls-jev)
  catalog.json         catalogued: a row's url or repo is that repository
  retired.json         catalogued, and retired since
  docs/declined.txt    a person read it and decided against it

Nothing here is stored. Each candidate's state is derived from those files on
every run, and a person's decision only ever comes from catalog.json,
retired.json or docs/declined.txt, never from the verdict file. The same files
give the same text byte for byte, so the workflow edits the issue only when
something changed; the only dates in it are each candidate's latest read.

A candidate catalogued under another name than the one the sibling lists cite
(a renamed or transferred repository) stays "to read": the verdict file keeps
the cited name, and nothing here asks GitHub which name is current.

Usage:
  python3 scripts/queue_sync.py               # print the description
  python3 scripts/queue_sync.py --out FILE    # write it to FILE
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import discover_seen  # noqa: E402
from _github import repo_of  # noqa: E402
from discover_candidates import CLAIM_EN, CLAIM_ZH, COMMAND, inert, parse_declined  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
# The site's address (readme.rows.SITE; a test holds them equal). A row's
# permalink there is ?lang=en#<slug>.
SITE = "https://kydlikebtc.github.io/awesome-jev/"
PROPOSED = discover_seen.PROPOSED
# In the order the description lists them.
STATES = ("open", "catalogued", "retired", "declined")
# GitHub refuses an issue body over 65,536 characters. The caps start here and
# are halved until the text fits under MAX_CHARS.
MAX_CHARS = 60_000
OPEN_SHOWN = 300
DONE_SHOWN = 150

HEADER = (
    "<!-- Written by scripts/queue_sync.py from .discover/seen.json, catalog.json, "
    "retired.json and docs/declined.txt. The weekly discover run rewrites this "
    "description, so an edit here is lost. -->"
)
INTRO_EN = (
    "The discovery queue: every repository the weekly `discover` run found calling "
    "Jev, and where it stands. A ticked box was catalogued, a struck-through one "
    "declined. The state comes from `catalog.json`, `retired.json` and "
    "`docs/declined.txt`, so merging the pull request that adds the row or the "
    "decline is what ticks a box, and this description catches up at the next "
    "weekly run. Each week's new candidates, with their call sites, are in the "
    "comments below."
)
# Model-written, so marked the way the README marks machine Chinese.
INTRO_ZH = (
    "发现队列：每周 `discover` 运行找到的、代码调用 Jev 的每个仓库，以及它目前的状态。"
    "打勾表示已收录，删除线表示已拒收。状态取自 `catalog.json`、`retired.json` 和 "
    "`docs/declined.txt`，所以合并添加该行或拒收它的 pull request 才会打勾，本描述在下一次"
    "每周运行时更新。每周的新候选及其调用点见下方评论。本描述里的中文（包括下面的标题和计数）"
    "都由模型写成。 <sub>(机翻)</sub>"
)
# Each list's heading, in both languages (the Chinese is model-written, as
# INTRO_ZH says).
TITLES = {
    "open": ("To read", "待读"),
    "catalogued": ("Catalogued", "已收录"),
    "declined": ("Declined", "已拒收"),
    "retired": ("Catalogued and since retired", "收录后已退役"),
}


@dataclasses.dataclass(frozen=True)
class Candidate:
    repo: str  # owner/name, lower-case, as the verdict file keys it
    read_on: str  # the script's latest read of it
    state: str  # one of STATES
    rows: tuple[str, ...] = ()  # catalogue slugs, when catalogued or retired
    reason: str = ""  # the reason given, when declined


def rows_by_repo(rows: list) -> dict[str, tuple[str, ...]]:
    """owner/name, lower-cased, to the slugs of every row that links to it."""
    found: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        if not isinstance(row, dict):
            continue
        repo = repo_of(row)
        if repo and isinstance(row.get("slug"), str):
            found[repo.lower()].add(row["slug"])
    return {repo: tuple(sorted(slugs)) for repo, slugs in found.items()}


def derive(
    seen: dict[str, dict], catalog: list, retired: list, declined: dict[str, str]
) -> list[Candidate]:
    """Every repository whose verdict is calls-jev, with its state. A row in
    catalog.json wins over one in retired.json, and either over a decline."""
    listed, gone = rows_by_repo(catalog), rows_by_repo(retired)
    out = []
    for repo in sorted(seen):
        entry = seen[repo]
        if entry["verdict"] != PROPOSED:
            continue
        if repo in listed:
            out.append(Candidate(repo, entry["on"], "catalogued", rows=listed[repo]))
        elif repo in gone:
            out.append(Candidate(repo, entry["on"], "retired", rows=gone[repo]))
        elif repo in declined:
            out.append(Candidate(repo, entry["on"], "declined", reason=declined[repo]))
        else:
            out.append(Candidate(repo, entry["on"], "open"))
    return out


def link(repo: str) -> str:
    return f"[{repo}](https://github.com/{repo})"


def line_for(c: Candidate) -> str:
    if c.state == "open":
        # The script's read, not a person's: nobody has read an open one yet.
        return f"- [ ] {link(c.repo)} · read by script {c.read_on} · `{COMMAND.format(slug=c.repo)}`"
    if c.state == "catalogued":
        rows = ", ".join(f"[`{slug}`]({SITE}?lang=en#{slug})" for slug in c.rows)
        return f"- [x] {link(c.repo)} → {rows}"
    if c.state == "retired":
        rows = ", ".join(f"`{slug}`" for slug in c.rows)
        return f"- [x] {link(c.repo)} → {rows}, since retired (`retired.json`)"
    reason = inert(c.reason, 160) if c.reason else "no reason given"
    return f"- [x] ~~{link(c.repo)}~~ · declined: {reason}"


def more(n: int) -> list[str]:
    if not n:
        return []
    return [f"- …and {n} more, not shown to keep this description under GitHub's limit. "
            f"另有 {n} 个未列出，以免本描述超出 GitHub 的长度上限。"]


def title(state: str) -> str:
    return " · ".join(TITLES[state])


def done_section(state: str, items: list[Candidate], shown: int) -> list[str]:
    if not items:
        return []
    lines = ["<details>", f"<summary>{title(state)} ({len(items)})</summary>", ""]
    lines += [line_for(c) for c in items[:shown]] + more(len(items) - min(shown, len(items)))
    return lines + ["", "</details>", ""]


def render(candidates: list[Candidate], *, open_shown: int = OPEN_SHOWN, done_shown: int = DONE_SHOWN) -> str:
    """The description. Waiting candidates oldest read first, the rest by name."""
    by = {state: [c for c in candidates if c.state == state] for state in STATES}
    by["open"].sort(key=lambda c: (c.read_on, c.repo))
    lines = [HEADER, "", INTRO_EN, "", INTRO_ZH, ""]
    lines += [
        f"**{len(by['open'])}** to read · **{len(by['catalogued'])}** catalogued · "
        f"**{len(by['declined'])}** declined · **{len(by['retired'])}** catalogued and since retired",
        "",
        " · ".join(f"{TITLES[s][1]} **{len(by[s])}**" for s in ("open", "catalogued", "declined", "retired"))
        + " <sub>(机翻)</sub>",
        "",
    ]
    if by["open"]:
        lines += [CLAIM_EN, "", CLAIM_ZH, "", f"### {title('open')}", ""]
        lines += [line_for(c) for c in by["open"][:open_shown]]
        lines += more(len(by["open"]) - min(open_shown, len(by["open"]))) + [""]
    elif candidates:
        lines += ["Nothing to read: every candidate so far is catalogued or declined.", "",
                  "没有待读的候选：迄今每个候选都已收录或已拒收。 <sub>(机翻)</sub>", ""]
    else:
        lines += ["No candidate yet: `.discover/seen.json` records no repository found calling Jev.", "",
                  "还没有候选：`.discover/seen.json` 没有记录任何被发现调用 Jev 的仓库。 <sub>(机翻)</sub>", ""]
    lines += done_section("catalogued", by["catalogued"], done_shown)
    lines += done_section("declined", by["declined"], done_shown)
    lines += done_section("retired", by["retired"], done_shown)
    return "\n".join(lines).rstrip("\n") + "\n"


def body(candidates: list[Candidate]) -> str:
    """render(), with the caps halved until the text fits GitHub's limit."""
    open_shown, done_shown = OPEN_SHOWN, DONE_SHOWN
    while True:
        text = render(candidates, open_shown=open_shown, done_shown=done_shown)
        if len(text) <= MAX_CHARS or not (open_shown or done_shown):
            return text
        open_shown, done_shown = open_shown // 2, done_shown // 2


def load_rows(path: pathlib.Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path.name}: top level is not an array")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the discovery issue's description.")
    parser.add_argument("--out", default="", metavar="FILE", help="write it here instead of stdout")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)  # tests
    args = parser.parse_args(argv)
    root = pathlib.Path(args.root)
    try:
        catalog = load_rows(root / "catalog.json")
        retired = load_rows(root / "retired.json")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    declined_file = root / "docs" / "declined.txt"
    declined = parse_declined(declined_file.read_text(encoding="utf-8")) if declined_file.exists() else {}
    seen, dropped = discover_seen.load(root / ".discover" / "seen.json", today=dt.date.today())
    discover_seen.report_dropped(".discover/seen.json", dropped)

    candidates = derive(seen, catalog, retired, declined)
    text = body(candidates)
    counts = collections.Counter(c.state for c in candidates)
    print(
        f"discovery queue: {len(candidates)} candidate(s) among {len(seen)} verdict(s): "
        + ", ".join(f"{counts[state]} {state}" for state in STATES),
        file=sys.stderr,
    )
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(text)} characters)", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
