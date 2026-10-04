# Building a RAG System That Works
@short: Building RAG
@subtitle: The full pipeline, measured stage by stage
@tier: core
@prereq: Chapter 33
@blurb: A RAG demo takes an afternoon; a RAG system that people trust takes considerably longer, and the difference is almost entirely measurement and failure handling. This chapter assembles the full pipeline, instruments every stage, and works through the failure taxonomy that tells you which stage to fix.
@objectives:
- Assemble ingestion, retrieval, generation and citation into one pipeline
- Instrument every stage so a failure is attributable
- Handle the four generation failures: no answer, wrong answer, no citation, over-claim
- Decide when RAG is the wrong tool
- Keep an index fresh without rebuilding it

## The pipeline

@fig: rag_pipeline | 148 | The full pipeline with measurement points. Each stage has its own metric; a system reporting only end-to-end answer quality cannot be debugged, because any stage could be responsible.

| Stage | Metric | Typical failure |
|---|---|---|
| Parse | extraction fidelity | tables flattened, PDF columns interleaved |
| Chunk | boundary quality | split mid-table, no context |
| Index | coverage | documents silently dropped on error |
| Retrieve | **recall@k** | wrong passages, exact terms missed |
| Rerank | precision@k | relevant passage ranked below noise |
| Generate | faithfulness, correctness | ignores context, or invents |
| Cite | citation accuracy | citation does not support the claim |

@tbl: Seven stages, seven metrics. Instrument all of them. The two in bold type are the ones that most often carry the problem.

## Ingestion

```python title="Parsing is where the quality ceiling is set"
def ingest(path):
    raw = parse(path)                      # layout-aware for PDFs
    if len(raw.strip()) < 100:
        raise IngestError(f"{path}: produced almost no text — scanned?")
    doc = normalise(raw)                   # unicode NFKC, whitespace, ligatures
    chunks = chunk_structurally(doc, target=800, overlap=120)

    out = []
    for i, c in enumerate(chunks):
        context = describe_chunk(doc_title, section_of(c), c)   # Chapter 33
        out.append({
            "id": f"{doc_id}#{i}",
            "text": c,
            "embed_text": f"{context}\n\n{c}",     # context is embedded ...
            "doc_id": doc_id, "title": doc_title,
            "section": section_of(c), "page": page_of(c),
            "updated_at": mtime(path), "source_url": url_of(path),
            "hash": sha256(c),                     # for incremental reindexing
        })
    return out
```

:::pitfall Parsing failures are silent and expensive
A scanned PDF yields an empty string. A two-column paper yields interleaved
lines. A financial table becomes a row of numbers with no headers. None of
these raise an exception, and all of them poison the index permanently.

Validate at ingest: minimum character count, a language check, a ratio of
alphabetic characters, and --- the one that catches the most --- **read
twenty parsed documents yourself** before indexing a million. Log the per-
document character count and look at the bottom percentile.
:::

## Generation

```python title="The prompt that produces faithful, cited answers"
PROMPT = """\
Answer the question using ONLY the sources below.

Rules:
- Cite the source id for every factual claim, like [S2].
- If the sources do not contain the answer, say exactly:
  "The provided sources do not answer this question."
- Do not use knowledge beyond the sources, even if you are confident.
- If sources conflict, say so and cite both.

<sources>
{sources}
</sources>

<question>
{question}
</question>
"""

def format_sources(chunks):
    return "\n\n".join(
        f'<source id="S{i}" title="{c["title"]}" section="{c["section"]}">\n'
        f'{c["text"]}\n</source>'
        for i, c in enumerate(chunks, start=1))
```

Three details carry most of the benefit. The **exact refusal string** makes
"no answer" machine-detectable, so you can measure and route it. **Per-claim
citations** make faithfulness checkable automatically. The **conflict clause**
handles the common case of a corpus containing both a current and a superseded
policy.

## The failure taxonomy

:::checklist Four generation failures, and which stage each implicates
**1. "The sources do not answer this" when they do.** The passage was
retrieved but the model did not use it. Causes: the passage is buried in the
middle of a long context (Chapter 29), the wording differs too much from the
question, or the instruction is too conservative. Check: does the answer
appear verbatim in the context you sent?

**2. A wrong answer with a citation.** The cited passage does not support the
claim. Causes: the model stitched two passages together, or extracted the
right field from the wrong row. This is the most dangerous failure because it
looks authoritative. Detect it with a separate faithfulness check (below).

**3. A right answer with no supporting passage.** The model used its
parametric knowledge, which may be out of date and is not auditable. Detect by
removing the sources and seeing whether the answer survives.

**4. Over-claiming from a partial match.** The sources say "most plans
include X"; the answer says "your plan includes X". Fix in the prompt with an
explicit hedging instruction, and measure.
:::

```python title="An automated faithfulness check"
FAITHFUL = """\
Claim: {claim}
Source: {source}

Does the source support the claim? Answer exactly one word:
SUPPORTED, CONTRADICTED, or NOT_MENTIONED.
"""

def faithfulness(answer, sources):
    claims = split_into_claims(answer)
    verdicts = [judge(FAITHFUL.format(claim=c, source=sources[cited(c)]))
                for c in claims]
    return sum(v == "SUPPORTED" for v in verdicts) / max(len(verdicts), 1)
```

