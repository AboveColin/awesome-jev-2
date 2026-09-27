# Contributing

This catalog is built around traceable sources and explicit limits. A submission
should say what you inspected and what remains unknown. A link, a code reading,
a text-matching check and a successful API run are different kinds of evidence;
do not present one as another.

So the bar is: **could a reader act on this row without opening the link?**

## Adding an entry

1. Add an object to `catalog.json`. Required fields: `slug`, `title`,
   `summary`, `summary_zh`, `url`, `kind`, `patterns`, `sources`, `license`.
   The file is kept in `slug` order, so add the row anywhere and let the
   next step move it into place (`sort_catalog.py`, which changes nothing
   else). A sorted file is what lets two pull requests adding different rows
   merge without conflicting.
2. Run the checks:

```bash
python3 scripts/check.py --fix
```

   That one command sorts `catalog.json`, then runs every check CI runs, in
   CI's order, and ends with one line per check. A check that needs Node.js or
   Chrome is reported as skipped where that is not installed; CI runs it.
3. Open a pull request. `catalog.json` alone is enough.

### Generated files are optional

The READMEs, the pages under `docs/by-pattern/`, the figures in `docs/assets/`,
[`docs/review-queue.md`](docs/review-queue.md) and the generated numbers in
`docs/status.md`, `docs/sources.md`, `docs/patterns.md`,
`docs/compatibility.md` and `llms.txt` are all derived from the JSON files at
the root. You do not need to regenerate them. CI regenerates everything on
every run, and after your pull request is merged, `github-actions[bot]`
commits the regenerated files to `main` as `chore: regenerate from
catalog.json`. Leaving them out also keeps two pull requests that add
different rows from conflicting over the generated files.

If you do include a generated file, it must be exactly what the generators
write. CI checks each generated file your pull request changes, and lists the
verdict for every one in the run's summary. A hand edit fails, because the bot
would silently overwrite it on `main`. To change what a generated file says,
change `catalog.json` or the generator in `scripts/`.

`check.py --fix` regenerates them in your working tree, as CI does, and then
judges them as CI judges a pull request against `origin/main`: a generated
file your branch changed must be exactly what the generators write, and one it
left alone may be stale. Commit what it rewrote, or leave it out. If your
remote for this repository has another name, say so with
`--base upstream/main`.

The same list of checks, run other ways:

```bash
python3 scripts/check.py --list    # every check in order, and what each needs
python3 scripts/check.py --quick   # without the preview images (Chrome), the PyPI check and the review card
python3 scripts/check.py --only lint,lint-docs   # just these checks
python3 scripts/check.py           # strict: every generated file committed and current
```

No Python dependencies are needed, only Python 3.11 or newer (CI uses 3.12).
The schema validator in `scripts/lint.py` is self-contained: it implements the
part of JSON Schema that `schema/entry.schema.json` uses, and a unit test fails
if the schema starts using a keyword it does not enforce, so implement that in
`validate()` first.

To preview the site locally:

```bash
python3 scripts/assemble_site.py && python3 -m http.server --directory site
```

A local preview has no link-preview tags: `site/index.html` keeps a
placeholder in git, and only the Pages deploy (`assemble_site.py --deploy`)
writes them.

### The review card

When CI runs on your pull request, `lint`'s `review` job writes a review card
to the run's summary (open the `lint` run from the pull request's checks, then
**Summary**) and marks each finding on its row's line in `catalog.json` under
**Files changed**. For each row you added, and for each changed field one of
its checks reads, it:

- reads the cited file and checks every `evidence.matched` string is in it, as
  the weekly `claims` job will, and that a row with `question_types`, or with
  code in a GitHub repository, cites a file or says in `evidence_none` why it
  cannot;
- asks GitHub about the repository: `repo_license` and the `archived` flag must
  match exactly, `stars` only has to be close (within 5, or a tenth of GitHub's
  count) because it moves every day, and a repository with one commit should
  carry `single-commit`;
