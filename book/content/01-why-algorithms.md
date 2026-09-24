# Why an ML Engineer Needs Algorithms
@short: Why Algorithms
@subtitle: The parts of your system that no amount of model quality can fix
@tier: foundation
@prereq: Python
@blurb: There is a widespread and comfortable belief that machine learning engineering is about models, and that data structures belong to a previous generation of software. This chapter dismantles that belief with specifics. We will look at where time and memory actually go in a modern ML system, why the answer is almost never "the matrix multiply", and what it costs a team when nobody on it can reason about an algorithm.
@objectives:
- Locate the algorithmic content hiding inside a "pure ML" system
- Read a latency budget and identify which line is an algorithm choice
- Understand why asymptotics start mattering exactly when a prototype becomes a product
- Recognise the four failure modes that algorithmic ignorance produces on ML teams
- Set up a working environment and a habit for the rest of the book

## A story that happens every year

A team ships a retrieval-augmented question answering service. In the
prototype it is beautiful: 40,000 documents, a sentence-transformer
embedding, cosine similarity computed with a single NumPy matrix multiply,
and a language model on top. Latency is 180 milliseconds. Everyone is
delighted.

Six months later the corpus is 40 million documents. The same matrix
multiply now needs 40 million dot products of dimension 768 per query. That
is about 61 billion multiply-accumulate operations, and even at a generous
50 GFLOP/s of achieved throughput on the serving box it takes over two
seconds --- per query, before the language model has produced a single
token. The index no longer fits in the pod's memory either: 40M x 768
float32 values is 123 GB.

The team's first instinct is to buy bigger machines. Their second is to
shard the corpus across twenty replicas and fan out. Both work, expensively.
What neither does is notice that the operation they are performing ---
"find the twenty nearest vectors" --- has been studied for fifty years, that
an HNSW graph answers it in roughly 2 milliseconds with 98% recall, and that
product quantisation would have compressed those 123 GB down to 4 GB with a
measurable and *tunable* accuracy loss.

@fig: latency_budget | 140 | A realistic latency budget for a retrieval-augmented generation request. Five of the six lines are determined by an algorithm or a data structure; only the model weights themselves are fixed.

The gap between two seconds and two milliseconds is a factor of a thousand.
No amount of model tuning produces a factor of a thousand. No framework
upgrade does either. This is what algorithms buy you, and it is why the
distinction between "ML work" and "algorithms work" is a fiction that the
people who write the systems you depend on never believed in.

:::insight The core claim of this book
In a modern ML system, the model is usually the part whose cost you cannot
change. Everything around it --- how data is deduplicated, sampled, indexed,
batched, cached, and decoded --- is an algorithm choice, and those choices
routinely span three orders of magnitude.
:::

## Where the algorithms actually are

It is worth being concrete rather than rhetorical. Here is a modern
training-and-serving stack with the algorithmic content named.

@fig: ml_pipeline_cost | 122 | The canonical pipeline. Under each stage is the family of data structures that stage is actually built from.

### Ingestion and deduplication

Training corpora are full of near-duplicates, and near-duplicates measurably
hurt models: they waste gradient steps, they inflate evaluation scores
through contamination, and they cause verbatim memorisation. Finding exact
duplicates is a hashing problem. Finding *near* duplicates in a corpus of
ten billion documents is a MinHash and locality-sensitive hashing problem,
solvable in a few CPU-hours; the naive pairwise comparison is $\binom{10^{10}}{2}
\approx 5 \times 10^{19}$ document pairs, which is not solvable at all.
Chapter 29 does this properly.

### Tokenization

Every token your model ever sees passed through a tokenizer. Byte-pair
encoding training is a repeated "find the most frequent adjacent pair"
operation, which is a priority queue with lazy deletion; a naive
implementation over a 300 GB corpus runs for days, and the standard one
runs in hours. Inference-time tokenization is a longest-match search over a
trie, or an Aho--Corasick automaton if you also need to detect forbidden
strings. Chapter 14 builds both.

### Sampling and batching

