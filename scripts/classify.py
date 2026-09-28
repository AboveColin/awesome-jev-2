"""Keyword rules that suggest a row's kind and decision patterns.

A suggestion from words, never a classification. The rules read a project's
own description and name: at discovery (discover_candidates.py) the GitHub
description and the repository name, and on a pull request's review card
(review_rows.py) the row's summary. They are a starting point and nothing more:
on the first bulk run of 223 rows they needed eight manual corrections, most of
them an SDK picking up a behavioural pattern from words describing its own API
("typed noul, choice and score" is not content scoring, and "observable
retries" is the HTTP client, not a retry decision). Read the suggestion, then
decide.

This lived in discover_candidates.py until that file passed 790 lines; it still
re-exports classify(), so `from discover_candidates import classify` works.

Since 2026-09-27 the tool-selection rule no longer counts "control", "harness"
or "screen" on their own, and counts a robot, an autonomous system, a vehicle
or a screen only beside a word for deciding or acting (TOOL_SELECTION_SETTING
and TOOL_SELECTION_ACTION). The broad rule it replaced is kept, as
classify_broad(), for one purpose: docs/review-queue.md lists the catalogue
rows it filed under tool-selection that the current rule would not, for a
person to re-read. Delete it together with that section once the section is
empty.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import re

# tool-selection is "which tool or action does the agent take next". Words that
# name that decision count on their own. Every alternative starts at a word
# boundary: the rule before 2026-09-27 had one only on its first few words, so
# "control" matched "remote control" and "uncontrolled" alike.
TOOL_SELECTION_DIRECT = (
    r"\b(browser|computer use|click|gui\b|next action|tool call|agent step|navigat|"
    r"tool routing|chains? .{0,14}primitive|reflex|which tool|picks? each action)"
)
# Words that name where an agent acts rather than the decision: a robot, an
# autonomous system, a vehicle, a screen. A robot arm choosing its next move is
# tool selection; "reads the screen through Accessibility" is not, on its own.
# So they count only beside a word for deciding or acting. "decis" is there
# because the "decid" stem misses "decision".
TOOL_SELECTION_SETTING = r"\b(robot|autonomous|drive[sn]?\b|screen)"
TOOL_SELECTION_ACTION = r"\b(decid|decis|action|step|command|move|which|next)"
# The rule until 2026-09-27, verbatim. It filed "Remote control for claude,
# codex, cursor…", "The harness for your harness" and "An Autonomous Agentic
# Agent for Mac" under tool-selection. Used only by classify_broad().
BROAD_TOOL_SELECTION = (
    r"\bbrowser|computer use|\bclick|\bgui\b|screen|next action|tool call|agent step|"
    r"control|robot|drive[sn]?\b|navigat|autonomous|tool routing|chains? .{0,14}primitive|"
    r"reflex|harness|which tool|picks? each action"
)


def tool_selection(has) -> bool:
    """The current tool-selection rule; `has(pattern)` searches the text."""
    return has(TOOL_SELECTION_DIRECT) or (has(TOOL_SELECTION_SETTING) and has(TOOL_SELECTION_ACTION))


def broad_tool_selection(has) -> bool:
    """The tool-selection rule as it was until 2026-09-27."""
    return has(BROAD_TOOL_SELECTION)


def classify(desc, name, lang=None) -> tuple[str, list[str]]:
    """(kind, up to three patterns) the rules suggest for a description and a
    name; the patterns are ["overview"] when no rule matches. `lang` is
    accepted for older callers and not read."""
    return _classify(desc, name, tool_selection)


def classify_broad(desc, name, lang=None) -> tuple[str, list[str]]:
    """classify() with the tool-selection rule it had until 2026-09-27. Only
    for replaying the old rules over the catalogue (docs/review-queue.md)."""
    return _classify(desc, name, broad_tool_selection)


def suggest(entry: dict, rules=classify) -> tuple[str, list[str]]:
    """What `rules` suggest for a catalogue row.

    catalog.json does not keep the GitHub description the rules read at
    discovery, so a row's summary and title stand in for it. For most rows
    from the bulk passes that is close: their summary is that description,
    normalised (docs/method.md, "The bulk pass").
    """
    return rules(entry.get("summary") or "", entry.get("title") or "")


def _classify(desc, name, tool_rule):
    d = (desc or "").lower()
    n = name.lower()
    t = f"{d} {n}"

    def has(p):
        return bool(re.search(p, t))

    if has(
        r"\b(alternative|jev-?like|jev-?style|reimplement|open-?jev|clone of|drop-?in replacement|"
        r"turn any .{0,24}llm into|local (take on|jev)|own decision model|fine-?tuned from|"
        r"without generating a single to|self-?hosted drop-?in)"
    ):
        kind = "alternative"
    elif has(
        r"\b(benchmark|bench\b|audit|leaderboard|capability (atlas|study)|head-?to-?head|"
        r"reproducible .{0,20}evaluation|measures how well|evaluation of jev)"
    ):
        kind = "benchmark"
    elif has(
        r"\b(sdk|client library|client for|idiomatic .{0,14}(client|sdk)|port of the|"
        r"bindings?\b|dependency-?free cli|small cli)"
    ):
        kind = "sdk"
    elif has(
        r"\b(mcp|skill\b|hook\b|plugin|extension|\.nvim|claude code|codex|neovim|vscode|cursor|"
        r"pytest|pre-?commit|starter\b)"
    ):
        kind = "plugin"
    elif has(
        r"\b(provider|integration|adapter|middleware|for (hono|django|rails|spring|langchain|duckdb))"
    ):
        kind = "integration"
    else:
        kind = "project"

    P = []

    def add(p):
        if p not in P:
            P.append(p)

    # Tightened: a circuit breaker genuinely decides whether to retry; a
    # benchmark about failure *attribution* does not, and matched before.
    if has(r"\bcircuit breaker|retry|retries|back-?off|resilien"):
        add("retry-control")
    if has(
        r"\brerank|re-?rank|relevance|retriev|\brag\b|semantic (search|find|sql|grep)|"
        r"\bgrep|ranking|rank(s|ing)? |select(or|ion) .{0,20}(context|evidence)|shortlist"
    ):
        add("search-ranking")
    if has(
        r"\b(which|cheapest|pick a) (model|llm)|model (routing|selection)|tier\b|"
        r"route .{0,16}model|route accordingly|when to use"
    ):
        add("model-routing")
    if has(
        r"\bclassif|categor|\btag\b|label(s|ling)?\b|taxonom|detect(s|ing|ion)?\b|identif|"
        r"sort(s|ing)?\b|triage"
    ):
        add("classification")
    # See TOOL_SELECTION_DIRECT: the one rule tightened on 2026-09-27.
    if tool_rule(has):
        add("tool-selection")
    if has(
        r"\bguard|block(s|ing)?\b|gate|safety|risk|secret|injection|moderat|spam|harmful|"
        r"malicio|permission|censor|sponsor|adblock|\bads?\b"
    ):
        add("safety-gating")
    if has(
        r"\bverif|validat|assert|lint(er|ing)?\b|review|quality|hallucinat|stop hook|"
        r"diagnostic|check(s|ing)?\b|claim|correctness"
    ):
        add("output-validation")
    if has(r"\bscore|rate[sd]?\b|grade|meter|judg"):
        add("content-scoring")
    if has(
        r"\bcompact|prune|trim|context (window|garbage|select)|token budget|history"
    ):
        add("context-compaction")
    if has(r"\bcalibrat|threshold|confidence|uncertain|human review|escalat"):
        add("human-escalation")
    if has(r"\bextract|parse|structured data|field"):
        add("data-extraction")
    if has(r"\bintent|support ticket|inbox|\bmail|email|customer"):
        add("intent-routing")
    if has(r"\bparallel|batch|fan-?out|many questions|more than 255|beyond 255"):
        add("fan-out")
    # Tightened: "suggest" alone matched a skill router, which is tool-selection.
    if has(r"\brecommend(s|ation|er)?\b|what to (watch|read|buy)|next-?best"):
        add("recommendation")
    if has(r"\bfeature (extraction|engineering)|training data|curation|dataset"):
        add("feature-extraction")
    if has(r"\bdocument|\binvoice|\breceipt|\bpdf\b|\bform\b"):
        add("document-triage")

    if not P:
        P = ["overview"]
    return kind, P[:3]
