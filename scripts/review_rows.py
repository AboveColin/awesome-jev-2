"""The checks behind the pull-request review card (scripts/review_pr.py).

A pull request that adds or changes rows in catalog.json used to be judged by
its own checkboxes: nothing in CI read a new row's cited file, asked GitHub
for its licence or looked at its link until the weekly jobs ran after the
merge. Each row a pull request adds or changes now gets six checks:

  call-site        verify_claims.check(): every evidence.matched string is in
                   the cited file, the question the weekly `claims` job asks;
                   a row claiming primitives, or with code in a GitHub
                   repository, cites a file or says in evidence_none why not
  repository       refresh_metadata.fetch(): repo_license and the archived
                   flag agree with GitHub exactly; stars within
                   max(STAR_SLACK, STAR_SHARE of GitHub's count), since stars
                   drift; a one-commit repository carries `single-commit`
  link             check_links.fetch_status(): the url answers 2xx
  self-submission  the pull request's author against the repository's owner
                   and the row's recorded author
  flag-notes       a flag that needs a reason has a notes line
  classification   discover_candidates.classify() on the summary, as a hint

An added row gets all six; a changed row only those reading a field that
changed (READS), and never the classification hint.

Each check returns Findings at one of five levels. `error`: a person fixes it
before merging, and it fails the card once the card stops being advisory.
`warning`: a person looks. `info`: a hint. `ok`: passed. `skipped`: could not
be checked (offline, a rate limit, a row too malformed to read) — never a pass.
A text match is a second gate, not a review: CONTRIBUTING.md says so.

Every string taken from a row or from GitHub is made inert before it enters a
finding — a code span without backticks, no line breaks, no @-mention —
because findings become Markdown in a job summary and workflow commands in a
log.

The three checks that read the network take a Net, so tests can pass a fake
one; default_net() wires in the functions the weekly jobs use.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _github import SELF, RateLimited, api_get, repo_of  # noqa: E402
from discover_candidates import classify, code_span, inert  # noqa: E402
from lint import FLAGS_NEEDING_NOTES, SELF_SUBMISSION_FLAG, SELF_SUBMISSION_SOURCE  # noqa: E402

# Most severe first; a table cell shows the worst of a check's findings.
LEVELS = ("error", "warning", "skipped", "info", "ok")
MARKS = {"error": "✗", "warning": "⚠", "skipped": "not checked", "info": "ℹ", "ok": "✓"}

CHECKS = (
    ("call-site", "Call site"),
    ("repository", "Repository"),
    ("link", "Link"),
    ("self-submission", "Author"),
    ("flag-notes", "Flag notes"),
    ("classification", "Kind / patterns"),
)
LABELS = dict(CHECKS)
NETWORK = frozenset({"call-site", "repository", "link"})

# The fields each check reads. A changed row gets a check only when one of
# them changed; self-submission runs on every row and classification only on
# added ones (see review_row).
READS = {
    "call-site": frozenset({"evidence", "evidence_none", "question_types", "has_code", "url", "repo"}),
    "repository": frozenset({"url", "repo", "stars", "repo_license", "flags"}),
    "link": frozenset({"url"}),
    "flag-notes": frozenset({"flags", "notes"}),
}

# Stars move every day, so only a count further off than this is worth a
# person's look: 1 against 0 is noise, 879 against 888 is a week.
STAR_SLACK = 5
STAR_SHARE = 0.10

# A GitHub login, or an app's `name[bot]`.
LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})(?:\[bot\])?$")
GITHUB_USER_URL = re.compile(r"^https://github\.com/([^/?#]+)/?$", re.I)


@dataclasses.dataclass(frozen=True)
class Finding:
    check: str  # a key of CHECKS
    level: str  # one of LEVELS
    text: str  # Markdown, every outside string already made inert


@dataclasses.dataclass(frozen=True)
class Change:
    slug: str
    kind: str  # "added" | "changed"
    row: dict
    fields: frozenset[str]  # the fields that changed; every field for an added row


@dataclasses.dataclass(frozen=True)
class RowReview:
    slug: str
    kind: str
    fields: tuple[str, ...]
    findings: tuple[Finding, ...]

    def worst(self, check: str | None = None) -> str | None:
        levels = {f.level for f in self.findings if check is None or f.check == check}
        return next((level for level in LEVELS if level in levels), None)


@dataclasses.dataclass(frozen=True)
class Net:
    """What the network checks ask, one function each."""

    claim: Callable[[dict], dict]  # verify_claims.check
    facts: Callable[[dict], dict | None]  # refresh_metadata.fetch
    commits: Callable[[str], int | None]  # commits on the default branch, counted to 2
    link: Callable[[str], tuple[int, str]]  # check_links.fetch_status


def commit_count(repo: str) -> int | None:
    """0, 1 or 2 (meaning two or more) commits on the default branch; None
    when GitHub did not say (an empty repository answers 409)."""
    data = api_get(f"/repos/{repo}/commits?per_page=2")
    return len(data) if isinstance(data, list) else None


def default_net() -> Net:
    import check_links
    import refresh_metadata
    import verify_claims

    return Net(
        claim=verify_claims.check,
        facts=refresh_metadata.fetch,
        commits=commit_count,
        link=check_links.fetch_status,
    )


def code(text: object) -> str:
    """An outside string as inline code: no backtick can end the span early."""
    return f"`{code_span(str(text))}`"


def said(text: object, limit: int = 160) -> str:
    """An outside string as plain text: one line, no @-mention, no table break,
    and no backtick to open a code span that swallows the rest of the line."""
    return inert(str(text), limit).replace("`", "'")


def login_of(value: object) -> str | None:
    """A GitHub login from `name`, `@name` or a github.com profile URL."""
    text = str(value or "").strip()
    match = GITHUB_USER_URL.match(text)
    if match:
        text = match.group(1)
    text = text.removeprefix("@")
    return text.lower() if LOGIN.match(text) else None


def people(row: dict) -> dict[str, str]:
    """The GitHub accounts a row names, lower-cased, and what each is."""
    found: dict[str, str] = {}
    author = row.get("author") if isinstance(row.get("author"), dict) else {}
    for value, role in (
        (author.get("url"), "the row's `author.url`"),
        (author.get("handle"), "the row's `author.handle`"),
    ):
        login = login_of(value) if value else None
        if login:
            found[login] = role
    repo = repo_of(row)
    if repo:
        owner = login_of(repo.split("/", 1)[0])
        if owner:
            found[owner] = f"the owner of {code(repo)}"
    return found


# ---------------------------------------------------------------------------
# The rows a pull request adds or changes
# ---------------------------------------------------------------------------


def by_slug(rows: object, label: str) -> tuple[dict[str, dict], list[str]]:
    """Rows keyed by slug, and what could not be keyed. lint fails those rows;
    the card only says it left them out."""
    keyed: dict[str, dict] = {}
    problems: list[str] = []
    if not isinstance(rows, list):
        return keyed, [f"{label} is not a JSON array; lint says why"]
    for index, row in enumerate(rows):
        slug = row.get("slug") if isinstance(row, dict) else None
        if not isinstance(slug, str) or not slug:
            problems.append(f"{label} row {index} has no slug and was left out; lint says why")
        elif slug in keyed:
            problems.append(f"{label} names {code(slug)} twice; the last one was reviewed, and lint fails it")
            keyed[slug] = row
        else:
            keyed[slug] = row
    return keyed, problems


def diff_rows(old: object, new: object) -> tuple[list[Change], list[str], list[str]]:
    """(changes, removed slugs, problems). Rows are matched by slug, so moving a
    row changes nothing; added rows come first, each group in slug order."""
    before, _ = by_slug(old, "the base's catalog.json")
    after, problems = by_slug(new, "catalog.json")
    added = [Change(slug, "added", row, frozenset(row)) for slug, row in sorted(after.items()) if slug not in before]
    changed = []
    for slug, row in sorted(after.items()):
        if slug in before and row != before[slug]:
            fields = frozenset(k for k in set(row) | set(before[slug]) if row.get(k) != before[slug].get(k))
            changed.append(Change(slug, "changed", row, fields))
    removed = sorted(slug for slug in before if slug not in after)
    return added + changed, removed, problems


# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------


def check_call_site(row: dict, net: Net | None, reason: str) -> list[Finding]:
    key = "call-site"
    evidence = row.get("evidence")
    if not evidence:
        if row.get("evidence_none"):
            return [Finding(key, "info", f"`evidence_none` is {code(row['evidence_none'])}: no file to re-read.")]
        if row.get("question_types"):
            return [Finding(
                key, "error",
                "`question_types` claims primitives but the row cites no call site: add `evidence` "
                f"(`python3 scripts/verify_claims.py --discover --only {code_span(row.get('slug', ''))}` "
                "proposes one) or `evidence_none` saying why there is no file.",
            )]
        # lint.py fails this too (since 2026-09-27); the card says what to do.
        if row.get("has_code") and repo_of(row):
            return [Finding(
                key, "error",
                "`has_code` is true and the repository is on GitHub, but the row cites no file: add "
                f"`evidence` (`python3 scripts/verify_claims.py --discover --only {code_span(row.get('slug', ''))}` "
                "proposes one), `evidence_none` saying why no file can be cited, or `has_code: false` "
                "if the link holds no code.",
            )]
        return []
    if net is None:
        return [Finding(key, "skipped", f"The cited file was not read: {reason}.")]
    repo = repo_of(row) or "?"
    path = evidence.get("path", "") if isinstance(evidence, dict) else ""
    where = code(f"{repo}:{path}")
    result = net.claim(row)
    status = result.get("status")
    if status == "ok":
        return [Finding(key, "ok", f"Every `evidence.matched` string is in {where}.")]
    if status == "skipped":
        return [Finding(key, "skipped", f"{where} was not read: GitHub rate limit.")]
    if status == "claim-gone":
        return [Finding(
            key, "error",
            f"{where} does not contain every `evidence.matched` string. Copy them from the file "
            "exactly as it reads on the default branch.",
        )]
    if status == "path-gone":
        return [Finding(
            key, "error",
            f"There is no {where} on the default branch: a typo, or the file moved upstream since the "
            "row was written (a person tells which).",
        )]
    if status == "repo-gone":
        return [Finding(key, "error", f"GitHub has no repository {code(repo)} to read the call site from.")]
    if status == "no-repo":
        return [Finding(key, "error", "`evidence` needs a GitHub repository in `url` or `repo` to re-read it from.")]
    return [Finding(key, "skipped", f"The claim check answered {code(status)}.")]


def check_repository(row: dict, fields: frozenset[str], added: bool, net: Net | None, reason: str) -> list[Finding]:
    key = "repository"
    repo = repo_of(row)
    if not repo or repo.lower() == SELF.lower():
        return []  # not a GitHub repository, or one of this repository's own examples
    if net is None:
        return [Finding(key, "skipped", f"GitHub was not asked about {code(repo)}: {reason}.")]
    fresh = net.facts(row)
    if not fresh:
        return []
    where = code(repo)
    state = fresh.get("state")
    if state == "skipped":
        return [Finding(key, "skipped", f"GitHub was not asked about {where}: rate limit.")]
    if state == "gone":
        return [Finding(key, "error", f"GitHub has no repository {where}: deleted, private or mistyped.")]
    if state == "blocked":
        return [Finding(
            key, "warning",
            f"GitHub refuses to serve {where} ({said(fresh.get('detail', ''))}); a person decides whether it belongs here.",
        )]

    def wants(field: str) -> bool:
        return added or bool(fields & {field, "url", "repo"})

    out: list[Finding] = []
    compared: list[str] = []
    full = fresh.get("full_name") or repo
    if full.lower() != repo.lower():
        out.append(Finding(key, "warning", f"GitHub redirects {where} to {code(full)}: point `url` and `repo` at the new name."))
    flags = row.get("flags") or []
    if wants("repo_license"):
        compared.append("licence")
        have, now = row.get("repo_license"), fresh.get("repo_license")
        why = {"unknown": " (no LICENSE file: `unknown`, with the `no-license` flag)",
               "NOASSERTION": " (a LICENSE file GitHub cannot identify)"}.get(now, "")
        if have is None:
            out.append(Finding(key, "warning", f"The row has no `repo_license`; GitHub says {code(now)}{why}."))
        elif have != now:
            out.append(Finding(key, "error", f"`repo_license` is {code(have)}, GitHub says {code(now)}{why}."))
    if wants("flags"):
        compared.append("archive status")
        if fresh.get("archived") and "archived" not in flags:
            out.append(Finding(key, "error", f"GitHub marks {where} archived; the row needs the `archived` flag."))
        elif not fresh.get("archived") and "archived" in flags:
            out.append(Finding(key, "error", f"The row is flagged `archived`, but GitHub does not mark {where} archived."))
    if wants("stars"):
        compared.append("stars")
        have, now = row.get("stars"), fresh.get("stars")
        if have is None:
            out.append(Finding(key, "warning", f"The row has no `stars`; GitHub counts {now}."))
        elif isinstance(have, int) and isinstance(now, int) and abs(have - now) > max(STAR_SLACK, STAR_SHARE * now):
            out.append(Finding(
                key, "warning",
                f"`stars` is {have}, GitHub counts {now} today: more than {STAR_SLACK} or "
                f"{STAR_SHARE:.0%} apart. Take the count from the API, not a badge.",
            ))
    if wants("flags"):
        found, counted = single_commit(key, repo, flags, net, known=fresh.get("commits"))
        if counted:
            compared.append("commit count")
        out += found
    if not any(f.level in ("error", "warning") for f in out):
        out.append(Finding(key, "ok", f"{where} agrees with GitHub on {', '.join(compared) or 'its name'}."))
    return out


def single_commit(
    key: str, repo: str, flags: list, net: Net, *, known: object = None
) -> tuple[list[Finding], bool]:
    """The finding, if any, and whether the commits were counted at all: an
    uncounted repository must not be said to agree on its commit count.
    `known` is the count the facts already carry (refresh_metadata.fetch()
    reads it since 2026-09-27); GitHub is asked again only without one."""
    if isinstance(known, int) and not isinstance(known, bool):
        count = known
    else:
        try:
            count = net.commits(repo)
        except RateLimited:
            return [Finding(key, "skipped", "Commits not counted: GitHub rate limit.")], False
    if count == 1 and "single-commit" not in flags:
        return [Finding(
            key, "warning",
            f"{code(repo)} has one commit on its default branch; the `single-commit` flag tells a reader.",
        )], True
    if count is not None and count > 1 and "single-commit" in flags:
        return [Finding(key, "info", f"Flagged `single-commit`, but {code(repo)} now has more than one commit.")], True
    return [], count is not None


def check_link(row: dict, net: Net | None, reason: str) -> list[Finding]:
    key = "link"
    url = row.get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        return [Finding(key, "error", f"`url` {code(url)} is not an https:// address, so it was not requested.")]
    if net is None:
        return [Finding(key, "skipped", f"The link was not requested: {reason}.")]
    status, note = net.link(url)
    if str(note).startswith("not checked"):
        return [Finding(key, "skipped", "The link was not checked: GitHub rate limit.")]
    if 200 <= status < 300:
        return [Finding(key, "ok", f"The link answered {status}.")]
    if status in (401, 403, 429):
        return [Finding(
            key, "warning",
            f"The host refused this checker ({status}), which is not a dead link: open it in a browser.",
        )]
    if 300 <= status < 400:
        return [Finding(key, "warning", f"The link redirects ({status}): point `url` at where it lands.")]
    return [Finding(
        key, "error",
        f"The link answered {status or 'nothing'}{': ' + said(note, 80) if note else ''}. "
        "catalog.json holds only links that answer 2xx.",
    )]


def check_self_submission(row: dict, added: bool, author: str | None) -> list[Finding]:
    key = "self-submission"
    if not author:
        if not added:
            return []
        return [Finding(key, "skipped", "No pull-request author to compare with (`--author LOGIN`, or `PR_AUTHOR` in CI).")]
    who = code(author)
    names = people(row)
    role = names.get(author.lower())
    flagged = SELF_SUBMISSION_FLAG in (row.get("flags") or [])
    if not added:
        if role and not flagged:
            return [Finding(
                key, "info",
                f"{who} opened this pull request and is {role}. Whether an edit by the project's own side "
                f"makes the row `{SELF_SUBMISSION_FLAG}` is a person's call.",
            )]
        return []
    if role and flagged:
        return [Finding(key, "ok", f"{who} opened this pull request and is {role}; the row discloses it.")]
    if role:
        sources = row.get("sources") if isinstance(row.get("sources"), list) else []
        if any(isinstance(s, dict) and s.get("catalog") == SELF_SUBMISSION_SOURCE for s in sources):
            return [Finding(
                key, "error",
                f"{who} opened this pull request and is {role}; the row's sources say "
                f"`{SELF_SUBMISSION_SOURCE}`, but `flags` lacks `{SELF_SUBMISSION_FLAG}`: add it.",
            )]
        return [Finding(
            key, "error",
            f"{who} opened this pull request and is {role}, but the row does not say so: add the source "
            f"`{{\"catalog\": \"{SELF_SUBMISSION_SOURCE}\", \"url\": <this pull request>}}` and "
            f"`{SELF_SUBMISSION_FLAG}` to `flags`.",
        )]
    if not names:
        return [Finding(
            key, "info",
            f"The row names no GitHub account to compare {who} with, so whether this is a "
            "self-submission is a person's call.",
        )]
    if flagged:
        return [Finding(
            key, "info",
            f"The row declares `{SELF_SUBMISSION_FLAG}`, and {who} is none of the accounts it names "
            "(an organisation's repository, or a co-maintainer's). A person confirms.",
        )]
    return [Finding(
        key, "ok",
        f"{who} is none of the accounts the row names. An organisation's repository can still be "
        "its author's own; that stays a person's call.",
    )]


def check_flag_notes(row: dict) -> list[Finding]:
    key = "flag-notes"
    flags = [flag for flag in FLAGS_NEEDING_NOTES if flag in (row.get("flags") or [])]
    if not flags:
        return []
    named = ", ".join(f"`{flag}`" for flag in flags)
    if not row.get("notes"):
        return [Finding(key, "error", f"Flagged {named} with no `notes` line, so a reader gets no reason.")]
    return [Finding(key, "ok", f"{named} explained in `notes`.")]


def check_classification(row: dict) -> list[Finding]:
    key = "classification"
    repo = repo_of(row)
    name = repo.split("/", 1)[1] if repo else str(row.get("slug", ""))
    languages = row.get("languages") or ["-"]
    kind, patterns = classify(str(row.get("summary", "")), name, str(languages[0]))
    have_kind, have = row.get("kind"), list(row.get("patterns") or [])
    if kind == have_kind and set(patterns) & set(have):
        return [Finding(key, "ok", f"Keyword rules on the summary agree: `{kind}`, sharing {', '.join(sorted(set(patterns) & set(have)))}.")]
    return [Finding(
        key, "info",
        f"Keyword rules on the summary suggest `{kind}` / {', '.join(patterns)}; the row says "
        f"{code(have_kind)} / {', '.join(code(p) for p in have) or 'none'}. A starting point, not a verdict: "
        "these rules needed eight corrections in 223 rows.",
    )]


# ---------------------------------------------------------------------------
# Putting them together
# ---------------------------------------------------------------------------

MAX_NETWORK_ROWS = 30
WORKERS = 4


def run(key: str, call: Callable[[], list[Finding]]) -> list[Finding]:
    """One check; whatever goes wrong inside it is `skipped`, never a pass."""
    try:
        return call()
    except RateLimited as exc:
        return [Finding(key, "skipped", f"Not checked: {said(exc)}.")]
    except Exception as exc:  # noqa: BLE001 - a malformed row must not end the card
        traceback.print_exc(file=sys.stderr)
        return [Finding(key, "skipped", f"Could not run: {said(type(exc).__name__)} {said(exc, 80)}. lint says what is malformed.")]


def review_row(change: Change, author: str | None, net: Net | None, reason: str) -> RowReview:
    row, fields = change.row, change.fields
    added = change.kind == "added"

    def wants(key: str) -> bool:
        return added or bool(READS[key] & fields)

    findings: list[Finding] = []
    if wants("call-site"):
        findings += run("call-site", lambda: check_call_site(row, net, reason))
    if wants("repository"):
        findings += run("repository", lambda: check_repository(row, fields, added, net, reason))
    if wants("link"):
        findings += run("link", lambda: check_link(row, net, reason))
    findings += run("self-submission", lambda: check_self_submission(row, added, author))
    if wants("flag-notes"):
        findings += run("flag-notes", lambda: check_flag_notes(row))
    if added:
        findings += run("classification", lambda: check_classification(row))
    order = [key for key, _ in CHECKS]
    findings.sort(key=lambda f: order.index(f.check))
    return RowReview(change.slug, change.kind, tuple(sorted(fields)) if not added else (), tuple(findings))


def review_rows(
    changes: list[Change],
    *,
    author: str | None,
    net: Net | None,
    offline: str = "offline",
    cap: int = MAX_NETWORK_ROWS,
) -> tuple[list[RowReview], list[str]]:
    """Every change reviewed, in order, and the card-level notes. Only the first
    `cap` rows are read from the network, so a pull request touching hundreds
    of rows cannot spend the repository's GitHub budget; the rest get the
    local checks and say so."""
    notes = []
    jobs = []
    for index, change in enumerate(changes):
        if net is None:
            jobs.append((change, author, None, offline))
        elif index >= cap:
            jobs.append((change, author, None, f"only the first {cap} rows are read from the network"))
        else:
            jobs.append((change, author, net, ""))
    if net is not None and len(changes) > cap:
        notes.append(
            f"{len(changes)} rows changed: the first {cap} (added rows first, then by slug) were read "
            "from the network, the rest got only the checks that need none."
        )
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        reviews = list(pool.map(lambda job: review_row(*job), jobs))
    return reviews, notes
