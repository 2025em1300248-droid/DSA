# Sorting and Order Statistics
@short: Sorting
@subtitle: The most-studied problem in computing, and what it buys you
@tier: core
@prereq: Chapters 2, 8
@blurb: You will rarely implement a sort. You will constantly decide whether to sort, what to sort by, and whether you need a full ordering at all --- and those decisions are worth far more than the implementation. This chapter covers the algorithms because their ideas recur everywhere, then spends equal time on the questions you actually face: stability, keys, partial sorts, and the linear-time alternatives.
@objectives:
- Explain why comparison sorting cannot beat $\Omega(n \log n)$, and how counting and radix sorts escape it
- Implement merge sort, quicksort and heapsort, and say when each is right
- Understand stability and why it matters for multi-key ranking
- Use quickselect and partial sorting to avoid a full sort
- Know what Timsort and `np.argsort` actually do
- Recognise sorting as a preprocessing step that enables other algorithms

## Sorting is preprocessing

Sorting is rarely the answer to a question; it is what makes the answer
cheap. Once data is sorted you can binary search it ($\Theta(\log n)$),
find duplicates in one pass, compute rank statistics by indexing, merge two
datasets in linear time, group by key without a hash table, and turn a
range query into two binary searches. Most of Part II is unlocked by
sorting.

:::insight The decision, in one line
Sorting costs $\Theta(n \log n)$ once and makes many later operations
$\Theta(\log n)$ instead of $\Theta(n)$. So sort when you will query more than
about $\log n$ times, and do not sort for a single query --- scan it.
:::

## The comparison lower bound

:::theorem Comparison sorting requires $\Omega(n \log n)$ comparisons
Any algorithm that sorts by comparing pairs of elements must, in the worst
case, perform at least $\log_2(n!) = \Omega(n \log n)$ comparisons.
:::

:::proof
A comparison sort's execution is a path down a binary decision tree: each
internal node is a comparison with two outcomes, each leaf is a permutation
the algorithm can output. To sort correctly the tree must have at least $n!$
leaves, one per possible input permutation. A binary tree with $L$ leaves has
height at least $\log_2 L$. Hence the worst-case number of comparisons is at
least $\log_2(n!)$, which by Stirling's approximation is
$n \log_2 n - n \log_2 e + \Theta(\log n) = \Omega(n \log n)$.
:::

The argument is information-theoretic: there are $n!$ possible answers, each
comparison yields one bit, so you need $\log_2 n!$ bits. It applies to *any*
comparison-based method, including ones nobody has invented yet. It does not
apply to methods that look at the *structure* of the keys --- which is the
loophole counting sort and radix sort walk through.

## The three classical algorithms

@fig: merge_sort | 185 | Merge sort. The recursion splits until every piece has one element, then merges upward. There are $\log n$ levels and each level does $\Theta(n)$ work.

```python title="Merge sort: stable, predictable, O(n) extra space"
def merge_sort(xs):
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    left, right = merge_sort(xs[:mid]), merge_sort(xs[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if right[j] < left[i]:        # '<' not '<=' keeps it STABLE
            out.append(right[j]); j += 1
        else:
            out.append(left[i]); i += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out
```

The single character in the comparison is the difference between a stable
and an unstable sort. With `<`, a tie keeps the left (earlier) element first.

```python title="Quicksort with Lomuto partition and a random pivot"
import random

def quicksort(xs, lo=0, hi=None):
    hi = len(xs) - 1 if hi is None else hi
    while lo < hi:
        k = random.randint(lo, hi)              # randomise: defeats adversaries
        xs[k], xs[hi] = xs[hi], xs[k]
        pivot, i = xs[hi], lo
        for j in range(lo, hi):
            if xs[j] < pivot:
                xs[i], xs[j] = xs[j], xs[i]
                i += 1
        xs[i], xs[hi] = xs[hi], xs[i]
        if i - lo < hi - i:                     # recurse on the smaller side,
            quicksort(xs, lo, i - 1)            # loop on the larger: O(log n)
            lo = i + 1                          # stack depth guaranteed
        else:
            quicksort(xs, i + 1, hi)
            hi = i - 1
    return xs
```

Quicksort is the fastest comparison sort in practice --- it sorts in place,
its inner loop is a sequential scan, and it has excellent cache behaviour ---
but its worst case is $\Theta(n^2)$ and that worst case is *reachable by an
adversary* if the pivot rule is deterministic. Randomising the pivot makes
the expected time $\Theta(n \log n)$ regardless of input. Production
implementations go further: `introsort` (C++ `std::sort`) counts its
recursion depth and switches to heapsort beyond $2 \log n$, giving a hard
$\Theta(n \log n)$ worst case while keeping quicksort's constants.

