# Complexity: Counting What Actually Costs You
@short: Complexity
@subtitle: Asymptotic analysis as a working tool, not an exam topic
@tier: foundation
@prereq: Chapter 1
@blurb: Asymptotic analysis has a reputation for being the dull, formal part of algorithms. It is neither dull nor especially formal once you see what it is for: it is a device for throwing away the parts of a cost that depend on your laptop, so that what remains depends only on the algorithm. This chapter builds that device from scratch, then shows exactly where it lies to you.
@objectives:
- Count the operations an algorithm performs without counting them one by one
- State and use the definitions of $O$, $\Omega$ and $\Theta$ correctly
- Read complexity off a piece of code in seconds, including nested and recursive code
- Perform an amortised analysis using the aggregate, accounting and potential methods
- Know the complexity of every common Python operation by heart
- Say precisely what asymptotic notation hides, and when that matters more than the notation

## The question complexity answers

Suppose you have two implementations of the same function and you want to
know which is better. You could time them. That answer is contaminated by
your CPU, your Python version, whether a background process was running,
how warm the cache was, and the specific input you happened to use.

Asymptotic analysis asks a narrower question with a more durable answer:
**as the input grows, how does the cost grow?** A function that takes
$3n + 40$ microseconds and one that takes $0.5n + 2000$ microseconds are
both *linear*: double the input and both roughly double. A function that
takes $0.001n^2$ microseconds is not, and there is some input size beyond
which it loses to both, permanently, on every machine that will ever be
built.

:::insight What the notation is actually for
Asymptotic notation deliberately discards constant factors and lower-order
terms because those are properties of your machine and your compiler, while
the growth rate is a property of your algorithm. It is a change of
coordinates that isolates the part you can control by thinking.
:::

The discipline this imposes is more useful than the notation. When you write
$O(n \log n)$, you are committing to a claim about behaviour at scales you
have not tested, and the claim is falsifiable.

## Counting without counting

Start concretely. Here is a function that finds the two closest values in a
list.

```python title="Closest pair, brute force"
def closest_pair(xs):
    best = float("inf")
    pair = None
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            d = abs(xs[i] - xs[j])
            if d < best:
                best, pair = d, (xs[i], xs[j])
    return pair, best
```

How many times does the inner body run? For $i = 0$ it runs $n - 1$ times,
for $i = 1$ it runs $n - 2$ times, and so on down to zero:

$$\sum_{i=0}^{n-1}(n - 1 - i) = \frac{n(n-1)}{2} = \frac{n^2}{2} - \frac{n}{2}$$

So the exact count is $\frac{1}{2}n^2 - \frac{1}{2}n$ iterations, each doing
a fixed amount of work. We call this $\Theta(n^2)$, and we mean: the leading
term is $n^2$, the $\frac{1}{2}$ is a machine-dependent detail, and the
$-\frac{1}{2}n$ is irrelevant once $n$ is large.

Notice what we did *not* do: we did not count Python bytecodes, or worry
that `abs` is cheaper than `**`, or measure anything. We identified the
dominant repeated operation and counted how many times it happens.

:::note The recipe
1. Find the operation that dominates --- usually the innermost statement in
   the deepest loop, or the recursive call.
2. Count how many times it executes as a function of the input size.
3. Keep only the fastest-growing term and drop its constant.
:::

## The three notations, stated properly

Practitioners use $O$ for everything, and that is usually harmless, but the
three symbols mean genuinely different things and there are moments when the
difference decides an argument.

:::definition Asymptotic bounds
Let $f, g : \mathbb{N} \to \mathbb{R}^+$.

- $f(n) = O(g(n))$ ("$f$ grows no faster than $g$") if there exist constants
  $c > 0$ and $n_0$ such that $f(n) \le c \cdot g(n)$ for all $n \ge n_0$.
- $f(n) = \Omega(g(n))$ ("$f$ grows at least as fast as $g$") if there exist
  $c > 0$ and $n_0$ with $f(n) \ge c \cdot g(n)$ for all $n \ge n_0$.
- $f(n) = \Theta(g(n))$ ("$f$ grows exactly like $g$") if both hold; equivalently
  there are $c_1, c_2 > 0$ and $n_0$ with $c_1 g(n) \le f(n) \le c_2 g(n)$ for
  $n \ge n_0$.
:::

@fig: bigo_definition | 150 | The definition of $f(n) = O(g(n))$ made visible. We are allowed to scale $g$ by any constant we like, and we are allowed to ignore everything before some threshold $n_0$. All that must hold is that beyond that point, the scaled $g$ is an upper envelope.

