# The Pattern Catalogue
@short: Pattern Catalogue
@subtitle: Thirty patterns that cover most of what you will be asked
@tier: reference
@prereq: Parts I--VIII
@blurb: This chapter is a reference, not a narrative. Each entry names a pattern, gives the signal that should make you think of it, a template compact enough to memorise, its complexity, and where it appears in real systems. Read it once end to end, then return to it when a problem looks familiar but you cannot place it.
@objectives:
- Recognise thirty recurring problem shapes by their surface signals
- Reproduce a correct template for each from memory
- Know each pattern's complexity and its common failure mode
- Connect each to the chapter that develops it and the ML system that uses it

## How to use this chapter

Each entry has the same five fields: **Signal** (what in the problem
statement points here), **Idea** (one sentence), **Template**, **Cost**, and
**In the wild**. Nothing here is new; everything refers back to a chapter
that derives it.

---

## Array and pointer patterns

### 1. Two pointers, converging

**Signal.** A pair with some property, in a *sorted* array.
**Idea.** Move the pointer whose side of the comparison cannot help.

```python
i, j = 0, len(a) - 1
while i < j:
    s = a[i] + a[j]
    if s == target: return i, j
    if s < target: i += 1
    else: j -= 1
```

**Cost.** $\Theta(n)$ after sorting. **Chapter 11.**
**In the wild.** Merging sorted posting lists; intersecting candidate sets.

### 2. Two pointers, read and write

**Signal.** Remove, dedupe or partition *in place*.
**Idea.** One cursor reads, one writes; the prefix before the write cursor is
the answer.

```python
w = 0
for r in range(len(a)):
    if keep(a[r]):
        a[w] = a[r]; w += 1
return w
```

**Cost.** $\Theta(n)$, $\Theta(1)$ extra. **Chapter 11.**
**In the wild.** GPU stream compaction after a prefix sum (Chapter 39).

### 3. Sliding window, fixed size

**Signal.** A statistic over every window of size $k$.
**Idea.** Add the entering element, remove the leaving one.

```python
s = sum(a[:k]); best = s
for i in range(k, len(a)):
    s += a[i] - a[i - k]
    best = max(best, s)
```

**Cost.** $\Theta(n)$. **Chapter 11.**
**In the wild.** Rolling metrics; $n$-gram shingles; sliding-window attention.

### 4. Sliding window, variable size

**Signal.** Longest or shortest *contiguous* run satisfying a monotone
condition.
**Idea.** Grow right always; shrink left only while invalid.

```python
left = 0
for right in range(len(a)):
    add(a[right])
    while not valid():
        remove(a[left]); left += 1
    best = max(best, right - left + 1)
```

**Cost.** $\Theta(n)$ amortised. **Chapter 11.**
**Failure mode.** The condition must be monotone in the window; with negative
values a sum condition is not.

### 5. Prefix sums

**Signal.** Many range-sum queries on static data.
**Idea.** `pre[i] = a[0] + ... + a[i-1]`; range $[l, r)$ is `pre[r] - pre[l]`.
**Cost.** $\Theta(n)$ build, $\Theta(1)$ query. **Chapters 4, 27.**
**In the wild.** Ragged offsets; sampling by cumulative weight; IoU.

### 6. Difference array

**Signal.** Many range *updates*, one query at the end.
**Idea.** `d[l] += v; d[r] -= v`, then prefix-sum once.
**Cost.** $\Theta(1)$ per update, $\Theta(n)$ once. **Chapter 27.**
**In the wild.** Accumulating attention masks; interval bookkeeping.

### 7. Monotonic stack

**Signal.** "Next greater", "previous smaller", largest rectangle.
**Idea.** Keep a stack sorted; pop everything the new element dominates.

```python
stack, out = [], [-1] * len(a)
for i, x in enumerate(a):
    while stack and a[stack[-1]] < x:
        out[stack.pop()] = i
    stack.append(i)
```

**Cost.** $\Theta(n)$: each index pushed and popped once. **Chapter 6.**

### 8. Monotonic deque

**Signal.** Max or min over every sliding window.
**Idea.** A monotonic stack with removal from the front when indices expire.
**Cost.** $\Theta(n)$. **Chapter 6.**

### 9. Cyclic sort / index-as-hash

