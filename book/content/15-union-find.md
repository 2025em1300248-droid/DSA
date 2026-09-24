# Union--Find and the Algebra of Merging
@short: Union--Find
@subtitle: Twenty lines that answer "are these two things the same thing?"
@tier: core
@prereq: Chapter 12
@blurb: Disjoint-set union is the smallest data structure in this book with a genuinely surprising analysis: two one-line optimisations take it from linear to effectively constant time per operation. It is also the structure you want whenever a pipeline merges things --- connected components, clustering, deduplication groups, entity resolution --- and it is routinely reimplemented badly.
@objectives:
- Implement union--find with union by rank and path compression
- Understand the inverse Ackermann bound and why it is effectively constant
- Apply it to connected components, Kruskal's MST and cycle detection
- Build transitive deduplication clusters from pairwise near-duplicate matches
- Know the variants: weighted union, union with rollback, and the offline trick
- Recognise when union--find is the wrong tool

## The problem

You have $n$ elements, initially each in its own group, and a stream of
operations:

- `union(a, b)`: merge the groups containing $a$ and $b$.
- `find(a)`: return a canonical representative of $a$'s group, so that
  `find(a) == find(b)` exactly when $a$ and $b$ are in the same group.

The obvious implementations are all bad. A list of sets makes `union`
$\Theta(n)$. An array of group labels makes `union` $\Theta(n)$ (relabel
everything). A dict of dicts makes both slow and the memory enormous.

The right idea is to represent each group as a *tree*, where `find` walks to
the root and `union` links one root under another. Then both operations cost
the tree's depth --- and the entire art is keeping that depth small.

@fig: union_find | 132 | Left: a chain, where `find` walks three links. Right: after path compression, every node on the path points directly at the root, so all subsequent finds are constant time.

## The implementation

```python title="Union-find, complete"
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))       # parent[i] == i means i is a root
        self.rank = [0] * n                # upper bound on the tree height
        self.size = [1] * n                # component sizes, often useful
        self.components = n

    def find(self, x):                     # iterative: no recursion limit
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:      # second pass: path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                   # already together
        if self.rank[ra] < self.rank[rb]:  # union by rank: shallow under deep
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)
```

Two optimisations, each one line:

**Union by rank** attaches the shallower tree under the deeper one, so the
height only grows when two equal-height trees merge. By induction, a tree of
rank $r$ contains at least $2^r$ nodes, so the height is at most $\log_2 n$.
(Union by *size* --- attach the smaller component under the larger --- gives
the same bound and is often more convenient because you want the sizes
anyway.)

**Path compression** makes every node visited by a `find` point directly at
the root. It costs nothing extra asymptotically --- you already walked the
path --- and it makes the structure flatter every time you query it.

:::theorem Tarjan's bound
With both union by rank and path compression, any sequence of $m$ operations
on $n$ elements takes $\Theta(m \, \alpha(n))$ time, where $\alpha$ is the
inverse Ackermann function. $\alpha(n) \le 4$ for every $n$ below
$2^{2^{2^{65536}}}$, so the amortised cost is constant for any input that
exists.
:::

The proof is a sophisticated potential-function argument and is not worth
reproducing here. The takeaway is practical: **use both optimisations**.
With only one you get $\Theta(\log n)$; with neither, $\Theta(n)$ worst case.

:::pitfall Rank is not height after compression
After path compression a tree's actual height may be far below its stored
`rank`. That is fine --- `rank` remains a valid *upper bound*, which is all
the argument needs --- but do not use `rank` as if it were the true height,
and do not try to "fix it up". Also note that union by rank and path
compression interact: neither analysis alone gives the $\alpha$ bound.
:::

## The four standard applications

**Connected components.** Union every edge; the number of components is
`dsu.components` and the component of a vertex is `find(v)`. This is
$\Theta(E \alpha(V))$, which beats a BFS/DFS ($\Theta(V + E)$) only in the
*incremental* setting --- when edges arrive over time and you must answer
queries in between. For a static graph, BFS is simpler and equally fast.

**Kruskal's minimum spanning tree.** Sort edges by weight, then add each
edge whose endpoints are not already connected. Union--find is what makes
the "already connected?" test cheap. Chapter 23.

**Cycle detection in an undirected graph.** `union(u, v)` returning `False`
means $u$ and $v$ were already connected, so the edge closes a cycle.

**Equivalence closure.** Given pairwise "these two are the same" assertions
--- from a near-duplicate detector, an entity resolver, or a merge of user
accounts --- union--find computes the transitive closure in one pass.

