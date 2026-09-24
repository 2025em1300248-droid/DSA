# Greedy Algorithms
@short: Greedy
@subtitle: Take the best-looking move, and be able to prove you may
@tier: core
@prereq: Chapter 9
@blurb: A greedy algorithm makes the locally best choice and never reconsiders. When that works it is the simplest and fastest approach available; when it does not, it produces confidently wrong answers that pass every small test. The whole skill is knowing which case you are in, and this chapter teaches the two proof techniques that tell you.
@objectives:
- State the two structural properties a problem needs for greedy to be correct
- Prove greedy correctness with an exchange argument and with "greedy stays ahead"
- Solve interval scheduling, Huffman coding and fractional knapsack
- Recognise where greedy fails and what to do instead
- Understand matroids as the general theory behind greedy
- Apply greedy reasoning to batching, caching and beam search

## The pattern and the danger

```python title="Every greedy algorithm"
def greedy(items, key):
    solution = []
    for item in sorted(items, key=key):      # the choice is the sort order
        if feasible(solution, item):
            solution.append(item)            # never reconsidered
    return solution
```

The algorithm is trivial. The *sort order* is the algorithm, and choosing it
correctly is the entire problem. In interval scheduling, sorting by start
time gives a wrong answer, sorting by duration gives a wrong answer, and
sorting by finish time gives the optimum --- with no visible difference in
the code.

@fig: interval_scheduling | 168 | Interval scheduling. Earliest-finish-time is optimal and earliest-start-time is not, on the same input. Nothing about the code distinguishes them; only a proof does.

:::definition The two properties greedy needs
**Greedy choice property.** There exists an optimal solution containing the
greedy first choice. (Equivalently: committing to the greedy choice never
makes the remaining problem worse.)

**Optimal substructure.** After making that choice, an optimal solution to
the remaining subproblem, combined with the choice, is optimal overall.

Optimal substructure alone gives you dynamic programming. The greedy choice
property is the extra ingredient that lets you skip the search.
:::

## Proving greedy correct

Two techniques cover almost everything.

**The exchange argument.** Take any optimal solution $O$. Show that you can
transform it, step by step, into the greedy solution $G$ without making it
worse. Therefore $G$ is optimal too.

:::proof Interval scheduling: earliest finish time is optimal
Let $G = g_1, g_2, \ldots$ be the greedy selection (by earliest finish) and
$O = o_1, o_2, \ldots$ any optimal selection, both sorted by finish time.
Suppose they agree on the first $k$ jobs and differ at $k+1$. By the greedy
rule, $g_{k+1}$ finishes no later than $o_{k+1}$. So replacing $o_{k+1}$ with
$g_{k+1}$ in $O$ leaves it feasible --- $g_{k+1}$ starts after $g_k = o_k$
ends, and finishes no later than $o_{k+1}$ did, so it cannot conflict with
$o_{k+2}$ --- and the same size. Repeating this exchange turns $O$ into a
solution agreeing with $G$ everywhere, with no loss. Hence $|G| = |O|$.
:::

**Greedy stays ahead.** Define a measure of partial progress and show that
after every step, the greedy solution is at least as far along as any other.
In interval scheduling the measure is "the finish time of the $i$-th chosen
job", and greedy's is always $\le$ any other solution's.

:::insight How to test a greedy idea in ninety seconds
Before proving anything, try to break it. Construct the smallest adversarial
input you can: two items where the greedy criterion and the true objective
disagree. If you find one, greedy is wrong and you have a counterexample for
free. If you cannot find one after genuine effort, look for the exchange
argument. Most incorrect greedy algorithms die in the first thirty seconds
of this exercise.
:::

## The canonical correct greedies

**Interval scheduling** (maximise count): sort by finish time.
$\Theta(n \log n)$.

**Fractional knapsack**: sort by value/weight ratio, take greedily, split
the last item. $\Theta(n \log n)$. Note that the 0/1 version --- where you
cannot split --- is *not* greedy-solvable and needs dynamic programming
(Chapter 18). The difference is one word in the problem statement.

**Huffman coding**: repeatedly merge the two least frequent symbols.

```python title="Huffman coding: a greedy algorithm built on a heap"
import heapq
from collections import Counter

def huffman(text):
    freq = Counter(text)
    if len(freq) == 1:                            # degenerate: one symbol
        return {next(iter(freq)): "0"}
    heap = [(f, i, sym) for i, (sym, f) in enumerate(freq.items())]
    heapq.heapify(heap)
    codes = {sym: "" for sym in freq}
    groups = {sym: [sym] for sym in freq}
    nxt = len(freq)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)            # two rarest
        f2, _, b = heapq.heappop(heap)
        for s in groups[a]:
            codes[s] = "0" + codes[s]             # prepend: deepest gets most
        for s in groups[b]:
            codes[s] = "1" + codes[s]
        merged = a + b
        groups[merged] = groups[a] + groups[b]
        heapq.heappush(heap, (f1 + f2, nxt, merged))
        nxt += 1
    return codes
```

The exchange argument for Huffman: in an optimal prefix code the two least
frequent symbols can be assumed to be siblings at maximum depth (otherwise
swap them with whatever is down there --- the cost cannot increase). So
merging them first is safe, and induction does the rest. The result is the
optimal prefix-free code, within one bit per symbol of the entropy.

**Minimum spanning tree** (Kruskal and Prim, Chapter 23) and **Dijkstra's
algorithm** are both greedy with exchange-argument proofs.

