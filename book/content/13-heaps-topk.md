# Heaps, Priority Queues and Top-k
@short: Heaps and Top-k
@subtitle: When you need the best element, not all of them in order
@tier: core
@prereq: Chapters 9, 12
@blurb: The heap answers exactly one question --- what is the smallest element? --- and answers it in constant time while supporting logarithmic insertion and removal. That narrow contract is enough to build top-k retrieval, beam search, Dijkstra's algorithm, event simulation, BPE training and the scheduler in your inference server. It is the highest leverage-per-line data structure in the book.
@objectives:
- Explain why a complete binary tree can be stored in a flat array with no pointers
- Implement sift-up, sift-down, push, pop and the $\Theta(n)$ heapify
- Use `heapq` correctly, including max-heaps, tuples and lazy deletion
- Solve top-k over a stream with $\Theta(k)$ memory
- Implement $k$-way merge, running median and a priority queue with `decrease-key`
- Recognise heaps inside beam search, BPE training and GPU schedulers

## A tree with no pointers

:::definition Binary heap
A **complete** binary tree (every level full except possibly the last, which
is filled left to right) satisfying the **heap property**: every node's key
is $\le$ both of its children's keys (a min-heap). The root is therefore the
global minimum. Note what is *not* required: siblings are unordered, and an
in-order traversal is meaningless.
:::

@fig: heap_array | 195 | Because the tree is complete, it maps onto an array with no gaps, and parent/child relationships become index arithmetic. No pointers, no allocation, perfect cache locality.

The index arithmetic is the whole trick:

$$\text{parent}(i) = \left\lfloor \frac{i-1}{2} \right\rfloor, \quad
\text{left}(i) = 2i+1, \quad \text{right}(i) = 2i+2$$

```python title="A binary min-heap from scratch"
class MinHeap:
    def __init__(self, items=None):
        self.a = list(items or [])
        for i in range(len(self.a) // 2 - 1, -1, -1):
            self._sift_down(i)               # heapify: theta(n), see below

    def push(self, x):
        self.a.append(x)
        self._sift_up(len(self.a) - 1)       # theta(log n)

    def pop(self):
        top = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last                 # move the last leaf to the root
            self._sift_down(0)               # then restore the property
        return top                           # theta(log n)

    def peek(self):
        return self.a[0]                     # theta(1)

    def _sift_up(self, i):
        while i > 0:
            p = (i - 1) >> 1
            if self.a[i] >= self.a[p]:
                break
            self.a[i], self.a[p] = self.a[p], self.a[i]
            i = p

    def _sift_down(self, i):
        n = len(self.a)
        while True:
            smallest, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and self.a[l] < self.a[smallest]:
                smallest = l
            if r < n and self.a[r] < self.a[smallest]:
                smallest = r
            if smallest == i:
                return
            self.a[i], self.a[smallest] = self.a[smallest], self.a[i]
            i = smallest
```

:::math Why heapify is $\Theta(n)$ and not $\Theta(n \log n)$
Building a heap by $n$ pushes costs $\Theta(n \log n)$. Building it by
sifting down from the last internal node costs only $\Theta(n)$, and the
reason is that most nodes are near the *bottom*, where sifting is cheap.
At height $h$ there are at most $\lceil n / 2^{h+1} \rceil$ nodes, each
costing $O(h)$:

$$\sum_{h=0}^{\lfloor \log n \rfloor} \frac{n}{2^{h+1}} \cdot O(h)
= O\!\left(n \sum_{h=0}^{\infty} \frac{h}{2^{h+1}}\right) = O(n)$$

because $\sum_{h \ge 0} h/2^h = 2$. Half the nodes are leaves and cost
nothing; only the single root costs $\log n$.
:::

| Operation | Cost | Note |
|---|---|---|
| `peek` | $\Theta(1)$ | the root |
| `push` | $\Theta(\log n)$ | sift up |
| `pop` | $\Theta(\log n)$ | sift down |
| `heapify(list)` | $\Theta(n)$ | bottom-up |
| `pushpop` / `replace` | $\Theta(\log n)$, one sift | half the cost of push then pop |
| search for arbitrary key | $\Theta(n)$ | heaps are not searchable |
| `decrease-key` | $\Theta(\log n)$ *with* an index map | otherwise $\Theta(n)$ to find it |
| merge two heaps | $\Theta(n)$ | $\Theta(\log n)$ for pairing/leftist heaps |

