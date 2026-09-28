"""The sibling Jev directories this repository reads, and which repositories each cites.

`docs/sibling-lists.txt` names them, one GitHub repository per line. Two
scripts read their READMEs: discover_candidates.py ranks the repositories they
cite that are not catalogued yet, and attribute_sources.py records, on every
catalogued row, which of them cite the row's repository. Both harvest through
here, so a list is read, and a citation is counted, the same way in each.

A citation is a link: the list's README contains `https://github.com/owner/name`
for the repository. It says the list's author linked it, not that anyone read
its code or that it calls Jev. These lists copy from each other, which is why
a count of them finds things and verifies nothing (docs/method.md).

Only URLs are taken from a list, never its descriptions: many of these lists
ship no licence, and a URL is a fact where a description is someone's writing.

A sibling-list citation in a row's `sources` has one fixed shape: `catalog` is
the list's `owner/name` and `url` is `https://github.com/owner/name`, both as
docs/sibling-lists.txt spells them (is_citation). No other kind of source
looks like that, which is how lint, _stats and attribute_sources.py tell the
weekly citations from the sources a person wrote. site/catalog-core.mjs
siblingCitations() holds the same rule for the site.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import collections
import pathlib
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, Iterable

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIBLINGS = ROOT / "docs" / "sibling-lists.txt"
WORKERS = 8
# This repository (_github.SELF; a test holds them equal). A row of its own,
# such as an example, is never cited: a list linking this repository links the
# list, not the row.
SELF = "kydlikebtc/awesome-jev"

GH = re.compile(r"https://github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+)")
# A list line, and the only url a citation may carry: a repository root.
LIST_URL = re.compile(r"https://github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+?)/?")

# GitHub's own paths, not repositories.
SKIP_OWNERS = {
    "sponsors",
    "topics",
    "features",
    "about",
    "pricing",
    "login",
    "apps",
    "marketplace",
    "orgs",
    "settings",
    "notifications",
    "explore",
    "collections",
    "readme",
    "search",
    "users",
    "site",
    "github",
}


def slug_of(owner: str, name: str) -> str:
    """The key repositories are compared by: owner/name, lower-cased, no `.git`."""
    name = re.sub(r"\.git$", "", name)
    return f"{owner.lower()}/{name.lower()}"


def list_url(line: str) -> str | None:
    """A sibling-lists.txt line as the one URL a citation of that list carries:
    `https://github.com/owner/name`, spelled as the line spells it, without a
    trailing slash. None for anything that is not a repository root."""
    match = LIST_URL.fullmatch(line.strip())
    if not match or match.group(2) in (".", ".."):
        return None
    return f"https://github.com/{match.group(1)}/{match.group(2)}"


def read_lists(path: pathlib.Path = SIBLINGS) -> list[str]:
    """Every list line of the file, comments and blank lines left out."""
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def listed_urls(lines: Iterable[str]) -> list[str]:
    """The lists' citation URLs (list_url), in file order, each once."""
    out: list[str] = []
    for line in lines:
        url = list_url(line)
        if url and url not in out:
            out.append(url)
    return out


def in_citation_order(urls: Iterable[str]) -> list[str]:
    """Citation URLs as a row keeps them: each once, sorted by URL ignoring
    case (owners mix it), with the exact spelling breaking a tie."""
    return sorted(set(urls), key=lambda url: (url.lower(), url))


def citation(url: str) -> dict:
    """The `sources` item recording that the list at `url` cites a row."""
    return {"catalog": url.removeprefix("https://github.com/"), "url": url}


def is_citation(source: object) -> bool:
    """A `sources` item shaped as a sibling-list citation (see the module docstring)."""
    if not isinstance(source, dict) or set(source) != {"catalog", "url"}:
        return False
    name, url = source.get("catalog"), source.get("url")
    return isinstance(name, str) and isinstance(url, str) and list_url(url) == url and url == f"https://github.com/{name}"


def own_repository(entry: dict) -> str | None:
    """The GitHub repository a row names (`repo`, else `url`) as slug_of()
    keys it, which is what a list must link to cite the row; None for a row
    without one, or whose repository is this one."""
    for candidate in (entry.get("repo"), entry.get("url")):
        match = re.match(r"https://github\.com/([^/]+)/([^/#?]+)", str(candidate or ""))
        if match:
            repo = slug_of(*match.groups())
            return None if repo == SELF else repo
    return None


def list_repository(url: str) -> str:
    """A list's citation URL as slug_of() keys the repository it is."""
    return slug_of(*url.removeprefix("https://github.com/").split("/", 1))


def citations_of(entry: dict) -> list[str]:
    """The URLs of the sibling lists a row's `sources` records citing it, in its order."""
    return [source["url"] for source in entry.get("sources") or [] if is_citation(source)]


# What puts a row's citations right without reading anything; lint names it.
FIX = "python3 scripts/attribute_sources.py --offline --write"


