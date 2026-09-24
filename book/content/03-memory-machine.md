# Memory, Cache and the Machine You Actually Run On
@short: Memory and Cache
@subtitle: Why two algorithms with identical operation counts differ tenfold
@tier: foundation
@prereq: Chapter 2
@blurb: Asymptotic analysis assumes every memory access costs the same. On real hardware that assumption is wrong by a factor of three hundred, and it has been wrong since about 1990. This chapter replaces the flat-memory fiction with an accurate mental model, and shows why it is the single most useful piece of systems knowledge an ML engineer can acquire.
@objectives:
- Explain the memory hierarchy and quote the latency of each level from memory
- Predict which of two loops with identical complexity will be faster, and why
- Use the three principles --- locality, contiguity, predictability --- as design constraints
- Choose between array-of-structs and struct-of-arrays for a given access pattern
- Understand why linked structures underperform their asymptotics so badly
- Reason about arithmetic intensity and the roofline model

## The lie in the RAM model

Chapter 2 counted operations as if each one costs the same. That model ---
called the *RAM model* --- was accurate in 1975, when a memory access and an
addition both took roughly one cycle. Since then processors have got about
50,000 times faster and main memory has got about 10 times faster in
*latency*. The gap is now enormous and it defines modern performance work.

@fig: memory_pyramid | 155 | The memory hierarchy on a 2026 server CPU, with honest numbers. Each level is roughly 4--8x slower and 10--50x larger than the one above it. The jump from L3 to DRAM is the cliff most code falls off.

Read the figure again and fix one number in your head: **a main-memory
access costs about 300 cycles**, during which the core could have performed
around 300 additions or, with vector instructions, several thousand. Your
program spends most of its life waiting for data, not computing.

:::insight The real cost model
Cost is not "operations performed". Cost is
$\max(\text{operations} / \text{throughput},\ \text{bytes moved} / \text{bandwidth})$,
and for most code that touches more data than fits in cache, the second term
wins. Algorithms should therefore be designed to minimise *data movement*,
not just operation count.
:::

## Cache lines: the unit that actually moves

Memory does not move a byte at a time. It moves a **cache line**, typically
64 bytes (16 float32 values, 8 float64 values, or 8 pointers on a 64-bit
machine). When you read `x[0]`, the hardware fetches the entire 64-byte line
containing it and places it in L1.

@fig: cache_line | 140 | Top: a sequential scan pays one miss and then gets fifteen free hits. Bottom: four random accesses into different lines pay four full misses.

This single mechanism explains the majority of performance differences
between data structures:

- **Sequential access is nearly free after the first element.** Scanning an
  array of a million floats costs about $10^6/16 = 62{,}500$ misses, not
  $10^6$.
- **The hardware prefetcher makes it better still.** Modern CPUs detect a
  constant stride and fetch lines ahead of the loop, hiding the latency
  almost entirely. A predictable sequential scan can run at full memory
  bandwidth --- tens of gigabytes per second.
- **Random access defeats both.** Every touch is a miss, and the prefetcher
  cannot help because there is no pattern to detect.

```python title="Same work, different order"
import numpy as np, time

n = 8192
A = np.zeros((n, n), dtype=np.float32)

def by_rows(A):                 # stride 4 bytes: perfectly sequential
    s = 0.0
    for r in range(A.shape[0]):
        s += A[r, :].sum()
    return s

def by_cols(A):                 # stride 32 KB: a new cache line every touch
    s = 0.0
    for c in range(A.shape[1]):
        s += A[:, c].sum()
    return s
```

Both functions touch exactly $n^2$ elements and perform exactly $n^2$
additions. On a typical machine `by_rows` is five to ten times faster. The
operation count did not change; the number of cache lines touched changed by
a factor of sixteen.

@fig: row_col_access | 135 | The first twelve memory touches of each loop over a row-major matrix. Row order stays inside one or two cache lines; column order pulls a new line for every single element.

:::pitfall The transposed matrix trap
NumPy's `A.T` is a *view* with reversed strides, not a copy --- it is free.
But every subsequent operation on that view now runs with the bad access
pattern. If you are going to touch a transposed array more than once, call
`np.ascontiguousarray(A.T)` and pay the copy up front. Chapter 4 makes the
stride mechanics explicit.
:::

## Three principles

Everything in this chapter reduces to three properties, and every fast data
structure has at least two of them.

**Temporal locality.** If you touch a datum, touch it again soon. Caches
keep recently used lines; reuse is free. This is why blocked (tiled) matrix
multiplication is faster than the naive triple loop even though it performs
the same multiplications: it arranges for each loaded tile to be used
$b$ times before eviction.

**Spatial locality.** If you touch a datum, touch its neighbour next. This
is contiguity, and it is why arrays beat linked lists and why struct-of-arrays
beats array-of-structs for column-wise work.

**Predictability.** If your access pattern is a constant stride, the
prefetcher will hide the latency. Random access, pointer chasing and
data-dependent branches all destroy predictability. A branch mispredict
costs 15--20 cycles; a data-dependent load chain costs the full latency
every time because nothing can be overlapped.