@tbl: Heap costs. The two rows that surprise people: a heap cannot be searched, and `decrease-key` needs an auxiliary map from element to array position.

## Using `heapq` without fighting it

Python's `heapq` operates on a plain list. It is a min-heap only, which
leads to four idioms worth knowing.

```python title="The four heapq idioms"
import heapq

# 1. Max-heap: negate the key.
h = []
for x in data:
    heapq.heappush(h, -x)
largest = -heapq.heappop(h)

# 2. Priority with a payload: push tuples, and add a tiebreaker so that
#    Python never has to compare the payloads (which may be uncomparable).
import itertools
counter = itertools.count()
heapq.heappush(h, (priority, next(counter), payload))

# 3. Bounded top-k: keep a MIN-heap of size k of the LARGEST items.
def top_k(stream, k):
    h = []
    for x in stream:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)      # one sift instead of two
    return sorted(h, reverse=True)

# 4. Lazy deletion: you cannot remove an arbitrary element, so mark it
#    dead in a side table and skip it when it surfaces.
def pop_alive(h, dead):
    while h:
        item = heapq.heappop(h)
        if item not in dead:
            return item
        dead.remove(item)
    return None
```

Idiom 3 is the one that matters most. It is counter-intuitive --- to find
the $k$ *largest* you keep a heap of *smallest* --- and the reason is that
the root then holds the weakest survivor, so deciding whether a new item
belongs is a single $\Theta(1)$ comparison.

@fig: topk_stream | 155 | Top-$k$ over a stream with a bounded min-heap. Items below the root are discarded in constant time; only items that make the cut pay $\Theta(\log k)$.

:::perf Which top-k should you actually use?
| Situation | Use | Cost |
|---|---|---|
| Stream, cannot hold $n$ | bounded min-heap | $\Theta(n \log k)$ time, $\Theta(k)$ space |
| Python list in memory | `heapq.nlargest(k, xs)` | same, but in C |
| NumPy array, $k \ll n$ | `np.argpartition` | $\Theta(n)$, 10--40x faster |
| Torch tensor on GPU | `torch.topk` | radix-select, $\Theta(n)$ |
| Need all $k$ *and* their order | partition then sort $k$ | $\Theta(n + k \log k)$ |
| $k$ close to $n$ | just sort | $\Theta(n \log n)$ |
:::

## $k$-way merge

Merging $k$ sorted streams is the canonical heap application, and it is how
external sorting, log aggregation and multi-shard retrieval all work.

```python title="Merge k sorted streams with a heap of size k"
import heapq

def merge_k(streams):
    """streams: list of sorted iterables. Yields one merged sorted stream."""
    h = []
    iters = [iter(s) for s in streams]
    for i, it in enumerate(iters):
        for first in it:
            heapq.heappush(h, (first, i))
            break
    while h:
        val, i = heapq.heappop(h)
        yield val
        for nxt in iters[i]:
            heapq.heappush(h, (nxt, i))
            break
```

Total cost: $\Theta(N \log k)$ for $N$ elements across $k$ streams, and the
memory is $\Theta(k)$ regardless of $N$. That memory bound is why this is the
merge step of external sort, and why a retrieval service can merge the
results of 64 index shards without materialising them.

:::ml Heaps in the ML stack, specifically
**Top-$k$ retrieval.** Every vector index --- flat, IVF, HNSW --- maintains a
bounded max-heap of candidates and a min-heap of results. HNSW's search is
literally two heaps (Chapter 33).

**Beam search.** Keep the $b$ best partial sequences; at each step expand
all of them and take the best $b$ of $b \times V$ continuations, which is a
bounded heap (or, faster, a `topk` over the flattened logits). Chapter 35.

**BPE training.** Repeatedly merge the most frequent adjacent pair. That is
a max-heap of pair counts with lazy deletion, because a merge changes the
counts of neighbouring pairs and you cannot efficiently find them in the
heap. Chapter 14.

**Schedulers.** An inference server's continuous batching loop picks which
requests to run next by priority --- deadline, sequence length, or fair
share --- which is a priority queue. So is the GPU work queue underneath it.