def citation_problems(entry: dict) -> list[str]:
    """What is wrong with a row's citations, one sentence each (lint prefixes
    the slug): they come after every source a person wrote, in_citation_order,
    never as the row's only sources, only on a row with a GitHub repository of
    its own (own_repository), and never a list citing its own row."""
    sources = entry.get("sources")
    if not isinstance(sources, list):
        return []
    marks = [is_citation(source) for source in sources]
    urls = [source["url"] for source, cited in zip(sources, marks) if cited]
    if not urls:
        return []
    problems = []
    if all(marks):
        problems.append(
            "every source is a sibling-list citation; keep the source saying where the row was "
            "found (a citation only records which lists link the repository). A source shaped "
            '{"catalog": "owner/name", "url": "https://github.com/owner/name"} is read as a citation: '
            "if you found the row in that directory, name it in words, e.g. \"owner's awesome-jev\""
        )
    if marks != sorted(marks) or urls != in_citation_order(urls):
        problems.append(
            "sibling-list citations in sources must come after every other source, sorted by url, "
            f"each once; run {FIX}"
        )
    own = own_repository(entry)
    if own is None:
        problems.append(
            "sources cite sibling lists but the row has no GitHub repository of its own for them "
            f"to link; run {FIX}"
        )
    elif any(list_repository(url) == own for url in urls):
        problems.append(f"a sibling list cannot cite its own row; run {FIX}")
    return problems


def unlisted_citations(catalog: list, listed: list[str]) -> dict[str, int]:
    """Rows citing each list that `listed` (docs/sibling-lists.txt) does not name."""
    names = set(listed)
    unlisted: dict[str, int] = {}
    for entry in catalog:
        if not isinstance(entry, dict) or not isinstance(entry.get("sources"), list):
            continue
        for source in entry["sources"]:
            if is_citation(source) and source["url"] not in names:
                unlisted[source["url"]] = unlisted.get(source["url"], 0) + 1
    return dict(sorted(unlisted.items()))


def fetch_readme(repo_url: str) -> tuple[str, str]:
    """A list's README from GitHub's raw host (no API budget), as (url, text).
    The text is empty when none of the usual branch and file names answers."""
    match = GH.match(repo_url)
    if not match:
        return repo_url, ""
    slug = f"{match.group(1)}/{match.group(2)}"
    for branch in ("main", "master"):
        for name in ("README.md", "readme.md"):
            try:
                req = urllib.request.Request(
                    f"https://raw.githubusercontent.com/{slug}/{branch}/{name}",
                    headers={"User-Agent": "awesome-jev"},
                )
                with urllib.request.urlopen(req, timeout=20) as response:
                    return repo_url, response.read().decode("utf-8", "replace")
            except Exception:  # noqa: BLE001
                continue
    return repo_url, ""


def cited_in(body: str) -> set[str]:
    """The repositories a README links, as slug_of() keys."""
    return {
        slug_of(owner, name)
        for owner, name in GH.findall(body)
        if owner.lower() not in SKIP_OWNERS
    }


@dataclass(frozen=True)
class Harvest:
    """What one read of the lists found. `cited` maps a repository (slug_of)
    to the lists (as read_lists() gave them) whose README links it; `reached`
    and `unreached` split the lists by whether a README could be read.

    `same` pairs a list with the earlier one whose README it returned word for
    word. GitHub keeps serving a renamed repository's files under its old name,
    so one directory listed under both names would otherwise cite every row
    twice; such a list is reached but cites nothing, and the file should keep
    one line for it."""

    cited: dict[str, frozenset[str]]
    reached: tuple[str, ...]
    unreached: tuple[str, ...]
    same: tuple[tuple[str, str], ...] = ()

    def counts(self) -> collections.Counter[str]:
        """How many lists cite each repository, repositories in slug order, so
        most_common() breaks a tie by name rather than by chance."""
        return collections.Counter({slug: len(self.cited[slug]) for slug in sorted(self.cited)})


def harvest(
    lists: list[str],
    *,
    fetch: Callable[[str], tuple[str, str]] = fetch_readme,
    workers: int = WORKERS,
) -> Harvest:
    """Read every list's README and record which repositories each links."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(fetch, lists))
    cited: dict[str, set[str]] = {}
    reached, unreached = [], []
    first: dict[str, str] = {}
    same: list[tuple[str, str]] = []
    for url, (_, body) in zip(lists, fetched):
        if not body:
            unreached.append(url)
            continue
        reached.append(url)
        # One directory under two names (see Harvest): counted once, as the earlier line.
        earlier = first.setdefault(body, url)
        if earlier != url:
            same.append((url, earlier))
            continue
        for slug in cited_in(body):
            cited.setdefault(slug, set()).add(url)
    return Harvest(
        {slug: frozenset(urls) for slug, urls in cited.items()},
        tuple(reached),
        tuple(unreached),
        tuple(same),
    )
