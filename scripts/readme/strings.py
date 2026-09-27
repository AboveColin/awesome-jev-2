"""The reader-facing sentences the READMEs and pattern pages print.

EN and ZH are one pack per language with the same keys; render() and
render_page() take a pack, which is what keeps the two READMEs structurally
identical instead of slowly diverging. The two tables below are bilingual rows
rather than packs because each row pairs a path with its description.

A few short labels (the reading-map summary, back links, the maintenance-check
captions, the caveat label in rows.py) are still chosen inline by language, and
coverage_note() in sections.py writes its own EN and zh sentences.
"""

from __future__ import annotations

EN = {
    "lang_code": "en",
    "other_readme": "README.zh-CN.md",
    "other_name": "中文",
    "site_label": "Searchable site",
    "collection_first": "First call",
    "collection_build": "Adapt a project",
    "collection_measured": "Independent reports",
    "tagline": (
        "Public resources for Jev — TypeSafe AI's System One decision model — "
        "indexed by the decision it makes, not by the blog that mentioned it."
    ),
    "generated": "This file is generated from catalog.json. Edit the catalog, then run `python3 scripts/build_readme.py`.",
    "badge_note": "Counts describe saved link and evidence records, not current CI passes or runtime tests.",
    "shot_alt": "Searchable Jev catalogue with curated paths, filters, dated source evidence and entry cards",
    "shot_cap": 'Filter by clicking a bar. Two more views: <a href="https://kydlikebtc.github.io/awesome-jev/?view=prims">primitives</a> · <a href="https://kydlikebtc.github.io/awesome-jev/?view=compat">compatibility</a>. Every filter and entry is a shareable URL.',
    # ---- what this is ----
    "about_h": "What this is",
    "about_rows": [
        (
            "**Jev** is a decision model from TypeSafe AI. It does not write text — you hand it "
            "state plus typed questions and it returns typed answers with calibrated confidence, "
            "fast and cheap enough to sit in an agent's inner loop.",
        ),
        (
            "**This repo** indexes public examples of using it, organised by the *decision* being "
            "made. The resource you read this week is disposable; the decision pattern is not.",
        ),
        (
            "**How to assess it:** every row names its source. Call-site citations, primitive "
            "claims and caveats are recorded where available, so you can inspect what was read "
            "and what remains untested.",
        ),
    ],
    "about_not": (
        "Not the product, not an SDK, not affiliated with TypeSafe AI, and not a recommendation. "
        "Inclusion is a source record, not a runtime or performance endorsement. "
        "See [what is verified](#what-is-verified-and-what-is-not)."
    ),
    # ---- primitives ----
    "prims_h": "What Jev returns",
    "prims_intro": (
        "Three primitives. Every pattern below is built out of them, and the asymmetry in the last "
        "row is the single most common source of bugs."
    ),
    "th_prim": "Primitive",
    "th_returns": "Returns",
    "th_limit": "Limits",
    "th_for": "Used for",
    "prims_after": (
        "Input is **text only** — string, JSON object, or array of text. Context is **64k** tokens "
        "per request, **32k** for the state plus the longest question. Output tokens are free. "
        "There are no published weights, so it cannot be run locally. "
        "Full cross-platform differences: [`docs/compatibility.md`](docs/compatibility.md)."
    ),
    # ---- sections ----
    "l_patterns": "Patterns",
    "l_compat": "Compatibility",
    "l_vetting": "Vetting",
    "cov_alt": "Horizontal bar chart of how many catalog examples exist for each of the eighteen decision patterns",
    "prim_alt": "Three panels describing the choice, score and noul primitives and what each returns",
    "start_h": "Start here",
    "start_intro": 'Six things in reading order. Hand-picked, because "most starred" is not the same as "read this first".',
    "th_why_read": "Why this one",
    "coverage_h": "Coverage",
    "coverage_intro": (
        "Every decision pattern, sized by how many entries this catalogue contains. "
        "Use the pattern index below the chart to jump to a section. A zero is a research gap, not a rendering bug."
    ),
    "measured_h": "Measured, not claimed",
    "measured_intro": (
        "Independent measurement reports in the catalogue, including **negative results** that "
        "help explain where an approach fails. These are the original authors' measurements; "
        "this repository has not independently reproduced them. Check each report's dataset, "
        "method and model version before comparing results."
    ),
    "patterns_h": "By decision pattern",
    "patterns_intro": (
        "The primary index. Each heading is a decision an agent has to make; the rows are examples "
        "of making it. Caveats appear as short tags — the full note for each row is in "
        "[`catalog.json`](catalog.json) and on [the site]({site})."
    ),
    "stars_note": (
        "★ gives a repository's GitHub stars as a band — {bands}; rows with no repository or "
        "under {floor} stars show no band. Rows run official first, then with code, then by band, "
        "then by title. A band is a popularity signal, not a quality verdict; the exact count, "
        "as last read from GitHub, is in [`catalog.json`]({catalog}) and on [the site]({site})."
    ),
    "list_sep": ", ",
    "list_and": " and ",
    "kinds_h": "By resource kind",
    "kinds_intro": "The same rows grouped by what you will find when you open the link.",
    "th_find": "What you will find",
    "repo_h": "Also in this repo",
    "repo_intro": "The parts that are not the catalog.",
    "th_file": "File",
    "th_what": "What it is",
    "verified_h": "What is verified, and what is not",
    "stat_rechecked": "evidence recorded",
    "verified_recheck": (
        "**Call-site text checks** — {n} rows record a file and matching strings in `evidence`. "
        "The weekly [claims job](https://github.com/kydlikebtc/awesome-jev/actions/workflows/claims.yml) "
        "checks that those strings remain on the default branch and reports missing text or files. "
        "This count measures recorded evidence, **not latest CI passes**. A text match does not "
        "prove that a call executes, the API is compatible, or the result is correct."
    ),
    "verified_yes": (
        "**Link checks** — {link_ok} rows carry an HTTP 2xx response and a `checked` date; "
        "{link_unstamped} carry no dated success record. Dates vary by row and a past success "
        "does not guarantee availability today. Stars and licences are repository metadata snapshots."
    ),
    "verified_read": (
        "**Source and code review** — `evidence.path` cites the file read, `evidence.read_on` "
        "records the reported review date, and `evidence_none` explains missing file evidence. "
        "Reading a call site is separate from running it. Summaries include source descriptions "
        "and machine translations; see the [method and its limits](docs/method.md)."
    ),
    "verified_no": (
        "**Runtime and performance not independently tested here** — treat every catalogue entry "
        "as untested by this repository, including entries without `code-untested`. Linked "
        "benchmarks describe their authors' measurements; this catalogue has not reproduced them. "
        "Repository build checks and package smoke tests do not exercise those integrations or "
        "the live Jev API, and inclusion is not a security review."
    ),
    "verified_flags_h": "What the tags mean",
    "th_tag": "Tag",
    "th_means": "Means",
    "data_h": "Machine-readable data",
    "data_intro": "One entry per example, validated against a JSON Schema on every push.",
    "contrib_h": "Contributing and licence",
    "contrib_body": (
        "Corrections take priority over additions — a wrong row costs more than a missing one. "
        "See [CONTRIBUTING.md](CONTRIBUTING.md); the bar is *could a reader act on this row without "
        "opening the link?*"
    ),
    "license_body": (
        "Code in `scripts/`, `site/` and `examples/` is [MIT](LICENSE-MIT). Catalog metadata is "
        "[CC0-1.0](LICENSE-CC0), with a per-row `license` field. Linked works keep their own "
        "licences — `repo_license` records what each declares."
    ),
    # ---- table headers ----
    "th_example": "Example",
    "th_shows": "What it shows",
    "th_kind": "Kind",
    "th_code": "Code",
    "th_caveats": "Caveats",
    "th_pattern": "Pattern",
    "th_count": "Examples",
    "no_entries": "_No entries yet._",
    "retired_h": "Retired links",
    "retired_intro": "Links that stopped resolving, kept so a dead reference stays searchable instead of vanishing.",
    "th_why": "Why",
    "pattern_more": "**{shown} of {n}** shown · [all {n} on one page →]({page}) · [filter on the site]({site})",
    "pattern_all": "All {n} shown · [on its own page]({page}) · [filter on the site]({site})",
    "page_intro": (
        "Every catalogued example of this decision — {n} of them. The same rows, with caveats, "
        "are in [the index]({readme}); [the site]({site}) can filter them further by language, "
        "primitive and kind."
    ),
    "page_other_lang": "[中文]({other})",
    "page_footer": (
        "<sub>Generated from `catalog.json` by `scripts/build_readme.py`. "
        "Edit the catalogue, not this file.</sub>"
    ),
    "gap": "no examples yet",
    # ---- stats ----
    "stat_entries": "entries",
    "stat_with_code": "with code",
    "stat_official": "official",
    "stat_verified": "dated 2xx",
    "stat_patterns": "patterns",
    "stat_retired": "retired",
}

