# Tree Learners: Decision Trees, Histograms and GBDT
@short: Tree Learners
@subtitle: The algorithms that still win on tabular data
@tier: advanced
@prereq: Chapters 9, 12, 17
@blurb: Gradient-boosted decision trees remain the strongest method for tabular data, and their speed comes almost entirely from data-structure engineering rather than from statistics. This chapter builds a decision tree from first principles, then shows the three ideas --- histogram binning, histogram subtraction and leaf-wise growth --- that made LightGBM and XGBoost orders of magnitude faster than their predecessors.
@objectives:
- Implement decision-tree induction with an exact split finder
- Derive the gain formula used by gradient boosting
- Implement histogram-based split finding and explain its complexity
- Understand histogram subtraction, leaf-wise growth and EFB
- Handle categorical features and missing values correctly
- Reason about inference cost and why tree models are fast to serve

## Decision-tree induction

A decision tree is built greedily (Chapter 17): at each node, choose the
split that maximally reduces impurity, then recurse. Finding the *globally*
optimal tree is NP-hard, so every practical learner is greedy and accepts
the suboptimality.

```python title="Exact split finding: the O(n log n) baseline"
import numpy as np

def best_split_exact(X, g, h, lam=1.0, min_child=1.0):
    """X: (n, d) features. g, h: gradient and hessian per sample.
    Returns (feature, threshold, gain)."""
    G, H = g.sum(), h.sum()
    parent = G * G / (H + lam)
    best = (None, None, 0.0)
    for j in range(X.shape[1]):
        order = np.argsort(X[:, j], kind="stable")       # theta(n log n)
        gs, hs = np.cumsum(g[order]), np.cumsum(h[order])
        xs = X[order, j]
        valid = np.flatnonzero(xs[1:] != xs[:-1])        # no split inside ties
        for i in valid:
            GL, HL = gs[i], hs[i]
            GR, HR = G - GL, H - HL
            if HL < min_child or HR < min_child:
                continue
            gain = GL * GL / (HL + lam) + GR * GR / (HR + lam) - parent
            if gain > best[2]:
                best = (j, 0.5 * (xs[i] + xs[i + 1]), gain)
    return best
```

:::math Where the gain formula comes from
Gradient boosting fits each tree to a second-order Taylor expansion of the
loss. With $g_i$ and $h_i$ the first and second derivatives at the current
prediction, the optimal constant output for a leaf containing set $I$ is
$$w^* = -\frac{\sum_{i \in I} g_i}{\sum_{i \in I} h_i + \lambda}$$
and the loss reduction achieved by that leaf is
$-\frac{1}{2}\frac{(\sum g_i)^2}{\sum h_i + \lambda}$. Splitting a node into
$L$ and $R$ therefore gains
$$\text{gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L + \lambda} +
\frac{G_R^2}{H_R + \lambda} - \frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right] - \gamma$$
The only quantities needed are the *sums* $G$ and $H$ on each side --- which
is exactly why prefix sums over a sorted feature give every candidate split
in one pass, and why histogram binning works.
:::

The exact method costs $\Theta(nd \log n)$ per level (the sorts dominate), or
$\Theta(nd)$ if you presort once and keep index lists. For $n = 10^7$ and
$d = 100$ that is still enormous, and it is where histograms come in.

## Histogram-based split finding

@fig: histogram_split | 145 | Histogram-based splitting. Feature values are bucketed once into at most 256 bins; finding the best split then scans bins rather than samples.

```python title="Histogram split finding"
import numpy as np

def build_bins(X, max_bins=255):
    """Quantile-bin each feature once, before training starts."""
    edges = []
    for j in range(X.shape[1]):
        qs = np.quantile(X[:, j], np.linspace(0, 1, max_bins + 1)[1:-1])
        edges.append(np.unique(qs))
    binned = np.empty(X.shape, dtype=np.uint8)
    for j in range(X.shape[1]):
        binned[:, j] = np.searchsorted(edges[j], X[:, j], side="right")
    return binned, edges

def node_histogram(binned, rows, g, h, n_bins=256):
    """Accumulate (sum g, sum h, count) per bin per feature: theta(|rows| * d)."""
    d = binned.shape[1]
    hist_g = np.zeros((d, n_bins))
    hist_h = np.zeros((d, n_bins))
    for j in range(d):
        np.add.at(hist_g[j], binned[rows, j], g[rows])
        np.add.at(hist_h[j], binned[rows, j], h[rows])
    return hist_g, hist_h

def best_split_hist(hist_g, hist_h, lam=1.0, min_child=1.0):
    """theta(d * n_bins) -- independent of the number of samples."""
    best = (None, None, 0.0)
    for j in range(hist_g.shape[0]):
        GL = np.cumsum(hist_g[j])
        HL = np.cumsum(hist_h[j])
        G, H = GL[-1], HL[-1]
        GR, HR = G - GL, H - HL
        parent = G * G / (H + lam)
        gain = GL ** 2 / (HL + lam) + GR ** 2 / (HR + lam) - parent
        gain[(HL < min_child) | (HR < min_child)] = -np.inf
        b = int(np.argmax(gain))
        if gain[b] > best[2]:
            best = (j, b, float(gain[b]))
    return best
```

Three consequences, and they compound:

**1. Binning is done once.** $\Theta(nd \log n)$ at the start, then never
again. Feature values become `uint8`, so the training matrix shrinks by 4x
(from float32) --- a direct bandwidth win (Chapter 3).

**2. Split finding is $\Theta(d \cdot \text{bins})$, not $\Theta(nd)$.**
Once the histogram is built, finding the best split does not look at the data
at all.

