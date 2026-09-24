# Randomised Algorithms and Reservoir Sampling
@short: Randomised Algorithms
@subtitle: When a coin flip is a better guarantee than a clever rule
@tier: core
@prereq: Chapters 9, 17
@blurb: Randomness in an algorithm is not a compromise. It buys simplicity, it defeats adversarial inputs, and for some problems it provides guarantees no deterministic algorithm can match at the same cost. This chapter covers the two kinds of randomised algorithm, the probabilistic tools you need to analyse them, and the sampling algorithms that every training pipeline depends on.
@objectives:
- Distinguish Las Vegas from Monte Carlo algorithms and know when each is appropriate
- Analyse a randomised algorithm using linearity of expectation and concentration bounds
- Implement reservoir sampling, including the weighted and $k$-item variants
- Understand random projection and the Johnson--Lindenstrauss lemma
- Implement correct shuffling, stratified sampling and deterministic seeding
- Recognise the reproducibility traps randomness introduces in ML pipelines

## Two kinds of randomised algorithm

:::definition Las Vegas and Monte Carlo
A **Las Vegas** algorithm is always correct; its *running time* is a random
variable. Randomised quicksort is the canonical example: the answer is
always a sorted array, and only the time varies.

A **Monte Carlo** algorithm always runs in the stated time; its *answer* may
be wrong with bounded probability. A Bloom filter is the canonical example:
it answers in $\Theta(k)$ always, and sometimes says "present" when the item
is absent.
:::

The choice is a design decision with real consequences. A Las Vegas
algorithm inside a latency budget can blow the budget; a Monte Carlo one
cannot, but you must be able to tolerate --- or detect --- a wrong answer.
Most systems pick Monte Carlo with a failure probability driven below the
hardware error rate, which is the engineering answer.

:::insight Why randomness beats cleverness against an adversary
A deterministic algorithm has a worst case, and if the input is chosen by
something that knows your code --- a user, an attacker, or simply a
production data distribution you did not anticipate --- you will meet it.
Randomising makes the worst case depend on *your* coin flips rather than on
the input, so no input is reliably bad. This is why quicksort randomises its
pivot, why Python salts string hashes, and why load balancers randomise.
:::

## The analysis toolkit

**Linearity of expectation.** $\mathbb{E}[X + Y] = \mathbb{E}[X] + \mathbb{E}[Y]$
*even when $X$ and $Y$ are dependent*. This is the workhorse: decompose a
complicated count into indicator variables and sum their probabilities.

:::math Randomised quicksort in three lines
Let $X_{ij} = 1$ if elements of rank $i$ and $j$ are ever compared. They are
compared exactly when the first pivot chosen from the range of ranks
$[i, j]$ is $i$ or $j$ itself --- otherwise they are separated. That range
has $j - i + 1$ elements, so
$\Pr[X_{ij} = 1] = \frac{2}{j - i + 1}$. Hence

$$\mathbb{E}[\text{comparisons}] = \sum_{i<j} \frac{2}{j-i+1} = 2n H_n + O(n) \approx 1.39 \, n \log_2 n$$

No recursion tree, no case analysis. This is the standard example of why
linearity of expectation is worth learning properly.
:::

**Concentration.** Expectation alone is not a guarantee. Markov, Chebyshev
and Chernoff bounds say how unlikely large deviations are.

| Bound | Requires | Gives |
|---|---|---|
| Markov | $X \ge 0$ | $\Pr[X \ge a] \le \mathbb{E}[X]/a$ |
| Chebyshev | finite variance | $\Pr[\|X - \mu\| \ge k\sigma] \le 1/k^2$ |
| Chernoff / Hoeffding | sum of bounded independent variables | $\Pr[\|X - \mu\| \ge \varepsilon\mu] \le 2e^{-\varepsilon^2\mu/3}$ |

@tbl: The three bounds, in increasing order of strength and of what they assume. Chernoff's exponential decay is what makes "repeat $k$ times and take the majority" work so well.

**Probability amplification.** If a Monte Carlo algorithm is wrong with
probability $p < 1/2$, running it $k$ times independently and taking the
majority reduces the error probability exponentially in $k$. This is why a
one-sided-error test with $p = 1/4$ becomes a certainty for practical
purposes after 40 repetitions ($p < 10^{-24}$).

## Reservoir sampling

The problem: draw a uniform sample of $k$ items from a stream whose length
you do not know in advance, in one pass, using $\Theta(k)$ memory.

