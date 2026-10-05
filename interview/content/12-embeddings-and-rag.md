# Embeddings, Vector Search and RAG
@short: Embeddings and RAG
@subtitle: The section most likely to decide the interview
@tier: core
@prereq: Chapter 11
@blurb: Two of your projects are retrieval systems and FAISS appears twice on your resume, so expect detail here. The questions that matter most are how you debug a bad retrieval and how you would evaluate the thing --- both are where candidates run out of answers.
@objectives:
- Explain embeddings and vector search in plain words
- Say what FAISS is and, honestly, what it is not
- Walk through your RAG pipeline in thirty seconds
- Debug a wrong retrieval by working backwards through the stages

## Embeddings and vector search

#### Q18.1 — What is an embedding?
Turning a piece of text into a list of numbers, arranged so that things with
similar meanings end up near each other. "Hard hat" and "safety helmet" land
close together even though they share no words.

#### Q18.2 — What is a vector database?
A store built for the question "what's most **similar** to this?" rather than
"find me the row with this exact ID". Normal databases are terrible at the
first question.

#### Q18.3 — What is FAISS, and is it a database?
A library for searching quickly through millions of these number-lists.

Strictly, it's not a database — it's an index. It doesn't save itself to disk
automatically, it has no way to filter by "only documents from 2024", and it
has no concept of users. You build all of that yourself.

Saying this shows you understand the tool's limits, which is a better answer
than praising it.

#### Q18.4 — Which embedding model did you use, and what are its properties?
MiniLM on SafeSight — 384 numbers per piece of text, small and fast, good
general-purpose sentence matching.

Know the dimension count. It gets asked.

#### Q18.5 — How do you choose an embedding model?
Match it to your domain, check it on your own data rather than trusting a
leaderboard, and weigh the number of dimensions against speed and storage.

And check its maximum input length is longer than your chunks — otherwise it's
silently cutting the end off every chunk and you'd never know.

#### Q18.6 — What distance metric do you use, and why cosine?
Cosine similarity, which compares the direction of two vectors and ignores
their length.

Because a long passage and a short one about the same thing should count as
similar. If you normalise the vectors first — which you should — a simple dot
product gives you the same answer faster.

#### Q18.7 — Exact vs approximate nearest neighbour search?
Exact compares your query against every single stored vector. Perfect results,
but the time grows with the collection.

Approximate uses a clever structure to check only a promising subset. You give
up a tiny bit of accuracy for an enormous speedup. You need it past roughly a
million items.

#### Q18.8 — Name some FAISS index types and when to use each.
**Flat**: compare against everything. Perfect, fine up to a few hundred
thousand.

**IVF**: group the vectors into clusters first, then only search the nearest
clusters.

**HNSW**: build a navigable graph and walk it towards the answer. Fast and
accurate, uses more memory. The usual default now.

**PQ**: compress the vectors so the index fits in less memory, at some
accuracy cost.

#### Q18.9 — What is HNSW?
A layered graph where you start at a sparse top layer, hop towards roughly the
right area, then drop into denser layers for precision. Like zooming in on a
map.

#### Q18.10 — What is IVF's `nprobe`, and what does tuning it do?
How many clusters to actually search. Search more and you find more of the
right answers but it takes longer. It's the main accuracy-versus-speed dial.

#### Q18.11 — Why does an IVF index need training when a flat index doesn't?
Because it has to learn where the cluster centres are, which it does from a
sample of your vectors. A flat index just stores everything, so there's
nothing to learn.

#### Q18.12 — FAISS vs Chroma vs Pinecone vs pgvector — how would you choose?
FAISS when you want something local with no extra service to run. Chroma for
a light local store that also handles metadata. Pinecone or Weaviate when you
want someone else to run it at scale with filtering. pgvector when your data
is already in Postgres and you'd rather have one system than two.

For your projects FAISS was the right call. Justify it on simplicity and cost.

#### Q18.13 — How do you persist and reload a FAISS index?
Write it out and read it back with FAISS's own functions — but you must save
the actual chunk texts alongside it yourself.

The index only stores the numbers and an ID. Lose the sidecar file and you
have an index that can tell you "result number 4,712 is the best match" and
nothing that can tell you what 4,712 says.

#### Q18.14 — How do you handle updates and deletions?
Some index types support removing items; others don't really, so you rebuild
the whole thing.

If your documents change often, that's the strongest argument for using a real
vector database instead.

