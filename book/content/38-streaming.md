# Streaming and Online Algorithms
@short: Streaming
@subtitle: One pass, bounded memory, and an answer at every moment
@tier: advanced
@prereq: Chapters 11, 28
@blurb: Production ML systems are streams: events arrive, predictions are made, metrics must be current, and nothing can be re-read. This chapter covers the algorithms that compute statistics, quantiles and drift in one pass with bounded memory --- including the numerically stable updates that stop your monitoring dashboard reporting negative variances.
@objectives:
- Implement numerically stable streaming mean, variance and covariance
- Implement exponentially weighted statistics and know their effective window
- Implement t-digest for accurate tail quantiles with mergeable state
- Detect distribution drift with a two-window test
- Understand the competitive-ratio framing of online algorithms
- Recognise which monitoring computations are safe to distribute

## Why streaming is a different discipline

A streaming algorithm sees each item once, uses memory sub-linear in the
stream length, and must have an answer available at any moment. That third
requirement is what separates it from a batch job.

| Statistic | Exact in one pass? | Memory |
|---|---|---|
| Count, sum, mean | yes | $\Theta(1)$ |
| Variance, covariance | yes (Welford) | $\Theta(1)$ |
| Min, max | yes | $\Theta(1)$ |
| Any quantile | no | $\Omega(n)$ for exact |
| Approximate quantile ($\pm\varepsilon$) | yes | $\Theta(1/\varepsilon)$ |
| Distinct count | no | $\Omega(n)$ exact; $\Theta(1)$ approximate (HLL) |
| Top-$k$ frequent | no | $\Theta(k)$ approximate (Space-Saving) |
| Median of a window | yes | $\Theta(w)$ (two heaps, Chapter 13) |

@tbl: What one pass can and cannot give you. The exactness boundary is worth knowing: quantiles and distinct counts *cannot* be exact in sub-linear memory, which is a theorem, not an implementation gap.

## Stable moments

```python title="Welford's algorithm: numerically stable, mergeable"
class RunningStats:
    __slots__ = ("n", "mean", "m2")

    def __init__(self):
        self.n, self.mean, self.m2 = 0, 0.0, 0.0

    def push(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)      # note: uses the NEW mean

    @property
    def variance(self):
        return self.m2 / (self.n - 1) if self.n > 1 else 0.0

    def merge(self, other):                     # Chan's parallel update
        if other.n == 0:
            return self
        n = self.n + other.n
        delta = other.mean - self.mean
        self.m2 += other.m2 + delta * delta * self.n * other.n / n
        self.mean += delta * other.n / n
        self.n = n
        return self
```

:::warning The naive variance formula is genuinely broken
$\text{Var} = \frac{1}{n}\sum x_i^2 - \bar{x}^2$ subtracts two nearly equal
large numbers. For values around $10^6$ with a standard deviation of 1, the
result in float64 loses most of its significant digits and frequently comes
out *negative*. Welford's update never forms those large intermediates and is
accurate to within a few units in the last place. Use it; it is the same
number of operations.

Note also `merge`: Welford's state combines exactly, so per-shard statistics
reduce to a global answer in a tree (Chapter 16). Not every statistic has
this property, and the ones that do are the ones you can compute across a
fleet.
:::

```python title="Exponentially weighted statistics for a drifting stream"
class EWMA:
    """alpha in (0,1); effective window is about 1/alpha samples."""
    def __init__(self, alpha=0.01):
        self.alpha = alpha
        self.mean = None
        self.var = 0.0

    def push(self, x):
        if self.mean is None:
            self.mean = float(x)
            return
        delta = x - self.mean
        self.mean += self.alpha * delta
        self.var = (1 - self.alpha) * (self.var + self.alpha * delta * delta)
```

An EWMA needs $\Theta(1)$ memory and forgets smoothly, which is what you want
for a metric on a non-stationary stream. Its effective window is $1/\alpha$
samples: $\alpha = 0.01$ averages over roughly the last 100 observations.
Choosing $\alpha$ *is* choosing how quickly your monitor reacts and how noisy
it is, and it should be stated in the alert definition.

## Quantiles: t-digest

Tail quantiles are what monitoring actually needs --- p99 latency, p999
score --- and they are exactly where naive approaches fail.

