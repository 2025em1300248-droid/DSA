# Two Pointers and Sliding Windows
@short: Two Pointers
@subtitle: Turning nested loops into single passes
@tier: core
@prereq: Chapters 9--10
@blurb: A large family of problems that look quadratic are linear if you notice that the two indices you are looping over never need to move backwards. This chapter develops that observation into two reliable techniques, proves why they are linear, and connects them to the batching, chunking and streaming code that sits in front of every model.
@objectives:
- Recognise when two indices can be advanced monotonically instead of restarted
- Write the converging-pointers and sliding-window templates from memory
- Prove the amortised $\Theta(n)$ bound for both
- Combine windows with hash maps, monotonic deques and prefix sums
- Apply the pattern to sequence batching, chunking and streaming metrics
- Know the variants: fixed window, variable window, window with a counter

## The observation

Consider finding two numbers in a *sorted* array that sum to a target. The
naive algorithm tries all pairs: $\Theta(n^2)$. But sortedness means that if
`xs[i] + xs[j]` is too large, *every* `j' > j` is also too large --- so `j`
can move left and never needs to come back.

```python title="Converging pointers: O(n) after sorting"
def two_sum_sorted(xs, target):
    i, j = 0, len(xs) - 1
    while i < j:
        s = xs[i] + xs[j]
        if s == target:
            return i, j
        if s < target:
            i += 1          # only a larger left value can help
        else:
            j -= 1          # only a smaller right value can help
    return None
```

Each iteration advances `i` or retreats `j`, and they meet after at most $n$
steps: $\Theta(n)$. The correctness argument is the important part --- it is an
*exchange* argument. When `s < target`, no pair `(i, j')` with `j' < j` can
work either, because `xs[j'] <= xs[j]`. So discarding `i` loses no solution.

:::insight The general condition
Two-pointer methods work when the problem has a *monotone structure*: moving
one pointer changes the objective in a known direction, so one side of the
search space can be discarded without examining it. Sorting is the usual way
to create that structure, which is another reason Chapter 9 comes first.
:::

This template generalises immediately: three-sum is a loop over the first
element with two-sum inside ($\Theta(n^2)$ instead of $\Theta(n^3)$); merging
two sorted lists is two pointers; the merge step of merge sort is two
pointers; intersecting two sorted posting lists is two pointers; removing
duplicates in place is two pointers where one is a read cursor and the other
a write cursor.

```python title="Read and write cursors: in-place partition"
def remove_duplicates(xs):            # xs sorted; returns new length
    w = 0
    for r in range(len(xs)):
        if w == 0 or xs[r] != xs[w - 1]:
            xs[w] = xs[r]
            w += 1
    return w
```

The read/write cursor pattern is worth internalising: it is how in-place
filtering, stable partitioning and compaction are written, and it is exactly
what a GPU stream-compaction kernel does after a prefix sum (Chapter 39).

## Sliding windows

@fig: sliding_window | 172 | A variable-size window. The right edge advances once per element; the left edge advances only when the window becomes invalid. Both move at most $n$ times in total.

The sliding-window template answers questions of the form "the longest (or
shortest) contiguous subarray satisfying $P$", where $P$ has the property
that shrinking a valid window keeps it valid (or shrinking an invalid one
eventually makes it valid).

```python title="The variable-window template"
def longest_window(xs, is_valid_after_add, remove_left):
    """Generic shape; specialise the two callbacks."""
    left, best = 0, 0
    for right in range(len(xs)):
        add(xs[right])                    # extend the window
        while not valid():                # restore the invariant
            remove_left(xs[left])
            left += 1
        best = max(best, right - left + 1)
    return best
```

```python title="Concrete: longest substring with no repeated character"
def longest_unique(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1           # jump past the previous occurrence
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```

```python title="Concrete: shortest subarray with sum >= target (positive values)"
def shortest_at_least(xs, target):
    left, total, best = 0, 0, float("inf")
    for right, x in enumerate(xs):
        total += x
        while total - xs[left] >= target: # shrink while still valid
            total -= xs[left]
            left += 1
        if total >= target:
            best = min(best, right - left + 1)
    return best if best < float("inf") else 0
```

:::math Why the inner `while` does not make it quadratic
The inner loop looks nested, but `left` only ever increases and is bounded by
$n$. Across the whole run, the inner loop body executes at most $n$ times
*in total*, not $n$ times per outer iteration. Formally: define the potential
$\Phi = \text{right} - \text{left}$; each outer step raises it by 1 and each
inner step lowers it by 1, and $\Phi \ge 0$ always, so the number of inner
steps is at most the number of outer steps. Total: $\Theta(n)$. This is the
accounting method from Chapter 2 in its simplest form.
:::

:::pitfall The window that must not shrink
The template requires that the validity condition be *monotone in the
window*. "Sum $\ge$ target" with **non-negative** values is monotone: removing
an element cannot increase the sum. With negative values present it is not,
and the sliding window is simply wrong --- the answer needs prefix sums plus
a monotonic deque, or a prefix-sum-plus-BIT approach. This is the single most
common incorrect application of the technique, and it passes small tests.
:::

## Windows with a counter

When the condition involves multiplicities --- "contains all characters of
$T$", "at most $k$ distinct values" --- carry a hash map of counts plus a
scalar summarising validity, so that checking validity stays $\Theta(1)$.

```python title="At most k distinct values: window plus counter"
from collections import defaultdict

def longest_at_most_k_distinct(xs, k):
    count, distinct, left, best = defaultdict(int), 0, 0, 0
    for right, x in enumerate(xs):
        if count[x] == 0:
            distinct += 1
        count[x] += 1
        while distinct > k:
            count[xs[left]] -= 1
            if count[xs[left]] == 0:
                distinct -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
```

