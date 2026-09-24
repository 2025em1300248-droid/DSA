# Suffix Structures, Substring Search and Contamination
@short: Suffix Structures
@subtitle: Indexing every substring of a corpus at once
@tier: advanced
@prereq: Chapters 9, 14
@blurb: A trie indexes a set of strings. A suffix array indexes every substring of one string --- which turns out to be the right tool for finding long exact repeats in a training corpus, detecting benchmark contamination, and measuring how much a model could be memorising. This chapter builds the structures and the pipeline that uses them at terabyte scale.
@objectives:
- Build a suffix array and an LCP array, and use them for substring search
- Implement KMP and understand its failure function as prefix knowledge
- Find the longest repeated substring and all long repeats in a corpus
- Build an exact substring-matching pipeline for contamination detection
- Compare suffix arrays, suffix automata and $n$-gram indexes
- Quantify memorisation and contamination in a training set

## Exact substring search: KMP

Before the index, the single-pattern scan. Naive search is $\Theta(nm)$
because a mismatch throws away everything learned. Knuth--Morris--Pratt keeps
it.

```python title="KMP: build the failure function, then scan without backtracking"
def kmp_failure(pat):
    """fail[i] = length of the longest proper prefix of pat[:i+1]
    that is also a suffix of it."""
    fail = [0] * len(pat)
    k = 0
    for i in range(1, len(pat)):
        while k and pat[i] != pat[k]:
            k = fail[k - 1]                  # fall back within the pattern
        if pat[i] == pat[k]:
            k += 1
        fail[i] = k
    return fail

def kmp_search(text, pat):
    if not pat:
        return []
    fail, hits, k = kmp_failure(pat), [], 0
    for i, ch in enumerate(text):
        while k and ch != pat[k]:
            k = fail[k - 1]
        if ch == pat[k]:
            k += 1
        if k == len(pat):
            hits.append(i - k + 1)
            k = fail[k - 1]                  # continue, allowing overlaps
    return hits
```

$\Theta(n + m)$, and the text pointer never moves backwards --- which means
it works on a stream. The failure function is the same idea as
Aho--Corasick's failure links (Chapter 14): a mismatch tells you how far you
may skip, because you know what you have already matched.

## Suffix arrays

:::definition Suffix array and LCP array
For a string $S$ of length $n$, the **suffix array** $SA$ is the permutation
of $0 \ldots n-1$ that lists the starting positions of all suffixes in
lexicographic order. The **LCP array** gives, for each adjacent pair in $SA$,
the length of their longest common prefix.
:::

@fig: suffix_array | 145 | The suffix array of "banana$". Because the suffixes are sorted, every occurrence of a pattern occupies a contiguous block, findable by two binary searches.

```python title="Suffix array by prefix doubling: O(n log^2 n)"
def suffix_array(s):
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    k = 1
    while True:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)                      # theta(n log n) per round
        new_rank = [0] * n
        for i in range(1, n):
            new_rank[sa[i]] = new_rank[sa[i - 1]] + (key(sa[i]) != key(sa[i - 1]))
        rank = new_rank
        if rank[sa[-1]] == n - 1:             # all ranks distinct: done
            return sa
        k <<= 1                               # compare twice as far next time

def lcp_array(s, sa):
    """Kasai's algorithm: theta(n)."""
    n = len(s)
    rank = [0] * n
    for i, p in enumerate(sa):
        rank[p] = i
    lcp, h = [0] * n, 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h:
                h -= 1                        # amortised: h drops by at most 1
        else:
            h = 0
    return lcp
```

Prefix doubling is $\Theta(n \log^2 n)$ with a comparison sort, or
$\Theta(n \log n)$ with radix sort. Linear-time constructions exist (SA-IS,
DC3) and are what production libraries use; for corpus work,
`libdivsufsort` or SA-IS on a memory-mapped file is the standard choice.

Kasai's algorithm for LCP is a small gem: the amortised argument is that $h$
increases at most $n$ times in total and decreases by at most one per
iteration, so the whole thing is linear.

| Query | With suffix array | Cost |
|---|---|---|
| Does $P$ occur? | binary search for the block | $\Theta(m \log n)$ |
| How many times? | size of the block | $\Theta(m \log n)$ |
| All occurrences | the block's entries | $\Theta(m \log n + occ)$ |
| Longest repeated substring | $\max(\text{LCP})$ | $\Theta(n)$ after construction |
| All repeats of length $\ge L$ | runs where $\text{LCP} \ge L$ | $\Theta(n)$ |
| Longest common substring of two texts | concatenate with separators, scan LCP | $\Theta(n)$ |

@tbl: What a suffix array answers. Adding an LCP-interval tree brings pattern search down to $\Theta(m + \log n)$, and an FM-index compresses the whole structure to near the entropy of the text.

## Contamination and memorisation

This is the application that matters for ML, and it is a direct use of the
table above.

:::ml Detecting benchmark contamination at corpus scale
The question: does any test-set example appear verbatim in the training
corpus? At $10^{12}$ tokens of training text and $10^5$ test examples, you
cannot run $10^5$ separate searches.

The standard pipeline:

