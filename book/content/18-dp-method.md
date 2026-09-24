# Dynamic Programming I: The Method
@short: Dynamic Programming
@subtitle: A repeatable procedure, not a flash of insight
@tier: core
@prereq: Chapters 8, 16
@blurb: Dynamic programming has a reputation for requiring inspiration. It does not. It requires a procedure, applied patiently: name the state, write the recurrence, identify the base cases, choose an evaluation order, and then optimise the memory. This chapter gives you that procedure and applies it to enough problems that the pattern becomes mechanical.
@objectives:
- Apply a five-step procedure to turn a problem into a dynamic program
- Distinguish problems with optimal substructure and overlapping subproblems from those without
- Choose between top-down memoisation and bottom-up tabulation for a given problem
- Reduce a DP's memory from $\Theta(n^2)$ to $\Theta(n)$, and recover the solution anyway
- Recognise the standard DP shapes: knapsack, interval, tree, bitmask, digit
- Apply DP to real space--time tradeoffs such as gradient checkpointing

## When dynamic programming applies

Two conditions, both necessary.

**Optimal substructure.** An optimal solution is built from optimal
solutions to subproblems. (Shared with divide and conquer and greedy.)

**Overlapping subproblems.** The same subproblem is needed many times.
(This is what divide and conquer lacks and what makes caching pay.)

:::insight The distinction, in one line
Divide and conquer: subproblems are *disjoint*, so recurse and combine.
Dynamic programming: subproblems *overlap*, so solve each once and store it.
Greedy: you can prove one choice is safe, so you need not solve subproblems
at all.
:::

## The five-step procedure

**1. Define the state.** What does `dp[...]` mean, in a full English
sentence? This is 80% of the work and the step people skip. "`dp[i][w]` is
the maximum value obtainable using the first $i$ items with total weight at
most $w$" is a state definition. "`dp[i][w]` is the answer for $i$ and $w$"
is not.

**2. Write the recurrence.** Express `dp[state]` in terms of strictly
smaller states, by enumerating the possible *last decisions*.

**3. Identify the base cases.** The states that need no recurrence. Getting
these wrong is the most common source of off-by-one bugs.

**4. Choose an evaluation order.** Any order in which every state's
dependencies are computed first. Equivalently: a topological order of the
dependency DAG (Chapter 24).

**5. Read off the answer, and optimise.** Which state holds the result?
Can you drop dimensions from memory?

@fig: dp_grid | 158 | A DP table is a DAG of dependencies. Once you know which earlier cells a cell needs, the evaluation order and the memory optimisation both follow mechanically.

## Worked example: 0/1 knapsack

*Problem.* $n$ items with weights $w_i$ and values $v_i$, capacity $W$.
Maximise total value; each item may be taken at most once.

**State.** `dp[i][c]` = the best value using items $0 \ldots i-1$ with
capacity exactly $c$ available.

**Recurrence.** The last decision is whether to take item $i-1$:

$$dp[i][c] = \max\big(dp[i-1][c],\ v_{i-1} + dp[i-1][c - w_{i-1}]\big)$$

where the second term applies only if $w_{i-1} \le c$.

**Base case.** `dp[0][c] = 0` for all $c$: no items, no value.

**Order.** Increasing $i$; $c$ in any order.

**Answer.** `dp[n][W]`.

```python title="0/1 knapsack: table, then rolling array"
def knapsack_table(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(W + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c:
                dp[i][c] = max(dp[i][c], v + dp[i - 1][c - w])
    return dp[n][W]                       # theta(nW) time, theta(nW) memory

def knapsack_rolling(weights, values, W):
    dp = [0] * (W + 1)
    for w, v in zip(weights, values):
        for c in range(W, w - 1, -1):     # DESCENDING: see the pitfall below
            dp[c] = max(dp[c], v + dp[c - w])
    return dp[W]                          # theta(nW) time, theta(W) memory
```

