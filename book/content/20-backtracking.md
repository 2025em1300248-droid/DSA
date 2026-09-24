# Backtracking and Combinatorial Search
@short: Backtracking
@subtitle: Exhaustive search that is not actually exhaustive
@tier: core
@prereq: Chapters 8, 18
@blurb: Some problems have no structure to exploit: no greedy rule, no overlapping subproblems, no polynomial algorithm at all. For those, the honest approach is to search --- but to search intelligently, cutting off whole regions of the space as soon as they are provably hopeless. This chapter builds the template, then shows the pruning techniques that make the difference between seconds and centuries.
@objectives:
- Write the choose / explore / un-choose template correctly
- Prune with feasibility checks, bounds and symmetry breaking
- Implement permutations, subsets, $N$-queens, Sudoku and graph colouring
- Understand branch and bound, and the role of a good heuristic ordering
- Distinguish backtracking from DP and from beam search
- Recognise where constrained search appears in ML systems

## The template

```python title="Choose, explore, un-choose"
def backtrack(state, partial, results):
    if is_complete(partial):
        results.append(snapshot(partial))       # copy! see the pitfall
        return
    for choice in candidates(state, partial):
        if not feasible(partial, choice):
            continue                            # prune
        apply(partial, choice)                  # choose
        backtrack(state, partial, results)      # explore
        undo(partial, choice)                   # un-choose
```

The `undo` is the defining feature. Instead of copying the state at every
node --- which would cost $\Theta(n)$ per node and dominate everything ---
you mutate one shared state and restore it on the way out. The saving is
the difference between $\Theta(n \cdot \text{nodes})$ and
$\Theta(\text{nodes})$.

:::pitfall Forgetting to copy at the leaf
`results.append(partial)` appends a *reference* to the mutable state, which
will be undone on the way back up. Every entry in `results` then ends up
identical (usually empty). Use `partial[:]`, `list(partial)`, or
`tuple(partial)`. This is the single most common backtracking bug.
:::

```python title="Permutations and subsets, the two skeletons"
def permutations(nums):
    out, used, cur = [], [False] * len(nums), []
    def go():
        if len(cur) == len(nums):
            out.append(cur[:])               # copy
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True; cur.append(x)
            go()
            cur.pop(); used[i] = False
    go()
    return out                                # theta(n * n!)

def subsets(nums):
    out, cur = [], []
    def go(i):
        if i == len(nums):
            out.append(cur[:])
            return
        go(i + 1)                             # exclude nums[i]
        cur.append(nums[i]); go(i + 1); cur.pop()   # include nums[i]
    go(0)
    return out                                # theta(n * 2^n)
```

## Pruning is the algorithm

Unpruned, $N$-queens for $N = 8$ examines $8^8 = 16.7$ million placements.
With three simple prunes it examines about two thousand nodes --- a factor
of eight thousand, from four lines of code.

@fig: nqueens_prune | 128 | Pruning cuts entire subtrees. Every node you never visit is an entire branch of the search space eliminated, so the savings compound multiplicatively with depth.

```python title="N-queens with O(1) conflict checks"
def n_queens(n):
    cols = [False] * n
    diag1 = [False] * (2 * n)          # r + c is constant on this diagonal
    diag2 = [False] * (2 * n)          # r - c + n is constant on this one
    placement, solutions = [], []

    def go(r):
        if r == n:
            solutions.append(placement[:])
            return
        for c in range(n):
            d1, d2 = r + c, r - c + n
            if cols[c] or diag1[d1] or diag2[d2]:
                continue                       # prune in theta(1)
            cols[c] = diag1[d1] = diag2[d2] = True
            placement.append(c)
            go(r + 1)
            placement.pop()
            cols[c] = diag1[d1] = diag2[d2] = False

    go(0)
    return solutions
```

The three boolean arrays make the feasibility test $\Theta(1)$ rather than
$\Theta(r)$. That is the general lesson: **maintain enough incremental state
that pruning is cheap**, exactly as in the sliding window of Chapter 11.

### The four pruning techniques

**1. Feasibility pruning.** Reject a partial solution that already violates
a constraint. The earlier you detect it, the more you save.

**2. Bound pruning (branch and bound).** Compute an optimistic bound on the
best completion of the current partial solution. If the bound is no better
than the best solution found so far, abandon the branch. This turns
exhaustive search into something usable for optimisation problems.

**3. Symmetry breaking.** If two branches produce equivalent solutions,
explore only one. In $N$-queens, restricting the first queen to the left half
halves the work. In subset problems, requiring indices to increase avoids
generating each subset $k!$ times. In graph colouring, fixing the colour of
the first vertex removes a factor of $k!$.

**4. Ordering heuristics.** Choose the *most constrained variable* next
(fewest remaining legal values) and try the *least constraining value*
first. For Sudoku this alone is the difference between minutes and
milliseconds, because it forces contradictions to surface immediately.

