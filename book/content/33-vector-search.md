# Vector Search in Production: IVF, PQ, HNSW, DiskANN
@short: Vector Search
@subtitle: The algorithms inside every vector database
@tier: expert
@prereq: Chapter 32
@blurb: This is the chapter that explains what your vector database is actually doing. Four ideas --- partition the space, compress the vectors, navigate a graph, and put it on disk --- combine into every index you will meet. Understanding them turns a set of opaque parameters into a set of decisions you can reason about.
@objectives:
- Build and tune an IVF index and reason about `nlist` and `nprobe`
- Explain product quantisation, its memory arithmetic and its asymmetric distance computation
- Implement HNSW search and explain the role of $M$ and `efSearch`
- Choose an index for a given corpus size, memory budget and recall target
- Understand filtered search, updates and deletion --- the parts that are actually hard
- Reason about disk-resident indexes and the IOPS constraint

## The four ideas

| Idea | Mechanism | Buys you | Costs you |
|---|---|---|---|
| Partition | cluster the space, probe a few cells (IVF) | scan 1% of the data | recall at cell boundaries |
| Compress | quantise vectors to bytes (PQ, SQ, binary) | 4--64x memory | precision |
| Navigate | greedy walk on a proximity graph (HNSW) | $\Theta(\log n)$ hops, high recall | memory, build time |
| Externalise | keep vectors on SSD, graph in RAM (DiskANN) | 10--100x capacity | one random read per hop |

@tbl: Every production index is a combination of these four. `IVF4096,PQ64` is partition + compress; `HNSW32,SQ8` is navigate + compress; DiskANN is navigate + externalise.

## IVF: partition the space

@fig: ivf_pq | 218 | Top: an inverted file index clusters the vectors and probes only the cells nearest the query. Bottom: product quantisation splits each vector into sub-vectors and replaces each with a one-byte codebook index.

```python title="An IVF index, in full"
import numpy as np

class IVFIndex:
    def __init__(self, nlist=1024, seed=0):
        self.nlist, self.seed = nlist, seed

    def train(self, X, iters=20):
        rng = np.random.default_rng(self.seed)
        self.centroids = X[rng.choice(len(X), self.nlist, replace=False)].copy()
        for _ in range(iters):                       # Lloyd's algorithm
            assign = self._assign(X)
            for c in range(self.nlist):
                members = X[assign == c]
                if len(members):
                    self.centroids[c] = members.mean(axis=0)
        return self

    def _assign(self, X, nprobe=1):
        sims = X @ self.centroids.T                  # unit vectors assumed
        if nprobe == 1:
            return sims.argmax(axis=1)
        return np.argpartition(-sims, nprobe, axis=1)[:, :nprobe]

    def add(self, X, ids):
        assign = self._assign(X)
        self.lists = [[] for _ in range(self.nlist)]
        self.vecs = [[] for _ in range(self.nlist)]
        for i, c in enumerate(assign):
            self.lists[c].append(ids[i])
            self.vecs[c].append(X[i])
        self.vecs = [np.asarray(v) if v else np.zeros((0, X.shape[1]),
                     dtype=X.dtype) for v in self.vecs]
        self.lists = [np.asarray(l, dtype=np.int64) for l in self.lists]
        return self

    def search(self, q, k=10, nprobe=8):
        cells = np.argpartition(-(q @ self.centroids.T), nprobe)[:nprobe]
        cand_ids, cand_scores = [], []
        for c in cells:
            if len(self.lists[c]):
                cand_ids.append(self.lists[c])
                cand_scores.append(self.vecs[c] @ q)
        if not cand_ids:
            return np.array([], dtype=np.int64)
        ids = np.concatenate(cand_ids)
        scores = np.concatenate(cand_scores)
        top = np.argpartition(-scores, min(k, len(scores) - 1))[:k]
        return ids[top[np.argsort(-scores[top])]]
```