Curriculum learning, importance sampling, class-balanced sampling and
prioritized experience replay all reduce to the same question: *sample an
index from a distribution whose weights keep changing*. Done naively that is
$O(n)$ per sample, and it will dominate your dataloader. Done with a Fenwick
tree it is $O(\log n)$; done with an alias table --- when the weights are
static --- it is $O(1)$. Chapters 27 and 34.

### Training

Automatic differentiation is a topological sort over a directed acyclic
graph followed by a reverse traversal. Gradient checkpointing is a
space--time tradeoff computed by dynamic programming. Distributed data
parallelism is ring all-reduce, an algorithm whose communication cost is
$2(P-1)/P \times$ the parameter size regardless of how many workers $P$ you
add --- a genuinely beautiful result that Chapter 41 derives.

### Indexing and serving

Vector search is nearest-neighbour search in high dimensions: k-d trees,
inverted file indexes, product quantisation, small-world graphs. Serving a
language model is a decoding algorithm (greedy, beam, nucleus, speculative)
on top of a memory manager for the key-value cache, and the best-known
memory manager --- paged attention --- is a straight port of operating-system
virtual memory. Chapters 32 through 36.

:::ml None of this is exotic
Every algorithm named above is inside a library you already import. The
question is not whether you will use them; you already do. The question is
whether you can reason about them when the defaults stop working --- which
is precisely the moment your project becomes important enough to have users.
:::

## Why asymptotics start mattering later than you think, and then all at once

The most common objection to studying algorithms is empirical and fair:
"my code is fast enough". It usually is. The reason to learn this material
anyway is that the transition is not gradual.

@fig: two_curves | 150 | Three algorithms for one task. At prototype scale the quadratic algorithm is *faster* --- it has the smallest constant and no index to build. The crossover is invisible until you cross it.

Consider a quadratic algorithm with a small constant versus a linearithmic
one with a large constant. At $n = 1{,}000$ the quadratic version may well
win; it has no setup cost, no index, no memory allocator pressure. At
$n = 100{,}000$ it loses by a factor of a hundred. Nothing in the code
changed. Nothing in the *profile* looked alarming at $n = 1{,}000$, either;
the function was 3% of runtime.

This is why experienced engineers react to an $O(n^2)$ loop the way a
structural engineer reacts to a cracked weld. It is not currently a problem.
It is a problem *shaped* like a countdown.

:::math The rule of thumb worth memorising
A modern CPU core performs roughly $10^9$ simple operations per second in
optimised native code, and roughly $10^7$ per second in interpreted Python.
So for a one-second budget:

- $O(n^2)$ is fine to about $n = 30{,}000$ in C, $n = 3{,}000$ in Python.
- $O(n \log n)$ is fine to about $n = 3 \times 10^7$ in C.
- $O(n)$ streaming over data you must read anyway is essentially free.
- $O(2^n)$ is fine to about $n = 30$, and never beyond, ever.

These four lines will correctly predict the feasibility of most things you
will be asked to build.
:::

## The four failure modes

Teams without algorithmic fluency fail in recognisable ways. Naming them
makes them easier to catch in review.

**1. The invisible quadratic.** Someone writes a loop over documents, and
inside it a lookup that is itself a scan --- `if doc_id in list_of_ids`. In
Python that is `O(n)` inside an `O(n)` loop. The fix is one character:
make it a `set`. The bug survives review because the inner operation looks
atomic. Chapter 7 will make you allergic to this.

**2. The premature index.** The inverse error. Someone builds an HNSW index
over 4,000 vectors because "vector search needs a vector database". The
brute-force matrix multiply would have taken 0.2 milliseconds and been
exact. Complexity has a cost too, and it is paid in bugs and on-call pages.

**3. The right algorithm on the wrong machine.** A linked list is
asymptotically superb for insertion, and empirically catastrophic, because
every node is a cache miss and a cache miss costs the time of roughly 200
arithmetic operations. Chapter 3 is entirely about this, because it is the
most common place where textbook knowledge produces slow code.

**4. The unreasoned default.** `sort()` is called in a hot loop that only
needs the largest element; `pandas.apply` is used where a vectorised
operation exists; a Python `dict` holds 400 million integer keys and the
pod is killed for memory. None of these is exotic. Each is a default that
nobody thought about.

