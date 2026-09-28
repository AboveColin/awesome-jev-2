"""The link to the file a row's `evidence` cites, built as the site builds it.

A Python copy of site/catalog-core.mjs evidenceUrl(), for the pages generated
here (the READMEs, docs/by-pattern/, docs/review-queue.md): the file
`evidence.path` names, at HEAD of the repository that `repo`, or else `url`,
points at, and only when that is an https github.com address with an owner and
a name. HEAD, never a commit, as the citation is re-checked against the default
branch every week (scripts/verify_claims.py): the link opens the file as it is
now, which may have changed since a person read it, and stops resolving once
the file moves or the repository goes.

The site reads the address with the browser's URL parser (the WHATWG URL
Standard), so this follows that standard for an https address far enough that
the two give the same link for anything written as a GitHub address: surrounding
spaces, tabs and newlines dropped, any run of slashes after the scheme, userinfo,
a port, a percent-encoded host, backslashes, `.` and `..` segments, and the
characters a path percent-encodes. scripts/tests/evidence_url_cases.json holds
cases both test suites run, and scripts/tests/test_call_site_links.py runs the
site's function beside this one over the whole catalogue and a few thousand
made-up addresses. One difference is left on purpose: a browser maps a non-ASCII
host through IDNA (a full-width "ｇｉｔｈｕｂ.com" is github.com to it), which this
does not; no catalogue address has a non-ASCII host.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import re
import urllib.parse

GITHUB_HOST = "github.com"

# What the URL Standard does to an address before reading it: trims C0 controls
# and spaces from both ends and removes every tab and newline.
_TRIM = "".join(chr(code) for code in range(0x21))
_TAB_NEWLINE = str.maketrans("", "", "\t\n\r")
# A string holding half a surrogate pair is not valid Unicode; a browser's
# string conversion puts U+FFFD in its place before parsing.
_SURROGATE = re.compile("[\ud800-\udfff]")
# The printable ASCII a URL path percent-encodes (Node's parser agrees): the rest
# of printable ASCII is kept, and C0 controls and anything past "~" are encoded.
_PATH_ENCODED = frozenset(' "<>^`{}')
_SINGLE_DOT = (".", "%2e")
_DOUBLE_DOT = ("..", ".%2e", "%2e.", "%2e%2e")
# encodeURIComponent() keeps ASCII letters, digits and - _ . ! ~ * ' ( );
# urllib keeps the letters, digits and - _ . ~ on its own.
_COMPONENT_SAFE = "!'()*"


def _path_segment(segment: str) -> str:
    return "".join(
        urllib.parse.quote(ch, safe="") if ord(ch) < 0x20 or ord(ch) > 0x7E or ch in _PATH_ENCODED else ch
        for ch in segment
    )


def repository(candidate: object) -> tuple[str, str] | None:
    """(owner, name) of an https github.com address, as its path spells them
    after parsing (percent-encoded where the standard encodes), or None."""
    if not isinstance(candidate, str) or not candidate:
        return None
    text = _SURROGATE.sub("\ufffd", candidate.strip(_TRIM).translate(_TAB_NEWLINE))
    scheme, colon, rest = text.partition(":")
    if not colon or scheme.lower() != "https":
        return None
    # Any number of slashes or backslashes may follow a special scheme; the
    # authority runs to the next one, or to a query or fragment.
    authority, path = re.match(r"([^/\\?#]*)([^?#]*)", rest.lstrip("/\\")).groups()
    host, _, port = authority.rpartition("@")[2].partition(":")
    if port and not (port.isascii() and port.isdigit() and int(port) <= 0xFFFF):
        return None
    try:
        host = urllib.parse.unquote_to_bytes(host).decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not (host.isascii() and host.lower() == GITHUB_HOST):
        return None
    kept: list[str] = []
    for segment in re.split(r"[/\\]", path)[1:]:
        dots = segment.lower()
        if dots in _DOUBLE_DOT:
            if kept:
                kept.pop()
        elif dots not in _SINGLE_DOT:
            kept.append(_path_segment(segment))
    parts = [part for part in kept if part]
    return (parts[0], parts[1]) if len(parts) >= 2 else None


def evidence_url(entry: dict) -> str | None:
    """https://github.com/<owner>/<name>/blob/HEAD/<evidence.path>, each path
    segment encoded as encodeURIComponent() encodes it, or None when the row
    cites no file or neither `repo` nor `url` is a GitHub repository."""
    evidence = entry.get("evidence")
    path = evidence.get("path") if isinstance(evidence, dict) else None
    if not path or not isinstance(path, str):
        return None
    for candidate in (entry.get("repo"), entry.get("url")):
        found = repository(candidate)
        if found is None:
            continue
        try:
            encoded = "/".join(urllib.parse.quote(segment, safe=_COMPONENT_SAFE) for segment in path.split("/"))
        except UnicodeEncodeError:
            # Half a surrogate pair: encodeURIComponent() throws, and the site
            # moves on to the next address, which fails the same way.
            continue
        return f"https://{GITHUB_HOST}/{found[0]}/{found[1]}/blob/HEAD/{encoded}"
    return None
