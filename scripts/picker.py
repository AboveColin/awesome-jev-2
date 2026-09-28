#!/usr/bin/env python3
"""The primitive picker: picker.json, TypeSafe's own guidance on which
primitive fits a decision, arranged as a decision list (I25).

One file, three readers. lint.py holds it to the rules below; build_assets.py
draws it into docs/assets/primitive-picker-{en,zh}-{light,dark}.svg for the
README; the site's primitives view fetches it at runtime and walks it with
pickerSteps in site/catalog-core.mjs (scripts/tests/picker_cases.json holds
that walk and walk() below to one answer).

The shape is a decision list, because that is what the figure draws: from
`start`, each node asks a yes/no question; yes ends at a leaf, no moves to the
next node, and the last node's no ends at a leaf. Every node and every leaf
cites the docs.typesafe.ai page it follows in source_url: the list arranges the
vendor's design guidance and recommends no catalogue row. A leaf may name a
primitive (the question_types enum) and a pattern (a patterns.json key) whose
rows the surfaces count beside it, from _stats.primitive_layers_by_pattern. No
text may state a number or name an answer field: limits live in compat.json
and what an answer carries in the primitives figure (build_assets.PRIMS), and a
second copy here would drift from them.

Standard library only.
"""

from __future__ import annotations

import json
import pathlib
import re
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATH = ROOT / "picker.json"

SOURCE_PREFIX = "https://docs.typesafe.ai/"
ANSWERS = ("yes", "no")
TOP_KEYS = frozenset({"_comment", "zh_machine", "start", "nodes", "leaves"})
NODE_KEYS = frozenset({"id", "question_en", "question_zh", "source_url", "branches"})
LEAF_REQUIRED = frozenset({"id", "label_en", "label_zh", "note_en", "note_zh", "source_url"})
LEAF_OPTIONAL = frozenset({"primitive", "pattern_key"})
NODE_TEXT = ("question_en", "question_zh")
LEAF_TEXT = ("label_en", "label_zh", "note_en", "note_zh")
ID = re.compile(r"^[a-z][a-z0-9-]*$")
CJK = re.compile(r"[\u3400-\u9fff]")
# A digit, or the name of a field an answer carries: facts that compat.json and
# the primitives figure own.
FACT = re.compile(r"\d|\b(?:probabilities|confidence|legend)\b|置信度|图例", re.IGNORECASE)


class NotADecisionList(ValueError):
    """picker.json's nodes do not form the chain the figure draws."""


def load(path: pathlib.Path | None = None) -> dict:
    """picker.json (or `path`), read when called so a test can patch PATH."""
    return json.loads((path or PATH).read_text(encoding="utf-8"))


def _by_id(items: Any) -> dict[str, dict]:
    return {item["id"]: item for item in items or [] if isinstance(item, dict) and isinstance(item.get("id"), str)}


def _branch(node: dict, answer: str) -> dict | None:
    found = [b for b in node.get("branches") or [] if isinstance(b, dict) and b.get("answer") == answer]
    return found[0] if len(found) == 1 else None


def walk(picker: dict) -> tuple[list[tuple[dict, dict]], dict]:
    """(steps, last): every node from `start` in reading order with the leaf
    its yes ends at, and the leaf the last node's no ends at. Raises
    NotADecisionList naming the first node that breaks that shape."""
    nodes, leaves = _by_id(picker.get("nodes")), _by_id(picker.get("leaves"))
    current = picker.get("start")
    if not isinstance(current, str) or current not in nodes:
        raise NotADecisionList(f"start: {current!r} is not a node id")
    steps: list[tuple[dict, dict]] = []
    seen: set[str] = set()
    for _ in nodes:  # at most one pass per node, so a malformed file cannot spin
        node, where = nodes[current], f"nodes[{current}]"
        seen.add(current)
        branches = node.get("branches")
        yes, no = _branch(node, "yes"), _branch(node, "no")
        if not isinstance(branches, list) or len(branches) != 2 or yes is None or no is None:
            raise NotADecisionList(f"{where}: needs exactly two branches, one answering yes and one no")
        if set(yes) != {"answer", "leaf"} or not isinstance(yes["leaf"], str) or yes["leaf"] not in leaves:
            raise NotADecisionList(f'{where}: yes must end at a leaf, as {{"answer": "yes", "leaf": <leaf id>}}')
        steps.append((node, leaves[yes["leaf"]]))
        target = no.get("leaf", no.get("node"))
        if not isinstance(target, str):
            raise NotADecisionList(f"{where}: no must name a node or a leaf by its id")
        if set(no) == {"answer", "leaf"} and target in leaves:
            return steps, leaves[target]
        if set(no) != {"answer", "node"} or target not in nodes:
            raise NotADecisionList(
                f'{where}: no must move to a node, as {{"answer": "no", "node": <node id>}}, or end at a leaf'
            )
        if no["node"] in seen:
            raise NotADecisionList(f"{where}: no leads back to {no['node']!r}; the list must not loop")
        current = no["node"]
    raise NotADecisionList(f"nodes[{current}]: the list never ends at a leaf")


def sources(picker: dict) -> list[str]:
    """Every source_url once, in reading order (a node, then the leaf its yes
    ends at; the last leaf at the end): the order the figure numbers them in."""
    steps, last = walk(picker)
    urls = [url for node, leaf in steps for url in (node["source_url"], leaf["source_url"])]
    return list(dict.fromkeys([*urls, last["source_url"]]))