## Where greedy fails

| Problem | Greedy gives | Why it fails | Correct approach |
|---|---|---|---|
| 0/1 knapsack | can be arbitrarily bad | taking the best ratio may block a better pair | DP, $\Theta(nW)$ |
| Coin change, arbitrary denominations | may fail entirely | 4, 3, 1 for target 6: greedy gives 4+1+1, optimal is 3+3 | DP, $\Theta(nA)$ |
| Longest path in a DAG | wrong | local best edge is not on the best path | DP over topological order |
| Travelling salesman | $\Theta(\log n)$ factor off | nearest-neighbour paints itself into corners | DP / approximation |
| Set cover | $\ln n$ factor off | unavoidable unless P = NP | greedy *is* the best known |
| Optimal BST | wrong | frequencies interact | DP, $\Theta(n^3)$ or $\Theta(n^2)$ |

@tbl: Greedy failures. Note the last row: sometimes greedy is not optimal but is provably the best you can do in polynomial time, and then its approximation ratio is the result.

:::pitfall The coin-change trap
Greedy coin change is optimal for the US and Euro denominations and wrong in
general. This matters because it is the classic example of an algorithm that
works on every input you are likely to test by hand and fails on inputs a
system will actually produce. Whenever a greedy rule "obviously" works, ask
what property of the specific numbers makes it work --- for coins it is that
each denomination is at least twice the previous one --- and whether your
data guarantees it.
:::

## Matroids: when greedy is *always* right

There is a complete theory, and it is worth knowing it exists.

:::definition Matroid
A matroid is a pair $(E, \mathcal{I})$ where $E$ is a finite set and
$\mathcal{I}$ a family of "independent" subsets satisfying: (1)
$\emptyset \in \mathcal{I}$; (2) subsets of independent sets are independent;
(3) the **exchange property** --- if $A, B \in \mathcal{I}$ and $|A| < |B|$,
there is some $x \in B \setminus A$ with $A \cup \{x\} \in \mathcal{I}$.
:::

:::theorem Rado--Edmonds
For any weight function on $E$, the greedy algorithm --- sort by weight
descending, add each element if it keeps the set independent --- finds a
maximum-weight independent set **if and only if** $(E, \mathcal{I})$ is a
matroid.
:::

Kruskal's algorithm is greedy over the *graphic matroid* (independent = acyclic
edge sets), which is why it is correct. Scheduling unit jobs with deadlines to
maximise profit is greedy over a *transversal matroid*. When your problem's
feasible sets satisfy the exchange property, greedy is guaranteed; when they
do not, you need a proof or a different paradigm.

:::ml Greedy decisions in ML systems
**Length bucketing.** Sort sequences by length, then greedily fill batches
until the padding waste exceeds a threshold. Optimal because, after sorting,
the cost is monotone --- the same structure as interval scheduling.

**Greedy decoding.** Take the argmax token at each step. This is greedy in
the technical sense and it is *not* optimal for sequence likelihood: the
highest-probability token now can lead to a low-probability continuation.
Beam search is the bounded-width relaxation, and it is still not optimal.
Chapter 35.

**Decision-tree induction.** Choosing the split that maximises information
gain at each node is greedy. Finding the globally optimal tree is NP-hard, so
every practical learner is greedy and accepts the suboptimality. Chapter 37.

**Cache admission.** Deciding whether a newly computed embedding is worth
caching, by value density (hit probability / size), is fractional knapsack ---
greedy and optimal if items are divisible, approximate otherwise.

**Token budget allocation in RAG.** Filling a context window with the
highest-relevance-per-token chunks is fractional knapsack again; since chunks
are not divisible, greedy by density is a 2-approximation, which in practice
is entirely acceptable.
:::

:::exercise
1. Give a counterexample showing that sorting intervals by duration does not
   maximise the number of non-overlapping intervals.
2. Prove, by exchange, that fractional knapsack by value/weight ratio is
   optimal. Then give an instance where the same rule applied to 0/1
   knapsack is off by a factor of nearly 2.
3. Implement Huffman coding and verify that the average code length is within
   one bit of the entropy for several distributions.
4. Find a set of coin denominations, all at least twice the previous, for
   which greedy change-making still fails --- or prove no such set exists.
5. Show that the set of forests of a graph forms a matroid, and deduce
   Kruskal's correctness from Rado--Edmonds.
6. Implement length bucketing that minimises total padded tokens given a
   maximum batch size. Prove your greedy rule is optimal or give a
   counterexample.
7. Greedy set cover is a $\ln n$ approximation. Implement it and construct an
   instance where it is a factor of $\ln n$ worse than optimal.
:::

:::recap
- Greedy makes a locally optimal choice and never revisits it; the sort order
  *is* the algorithm.
- Correctness needs the greedy choice property plus optimal substructure.
  Prove it with an exchange argument or by showing greedy stays ahead.
- Before proving, spend ninety seconds trying to break it --- most wrong
  greedy ideas die immediately.
- Correct: interval scheduling by finish time, fractional knapsack by
  density, Huffman by merging rarest pairs, Kruskal, Prim, Dijkstra.
- Wrong: 0/1 knapsack, general coin change, longest path, TSP. For some
  NP-hard problems greedy is the best known approximation and its ratio is
  the result.
- Matroids characterise exactly when greedy always works.
- In ML: length bucketing (correct), greedy decoding (suboptimal by design),
  decision-tree splitting (necessarily suboptimal), context budgeting
  (approximate).
:::
