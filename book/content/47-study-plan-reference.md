# Study Plan and Reference
@short: Plan and Reference
@subtitle: Sixteen weeks, and the tables worth keeping open
@tier: reference
@prereq: none
@blurb: The last chapter is a plan and a reference. The plan is what this book is optimised for --- sixteen weeks at four to six hours, half of them at a keyboard. The reference is the set of tables you will come back to long after you have read the prose: complexities, memory formulas, Python costs, and the cost model of a machine learning system.
@objectives:
- Follow a week-by-week plan through the whole book
- Use the complexity tables as a working reference
- Estimate the memory and time cost of an ML system from its parameters
- Find the chapter that covers whatever you are currently fighting

## The plan

@fig: study_plan | 118 | Sixteen weeks. The proportions reflect how much practice each part needs, not how many pages it has.

| Weeks | Chapters | Deliverable each week |
|---|---|---|
| 1 | 1--2 | Measure your machine's ops/sec; complexity-annotate a file of your own code |
| 2 | 3--4 | Reproduce the cache-cliff experiment; convert a loop to NumPy and measure |
| 3 | 5--6 | Write a tokenizer trie; implement a ring buffer and an LRU from memory |
| 4 | 7--8 | Implement a hash map with resizing; convert three recursions to iteration |
| 5 | 9--10 | Implement merge, quick, radix sort; write `lower_bound` from memory |
| 6 | 11 + P1--P10 | Ten foundation problems, timed |
| 7 | 12--13 | Implement a BST and a binary heap; solve top-$k$ four ways and benchmark |
| 8 | 14--15 | Build a trie tokenizer and a union--find dedup clusterer |
| 9 | 16--17 | Apply the master theorem to ten recurrences; prove two greedy algorithms |
| 10 | 18 | Five dynamic programs, each written top-down then bottom-up |
| 11 | 19--21 | Implement edit distance, Viterbi and reservoir sampling |
| 12 | 22--24 | Build a CSR graph; implement BFS, Dijkstra, topological sort, a tiny autograd |
| 13 | 25--26 | Implement a matching loss with `linear_sum_assignment`; implement PageRank |
| 14 | 27--31 | Build a Fenwick tree, a Bloom filter and a MinHash deduplicator |
| 15 | 32--36 | Build an IVF-PQ index; implement beam search and a block-paged KV manager |
| 16 | 37--42 + P31--P54 | Histogram split finder; parallel scan; profile a real dataloader |

@tbl: A week-by-week plan at four to six hours per week. The deliverable column is the point: reading without implementing produces recognition, not recall.

:::practice Three rules that make the plan work
**Implement from memory.** Read the chapter, close it, and write the
structure. Getting stuck is the signal that you understood it less than you
thought --- and it is the moment the learning happens.

**Keep a bug log.** One line per bug: what it was, what the symptom was, and
what would have caught it. After a month it becomes a personal checklist, and
it is worth more than any generic list --- including the ones in this book.

**Measure something every week.** A number you measured yourself is worth ten
you read. The habit of reaching for a benchmark before an opinion is the most
transferable thing this book teaches.
:::

## Complexity of data structures

