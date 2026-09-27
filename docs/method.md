# Data and method

How the first build of this catalog was produced, what was checked, and where it
is weakest. If you want to reproduce or audit it, this is the page.

## Pipeline

1. **Establish the primary facts first.** The official docs serve raw Markdown at
   `<page>.md`, so the API reference, primitives, confidence, models and
   limitations pages were fetched and read directly rather than summarised. Every
   claim about the model in this repo traces to one of those.
2. **Sweep in parallel, along four axes.** Official sources; platform and
   framework integrations; open-source projects and packages; articles, videos
   and discussion. Four passes, each required to cite a URL per claim and to mark
   anything it could not confirm.
3. **Verify code entries at the call site.** For every row claiming code, the
   actual calling file was read to confirm which primitives are used. This is
   where README descriptions and reality diverge most often.
4. **Verify repository metadata from the API.** Stars, licence, creation date and
   last push came from the GitHub API on 2026-09-22, not from badges.
5. **Reject aggressively.** See "What was excluded".
6. **Write both summaries by hand**, English and Chinese, from what the page
   actually said.
7. **Validate and generate.** `scripts/lint.py` then `scripts/build_readme.py`.

## What the first build checked, and what it found

- **148 entries**, 124 carrying code, 36 official.
- **Two agent reports contradicted each other twice**, and both conflicts were
  resolved by direct inspection rather than by majority:
  - A Discord moderation bot was called a name collision by one pass. Reading
    `moderator.py` showed a real `typesafe` import and `jev-latest` default. It
    stayed in.
  - A widely-starred repository was catalogued by the community site as a visual
    inference tool using Jev. Scanning all 52 of its files found **zero**
    references to the API. Its own README says it is a research starter, not a
    copy. It was reclassified as `alternative` with a `not-jev` flag.
- **A fabricated integration was found and excluded**: a skills repository
  documenting a Jev API that does not exist, with primitives' meanings inverted,
  linking to a repository that returns 404.
- **The linter caught a bug in its own rule.** The `official` check originally
  accepted only `typesafe.ai` hosts, which wrongly rejected the vendor's own
  GitHub org. The rule was widened to the org and no further.

## Call-site text is re-checked separately from human review

A row carrying `question_types` asserts which primitives a project's code calls.
That was true when a person read the call site, and nothing stopped it going
stale — an upstream refactor could remove the integration entirely and this
catalog would keep claiming it.

Readable repository sources record `evidence`: the file the claim was read in,
strings from that file, and the reported reading date in `read_on`.
`scripts/verify_claims.py` fetches
each one from the repository's default branch and asserts those strings are
still there. A scheduled job runs it weekly and opens an issue on failure,
rather than failing the build — a moved file needs a reviewer to distinguish a
rename from a removed integration.

The evidence count is the number of stored citations, not the number that passed
the latest job. A successful string match establishes only that those strings
remain in the fetched file. It does not execute a call path, check API
compatibility, reproduce performance, or renew the human review date. The
workflow report and any resulting issue must be read to assess its latest run.

Deliberately unpinned to a commit. Pinning would verify a historical snapshot
forever and never notice a removal, which defeats the purpose.

The first backfill was machine-assisted and human-reviewed: a `--discover` mode
reads each repository and proposes a path, then a person checks it. That review
mattered — the discoverer favoured test files over implementations in seven
cases, and proposed the same file for all four of this repo's own examples. It
also caught a mistake in the review itself: one hand-written override cited a
file that did not contain the strings claimed, and the verifier failed it on the
first real run.

Rows whose source is not a readable repository file — a docs page, a video, a
paywalled article — carry `evidence_none` saying which, rather than a fabricated
citation.

## Discovery is crowdsourced, verification is not

There are dozens of Jev directories. Each is a different person's sweep of the
same ecosystem, so their union is a far better discovery surface than any single
one — including this one. `docs/sibling-lists.txt` names them, and
`scripts/discover_candidates.py` harvests them, ranks repositories by how many
cite each, and then reads the candidate's own code looking for a call site.