Two consequences are worth internalising because they are the source of most
confusion.

First, $O$ is an *upper bound*, not a tight one. It is true that binary
search is $O(n^2)$. It is a useless statement, but it is true, and the fact
that it is true is why $\Theta$ exists. When you say "this is $O(n \log n)$"
you almost always mean $\Theta(n \log n)$; say what you mean when precision
matters.

Second, the equals sign is an abuse of notation. $O(g)$ is a *set* of
functions, and $f = O(g)$ really means $f \in O(g)$. This is why you can
write $n^2 + n = O(n^2)$ but not $O(n^2) = n^2 + n$. Nobody will correct you
in a code review, but knowing it stops you writing nonsense in a design doc.

:::pitfall "Big-O of the worst case" is two independent choices
$O$/$\Omega$/$\Theta$ describe how a function grows. Worst/average/best case
describe *which* function you are talking about. They are orthogonal. It is
perfectly meaningful to say "quicksort's best case is $\Theta(n \log n)$" and
"quicksort's worst case is $\Theta(n^2)$". Saying "quicksort is $O(n \log n)$"
without qualification is simply wrong.
:::

## The hierarchy you must know cold

@fig: growth_curves | 150 | The standard growth hierarchy. Each curve is eventually and permanently below the one above it. The only interesting question for a given problem is which band you are in.

@cols: 14,14,12,12,12,30
| Growth | Name | $n=10$ | $n=1000$ | $n=10^6$ | Typical source |
|---|---|---:|---:|---:|---|
| $O(1)$ | constant | 1 | 1 | 1 | hash lookup, array index |
| $O(\log n)$ | logarithmic | 3 | 10 | 20 | binary search, balanced tree |
| $O(\sqrt{n})$ | root | 3 | 32 | 1000 | block decomposition |
| $O(n)$ | linear | 10 | 1000 | $10^6$ | one pass over the data |
| $O(n \log n)$ | linearithmic | 33 | $10^4$ | $2\times10^7$ | sorting, FFT, divide and conquer |
| $O(n^2)$ | quadratic | 100 | $10^6$ | $10^{12}$ | all pairs, nested loop |
| $O(n^3)$ | cubic | 1000 | $10^9$ | $10^{18}$ | naive matrix multiply |
| $O(2^n)$ | exponential | 1024 | $\approx10^{301}$ | --- | subset enumeration |
| $O(n!)$ | factorial | $3.6\times10^6$ | --- | --- | permutation enumeration |

@tbl: How the standard growth rates behave at three scales. The empty cells are not omissions; those numbers exceed the number of atoms in the observable universe.

Two rows deserve comment because ML engineers meet them constantly.

$O(n \log n)$ is, for practical purposes, *almost linear*. The logarithm of
a billion is thirty. A sorting-based solution to a billion-element problem
costs about thirty times a single pass, and a single pass over a billion
elements is something you were going to do anyway. Do not contort an
algorithm to avoid a sort.