| Structure | Access | Search | Insert | Delete | Ordered? | Space | Chapter |
|---|---|---|---|---|---|---|---|
| Array | $\Theta(1)$ | $\Theta(n)$ | $\Theta(n)$ | $\Theta(n)$ | no | $n$ | 4 |
| Dynamic array | $\Theta(1)$ | $\Theta(n)$ | $\Theta(1)^*$ | $\Theta(n)$ | no | $n$ | 4 |
| Sorted array | $\Theta(1)$ | $\Theta(\log n)$ | $\Theta(n)$ | $\Theta(n)$ | yes | $n$ | 10 |
| Linked list | $\Theta(n)$ | $\Theta(n)$ | $\Theta(1)^\ddagger$ | $\Theta(1)^\ddagger$ | no | $2n$ | 6 |
| Deque | $\Theta(n)$ | $\Theta(n)$ | $\Theta(1)$ ends | $\Theta(1)$ ends | no | $n$ | 6 |
| Hash table | --- | $\Theta(1)^*$ | $\Theta(1)^*$ | $\Theta(1)^*$ | no | $\approx 1.4n$ | 7 |
| Binary heap | $\Theta(1)$ min | $\Theta(n)$ | $\Theta(\log n)$ | $\Theta(\log n)$ | partial | $n$ | 13 |
| Balanced BST | --- | $\Theta(\log n)$ | $\Theta(\log n)$ | $\Theta(\log n)$ | yes | $n$ | 12 |
| Skip list | --- | $\Theta(\log n)^*$ | $\Theta(\log n)^*$ | $\Theta(\log n)^*$ | yes | $\approx 2n$ | 31 |
| B+ tree | --- | $\Theta(\log_B n)$ | $\Theta(\log_B n)$ | $\Theta(\log_B n)$ | yes | $\approx 1.5n$ | 12, 31 |
| Trie | --- | $\Theta(m)$ | $\Theta(m)$ | $\Theta(m)$ | yes | shared prefixes | 14 |
| Union--find | --- | $\Theta(\alpha(n))$ | $\Theta(\alpha(n))$ | --- | no | $n$ | 15 |
| Fenwick tree | --- | $\Theta(\log n)$ | $\Theta(\log n)$ | --- | prefix | $n$ | 27 |
| Segment tree | --- | $\Theta(\log n)$ | $\Theta(\log n)$ | --- | range | $2n$--$4n$ | 27 |
| Bloom filter | --- | $\Theta(k)$ | $\Theta(k)$ | no | no | $1.44n\log_2\frac{1}{p}$ bits | 28 |
| LSM tree | --- | $\Theta(L)$ levels | $\Theta(1)$ | $\Theta(1)$ | yes | $\approx 1.1n$ | 31 |
| HNSW | --- | $\Theta(\log n)$ approx | $\Theta(\log n)$ | tombstone | no | $\approx 8Mn$ bytes | 33 |

@tbl: $^*$ expected or amortised. $^\ddagger$ given a reference to the node.

## Complexity of algorithms

| Algorithm | Best | Average | Worst | Space | Chapter |
|---|---|---|---|---|---|
| Binary search | $\Theta(1)$ | $\Theta(\log n)$ | $\Theta(\log n)$ | $\Theta(1)$ | 10 |
| Insertion sort | $\Theta(n)$ | $\Theta(n^2)$ | $\Theta(n^2)$ | $\Theta(1)$ | 9 |
| Merge sort | $\Theta(n\log n)$ | $\Theta(n\log n)$ | $\Theta(n\log n)$ | $\Theta(n)$ | 9 |
| Quicksort | $\Theta(n\log n)$ | $\Theta(n\log n)$ | $\Theta(n^2)$ | $\Theta(\log n)$ | 9 |
| Heapsort | $\Theta(n\log n)$ | $\Theta(n\log n)$ | $\Theta(n\log n)$ | $\Theta(1)$ | 13 |
| Timsort | $\Theta(n)$ | $\Theta(n\log n)$ | $\Theta(n\log n)$ | $\Theta(n)$ | 9 |
| Radix sort | $\Theta(dn)$ | $\Theta(dn)$ | $\Theta(dn)$ | $\Theta(n+b)$ | 9 |
| Quickselect | $\Theta(n)$ | $\Theta(n)$ | $\Theta(n^2)$ | $\Theta(1)$ | 9 |
| BFS / DFS | --- | $\Theta(V+E)$ | $\Theta(V+E)$ | $\Theta(V)$ | 22 |
| Dijkstra (heap) | --- | $\Theta((V+E)\log V)$ | same | $\Theta(V)$ | 23 |
| Bellman--Ford | $\Theta(E)$ | $\Theta(VE)$ | $\Theta(VE)$ | $\Theta(V)$ | 23 |
| Floyd--Warshall | $\Theta(V^3)$ | $\Theta(V^3)$ | $\Theta(V^3)$ | $\Theta(V^2)$ | 23 |
| Kruskal | --- | $\Theta(E\log E)$ | same | $\Theta(V)$ | 23 |
| Topological sort | --- | $\Theta(V+E)$ | same | $\Theta(V)$ | 24 |
| Dinic max-flow | --- | $\Theta(V^2E)$ | same | $\Theta(V+E)$ | 25 |
| Hungarian | --- | $\Theta(n^3)$ | same | $\Theta(n^2)$ | 25 |
| Edit distance | --- | $\Theta(nm)$ | same | $\Theta(\min(n,m))$ | 19 |
| Viterbi | --- | $\Theta(TS^2)$ | same | $\Theta(TS)$ | 19 |
| CTC forward | --- | $\Theta(TS)$ | same | $\Theta(TS)$ | 19 |
| KMP | --- | $\Theta(n+m)$ | same | $\Theta(m)$ | 30 |
| Aho--Corasick | --- | $\Theta(n+\sum m_i+z)$ | same | $\Theta(\sum m_i)$ | 14 |
| Suffix array (SA-IS) | --- | $\Theta(n)$ | same | $\Theta(n)$ | 30 |
| FFT | --- | $\Theta(n\log n)$ | same | $\Theta(n)$ | 16 |
| Matrix multiply | --- | $\Theta(n^3)$ | same | $\Theta(n^2)$ | 16 |
| Strassen | --- | $\Theta(n^{2.807})$ | same | $\Theta(n^2)$ | 16 |
| PageRank | --- | $\Theta(E)$ / iteration | same | $\Theta(V)$ | 26 |

