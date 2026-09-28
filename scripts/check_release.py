#!/usr/bin/env python3
"""Check that the MCP package's version is released on PyPI, and that every
file declaring that version agrees.

SKILL.md, llms.txt and the package's README told everyone outside Claude Code
to `pip install awesome-jev-mcp`. PyPI answered 404: publish.yml uploads only
from a release tag, no tag had ever been pushed, and nothing in CI looked at
PyPI, so the first step of the documented route failed for every reader while
every build stayed green. This looks.

Verdicts, written to $GITHUB_OUTPUT as `status=`:
  published  pyproject.toml's version is on PyPI.
  pending    it is not there yet: the package has never been published, or the
             version is newer than every release. That is the normal state
             between merging a version bump and pushing its tag (publish.yml's
             release steps), so it is a warning carrying the tag command, not a
             failure.
  behind     PyPI already has a newer version than pyproject.toml, so the
             version went backwards. Fails.
  mismatch   pyproject.toml and .claude-plugin/plugin.json (and marketplace.json,
             if it ever declares one) disagree. Fails, without the network.
  skipped    PyPI could not be read: unreachable, a timeout, a 5xx, an answer
             cut off midway or that is not the JSON API. Exit 0, after one
             retry: a network hiccup is not a release problem.
  offline    --offline: only the files were compared.

lint.yml runs it on every push to main and never on a pull request, where a
version bump is expected to be unreleased and the network must not decide the
result. The file comparison also runs on pull requests, as a unit test.

Read-only, standard library only.

Usage:
  python3 scripts/check_release.py              # files, then PyPI
  python3 scripts/check_release.py --offline    # files only
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import pathlib
import re
import sys
import time
import tomllib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = "awesome-jev-mcp"
TAG_PREFIX = "awesome-jev-mcp-v"  # publish.yml's tag filter
PYPI = "https://pypi.org/pypi"
TIMEOUT = 20
RETRY_DELAY = 5.0

# Plain releases and a/b/rc pre-releases, the forms this package would use.
# Anything else (post, dev, local, epochs) is left unordered, not guessed at.
VERSION = re.compile(r"^(\d+(?:\.\d+)*)(?:(a|b|rc)(\d+))?$")
PRE_ORDER = {"a": 0, "b": 1, "rc": 2}


def version_key(text: str) -> tuple | None:
    """A sortable key, or None for a version this cannot order."""
    match = VERSION.match(text.strip())
    if not match:
        return None
    release = [int(part) for part in match.group(1).split(".")]
    while len(release) > 1 and release[-1] == 0:
        release.pop()  # 1.0 == 1.0.0
    pre = (PRE_ORDER[match.group(2)], int(match.group(3))) if match.group(2) else (3, 0)
    return (tuple(release), pre)


def pyproject_version(root: pathlib.Path = ROOT) -> str:
    with open(root / "pyproject.toml", "rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def declared_versions(root: pathlib.Path = ROOT) -> dict[str, str]:
    """Every place that states the package's version, by file."""
    found = {"pyproject.toml": pyproject_version(root)}
    plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
    found[".claude-plugin/plugin.json"] = plugin.get("version", "(none)")
    market_path = root / ".claude-plugin" / "marketplace.json"
    if market_path.exists():
        market = json.loads(market_path.read_text())
        for plugin_entry in market.get("plugins", []):
            if "version" in plugin_entry:
                found[f".claude-plugin/marketplace.json ({plugin_entry.get('name')})"] = plugin_entry["version"]
    return found


def fetch(url: str) -> tuple[str, list[str] | str | None]:
    """('found', [versions]) | ('absent', None) | ('unreachable', reason).

    A 404 is PyPI's answer for a package it has never published, so it is not
    retried; anything else that is not the JSON API is retried once."""
    request = urllib.request.Request(url, headers={"User-Agent": "awesome-jev", "Accept": "application/json"})
    reason = "no answer"
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                data = json.loads(response.read())
            published = data.get("releases") if isinstance(data, dict) else None
            if isinstance(published, dict):
                return "found", sorted(published)
            reason = "the answer is not PyPI's JSON API (no `releases`)"
        except urllib.error.HTTPError as exc:
            exc.close()
            if exc.code == 404:
                return "absent", None
            reason = f"HTTP {exc.code}"
        except ValueError as exc:
            reason = f"the answer is not JSON ({exc.__class__.__name__})"
        except (urllib.error.URLError, OSError) as exc:
            reason = f"{exc.__class__.__name__}: {getattr(exc, 'reason', exc)}"
        except http.client.HTTPException as exc:
            # A connection cut mid-answer (IncompleteRead) or a malformed
            # status line is not an OSError, and is no more a release problem.
            reason = f"{exc.__class__.__name__}: the answer broke off or was malformed"
        if attempt == 1:
            print(f"  attempt 1: {reason}; retrying in {RETRY_DELAY:g}s")
            time.sleep(RETRY_DELAY)
    return "unreachable", reason


