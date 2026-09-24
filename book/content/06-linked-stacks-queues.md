# Linked Structures: Lists, Stacks, Queues, Ring Buffers
@short: Stacks and Queues
@subtitle: Four structures that differ only in which end you touch
@tier: foundation
@prereq: Chapter 4
@blurb: Stacks, queues, deques and ring buffers are the same idea with different access rules, and that rule is often the entire difference between two algorithms --- swapping a stack for a queue turns depth-first search into breadth-first search and nothing else changes. This chapter builds all of them, then uses them to build an LRU cache and a replay buffer.
@objectives:
- Implement singly and doubly linked lists and know exactly when they earn their overhead
- Use stacks and queues fluently, including the iterative rewrite of any recursion
- Build a deque and understand why `list.pop(0)` is the most common Python performance bug
- Implement a ring buffer with $\Theta(1)$ push and eviction and zero allocation
- Build an $O(1)$ LRU cache from a hash map plus a doubly linked list
- Recognise these structures inside dataloaders, replay buffers and serving queues

## The linked list, done once

A linked list stores each element in its own node together with a pointer to
the next node. Its virtue is that inserting or removing a node you already
hold a reference to costs $\Theta(1)$ with no shifting. Its vice is Chapter 3:
every traversal step is a dependent cache miss.

```python title="Singly linked list with O(1) push-front and O(1) append"
class Node:
    __slots__ = ("val", "next")           # __slots__ saves ~50% of the memory
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt

class LinkedList:
    def __init__(self):
        self.head = self.tail = None
        self.n = 0

    def push_front(self, v):              # theta(1)
        self.head = Node(v, self.head)
        if self.tail is None:
            self.tail = self.head
        self.n += 1

    def append(self, v):                  # theta(1) thanks to the tail pointer
        node = Node(v)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.n += 1

    def pop_front(self):                  # theta(1)
        if self.head is None:
            raise IndexError("empty")
        v, self.head = self.head.val, self.head.next
        if self.head is None:
            self.tail = None
        self.n -= 1
        return v

    def reverse(self):                    # theta(n), theta(1) extra space
        prev, cur = None, self.head
        self.tail = cur
        while cur:
            cur.next, prev, cur = prev, cur, cur.next
        self.head = prev

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.val
            cur = cur.next
```

The `reverse` method deserves attention because it is the archetype of a
whole family of pointer manipulations: three variables, one simultaneous
assignment, $\Theta(1)$ extra space. Cycle detection is the other archetype.

```python title="Floyd's cycle detection: constant space, linear time"
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False
```

Why it works: if there is a cycle, the fast pointer enters it and gains one
position per step on the slow pointer, so it must eventually coincide with
it --- within $\Theta(n)$ steps. The same two-speed idea finds the middle of a
list in one pass and detects cycles in a functional graph, which is how
Pollard's rho factorisation works.

:::pitfall When you actually want a linked list in Python
Almost never on its own. You want one *inside* another structure: the
recency list of an LRU cache, the free list of an allocator, the collision
chain of a hash table, the symbol list during BPE encoding. In each case the
list is not traversed from the head --- you always arrive at a node via a
hash map --- so the cache-miss penalty never materialises and the $\Theta(1)$
splice is the whole point.
:::

## Stacks and queues: the same array, different ends

@fig: stack_queue | 130 | A stack pushes and pops at one end; a queue pushes at one end and pops at the other. This is the only difference between depth-first and breadth-first search.

A stack is a Python list used with `append` and `pop`: both $\Theta(1)$
amortised, both cache-friendly, nothing more is needed. A queue is *not* a
Python list, because `pop(0)` shifts every remaining element.

| Structure | Push | Pop | Python |
|---|---|---|---|
| Stack (LIFO) | `append` $\Theta(1)$ | `pop()` $\Theta(1)$ | `list` |
| Queue (FIFO) | `append` $\Theta(1)$ | `popleft` $\Theta(1)$ | `collections.deque` |
| Queue, wrongly | `append` $\Theta(1)$ | `pop(0)` $\Theta(n)$ | `list` --- never |
| Deque | both ends $\Theta(1)$ | both ends $\Theta(1)$ | `collections.deque` |

@tbl: Stacks, queues and the one mistake to avoid. `deque` is a doubly linked list of fixed-size blocks, which gives $\Theta(1)$ at both ends while keeping most of the array's cache behaviour.

