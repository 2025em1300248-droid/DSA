# KV Caches as Data Structures
@short: KV Caches
@subtitle: Paging, prefix trees and eviction inside an inference server
@tier: expert
@prereq: Chapters 6, 14, 31
@blurb: The key--value cache is the single largest consumer of memory in LLM serving, and managing it is a pure data-structures problem --- one whose best-known solution is a direct port of operating-system virtual memory. This chapter works through the memory arithmetic, the paging scheme, the prefix tree that makes shared prompts free, and the scheduling that ties them together.
@objectives:
- Compute KV cache size exactly and see why it dominates serving memory
- Explain the fragmentation problem in contiguous allocation
- Understand paged attention as virtual memory for the cache
- Implement a radix tree over token prefixes for cache sharing
- Understand continuous batching and its scheduling decisions
- Reason about eviction, recomputation and offloading

## The memory arithmetic

For a transformer with $L$ layers, $H$ key/value heads, head dimension $d_h$,
batch $B$, sequence length $S$, in 2-byte precision:

$$\text{KV bytes} = 2 \times 2 \times B \times S \times L \times H \times d_h$$

(the outer 2 for keys and values, the inner 2 for bytes per element).

:::math Worked example
A 70-billion-parameter model with $L = 80$, 64 attention heads of $d_h = 128$
and 8 key/value heads (grouped-query attention):

$$2 \times 2 \times 1 \times 4096 \times 80 \times 8 \times 128 = 1.34\ \text{GB per sequence}$$

At batch 32 that is 43 GB --- on an 80 GB device that already holds 140 GB of
weights in fp16, which is why the model must be sharded before you even
begin. Without grouped-query attention ($H = 64$) it would be 10.7 GB per
sequence: 8x more. GQA exists almost entirely for this reason.
:::

| Knob | Effect on KV cache |
|---|---|
| Grouped-query attention ($H_{kv} < H_q$) | linear reduction, 4--8x typical |
| Multi-query attention ($H_{kv} = 1$) | maximal reduction, some quality cost |
| KV quantisation to int8 / fp8 | 2x |
| Sliding-window attention (window $w$) | caps $S$ at $w$ |
| Cross-layer sharing | linear in the number of shared layers |
| Longer context | linear --- and this is the growth direction |

@tbl: Every serving optimisation you have heard of is a row in this table. The cache grows linearly in context length, so a 1M-token context is not a small change.

## Fragmentation, and why contiguity is the enemy

The naive implementation allocates a contiguous buffer per request, sized to
`max_tokens`. That produces three kinds of waste:

- **Internal fragmentation.** A request that generates 100 tokens out of a
  2048 reservation wastes 95% of its allocation.
- **External fragmentation.** Freed blocks of varying sizes leave holes too
  small for the next request.
- **Reservation waste.** Space reserved for tokens not yet generated cannot
  be used by anyone else.

Measured in the vLLM paper, contiguous allocation wasted 60--80% of KV
memory. Since KV memory bounds the batch size, and batch size determines
throughput, that waste is a direct multiple on serving cost.

## Paged attention

@fig: paged_attention | 160 | Paged attention. Each request's logical token sequence is mapped through a block table to fixed-size physical blocks that need not be contiguous --- precisely the page-table mechanism of an operating system.

```python title="A block-based KV cache manager"
class BlockManager:
    """Fixed-size blocks of `block_size` tokens; a block table per request."""

    def __init__(self, num_blocks, block_size=16):
        self.block_size = block_size
        self.free = list(range(num_blocks))       # free list
        self.tables = {}                          # req_id -> [block ids]
        self.refcount = {}                        # block id -> users

    def allocate(self, req_id, num_tokens):
        need = (num_tokens + self.block_size - 1) // self.block_size
        if len(self.free) < need:
            return False                          # trigger preemption
        blocks = [self.free.pop() for _ in range(need)]
        for b in blocks:
            self.refcount[b] = 1
        self.tables[req_id] = blocks
        return True

    def append_token(self, req_id):
        """Grow by one token; allocate a block only when the last one fills."""
        table = self.tables[req_id]
        used = self.used_tokens.get(req_id, 0)
        if used % self.block_size == 0:
            if not self.free:
                return False
            b = self.free.pop()
            self.refcount[b] = 1
            table.append(b)
        self.used_tokens[req_id] = used + 1
        return True

    def fork(self, parent_id, child_id):
        """Copy-on-write: a beam or a parallel sample shares the prefix."""
        blocks = self.tables[parent_id]
        for b in blocks:
            self.refcount[b] += 1
        self.tables[child_id] = list(blocks)

    def free_request(self, req_id):
        for b in self.tables.pop(req_id, []):
            self.refcount[b] -= 1
            if self.refcount[b] == 0:
                self.free.append(b)
```

