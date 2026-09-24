# How to Read This Book

This is a long book, and you should not read it the way you read a novel.
What follows is an honest account of who it is for, how it is organised,
and how to extract the most from it per hour spent.

## Who this is for

You write code that touches machine learning. Maybe you train models, maybe
you serve them, maybe you build the pipelines that feed them. You are
comfortable in Python. You know what a list and a dictionary are. Perhaps
you have never formally studied algorithms; perhaps you did, years ago, and
it has faded into a vague memory of Big-O notation and a red-black tree you
never used again.

The premise of this book is that the second group is larger than anyone
admits, and that both groups are being underserved. General algorithms
textbooks are rigorous but speak a different dialect: their examples are
schedulers and compilers, not dataloaders and vector indexes. Interview-prep
books are practical but shallow: they teach you to recognise a pattern, not
to reason about a machine. Meanwhile the actual algorithmic content of
modern machine learning --- paged attention, product quantisation, ring
all-reduce, histogram-based tree splitting, speculative decoding --- appears
in neither.

:::insight What this book assumes
Python fluency, comfort with arrays and dictionaries, and the ability to read
a mathematical expression without panic. It does **not** assume a computer
science degree, prior exposure to formal proofs, or knowledge of C++. Where
the book needs mathematics, it derives it.
:::

## The shape of the book

The forty-seven chapters are arranged in nine parts, and the difficulty is
genuinely monotonic. Part I is about counting operations and understanding
what a memory hierarchy is; Part VIII is about designing algorithms that
saturate a thousand GPUs. A reader who starts at Chapter 1 with no
background should be able to reach Chapter 47 without ever hitting a wall.

- **Parts I--III** build the foundation: cost models, memory, arrays,
  hashing, sorting, searching, trees, heaps. If you have never studied
  algorithms, this is your course. If you have, read Chapters 3 and 4
  anyway --- almost nobody was taught the memory-hierarchy story properly,
  and it silently governs everything else.
- **Parts IV--VI** are the classical algorithmic core, taught with an ML
  accent: dynamic programming through the lens of dynamic time warping and
  Viterbi decoding, graphs through the lens of autograd and GNN sampling,
  sketches through the lens of deduplicating a web-scale corpus.
- **Part VII** is the part you cannot find elsewhere: the algorithms inside
  the systems you use every day. Vector search, samplers, decoders, KV
  caches, gradient-boosted trees.
- **Part VIII** takes the whole toolkit to parallel and distributed
  hardware, where the cost model changes shape entirely.
- **Part IX** is for consolidation: a problem-solving method, a catalogue of
  patterns, a graded problem set with complete solutions, and a study plan.

## How each chapter works

Every chapter follows the same rhythm, and knowing it lets you skim
deliberately rather than accidentally.

| Element | What it is | How to use it |
|---|---|---|
| Opening blurb and objectives | The chapter's promise | Read first; return to it to self-test |
| Main exposition | Idea, then mechanism, then code | Read linearly; do not skip the derivations |
| `KEY INSIGHT` boxes | The one sentence worth memorising | If you remember nothing else, remember these |
| `WHERE THIS SHOWS UP IN ML` | The concrete production connection | Skim on first pass, study on second |
| `COMMON PITFALL` | Mistakes practitioners actually make | Read every one; they are cheap experience |
| `PERFORMANCE NOTE` | Constants, cache behaviour, real numbers | Read if you ship code |
| Figures | Mechanism made visible | Trace them with a finger; they repay it |
| `EXERCISES` | Graded practice, hardest last | Do at least the first three |
| `CHAPTER RECAP` | Compressed summary | Use for review; never as a substitute |

## Three ways to read it

:::note Choose your path
**The course (14--16 weeks).** Chapters 1 to 47 in order, three to five
hours a week, doing the exercises. This is what the book is optimised for,
and Chapter 47 contains a week-by-week plan.

**The interview sprint (5--6 weeks).** Chapters 2, 4, 6--13, 16--20, 22--24,
then Part IX. Skip Parts VI--VIII on the first pass. Do every exercise
marked with a dagger.

**The reference.** Read Chapter 2 and Chapter 3 once, properly. After that,
jump to whichever chapter names the thing you are fighting. Each chapter is
written to survive being read alone, and cross-references are explicit.
:::

## About the code

Every implementation in this book is real, runnable Python. It is written
for clarity first, but never at the cost of being wrong about complexity:
where the clear version is asymptotically worse than the production version,
the book says so and shows both. Type hints are used where they clarify and
omitted where they only add noise.

Python is not a fast language, and some of the structures here would be
written in C++ or CUDA in a real system. That is not a reason to avoid
Python for teaching: the algorithm is the idea, and the idea transfers.
Where the constant factor matters enough to change the decision --- and it
often does --- the book gives you the measured numbers, not hand-waving.

:::pitfall The trap of reading without writing
Algorithms are a motor skill. Reading a description of a Fenwick tree
produces a warm feeling of comprehension that evaporates within days. Typing
one out, breaking it, and fixing it produces a memory that lasts years.
Budget half your time for the keyboard.
:::

## A note on rigour

This book proves things when the proof teaches you something and states
results plainly when it does not. You will find a full amortised analysis of
the dynamic array, because that analysis is a reusable way of thinking. You
will not find a proof that comparison sorting requires $\Omega(n \log n)$
comparisons --- you will find the information-theoretic argument in two
paragraphs, which is the part you can actually reuse.

Where a claim depends on hardware, the book names the hardware. Where a
constant matters, it gives an order of magnitude. Where the honest answer is
"measure it", it says so.
