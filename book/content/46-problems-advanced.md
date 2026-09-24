# Problem Set II: Advanced and ML-Flavoured
@short: Problems II
@subtitle: Twenty-eight harder problems, most of them from real systems
@tier: practice
@prereq: Chapters 22--42
@blurb: The second problem set covers graphs, advanced dynamic programming, and the algorithms of Parts VI through VIII. Many of these are not interview questions --- they are problems you will actually be handed, phrased the way they arrive. Solutions include the design reasoning, not just the code.
@objectives:
- Solve graph, DP and systems problems end to end
- Translate a vague production requirement into a precise algorithmic one
- Choose data structures under real memory and latency budgets
- Justify approximation where exactness is unaffordable

## Graphs

### P31. Course schedule $\dagger$

Given prerequisites, return a valid order or report a cycle.

:::solution
Kahn's algorithm; the length check is the cycle detector (Chapter 24).

```python
from collections import deque, defaultdict

def course_order(n, prereqs):
    adj, indeg = defaultdict(list), [0] * n
    for course, need in prereqs:
        adj[need].append(course)
        indeg[course] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for u in adj[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                q.append(u)
    return order if len(order) == n else []
```
$\Theta(V + E)$.
:::

### P32. Number of islands $\dagger$

:::solution
Connected components on an implicit grid graph. BFS/DFS is $\Theta(mn)$;
union--find is the same asymptotically but wins when the grid is *streamed*
or cells are added over time.

```python
def num_islands(grid):
    if not grid:
        return 0
    m, n, count = len(grid), len(grid[0]), 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] != "1":
                continue
            count += 1
            stack = [(i, j)]
            grid[i][j] = "0"                       # mark on push
            while stack:
                r, c = stack.pop()
                for dr, dc in ((1,0), (-1,0), (0,1), (0,-1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == "1":
                        grid[nr][nc] = "0"
                        stack.append((nr, nc))
    return count
```
:::

### P33. Word ladder

Shortest transformation sequence between two words of equal length.

:::solution
BFS on an implicit graph. The key optimisation is the wildcard index: build
buckets keyed by `"h*t"` so neighbours are $\Theta(L)$ to find instead of
$\Theta(|\text{wordlist}| \cdot L)$.

```python
from collections import deque, defaultdict

def word_ladder(begin, end, wordlist):
    words = set(wordlist)
    if end not in words:
        return 0
    buckets = defaultdict(list)
    for w in words | {begin}:
        for i in range(len(w)):
            buckets[w[:i] + "*" + w[i+1:]].append(w)
    seen, q = {begin}, deque([(begin, 1)])
    while q:
        w, d = q.popleft()
        if w == end:
            return d
        for i in range(len(w)):
            for nb in buckets[w[:i] + "*" + w[i+1:]]:
                if nb not in seen:
                    seen.add(nb)
                    q.append((nb, d + 1))
    return 0
```
Bidirectional BFS roughly squares the reachable depth (Chapter 22).
:::

### P34. Network delay time

Time for a signal from one node to reach all others.

:::solution
Dijkstra; the answer is the maximum settled distance, or $-1$ if any node is
unreachable.

```python
import heapq
from collections import defaultdict

def network_delay(times, n, src):
    adj = defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
    dist = {}
    pq = [(0, src)]
    while pq:
        d, v = heapq.heappop(pq)
        if v in dist:
            continue                       # lazy deletion
        dist[v] = d
        for u, w in adj[v]:
            if u not in dist:
                heapq.heappush(pq, (d + w, u))
    return max(dist.values()) if len(dist) == n else -1
```
$\Theta((V+E)\log V)$.
:::

### P35. Cheapest flight with at most $k$ stops

:::solution
Not Dijkstra --- the constraint is on hop count, so the state is
(node, hops). Bellman--Ford limited to $k+1$ rounds is cleaner and correct.

