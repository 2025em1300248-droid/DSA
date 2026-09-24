# Probabilistic Structures: Bloom, Count--Min, HyperLogLog
@short: Sketches
@subtitle: Trading a known, tunable error for orders of magnitude of memory
@tier: advanced
@prereq: Chapters 7, 21
@blurb: When exact answers need more memory than you have, the question changes from "what is the answer?" to "how much error will I accept, and how little memory can I get away with?" Sketches answer that question with a tunable knob and a proof. They are the reason a single machine can deduplicate a trillion documents or count distinct users across a billion events.
@objectives:
- Implement a Bloom filter and derive its optimal parameters
- Choose between Bloom, counting Bloom, cuckoo and quotient filters
- Implement a Count--Min sketch and state its error guarantee
- Implement HyperLogLog and explain why it needs only 12 KB
- Understand mergeability and why it matters for distributed aggregation
- Apply sketches to deduplication, heavy hitters and cardinality in real pipelines

## Why sketches exist

An exact set of $n$ 16-byte hashes needs $16n$ bytes plus hash-table
overhead: about 40 GB for a billion items. A Bloom filter that answers
membership with a 1% false-positive rate needs **10 bits per item** --- 1.2
GB --- regardless of how large the items are. That is a factor of 30, and it
is the difference between a cluster and a laptop.

:::insight The three questions sketches answer
**Membership**: have I seen $x$? (Bloom, cuckoo, quotient filters.)
**Frequency**: how many times have I seen $x$? (Count--Min, Count-Sketch.)
**Cardinality**: how many *distinct* items have I seen? (HyperLogLog.)

Each gives up exactness in a specific, bounded direction, and each is
*mergeable*: sketches computed on different shards combine into the sketch of
the union. That property is what makes them work in a distributed pipeline.
:::

## Bloom filters

@fig: bloom_filter | 155 | A Bloom filter. Insertion sets $k$ bits; a query that finds any zero bit proves absence. False positives are possible; false negatives are not.

```python title="A Bloom filter with double hashing"
import math
from bitarray import bitarray     # or use an int and bit operations

class BloomFilter:
    def __init__(self, n, fp_rate=0.01):
        self.m = max(8, int(math.ceil(-n * math.log(fp_rate) / math.log(2) ** 2)))
        self.k = max(1, int(round(self.m / n * math.log(2))))
        self.bits = bitarray(self.m)
        self.bits.setall(False)
        self.count = 0

    def _indices(self, item):
        h = hash(item)                       # use blake2b/xxhash if persisted
        h1, h2 = h & 0xFFFFFFFF, (h >> 32) | 1
        for i in range(self.k):              # Kirsch-Mitzenmacher: two hashes
            yield (h1 + i * h2) % self.m     # simulate k independent ones

    def add(self, item):
        for i in self._indices(item):
            self.bits[i] = True
        self.count += 1

    def __contains__(self, item):
        return all(self.bits[i] for i in self._indices(item))
```

:::math Deriving the optimal $k$ and $m$
After inserting $n$ items with $k$ hashes into $m$ bits, the probability a
given bit is still zero is $(1 - 1/m)^{kn} \approx e^{-kn/m}$. A false
positive requires all $k$ bits to be set:
$$p \approx \left(1 - e^{-kn/m}\right)^k$$
Differentiating with respect to $k$ gives the optimum
$k^* = \frac{m}{n}\ln 2 \approx 0.693\,\frac{m}{n}$, at which
$p = 2^{-k^*}$, equivalently
$$m = -\frac{n \ln p}{(\ln 2)^2} \approx 1.44\, n \log_2(1/p)$$
So **9.6 bits per item for 1%, 14.4 for 0.1%, 19.2 for 0.01%** --- each
additional decimal place of accuracy costs 4.8 bits per item. And note what
is *absent* from the formula: the size of the items.
:::

The Kirsch--Mitzenmacher trick in `_indices` is worth knowing: $k$ independent
hash functions can be simulated by $h_1 + i \cdot h_2$ for $i = 0 \ldots k-1$
with no measurable loss in the false-positive rate. One hash computation
instead of $k$.

| Filter | Bits/item at 1% | Deletes | Lookup | Notes |
|---|---|---|---|---|
| Bloom | 9.6 | no | $k$ random probes | the baseline |
| Counting Bloom | 38 | yes | $k$ probes | 4-bit counters instead of bits |
| Cuckoo | 9.0 | yes | 2 probes | better locality, can fail to insert |
| Quotient | 10--12 | yes | 1 probe | cache-friendly, resizable, mergeable |
| Blocked Bloom | 10.5 | no | 1 cache line | all $k$ bits in one 64-byte block |

@tbl: The filter family. Blocked Bloom trades a slightly worse rate for a single cache miss per query --- usually the right trade in a hot path (Chapter 3).