The two halves matter separately. Crowd agreement finds things: a repository
cited by twenty lists is worth looking at. Crowd agreement does not verify
anything: these lists copy from each other, so one miscataloguing propagates
everywhere. The most-starred "Jev visual inference tool" in this ecosystem
contains zero references to the API and is listed as a Jev project almost
universally.

So the script emits a shortlist with a verdict per candidate — `calls-jev` with
the file and strings that prove it, `mentions-only` when the README claims what
the code does not, or `no-signal`. A `calls-jev` verdict is not a catalog row.
Someone still reads it and writes the summary.

The first aggregation run harvested 32 lists, found 1,885 distinct repositories
cited, verified the 45 most-cited that were missing here, and added 34. Six were
`mentions-only` — including one cited by twenty lists — and four were dropped
because their only Jev reference was in a fixture named `fake_jev`, which proves
the request shape and nothing else.

Sibling lists that ship no licence can be used as pointers but not as prose: a
URL is a fact, a description is someone's writing. Rows discovered that way were
re-read at the call site and summarised independently.

Since 2026-09-27, who proposed a row is a caveat like any other. A row whose
`sources` include the fixed string `author submission` — the project's own
author or maintainer asked for it — carries the `self-submitted` flag, and
`lint.py` fails if either appears without the other. The flag is declared by
the submitter, never inferred: GitHub handles are rarely recorded and an owner
is often an organisation, and matching the wording of a note is guesswork. The
backfill therefore covered only rows already recorded as `author submission`.
Rows recorded as `maintainer submission` (this list's maintainer adding a row on
their own initiative) or `community submission` were not reclassified, so the
flag's absence is not evidence that a row was not self-submitted.

### The bulk pass, and what it cost

A second aggregation run verified the 320 most-cited repositories missing here
and added 223. At that volume two standards had to bend, and both are recorded
in the data rather than hidden:

- **Summaries are the project's own description**, normalised, rather than a
  sentence written after reading the code. What _was_ read is the call site,
  and `evidence` on every row proves it.
- **Chinese is bulk-translated**, so those rows carry `zh_machine: true`. The
  counts script reports the split — 183 of 404 hand-written at the time of
  writing — because a catalogue that claimed all of them were would be lying
  about the one thing it sells.

Patterns were suggested by keyword rules over the description and then
reviewed. The review caught eight errors in 223, almost all of the same shape:
an SDK picking up a behavioural pattern from words describing its own API.
"Typed noul, choice and score" is an API surface, not content scoring;
"observable retries" is an HTTP client, not a retry decision. One was a plain
regex bug — `form\b` with no leading boundary matched "platform" and filed a
.NET SDK under document triage.

`retry-control` went from zero to one genuine example, a semantic circuit
breaker that asks whether an HTTP 200 is a silent failure. The other apparent
matches were false positives and were removed. `recommendation` is still empty
across 32 lists and 1,887 repositories, which is now a reasonably strong claim
that nobody has published one.

### The long tail, 2026-09-22

A third run took the next 700 most-cited repositories and added 401, taking the
catalogue from 404 to 805. The median candidate was cited by two lists and had
two stars, so this pass is mostly the long tail rather than anything popular.
The same two concessions apply, and the same `zh_machine` flag records them.

Running at this size broke three things that had worked at 400 rows, all of
them in the machinery that keeps the catalogue honest rather than in the data:

- Two of the first three `path-gone` verdicts were transient fetch failures, not
  deleted files. The raw-file fetch now retries once before believing a miss.
- Scraping github.com HTML for link status hit its rate limit a few dozen rows
  in, so most GitHub rows never got stamped. Bare repository URLs now go through
  the authenticated API; paths inside a repository still go through HTTP,
  because the API answering for the repository says nothing about one file.
- The published repository description still said 148. It is the one claim
  that lives in GitHub's database rather than in git, so no build had ever
  checked it. It is checked now.

`recommendation` is still empty.

### The first weekly cycle, 2026-09-24

The scheduled jobs ran for the first time, and each surfaced something only
running could:

* The call-site re-read failed 18 of 721 claims a day after they were read.
  Fifteen call sites had moved in refactors; two repositories had been deleted
  and were retired with a reason; and one project had removed its Jev
  integration on purpose, with a published measurement of why. That row stayed
  as a negative result under a new `evidence_none` value, `removed-upstream`.