:::hardware Why `sorted` data is faster to filter
Branch prediction is a real, measurable effect. A loop that sums values
above a threshold runs roughly 3x faster on sorted input than on shuffled
input --- identical work, identical memory pattern, but on sorted data the
branch is taken in one long run and then not taken in another, which the
predictor gets right almost every time. On shuffled data it is a coin flip
and the pipeline stalls constantly.
:::

## Why linked lists lose

The classic analysis says: array insertion in the middle is $\Theta(n)$
because you must shift elements; linked-list insertion is $\Theta(1)$ because
you just rewire two pointers. Therefore linked lists win for
insertion-heavy workloads.

In practice, for anything below roughly a hundred thousand elements, the
array wins --- often by an order of magnitude --- even for insertion-heavy
workloads. Here is why.

@fig: pointer_chase | 150 | A four-node linked list. Logically it is a straight line; physically the nodes are wherever the allocator put them, and traversing it is four dependent cache misses in a row.

1. **Every node is a separate allocation.** After a few thousand
   insertions and deletions the nodes are scattered across the heap, so
   traversal is pointer chasing: each `node.next` is a cache miss, and worse,
   the misses are *serially dependent* --- you cannot start fetching node 3
   until node 2 has arrived. No parallelism, no prefetching.
2. **Memory overhead is brutal.** A Python list of a million ints stores a
   million pointers plus the objects. A linked list adds a node object per
   element: in CPython that is roughly 56 bytes of object header and
   pointers *per element* before the payload.
3. **Shifting is vectorised.** Moving $n$ contiguous bytes in an array is a
   `memmove`, which runs at tens of gigabytes per second. Shifting ten
   thousand 8-byte elements moves 80 KB --- about 3 microseconds. One cache
   miss is 0.09 microseconds, so the array's "expensive" $\Theta(n)$ shift is
   worth about 33 pointer dereferences.

:::insight When linked structures do earn their keep
Not never --- just less often than the textbook implies. They win when:
nodes are large (so the pointer overhead is proportionally small); you hold
long-lived references *into* the middle and need stable addresses; you need
$O(1)$ splice of entire sublists; or the structure is intrusive and
allocation-free, as in a kernel scheduler's run queue or an LRU cache's
recency list (Chapter 6).
:::

## Array of structs versus struct of arrays

This is the most actionable layout decision in data-intensive code, and it
appears constantly in ML pipelines.

@fig: aos_soa | 140 | The same five-field records in two layouts. If your loop reads one field across many records, struct-of-arrays moves five times fewer bytes.

Suppose you have ten million records, each with an id, three coordinates and
a weight. If your hot loop computes the mean of `x`:

- **Array of structs** (`[{id, x, y, z, w}, ...]`, or a list of objects, or
  a pandas row-oriented view) loads every field of every record because they
  share cache lines. You move 200 MB to read 40 MB of useful data.
- **Struct of arrays** (`{id: [...], x: [...], ...}`, which is exactly what a
  NumPy structured layout, a pandas DataFrame column, or an Arrow record
  batch gives you) loads only the `x` array. You move 40 MB, and the loop
  vectorises.

:::ml This is why the whole ML data stack is columnar
Parquet, Arrow, pandas, Polars, and every feature store you will meet are
column-oriented for exactly this reason. It is also why a `Dataset` that
returns Python dicts of scalars is slow and one that returns batched NumPy
arrays is fast: the first is array-of-structs with an interpreter on top.
Embedding tables are the same story --- they are stored as one contiguous
$V \times d$ matrix, and a lookup is a contiguous $d$-element read.
:::

## Measuring it yourself

Do not take any of this on faith. The following measures your machine's
actual cliff, and takes about ten seconds.

```python title="Find your cache sizes empirically"
import numpy as np, time

def bench(size_kb, steps=4_000_000):
    n = size_kb * 1024 // 4                      # float32 elements
    a = np.random.rand(n).astype(np.float32)
    idx = np.random.randint(0, n, size=1 << 20)  # random, defeats prefetch
    t0 = time.perf_counter()
    for _ in range(steps // (1 << 20)):
        a[idx].sum()
    return (time.perf_counter() - t0) / steps * 1e9   # ns per access

for kb in [16, 64, 256, 1024, 4096, 16384, 65536]:
    print(f"{kb:>6} KB  {bench(kb):6.2f} ns/access")
```

You will see a roughly flat region, then a step, then another step. The
steps are your L1, L2 and L3 boundaries. Knowing where your L2 ends turns
"make the batch smaller" from folklore into arithmetic.

:::perf Tiling, in one paragraph
If a loop touches a working set larger than a cache level, restructure it to
work on blocks that fit. Naive $n \times n$ matrix multiply reads $\Theta(n^3)$
words from memory; blocked multiply with block size $b$ reads
$\Theta(n^3 / b + n^2)$, and choosing $b$ so that three $b \times b$ tiles fit
in L2 reduces traffic by a factor of $b$ --- typically 30--60x. This is the
same idea that makes FlashAttention fast (Chapter 40), and it is a
*restructuring*, not a different algorithm.
:::

