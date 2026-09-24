# Data Structures & Algorithms for AI/ML Engineers

A complete, self-contained 367-page book, written and typeset from source in
this repository.

**[→ build/DSA-for-AI-ML-Engineers.pdf](build/DSA-for-AI-ML-Engineers.pdf)**

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

## Building it

```bash
pip install reportlab pygments pyphen
cd book && python3 build_book.py -o ../build/DSA-for-AI-ML-Engineers.pdf
```

Takes about 22 seconds. No LaTeX, no external services.

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
build/
  DSA-for-AI-ML-Engineers.pdf
```

The content format is a small extended Markdown: headings, lists, tables,
fenced code, `$math$`, `:::callout` blocks, and `@fig:` references to the
diagram registry. Adding a chapter means adding one file to `content/` and
one line to `manifest.py`.

## Fonts

Source Serif Pro and Source Sans Pro (SIL Open Font License) and DejaVu Sans
Mono (Bitstream Vera licence). DejaVu also serves as an automatic fallback
for mathematical glyphs the Source families do not carry.