:::ml Bloom filters in the ML stack
**Corpus deduplication.** Stream documents, hash, query the filter, insert.
A 1% false-positive rate discards 1% of *unique* documents, which for a
web-scale corpus is entirely acceptable and saves 30x the memory.

**Training--test contamination checks.** Put every test-set $n$-gram in a
filter and stream the training corpus past it; any hit is investigated
exactly. The filter is a cheap pre-filter for an expensive exact check.

**LSM-tree reads.** Every SSTable carries a Bloom filter so a lookup can skip
files that certainly do not contain the key. This is the single most
important optimisation in an LSM store (Chapter 31).

**Negative caching.** "This embedding is definitely not in the cache" avoids
a network round trip. False positives merely cost a wasted lookup.
:::

:::pitfall Bloom filters have one-sided error --- know which side
A Bloom filter never says "absent" about something present. It sometimes says
"present" about something absent. So it is safe for *skipping work* and
unsafe for *asserting existence*. Using one to decide "this user already
consented" is a correctness bug; using one to decide "this SSTable might
contain the key, go and check" is correct by construction. Always ask which
direction an error would take you.
:::

## Count--Min sketch

Bloom answers yes/no. Count--Min answers "how many", using $d$ rows of $w$
counters and $d$ independent hash functions.

@fig: count_min | 128 | A Count--Min sketch. Each item increments one counter per row; the estimate is the minimum across rows, because collisions can only ever inflate a counter.

```python title="Count-Min sketch"
import numpy as np

class CountMin:
    def __init__(self, epsilon=0.001, delta=1e-4, seed=0):
        self.w = int(np.ceil(np.e / epsilon))      # error <= eps * total
        self.d = int(np.ceil(np.log(1 / delta)))   # with prob. 1 - delta
        self.table = np.zeros((self.d, self.w), dtype=np.int64)
        rng = np.random.default_rng(seed)
        self.seeds = rng.integers(1, 2 ** 31, size=self.d)

    def _cols(self, key):
        h = hash(key)
        return [(h ^ int(s)) % self.w for s in self.seeds]

    def add(self, key, count=1):
        for r, c in enumerate(self._cols(key)):
            self.table[r, c] += count

    def estimate(self, key):
        return min(self.table[r, c] for r, c in enumerate(self._cols(key)))

    def merge(self, other):                        # mergeable: just add
        self.table += other.table
        return self
```

:::theorem Count--Min error bound
With $w = \lceil e/\varepsilon \rceil$ and $d = \lceil \ln(1/\delta) \rceil$,
the estimate $\hat{f}_x$ satisfies $f_x \le \hat{f}_x$ always, and
$\hat{f}_x \le f_x + \varepsilon N$ with probability at least $1 - \delta$,
where $N$ is the total count of all items.
:::

The error is relative to the *total* stream, not to the item's own count.
That is why Count--Min is excellent for heavy hitters --- items whose counts
are a significant fraction of $N$ --- and poor for rare items, whose true
count may be dwarfed by $\varepsilon N$. If you need accurate estimates of
small counts, use a Count-Sketch (which uses signed updates and takes a
median, giving a two-sided but much tighter bound for small items) or keep
exact counts for the heavy hitters found by the sketch.

:::ml Count--Min in practice
Tracking the most frequent tokens, queries, user agents or feature values in
a stream too large to count exactly; detecting hot keys in a sharded cache
or a parameter server; estimating $n$-gram frequencies for a language model
without storing the full table; monitoring per-tenant request rates. In each
case the pattern is: sketch everything, and keep an exact heap of the top
$k$ discovered heavy hitters.
:::

## HyperLogLog

Counting *distinct* items exactly requires storing them. HyperLogLog
estimates the count using a single insight: if you hash items uniformly, the
maximum number of leading zeros you observe tells you roughly how many
distinct items there were --- seeing a hash beginning with 20 zeros suggests
about $2^{20}$ distinct items.

```python title="HyperLogLog in forty lines"
import math

class HyperLogLog:
    def __init__(self, p=14):                  # 2^14 = 16384 registers
        self.p = p
        self.m = 1 << p
        self.registers = bytearray(self.m)     # 6 bits each would suffice
        self.alpha = {4: 0.673, 5: 0.697, 6: 0.709}.get(
            p, 0.7213 / (1 + 1.079 / self.m))

    def add(self, item):
        h = hash(item) & ((1 << 64) - 1)
        idx = h >> (64 - self.p)               # first p bits pick a register
        rest = (h << self.p) & ((1 << 64) - 1) # remaining bits
        rank = 1
        while rest and not (rest >> 63):       # count leading zeros + 1
            rest <<= 1
            rank += 1
        if rank > self.registers[idx]:
            self.registers[idx] = rank

    def count(self):
        raw = self.alpha * self.m ** 2 / sum(2.0 ** -r for r in self.registers)
        zeros = self.registers.count(0)
        if raw <= 2.5 * self.m and zeros:      # small-range correction
            return int(round(self.m * math.log(self.m / zeros)))
        return int(round(raw))

    def merge(self, other):                    # mergeable: element-wise max
        self.registers = bytearray(max(a, b) for a, b in
                                   zip(self.registers, other.registers))
        return self
```