* Discovery proposed 80 candidates. Four were catalogued projects under an old
  or new name, which led to the weekly refresh following renames. Sixteen
  looked test-only; every one had a real call site the scanner missed —
  because it had no C or C++ at all, and read only files named after Jev.
  Both are fixed, and the language list is now checked against the schema.
* Of the 76 added, nine are reimplementations of the interface rather than
  Jev, including one with more stars than anything else found this week. The
  keyword classifier filed all nine as ordinary projects; each was corrected by
  hand.
* Four pull requests from outside contributors were merged after their claims
  were re-read against the code, and nineteen more sibling directories were
  added to the harvest.

### The second discovery batch, 2026-09-24

With 51 sibling directories instead of 32, the harvest cited 3,285 repositories,
2,368 of them uncatalogued. The 400 most-cited were read; 325 had a call site,
and 323 were added — taking the catalogue past 1,200.

* `recommendation`, empty since the first build, got its first example: a movie
  recommender that narrows 4,800 films by retrieval, then has Jev parse the
  request and choose from the shortlist. The absence recorded above was true
  for every list harvested at the time; it is not true any more.
* Twenty-two rows are reimplementations of the interface, among them wrappers
  that serve another vendor's model in Jev's API shape. The classifier again
  filed them as Jev projects.
* Independent measurements outside English arrived — Russian and Spanish
  calibration audits, and Brazil's national exam — which is the gap the status
  page lists as worth watching.
* The scanner learned two more places a call site hides: Google Apps Script
  (`.gs`), and extensionless CLI scripts named after Jev.
* Two candidates were declined with a reason in `docs/declined.txt`: an early
  copy of a catalogued project, and an account-pooling gateway.

## Why a status code is not a verdict

Every row's `link_status` says the URL answered. That is all it says. It does not
mean the code runs, the project is maintained, the benchmark is sound, or the
approach suits your system.

The distinction matters more here than in most catalogs, because this ecosystem
is days old. A repository can have four figures of stars, one commit, no licence
and a description written for a launch-week audience. Popularity and substance
have not had time to correlate. That is why `stars` is documented in the schema
as "a popularity signal, not a quality verdict", and why `single-commit`,
`no-license`, `archived` and `shadow-mode-only` exist as flags.

Since 2026-09-27, the READMEs and the pattern pages print `stars` as a band —
★10+, ★100+, ★1k+, ★10k+ or ★100k+, and nothing under 10 — and order rows by
band, then title, where they used to print and sort by the exact count. Most
counts move every week, so every weekly refresh rewrote over a thousand
generated lines for a precision no reader of a list needs: the refresh of
2026-09-23 (b8bae37) changed 220 rows, all of them stars only, and 32 generated
files. Replaying that refresh through today's generator, exact counts change
1,158 lines each way in 32 files; bands change 24 lines each way in 6 files,
all of them the 3 rows that crossed the 10-star floor. `catalog.json`
keeps the exact count and still changes every week; the site and the MCP server
still show and sort by it, so inside a band their order can differ from the
README's. The README's link to the site screenshot still changes with any edit
to `catalog.json`, because the site it shows sorts by the exact count.
`scripts/tests/test_star_bands.py` moves every count inside its band on a copy
of the catalogue, runs every generator, and requires every generated file to
come out the same except that link.

## Field precedence

When sources disagree:

1. The official raw Markdown docs win on anything about the model.
2. A platform's own docs win on how to reach the model through that platform.
3. The code at the call site wins over any prose describing it, including the
   project's own README.
4. The GitHub API wins over README badges.
5. Where a page's `<title>` and on-page heading differ, the heading a reader sees
   is used, and `notes` records the discrepancy.

## What was excluded

- **Content-farm and SEO rewrites of the launch announcement.** Dozens exist.
  Exclusion criterion: adds no observation of its own.
- **Press-release redistributions.** Many outlets carried the same wire copy.
- **Fabricated API documentation**, including the community site's own `/jev-api`
  page, whose request shape matches neither the official API nor that same
  site's other documentation.
