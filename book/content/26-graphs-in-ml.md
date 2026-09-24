# Graphs in Machine Learning
@short: Graphs in ML
@subtitle: PageRank, spectral methods and the sampling that makes GNNs trainable
@tier: advanced
@prereq: Chapters 22--24
@blurb: This chapter is about the graph algorithms that are themselves machine learning: random walks that compute importance, eigenvectors that reveal cluster structure, and message passing whose cost explodes unless you sample. The unifying observation is that all of them are sparse matrix operations, so the data structure from Chapter 22 --- CSR --- is what actually determines whether they run.
@objectives:
- Derive PageRank as a random walk and implement it by power iteration
- Implement personalised PageRank and use it for recommendation and retrieval
- Understand spectral clustering and what the graph Laplacian's eigenvectors mean
- Explain the neighbour explosion in GNNs and the three families of fixes
- Implement neighbour sampling and mini-batch construction for a GNN
- Estimate the cost of a graph algorithm from $V$, $E$ and the degree distribution

## Everything is a sparse matrix product

A graph with adjacency matrix $A$ turns graph algorithms into linear algebra:

| Graph operation | Linear algebra | Cost |
|---|---|---|
| One step of BFS from a frontier $x$ | $A^\top x$ (boolean semiring) | $\Theta(E)$ |
| Count paths of length $k$ | $A^k$ | $\Theta(kE)$ sparse, $\Theta(V^3\log k)$ dense |
| Random walk step | $P^\top x$ with $P = D^{-1}A$ | $\Theta(E)$ |
| GNN message passing layer | $\hat{A} X W$ | $\Theta(Ed + Vd^2)$ |
| Spectral embedding | eigenvectors of $L$ | $\Theta(E k)$ per Lanczos step |

@tbl: Graph algorithms as sparse matrix operations. Since a sparse mat-vec is $\Theta(E)$ and memory-bound, the practical cost of nearly every graph algorithm is "number of passes over the edge list".

:::insight Why CSR keeps coming back
A sparse matrix--vector product in CSR is: for each row, gather the entries
its column indices point to and accumulate. That is a sequential scan over
`indices` (good) plus a random gather from the vector (bad). The gather is
the bottleneck, which is why graph algorithms are memory-bound, why vertex
reordering (RCM, Gorder) can speed them up by 2--3x with no change to the
algorithm, and why GPU implementations obsess over coalescing.
:::

## PageRank

@fig: pagerank_flow | 145 | PageRank as a random surfer. Rank flows along out-edges and pools in well-connected regions; the damping term stops it draining into sinks.

Model a surfer who, at each step, follows a uniformly random out-link with
probability $\alpha$, and teleports to a uniformly random page with
probability $1-\alpha$. The stationary distribution of this walk is PageRank:

$$r = \alpha P^\top r + \frac{1-\alpha}{N}\mathbf{1}, \qquad P_{ij} = \frac{A_{ij}}{\deg(i)}$$

The teleport term does two jobs: it makes the chain irreducible and aperiodic
(so a unique stationary distribution exists), and it makes the iteration
contract at rate $\alpha$, so the error falls by a factor of $\alpha$ per
step. With $\alpha = 0.85$, reaching $10^{-8}$ takes
$\log(10^{-8})/\log(0.85) \approx 113$ iterations; in practice 50 is plenty.

```python title="PageRank by power iteration, with dangling-node handling"
import numpy as np

def pagerank(indptr, indices, n, alpha=0.85, iters=60, tol=1e-9):
    out_deg = np.diff(indptr).astype(np.float64)
    dangling = out_deg == 0
    r = np.full(n, 1.0 / n)
    for _ in range(iters):
        contrib = np.zeros(n)
        w = np.where(dangling, 0.0, r / np.maximum(out_deg, 1))
        np.add.at(contrib, indices, np.repeat(w, np.diff(indptr)))
        leaked = r[dangling].sum()                  # mass with nowhere to go
        new = alpha * (contrib + leaked / n) + (1 - alpha) / n
        if np.abs(new - r).sum() < tol:
            return new
        r = new
    return r
```

Dangling nodes --- vertices with no out-edges --- are the detail everyone
gets wrong. Their rank has nowhere to flow and simply disappears, so the
vector stops summing to 1 and the result is quietly wrong. Redistributing
that leaked mass uniformly is the standard fix.

:::ml Personalised PageRank is a retrieval algorithm
Replace the uniform teleport vector with a distribution concentrated on a
seed set $S$, and the stationary distribution measures *proximity to $S$*
rather than global importance. This gives:

- **Recommendation.** Seed at a user's interacted items in a bipartite
  user--item graph; the top-ranked unseen items are recommendations. This is
  Pixie, the algorithm behind Pinterest's related-pins, which runs
  approximate personalised PageRank by *sampling* random walks rather than
  iterating the matrix --- a few thousand short walks give a good top-$k$ in
  milliseconds.
