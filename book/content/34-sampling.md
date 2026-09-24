# Sampling Algorithms
@short: Sampling
@subtitle: Drawing from a distribution, fast, correctly, and at the right time
@tier: advanced
@prereq: Chapters 21, 27
@blurb: Sampling appears at every layer of a machine learning system: choosing examples for a batch, choosing negatives for a contrastive loss, choosing a token to emit. Doing it naively costs a linear scan per draw; doing it well costs constant time. This chapter collects the handful of algorithms that make the difference, including the Gumbel trick that quietly underlies a surprising amount of modern practice.
@objectives:
- Implement inverse-CDF, alias-method and Gumbel-max sampling and know their costs
- Choose the right method given whether weights are static or dynamic
- Implement Gumbel top-$k$ for sampling without replacement
- Implement negative sampling and understand the unigram$^{3/4}$ distribution
- Implement stratified, balanced and curriculum samplers correctly
- Avoid the classic bias bugs in distributed and multi-worker sampling

## The core problem

Draw $i \in \{1, \ldots, n\}$ with probability $p_i \propto w_i$.

| Method | Preprocess | Per sample | Weights may change? |
|---|---|---|---|
| Linear scan | none | $\Theta(n)$ | yes |
| Inverse CDF (prefix sums + binary search) | $\Theta(n)$ | $\Theta(\log n)$ | no (rebuild is $\Theta(n)$) |
| Fenwick tree | $\Theta(n)$ | $\Theta(\log n)$ | yes, $\Theta(\log n)$ per update |
| Alias method | $\Theta(n)$ | $\Theta(1)$ | no |
| Gumbel-max | none | $\Theta(n)$ | yes (and needs no normalisation) |
| Gumbel top-$k$ | none | $\Theta(n)$ for $k$ items | yes |

@tbl: Sampling methods. The decision is almost entirely "do the weights change between draws?"

## The alias method

@fig: alias_table | 162 | The alias method. Redistribute probability mass so that every one of the $n$ columns has height exactly $1/n$, each holding at most two outcomes. A draw is then one integer and one float.

```python title="Vose's alias method: O(n) build, O(1) sample"
import numpy as np

class AliasSampler:
    def __init__(self, weights, seed=0):
        w = np.asarray(weights, dtype=np.float64)
        n = len(w)
        self.n = n
        self.prob = w * n / w.sum()              # mean is now 1
        self.alias = np.zeros(n, dtype=np.int64)
        small = [i for i in range(n) if self.prob[i] < 1.0]
        large = [i for i in range(n) if self.prob[i] >= 1.0]
        while small and large:
            s, l = small.pop(), large.pop()
            self.alias[s] = l
            self.prob[l] -= 1.0 - self.prob[s]   # l absorbs s's deficit
            (small if self.prob[l] < 1.0 else large).append(l)
        for i in small + large:
            self.prob[i] = 1.0                   # floating-point residue
        self.rng = np.random.default_rng(seed)

    def sample(self, size=1):
        i = self.rng.integers(0, self.n, size=size)
        u = self.rng.random(size=size)
        return np.where(u < self.prob[i], i, self.alias[i])
```

The invariant: every column has total height 1, consisting of some of
outcome $i$ and the rest of `alias[i]`. Pick a column uniformly, then pick
within it with one coin flip. Two random numbers, two array reads, no
search.

:::ml Where the alias method belongs
**Negative sampling** in word2vec, contrastive learning and
recommender training: the noise distribution is fixed for an epoch, and you
draw billions of samples from it. Building an alias table once and sampling
in $\Theta(1)$ is the difference between the sampler being negligible and
being the bottleneck.

**Static class-balanced sampling**: weights are $1/\text{class frequency}$
and do not change.

**Data mixture sampling**: choosing which corpus a batch comes from,
according to fixed mixture weights.

It is the *wrong* choice whenever weights change --- prioritized replay,
active learning, curriculum learning --- because every change costs a
$\Theta(n)$ rebuild. That is Chapter 27's Fenwick tree.
:::

## The Gumbel trick