```python
def cheapest_flight(n, flights, src, dst, k):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        nxt = dist[:]                      # copy: use only k-hop distances
        for u, v, w in flights:
            if dist[u] + w < nxt[v]:
                nxt[v] = dist[u] + w
        dist = nxt
    return -1 if dist[dst] == INF else dist[dst]
```
The copy is essential: without it, a path could use more than $k+1$ edges
within one round.
:::

### P36. Accounts merge

Merge accounts sharing any email address.

:::solution
Union--find over accounts, keyed by email (Chapter 15).

```python
def accounts_merge(accounts):
    parent = list(range(len(accounts)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]        # path halving
            x = parent[x]
        return x
    owner = {}
    for i, acc in enumerate(accounts):
        for email in acc[1:]:
            if email in owner:
                a, b = find(i), find(owner[email])
                parent[a] = b
            else:
                owner[email] = i
    groups = {}
    for email, i in owner.items():
        groups.setdefault(find(i), set()).add(email)
    return [[accounts[i][0]] + sorted(e) for i, e in groups.items()]
```
This is exactly the deduplication-clustering pattern of Chapter 29.
:::

### P37. Alien dictionary

Infer the letter order from a sorted list of words.

:::solution
Build the constraint graph from adjacent word pairs, then topologically
sort. The trap is the invalid case where a word is a strict prefix of its
predecessor.

```python
from collections import defaultdict, deque

def alien_order(words):
    adj = defaultdict(set)
    indeg = {c: 0 for w in words for c in w}
    for a, b in zip(words, words[1:]):
        if len(a) > len(b) and a.startswith(b):
            return ""                            # invalid input
        for x, y in zip(a, b):
            if x != y:
                if y not in adj[x]:
                    adj[x].add(y)
                    indeg[y] += 1
                break
    q = deque(c for c in indeg if indeg[c] == 0)
    out = []
    while q:
        c = q.popleft()
        out.append(c)
        for nxt in adj[c]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return "".join(out) if len(out) == len(indeg) else ""
```
:::

### P38. Critical connections (bridges)

Find every edge whose removal disconnects the graph.

:::solution
DFS with discovery times and low-link values. An edge $(u,v)$ is a bridge
when `low[v] > disc[u]` --- no back edge from $v$'s subtree reaches $u$ or
above.

```python
def critical_connections(n, connections):
    adj = [[] for _ in range(n)]
    for u, v in connections:
        adj[u].append(v)
        adj[v].append(u)
    disc, low, out = [-1] * n, [0] * n, []
    timer = [0]
    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v in adj[u]:
            if v == parent:
                continue
            if disc[v] == -1:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    out.append([u, v])
            else:
                low[u] = min(low[u], disc[v])
    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return out
```
$\Theta(V+E)$. Note `low[u] = min(low[u], disc[v])` --- not `low[v]` --- for
back edges; that is the classic bug.
:::

## Advanced dynamic programming

### P39. Edit distance with traceback $\dagger$

See Chapter 19 for the full derivation. The interview version wants the
$\Theta(nm)$ table; the production version wants the banded variant and
Myers' bit-parallel algorithm.

### P40. Regular expression matching

Support `.` and `*`.

:::solution
Two-sequence DP where `*` means "zero occurrences" or "one more occurrence".

```python
def is_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]            # x* matches empty
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                zero = dp[i][j - 2]
                more = dp[i - 1][j] and p[j - 2] in (s[i - 1], ".")
                dp[i][j] = zero or more
            else:
                dp[i][j] = (dp[i - 1][j - 1]
                            and p[j - 1] in (s[i - 1], "."))
    return dp[m][n]
```
$\Theta(nm)$ --- and note this is *why* an automaton-based matcher is
$\Theta(nm)$ worst case with no backtracking (Chapter 5).
:::

### P41. Burst balloons

Maximise `nums[i-1] * nums[i] * nums[i+1]` summed over a bursting order.

:::solution
Interval DP with the reversal that makes it work: think about which balloon
is burst **last** in an interval, because then its neighbours are the
interval's boundaries.

