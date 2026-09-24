# Strings, Bytes and Tokens
@short: Strings and Tokens
@subtitle: The data structure between your text and your model
@tier: foundation
@prereq: Chapter 4
@blurb: Text is the input to most modern models, and it is the one data type where almost everyone carries a wrong mental model. A string is not a list of characters; a character is not a byte; and the token your model consumes is a third thing again. This chapter fixes the model, then covers the string algorithms that actually appear in data pipelines.
@objectives:
- Distinguish bytes, code points, grapheme clusters and tokens, and know which one your code means
- Predict the cost of common string operations, including the quadratic traps
- Implement efficient string building, searching and normalisation
- Understand what a tokenizer is doing and why its data structures matter
- Build a rolling hash and use it for substring search and chunking

## Four different things called "length"

@fig: utf8_layout | 135 | The same text measured four ways. Nearly every text-processing bug comes from an algorithm that assumes two of these units are the same.

- A **byte** is 8 bits. UTF-8 encodes ASCII in one byte, most European and
  Middle Eastern scripts in two, most CJK in three, and emoji in four.
- A **code point** is a Unicode scalar value, `U+0041` to `U+10FFFF`. Python 3
  strings are sequences of code points, so `len("café") == 4`.
- A **grapheme cluster** is what a reader calls a character. `"é"` may be one
  code point (`U+00E9`) or two (`e` + combining acute `U+0301`); a family
  emoji is five code points joined by zero-width joiners but one glyph.
- A **token** is whatever your tokenizer emits: typically a subword of one
  to six characters, drawn from a vocabulary of 30,000 to 300,000 entries.

:::pitfall The truncation bug
`text[:512]` truncates to 512 *code points*, which may be 512 tokens, or 150,
or 2000, depending on the language. Truncating to a byte limit can split a
multi-byte sequence and produce invalid UTF-8. Truncating a grapheme cluster
separates a base character from its combining mark. If you need "512 tokens",
truncate the token ids, not the string --- and if you must truncate bytes,
back off to a code-point boundary (a byte whose top bits are not `10`).
:::

:::ml Why the unit mismatch costs money
Context windows, pricing and positional encodings are all counted in tokens.
English averages about 4 characters per token; code averages about 3;
Hindi, Thai and Japanese often exceed 1 token per character under a
predominantly English BPE vocabulary. A "4000-character" document can be
1000 tokens or 4000 depending on language, which changes both cost and
whether it fits. Always measure with the actual tokenizer.
:::

## The cost of string operations

Python strings are immutable, contiguous arrays of fixed-width code units
(1, 2 or 4 bytes per code point depending on the largest one present). Two
consequences dominate.

| Operation | Cost | Note |
|---|---|---|
| `len(s)`, `s[i]` | $\Theta(1)$ | fixed-width representation |
| `s + t` | $\Theta(\|s\| + \|t\|)$ | allocates a new string |
| `s += t` in a loop | $\Theta(n^2)$ total | the classic trap |
| `"".join(parts)` | $\Theta(\text{total})$ | one allocation, always use this |
| `s.find(t)` | $\Theta(nm)$ worst, near $\Theta(n)$ typical | CPython uses a Boyer-Moore-Horspool/two-way hybrid |
| `s.split(sep)` | $\Theta(n)$ | allocates one object per piece |
| `s.replace(a, b)` | $\Theta(n)$ | single pass |
| `re` match | depends | backtracking engines can be exponential |
| `s.encode("utf-8")` | $\Theta(n)$ | allocates |
| `hash(s)` | $\Theta(n)$ first time | cached on the object afterwards |

@tbl: Cost of Python string operations. Rows three and four are the difference between a pipeline that finishes and one that does not.

```python title="Building a large string: three ways"
# theta(n^2): each += copies everything built so far
out = ""
for piece in pieces:
    out += piece

# theta(n): one allocation at the end.  Always this.
out = "".join(pieces)

# theta(n) and streaming: when the result is too big to hold
import io
buf = io.StringIO()
for piece in pieces:
    buf.write(piece)
out = buf.getvalue()
```