- requests the link and expects a 2xx answer;
- compares your GitHub login with the repository's owner and the row's
  `author.handle` and `author.url`: a match without `self-submitted` is marked.
  An organisation's repository escapes this comparison, so the template's
  checkbox still counts;
- checks that `ai-generated`, `unverified-claims` and `code-untested` come with
  a `notes` line;
- and, as a hint only, says which kind and patterns the keyword rules that
  `discover` uses (`scripts/classify.py`) would have guessed from your summary.

✗ is for you to fix before merging, ⚠ for a person to look at, ℹ is a hint,
and *not checked* is not a pass. The card is advisory while it is new: it never
fails the check. It is a second gate that matches text and compares facts with
GitHub; it is not a review, and it does not replace a maintainer, who still
reads the call site: strings present in a file do not show that the code calls
Jev the way the row says, and a clean card is not an approval.

The card runs the base branch's copy of `scripts/`, not your pull request's,
so a pull request that edits the checks is still judged by the ones on `main`.
On a first pull request it runs only after a maintainer clicks **Approve and
run** (see *How changes reach `main`*). To see the same card before you push:

```bash
GITHUB_TOKEN=$(gh auth token) python3 scripts/review_pr.py --author <your GitHub login>
```

It compares your branch with `origin/main` (`--base upstream/main` if your
remote has another name), and `--offline` leaves out everything that reads the
network. `python3 scripts/check.py` runs it too, without an author.

## How changes reach `main`

Every change lands through a pull request, the maintainer's own included.
Maintainers and agent sessions (Claude, Codex and the like) push a `claude/*`
or `codex/*` branch and open a pull request from it, and do not push to `main`
directly. The only commits made straight to `main` are the two bots':
`github-actions[bot]`'s weekly `metadata` refresh and `lint`'s `regenerate`
job. Neither ever force-pushes `main`; when it moves underneath one of them,
the bot rebases or leaves its commit on a branch.

GitHub may hold the checks on your first pull request here until a maintainer
clicks **Approve and run**. That is GitHub's safeguard for first-time
contributors to a repository, not a verdict on your change, and it stops once
you have had a pull request merged.

## Numbers in prose

Never type a catalogue count into a doc. Every one that was typed by hand froze
at the first build and quietly became wrong. Either reword the sentence without
the number, or let `build_docs.py` fill it:

```markdown
In all, <!--n:no_licence-->141<!--/n--> linked projects declare no licence.
```

The keys are in `inline_values()` in `scripts/build_docs.py`. Put a word before
the marker — a line that *starts* with `<!--` is a raw HTML block in Markdown
and splits the sentence in two. `lint_docs.py` rejects bare counts, hand-written
count tables and line-leading markers. Dated history in `docs/method.md` is
exempt: a log entry about the first build is true forever.

Model strings and limits are held to `compat.json` the same way: write
`jev-latest` or `max 255` anywhere and `lint_docs.py` checks it against that
file. If the vendor changes one, change `compat.json` and every stale copy
turns red.

## Field rules

- **`title`** — as published at the source. If the page's `<title>` and its
  on-page heading disagree, use the heading a reader sees, and say so in `notes`.
- **`summary`** — what the example _actually demonstrates_, not what its README
  claims. "Routes support tickets with a choice and a score" beats "revolutionary
  AI-powered triage".
- **`summary_source`** — whose words `summary` is. Wrote it yourself? Set
  `curated`; lint then warns about marketing words and emoji in it. Pasted the
  repository's own GitHub description? Leave the field out: the weekly refresh
  compares the two and sets `upstream-description` when they are identical, and
  `upstream-description-stale` once a labelled one stops matching. Never write
  `upstream-description` for a text that differs. Rewriting a summary labelled
  with either upstream value? Set `curated`, or the refresh will call your
  words the project's old ones. The READMEs, pattern pages and site mark the
  project's own words, and [`docs/sources.md`](docs/sources.md#licences) says
  why: the copyright in them is the project author's, not this catalogue's.
- **`summary_zh`** — write it yourself if you can. If you machine-translated it,
  set `zh_machine: true`. The READMEs report the split. This field describes
  translation provenance, not code quality or runtime testing.