- **Graph-augmented retrieval.** Seed at the entities matched by a query in
  a knowledge graph, and rank documents by the resulting mass. This captures
  multi-hop relevance that vector similarity alone misses.
- **Local clustering.** The sweep cut over a personalised PageRank vector
  finds a good local cluster around a seed without touching the whole graph
  --- $\Theta(1/\varepsilon)$ work, independent of graph size.
:::

## Spectral methods

:::definition Graph Laplacian
For an undirected graph with adjacency $A$ and degree matrix $D$, the
unnormalised Laplacian is $L = D - A$ and the symmetric normalised Laplacian
is $L_{\text{sym}} = I - D^{-1/2} A D^{-1/2}$. Both are positive
semi-definite; the multiplicity of eigenvalue 0 equals the number of
connected components.
:::

The key identity is
$$x^\top L x = \sum_{(u,v) \in E} w_{uv} (x_u - x_v)^2$$
so the quadratic form measures how much $x$ varies across edges.
Eigenvectors with small eigenvalues are therefore *smooth* over the graph:
they take similar values on connected vertices. The eigenvector of the second
smallest eigenvalue --- the **Fiedler vector** --- is the smoothest non-trivial
signal, and thresholding it gives a low-conductance cut.

```python title="Spectral clustering in a dozen lines"
import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans

def spectral_clusters(A, k):
    d = np.asarray(A.sum(axis=1)).ravel()
    d_inv_sqrt = diags(1.0 / np.sqrt(np.maximum(d, 1e-12)))
    L = diags(np.ones(A.shape[0])) - d_inv_sqrt @ A @ d_inv_sqrt
    vals, vecs = eigsh(L, k=k, sigma=0, which="LM")   # k smallest eigenpairs
    U = vecs / np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-12)
    return KMeans(n_clusters=k, n_init=10).fit_predict(U)
```

Spectral clustering finds non-convex clusters that $k$-means on raw
coordinates cannot, because it clusters in a space where the *graph* geometry
is Euclidean. Its cost is dominated by the eigendecomposition: Lanczos needs
$\Theta(Ek)$ per iteration, so it is practical to millions of edges and not
to billions.

:::insight Spectral methods, graph signal processing and GNNs are one story
$L$'s eigenvectors are a Fourier basis for signals on the graph: small
eigenvalues are low frequencies (smooth), large ones are high frequencies
(oscillating). Filtering a graph signal means reweighting its spectrum.
Evaluating a polynomial filter $\sum_k \theta_k L^k x$ needs only sparse
mat-vecs --- no eigendecomposition. A graph convolution is exactly such a
polynomial filter, usually of degree 1, and stacking $L$ layers gives a
degree-$L$ filter. That is the derivation of the GCN from spectral graph
theory, and it explains why deep GCNs over-smooth: a high-degree low-pass
filter drives every vertex toward the same value.
:::

## Message passing and the neighbour explosion

A graph neural network layer computes, for each vertex,
$$h_v^{(l+1)} = \sigma\Big( W^{(l)} \cdot \text{aggregate}\big(\{h_u^{(l)} : u \in N(v)\} \cup \{h_v^{(l)}\}\big) \Big)$$
which in matrix form is $H^{(l+1)} = \sigma(\hat{A} H^{(l)} W^{(l)})$: one
sparse mat-mat product per layer, $\Theta(Ed + Vd^2)$.

That is fine for full-graph training when the graph fits in memory. It is not
fine for mini-batch training, because computing $h_v^{(L)}$ for a single
vertex requires its entire $L$-hop neighbourhood.

@fig: gnn_sampling | 158 | The neighbour explosion. With average degree $d$, an $L$-layer GNN touches $d^L$ vertices per target. At $d = 100$ and $L = 3$ that is a million vertices --- per example in the batch.

Three families of fixes:

**Node sampling (GraphSAGE).** Sample a fixed number of neighbours per hop:
$s_1 \times s_2 \times \cdots \times s_L$ vertices per target, bounded and
tunable. Typical values are $(25, 10)$ for two layers. The estimator is
biased for mean aggregation unless you reweight, but works well in practice.

**Layer sampling (FastGCN, LADIES).** Sample a fixed set of vertices *per
layer* shared by the whole batch, with importance weights. Avoids the
exponential blow-up entirely and gives lower variance than independent node
sampling.

**Subgraph sampling (Cluster-GCN, GraphSAINT).** Partition the graph into
dense clusters (with METIS) and train on whole clusters. Every edge inside
the cluster is used with no sampling at all, so there is no neighbour
explosion and the memory is predictable; the cost is that cross-cluster
edges are dropped.

