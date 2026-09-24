# Recursion, Memoisation and the Call Stack
@short: Recursion
@subtitle: Solving a problem by assuming you have already solved it
@tier: foundation
@prereq: Chapter 6
@blurb: Recursion is the technique that makes divide and conquer, dynamic programming, backtracking and tree algorithms possible, and it is also the technique most likely to produce an algorithm that is exponentially slower than necessary. This chapter covers both sides: how to write a correct recursion, how to analyse it, and how memoisation turns a recursion tree into a graph.
@objectives:
- Write a recursion by identifying its base case, recursive case and measure of progress
- Draw the recursion tree of an algorithm and read its cost off the drawing
- Recognise overlapping subproblems and eliminate them with memoisation
- Convert any recursion into an iterative form with an explicit stack
- Understand tail calls, stack depth limits and why Python has no tail-call optimisation
- See how memoisation appears in ML systems as caching, not as an algorithm

## Three parts of a recursion

A recursion is a function defined in terms of itself on smaller inputs. It
is correct if and only if three things hold.

1. **A base case** that terminates without recursing.
2. **A recursive case** that is correct *assuming* the recursive calls are
   correct. This is the leap people find hard: you may assume the function
   already works, as long as you only call it on strictly smaller inputs.
3. **A measure that strictly decreases** on every call and is bounded below.
   Usually the size of the input; sometimes a subtler quantity.

```python title="The shape of every correct recursion"
def solve(problem):
    if is_trivial(problem):            # 1. base case
        return trivial_answer(problem)
    parts = decompose(problem)         # 3. each part is strictly smaller
    answers = [solve(part) for part in parts]
    return combine(answers)            # 2. assume the parts are right
```

The third condition is where real bugs live. `solve(n - 1)` obviously
decreases; `solve(n // 2)` decreases until $n = 1$ and then loops forever if
your base case is `n == 0`. When recursing on a graph, the measure is not the
input size but the number of unvisited nodes --- which is why graph recursion
needs a `visited` set and tree recursion does not (Chapter 22).

## Recursion trees

The cost of a recursion is the total work across all nodes of its call tree.
Drawing that tree is the fastest way to get the answer.

@fig: recursion_tree | 155 | Left: the call tree of naive `fib(5)`. Red nodes are recomputations. Right: with memoisation the tree collapses into a chain --- each distinct subproblem is solved once.

For naive Fibonacci, $T(n) = T(n-1) + T(n-2) + \Theta(1)$, which grows as
$\varphi^n \approx 1.618^n$. Concretely, `fib(40)` makes 331 million calls
and takes about a minute in Python; `fib(50)` would take two hours.

The pathology is not recursion. It is that the tree contains the same
subproblem many times. Count the *distinct* subproblems: there are only $n$
of them. That gap --- exponentially many nodes, linearly many distinct
values --- is the entire opportunity.

:::definition Overlapping subproblems
A recursion has *overlapping subproblems* when the same argument occurs at
more than one node of the call tree. When it does, caching results by
argument reduces the cost from the number of tree nodes to the number of
distinct arguments. This is **memoisation**, and it is the top-down half of
dynamic programming (Chapter 18).
:::