**Tuning.** Set $\text{nlist} \approx \sqrt{n}$ (so each cell holds about
$\sqrt n$ vectors) --- 4096 for a million, 65536 for a hundred million.
`nprobe` then trades recall for latency: 1 is fast and poor, 8--32 is the
usual operating range, and `nprobe = nlist` degenerates to brute force.

:::pitfall The boundary problem
A vector near a cell boundary may be the true nearest neighbour of a query
in an adjacent cell that you did not probe. This is the *only* source of
recall loss in a plain IVF index, and it is why recall improves so smoothly
with `nprobe`. Training the centroids on a representative sample (100--200
vectors per centroid is plenty) matters more than the number of $k$-means
iterations.
:::

## Product quantisation: compress the vectors

An IVF index still stores every vector at full precision --- 768 float32
values, 3 KB each, so 300 GB for $10^8$ vectors. Product quantisation makes
that 8 bytes.

:::definition Product quantisation
Split each $d$-dimensional vector into $m$ sub-vectors of $d/m$ dimensions.
Run $k$-means with $2^b$ centroids (usually $b = 8$, so 256) independently on
each sub-space. Represent a vector by the $m$ codes of its nearest
sub-centroids: $mb$ bits total. The effective codebook size is $2^{mb}$ ---
$2^{64}$ for $m = 8$, $b = 8$ --- from only $m \cdot 2^b = 2048$ stored
centroids.
:::

```python title="Product quantisation with asymmetric distance computation"
import numpy as np

class PQ:
    def __init__(self, m=8, nbits=8, seed=0):
        self.m, self.k = m, 1 << nbits
        self.seed = seed

    def train(self, X, iters=25):
        n, d = X.shape
        self.dsub = d // self.m
        rng = np.random.default_rng(self.seed)
        self.codebooks = np.zeros((self.m, self.k, self.dsub), dtype=np.float32)
        for j in range(self.m):
            sub = X[:, j * self.dsub:(j + 1) * self.dsub]
            C = sub[rng.choice(n, self.k, replace=False)].copy()
            for _ in range(iters):
                a = np.argmin(((sub[:, None, :] - C[None, :, :]) ** 2).sum(-1),
                              axis=1)
                for c in range(self.k):
                    members = sub[a == c]
                    if len(members):
                        C[c] = members.mean(axis=0)
            self.codebooks[j] = C
        return self

    def encode(self, X):
        codes = np.empty((len(X), self.m), dtype=np.uint8)
        for j in range(self.m):
            sub = X[:, j * self.dsub:(j + 1) * self.dsub]
            d2 = ((sub[:, None, :] - self.codebooks[j][None]) ** 2).sum(-1)
            codes[:, j] = d2.argmin(axis=1)
        return codes                                  # (n, m) bytes

    def distance_table(self, q):
        """ADC: precompute q's distance to every sub-centroid. theta(k*d)."""
        return np.stack([
            ((q[j * self.dsub:(j + 1) * self.dsub][None] -
              self.codebooks[j]) ** 2).sum(-1)
            for j in range(self.m)])                  # (m, k)

    def search(self, codes, q, k=10):
        table = self.distance_table(q)                # once per query
        d2 = table[np.arange(self.m), codes.T].sum(axis=0)   # m adds per vector
        top = np.argpartition(d2, k)[:k]
        return top[np.argsort(d2[top])]
```

:::insight Asymmetric distance computation is the whole point
The query is *not* quantised. We build an $m \times 256$ table of distances
from the query's sub-vectors to every sub-centroid, then each database
vector's distance is $m$ table lookups and $m$ additions --- 8 operations
instead of 768 multiply-adds, and the data read per vector is 8 bytes
instead of 3072. It is roughly 100x less memory traffic, which on
memory-bound hardware (Chapter 3) is roughly a 100x speedup. Keeping the
query unquantised is what makes the estimate accurate enough to be useful.
:::

:::perf The memory arithmetic that drives index choice
For $10^8$ vectors of dimension 768:

| Storage | Bytes/vector | Total | Recall@10 (typical) |
|---|---:|---:|---|
| float32 | 3072 | 307 GB | 1.00 (exact) |
| float16 | 1536 | 154 GB | ~1.00 |
| int8 (scalar quant.) | 768 | 77 GB | 0.97--0.99 |
| PQ, m=64, 8 bits | 64 | 6.4 GB | 0.90--0.95 |
| PQ, m=16, 8 bits | 16 | 1.6 GB | 0.70--0.85 |
| Binary (1 bit/dim) | 96 | 9.6 GB | 0.60--0.80 (rerank!) |

Every row below float16 should be paired with reranking: retrieve $5k$
candidates with the compressed representation, then rescore those with
full-precision vectors fetched from disk. Recall usually returns to within a
point or two of exact.
:::

## HNSW: navigate a graph

@fig: hnsw_layers | 165 | HNSW. Higher layers are sparse and have long-range links for fast global movement; layer 0 contains every vector with short links for local refinement. A search descends layer by layer.

:::definition Hierarchical navigable small world
A multi-layer proximity graph. Each vector appears in layer 0 and, with
probability $p^\ell$, in layers $1 \ldots \ell$. Within a layer, each node
links to about $M$ approximate nearest neighbours, pruned by a *diversity*
heuristic that keeps links pointing in different directions. Search starts at
the top layer's entry point and greedily descends.
:::

```python title="HNSW search: two heaps and a greedy walk"
import heapq

def search_layer(graph, vectors, q, entry_points, ef, layer):
    """Returns the ef closest nodes found in this layer."""
    visited = set(entry_points)
    candidates = []                       # min-heap by distance: what to expand
    results = []                          # max-heap by distance: what to keep
    for ep in entry_points:
        d = dist(q, vectors[ep])
        heapq.heappush(candidates, (d, ep))
        heapq.heappush(results, (-d, ep))
    while candidates:
        d, c = heapq.heappop(candidates)
        if d > -results[0][0] and len(results) >= ef:
            break                         # the nearest candidate is worse than
                                          # our worst keeper: stop
        for nbr in graph[layer][c]:
            if nbr in visited:
                continue
            visited.add(nbr)
            dn = dist(q, vectors[nbr])
            if len(results) < ef or dn < -results[0][0]:
                heapq.heappush(candidates, (dn, nbr))
                heapq.heappush(results, (-dn, nbr))
                if len(results) > ef:
                    heapq.heappop(results)
    return [(-d, i) for d, i in results]

def hnsw_search(graph, vectors, q, k, ef_search, entry, max_layer):
    ep = [entry]
    for layer in range(max_layer, 0, -1):
        ep = [max(search_layer(graph, vectors, q, ep, 1, layer))[1]]
    found = search_layer(graph, vectors, q, ep, max(ef_search, k), 0)
    return [i for _, i in sorted(found)[:k]]
```

Two heaps: a min-heap of candidates to expand, and a bounded max-heap of the
`ef` best found so far. The termination test --- "the closest unexpanded
candidate is farther than our worst keeper" --- is what makes it terminate
quickly. This is best-first search (Chapter 23) with a bounded frontier.

**Parameters.** $M$ (links per node, 16--64) controls memory and recall:
memory is $\approx 8Mn$ bytes for the graph alone, so $M = 32$ on $10^8$
vectors is 25 GB *before* the vectors. `efConstruction` (100--500) controls
build quality and build time; `efSearch` ($\ge k$, typically 50--200) is the
runtime recall/latency knob.

:::pitfall HNSW's real costs
**Memory.** The graph is often larger than compressed vectors. HNSW with
$M=32$ plus PQ codes can be dominated by the graph.

**Build time.** $\Theta(n \log n)$ distance computations with a large
constant; hours for $10^8$ vectors.

**Deletion.** There is no clean removal --- deleting a node breaks the
connectivity its links provided. Implementations use tombstones and
periodic rebuilds. If your corpus has high churn, this is the constraint
that decides your architecture.

**Filtered search.** "Nearest neighbours where `tenant_id = 42`" is genuinely
hard: filtering *after* search returns too few results, and filtering
*during* the graph walk can disconnect the graph so the walk gets stuck. The
practical answers are partitioned indexes per high-cardinality filter value,
or pre-filtering into a candidate id set and brute-forcing when it is small.
Always check how your database implements this before designing around it.
:::

