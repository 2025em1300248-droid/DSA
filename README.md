# Two books for AI/ML engineers

Two complete, self-contained books, written and typeset from source in this
repository. No LaTeX, no external services — the typesetting engine in
`book/engine/` is part of the repository and builds both volumes.

| | Volume | Pages |
|---|---|---|
| **I** | **[Data Structures & Algorithms for AI/ML Engineers](build/DSA-for-AI-ML-Engineers.pdf)** — the algorithmic core, taught from first principles | 367 |
| **II** | **[The AI/ML Engineer Skill Map](build/AI-ML-Engineer-Skill-Map.pdf)** — the current competency roadmap, role by role | 123 |

The first teaches you the material. The second tells you what material to
learn, in what order, for which job.

---

# Volume I — Data Structures & Algorithms for AI/ML Engineers

## What it is

Forty-seven chapters in nine parts, from counting operations to serving a
trillion-parameter model. The difficulty is monotonic: Part I assumes only
Python fluency, Part VIII covers algorithms that saturate a thousand GPUs.

| Part | Chapters | Subject |
|---|---|---|
| I | 1–5 | Foundations: complexity, the memory hierarchy, arrays and strides, strings and tokens |
| II | 6–11 | The core toolkit: linked structures, hashing, recursion, sorting, binary search, windows |
| III | 12–15 | Hierarchies and priorities: trees, heaps, tries and automata, union–find |
| IV | 16–21 | Design paradigms: divide and conquer, greedy, dynamic programming, backtracking, randomisation |
| V | 22–26 | Graphs: traversal, shortest paths, DAGs and autograd, flows and matching, graphs in ML |
| VI | 27–31 | Structures for scale: Fenwick/segment trees, sketches, LSH, suffix structures, on-disk engines |
| VII | 32–38 | The ML-native canon: ANN search, vector indexes, samplers, decoders, KV caches, tree learners, streaming |
| VIII | 39–42 | Parallel, distributed and hardware-aware: scan/reduce, GPU design, all-reduce, data pipelines |
| IX | 43–47 | Mastery: a problem-solving method, a pattern catalogue, 54 solved problems, a study plan and reference |

## Why it is different from a general algorithms text

Every chapter connects the classical material to the systems an ML engineer
actually runs. Dynamic programming is taught through edit distance, DTW,
Viterbi and CTC; DAGs through automatic differentiation and gradient
checkpointing; heaps through top-*k* retrieval, beam search and BPE training;
hashing through feature hashing and corpus deduplication. Part VII covers
material that appears in no general algorithms textbook: product
quantisation, HNSW, the alias method and the Gumbel trick, speculative
decoding, paged attention and radix prefix caches, histogram-based tree
splitting, t-digest.

## Contents by the numbers

- 367 pages, 47 chapters, 9 parts
- ~82,000 words of prose
- 198 runnable Python listings (~3,700 lines), syntax highlighted
- 75 hand-drawn vector figures (no raster images; the PDF is 1.9 MB)
- 68 captioned reference tables
- 395 callout boxes (key insights, ML connections, pitfalls, performance
  notes, theorems and proofs)
- 378 exercises and worked problems, 54 of them with complete solutions
- Full PDF outline (402 bookmarks), two tables of contents, roman/arabic
  page labels

Every algorithm in the two problem-set chapters was verified against a
brute-force reference on thousands of randomised inputs before publication.

---

# Volume II — The AI/ML Engineer Skill Map

**[→ build/AI-ML-Engineer-Skill-Map.pdf](build/AI-ML-Engineer-Skill-Map.pdf)**

A 123-page competency roadmap, current as of 2026. Twenty-four chapters in
eight parts, covering what an AI/ML engineer is actually expected to know
today — and, unusually, what has stopped mattering.

| Part | Chapters | Subject |
|---|---|---|
| I | 1–2 | The landscape: five jobs behind one job title; how to use the map |
| II | 3–5 | Foundations: Python and engineering, mathematics, algorithms and systems |
| III | 6–7 | Data: pipelines and feature stores, dataset curation |
| IV | 8–10 | Modelling: classical ML, deep learning, training at scale |
| V | 11–15 | Foundation models: LLM internals, retrieval and RAG, post-training, agents, evaluation |
| VI | 16–18 | Production: inference and serving, MLOps, hardware and systems |
| VII | 19–20 | Judgement: safety, security and compliance; product and communication |
| VIII | 21–24 | Getting there: what changed, four learning tracks, portfolio, self-assessment |

Every chapter carries an explicit skill inventory split into **essential**,
**core** and **advanced** tiers, a *how to tell you have it* section with a
concrete build task, a realistic time-to-competence estimate, and the failure
modes that come with the territory. Chapter 21 states plainly which skills
became scarce recently and which are no longer worth your study time;
Chapter 24 is a 28-row, five-level rubric for scoring yourself honestly.

- 123 pages, 24 chapters, 8 parts
- ~29,000 words
- 11 vector figures, 18 reference tables, 218 callout boxes
- Four week-by-week learning tracks with per-week deliverables
- Six portfolio project specifications, each containing a real decision
- Full PDF outline (126 bookmarks), two tables of contents

## Building it

```bash
pip install reportlab pygments pyphen

cd book     && python3 build_book.py    -o ../build/DSA-for-AI-ML-Engineers.pdf
cd roadmap  && python3 build_roadmap.py -o ../build/AI-ML-Engineer-Skill-Map.pdf
```

Volume I takes about 22 seconds, Volume II about 3. Both are multi-pass
builds (the tables of contents and page labels have to converge).

## Repository layout

```
book/
  build_book.py      assemble the story and run the multi-pass build
  manifest.py        book metadata, parts, chapter running order
  content/*.md       47 chapters + front matter in an extended Markdown
  engine/
    style.py         design system: fonts, palette, page geometry, type scale
    markup.py        inline markup compiler + a TeX-like math renderer
    draw.py          vector drawing layer (boxes, arrows, trees, plots)
    flowables.py     callouts, syntax-highlighted code blocks, tables
    parser.py        block parser: Markdown → ReportLab flowables
    doc.py           page furniture, running heads, TOC, PDF outline
    pages.py         cover, part dividers, chapter openers
  figures/*.py       75 diagrams, one function each
  fonts/             Source Serif Pro, Source Sans Pro, DejaVu Sans Mono
roadmap/
  build_roadmap.py   volume II, reusing book/engine and book/figures
  manifest.py        metadata, 8 parts, 24 chapters
  content/*.md       24 chapters + front matter
  figures_roadmap.py 11 diagrams specific to this volume
build/
  DSA-for-AI-ML-Engineers.pdf
  AI-ML-Engineer-Skill-Map.pdf
```

The content format is a small extended Markdown: headings, lists, tables,
fenced code, `$math$`, `:::callout` blocks, and `@fig:` references to the
diagram registry. Adding a chapter means adding one file to `content/` and
one line to `manifest.py`. Volume II imports the engine and figure registry
from `book/` unchanged and only adds its own content and diagrams.

## Fonts

Source Serif Pro and Source Sans Pro (SIL Open Font License) and DejaVu Sans
Mono (Bitstream Vera licence). DejaVu also serves as an automatic fallback
for mathematical glyphs the Source families do not carry.
