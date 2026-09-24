# Nearest-Neighbour Search and the Curse of Dimensionality
@short: Nearest Neighbours
@subtitle: Why the obvious data structures stop working above twenty dimensions
@tier: advanced
@prereq: Chapters 12, 21
@blurb: Nearest-neighbour search is the operation underneath retrieval, recommendation, clustering and deduplication. In two dimensions it is a solved problem with a beautiful data structure. In seven hundred and sixty-eight dimensions --- which is where your embeddings live --- that data structure is slower than a linear scan, for reasons worth understanding precisely.
@objectives:
- State the exact and approximate nearest-neighbour problems and their cost
- Implement a k-d tree and understand its pruning rule
- Explain the curse of dimensionality quantitatively, not just as a slogan
- Know when brute force is genuinely the right answer
- Understand distance metrics and their normalisation traps
- Set up the approximate methods that Chapter 33 develops

## The problem and the honest baseline

:::definition Nearest-neighbour search
Given a set $X$ of $n$ points in $\mathbb{R}^d$ and a query $q$, find the
$k$ points of $X$ minimising a distance $D(q, \cdot)$. The **approximate**
version asks only for points within a factor $(1+\varepsilon)$ of the true
nearest distance, or --- more usefully in practice --- for a set whose
*recall* against the true top-$k$ exceeds a target.
:::

The baseline is brute force, and it is much better than people expect,
because it is one matrix multiply.

```python title="Brute-force top-k: the baseline you must beat"
import numpy as np

def brute_force_topk(X, Q, k=10, normalised=True):
    """X: (n, d) database.  Q: (m, d) queries.  Returns (m, k) indices."""
    if normalised:                       # cosine == inner product
        scores = Q @ X.T                 # (m, n) -- one GEMM
    else:                                # squared L2 without materialising diffs
        scores = -(np.einsum("ij,ij->i", Q, Q)[:, None]
                   - 2 * Q @ X.T
                   + np.einsum("ij,ij->i", X, X)[None, :])
    idx = np.argpartition(-scores, k, axis=1)[:, :k]     # theta(nm)
    rows = np.arange(len(Q))[:, None]
    return idx[rows, np.argsort(-scores[rows, idx], axis=1)]
```

:::perf When brute force is the right answer
Cost is $\Theta(nmd)$ FLOPs, and a modern CPU does about $10^{11}$ FLOP/s
with a good BLAS; a GPU does $10^{14}$.

- $n = 10^5$, $d = 768$, one query: 77 MFLOP, about 1 ms on CPU. **Use
  brute force.**
- $n = 10^6$, $d = 768$, one query: 770 MFLOP, about 8 ms on CPU, 0.1 ms on
  GPU. **Still fine**, especially batched.
- $n = 10^8$, $d = 768$: 77 GFLOP per query, and 300 GB of memory. **Now you
  need an index.**

The memory limit usually bites before the compute limit. Note also that the
identity in the code --- expanding $\|q - x\|^2$ --- is what turns a
distance computation into a GEMM; computing differences explicitly would
allocate an $(m, n, d)$ tensor and exhaust memory (Chapter 4).
:::

## k-d trees

A k-d tree partitions space by axis-aligned splits: at depth $\ell$, split on
axis $\ell \bmod d$ at the median.

```python title="k-d tree with the pruning rule that makes it work"
import numpy as np

class KDTree:
    def __init__(self, points, indices=None, depth=0, leaf_size=16):
        indices = np.arange(len(points)) if indices is None else indices
        self.axis = depth % points.shape[1]
        self.leaf = len(indices) <= leaf_size
        if self.leaf:
            self.indices = indices
            return
        order = indices[np.argsort(points[indices, self.axis])]
        mid = len(order) // 2
        self.split = points[order[mid], self.axis]
        self.point_idx = order[mid]
        self.left = KDTree(points, order[:mid], depth + 1, leaf_size)
        self.right = KDTree(points, order[mid + 1:], depth + 1, leaf_size)

    def query(self, points, q, k, heap=None):
        import heapq
        heap = [] if heap is None else heap
        if self.leaf:
            for i in self.indices:
                d = -np.sum((points[i] - q) ** 2)
                if len(heap) < k:
                    heapq.heappush(heap, (d, int(i)))
                elif d > heap[0][0]:
                    heapq.heapreplace(heap, (d, int(i)))
            return heap
        d = -np.sum((points[self.point_idx] - q) ** 2)
        if len(heap) < k:
            heapq.heappush(heap, (d, int(self.point_idx)))
        elif d > heap[0][0]:
            heapq.heapreplace(heap, (d, int(self.point_idx)))
        diff = q[self.axis] - self.split
        near, far = (self.left, self.right) if diff < 0 else (self.right, self.left)
        near.query(points, q, k, heap)
        # THE PRUNING RULE: can anything on the far side beat the worst so far?
        if len(heap) < k or diff ** 2 < -heap[0][0]:
            far.query(points, q, k, heap)
        return heap
```