:::warning Catastrophic backtracking
A regular expression like `(a+)+b` against a string of 30 `a`s takes
exponential time in a backtracking engine, which includes Python's `re`.
This is a real denial-of-service vector when patterns touch user text.
Fixes: avoid nested quantifiers, use possessive/atomic groups via the
`regex` module, or switch to `re2`-style automaton matching, which is
$\Theta(nm)$ worst case with no backtracking. Chapter 14 explains the
automaton.
:::

## Rolling hashes: fingerprinting a window in $\Theta(1)$

A surprising amount of text infrastructure rests on one idea: maintain a
hash of a sliding window so that moving the window by one character costs
constant time.

Treat the window as a number in base $B$ modulo a large prime $M$:

$$H(s_i \ldots s_{i+m-1}) = \sum_{j=0}^{m-1} s_{i+j} \cdot B^{m-1-j} \bmod M$$

Sliding one step removes the leading term and appends a new one:

$$H' = \left( (H - s_i \cdot B^{m-1}) \cdot B + s_{i+m} \right) \bmod M$$

```python title="Rabin-Karp: substring search in expected linear time"
def rabin_karp(text: str, pat: str, B: int = 257, M: int = (1 << 61) - 1):
    n, m = len(text), len(pat)
    if m == 0 or m > n:
        return []
    high = pow(B, m - 1, M)
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(pat[i])) % M
        ht = (ht * B + ord(text[i])) % M
    hits = []
    for i in range(n - m + 1):
        if hp == ht and text[i:i + m] == pat:     # verify: hashes can collide
            hits.append(i)
        if i + m < n:
            ht = ((ht - ord(text[i]) * high) * B + ord(text[i + m])) % M
    return hits
```

Expected $\Theta(n + m)$; worst case $\Theta(nm)$ if an adversary forces
collisions, which is why $M$ should be large and, in adversarial settings,
randomly chosen per process.

:::ml Three places rolling hashes appear in ML pipelines
**Content-defined chunking.** To split documents into chunks that stay
stable when the document is edited, cut wherever the rolling hash of the last
48 bytes has $k$ low zero bits. An insertion near the start no longer shifts
every downstream boundary, so deduplication and incremental re-embedding both
keep working. This is how `rsync`, `restic` and most vector-store ingestion
pipelines chunk.

**Exact deduplication and contamination checks.** Hash every 50-token window
of every document; any test-set window appearing in training data is
contamination. Chapter 30 does this at corpus scale.

**The hashing trick.** Map an unbounded feature space to $m$ buckets with
`hash(feature) % m`, avoiding a vocabulary entirely. Collisions act as
weight sharing and are usually harmless; add a sign hash to keep the
inner-product estimate unbiased. Chapter 7.
:::

## What a tokenizer actually is

A tokenizer is two algorithms wearing a trench coat: a training procedure
that builds a vocabulary, and an encoding procedure that applies it.

@fig: bpe_merge | 125 | Byte-pair encoding training. Repeatedly find the most frequent adjacent pair across the corpus and merge it into a new symbol. The vocabulary is the ordered list of merges.

**Training (BPE).** Start with every byte as a symbol. Count all adjacent
pairs across the corpus; merge the most frequent into a new symbol; repeat
until the vocabulary reaches the target size. The naive implementation
recounts every pair after each merge: $\Theta(V \cdot N)$, which is days on a
large corpus. The real implementation keeps a priority queue of pair counts
and an index from each pair to the positions where it occurs, so a merge only
updates the pairs adjacent to the merged positions --- roughly
$\Theta(N + V \log V)$. Chapter 13 builds the queue and Chapter 14 the index.

**Encoding.** Given the merge list, apply merges to a word in rank order.
The straightforward implementation is $\Theta(m^2)$ per word for a word of
$m$ characters; using a linked list of symbols plus a heap of candidate
merges makes it $\Theta(m \log m)$. WordPiece instead does greedy
longest-match against a trie, which is $\Theta(m)$ amortised. Unigram
(SentencePiece) runs Viterbi over a lattice to find the highest-probability
segmentation --- a dynamic program, Chapter 19.