**Sparse attention and MoE routing.** Top-$k$ over scores, per token, is a
heap or a radix-select depending on hardware.
:::

## Two useful variants

**Running median with two heaps.** Keep a max-heap of the lower half and a
min-heap of the upper half, with sizes differing by at most one. The median
is the root of the larger heap, or the mean of the two roots.

```python title="Streaming median in O(log n) per element"
import heapq

class RunningMedian:
    def __init__(self):
        self.lo = []      # max-heap via negation: the smaller half
        self.hi = []      # min-heap: the larger half

    def push(self, x):
        heapq.heappush(self.lo, -heapq.heappushpop(self.hi, x))
        if len(self.lo) > len(self.hi):                 # rebalance
            heapq.heappush(self.hi, -heapq.heappop(self.lo))

    def median(self):
        if len(self.hi) > len(self.lo):
            return self.hi[0]
        return (self.hi[0] - self.lo[0]) / 2.0
```

**Indexed priority queue with `decrease-key`.** Dijkstra's algorithm
(Chapter 23) wants to lower a vertex's tentative distance. A plain heap
cannot find that vertex. Two solutions: keep a `pos` dict from element to
array index and update it on every swap; or --- far simpler and what almost
everyone does in practice --- push a new entry and ignore stale ones on pop.
The lazy version uses $\Theta(E)$ memory instead of $\Theta(V)$ and is faster
in practice because the bookkeeping is free.

:::note Fibonacci heaps, and why nobody uses them
Fibonacci heaps achieve $\Theta(1)$ amortised `decrease-key`, improving
Dijkstra from $\Theta(E \log V)$ to $\Theta(E + V \log V)$. They are a
beautiful piece of amortised analysis (the potential method of Chapter 2 at
its best) and essentially never used: the constant factors are large, the
structure is a forest of pointer-linked trees with terrible locality, and
pairing heaps get most of the benefit with a tenth of the code. A good
reminder that an asymptotic improvement is a claim about large $n$, not about
your $n$.
:::

:::exercise
1. Prove that a complete binary tree of $n$ nodes has height
   $\lfloor \log_2 n \rfloor$, and that the last internal node is at index
   $n/2 - 1$.
2. Implement `heapify` both ways (repeated push, and bottom-up sift-down) and
   measure the ratio at $n = 10^6$. Confirm the $\Theta(n)$ versus
   $\Theta(n \log n)$ prediction.
3. Implement a max-heap without negating keys, by parameterising the
   comparison. Then explain why `heapq` does not offer this.
4. Find the top 100 of $10^7$ float32 scores four ways: `sorted`,
   `heapq.nlargest`, a hand-written bounded heap, and `np.argpartition`.
   Report times and peak memory.
5. Implement an indexed priority queue with `decrease-key` in
   $\Theta(\log n)$, and compare it to the lazy-deletion approach inside
   Dijkstra on a graph with $10^6$ edges.
6. Implement $k$-way merge of 1000 sorted files totalling more than memory.
   How does the running time vary with the merge fan-in $k$, and where is the
   optimum?
7. Extend `RunningMedian` to an arbitrary quantile $q$, keeping the two-heap
   invariant. What changes, and why is this harder than the median?
8. A serving queue must run requests by (deadline, then arrival). Implement
   it with `heapq`, supporting cancellation of an arbitrary request.
:::

:::recap
- A binary heap is a complete tree stored as a flat array; parent and child
  are index arithmetic, so there are no pointers and locality is perfect.
- `peek` is $\Theta(1)$; `push` and `pop` are $\Theta(\log n)$; bottom-up
  `heapify` is $\Theta(n)$ because most nodes are leaves.
- A heap cannot be searched, and `decrease-key` requires an auxiliary index
  map --- or lazy deletion, which is usually better in practice.
- Top-$k$ over a stream uses a *min*-heap of size $k$: the root is the
  weakest survivor, so rejection is $\Theta(1)$.
- $k$-way merge costs $\Theta(N \log k)$ with $\Theta(k)$ memory, which is
  what makes external sorting and multi-shard retrieval possible.
- Two heaps give a streaming median; the same trick gives any fixed quantile
  with more care.
- Heaps appear in retrieval, beam search, BPE training, schedulers and MoE
  routing. In NumPy or Torch, prefer `argpartition` / `topk`.
:::
