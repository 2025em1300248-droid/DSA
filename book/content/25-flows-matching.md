# Flows, Matchings and Assignment
@short: Flows and Matching
@subtitle: The algorithm inside your object detector's loss function
@tier: advanced
@prereq: Chapters 17, 23
@blurb: Network flow is the classical topic that looks furthest from machine learning and turns out to be inside it. The Hungarian algorithm assigns predictions to ground-truth objects in DETR-style detectors; bipartite matching balances experts in a mixture-of-experts layer; min-cut solves image segmentation exactly. This chapter develops the theory only as far as those applications need, and no further.
@objectives:
- State the max-flow min-cut theorem and use it to reason about bottlenecks
- Implement Edmonds--Karp and Dinic's algorithm
- Find maximum bipartite matchings with augmenting paths and Hopcroft--Karp
- Implement the Hungarian algorithm for minimum-cost assignment
- Recognise assignment problems in detection losses, MoE routing and tracking
- Know when to use a solver rather than writing one

## Flow networks

:::definition Flow network and max-flow
A directed graph with a capacity $c(u,v) \ge 0$ on each edge, a source $s$
and a sink $t$. A **flow** assigns $f(u,v) \le c(u,v)$ to each edge such that
every vertex other than $s$ and $t$ has equal in-flow and out-flow. The
**value** of the flow is the net flow out of $s$; max-flow asks to maximise it.
:::

:::theorem Max-flow min-cut
The maximum value of an $s$--$t$ flow equals the minimum capacity of an
$s$--$t$ cut: a partition of the vertices with $s$ on one side and $t$ on the
other, whose capacity is the total capacity of edges crossing forwards.
:::

@fig: maxflow_cut | 130 | A flow network. The max-flow value equals the capacity of the *minimum* cut; finding one gives you the other, and the cut identifies exactly which edges are the bottleneck.

The theorem is the practically useful half: max-flow tells you the throughput,
and the min-cut tells you *which resources to add*. After running a max-flow,
the vertices reachable from $s$ in the residual graph form one side of a
minimum cut --- a one-line BFS at the end.

### Algorithms

**Ford--Fulkerson** repeatedly finds any augmenting path in the residual
graph and pushes flow along it. With arbitrary path choice it can be slow (and
with irrational capacities, non-terminating). **Edmonds--Karp** chooses the
*shortest* augmenting path by BFS, giving $\Theta(VE^2)$. **Dinic's
algorithm** builds a level graph by BFS and then finds a blocking flow by
DFS, giving $\Theta(V^2E)$ in general and $\Theta(E\sqrt{V})$ on unit-capacity
graphs --- which is the bipartite-matching case.

```python title="Dinic's algorithm"
from collections import deque

class Dinic:
    def __init__(self, n):
        self.n = n
        self.g = [[] for _ in range(n)]      # adjacency of edge indices
        self.edges = []                      # (to, capacity)

    def add_edge(self, u, v, cap):
        self.g[u].append(len(self.edges)); self.edges.append([v, cap])
        self.g[v].append(len(self.edges)); self.edges.append([u, 0])  # reverse

    def _levels(self, s, t):
        self.level = [-1] * self.n
        self.level[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for i in self.g[v]:
                to, cap = self.edges[i]
                if cap > 0 and self.level[to] < 0:
                    self.level[to] = self.level[v] + 1
                    q.append(to)
        return self.level[t] >= 0

    def _dfs(self, v, t, pushed):
        if v == t or pushed == 0:
            return pushed
        while self.it[v] < len(self.g[v]):
            i = self.g[v][self.it[v]]
            to, cap = self.edges[i]
            if cap > 0 and self.level[to] == self.level[v] + 1:
                d = self._dfs(to, t, min(pushed, cap))
                if d > 0:
                    self.edges[i][1] -= d
                    self.edges[i ^ 1][1] += d      # XOR trick pairs the edges
                    return d
            self.it[v] += 1
        return 0

    def maxflow(self, s, t):
        total = 0
        while self._levels(s, t):
            self.it = [0] * self.n
            while True:
                pushed = self._dfs(s, t, float("inf"))
                if pushed == 0:
                    break
                total += pushed
        return total
```

The `i ^ 1` trick is worth noting: storing each edge immediately before its
reverse makes the reverse edge's index the forward index with the low bit
flipped. Small, but it removes a whole class of bookkeeping bugs.

## Bipartite matching

@fig: bipartite_matching | 130 | Maximum bipartite matching via augmenting paths. The classical formulation on the left is exactly the set-prediction problem on the right.

A matching is a set of edges with no shared endpoints. Maximum bipartite
matching reduces to max-flow: add a source connected to every left vertex and
a sink from every right vertex, all capacities 1. Dinic on this unit-capacity
network is Hopcroft--Karp, running in $\Theta(E\sqrt{V})$.

```python title="Kuhn's algorithm: simple augmenting-path matching"
def bipartite_match(adj, n_left, n_right):
    """adj[u] = list of right-vertices adjacent to left-vertex u."""
    match_r = [-1] * n_right
    def try_kuhn(u, seen):
        for v in adj[u]:
            if seen[v]:
                continue
            seen[v] = True
            if match_r[v] == -1 or try_kuhn(match_r[v], seen):
                match_r[v] = u            # augment along the path
                return True
        return False
    count = 0
    for u in range(n_left):
        if try_kuhn(u, [False] * n_right):
            count += 1
    return count, match_r
```

$\Theta(VE)$, perfectly adequate below a few thousand vertices, and about
fifteen lines. Reach for Hopcroft--Karp only when profiling says to.

