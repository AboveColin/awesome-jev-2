# Runnable examples

Four small programs, each isolating one idea. They are written against the
official Python SDK and the request shapes in the official API reference.

**Honest status:** these were written from the published API reference, and the
shapes were checked field by field against it — but they have **not been
executed against the live API**, because early access is gated. Treat them as
carefully-read reference code, not as verified-working code. If you run one and
something is wrong, that is a bug worth [opening an issue](https://github.com/kydlikebtc/awesome-jev/issues) over.

## Setup

```bash
pip install typesafe-sdk
export TYPESAFE_API_KEY=...
```

No key yet? Two options, both with the same caveat:

- The official [`system-one-adapter`](https://github.com/typesafe-ai/system-one-adapter-python)
  is a drop-in client backed by ordinary LLM APIs.
- Several self-hostable projects in the catalog serve the same wire format.

Either lets you run the shapes. **Neither reproduces the calibration**, so do not
tune a threshold against a substitute and then ship it against the real model.

## The examples

|                                                      | What it isolates                            | Why it is here                                                                                        |
| ---------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [`01-three-primitives`](01-three-primitives/main.py) | `choice`, `score` and `noul` in one request | The asymmetry that catches everyone: `noul` returns no confidence, and a `score` lands between levels |
| [`02-confidence-gate`](02-confidence-gate/main.py)   | Act above a threshold, escalate below       | The policy function is left unimplemented on purpose — see below                                      |
| [`03-fan-out`](03-fan-out/main.py)                   | Many questions, including speculative ones  | Why asking more can be cheaper than asking twice                                                      |
| [`04-tool-selection`](04-tool-selection/main.py)     | Choosing a tool, including choosing none    | A closed set with no escape hatch cannot decline                                                      |

Run any of them with `python main.py` from its directory.

[`index.json`](index.json) beside them is generated, never edited: each
example's code with the catalogue row that describes it (patterns, languages,
flags), written by `scripts/build_examples_index.py` for the MCP server's
`wire_pattern` prompt, which inlines the one that fits the pattern and language
it is asked about.

## About `02-confidence-gate`

That example stops short of a decision on purpose. The model call, the dataclass
and the printing are done; `decide_action` is left for you.

This is not busywork. Where the thresholds sit, whether there is one cutoff or
two, and whether the cutoff varies by queue are **policy questions, not modelling
questions** — they depend on what being wrong costs in your system. The docstring
lays out the trade-offs worth weighing. The Inbox Zero entry in the catalog is
worth a look first: it uses seven different thresholds for seven decisions,
ranging roughly from 0.3 to 0.9, which is the honest answer to "what threshold
should I use".

## Not covered here

Two catalog patterns have no in-repo example yet, because no good public one
exists to base it on either — see the gaps reported by `scripts/counts.py`:

- `retry-control` — deciding whether a failed step is worth retrying
- `recommendation` — real-time next-best-thing selection

A well-made example of either would be a genuinely useful contribution. See
[`../CONTRIBUTING.md`](../CONTRIBUTING.md).