**Signal.** Values are a permutation of $1..n$; find missing or duplicate in
$\Theta(1)$ space.
**Idea.** Place each value at its own index, or use the sign of `a[abs(x)]`
as a visited bit.
**Cost.** $\Theta(n)$, $\Theta(1)$ extra.

---

## Search and ordering patterns

### 10. Binary search on an array

**Signal.** Sorted data, a target or a boundary.
**Idea.** Half-open interval, `lower_bound`/`upper_bound`. **Chapter 10.**

### 11. Binary search on the answer

**Signal.** "Minimum $x$ such that …", "can it be done with capacity $c$?"
**Idea.** Find a monotone predicate and bisect the answer space.

```python
lo, hi = 0, upper
while lo < hi:
    mid = lo + (hi - lo) // 2
    if feasible(mid): hi = mid
    else: lo = mid + 1
```

**Cost.** $\Theta(\log(\text{range}) \times \text{cost of } \textit{feasible})$.
**Chapter 10.**
**In the wild.** Calibration thresholds; maximum batch size; temperature for
a target entropy.

### 12. Exponential (galloping) search

**Signal.** Unbounded input, or the answer is near the start.
**Idea.** Double until you bracket, then binary search. $\Theta(\log i)$.
**In the wild.** Timsort's galloping merge; posting-list skipping.

### 13. Quickselect

**Signal.** The $k$-th element, or the top $k$ unordered.
**Idea.** Partition, recurse into one side only. $\Theta(n)$ expected.
**Chapter 9.** Prefer `np.argpartition` when the data is an array.

### 14. Top-$k$ with a bounded heap

**Signal.** Top $k$ of a *stream*, or $k \ll n$ with bounded memory.
**Idea.** A min-heap of size $k$; the root is the weakest survivor.
**Cost.** $\Theta(n \log k)$ time, $\Theta(k)$ space. **Chapter 13.**
**In the wild.** Retrieval candidate sets; beam search; heavy hitters.

### 15. $k$-way merge

**Signal.** Merge $k$ sorted streams.
**Idea.** A heap of one element per stream. $\Theta(N \log k)$, $\Theta(k)$
memory. **Chapter 13.** **In the wild.** External sort; multi-shard retrieval.

---

## Hashing and set patterns

### 16. Hash set for membership

**Signal.** "Have I seen this?", "any duplicates?", "complement exists?"
**Idea.** Trade $\Theta(n)$ memory for $\Theta(1)$ lookup. **Chapter 7.**
**Failure mode.** Memory at scale --- 100 bytes per entry in Python.

### 17. Hash map for grouping

**Signal.** "Group by", "anagrams", "count occurrences".
**Idea.** A canonical key (sorted tuple, character count, normalised form).
**Cost.** $\Theta(n \cdot |\text{key}|)$.

### 18. Prefix-sum plus hash map

**Signal.** Subarrays summing to $k$, with negative values allowed.
**Idea.** Count previously seen prefix sums; `pre[r] - pre[l] == k` means
`pre[l] == pre[r] - k`.

```python
from collections import defaultdict
seen, s, count = defaultdict(int, {0: 1}), 0, 0
for x in a:
    s += x
    count += seen[s - k]
    seen[s] += 1
```

**Cost.** $\Theta(n)$. **The standard replacement for a sliding window when
values can be negative.**

### 19. Sketching

**Signal.** Too large to store exactly; approximate is acceptable.
**Idea.** Bloom for membership, Count--Min for frequency, HyperLogLog for
cardinality, MinHash for similarity. **Chapters 28, 29.**

---

## Tree and graph patterns

### 20. DFS on a tree, combine upward

**Signal.** Any per-subtree quantity.
**Idea.** Recurse on children, combine, return.

```python
def go(node):
    if node is None: return identity
    return combine(node.val, go(node.left), go(node.right))
```

**Cost.** $\Theta(n)$. **Chapter 12.** Use an explicit stack when depth can
exceed a few thousand.

### 21. BFS for shortest path

**Signal.** Fewest steps, unweighted.
**Idea.** Queue, mark on push, parent array is the shortest-path tree.
**Cost.** $\Theta(V + E)$. **Chapter 22.** Multi-source BFS seeds the queue
with all sources.

### 22. Dijkstra / best-first