@fig: tdigest | 140 | t-digest. A scale function makes centroids small near $q=0$ and $q=1$ and large in the middle, so the tails stay accurate while total memory stays bounded.

:::definition t-digest
A set of *centroids*, each with a count and a mean. A centroid at quantile
$q$ may absorb at most $4n\delta\, q(1-q)$ points, where $\delta$ is a
compression parameter. This is small near the tails and large in the middle,
so relative error at $q=0.999$ stays tiny while memory stays $\Theta(\delta)$.
Digests merge by concatenating centroid lists and re-compressing.
:::

```python title="A simple t-digest"
import bisect

class TDigest:
    def __init__(self, compression=100):
        self.delta = compression
        self.centroids = []          # sorted list of [mean, count]
        self.n = 0

    def push(self, x, w=1):
        self.n += w
        i = bisect.bisect_left([c[0] for c in self.centroids], x)
        best, best_d = None, float("inf")
        for j in (i - 1, i):         # nearest centroid on either side
            if 0 <= j < len(self.centroids):
                d = abs(self.centroids[j][0] - x)
                if d < best_d and self._can_absorb(j, w):
                    best, best_d = j, d
        if best is None:
            self.centroids.insert(i, [float(x), w])
        else:
            m, c = self.centroids[best]
            self.centroids[best] = [m + (x - m) * w / (c + w), c + w]
        if len(self.centroids) > 20 * self.delta:
            self._compress()

    def _can_absorb(self, j, w):
        before = sum(c[1] for c in self.centroids[:j])
        q = (before + self.centroids[j][1] / 2) / max(self.n, 1)
        limit = 4 * self.n * q * (1 - q) / self.delta
        return self.centroids[j][1] + w <= max(limit, 1)

    def _compress(self):
        import random
        pts = [(m, c) for m, c in self.centroids]
        random.shuffle(pts)
        self.centroids, self.n = [], 0
        for m, c in pts:
            self.push(m, c)

    def quantile(self, q):
        if not self.centroids:
            return float("nan")
        target = q * self.n
        acc = 0.0
        for m, c in self.centroids:
            if acc + c / 2 >= target:
                return m
            acc += c
        return self.centroids[-1][0]
```

| Method | Memory | Tail accuracy | Mergeable |
|---|---|---|---|
| Store everything, sort | $\Theta(n)$ | exact | yes (concatenate) |
| Fixed histogram | $\Theta(B)$ | poor unless range is known | yes |
| Reservoir sample | $\Theta(k)$ | sampling error at the tail | no (needs care) |
| P² algorithm | $\Theta(1)$ per quantile | poor on skew | no |
| GK (Greenwald--Khanna) | $\Theta(\frac{1}{\varepsilon}\log \varepsilon n)$ | uniform $\varepsilon$ | yes |
| t-digest | $\Theta(\delta)$ | excellent at the tails | yes |
| DDSketch | $\Theta(\frac{1}{\gamma}\log \text{range})$ | relative error guarantee | yes |

@tbl: Quantile sketches. t-digest is the usual choice for latency monitoring; DDSketch gives a *guaranteed* relative error, which t-digest does not.

## Drift detection

```python title="A two-window drift test"
import numpy as np
from collections import deque

class DriftDetector:
    """Compare a reference window to a recent window."""
    def __init__(self, ref_size=10_000, cur_size=1_000, bins=32):
        self.ref = deque(maxlen=ref_size)
        self.cur = deque(maxlen=cur_size)
        self.bins = bins

    def push(self, x):
        self.cur.append(x)
        if len(self.ref) < self.ref.maxlen:
            self.ref.append(x)

    def psi(self):
        """Population stability index: sum (p - q) * log(p / q)."""
        if len(self.cur) < self.cur.maxlen:
            return 0.0
        edges = np.quantile(self.ref, np.linspace(0, 1, self.bins + 1))
        edges[0], edges[-1] = -np.inf, np.inf
        p, _ = np.histogram(self.ref, bins=edges)
        q, _ = np.histogram(self.cur, bins=edges)
        p = (p + 1) / (p.sum() + self.bins)        # Laplace smoothing
        q = (q + 1) / (q.sum() + self.bins)
        return float(((p - q) * np.log(p / q)).sum())
```