@fig: reservoir | 152 | Reservoir sampling. The first $k$ items fill the reservoir; item $i > k$ replaces a uniformly chosen slot with probability $k/i$. Every item ends up in the sample with probability exactly $k/n$.

```python title="Reservoir sampling, uniform k of n"
import random

def reservoir(stream, k, rng=random):
    res = []
    for i, x in enumerate(stream, start=1):
        if i <= k:
            res.append(x)
        else:
            j = rng.randrange(i)          # uniform in [0, i)
            if j < k:
                res[j] = x                # probability k/i
    return res
```

:::proof Every item is retained with probability exactly $k/n$
By induction on the stream length $n$. For $n = k$ the claim is trivial.
Assume it holds after $n - 1$ items. Item $n$ is kept with probability
$k/n$ directly. An earlier item was in the reservoir with probability
$k/(n-1)$ and survives item $n$ unless it is the one evicted, which happens
with probability $\frac{k}{n} \cdot \frac{1}{k} = \frac{1}{n}$. So it
survives with probability
$\frac{k}{n-1} \cdot \left(1 - \frac{1}{n}\right) = \frac{k}{n-1} \cdot \frac{n-1}{n} = \frac{k}{n}$.
:::

**Weighted reservoir sampling (A-Res).** For sampling without replacement
proportional to weights $w_i$, assign each item the key $u_i^{1/w_i}$ with
$u_i$ uniform in $(0,1)$, and keep the $k$ largest keys in a min-heap.

```python title="Weighted reservoir sampling with a heap"
import heapq, random

def weighted_reservoir(stream, k, rng=random):
    heap = []                              # min-heap of (key, item)
    for item, w in stream:
        if w <= 0:
            continue
        key = rng.random() ** (1.0 / w)    # exponential-race trick
        if len(heap) < k:
            heapq.heappush(heap, (key, item))
        elif key > heap[0][0]:
            heapq.heapreplace(heap, (key, item))
    return [item for _, item in heap]
```

The identity that makes this work: $\Pr[u^{1/w} > t] = 1 - t^{w}$, so
larger weights produce larger keys in exactly the right proportion. This is
the same "exponential race" argument behind the Gumbel-max trick (Chapter 34).

:::ml Where reservoir sampling actually runs
Building a held-out evaluation set from a data stream you are still writing;
sampling training examples for human review without a second pass; sampling
log lines for monitoring at a fixed rate regardless of traffic; drawing a
random subset of a dataset too large to shuffle. In each case the property
that matters is *one pass, bounded memory, no need to know $n$*.
:::

## Shuffling, correctly

```python title="Fisher-Yates: the only correct in-place shuffle"
import random

def shuffle(a, rng=random):
    for i in range(len(a) - 1, 0, -1):
        j = rng.randint(0, i)              # INCLUSIVE of i
        a[i], a[j] = a[j], a[i]
    return a
```

Two classic ways to get this wrong. Choosing `j` from the whole array
(`randint(0, n-1)`) produces $n^n$ equally likely execution paths mapping
onto $n!$ permutations, and since $n! \nmid n^n$ the distribution cannot be
uniform --- a bias large enough to detect with a few thousand trials on
$n = 4$. And `sorted(a, key=lambda _: random.random())` is uniform but
$\Theta(n \log n)$ and allocates; it was also the source of a famous
browser-ballot bias when implemented with a random *comparator* instead of a
random key.

:::pitfall Shuffling a dataset larger than memory
Fisher--Yates needs random access. For a dataset on disk you cannot shuffle
in place. The standard approaches: (1) *shard shuffle* --- shuffle the file
order, then shuffle a buffer of $B$ examples in memory (what
`tf.data.shuffle(B)` and WebDataset do); the randomness is only as good as
$B$, and a buffer smaller than one class's run length leaves correlated
batches. (2) *Two-pass shuffle* --- scatter records into $m$ random files,
then shuffle each file in memory; this is a true uniform shuffle and costs
two passes. (3) Pre-shuffle once at write time and read sequentially with a
random offset each epoch.
:::

## Random projection

:::theorem Johnson--Lindenstrauss
For any $0 < \varepsilon < 1$ and any set of $n$ points in $\mathbb{R}^d$,
there is a linear map $f : \mathbb{R}^d \to \mathbb{R}^m$ with
$m = O(\varepsilon^{-2} \log n)$ such that for all pairs $u, v$,

$$(1 - \varepsilon)\|u - v\|^2 \le \|f(u) - f(v)\|^2 \le (1 + \varepsilon)\|u - v\|^2$$

