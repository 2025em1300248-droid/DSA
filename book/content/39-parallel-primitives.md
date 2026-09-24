# Parallel Primitives: Scan, Reduce, Sort
@short: Parallel Primitives
@subtitle: Six operations from which every parallel algorithm is built
@tier: expert
@prereq: Chapters 16, 39
@blurb: Parallel programming looks like an open-ended discipline and is mostly not: a small set of primitives --- map, reduce, scan, compaction, sort, gather/scatter --- composes into the overwhelming majority of parallel algorithms, and every GPU library implements exactly these. This chapter derives them, analyses them in the work/depth model, and shows where each appears in an ML stack.
@objectives:
- Analyse parallel algorithms with work, depth and Brent's theorem
- Implement parallel reduction and understand tree contraction
- Derive the Blelloch scan and its $\Theta(n)$ work, $\Theta(\log n)$ depth
- Use scan to build compaction, partition, histogram and radix sort
- Recognise these primitives inside dataloaders, tokenizers and attention kernels
- Reason about Amdahl's law and where parallel speedup actually stops

## Work and depth

:::definition Work and depth
The **work** $W$ is the total number of operations, and the **depth** (or
span) $D$ is the length of the longest chain of dependencies --- the time
with unlimited processors. Parallelism is $W/D$.

**Brent's theorem.** With $P$ processors, the running time is at most
$\frac{W}{P} + D$. So an algorithm is efficient if its work matches the best
sequential algorithm (it is *work-efficient*) and its depth is small.
:::

This is the right model because it separates two questions: are you doing
more total work than necessary, and is there a serial bottleneck?

| Primitive | Work | Depth | Example use |
|---|---|---|---|
| Map | $\Theta(n)$ | $\Theta(1)$ | elementwise ops, embedding lookup |
| Reduce | $\Theta(n)$ | $\Theta(\log n)$ | loss sum, norm, softmax denominator |
| Scan (prefix sum) | $\Theta(n)$ | $\Theta(\log n)$ | offsets, compaction, sorting |
| Compaction / filter | $\Theta(n)$ | $\Theta(\log n)$ | sparse masking, candidate pruning |
| Sort (radix) | $\Theta(kn)$ | $\Theta(k \log n)$ | top-k, grouping, MoE routing |
| Gather / scatter | $\Theta(n)$ | $\Theta(1)$ | embedding lookup and its gradient |
| Segmented scan | $\Theta(n)$ | $\Theta(\log n)$ | ragged batches, CSR row sums |

@tbl: The primitive set. Every entry has $\Theta(\log n)$ or better depth, which is why these compose into scalable algorithms.

## Reduction

```python title="Tree reduction: the shape, in one function"
def tree_reduce(xs, op):
    """Work theta(n), depth theta(log n)."""
    cur = list(xs)
    while len(cur) > 1:
        nxt = [op(cur[i], cur[i + 1]) for i in range(0, len(cur) - 1, 2)]
        if len(cur) % 2:
            nxt.append(cur[-1])
        cur = nxt                      # each level runs fully in parallel
    return cur[0]
```

On a GPU this is done within a warp with shuffle instructions (no shared
memory at all), then across warps in shared memory, then across blocks with
atomics or a second kernel. The three-level structure --- warp, block, grid
--- is the standard shape of every reduction kernel you will read.

:::pitfall Floating-point reduction is not associative
$(a + b) + c \ne a + (b + c)$ in floating point, so a tree reduction gives a
different answer from a sequential one, and a *different* answer on a
different number of threads. This is the main source of "why is my loss not
bit-identical across runs?" and why `torch.use_deterministic_algorithms(True)`
makes some kernels slower: it forces a fixed reduction order. Tree reduction
is usually *more* accurate than sequential summation (error grows as
$\log n$ rather than $n$), but it is not reproducible unless the order is
pinned.
:::

## Scan

The prefix sum looks inherently sequential --- each output depends on the one
before it --- and is not.

@fig: parallel_scan | 188 | The Blelloch scan. An up-sweep builds a reduction tree in place; a down-sweep pushes prefixes back down. Both phases are $\Theta(n)$ work and $\Theta(\log n)$ depth.

```python title="Blelloch exclusive scan"
def blelloch_scan(a):
    """Exclusive prefix sum. Work theta(n), depth theta(log n)."""
    n = len(a)
    x = list(a)
    step = 1
    while step < n:                        # up-sweep: build the reduce tree
        for i in range(step * 2 - 1, n, step * 2):     # parallel
            x[i] += x[i - step]
        step *= 2
    total = x[n - 1]
    x[n - 1] = 0                           # clear the root
    step //= 2
    while step >= 1:                       # down-sweep: distribute prefixes
        for i in range(step * 2 - 1, n, step * 2):     # parallel
            left = x[i - step]
            x[i - step] = x[i]
            x[i] += left
        step //= 2
    return x, total
```