$O(n^2)$ with a small constant beats $O(n \log n)$ with a large one for
surprisingly long. Insertion sort beats merge sort below roughly 32
elements, which is why every production sort (including CPython's Timsort)
switches to insertion sort for small runs. Asymptotics tell you who wins
eventually; they do not tell you when eventually starts.

## Reading complexity off code

With practice this becomes instant. The rules:

**Sequential blocks add.** Two loops one after another, each $\Theta(n)$,
give $\Theta(n) + \Theta(n) = \Theta(n)$. Addition means "take the max".

**Nested loops multiply**, but only if the inner bound is independent of the
outer variable. A loop to $n$ containing a loop to $n$ is $\Theta(n^2)$. A
loop to $n$ containing a loop to $i$ is $\Theta(n^2)$ as well --- we computed
it above --- but a loop to $n$ containing a loop to $\log n$ is
$\Theta(n \log n)$.

**Halving gives a logarithm.** Any loop whose variable is multiplied or
divided by a constant each iteration runs $\Theta(\log n)$ times.

**Recursion needs a recurrence.** `T(n) = 2T(n/2) + O(n)` is $\Theta(n\log n)$;
`T(n) = T(n-1) + O(1)` is $\Theta(n)$; `T(n) = 2T(n-1) + O(1)` is $\Theta(2^n)$.
Chapter 16 gives you the master theorem to do these mechanically.

```python title="Four loops, four complexities"
def a(xs):                       # theta(n)
    return sum(x * x for x in xs)

def b(xs):                       # theta(n^2): inner bound independent of i
    return [[x * y for y in xs] for x in xs]

def c(n):                        # theta(log n): k doubles each step
    k, steps = 1, 0
    while k < n:
        k *= 2
        steps += 1
    return steps

def d(xs):                       # theta(n log n): outer n, inner log n
    total = 0
    for x in xs:
        k = len(xs)
        while k > 1:
            total += x
            k //= 2
    return total
```

:::pitfall The hidden loop
The single most common complexity bug in Python is a library call that looks
atomic but is not. `x in some_list` is $\Theta(n)$. `list.insert(0, x)` is
$\Theta(n)$. `str += piece` inside a loop is $\Theta(n^2)$ overall because
strings are immutable and each concatenation copies. `df.append(row)` in a
pandas loop is $\Theta(n^2)$ for the same reason. None of these looks like a
loop, and all of them are.
:::

## Best, average and worst case

The cost of an algorithm generally depends on which input of size $n$ you
give it, so "the" complexity is ambiguous until you say which input.

- **Worst case** is the maximum over all inputs of size $n$. It is what you
  quote for anything with a latency SLA, because it is a promise.
- **Best case** is the minimum. It is rarely useful except to show an
  algorithm is adaptive: insertion sort is $\Theta(n)$ on sorted input, and
  that is genuinely why Timsort exploits existing runs.
- **Average case** is the expectation over some distribution of inputs.
  This is where people get sloppy: *the average is meaningless without
  naming the distribution*. Quicksort's $\Theta(n \log n)$ average assumes a
  uniformly random pivot, which is why real implementations randomise rather
  than trust the input.

:::ml Why worst case matters more in serving than in training
A training job that occasionally takes 20% longer on one batch is invisible.
An inference service at p99 latency is not: the 1% of requests that hit the
worst case are the ones that page you. This is why production retrieval
systems prefer structures with bounded worst-case behaviour (or a hard
timeout and a fallback) over structures with a better average.
:::

## Amortised analysis: the dynamic array

Some operations are usually cheap and occasionally expensive, and reporting
their worst case is misleading. Python's `list.append` is the canonical
example, and understanding it properly is worth the page it takes.

A Python list is a contiguous block of pointers with some spare capacity.
Appending writes into the spare slot: $\Theta(1)$. When the spare capacity
runs out, the list allocates a larger block, copies everything across, and
frees the old block: $\Theta(n)$. So the worst case of `append` is
$\Theta(n)$ --- and yet a million appends take a million cheap steps, not a
million expensive ones.

@fig: amortized_append | 155 | The cost of each individual append when capacity doubles. The spikes are real, but they are rare in exactly the right proportion: each spike of size $k$ is preceded by $k/2$ appends that cost 1.

:::math Three ways to prove it is $\Theta(1)$ per append
**Aggregate method.** Over $n$ appends, the resizes happen at capacities
$1, 2, 4, \ldots$ up to $n$, costing $1 + 2 + 4 + \cdots + n < 2n$ copies in
total. Add the $n$ cheap writes: total work $< 3n$, so the average per
operation is at most 3. Constant.

**Accounting method.** Charge every append 3 credits: 1 to write its own
value, and 2 saved on the object. When the array of size $k$ doubles, the
$k/2$ items appended since the last resize have saved $2 \times k/2 = k$
credits, exactly paying for the $k$ copies. No operation is ever in debt,
so the true total never exceeds the charged total of $3n$.

**Potential method.** Define $\Phi = 2 \cdot \text{size} - \text{capacity}$
(non-negative once the array is at least half full). A cheap append raises
$\Phi$ by 2, so its amortised cost is $1 + 2 = 3$. A doubling append costs
$\text{size}$ real work but drops $\Phi$ from $\text{size}$ to $2$, releasing
$\text{size} - 2$: amortised cost is again about 3.
:::

All three give the same answer, and each generalises differently. The
potential method is the one you will use again --- it reappears in Fibonacci
heaps, splay trees, and the analysis of union--find in Chapter 15.

:::insight Growth factor is the whole trick
The magic is not doubling specifically; it is growing by a constant *factor*.
Growing by a constant *amount* --- say, 1000 slots at a time --- gives
$\Theta(n^2)$ total work for $n$ appends. CPython actually grows by about
1.125x for large lists, trading a bigger constant for less wasted memory.
Go's slices double up to 1024 elements then grow by 1.25x. The factor is a
memory--time knob, and any factor $> 1$ preserves the $\Theta(1)$ amortised
bound.
:::

:::warning Amortised is not average, and not worst case
Amortised $\Theta(1)$ means: *any sequence* of $n$ operations costs
$\Theta(n)$ --- a guarantee, with no probability in it. But a single
operation can still take $\Theta(n)$. If you have a hard per-request latency
bound, amortised analysis does not save you; you need a structure with
worst-case guarantees, or you need to do the resize incrementally.
:::

## Space complexity

Every statement above has a memory analogue, and in ML work memory is
usually the binding constraint rather than time. Two distinctions matter.

**Total space** includes the input. **Auxiliary space** excludes it. An
in-place sort uses $\Theta(1)$ auxiliary space even though it touches $n$
elements; merge sort uses $\Theta(n)$ auxiliary space, which is precisely why
NumPy's `np.sort` defaults to quicksort rather than mergesort.

**The recursion stack counts.** A recursive function of depth $d$ uses
$\Theta(d)$ space even if it allocates nothing. Naive recursion over a linked
list of a million nodes does not merely run slowly --- it raises
`RecursionError`, and in a compiled language it segfaults.

```python title="Same output, very different memory"
# theta(n) extra memory: the whole list is materialised.
squares = [x * x for x in range(10**8)]        # ~4 GB, will be killed

# theta(1) extra memory: one value at a time.
total = sum(x * x for x in range(10**8))       # fine
```

:::ml The memory ladder you actually live on
For a transformer of $P$ parameters trained in mixed precision with Adam, the
optimiser state alone is roughly $12P$ bytes (fp32 master weights, first and
second moments), plus $2P$ for bf16 weights and $2P$ for gradients: about
$16P$ bytes before a single activation is stored. For a 7-billion-parameter
model that is 112 GB --- which is why sharding, offloading, and
activation checkpointing (a dynamic-programming space--time tradeoff, see
Chapter 18) exist at all.
:::

## The complexity of Python itself

You cannot reason about your code without knowing the cost of the primitives
you build on. These are the ones worth memorising.

@cols: 26,15,15,19,17
| Operation | `list` | `deque` | `dict` / `set` | `heapq` list |
|---|---|---|---|---|
| index / access by key | $\Theta(1)$ | $\Theta(n)$ | $\Theta(1)^*$ | --- |
| append / push right | $\Theta(1)^\dagger$ | $\Theta(1)$ | $\Theta(1)^*$ | $\Theta(\log n)$ |
| pop right | $\Theta(1)$ | $\Theta(1)$ | $\Theta(1)^*$ | --- |
| insert / pop left | $\Theta(n)$ | $\Theta(1)$ | --- | --- |
| membership `in` | $\Theta(n)$ | $\Theta(n)$ | $\Theta(1)^*$ | $\Theta(n)$ |
| min / pop min | $\Theta(n)$ | $\Theta(n)$ | $\Theta(n)$ | $\Theta(\log n)$ |
| sort | $\Theta(n\log n)$ | --- | --- | --- |
| `+` concatenate | $\Theta(n+m)$ | --- | --- | --- |
| slice `a[i:j]` | $\Theta(j-i)$ | --- | --- | --- |

@tbl: Complexity of Python's core containers. $^*$ expected, amortised, assuming well-distributed hashes. $^\dagger$ amortised.

:::pitfall Three real bugs these tables prevent
1. `while queue: item = queue.pop(0)` --- a BFS written with a list instead of
   a `deque` is $\Theta(n^2)$. Every ML engineer writes this once.
2. `if candidate in seen_list` inside a dedup loop --- $\Theta(n^2)$. Use a
   `set`; the change takes four characters and turns hours into seconds.
3. `sorted(scores)[-k:]` to get the top $k$ --- $\Theta(n \log n)$ where
   `heapq.nlargest(k, scores)` is $\Theta(n \log k)$. For $n = 10^7$ and
   $k = 10$ that is a 20x difference, and Chapter 13 explains why.
:::

## What complexity hides, and when that matters

This is the part most courses omit, and it is the part that decides real
performance.

**Constants are not small.** A hash table lookup and an array index are both
$\Theta(1)$, and the array index is about 20 times faster. A B-tree and a
balanced binary search tree are both $\Theta(\log n)$, and on disk the B-tree
is a hundred times faster because it matches the page size. Chapter 31.

**Memory traffic is invisible to the operation count.** Two $\Theta(n)$ loops
over the same array can differ by 10x depending on access order, because one
streams cache lines and the other thrashes. Chapter 3 is entirely about this
and it is, empirically, the highest-value chapter in Part I.

**The model of computation may be wrong.** On a GPU, the cost of an algorithm
is dominated by memory movement and by how uniformly its threads branch, not
by its operation count. FlashAttention performs *more* arithmetic than naive
attention and is several times faster, because it moves far less data.
Chapter 40 derives this.

**$n$ may not be what you think.** For a nearest-neighbour query over $n$
vectors of dimension $d$, the honest complexity is $\Theta(nd)$, and in
practice $d$ dominates the constant. Always name every parameter in the
bound: $\Theta(nd)$, $\Theta(V E)$, $\Theta(bnh d)$.

:::hardware A cost model that fits on a line
$\text{time} \approx \max\!\left(\dfrac{\text{FLOPs}}{\text{peak FLOP/s}},\ \dfrac{\text{bytes moved}}{\text{memory bandwidth}}\right)$

The ratio $\text{FLOPs} / \text{bytes}$ is called *arithmetic intensity*. If
it is below your hardware's ratio of peak-FLOPs to bandwidth (about 100 on a
modern accelerator, about 10 on a CPU), you are memory-bound and reducing
operation count will do nothing at all. Batched matrix multiply is
compute-bound; elementwise activation, layer norm, and attention decoding
are memory-bound. Chapter 40.
:::

