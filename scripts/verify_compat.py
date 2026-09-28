#!/usr/bin/env python3
"""Re-read each platform's documentation and check compat.json still matches it.

compat.json is the source every other copy of a model string is linted against,
which makes it the one place a wrong string would propagate from. It records
thirteen surfaces the project does not control, each of which can rename a model
or retire an alias in an afternoon. verify_claims.py re-reads code call sites
weekly; this does the same for the platform matrix.

For every platform with a documentation URL, each model string compat.json
records for it must still appear on that page — or on `model_source`, when the
strings are documented somewhere other than the page readers are linked to. Four verdicts:

  ok            every recorded string is on the page
  string-gone   the page loaded but a recorded string is missing — a person
                needs to look; the platform may have renamed the model
  newer-version the page names a model version newer than any compat.json
                records (since 2026-09-27): most likely a release. A person
                reads the page, rehearses with
                `python3 scripts/lint_docs.py --simulate-model <version>`,
                and updates compat.json
  unreadable    the page refused a scripted request or renders client-side,
                so absence proves nothing. Reported, never failed on.

`as_of` in compat.json is deliberately not bumped by this script. It records
when a person last read the pages; a string match is weaker evidence than that,
and pretending otherwise would overstate what was checked. The report says how
many days ago that was, and past STALE_DAYS asks for a reading: the age is
printed and written to the job's outputs, never to a committed file, where it
would be wrong the next day.

Run: python3 scripts/verify_compat.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _github import VERSION, version_parts, version_stem  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TIMEOUT = 25
# A person's reading of every platform page older than this is due again.
# A judgement, not a measured release cadence: about six weeks, so the weekly
# run does not ask every week, yet what a string match cannot see (a renamed
# field, another envelope) waits at most that long for a person.
STALE_DAYS = 45
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def expected_strings(platform: dict) -> list[str]:
    return [
        re.sub(r"\s*\(.*\)$", "", part.strip())
        for part in platform["model"].split("·")
        if part.strip() not in ("", "—")
    ]


def fetch(url: str) -> tuple[str | None, str]:
    request = urllib.request.Request(url, headers=HEADERS)
    for _attempt in range(2):  # one retry: a transient miss is not a verdict
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.read().decode("utf-8", "replace"), ""
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None, "HTTP 404 — the page itself is gone"
            reason = f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001 - one platform must not stop the sweep
            reason = exc.__class__.__name__
    return None, reason


def newest_recorded(compat: dict) -> tuple[int, ...]:
    """The newest model version (major.minor) any platform's cell records."""
    stems = [version_stem(t) for p in compat["platforms"] for t in VERSION.findall(p.get("model") or "")]
    return max((version_parts(s) for s in stems), default=())


def newer_versions(text: str, newest: tuple[int, ...]) -> list[str]:
    """Model versions a page names that are newer than `newest`, oldest first."""
    found = {t for t in VERSION.findall(text) if newest and version_parts(version_stem(t)) > newest}
    return sorted(found, key=version_parts)


def check(platform: dict, newest: tuple[int, ...] = ()) -> tuple[str, dict, list[str], str]:
    wanted = expected_strings(platform)
    # model_source, when set, is the page the strings are actually documented
    # on: the native API reference defers to a separate Models page, and a
    # GitHub tree URL renders client-side. Checking the linked page instead
    # would report a false `string-gone` every week.
    url = platform.get("model_source") or platform.get("url")
    if not url or not wanted:
        return "skipped", platform, [], "no URL or no model string recorded"
    page, reason = fetch(url)
    if page is None:
        verdict = "string-gone" if reason.startswith("HTTP 404") else "unreadable"
        return verdict, platform, wanted, reason
    text = html.unescape(page)
    missing = [s for s in wanted if s not in text]
    newer = newer_versions(text, newest)
    if not missing and newer:
        # The strings listed are the newer versions, not missing ones.
        return "newer-version", platform, newer, "newer than any version compat.json records"
    if not missing:
        return "ok", platform, [], ""
    # A page that mentions none of the recorded strings, and not even "jev",
    # is almost certainly rendered client-side. Absence there proves nothing.
    if "jev" not in text.lower():
        return (
            "unreadable",
            platform,
            missing,
            "page carries no server-rendered text about Jev",
        )
    return "string-gone", platform, missing, ""


def _today() -> dt.date:
    return dt.date.today()


def age_lines(as_of: str, today: dt.date) -> tuple[int | None, list[str]]:
    """How many days since a person read the pages, and what to say about it."""
    try:
        days = (today - dt.date.fromisoformat(as_of)).days
    except ValueError:
        return None, [f"compat.json as_of {as_of!r} is not a date"]
    lines = [f"compat.json as_of {as_of}: a person last read every platform page {days} day(s) ago"]
    if days > STALE_DAYS:
        lines.append(
            f"That is more than {STALE_DAYS} days. Read each platform's page, correct compat.json, and set "
            "as_of to the day of that reading; a string match by this script does not count as one."
        )
    return days, lines


def write_outputs(values: dict[str, str]) -> None:
    """step outputs for claims.yml, when running in GitHub Actions."""
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.writelines(f"{key}={value}\n" for key, value in values.items())


def main() -> int:
    compat = json.loads((ROOT / "compat.json").read_text())
    newest = newest_recorded(compat)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda platform: check(platform, newest), compat["platforms"]))

    counts: dict[str, int] = {}
    for verdict, platform, strings, note in results:
        counts[verdict] = counts.get(verdict, 0) + 1
        label = "names" if verdict == "newer-version" else "missing"
        detail = f"  {label} {strings}" if strings else ""
        detail += f"  ({note})" if note else ""
        print(f"  {verdict:12} {platform['id']:24}{detail}")

    print()
    print(
        f"{counts.get('ok', 0)} ok, {counts.get('string-gone', 0)} string-gone, "
        f"{counts.get('newer-version', 0)} newer-version, "
        f"{counts.get('unreadable', 0)} unreadable — compat.json as_of {compat['as_of']}"
    )
    days, lines = age_lines(compat["as_of"], _today())
    for line in lines:
        print(line)
    stale = days is None or days > STALE_DAYS
    write_outputs({"stale": "true" if stale else "false", "age": "" if days is None else str(days)})
    if stale:
        print(f"::warning title=compat.json not read lately::{lines[0]}", file=sys.stderr)
    if counts.get("string-gone"):
        print(
            "\nA recorded model string is no longer on its platform's page. Open the "
            "page, update compat.json, and run build_compat.py and lint_docs.py — "
            "every copy of the old string will then show up as an error."
        )
    if counts.get("newer-version"):
        newer = sorted(
            {v for verdict, _, strings, _ in results if verdict == "newer-version" for v in strings},
            key=version_parts,
        )
        print(
            f"\nA platform's page names {', '.join(newer)}, newer than any version compat.json records. "
            f"Rehearse the release: python3 scripts/lint_docs.py --simulate-model {newer[-1]} lists "
            "every copy that would go red; then read the pages and update compat.json."
        )
    return 1 if counts.get("string-gone") or counts.get("newer-version") else 0


if __name__ == "__main__":
    sys.exit(main())
