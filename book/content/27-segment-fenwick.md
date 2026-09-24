# Segment Trees and Fenwick Trees
@short: Segment and Fenwick Trees
@subtitle: Range queries on data that keeps changing
@tier: advanced
@prereq: Chapters 12, 13
@blurb: A prefix-sum array answers range queries in constant time and forbids updates. A plain array allows updates and forces linear queries. Segment trees and Fenwick trees give you both in logarithmic time, and they are the structure behind weighted sampling with changing weights --- which is exactly what prioritized experience replay needs.
@objectives:
- Build a segment tree and implement range query and point update
- Implement a Fenwick tree and explain the lowest-set-bit arithmetic
- Choose between prefix sums, Fenwick trees and segment trees
- Add lazy propagation for range updates
- Implement $\Theta(\log n)$ weighted sampling with dynamic weights
- Build a prioritized replay buffer and understand its importance-sampling correction

## The three-way tradeoff

| Structure | Build | Range query | Point update | Range update | Memory |
|---|---|---|---|---|---|
| Plain array | $\Theta(n)$ | $\Theta(n)$ | $\Theta(1)$ | $\Theta(n)$ | $n$ |
| Prefix sums | $\Theta(n)$ | $\Theta(1)$ | $\Theta(n)$ | $\Theta(n)$ | $n$ |
| Fenwick tree | $\Theta(n)$ | $\Theta(\log n)$ | $\Theta(\log n)$ | $\Theta(\log n)$* | $n$ |
| Segment tree | $\Theta(n)$ | $\Theta(\log n)$ | $\Theta(\log n)$ | $\Theta(\log n)$† | $2n$--$4n$ |
| Sqrt decomposition | $\Theta(n)$ | $\Theta(\sqrt n)$ | $\Theta(1)$ | $\Theta(\sqrt n)$ | $n + \sqrt n$ |

@tbl: \*with a second tree, for range-add point-query. †with lazy propagation. If your data never changes, use prefix sums; if it changes constantly, use one of the trees.

## Segment trees

@fig: segment_tree | 155 | A segment tree. Each node stores the aggregate of a contiguous range; a query decomposes into $O(\log n)$ maximal nodes that tile it exactly.

```python title="Iterative segment tree: sum query, point update"
class SegTree:
    def __init__(self, data, op=lambda a, b: a + b, identity=0):
        self.n = len(data)
        self.op, self.id = op, identity
        self.t = [identity] * (2 * self.n)
        self.t[self.n:] = data
        for i in range(self.n - 1, 0, -1):            # build bottom-up
            self.t[i] = op(self.t[2 * i], self.t[2 * i + 1])

    def update(self, i, value):                       # theta(log n)
        i += self.n
        self.t[i] = value
        while i > 1:
            i >>= 1
            self.t[i] = self.op(self.t[2 * i], self.t[2 * i + 1])

    def query(self, lo, hi):                          # [lo, hi), theta(log n)
        res_l, res_r = self.id, self.id
        lo += self.n; hi += self.n
        while lo < hi:
            if lo & 1:
                res_l = self.op(res_l, self.t[lo]); lo += 1
            if hi & 1:
                hi -= 1; res_r = self.op(self.t[hi], res_r)
            lo >>= 1; hi >>= 1
        return self.op(res_l, res_r)
```

The iterative bottom-up form is shorter and roughly twice as fast as the
recursive one, and it has a nice property: it works for *any associative*
operation. Pass `min`, `max`, `gcd`, matrix multiplication, or "the maximum
subarray sum of this range" (a four-field struct) and the structure is
unchanged.

:::insight The requirement is associativity, not commutativity
Note that `query` keeps two accumulators, one from the left and one from the
right, and combines them at the end. That is what makes the structure work
for non-commutative operations such as matrix products and function
composition. Get this wrong and it silently works for sums and fails for
everything else.
:::

### Lazy propagation

To support *range* updates ("add 5 to every element in $[l, r)$") without
touching every leaf, store a pending update at each node and push it down
only when a query needs to descend past it.

