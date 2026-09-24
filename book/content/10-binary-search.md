# Binary Search and Searching the Answer Space
@short: Binary Search
@subtitle: The most under-generalised algorithm in the toolkit
@tier: core
@prereq: Chapter 9
@blurb: Everyone can describe binary search and most people cannot write it correctly on the first attempt. Worse, almost everyone under-uses it: binary search over a sorted array is the least interesting of its applications. The important idea is binary search over an *answer space*, which turns a large family of optimisation problems into a few lines of code.
@objectives:
- Write binary search correctly, including the two boundary variants, without off-by-one errors
- Use `bisect` and `np.searchsorted` as they are meant to be used
- Recognise the monotone-predicate pattern and binary search over answers
- Apply binary search to real ML problems: calibration thresholds, batch sizing, quantile lookup
- Understand exponential (galloping) search and interpolation search
- Know when a hash table is the better answer

## The algorithm, written correctly

@fig: binary_search_trace | 150 | Binary search on ten elements. Each probe eliminates half the remaining interval, so the number of probes is $\lceil \log_2 n \rceil$.

The classic version, with the two invariants that make it correct:

```python title="Binary search, half-open interval"
def binary_search(xs, target):
    """Return an index of target, or -1. Invariant: if target is present,
    it lies in xs[lo:hi]."""
    lo, hi = 0, len(xs)                  # half-open: [lo, hi)
    while lo < hi:
        mid = (lo + hi) // 2             # lo <= mid < hi, so it always shrinks
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1                 # target cannot be at mid
        else:
            hi = mid                     # target cannot be at mid
    return -1
```

Three rules prevent every off-by-one error people make here:

1. **Use a half-open interval `[lo, hi)`.** The loop condition is `lo < hi`,
   the answer region is `xs[lo:hi]`, and `hi` starts at `len(xs)`, not
   `len(xs) - 1`. This makes the empty interval `lo == hi` natural rather
   than a special case.
2. **Make sure the interval strictly shrinks.** With `mid = (lo + hi) // 2`
   we have `mid < hi`, so `hi = mid` shrinks. If you use a closed interval
   and write `lo = mid`, you get an infinite loop when `hi == lo + 1`.
3. **Say what each branch rules out.** `xs[mid] < target` means index `mid`
   is definitely not the answer, hence `mid + 1`.

:::note The overflow that lived in production for twenty years
`mid = (lo + hi) // 2` overflows in fixed-width integer languages when
`lo + hi` exceeds the integer range. The bug was in the JDK's
`Arrays.binarySearch` from 1997 until 2006. The fix is
`mid = lo + (hi - lo) // 2`. Python's arbitrary-precision integers make this
a non-issue, but you will meet it the moment you write C++ or Rust.
:::

## The two boundary variants

In practice you almost never want "an index of the target". You want one of
two boundaries, and getting these right removes an entire class of bugs.

```python title="lower_bound and upper_bound"
def lower_bound(xs, t):
    """First index i with xs[i] >= t.  == bisect.bisect_left"""
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < t:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(xs, t):
    """First index i with xs[i] > t.   == bisect.bisect_right"""
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] <= t:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

With these two, everything else is a one-liner:

| Query | Expression |
|---|---|
| Is `t` present? | `lower_bound(xs,t) < len(xs) and xs[lower_bound(xs,t)] == t` |
| Count of `t` | `upper_bound(xs,t) - lower_bound(xs,t)` |
| Number of elements `< t` | `lower_bound(xs, t)` |
| Number in range `[a, b]` | `upper_bound(xs,b) - lower_bound(xs,a)` |
| Insertion point keeping order | `lower_bound(xs, t)` |
| Predecessor of `t` | `lower_bound(xs,t) - 1` |

@tbl: Every ordered query in terms of two primitives. Python's `bisect` module provides both; `np.searchsorted(a, v, side="left"/"right")` provides them vectorised over an entire array of queries at once.

:::perf `np.searchsorted` is the batch version
`np.searchsorted(sorted_keys, query_keys)` performs $m$ binary searches in
one C call: $\Theta(m \log n)$ with no Python overhead. This is the
idiomatic replacement for a large `dict` when keys are numeric (Chapter 7):
1.6 GB instead of 20 GB for 200 million int64 keys, and faster for batched
lookups because it is vectorised and cache-friendly.
:::

## The real idea: binary search over answers

Binary search does not need an array. It needs a **monotone predicate**: a
boolean function $P$ over a range such that once $P$ becomes true it stays
true. Then binary search finds the boundary.

:::definition Binary search on a predicate
Let $P : \{lo, \ldots, hi\} \to \{\text{false}, \text{true}\}$ be monotone:
$P(x) \Rightarrow P(x+1)$. Then the smallest $x$ with $P(x)$ true can be
found in $\Theta(\log(hi - lo))$ evaluations of $P$.
:::

```python title="The template worth memorising"
def first_true(lo, hi, pred):
    """Smallest x in [lo, hi) with pred(x) true; hi if none."""
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