The construction: split the hash into a register index and a tail; store the
maximum rank per register; and combine the registers with a *harmonic* mean
(which suppresses the influence of outlier registers, the key improvement of
HyperLogLog over LogLog). The standard error is
$1.04/\sqrt{m}$, so $m = 2^{14}$ registers at 6 bits each --- **12 KB** ---
gives about 0.81% error for cardinalities from zero to $10^9$.

:::insight Mergeability is the property that makes sketches distributed
Bloom filters merge with OR. Count--Min merges with addition. HyperLogLog
merges with element-wise maximum. In every case, merging sketches of disjoint
shards yields exactly the sketch of the union --- so you can compute a global
answer by a tree reduction (Chapter 16), with no coordination and no data
movement beyond the sketches themselves. This is why they are the native
aggregation primitive in Spark, Druid, Redis and BigQuery.
:::

:::pitfall The union of HyperLogLogs is free; the intersection is not
HLL merges give you $|A \cup B|$ exactly as well as it gives you either. To
get $|A \cap B|$ you must use inclusion--exclusion,
$|A| + |B| - |A \cup B|$, and the errors *add* while the answer may be small
--- so the relative error on the intersection can be enormous. For
intersections use a different structure (MinHash, Chapter 29, whose whole
point is estimating Jaccard similarity) or keep exact sets.
:::

| Sketch | Answers | Memory | Error | Merge |
|---|---|---|---|---|
| Bloom filter | membership | $1.44 n \log_2(1/p)$ bits | one-sided, $p$ | OR |
| Count--Min | frequency | $\frac{e}{\varepsilon}\ln\frac{1}{\delta}$ counters | $+\varepsilon N$, one-sided | add |
| Count-Sketch | frequency | same | $\pm\varepsilon\|f\|_2$, two-sided | add |
| HyperLogLog | cardinality | $m$ registers of 6 bits | $1.04/\sqrt m$ | max |
| t-digest | quantiles | $\Theta(\delta)$ centroids | tight at the tails | merge centroids |
| MinHash | Jaccard | $k$ hashes per set | $1/\sqrt k$ | min |

@tbl: The sketch family. Note that memory depends on the *accuracy target*, not on the data size --- that is the defining property.

:::exercise
1. Implement the Bloom filter and measure the empirical false-positive rate
   for $p \in \{0.1, 0.01, 0.001\}$ at $n = 10^6$. Compare to the formula.
2. Show empirically that the Kirsch--Mitzenmacher double-hashing trick gives
   the same false-positive rate as $k$ independent hashes.
3. Implement a blocked Bloom filter (all $k$ bits within one 64-byte block)
   and measure the lookup throughput against the plain version. Quantify the
   accuracy cost.
4. Build a Count--Min sketch over a Zipf-distributed stream of $10^8$ events.
   Measure the relative error for the top 10, top 1000 and tail items, and
   explain the pattern.
5. Implement the heavy-hitters pattern: a Count--Min sketch plus a
   size-$k$ min-heap of candidates. Compare its top-100 to the exact answer.
6. Implement HyperLogLog and plot the relative error against true
   cardinality from $10^2$ to $10^9$. Identify the range where the
   small-range correction matters.
7. Estimate $|A \cap B|$ by inclusion--exclusion on HLLs where
   $|A| = |B| = 10^8$ and $|A \cap B| = 10^4$. Report the relative error and
   explain it.
8. Design a memory budget: deduplicate 10 billion documents on a machine with
   32 GB of RAM. State your structure, its parameters, its error rate, and
   what that error costs you.
:::

:::recap
- Sketches trade a bounded, tunable error for memory that depends on the
  accuracy target rather than on the data size.
- Bloom filters cost $1.44 n \log_2(1/p)$ bits with $k = (m/n)\ln 2$ hashes.
  Their error is one-sided: safe for skipping work, unsafe for asserting
  existence.
- Count--Min never underestimates and overestimates by at most $\varepsilon N$
  with probability $1-\delta$; it is good for heavy hitters and poor for rare
  items.
- HyperLogLog estimates cardinality from the maximum leading-zero rank per
  register, with error $1.04/\sqrt m$ --- about 0.8% in 12 KB for any
  cardinality up to $10^9$.
- Mergeability (OR, add, max) lets sketches be combined by tree reduction
  across shards with no coordination.
- Unions of HLLs are accurate; intersections by inclusion--exclusion are not.
:::