```python
def max_coins(nums):
    a = [1] + list(nums) + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for lo in range(0, n - length):
            hi = lo + length
            for k in range(lo + 1, hi):
                dp[lo][hi] = max(dp[lo][hi],
                                 dp[lo][k] + a[lo] * a[k] * a[hi] + dp[k][hi])
    return dp[0][n - 1]
```
$\Theta(n^3)$. Thinking "first" instead of "last" gives a recurrence with
non-local dependencies and does not work --- a good illustration that the
*choice of last decision* is the creative step in DP.
:::

### P42. Word break II

Return every sentence formed by splitting a string into dictionary words.

:::solution
Memoised recursion on the suffix, returning lists of completions. Bottom-up
tabulation is awkward here because the output is exponential --- the
top-down version only explores reachable states.

```python
from functools import lru_cache

def word_break(s, words):
    wordset = frozenset(words)
    @lru_cache(maxsize=None)
    def go(i):
        if i == len(s):
            return [""]
        out = []
        for j in range(i + 1, len(s) + 1):
            w = s[i:j]
            if w in wordset:
                for rest in go(j):
                    out.append(w if not rest else w + " " + rest)
        return out
    return go(0)
```
Add a feasibility pre-pass (a simple $\Theta(n^2)$ word-break DP) to avoid
exponential work on strings with no valid split at all.
:::

### P43. Best time to buy and sell stock with $k$ transactions

:::solution
Two-state DP over (day, transactions, holding).

```python
def max_profit(prices, k):
    if not prices or k == 0:
        return 0
    n = len(prices)
    if k >= n // 2:                              # unlimited: take every rise
        return sum(max(0, prices[i + 1] - prices[i]) for i in range(n - 1))
    buy = [float("-inf")] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)
            sell[t] = max(sell[t], buy[t] + p)
    return sell[k]
```
$\Theta(nk)$ time, $\Theta(k)$ space. The $k \ge n/2$ shortcut avoids a
pointless $\Theta(n^2)$ when $k$ is large.
:::

### P44. Longest palindromic substring

:::solution
Expand around each of the $2n-1$ centres: $\Theta(n^2)$ with $\Theta(1)$
space, and much faster in practice than the DP table. Manacher's algorithm
achieves $\Theta(n)$ by reusing previously computed radii --- the same
"remember what you matched" idea as KMP (Chapter 30).

```python
def longest_palindrome(s):
    if not s:
        return ""
    best = (0, 1)
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1
                hi += 1
            if hi - lo - 1 > best[1] - best[0]:
                best = (lo + 1, hi)
    return s[best[0]:best[1]]
```
:::

## Systems and ML-flavoured problems

### P45. Design a rate limiter

Allow $N$ requests per user per minute, with a memory budget of 100 bytes
per user and $10^7$ users.

:::solution
A sliding-window log is exact and costs $\Theta(N)$ timestamps per user ---
too much. Two better options:

**Token bucket.** Per user store `(tokens: float32, last_refill: uint32)`:
8 bytes. On a request, refill by `elapsed * rate`, cap at the burst size,
and spend one token if available. $\Theta(1)$ time, exact for the
rate, approximate for the exact window boundary.

**Sliding-window counter.** Store the counts for the current and previous
minute and interpolate: `estimate = prev * (1 - t) + cur`. 12 bytes,
$\Theta(1)$, and within a few percent of exact.

```python
import time

class TokenBucket:
    __slots__ = ("rate", "burst", "tokens", "last")
    def __init__(self, rate, burst):
        self.rate, self.burst = rate, burst
        self.tokens, self.last = float(burst), time.monotonic()

    def allow(self, n=1.0):
        now = time.monotonic()
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False
```
Across a fleet, either shard users by consistent hashing so each user has one
owner (Chapter 41), or accept per-replica limits at $1/R$ of the global rate.
:::

### P46. Deduplicate a 10-billion-document corpus on one machine

:::solution
Exact dedup with 16-byte digests needs 400 GB --- it does not fit. The
pipeline (Chapters 28, 29, 15):