```python title="Three lines that change O(1.618^n) to O(n)"
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

`fib(400)` now returns instantly. The cache turns the *tree* into a
*directed acyclic graph*: each node is computed once and its result reused by
every parent that needs it.

:::pitfall `lru_cache` on the wrong function
`@lru_cache` requires hashable arguments, so it cannot memoise a function
taking a list or a NumPy array --- convert to a tuple or pass an index.
It also holds references to every argument and result forever with
`maxsize=None`, which leaks memory in a long-running process, and it is
per-process, so it does nothing across worker restarts. And memoising a
function whose result depends on anything other than its arguments (a file,
the clock, a random seed) silently produces wrong answers.
:::

## Analysing recursive cost

Three recurrence shapes cover most cases; Chapter 16 gives the general tool.

| Recurrence | Shape | Solution | Example |
|---|---|---|---|
| $T(n) = T(n-1) + \Theta(1)$ | linear chain | $\Theta(n)$ | list traversal, factorial |
| $T(n) = T(n-1) + \Theta(n)$ | shrinking work | $\Theta(n^2)$ | selection sort, naive quicksort worst case |
| $T(n) = 2T(n-1) + \Theta(1)$ | branching, size $-1$ | $\Theta(2^n)$ | subsets, Towers of Hanoi |
| $T(n) = T(n/2) + \Theta(1)$ | halving | $\Theta(\log n)$ | binary search |
| $T(n) = 2T(n/2) + \Theta(n)$ | halving, linear merge | $\Theta(n \log n)$ | merge sort, FFT |
| $T(n) = 2T(n/2) + \Theta(1)$ | halving, cheap merge | $\Theta(n)$ | tree traversal, max of array |

@tbl: The recurrences worth recognising on sight. Branching on $n - 1$ is exponential; branching on $n/2$ is not. That single distinction explains most of the difference between a feasible and an infeasible recursion.

:::insight Branching factor versus shrink rate
A recursion that makes $a$ calls on inputs of size $n/b$ has a tree of depth
$\log_b n$ and $a^{\log_b n} = n^{\log_b a}$ leaves. Two calls on half the
input gives $n^1$ leaves --- linear. Two calls on $n - 1$ gives $2^n$ leaves.
The shrink rate is multiplicative and the branching factor is exponential;
whenever they are not matched, one of them dominates completely.
:::

## The call stack, and its limits

Each call pushes a frame holding arguments, locals and the return address.
Python's default recursion limit is 1000 frames, and the underlying C stack
will segfault at around 10,000--50,000 even if you raise it.

```python title="When recursion depth is the bug"
import sys
sys.setrecursionlimit(30_000)      # buys you a little; not a real fix

def depth_rec(node):               # fails on a 100k-node degenerate tree
    return 0 if node is None else 1 + max(depth_rec(node.left),
                                          depth_rec(node.right))

def depth_iter(root):              # fine at any depth: heap, not C stack
    best, stack = 0, [(root, 1)]
    while stack:
        node, d = stack.pop()
        if node is None:
            continue
        best = max(best, d)
        stack.append((node.left, d + 1))
        stack.append((node.right, d + 1))
    return best
```

A *balanced* tree of a billion nodes has depth 30 and recursion is perfectly
safe. A degenerate tree --- a linked list in disguise, which is exactly what
you get from inserting sorted data into an unbalanced BST --- has depth $n$
and recursion is fatal. This asymmetry is why Chapter 12 cares so much about
balance.

:::note Why Python has no tail-call optimisation
A *tail call* is a recursive call in return position, which in principle can
reuse the current frame instead of pushing a new one, making the recursion a
loop. Scheme and most functional languages guarantee this. Python
deliberately does not, because it would destroy the tracebacks that make
debugging possible --- the frames are the stack trace. The practical rule:
in Python, if depth can exceed a few thousand, write the loop.
:::

## Recursion patterns worth having at hand

```python title="Four shapes that cover most recursive code"
# 1. Linear: process head, recurse on tail.
def total(xs, i=0):
    return 0 if i == len(xs) else xs[i] + total(xs, i + 1)

# 2. Binary divide and conquer: split, solve halves, combine.
def max_dc(xs, lo, hi):
    if hi - lo == 1:
        return xs[lo]
    mid = (lo + hi) // 2
    return max(max_dc(xs, lo, mid), max_dc(xs, mid, hi))

# 3. Tree recursion: recurse on children, combine upward.
def sum_tree(node):
    if node is None:
        return 0
    return node.val + sum_tree(node.left) + sum_tree(node.right)

# 4. Backtracking: choose, recurse, un-choose.  (Chapter 20)
def permutations(items, chosen=None, out=None):
    chosen = chosen if chosen is not None else []
    out = out if out is not None else []
    if not items:
        out.append(chosen[:])
        return out
    for i, x in enumerate(items):
        chosen.append(x)
        permutations(items[:i] + items[i + 1:], chosen, out)
        chosen.pop()                       # un-choose: restore the state
    return out