:::pitfall The direction of the inner loop
In the rolling version the inner loop must run **downwards**. Going upwards
would let `dp[c - w]` already include item $i$, so the item could be used
more than once --- which is the *unbounded* knapsack, a different problem.
Reversing one loop changes which problem you are solving, silently. (If you
*want* unbounded knapsack, loop upwards; that is the trick, not a bug.)
:::

:::note "Pseudo-polynomial" means what it says
$\Theta(nW)$ looks polynomial but $W$ is a *value*, not an input length. A
capacity written with 64 bits gives $W$ up to $2^{64}$, so the running time
is exponential in the input *size*. 0/1 knapsack is NP-hard; the DP is
efficient only when $W$ is small. The same caveat applies to coin change and
subset-sum.
:::

## Top-down or bottom-up?

| | Top-down (memoised recursion) | Bottom-up (tabulation) |
|---|---|---|
| Written as | the recurrence, directly | nested loops |
| Computes | only reachable states | all states |
| Order | automatic | you must find it |
| Memory | recursion stack + cache | table only |
| Speed in Python | slower (call + hash per state) | 10--50x faster |
| Memory optimisation | hard | easy (drop dimensions) |
| When it wins | sparse or hard-to-order state space | dense state space, big $n$ |

@tbl: The two directions. Write top-down first --- it is a transcription of the recurrence and therefore hard to get wrong --- then convert to bottom-up if you need the speed or the memory.

```python title="The same knapsack, top-down"
from functools import lru_cache

def knapsack_topdown(weights, values, W):
    @lru_cache(maxsize=None)
    def best(i, c):
        if i == 0:
            return 0
        skip = best(i - 1, c)
        take = (values[i - 1] + best(i - 1, c - weights[i - 1])
                if weights[i - 1] <= c else 0)
        return max(skip, take)
    return best(len(weights), W)
```

## Recovering the solution, not just its value

Memory optimisation destroys the table you would traceback through. Two
standard fixes.

**Keep a decision table.** Store one bit per state ("did we take item $i$?"),
which is $\Theta(nW)$ bits rather than $\Theta(nW)$ integers --- often a 32x
saving and enough to fit.

**Hirschberg's divide-and-conquer traceback.** For sequence alignment
(Chapter 19) you can compute the optimal alignment in $\Theta(nm)$ time and
$\Theta(\min(n,m))$ memory by recursively finding the midpoint of the optimal
path: run the DP forwards to the middle row and backwards from the end, add
the two rows, and the argmin is where the optimal path crosses. Then recurse
on the two halves. The time doubles; the memory becomes linear. This is the
standard trick in bioinformatics and it is worth knowing because the same
idea reappears as gradient checkpointing.

## The standard shapes

| Shape | State | Typical recurrence | Examples |
|---|---|---|---|
| Linear / prefix | `dp[i]` | from `dp[i-1]`, `dp[i-2]`, … | Fibonacci, house robber, LIS |
| Two sequences | `dp[i][j]` | from three neighbours | edit distance, LCS, DTW |
| Knapsack | `dp[i][c]` | take / skip | subset sum, coin change, partition |
| Interval | `dp[i][j]` | split at $k$ in $(i,j)$ | matrix chain, optimal BST, burst balloons |
| Tree | `dp[v][state]` | combine children | tree independent set, tree diameter |
| Bitmask | `dp[mask][i]` | add one element to the set | TSP, assignment, scheduling |
| Digit | `dp[pos][tight][…]` | choose next digit | counting numbers with a property |
| On a DAG | `dp[v]` | over incoming edges | longest path, autograd, Viterbi |

@tbl: Eight DP shapes that cover the overwhelming majority of problems. Identifying the shape tells you the state and usually the recurrence.

```python title="Longest increasing subsequence: two ways"
def lis_quadratic(a):
    dp = [1] * len(a)                       # dp[i]: LIS ending at i
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)               # theta(n^2)

from bisect import bisect_left
def lis_nlogn(a):
    tails = []                              # tails[k]: smallest tail of an
    for x in a:                             # increasing subsequence of length k+1
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)                       # theta(n log n)
```