Run this over a sample continuously. A faithfulness score that drops is the
earliest signal that retrieval has degraded --- usually before anyone
complains.

## Measurement

```python title="The harness, reporting every stage"
def evaluate(pipeline, dataset):
    rows = []
    for q in dataset:
        retrieved = pipeline.retrieve(q.question, k=10)
        hit = len(set(r.id for r in retrieved) & set(q.relevant_ids)) > 0
        rank = next((i for i, r in enumerate(retrieved, 1)
                     if r.id in q.relevant_ids), None)

        answer = pipeline.generate(q.question, retrieved)
        rows.append(dict(
            recall_at_10=hit,
            mrr=1.0 / rank if rank else 0.0,
            refused=answer.strip().startswith("The provided sources do not"),
            correct=grade(answer, q.expected),            # Chapter 37
            faithful=faithfulness(answer, retrieved),
            cited=all_claims_cited(answer),
            latency_ms=answer.latency, cost=answer.cost,
        ))
    return summarise(rows)
```

| Diagnostic pattern | Conclusion |
|---|---|
| recall low, correctness low | fix **retrieval** |
| recall high, correctness low | fix **generation** |
| recall high, correctness high, faithfulness low | the model is using parametric knowledge |
| refusal rate high, recall high | the prompt is too conservative |
| refusal rate low, correctness low | the model is not refusing when it should |

@tbl: Reading the harness. These five patterns cover the overwhelming majority of RAG debugging, and none of them is visible from an end-to-end score alone.

## Keeping the index fresh

```python title="Incremental reindexing by content hash"
def sync(source_docs, index):
    current = {d.id: d.hash for d in source_docs}
    indexed = index.all_hashes()

    for doc_id in set(indexed) - set(current):
        index.delete_document(doc_id)                 # removed at source
    for doc_id, h in current.items():
        if indexed.get(doc_id) != h:
            index.delete_document(doc_id)             # changed, or new
            index.add(ingest(doc_id))
```

Deleting before adding is what keeps stale chunks out. The most common
freshness bug is a document being re-chunked into fewer pieces after an edit,
leaving the surplus old chunks in the index forever --- where they continue to
be retrieved and cited.

:::insight When RAG is the wrong tool
- **The answer requires aggregation over the whole corpus** ("how many
  contracts expire this quarter?"). Retrieval returns $k$ passages, not a
  count. Use SQL, or give the model a query tool.
- **The corpus is small and static.** Under roughly 50,000 tokens, put the
  whole thing in the context and skip retrieval entirely --- it is simpler,
  cheaper after prompt caching, and strictly more accurate.
- **The task needs style or format, not knowledge.** That is fine-tuning
  (Chapter 35).
- **The answer requires multi-hop reasoning across documents.** Single-shot
  retrieval finds passages relevant to the *question*, not to the intermediate
  steps. Use an agent that can retrieve iteratively (Chapter 38 in the
  Skill Map's terms; here, Chapter 32's tool loop).
- **Freshness is measured in seconds.** Index lag will not meet it; query the
  source system directly through a tool.
:::

:::practice The task
Build the full pipeline on a real corpus with at least 100 labelled queries.
(a) Instrument all seven stages. (b) Report the five-row diagnostic table and
state which stage is your bottleneck. (c) Implement the faithfulness check and
run it over 200 answers; read 20 of the failures by hand and classify them
into the four-failure taxonomy. (d) Remove the sources for 50 questions and
measure how many the model answers anyway. (e) Edit a source document so it
re-chunks into fewer pieces, sync, and verify no stale chunks survive.

**You have this skill when** a wrong answer leads you to the responsible stage
in one query of your logs.
:::

:::exercise
1. Ingest a scanned PDF and show the pipeline fails silently. Add the
   validation that catches it.
2. Build a case where the answer is in the retrieved context and the model
   says it is not. Diagnose and fix.
3. † Implement the faithfulness judge, validate it against 60 human labels,
   and report the agreement rate.
4. Measure the refusal rate as the retrieval quality is deliberately degraded.
   Plot it.
5. Put a 40,000-token corpus entirely in context and compare accuracy, cost
   and latency against RAG over the same corpus.
6. † Construct a multi-hop question and show single-shot retrieval fails.
   Implement iterative retrieval and measure the improvement.
7. Demonstrate the stale-chunk bug and fix it with hash-based sync.
:::

:::recap
- Seven stages, seven metrics; an end-to-end score alone cannot be debugged.
- Parsing failures are silent and permanent --- validate at ingest and read
  twenty parsed documents by hand.
- The generation prompt needs an exact refusal string, per-claim citations and
  a conflict clause.
- Four generation failures: false refusal, wrong answer with citation, right
  answer without support, over-claiming.
- The recall/correctness cross-tabulation tells you which half to fix.
- Reindex incrementally by content hash, deleting before adding.
- RAG is wrong for aggregation, small static corpora, style tasks, multi-hop
  reasoning and second-level freshness.
:::
