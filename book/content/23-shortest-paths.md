# Shortest Paths, Minimum Spanning Trees and A*
@short: Shortest Paths
@subtitle: Weighted traversal, and what a good heuristic buys you
@tier: core
@prereq: Chapters 13, 22
@blurb: Once edges have weights, BFS stops working and a family of algorithms takes over, each making a different assumption about the weights in exchange for a different running time. This chapter covers the four you need, the one that handles negative weights, the two minimum-spanning-tree algorithms, and A* --- which is the bridge between classical search and the heuristic search inside modern systems.
@objectives:
- Implement Dijkstra's algorithm with a priority queue and understand why it needs non-negative weights
- Use Bellman--Ford for negative weights and negative-cycle detection
- Compute all-pairs shortest paths with Floyd--Warshall and know when it wins
- Implement A* and state the admissibility and consistency conditions
- Implement Kruskal and Prim for minimum spanning trees
- Recognise these algorithms inside routing, scheduling and retrieval systems

## Why BFS stops working

BFS explores in order of *hop count*. With weights, the fewest-hops path is
often not the cheapest: a single edge of weight 100 versus two edges of
weight 1 each. The fix is to explore in order of *accumulated cost*, which
means replacing the queue with a priority queue --- one line, again.

| Algorithm | Weights | Time | Space | Gives |
|---|---|---|---|---|
| BFS | unweighted | $\Theta(V+E)$ | $\Theta(V)$ | single-source shortest paths |
| 0-1 BFS | weights in $\{0,1\}$ | $\Theta(V+E)$ | $\Theta(V)$ | same, using a deque |
| Dijkstra | non-negative | $\Theta((V+E)\log V)$ | $\Theta(V)$ | single-source |
| Bellman--Ford | any | $\Theta(VE)$ | $\Theta(V)$ | single-source + negative-cycle detection |
| SPFA | any | $\Theta(VE)$ worst, fast in practice | $\Theta(V)$ | single-source |
| Floyd--Warshall | any (no negative cycle) | $\Theta(V^3)$ | $\Theta(V^2)$ | all pairs |
| Johnson | any | $\Theta(VE + V^2\log V)$ | $\Theta(V^2)$ | all pairs, sparse graphs |
| A* | non-negative + heuristic | $\Theta((V+E)\log V)$ worst | $\Theta(V)$ | single pair, much faster in practice |
| DAG relaxation | any, but acyclic | $\Theta(V+E)$ | $\Theta(V)$ | single-source, longest path too |

@tbl: The shortest-path family. The last row is worth remembering: on a DAG you can relax edges in topological order and handle negative weights in linear time, which is why DP on a DAG (Chapter 18) is so cheap.

## Dijkstra

@fig: dijkstra_step | 142 | Dijkstra settles vertices in increasing order of distance. Once a vertex is settled, its distance is final --- a claim that is only true when weights are non-negative.

```python title="Dijkstra with lazy deletion"
import heapq

def dijkstra(indptr, indices, weights, src):
    n = len(indptr) - 1
    dist = [float("inf")] * n
    parent = [-1] * n
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]:
            continue                       # stale entry: skip it
        for i in range(indptr[v], indptr[v + 1]):
            u, w = indices[i], weights[i]
            nd = d + w
            if nd < dist[u]:
                dist[u] = nd
                parent[u] = v
                heapq.heappush(pq, (nd, u))     # lazy: no decrease-key
    return dist, parent
```

:::proof Why non-negative weights are required
The invariant is: when a vertex $v$ is popped with distance $d$, $d$ is the
true shortest distance to $v$. Suppose not --- some shorter path $P$ to $v$
exists. $P$ must leave the settled set at some edge $(x, y)$ where $x$ is
settled and $y$ is not. Then $\text{dist}[y] \le \text{dist}[x] + w(x,y) \le
\text{length of } P \le d$. Since $y$ is still in the queue with a key no
larger than $d$, and we popped $v$ instead, we have $\text{dist}[y] \ge d$,
so the whole prefix has length exactly $d$ and the remainder of $P$ has
length $\le 0$. With non-negative weights that remainder is exactly 0, so
$P$ is no shorter after all. With a negative edge, the remainder can be
negative and the invariant fails.
:::