:::insight One line separates DFS from BFS
```
frontier.pop()       # stack  -> depth-first
frontier.popleft()   # queue  -> breadth-first
heapq.heappop()      # heap   -> best-first / Dijkstra / A*
```
The traversal skeleton is identical. Chapter 22 makes this explicit, and
Chapter 35 shows that beam search is the same skeleton with a bounded
priority queue.
:::

## Converting recursion to iteration

Every recursion is a loop plus an explicit stack --- the machine does exactly
this, and doing it manually is how you avoid `RecursionError` on deep
structures.

```python title="Recursive and iterative in-order traversal"
def inorder_rec(node, out):
    if node:
        inorder_rec(node.left, out)
        out.append(node.val)
        inorder_rec(node.right, out)

def inorder_iter(root):
    out, stack, node = [], [], root
    while stack or node:
        while node:                 # push the whole left spine
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right           # then go right and repeat
    return out
```

The iterative version uses the same $\Theta(h)$ memory as the recursive one,
but on the heap rather than the C stack, so it survives a million-node
degenerate tree. This matters in practice for deep JSON, deep expression
graphs, and linked lists of parsed records.

:::ml Where the stack is the algorithm
Reverse-mode automatic differentiation is a stack discipline: the forward
pass pushes the values needed by each operation's backward function, and the
backward pass pops them in reverse order. That stack is the *activation
memory* that dominates training memory, and gradient checkpointing is the
decision to push fewer things and recompute them instead --- a direct
space--time trade, analysed in Chapter 18 and applied in Chapter 24.
:::

## The ring buffer

When you need a bounded FIFO with no allocation --- the common case in
streaming systems --- use a fixed array and two indices modulo its length.

@fig: ring_buffer | 155 | A ring buffer. The array never grows, pushes never allocate, and when it is full the oldest element is silently overwritten.

```python title="Ring buffer with uniform sampling, as used for experience replay"
import numpy as np

class ReplayBuffer:
    def __init__(self, capacity, obs_dim):
        self.cap = capacity
        self.obs = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.act = np.zeros(capacity, dtype=np.int64)
        self.rew = np.zeros(capacity, dtype=np.float32)
        self.done = np.zeros(capacity, dtype=bool)
        self.pos = 0
        self.full = False

    def push(self, o, a, r, d):           # theta(1), never allocates
        i = self.pos
        self.obs[i], self.act[i], self.rew[i], self.done[i] = o, a, r, d
        self.pos = (i + 1) % self.cap
        self.full |= self.pos == 0

    def __len__(self):
        return self.cap if self.full else self.pos

    def sample(self, batch):              # theta(batch)
        idx = np.random.randint(0, len(self), size=batch)
        return self.obs[idx], self.act[idx], self.rew[idx], self.done[idx]
```

Note the layout: struct-of-arrays, not an array of transition objects
(Chapter 3). Sampling a batch is then four contiguous gathers rather than
`batch` pointer dereferences, and the whole buffer is four flat arrays that
can be memory-mapped or moved to a GPU as-is.

:::perf Preallocate, then never allocate again
The ring buffer's real virtue in a training loop is not its $\Theta(1)$
push --- it is that steady-state memory is exactly `capacity` and the
allocator is never touched. A growing list of transition objects fragments
the heap, triggers garbage collection pauses in the middle of training, and
makes memory usage a function of how long the job has been running. Bounded
structures make performance predictable, which is worth more than raw speed.
:::

## The LRU cache: hash map plus doubly linked list

An LRU cache must answer three questions in $\Theta(1)$: does key $k$ exist,
what is its value, and which key is least recently used? A hash map answers
the first two. A doubly linked list in recency order answers the third. The
trick is to store the list *node* as the map's value, so you can splice in
$\Theta(1)$ without traversing.

@fig: lru_cache | 108 | The classic $O(1)$ LRU. The hash map gives random access to a node; the doubly linked list gives ordering. Neither structure alone is enough.

