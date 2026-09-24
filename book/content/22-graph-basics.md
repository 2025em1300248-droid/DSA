# Graph Representations and Traversal
@short: Graphs and Traversal
@subtitle: The structure that appears once relationships matter more than order
@tier: core
@prereq: Chapters 6, 13
@blurb: A graph is the most general of the structures in this book: arrays, trees and lists are all special cases. This chapter covers how to store one, how to walk one, and the handful of traversal variants that solve a remarkable share of real problems --- including several you have already run today without noticing.
@objectives:
- Choose between adjacency matrix, adjacency list and CSR for a given workload
- Implement BFS and DFS iteratively and know exactly what each one computes
- Find connected components, detect cycles and test bipartiteness
- Understand CSR as the format that makes graphs work on GPUs
- Recognise the graph inside a computation graph, a dependency tree and a retrieval index
- Estimate memory for a graph with a billion edges

## Definitions, quickly

A graph $G = (V, E)$ is a set of vertices and a set of edges. Edges may be
**directed** or **undirected**, **weighted** or not. A graph is **sparse**
when $|E| = O(|V|)$ and **dense** when $|E| = \Theta(|V|^2)$; almost every
real graph is sparse, and almost every asymptotic decision follows from that.

| Term | Meaning | Where it matters |
|---|---|---|
| Degree | edges incident to a vertex | power-law degrees break load balancing |
| Path | sequence of adjacent vertices | routing, reachability |
| Cycle | path returning to its start | deadlock, invalid dependency |
| Connected component | maximal mutually reachable set | clustering, deduplication |
| DAG | directed, acyclic | schedules, autograd, build systems |
| Bipartite | vertices split so all edges cross | user--item, matching |

@tbl: The vocabulary you need. Everything else in Part V is built from these six ideas.

## Three representations

@fig: graph_representations | 132 | The same graph three ways. The matrix answers "is there an edge?" in $\Theta(1)$ but costs $\Theta(V^2)$ memory; the list costs $\Theta(V+E)$ but must scan to answer the same question; CSR is the list flattened into two arrays.

| Representation | Memory | Edge test | Enumerate neighbours | Add edge |
|---|---|---|---|---|
| Adjacency matrix | $\Theta(V^2)$ | $\Theta(1)$ | $\Theta(V)$ | $\Theta(1)$ |
| Adjacency list | $\Theta(V + E)$ | $\Theta(\deg)$ | $\Theta(\deg)$ | $\Theta(1)$ |
| Adjacency set | $\Theta(V + E)$ | $\Theta(1)$ | $\Theta(\deg)$ | $\Theta(1)$ |
| CSR (compressed sparse row) | $\Theta(V + E)$, smallest constant | $\Theta(\log \deg)$ | $\Theta(\deg)$, contiguous | rebuild |
| Edge list | $\Theta(E)$ | $\Theta(E)$ | $\Theta(E)$ | $\Theta(1)$ |

@tbl: Choose by workload. Matrices for small dense graphs (under a few thousand vertices); adjacency sets for graphs that change; CSR for large static graphs you will traverse many times.

:::insight CSR is the format that matters at scale
CSR stores a graph as two flat integer arrays: `indptr` of length $V+1$ and
`indices` of length $E$. The neighbours of vertex $v$ are
`indices[indptr[v]:indptr[v+1]]` --- a contiguous slice. That is one
sequential read per vertex, no pointer chasing, trivially memory-mappable,
and directly usable by a GPU kernel. It is `scipy.sparse.csr_matrix`, it is
PyTorch Geometric's edge storage, and it is the layout of every serious
graph engine. It is also exactly the ragged layout from Chapter 4.
:::

```python title="Building CSR from an edge list"
import numpy as np

def build_csr(n, edges, undirected=True):
    src = np.asarray([u for u, v in edges], dtype=np.int64)
    dst = np.asarray([v for u, v in edges], dtype=np.int64)
    if undirected:
        src, dst = np.concatenate([src, dst]), np.concatenate([dst, src])
    order = np.argsort(src, kind="stable")          # group by source vertex
    src, dst = src[order], dst[order]
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.add.at(indptr, src + 1, 1)                   # degree of each vertex
    np.cumsum(indptr, out=indptr)                   # prefix sum -> offsets
    return indptr, dst

def neighbours(indptr, indices, v):
    return indices[indptr[v]:indptr[v + 1]]         # contiguous, no copy
```

