"""The README generator, split by what changes together.

scripts/build_readme.py is the command, and the names other scripts and tests
import from it. The work lives here:

  strings.py   the two string packs, EN and zh-CN side by side
  rows.py      paths, taxonomy labels, and how one catalogue row is written
  sections.py  README.md and README.zh-CN.md, one function per section
  pages.py     docs/by-pattern/, one page per decision pattern, and
               docs/measured.md, every independent measurement report

Not every reader-facing word is in the packs yet: coverage_note() and the
short labels written `"…" if lang == "zh" else "…"` (the reading-map toggle,
the pattern index, the caveat and back-to-top labels) sit in sections.py and
rows.py beside the code that prints them. Change both languages there too.

Import it with scripts/ on sys.path, as build_readme.py and the tests do: it
reads the shared _stats, _github and build_readme_cover modules from there.
To change what a test sees, patch the module that reads the name (for example
readme.sections.START_HERE), not build_readme, whose copies nothing reads.
"""