- **Name collisions.** "JEV" is also Japanese encephalitis virus, a person's
  name, an Eve Online asset manager, a smart-camera vision framework, a Joomla
  component and several car models. Every candidate was checked for whether it
  genuinely concerns TypeSafe's model. All searching used qualifying terms;
  bare "JEV" returns mostly noise.
- **Claimed research papers.** There is no published paper for the training
  method. An unrelated 2023 paper abbreviates to the same four letters, and an
  arXiv link labelled as "the paper" is almost certainly that one.

## Known limits

- **Catalogue code and the live API were not executed as part of this review.**
  Treat all rows as untested by this repository, even when `code-untested` is
  absent. That flag is an additional caveat, not a complete testing-status
  field. Repository generation checks and package smoke tests validate this
  repository's tooling; they do not test the catalogued integrations against
  the live API.
- **Performance claims were not reproduced.** Rows repeating vendor benchmarks
  carry `vendor-reported`. Independent reports keep their authors' methods and
  limitations; inclusion does not turn those reports into our own reproduction.
- **Reddit produced nothing verifiable.** Four retrieval routes failed. There is
  no Reddit row, which is a gap rather than a judgement that none exists.
- **X/Twitter is barely represented**, for the same reason.
- **Video content was verified by metadata only.** Channel, title and existence
  were confirmed; the demonstrations inside were not reviewed, and the rows say
  so.
- **The ecosystem is far larger than this catalog.** Searching for the model
  alongside the vendor name returns repositories in the thousands. This is a
  curated subset chosen for being verifiable, not an enumeration. Nobody can
  enumerate it at this growth rate.
- **Star counts move hourly** and were true on 2026-09-22.

## Reproducing it

```bash
git clone https://github.com/kydlikebtc/awesome-jev
cd awesome-jev

python3 scripts/check.py         # every check lint runs, in lint's order; --list names them

# or one at a time:
python3 scripts/sort_catalog.py  # keep catalog.json and retired.json in slug order
python3 scripts/lint.py          # schema plus cross-entry invariants
python3 scripts/build_readme.py  # regenerate both READMEs and docs/by-pattern/
python3 scripts/counts.py        # coverage, with gaps marked
python3 scripts/check_links.py   # sweep every URL, report only
python3 scripts/verify_claims.py # re-read every cited call site
python3 scripts/build_assets.py  # regenerate the README figures
python3 scripts/build_compat.py  # regenerate the compatibility tables
python3 scripts/regenerate.py    # or: every generator above, in order
```

`refresh_metadata.py` and `check_links.py` need `GITHUB_TOKEN` set, and
`verify_claims.py` wants it — unauthenticated GitHub is 60 API requests an hour
and no GraphQL at all, which will not cover a full sweep. Locally,
`GITHUB_TOKEN=$(gh auth token)` does. `--discover` proposes
evidence for a row that has none; the proposal is a starting point for a
person, never written automatically.

`check_links.py --write` stamps `checked` and `link_status` on rows that
answered. It never retires a row: that needs a human-written reason.

Since 2026-09-27, `catalog.json` and `retired.json` are kept in slug order and
`lint.py` fails when either is not. The order carries no meaning: the figures
and docs only count rows, while the READMEs, pattern pages, site and MCP server
each sort for themselves, with slug now the last tie-break in every one of those
orders, so rows that tie on everything else (forks sharing a title and star
count) no longer fall back to their position in the file. The fixed order exists
only so that pull requests adding different rows insert at different places
instead of all appending at the end and conflicting.

Since 2026-09-27, `scripts/check.py` holds the one list of the checks `lint`
runs, in its order. The list used to be written out four times — in
`lint.yml`, in `CONTRIBUTING.md`, in the pull-request template and in the
weekly `metadata` refresh — and the copies had drifted: the contributor
instructions named a handful of the checks, so a pull request could pass them
and still fail `lint` on the unit tests, the site data or the curated
collections, and `metadata` pushed to `main` after only the generators and
four checks. Now `lint` runs `check.py --ci`; its `regenerate` job and
`metadata` run `check.py --ci --quick` — every check but the preview images,
which `pages` renders at deploy — on what they are about to commit; the
contributor instructions and the template name `check.py --fix`, which first
sorts the catalogue. A unit test fails if `lint.yml` runs a script the list
does not cover. Each check still runs even after an earlier one fails, so one
run shows every problem. Locally, a check whose tool is missing — Node.js for
the site's filter tests, Chrome for the preview images — is reported as
skipped, never as passed; in CI a missing tool fails the run. `metadata` now
commits on the runner first and runs the checks strictly against that commit
before pushing, so a regenerated file its `git add` left out would fail too.