The design: fixed-size blocks (16 tokens is standard) eliminate external
fragmentation entirely; internal fragmentation is bounded by half a block per
request; and a reference count per block gives copy-on-write sharing for
free. The attention kernel is modified to gather keys and values through the
block table rather than assuming contiguity --- which costs a little
indirection and buys a 2--4x larger batch.

:::insight The same idea, three times
Fixed-size blocks with an indirection table is *the* answer to fragmentation,
and you have now seen it in three places: the ragged values-plus-offsets
layout of Chapter 4, the page table of an operating system, and the block
table here. Whenever a system must store many variable-length things in a
fixed pool, this is the structure.
:::

## Prefix sharing with a radix tree

In a chat service, every request shares a long system prompt, and successive
turns of one conversation share the whole history. Recomputing that KV cache
is pure waste --- prefill is compute-bound and linear in prefix length.

A radix tree (Chapter 14) over token sequences, with KV blocks attached to
its nodes, makes the sharing automatic.

```python title="A radix tree over token prefixes"
class RadixNode:
    __slots__ = ("children", "tokens", "blocks", "refs", "last_used")
    def __init__(self, tokens=(), blocks=()):
        self.children = {}           # first token -> RadixNode
        self.tokens = tuple(tokens)  # the edge label
        self.blocks = list(blocks)   # KV blocks for these tokens
        self.refs = 0
        self.last_used = 0.0

class PrefixCache:
    def __init__(self):
        self.root = RadixNode()

    def match(self, tokens):
        """Longest cached prefix: returns (matched_len, blocks, node)."""
        node, i, blocks = self.root, 0, []
        while i < len(tokens):
            child = node.children.get(tokens[i])
            if child is None:
                break
            k = 0
            while (k < len(child.tokens) and i + k < len(tokens)
                   and child.tokens[k] == tokens[i + k]):
                k += 1
            blocks.extend(child.blocks[:k])
            i += k
            if k < len(child.tokens):
                break                       # partial edge match: stop here
            node = child
        return i, blocks, node

    def insert(self, tokens, blocks, node=None, start=0):
        node = node or self.root
        if start >= len(tokens):
            return node
        child = RadixNode(tokens[start:], blocks[start:])
        node.children[tokens[start]] = child
        return child
```

**Eviction.** LRU over *leaves only*: an internal node's blocks are in use by
every descendant, so evicting it would corrupt them. Maintain a reference
count and an LRU list of evictable leaves --- which is the LRU cache of
Chapter 6 with a tree-shaped validity constraint.

:::ml What prefix caching is worth
On real chat traffic, cache hit rates of 50--90% are typical, because system
prompts are shared and multi-turn conversations re-send their history. Since
prefill cost is linear in the uncached prefix length, a 90% hit rate turns a
4000-token prefill into a 400-token one --- roughly a 10x reduction in
time-to-first-token for that request, and a large increase in the number of
concurrent conversations a server can hold.

This is why API providers offer discounted "cached input" pricing: the
mechanism is exactly the structure above, and the discount reflects a real
cost saving.
:::

## Continuous batching

Static batching --- collect $B$ requests, run them together to completion ---
wastes enormous capacity because requests finish at different lengths and the
whole batch waits for the longest.

Continuous batching (also called in-flight batching) runs the scheduler
*per decoding step*:

1. Finished sequences leave the batch immediately and free their blocks.
2. Waiting requests are admitted if there are enough free blocks for their
   prompt.