#### Q18.15 — What is metadata filtering, and what's the catch with FAISS?
Restricting a search — only this department, only this year.

FAISS can't do it. So you either keep separate indexes per category, or you
fetch more results than you need and filter afterwards — which sometimes
leaves you short.

#### Q18.16 — What is k in top-k retrieval, and how do you pick it?
How many passages you hand to the model.

Too few and you miss the answer. Too many and the right passage gets buried in
irrelevant text, and you pay for all of it. Three to five is a sensible
starting point; tune it on real questions.

#### Q18.17 — What is a reranker, and why add one?
A second, slower model that reads the question and each candidate passage
**together** and rescores them.

The pattern: fetch fifty cheaply, rerank down to the best five. It's the
single biggest easy improvement available in RAG — worth more than most other
changes combined.

#### Q18.18 — Bi-encoder vs cross-encoder?
A bi-encoder turns the question and the document into numbers separately, so
you can prepare the documents in advance. Fast, less accurate.

A cross-encoder reads both together, so it understands how they relate. Much
more accurate, far too slow to run over a whole collection — which is why you
only use it on the shortlist.

#### Q18.19 — What is hybrid search?
Combining meaning-based search with plain keyword search, then merging the
rankings.

It fixes the one thing embeddings are bad at: exact strings. Part numbers,
regulation codes, specific names. Very relevant to safety manuals, where "Reg
14(2)(b)" needs to match exactly.

## RAG

#### Q19.1 — What is RAG, in one sentence?
Find the relevant passages from your own documents, paste them into the
prompt, and let the model answer from those — so the answer comes from your
data rather than the model's memory.

#### Q19.2 — Why use RAG instead of fine-tuning?
Your documents change, and retraining takes hours every time. With RAG you add
a document in seconds.

It also lets you cite the source, which fine-tuning can't. And fine-tuning
doesn't actually stop the model making things up.

#### Q19.3 — Walk me through your RAG pipeline end to end.
"Load the PDF. Split it into 800-character chunks with 150 characters of
overlap. Turn each chunk into numbers and store them in FAISS. When a question
comes in, turn it into numbers the same way, find the closest chunks, paste
them into the prompt with the question, and have Llama 3 answer from them —
returning the source passages alongside the answer."

Be able to say that in thirty seconds.

#### Q19.4 — What is chunking, and why not embed whole documents?
Splitting the document into passages.

Two reasons you can't use whole documents. One embedding for a whole document
averages everything together until it means nothing specific. And a whole
document wouldn't fit in the model's context anyway.

#### Q19.5 — Why 800 characters with 150 overlap specifically?
Big enough to contain one complete idea, small enough to stay precise and
cheap. The overlap means a sentence sitting across a boundary still appears
whole in one of the two chunks.

Say honestly whether you tuned it or picked a sensible default.

#### Q19.6 — What is `RecursiveCharacterTextSplitter` doing?
It tries to split at natural boundaries in order of preference — paragraph
breaks first, then line breaks, then sentences, and only chops mid-sentence as
a last resort.

#### Q19.7 — What other chunking strategies exist?
Fixed size, by sentence, by meaning (split where the topic shifts), or by
document structure (by heading or section).

For regulations, splitting by clause beats any character count — a rule is a
natural unit and chopping one in half is exactly the wrong thing to do.

#### Q19.8 — How does chunk size affect quality in both directions?
Too small: the answer gets split across several chunks and none of them is
sufficient on its own.

Too large: irrelevant text comes along for the ride, the search gets less
precise, and you burn context.

There's no universal number — it depends on how your documents are written.

#### Q19.9 — What goes in a RAG prompt?
A role instruction, the retrieved passages clearly marked off as source
material, the question, and an explicit rule: answer only from what's above,
and say so if it isn't there.

#### Q19.10 — How do you make the model cite its sources?
Give every chunk an identifier — file, page, chunk number. Include those
identifiers in the prompt. Instruct the model to reference them. Then check
the citations actually point at real passages.

Your traceability claim rests entirely on that last step.

#### Q19.11 — How do you stop it answering from its own knowledge?
Tell it to use only the provided text. Keep temperature near zero. And verify
that what it cited actually appears in the retrieved passages.

Belt and braces, because instructions alone leak — the model will sometimes
answer from memory regardless of what you told it.

#### Q19.12 — What is "lost in the middle"?
Models pay most attention to the beginning and the end of a long context, and
can skip over material in the middle.

