"""Where the catalogue comes from, and how honest that answer is.

Installed as a package, this has no repository around it, so the five JSON
files it serves have to come from somewhere. It fetches them, and every result
the server returns says which layer answered.

That last part is the whole point. This repository's argument is that a claim
without its provenance is worth less than no claim, and a catalogue served from
a six-month-old snapshot while quietly presenting itself as current would be
making exactly the mistake it catalogues other people making.

The ladder, in order:

1. ``AWESOME_JEV_CATALOG`` — a directory holding the five files. For anyone
   testing an edit, and the escape hatch when the rest of this is in the way.
2. **A repository checkout above this file** — that is, running from source or
   an editable install, not merely being launched from inside a checkout.
   Contributors testing an edit should be served their own working tree, and
   fetching the published copy of a file they are mid-edit on would be absurd.

   Deliberately keyed on ``__file__`` rather than the working directory. MCP
   clients launch servers with whatever cwd they please, and a server whose data
   changed depending on where it happened to be started would be far worse than
   one that simply never reads the tree.
3. **The network**, conditional on the cached ETag. GitHub answers a revalidated
   request with 304 and no body, so the steady state costs five small
   round trips rather than megabytes.
4. **The cache**, when the network fails but we have fetched before. Degraded,
   and says so.
5. **The snapshot bundled in the wheel**, when there is no cache either. This is
   the offline first run. It announces itself loudly in every result, because
   it is the one layer that can be arbitrarily old.

Nothing below layer 3 is silent. A stale answer presented as fresh is worse than
a failure.

## All five files move together

A mixed load is a correctness bug, not just untidiness: catalog.json may use a
pattern key that only exists in a newer patterns.json, or a flag that only a
newer taxonomy.json explains, and collections.json names catalogue rows; lint
enforces those relationships inside a commit. So a source either supplies all
five or it is skipped entirely, and the ladder moves on.

They are the five files the catalogue's site fetches at runtime
(scripts/assemble_site.py PAGE_FILES; a test holds the two lists equal), so an
agent asking this server and a person reading the site are served one data set.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, NamedTuple

FILES = ("catalog.json", "compat.json", "patterns.json", "taxonomy.json", "collections.json")
RAW = "https://raw.githubusercontent.com/kydlikebtc/awesome-jev/main/"

# Long enough for a megabyte on a slow line, short enough that a hung GitHub
# does not hold an MCP client's startup open until it gives up on us.
TIMEOUT = 8

BUNDLED = pathlib.Path(__file__).resolve().parent / "_bundled"


@dataclass(frozen=True)
class Provenance:
    """Which layer answered, and how much to trust it."""

    source: str
    detail: str
    as_of: str
    rows: int

    @property
    def degraded(self) -> bool:
        return self.source in {"cache", "bundled"}

    def line(self) -> str:
        """One compact line, because an agent pays for every token of this."""
        prefix = "STALE — " if self.degraded else ""
        return (
            f"{prefix}{self.detail} · {self.rows} rows · catalogue checked {self.as_of}"
        )


class Loaded(NamedTuple):
    """The five files, as the server reads them, and which layer answered."""

    catalog: list[dict]
    compat: dict[str, Any]
    patterns: list[dict]
    taxonomy: dict[str, Any]
    collections: list[dict]
    provenance: Provenance


def cache_dir() -> pathlib.Path:
    """Per-user cache, following whatever the platform calls that."""
    if sys.platform == "darwin":
        base = pathlib.Path.home() / "Library" / "Caches"
    elif os.name == "nt":
        base = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home()))
    else:
        base = pathlib.Path(
            os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")
        )
    return base / "awesome-jev-mcp"


def _read_dir(path: pathlib.Path) -> dict[str, Any] | None:
    """Every file in FILES from one directory, or nothing. See the module docstring."""
    try:
        return {name: json.loads((path / name).read_text()) for name in FILES}
    except (OSError, json.JSONDecodeError):
        return None


def _find_checkout(start: pathlib.Path | str | None = None) -> pathlib.Path | None:
    """A repository working tree at or above `start` — by default this file,
    so one is found only when this is running from source."""
    here = pathlib.Path(__file__ if start is None else start).resolve()
    for parent in (here, *here.parents):
        if (parent / ".git").exists() and (parent / "catalog.json").exists():
            return parent
    return None


def _fetch() -> tuple[dict[str, Any], bool] | None:
    """Fetch every file in FILES, revalidating against the cached ETags.

    Returns the payload and whether anything actually changed, or None if any
    file could not be had — a partial fetch is discarded rather than mixed with
    the cache.
    """
    cache = cache_dir()
    try:
        etags = json.loads((cache / "etags.json").read_text())
    except (OSError, json.JSONDecodeError):
        etags = {}

    payload: dict[str, Any] = {}
    fresh_etags = dict(etags)
    changed = False

    for name in FILES:
        request = urllib.request.Request(RAW + name)
        if etags.get(name) and (cache / name).exists():
            request.add_header("If-None-Match", etags[name])
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                body = response.read()
                if tag := response.headers.get("ETag"):
                    fresh_etags[name] = tag
                payload[name] = json.loads(body)
                changed = True
        except urllib.error.HTTPError as error:
            if error.code != 304:
                return None
            # Revalidated: the cached copy is current, which is the steady state.
            try:
                payload[name] = json.loads((cache / name).read_text())
            except (OSError, json.JSONDecodeError):
                return None
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return None

    if changed:
        try:
            cache.mkdir(parents=True, exist_ok=True)
            for name in FILES:
                (cache / name).write_text(json.dumps(payload[name]))
            (cache / "etags.json").write_text(json.dumps(fresh_etags))
        except OSError:
            # An unwritable cache costs a refetch next time; it is not a reason
            # to refuse data we already hold in memory.
            pass

    return payload, changed


def _as_of(catalog: list[dict]) -> str:
    """The catalogue's own latest check date.

    Deliberately read from the data rather than from the fetch clock. It answers
    "how current is what you are being told", which is the question, and it
    stays meaningful whichever layer served the bytes.
    """
    dates = [entry["checked"] for entry in catalog if entry.get("checked")]
    return max(dates) if dates else "unknown"


def load(checkout_from: pathlib.Path | str | None = None) -> Loaded:
    """Walk the ladder and return the first complete answer, with its provenance.

    `checkout_from` is where the search for a checkout (layer 2) starts: this
    file unless given. The tests give a directory outside any repository,
    because they run inside one and would otherwise never reach layers 3 to 5.
    """
    attempts: list[tuple[str, str, dict[str, Any] | None]] = []

    if override := os.environ.get("AWESOME_JEV_CATALOG"):
        attempts.append(
            (
                "override",
                f"from AWESOME_JEV_CATALOG={override}",
                _read_dir(pathlib.Path(override)),
            )
        )

    if checkout := _find_checkout(checkout_from):
        attempts.append(
            ("checkout", f"from the repository at {checkout}", _read_dir(checkout))
        )

    for source, detail, payload in attempts:
        if payload:
            return _unpack(payload, source, detail)

    if result := _fetch():
        payload, changed = result
        detail = "fetched from GitHub" if changed else "revalidated against GitHub"
        return _unpack(payload, "network", detail)

    if payload := _read_dir(cache_dir()):
        return _unpack(
            payload,
            "cache",
            "network unreachable, serving the last copy fetched to this machine",
        )

    if payload := _read_dir(BUNDLED):
        return _unpack(
            payload,
            "bundled",
            "network unreachable and nothing cached, serving the snapshot shipped "
            "inside this package — it is as old as the release you installed",
        )

    raise RuntimeError(
        "awesome-jev: no catalogue available. The network is unreachable, nothing "
        "is cached, and this build carries no bundled snapshot. Set "
        f"AWESOME_JEV_CATALOG to a directory holding {', '.join(FILES[:-1])} and "
        f"{FILES[-1]}, or run the server from a repository checkout."
    )


def _unpack(payload: dict[str, Any], source: str, detail: str) -> Loaded:
    catalog = payload["catalog.json"]
    return Loaded(
        catalog,
        payload["compat.json"],
        payload["patterns.json"]["patterns"],
        payload["taxonomy.json"],
        payload["collections.json"]["collections"],
        Provenance(source, detail, _as_of(catalog), len(catalog)),
    )