:::pitfall "The library handles it"
Libraries handle the common case. FAISS will happily let you build an index
that needs 200 GB, PyTorch will happily let your dataloader become the
bottleneck, and a vector database will happily return 60% recall while
reporting success. Libraries expose knobs; knobs require a model of what
they do. That model is this book.
:::

## What "world class" means here

A great deal of algorithm education optimises for reproducing a known
solution under time pressure. That is a real skill --- it is how you pass
interviews, and Part IX takes it seriously --- but it is not the skill that
makes systems fast. The skill that makes systems fast is a three-part habit:

1. **Name the operation.** "I need the twenty nearest vectors" is a named
   problem with a literature. "I need to make this faster" is not.
2. **Write down the cost model.** How many times will this run? On what $n$?
   Is the bottleneck operations, memory traffic, or network? Chapter 2 and
   Chapter 3 give you the vocabulary.
3. **Know the shape of the solution space.** Between brute force and the
   state of the art there are usually four or five options with different
   accuracy, memory and build-time tradeoffs. Knowing they exist is 90% of
   the value; this book's job is to put them in your head.

:::insight Recognition beats derivation
You will almost never derive a new algorithm at work. You will constantly
*recognise* that a problem in front of you is an instance of one you have
seen. This is why breadth matters, why the ML-specific chapters in Part VII
matter, and why you should read even the chapters you will not immediately
use.
:::

## Setting up

Everything in this book runs on a plain Python 3.10+ installation. A handful
of chapters use NumPy; a few use `matplotlib` for you to plot your own
measurements. Nothing requires a GPU, though Part VIII will make more sense
if you have ever seen one.

```python title="Environment check"
import sys, timeit, platform

print(sys.version.split()[0], platform.machine())

# How many simple Python operations does this machine do per second?
n = 1_000_000
t = timeit.timeit("total += 1", setup="total = 0", number=n)
print(f"{n/t:,.0f} simple statements/sec")

# ... and how many with NumPy doing the loop for us?
import numpy as np
a = np.ones(10_000_000, dtype=np.float32)
t = timeit.timeit(lambda: a.sum(), number=10) / 10
print(f"{a.size/t:,.0f} float adds/sec in NumPy")
```

Run it. On a typical 2026 laptop you will see something like 30 million
Python statements per second and 3 billion float additions per second in
NumPy --- a hundredfold gap that explains most of what you will ever need to
know about why vectorisation matters. Write the two numbers down; you will
use them as a sanity check for the rest of the book.

:::exercise
1. Take a piece of code you have written in the last month. Identify the
   single loop with the largest $n$. Write down its complexity in terms of
   that $n$. If you cannot, mark it and come back after Chapter 2.
2. Estimate, without running anything, how long a brute-force nearest
   neighbour search over one million 768-dimensional float32 vectors takes
   on one CPU core. Then measure it with NumPy. Explain the difference
   between your estimate and reality --- Chapter 3 contains the answer.
3. Find one place in a codebase you work in where a `list` is used for
   membership tests. Estimate the speedup from changing it to a `set` at
   your current data size and at 100x that size.
4. Read the documentation page for `faiss.IndexFlatL2` and
   `faiss.IndexHNSWFlat`. Write one sentence on what you would need to know
   to choose between them. Keep the sentence; compare it to what you write
   after Chapter 33.
:::

:::recap
- The expensive parts of an ML system are usually not the model: they are
  deduplication, sampling, indexing, caching and decoding, all of which are
  data-structure problems.
- The cost difference between a naive and a good choice is routinely
  $10^2$--$10^3$, far beyond what tuning or hardware provides.
- Asymptotic behaviour is invisible at prototype scale and decisive at
  production scale; the crossover gives no warning.
- Four recognisable failure modes: the invisible quadratic, the premature
  index, the right algorithm on the wrong machine, and the unreasoned
  default.
- The skill to build is *recognition*: naming the operation, writing down
  the cost model, and knowing the shape of the solution space.
:::