- **`kind`** — the form of the thing. Use `alternative` for anything that does
  not call Jev, however Jev-shaped it is.
- **`patterns`** — which decisions it demonstrates. Read
  [`docs/patterns.md`](docs/patterns.md) first. `overview` cannot be combined
  with a specific pattern; the linter enforces that. `overview` is for a row
  that surveys the model or the space, not for a project nobody has placed: a
  project or plugin with code filed only under `overview` is listed as *not
  yet indexed by pattern* until someone reads it.
- **`patterns_reviewed`** — the date you read the row against
  [`docs/patterns.md`](docs/patterns.md) and set or confirmed its `patterns`.
  Only a person writes it: never because the keyword rules agree, and never
  for a row you did not read. It takes the row off the *not yet indexed by
  pattern* list and off the pattern sections of
  [`docs/review-queue.md`](docs/review-queue.md).
- **`question_types`** — only the primitives the code _actually_ calls. Read the
  call site; do not infer from the README. Several projects describe "scoring"
  while using only `noul`. The primitive is `noul`, never `binary`.
- **`primitives_seen`** — leave it out; the weekly `metadata` run writes it
  (`python3 scripts/verify_claims.py --write-signals`). It lists the primitives
  whose request or answer shape — `"type": "choice"`, `Noul(`, `.noul` and the
  like — appears in the one file `evidence` cites: a text signal about that
  file, not a reading of the call. It never stands in for `question_types`: no
  filter, count or lint rule reads it as a primitive claim, and a shape in a
  file (a type definition, a test double) is not a call. Lint allows it only on
  a row with `evidence`.
- **`evidence`** — the file you read the row's code in (for a row with
  `question_types`, the file you read that claim in), and strings from it that
  substantiate it. This is what makes the claim re-checkable rather than
  asserted, so a weekly job can notice when it stops being true. Let the
  discoverer propose one and then check it yourself:

  ```bash
  python3 scripts/verify_claims.py --discover --only <slug>
  python3 scripts/verify_claims.py --only <slug>
  ```

  Prefer the implementation over a test file: tests get deleted while features
  stay, and a mocked string is weaker proof than a real call site. When the
  source is a docs page, a video or a paywalled post, set `evidence_none`
  instead and say which; when the repository's code neither calls Jev nor
  speaks its request shape (a reimplementation with its own interface, tooling
  about Jev), `no-jev-call-site`. A link holding no code at all, such as a list
  of links or a community site, gets `has_code: false` rather than either. Set
  `read_on` to the date you actually read that file; do not advance it after an
  automated text check. An `evidence` record is a
  citation, not a stored CI pass or proof that the integration executes.
  `evidence.kind` says what the file shows: leave it out (or write
  `call-site`) when the project calls Jev there; write `wire-shape` when it only
  speaks Jev's request shape — lint requires this on every `alternative` — and
  `example-only` when the call is in an example the project ships rather than in
  its own code. Rows a script marks for a person to re-read (a file under
  `examples/`, a citation resting on one model name, a `tool-selection` that
  only words the keyword rules no longer count suggested) are listed in
  [`docs/review-queue.md`](docs/review-queue.md); each section there says what
  to record to take a row off.
  `lint.py` fails a row with `question_types`, and a row with `has_code: true`
  whose `url` or `repo` is a GitHub repository, when it has neither `evidence`
  nor `evidence_none`; `not-yet-backfilled` is an honest value while you look.
- **`official`** — true only for `typesafe.ai` hosts and the `typesafe-ai`
  GitHub org. A first-party integration published by another vendor is not
  official. The linter checks this.
- **`stars`**, **`repo_license`** — from the GitHub API on the date you add the
  row, not from a README badge. Several repos have a licence badge and no
  `LICENSE` file; that gets the `no-license` flag. The READMEs and pattern
  pages print only the band a count falls in (★10+, ★100+, …, nothing under
  10) and sort by it; the exact number stays in the row, and the weekly
  refresh keeps it current.
