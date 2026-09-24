# Tries, Automata and the Anatomy of a Tokenizer
@short: Tries and Automata
@subtitle: Structures indexed by strings rather than by hashes of strings
@tier: core
@prereq: Chapters 5, 7
@blurb: A hash table can tell you whether a string is in a set. It cannot tell you which strings start with a prefix, which of them is the longest match at this position, or where in a document any of a million patterns occur. Those questions need a structure that indexes the string itself, and the answer is a trie --- which, with one addition, becomes an automaton that scans text without ever backtracking.
@objectives:
- Implement a trie with insert, search, prefix enumeration and longest-match
- Compare tries with hash tables and know exactly which queries each supports
- Build an Aho--Corasick automaton and use it for multi-pattern search
- Understand compressed tries (radix trees) and their memory behaviour
- Implement a working BPE tokenizer with the right data structures
- See how radix trees index prefix caches in LLM serving

## The trie

:::definition Trie (prefix tree)
A rooted tree in which each edge is labelled with a symbol, so each node
corresponds to the string spelled by the path from the root. A node is
*terminal* if that string is a member of the stored set. Lookup, insertion
and deletion all cost $\Theta(|\text{key}|)$, independent of how many keys
the trie holds.
:::

@fig: trie_structure | 118 | A trie over {cat, cats, dog, dogs}. Shared prefixes are stored once, and every operation's cost depends on the length of the query, not on the size of the set.

```python title="A trie with the four operations that matter"
class Trie:
    __slots__ = ("children", "terminal", "value")

    def __init__(self):
        self.children = {}
        self.terminal = False
        self.value = None

    def insert(self, word, value=None):          # theta(|word|)
        node = self
        for ch in word:
            node = node.children.setdefault(ch, Trie())
        node.terminal, node.value = True, value

    def _walk(self, prefix):
        node = self
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def __contains__(self, word):                # theta(|word|)
        node = self._walk(word)
        return node is not None and node.terminal

    def with_prefix(self, prefix):               # theta(|prefix| + output)
        """Every stored word beginning with prefix, in lexicographic order."""
        node = self._walk(prefix)
        out = []
        if node is None:
            return out
        stack = [(node, prefix)]
        while stack:
            n, s = stack.pop()
            if n.terminal:
                out.append(s)
            for ch in sorted(n.children, reverse=True):
                stack.append((n.children[ch], s + ch))
        return out

    def longest_prefix_of(self, s, start=0):     # theta(|s| - start)
        """Longest stored word that is a prefix of s[start:], or None."""
        node, best, i = self, None, start
        while i < len(s):
            node = node.children.get(s[i])
            if node is None:
                break
            i += 1
            if node.terminal:
                best = (i, node.value)
        return best
```

`longest_prefix_of` is the operation that justifies the whole structure. It
is how a WordPiece tokenizer segments a word, how an IP router matches the
longest routing prefix, and how a dictionary-based segmenter handles Chinese
and Japanese --- and no hash table can do it without trying every prefix
length separately.

| Query | Hash set | Trie |
|---|---|---|
| Is `w` present? | $\Theta(\|w\|)$ to hash | $\Theta(\|w\|)$ |
| All words with prefix `p` | $\Theta(n)$ scan | $\Theta(\|p\| + \text{output})$ |
| Longest stored prefix of `s` | $\Theta(\|s\|^2)$ | $\Theta(\|s\|)$ |
| Lexicographic iteration | $\Theta(n \log n)$ | $\Theta(\text{total length})$ |
| Fuzzy match within edit distance 1 | $\Theta(n)$ | $\Theta(\|w\| \cdot \|\Sigma\|)$ |
| Memory | keys stored whole | prefixes shared, nodes have overhead |

@tbl: Tries versus hash sets. A trie loses on plain membership and wins on every query that mentions a prefix.

:::pitfall Trie memory in Python
A naive Python trie over a 200,000-word vocabulary can use hundreds of
megabytes: every node is a `dict` (over 200 bytes) plus the `Trie` object.
Three fixes, each roughly an order of magnitude: use `__slots__` and a plain
dict (as above); compress single-child chains into a radix tree; or use a
double-array trie or an LOUDS-encoded succinct trie, which store the whole
structure in two flat integer arrays and query it with bit operations.
Production tokenizers use the last option.
:::

## Compressed tries (radix trees)

