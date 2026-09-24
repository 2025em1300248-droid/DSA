# DAGs: Topological Order, Autograd and Computation Graphs
@short: DAGs and Autograd
@subtitle: The graph your training loop is
@tier: core
@prereq: Chapters 18, 22
@blurb: Directed acyclic graphs are the best-behaved graphs: they have a linear order consistent with their edges, which makes dynamic programming over them trivial and shortest and longest paths equally easy. They are also the exact structure of a neural network's computation, so this chapter doubles as a proper explanation of how automatic differentiation works and where its memory goes.
@objectives:
- Compute a topological order two ways and detect cycles while doing it
- Solve longest path, critical path and DP on a DAG in linear time
- Explain reverse-mode automatic differentiation as a reverse topological sweep
- Account precisely for training memory and understand gradient checkpointing
- Understand operator fusion and scheduling as graph transformations
- Recognise DAG scheduling in pipelines, build systems and model parallelism

## Topological order

:::definition Topological order
A linear ordering of a directed graph's vertices such that every edge
$(u, v)$ has $u$ before $v$. It exists if and only if the graph is acyclic,
and it is generally not unique.
:::

```python title="Kahn's algorithm: peel off zero in-degree vertices"
from collections import deque

def topo_sort(n, indptr, indices):
    indeg = [0] * n
    for v in range(n):
        for u in indices[indptr[v]:indptr[v + 1]]:
            indeg[u] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for u in indices[indptr[v]:indptr[v + 1]]:
            indeg[u] -= 1
            if indeg[u] == 0:
                q.append(u)
    if len(order) != n:
        raise ValueError("graph has a cycle")   # free cycle detection
    return order
```

$\Theta(V+E)$, and the length check at the end is a complete cycle detector:
if any vertex never reaches in-degree zero, it is on or downstream of a
cycle. The alternative is reverse DFS finishing order, which is equally
valid; Kahn's is easier to parallelise (all zero in-degree vertices are
independent) and gives a natural notion of "levels".

:::insight Any topological order is a valid evaluation order
This is why dynamic programming on a DAG needs no thought about ordering
(Chapter 18, step 4): compute a topological order and evaluate in it. It is
also why a build system, a data pipeline and a neural network forward pass
are the same computation.
:::

## Linear-time DP on a DAG

```python title="Longest path in a DAG: the critical path of a schedule"
def longest_path(n, indptr, indices, weights, order):
    dist = [0.0] * n
    parent = [-1] * n
    for v in order:                               # dependencies come first
        for i in range(indptr[v], indptr[v + 1]):
            u, w = indices[i], weights[i]
            if dist[v] + w > dist[u]:
                dist[u] = dist[v] + w
                parent[u] = v
    end = max(range(n), key=lambda v: dist[v])
    path, cur = [], end
    while cur != -1:
        path.append(cur); cur = parent[cur]
    return path[::-1], dist[end]
```

In a general graph, longest path is NP-hard. On a DAG it is one pass. That
gap is why *acyclic* is such a valuable property and why so many systems go
to trouble to guarantee it.

The **critical path** --- the longest weighted path through a task graph ---
is the minimum possible makespan with unlimited parallelism. It tells a
pipeline engineer exactly which tasks to optimise: shortening anything off
the critical path changes nothing at all.

## Automatic differentiation

A neural network's forward pass builds a DAG: leaves are inputs and
parameters, internal nodes are operations, and the root is the loss.

@fig: autograd_dag | 134 | A computation graph. The forward pass evaluates in topological order; the backward pass traverses the exact reverse, and each node's vector--Jacobian product runs once, after every node that consumes its output.

:::definition Reverse-mode automatic differentiation
Let the computation be $L = f_k(f_{k-1}(\cdots f_1(x)))$. Forward mode
propagates $\frac{\partial \text{node}}{\partial x}$ from inputs to outputs;
reverse mode propagates $\bar{v} = \frac{\partial L}{\partial \text{node}}$
from the output back to the inputs. Each node needs a **vector--Jacobian
product**: given $\bar{v}$ for its output, produce $\bar{v}$ for each input,
without ever materialising the Jacobian.
:::

For a function $\mathbb{R}^n \to \mathbb{R}^m$, forward mode costs $O(n)$
passes and reverse mode costs $O(m)$. Neural network training has
$n = $ millions of parameters and $m = 1$ (a scalar loss), so reverse mode
is cheaper by a factor of millions. That asymmetry --- not any deep
mathematics --- is why backpropagation is the algorithm.

```python title="A minimal reverse-mode autodiff engine"
class Var:
    __slots__ = ("val", "grad", "_parents", "_backward")

    def __init__(self, val, parents=(), backward=None):
        self.val = val
        self.grad = 0.0
        self._parents = parents
        self._backward = backward or (lambda g: ())

    def __add__(self, other):
        other = other if isinstance(other, Var) else Var(other)
        return Var(self.val + other.val, (self, other), lambda g: (g, g))

    def __mul__(self, other):
        other = other if isinstance(other, Var) else Var(other)
        return Var(self.val * other.val, (self, other),
                   lambda g: (g * other.val, g * self.val))

    def relu(self):
        return Var(max(0.0, self.val), (self,),
                   lambda g: (g * (1.0 if self.val > 0 else 0.0),))

    def backward(self):
        order, seen = [], set()
        def visit(v):                        # DFS post-order = topological
            if id(v) in seen:
                return
            seen.add(id(v))
            for p in v._parents:
                visit(p)
            order.append(v)
        visit(self)
        self.grad = 1.0
        for v in reversed(order):            # reverse topological sweep
            for parent, g in zip(v._parents, v._backward(v.grad)):
                parent.grad += g             # ACCUMULATE: a node may have
                                             # several consumers
    def __radd__(self, o):
        return self + o

    def __rmul__(self, o):
        return self * o
```

