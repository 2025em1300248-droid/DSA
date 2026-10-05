# Four books for AI/ML engineers

Four complete, self-contained books, written and typeset from source in this
repository. No LaTeX, no external services — the typesetting engine in
`book/engine/` is part of the repository and builds all four volumes.

| | Volume | Pages | What it is |
|---|---|---|---|
| **I** | **[Data Structures & Algorithms for AI/ML Engineers](build/DSA-for-AI-ML-Engineers.pdf)** | 367 | the algorithmic core, from first principles |
| **II** | **[The AI/ML Engineer Skill Map](build/AI-ML-Engineer-Skill-Map.pdf)** | 123 | the competency roadmap: what to learn, in what order, for which job |
| **III** | **[The AI/ML Engineering Handbook](build/AI-ML-Engineering-Handbook.pdf)** | 317 | every skill on that map, taught properly |
| **IV** | **[Say It Simply](build/Interview-Answers-Plain-English.pdf)** | 118 | 627 interview questions answered in plain English |

Volume II says what to learn. Volume III teaches it. Volume I is the
algorithmic foundation both of them assume. Volume IV is a personal interview
preparation book, answering a 627-question bank in spoken English.

**Together: 925 pages, 137 chapters, ~245,000 words, 131 vector figures,
432 runnable listings.**

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

---

# Volume III — The AI/ML Engineering Handbook

**[→ build/AI-ML-Engineering-Handbook.pdf](build/AI-ML-Engineering-Handbook.pdf)**

The teaching volume: 317 pages, 47 chapters in 8 parts, building every
competency in the Skill Map from the ground up.

| Part | Chapters | Subject |
|---|---|---|
| I | 1–6 | The engineering foundation: modern Python, types and validation, testing ML code, environments, git, containers |
| II | 7–11 | The mathematics you actually use: linear algebra as data movement, backprop derived, probability, statistics, optimisation |
| III | 12–16 | Data: SQL and query engines, Polars and Arrow, point-in-time-correct pipelines, features and skew, corpus curation |
| IV | 17–21 | Classical ML: generalisation, linear models, gradient boosting, calibration and thresholds, explanation |
| V | 22–28 | Deep learning: tensors and autograd, the training loop, architectures, the transformer from scratch, modern components, debugging, scale |
| VI | 29–36 | Foundation models: tokenisation and cost, the forward pass, prompting, structure and tools, retrieval, RAG, fine-tuning, preference optimisation |
| VII | 37–43 | Making it real: evaluation, its statistics, agents, inference and serving, compression, MLOps, hardware |
| VIII | 44–47 | Judgement: security, privacy and compliance, communication, and when not to use ML |

Every chapter opens with a problem rather than a definition, builds the
smallest correct version before any optimisation, closes the gap to the
production version, and ends with the failure modes named by their symptoms.
Each has a *practice* task that verifies the skill and an exercise set.

- 317 pages, 47 chapters, 8 parts
- ~82,000 words
- 233 runnable code listings
- 45 hand-drawn vector figures
- 96 captioned reference tables
- 317 callout boxes, 47 practice tasks, 329 exercises
- Full PDF outline (315 bookmarks), two tables of contents

Representative listings were executed and checked against known results before
publication: the autograd engine against central differences, the
gradient-boosting split finder against a known threshold, BPE for round-trip
fidelity, BM25 and reciprocal rank fusion against hand-worked examples, PSI
against known distribution shifts, the cluster bootstrap against a simulated
clustered set, and the parameter-count formula against the published GPT-2
sizes.

---

# Volume IV — Say It Simply

**[→ build/Interview-Answers-Plain-English.pdf](build/Interview-Answers-Plain-English.pdf)**

A personal interview preparation book: 118 pages, 19 chapters, answering a
627-question bank in plain spoken English rather than textbook phrasing.

Same questions, same facts — the wording is what changed. Ordinary words
instead of jargon, two or three sentences per answer, and an explanation of
any term that could not be avoided. Where an answer can land on one of the
candidate's own projects, it does.

| Part | Chapters | Subject |
|---|---|---|
| I | 1–2 | The behavioural round, and defending the numbers on your own resume |
| II | 3–4 | Python, SQL, C++ and MongoDB |
| III | 5–8 | Statistics, data handling, classical ML, imbalance and metrics |
| IV | 9–10 | Deep learning, CNNs, YOLO and OpenCV |
| V | 11–13 | NLP and transformers, embeddings and RAG, prompting and agents |
| VI | 14–16 | MLOps, APIs and Git, ML system design |
| VII | 17–19 | The four projects defended, the coding round, and the final checklist |

- 118 pages, 19 chapters, 7 parts
- All 627 questions from the source bank, verified present with none invented
- ~35,000 words

## Building it

```bash
pip install reportlab pygments pyphen

cd book      && python3 build_book.py      -o ../build/DSA-for-AI-ML-Engineers.pdf
cd roadmap   && python3 build_roadmap.py   -o ../build/AI-ML-Engineer-Skill-Map.pdf
cd handbook  && python3 build_handbook.py  -o ../build/AI-ML-Engineering-Handbook.pdf
cd interview && python3 build_interview.py -o ../build/Interview-Answers-Plain-English.pdf
```

Volume I takes about 20 seconds, Volume II about 3, Volume III about 13, and
Volume IV about 2. All four are multi-pass builds (the tables of contents and page labels have to
converge).

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
interview/
  build_interview.py volume IV, same engine
  manifest.py        metadata, 7 parts, 19 chapters
  content/*.md       19 chapters covering all 627 questions
handbook/
  build_handbook.py  volume III, same engine
  manifest.py        metadata, 8 parts, 47 chapters
  content/*.md       47 chapters + front matter
  figures_handbook.py 45 diagrams specific to this volume
build/
  DSA-for-AI-ML-Engineers.pdf
  AI-ML-Engineer-Skill-Map.pdf
  AI-ML-Engineering-Handbook.pdf
  Interview-Answers-Plain-English.pdf
```

The content format is a small extended Markdown: headings, lists, tables,
fenced code, `$math$`, `:::callout` blocks, and `@fig:` references to the
diagram registry. Adding a chapter means adding one file to `content/` and
one line to `manifest.py`. Volumes II and III import the engine and figure
registry from `book/` unchanged and only add their own content and diagrams.

## Fonts

Source Serif Pro and Source Sans Pro (SIL Open Font License) and DejaVu Sans
Mono (Bitstream Vera licence). DejaVu also serves as an automatic fallback
for mathematical glyphs the Source families do not carry.
