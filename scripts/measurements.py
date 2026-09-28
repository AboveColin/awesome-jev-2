"""What a benchmark row's `measurement` holds, and the rules lint.py keeps on it.

A kind: benchmark row may carry `measurement` (schema/entry.schema.json): what
its own author measured, indexed field by field from the author's report — the
task, named datasets, comparators, kinds of metric, n, the model string, when,
whether per-item data is published, whether the protocol was fixed first, and
the author's own `direction`. Nothing in it was measured or reproduced here.
`read_on` dates a person's reading of the report against the fields; without
it a script or a model filled them in (docs/review-queue.md lists those rows).

How a measurement is read — which rows have one, how a direction is shown — is
the MCP package's query.py, loaded by its path as platform_values.py loads it,
so lint, the generated pages and the server read the same thing.
site/catalog-core.mjs applies the same rules on the site.

What lint holds (lint.check_measurement, lint.check_measurement_models):
* a measurement only on a kind: benchmark row;
* `as_of`, or the row's `published`, dates it: model versions move, and a
  measurement is of the model served that day;
* `as_of` and `read_on` are real dates, not in the future, and nobody read the
  report before the measurement was taken;
* `model_string` is a string compat.json lists on some surface (a string it
  does not list is left out of the row rather than recorded).

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import datetime as dt

from platform_values import load_query

KIND = "benchmark"
FIELD = "measurement"
DATED = ("as_of", "read_on")


def _date(value: object) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def row_problems(entry: dict, today: dt.date) -> list[str]:
    """Each way one row's measurement breaks a rule that needs no other file."""
    if FIELD not in entry:
        return []
    found: list[str] = []
    if entry.get("kind") != KIND:
        found.append(
            f"has a measurement but kind is {entry.get('kind')!r}: a measurement indexes a benchmark's "
            "own report, so it belongs only on a kind: benchmark row"
        )
    measurement = entry[FIELD]
    if not isinstance(measurement, dict):
        return found  # the schema says what it should be
    if "as_of" not in measurement and not entry.get("published"):
        found.append(
            "has a measurement with no as_of and no published date: give the day the author gives for "
            "the measurement, or the day its results were first committed or posted, as measurement.as_of"
        )
    dates = {}
    for field in DATED:
        if field in measurement:
            parsed = _date(measurement[field])
            if parsed is None:
                found.append(f"measurement.{field} is not a valid date")
            elif parsed > today:
                found.append(f"measurement.{field} {measurement[field]} is in the future")
            else:
                dates[field] = parsed
    if len(dates) == 2 and dates["read_on"] < dates["as_of"]:
        found.append(
            f"measurement.read_on {measurement['read_on']} is before as_of {measurement['as_of']}: nobody "
            "can read the report of a measurement not yet taken"
        )
    return found


def accepted_strings(compat: dict) -> list[str]:
    """Every model string compat.json lists on any surface, sorted."""
    query = load_query()
    platforms = [platform for platform in compat.get("platforms") or [] if "model" in platform]
    return sorted({string for platform in platforms for string in query.accepted(platform)})


def model_problems(catalog: list, retired: list, compat: dict) -> list[tuple[str, str]]:
    """(where, message) for each measurement whose model_string compat.json does
    not list. Reads compat.json only when some row records a model string."""
    found: list[tuple[str, str]] = []
    accepted: list[str] | None = None
    for label, rows in (("catalog.json", catalog), ("retired.json", retired)):
        for i, entry in enumerate(rows):
            measurement = entry.get(FIELD) if isinstance(entry, dict) else None
            string = measurement.get("model_string") if isinstance(measurement, dict) else None
            if not isinstance(string, str):
                continue
            if accepted is None:
                accepted = accepted_strings(compat)
            if string in accepted:
                continue
            listed = {**compat, "platforms": [p for p in compat.get("platforms") or [] if "model" in p]}
            reason = load_query().model_string_check(listed, string)["reason"]
            found.append((
                f"{label}[{i}]",
                f"{entry.get('slug', '?')}: measurement.model_string {string!r} is not a string compat.json "
                f"lists ({reason}); record the one the author sent or says answered if compat.json lists "
                f"it, else leave model_string out. Listed: {', '.join(accepted)}",
            ))
    return found


def measured(catalog: list[dict]) -> list[dict]:
    """The rows carrying a measurement object, in the order given."""
    query = load_query()
    return [entry for entry in catalog if query.measurement_of(entry)]


def unread(catalog: list[dict]) -> list[dict]:
    """Measured rows no person has read against their report (no measurement.read_on)."""
    query = load_query()
    return [entry for entry in measured(catalog) if not query.measurement_of(entry).get("read_on")]


def directions(catalog: list[dict]) -> dict[str, int]:
    """{direction: measured rows whose author states it}, in the schema's order,
    then "not stated" for measured rows whose author states none."""
    query = load_query()
    rows = measured(catalog)
    counts = {key: sum(1 for e in rows if query.measurement_of(e).get("direction") == key) for key in query.DIRECTIONS}
    counts["not stated"] = sum(1 for e in rows if query.measurement_of(e).get("direction") not in query.DIRECTIONS)
    return counts
