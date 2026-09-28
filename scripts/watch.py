"""The questions docs/status.md watches, and what the catalogue can say about each.

watch.json (at the root, hand-written) lists each question and how it is
tracked (`signal`):

  * independent-reports: benchmark rows not flagged vendor-reported
    (query.is_independent_report, the rule every surface shares), with the
    directions their authors state (author-stated, not reproduced here);
  * alternatives-matching: of the kind: alternative rows citing a file, those
    whose evidence.matched strings include the item's `matched_contains` — a
    proxy, and the item's definition says for what;
  * listed-rows: rows the item names by hand, since no field records the
    topic, with a status someone read;
  * manual: a status someone read at its source (`url`).

A status always carries the date it was checked (`as_of`) and whether a person
or a model checked it (`checked_by`): a reading is a different claim from a
count, and a model's reading is not a person's.

A counted signal's recent change is stated against the snapshot before the
newest in history/ (the newest is the refresh's own, the state now), whose
`watch` values scripts/snapshot_stats.py records; until there are two
snapshots holding the value, against the rows whose first_seen falls in the
newest week of first_seen dates. Either way the dates are printed: a table
that said "this week" would be wrong a week later without a byte changing.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re

from platform_values import load_query

ROOT = pathlib.Path(__file__).resolve().parent.parent
WATCH_FILE = ROOT / "watch.json"
SITE = "https://kydlikebtc.github.io/awesome-jev/"

COUNTED = ("independent-reports", "alternatives-matching")
SIGNALS = (*COUNTED, "listed-rows", "manual")
CHECKERS = ("person", "model")
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CJK = re.compile(r"[\u4e00-\u9fff]")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TEXTS = ("question", "definition")
# The first_seen window that stands in for a recent change until history/
# holds two snapshots with the value: the newest date and the six before it.
WEEK = dt.timedelta(days=6)
ALTERNATIVE = "alternative"


def load(path: pathlib.Path = WATCH_FILE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _item_problems(item: dict, slugs: set[str], today: dt.date) -> list[str]:
    where = f"watch.json: {item.get('id')!r}"
    found = []
    signal = item.get("signal")
    if signal not in SIGNALS:
        return [f"{where}: signal must be one of {', '.join(SIGNALS)}"]
    needed = [f"{t}_{lang}" for t in TEXTS for lang in ("en", "zh")]
    if signal in ("listed-rows", "manual"):
        needed += ["status_en", "status_zh"]
        if item.get("checked_by") not in CHECKERS:
            found.append(f"{where}: checked_by must be one of {', '.join(CHECKERS)}")
        as_of = item.get("as_of")
        if not (isinstance(as_of, str) and DATE.match(as_of)) or dt.date.fromisoformat(as_of) > today:
            found.append(f"{where}: as_of must be a YYYY-MM-DD date, not after {today.isoformat()}")
    for key in needed:
        text = item.get(key)
        if not isinstance(text, str) or not text.strip():
            found.append(f"{where}: {key} is missing")
        elif key.endswith("_zh") and not CJK.search(text):
            found.append(f"{where}: {key} has no Chinese in it")
    if "url" in item and not str(item["url"]).startswith("https://"):
        found.append(f"{where}: url must be https")
    if signal == "manual" and "url" not in item:
        found.append(f"{where}: a manual status needs the url it was read at")
    if signal == "listed-rows":
        rows = item.get("rows")
        if not isinstance(rows, list) or not rows or len(set(rows)) != len(rows):
            found.append(f"{where}: rows must be a list of distinct slugs")
        else:
            found += [f"{where}: lists {slug!r}, which is not in catalog.json" for slug in rows if slug not in slugs]
    if signal == "alternatives-matching" and not str(item.get("matched_contains") or "").strip():
        found.append(f"{where}: matched_contains must name the string the proxy looks for")
    return found


def problems(watch: dict, catalog: list[dict], today: dt.date | None = None) -> list[str]:
    """Why watch.json cannot be rendered as it stands."""
    today = today or dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1)
    items = watch.get("items") if isinstance(watch, dict) else None
    if not isinstance(items, list) or not items:
        return ["watch.json: items must be a non-empty list"]
    found = []
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if len(ids) != len(items) or not all(isinstance(i, str) and ID.match(i) for i in ids):
        found.append("watch.json: every item needs an id in lower-case-and-hyphens")
    if len(set(ids)) != len(ids):
        found.append("watch.json: ids must be distinct")
    slugs = {e["slug"] for e in catalog}
    for item in items:
        if isinstance(item, dict):
            found += _item_problems(item, slugs, today)
    return found


def matches(item: dict, entry: dict) -> bool:
    """Whether a row counts towards a counted item's signal."""
    if item["signal"] == "independent-reports":
        return load_query().is_independent_report(entry)
    if item["signal"] == "alternatives-matching":
        matched = (entry.get("evidence") or {}).get("matched") or []
        return entry.get("kind") == ALTERNATIVE and any(item["matched_contains"] in m for m in matched)
    return False