The scalar `distinct` is the trick: recomputing "how many distinct values are
in the window" from the map would be $\Theta(k)$ per step. Maintaining it
incrementally keeps the whole algorithm $\Theta(n)$. Every efficient window
algorithm has some such incremental summary --- a count, a running sum, a
monotonic deque for the max (Chapter 6), or a heap.

## Fixed windows and streaming statistics

For a fixed window of size $k$, the incremental update is even simpler, and
this is the form that appears in every metrics pipeline.

```python title="Streaming mean and variance over a fixed window"
from collections import deque

class RollingStats:
    """O(1) per update, O(k) memory. Welford-style for stability."""
    def __init__(self, k):
        self.k, self.buf = k, deque(maxlen=k)
        self.s = 0.0        # running sum
        self.s2 = 0.0       # running sum of squares

    def push(self, x):
        if len(self.buf) == self.k:
            old = self.buf[0]
            self.s -= old
            self.s2 -= old * old
        self.buf.append(x)
        self.s += x
        self.s2 += x * x

    def mean(self):
        return self.s / len(self.buf)

    def var(self):
        n = len(self.buf)
        return max(0.0, self.s2 / n - (self.s / n) ** 2)
```

:::warning Catastrophic cancellation in the rolling variance
The `s2/n - mean^2` formula is numerically unstable: if the values are large
and the variance small, you subtract two nearly equal large numbers and lose
most of your significant digits, sometimes producing a negative variance. For
a *streaming* (non-windowed) variance use Welford's algorithm, which is
stable. For a *windowed* variance there is no exactly stable $O(1)$ update;
the practical answer is to recompute from the buffer every few thousand
updates, or to keep the values centred by subtracting a slowly updated
running mean. Chapter 38 treats streaming statistics properly.
:::

:::ml Windows in the ML stack
**Sequence chunking.** Splitting a long document into overlapping windows of
512 tokens with a 64-token stride is a fixed sliding window; the stride is a
recall-versus-cost knob.

**Length bucketing.** Sorting a batch by sequence length and cutting it into
groups whose padding waste stays under a threshold is a variable window over
the sorted lengths --- the greedy window is optimal because length is
monotone after sorting (Chapter 17).

**Sliding-window attention.** Longformer and Mistral-style local attention
restrict each token to attend to the previous $w$ tokens, which turns the
$\Theta(n^2)$ attention matrix into $\Theta(nw)$. The KV cache then becomes a
ring buffer of size $w$ (Chapter 6), with eviction for free.

**Online drift detection.** Comparing a rolling window of recent predictions
to a reference distribution is two windows and a divergence.

**Deduplication by shingles.** A $k$-token shingle is a fixed window, and
hashing it incrementally is the rolling hash of Chapter 5.
:::

## Choosing between the patterns

| Problem shape | Technique | Cost |
|---|---|---|
| Pair with property, sorted input | converging pointers | $\Theta(n)$ after sort |
| Longest/shortest contiguous run with monotone property | variable window | $\Theta(n)$ |
| Statistic over a fixed window | fixed window + incremental update | $\Theta(1)$ per step |
| Max/min over a window | window + monotonic deque | $\Theta(1)$ amortised |
| Sum over an arbitrary range, static array | prefix sums | $\Theta(1)$ per query |
| Sum over an arbitrary range, with updates | Fenwick tree (Chapter 27) | $\Theta(\log n)$ |
| Contiguous subarray with negative values | prefix sums + map or deque | $\Theta(n)$ |
| Non-contiguous subsequence | dynamic programming (Chapter 18) | usually $\Theta(n^2)$ or more |

@tbl: Deciding which linear-scan technique applies. The last row is the important boundary: windows require contiguity, and the moment the problem allows skipping elements you are in dynamic-programming territory.

:::exercise
1. Implement three-sum in $\Theta(n^2)$ using sort plus converging pointers,
   handling duplicates so that each triple is reported once.
2. Prove that `longest_unique` is correct when `left` jumps forward rather
   than shrinking one step at a time. Why is the `last[ch] >= left` guard
   necessary?
3. Give a concrete array with negative numbers on which `shortest_at_least`
   returns the wrong answer, and then write a correct $\Theta(n \log n)$
   version using prefix sums and a monotonic deque.
4. Implement "minimum window substring": the shortest substring of $S$
   containing all characters of $T$ with multiplicity, in $\Theta(|S| + |T|)$.
5. Use a sliding window plus a monotonic deque to compute the rolling maximum
   drawdown of a price series in one pass.
6. Given 100,000 sequences with lengths drawn from a log-normal distribution,
   implement length bucketing that keeps padding waste below 10%, and report
   the number of batches versus naive fixed-size batching.
7. Show that the windowed variance above can return a negative number, and
   fix it two ways: with a periodic recomputation, and by centring.
:::

:::recap
- Two-pointer methods apply when moving a pointer changes the objective
  monotonically, so half the search space can be discarded without
  examination. Sorting is the usual way to create that structure.
- The read/write cursor is the in-place filtering idiom and the sequential
  analogue of GPU stream compaction.
- The sliding window is $\Theta(n)$ because each index enters and leaves the
  window once; the potential-function argument makes this precise.
- The window technique is only correct when validity is monotone in the
  window --- non-negative values for sum conditions, for example.
- Efficient windows keep an incremental summary: a count, a running sum, a
  monotonic deque, or a heap. Recomputing from the window is what makes a
  window algorithm accidentally quadratic.
- Windows require contiguity. Non-contiguous subsequence problems belong to
  dynamic programming.
:::