1. **Exact duplicates**: a Bloom filter at 10 bits per document is 12.5 GB
   for a 1% false-positive rate, which discards 1% of unique documents ---
   acceptable. Or, better, sort 8-byte digests externally (Chapter 42):
   two passes, exact, 80 GB on disk.
2. **Near-duplicates**: MinHash with $K = 128$, banded into $b = 16$ bands of
   $r = 8$ (threshold $\approx 0.69$). Process one band at a time as an
   external sort by band hash, emitting candidate pairs from equal runs --- no
   in-memory index at all.
3. **Verify** candidates with the signature estimate; **cluster** with
   union--find over a 4-byte parent array (40 GB for $10^{10}$ documents ---
   so shard by connected component or process in blocks).
4. **Cap cluster size** to avoid transitive over-merging.

Cost: roughly 200 CPU-hours for signatures plus 16 external-sort passes.
State explicitly what the 1% false-positive rate costs you: 1% of unique
documents dropped, which is a fair trade for a 30x memory reduction.
:::

### P47. Serve top-$k$ retrieval over 500M vectors, 64 GB RAM, p99 < 20 ms

:::solution
Memory arithmetic first (Chapter 33). At $d = 1024$, float32 is 2 TB: out of
the question.

- **PQ with $m = 64$, 8 bits**: 64 bytes per vector = 32 GB. Fits, leaving
  32 GB.
- **IVF with nlist $= \sqrt{5 \times 10^8} \approx 22{,}000$** centroids:
  22K × 4 KB = 90 MB, negligible.
- **HNSW would need** $\approx 8 M n$ bytes = 128 GB at $M = 32$: does not
  fit alongside the codes. So IVF-PQ, not HNSW.
- **Query**: probe `nprobe = 32` cells, about $32 \times 22{,}700 =
  727{,}000$ candidates, each 64 table lookups and adds: about 46 million
  operations, a few milliseconds with SIMD.
- **Rerank**: fetch the top 200 full-precision vectors from an SSD-backed
  store (200 random reads, issued concurrently: about 1 ms at depth 32) and
  rescore exactly.
- **Budget**: 2 ms embed + 5 ms search + 1 ms rerank fetch + 1 ms rescore,
  leaving headroom for p99 jitter.
- **Validate**: measure recall@10 against brute force on 10,000 sampled
  queries; tune `nprobe` until recall meets target, then re-check latency.
:::

### P48. Bound KV-cache memory for a serving fleet

Given a model and a GPU, how many concurrent sequences can you serve?

:::solution
Chapter 36's formula. For $L = 80$, $H_{kv} = 8$, $d_h = 128$, fp16:
$4 \times 80 \times 8 \times 128 = 327{,}680$ bytes per token, so 1.34 GB at
4096 tokens.

On an 80 GB device holding a 40 GB shard of weights, 35 GB remains after
activations and workspace: **26 sequences** at full context. With 16-token
paging and a realistic length distribution (mean 800 tokens), the *average*
sequence needs 262 MB, so about 130 concurrent sequences --- which is the
argument for paging stated numerically. Add int8 KV quantisation for another
2x.
:::

### P49. Detect training--test contamination

:::solution
Two-stage (Chapter 30). Stage 1: hash every 13-gram of every test example
into a Bloom filter (a few GB), stream the training corpus past it, and
collect hits. Stage 2: for each hit, verify exactly against the test set and
measure the fraction of each test example covered by matches of at least 50
tokens.

Report: the fraction of test examples with any match, the distribution of
coverage, and --- crucially --- the metric computed on the *clean* subset
alongside the full-set number. Specify whether you matched tokens or
characters; the numbers are not comparable otherwise.
:::

### P50. Choose a sampler for a changing curriculum

Weights over 50 million examples, updated after every epoch, sampled 10
million times per epoch.

:::solution
Weights change once per epoch, not per draw. So the alias table's
$\Theta(n)$ rebuild is amortised over $10^7$ draws --- 50 million operations
per epoch to build, $10^7$ constant-time draws. That is the right choice.