```python title="O(1) LRU cache"
class _N:
    __slots__ = ("k", "v", "prev", "next")
    def __init__(self, k=None, v=None):
        self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, cap):
        self.cap = cap
        self.map = {}
        self.head, self.tail = _N(), _N()      # sentinels remove edge cases
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _push_front(self, n):
        n.next, n.prev = self.head.next, self.head
        self.head.next.prev = self.head.next = n

    def get(self, k, default=None):
        n = self.map.get(k)
        if n is None:
            return default
        self._unlink(n)
        self._push_front(n)                    # mark as most recent
        return n.v

    def put(self, k, v):
        n = self.map.get(k)
        if n is not None:
            n.v = v
            self._unlink(n)
            self._push_front(n)
            return
        if len(self.map) >= self.cap:
            lru = self.tail.prev                # evict from the back
            self._unlink(lru)
            del self.map[lru.k]
        n = _N(k, v)
        self.map[k] = n
        self._push_front(n)
```

The two sentinel nodes are not decoration: without them every operation
needs four special cases for empty, single-element, front and back. Sentinels
are a technique worth internalising --- they reappear in skip lists, in
segment trees, and in every balanced-tree implementation.

:::ml Caching in ML systems, and where LRU is the wrong policy
LRU is the default for embedding caches, feature-store reads and tokenizer
memoisation. It is the *wrong* default in three common situations. (1) A
full scan of a dataset larger than the cache evicts everything useful ---
this is sequential flooding, and the fix is a scan-resistant policy such as
2Q, ARC or `SLRU`. (2) When items have very different costs (recomputing a
1024-dimension embedding versus a scalar), use GDSF or a simple
cost-weighted priority queue. (3) When items have different sizes ---
variable-length KV-cache blocks --- use a size-aware policy, which is exactly
what vLLM's block manager implements (Chapter 36).
:::

## Monotonic stacks and queues

One more pattern, because it converts several quadratic algorithms into
linear ones: maintain a stack (or deque) whose contents are always sorted.

```python title="Sliding-window maximum in O(n) with a monotonic deque"
from collections import deque

def window_max(xs, k):
    dq = deque()                     # holds indices, values decreasing
    out = []
    for i, x in enumerate(xs):
        while dq and xs[dq[-1]] <= x:
            dq.pop()                 # x dominates everything smaller
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()             # drop indices that left the window
        if i >= k - 1:
            out.append(xs[dq[0]])
    return out
```

Every index is pushed once and popped once, so the total work is $\Theta(n)$
despite the inner `while`. The same idea --- discard elements that can never
be the answer again --- gives the "next greater element" problem, the largest
rectangle in a histogram, and online maximum drawdown. It is one of the
highest-yield patterns in Part IX's catalogue.

:::exercise
1. Implement `reverse_k_group`: reverse every consecutive group of $k$ nodes
   in a singly linked list, $\Theta(n)$ time, $\Theta(1)$ extra space.
2. Extend Floyd's algorithm to return the *first node of the cycle*, and
   prove the pointer arithmetic that makes it work.
3. Implement a queue using two stacks with $\Theta(1)$ amortised `dequeue`.
   Give the potential-function argument (Chapter 2).
4. Measure `list.pop(0)` against `deque.popleft()` for $n = 10^5$ and
   $n = 10^6$. Confirm the quadratic.
5. Add a `sample` method to `LRUCache` that returns the $k$ most recent keys
   in $\Theta(k)$.
6. Modify `ReplayBuffer` to store $n$-step returns, keeping $\Theta(1)$ push.
   What breaks when an episode boundary falls inside the $n$-step window?
7. Use a monotonic deque to compute, for each position of a 1M-element array,
   the maximum over the preceding 1000 elements. Compare to
   `np.lib.stride_tricks.sliding_window_view(...).max(axis=1)` in time and
   peak memory.
:::

:::recap
- A linked list buys $\Theta(1)$ splicing at a node you already hold, at the
  cost of pointer chasing; it is almost always a component inside another
  structure rather than a standalone container.
- Two pointer idioms are worth memorising: three-variable reversal, and
  Floyd's two-speed cycle detection.
- Stack versus queue is the only difference between DFS and BFS; swapping in
  a heap gives best-first search.
- Any recursion becomes a loop plus an explicit stack, which is how you avoid
  stack overflow on deep structures. Autograd is this pattern.
- Ring buffers give bounded memory, $\Theta(1)$ push and zero allocation ---
  the right structure for replay buffers and streaming windows.
- A hash map plus a doubly linked list gives $\Theta(1)$ LRU; sentinels
  remove all the edge cases. LRU is wrong under sequential flooding, uneven
  costs, or variable item sizes.
- A monotonic stack or deque turns several quadratic scan problems into
  linear ones by discarding elements that can never be the answer again.
:::