## A worked example: three ways to find the top k

The value of all this is that it turns a vague "make it faster" into a
decision you can make on paper. Suppose you need the $k$ highest-scoring
items out of $n$ candidates in a reranking stage.

| Approach | Time | Auxiliary space | When it wins |
|---|---|---|---|
| Sort, take last $k$ | $\Theta(n \log n)$ | $\Theta(n)$ | $k$ close to $n$; you need full order anyway |
| Min-heap of size $k$ | $\Theta(n \log k)$ | $\Theta(k)$ | $k \ll n$; streaming input; bounded memory |
| Quickselect | $\Theta(n)$ expected | $\Theta(1)$ | Data in memory, $k$ arbitrary, order not needed |
| `np.argpartition` | $\Theta(n)$ | $\Theta(n)$ | NumPy array; wins on constants by 10--50x |

@tbl: Four ways to take the top $k$. All four are correct; the difference at $n = 10^7$, $k = 100$ is over two orders of magnitude.

The heap version is the one to reach for when the candidates arrive as a
stream and you cannot hold them all, which is the normal situation in a
retrieval pipeline. Chapter 13 builds it.

:::exercise
1. Give the complexity of each: (a) a loop that runs `n` times containing a
   `sorted()` of a fixed-size 100-element list; (b) a loop that runs `n`
   times containing `sorted()` of the full `n` elements; (c) a recursive
   function that calls itself twice on inputs of size $n/2$ and does
   $\Theta(1)$ work.
