# history/

One JSON file per weekly refresh, named by the UTC date it ran
(`YYYY-MM-DD.json`), written by
[`scripts/snapshot_stats.py`](../scripts/snapshot_stats.py) in
[`metadata.yml`](../.github/workflows/metadata.yml) just before that refresh's
commit. Each holds every number `_stats.compute()` published that day; rows
per kind, pattern, flag, language and declared licence; the value of each
question [`watch.json`](../watch.json) counts; and each row's slug, stars,
licence and flags.

These are generated data, not a source of truth: `catalog.json` is, and
nothing reads a snapshot back into it. Do not edit or add files here by hand.
Nothing was backfilled from git's history of `catalog.json`, because nobody
published those numbers at the time. [`docs/shape.md`](../docs/shape.md)
reads the files for its "Over time" table once there are three. A star count
is GitHub's at the refresh: a popularity signal, not a quality verdict.

## 中文 <sub>(机翻)</sub>

每次每周刷新写一个 JSON 文件，按运行当天的 UTC 日期命名（`YYYY-MM-DD.json`），由
[`metadata.yml`](../.github/workflows/metadata.yml) 在该次刷新提交之前运行
[`scripts/snapshot_stats.py`](../scripts/snapshot_stats.py) 写入。每个文件记录当天
`_stats.compute()` 公布的全部数字；按类型、模式、标记、语言和声明的许可证统计的行数；
[`watch.json`](../watch.json) 所计数的每个问题的值；以及每一行的
slug、star、许可证和标记。

这些是生成的数据，不是事实来源：事实来源是 `catalog.json`，任何快照都不会被读回其中。请不要手动编辑或添加这里的文件。
没有根据 `catalog.json` 的 git 历史回填，因为当时没有人公布过那些数字。
[`docs/shape.zh-CN.md`](../docs/shape.zh-CN.md) 在有三份快照后会读取它们，生成「随时间的变化」表。
star 数是刷新时 GitHub 的计数：热度信号，不是质量结论。