```python title="Sudoku with most-constrained-variable ordering"
def solve_sudoku(grid):
    """grid: 9x9 list of ints, 0 = empty. Solves in place."""
    def candidates(r, c):
        used = set(grid[r]) | {grid[i][c] for i in range(9)}
        br, bc = 3 * (r // 3), 3 * (c // 3)
        used |= {grid[br + i][bc + j] for i in range(3) for j in range(3)}
        return [v for v in range(1, 10) if v not in used]

    best, best_opts = None, None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                opts = candidates(r, c)
                if not opts:
                    return False                    # dead end, prune now
                if best_opts is None or len(opts) < len(best_opts):
                    best, best_opts = (r, c), opts
                    if len(opts) == 1:
                        break                       # cannot do better
    if best is None:
        return True                                 # no empty cells: solved
    r, c = best
    for v in best_opts:
        grid[r][c] = v
        if solve_sudoku(grid):
            return True
        grid[r][c] = 0                              # un-choose
    return False
```

:::insight Branch and bound in one sentence
Keep the best complete solution found so far; prune any branch whose
optimistic bound cannot beat it. Everything else --- the choice of bound,
the exploration order, the data structures --- is engineering around that
one idea, and it is how integer programming solvers, TSP solvers and
alpha--beta game search all work.
:::

## Backtracking versus its neighbours

| Technique | Explores | Memory | Optimal? | Use when |
|---|---|---|---|---|
| Backtracking | a tree, with undo | $\Theta(\text{depth})$ | yes, if exhaustive | no structure to exploit |
| Branch and bound | a pruned tree | $\Theta(\text{depth})$ | yes | optimisation with a good bound |
| Dynamic programming | a DAG of states | $\Theta(\text{states})$ | yes | subproblems overlap |
| Greedy | one path | $\Theta(1)$ | only with proof | exchange argument holds |
| Beam search | $b$ paths | $\Theta(b)$ | no | state space too large, approximate is fine |
| MCTS | a sampled tree | $\Theta(\text{nodes kept})$ | asymptotically | huge branching, simulation available |

@tbl: The search spectrum. Note the progression: backtracking explores everything, beam search keeps the best $b$ and discards the rest, and MCTS decides where to look by sampling. They are the same tree, explored with different budgets.

:::ml Search in machine learning systems
**Beam search** (Chapter 35) is backtracking with a hard memory cap and no
undo: at each depth, keep the $b$ best partial sequences and discard the
rest. It is not optimal and cannot be made so, but the failure mode is
benign.

**Constrained decoding** is backtracking's feasibility pruning applied to
token generation: a grammar or regex automaton says which tokens are legal
in the current state, and the rest are masked out of the softmax. Unlike
backtracking there is no undo --- the model cannot take back an emitted
token --- so the automaton must guarantee that every legal prefix can be
completed. That guarantee is what distinguishes a correct grammar-constrained
sampler from one that paints itself into a corner.

**Neural architecture search and hyperparameter search** are branch and
bound with a learned or statistical bound; successive halving and Hyperband
are precisely "prune the branches whose optimistic bound is poor, cheaply".

**Alpha--beta pruning** in game-playing systems is branch and bound with two
bounds, and MCTS replaces the bound with a statistical estimate from
rollouts.
:::

:::pitfall Backtracking on an exponential space is still exponential
Pruning changes the constant and often the effective base, not the
complexity class. $N$-queens is fine to $N \approx 30$; TSP by branch and
bound is fine to perhaps 50 cities with a good bound; Boolean satisfiability
solvers routinely handle a million variables *because industrial instances
have structure*, not because the algorithm is polynomial. Know which regime
you are in before promising a runtime.
:::

:::exercise
1. Implement `combinations(n, k)` by backtracking with index-increasing
   symmetry breaking. Verify the count is $\binom{n}{k}$.
2. Instrument `n_queens` to count visited nodes with and without the diagonal
   pruning, for $N = 6, 8, 10$. Plot the ratio.
3. Add symmetry breaking to `n_queens` (restrict the first row to the left
   half, handling odd $N$) and measure the saving.
4. Implement the word-break problem two ways: backtracking with memoisation,
   and bottom-up DP. Explain when each is preferable.
5. Implement branch and bound for the 0/1 knapsack using the fractional
   relaxation as the upper bound (Chapter 17). Compare visited nodes to the
   DP's table size for $n = 40$ and $W = 10^6$.
6. Implement graph colouring with most-constrained-variable ordering and test
   it on random graphs of increasing density. Find the density at which it
   becomes intractable.
7. Write a constrained decoder that generates only strings matching a given
   regular expression, by compiling the regex to a DFA and masking logits.
   What must be true of the DFA for the decoder never to get stuck?
:::

:::recap
- The template is choose / explore / un-choose; mutate shared state and
  restore it rather than copying, and copy only at the leaf.
- Pruning is the algorithm, not an optimisation: feasibility checks, bounds,
  symmetry breaking and ordering heuristics each cut whole subtrees, and
  their effects compound with depth.
- Maintain incremental state so that feasibility tests are $\Theta(1)$.
- Branch and bound keeps the best solution so far and prunes any branch whose
  optimistic bound cannot beat it.
- Most-constrained-variable ordering surfaces contradictions early and is
  often the single largest win.
- Beam search, constrained decoding, alpha--beta and MCTS are all the same
  tree explored under different budgets.
- Pruning improves the base of the exponential, not the complexity class.
:::