```python title="Lazy propagation: range add, range sum"
class LazySeg:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def _push(self, node, lo, hi):
        if self.lazy[node]:
            self.t[node] += self.lazy[node] * (hi - lo)
            if hi - lo > 1:                   # not a leaf: defer to children
                self.lazy[2 * node + 1] += self.lazy[node]
                self.lazy[2 * node + 2] += self.lazy[node]
            self.lazy[node] = 0

    def update(self, l, r, val, node=0, lo=0, hi=None):
        hi = self.n if hi is None else hi
        self._push(node, lo, hi)
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self.lazy[node] += val
            self._push(node, lo, hi)
            return
        mid = (lo + hi) // 2
        self.update(l, r, val, 2 * node + 1, lo, mid)
        self.update(l, r, val, 2 * node + 2, mid, hi)
        self.t[node] = self.t[2 * node + 1] + self.t[2 * node + 2]

    def query(self, l, r, node=0, lo=0, hi=None):
        hi = self.n if hi is None else hi
        self._push(node, lo, hi)
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.t[node]
        mid = (lo + hi) // 2
        return (self.query(l, r, 2 * node + 1, lo, mid)
                + self.query(l, r, 2 * node + 2, mid, hi))
```

## Fenwick trees

A Fenwick tree (binary indexed tree) does less than a segment tree --- prefix
aggregates under an invertible operation --- in half the memory and with a
much smaller constant.

@fig: fenwick | 138 | The Fenwick tree's coverage pattern. `tree[i]` stores the aggregate of the range of length `i & -i` ending at `i`, so both query and update walk $O(\log n)$ indices by adding or removing the lowest set bit.

```python title="Fenwick tree, complete"
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0.0] * (n + 1)              # 1-indexed

    def update(self, i, delta):               # theta(log n)
        i += 1
        while i <= self.n:
            self.t[i] += delta
            i += i & -i                       # jump to the covering parent

    def prefix(self, i):                      # sum of [0, i), theta(log n)
        s = 0.0
        while i > 0:
            s += self.t[i]
            i -= i & -i                       # strip the lowest set bit
        return s

    def range_sum(self, lo, hi):
        return self.prefix(hi) - self.prefix(lo)

    def find_prefix(self, target):
        """Smallest i with prefix(i+1) > target. theta(log n), no binary
        search over prefix() -- this walks the tree directly."""
        pos, rest = 0, target
        step = 1 << (self.n.bit_length())
        while step:
            nxt = pos + step
            if nxt <= self.n and self.t[nxt] <= rest:
                pos = nxt
                rest -= self.t[nxt]
            step >>= 1
        return pos
```

`i & -i` isolates the lowest set bit: for `i = 12 = 0b1100` it gives
`4 = 0b100`. Adding it moves to the next node that covers `i`; subtracting it
moves to the previous disjoint block. Two lines of bit arithmetic replace an
explicit tree.

:::insight `find_prefix` is the operation that matters for sampling
Searching for the smallest index whose prefix sum exceeds a target is the
inverse-CDF sampling step. Doing it with `bisect` over `prefix()` costs
$\Theta(\log^2 n)$; walking the tree as above costs $\Theta(\log n)$ and is
the reason a Fenwick tree beats a sorted cumulative array when weights change.
:::

## Dynamic weighted sampling

Here is the problem this chapter exists for. You must sample an index with
probability proportional to $w_i$, and the weights change after every sample.

| Approach | Sample | Update | Notes |
|---|---|---|---|
| Linear scan | $\Theta(n)$ | $\Theta(1)$ | fine below a few thousand |
| Cumulative array + `searchsorted` | $\Theta(\log n)$ | $\Theta(n)$ | wrong choice if weights change |
| Alias table | $\Theta(1)$ | $\Theta(n)$ rebuild | best for *static* weights (Chapter 34) |
| Fenwick / segment tree | $\Theta(\log n)$ | $\Theta(\log n)$ | the right answer when both happen |

@tbl: Sampling with changing weights. The Fenwick tree is the only row where both operations are logarithmic.

```python title="Prioritized experience replay, the data-structure core"
import numpy as np

class PrioritizedBuffer:
    def __init__(self, capacity, alpha=0.6, eps=1e-6):
        self.cap, self.alpha, self.eps = capacity, alpha, eps
        self.sum_tree = Fenwick(capacity)     # sum of p_i^alpha
        self.max_priority = 1.0
        self.pos, self.size = 0, 0
        self.data = [None] * capacity

    def add(self, item, priority=None):
        p = self.max_priority if priority is None else priority
        i = self.pos
        old = self.sum_tree.range_sum(i, i + 1)
        self.sum_tree.update(i, (p + self.eps) ** self.alpha - old)
        self.data[i] = item
        self.pos = (i + 1) % self.cap         # ring buffer, Chapter 6
        self.size = min(self.size + 1, self.cap)

    def sample(self, batch, beta=0.4, rng=np.random):
        total = self.sum_tree.prefix(self.cap)
        idx, weights = [], []
        for _ in range(batch):
            u = rng.random() * total
            i = self.sum_tree.find_prefix(u)          # theta(log n)
            idx.append(i)
            p_i = self.sum_tree.range_sum(i, i + 1) / total
            weights.append((self.size * p_i) ** (-beta))   # IS correction
        w = np.asarray(weights)
        return idx, [self.data[i] for i in idx], w / w.max()

    def update_priorities(self, idx, td_errors):
        for i, err in zip(idx, td_errors):
            p = (abs(err) + self.eps) ** self.alpha
            old = self.sum_tree.range_sum(i, i + 1)
            self.sum_tree.update(i, p - old)           # theta(log n)
            self.max_priority = max(self.max_priority, abs(err) + self.eps)
```

