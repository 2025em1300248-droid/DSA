# MinHash, SimHash and LSH: Deduplicating a Training Corpus
@short: LSH and Dedup
@subtitle: Finding near-duplicates among ten billion documents
@tier: advanced
@prereq: Chapters 15, 28
@blurb: Exact deduplication is a hash set. Near-duplicate detection --- documents differing by a header, a licence block, or one paragraph --- cannot use a hash set, because hashing destroys similarity by design. Locality-sensitive hashing is the repair: a family of hashes engineered so that similar inputs collide on purpose. This is the algorithm behind every serious corpus-cleaning pipeline.
@objectives:
- Explain why near-duplicate detection is not a hash-set problem
- Implement shingling and MinHash, and prove the collision identity
- Tune the banding parameters to hit a target similarity threshold
- Implement SimHash for cosine similarity and know when to prefer it
- Build a complete corpus deduplication pipeline and estimate its cost
- Understand LSH as the ancestor of modern vector indexes

## The problem

A web-scale corpus is 30--60% near-duplicate by document count. Duplicates
waste training compute, inflate benchmark scores through contamination, and
increase verbatim memorisation. Removing them measurably improves models per
unit of compute.

Comparing all pairs of $10^{10}$ documents is $5 \times 10^{19}$
comparisons --- not "slow", but impossible. We need a method that only
compares documents that have a real chance of being similar.

:::definition Locality-sensitive hash family
A family $\mathcal{H}$ of hash functions is $(s_1, s_2, p_1, p_2)$-sensitive
for a similarity measure $\text{sim}$ if, for $h$ drawn at random from
$\mathcal{H}$:

- $\text{sim}(x,y) \ge s_1 \implies \Pr[h(x) = h(y)] \ge p_1$
- $\text{sim}(x,y) \le s_2 \implies \Pr[h(x) = h(y)] \le p_2$

with $s_1 > s_2$ and $p_1 > p_2$. In words: similar items collide often,
dissimilar items collide rarely. An ordinary hash function has
$p_1 = p_2 = 0$ for $x \neq y$, which is exactly what makes it useless here.
:::

## Step 1: shingling

Represent each document as a *set*, so that similarity becomes set
similarity.

```python title="Shingling: a document becomes a set of hashed n-grams"
import hashlib

def shingles(text, k=9, word_level=True):
    """k-shingles as 64-bit hashes. k=5..10 words, or 8..12 characters."""
    units = text.split() if word_level else list(text)
    out = set()
    for i in range(len(units) - k + 1):
        piece = " ".join(units[i:i + k]) if word_level else "".join(units[i:i + k])
        out.add(int.from_bytes(
            hashlib.blake2b(piece.encode("utf-8"), digest_size=8).digest(),
            "big"))
    return out
```

The choice of $k$ is a real decision. Too small and unrelated documents share
shingles by chance (every English document contains "of the"); too large and
a single word change destroys many shingles. Word-level $k = 5$ to $9$ is
standard for prose.

:::definition Jaccard similarity
$J(A, B) = \dfrac{|A \cap B|}{|A \cup B|}$. Two documents with identical
shingle sets have $J = 1$; disjoint sets give $J = 0$. Empirically $J > 0.8$
means near-duplicate for prose, $J > 0.5$ means substantial overlap.
:::

## Step 2: MinHash

Storing shingle sets is expensive --- a 10 KB document has thousands of
shingles. MinHash compresses each set to a fixed-length signature that
preserves Jaccard similarity.

:::theorem The MinHash identity
Let $\pi$ be a random permutation of the universe, and define
$h_\pi(A) = \min_{a \in A} \pi(a)$. Then
$$\Pr[h_\pi(A) = h_\pi(B)] = J(A, B)$$
:::

:::proof
Consider the elements of $A \cup B$. Under a random permutation, each is
equally likely to be the one with the smallest $\pi$-value. That minimum
element yields $h_\pi(A) = h_\pi(B)$ exactly when it lies in $A \cap B$, and
otherwise the minima differ. The probability of that event is
$|A \cap B| / |A \cup B| = J(A,B)$.
:::

So with $K$ independent hash functions, the fraction of the $K$ signature
positions on which two documents agree is an unbiased estimate of $J$, with
standard error $\sqrt{J(1-J)/K} \le 1/(2\sqrt K)$. $K = 128$ gives about
4.4% error; $K = 256$ gives 3%.

```python title="MinHash signatures, vectorised"
import numpy as np

MERSENNE = (1 << 61) - 1

class MinHasher:
    def __init__(self, num_perm=128, seed=0):
        rng = np.random.default_rng(seed)
        self.a = rng.integers(1, MERSENNE, size=num_perm, dtype=np.uint64)
        self.b = rng.integers(0, MERSENNE, size=num_perm, dtype=np.uint64)
        self.num_perm = num_perm

    def signature(self, shingle_hashes):
        if not shingle_hashes:
            return np.full(self.num_perm, MERSENNE, dtype=np.uint64)
        x = np.fromiter(shingle_hashes, dtype=np.uint64)
        # (a*x + b) mod p, for all permutations at once: (n, num_perm)
        h = (np.outer(x, self.a) + self.b) % MERSENNE
        return h.min(axis=0)                      # one min per permutation

    @staticmethod
    def estimate(sig_a, sig_b):
        return float((sig_a == sig_b).mean())
```