:::theorem Gumbel-max
Let $g_1, \ldots, g_n$ be i.i.d. samples from the standard Gumbel
distribution, $g_i = -\log(-\log u_i)$ with $u_i \sim \text{Uniform}(0,1)$.
Then
$$\arg\max_i \left( \log w_i + g_i \right) \sim \text{Categorical}\!\left(\frac{w_i}{\sum_j w_j}\right)$$
:::

This is remarkable in three ways. It needs no normalisation --- unnormalised
log-weights (logits) are enough. It is a pure `argmax`, so it vectorises
perfectly on a GPU. And its extension is immediate:

:::theorem Gumbel top-$k$
Taking the **top $k$** of $\log w_i + g_i$ gives a sample of $k$ distinct
items drawn **without replacement** from the same categorical distribution.
:::

```python title="Gumbel-max and Gumbel top-k"
import numpy as np

def gumbel_sample(logits, rng=np.random):
    g = -np.log(-np.log(rng.random(logits.shape) + 1e-20) + 1e-20)
    return int(np.argmax(logits + g))

def gumbel_topk(logits, k, rng=np.random):
    """k distinct items, without replacement, in one vectorised pass."""
    g = -np.log(-np.log(rng.random(logits.shape) + 1e-20) + 1e-20)
    perturbed = logits + g
    idx = np.argpartition(-perturbed, k)[:k]
    return idx[np.argsort(-perturbed[idx])]
```

:::ml Gumbel in practice
**Temperature sampling from a language model** is exactly Gumbel-max on
`logits / temperature` --- which is what every framework's `multinomial` does
under the hood on a GPU, because `argmax` is cheaper than a cumulative sum
plus a search.

**Sampling without replacement at scale**: choosing $k$ distinct items from a
billion-item catalogue for a slate, in one vectorised pass.

**Gumbel-softmax (concrete) relaxation**: replacing `argmax` with a
temperature-scaled `softmax` makes the sample differentiable, which is how
discrete latent variables, hard attention and differentiable architecture
search are trained.

**Weighted reservoir sampling** (Chapter 21) is the Gumbel trick in disguise:
the key $u^{1/w}$ is a monotone transform of $\log w + g$, which is why it
produces the same distribution.
:::

## Negative sampling

Training a model to distinguish observed pairs from noise requires drawing
negatives, and the noise distribution matters more than its implementation.

```python title="The unigram^0.75 distribution and the sampler"
import numpy as np

def build_negative_sampler(counts, power=0.75, seed=0):
    """counts: array of item frequencies in the corpus."""
    w = np.asarray(counts, dtype=np.float64) ** power
    return AliasSampler(w, seed=seed)

def sample_negatives(sampler, positives, num_neg, max_tries=4):
    """Draw num_neg negatives per positive, rejecting accidental positives."""
    pos = set(positives.tolist())
    out = sampler.sample(size=len(positives) * num_neg).reshape(
        len(positives), num_neg)
    for _ in range(max_tries):
        bad = np.isin(out, list(pos))
        if not bad.any():
            break
        out[bad] = sampler.sample(size=int(bad.sum()))
    return out
```

The exponent $0.75$ is empirical and comes from word2vec: raising counts to a
power below 1 flattens the distribution, so rare items are sampled more often
than their frequency would suggest and common items less. Pure unigram
($\text{power} = 1$) oversamples stopwords and gives weak gradients; uniform
($\text{power} = 0$) samples implausible negatives that are too easy.

:::pitfall False negatives and sampling bias
Randomly drawn negatives are sometimes actually positive --- an item the user
would have liked, a document that does answer the query. The rejection loop
above handles *known* positives; unknown ones are an inherent bias. Two
standard mitigations: *in-batch negatives* (use other examples in the batch,
which is free and makes negatives harder as batch size grows) and
*hard-negative mining* (retrieve near-misses with the current model, which
is much more informative and much more prone to false negatives). The usual
production compromise is in-batch negatives plus a small number of mined hard
negatives with a similarity ceiling that filters out likely positives.
:::

## Samplers that appear in every dataloader