:::ml Why the importance-sampling weight is not optional
Sampling transitions in proportion to $p_i^\alpha$ makes the gradient
estimate *biased*: high-error transitions are over-represented relative to
the distribution the loss is defined over. The correction is to weight each
sampled transition's loss by $\left(\frac{1}{N p_i}\right)^\beta$, normalised
by the maximum weight in the batch for stability. With $\beta = 1$ the bias
is fully removed; in practice $\beta$ is annealed from about 0.4 to 1 over
training, because early on the bias matters less than the variance reduction.

Omitting the correction is a common and silent bug: training still works, but
it converges to a subtly different objective, and the effect looks like
instability rather than like a bug.
:::

:::pitfall Choosing $\alpha$ and the sampling distribution
$\alpha = 0$ gives uniform sampling; $\alpha = 1$ gives fully proportional
sampling, which collapses onto a handful of transitions and starves the rest.
The typical $\alpha \approx 0.6$ is a compromise nobody has improved on much.
Also note that the *rank-based* variant --- priority proportional to
$1/\text{rank}$ --- is more robust to outlier TD errors, at the cost of needing
an order-maintaining structure instead of a sum tree.
:::

:::ml Other places these trees appear
**Ranking and counting.** "How many documents scored above $x$ in the last
hour?" with a stream of updates is a Fenwick tree over score buckets.

**Online quantiles.** A Fenwick tree over a fixed bucketisation gives
approximate quantiles in $\Theta(\log B)$ per update and query --- simpler
than t-digest (Chapter 38) when the value range is known.

**Sliding-window statistics.** A segment tree over a window supports
arbitrary associative aggregates with updates, where a monotonic deque
(Chapter 6) only supports min and max.

**Token budget accounting.** Maintaining per-tenant usage with range queries
in a multi-tenant serving system.
:::

:::exercise
1. Implement a segment tree for range minimum, and use it to answer
   $10^6$ random range-min queries on an array of $10^6$ elements. Compare to
   a sparse-table (which is $\Theta(1)$ per query but immutable).
2. Verify that your segment-tree query is correct for a non-commutative
   operation by using $2 \times 2$ matrix multiplication.
3. Implement a Fenwick tree and a prefix-sum array; measure query and update
   throughput for both at $n = 10^6$, and find the update frequency at which
   the Fenwick tree wins.
4. Implement `find_prefix` with (a) `bisect` over `prefix()` and (b) the
   direct tree walk. Measure both at $n = 10^6$ and confirm the
   $\log^2$ versus $\log$ difference.
5. Add lazy propagation for "assign a value to a range" (rather than "add"),
   and explain why the two compose differently.
6. Implement the full prioritized replay buffer and train a small DQN with
   and without the importance-sampling correction. Plot the learning curves.
7. Implement rank-based prioritized replay using a segment tree over rank
   buckets, and compare its robustness to an injected outlier TD error.
:::

:::recap
- Prefix sums give $\Theta(1)$ queries and forbid updates; Fenwick and
  segment trees give $\Theta(\log n)$ for both.
- A segment tree works for any associative operation; keep separate left and
  right accumulators so non-commutative operations are correct.
- Lazy propagation defers range updates until a query forces them down,
  keeping range update and range query both $\Theta(\log n)$.
- A Fenwick tree is half the memory and a much smaller constant, for
  invertible prefix aggregates; `i & -i` is the whole trick.
- `find_prefix` walks the tree in $\Theta(\log n)$ and is the inverse-CDF
  sampling step --- the reason to use a Fenwick tree for dynamic weighted
  sampling.
- Prioritized experience replay is a sum tree over priorities plus a ring
  buffer; the importance-sampling weight is required for an unbiased
  gradient.
:::