## Arithmetic intensity and the roofline

To decide whether an optimisation can possibly help, compute the arithmetic
intensity: FLOPs performed per byte moved from memory.

| Operation | FLOPs | Bytes moved | Intensity | Verdict |
|---|---:|---:|---:|---|
| Vector add `c = a + b` ($n$ fp32) | $n$ | $12n$ | 0.08 | memory-bound |
| `softmax` over $n$ | $\approx 5n$ | $8n$ | 0.6 | memory-bound |
| Matrix--vector $n \times n$ | $2n^2$ | $4n^2$ | 0.5 | memory-bound |
| Matrix--matrix $n \times n$ | $2n^3$ | $12n^2$ | $n/6$ | compute-bound for large $n$ |
| Attention, decode (batch 1) | $\approx 4nd$ | $\approx 4nd$ | 1 | memory-bound |
| Attention, prefill | $\approx 4n^2d$ | $\approx 8nd$ | $n/2$ | compute-bound |

@tbl: Arithmetic intensity of common kernels. A modern accelerator needs an intensity above roughly 100 to reach peak FLOPs; below that, performance is set by bandwidth alone.

The practical consequence is blunt and worth stating as a rule: **for a
memory-bound kernel, reducing the operation count does nothing.** You must
reduce the bytes moved --- by fusing operations so intermediates never leave
registers, by using a smaller dtype, or by restructuring to reuse loaded
data. This is why `torch.compile` and Triton kernels chase *fusion* rather
than arithmetic, and why quantising a model from fp16 to int8 roughly
doubles decode throughput even though the arithmetic is the same shape.

:::ml Token generation is a bandwidth problem
Generating one token from a 7-billion-parameter model in fp16 requires
reading all 14 GB of weights from HBM, and performing about 14 GFLOPs. On a
device with 2 TB/s of bandwidth and 500 TFLOP/s of compute, the read takes
7 ms and the arithmetic takes 0.03 ms. Decoding is 200x memory-bound. Every
serving trick you have heard of --- batching, speculative decoding,
quantisation, paged KV caches --- exists to improve that ratio. Chapters 35
and 36.
:::

## A checklist you can apply today

:::checklist Before optimising anything that touches data
1. Is the working set larger than L2? If not, stop --- memory is not your
   problem and you should count operations after all.
2. Is the access pattern sequential? If not, can it be made sequential by
   sorting, by reordering the loop, or by changing the layout?
3. Are you moving fields you do not use? Switch to columnar, or use a
   narrower dtype.
4. Is the kernel memory-bound? Compute the intensity before you optimise
   arithmetic.
5. Are you allocating per item? Per-element allocation is the hidden cost in
   most slow Python data pipelines.
6. Only now: is there an asymptotically better algorithm?
:::

:::exercise
1. Predict, then measure, the ratio between summing a $4096 \times 4096$
   float32 NumPy array along axis 0 versus axis 1. Explain the direction of
   the difference in terms of strides.
2. A structure holds 50 million records of 40 bytes each. Your query reads
   one 4-byte field of each. How many bytes does an array-of-structs layout
   move? How many does struct-of-arrays? At 50 GB/s, how long does each take?
3. Implement a singly linked list and a Python list, and time (a) appending
   a million elements, (b) iterating and summing, (c) inserting at position
   0 a hundred thousand times. Explain each result using this chapter.
4. Compute the arithmetic intensity of a batched matrix multiply with
   $M = N = 4096$, $K = 4096$, in fp16. Is it compute-bound on a device with
   1.5 TB/s bandwidth and 400 TFLOP/s of fp16 throughput? What if $M = 1$?
5. A colleague proposes replacing a `dict` lookup in a hot loop with a
   sorted array plus binary search, arguing that the array is contiguous.
   For one million int keys, which is faster and why? Does your answer change
   at one billion keys?
6. Explain why, in a batched inference server, doubling the batch size often
   increases throughput almost twofold while barely changing latency per
   request. Frame your answer entirely in terms of arithmetic intensity.
:::

:::recap
- The flat-memory RAM model is wrong: DRAM latency is roughly 300 cycles, so
  most programs are waiting, not computing.
- Memory moves in 64-byte cache lines. Sequential access amortises a miss
  over sixteen float32 values; random access does not.
- The three properties that make code fast are temporal locality, spatial
  locality and predictability. Design for them explicitly.
- Linked structures lose to arrays at practical sizes because traversal is a
  chain of dependent cache misses and every node carries allocation overhead.
- Struct-of-arrays moves only the fields you read; this is the reason the
  entire modern data stack is columnar.
- Compute arithmetic intensity before optimising. For memory-bound kernels,
  only reducing bytes moved helps --- which is what fusion, tiling and
  quantisation all do.
:::
