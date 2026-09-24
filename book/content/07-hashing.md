# Hashing: Dictionaries, Sets and the Hashing Trick
@short: Hashing
@subtitle: Constant-time lookup, and the fine print that makes it true
@tier: foundation
@prereq: Chapters 2--4
@blurb: The hash table is the most-used non-trivial data structure in existence and the one most people use without a model of how it works. That model pays for itself the first time a lookup becomes slow, a dict eats forty gigabytes, or two runs of the same script produce different results. This chapter builds hash tables from scratch, then applies them to deduplication, feature hashing and vocabulary management.
@objectives:
- Explain what a hash function must guarantee and what it must not
- Implement separate chaining and open addressing, and choose between them
- Reason about load factor, resizing and the amortised cost of insertion
- Predict and fix the memory cost of large Python dictionaries
- Apply the hashing trick, and know when collisions will and will not hurt
- Recognise the security and reproducibility traps in hashing

## What a hash table is

A hash table stores key--value pairs in an array of $m$ buckets. A hash
function $h$ maps a key to a bucket index. If $h$ spreads keys evenly, each
bucket holds about $n/m$ keys, and with $m$ proportional to $n$ that is a
constant --- hence $\Theta(1)$ expected lookup.

Everything interesting is in the two failure modes: *collisions* (two keys in
one bucket) and *growth* (what happens when $n$ outruns $m$).

:::definition What a hash function must do
A hash function $h: K \to \{0, \ldots, m-1\}$ should be **fast** (a few
nanoseconds), **deterministic** within a process, and **uniform**: for keys
drawn from any realistic distribution, the bucket indices should look
uniformly distributed and independent. It does *not* need to be
cryptographic; it needs to be hard to hit collisions *by accident*, and ---
when keys come from users --- hard to hit them on purpose.
:::

## Separate chaining

@fig: hash_chaining | 165 | Separate chaining: each bucket holds a list of entries. With load factor $\alpha = n/m$, an unsuccessful lookup scans $\alpha$ entries on average.

```python title="A hash map with separate chaining and resizing"
class HashMap:
    def __init__(self, capacity=8, max_load=0.75):
        self._buckets = [[] for _ in range(capacity)]
        self._n = 0
        self._max_load = max_load

    def _index(self, key):
        return hash(key) & (len(self._buckets) - 1)   # power-of-2 mask

    def get(self, key, default=None):
        for k, v in self._buckets[self._index(key)]:
            if k == key:                 # == not 'is': equal keys must match
                return v
        return default

    def put(self, key, value):
        bucket = self._buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._n += 1
        if self._n > self._max_load * len(self._buckets):
            self._resize(len(self._buckets) * 2)

    def _resize(self, capacity):
        old = self._buckets
        self._buckets = [[] for _ in range(capacity)]
        for bucket in old:
            for k, v in bucket:
                self._buckets[hash(k) & (capacity - 1)].append((k, v))
```

Two details in `_index` matter. Using a power-of-two capacity lets us replace
a modulo (about 20 cycles) with a bitwise AND (one cycle). The cost is that
we now depend on the *low* bits of the hash being well mixed --- which is why
Java's `HashMap` XORs the high bits down before masking, and why using a
power-of-two table with a weak hash such as Python's identity hash for small
ints can produce clustering.

The resize is the dynamic-array argument again: doubling makes rehashing
$\Theta(1)$ amortised per insertion. But note that rehashing is $\Theta(n)$ in
one operation, so a hash table gives amortised, not worst-case, $\Theta(1)$
insertion. In a latency-sensitive path this is a real spike; incremental
resizing (Redis does this) spreads the work over subsequent operations.

## Open addressing

The alternative is to keep everything in one array and, on collision, probe
for another slot.

@fig: open_addressing | 110 | Linear probing. All entries live in a single contiguous array, so a probe sequence is a cache-line scan rather than a pointer chase.

| Scheme | Probe sequence | Pros | Cons |
|---|---|---|---|
| Linear | $h, h+1, h+2, \ldots$ | perfect locality, simple | primary clustering |
| Quadratic | $h, h+1, h+4, h+9, \ldots$ | less clustering | worse locality |
| Double hashing | $h_1, h_1+h_2, h_1+2h_2, \ldots$ | near-uniform probing | two hashes, poor locality |
| Robin Hood | linear, but steal from the rich | low variance in probe length | more work per insert |
| Swiss / F14 | SIMD scan of 16 control bytes | fastest in practice | complex |