1. **Concatenate** the training corpus with a unique separator byte and build
   a suffix array over it. For 1 TB with 40-bit indices this is about 5 TB on
   disk --- built in shards and merged.
2. For each test example, **binary search** the suffix array for every
   50-token window. Any hit is a candidate contamination.
3. **Verify and measure**: report the fraction of each test example covered
   by matches of length $\ge L$ (typically 50 tokens).

The cheaper approximation that most pipelines actually run first: build a
Bloom filter (Chapter 28) or a hash set of all $n$-gram hashes of the test
sets, stream the training corpus past it, and exact-check the hits. That is
one pass, no index, and it answers the same question for a fixed $n$.
:::

:::ml Measuring memorisation
The same structure answers "how much of the training data can the model
reproduce?" Prompt the model with the first $k$ tokens of a training
document, sample a continuation, and check whether the continuation appears
in the corpus by substring search. The fraction of prompts for which a
50-token verbatim match occurs is the standard extractable-memorisation
metric.

A related corpus-only question --- *how much of the corpus is exactly
duplicated?* --- is answered by scanning the LCP array for runs of long
common prefixes, which is what the "deduplicating training data makes
language models better" line of work does. Note that this is an *exact*
substring method and is complementary to the *approximate* similarity of
Chapter 29: LSH finds documents that are 85% similar, suffix structures find
the 50-token spans they share.
:::

## Suffix automata and the alternatives

A **suffix automaton** (DAWG) is the minimal deterministic automaton
recognising all suffixes of $S$. It has at most $2n - 1$ states and $3n - 4$
transitions, is built online in $\Theta(n)$, and answers "is $P$ a substring?"
in $\Theta(m)$ with no binary search --- but it is a pointer structure with
poor locality, so at corpus scale suffix arrays usually win despite the
$\log$ factor.

| Structure | Build | Query | Memory | Notes |
|---|---|---|---|---|
| Suffix array | $\Theta(n)$ (SA-IS) | $\Theta(m \log n)$ | $4$--$5n$ bytes | the practical default |
| SA + LCP interval tree | $\Theta(n)$ | $\Theta(m)$ | $\approx 9n$ bytes | when query time dominates |
| Suffix tree | $\Theta(n)$ | $\Theta(m)$ | $20$--$40n$ bytes | rarely worth the memory |
| Suffix automaton | $\Theta(n)$ | $\Theta(m)$ | $\approx 10n$ bytes | online construction |
| FM-index (BWT) | $\Theta(n)$ | $\Theta(m)$ | $\approx n H_k$ bytes | compressed; genomics standard |
| $n$-gram hash index | $\Theta(n)$ | $\Theta(1)$ | $\Theta(n)$ | only for fixed $n$ |

@tbl: Substring index structures. For a fixed $n$-gram length, a hash index is simpler and faster; suffix structures earn their keep when the query length is not known in advance.

:::pitfall Tokens or bytes?
Contamination measured over *characters* and over *tokens* give different
answers, and neither is obviously right. Character-level matching catches
paraphrase-free copies with different tokenisation; token-level matching
aligns with what the model actually saw. Report which you used --- published
contamination numbers are not comparable without it. Normalise first
(Chapter 5), or trivial whitespace differences will hide real matches.
:::

:::exercise
1. Implement KMP and verify the failure function on "ababcabab". Explain what
   `fail[7]` means in terms of the string.
2. Build the suffix array for a 1 MB text by prefix doubling and by
   `sorted(range(n), key=lambda i: s[i:])`. Explain the memory blow-up of the
   second and measure it.
3. Implement Kasai's algorithm and prove the amortised bound.
4. Use the LCP array to find the longest repeated substring of a book-length
   text, and all repeats of length $\ge 100$.
5. Find the longest common substring of two documents by concatenating them
   with a separator and scanning the LCP array with a bitmask of which
   document each suffix came from.
6. Build an $n$-gram hash index for $n = 13$ over 100 MB of text and use it
   to find all test-set windows present in it. Compare its memory and query
   time to a suffix array.
7. Implement the contamination pipeline end-to-end on a small corpus with
   deliberately injected test examples, and report the coverage metric.
8. Estimate the disk, memory and wall-clock cost of building a suffix array
   over 1 TB of tokenised text, given a machine with 256 GB of RAM.
:::

:::recap
- KMP scans in $\Theta(n+m)$ without backtracking; its failure function is
  the same "reuse what you already matched" idea as Aho--Corasick.
- A suffix array sorts all suffixes, so every occurrence of a pattern is a
  contiguous block found by two binary searches: $\Theta(m \log n)$.
- Kasai's algorithm builds the LCP array in linear time, and the LCP array
  gives longest repeats, all long repeats, and longest common substrings.
- Contamination detection and memorisation measurement are substring-search
  problems; a Bloom filter over fixed-length $n$-grams is the cheap first
  pass, a suffix array the general one.
- Suffix arrays beat suffix trees and automata in practice on memory and
  locality; FM-indexes compress to near text entropy.
- Exact substring methods (this chapter) and approximate similarity
  (Chapter 29) answer different questions; a full pipeline uses both.
:::