## The assignment problem

Maximum matching asks *how many* pairs. The assignment problem asks for the
*cheapest* perfect matching given an $n \times n$ cost matrix. The Hungarian
(Kuhn--Munkres) algorithm solves it in $\Theta(n^3)$.

The idea: maintain dual variables (potentials) $u_i$ on rows and $v_j$ on
columns with $u_i + v_j \le C_{ij}$ for all pairs. Edges where the
constraint is tight form the "equality subgraph"; find a maximum matching in
it; if it is not perfect, adjust the potentials by the smallest slack, which
adds at least one new tight edge. Repeat. When the matching is perfect,
complementary slackness proves it is optimal.

```python title="Use the library, and know what it is doing"
import numpy as np
from scipy.optimize import linear_sum_assignment

cost = np.random.rand(200, 200)
rows, cols = linear_sum_assignment(cost)      # Jonker-Volgenant, theta(n^3)
print(cost[rows, cols].sum())                 # provably minimal total cost
```

:::ml The Hungarian algorithm inside modern detectors
DETR and every set-prediction model after it face a problem: the model emits
$N$ object queries in no particular order, and the image has $M$ ground-truth
objects. To compute a loss you must decide which prediction corresponds to
which object --- and any fixed rule (by index, by confidence) makes the loss
discontinuous and the training unstable.

The solution is a **bipartite matching loss**. Build an $N \times M$ cost
matrix where $C_{ij}$ combines classification cost and box distance for
prediction $i$ against object $j$, run `linear_sum_assignment`, and apply the
loss only along the matched pairs. Unmatched predictions are trained toward
"no object".

This makes the loss permutation-invariant, removes the need for non-maximum
suppression entirely, and is why DETR-family models are end-to-end. The cost
is one $\Theta(N^3)$ assignment per image per step --- with $N = 100$ that is
about a million operations, negligible beside the backbone.
:::

:::ml Three more matching problems you will meet
**Mixture-of-experts routing.** Top-$k$ routing overloads popular experts.
Balanced assignment --- solving a transportation problem so each expert gets
roughly equal load --- is what Sinkhorn-based routers (BASE layers, Sinkhorn
Transformers) do; Sinkhorn iteration is an entropic relaxation of the
assignment problem that is differentiable and runs on a GPU.

**Multi-object tracking.** Associating detections in frame $t$ with tracks
from frame $t-1$ is exactly the assignment problem; SORT and DeepSORT call
the Hungarian algorithm every frame with a cost built from IoU and appearance
distance.

**Optimal transport.** Wasserstein distance between two discrete
distributions is a transportation problem --- assignment with fractional
masses. The Sinkhorn algorithm solves the entropy-regularised version in
$\Theta(n^2)$ per iteration, and appears in domain adaptation, in
self-supervised clustering (SwAV), and in generative model evaluation.
:::

:::insight Min-cut as exact inference
For an energy function over binary variables that is *submodular* ---
roughly, pairwise terms that prefer agreement --- the global minimum can be
found exactly by a single min-cut. This is the basis of graph-cut image
segmentation: pixels are vertices, the source and sink are foreground and
background, unary terms become terminal capacities, and smoothness terms
become inter-pixel capacities. It is one of the few cases in vision where a
global optimum over an exponential space is available in polynomial time, and
it remains the method of choice for interactive segmentation.
:::

:::pitfall Do not implement min-cost flow yourself
Max-flow and bipartite matching are reasonable to write. Min-cost flow and
the assignment problem have subtle degenerate cases, and mature
implementations (`scipy.optimize.linear_sum_assignment`, Google OR-Tools,
LEMON) are both faster and correct. Write them once to understand them, then
use the library.
:::

:::exercise
1. Find the minimum cut in the figure's network and verify it equals the
   max-flow value.
2. Implement Edmonds--Karp and Dinic, and compare them on a unit-capacity
   bipartite graph with 10,000 vertices.
3. Show that Kuhn's algorithm is $\Theta(VE)$ and construct a graph on which
   it hits that bound.
4. Implement a DETR-style matching loss: build the cost matrix from
   classification log-probabilities and generalised IoU, call
   `linear_sum_assignment`, and verify the loss is invariant to permuting the
   predictions.
5. Implement Sinkhorn iteration for entropic optimal transport and show that
   as the regularisation goes to zero the solution approaches the Hungarian
   assignment.
6. Model balanced expert routing as a transportation problem with capacity
   constraints, solve it, and compare expert load to plain top-1 routing.
7. Implement binary image segmentation via min-cut on a $200 \times 200$
   image with user-supplied foreground and background scribbles.
:::

:::recap
- Max-flow equals min-cut; the cut identifies the bottleneck edges, which is
  usually the actionable output.
- Edmonds--Karp is $\Theta(VE^2)$; Dinic is $\Theta(V^2E)$ generally and
  $\Theta(E\sqrt V)$ on unit capacities, which covers bipartite matching.
- Maximum bipartite matching reduces to unit-capacity max-flow; Kuhn's
  fifteen-line algorithm is $\Theta(VE)$ and usually enough.
- The assignment problem --- cheapest perfect matching --- is solved in
  $\Theta(n^3)$ by the Hungarian algorithm; use `linear_sum_assignment`.
- Set-prediction losses (DETR), multi-object tracking and balanced MoE
  routing are all assignment problems; optimal transport is its fractional
  relaxation, solved by Sinkhorn.
- Submodular binary energies are globally minimised by one min-cut, which is
  how graph-cut segmentation works.
:::