:::perf The memory arithmetic for a billion-edge graph
CSR with int32 indices: $4(V + E)$ bytes. A graph with $10^8$ vertices and
$10^9$ edges needs about 4.4 GB --- it fits on one machine. The same graph as
a Python dict of lists needs roughly $10^9 \times 40$ bytes for the list
elements alone, plus per-vertex dict and list overhead: over 60 GB. The
representation choice is the difference between one machine and a cluster.
:::

## The universal traversal

BFS and DFS differ in one line. Writing them as the same function makes the
relationship impossible to forget.

@fig: bfs_dfs | 130 | The same graph traversed two ways. Neither order is "better"; they compute different things.

```python title="One traversal skeleton"
from collections import deque

def traverse(indptr, indices, start, mode="bfs"):
    n = len(indptr) - 1
    seen = bytearray(n)
    parent = [-1] * n
    order = []
    frontier = deque([start])
    seen[start] = 1
    while frontier:
        v = frontier.popleft() if mode == "bfs" else frontier.pop()
        order.append(v)
        for u in indices[indptr[v]:indptr[v + 1]]:
            if not seen[u]:
                seen[u] = 1
                parent[u] = v
                frontier.append(u)
    return order, parent
```

Both are $\Theta(V + E)$: every vertex is enqueued once and every edge
examined once (twice for undirected graphs).

:::pitfall Mark when you enqueue, not when you dequeue
If you set `seen[u] = 1` only when you pop $u$, a vertex reachable by several
edges gets pushed multiple times. On a dense graph that turns $\Theta(V+E)$
into $\Theta(V \cdot E)$ and can exhaust memory. Mark on push. (The one
exception is Dijkstra with lazy deletion, Chapter 23, where you *must* allow
duplicate pushes because distances improve.)
:::

### What BFS gives you

BFS visits vertices in non-decreasing distance from the source, so the
`parent` array is a **shortest-path tree** for an unweighted graph. That
single fact solves: minimum number of moves in a puzzle, degrees of
separation, shortest word ladder, minimum hops in a network, and the
"level" of each node in a dependency graph.

Two refinements are worth knowing. **Multi-source BFS** --- seed the queue
with every source at distance 0 --- computes, for every vertex, the distance
to the *nearest* source, in the same $\Theta(V+E)$. This is how you compute
"distance to the nearest labelled node" for semi-supervised learning on a
graph. **Bidirectional BFS** --- search forward from the source and backward
from the target, stopping when the frontiers meet --- reduces the explored
set from $b^d$ to $2b^{d/2}$, which for a social graph with $b \approx 200$
and $d = 6$ is a factor of $10^6$.

### What DFS gives you

DFS is about *structure*, not distance. Its discovery and finish times
expose:

- **Cycle detection.** In a directed graph, a back edge (to a vertex
  currently on the stack) means a cycle. This is how a build system detects
  a circular dependency and how an autograd engine detects an illegal
  in-place operation.
- **Topological order.** Reverse finishing order of a DFS on a DAG
  (Chapter 24).
- **Strongly connected components.** Tarjan's and Kosaraju's algorithms are
  DFS with extra bookkeeping.
- **Bridges and articulation points.** Edges and vertices whose removal
  disconnects the graph --- single points of failure in a network.

```python title="Cycle detection in a directed graph, iteratively"
WHITE, GREY, BLACK = 0, 1, 2

def has_cycle(indptr, indices):
    n = len(indptr) - 1
    colour = bytearray(n)
    for s in range(n):
        if colour[s] != WHITE:
            continue
        stack = [(s, indptr[s])]
        colour[s] = GREY
        while stack:
            v, i = stack[-1]
            if i < indptr[v + 1]:
                stack[-1] = (v, i + 1)
                u = indices[i]
                if colour[u] == GREY:
                    return True                  # back edge: cycle
                if colour[u] == WHITE:
                    colour[u] = GREY
                    stack.append((u, indptr[u]))
            else:
                colour[v] = BLACK                # finished
                stack.pop()
    return False
```

The three colours are the standard idiom: white = unvisited, grey = on the
current path, black = fully explored. Grey is what distinguishes a back edge
(a cycle) from a cross edge (not a cycle), and forgetting it is the classic
bug.

## Connected components and bipartiteness