ZH = {
    "lang_code": "zh",
    "other_readme": "README.md",
    "other_name": "English",
    "site_label": "可搜索站点",
    "collection_first": "第一次调用",
    "collection_build": "改造现有项目",
    "collection_measured": "独立测量报告",
    "tagline": (
        "Jev（TypeSafe AI 的 System One 决策模型）公开资源索引 —— "
        "按它做的**决策**归类，而不是按提到它的博客归类。"
    ),
    "generated": "本文件由 catalog.json 生成。请修改目录数据后运行 `python3 scripts/build_readme.py`。",
    "badge_note": "数字统计已保存的链接与证据记录，不代表当前 CI 通过数或运行测试结果。",
    "shot_alt": "可搜索的 Jev 目录：精选路径、筛选排序、带日期的来源证据与条目卡片",
    "shot_cap": '点击条形即可筛选。另有两个视图：<a href="https://kydlikebtc.github.io/awesome-jev/?view=prims&lang=zh">三个原语</a> · <a href="https://kydlikebtc.github.io/awesome-jev/?view=compat&lang=zh">兼容性矩阵</a>。每个筛选条件和每个条目都是可分享的 URL。',
    "about_h": "这是什么",
    "about_rows": [
        (
            "**Jev** 是 TypeSafe AI 的决策模型。它不生成文本 —— 你给它状态和类型化问题，"
            "它返回带校准置信度的类型化答案，快且便宜到可以放进智能体的内层循环。",
        ),
        (
            "**本仓库**收集它的公开使用例子，按所做的**决策**组织。"
            "你这周读的那篇资料是一次性的，决策模式不是。",
        ),
        (
            "**如何判断可信度：**每一行都写明来源；有依据时记录调用点、原语声明和注意事项，"
            "方便你查看读过什么，以及哪些部分仍未实测。",
        ),
    ],
    "about_not": (
        "不是产品本身，不是 SDK，与 TypeSafe AI 无隶属关系，也不构成推荐。"
        "收录是一份来源记录，不代表运行验证或性能背书。"
        "详见[哪些经过核实](#哪些经过核实哪些没有)。"
    ),
    "prims_h": "Jev 返回什么",
    "prims_intro": "三个原语。下面所有模式都由它们构成，而最后一行那个不对称是最常见的 bug 来源。",
    "th_prim": "原语",
    "th_returns": "返回",
    "th_limit": "限制",
    "th_for": "用来",
    "prims_after": (
        "输入**仅支持文本** —— 字符串、JSON 对象、或文本数组。上下文每次请求 **64k** token，"
        "其中 state 加最长的那个问题占 **32k**。输出 token 免费。"
        "权重未公开，因此无法本地运行。"
        "跨平台差异全表见 [`docs/compatibility.md`](docs/compatibility.md)。"
    ),
    "l_patterns": "决策模式",
    "l_compat": "兼容性",
    "l_vetting": "核查指南",
    "cov_alt": "十八个决策模式各有多少个目录条目的横向条形图",
    "prim_alt": "三个面板，分别说明 choice、score、noul 三个原语各自返回什么",
    "start_h": "从这里开始",
    "start_intro": "六条，按阅读顺序。手工挑选 —— 因为「star 最多」和「该先读哪个」不是一回事。",
    "th_why_read": "为什么是它",
    "coverage_h": "覆盖度",
    "coverage_intro": (
        "全部决策模式，按本目录的收录数量排列长度。图表下方的场景索引可跳转到对应章节。"
        "数字为 0 的是待补的研究缺口，不是渲染 bug。"
    ),
    "measured_h": "实测，而非宣称",
    "measured_intro": (
        "本目录收录的独立测量报告，包括有助于理解适用边界的**负面结果**。这些是原作者的测量，"
        "本仓库没有独立复现。比较结果前，请分别查看数据集、测试方法和模型版本。"
    ),
    "patterns_h": "按决策模式",
    "patterns_intro": (
        "主索引。每个标题是智能体必须做的一个决策；下面的行是做这个决策的例子。"
        "警示以短标记呈现 —— 每行的完整备注在 [`catalog.json`](catalog.json) 和[站点]({site})里。"
    ),
    "stars_note": (
        "★ 以区间给出仓库的 GitHub star 数 —— {bands}；没有仓库或不足 {floor} 星的行不标区间。"
        "排序：官方优先，其次是含代码的，再按区间，最后按标题。区间只反映热度，不代表质量；"
        "最近一次从 GitHub 读到的精确数字在 [`catalog.json`]({catalog}) 和[站点]({site})上。"
    ),
    "list_sep": "、",
    "list_and": "、",
    "kinds_h": "按资源形态",
    "kinds_intro": "同样这些行，按你点开链接后会看到什么来分组。",
    "th_find": "点开会看到",
    "repo_h": "本仓库还有什么",
    "repo_intro": "除目录数据之外的部分。",
    "th_file": "文件",
    "th_what": "是什么",
    "verified_h": "哪些经过核实，哪些没有",
    "stat_rechecked": "已记录证据",
    "verified_recheck": (
        "**调用点文本复查** —— 有 {n} 行通过 `evidence` 记录了文件和匹配字符串。"
        "每周 [claims 任务](https://github.com/kydlikebtc/awesome-jev/actions/workflows/claims.yml) "
        "检查这些字符串是否仍在默认分支，发现文本或文件缺失时报告。"
        "这个数字是已记录的证据数量，**不是最新 CI 通过数**。文本匹配不能证明调用实际执行、"
        "API 兼容或结果正确。"
    ),
    "verified_yes": (
        "**链接检查** —— 有 {link_ok} 行记录了 HTTP 2xx 响应和 `checked` 日期，"
        "另有 {link_unstamped} 行没有带日期的成功记录。检查日期因条目而异，过去成功不保证今天仍可访问。"
        "star 数和许可证也是仓库元数据的快照。"
    ),
    "verified_read": (
        "**来源与代码阅读** —— `evidence.path` 指向所读文件，`evidence.read_on` 记录声明的阅读日期，"
        "`evidence_none` 解释缺少文件证据的原因。阅读调用点与运行代码是两件事。"
        "摘要包含源项目描述与机翻，详见[方法与局限](docs/method.md)。"
    ),
    "verified_no": (
        "**本仓库未独立验证运行与性能** —— 所有目录条目默认都未经本仓库实测，没有 "
        "`code-untested` 标签也不代表已测试。被收录的基准是原作者的测量，本目录没有独立复现。"
        "仓库构建检查与安装包冒烟测试不运行这些集成，也不调用 Jev 在线 API；收录亦不代表安全审计。"
    ),
    "verified_flags_h": "这些标记是什么意思",
    "th_tag": "标记",
    "th_means": "含义",
    "data_h": "机器可读数据",
    "data_intro": "每个例子一条记录，每次推送都按 JSON Schema 校验。",
    "contrib_h": "参与贡献与许可",
    "contrib_body": (
        "纠错优先于新增 —— 一个错的条目比一个缺失的条目代价更大。"
        "详见 [CONTRIBUTING.md](CONTRIBUTING.md)；收录标准是：*读者不点开链接，能否据此行动？*"
    ),
    "license_body": (
        "`scripts/`、`site/`、`examples/` 中的代码采用 [MIT](LICENSE-MIT)。"
        "目录元数据采用 [CC0-1.0](LICENSE-CC0)，并带逐行 `license` 字段。"
        "被链接的作品各自保留原许可 —— `repo_license` 记录了各自声明的内容。"
    ),
    "th_example": "例子",
    "th_shows": "展示了什么",
    "th_kind": "形态",
    "th_code": "代码",
    "th_caveats": "警示",
    "th_pattern": "模式",
    "th_count": "例子数",
    "no_entries": "_暂无条目。_",
    "retired_h": "已退休的链接",
    "retired_intro": "已无法访问的链接。保留下来，让失效的引用仍可被搜索到，而不是凭空消失。",
    "th_why": "原因",
    "pattern_more": "已显示 **{shown} / {n}** 条 · [在单独页面查看全部 {n} 条 →]({page}) · [在站点上筛选]({site})",
    "pattern_all": "已显示全部 {n} 条 · [单独页面]({page}) · [在站点上筛选]({site})",
    "page_intro": (
        "这个决策的全部已收录例子 —— 共 {n} 条。"
        "同样这些行及其警示也在[索引]({readme})里；[站点]({site})还能按语言、原语和形态进一步筛选。"
    ),
    "page_other_lang": "[English]({other})",
    "page_footer": (
        "<sub>由 `scripts/build_readme.py` 从 `catalog.json` 生成。"
        "请修改目录，不要改这个文件。</sub>"
    ),
    "gap": "暂无例子",
    "stat_entries": "条目",
    "stat_with_code": "含代码",
    "stat_official": "官方",
    "stat_verified": "带日期的2xx",
    "stat_patterns": "覆盖模式",
    "stat_retired": "已退休",
}