## Choosing an index

| Situation | Index | Why |
|---|---|---|
| $n < 10^5$, any $d$ | brute force | exact, simple, fast enough |
| $n < 10^7$, memory plentiful | HNSW (flat) | best recall/latency, no training |
| $n < 10^7$, memory tight | IVF + PQ | 10--60x compression |
| $n > 10^8$, memory tight | IVF-PQ, or HNSW + PQ | partition and compress |
| $n > 10^9$, one machine | DiskANN / SPANN | graph in RAM, vectors on SSD |
| High churn (frequent deletes) | IVF | rebuilding one cell is cheap |
| Heavy metadata filtering | partitioned IVF | filter selects cells |
| GPU available, batch queries | brute force or IVF-flat on GPU | GEMM throughput wins |

@tbl: Index selection. The two questions that decide it are "does it fit in memory?" and "how much does the corpus change?"

:::ml DiskANN and the IOPS constraint
DiskANN keeps a graph in memory (with PQ codes for cheap approximate distance
ranking) and full-precision vectors on SSD. Each hop of the search does one
random SSD read of one node's neighbours and vector. A query making 100 hops
therefore needs 100 random reads; at 100 microseconds each *sequentially*
that is 10 ms, which is too slow --- so the reads must be issued
concurrently, with a deep queue, which is exactly Chapter 31's point about
IOPS versus bandwidth.

The design consequence is that DiskANN's graph is built to be *short*:
a single flat graph with careful long-range pruning rather than HNSW's
layers, tuned to minimise the number of hops rather than the work per hop.
When the bottleneck is random reads, the algorithm optimises for read count.
:::

:::exercise
1. Build an IVF index over $10^6$ random 128-dimensional vectors. Plot
   recall@10 against `nprobe` for `nlist` $\in \{256, 1024, 4096\}$ and find
   the knee.
2. Implement PQ and measure the recall loss as $m$ goes from 4 to 64 at
   $d = 128$. Then add reranking with the exact vectors and re-measure.
3. Verify the asymmetric-distance speedup: time PQ search against exact
   search on the same candidates, and attribute the gap to memory traffic.
4. Implement `search_layer` and measure the number of distance computations
   per query against `efSearch`. Plot it against recall.
5. Compute the total memory of HNSW($M{=}32$) plus PQ($m{=}64$) for $10^8$
   vectors at $d = 768$, and compare to IVF-PQ with the same PQ settings.
6. Implement filtered search three ways --- post-filter, pre-filter with
   brute force, and a partitioned index --- and compare recall and latency as
   the filter selectivity goes from 100% to 0.1%.
7. Build an index, delete 30% of the vectors with tombstones, and measure how
   recall and latency degrade before a rebuild.
8. Given 500M vectors at $d = 1024$, a 64 GB RAM budget, a 10 ms p99 target
   and a 0.9 recall@10 requirement: choose an index, state every parameter,
   and justify the memory arithmetic.
:::

:::recap
- Every production vector index combines four ideas: partition, compress,
  navigate, externalise.
- IVF clusters the space and probes `nprobe` cells; set
  $\text{nlist} \approx \sqrt n$ and tune `nprobe` for recall. Its only
  recall loss is at cell boundaries.
- PQ splits vectors into sub-vectors and stores one byte per sub-vector,
  giving 64x compression; asymmetric distance computation keeps the query
  unquantised and turns search into table lookups and additions.
- HNSW is best-first search on a layered proximity graph with two heaps; $M$
  sets memory and recall ceiling, `efSearch` is the runtime knob.
- HNSW's real costs are memory, build time, deletion and filtered search ---
  not query latency.
- Index choice is decided by whether the data fits in memory and how much it
  changes.
- Disk-resident indexes optimise for the *number* of random reads, because
  IOPS and queue depth are the binding constraint.
- Over-retrieve and rerank with exact vectors after any compression.
:::