A trie over long, sparse keys has many chains of single-child nodes. A
**radix tree** (or Patricia trie) collapses each such chain into one edge
labelled with a whole substring. The result has at most $2k - 1$ nodes for
$k$ keys regardless of key length, which for URLs, file paths or token
sequences is a huge saving.

Radix trees are what implement IP routing tables, the Linux kernel's page
cache index, and --- the reason they appear in this book --- the prefix cache
of an LLM server.

:::ml RadixAttention: a radix tree over KV caches
In a chat service most requests share a long system prompt, and many share a
conversation prefix. Recomputing the KV cache for a shared prefix is pure
waste. SGLang's RadixAttention keeps a radix tree whose edges are token
sequences and whose nodes point at the cached KV blocks for that prefix.

- A new request walks the tree to find its longest cached prefix, then
  computes only the remaining suffix.
- Eviction is LRU *over the tree*: only leaves may be evicted, because an
  internal node's blocks are shared by its descendants.
- The hit rate on real chat traffic is 50--90%, and since prefill is
  compute-bound and proportional to prefix length, this translates almost
  directly into throughput.

The data structure is exactly the radix tree above, with token ids instead
of characters and reference counts on nodes. Chapter 36 returns to it.
:::

## Aho--Corasick: searching for everything at once

Suppose you must find every occurrence of any of 50,000 patterns in a
document --- a profanity list, a PII detector, a set of blocked domains, a
gazetteer of entity names. Running 50,000 separate searches is
$\Theta(50000 \cdot n)$. Aho--Corasick does it in one pass.

@fig: aho_corasick | 128 | An Aho--Corasick automaton. The black edges are the trie of the patterns; the red failure links jump to the longest proper suffix that is still a prefix of some pattern, so the text pointer never moves backwards.

```python title="Aho-Corasick: build and scan"
from collections import deque

class AhoCorasick:
    def __init__(self, patterns):
        self.next = [{}]          # next[state][char] -> state
        self.fail = [0]
        self.out = [[]]           # patterns ending at this state
        for p in patterns:
            self._add(p)
        self._build_links()

    def _add(self, p):
        s = 0
        for ch in p:
            if ch not in self.next[s]:
                self.next.append({}); self.fail.append(0); self.out.append([])
                self.next[s][ch] = len(self.next) - 1
            s = self.next[s][ch]
        self.out[s].append(p)

    def _build_links(self):
        q = deque()
        for ch, s in self.next[0].items():
            self.fail[s] = 0
            q.append(s)
        while q:
            s = q.popleft()
            for ch, t in self.next[s].items():
                q.append(t)
                f = self.fail[s]
                while f and ch not in self.next[f]:
                    f = self.fail[f]
                self.fail[t] = self.next[f].get(ch, 0) if f or ch in self.next[0] else 0
                self.out[t] += self.out[self.fail[t]]      # inherit suffix hits

    def find(self, text):
        s = 0
        for i, ch in enumerate(text):
            while s and ch not in self.next[s]:
                s = self.fail[s]                            # follow failure links
            s = self.next[s].get(ch, 0)
            for p in self.out[s]:
                yield i - len(p) + 1, p
```

Total cost: $\Theta(\sum |p_i|)$ to build and $\Theta(|T| + \text{matches})$
to scan --- independent of the number of patterns. The amortised argument is
the same shape as the sliding window in Chapter 11: the state depth
increases by at most one per character and each failure step decreases it, so
the total number of failure steps is bounded by the text length.

:::insight The general principle behind failure links
The knowledge you gained from a partial match is not wasted when the match
breaks; it tells you exactly how far you may skip. That is the idea in
Knuth--Morris--Pratt (one pattern), Aho--Corasick (many patterns), and the
Z-algorithm. Whenever an algorithm restarts from scratch after a mismatch,
ask what it already knows.
:::

## Building a tokenizer, properly

Chapter 5 described what a tokenizer does. Here is what it is *made of*.

**Training BPE.** Maintain (a) a max-heap of candidate pairs keyed by count
and (b) an index from each pair to the word positions where it occurs. Pop
the best pair; merge it everywhere it occurs; for each affected position,
decrement the counts of the two pairs that were destroyed and increment the
two that were created, pushing the updated entries onto the heap. Old heap
entries are stale, so check the current count on pop and discard mismatches:
lazy deletion again.