def judge(version: str, published: list[str] | None) -> tuple[str, list[str]]:
    """Verdict for pyproject's `version` against PyPI's release list (None
    when PyPI has never heard of the package)."""
    if not published:
        return "pending", [f"{PACKAGE} has never been published to PyPI."]
    key = version_key(version)
    ordered = [(version_key(v), v) for v in published if version_key(v) is not None]
    newer = sorted((k, v) for k, v in ordered if key is not None and k > key)
    if newer:
        return "behind", [
            f"PyPI already has {', '.join(v for _, v in newer)}, newer than pyproject.toml's {version}.",
            "A version on PyPI can never be uploaded again, so the next release must be newer than",
            f"{newer[-1][1]}: set pyproject.toml and .claude-plugin/plugin.json to it.",
        ]
    if version in published or (key is not None and any(k == key for k, _ in ordered)):
        return "published", [f"{PACKAGE} {version} is on PyPI."]
    latest = max(ordered)[1] if ordered else ", ".join(published)
    return "pending", [f"{PACKAGE} {version} is not on PyPI yet; the newest release there is {latest}."]


def append(variable: str, text: str) -> None:
    path = os.environ.get(variable)
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(text)


def release_steps(version: str, first: bool) -> list[str]:
    commit = os.environ.get("GITHUB_SHA") or "<the commit on main>"
    tag = f"{TAG_PREFIX}{version}"
    lines = []
    if first:
        lines += [
            "The first upload needs two one-time settings, both by a maintainer:",
            "",
            f"1. On PyPI, add a pending trusted publisher for project `{PACKAGE}`: owner",
            "   `kydlikebtc`, repository `awesome-jev`, workflow `publish.yml`, environment `pypi`",
            "   (https://pypi.org/manage/account/publishing/, see",
            "   https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).",
            "2. In this repository, create the `pypi` environment (Settings → Environments → New",
            "   environment) and give it a required reviewer if releases should need a second",
            "   person; the first release would otherwise create it unprotected.",
            "",
        ]
    lines += [
        "Then tag the commit whose pyproject.toml carries this version, and push the tag:",
        "",
        "```bash",
        f"git tag {tag} {commit}",
        f"git push origin {tag}",
        "```",
        "",
        "publish.yml builds it, uploads it and installs it back from PyPI.",
    ]
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--offline", action="store_true", help="compare the files only")
    parser.add_argument("--pypi", default=PYPI, help=argparse.SUPPRESS)
    parser.add_argument("--root", type=pathlib.Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    declared = declared_versions(args.root)
    for where, value in declared.items():
        print(f"  {where}: {value}")
    if len(set(declared.values())) > 1:
        listing = ", ".join(f"{where} says {value}" for where, value in declared.items())
        print(f"::error title=MCP package version::The package version is declared differently: {listing}. Set them all to the same version.")
        append("GITHUB_OUTPUT", "status=mismatch\n")
        return 1
    version = declared["pyproject.toml"]
    if args.offline:
        print(f"offline: every file declares {version}; PyPI not consulted")
        append("GITHUB_OUTPUT", "status=offline\n")
        return 0

    url = f"{args.pypi.rstrip('/')}/{PACKAGE}/json"
    state, payload = fetch(url)
    if state == "unreachable":
        print(f"skipped: could not read {url}: {payload}. Not a release problem; the next push checks again.")
        append("GITHUB_OUTPUT", "status=skipped\n")
        return 0

    published = payload if state == "found" else None
    status, lines = judge(version, published)
    append("GITHUB_OUTPUT", f"status={status}\n")
    for line in lines:
        print(line)
    if status == "published":
        return 0
    if status == "behind":
        print(f"::error title=MCP package version went backwards::{' '.join(lines)}")
        append("GITHUB_STEP_SUMMARY", "## MCP package version is behind PyPI\n\n" + "\n".join(lines) + "\n")
        return 1

    steps = release_steps(version, first=published is None)
    print("\n".join(steps))
    print(
        f"::warning title=MCP package release pending::{PACKAGE} {version} is not on PyPI, so "
        "`pip install awesome-jev-mcp` does not give readers this version. The step summary "
        "has the release commands."
    )
    append(
        "GITHUB_STEP_SUMMARY",
        f"## {PACKAGE} {version} is not on PyPI yet\n\n" + "\n".join(lines) + "\n\n" + "\n".join(steps) + "\n",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