Since 2026-09-27, every rule `lint.py` enforces is pinned by a unit test,
`scripts/tests/test_lint.py`: each test starts from a row that passes
everything, breaks one rule, and checks that lint reports exactly that one
finding in that rule's own words. Before, only the slug-order and
self-submission rules had tests, so any other rule written backwards would have
passed CI and let through every row it was meant to stop.
The same file holds the schema to what the validator actually does. `lint.py`
implements the part of JSON Schema the schema uses, and a keyword it does not
know (`oneOf`, `format: date`) is ignored rather than rejected, so a constraint
added to `schema/entry.schema.json` could look enforced while checking nothing.
The tests now fail when the schema uses a keyword, `format` or `type` outside
that part, until `validate()` implements it. What lint accepts and rejects did
not change.

Since 2026-09-27, the three weekly jobs that read GitHub (`links`, `claims`,
`metadata`) tell a rate limit from a refusal, keep what they read before one,
and say what they spent. Before, every 403 from the API ended the run — so one
repository GitHub blocks would have stopped the weekly refresh before it wrote
anything — while a 429 from the raw-file host counted as a deleted file, the
link sweep in `links` ran without a token, and `metadata` cut its sweep's
report to five lines, so how many links were stamped or refused was never
visible. GitHub documents the workflow token's budget as 1,000 REST requests an
hour per repository; yet the scheduled run on 2026-09-23 made over a thousand
authenticated requests in under two minutes, and the 734 repository reads at
the end of it met no limit. Rather than plan around either figure, every run
now records GitHub's `x-ratelimit-*` headers and writes what it spent and what
is left to its job summary.

- A rate limit (403 or 429 with `x-ratelimit-remaining: 0`, a `retry-after`, or
  "rate limit" in the message) is waited out once — at most 90 seconds, as
  GitHub asks — then that budget is closed for the run and the rows it would
  have read are counted as skipped, never as gone or failed. A budget with
  fewer than 50 requests left (a tenth, for a small one) is not spent further
  until it resets, leaving room for the job's own issue and dispatch calls.
  A 403 or 451 without those signals is a repository GitHub will not serve: one
  row, listed for a person, not the end of the run.
- `refresh_metadata.py` reads a hundred repositories per GraphQL query — about
  a dozen requests for the whole catalogue — and reads over REST any row the
  query did not answer. `--compare` reads rows both ways; on 203 rows (every
  `NOASSERTION` licence, every archived row, 40 unlicensed and 110 random) and
  two renamed repositories the two gave identical facts.
- `verify_claims.py` reads each cited file at `HEAD` on the raw-file host,
  which resolves to the default branch without an API request. That is
  observed behaviour, not documented, so only a pass is taken from it: a file
  missing or changed there is read again at the branch the API names, and that
  read is the one reported.
- `check_links.py` asks the API about bare repository URLs with a token in
  `links` too, and counts refusals (401, 403, 429) for GitHub and for other
  hosts apart. When more than a fifth of either group — of at least twenty
  URLs — refused, it exits 3 and says the sweep was rate limited or blocked
  rather than passing for a quiet week; dead links still exit 1. `metadata`
  keeps stamping through both, fails only if the sweep never reported, and
  keeps every row's verdict as a run artifact.
- `status.md` and `llms.txt` now give how many rows share the newest
  successful check date. The date alone read as if everything had been checked
  then, while seventy rows carried an older date or none.

## Kept current

Every figure this repository publishes changes for one of four reasons, and each
reason has its own mechanism. The rule underneath all of them: **a number may
appear only where something re-derives it.** Anything typed by hand froze at the
first build — the status page, the licence warning, the link-preview text, the
social card and the README screenshots all said 148 entries long after the
catalogue passed 800, and no build ever went red.

