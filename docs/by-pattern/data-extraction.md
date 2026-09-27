# Structured extraction

<sub>[awesome-jev](../../README.md) · [中文](data-extraction.zh-CN.md)</sub>

_Pull typed fields out of messy text by choosing among candidates rather than generating them._

Every catalogued example of this decision — 16 of them. The same rows, with caveats, are in [the index](../../README.md#structured-extraction); [the site](https://kydlikebtc.github.io/awesome-jev/?p=data-extraction&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show none. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

- **[Cookbook: Date extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook)** ⭐ — Extracts absolute and relative dates by asking for the parts a document names, then resolving and validating them in code with confidence-based review.
  <sub>`Official docs` · `Py`</sub>

- **[Cookbook: Pre-parsed value extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook)** ⭐ — Regexes find candidate emails, phone numbers and amounts; the model selects the requested span so code can normalise a verbatim value.
  <sub>`Official docs` · `Py` · `choice`</sub>

- **[Cookbook: Structure recovery](https://docs.typesafe.ai/cookbooks/autoformat)** ⭐ — Reconstructs Markdown from plain text that lost its formatting, in two requests: one restitches hard-wrapped lines, one classifies every block.
  <sub>`Official docs` · `Py`</sub>

- **[Cookbook: Structured data extraction cascade](https://docs.typesafe.ai/cookbooks/sde_cascade)** ⭐ — A two-stage mini-then-verify-then-reasoning cascade that reaches most of a big reasoning model's quality at a fraction of the cost.
  <sub>`Official docs` · `Py`</sub>

- **[jev-macos-loop](https://github.com/jcpsimmons/jev-macos-loop)** — Open-source macOS AI computer use and native GUI automation on Apple silicon. Jev + OmniParser CoreML + Apple Vision OCR. Bring your own OpenRouter, Vercel AI Gateway, or TypesafeAI token.
  <sub>`Project` · ★10+ · jcpsimmons · `JS`</sub>

- **[jev-reviewer](https://github.com/choxos/jev-reviewer)** — Data extraction for systematic reviews, quoted from the papers. Ask a trial report and its supplements your extraction form or a RoB 2, ROBINS-I, QUADAS-2 or TIDieR template; Jev points at the lines, every answer is a verbatim quote with its page, you check it and export the table. Files stay i
  <sub>`Project` · ★10+ · choxos · `JS`</sub>

- **[jevfill](https://github.com/imohitmayank/jevfill)** — A Chrome extension that fills web forms from unstructured notes with Jev: paste your details once as plain text, with no structured profile, then fill forms on demand.
  <sub>`Plugin` · ★10+ · imohitmayank · `TS`</sub>

- **[smart-paste](https://github.com/nomanjack/smart-paste)** — Fills form fields from pasted text: the form's heading, labels and your text go to TypeSafe, and it inserts the values it matches for you to review before submitting.
  <sub>`Plugin` · ★10+ · nomanjack · `JS`</sub>

- **[ask-jev](https://github.com/logicrw/ask-jev)** — Ultra-fast, fail-open advisory decisions and verbatim extractive reading view for AI coding agents and CLI pipelines
  <sub>`Project` · logicrw · `Py`</sub>

- **[jev-data-questions](https://github.com/narulaskaran/jev-data-questions)** — Bring a dataset and see the right chart: the UI inspects the CSV's shape and proposes insights, and Jev fills in the values.
  <sub>`Project` · narulaskaran · `TS` · ⚠ `no licence`</sub>

- **[jev-information-extraction](https://github.com/abhishekmamdapure/jev-information-extraction)** — Parsing the PDF and extracting the relevant information
  <sub>`Project` · abhishekmamdapure · `Py` · ⚠ `no licence`</sub>

- **[jev-mcp-dispatcher](https://github.com/abhishekashokvkumar/jev-mcp-dispatcher)** — Natural-language MCP tool dispatcher powered entirely by TypeSafe's Jev — no general-purpose LLM. Discovers a simple MCP server's tool signatures at runtime and uses Jev's typed primitives (Choice/Noul) to pick the right tool and extract its arguments straight out of the sentence.
  <sub>`Plugin` · abhishekashokvkumar · `Py` · ⚠ `no licence`</sub>

- **[jeveryword](https://github.com/jkrup/jeveryword)** — Text extraction with Jev: field extraction, PII detection and exact quotes, built on TypeSafe's Jev.
  <sub>`Project` · jkrup · `JS`</sub>

- **[jevsume](https://github.com/unownone/jevsume)** — ATS-friendly resume review powered by Jev (TypeSafe System One). The frontend extracts resume text the way a parser would, then a Cloudflare Worker runs typed JEV questions and composes a JevScore.
  <sub>`Project` · unownone · `TS` · ⚠ `no licence`</sub>

- **[smoking-extraction-benchmark](https://github.com/vclic/smoking-extraction-benchmark)** — Synthetic smoking-history extraction benchmark comparing TypeSafe Jev and OpenAI structured outputs, with reproducible accuracy, cost, and latency results.
  <sub>`Benchmark` · vclic · `Py` · ⚠ `no licence`</sub>

- **[typesafe-ai-jev-example](https://github.com/ItBayMax/typesafe-ai-jev-example)** — Hands-on demos for TypeSafe's Jev (System One) model: six runnable examples and four field notes. Runs offline with no API key; samples/ holds real measured output from jev-1.13.0.
  <sub>`Project` · itbaymax · `Py`</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
