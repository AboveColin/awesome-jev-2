<!-- Written by scripts/build_shape.py from catalog.json, compat.json, patterns.json and the entry schema. Edit those, not this file. -->

# The catalogue's shape

<sub>[awesome-jev](../README.md) · [中文](shape.zh-CN.md)</sub>

Counts that describe this catalogue as a dataset, regenerated from `catalog.json` whenever it changes; the newest link check behind them is dated **2026-09-24**. They describe what the catalogue holds, which is what reached it through the sibling directories, this repository's discovery and its contributors, not the ecosystem at large. A star band is a popularity signal, not a quality verdict, and nothing here was run or reproduced by this repository. `python3 scripts/counts.py` prints the same numbers as text; the headline figures are on [the status page](status.md).

## Languages

Rows recording each language (`languages`; a row may record several). 28 rows record none.

| Language | Rows |
| --- | --- |
| `python` | 456 |
| `typescript` | 401 |
| `javascript` | 152 |
| `rust` | 52 |
| `go` | 42 |
| `swift` | 16 |
| `java` | 15 |
| `ruby` | 12 |
| `shell` | 10 |
| `kotlin` | 8 |
| `csharp` | 7 |
| `elixir` | 7 |
| `php` | 7 |
| `c` | 5 |
| `cpp` | 4 |
| `haskell` | 1 |
| `lua` | 1 |

## How rows reach Jev

`platforms` records how a row reaches Jev. Discovery does not tag it: `scripts/discover_candidates.py` and the drafts it writes leave the field to the person adding a row, and `typesafe-api` is what a row records when nobody named another route. So the first group below counts that default at least as much as a finding: a row that reaches Jev through a pass-through may record `typesafe-api` alone ([compatibility](compatibility.md)). Each row counts in exactly one group.

| Group | Rows |
| --- | --- |
| `typesafe-api` and nothing else | 1090 |
| At least one value another surface in [the compatibility table](compatibility.md) stands for (a gateway, SDK or framework), and not `self-hosted` | 34 |
| Besides `typesafe-api`, only values no compatibility surface stands for (a host, tool or framework the example runs in, or a route that table does not describe), and not `self-hosted` | 28 |
| `self-hosted`, whatever else is recorded | 38 |
| No value recorded | 17 |

Every value rows record, with the compatibility surfaces that stand for it:

| Value | Compatibility surface | Rows |
| --- | --- | --- |
| `typesafe-api` | `typesafe-native` | 1116 |
| `self-hosted` | — | 38 |
| `vercel-ai-gateway` | `vercel-eval`, `vercel-compat` | 15 |
| `claude-code` | — | 8 |
| `openrouter` | `openrouter` | 5 |
| `github` | — | 4 |
| `langchain` | `langchain` | 4 |
| `jevai-org` | — | 3 |
| `mcp` | — | 3 |
| `pydantic-ai` | `pydantic-ai` | 2 |
| `vercel-ai-sdk` | `vercel-eval`, `ai-sdk-direct` | 2 |
| `aimlapi` | `aimlapi` | 1 |
| `airflow` | — | 1 |
| `autogpt` | — | 1 |
| `bifrost` | `bifrost` | 1 |
| `cloudflare-workers-ai` | `cloudflare` | 1 |
| `composio` | — | 1 |
| `discord` | — | 1 |
| `effect` | — | 1 |
| `kiln` | — | 1 |
| `lancedb` | — | 1 |
| `langfuse` | — | 1 |
| `litellm` | `litellm` | 1 |
| `netlify` | `netlify` | 1 |
| `opencode-zen` | — | 1 |
| `opik` | — | 1 |
| `postgresql` | — | 1 |
| `rig` | `rig` | 1 |
| `ruby-llm` | — | 1 |
| `spring-ai` | — | 1 |

## Licences