3. When memory runs short, a request is **preempted** --- either swapped out
   to host memory, or dropped and recomputed later (recompute is usually
   cheaper, since prefill is fast and PCIe is slow).
4. Prefill and decode are interleaved, or separated onto different devices
   (disaggregated serving), because they have opposite bottlenecks: prefill
   is compute-bound, decode is bandwidth-bound.

```python title="The scheduler's core decision"
def schedule(running, waiting, block_mgr, max_batch):
    """One step of continuous batching."""
    running = [r for r in running if not r.finished]
    for r in list(running):
        if not block_mgr.append_token(r.id):          # out of memory
            victim = max(running, key=lambda x: x.remaining_estimate)
            block_mgr.free_request(victim.id)
            victim.preempted = True                   # recompute later
            running.remove(victim)
            waiting.insert(0, victim)
    while waiting and len(running) < max_batch:
        r = waiting[0]
        matched, blocks, _ = prefix_cache.match(r.tokens)
        if block_mgr.allocate(r.id, len(r.tokens) - matched):
            r.cached_prefix = matched
            running.append(waiting.pop(0))
        else:
            break                                     # no room; wait
    return running, waiting
```

The scheduling policy is a real choice with real tradeoffs: first-come
first-served is fair and has poor tail latency; shortest-remaining-first
maximises throughput and starves long requests; a priority queue by deadline
(Chapter 13) gives predictable service levels. It is the same scheduling
problem as any queueing system, and the same answers apply.

:::pitfall Eviction and recomputation are not equivalent
Swapping a KV cache to host memory over PCIe at 25 GB/s takes about 54 ms
for a 1.34 GB sequence. Recomputing the prefill for 4096 tokens on a modern
accelerator takes perhaps 200 ms but uses no PCIe bandwidth and no host
memory. Which is better depends on how loaded the interconnect is and
whether the request will resume soon. Most servers default to recomputation
for short prefixes and swapping for long ones --- and the threshold is worth
measuring on your own hardware rather than accepting the default.
:::

:::exercise
1. Compute the KV cache size for Llama-3-8B ($L=32$, $H_q=32$, $H_{kv}=8$,
   $d_h=128$) at context lengths 4K, 32K and 128K in fp16 and in int8.
2. Simulate contiguous allocation with request lengths drawn from a
   log-normal distribution and measure the fragmentation waste. Then simulate
   16-token paging and measure it again.
3. Implement `BlockManager` including copy-on-write `fork`, and use it for
   beam search with width 4 sharing a common prefix. Measure the memory saved.
4. Implement `PrefixCache` and measure the hit rate on a synthetic chat
   workload with a shared 2000-token system prompt and 5-turn conversations.
5. Implement leaf-only LRU eviction over the radix tree and show that naive
   LRU can evict an internal node still in use.
6. Simulate static versus continuous batching with a mix of short and long
   requests. Report throughput and p99 latency for both.
7. Compare preemption policies: swap-to-host versus recompute, as a function
   of prefix length. Find the crossover for a given PCIe bandwidth and
   prefill throughput.
8. Design a scheduler that guarantees a p99 time-to-first-token under 500 ms
   while maximising throughput. State the data structures.
:::

:::recap
- KV cache size is $4 \cdot B \cdot S \cdot L \cdot H_{kv} \cdot d_h$ bytes
  in fp16, and it dominates serving memory; grouped-query attention, KV
  quantisation and sliding windows are all attacks on this formula.
- Contiguous per-request allocation wastes 60--80% of KV memory to internal,
  external and reservation fragmentation.
- Paged attention stores the cache in fixed-size blocks with a per-request
  block table --- OS virtual memory --- eliminating external fragmentation
  and enabling copy-on-write sharing.
- A radix tree over token prefixes makes shared system prompts and multi-turn
  histories free to reuse; eviction must be LRU over leaves only.
- Continuous batching schedules per decoding step, admitting and preempting
  requests as blocks free up; prefill and decode have opposite bottlenecks.
- Preemption by recomputation and by swapping have different costs; the
  crossover depends on prefix length and interconnect load.
:::