The lazy-deletion pattern is worth internalising: rather than a
`decrease-key` operation (which needs an indexed heap, Chapter 13), push a
new entry and discard stale ones on pop. The heap holds $O(E)$ entries
instead of $O(V)$, but the constant factors are much better and the code is
half the length.

:::ml Dijkstra-shaped problems in ML systems
**Best-first decoding.** Replacing beam search's fixed width with a priority
queue over partial hypotheses ordered by score gives A*-style decoding, which
with an admissible heuristic returns the true best sequence.

**Cheapest execution plan.** Choosing among fused kernel implementations, or
among quantisation levels per layer under a latency budget, is a shortest
path over a layered DAG --- and being a DAG, it is linear-time.

**Graph-based retrieval.** HNSW's search is a greedy variant of this loop
with a bounded candidate heap; the "settled" set is the result heap.
:::

## Bellman--Ford and negative weights

Bellman--Ford relaxes *every* edge, $V-1$ times. After $k$ rounds, every
shortest path using at most $k$ edges has been found; since a simple path
uses at most $V-1$ edges, $V-1$ rounds suffice.

```python title="Bellman-Ford with negative-cycle detection"
def bellman_ford(n, edges, src):
    dist = [float("inf")] * n
    dist[src] = 0.0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break                          # early exit: converged
    for u, v, w in edges:                  # one more round
        if dist[u] + w < dist[v]:
            return None                    # still improving: negative cycle
    return dist
```

The negative-cycle check is not an afterthought --- it is often the *point*.
Detecting a negative cycle finds an arbitrage opportunity in a currency
graph, an inconsistent set of difference constraints in a scheduler, and an
unsatisfiable constraint system in a solver.

## A*: Dijkstra with a conscience

A* orders the priority queue by $f(v) = g(v) + h(v)$, where $g$ is the cost
so far and $h$ is an estimate of the remaining cost.

:::definition Admissible and consistent heuristics
$h$ is **admissible** if $h(v) \le$ the true remaining cost for every $v$:
it never overestimates. Admissibility guarantees A* returns an optimal path.

$h$ is **consistent** (monotone) if $h(u) \le w(u,v) + h(v)$ for every edge.
Consistency implies admissibility and additionally guarantees that each
vertex is settled only once --- so A* with a consistent heuristic is exactly
Dijkstra on a reweighted graph, with the same complexity bound and a much
smaller explored set.
:::

With $h \equiv 0$, A* *is* Dijkstra. With a perfect $h$, it walks straight to
the goal. Everything useful is in between, and the quality of $h$ is the
whole engineering problem: for road routing, straight-line distance divided
by the maximum speed; for puzzles, the sum of Manhattan distances; for
sequence decoding, an optimistic bound on the remaining log-probability.

```python title="A* over an implicit graph"
import heapq

def astar(start, goal, neighbours, h):
    g = {start: 0.0}
    pq = [(h(start), 0.0, start, None)]
    came = {}
    while pq:
        f, gv, v, parent = heapq.heappop(pq)
        if v in came:
            continue
        came[v] = parent
        if v == goal:
            path, cur = [], v
            while cur is not None:
                path.append(cur); cur = came[cur]
            return path[::-1], gv
        for u, w in neighbours(v):
            ng = gv + w
            if ng < g.get(u, float("inf")):
                g[u] = ng
                heapq.heappush(pq, (ng + h(u), ng, u, v))
    return None, float("inf")
```

Note `neighbours` is a *function*, not a stored graph. A* is usually run over
an implicit graph --- puzzle states, decoder states, plan states --- that is
far too large to materialise. This is the same "generate the graph as you
explore it" pattern as backtracking (Chapter 20).

## Minimum spanning trees

An MST connects all vertices with minimum total edge weight. Both standard
algorithms are greedy (Chapter 17) and both are correct for the same reason.

:::theorem The cut property
For any partition of the vertices into two non-empty sets, the minimum-weight
edge crossing the partition belongs to some MST. (With distinct weights, to
*every* MST.)
:::