**3. Histogram subtraction halves the work.** Build the histogram of the
*smaller* child by scanning its rows, then obtain the larger child's for free:
$$\text{hist}(\text{right}) = \text{hist}(\text{parent}) - \text{hist}(\text{left})$$
Since you always scan the smaller side, the total work per level is at most
half the node's rows, and the whole tree costs $\Theta(n d)$ rather than
$\Theta(nd \cdot \text{depth})$.

:::insight The accuracy cost of binning is close to zero
Quantising a feature to 255 bins loses almost nothing, because a decision
tree only ever uses a threshold --- it cannot exploit resolution finer than
the gap between adjacent training values in a region. Empirically, 255 bins
matches exact splitting to within noise on almost every dataset, while
running 10--50x faster. This is a rare case where an approximation is
essentially free.
:::

## Leaf-wise versus level-wise growth

| Strategy | Grows | Used by | Behaviour |
|---|---|---|---|
| Level-wise (depth-first by level) | all nodes at depth $\ell$ | XGBoost (default) | balanced, more robust, more wasted splits |
| Leaf-wise (best-first) | the single highest-gain leaf anywhere | LightGBM | fewer leaves for the same loss; deeper, can overfit |

@tbl: Growth strategies. Leaf-wise is greedy best-first search over leaves, so it needs `num_leaves` and `min_data_in_leaf` to control it --- `max_depth` alone is not enough.

Leaf-wise growth is maintained with a priority queue of (leaf, best gain),
which is the heap of Chapter 13: pop the best leaf, split it, push its two
children. That is the entire control structure of LightGBM's tree builder.

## Categorical features and missing values

**Categoricals.** One-hot encoding a 10,000-category feature creates 10,000
nearly-empty binary features, and a tree needs depth 10,000 to isolate one
category. The correct treatment is the *optimal partition* of categories into
two groups --- which is exponential in general, but Fisher's theorem says
that for a convex loss, sorting categories by $\sum g / \sum h$ and taking a
contiguous split of that ordering is optimal. So: sort the bins by their
gradient statistics, then run the same prefix-sum scan. $\Theta(k \log k)$
instead of $\Theta(2^k)$.

**Missing values.** Rather than imputing, learn a default direction: during
split finding, try sending all missing values left and all right, and keep
whichever gives more gain. This costs one extra pass over the histogram and
handles missingness as signal rather than noise --- which matters, because
missingness is very often informative.

:::ml Why GBDT still wins on tabular data
Neural networks have strong inductive biases for images, audio and text ---
locality, translation invariance, sequence structure. Tabular data has none
of those: columns are heterogeneous, unordered, differently scaled, and often
have sharp thresholds ("age > 65"). Trees represent axis-aligned thresholds
natively, are invariant to monotone transformations of any feature, handle
missing values and categoricals without preprocessing, and need no
normalisation. That combination is hard to beat, and repeated benchmark
studies continue to find GBDT at or above the best deep models on medium-sized
tabular datasets --- at a fraction of the training cost.
:::

:::perf Inference is where trees really shine
A trained GBDT with 500 trees of depth 6 evaluates 500 root-to-leaf paths of
6 comparisons: 3000 comparisons and 500 additions per prediction --- perhaps
2 microseconds. Compare with a small MLP: hundreds of thousands of
multiply-accumulates. This is why trees dominate latency-critical ranking
and fraud systems.

The engineering is all about branch prediction and cache: a naive pointer
tree is a chain of dependent, unpredictable loads. Production implementations
flatten trees into arrays, evaluate several trees in an interleaved loop so
independent loads overlap, and compile to branchless arithmetic on the
comparison results. QuickScorer and Treelite reach 5--10x over naive
traversal by exactly the techniques of Chapter 3.
:::

:::exercise
1. Implement exact split finding and histogram split finding, and compare
   training time and final accuracy on a dataset with $10^6$ rows.
2. Implement histogram subtraction and measure the reduction in histogram
   build time. Confirm the "always scan the smaller child" rule matters.
3. Vary `max_bins` from 8 to 1024 and plot validation accuracy against
   training time. Find the knee.
4. Derive the optimal leaf value $w^*$ and the gain formula from the
   second-order Taylor expansion of squared loss and of logistic loss.
5. Implement leaf-wise growth with a priority queue and compare tree shape
   and validation loss to level-wise at equal leaf count.
6. Implement Fisher's sorted-category split for a 5,000-category feature and
   compare to one-hot encoding in accuracy and training time.
7. Implement the learned default direction for missing values and construct a
   dataset where missingness is informative. Compare to mean imputation.
8. Flatten a trained tree ensemble into arrays and implement a branchless
   batched evaluator. Measure predictions per second against a recursive
   traversal.
:::

:::recap
- Tree induction is greedy: pick the best split by gain, recurse. Globally
  optimal trees are NP-hard.
- The gradient-boosting gain formula needs only $\sum g$ and $\sum h$ on each
  side, which is why prefix sums and histograms both work.
- Histogram binning makes split finding $\Theta(d \cdot \text{bins})$ instead
  of $\Theta(nd)$, shrinks the feature matrix to `uint8`, and costs almost no
  accuracy.
- Histogram subtraction gives the larger child's histogram for free; always
  scan the smaller child.
- Leaf-wise growth is best-first search with a priority queue; it needs leaf
  count and minimum-samples controls rather than depth alone.
- Categoricals are split optimally by sorting on $\sum g / \sum h$
  (Fisher), and missing values get a learned default direction.
- Inference is thousands of comparisons, so tree models are extremely fast to
  serve --- provided the trees are flattened and the loads overlap.
:::