```python title="The core loop of BPE training"
import heapq
from collections import defaultdict

def train_bpe(word_freqs, num_merges):
    """word_freqs: {tuple_of_symbols: frequency}"""
    pair_counts = defaultdict(int)
    for word, f in word_freqs.items():
        for a, b in zip(word, word[1:]):
            pair_counts[(a, b)] += f

    heap = [(-c, p) for p, c in pair_counts.items()]
    heapq.heapify(heap)                                   # theta(n)
    merges = []
    while heap and len(merges) < num_merges:
        negc, pair = heapq.heappop(heap)
        if -negc != pair_counts.get(pair, 0):
            continue                                       # stale: skip
        merges.append(pair)
        new_sym = pair[0] + pair[1]
        updated = {}
        for word, f in word_freqs.items():
            if pair[0] not in word:
                continue
            out, i = [], 0
            while i < len(word):
                if (i + 1 < len(word) and word[i] == pair[0]
                        and word[i + 1] == pair[1]):
                    out.append(new_sym); i += 2
                else:
                    out.append(word[i]); i += 1
            new_word = tuple(out)
            if new_word != word:
                updated[word] = (new_word, f)
        for old, (new, f) in updated.items():             # incremental counts
            for a, b in zip(old, old[1:]):
                pair_counts[(a, b)] -= f
            for a, b in zip(new, new[1:]):
                pair_counts[(a, b)] += f
                heapq.heappush(heap, (-pair_counts[(a, b)], (a, b)))
            del word_freqs[old]
            word_freqs[new] = word_freqs.get(new, 0) + f
    return merges
```

This is still simplified --- a production implementation keeps a position
index so it does not scan every word --- but it has the right shape: a heap
for the argmax, incremental count updates, and lazy deletion for staleness.
The naive alternative recomputes all pair counts after every merge and is
$\Theta(V \cdot N)$ instead of roughly $\Theta(N + V \log V)$.

**Encoding.** WordPiece uses `longest_prefix_of` against a trie. BPE applies
merges in rank order, which is best done with a linked list of symbols plus a
heap of candidate merge positions: $\Theta(m \log m)$ per word instead of the
naive $\Theta(m^2)$. Unigram/SentencePiece runs Viterbi over a lattice
(Chapter 19).

:::ml Constrained decoding is a trie walk
When you require a model's output to be valid JSON, to match a regex, or to
name one of 100,000 allowed entities, you compile the constraint into a
finite automaton --- often literally a trie of allowed continuations --- and
at each decoding step mask the logits of tokens that would leave the
automaton's valid transitions. The mask is precomputed per state, so the
runtime cost is one lookup and one masked softmax per token. This is how
`outlines`, `guidance` and `llama.cpp`'s grammar sampler work, and the data
structure is the one in this chapter.
:::

:::exercise
1. `with_prefix` sorts each node's children on every visit. Replace the
   explicit stack with a recursive generator that yields lazily, and state
   the complexity of taking only the first ten results.
2. Implement a radix tree (compressing single-child chains) and measure the
   node count and memory against a plain trie for 100,000 URLs.
3. Implement fuzzy search over a trie: all words within edit distance 1 of a
   query, in $\Theta(|w| \cdot |\Sigma|)$ per candidate. (Hint: carry a
   dynamic-programming row down the trie --- this previews Chapter 19.)
4. Build an Aho--Corasick automaton over 10,000 patterns and scan a 100 MB
   document. Compare to running `str.find` per pattern.
5. Explain why `out[t] += out[fail[t]]` is necessary, and give a pattern set
   and text where omitting it loses a match.
6. Implement BPE encoding with a linked list plus a heap and compare to the
   naive repeated-scan version on 100,000 words.
7. Design the radix tree for a prefix cache: nodes hold token spans and
   reference counts, eviction is LRU over leaves only. What invariant must
   hold before a node can be evicted, and how do you maintain it?
:::

:::recap
- A trie indexes strings by their content, so cost depends on key length,
  not on set size, and prefix queries become natural.
- Tries beat hash sets on prefix enumeration, longest-prefix match,
  lexicographic iteration and fuzzy matching; hash sets win on plain
  membership and memory.
- Naive Python tries are memory-hungry; radix compression and succinct
  encodings are the production answers.
- Aho--Corasick adds failure links to a trie, giving
  $\Theta(|T| + \text{matches})$ multi-pattern search with no backtracking.
- BPE training is a max-heap of pair counts with incremental updates and
  lazy deletion; WordPiece encoding is a trie longest-match; Unigram is
  Viterbi over a lattice.
- Radix trees index prefix caches in LLM serving, and tries drive
  constrained decoding by masking invalid continuations.
:::
