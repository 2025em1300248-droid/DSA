# Retrieval: From BM25 to Hybrid Search
@short: Retrieval
@subtitle: Finding the right passages, which is the hard half of RAG
@tier: core
@prereq: Chapter 29
@blurb: Most RAG systems fail at retrieval, not at generation, and the usual cause is that the whole pipeline was built on dense vectors alone. This chapter covers the retrieval stack properly --- lexical search, embeddings, hybrid fusion, reranking, and the index structures underneath --- and how to measure each stage separately.
@objectives:
- Explain BM25 and why lexical search still beats embeddings on some queries
- Choose and evaluate an embedding model for your domain
- Fuse lexical and dense results correctly
- Add a reranker and know what it buys
- Pick an index (flat, IVF, HNSW) from the size and recall you need

## BM25: the baseline that is hard to beat

```python title="BM25, implemented"
import math
from collections import Counter

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [d.lower().split() for d in docs]
        self.k1, self.b = k1, b
        self.lens = [len(d) for d in self.docs]
        self.avg_len = sum(self.lens) / len(self.lens)
        self.tf = [Counter(d) for d in self.docs]
        df = Counter(t for d in self.docs for t in set(d))
        N = len(self.docs)
        self.idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5))
                    for t, n in df.items()}

    def score(self, query, i):
        s = 0.0
        for term in query.lower().split():
            f = self.tf[i].get(term, 0)
            if not f:
                continue
            norm = 1 - self.b + self.b * self.lens[i] / self.avg_len
            s += self.idf[term] * f * (self.k1 + 1) / (f + self.k1 * norm)
        return s

    def search(self, query, k=10):
        scores = [(self.score(query, i), i) for i in range(len(self.docs))]
        return sorted(scores, reverse=True)[:k]
```

Three ideas are in that formula. **IDF** weights rare terms more. **Term
frequency saturation** --- the $f/(f+k_1)$ shape --- means the tenth
occurrence of a word adds much less than the second, which stops long
keyword-stuffed documents from dominating. **Length normalisation**, the $b$
term, prevents long documents from winning simply by containing more words.

:::insight Why you cannot skip lexical search
Embeddings are good at meaning and bad at exact strings. BM25 is the reverse.
For these queries BM25 wins outright, and the gap does not close with a better
embedding model:

- Product codes, SKUs, error codes: `ERR_CONN_4042`
- Names and rare proper nouns not in the embedding's training data
- Version numbers, dates, identifiers: `v2.14.3`
- Quoted phrases where exactness matters
- Any term coined after the embedding model was trained

A dense-only retriever fails these silently --- it returns plausible-looking,
semantically related, wrong passages. That failure is invisible unless you
measure retrieval separately from generation.
:::

## Embeddings

```python title="Choosing and using an embedding model"
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Many models are trained with asymmetric prefixes. Using the wrong one,
# or omitting them, measurably degrades retrieval.
q_emb = model.encode(["what is the refund window?"],
                     prompt="Represent this sentence for searching relevant passages: ",
                     normalize_embeddings=True)
d_emb = model.encode(passages, normalize_embeddings=True, batch_size=256)

scores = d_emb @ q_emb.T            # normalised, so dot product = cosine
```

| Consideration | Guidance |
|---|---|
| Dimension | 384--1024 is the useful range; larger costs memory for small gains |
| Max sequence | must exceed your chunk size, or chunks are silently truncated |
| Domain | general models underperform on legal, medical, code --- test on your data |
| Multilingual | use a multilingual model if any query or document is not English |
| Matryoshka models | one model, truncatable dimensions --- cheap way to trade recall for memory |
| Instruction prefixes | required by many models; check the model card |

@tbl: Choosing an embedding model. The only reliable method is to evaluate candidates on *your* queries and *your* corpus; public leaderboard order frequently inverts on a specific domain.

:::pitfall Chunking decides your ceiling
Retrieval can only return what chunking produced. The common failures:

- **Chunks too small** (under ~200 tokens): each lacks the context to be
  understood alone, and the generator cannot assemble the answer.
- **Chunks too large** (over ~1500 tokens): one embedding must represent too
  many ideas, so it matches nothing well.
- **Split mid-sentence or mid-table**: the chunk is unusable.
- **No overlap**: an answer straddling a boundary is in neither chunk.
- **No context**: a chunk saying "it costs £40" with no indication of what
  "it" is cannot be retrieved by a query naming the product.

