# On-Disk Structures: B-Trees, LSM Trees and Feature Stores
@short: On-Disk Structures
@subtitle: When the data structure is larger than memory
@tier: advanced
@prereq: Chapters 12, 28
@blurb: Every structure so far assumed the data fits in RAM. When it does not, the cost model changes: a random read costs 100 microseconds instead of 100 nanoseconds, and the block is the unit of everything. This chapter covers the two storage engines the world runs on, the amplification tradeoffs that distinguish them, and how they show up in feature stores and vector databases.
@objectives:
- Reason with the external-memory cost model and the block size $B$
- Explain why B+ trees dominate read-heavy on-disk indexing
- Understand LSM trees, compaction, and the read/write/space amplification triangle
- Choose between B-tree and LSM storage for a given workload
- Understand skip lists and why memtables use them
- Map these structures onto feature stores, vector databases and checkpoint storage

## The external-memory model

:::definition The external-memory (I/O) model
Memory holds $M$ items; disk is unbounded; data moves in blocks of $B$
items. The cost of an algorithm is the number of block transfers. This is
the right model whenever the data exceeds memory --- and, with $B$
reinterpreted as a cache line, it is also the right model for cache
behaviour (Chapter 3).
:::

The model immediately changes what is optimal:

| Operation | RAM model | External-memory model |
|---|---|---|
| Scan $n$ items | $\Theta(n)$ | $\Theta(n/B)$ |
| Sort $n$ items | $\Theta(n \log n)$ | $\Theta\!\left(\frac{n}{B}\log_{M/B}\frac{n}{B}\right)$ |
| Search in a sorted structure | $\Theta(\log_2 n)$ | $\Theta(\log_B n)$ |
| Binary search on disk | $\Theta(\log_2 n)$ I/Os | terrible: each probe is a block |
| B-tree search | --- | $\Theta(\log_B n)$ I/Os |

@tbl: The same problems, re-costed. Note the sorting bound: with $M = 10^{10}$ bytes and $B = 10^6$, $\log_{M/B}$ is about 1, so external sorting is essentially two passes over the data.

:::insight $\log_B$ versus $\log_2$ is the whole story
$\log_2(10^9) = 30$. $\log_{200}(10^9) = 3.9$. At 80 microseconds per random
read, that is 2.4 ms versus 0.3 ms. Every on-disk structure in this chapter
exists to make the base of that logarithm as large as possible, by matching
the node size to the block size.
:::

## B+ trees

A B+ tree (Chapter 12) stores keys in internal nodes and *all* values in the
leaves, with the leaves linked into a list.

| Property | Consequence |
|---|---|
| Node = one page (4--16 KB) | branching factor 200--800 |
| Height 3--4 at $10^9$ keys | 3--4 random reads per point lookup |
| All values in linked leaves | range scans are sequential |
| Updates in place | one random write per update |
| Node fill 50--70% | 30--50% space overhead |

@tbl: The B+ tree's profile. Its strength is predictable, low read amplification; its weakness is that every update is a random write.

:::perf Why the top levels are free
A B+ tree's root and second level are tiny --- for a 4 KB page size and
$10^9$ keys, the top two levels are a few megabytes --- so they stay
permanently in the buffer pool. The effective cost of a lookup is therefore
one or two disk reads, not four. This is why "the index fits in memory, the
data does not" is such a common and comfortable operating point.
:::

## LSM trees

An LSM (log-structured merge) tree accepts a very different tradeoff: never
update in place, only append.

@fig: lsm_vs_btree | 172 | The two write paths. A B-tree does one random write per update. An LSM tree buffers in memory, flushes sequentially, and merges in the background --- so all writes are sequential, at the cost of reads that may touch several levels.

**Write path.** New records go into an in-memory *memtable*. When it fills,
it is written out as an immutable sorted file (an SSTable) --- one sequential
write. Background **compaction** merges SSTables, discarding superseded
versions.

**Read path.** Check the memtable, then each level in order, newest first.
Every SSTable has a Bloom filter (Chapter 28) so most levels can be skipped
without any I/O, and a sparse index so the right block can be found with one
read.