**Signal.** Cheapest path with non-negative weights.
**Idea.** BFS with a priority queue and lazy deletion.
$\Theta((V+E)\log V)$. **Chapter 23.**

### 23. Topological order

**Signal.** Dependencies, ordering, "is there a cycle?"
**Idea.** Kahn's algorithm; the length check detects cycles.
$\Theta(V+E)$. **Chapter 24.** **In the wild.** Autograd; build systems;
pipeline DAGs.

### 24. Union--find

**Signal.** "Connected", "same group", incremental merging.
**Idea.** Union by rank plus path compression: $\Theta(\alpha(n))$.
**Chapter 15.** **In the wild.** Deduplication clusters; Kruskal.

### 25. Trie

**Signal.** Prefixes, autocomplete, longest match, many patterns at once.
**Idea.** Index by the string itself; add failure links for Aho--Corasick.
**Chapter 14.** **In the wild.** Tokenizers; constrained decoding; prefix
caches.

---

## Dynamic programming patterns

### 26. Linear DP

**Signal.** `dp[i]` depends on a constant number of earlier positions.
**Idea.** One array, one pass; often reducible to $\Theta(1)$ memory.
**Chapter 18.** *Examples.* Climbing stairs, house robber, max subarray.

### 27. Two-sequence DP

**Signal.** Two strings or series compared.
**Idea.** `dp[i][j]` from its three neighbours.
$\Theta(nm)$, $\Theta(\min(n,m))$ memory with a rolling row. **Chapter 19.**
*Examples.* Edit distance, LCS, DTW, alignment.

### 28. Knapsack DP

**Signal.** Choose a subset subject to a budget.
**Idea.** `dp[capacity]`; iterate capacity *downwards* for 0/1, *upwards* for
unbounded. **Chapter 18.**
**In the wild.** Gradient checkpointing; context-window budgeting.

### 29. Interval DP

**Signal.** "Combine adjacent items", "best way to split".
**Idea.** `dp[i][j] = min over k of dp[i][k] + dp[k][j] + cost`.
$\Theta(n^3)$. **Chapter 18.**
**In the wild.** Matrix-chain order; pipeline-stage partitioning.

### 30. Bitmask DP

**Signal.** $n \le 20$ and subsets matter.
**Idea.** `dp[mask][i]` = best over the visited set `mask` ending at `i`.
$\Theta(2^n n^2)$. **Chapter 18.** *Examples.* TSP, assignment, scheduling.

---

## Choosing between similar patterns

| If you are tempted by | But also consider | Because |
|---|---|---|
| Sliding window | prefix sums + hash map | negative values break the window |
| Sorting | heap or quickselect | you may not need a total order |
| A hash map | a sorted array + `searchsorted` | memory at tens of millions of keys |
| DP over all states | greedy with an exchange proof | if a safe choice exists, DP is overkill |
| Recursion | an explicit stack | depth can exceed the limit |
| BFS on a grid | multi-source BFS | if several starts share an answer |
| A balanced tree | a sorted list of sorted lists | constants dominate in Python |
| Exact counting | a sketch | when the data does not fit |
| A new index | brute force | below $10^6$ vectors, a GEMM wins |

@tbl: The second-guess table. Most sub-optimal solutions come from reaching for the first pattern that fits rather than the best one.

:::insight How to actually memorise this
Not by rereading. Take one pattern a day, implement it from memory in ten
minutes, then find one problem in Chapters 45--46 that uses it and solve that
problem *without* looking at the template. Thirty days, thirty patterns, and
the recall is durable because it was reconstructed rather than recognised.
:::

:::recap
- Thirty patterns cover the large majority of algorithmic problems; each has
  a surface signal, a short template and a known cost.
- Array patterns: two pointers (converging and read/write), fixed and
  variable windows, prefix and difference arrays, monotonic stack and deque,
  cyclic sort.
- Search patterns: binary search on an array and on the answer, galloping
  search, quickselect, bounded heaps, $k$-way merge.
- Hash patterns: membership, grouping by canonical key, prefix sums plus a
  map, and sketches when exactness is negotiable.
- Graph patterns: subtree DFS, BFS shortest paths, Dijkstra, topological
  order, union--find, tries.
- DP shapes: linear, two-sequence, knapsack, interval, bitmask.
- Always second-guess the first pattern that fits.
:::