The last is the one with the best fix: prepend a short, model-generated
description of where the chunk sits in its document ("From the *Returns
Policy* section of the 2026 Customer Handbook, discussing restocking fees:")
before embedding it. This *contextual retrieval* step reliably produces a
large recall improvement for a one-off indexing cost.
:::

```python title="Chunking that preserves structure"
def chunk(doc_text, target=800, overlap=120):
    """Split on the largest structural boundary that fits."""
    sections = split_on_headings(doc_text)
    out = []
    for section in sections:
        paras = section.split("\n\n")
        buf = []
        for p in paras:
            if toklen(" ".join(buf + [p])) > target and buf:
                out.append(" ".join(buf))
                buf = buf[-1:] if overlap else []      # carry a tail
            buf.append(p)
        if buf:
            out.append(" ".join(buf))
    return out
```

## Hybrid: fusing lexical and dense

@fig: hybrid_retrieval | 160 | The retrieval stack. Two retrievers with complementary failure modes are fused, then a cross-encoder reranks a shortlist. Each stage narrows the candidate set and increases precision at increasing cost per document.

```python title="Reciprocal rank fusion — rank-based, so no score calibration needed"
def rrf(result_lists, k=60, top_n=50):
    """result_lists: [[doc_id ranked best-first], ...]"""
    scores = {}
    for results in result_lists:
        for rank, doc_id in enumerate(results, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)[:top_n]

candidates = rrf([bm25.search(q, 100), dense.search(q, 100)])
```

RRF fuses on *rank* rather than score, which matters because BM25 scores are
unbounded and cosine similarities live in $[-1, 1]$ --- combining them
linearly requires calibration that drifts. RRF needs none, has one parameter,
and is hard to beat.

## Reranking

A **bi-encoder** (the embedding model) encodes query and document separately,
so documents can be indexed ahead of time --- fast, but the query never sees
the document. A **cross-encoder** reads query and document *together* and
scores the pair --- far more accurate, and far too slow to run over a whole
corpus.

So: retrieve 50--100 candidates cheaply, rerank them with a cross-encoder,
keep the top 5--10.

```python title="Adding a reranker"
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

pairs = [(query, doc_text[c]) for c in candidates]
scores = reranker.predict(pairs)
final = [c for _, c in sorted(zip(scores, candidates), reverse=True)[:8]]
```

| Stage | Candidates | Latency | Typical recall@k |
|---|---|---|---|
| Dense only | 10 | 20 ms | 0.61 |
| + BM25 hybrid (RRF) | 10 | 45 ms | 0.78 |
| + cross-encoder rerank | 10 from 100 | 180 ms | 0.89 |
| + contextual chunk descriptions | 10 from 100 | 180 ms | 0.94 |

@tbl: Illustrative stage-by-stage gains on a technical-documentation corpus. The shape is consistent across domains even though the absolute numbers are not: hybrid is the single largest step, reranking is next, and contextual chunking is nearly free at query time.

## Index structures

| Index | Recall | Build | Query | Memory | Use when |
|---|---|---|---|---|---|
| Flat (exact) | 1.00 | none | $O(n)$ | $4nd$ bytes | under ~100k vectors |
| IVF | 0.90--0.99 | minutes | $O(n/\sqrt{\text{lists}})$ | $4nd$ | 100k--10M |
| IVF + PQ | 0.80--0.95 | minutes | fast | $n \times m$ bytes | memory-constrained |
| HNSW | 0.95--0.999 | slow | $O(\log n)$ | $4nd + $ graph | the default above 100k |
| DiskANN | 0.90--0.98 | very slow | SSD-bound | small RAM | billions of vectors |

@tbl: Index choice. Below about 100,000 vectors, exact search over a NumPy matrix takes a few milliseconds and beats every approximate index on both recall and operational complexity --- do not add a vector database until you need one.

:::warning Measure retrieval separately from generation
The single most common mistake in RAG work is evaluating only the final
answer. When the answer is wrong you cannot tell whether retrieval missed the
passage or the generator ignored it, so you tune the wrong half.

Build a labelled set of (query, relevant passage ids) and report **recall@k**
for retrieval and answer quality for generation, separately, on every change.
Chapter 34 builds the full harness.
:::

:::practice The task
On a corpus of at least 5000 documents with 100 labelled queries:
(a) implement BM25 and measure recall@10; (b) add dense retrieval and measure;
(c) fuse with RRF and measure; (d) add a cross-encoder reranker over 100
candidates and measure, including latency; (e) add model-generated contextual
descriptions to each chunk, re-index, and measure again. Report the four
numbers and the latency at each stage, and find ten queries where BM25 beats
dense and ten where the reverse holds.

**You have this skill when** you can state your system's recall@10 and name
the query types each retriever fails on.
:::

:::exercise
1. Implement BM25 and show the effect of $k_1$ and $b$ on ranking for a long
   document.
2. Construct five queries where dense retrieval fails and BM25 succeeds, and
   five the other way. Characterise each class.
3. † Measure recall against chunk size at 200, 400, 800, 1600 tokens with and
   without overlap. Find the optimum for your corpus.
4. Implement contextual chunk descriptions and quantify the recall gain and
   the one-off indexing cost.
5. Compare RRF against a linear score combination with tuned weights. Does the
   tuning survive a corpus change?
6. † Measure recall and latency for flat, IVF and HNSW at 10k, 100k and 1M
   vectors. Find the crossover where approximate search pays.
7. Build a retrieval-only evaluation set and show a case where answer quality
   is good despite poor retrieval (the model knew the answer anyway).
:::

:::recap
- BM25 scores by IDF, saturating term frequency and length normalisation, and
  beats embeddings on exact strings, codes, names and new terms.
- Embedding choice must be validated on your own corpus; respect the model's
  instruction prefixes and sequence limit.
- Chunking sets the ceiling: 400--1000 tokens, structural boundaries, overlap,
  and a generated context description before embedding.
- Fuse with reciprocal rank fusion, which works on ranks and needs no score
  calibration.
- Retrieve broadly with a bi-encoder, then rerank a shortlist with a
  cross-encoder.
- Below ~100k vectors use exact search; HNSW is the default above that.
- Measure retrieval and generation separately, always.
:::