```python title="A minimal LSM structure, to fix the idea"
import bisect

class MiniLSM:
    def __init__(self, memtable_limit=1000):
        self.memtable = {}                       # a skip list in reality
        self.levels = []                         # each: sorted list of (k, v)
        self.limit = memtable_limit

    def put(self, key, value):
        self.memtable[key] = value               # theta(1), no disk I/O
        if len(self.memtable) >= self.limit:
            self._flush()

    def delete(self, key):
        self.memtable[key] = TOMBSTONE           # deletion is also a write

    def _flush(self):
        run = sorted(self.memtable.items())      # one sequential write
        self.levels.insert(0, run)
        self.memtable = {}
        self._maybe_compact()

    def get(self, key):
        if key in self.memtable:                 # newest first
            v = self.memtable[key]
            return None if v is TOMBSTONE else v
        for run in self.levels:
            i = bisect.bisect_left(run, (key,))
            if i < len(run) and run[i][0] == key:
                v = run[i][1]
                return None if v is TOMBSTONE else v
        return None

    def _maybe_compact(self):
        while len(self.levels) > 4:              # merge the two oldest
            a, b = self.levels.pop(), self.levels.pop()
            merged, i, j = [], 0, 0
            while i < len(a) or j < len(b):      # k-way merge, Chapter 13
                if j >= len(b) or (i < len(a) and a[i][0] <= b[j][0]):
                    if not merged or merged[-1][0] != a[i][0]:
                        merged.append(a[i])
                    i += 1
                else:
                    if not merged or merged[-1][0] != b[j][0]:
                        merged.append(b[j])
                    j += 1
            self.levels.append(merged)

TOMBSTONE = object()
```

Two details that matter in real systems: **deletion is a write** (a
tombstone that must survive until every older copy has been compacted away),
and **compaction is where the CPU and I/O budget actually goes** --- a
write-heavy LSM store can spend more I/O on compaction than on the original
writes.

## The amplification triangle

:::definition The three amplifications
**Write amplification**: bytes written to disk per byte of user data. A
B-tree writes a whole page per update; a levelled LSM rewrites each record
once per level, so $\approx L \times$ the fan-out ratio.

**Read amplification**: blocks read per lookup. B-tree: the tree height.
LSM: potentially one per level, reduced to near 1 by Bloom filters.

**Space amplification**: bytes stored per byte of live data. B-tree: 1.4--2x
from partial page fill. Levelled LSM: about 1.1x. Tiered LSM: 2--10x, because
superseded versions linger.
:::

You cannot minimise all three. Levelled compaction (RocksDB default,
LevelDB) minimises space and read amplification at the cost of write
amplification; tiered compaction (Cassandra, ScyllaDB) minimises write
amplification at the cost of the other two.

| Workload | Choose | Why |
|---|---|---|
| Read-heavy, range scans | B+ tree | low read amplification, sequential leaves |
| Write-heavy, point lookups | LSM (levelled) | sequential writes, Bloom-filtered reads |
| Append-only time series | LSM (tiered) | writes dominate; old data rarely read |
| Small dataset, in memory | neither | use a hash map |
| Immutable after build | sorted file + sparse index | no update machinery needed at all |

@tbl: Storage engine selection. The last row is underused: many ML artefacts --- a built vector index, a feature snapshot, a tokenizer --- are written once and read many times, and need none of this complexity.

## Skip lists, and why memtables use them

A memtable must be sorted (so it can be flushed as an SSTable), support
concurrent writes, and be fast. A balanced tree needs rebalancing with locks;
a skip list does not.

:::definition Skip list
A sorted linked list with additional "express lane" levels. An element is
promoted to level $i+1$ with probability $p$ (usually 1/2 or 1/4), so the
expected height is $\Theta(\log n)$ and search, insert and delete are all
$\Theta(\log n)$ expected.
:::

```python title="Skip list search: the shape that makes it worth knowing"
def search(head, key):
    node = head
    for level in range(len(head.forward) - 1, -1, -1):   # top lane down
        while node.forward[level] and node.forward[level].key < key:
            node = node.forward[level]                   # skip ahead
    node = node.forward[0]
    return node if node and node.key == key else None
```