Kruskal repeatedly adds the globally lightest edge that does not create a
cycle --- the cut is "the components at that moment". Prim grows a single
tree, repeatedly adding the lightest edge leaving it --- the cut is
"tree versus rest".

```python title="Kruskal, with union-find from Chapter 15"
def kruskal(n, edges):
    dsu = DSU(n)
    total, tree = 0.0, []
    for w, u, v in sorted(edges):           # theta(E log E)
        if dsu.union(u, v):                 # theta(alpha(n))
            tree.append((u, v, w))
            total += w
            if len(tree) == n - 1:
                break
    return tree, total
```

Kruskal is $\Theta(E \log E)$, dominated by the sort; Prim with a binary heap
is $\Theta(E \log V)$. Kruskal is simpler and parallelises better (sort then
scan); Prim wins on dense graphs and when the edges are generated lazily.

:::ml MSTs and single-linkage clustering
Single-linkage hierarchical clustering is *exactly* the MST: cutting the MST
at all edges heavier than $\tau$ gives the single-linkage clusters at
threshold $\tau$. So you can compute a full single-linkage dendrogram for $n$
points in $\Theta(n^2)$ with Prim on the complete distance graph --- or much
faster with a spatial index. Related: the minimum spanning tree of a
$k$-nearest-neighbour graph underlies HDBSCAN, and MST-based clustering is
the standard way to turn a near-duplicate similarity graph into groups when
plain connected components (Chapter 15) over-merges.
:::

:::pitfall Longest path is not shortest path with negated weights
Negating the weights and running a shortest-path algorithm fails, because the
negation creates negative cycles and the longest simple path problem is
NP-hard in general. The exception is a DAG: there are no cycles, so
relaxation in topological order finds the longest path in $\Theta(V+E)$.
This is exactly why critical-path analysis works on a schedule and not on a
general graph.
:::

:::exercise
1. Implement 0-1 BFS with a deque (push-front for weight-0 edges, push-back
   for weight-1) and show it is $\Theta(V+E)$.
2. Construct a graph with one negative edge and no negative cycle on which
   Dijkstra returns a wrong answer. Verify Bellman--Ford gets it right.
3. Implement Dijkstra with an indexed heap supporting `decrease-key` and
   compare it to the lazy version on a graph with $10^6$ edges. Explain the
   result in terms of constants.
4. Implement A* for the 15-puzzle with (a) misplaced-tile and (b) Manhattan
   distance heuristics. Compare expanded nodes. Prove both are admissible.
5. Show that if $h$ is consistent then A* never re-expands a settled vertex.
   Then construct an admissible-but-inconsistent $h$ that causes
   re-expansion.
6. Implement both Kruskal and Prim; verify they produce the same total weight
   on random graphs, and compare their times at densities $E = 2V$ and
   $E = V^2/10$.
7. Build a single-linkage dendrogram of 5,000 points by computing the MST of
   the complete distance graph, and verify it matches
   `scipy.cluster.hierarchy.linkage(method="single")`.
8. Model "choose a quantisation level per layer to minimise latency subject
   to an accuracy floor" as a shortest path on a layered DAG, and solve it.
:::

:::recap
- With weights, replace BFS's queue with a priority queue: that is Dijkstra.
  Lazy deletion is simpler and usually faster than an indexed heap.
- Dijkstra requires non-negative weights; the settled-vertex invariant fails
  otherwise. Bellman--Ford handles negative weights in $\Theta(VE)$ and
  detects negative cycles, which is frequently the real goal.
- On a DAG, relaxing in topological order is $\Theta(V+E)$ and handles
  negative weights and longest paths.
- A* orders by $g + h$. Admissible $h$ gives optimality; consistent $h$ also
  gives single expansion. With $h = 0$ it is Dijkstra.
- A* is usually run over an implicit graph generated on demand.
- Kruskal and Prim both follow from the cut property; Kruskal is
  sort-dominated and simple, Prim is better on dense graphs.
- Single-linkage clustering is the MST, cut at a threshold.
:::