The pruning test is the whole algorithm: if the squared distance from the
query to the splitting *plane* already exceeds the distance to the current
$k$-th best point, the entire far subtree can be skipped. In two dimensions
this fires almost always and the query is $\Theta(\log n)$. In high
dimensions it almost never fires.

## The curse of dimensionality, quantitatively

@fig: curse_dimensions | 138 | Two views of the same phenomenon. Left: the relative gap between the nearest and farthest neighbour shrinks as $d$ grows. Right: in high dimensions nearly all of a cube's volume is near its surface, so a query's neighbourhood almost always straddles a split.

Three facts, each sufficient on its own to kill spatial trees.

**1. Distance concentration.** For i.i.d. random points, the ratio
$$\frac{\max_i \|q - x_i\| - \min_i \|q - x_i\|}{\min_i \|q - x_i\|} \to 0
\quad \text{as } d \to \infty$$
at rate roughly $1/\sqrt{d}$. At $d = 1000$ the nearest and farthest points
differ by a few percent, so "nearest" becomes a statement about noise. (Real
embeddings are not i.i.d. --- they lie on a much lower-dimensional manifold
--- which is exactly why nearest-neighbour search still works at all.)

**2. Volume concentrates at the surface.** The fraction of a unit cube within
$\epsilon$ of its boundary is $1 - (1-2\epsilon)^d$. At $\epsilon = 0.05$ and
$d = 100$, that is 99.997%. A query ball therefore almost always crosses many
splitting planes.

**3. The pruning test fails.** A k-d tree must examine both sides whenever
the query ball crosses the split, and by fact 2 it nearly always does. The
expected number of leaves examined grows roughly as $2^d$ until it saturates
at "all of them". Empirically, k-d trees beat a linear scan up to about
$d = 20$ and lose beyond it --- and they lose while also adding a pointer
structure with terrible cache behaviour (Chapter 3).

| Structure | Good to about | Fails because |
|---|---|---|
| k-d tree | $d \approx 20$ | axis-aligned splits; pruning stops firing |
| Ball tree | $d \approx 30$ | tighter bounds, but same concentration |
| Cover tree | intrinsic dimension | good when data lies on a low-dim manifold |
| VP tree | $d \approx 30$ | metric-only; same limits |
| R-tree | $d \approx 10$ | designed for spatial extents, not points |
| Brute force | any $d$ | $\Theta(nd)$ always, but cache-perfect and vectorised |
| LSH / IVF / PQ / HNSW | any $d$ | approximate, Chapter 33 |

@tbl: Exact spatial indexes and where they stop. Above roughly 30 dimensions, the only options are brute force and approximation.

:::insight The one-sentence version
There is no known exact nearest-neighbour structure that beats a linear scan
in high dimensions, and there are theoretical reasons (hardness results based
on the Strong Exponential Time Hypothesis) to believe none exists. So
high-dimensional nearest-neighbour search is *necessarily* approximate ---
which is why every vector database exposes a recall knob.
:::

## Intrinsic dimension

The saving grace is that real data is not uniformly distributed in
$\mathbb{R}^{768}$. Embeddings lie near a manifold of much lower *intrinsic*
dimension --- typically 10--50 for text and image embeddings --- and all
practical methods exploit that.

```python title="Estimating intrinsic dimension (two-NN estimator)"
import numpy as np

def intrinsic_dimension(X, sample=5000, rng=np.random):
    """Facco et al. two-NN estimator: robust and needs only the two
    nearest neighbours of each sampled point."""
    idx = rng.choice(len(X), size=min(sample, len(X)), replace=False)
    S = X[idx]
    d2 = ((S[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    d2.sort(axis=1)
    r1, r2 = np.sqrt(d2[:, 1]), np.sqrt(d2[:, 2])    # skip self at index 0
    mu = r2 / np.maximum(r1, 1e-12)
    mu = np.sort(mu)
    F = np.arange(1, len(mu) + 1) / len(mu)
    x = np.log(mu[:-1])
    y = -np.log(1 - F[:-1])
    return float(np.dot(x, y) / np.dot(x, x))        # slope through origin
```