```python title="Three correct samplers"
import numpy as np

def stratified_indices(labels, n_per_class, rng=np.random):
    """Exactly n_per_class from each class -- not an expectation."""
    out = []
    for c in np.unique(labels):
        idx = np.flatnonzero(labels == c)
        take = rng.choice(idx, size=min(n_per_class, len(idx)), replace=False)
        out.append(take)
    out = np.concatenate(out)
    rng.shuffle(out)
    return out

def class_balanced_weights(labels, beta=0.999):
    """Effective-number reweighting: softer than 1/frequency."""
    counts = np.bincount(labels)
    eff = (1.0 - np.power(beta, counts)) / (1.0 - beta)
    w = 1.0 / np.maximum(eff, 1e-12)
    return (w / w.sum())[labels]

def distributed_shard(indices, rank, world_size, epoch, seed=0):
    """Every rank gets a disjoint, deterministic shard of a common shuffle."""
    rng = np.random.default_rng(seed + epoch)        # SAME seed on all ranks
    perm = rng.permutation(len(indices))
    pad = (-len(perm)) % world_size                  # pad so shards are equal
    if pad:
        perm = np.concatenate([perm, perm[:pad]])
    return indices[perm[rank::world_size]]
```

:::warning Three sampling bugs that are hard to see
**Different seeds per rank.** If each rank shuffles independently, the ranks
see overlapping data and the effective epoch is wrong. Seed the *shuffle*
identically on every rank and shard the result; seed *augmentation*
differently per rank.

**Unequal shard sizes.** If the dataset does not divide by `world_size`, one
rank finishes early and the all-reduce hangs or silently drops a batch. Pad
the permutation (as above) or drop the remainder --- but do it explicitly.

**Worker seeds that repeat.** PyTorch dataloader workers each get a derived
seed, but a `Dataset` that calls the global `random` module without reseeding
per worker will produce *identical* augmentations in every worker. Verify by
printing a hash of the first batch with `num_workers` set to 1 and to 4.
:::

:::ml Sampling in RL and curriculum learning
**Prioritized replay** needs dynamic weights: Fenwick tree (Chapter 27).
**Curriculum learning** raises the weight of harder examples over time:
dynamic weights again, but updated in bulk once per epoch, so a rebuilt alias
table is fine. **Active learning** scores the entire pool with the current
model and samples the top of it: not a sampling-structure problem at all but
a top-$k$ problem (Chapter 13). Identifying which of the three you have
determines the data structure.
:::

:::exercise
1. Implement the alias method and verify the empirical distribution against
   the target with a chi-squared test at $n = 1000$ and $10^7$ draws.
2. Compare sampling throughput for linear scan, `np.random.choice` with `p`,
   inverse CDF with `searchsorted`, and the alias method at
   $n \in \{10^3, 10^5, 10^7\}$.
3. Verify the Gumbel-max theorem empirically for $n = 5$ with skewed
   weights, using $10^6$ samples.
4. Verify that Gumbel top-$k$ gives the same distribution as $k$ sequential
   draws without replacement, for $n = 6$, $k = 3$.
5. Show that weighted reservoir sampling's key $u^{1/w}$ induces the same
   ordering as $\log w + g$ with $g$ Gumbel.
6. Implement the unigram$^{0.75}$ negative sampler and plot the sampling
   probability against rank for $\text{power} \in \{0, 0.5, 0.75, 1\}$ on a
   Zipf distribution.
7. Construct the "different seed per rank" bug in a two-process script and
   measure how much of the dataset each rank actually sees per epoch.
8. Implement a curriculum sampler whose weights depend on a per-example
   difficulty updated every epoch. Choose the data structure and justify it.
:::

:::recap
- The choice of sampling algorithm is decided by whether weights change
  between draws: alias for static, Fenwick tree for dynamic, Gumbel when you
  want vectorisation and no normalisation.
- The alias method redistributes mass so every column has height $1/n$,
  giving $\Theta(1)$ sampling after $\Theta(n)$ setup.
- Gumbel-max samples by `argmax` of perturbed logits, needs no normalising
  constant, vectorises perfectly, and its top-$k$ form samples $k$ items
  without replacement in one pass.
- Gumbel-softmax makes the sample differentiable, which is how discrete
  latents are trained.
- Negative sampling uses unigram$^{0.75}$; the real difficulties are false
  negatives, and in-batch plus lightly mined hard negatives is the standard
  compromise.
- Distributed sampling bugs --- per-rank seeds, unequal shards, repeated
  worker seeds --- are silent and change what your model trains on.
:::