- **`sources`** — at least one, so the row is attributable. Name where you found
  it, not where it lives. Two fixed strings name submissions made directly to
  this repository, and they mean different things:
  - `author submission` — the project's own author or maintainer proposed the
    row. Use it for your own project, with the pull request or issue as `url`.
    The row must then also carry the `self-submitted` flag; `lint.py` fails if
    either appears without the other.
  - `maintainer submission` — this list's maintainer added the row on their own
    initiative. It says nothing about who wrote the project and is not a
    self-submission, unless the maintainer is also that project's author, in
    which case it is an `author submission` like any other.

## Flags are the point

Use them generously. A flagged row is more useful than an unflagged one.

| Flag                                     | Use when                                        |
| ---------------------------------------- | ----------------------------------------------- |
| `vendor-reported`                        | it repeats the vendor's own performance numbers |
| `unverified-claims`                      | it makes measurement claims you could not check |
| `not-jev`                                | it does not call Jev at all                     |
| `shadow-mode-only`                       | Jev is wired in but changes no behaviour        |
| `code-untested`                          | you read the code but did not run it            |
| `single-commit`                          | one commit, so maintenance is unlikely          |
| `no-license`                             | no `LICENSE` file, whatever the README says     |
| `archived`                               | development visibly stopped                     |
| `paywalled`, `marketing`, `ai-generated` | as they say                                     |
| `early-access-required`                  | needs waitlist access to use                    |
| `third-party-api-key`                    | needs a key for a service other than TypeSafe   |
| `self-submitted`                         | its own author or maintainer proposed the row   |

`ai-generated`, `unverified-claims` and `code-untested` require a `notes` line
saying why — a flag a reader cannot interpret is worse than no flag.

`self-submitted` is a disclosure, not a defect: every surface shows it so a
reader knows the description came from the project's side. It is declared,
never guessed — it goes with an `author submission` source and nothing else.
Older rows recorded as `maintainer submission` or `community submission` have
not been classified, so a row without the flag is not a statement that nobody
self-submitted it.

All catalogue code is **untested by this repository by default**, including rows
without `code-untested`. That flag adds a caveat; its absence must never be used
as a passed-test signal. Upstream benchmark results belong to their authors and
have not been independently reproduced here. A future runtime-verification claim
needs a dated report with the source revision, environment, model version and
result; neither `checked` nor `evidence.read_on` is a substitute.

## What does not belong here

- **Anything you have not opened.** Including anything an AI tool suggested and
  you did not check. Fabricated entries are the failure mode this catalog is
  built to avoid.
- **A model string, package name or endpoint you have not seen in a primary
  source.** `typesafe/jev-1` is the canonical example: it appears in no
  documentation and keeps getting repeated.
- **Content-farm rewrites of the launch announcement.** There are hundreds. If it
  adds no observation of its own, it adds nothing here.
- **"Run Jev locally" content filed as a Jev tutorial.** There are no published
  weights. File it as `alternative` with `not-jev`.
- **Your own project, described the way you would describe it to an investor.**
  Self-submissions are welcome; marketing copy is not. Say what decision it makes
  and which primitive it uses, record the source as `author submission`, add the
  `self-submitted` flag, and tick the box in the pull request template.

## Finding things to add

The weekly `discover` workflow does this for you and keeps an open issue
labelled `discovery`. Its description is the queue: every repository the run
has found calling Jev, ticked once `catalog.json` has its row, struck through
once `docs/declined.txt` declines it, and otherwise waiting to be read.
`scripts/queue_sync.py` derives those states from `catalog.json`,
`retired.json`, `docs/declined.txt` and `.discover/seen.json`, and the weekly
run rewrites the description with them, so nobody ticks a box by hand: merging
the pull request that adds the row or the decline is what ticks it. Each
week's new candidates arrive as a comment, a task list with one box per
repository, its call site, and under it the command that reads that one
repository again:

```bash
python3 scripts/discover_candidates.py --only owner/name
```