```python title="Neighbour sampling for a two-layer GNN"
import numpy as np

def sample_block(indptr, indices, seeds, fanout, rng):
    """One hop: for each seed, sample up to `fanout` neighbours."""
    src, dst = [], []
    for v in seeds:
        nbrs = indices[indptr[v]:indptr[v + 1]]
        if len(nbrs) > fanout:
            nbrs = rng.choice(nbrs, fanout, replace=False)
        src.append(nbrs)
        dst.append(np.full(len(nbrs), v))
    src = np.concatenate(src) if src else np.array([], dtype=np.int64)
    dst = np.concatenate(dst) if dst else np.array([], dtype=np.int64)
    frontier = np.unique(np.concatenate([src, np.asarray(seeds)]))
    return frontier, src, dst

def make_minibatch(indptr, indices, targets, fanouts, rng):
    blocks, seeds = [], np.asarray(targets)
    for f in reversed(fanouts):              # build from the output backwards
        frontier, src, dst = sample_block(indptr, indices, seeds, f, rng)
        blocks.append((src, dst, seeds))
        seeds = frontier
    return seeds, blocks[::-1]               # input frontier, then layers
```

:::pitfall Sampling changes what you compute
Neighbour sampling gives a *stochastic* estimate of the full-neighbourhood
aggregation. With mean aggregation and uniform sampling the estimate is
unbiased; with sum aggregation it is not, unless you rescale by
$\deg(v)/s$. Attention-based aggregation (GAT) is biased under sampling
because the softmax denominator is computed over the sample rather than the
full neighbourhood. And at *inference* time you usually want the full
neighbourhood, so a model trained with sampling and served without it sees a
distribution shift. Decide deliberately, and evaluate the served
configuration.
:::

:::ml A cost model for GNN training
For $L$ layers, hidden dimension $d$, fanouts $s_1, \ldots, s_L$ and batch
size $B$:

- Vertices touched per batch: $B \prod_i s_i$ --- this is the number that
  explodes.
- Feature-fetch bytes: $4 d B \prod_i s_i$, usually the bottleneck, and it
  is a random gather from a feature table that may not fit in GPU memory.
- FLOPs: $\Theta(B d^2 \prod_i s_i)$.

The practical consequence is that GNN training is almost always
*data-loading* bound, not compute bound, and the effective optimisations are
feature caching for high-degree vertices, quantised feature storage, and
historical embeddings (reuse a stale $h^{(l)}$ instead of recursing). Once
again the algorithm's cost is determined by memory movement rather than
arithmetic.
:::

:::exercise
1. Implement PageRank with and without dangling-node handling on a graph with
   sinks. Show that the vector stops summing to 1 without it.
2. Implement personalised PageRank two ways --- power iteration and
   random-walk sampling --- and compare the top-20 results and the runtimes
   on a graph with $10^6$ edges.
3. Compute the Fiedler vector of a two-cluster graph and show that
   thresholding it at zero recovers the clusters. Then add noise edges and
   find the point at which it fails.
4. Verify $x^\top L x = \sum_{(u,v)} (x_u - x_v)^2$ numerically, and use it
   to explain why low eigenvalues correspond to smooth signals.
5. Implement `make_minibatch` and measure the number of vertices touched for
   fanouts $(25,10)$ versus full neighbourhoods on a graph with a power-law
   degree distribution.
6. Show empirically that sum aggregation under neighbour sampling is biased,
   and that rescaling by $\deg(v)/s$ removes the bias.
7. Implement Cluster-GCN sampling with a simple graph partitioner and compare
   memory and accuracy to neighbour sampling on the same model.
8. Reorder the vertices of a large graph by BFS order and measure the change
   in sparse mat-vec throughput. Explain it using Chapter 3.
:::

:::recap
- Graph algorithms are sparse matrix operations; their cost is passes over
  the edge list and the random gathers those passes perform, so they are
  memory-bound.
- PageRank is the stationary distribution of a damped random walk, computed
  by power iteration in $\Theta(E)$ per step; handle dangling nodes or the
  mass leaks.
- Personalised PageRank measures proximity to a seed set and is a practical
  recommender and multi-hop retriever, often approximated by sampled walks.
- The graph Laplacian's small eigenvalues correspond to smooth signals; the
  Fiedler vector gives a good cut, and spectral clustering clusters in that
  embedding.
- A GCN layer is a degree-1 polynomial filter in the Laplacian; stacking
  layers raises the degree, which is why deep GCNs over-smooth.
- $L$-layer message passing touches $d^L$ vertices per target; node, layer
  and subgraph sampling are the three fixes, each with different bias.
- GNN training is usually data-loading bound; feature caching and quantised
  storage matter more than kernel optimisation.
:::