| What changes | When | Kept current by |
| --- | --- | --- |
| Counts and tables about the catalogue | Whenever a row is added or edited | Generated from `catalog.json` — the READMEs by `build_readme.py`, the figures by `build_assets.py`, and every number inside the hand-written docs and `llms.txt` by `build_docs.py`. The site's link-preview tags are written into the Pages artifact at deploy by `assemble_site.py --deploy` and never committed. All numbers share one definition in `scripts/_stats.py`. `lint` regenerates all of them on every run (next row), and `lint_docs.py` rejects a catalogue count typed anywhere else. |
| Generated files after a merge | Whenever a pull request lands | A pull request need only change the sources. `lint` runs `regenerate.py` on every event, then `check_generated.py` decides: on a pull request each generated file must be untouched since the merge base or byte-identical to the regenerated output, with every verdict in the run's summary; on `main`, drift is handed to the `regenerate` job, which rebuilds from the tip, runs `lint`'s checks again and commits `chore: regenerate from catalog.json` as `github-actions[bot]` — rebasing if `main` moved, leaving a `regenerate/<sha>` branch if that no longer applies, never force-pushing. A dispatched or manual `lint` run is strict: any drift fails. |
| Images that show data | Same | Rendered from the data on every Pages deploy by `render_images.py` and never committed: the site's `og:image`, and the README and compatibility screenshots. The deploy refuses to publish a page that did not finish loading its data. |
| The GitHub social preview | Never | It can only be uploaded by hand, so it is the durable card: its one figure is a floor ("800+") that growth can only make an understatement, never wrong. `description` reports whether one is uploaded. |
| The repository description | When the count crosses a hundred, or the wording changes | Only an admin can edit it, so it states the count floored to the hundred: `_stats.pitch_public()`, the same sentence as the site's `description` and `og:description`. The `description` workflow compares the whole sentence on every push to `main`; on drift it warns and keeps one open issue, labelled `description`, holding the exact `gh repo edit` command, instead of failing a build nobody but an admin can fix. `lint` prints the would-be sentence on every run, pull requests included. Every other surface — the READMEs, `status.md`, `llms.txt`, the figures — carries the exact count. |
| Labels for patterns, kinds and flags | When the taxonomy changes | One copy each, in `patterns.json` and `taxonomy.json`, read by the README generators and by the site at runtime. `lint` checks both against the schema; `lint_docs` checks `docs/patterns.md` has a section for each pattern. |
| Model strings and limits | When the vendor or a gateway ships | One source, `compat.json`. `lint_docs` checks every copy — in docs, examples, and the generated README and figures — against it. `claims` re-reads each platform's documentation weekly and opens an issue if a recorded string disappears. |
| Link status, stars, licences, archive status | Continuously, upstream | `metadata` weekly: stamps every link that answers, re-reads the GitHub API, rebuilds everything generated, commits it, runs `lint`'s checks on that commit (`check.py --ci --quick`: all but the preview images, which `pages` renders), pushes to `main`, and redeploys the site. It opens an issue only for a change that is more than a star count, and falls back to a branch if `main` moved underneath it. `links` weekly is the separate alarm for a dead link, which only a person may retire, and for a sweep so refused by GitHub or by other hosts that it checked little. Both jobs, and `claims`, write their counts and the GitHub budget they spent to the run's summary. The site shows the date of the sweep its figure comes from, and the status page how many rows share it. |
| Whether cited text is still present | Continuously, upstream | `claims` is scheduled weekly to fetch each `evidence` file and report missing strings or files. Counts show citations recorded, not CI passes, and the job does not update the human `read_on` date. |
| What the catalogue is missing | Continuously, upstream | `discover` weekly: harvests every sibling directory, reads the code of the most-cited uncatalogued repositories, searches for sibling directories not yet harvested, and files one issue. It never adds a row. |
| The MCP package on PyPI | When `pyproject.toml`'s version changes | A release is a tag a maintainer pushes, so PyPI can lag `main`. `check_release.py` compares the two on every push to `main`, in `lint`'s `release` job: a version not yet on PyPI is a warning carrying the tag command; a version older than PyPI's newest, or `pyproject.toml` and `.claude-plugin/plugin.json` disagreeing, fails. The file comparison also runs on every pull request, as a unit test. After an upload, `publish` installs the release back from PyPI. |
| Dated history | Never | This page's log sections are append-only and exempt from the number rules: what the first build found is true forever. |

