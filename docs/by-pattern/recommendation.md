# Recommendation

<sub>[awesome-jev](../../README.md) · [中文](recommendation.zh-CN.md)</sub>

_Choose what to surface next, fast enough for a live conversation._

Every catalogued example of this decision — 1 of them. The same rows, with caveats, are in [the index](../../README.md#recommendation); [the site](https://kydlikebtc.github.io/awesome-jev/?p=recommendation&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show no band. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

A *call site* link opens the one file a row cites (`evidence.path`) at `HEAD` of the repository's default branch; the date after it is the day a person last read that file (`evidence.read_on`): a reading, not a run of the code. A *cited file* link is the same for a file that shows the project speaking Jev's request shape rather than building on Jev, or only an example it ships (`evidence.kind`). Neither is pinned to a commit, so it opens the file as it is now, which may differ from what was read, and stops resolving once the file moves; the weekly claims check reports that.

- **[Jevflix](https://github.com/ArielBubis/Jevflix)** — Jev picks, you watch. A hybrid movie recommender: fast semantic + keyword search narrows 4,800 films to a shortlist, then TypeSafe Jev reads your constraints and picks the one film that fits - with a confidence score that decides whether to answer instantly or ask a follow-up. <sub>(upstream description)</sub>
  <sub>`Project` · arielbubis · `Py` · call site [`movie_rec/jev_client.py`](https://github.com/ArielBubis/Jevflix/blob/HEAD/movie_rec/jev_client.py), read 2026-09-24</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