Moreover, a matrix with i.i.d. Gaussian entries works with high probability.
:::

Read the bound carefully: $m$ depends on $\log n$ and **not at all on $d$**.
You can project a million 4096-dimensional vectors into about 500 dimensions
and preserve all pairwise distances to within 10%. The proof is a Chernoff
bound on the squared length of a projected vector plus a union bound over
$\binom{n}{2}$ pairs.

```python title="Random projection for cheap distance-preserving compression"
import numpy as np

def project(X, m, seed=0):
    rng = np.random.default_rng(seed)
    d = X.shape[1]
    R = rng.standard_normal((d, m)).astype(np.float32) / np.sqrt(m)
    return X @ R                            # (n, m), distances preserved
```

:::ml Random projection in the retrieval stack
It is the theoretical basis for LSH (Chapter 29), it is used to shrink
embeddings before building an index when memory is tight, and the sparse
variants (Achlioptas: entries in $\{-1, 0, +1\}$ with probability
$\{1/6, 2/3, 1/6\}$) make the projection itself cheap. It also explains why
reducing an embedding from 1536 to 384 dimensions often costs surprisingly
little recall --- the information you need for *relative* distances survives
projection, even though the individual coordinates do not.
:::

## Reproducibility

Randomness that you cannot reproduce is a debugging catastrophe. Four rules.

1. **Seed explicitly, and seed everything**: Python's `random`, NumPy,
   the framework, and each dataloader worker (which by default gets a
   different seed derived from the base seed --- verify what yours does).
2. **Prefer generator objects to global state.** `np.random.default_rng(seed)`
   passed explicitly makes the dependency visible; the global `np.random`
   is shared mutable state and breaks under concurrency.
3. **Derive per-item seeds from content, not from position.** Seeding an
   augmentation with `hash(example_id) ^ epoch_seed` makes it reproducible
   regardless of sharding, worker count or ordering. Seeding with the batch
   index does not.
4. **Know what is still nondeterministic.** Floating-point reduction order
   on a GPU, atomic scatter-adds, and non-deterministic cuDNN kernels all
   produce run-to-run differences that no seed controls. If you need
   bit-exact reproducibility, you must also request deterministic kernels
   and accept the slowdown.

:::exercise
1. Implement the biased shuffle (`randint(0, n-1)`) and the correct one.
   For $n = 4$, run $10^6$ trials of each and plot the frequency of all 24
   permutations. Quantify the bias with a chi-squared test.
2. Verify reservoir sampling empirically: run it $10^5$ times on a stream of
   100 items with $k = 10$ and check that each item appears close to 10% of
   the time.
3. Implement weighted reservoir sampling and verify that the inclusion
   probability of each item is proportional to its weight.
4. Use linearity of expectation to compute the expected number of fixed
   points of a random permutation. (The answer is 1, for every $n$.)
5. Empirically verify Johnson--Lindenstrauss: project $10^4$ random
   1000-dimensional points to $m \in \{50, 100, 200, 500\}$ and plot the
   distribution of relative distance distortion. Compare to the bound.
6. Implement a two-pass shuffle of a 100 GB file using $m$ intermediate
   shards. How large must $m$ be for each shard to fit in 8 GB, and what is
   the total I/O?
7. Show that `tf.data.shuffle(buffer_size=B)` on a dataset sorted by class
   produces correlated batches when $B$ is smaller than a class run.
   Quantify the correlation and propose a fix.
:::

:::recap
- Las Vegas algorithms are always correct with variable time; Monte Carlo
  always finish on time but may be wrong with bounded probability.
- Randomisation defeats adversarial inputs by moving the worst case from the
  input to your own coin flips.
- Linearity of expectation decomposes complicated counts into indicators;
  Chernoff bounds turn expectations into guarantees and justify repetition.
- Reservoir sampling gives a uniform $k$-sample in one pass with $\Theta(k)$
  memory and no knowledge of $n$; the weighted version uses the key
  $u^{1/w}$ and a min-heap.
- Fisher--Yates is the only correct in-place shuffle; the off-by-one variant
  is measurably biased. Shuffling out-of-core needs a buffer shuffle or a
  two-pass scatter.
- Johnson--Lindenstrauss: $O(\varepsilon^{-2}\log n)$ dimensions preserve all
  pairwise distances, independent of the original dimension.
- Seed explicitly, pass generators rather than using global state, derive
  per-item seeds from content, and know what remains nondeterministic on
  accelerators.
:::