The naive parallel scan (Hillis--Steele) is simpler but does
$\Theta(n \log n)$ work --- fine when $n$ is small and processors are idle,
wasteful otherwise. Blelloch is work-efficient, which matters when the scan
is over millions of elements. Real implementations use a *decoupled look-back*
single-pass scan that achieves near-memory-bandwidth throughput.

### What scan gives you

**Stream compaction.** Keep the elements passing a predicate, contiguously.

```python title="Compaction: the canonical scan application"
def compact(xs, keep):
    flags = [1 if k else 0 for k in keep]
    offsets, total = blelloch_scan(flags)       # where each survivor goes
    out = [None] * total
    for i, f in enumerate(flags):               # fully parallel scatter
        if f:
            out[offsets[i]] = xs[i]
    return out
```

**Radix sort.** One pass per digit: compute a histogram of digit values, scan
it to get bucket offsets, scatter. Entirely built from reduce, scan and
scatter --- which is why GPU sorting is radix sorting (Chapter 9).

**Ragged offsets.** Given per-sequence lengths, the scan gives the `offsets`
array of Chapter 4 --- the layout behind nested tensors, CSR graphs and
paged KV caches.

**Segmented scan.** A scan that restarts at segment boundaries, computing
per-sequence cumulative sums in one pass. This is how a batched softmax
denominator, a per-row CSR sum, and a per-sequence cumulative reward are all
computed without a loop over sequences.

:::ml The primitives inside your stack
**`torch.cumsum`** is a scan. **`torch.nonzero`** is compaction (and it is
synchronising, because the output size is data-dependent --- the usual cause
of an unexplained stall in a training loop). **`torch.topk`** is a radix
select. **`scatter_add`** for embedding gradients is a scatter with atomics.
**MoE routing** sorts tokens by expert id (radix sort), scans to find each
expert's offsets, and gathers --- exactly the compaction pattern. The
softmax denominator is a segmented reduction. Recognising them tells you the
cost and where the synchronisation points are.
:::

## Amdahl, Gustafson, and where speedup stops

:::math Amdahl's law
If a fraction $s$ of a program is inherently serial, the speedup with $P$
processors is
$$S(P) = \frac{1}{s + (1-s)/P} \le \frac{1}{s}$$
With $s = 0.05$, the speedup is capped at 20 no matter how many processors
you add. Gustafson's rejoinder is that in practice we scale the *problem*
with the machine, so the serial fraction shrinks --- which is exactly what
happens when you raise the batch size along with the GPU count.
:::

The serial fraction in ML training is rarely arithmetic. It is data loading,
the optimiser step, checkpointing, and the synchronisation barrier at each
all-reduce. Those are what limit scaling, which is why the next chapters are
about moving data rather than doing arithmetic.

:::perf The parallel primitives you should never hand-write
`cub::DeviceScan`, `cub::DeviceRadixSort`, `cub::DeviceReduce`, and their
Thrust and PyTorch wrappers are tuned to within a few percent of memory
bandwidth by people who have measured every variant. A hand-written scan is
typically 3--10x slower. Write your own only to fuse a primitive with
surrounding work so that intermediates never reach memory --- which is the
one thing a library cannot do for you, and exactly what Chapter 40 is about.
:::

:::exercise
1. Compute work, depth and parallelism for: tree reduction, Hillis--Steele
   scan, Blelloch scan, and bitonic sort.
2. Implement both scans and verify their work counts empirically by
   instrumenting the operation count.
3. Implement stream compaction with a scan and compare it to a sequential
   filter for $n = 10^7$.
4. Implement radix sort using only histogram, scan and scatter. Verify it is
   stable.
5. Implement segmented scan and use it to compute per-sequence cumulative
   sums for a ragged batch, without a Python loop.
6. Demonstrate non-associativity: sum $10^7$ float32 values sequentially and
   by tree reduction, and compare both to a float64 reference. Which is more
   accurate?
7. Measure the serial fraction of a small training loop by timing with 1, 2,
   4 and 8 dataloader workers, and fit Amdahl's law.
8. Show that `torch.nonzero` synchronises, by timing a loop with and without
   it under `torch.cuda.synchronize` instrumentation. Propose an alternative
   that keeps a fixed output size.
:::

:::recap
- Work is total operations, depth is the longest dependency chain; Brent's
  theorem gives time $\le W/P + D$.
- Map, reduce, scan, compaction, sort and gather/scatter compose into
  essentially every parallel algorithm, and all have $\Theta(\log n)$ depth
  or better.
- Tree reduction is the shape of every GPU reduction kernel: warp, block,
  grid.
- Floating-point reduction is not associative, so results depend on thread
  count; determinism costs speed.
- The Blelloch scan is work-efficient with logarithmic depth, and scan is the
  building block of compaction, radix sort, ragged offsets and segmented
  aggregation.
- Amdahl's law caps speedup at $1/s$; in ML the serial fraction is usually
  data loading and synchronisation, not arithmetic.
- Use the library primitives; write your own only to fuse them with
  neighbouring work.
:::