Everything below is an instance of this template. The work is not in the
search; it is in *finding the monotone predicate*.

**Minimum capacity to finish in $D$ days.** Given daily workloads, find the
smallest per-day capacity such that the work fits in $D$ days. `pred(c)` =
"capacity $c$ suffices", which is monotone because more capacity never hurts.
Evaluating `pred` is one $\Theta(n)$ greedy pass, so the whole thing is
$\Theta(n \log(\text{range}))$.

**The square root, or any inverse.** `pred(x)` = "$x^2 \ge v$".

**The $k$-th smallest in a sorted matrix.** `pred(v)` = "at least $k$
elements are $\le v$", counted in $\Theta(n)$ by walking the staircase.

```python title="Binary search over a continuous answer space"
def solve_real(pred, lo, hi, iters=60):
    """Smallest real x in [lo, hi] with pred(x) true."""
    for _ in range(iters):            # 60 halvings ~ 1e-18 relative precision
        mid = (lo + hi) / 2
        if pred(mid):
            hi = mid
        else:
            lo = mid
    return hi
```

For real-valued answers, iterate a fixed number of times rather than testing
for convergence: 60 iterations of bisection reduce the interval by $2^{-60}$,
which is below double-precision resolution. This avoids the infinite loops
that `while hi - lo > eps` produces when `eps` is smaller than the
representable gap.

:::ml Five places you should reach for binary search over answers
**Calibration thresholds.** Find the classification threshold achieving
exactly 95% precision. Precision is monotone in the threshold (up to ties),
so this is `first_true` over the threshold, evaluated on a validation set.
Much more robust than scanning a grid.

**Largest batch size that fits in memory.** Peak memory is monotone in batch
size. Binary search it with a try/except around an actual forward--backward
pass: about 12 probes to find the exact limit between 1 and 4096, instead of
doubling until it crashes and halving once.

**Temperature or top-p for a target entropy.** Entropy is monotone in
temperature; bisect to hit a target.

**Quantiles of a sorted score array.** `np.searchsorted` on the cumulative
distribution.

**Sampling from a discrete distribution.** Build the prefix sums once, then
each sample is `searchsorted(cumsum, u)` for a uniform $u$: $\Theta(\log n)$
per sample, and vectorised over a whole batch. Chapter 34 shows the
$\Theta(1)$ alternative.
:::

## Exponential (galloping) search

When the array is unbounded, or when the target is likely near the start,
first find a bracketing range by doubling, then binary search inside it.

```python title="Exponential search: O(log i) for a target at index i"
def exponential_search(xs, t):
    if not xs:
        return -1
    bound = 1
    while bound < len(xs) and xs[bound] < t:
        bound *= 2                                  # 1, 2, 4, 8, ...
    lo, hi = bound // 2, min(bound + 1, len(xs))
    i = lower_bound(xs[lo:hi], t) + lo
    return i if i < len(xs) and xs[i] == t else -1
```

