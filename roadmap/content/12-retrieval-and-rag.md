# Retrieval and RAG
@short: Retrieval and RAG
@subtitle: A chain of decisions, each with its own failure mode and its own eval
@tier: core
@prereq: Chapters 11, 5
@blurb: Retrieval-augmented generation is the most commonly built and most commonly mis-built pattern in applied AI. It is not one technique but a pipeline of six or seven decisions, each of which can silently destroy quality. The distinguishing skill is not building one; it is being able to say which stage is broken.
@objectives:
- Build a retrieval pipeline and measure each stage independently
- Choose chunking, embedding, indexing and reranking strategies from the data
- Implement hybrid search and know when it beats dense retrieval alone
- Diagnose whether a bad answer is a retrieval failure or a generation failure

## The pipeline

@fig: rag_decisions | 160 | A retrieval pipeline is a chain of tunable decisions. Recall lost at chunking or retrieval cannot be recovered downstream, which is why each stage needs its own measurement.

## The capabilities

:::checklist ESSENTIAL --- chunking
- Fixed-size with overlap as a baseline; semantic and structural chunking
  (by heading, by section, by function) usually better
- Chunk size as a tradeoff: small chunks retrieve precisely and lose context;
  large chunks carry context and dilute the embedding
- Late chunking and contextual retrieval: embed with surrounding context or
  prepend a generated document-level summary to each chunk. This is one of
  the highest-yield cheap improvements available
- Preserving metadata (source, section, date, permissions) on every chunk ---
  you will need it for filtering, citation and access control
- Handling tables, code and images, which fixed-size text chunking destroys
:::

:::checklist ESSENTIAL --- embeddings and search
- Embedding model selection: dimension, context length, domain match,
  multilingual support, and cost. Benchmarks are a starting point, not an
  answer --- evaluate on your own queries
- Normalisation, and why cosine and inner product coincide for unit vectors
- Asymmetric retrieval: queries and documents are different distributions;
  models with separate query/document prefixes exist for this reason
- Hybrid search: BM25 (lexical) plus dense (semantic), fused with reciprocal
  rank fusion. Lexical search is dramatically better at exact identifiers,
  codes, names and rare terms, which dense embeddings routinely miss
- Metadata filtering, and the fact that filtered vector search is genuinely
  hard (Chapter 33 of the companion volume)
- Reranking with a cross-encoder: retrieve 50--100, rerank to 5--10. Usually
  the largest single quality gain per unit of effort in the whole pipeline
:::

:::checklist ESSENTIAL --- indexing
- Exact search is correct and fast below roughly a million vectors; do not
  build an index before you need one
- IVF, product quantisation, HNSW: what each trades, and the memory
  arithmetic
- Recall@$k$ against a brute-force ground truth as the *only* honest measure
  of an index configuration
- Updates and deletions: HNSW deletes poorly; if your corpus churns, that
  constrains your architecture
- Vector database options: pgvector when you already have Postgres and the
  scale is modest, a dedicated store when it is not
:::

:::checklist CORE --- query processing
- Query rewriting and expansion, and multi-query retrieval (generate several
  phrasings, retrieve for each, fuse)
- HyDE: generate a hypothetical answer and retrieve against that, which often
  matches the document distribution better than the question does
- Query routing: not every question needs retrieval, and a classifier that
  decides saves latency and reduces distraction
- Conversational retrieval: resolving "what about the second one?" into a
  standalone query before retrieving
:::

:::checklist CORE --- generation and assembly
- Context ordering: most relevant at the edges rather than the middle
- Deduplicating retrieved chunks
- Citation and attribution, with spans if you can
- Instructing abstention when the context does not contain the answer, and
  measuring whether it complies
- Token budget management across system prompt, context, history and output
:::

:::checklist CORE --- evaluation, which is the actual skill
| Measure | What it tells you |
|---|---|
| Retrieval recall@$k$ | did the right chunk get retrieved at all |
| Retrieval precision / MRR / NDCG | is the ranking any good |
| Context relevance | is the retrieved material actually about the question |
| Faithfulness / groundedness | is the answer supported by the retrieved context |
| Answer correctness | is the answer right, against a reference |
| Abstention accuracy | does it decline when it should |
| End-to-end latency and cost | can you afford it |
:::

:::insight The diagnostic that resolves most RAG problems in an afternoon
Measure retrieval recall separately from answer quality, on the same
examples. There are only three cases, and each has a different fix:

- **Low recall, good answers when retrieval succeeds.** The problem is
  chunking, embedding or the index. Prompting will not help.
- **Good recall, bad answers.** The problem is generation: the prompt, the
  context ordering, the model, or the amount of distracting context.
- **Both bad.** Fix retrieval first; answer quality is bounded by it.

Teams routinely spend months tuning prompts against a retrieval problem,
because they only ever looked at the final answer.
:::

## When RAG is the wrong answer

| Situation | Better |
|---|---|
| The corpus fits comfortably in context | Put it in the prompt with prefix caching |
| The knowledge is stable and narrow | Fine-tune, or just write it in the system prompt |
| The question needs aggregation over many documents | Query a database; retrieval returns $k$ chunks, not a `GROUP BY` |
| The question needs multi-hop reasoning over structure | A knowledge graph, or an agent with a search tool |
| You need guaranteed coverage | Retrieval is probabilistic; use a deterministic lookup |

@tbl: RAG is a default, not a law. The third row is the most common misuse: "how many of our contracts mention X" is a database question, and retrieval will answer it confidently and wrongly.

## How to tell you have it

:::practice The task
Build a retrieval system over a corpus you know well, then:
1. Construct 100 question/answer pairs with the *correct chunk* labelled ---
   this is the work, and it is what makes everything else measurable.
2. Report recall@5 and recall@20 for: fixed chunking, semantic chunking,
   dense only, hybrid, and hybrid plus reranking. Five numbers.
3. Report faithfulness and answer correctness for the best two configurations.
4. Find three questions the system answers wrongly and classify each as a
   retrieval or a generation failure, with evidence.
5. Measure end-to-end p50 and p95 latency and cost per query.
:::

:::pitfall The five RAG mistakes
1. **No retrieval metric.** Only end-to-end quality is measured, so nobody
   knows which half is broken.
2. **Dense-only search.** Exact identifiers, error codes and rare names fail;
   BM25 would have found them.
3. **No reranker.** The cheapest large quality gain, routinely skipped.
4. **Chunks without context.** A chunk saying "it increased by 12%" is
   useless without knowing what "it" is.
5. **Building an ANN index at 50,000 documents.** Brute force is exact,
   faster, and has no tuning.
:::

:::note Time to competence
**4--6 weeks** to build and *evaluate* a real pipeline. Building one takes a
weekend; the evaluation is the skill and the remainder of the time.
:::

:::recap
- RAG is a chain of decisions --- chunk, embed, index, retrieve, rerank,
  assemble --- each with its own failure mode and its own metric.
- Hybrid lexical plus dense search, and a cross-encoder reranker, are the two
  highest-yield additions to a naive pipeline.
- Contextual or late chunking fixes the "chunk without context" failure
  cheaply.
- Do not build an ANN index below roughly a million vectors.
- Measure retrieval recall separately from answer quality; that one split
  resolves most RAG debugging.
- RAG is wrong for aggregation questions, for stable narrow knowledge, and
  when guaranteed coverage is required.
:::