```python title="Turning pairwise near-duplicates into clusters"
def dedup_clusters(n_docs, pairs):
    """pairs: iterable of (i, j) judged near-duplicate by LSH (Chapter 29)."""
    dsu = DSU(n_docs)
    for i, j in pairs:
        dsu.union(i, j)
    clusters = {}
    for i in range(n_docs):
        clusters.setdefault(dsu.find(i), []).append(i)
    return list(clusters.values())
```

:::ml Deduplicating a training corpus
This is the standard final step of corpus deduplication. MinHash and LSH
(Chapter 29) produce *candidate pairs* of near-duplicate documents; those
pairs form an implicit graph; union--find turns the graph into clusters; and
you keep one representative per cluster.

Two things to know. First, this is the right place for the work: the pair
list for a billion-document corpus can be tens of billions of pairs, and
union--find processes them in a single streaming pass with one array of
integers --- 4 GB for a billion documents, no graph materialised.

Second, transitivity is an *assumption*, and it is a slightly false one.
Near-duplicate is not a transitive relation: A resembles B, B resembles C,
and A and C may be quite different. Chaining through a dense region can
therefore merge a large cluster of loosely related documents. Production
pipelines cap cluster size, or cluster by connected components of a
*thresholded, mutual* $k$-nearest-neighbour graph instead.
:::

## Variants worth knowing

**Weighted / potential DSU.** Store, along with each parent pointer, an
offset relative to the parent --- a difference, a ratio, or a group element.
Then `find` accumulates the offset along the path, and you can answer "what
is $x - y$?" as well as "are $x$ and $y$ related?". This solves systems of
difference constraints and the classic "evaluate division" problem.

**DSU with rollback.** Path compression makes undo impossible, so drop it,
keep union by rank only, and push each parent change onto a stack. Each
operation is $\Theta(\log n)$ and can be undone. This enables offline
dynamic connectivity: process a query tree (segment tree on time) and roll
back on the way out.

**Persistent / partial DSU.** Store, for each union, the timestamp at which
it happened; then "were $u$ and $v$ connected at time $t$?" is answered by
walking upward while the recorded timestamps are $\le t$. Useful for
time-travel queries over a merge history.

:::warning What union--find cannot do
There is no efficient `split` or `un-union` in the plain structure --- the
relation is monotone, groups only ever merge. If your problem deletes edges,
union--find is the wrong tool; you need a link-cut tree, or the offline
segment-tree-on-time trick, or simply to rebuild. Recognising this
limitation early saves a great deal of wasted effort.
:::

:::exercise
1. Implement `DSU` without path compression and measure the average `find`
   depth after $10^6$ random unions on $10^6$ elements. Then add compression
   and measure again.
2. Prove that with union by rank, a tree of rank $r$ has at least $2^r$
   nodes, and conclude that the height is at most $\log_2 n$.
3. Implement path *halving* (`parent[x] = parent[parent[x]]` during the walk)
   and compare it to full two-pass compression in wall-clock time. Why is
   halving often faster in practice despite the same asymptotics?
4. Use union--find to implement Kruskal's algorithm and run it on a graph
   with $10^6$ edges. Profile the split between sorting and union--find.
5. Implement a weighted DSU that answers $x - y$ for a stream of constraints
   $x - y = c$, and detects contradictions.
6. Given 100 million near-duplicate pairs over 20 million documents, build
   clusters with DSU. Report memory and time. Then cap cluster size at 1000
   and describe the policy you used for choosing which merges to reject.
7. Show that the "offline dynamic connectivity" problem (edges are added and
   removed over time; answer connectivity queries) can be solved in
   $\Theta((n + q) \log q \log n)$ with DSU with rollback and a segment tree
   over time.
:::

:::recap
- Union--find represents each group as a tree; `find` walks to the root and
  `union` links roots. Cost is the depth.
- Union by rank (or size) bounds the height at $\log_2 n$; path compression
  flattens the tree on every query. Together they give $\Theta(\alpha(n))$
  amortised, which is at most 4 for any real input --- use both.
- `rank` remains a valid upper bound after compression even though the true
  height may be smaller.
- Applications: connected components (especially incremental), Kruskal's
  MST, undirected cycle detection, and equivalence closure.
- Corpus deduplication uses DSU to turn LSH candidate pairs into clusters in
  one streaming pass; beware that near-duplicate is not really transitive.
- Variants: weighted DSU for offsets, rollback DSU for undo and offline
  dynamic connectivity, timestamped DSU for time-travel queries.
- There is no efficient split; if your problem removes edges, use a
  different structure.
:::