@tbl: Open-addressing schemes. Modern high-performance tables (Abseil's `flat_hash_map`, Rust's `hashbrown`, Folly's `F14`) all use a variant of the last row: a separate array of one-byte tags scanned sixteen at a time with SIMD.

Open addressing wins on speed below a load factor of about 0.7 because the
probe sequence is contiguous. It degrades sharply above that --- the expected
probe count for linear probing is roughly $\frac{1}{2}(1 + \frac{1}{(1-\alpha)^2})$,
which at $\alpha = 0.9$ is 50 probes. Chaining degrades gracefully but pays a
pointer dereference on every lookup.

:::pitfall Deletion in open addressing
You cannot simply clear a slot: doing so breaks the probe sequences of
entries that were displaced past it. You must write a *tombstone*, a marker
meaning "empty for insertion, keep probing for lookup". Tables that delete
heavily accumulate tombstones and must be rehashed periodically. If you ever
write your own table, this is the bug you will have.
:::

## Python's dict, concretely

CPython's `dict` is open-addressed with a perturbation-based probe sequence,
and since version 3.6 it is *split*: a compact array of `(hash, key, value)`
entries in insertion order, plus an index array of small integers pointing
into it. That layout is why dicts preserve insertion order and why they got
about 25% smaller in 3.6.

| Structure | Bytes per entry (CPython 3.11, 64-bit) |
|---|---|
| `dict` of int to int | $\approx 100$ including the boxed ints |
| `set` of int | $\approx 60$ |
| `list` of int | $\approx 36$ (8 pointer + 28 int object) |
| `array.array("q")` | 8 |
| `np.int64` array | 8 |
| `dict` of str to int, 12-char keys | $\approx 170$ |

@tbl: Approximate per-entry memory. The factor of twelve between a `dict` of ints and a NumPy array is the reason large ID mappings must not be dicts.

:::pitfall The forty-gigabyte vocabulary
A `dict` mapping 200 million integer user ids to integer row indices needs
roughly 20 GB in CPython and will be killed by the OOM reaper. Three fixes,
in increasing order of effort: (1) sort the ids into a NumPy array and use
`np.searchsorted` --- 1.6 GB, $\Theta(\log n)$ lookup, and vectorised over a
whole batch at once; (2) use a perfect hash or a minimal perfect hash if the
key set is static; (3) drop the mapping entirely and use the hashing trick,
below.
:::

## Hashing your own objects

```python title="Correct __hash__ and __eq__"
class Doc:
    __slots__ = ("doc_id", "shard")
    def __init__(self, doc_id, shard):
        self.doc_id, self.shard = doc_id, shard

    def __eq__(self, other):
        return (isinstance(other, Doc)
                and (self.doc_id, self.shard) == (other.doc_id, other.shard))

    def __hash__(self):
        return hash((self.doc_id, self.shard))   # tuple hash mixes properly
```

Three invariants, and violating any of them produces a bug that is very hard
to find:

1. **If `a == b` then `hash(a) == hash(b)`.** Otherwise equal keys land in
   different buckets and your set contains duplicates.
2. **The hash must not change while the object is in a container.** Mutating
   a field used by `__hash__` makes the entry unreachable --- it is still in
   the table, occupying memory, and `k in d` returns `False`.
3. **Hash only immutable, identity-defining fields.** Never hash a
   floating-point score or a timestamp.

:::warning `hash()` of a string is randomised per process
Python salts string and bytes hashes with a per-process random seed
(`PYTHONHASHSEED`) to prevent collision-based denial of service. The
consequence is that `hash("abc")` differs between runs, so anything you
*persist* or *shard on* must use an explicit stable hash --- `hashlib.blake2b`,
`xxhash`, `mmh3` --- not the builtin. Sharding a dataset with `hash(key) % n`
will silently reassign every record on restart.
:::

## The hashing trick

Suppose you need feature indices for an unbounded, growing categorical space:
user agents, URL n-grams, product ids in a live catalogue. The textbook
answer is a vocabulary dict, which must be built, stored, versioned and
synchronised between training and serving. The hashing trick removes it
entirely.

$$\text{index}(f) = h(f) \bmod m, \qquad \text{sign}(f) = \pm 1 \text{ from a second hash}$$

```python title="Signed feature hashing"
import xxhash, numpy as np

def hash_features(features, m=2 ** 20):
    x = np.zeros(m, dtype=np.float32)
    for f, value in features.items():
        h = xxhash.xxh64(f).intdigest()
        idx = h % m
        sign = 1.0 if (h >> 63) & 1 else -1.0   # independent bit
        x[idx] += sign * value
    return x
```

The signed variant matters. Without signs, colliding features add
constructively and the inner product between two hashed vectors is biased
upward. With random signs the collisions cancel in expectation, so
$\mathbb{E}[\langle \phi(a), \phi(b) \rangle] = \langle a, b \rangle$: the
hashed inner product is an unbiased estimator of the true one, with variance
falling as $1/m$.

:::ml Where the hashing trick is the right call
- **Very high-cardinality categoricals** in ranking and ads models, where a
  vocabulary would be larger than the model.
- **Online / streaming features** where new values appear constantly and a
  frozen vocabulary would map them all to `UNK`.
- **Train--serve consistency**, because there is no artefact to keep in sync;
  the hash function *is* the vocabulary.

And where it is not: any setting where you must explain or inspect a
feature (collisions destroy interpretability), where the vocabulary is small
and stable (a dict is exact and just as fast), or where a single collision
between two very high-signal features would be costly. In practice, choose
$m$ so that the expected number of colliding *frequent* features is small;
$m = 2^{20}$ to $2^{24}$ is typical.
:::

## Deduplication, the canonical application

```python title="Exact dedup of a document stream in one pass"
import hashlib

def dedup(stream):
    seen = set()                       # stores 16-byte digests, not documents
    for doc in stream:
        digest = hashlib.blake2b(doc.encode("utf-8"), digest_size=16).digest()
        if digest not in seen:
            seen.add(digest)
            yield doc
```

Storing the digest rather than the document keeps memory at roughly 80 bytes
per unique document instead of the document itself. With 16-byte digests the
probability of a collision among $n$ documents is about $n^2 / 2^{129}$,
which for $n = 10^{12}$ is around $10^{-15}$ --- comfortably below your
hardware's error rate.

This is exact deduplication. *Near*-duplicate detection --- documents that
differ by a boilerplate header --- cannot be done with a hash set, because
hashes destroy similarity by design. That needs MinHash and LSH, Chapter 29.

:::insight The one-sentence summary of hashing
A hash function deliberately destroys structure, which is exactly why it
gives you $\Theta(1)$ exact lookup and exactly why it can never give you
"similar to". Every approximate-similarity structure in Part VI is a hash
that has been carefully weakened so that *some* structure survives.
:::

## Consistent hashing, in brief

Sharding with `hash(key) % N` has a fatal operational property: changing $N$
remaps almost every key. Consistent hashing places both shards and keys on a
circle and assigns each key to the next shard clockwise; adding a shard then
moves only $1/N$ of the keys. With $v$ virtual nodes per physical shard the
load imbalance falls as $1/\sqrt{v}$; $v = 100$ to $200$ is standard.

This is how distributed caches, sharded vector indexes and parameter servers
avoid a full reshuffle on every scaling event. Chapter 41 builds it.

:::exercise
1. Implement the `HashMap` above with open addressing and linear probing,
   including tombstones. Measure the average probe count at load factors
   0.5, 0.7, 0.9 and compare to $\frac{1}{2}(1 + (1-\alpha)^{-2})$.
2. Construct a set of 10,000 Python strings that all collide modulo $2^{10}$
   under a fixed `PYTHONHASHSEED`. Measure lookup time before and after.
   Explain why randomised hashing prevents this in the wild.
3. A dict maps 50 million 8-character strings to float scores. Estimate its
   memory. Design a replacement using sorted arrays plus `np.searchsorted`
   and measure both.
4. Show empirically that unsigned feature hashing biases inner products
   upward and that signed hashing does not. Plot the variance against $m$.
5. Write a `__hash__` that violates invariant 2, insert the object into a
   set, mutate it, and demonstrate that `obj in s` is now `False` while
   `len(s) == 1`.
6. Implement consistent hashing with virtual nodes and measure the fraction
   of keys that move when a shard is added, for $v \in \{1, 10, 100\}$.
7. You must deduplicate 4 billion documents on one machine with 64 GB of RAM.
   Exact dedup with a 16-byte digest set needs roughly 400 GB. Give two
   designs that fit, and state precisely what each one gives up.
:::

:::recap
- A hash table trades a small probability of collision for $\Theta(1)$
  expected lookup; load factor governs the trade and resizing keeps it bounded.
- Chaining degrades gracefully and tolerates high load; open addressing is
  faster below $\alpha \approx 0.7$ because probes are cache-line scans.
  Deleting from an open-addressed table requires tombstones.
- Insertion is amortised $\Theta(1)$, not worst-case: a resize is a real
  latency spike.
- Python dicts cost roughly 100 bytes per int-to-int entry; at tens of
  millions of keys switch to sorted arrays plus `searchsorted`, a perfect
  hash, or the hashing trick.
- `__hash__` must agree with `__eq__`, must never change while the object is
  in a container, and must use only identity-defining fields.
- Builtin string hashing is per-process randomised; never persist or shard
  on it.
- Signed feature hashing gives an unbiased estimate of inner products and
  removes the vocabulary artefact entirely --- at the cost of
  interpretability.
- Consistent hashing moves only $1/N$ of keys when a shard is added.
:::
