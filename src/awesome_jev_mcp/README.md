# awesome-jev-mcp

Query the [awesome-jev](https://github.com/kydlikebtc/awesome-jev) catalogue
from an agent instead of reading it.

A catalogue about how agents make decisions that only humans can read is a
strange artefact. This exposes it: an assistant about to wire Jev into
something can ask for examples of the exact decision it is making, on the
platform it is using, in the language it is writing.

## Install

**In Claude Code**, install the plugin. It brings this server and the
[agent skill](https://github.com/kydlikebtc/awesome-jev/blob/main/skills/awesome-jev/SKILL.md) together, and starts the server
for you:

```
/plugin marketplace add kydlikebtc/awesome-jev
/plugin install awesome-jev@awesome-jev
```

The plugin launches the server with `uvx`, so it needs
[uv](https://docs.astral.sh/uv/) on your PATH. It rebuilds the package from the
plugin's own copy every time it starts, which costs about two seconds in the
background. Without that, uvx keeps the first environment it built for a local
directory and ignores later changes to it — so a plugin whose code or bundled
snapshot had been updated would go on running the old one, with nothing to say
so. The dependencies stay cached; only this package is rebuilt.

**Anywhere else**, install the package and register the command with your
client:

```bash
pip install awesome-jev-mcp
awesome-jev-mcp
```

It speaks stdio, so any MCP client works. The catalogue it serves is fetched
from the repository's `main`, not frozen into the release, so a release only
needs upgrading for changes to the server itself. If pip finds no
`awesome-jev-mcp` to install, or to run the server as it is on `main` rather
than as released, install it from the repository:

```bash
pip install git+https://github.com/kydlikebtc/awesome-jev
```

Needs the 2.x MCP SDK, which the package declares. `MCPServer` is the name 2.x
gave what 1.x called `FastMCP`, so an environment already pinned to `mcp<2`
resolves to something that dies at import — check that first if the server
never starts.

## Tools

| Tool                 | What it answers                                                    |
| -------------------- | ------------------------------------------------------------------ |
| `search_examples`    | "Show me safety-gating examples in TypeScript that call `noul`."   |
| `get_example`        | One row in full, including its sources and its `evidence`.         |
| `list_patterns`      | The decision taxonomy, with how many examples exist for each.      |
| `compatibility`      | Model string, field names, request shape and env var per platform. |
| `check_model_string` | "Is `typesafe/jev-1` real?" — it is not, and that matters.         |

## Three things it does on purpose

**Caveats are never optional.** Every result carries its flags. An agent that
got a recommendation without `not-jev` or `vendor-reported` attached would be
worse informed than one that read the README.

**Reimplementations are excluded by default.** Rows flagged `not-jev` do not
call the API and `shadow-mode-only` rows are deliberately inert; neither
answers "how do I do this". Pass `include_non_jev=True` when you want them.

**Every result says how current it is.** The catalogue changes; this package
does not change with it. So each result carries a `data` line naming which
source answered, and anything stale says so in capitals:

```
"data": "revalidated against GitHub · <rows> rows · catalogue checked <date>"
"data": "STALE — network unreachable, serving the last copy fetched to this machine · …"
```

## Where the catalogue comes from

Installed as a package there is no repository around this code, so the three JSON
files have to be fetched. They are, in this order, and the first complete answer
wins:

|     | Source                                                          | Reported as           |
| --- | --------------------------------------------------------------- | --------------------- |
| 1   | `AWESOME_JEV_CATALOG`, a directory holding the three files      | `override`            |
| 2   | A repository checkout above this file, when running from source | `checkout`            |
| 3   | GitHub, conditional on the cached ETag                          | `network`             |
| 4   | The cache, when the network fails                               | `cache` — **stale**   |
| 5   | The snapshot inside the wheel, when there is no cache either    | `bundled` — **stale** |

Layer 3 is the normal case and costs almost nothing after the first run: GitHub
answers a revalidated request with `304` and no body, so the steady state is
three small round trips rather than a megabyte.

Layer 5 is the offline first run. It works, and it is the one source that can be
arbitrarily old, so it is the loudest.

Three properties worth stating plainly, because two of them are trade-offs:

- **The three files always move together.** A source supplies all of them or it
  is skipped. A fresh `catalog.json` beside a cached `patterns.json` could use a
  pattern key the taxonomy does not have yet, and that is a correctness bug
  rather than untidiness.
- **A stale answer is never presented as fresh.** That is the whole reason the
  `data` line exists on every result instead of only on degraded ones: a warning
  that appears only when something is wrong teaches readers to skim past it.
- **This version reaches the network, and earlier ones did not.** Before it was
  packaged, the server read the repository it sat inside, which made it offline
  by construction. Fetching is what buys a catalogue that stays current after
  you install it once; the cost is a dependency on GitHub being reachable, paid
  down by the cache and the bundled snapshot. `AWESOME_JEV_CATALOG` opts out
  entirely.

## Why this has a dependency when the rest of the repository does not

The catalogue's own pipeline — lint, build, verify, refresh — is stdlib-only, so
CI stays `setup-python` with no install step, and nothing under `scripts/`
imports anything declared in `pyproject.toml`. Hand-rolling stdio JSON-RPC would
extend that streak to here too, but a subtly broken MCP server is worse than a
dependency.