If instead weights changed after *every draw* (prioritized replay), the
rebuild would cost $5 \times 10^{14}$ operations per epoch and you would need
a Fenwick tree: $\Theta(\log n) \approx 26$ operations per draw and per
update. Stating which regime you are in is the entire decision (Chapters 27,
34).
:::

### P51. Diagnose a training job at 40% GPU utilisation

:::solution
Chapter 42's procedure, in order: time the dataloader alone; if it is slower
than the step, it is the ceiling. Then time each stage. Then do the
arithmetic --- decoded bytes per second required versus what your CPU count
can produce.

The common findings, in rough order of frequency: too few dataloader
workers; JPEG decode on CPU (move to GPU with DALI/nvJPEG); small files on
network storage (re-shard); no `pin_memory` or no separate copy stream;
a synchronising call such as `.item()`, `.cpu()` or `torch.nonzero` inside
the step; and `torch.compile` graph breaks. "Buy a bigger GPU" is on none of
these lists.
:::

### P52. Design a feature store point-in-time join

Training rows are `(entity, label_time, label)`; features are
`(entity, feature_time, value)`. Join each label with the most recent
feature *strictly before* its label time, over $10^9$ rows.

:::solution
This is an as-of join, and doing it wrong leaks future information into
training --- one of the most damaging bugs in applied ML.

Sort both sides by `(entity, time)`, then one merge pass with two pointers
(Chapter 11): for each label, advance the feature pointer while
`feature_time < label_time` and take the last one passed. Both sorts are
external (Chapter 42), so the whole job is $\Theta(n \log_{M/B} n)$ ---
two passes each --- plus one linear merge.

The correctness details that matter: strict inequality (a feature computed
*at* the label time may already encode the label); a maximum staleness bound
so a year-old feature is treated as missing; and identical logic in the
serving path, which is what training--serving skew means in practice.
:::

### P53. Bound the memory of a streaming metrics service

Compute p50/p95/p99 latency per endpoint per minute, for 10,000 endpoints,
across 200 replicas.

:::solution
Per endpoint per minute, a t-digest with compression 100 is about 100
centroids of 16 bytes: 1.6 KB. For 10,000 endpoints that is 16 MB per
replica per minute --- trivially affordable.

The property that makes it work is mergeability (Chapter 38): each replica
keeps its own digests and the aggregator merges 200 of them, giving the exact
same answer as a global computation would, with no global sort and no data
movement beyond the digests. Storing raw latencies instead would be
$\Theta(\text{requests})$ and would require a global sort per minute.
:::

### P54. Pick a parallelism strategy

A 70B model, 64 GPUs with NVLink within 8-GPU nodes and 100 Gbit/s between
nodes.

:::solution
Chapter 41. Weights plus optimiser state at $16P$ bytes is 1.1 TB, so the
model cannot be data-parallel alone.

- **Tensor parallel within a node** (8-way): two all-reduces per layer, high
  volume, and NVLink at 400+ GB/s can carry it. Across nodes it could not.
- **Pipeline parallel across nodes** (say 4 stages): only boundary
  activations cross the slow link, which is small. Use enough micro-batches
  that the bubble fraction $(S-1)/(M+S-1)$ is under 10%: $S = 4$ needs
  $M \ge 28$.
- **Data parallel across the remaining 2 replicas**, with ZeRO/FSDP sharding
  the optimiser state to fit.

The principle: the highest-volume communication rides the fastest link.
State the bytes per step for each option and the decision makes itself.
:::

:::recap
- Graph problems are almost always one of: BFS, Dijkstra, topological sort,
  union--find, or DFS with low-link values.
- Advanced DP is about choosing the right *last decision*; burst balloons is
  the canonical example of a problem that only works backwards.
- Systems problems are answered with arithmetic first: bytes, operations,
  and the budget. The data structure follows from the numbers.
- State what an approximation costs you, in the units the user cares about.
- Point-in-time correctness, contamination checks and train--serve
  consistency are algorithmic problems with correctness consequences far
  larger than a latency regression.
:::