def layers(leaf: dict, by_pattern: dict[str, dict[str, dict[str, int]]]) -> dict[str, int] | None:
    """The counts printed beside a leaf that names a primitive and a pattern:
    {"read", "signal_only"} from _stats.primitive_layers_by_pattern. None for
    any other leaf."""
    primitive, pattern = leaf.get("primitive"), leaf.get("pattern_key")
    if not (primitive and pattern):
        return None
    return by_pattern.get(pattern, {}).get(primitive, {"read": 0, "signal_only": 0})


def _text_problems(where: str, item: dict, keys: tuple[str, ...], names: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    """Each text present: non-empty, Chinese where it should be, and stating
    no number or answer field. A missing key is _key_problems' to report."""
    found = []
    for key in (key for key in keys if key in item):
        value = item[key]
        if not isinstance(value, str) or not value.strip():
            found.append((f"{where}.{key}", "must be a non-empty string"))
            continue
        # A leaf labelled with a primitive's name keeps the name in Chinese too.
        named = key == "label_zh" and value == item.get("label_en") and value in names
        if key.endswith("_zh") and not named and not CJK.search(value):
            found.append((f"{where}.{key}", "is not Chinese"))
        if FACT.search(value):
            found.append((
                f"{where}.{key}",
                f"states {FACT.search(value).group(0)!r}: a number or an answer field belongs in compat.json "
                "and the primitives figure, not here",
            ))
    return found


def _source_problems(where: str, item: dict) -> list[tuple[str, str]]:
    if "source_url" not in item:
        return []  # _key_problems reports it missing
    url = item["source_url"]
    if not isinstance(url, str) or not url.startswith(SOURCE_PREFIX) or url == SOURCE_PREFIX or " " in url:
        return [(f"{where}.source_url", f"must name the {SOURCE_PREFIX} page (and heading) this step follows")]
    return []


def _key_problems(where: str, item: dict, required: frozenset, optional: frozenset = frozenset()) -> list[tuple[str, str]]:
    found = [(where, f"lacks {key!r}") for key in sorted(required - set(item))]
    found += [(where, f"has unknown field {key!r}") for key in sorted(set(item) - required - optional)]
    return found


def _item_problems(kind: str, items: Any, required: frozenset, optional: frozenset) -> list[tuple[str, str]]:
    if not isinstance(items, list) or not items:
        return [(f"picker.json {kind}", "must be a non-empty array of objects")]
    found: list[tuple[str, str]] = []
    ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            found.append((f"picker.json {kind}[{index}]", "must be an object"))
            continue
        name = item.get("id")
        where = f"picker.json {kind}[{name if isinstance(name, str) else index}]"
        if not isinstance(name, str) or not ID.match(name):
            found.append((where, "id must be lower-case letters, digits and hyphens"))
        elif name in ids:
            found.append((where, "repeats an id"))
        else:
            ids.add(name)
        found += _key_problems(where, item, required, optional)
    return found


def problems(picker: Any, pattern_keys: set[str] | list[str], primitives: set[str] | list[str]) -> list[tuple[str, str]]:
    """Every way picker.json breaks the rules, as (where, message), empty when
    it keeps them. `pattern_keys` are patterns.json's keys and `primitives` the
    question_types enum."""
    if not isinstance(picker, dict):
        return [("picker.json", "must be an object")]
    found = _key_problems("picker.json", picker, TOP_KEYS - {"_comment"}, frozenset({"_comment"}))
    if not isinstance(picker.get("zh_machine"), bool):
        found.append(("picker.json.zh_machine", "must be true while a model's Chinese is unreviewed, else false"))
    found += _item_problems("nodes", picker.get("nodes"), NODE_KEYS, frozenset())
    found += _item_problems("leaves", picker.get("leaves"), LEAF_REQUIRED, LEAF_OPTIONAL)
    nodes, leaves = _by_id(picker.get("nodes")), _by_id(picker.get("leaves"))
    for name, node in nodes.items():
        where = f"picker.json nodes[{name}]"
        found += _text_problems(where, node, NODE_TEXT) + _source_problems(where, node)
    for name, leaf in leaves.items():
        where = f"picker.json leaves[{name}]"
        found += _text_problems(where, leaf, LEAF_TEXT, tuple(primitives)) + _source_problems(where, leaf)
        primitive, pattern = leaf.get("primitive"), leaf.get("pattern_key")
        if primitive is not None and primitive not in primitives:
            found.append((f"{where}.primitive", f"{primitive!r} is not one of: {', '.join(primitives)}"))
        if pattern is not None and pattern not in pattern_keys:
            found.append((f"{where}.pattern_key", f"{pattern!r} is not a pattern in patterns.json"))
        if primitive is not None and pattern is None:
            found.append((where, "names a primitive but no pattern_key, so nothing can be counted beside it"))
    try:
        steps, last = walk(picker)
    except NotADecisionList as error:
        return found + [(f"picker.json {str(error).split(':', 1)[0]}", str(error).split(": ", 1)[1])]
    reached = [node["id"] for node, _ in steps]
    for name in nodes:
        if name not in reached:
            found.append((f"picker.json nodes[{name}]", "is never reached from start"))
    used = [leaf["id"] for _, leaf in steps] + [last["id"]]
    for name in leaves:
        if used.count(name) != 1:
            found.append((
                f"picker.json leaves[{name}]",
                "is never reached" if name not in used else "is reached from more than one node",
            ))
    return found