- `lint` runs on every pull request, every push to `main`, and by hand; after
  a push to `main` it also commits the regenerated files and asks PyPI whether
  the MCP package's version is released. Its checks, and their order, are
  `scripts/check.py`'s list; `python3 scripts/check.py` runs them locally.
- `description` runs on every push to `main`, and by hand.
- `pages` rebuilds the site and its images whenever the data, the site or the
  rendering scripts change.
- `publish` builds and smoke-tests the MCP package on a pull request that
  changes the package (`src/`, `pyproject.toml` or the workflow itself), and
  uploads it only from a release tag, then installs that release back from
  PyPI. Since 2026-09-27 a pull request that changes only data no longer runs
  it: the wheel copies the data in verbatim, and `lint` already validates it.

Since 2026-09-27, the repository description and the site's meta description
state the catalogue size floored to the hundred rather than exactly, and the
description's drift opens an issue instead of failing `lint`. The exact count
made `main` red after every merged row, in the one check CI could never repair
— editing the description needs admin rights — until someone ran
`gh repo edit` by hand; a wording change alone did the same. A floor, like the
social preview's, stays true as the catalogue grows and goes stale once per
hundred rows. Until then the two surfaces show a smaller number than the
READMEs; that difference is deliberate, and the READMEs are the exact figure.

Since 2026-09-27, the site's link-preview tags (`description`, `og:*`,
`twitter:card`) are written into `site/index.html` only in the Pages artifact,
by `assemble_site.py --deploy`, from the same stats as the rest of the page.
Git keeps a placeholder between the `meta` markers. The tags quote the
catalogue size, so while `build_docs.py` kept them in git every pull request
that added a row also had to change the site's HTML. `check_site_data.py` holds
both ends: a committed file carrying anything but the placeholder fails `lint`,
and a deploy without current tags fails `pages` before anything is published.

Since 2026-09-27, `lint` checks on every push to `main` that the MCP
package's version is on PyPI (`check_release.py`). The package README, the
agent skill and `llms.txt` told everyone outside Claude Code to
`pip install awesome-jev-mcp`, and PyPI had never heard of it: `publish`
uploads only from a release tag, no tag had been pushed, and no check looked
at PyPI, so the documented route failed at its first step while every build
stayed green. A version not yet on PyPI is reported, not failed, because it is
the normal state between merging a version bump and pushing its tag, and only
a maintainer can push the tag; a version older than PyPI's newest fails,
because an uploaded version can never be uploaded again. An unreachable PyPI
is `skipped`. The same three documents now also give
`pip install git+https://github.com/kydlikebtc/awesome-jev`, which builds the
same package from the repository.

Since 2026-09-27, a pull request no longer has to carry generated files, and
`lint` no longer fails a pull request because one is stale. Every pull request
that added a row used to change twenty-odd generated files, so any two open at
once conflicted, and each had to be brought up to date by hand before it could
merge. Now `lint` regenerates everything itself and judges each generated file
by event. On a pull request, a file the pull request did not touch may be
stale, since the bot rebuilds it after the merge; a file it did touch must be
exactly what the generators write, because anything else is a hand edit the bot
would silently overwrite. On `main`, the `regenerate` job commits the rebuilt
files, so `main` is behind its own sources for the minute between a merge and
that commit, and a dispatched `lint` run on `main` remains strict. This relaxes
the rule this section used to state as "`lint` fails on any drift": drift is
now repaired by a commit rather than refused at review. `.gitattributes` marks
the wholly generated files (both READMEs, `docs/by-pattern/`, `docs/assets/`)
`linguist-generated`, so GitHub collapses them in a pull request's diff; files
that are hand-written around generated blocks are not marked, because their
prose still needs reading.