```

Pattern 3 is the shape of nearly every tree algorithm, and pattern 4 is the
shape of nearly every exhaustive search. Pattern 4's `pop` is the part people
forget, and forgetting it produces answers that are all the same object.

:::ml Memoisation by another name
Most of what an ML system calls "caching" is memoisation of a pure function.
**Prefix caching** in an LLM server: the KV cache for a prompt prefix is the
memoised result of running the model on it, and SGLang's RadixAttention is
literally a trie of memoised prefixes (Chapters 14 and 36). **Embedding
caches**: `embed(text)` is pure, so the result can be cached by content hash.
**Feature stores**: precomputed features are memoised aggregations keyed by
entity and time. **`torch.compile`**: compiled kernels are memoised by input
shape --- which is why a new shape triggers a recompile and why dynamic
shapes are set up specially.

In every case the question is the same as for `lru_cache`: is the function
actually pure, what is the key, and what is the eviction policy?
:::

## From memoisation to tabulation

Memoisation is top-down: start from the goal and recurse, caching. The same
computation can be done bottom-up, filling a table in an order where every
dependency is already computed.

```python title="The same recurrence, two directions"
from functools import lru_cache

def grid_paths_top_down(m, n):
    @lru_cache(maxsize=None)
    def go(i, j):
        if i == 0 or j == 0:
            return 1
        return go(i - 1, j) + go(i, j - 1)
    return go(m - 1, n - 1)

def grid_paths_bottom_up(m, n):
    row = [1] * n                       # theta(n) memory instead of theta(mn)
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]
        # row[j] now holds the number of paths to (i, j)
    return row[-1]
```

Both are $\Theta(mn)$ time. The bottom-up version uses $\Theta(n)$ memory
instead of $\Theta(mn)$, has no recursion depth, no function-call overhead
and no cache lookups --- typically 10--50x faster in Python. The top-down
version has one advantage that sometimes decides the matter: it only computes
the subproblems that are actually reachable, which for sparse state spaces
can be a tiny fraction. Chapter 18 makes this choice systematically.

:::exercise
1. Write a recursion for the number of ways to climb $n$ stairs taking 1, 2
   or 3 steps. Give the recurrence, the naive complexity, and the memoised
   complexity. Then write the $\Theta(1)$-space bottom-up version.
2. Draw the recursion tree of `max_dc` on eight elements. How many nodes?
   How many comparisons? Prove the general formula.
3. Implement `flatten` for an arbitrarily nested list both recursively and
   iteratively. Construct an input on which the recursive version fails.
4. Memoise a function of two arguments where one is a NumPy array. Show
   three ways to make the key hashable and compare their cost and their
   collision risk.
5. Ackermann's function $A(m, n)$ grows faster than any primitive recursive
   function. Compute $A(3, 3)$ with memoisation and explain why memoisation
   helps here but does not make it tractable for $A(4, 2)$.
6. Convert `permutations` to an iterative algorithm using an explicit stack.
   Then rewrite it as a generator that yields permutations lazily, and
   explain why the generator uses $\Theta(n)$ memory rather than $\Theta(n!)$.
7. A colleague memoises `score(model_version, document)` with `lru_cache`.
   Identify three distinct ways this can return a wrong answer in production.
:::

:::recap
- A correct recursion needs a base case, a recursive case that may assume the
  calls are correct, and a strictly decreasing measure.
- Read a recursion's cost off its call tree. Branching on $n - 1$ is
  exponential; branching on $n / b$ is polynomial.
- Overlapping subproblems make the tree exponentially larger than the set of
  distinct arguments; memoisation collapses it to a DAG.
- `lru_cache` requires hashable arguments and purity, and leaks without a
  bound.
- Any recursion converts to a loop with an explicit stack, which is
  mandatory when depth can exceed a few thousand. Python has no tail-call
  optimisation, by design.
- Bottom-up tabulation is usually faster and more memory-efficient; top-down
  memoisation wins when the reachable state space is sparse.
- Most caching in ML systems --- prefix caches, embedding caches, feature
  stores, compiled-kernel caches --- is memoisation of a pure function.
:::