That is the whole idea. PyTorch's `autograd` and JAX's `grad` differ in
engineering --- tensors instead of scalars, C++ kernels, a tape or a traced
program --- but not in structure. Two details in the code are the ones people
get wrong:

- **Accumulate, never assign.** A node feeding several consumers receives a
  gradient contribution from each, and they sum. Assigning instead of
  accumulating silently drops all but the last.
- **Reverse topological order, not reverse call order.** A node's gradient is
  complete only after every consumer has contributed. That is why the sort
  is necessary and why a naive "call backward as you go" is wrong for any
  graph with a branch.

:::ml Where training memory actually goes
Peak memory during training is
$$M = \underbrace{P(2 + 2 + 12)}_{\text{weights, grads, Adam states}} + \underbrace{\sum_{\text{nodes}} \text{size}(\text{saved tensors})}_{\text{activations}} + \text{workspace}$$
for a $P$-parameter model in mixed precision. The first term is fixed. The
second grows with batch size $\times$ sequence length $\times$ depth, and it
is the term you can actually control:

- **Gradient checkpointing** saves only segment boundaries and recomputes
  the rest: $\Theta(\sqrt{L})$ memory for one extra forward pass
  (Chapter 18).
- **Activation offload** moves saved tensors to host memory and back, trading
  PCIe bandwidth for capacity.
- **Fusion** removes intermediates entirely --- a fused
  `bias + gelu + dropout` never writes the two intermediate tensors.
- **In-place operations** overwrite a tensor that is not needed for the
  backward pass. When it *is* needed, the framework raises an error; that
  error is a DAG check, which is why it can detect the problem at all.
:::

## Graph transformations

Modern compilers (`torch.compile`, XLA, TensorRT) operate on this DAG.

**Operator fusion** replaces a chain of elementwise nodes with a single
kernel. The benefit is not fewer FLOPs --- it is fewer round trips to memory,
which for memory-bound kernels is the entire cost (Chapter 3). Fusing
`x -> mul -> add -> gelu` turns four reads and four writes into one of each.

**Common subexpression elimination** merges identical nodes; the DAG makes
this a hash of (op, inputs).

**Scheduling** chooses a specific topological order. Different valid orders
have very different peak memory, because memory is determined by how long
tensors stay live. Choosing the order that minimises peak live memory is
NP-hard in general, and compilers use heuristics plus DP on segments.

**Dead code elimination** drops nodes not reachable backwards from the
outputs --- a reverse traversal.

:::insight Why `torch.compile` cares so much about graph breaks
A graph break --- caused by data-dependent Python control flow, an
unsupported operation, or a print statement --- splits the DAG into
independent pieces. Fusion, scheduling and memory planning cannot cross the
boundary, so each break costs you the optimisations that span it. This is
why "remove graph breaks" is the first thing a performance guide tells you,
and why `torch.compile(fullgraph=True)` exists: it turns a silent slowdown
into an error.
:::

:::exercise
1. Implement topological sort both ways (Kahn and reverse DFS finishing
   order) and verify they produce valid but generally different orders.
2. Compute the critical path of a 50-task pipeline with random durations and
   dependencies. Show that shortening a non-critical task does not change the
   makespan.
3. Extend the `Var` class with `exp`, `log`, `pow` and division, and verify
   all gradients against finite differences.
4. Construct a computation graph where a node has three consumers.
   Demonstrate that assigning rather than accumulating gradients gives a
   wrong answer, and quantify how wrong.
5. Implement forward-mode autodiff with dual numbers. For a function
   $\mathbb{R}^{1000} \to \mathbb{R}$, measure the cost of forward mode
   versus reverse mode and confirm the factor of 1000.
6. For a chain of $L$ layers with equal activation sizes, derive the optimal
   number of checkpoint segments and show that the optimum is $\sqrt{L}$.
7. Take a small model, print its graph with `torch.fx` or
   `torch._dynamo.explain`, count the graph breaks, and remove them.
8. Given a DAG with tensor sizes on edges, write a program that evaluates
   peak live memory for a given topological order, and search over orders to
   find a better one.
:::

:::recap
- A topological order exists exactly when the graph is acyclic; Kahn's
  algorithm produces one in $\Theta(V+E)$ and detects cycles for free.
- Any topological order is a valid evaluation order, which is why DP on a
  DAG needs no ordering argument and why longest path --- NP-hard in general
  --- is linear here.
- The critical path is the minimum makespan; optimising off it changes
  nothing.
- Reverse-mode autodiff is a reverse topological sweep of vector--Jacobian
  products. It is cheap for scalar losses because cost scales with the number
  of *outputs*, not inputs.
- Accumulate gradients across consumers and respect topological order; those
  are the two correctness requirements.
- Training memory is fixed optimiser state plus controllable activations;
  checkpointing, offload, fusion and in-place ops each attack the second.
- Compilers transform this DAG: fusion for memory traffic, CSE, scheduling
  for peak memory, dead-code elimination. Graph breaks cost you all of them.
:::