So put the most relevant passages first, and keep the number of passages
modest rather than dumping everything in and hoping.

#### Q19.13 — How do you evaluate your RAG system?
Split it in two.

**Retrieval**: build a set of questions where you know which passage contains
the answer, then measure how often that passage comes back in the top results.

**Generation**: check whether the answer is actually supported by what was
retrieved, and whether anything was invented.

Fifty real questions is enough to catch regressions.

#### Q19.14 — What is RAGAS?
A ready-made evaluation library that scores faithfulness, answer relevance,
and whether the retrieved context was any good — so you don't build all of it
yourself.

#### Q19.15 — Your RAG returns the wrong chunk. How do you debug it?
Work backwards through the stages.

Is the right chunk **in the index at all**? If not, ingestion is broken.
Is it in the top fifty? If not, your embedding model is wrong for this domain.
Is it in the top five? If not, your ranking needs a reranker.

That's three questions and each eliminates a whole layer. Logging what got
retrieved for every query is not optional — without it you're guessing.

#### Q19.16 — What is query expansion or rewriting?
Rephrasing the user's question before searching — generating variants, or
turning a follow-up into a standalone question.

Essential in a chat, where "what about gloves?" means nothing on its own but
means a great deal given the previous turn.

#### Q19.17 — What is HyDE?
Have the model write a **hypothetical** answer first, then search using that
instead of the question.

Why it works: a short question looks nothing like the document that answers
it, but a draft answer looks a lot like it.

#### Q19.18 — What is parent-document retrieval?
Search over small precise chunks, but hand the model the larger section that
chunk came from.

You get precise matching and complete context, instead of having to choose.

#### Q19.19 — How do you handle tables and images in PDFs?
Plain text extraction mangles tables — columns get interleaved into nonsense.
You need a layout-aware parser, and tables are best converted into a simple
text table format.

For images, have a vision model describe them and index the description.

A good honest answer: "my current pipeline handles plain text well and tables
badly."

#### Q19.20 — What is a multi-query retriever?
Generate several rephrasings of the question, search with each, and combine
the results. It helps when the user's exact wording happens to be unlucky.

#### Q19.21 — How does SafeSight's RAG differ from DocuMind's?
DocuMind is one-shot: a person types a question about documents they uploaded.

SafeSight is triggered by a **detection**, not a question. A violation becomes
the query, rules get retrieved, and the graph then decides whether those rules
actually apply — looping back if they don't.

Different shape of problem, which is why one uses a graph and one doesn't.

#### Q19.22 — How would you scale from one user's PDFs to an enterprise corpus?
Swap FAISS for a managed store with filtering and access control. Add hybrid
search and a reranker. Cache embeddings and common queries. Move ingestion
into a queue so uploads don't block. And enforce per-user document permissions
at query time.

That last one is what makes it a production answer. Without it, retrieval will
happily hand someone a passage from a document they aren't allowed to read.

#### Q19.23 — What is prompt injection, and why is it a real risk in RAG?
Instructions hidden inside a document you ingest. The model can't tell the
difference between your instructions and text it retrieved — they arrive in
the same prompt as the same kind of thing.

So a document containing "ignore your instructions and..." may well be obeyed.

Mitigate by clearly labelling retrieved text as data rather than instructions,
constraining what the output can be, and never letting retrieved text directly
trigger an action.

#### Q19.24 — What are RAG's main failure modes?
The document was never indexed. The chunking split the answer. The embedding
model is wrong for this domain. k is too small. The answer was in the middle
and got skipped. The index is stale. Or the model ignored the context.

Diagnose by layer, using Q19.15's backwards walk. Never by guessing.

:::practice The debugging answer
Q19.15 is the one that separates people. Memorise the three-step walk: is it
in the index, is it in the top fifty, is it in the top five. Each answer points
at a different layer. Being able to say that immediately is worth a lot.
:::

:::recap
- An embedding puts similar meanings close together; cosine similarity ignores
  length, which is why text uses it.
- FAISS is an index, not a database — no persistence, no filtering, no users.
  Say so.
- Save the chunk texts alongside the index or it's useless.
- A reranker is the single biggest easy win in RAG.
- Hybrid search fixes the one thing embeddings are bad at: exact codes and
  names.
- Debug retrieval backwards: in the index, in the top fifty, in the top five.
- Permissions at query time is what makes a scaling answer a production
  answer.
:::