Skip lists are the memtable in RocksDB and LevelDB, the sorted set in Redis,
and a common choice in lock-free concurrent structures --- because an insert
touches $\Theta(\log n)$ pointers and each can be published with a single
atomic compare-and-swap, with no rotation and no global restructuring. They
are the practical answer to "I need a balanced tree but I do not want to
write one".

:::ml Where these structures appear in an ML system
**Feature stores.** The offline store is columnar files (Parquet) for
training-time scans; the online store is a key-value store --- usually LSM
(RocksDB, Cassandra, DynamoDB) --- for point lookups at serving time. The
hard part is not the storage engine but *point-in-time correctness*: joining
features as they were at the label's timestamp, which is a range query on a
$(\text{entity}, \text{timestamp})$ key and therefore wants sorted storage.

**Vector databases.** The vectors live in a flat memory-mapped file or an
HNSW graph (Chapter 33); the *metadata and filters* live in a B-tree or LSM
store; and the mapping from external id to internal offset is a hash index.
A "vector database" is a vector index plus a conventional storage engine.

**Checkpoints and datasets.** Model checkpoints and shard files are
write-once, read-many blobs: no index structure needed, just object storage
and an offset table. WebDataset's tar shards plus an index file are exactly
the "sorted file + sparse index" row of the table above.

**Embedding tables larger than memory.** Billion-scale embedding tables in
recommendation systems are stored in an LSM key-value store with an in-memory
cache of hot ids --- which is why cache policy (Chapter 6) matters so much to
their throughput.
:::

:::pitfall Random reads dominate; measure IOPS, not bandwidth
An NVMe drive advertising 7 GB/s delivers that on sequential reads. Random
4 KB reads give perhaps 1 million IOPS, which is 4 GB/s only if fully
queued --- and a single-threaded synchronous read loop will see 10--20
thousand IOPS, two orders of magnitude worse. If your structure does random
reads, you must issue them concurrently (io_uring, async I/O, or many
threads). This is the dominant consideration for disk-resident vector
indexes such as DiskANN (Chapter 33), whose entire design is about
minimising the *number* of random reads per query.
:::

:::exercise
1. Compute the height of a B+ tree over $10^{10}$ keys with 8-byte keys and
   16 KB pages. How many of its levels fit in 1 GB of buffer pool?
2. Implement external merge sort for a file of $10^8$ integers with a 100 MB
   memory budget. Count the passes and verify the
   $\log_{M/B}$ prediction.
3. Implement `MiniLSM` with Bloom filters per run and measure the reduction
   in blocks touched per lookup.
4. Compute the write amplification of a levelled LSM with 4 levels and a
   fan-out of 10. Compare with tiered compaction.
5. Implement a skip list with insert, delete and search. Measure the height
   distribution and confirm $\Theta(\log n)$ expected.
6. Benchmark random 4 KB reads on your machine, single-threaded synchronous
   versus 32-deep asynchronous. Report the IOPS ratio.
7. Design the storage layer for an online feature store serving 100,000
   lookups per second over 500 GB of features with a 20 ms p99 budget. State
   the engine, the cache, and the expected hit rate you would need.
:::

:::recap
- In the external-memory model cost is block transfers; $\log_B n$ replaces
  $\log_2 n$, which is why node size should match page size.
- B+ trees give 3--4 reads per lookup, sequential range scans, and one random
  write per update; their top levels stay cached.
- LSM trees make all writes sequential by buffering in a memtable and
  flushing immutable sorted runs, at the cost of reads that may touch several
  levels --- mitigated by a Bloom filter per SSTable.
- Write, read and space amplification form a triangle; levelled compaction
  favours space and reads, tiered favours writes.
- Skip lists give $\Theta(\log n)$ expected operations with no rebalancing,
  which makes them the standard concurrent memtable.
- Feature stores, vector databases and embedding tables are all built on
  these engines; write-once artefacts need none of them.
- Random-read throughput is limited by IOPS and queue depth, not bandwidth.
:::
