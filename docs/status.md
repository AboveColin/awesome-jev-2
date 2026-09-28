# Ecosystem status

This page has two halves that age differently. The first is regenerated from
`catalog.json` by `scripts/build_docs.py` on every build, so it is current by
construction. The second is a dated snapshot, written at **2026-09-22** — a week
after the model entered early access on 2026-09-15 — and is meant to age; that
is the point of dating it.

## The catalogue, now

<!-- shape:start -->
|  |  |
| --- | --- |
| Entries | 1207 |
| Carrying code | 1179 |
| Official (TypeSafe AI's own) | 36 |
| Links with a dated 2xx response record | 1204 |
| Most recent successful link-check date (dates vary by row) | 2026-09-24 |
| Rows whose latest successful check is on that date | 1137 of 1207 |
| Rows citing a file where the project calls Jev (`evidence`; not a CI pass count) | 1074 |
| Rows citing a file that speaks Jev's request shape rather than building on Jev (`evidence.kind` `wire-shape`) | 55 |
| Rows citing only an example the project ships (`evidence.kind` `example-only`) | 0 |
| Rows with code citing no file and giving no reason (neither `evidence` nor `evidence_none`) | 0 |
| Rows naming the primitives a person read the code calling (`question_types`) | 100 |
| Machine text signal: rows whose cited file contains a primitive's request or answer shape (`primitives_seen`; not a reading, never counted as `question_types`) | 686 |
| Of those, rows with no `question_types`: the text signal is all that is recorded about their primitives | 637 |
| Machine signal: evidence under an examples directory, not yet judged ([review queue](review-queue.md#examples-dir)) | 22 |
| Machine signal: evidence resting on one model name or the API host ([review queue](review-queue.md#single-model-name)) | 76 |
| Machine signal: `tool-selection` suggested only by keyword-rule words dropped on 2026-09-27 ([review queue](review-queue.md#tool-selection-broad-words)) | 65 |
| Patterns covered | 18 of 18 |
| Rows whose `patterns` are exactly what the keyword rules suggest for their summary (agreement with the rules, not a review: any review of these rows was not recorded) | 758 of 1207 |
| Rows whose patterns a person recorded reading (`patterns_reviewed`) | 0 |
| Overview rows that are projects or plugins with code, listed apart as not yet indexed by pattern ([review queue](review-queue.md#unsorted-overview)) | 252 |
| Summaries that are the project's own GitHub description (`summary_source` `upstream-description`) | 890 of 1207 |
| Summaries taken from that description that no longer match it (`upstream-description-stale`) | 0 |
| Summaries marked as written for this catalogue (`curated`) | 0 |
| Chinese summaries hand-written | 196 of 1207 |
| Rows recording GitHub's creation date, last push and default-branch commit count for their repository (`repo_created_at`, `repo_pushed_at`, `repo_commits`; GitHub's facts at the last weekly refresh, not a judgement of upkeep) | 1134 of 1207 |
| Rows flagged `single-commit`: one commit on the default branch (the refresh sets and clears it from `repo_commits`) | 91 |
| Rows with a GitHub repository that at least one sibling directory links (`sources` citations, from the lists' READMEs at the last weekly read; a count of mentions, not a review) | 1129 of 1136 |
| Retired links | 2 |
<!-- shape:end -->

### When each repository was last pushed

GitHub's `pushed_at` for every row that records one (`repo_pushed_at`), as the
weekly refresh last read it, grouped by calendar month in UTC. A month says
when someone last pushed to any branch, not whether a project is maintained or
works; nothing here turns it into a verdict. The creation dates and commit
counts behind the same refresh are on the site and in the MCP server's rows.

<!-- pushed:start -->
| Month of the last push (UTC) | Rows |
| --- | --- |
| 2026-09 | 1134 |
<!-- pushed:end -->

### How many sibling directories link each repository

Every row with a GitHub repository, by how many of the sibling directories in
[`docs/sibling-lists.txt`](sibling-lists.txt) link that repository in their
README, as the weekly refresh last read them (`scripts/attribute_sources.py`
records each one in the row's `sources`). The lists copy from each other, so
this counts how widely a project is mentioned. It is not a review of the
project, and a repository no list links is not thereby worse.

<!-- cited-by:start -->
| Sibling directories linking the repository | Rows |
| --- | --- |
| 0 | 7 |
| 1 | 21 |
| 2 | 92 |
| 3–5 | 500 |
| 6–10 | 323 |
| 11–20 | 142 |
| 21 or more | 51 |
<!-- cited-by:end -->

### Coverage gaps

<!-- gaps:start -->
Every pattern has at least one entry.

Empty kinds:

- **`case-study`**. The catalogue has no case study documenting both cost and observed outcomes.

Thin — under 2.5% of the catalogue:

- `recommendation` (1 of 1207) — The first example is a movie recommender: retrieval narrows the field, and Jev parses the request and chooses from the shortlist.
- `retry-control` (6 of 1207) — Most apparent matches are false positives: an HTTP client advertising "observable retries" is not a retry decision. The first real one was a semantic circuit breaker asking whether an HTTP 200 is a silent failure.
- `feature-extraction` (8 of 1207)
- `support-triage` (8 of 1207)
- `data-extraction` (16 of 1207)
- `document-triage` (20 of 1207)
<!-- gaps:end -->

Two holes are in the research rather than the ecosystem: **Reddit** produced
nothing verifiable across four retrieval routes, and **X/Twitter** is barely
represented for the same reason. Both are gaps, not judgements.

Run `python3 scripts/counts.py` for the full breakdown by kind, language and
platform.

Link counts describe dated response records, and evidence counts describe saved
citations. They are not a count of successful current CI checks. The latest
successful link-check date can differ from an individual row's date. Catalogue
coverage does not imply that this repository ran the code or reproduced the
linked performance measurements; see [the review limits](vetting.md).

## Snapshot at 2026-09-22: what week one looked like

**The official material is the best material.** The cookbooks and pattern pages
in the vendor's docs are more useful than almost anything written about them,
and they are primary sources. If you only read five things, read those.

**Adoption was unusually fast.** First-class integrations landed within days
across the AI SDK, LangChain in both languages, Pydantic AI, LiteLLM, Effect,
Pydantic, Rig, ruby_llm and more, plus four or more hosted gateways. Production
integrations exist in repositories with six-figure star counts.

**Almost every number in circulation is vendor-reported.** The widely-quoted
speed and cost multiples come from the vendor's own workflow evaluations, whose
reference answers were derived from other models' judgements rather than human
ground truth. The vendor's launch post itself describes the headline figures as
an upper bound.

**Independent measurement is scarce, and the honest ones are the most useful
thing in this catalog.** A handful of projects published results that did not
flatter the model:

- A large agent framework ported the compaction approach, measured it, and
  concluded not to adopt it — recall came out below their existing summariser,
  and at a matched context budget it tied plain recency ordering.
- A news classifier found the model merely tied their incumbent on blind-judged
  headlines, and kept it in shadow mode rather than shipping it.
- A code-review tool measured materially more billed input for essentially no
  wall-clock gain, and recommended keeping the feature off by default.
- An independent tester found that reversing option order shifted a probability
  enough to cross a 0.9 threshold.

Cost was consistently the clear win. Quality was frequently a wash. Both of those
are useful to know before you build.

**A large fraction of "Jev projects" are not Jev.** Independent
reimplementations with a compatible wire format are among the most-starred
repositories mentioning the model, and are routinely miscatalogued as usage
examples. They are `kind: alternative` here with a `not-jev` flag. A compatible
API does not imply compatible calibration.

**Popularity and substance have not had time to correlate.** Four-figure star
counts sit on single commits; several notable projects declare no licence;
at least two ship the integration deliberately inert. Hence the `single-commit`,
`no-license` and `shadow-mode-only` flags.

**Nothing about the training method is published.** There is no paper, no reward
function, no dataset description and no reproducible evaluation for RLCD. An
unrelated 2023 paper abbreviates to the same four letters, which is a reliable
source of confusion.

## What to watch

- Whether independent benchmarks accumulate, and whether they keep landing on
  "cheap but comparable" rather than "better".
- Whether the option-ordering sensitivity reproduces. If it does, option order
  becomes part of everyone's prompt-freezing discipline.
- Whether a paper appears.
- Whether the alternatives converge on the wire format well enough that patterns
  really do become portable, calibration aside.
- Whether rate limits and pricing settle. The docs currently carry an explicit
  warning that limits can change without notice.