PSI above 0.1 conventionally indicates moderate drift and above 0.25
significant drift. The alternatives are a Kolmogorov--Smirnov test
(distribution-free, but sensitive to sample size, so it flags trivial drift
in large windows), and ADWIN, which adaptively resizes the window and has a
false-positive guarantee.

:::pitfall Drift detection on a schedule is drift detection on the wrong data
Comparing "today" to "the training set" flags seasonality as drift every
Monday. Comparing to "last week" misses slow degradation entirely. And
feature drift is not the same as *performance* drift --- features can move a
long way with no accuracy loss, and accuracy can fall with no feature drift
at all (label shift, concept drift). Monitor both, and alert on the one
you actually care about: the metric that affects users.
:::

## Online algorithms and competitive ratios

:::definition Competitive ratio
An online algorithm, which must decide irrevocably without seeing the future,
is $c$-competitive if for every input its cost is at most $c$ times the cost
of the optimal offline algorithm that knows the entire input in advance.
:::

This framing turns several practical questions into provable statements.
Caching: LRU is $k$-competitive for a cache of size $k$, and no
deterministic policy does better; randomised marking is
$O(\log k)$-competitive. The ski-rental problem (buy or keep renting?) has a
2-competitive deterministic solution and an $e/(e-1) \approx 1.58$
randomised one --- and it is the exact shape of "keep a GPU instance warm or
pay cold-start latency?", "keep a KV cache or recompute it?", and "hold a
connection open or reconnect?".

:::ml The streaming pieces of an ML system
**Online feature computation.** Rolling counts and rates per entity, computed
with EWMA or a windowed aggregate, must match exactly between training and
serving or you get training--serving skew. The usual bug is computing the
feature in batch SQL for training and in a stream processor for serving,
with subtly different window semantics.

**Metric monitoring.** Throughput, latency percentiles and error rates from
t-digests merged across replicas.

**Online learning.** SGD is itself an online algorithm; bandit algorithms
(UCB, Thompson sampling) have regret bounds that are the online-algorithm
framing of exploration.

**Streaming inference.** Sliding-window attention with a ring-buffer KV cache
(Chapters 6 and 36) is a streaming algorithm: bounded memory, one pass,
answer available at every step.
:::

:::exercise
1. Show that the naive variance formula returns a negative value for
   $10^6$ samples drawn from $\mathcal{N}(10^8, 1)$ in float32, and that
   Welford's does not.
2. Implement Welford's `merge` and verify it exactly matches a single-pass
   computation over the concatenated data.
3. Derive the effective window of an EWMA with parameter $\alpha$, and verify
   it by measuring the lag of the mean after a step change.
4. Implement t-digest and measure the relative error at $q \in \{0.5, 0.9,
   0.99, 0.999\}$ for a log-normal stream, as a function of `compression`.
5. Merge 100 t-digests computed on disjoint shards and compare the merged
   quantiles to the exact ones on the full data.
6. Implement Space-Saving for top-$k$ heavy hitters and compare it to a
   Count--Min sketch plus heap (Chapter 28) at equal memory.
7. Implement PSI and KS drift tests, and show that KS flags drift on a
   distribution that has not meaningfully changed when the window is large.
8. Formulate "keep the model warm on a GPU or evict it and pay the load time"
   as ski-rental. State the 2-competitive policy and simulate it against the
   offline optimum on a realistic request trace.
:::

:::recap
- Streaming algorithms see each item once, use sub-linear memory, and must
  have an answer at any moment.
- Welford's algorithm gives stable mean and variance and merges exactly
  across shards; the naive $E[x^2] - E[x]^2$ formula is numerically broken.
- EWMA gives $\Theta(1)$ forgetting with effective window $1/\alpha$; state
  that window in your alert definitions.
- Exact quantiles need linear memory; t-digest keeps small centroids at the
  tails for excellent p99 accuracy in bounded, mergeable state. DDSketch
  gives a relative-error guarantee.
- Drift detection needs the right reference window and should distinguish
  feature drift from performance drift.
- The competitive ratio formalises online decisions: LRU is
  $k$-competitive; ski-rental is 2-competitive deterministically and
  $e/(e-1)$ randomised, and describes several real caching decisions.
:::