@tbl: Reference complexities. "Same" means the average and worst coincide.

## Python cost reference

| Operation | Cost | Note |
|---|---|---|
| `x in list` | $\Theta(n)$ | the most common accidental quadratic |
| `x in set` / `dict` | $\Theta(1)^*$ | use this |
| `list.append` | $\Theta(1)^*$ | amortised |
| `list.insert(0, x)` / `pop(0)` | $\Theta(n)$ | use `deque` |
| `deque.appendleft` / `popleft` | $\Theta(1)$ | |
| `list.sort()` | $\Theta(n\log n)$ | Timsort, stable, adaptive |
| `heapq.heappush` / `heappop` | $\Theta(\log n)$ | min-heap only |
| `heapq.nlargest(k, xs)` | $\Theta(n\log k)$ | in C |
| `s += t` in a loop | $\Theta(n^2)$ | use `"".join` |
| `a[i:j]` (list or str) | $\Theta(j-i)$ | allocates |
| `bisect.*` | $\Theta(\log n)$ | on a sorted list |
| `np.argsort` | $\Theta(n\log n)$ | pass `kind="stable"` for ties |
| `np.argpartition` | $\Theta(n)$ | top-$k$ without full ordering |
| `np.searchsorted` | $\Theta(m\log n)$ | batched binary search |
| `dict` memory, int keys | $\approx 100$ B/entry | switch to arrays past $10^7$ |
| `np` array memory | `dtype` bytes/entry | 8 for int64, 4 for float32 |
| Python statement | $\approx 30$--100 ns | $\approx 10^7$/s |
| NumPy float add | $\approx 0.3$ ns | $\approx 3\times10^9$/s |

@tbl: The Python numbers worth memorising. The last two lines explain most performance surprises in ML code.

## Hardware cost reference

| Event | Latency | Relative |
|---|---|---|
| L1 cache hit | 1 ns | 1 |
| Branch mispredict | 5 ns | 5 |
| L2 cache hit | 4 ns | 4 |
| L3 cache hit | 15 ns | 15 |
| Main memory | 90 ns | 90 |
| NVMe random read | 80 µs | 80,000 |
| Same-datacentre round trip | 500 µs | 500,000 |
| Disk seek (HDD) | 5 ms | 5,000,000 |
| Cross-continent round trip | 150 ms | 150,000,000 |

@tbl: Latency numbers, normalised to an L1 hit. The two orders of magnitude between memory and NVMe, and the three between NVMe and a network hop, are the boundaries that structure every system.

## ML system cost formulas

:::math The formulas worth keeping
**Model memory** (mixed-precision training, Adam), $P$ parameters:
$$M \approx 16P \text{ bytes} = 2P\,(\text{bf16 weights}) + 2P\,(\text{grads}) + 12P\,(\text{fp32 master} + m + v)$$

**KV cache**, $L$ layers, $H_{kv}$ key/value heads, head dim $d_h$, batch
$B$, length $S$, fp16:
$$\text{bytes} = 4 \cdot B \cdot S \cdot L \cdot H_{kv} \cdot d_h$$

