## What this changes

<!-- One or two lines. -->

## If you edited catalog.json

- [ ] `sort_catalog.py`, `lint.py`, `build_readme.py`, `build_assets.py`, `build_docs.py` and `lint_docs.py` run, and everything they rewrote is committed — both READMEs, and every page under `docs/by-pattern/`, including any it created or deleted
- [ ] I opened every link I added and wrote the summaries from what was there
- [ ] `question_types` reflects the actual call site, not the README
- [ ] `stars` / `repo_license` came from the GitHub API, not a badge
- [ ] Caveats are flagged, and any flag needing an explanation has a `notes` line
- [ ] `summary_zh` is hand-written, or `zh_machine: true` is set
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