Heapsort, built on the binary heap of Chapter 13, sorts in place with a
guaranteed $\Theta(n \log n)$ worst case but poor locality --- it jumps around
the array by powers of two --- which is why it loses to quicksort by a
factor of two or three despite identical asymptotics. A clean illustration of
Chapter 3's thesis.

@fig: sort_landscape | 150 | The sorting landscape. The rightmost column is the one that decides real choices; the complexity columns rarely do.

## Stability, and why ranking depends on it

A sort is **stable** if elements comparing equal keep their original relative
order. This sounds like a technicality until you sort by multiple keys.

```python title="Multi-key ranking via stable sorts"
docs = [...]                                  # (score, recency, source)
# Sort by the LEAST significant key first, then the most significant.
docs.sort(key=lambda d: d.recency, reverse=True)
docs.sort(key=lambda d: d.score, reverse=True)
# Now: ordered by score, and within equal scores, by recency.
```

This works only because `list.sort` is stable. The same idea is the entire
mechanism of LSD radix sort, and it is how a search ranker applies tie-break
rules without constructing a composite key. NumPy's default
`np.argsort(kind="quicksort")` is **not** stable; pass `kind="stable"` when
ties matter --- a silent source of nondeterminism between runs and between
CPU and GPU implementations.

:::pitfall Nondeterministic ranking
Two models with identical scores can produce different top-10 lists on
different machines if the sort is unstable, because ties break by whatever
order the partition happened to produce. In evaluation this shows up as
metrics that shift by 0.1% for no reason. Fix: always sort by an explicit
total order --- append a deterministic tiebreaker such as the document id.
:::

## Escaping the lower bound

When keys are small integers, you can sort without comparing.

```python title="Counting sort: O(n + k), stable"
def counting_sort(xs, k):                 # keys in [0, k)
    count = [0] * k
    for x in xs:
        count[x] += 1
    pos, total = [0] * k, 0
    for v in range(k):                    # prefix sums give output positions
        pos[v], total = total, total + count[v]
    out = [0] * len(xs)
    for x in xs:                          # forward pass preserves stability
        out[pos[x]] = x
        pos[x] += 1
    return out
```

Counting sort is $\Theta(n + k)$ time and $\Theta(k)$ space, so it wins when
$k = O(n)$ and is useless when $k$ is large. Radix sort applies counting sort
to one digit at a time, least significant first, relying on stability to
preserve the work of earlier passes: $\Theta(d(n + b))$ for $d$ digits in
base $b$. For 32-bit integers with $b = 2^{16}$, that is two passes --- which
is why radix sort is the standard sort on GPUs and in columnar databases.

:::ml Where non-comparison sorts show up
GPU sorting is almost always radix sorting: it is branch-free, its memory
access is a sequence of scatters that can be made coalesced, and it
parallelises through prefix sums (Chapter 39). CUB's `DeviceRadixSort`, the
sort inside a top-k kernel, and the bucketing step in sparse attention all
use it. Counting sort appears whenever you bucket by a small categorical:
sorting a batch by sequence length before padding, grouping tokens by expert
in a mixture-of-experts layer, or histogram binning in gradient-boosted trees
(Chapter 37).
:::

## When you do not need a full sort

This is the practically important section. A full sort gives you a total
order; most questions need far less.

| Question | Full sort | Better | Gain at $n=10^7, k=100$ |
|---|---|---|---|
| The $k$ largest | $\Theta(n \log n)$ | heap: $\Theta(n \log k)$ | $\approx 3\times$ |
| The $k$ largest, in memory | $\Theta(n \log n)$ | `argpartition`: $\Theta(n)$ | $\approx 25\times$ |
| The median | $\Theta(n \log n)$ | quickselect: $\Theta(n)$ expected | $\approx 20\times$ |
| The $p$-th percentile | $\Theta(n \log n)$ | quickselect or t-digest | $\approx 20\times$ |
| Any duplicates? | $\Theta(n \log n)$ | hash set: $\Theta(n)$ | $\approx 15\times$ |
| Top $k$ from a stream | impossible | bounded heap: $\Theta(n \log k)$, $\Theta(k)$ space | --- |

@tbl: Sorting is often a needlessly strong answer. The right question is "what is the weakest ordering that answers my query?"

```python title="Quickselect: the k-th smallest in expected linear time"
import random

def quickselect(xs, k):                 # 0-indexed: k=0 is the minimum
    lo, hi = 0, len(xs) - 1
    while True:
        if lo == hi:
            return xs[lo]
        p = random.randint(lo, hi)
        xs[p], xs[hi] = xs[hi], xs[p]
        pivot, i = xs[hi], lo
        for j in range(lo, hi):
            if xs[j] < pivot:
                xs[i], xs[j] = xs[j], xs[i]
                i += 1
        xs[i], xs[hi] = xs[hi], xs[i]
        if k == i:
            return xs[i]
        elif k < i:
            hi = i - 1                  # recurse into ONE side only
        else:
            lo = i + 1
```

