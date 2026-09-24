# Divide and Conquer
@short: Divide and Conquer
@subtitle: Break it, solve the pieces, pay for the glue
@tier: core
@prereq: Chapter 8
@blurb: Divide and conquer is the first of the four design paradigms, and the one with the cleanest analysis: split the problem into independent subproblems, solve them recursively, and combine. The master theorem turns that description into a complexity in about ten seconds, and the same structure is what makes an algorithm parallelisable --- which is why this paradigm matters more on modern hardware than it did on a single core.
@objectives:
- Recognise the divide-and-conquer structure and write down its recurrence
- Apply the master theorem, including all three cases and when it does not apply
- Derive the cost of merge sort, binary search, Karatsuba and Strassen
- Use divide and conquer for counting inversions and closest pairs
- Understand why divide and conquer maps onto parallel hardware
- Know when the combine step makes the whole approach pointless

## The structure

```python title="The shape"
def solve(problem):
    if small(problem):
        return base_case(problem)
    subproblems = divide(problem)              # a pieces, each of size n/b
    answers = [solve(s) for s in subproblems]  # independent: can be parallel
    return combine(answers)                    # cost f(n)
```

The resulting recurrence is

$$T(n) = a \cdot T(n/b) + f(n)$$

with $a$ the number of subproblems, $b$ the shrink factor, and $f(n)$ the
cost of dividing and combining. Three numbers determine everything.

:::insight The key word is *independent*
The subproblems must not depend on one another's answers. When they do
overlap, this paradigm recomputes them exponentially often and you should be
doing dynamic programming instead (Chapter 18). "Do the subproblems overlap?"
is the single question that separates the two chapters.
:::

## The master theorem

@fig: master_levels | 128 | The three regimes. Compare the total work at the leaves, $n^{\log_b a}$, with the work at the root, $f(n)$. One dominates, or they balance.

:::theorem Master theorem
Let $T(n) = a T(n/b) + f(n)$ with $a \ge 1$, $b > 1$. Write
$c = \log_b a$, so $n^c$ is the number of leaves.

1. If $f(n) = O(n^{c - \varepsilon})$ for some $\varepsilon > 0$, then
   $T(n) = \Theta(n^c)$. *(Leaves dominate.)*
2. If $f(n) = \Theta(n^c \log^k n)$ with $k \ge 0$, then
   $T(n) = \Theta(n^c \log^{k+1} n)$. *(Balanced.)*
3. If $f(n) = \Omega(n^{c + \varepsilon})$ and $a f(n/b) \le d f(n)$ for some
   $d < 1$ and large $n$ (the regularity condition), then
   $T(n) = \Theta(f(n))$. *(Root dominates.)*
:::

The intuition is worth more than the statement. The recursion tree has
$\log_b n$ levels; level $i$ contains $a^i$ nodes each doing $f(n/b^i)$ work.
The leaves number $a^{\log_b n} = n^{\log_b a}$. So you are comparing a
geometric series' two ends: if the terms grow going down, the leaves
dominate; if they shrink, the root dominates; if they are equal, multiply by
the number of levels.

| Recurrence | $a$ | $b$ | $n^{\log_b a}$ | $f(n)$ | Case | $T(n)$ |
|---|---|---|---|---|---|---|
| Binary search | 1 | 2 | $n^0 = 1$ | $\Theta(1)$ | 2 | $\Theta(\log n)$ |
| Merge sort | 2 | 2 | $n$ | $\Theta(n)$ | 2 | $\Theta(n \log n)$ |
| Tree traversal | 2 | 2 | $n$ | $\Theta(1)$ | 1 | $\Theta(n)$ |
| Karatsuba | 3 | 2 | $n^{1.585}$ | $\Theta(n)$ | 1 | $\Theta(n^{1.585})$ |
| Strassen | 7 | 2 | $n^{2.807}$ | $\Theta(n^2)$ | 1 | $\Theta(n^{2.807})$ |
| Naive matmul | 8 | 2 | $n^3$ | $\Theta(n^2)$ | 1 | $\Theta(n^3)$ |
| Closest pair | 2 | 2 | $n$ | $\Theta(n)$ | 2 | $\Theta(n \log n)$ |
| Quickselect (expected) | 1 | 2 | 1 | $\Theta(n)$ | 3 | $\Theta(n)$ |