If the estimate comes back near 10, an index will work very well; if it comes
back near 100, expect to need many more probes for the same recall. It is
worth measuring before choosing an index configuration.

## Metrics and their traps

| Metric | Formula | Notes |
|---|---|---|
| Euclidean (L2) | $\|q-x\|_2$ | the default; sensitive to vector norm |
| Squared L2 | $\|q-x\|_2^2$ | same ordering, no `sqrt` --- always use this |
| Cosine | $1 - \frac{q \cdot x}{\|q\|\|x\|}$ | scale-invariant; the usual choice for embeddings |
| Inner product | $-q \cdot x$ | **not a metric**: no triangle inequality |
| Manhattan (L1) | $\sum_i \|q_i - x_i\|$ | more robust in high $d$ |
| Hamming | bits differing | for binary codes |

@tbl: Distance measures. Squared L2 preserves ordering and saves a square root per comparison; always use it for ranking.

:::pitfall Maximum inner product search is not nearest-neighbour search
If you normalise vectors, cosine similarity and Euclidean distance induce the
same ranking ($\|q - x\|^2 = 2 - 2q\cdot x$ for unit vectors), and every
index works. If you do *not* normalise --- because vector norm encodes
something, as it does in some recommender models --- then maximum inner
product search (MIPS) is a genuinely different problem. It has no triangle
inequality, so tree pruning and graph-based methods lose their correctness
argument. The standard fix is a transformation that converts MIPS into
ordinary nearest-neighbour search by appending a component that absorbs the
norm. Check your index's documentation: many silently assume normalised
vectors.
:::

:::ml Practical guidance
- **Normalise once, at write time.** Store unit vectors, use inner product,
  and never think about it again.
- **Use float32, or less.** float64 doubles bandwidth for no recall benefit
  (Chapter 3). float16 or int8 halves or quarters it again with a small,
  measurable recall cost.
- **Measure recall, not "approximate-ness".** The useful metric is
  recall@$k$ against a brute-force ground truth on a sample of a few
  thousand queries. Compute it whenever you change any index parameter.
- **Rerank.** Retrieve 5--10x more candidates with the cheap index, then
  rescore them exactly with the full-precision vectors. This recovers almost
  all the recall lost to quantisation at a negligible cost, and it is the
  single most valuable trick in the area.
:::

:::exercise
1. Measure brute-force query time for $n \in \{10^4, 10^5, 10^6\}$ at
   $d = 768$ on CPU and on GPU, batched and unbatched. Find your crossover
   into "needs an index".
2. Implement the k-d tree and measure the fraction of leaves visited as $d$
   grows from 2 to 64 at fixed $n$. Plot it against a linear scan.
3. Verify distance concentration: for $d \in \{2, 10, 100, 1000\}$, sample
   $10^4$ uniform points and plot the distribution of
   $(d_{\max} - d_{\min})/d_{\min}$.
4. Estimate the intrinsic dimension of a real embedding set (any
   sentence-transformer output) and compare it to the ambient dimension.
5. Show that for unit vectors, ranking by squared L2 and by inner product
   give identical orderings. Then construct non-unit vectors where they
   differ.
6. Implement rerank-after-retrieve on top of a quantised index and measure
   the recall gained as a function of the over-retrieval factor.
7. Show empirically that a k-d tree over 20-dimensional data lying on a
   3-dimensional manifold performs like 3-dimensional data, not
   20-dimensional.
:::

:::recap
- Brute-force search is one GEMM and is the right answer up to roughly
  $10^6$ vectors; memory usually binds before compute.
- k-d trees prune by comparing the distance to the splitting plane against
  the current $k$-th best; this test stops firing above about 20 dimensions.
- The curse of dimensionality is three concrete facts: distances concentrate,
  volume moves to the surface, and pruning therefore fails.
- No exact high-dimensional structure beats a linear scan, so practical
  methods are approximate and expose a recall knob.
- Real embeddings have low intrinsic dimension, which is why approximate
  methods work at all; measure it before tuning an index.
- Normalise at write time and use inner product; use squared L2 for ranking;
  MIPS on unnormalised vectors is a different problem.
- Over-retrieve and rerank with exact vectors: the cheapest large recall win
  available.
:::