```python title="Components by repeated BFS, and a 2-colouring test"
def components(indptr, indices):
    n = len(indptr) - 1
    comp = [-1] * n
    k = 0
    for s in range(n):
        if comp[s] != -1:
            continue
        stack = [s]
        comp[s] = k
        while stack:
            v = stack.pop()
            for u in indices[indptr[v]:indptr[v + 1]]:
                if comp[u] == -1:
                    comp[u] = k
                    stack.append(u)
        k += 1
    return comp, k

def is_bipartite(indptr, indices):
    n = len(indptr) - 1
    colour = [-1] * n
    for s in range(n):
        if colour[s] != -1:
            continue
        colour[s] = 0
        stack = [s]
        while stack:
            v = stack.pop()
            for u in indices[indptr[v]:indptr[v + 1]]:
                if colour[u] == -1:
                    colour[u] = 1 - colour[v]
                    stack.append(u)
                elif colour[u] == colour[v]:
                    return False           # odd cycle
    return True
```

A graph is bipartite exactly when it has no odd cycle, and the 2-colouring
*is* the proof. Bipartite structure is what makes user--item recommendation
graphs, document--term matrices and bipartite matching (Chapter 25) tractable.

:::ml Graphs you are already using
**The computation graph.** Every framework builds a DAG of operations;
forward is a topological traversal and backward is its reverse (Chapter 24).

**The dependency graph of a pipeline.** Airflow, Dagster, `make`, Bazel: all
topological sorts with cycle detection.

**The retrieval graph.** HNSW is a navigable small-world graph and its
search is a greedy best-first traversal --- literally the skeleton above with
a priority queue (Chapter 33).

**The user--item graph.** Collaborative filtering is a bipartite graph;
random walks on it (PageRank-style) are a strong baseline recommender
(Chapter 26).

**The knowledge graph.** Multi-hop retrieval is bounded-depth BFS from the
entities mentioned in a query.

**The attention graph.** Sparse attention patterns are adjacency structures;
sliding-window attention is a band matrix, and the "graph" framing is how
BigBird's random+window+global pattern was designed and analysed.
:::

:::pitfall Power-law degree distributions break everything
Real graphs are not regular. In a social or web graph the top 0.01% of
vertices have millions of neighbours while the median has three. This breaks
naive parallel BFS (one thread gets the celebrity vertex and everyone waits),
breaks vertex-partitioned distributed graphs (one machine holds the hub), and
breaks GNN mini-batching (one sampled neighbourhood explodes). The standard
mitigations are edge-based rather than vertex-based partitioning, degree
capping, and neighbour sampling (Chapter 26).
:::

:::exercise
1. Build CSR for a graph with $10^6$ vertices and $10^7$ edges and measure
   the memory against a `dict` of `list`s. Then measure BFS time for both.
2. Implement multi-source BFS and use it to compute, for each vertex, the
   distance to the nearest of 100 labelled vertices.
3. Implement bidirectional BFS and compare the number of vertices explored to
   ordinary BFS on a random graph with average degree 10 and 100,000
   vertices.
4. Demonstrate the "mark on pop" bug: construct a graph where it causes the
   queue to grow quadratically.
5. Implement Tarjan's strongly connected components algorithm iteratively and
   use it to find cycles in a package dependency graph.
6. Find all bridges of a graph in $\Theta(V+E)$ using DFS low-link values,
   and interpret the result for a network reliability question.
7. Given a power-law graph, measure the imbalance of a vertex-partitioned
   BFS across 8 workers. Then implement degree capping and measure again.
:::

:::recap
- Real graphs are sparse, so $\Theta(V + E)$ representations dominate. CSR ---
  `indptr` plus `indices` --- is the layout for large static graphs and the
  one GPUs use.
- BFS and DFS are the same skeleton with a queue or a stack. Both are
  $\Theta(V+E)$; mark vertices when you push, not when you pop.
- BFS gives shortest paths in unweighted graphs; multi-source BFS gives
  distance to the nearest source; bidirectional BFS squares the reachable
  depth.
- DFS gives structure: cycles via grey back edges, topological order,
  strongly connected components, bridges and articulation points.
- Connected components and bipartiteness are two-line variations on the
  traversal.
- Computation graphs, pipeline DAGs, HNSW indexes, user--item graphs and
  sparse attention patterns are all graphs you already use.
- Power-law degree distributions break naive partitioning and sampling; cap
  degrees or partition by edges.
:::