Universal hashing $h(x) = (ax + b) \bmod p$ with a Mersenne prime is the
standard substitute for a true random permutation: cheap, and provably good
enough for this bound.

## Step 3: banding into an LSH index

@fig: minhash_lsh | 152 | MinHash signatures split into $b$ bands of $r$ rows. Two documents become candidates if any band matches exactly, which turns similarity search into hash-table lookups.

Split the $K$-element signature into $b$ bands of $r$ rows ($K = br$). Hash
each band; two documents are *candidates* if they share a bucket in any band.

:::math The S-curve
If two documents have Jaccard similarity $s$:
- one row agrees with probability $s$;
- a whole band of $r$ rows agrees with probability $s^r$;
- no band agrees with probability $(1 - s^r)^b$;
- so $\Pr[\text{candidate}] = 1 - (1 - s^r)^b$.

This is an S-curve with its steep region near $s^* \approx (1/b)^{1/r}$.
Choosing $b$ and $r$ *is* choosing your similarity threshold.

For $K = 128$: $(b, r) = (16, 8)$ gives $s^* \approx 0.69$;
$(32, 4)$ gives $s^* \approx 0.42$; $(8, 16)$ gives $s^* \approx 0.88$.
Fewer, longer bands means a higher, sharper threshold.
:::

```python title="The LSH index"
from collections import defaultdict

class LSHIndex:
    def __init__(self, num_perm=128, bands=16):
        assert num_perm % bands == 0
        self.bands, self.rows = bands, num_perm // bands
        self.tables = [defaultdict(list) for _ in range(bands)]

    def add(self, doc_id, signature):
        for i, table in enumerate(self.tables):
            band = signature[i * self.rows:(i + 1) * self.rows].tobytes()
            table[band].append(doc_id)

    def candidates(self, signature):
        out = set()
        for i, table in enumerate(self.tables):
            band = signature[i * self.rows:(i + 1) * self.rows].tobytes()
            out.update(table.get(band, ()))
        return out
```

## Step 4: clustering

Candidate pairs are verified (recompute the MinHash estimate, or the exact
Jaccard if you kept the shingles) and then turned into groups with union--find
(Chapter 15). Keep one representative per cluster.

```python title="The complete pipeline"
def deduplicate(docs, num_perm=128, bands=16, threshold=0.8):
    hasher = MinHasher(num_perm)
    index = LSHIndex(num_perm, bands)
    sigs = {}
    pairs = []
    for doc_id, text in docs:                          # one streaming pass
        sig = hasher.signature(shingles(text))
        for other in index.candidates(sig):
            if MinHasher.estimate(sig, sigs[other]) >= threshold:
                pairs.append((doc_id, other))
        index.add(doc_id, sig)
        sigs[doc_id] = sig
    dsu = DSU(len(sigs))
    for a, b in pairs:
        dsu.union(a, b)
    keep = {}
    for doc_id in sigs:
        keep.setdefault(dsu.find(doc_id), doc_id)      # one per cluster
    return set(keep.values())
```

:::perf Cost of deduplicating a billion documents
Signatures: $128 \times 8$ bytes $= 1$ KB per document, so 1 TB for $10^9$
documents --- too much for memory, fine on disk or sharded across a cluster.
Use 4-byte hashes and $K = 128$ to get 512 bytes each.

The LSH index holds $b$ entries per document; with $b = 16$ that is $1.6
\times 10^{10}$ entries. The standard approach is to run one band at a time:
sort all documents by their band hash (an external sort, Chapter 42), and
emit candidate pairs from each equal run. That is 16 passes of an external
sort and needs no random-access index at all --- which is exactly how the
published pipelines (C4, The Pile, RefinedWeb, FineWeb) do it.

Total: about 20 CPU-hours per billion documents for signatures, plus the
sorts. Comfortably feasible; the naive pairwise comparison is not.
:::

## SimHash: LSH for cosine similarity

MinHash targets Jaccard similarity on sets. For *vectors* and cosine
similarity, the right family is random hyperplanes.

:::theorem The random-hyperplane identity
For a random unit vector $r$, define $h_r(x) = \text{sign}(r \cdot x)$. Then
$$\Pr[h_r(x) = h_r(y)] = 1 - \frac{\theta(x,y)}{\pi}$$
where $\theta$ is the angle between $x$ and $y$.
:::