@tbl: The master theorem applied. Notice how Karatsuba and Strassen both buy their speedup by trading one multiplication for several additions --- reducing $a$ at the cost of a larger $f(n)$, which is worth it because $a$ sits in an exponent.

:::warning When the master theorem does not apply
It requires subproblems of *equal* size and a polynomial $f$. It says nothing
about $T(n) = T(n-1) + n$ (not a constant-factor shrink), about
$T(n) = T(n/3) + T(2n/3) + n$ (unequal splits --- draw the tree; the answer is
$\Theta(n \log n)$), or about $T(n) = 2T(n/2) + n/\log n$ (falls in the gap
between cases 1 and 2; the Akra--Bazzi method handles it).
:::

## Karatsuba: why reducing $a$ matters

Multiplying two $n$-digit numbers the schoolbook way is $\Theta(n^2)$. Split
each into halves, $x = x_1 B + x_0$ and $y = y_1 B + y_0$:

$$xy = x_1y_1 B^2 + (x_1y_0 + x_0y_1)B + x_0y_0$$

That is four half-size multiplications: $T(n) = 4T(n/2) + \Theta(n)$, which
by case 1 is $\Theta(n^2)$ --- no gain. Karatsuba's observation is that

$$x_1y_0 + x_0y_1 = (x_1 + x_0)(y_1 + y_0) - x_1y_1 - x_0y_0$$

so three multiplications suffice. $T(n) = 3T(n/2) + \Theta(n) =
\Theta(n^{\log_2 3}) = \Theta(n^{1.585})$.

```python title="Karatsuba multiplication"
def karatsuba(x, y):
    if x < 10 or y < 10:                      # base case: schoolbook
        return x * y
    n = max(x.bit_length(), y.bit_length()) // 2
    mask = (1 << n) - 1
    x1, x0 = x >> n, x & mask
    y1, y0 = y >> n, y & mask
    z2 = karatsuba(x1, y1)
    z0 = karatsuba(x0, y0)
    z1 = karatsuba(x1 + x0, y1 + y0) - z2 - z0   # one multiply, not two
    return (z2 << (2 * n)) + (z1 << n) + z0
```

Strassen's algorithm does the same thing for matrices: eight $n/2$ block
multiplications become seven, giving $\Theta(n^{2.807})$.

:::hardware Why Strassen is rare in practice
Strassen is asymptotically faster and is used, but only above roughly
$n = 1000$ and with care. Three reasons. It is numerically less stable ---
the subtractions cause cancellation, so the error bound is weaker than for
the standard algorithm. It needs $\Theta(n^2)$ temporary matrices, which
hurts on memory-bound hardware. And standard matmul has been optimised into
the ground: a tuned GEMM reaches 90%+ of peak FLOPs through tiling and vector
instructions, so Strassen's 12% fewer operations can easily be outweighed by
worse locality. The asymptotically best known exponent is around 2.37, and
those algorithms are entirely theoretical --- their constants are
astronomical.
:::

## Two classic applications

**Counting inversions.** How far is a permutation from sorted? Count pairs
$(i, j)$ with $i < j$ and $a_i > a_j$. Brute force is $\Theta(n^2)$; merge
sort counts them for free, because during the merge, when an element from
the right half is taken, it is smaller than everything remaining in the left
half.

```python title="Inversions in O(n log n), piggybacking on merge sort"
def sort_count(a):
    if len(a) <= 1:
        return a, 0
    m = len(a) // 2
    left, cl = sort_count(a[:m])
    right, cr = sort_count(a[m:])
    out, i, j, cross = [], 0, 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
            cross += len(left) - i        # all remaining left elements invert
    out += left[i:] + right[j:]
    return out, cl + cr + cross
```

This is exactly how Kendall's $\tau$ rank correlation is computed
efficiently --- a metric you will meet when evaluating rankers.

**Closest pair of points.** Sort by $x$, split at the median, recurse on
both halves to get the best distance $\delta$, then check the strip of width
$2\delta$ around the dividing line. The non-obvious part is that within that
strip, sorted by $y$, each point needs to be compared with at most the next
seven --- a geometric argument --- so the combine step is $\Theta(n)$ and the
total is $\Theta(n \log n)$ rather than $\Theta(n^2)$.