The analysis is the geometric-series argument: each partition is expected to
discard a constant fraction, so the expected work is
$n + n/2 + n/4 + \cdots = \Theta(n)$. Only one side is explored, which is the
whole difference from quicksort. The median-of-medians variant achieves
$\Theta(n)$ in the *worst* case, at a constant factor that makes it slower in
practice --- a classic case of a theoretically superior algorithm nobody uses.

## Timsort, and what your language actually runs

Python's `list.sort` and `sorted` use Timsort, and so does Java's
`Arrays.sort` for objects and Android's runtime. It is worth knowing what it
does because it explains some surprising timings.

1. **Find natural runs.** Scan for maximal ascending or descending stretches;
   reverse the descending ones in place. Real data is full of runs --- log
   files, time series, partially updated indexes --- and Timsort's best case
   on such data is $\Theta(n)$.
2. **Extend short runs** to a minimum length (32--64) with binary insertion
   sort, which is fast and cache-friendly at that size.
3. **Merge runs** with a stack, maintaining invariants that keep merges
   balanced, plus *galloping mode*: when one run is consistently winning,
   switch to exponential search to skip ahead in $\Theta(\log n)$ instead of
   one element at a time.

The result is $\Theta(n)$ on nearly sorted data, $\Theta(n \log n)$ worst case,
stable, and adaptive. `np.sort` by contrast defaults to an introsort variant
which is faster on random numeric data but unstable and not adaptive.

:::perf The `key=` function dominates
`sorted(items, key=f)` calls `f` exactly once per element (the
decorate--sort--undecorate pattern, built in). But `f` is a Python function
call, roughly 100 ns, so sorting a million items with a lambda spends 0.1 s
in the key function and perhaps 0.5 s in comparisons. Sorting with
`key=operator.itemgetter(1)` instead of `key=lambda t: t[1]` is measurably
faster because it is C. Sorting NumPy data with a Python key is a
catastrophe --- use `np.argsort` on the key array and then a fancy index.
:::

```python title="The NumPy idiom for sorting records by a key"
import numpy as np
scores = np.random.rand(10_000_000).astype(np.float32)
ids = np.arange(10_000_000)

order = np.argsort(-scores, kind="stable")    # theta(n log n), all in C
top_ids = ids[order[:100]]                    # one gather

# Better still when you only need 100 of ten million:
part = np.argpartition(-scores, 100)[:100]    # theta(n)
top_ids = ids[part[np.argsort(-scores[part])]]
```

:::exercise
1. Prove that any stable sort can be simulated by an unstable sort at the
   cost of $\Theta(n)$ extra space. (Hint: augment each key with its index.)
2. Implement bottom-up (iterative) merge sort with no recursion, and
   external merge sort that sorts a file larger than memory using $k$-way
   merging with a heap.
3. Construct an input on which a median-of-three quicksort is $\Theta(n^2)$.
   Explain why randomisation prevents this and why "shuffle then sort" is
   equivalent.
4. Implement LSD radix sort for 32-bit unsigned integers with base $2^8$ and
   compare it to `sorted()` at $n = 10^6$ and $n = 10^8$. Then extend it to
   signed integers and to IEEE-754 floats. (Hint: for floats, flip the sign
   bit; for negatives, flip all bits.)
5. Measure Timsort's adaptivity: sort an array that is 0%, 1%, 10% and 100%
   shuffled and plot the time.
6. You have 500 GB of `(user_id, timestamp, event)` records on disk and 32 GB
   of RAM, and you need them ordered by `(user_id, timestamp)`. Design the
   sort. How many passes over the data does it need?
7. A reranker scores 50,000 candidates and needs the top 50. Compare a full
   `argsort`, a `heapq.nlargest`, and an `argpartition` in time and in peak
   memory. Which would you choose for a p99 latency budget, and why might
   the answer differ from the mean-latency answer?
:::

:::recap
- Sorting is preprocessing: it costs $\Theta(n \log n)$ once and makes later
  queries logarithmic. Sort when you will query more than $\log n$ times.
- Comparison sorting needs $\Omega(n \log n)$ comparisons by an
  information-theoretic argument; counting and radix sorts escape it by
  inspecting key structure rather than comparing.
- Merge sort is stable and predictable; quicksort is fastest in practice but
  needs a random pivot; heapsort has the best worst case and the worst
  locality. Introsort combines them.
- Stability is what makes multi-key sorting work, and instability is a
  common source of nondeterministic rankings. Add an explicit tiebreaker.
- Most questions need less than a total order: use quickselect,
  `argpartition`, or a bounded heap. The gains are 3--25x, not percentages.
- Timsort exploits natural runs and galloping, giving $\Theta(n)$ on nearly
  sorted data. NumPy's default sort is faster but unstable.
- In NumPy, sort the key array with `argsort` and gather; never pass a Python
  `key=` over array data.
:::