```python title="Greedy longest-match encoding against a trie"
class TrieNode:
    __slots__ = ("children", "token_id")
    def __init__(self):
        self.children = {}
        self.token_id = None

def build(vocab):                       # vocab: token string -> id
    root = TrieNode()
    for tok, tid in vocab.items():
        node = root
        for ch in tok:
            node = node.children.setdefault(ch, TrieNode())
        node.token_id = tid
    return root

def encode(root, text, unk):
    out, i, n = [], 0, len(text)
    while i < n:
        node, j, best = root, i, None
        while j < n and text[j] in node.children:
            node = node.children[text[j]]
            j += 1
            if node.token_id is not None:
                best = (node.token_id, j)   # remember the longest match
        if best is None:
            out.append(unk)
            i += 1
        else:
            out.append(best[0])
            i = best[1]
    return out
```

This is $\Theta(\text{total matched length})$ and is exactly what WordPiece
does after its `##` continuation handling. Chapter 14 extends the trie to an
Aho--Corasick automaton, which finds *all* occurrences of *all* vocabulary
entries in one pass --- the basis of profanity filters, PII scrubbers and
constrained decoding.

:::pitfall Tokenizers are not reversible in the way you expect
`decode(encode(s))` may not equal `s`: normalisation (NFKC, lowercasing,
whitespace collapsing) is lossy, and byte-level BPE round-trips bytes but not
necessarily the original Unicode normalisation form. If you are computing
character-level spans --- for extractive QA, for highlighting, for
alignment --- you must carry an explicit offset mapping from tokens back to
byte ranges. Every serious tokenizer library exposes one; use it rather than
re-searching the string.
:::

## Normalisation, the unglamorous prerequisite

Before any of this, text needs normalising, and the choices are consequential.

- **Unicode normalisation.** NFC composes `e` + `́` into `é`; NFD decomposes.
  NFKC additionally folds compatibility characters --- full-width Latin,
  ligatures, superscripts. Pick one and apply it everywhere, including at
  query time in a retrieval system, or identical-looking strings will fail to
  match.
- **Case folding.** `str.lower()` is not the same as `str.casefold()`
  (which handles German `ß` to `ss`), and neither is safe for Turkish
  dotted/dotless `i` without locale awareness.
- **Whitespace and control characters.** Zero-width spaces, non-breaking
  spaces, and bidirectional control characters are invisible and will
  silently split your tokens. Strip the `Cf` category unless you have a
  reason not to.
- **Homoglyphs.** Cyrillic `а` and Latin `a` are different code points that
  render identically; this matters for deduplication, and for anyone trying
  to slip past a filter.

:::insight Normalise once, at the boundary
The rule that prevents most text bugs: normalise on ingestion, store the
normalised form, and never normalise again. Systems that normalise lazily in
several places end up with different normalisations in the index and in the
query path, which produces silent recall loss that no test catches.
:::

:::exercise
1. Write a function that truncates a UTF-8 byte string to at most $k$ bytes
   without splitting a code point. Test it on text containing emoji.
2. Measure characters-per-token for the same paragraph translated into
   English, German, Hindi and Japanese using any BPE tokenizer. Explain the
   spread.
3. Implement content-defined chunking with a 48-byte rolling hash and a
   13-bit boundary condition. Show that inserting a character at the start of
   a document changes only the first chunk.
4. Build the greedy trie encoder above for a 5,000-entry vocabulary and
   compare its throughput to a regex-based tokenizer.
5. Construct a regex and an input for which Python's `re` takes more than ten
   seconds on a 40-character string. Then rewrite the regex so it does not.
6. Given a token sequence and an offset mapping, write a function that maps a
   character span to the minimal covering token span. This is the core of
   extractive QA evaluation.
:::

:::recap
- Bytes, code points, grapheme clusters and tokens are four different units;
  almost every text bug is a confusion between two of them.
- Python strings are immutable: `+=` in a loop is $\Theta(n^2)$, `join` is
  $\Theta(n)$. Regex backtracking can be exponential.
- A rolling hash makes a sliding-window fingerprint $\Theta(1)$ per step, and
  underpins substring search, content-defined chunking, deduplication and the
  hashing trick.
- A tokenizer is a training algorithm (priority queue plus position index for
  BPE; Viterbi for Unigram) and an encoding algorithm (trie longest-match, or
  ranked merges).
- Carry an explicit offset mapping if you need character spans; do not
  re-search the string.
- Normalise once, on ingestion, and use the same normalisation in the index
  and the query path.
:::