# ZH keys whose Chinese a model wrote rather than a person: the same disclosure
# `zh_machine` makes for a catalogue row, and rendered the same way, with
# "(机翻)" after it. A person who rewrites one removes its key from here.
ZH_MACHINE = frozenset({"stars_note"})

# The non-catalog parts of the repo, so navigation is a table rather than a
# scattering of inline links the reader has to hunt for.
REPO_FILES = [
    (
        "docs/patterns.md",
        "Every pattern defined, each with an explicit *when NOT to use this*.",
        "逐个定义每个模式，并明确写出**什么时候不该用它**。",
    ),
    (
        "docs/compatibility.md",
        "Model string, field names, request shape, endpoint and env var differ per platform. This is that table.",
        "模型串、字段名、请求结构、端点、环境变量 —— 每个平台都不一样。这就是那张对照表。",
    ),
    (
        "docs/vetting.md",
        "What to check before trusting a row, and the one mistake most people make.",
        "信任一个条目之前该检查什么，以及大多数人会犯的那一个错。",
    ),
    (
        "docs/status.md",
        "What week one of this ecosystem actually looked like, gaps included.",
        "这个生态第一周的真实样貌，包括缺口。",
    ),
    (
        "docs/method.md",
        "How the catalog was built, what was excluded, and where it is weakest.",
        "目录是如何建起来的、排除了什么、以及它最弱的地方在哪。",
    ),
    (
        "docs/sources.md",
        "Where every row came from, and the licence position.",
        "每一行的来源，以及许可状况。",
    ),
    (
        "examples/",
        "Four runnable examples. One deliberately leaves the threshold policy to you.",
        "四个可运行样例。其中一个刻意把阈值策略留给你写。",
    ),
    (
        "schema/entry.schema.json",
        "What a catalog entry may contain.",
        "一条目录记录允许包含什么。",
    ),
    (
        ".claude-plugin/",
        "Install the skill and the MCP server together in Claude Code: `/plugin marketplace add kydlikebtc/awesome-jev`, then `/plugin install awesome-jev@awesome-jev`.",
        "在 Claude Code 里一次装好技能和 MCP server：先 `/plugin marketplace add kydlikebtc/awesome-jev`，再 `/plugin install awesome-jev@awesome-jev`。",
    ),
    (
        "src/awesome_jev_mcp/",
        "An MCP server, so an agent can query the catalogue instead of reading it. Caveats travel with every result, and so does how current the data is.",
        "一个 MCP server —— 让智能体可以查询目录而不是阅读它。每条结果都带着它的警示，也带着数据有多新。",
    ),
    (
        "skills/awesome-jev/",
        "An agent skill: the facts that generated Jev code most often gets wrong, and the design rules worth following.",
        "一份 agent 技能：生成的 Jev 代码最常搞错的那些事实，以及值得遵循的设计规则。",
    ),
    (
        "scripts/verify_claims.py",
        "Re-reads every cited call site weekly, so a primitive claim is checkable rather than asserted.",
        "每周重读每一处被引用的调用点 —— 让原语声明可核实，而不只是被断言。",
    ),
    (
        "scripts/refresh_metadata.py",
        "Re-reads stars, licences and archive status from the GitHub API and opens a PR.",
        "从 GitHub API 重新读取 star、许可证与归档状态，并开 PR。",
    ),
]

# The data files listed under "Machine-readable data", after catalog.json and
# retired.json, whose rows carry live counts and are written in sections.py.
DATA_FILES = [
    ("compat.json", "The platform matrix behind `docs/compatibility.md`", "`docs/compatibility.md` 使用的平台兼容性数据"),
    ("patterns.json", "The decision taxonomy both generators and the MCP server read", "生成器与 MCP server 共用的决策模式分类"),
    ("collections.json", "Bilingual editorial paths, selection reasons and limitations", "双语精选路径、推荐理由与使用限制"),
    ("schema/entry.schema.json", "One entry's shape", "每条目录记录的字段规范"),
    ("llms.txt", "For agents, with the caveats spelled out", "供智能体读取的目录说明，明确附带限制"),
]