2. Prove that $\log_a n = \Theta(\log_b n)$ for any constants $a, b > 1$.
   Explain why this justifies writing $O(\log n)$ without a base.
3. An array grows by a fixed 1024 slots whenever it fills. Show that $n$
   appends cost $\Theta(n^2)$ in total, and find the crossover $n$ at which
   this becomes slower than doubling for a specific copy cost.
4. Using the potential method, show that a stack supporting `push`, `pop`
   and `multipop(k)` (pop up to $k$ items) has $\Theta(1)$ amortised cost per
   operation even though `multipop` is $\Theta(k)$.
5. You profile a training step at batch size 32 and at batch size 64 and
   find times of 41 ms and 79 ms. At 512 you measure 690 ms rather than the
   predicted 630 ms. Give two distinct explanations and an experiment that
   distinguishes them.
6. `str.join` on a list of $n$ pieces is $\Theta(\text{total length})$, while
   repeated `s += piece` is $\Theta(n \cdot \text{total length})$ in the worst
   case. Explain why, then explain why CPython sometimes makes the second one
   fast anyway --- and why you should not rely on that.
:::

:::recap
- Asymptotic notation exists to discard machine-dependent constants and
  isolate the growth rate, which is the part you control by design.
- $O$ is an upper bound, $\Omega$ a lower bound, $\Theta$ both. Best, average
  and worst case are a separate axis; state both.
- Read complexity by finding the dominant repeated operation and counting
  its executions: blocks add, independent nested loops multiply, halving
  gives a logarithm, recursion needs a recurrence.
- Amortised analysis (aggregate, accounting, potential) proves that dynamic
  arrays give $\Theta(1)$ appends. Amortised is a guarantee over sequences,
  not a probability, and not a worst-case bound on one operation.
- Memorise the Python container table; three of the most common performance
  bugs in ML code are direct consequences of not knowing it.
- Complexity hides constants, memory traffic, the machine model, and
  sometimes the real parameters. On accelerators, bytes moved usually matters
  more than operations performed.
:::