**Training FLOPs** (Kaplan/Chinchilla approximation), $N$ tokens:
$$C \approx 6PN \quad (\text{2}PN \text{ forward} + 4PN \text{ backward})$$

**Inference FLOPs per token**: $\approx 2P$, plus attention
$\approx 4 L S d$.

**Arithmetic intensity**: $I = \text{FLOPs} / \text{bytes moved}$;
memory-bound if $I < \text{peak FLOP/s} / \text{bandwidth}$ (about 100--500).

**Ring all-reduce bytes per worker**: $2(P-1)/P \cdot N$, independent of $P$.

**Pipeline bubble fraction**: $(S-1)/(M+S-1)$ for $S$ stages, $M$
micro-batches.

**Bloom filter**: $m = 1.44 n \log_2(1/p)$ bits, $k = (m/n)\ln 2$.

**HyperLogLog**: standard error $1.04/\sqrt{m}$ registers.

**MinHash**: standard error $\le 1/(2\sqrt{K})$; LSH threshold
$\approx (1/b)^{1/r}$.

**Johnson--Lindenstrauss**: $m = O(\varepsilon^{-2}\log n)$ dimensions
preserve all pairwise distances.
:::

## The pitfalls index

| Symptom | Likely cause | Chapter |
|---|---|---|
| Fine in dev, unusable in prod | invisible quadratic (`in list`, `+=` on strings) | 2, 7 |
| Same complexity, 10x slower | access pattern, not operation count | 3 |
| Out of memory in a distance computation | materialised broadcast | 4 |
| Dataloader results change with `num_workers` | view aliasing, or per-worker seeds | 4, 21 |
| Nondeterministic rankings | unstable sort, no tiebreaker | 9 |
| `RecursionError` on real data | unbalanced tree or deep list | 8, 12 |
| Dict of 100M keys killed by OOM | Python object overhead | 7 |
| Sharding reshuffles on restart | using `hash()` on strings | 7 |
| Sliding window gives wrong answers | negative values break monotonicity | 11 |
| Vector search recall silently poor | unnormalised vectors, or too few probes | 32, 33 |
| Deleting from an ANN index degrades it | tombstones, needs rebuild | 33 |
| Negative variance in a dashboard | naive $E[x^2]-E[x]^2$ | 38 |
| Training hangs at an all-reduce | unequal shards per rank | 42 |
| GPU at 40% utilisation | input pipeline, not the model | 42 |
| Loss differs between runs with a fixed seed | float reduction order | 39 |
| Benchmark scores suspiciously high | test-set contamination | 30 |
| Model memorises verbatim | training-data duplication | 29 |

@tbl: Symptom to cause. This is the table to read when something is wrong and you do not yet know what.

## Where to go next

- **For rigour**: Cormen, Leiserson, Rivest and Stein, *Introduction to
  Algorithms*, for proofs this book states; Kleinberg and Tardos,
  *Algorithm Design*, for the best treatment of exchange arguments and
  network flow.
- **For competitive practice**: the Competitive Programmer's Handbook, and
  daily problems. The patterns of Chapter 44 map onto them directly.
- **For systems**: Kleppmann, *Designing Data-Intensive Applications*, which
  is the operational counterpart to Part VI.
- **For the ML-native material**: the primary papers. FAISS, HNSW, DiskANN,
  ScaNN for retrieval; vLLM and SGLang for serving; FlashAttention and its
  successors for kernels; LightGBM and XGBoost for trees. They are readable,
  and by now you have the vocabulary.
- **For the habit**: pick one system you use --- a vector database, a
  dataloader, a tokenizer --- and read its source until you can name every
  data structure in it. That exercise, done three or four times, is worth
  more than any further reading.

:::recap
- Sixteen weeks, four to six hours a week, half of them at a keyboard.
  Implement from memory, keep a bug log, and measure something every week.
- The complexity tables are for reference; the ML formulas are for estimating
  before building.
- The latency table's boundaries --- memory to NVMe to network --- are what
  structure every system in this book.
- The pitfalls index maps symptoms to causes; most production problems in ML
  systems are on it.
- The most durable exercise is to read the source of a system you already
  use and name every structure in it.
:::