def values(watch: dict, catalog: list[dict]) -> dict[str, int]:
    """Each counted item's value now, by id: what a snapshot records."""
    return {
        item["id"]: sum(1 for e in catalog if matches(item, e)) for item in watch["items"] if item["signal"] in COUNTED
    }


def baseline(history, item_id: str) -> tuple[str, int] | None:
    """(date, value) from the snapshot before the newest that recorded this
    item, or None while fewer than two have."""
    recorded = [(date, snap["watch"][item_id]) for date, snap in history if item_id in (snap.get("watch") or {})]
    return recorded[-2] if len(recorded) >= 2 else None


def newest_week(catalog: list[dict]) -> tuple[str, str] | None:
    """The newest first_seen date and the date six days before it."""
    dates = [e["first_seen"] for e in catalog if isinstance(e.get("first_seen"), str) and DATE.match(e["first_seen"])]
    if not dates:
        return None
    end = max(dates)
    return (dt.date.fromisoformat(end) - WEEK).isoformat(), end


def change(item: dict, catalog: list[dict], history, now: int) -> str:
    """A counted item's recent change, with the dates it is counted between."""
    since = baseline(history, item["id"])
    if since:
        date, before = since
        return f"{now - before:+d} since the {date} snapshot (then {before})"
    week = newest_week(catalog)
    if not week:
        return "—"
    new = sum(1 for e in catalog if matches(item, e) and week[0] <= e.get("first_seen", "") <= week[1])
    return f"{new:+d} first seen {week[0]} to {week[1]} (history/ does not yet hold two snapshots)"


def reading(item: dict) -> str:
    """A status with who read it, when, and where."""
    who = "read by a person" if item["checked_by"] == "person" else "read by a model, not yet by a person"
    source = f"; [source]({item['url']})" if item.get("url") else ""
    return f"{item['status_en']} ({who}, {item['as_of']}{source})"


def row_link(entry: dict) -> str:
    return f"[{entry['title']}]({SITE}?lang=en#{entry['slug']})"


def now_cell(item: dict, catalog: list[dict]) -> str:
    """What the catalogue says about the item today."""
    signal = item["signal"]
    if signal == "independent-reports":
        rows = [e for e in catalog if matches(item, e)]
        query = load_query()
        stated = [(query.measurement_of(e) or {}).get("direction") for e in rows]
        parts = [f"{d} {stated.count(d)}" for d in query.DIRECTIONS if stated.count(d)]
        parts.append(f"none recorded {sum(1 for d in stated if d not in query.DIRECTIONS)}")
        return (
            f"**{len(rows)}** independent reports ([on the site]({SITE}?indep=1&lang=en)); directions their "
            f"authors state, not reproduced here: {', '.join(parts)}"
        )
    if signal == "alternatives-matching":
        cited = [e for e in catalog if e.get("kind") == ALTERNATIVE and e.get("evidence")]
        n = sum(1 for e in cited if matches(item, e))
        return f"**{n}** of the {len(cited)} alternatives citing a file ([on the site]({SITE}?k={ALTERNATIVE}&lang=en))"
    if signal == "listed-rows":
        by_slug = {e["slug"]: e for e in catalog}
        links = ", ".join(row_link(by_slug[slug]) for slug in item["rows"])
        return f"{links}. {reading(item)}"
    return reading(item)


def render(watch: dict, catalog: list[dict], history=()) -> str:
    """The table between docs/status.md's watch markers."""
    head = ["Question", "Now", "Recent change", "How it is tracked"]
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    for item in watch["items"]:
        if item["signal"] in COUNTED:
            recent = change(item, catalog, history, sum(1 for e in catalog if matches(item, e)))
        else:
            recent = "— (a reading, dated in the cell before)"
        cells = [item["question_en"], now_cell(item, catalog), recent, item["definition_en"]]
        lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
    return "\n".join(lines)
