## What this changes

<!-- One or two lines. A candidate from the `discovery` issue? Name the owner/name you claimed there. -->

## If you edited catalog.json

<!-- Once CI has run, the lint run's summary holds a review card for each row you added or changed: fix what it marks ✗. It matches text; a maintainer still reads the call site. -->

- [ ] `python3 scripts/check.py --fix` passes: it sorts `catalog.json`, then runs every check CI runs
- [ ] Generated files (READMEs, `docs/by-pattern/`, `docs/assets/`, generated numbers in docs) are either left out — a bot regenerates them on `main` after the merge — or exactly what `python3 scripts/check.py --fix` wrote, never edited by hand
- [ ] I opened every link I added and wrote the summaries from what was there
- [ ] `question_types` reflects the actual call site, not the README, and I left `primitives_seen` to the weekly run (a script's text signal, never a substitute for reading the call)
- [ ] A row with code cites the file I read in `evidence`, or says in `evidence_none` why it cannot (lint requires one when the repository is on GitHub)
- [ ] `patterns_reviewed` is set only on rows whose `patterns` I read against `docs/patterns.md`, to the day I read them
- [ ] `evidence.kind` says what the cited file shows when it is not a call site: `wire-shape` for an `alternative` (lint requires it), `example-only` for an example
- [ ] `stars` / `repo_license` came from the GitHub API, not a badge
- [ ] Caveats are flagged, and any flag needing an explanation has a `notes` line
- [ ] `summary_zh` is hand-written, or `zh_machine: true` is set
- [ ] `summary_source` is `curated` if I wrote or rewrote the summary, and left out if I pasted the repository's own GitHub description (the weekly refresh labels that)
- [ ] A row started from a discovery draft (`--drafts`): I read its call site myself, checked the `kind`, `patterns` and `languages` the script guessed, and deleted `_draft`. Leave unticked otherwise.
- [ ] This is my own project (I wrote or maintain it): its row has a source `{"catalog": "author submission", "url": <this pull request>}` and `self-submitted` in `flags`. Leave unticked otherwise.

## If you added a pattern

- [ ] Schema enum, `patterns.json` (both languages, long and short blurb) and a `## key` section in `docs/patterns.md` all updated
- [ ] There are at least two independent real examples of it

## If you touched any doc

- [ ] No catalogue count typed by hand — reworded, or filled by `build_docs.py` (see CONTRIBUTING, *Numbers in prose*)

## If you added a runnable example

- [ ] The file states plainly whether it was run against the live API
- [ ] `examples/README.md` updated

## Anything you are unsure about

<!-- Say so here. An honest question costs nothing; a wrong row costs a reader's trust. -->