The second version is not a faster DP; it is a different algorithm that
maintains a cleverer invariant. It illustrates a general point: once you have
a correct DP, look for structure in the recurrence --- monotonicity,
convexity, a matrix that can be exponentiated --- that lets you evaluate it
faster than state-by-state. Convex hull trick, divide-and-conquer
optimisation, Knuth optimisation and matrix-power DP are all instances.

:::ml Gradient checkpointing is a dynamic program
Training uses memory proportional to the number of stored activations. If you
store none, you must recompute the entire forward pass for every backward
step; if you store all, memory is $\Theta(L)$ for $L$ layers. Checkpointing
stores a subset and recomputes the rest.

The optimal policy --- which layers to store, given a memory budget --- is a
dynamic program over (layer range, budget), and it is exactly the same shape
as knapsack. The famous $\Theta(\sqrt{L})$ result (store every
$\sqrt{L}$-th layer, recompute within a segment) is the solution for a
uniform-cost network, giving $\Theta(\sqrt{L})$ memory for one extra forward
pass. Real implementations (`torch.utils.checkpoint`, DeepSpeed) solve the
non-uniform version numerically. This is a space--time tradeoff computed by
DP, running inside your training loop.
:::

:::ml Two more dynamic programs you are already running
**Beam search with length normalisation** is a truncated DP over
(position, partial hypothesis).

**Optimal batch splitting for pipeline parallelism** --- how to divide a
model into stages so that the slowest stage is as fast as possible --- is an
interval DP over layer ranges, and is what a pipeline partitioner solves.
:::

:::exercise
1. For each of these, write the state definition in one English sentence:
   (a) longest common subsequence; (b) minimum number of coins for amount
   $A$; (c) maximum sum of non-adjacent elements; (d) the number of distinct
   ways to decode a digit string.
2. Implement `knapsack_rolling` with the inner loop ascending, and show
   empirically that it solves unbounded knapsack instead.
3. Implement coin change (minimum coins) both top-down and bottom-up, and
   measure the ratio at $A = 10^5$.
4. Add a decision table to `knapsack_rolling` so that it also returns the
   chosen items, using $\Theta(nW)$ *bits*.
5. Implement matrix-chain multiplication ($\Theta(n^3)$ interval DP) and use
   it to find the cheapest order to multiply a chain of 15 matrices with
   random dimensions. Compare to left-to-right.
6. Implement the $\Theta(n \log n)$ LIS and extend it to *return* the
   subsequence, not just its length.
7. Implement bitmask DP for the travelling salesman problem on 18 cities,
   $\Theta(2^n n^2)$. Measure the memory and explain why 25 cities is out of
   reach.
8. Formulate gradient checkpointing as a DP: given $L$ layers with forward
   costs $f_i$, recompute costs $r_i$ and activation sizes $s_i$, and a
   memory budget $M$, minimise total recomputation. Write the recurrence.
:::

:::recap
- DP needs optimal substructure *and* overlapping subproblems; without
  overlap use divide and conquer, and with a provable safe choice use greedy.
- The five steps: define the state in a sentence, write the recurrence by
  enumerating last decisions, fix the base cases, choose an order that
  respects dependencies, read off the answer and optimise memory.
- Write top-down first (it transcribes the recurrence), convert to bottom-up
  for speed and memory.
- Rolling arrays reduce memory by a dimension; the loop direction then
  encodes which problem you are solving.
- To recover the solution after memory optimisation, keep a bit-level
  decision table or use Hirschberg's divide-and-conquer traceback.
- Eight standard shapes cover most problems; identifying the shape gives you
  the state.
- Pseudo-polynomial bounds like $\Theta(nW)$ are exponential in input size.
- Gradient checkpointing and pipeline partitioning are dynamic programs
  running inside your training stack.
:::
