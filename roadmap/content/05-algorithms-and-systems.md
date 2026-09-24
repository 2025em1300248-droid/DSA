# Algorithms and Systems
@short: Algorithms and Systems
@subtitle: Why the interview tests it, and why the job needs it more
@tier: foundation
@prereq: Chapter 3
@blurb: Data structures and algorithms are tested in interviews for reasons that are only partly about interviews. The same material determines whether your deduplication job finishes, whether your retrieval index fits in memory, and whether your dataloader starves the GPU. This chapter states the requirement precisely and points at the companion volume that covers it.
@objectives:
- Know exactly which algorithmic material is expected, and to what depth
- Reason about the memory hierarchy well enough to explain a 10x performance gap
- Understand operating-system and networking fundamentals at the level production requires
- Apply the specific structures that recur in ML systems

## What this is for

Two distinct reasons, and it is worth separating them.

**The interview reason.** Most ML and AI engineering loops include a coding
round at roughly the level of arrays, hashing, two pointers, trees, heaps,
graphs and dynamic programming. This is not going away, and it is the most
mechanically preparable part of any loop.

**The job reason, which is larger.** The algorithmic content of a modern ML
system is substantial and mostly invisible until it breaks: deduplicating a
corpus is locality-sensitive hashing; a tokenizer is a trie and a priority
queue; prioritized replay is a Fenwick tree; vector search is quantisation
and a navigable graph; a KV cache manager is a paging system; distributed
gradient reduction is a ring algorithm with a provable bandwidth bound.

## The capabilities

:::checklist ESSENTIAL --- algorithms
- Complexity analysis, including amortised, and the discipline of stating
  time *and* space
- Arrays, hashing, sets, and the reflex that `x in list` is linear
- Sorting, binary search --- including binary search over an answer space,
  which is the form that actually appears at work
- Two pointers and sliding windows
- Trees: traversal, binary search trees, balance
- Heaps and top-$k$, including top-$k$ over a stream with bounded memory
- Graphs: representations, BFS, DFS, topological sort, shortest paths
- Dynamic programming: recognise it, formulate the state, write it both
  top-down and bottom-up
- Recursion, and converting it to iteration when depth is a risk
:::

:::checklist CORE --- systems
- The memory hierarchy: cache lines, why sequential access is an order of
  magnitude faster than random, why a linked list underperforms its
  asymptotics
- Arithmetic intensity: FLOPs per byte moved, and the roofline test for
  whether an optimisation can possibly help
- Processes, threads, the GIL, and which concurrency model fits which problem
- Virtual memory, page cache, memory mapping --- which is how large datasets
  are actually read
- Networking enough to reason about latency budgets: round trips, TLS
  handshakes, HTTP/2 multiplexing, gRPC, why a chatty client is slow
- File formats and their access patterns: Parquet, Arrow, and why columnar
  beats row-oriented for analytics
:::

:::checklist CORE --- the ML-specific structures
| Structure | Where it appears |
|---|---|
| Hash set / Bloom filter | exact and approximate deduplication, contamination checks |
| MinHash + LSH | near-duplicate detection in a training corpus |
| Trie, Aho--Corasick | tokenizers, PII scrubbing, constrained decoding |
| Heap | top-$k$ retrieval, beam search, BPE training, schedulers |
| Fenwick / segment tree | prioritized replay, dynamic weighted sampling |
| Ring buffer | replay buffers, sliding-window KV caches, streaming windows |
| Union--find | turning pairwise near-duplicates into clusters |
| Radix / prefix tree | KV-cache prefix sharing in LLM serving |
| Product quantisation, HNSW | vector indexes |
| Count--Min, HyperLogLog | stream statistics at corpus scale |
:::

:::checklist AWARENESS
- Database internals: B+ trees, LSM trees, query planning
- Distributed systems theory: consistency models, consensus, partitioning
- Compiler basics, enough to understand what `torch.compile` does
:::

## Depth required, by role

| Role | Interview depth | Job depth |
|---|---|---|
| AI engineer | medium --- expect a coding round | medium: retrieval, caching, cost |
| ML engineer | medium | medium: data processing at scale |
| ML platform | high | high: this *is* the job |
| Research engineer | medium--high | high: kernels, memory, parallelism |
| Data scientist | low--medium | low |

@tbl: How deep to go. Nobody gets away with "low" on the interview side except in a few data-science loops.

:::insight The companion volume
This map's sibling --- *Data Structures & Algorithms for AI/ML Engineers* ---
covers exactly this material in 47 chapters, from complexity and the memory
hierarchy through to paged attention, ring all-reduce and FlashAttention as
an IO-aware algorithm. Every structure in the table above has a chapter. If
you are working through this map, that volume is the Part II reading.
:::

## How to tell you have it

:::practice The tasks
1. Solve 50--75 problems across the standard patterns, timed, without
   looking at solutions first. Track which patterns you fail.
2. Explain, without notes, why summing a 4096×4096 matrix along axis 0 and
   along axis 1 differ by 5--10x in wall-clock time.
3. Given 100 million documents and 32 GB of RAM, design a deduplication
   pipeline. State the structures, the memory arithmetic, and what your
   approximation costs you in dropped unique documents.
4. Profile a training loop that is at 40% GPU utilisation and find the
   bottleneck. (It will be the input pipeline. Prove it.)
:::

:::pitfall Grinding problems without patterns
Solving 300 problems by memorising 300 solutions produces nothing durable.
Solving 60 while explicitly naming the pattern each one belongs to, and
reimplementing the pattern from memory a day later, produces recall that
survives. The catalogue of patterns matters more than the count of problems.
:::

:::note Time to competence
Interview-ready from a software background: **5--6 weeks** at 12 hours.
Job-ready systems intuition: continuous, but the memory-hierarchy chapter
alone is a weekend and changes how you read every profile afterwards.
:::

:::recap
- Algorithms are tested because loops test them, and needed because ML
  systems are built out of them.
- ESSENTIAL: complexity, hashing, sorting and binary search (including over
  an answer space), windows, trees, heaps, graphs, dynamic programming.
- CORE systems: the memory hierarchy, arithmetic intensity, concurrency
  models, memory mapping, latency budgets, columnar formats.
- Ten specific structures recur throughout ML systems; learn them by the
  system that uses them.
- Practise by pattern, not by problem count.
:::