The licences the linked repositories declare are counted on [the sources page](sources.md#licences), beside what this repository's own licence covers.

## Stars by kind

Rows of each kind per star band, from GitHub's count at the last weekly refresh; a row without a repository has no count. The median is the band of the middle row (the lower of two). A band is a popularity signal, not a quality verdict, and says nothing about upkeep.

| Kind | Rows | With a star count | under 10 | ★10+ | ★100+ | ★1k+ | ★10k+ | ★100k+ | Median band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Official docs (`official-docs`) | 31 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | ★1k+ |
| Integration (`integration`) | 34 | 24 | 10 | 4 | 1 | 3 | 5 | 1 | ★10+ |
| Project (`project`) | 653 | 650 | 411 | 142 | 68 | 13 | 14 | 2 | under 10 |
| Plugin (`plugin`) | 238 | 238 | 150 | 62 | 22 | 3 | 1 | 0 | under 10 |
| SDK (`sdk`) | 94 | 93 | 75 | 14 | 3 | 0 | 1 | 0 | under 10 |
| Snippet (`snippet`) | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| Tutorial (`tutorial`) | 9 | 6 | 3 | 1 | 0 | 2 | 0 | 0 | under 10 |
| Article (`article`) | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| Video (`video`) | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| Benchmark (`benchmark`) | 70 | 68 | 54 | 8 | 3 | 1 | 1 | 1 | under 10 |
| Discussion (`discussion`) | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| Jev-like alternative (`alternative`) | 57 | 56 | 17 | 21 | 11 | 5 | 2 | 0 | ★10+ |

## Languages by decision pattern

Rows per pattern recording each of the 6 most recorded languages; the rest share one column. A row recording two languages counts in both, and a row filed under two patterns counts in both.

| Pattern | `python` | `typescript` | `javascript` | `rust` | `go` | `swift` | Other languages |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Tool selection](by-pattern/tool-selection.md) | 89 | 83 | 45 | 4 | 4 | 5 | 1 |
| [Intent routing](by-pattern/intent-routing.md) | 18 | 13 | 3 | 0 | 1 | 0 | 1 |
| [Context compaction](by-pattern/context-compaction.md) | 10 | 20 | 3 | 1 | 0 | 0 | 0 |
| [Safety gating](by-pattern/safety-gating.md) | 46 | 60 | 20 | 5 | 4 | 0 | 4 |
| [Output validation](by-pattern/output-validation.md) | 45 | 52 | 19 | 8 | 3 | 1 | 4 |
| [Retry control](by-pattern/retry-control.md) | 2 | 1 | 1 | 0 | 0 | 1 | 1 |
| [Human escalation](by-pattern/human-escalation.md) | 40 | 21 | 0 | 1 | 0 | 0 | 2 |
| [Model routing](by-pattern/model-routing.md) | 16 | 18 | 9 | 0 | 0 | 1 | 0 |
| [Speculative fan-out](by-pattern/fan-out.md) | 15 | 12 | 3 | 1 | 1 | 1 | 4 |
| [Search & ranking](by-pattern/search-ranking.md) | 28 | 19 | 5 | 7 | 2 | 0 | 4 |
| [Structured extraction](by-pattern/data-extraction.md) | 9 | 3 | 4 | 0 | 0 | 0 | 0 |
| [Classification](by-pattern/classification.md) | 40 | 36 | 24 | 3 | 0 | 0 | 13 |
| [ML feature extraction](by-pattern/feature-extraction.md) | 4 | 2 | 1 | 1 | 0 | 0 | 0 |
| [Document triage](by-pattern/document-triage.md) | 7 | 4 | 6 | 2 | 0 | 0 | 0 |
| [Support triage](by-pattern/support-triage.md) | 5 | 2 | 0 | 0 | 1 | 0 | 3 |
| [Content scoring](by-pattern/content-scoring.md) | 68 | 58 | 25 | 6 | 1 | 1 | 8 |
| [Recommendation](by-pattern/recommendation.md) | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| [Overview](by-pattern/overview.md) | 165 | 118 | 45 | 24 | 29 | 8 | 50 |

## Patterns filed together

284 rows are filed under more than one pattern. The 10 pairs most often filed on the same row:

| Patterns | Rows |
| --- | --- |
| [Safety gating](by-pattern/safety-gating.md) + [Output validation](by-pattern/output-validation.md) | 30 |
| [Tool selection](by-pattern/tool-selection.md) + [Safety gating](by-pattern/safety-gating.md) | 28 |
| [Human escalation](by-pattern/human-escalation.md) + [Content scoring](by-pattern/content-scoring.md) | 27 |
| [Safety gating](by-pattern/safety-gating.md) + [Classification](by-pattern/classification.md) | 23 |
| [Output validation](by-pattern/output-validation.md) + [Content scoring](by-pattern/content-scoring.md) | 23 |
| [Classification](by-pattern/classification.md) + [Content scoring](by-pattern/content-scoring.md) | 23 |
| [Safety gating](by-pattern/safety-gating.md) + [Content scoring](by-pattern/content-scoring.md) | 22 |
| [Tool selection](by-pattern/tool-selection.md) + [Output validation](by-pattern/output-validation.md) | 19 |
| [Tool selection](by-pattern/tool-selection.md) + [Content scoring](by-pattern/content-scoring.md) | 17 |
| [Safety gating](by-pattern/safety-gating.md) + [Human escalation](by-pattern/human-escalation.md) | 16 |

## Authors

1089 rows name an author; they name 982 different ones, compared by display name without regard to case. 907 of them have one row here, 60 two, and 15 three or more; the most any one author has is 11. No author is named on this page: it shows how concentrated the catalogue is, not who contributes to it.

---

Generated by `scripts/build_shape.py` from `catalog.json`, `compat.json`, `patterns.json` and the entry schema; edit those, not this page.