This is $\Theta(\log i)$ where $i$ is the answer's index, rather than
$\Theta(\log n)$. It matters when $i \ll n$ --- which is exactly the situation
inside Timsort's galloping merge (Chapter 9) and inside inverted-index
intersection, where you repeatedly skip forward in a long posting list to
match a short one.

:::insight Interpolation search, and why it is rarely used
If keys are close to uniformly distributed, guess the position by linear
interpolation instead of taking the midpoint: expected $\Theta(\log \log n)$
probes. That sounds impressive and is almost never worth it. For $n = 10^9$,
$\log_2 n = 30$ and $\log_2 \log_2 n \approx 5$ --- but each probe is a cache
miss either way, the arithmetic per probe is more expensive, and on skewed
data it degrades to $\Theta(n)$. The lesson generalises: below about
$n = 10^{12}$, $\log n$ is already a small number, and constant factors decide.
:::

## When not to binary search

| Situation | Better tool | Why |
|---|---|---|
| Exact-match lookup, many queries | hash table | $\Theta(1)$ beats $\Theta(\log n)$ |
| Data changes frequently | balanced BST / skip list | keeping an array sorted costs $\Theta(n)$ per insert |
| Predicate is not monotone | ternary search (unimodal), or scan | the invariant fails |
| Evaluating the predicate is expensive and noisy | Bayesian optimisation | binary search assumes an exact oracle |
| $n < 64$ | linear scan | branch-free SIMD scan beats branchy binary search |

@tbl: Binary search's competitors. The last row surprises people: for a small sorted array, a vectorised linear scan is faster than binary search because it has no unpredictable branches.

:::pitfall The noisy predicate
Binary searching a threshold on a *validation set* gives you the answer for
that sample, not the population. If the metric is noisy --- and with 500
positive examples it is very noisy --- the located boundary has a confidence
interval far wider than the bisection's precision. Reporting a threshold to
six decimal places because bisection converged is false precision. Bootstrap
the search and report the spread.
:::

:::exercise
1. Write `lower_bound` and `upper_bound` from memory, then test them against
   `bisect` on 10,000 random arrays including empty arrays, all-equal
   arrays, and arrays with the target absent at both ends.
2. Find the smallest positive integer $x$ with $x^3 \ge 10^{18}$ using
   `first_true`, without floating point.
3. Given daily page counts and $D$ days, find the minimum number of pages per
   day to finish. State the predicate and prove it is monotone.
4. Implement "find the $k$-th smallest element of a row-and-column sorted
   $n \times n$ matrix" in $\Theta(n \log(\max - \min))$ by binary searching the
   value.
5. Write a routine that finds the largest batch size fitting in GPU memory by
   binary searching over a function that runs one training step and catches
   out-of-memory. How many probes for a range of 1 to 4096?
6. Replace a 50-million-entry `dict[int, int]` with sorted NumPy arrays and
   `searchsorted`. Measure memory and the time for one lookup and for a
   batch of 10,000 lookups. Explain the difference in the two timings.
7. Implement galloping search and use it to intersect two sorted posting
   lists of lengths 10 and 10,000,000. Compare to a linear merge.
:::

:::recap
- Use half-open intervals `[lo, hi)`, ensure the interval strictly shrinks,
  and state what each branch rules out. These three rules eliminate
  off-by-one errors.
- `lower_bound` and `upper_bound` are the useful primitives; every ordered
  query is a combination of them. `np.searchsorted` is the vectorised form
  and often replaces a large dict.
- The general pattern is binary search over a *monotone predicate*, not over
  an array. Finding the predicate is the creative step; the search is a
  template.
- Real ML uses: calibration thresholds, maximum batch size, temperature for
  target entropy, quantiles, and sampling by inverse CDF.
- Exponential search costs $\Theta(\log i)$ and is what makes Timsort's
  galloping and posting-list skipping fast.
- Prefer a hash table for repeated exact lookups, a balanced tree for
  frequently changing data, and a linear scan below about 64 elements.
- A binary search on a noisy metric converges to more precision than the
  metric deserves.
:::