To take one, comment `claim owner/name` on the issue, so two people do not
read the same code; the first comment wins, and nothing arbitrates beyond
that. Then read the call site and add the row as described above. Candidates
from earlier weeks that are still neither catalogued nor declined are listed by
name under the new ones.

To start the row from what the script already knows, add `--drafts drafts`:

```bash
python3 scripts/discover_candidates.py --only owner/name --drafts drafts
```

That also writes `drafts/<slug>.json`, a draft row: the URL, GitHub's stars
and licence, the call site's path and the strings matched there, and the
keyword rules' guess at `kind` and `patterns` are filled in; `summary`,
`summary_zh` and `evidence.read_on` are left for you, and so is `sources`,
since a single read cannot know where you found the repository. Its first
field, `_draft`, lists what is left to do. Read the call site, complete the
row, delete `_draft`, and move the row into `catalog.json`. `drafts/` is
ignored by git, and the command never writes over a draft that is already
there.

`lint.py` refuses any row that still has a `_draft` field, and that is the
only thing that keeps a draft out as it is. Do not count on anything else to
catch an unfinished one: an empty `summary` fails, but a one-word summary
passes, and `read_on` is optional. The review card on your pull request is a
second gate that compares facts and matches text; neither it nor lint reads
the code for you.

To run the whole harvest by hand:

```bash
python3 scripts/discover_candidates.py --top 40
```

This harvests every list in `docs/sibling-lists.txt`, ranks repositories by how
many cite each, and reads the candidate's code before reporting. A `calls-jev`
verdict means a call site was found — it is a shortlist, not a row. Read it,
write the summary yourself, and keep the evidence path the scan produced.
`verify_claims.py --discover` is for rows already in `catalog.json`; for a
candidate it finds nothing to read.

Read one and decided it does not belong? Add it to `docs/declined.txt` with a
reason, and the weekly run stops proposing it.

The script's own verdicts (which repositories it read, on what date, and what
it found in the files it read) are kept in `.discover/seen.json`, so the weekly
run does not read the same code again until a verdict is old (`RECHECK_DAYS` in
`scripts/discover_seen.py`) and does not propose a candidate twice. The weekly
`metadata` run commits that file; do not edit it by hand. It records a script's
verdicts, not anyone's decision: yours goes in `catalog.json` or
`docs/declined.txt`.

Know a directory we are not harvesting? Add it to `docs/sibling-lists.txt`.
That is a useful contribution on its own.

## Reporting a dead link

Open an issue with the slug. Do not delete the row — retiring an entry means
moving it to `retired.json` with a `notes` line explaining why, so the dead
reference stays searchable. `retired.json` is kept in slug order too, so run
`python3 scripts/check.py --fix` after moving it; it sorts both files.
`scripts/check_links.py` finds them but deliberately never moves them; that
judgement is a person's.

## Adding a pattern

A pattern earns a heading once **two independent real examples** exist. Adding
one means editing three places:

1. the enum in `schema/entry.schema.json`
2. `patterns.json` — the English and Chinese label, the long blurb the README
   uses and the short one the site uses. The README, the figures, the site and
   the MCP server all read this one file.
3. `docs/patterns.md`, a `## key` section with an explicit *when NOT to use this*

`lint.py` fails if the schema and `patterns.json` disagree or a field is
missing, and `lint_docs.py` fails if `docs/patterns.md` has no section for it —
a silent fallback to a raw slug is how a bilingual list starts rotting.

A new `kind` or flag is the same, minus the doc section: the schema enum, then
`taxonomy.json`, which holds both languages' labels for the README and the
site.

## Adding a runnable example

See [`examples/README.md`](examples/README.md) for the runnable examples maintained
inside this repository. Their coverage is separate from the public resources in
the catalogue; use [`docs/status.md`](docs/status.md) for current catalogue gaps.
Say plainly in the file whether you ran it against the live API, and include a
reproducible test record before claiming that you did.

## Ground rules

Be accurate, be brief, and say what you do not know. If you are not sure whether
something qualifies, open an issue and ask rather than guessing — an honest
question costs nothing and a wrong row costs a reader's trust.