## Divide and conquer is the parallel paradigm

The subproblems are independent, which means they can run on different
cores, different threads, or different machines with no coordination until
the combine step. This is the structural reason divide and conquer matters
more now than when it was invented.

| Sequential algorithm | Parallel form | Where you meet it |
|---|---|---|
| Sum of an array | tree reduction | `all_reduce`, `torch.sum` |
| Prefix sum | Blelloch scan (Chapter 39) | ragged offsets, sampling |
| Merge sort | parallel merge sort / sample sort | GPU sort, Spark shuffle |
| Matrix multiply | block decomposition | every GEMM ever written |
| Max / argmax | tree reduction | `topk`, softmax denominator |
| FFT | butterfly network | convolution, positional encodings |

@tbl: Divide and conquer as the parallel skeleton. In each case the depth of the recursion is the *critical path* --- $\Theta(\log n)$ --- and the total work is the sequential cost.

:::ml Tree reduction is why `all_reduce` scales
Summing gradients across $P$ workers naively means every worker sends to one
master: $\Theta(P)$ messages through one link. A tree reduction has depth
$\Theta(\log P)$ and no hot spot. Ring all-reduce goes further and achieves
optimal bandwidth: each worker sends exactly $2(P-1)/P$ times the parameter
size, *independent of $P$*. Chapter 41 derives it. The structural idea ---
combine pairwise, in a tree --- is this chapter's.
:::

:::pitfall When the combine step kills you
Divide and conquer only wins if `combine` is cheaper than solving the
problem directly. If combining is $\Theta(n^2)$, then
$T(n) = 2T(n/2) + \Theta(n^2) = \Theta(n^2)$ by case 3: you did all that
recursion for nothing. Always check which case you land in *before*
implementing. Equally, if the division is expensive --- copying slices in
Python is $\Theta(n)$ per level and allocates --- you may add a constant
factor that erases the benefit. Pass indices, not slices.
:::

:::exercise
1. Solve with the master theorem: (a) $T(n) = 9T(n/3) + n$;
   (b) $T(n) = T(2n/3) + 1$; (c) $T(n) = 3T(n/4) + n \log n$;
   (d) $T(n) = 2T(n/2) + n \log n$.
2. Show that $T(n) = T(n/3) + T(2n/3) + n$ is $\Theta(n \log n)$ by drawing
   the recursion tree and bounding its depth.
3. Implement Karatsuba and find empirically the input size at which it beats
   schoolbook multiplication in Python. Explain the crossover.
4. Implement `sort_count` and verify it against a brute-force $\Theta(n^2)$
   count on random permutations. Use it to compute Kendall's $\tau$ between
   two rankings of 100,000 items.
5. Implement the closest-pair algorithm and prove the "at most seven
   neighbours in the strip" claim.
6. Implement Strassen's algorithm with a cutoff to standard multiplication
   below size $k$. Tune $k$ and explain why the optimum is well above 2.
7. A divide-and-conquer algorithm splits into three subproblems of size
   $n/2$ and combines in $\Theta(n)$. What is its complexity? Would you use
   it in place of an $\Theta(n \log n)$ alternative? At what $n$?
:::

:::recap
- Divide and conquer: split into $a$ independent subproblems of size $n/b$,
  recurse, combine in $f(n)$. The recurrence $T(n) = aT(n/b) + f(n)$ follows
  directly.
- The master theorem compares $n^{\log_b a}$ (work at the leaves) with
  $f(n)$ (work at the root): whichever dominates polynomially wins; if they
  balance, multiply by $\log n$.
- Reducing $a$ is worth a lot because it sits in an exponent --- the
  insight behind Karatsuba and Strassen.
- Strassen is asymptotically better and practically marginal, because
  standard GEMM is heavily optimised and Strassen is less stable and more
  memory-hungry.
- Counting inversions and closest-pair both ride on the merge structure and
  become $\Theta(n \log n)$.
- Independence of subproblems is what makes this the parallel paradigm:
  tree reductions, scans, block matmul and FFT are all instances.
- If subproblems overlap, use dynamic programming; if combining is as
  expensive as the whole problem, the paradigm buys nothing.
:::