```python title="SimHash: 64 random hyperplanes, one 64-bit fingerprint"
import numpy as np

def simhash(vectors, bits=64, seed=0):
    rng = np.random.default_rng(seed)
    R = rng.standard_normal((vectors.shape[1], bits)).astype(np.float32)
    signs = (vectors @ R) > 0                      # (n, bits) booleans
    weights = (1 << np.arange(bits, dtype=np.uint64))
    return (signs * weights).sum(axis=1)           # pack into uint64

def hamming(a, b):
    return bin(int(a) ^ int(b)).count("1")
```

Two documents are near-duplicates if their fingerprints differ in few bits.
Finding all pairs within Hamming distance $d$ of each other among billions of
fingerprints is itself an indexing problem: the standard solution splits the
64 bits into $d+1$ blocks, since two fingerprints within distance $d$ must
agree exactly on at least one block --- the pigeonhole principle, and the
same banding idea as MinHash.

| Method | Similarity | Signature | Best for |
|---|---|---|---|
| MinHash + LSH | Jaccard | $K$ integers (512 B--1 KB) | documents as shingle sets |
| SimHash | cosine | 64 bits | documents as tf-idf or embedding vectors |
| SimHash on embeddings | cosine | 64--256 bits | semantic near-duplicates |
| Exact hash | equality | 16 bytes | byte-identical duplicates |
| Suffix automaton | substring | index | long exact substrings, Chapter 30 |

@tbl: Choose by the similarity you actually mean. SimHash is far more compact; MinHash is more accurate at high similarity and its parameters are easier to reason about.

:::ml Deduplication decisions that matter more than the algorithm
**Granularity.** Document-level deduplication misses boilerplate repeated
across otherwise different pages. Paragraph or line-level deduplication
(as in RefinedWeb and FineWeb) removes far more redundancy but risks
fragmenting documents; the usual compromise is to remove lines appearing in
more than $N$ documents.

**Which copy to keep.** Longest, highest-quality-score, or earliest-crawled.
This matters more for final model quality than the threshold does.

**Cross-split contamination.** Run deduplication *between* training and
evaluation sets as well as within training. Reporting the overlap you found
is now standard practice in model cards.

**Transitivity.** Union--find merges $A$--$B$ and $B$--$C$ into one cluster
even if $A$ and $C$ are unrelated (Chapter 15). At scale this produces
occasional enormous clusters. Cap cluster size, or use connected components
of the *mutual* top-$k$ graph instead.
:::

:::insight LSH is the ancestor of every vector index
The idea --- hash so that near things collide, then search only within a
bucket --- is the direct ancestor of the inverted-file index (partition space,
probe a few cells) in Chapter 33. LSH has been largely superseded for
high-dimensional nearest-neighbour search by graph methods such as HNSW,
because LSH needs many tables to achieve good recall and graph methods get
there with less memory. But for *deduplication*, where you want all pairs
above a threshold rather than the $k$ nearest to a query, LSH is still the
right tool and is not close to being displaced.
:::

:::exercise
1. Verify the MinHash identity empirically: generate random sets with known
   Jaccard similarity and check that the signature agreement matches, and
   that the error scales as $1/\sqrt K$.
2. Plot the S-curve $1 - (1 - s^r)^b$ for $(b,r) \in \{(16,8), (32,4),
   (8,16)\}$ and mark the thresholds. Choose $(b, r)$ for a target threshold
   of 0.75 with $K = 200$.
3. Implement the full pipeline and run it on 100,000 documents with injected
   near-duplicates. Report precision and recall against ground truth as a
   function of $(b, r)$.
4. Implement the band-sort variant that avoids holding the index in memory,
   and verify it produces the same candidate pairs.
5. Implement SimHash over tf-idf vectors and compare its precision/recall to
   MinHash at the same signature size in bytes.
6. Implement the pigeonhole block search for all fingerprint pairs within
   Hamming distance 3 among $10^6$ 64-bit fingerprints.
7. Demonstrate the transitive-merging problem: construct documents
   $A, B, C$ with $J(A,B) = J(B,C) = 0.85$ and $J(A,C) = 0.3$, and show they
   end up in one cluster. Propose and implement a mitigation.
:::

:::recap
- Ordinary hashing destroys similarity; LSH families are engineered so that
  similar inputs collide with high probability.
- Shingling turns documents into sets so that similarity becomes Jaccard.
- MinHash compresses a set to $K$ numbers with
  $\Pr[\text{collision}] = J$, so signature agreement estimates Jaccard with
  error $\approx 1/(2\sqrt K)$.
- Banding $K = br$ gives a candidate probability $1-(1-s^r)^b$, an S-curve
  with threshold $\approx (1/b)^{1/r}$; choosing $b$ and $r$ is choosing the
  threshold.
- Candidate pairs are verified and clustered with union--find; the band-sort
  variant scales to billions without an in-memory index.
- SimHash uses random hyperplanes for cosine similarity and gives a 64-bit
  fingerprint; pigeonhole blocking finds close pairs.
- The hard decisions are granularity, which copy to keep, cross-split
  contamination and transitive over-merging --- not the hashing.
:::
