# Curating a Training Corpus
@short: Corpus Curation
@subtitle: The work that produced the largest quality gains of recent years
@tier: advanced
@prereq: Chapter 13
@blurb: Between two models with the same architecture and compute budget, the difference is the data. Deduplication, quality filtering, mixture design and contamination control are unglamorous, largely mechanical, and account for more measured improvement than most architectural work. This chapter covers each at the scale where it matters.
@objectives:
- Deduplicate at scale, exactly and approximately, and know why it matters
- Build quality filters that are measurably better than heuristics alone
- Design a data mixture and reason about epochs and repetition
- Detect and prevent benchmark contamination
- Generate and validate synthetic data without collapsing the distribution

## Why deduplication comes first

Web-scraped corpora are 10--50% duplicate. Duplicates hurt three ways: the
model memorises repeated text instead of generalising, training compute is
spent on content already learned, and --- worst --- duplicates that straddle
your train/eval split silently invalidate the evaluation.

@fig: dedup_pipeline | 136 | The deduplication ladder, run cheapest first. Removal rates are strongly corpus-dependent; what is stable is the ordering, because each stage shrinks the input to the next. Duplicates straddling the train/eval split do not merely waste compute --- they invalidate the evaluation.

```python title="Exact deduplication: start here, it is nearly free"
import hashlib

def exact_dedup(docs):
    seen = set()
    for d in docs:
        # Normalise first, or you will keep the same text with different
        # whitespace, casing and unicode forms.
        norm = " ".join(unicodedata.normalize("NFKC", d["text"]).lower().split())
        h = hashlib.blake2b(norm.encode(), digest_size=16).digest()
        if h not in seen:
            seen.add(h)
            yield d
```

Sixteen bytes per document: a billion documents needs 16 GB of hashes, which
fits. Above that, shard by the first bytes of the hash and dedup each shard
independently --- identical documents always land in the same shard, so the
result is exact.

```python title="Near-duplicates: MinHash + LSH"
from datasketch import MinHash, MinHashLSH

def shingles(text, k=5):
    ws = text.split()
    return {" ".join(ws[i:i+k]) for i in range(max(1, len(ws) - k + 1))}

lsh = MinHashLSH(threshold=0.8, num_perm=128)
for doc_id, text in corpus:
    m = MinHash(num_perm=128)
    for s in shingles(text):
        m.update(s.encode())
    if not lsh.query(m):          # no near-duplicate already indexed
        lsh.insert(doc_id, m)
        keep(doc_id)
```

MinHash estimates Jaccard similarity from 128 numbers instead of the full
shingle set; LSH buckets similar sketches so you compare each document against
a handful of candidates rather than all $n$. The cost is $O(n)$ rather than
$O(n^2)$, which is the difference between feasible and not.

:::insight The measured effect
Published work on large web corpora consistently finds that deduplication lets
a model reach the same loss with substantially less compute, and reduces
verbatim memorisation of training text by a large factor. It is the single
highest return-on-effort operation in corpus preparation --- more reliable
than most architectural changes, and far cheaper.
:::

## Quality filtering

A ladder, cheapest first, because each stage reduces the volume the next one
must process.

```python title="Stage 1: heuristics — fast, and they remove the obvious"
def heuristic_ok(text: str) -> bool:
    words = text.split()
    if not (50 <= len(words) <= 100_000):
        return False
    if sum(len(w) for w in words) / len(words) > 10:      # base64, code dumps
        return False
    if text.count("\n") / max(len(text), 1) > 0.30:       # mostly newlines
        return False
    alpha = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha < 0.60:                                      # tables, gibberish
        return False
    lines = text.split("\n")
    if len(set(lines)) / max(len(lines), 1) < 0.50:       # repeated boilerplate
        return False
    if any(p in text.lower() for p in BLOCKLIST_PHRASES): # lorem ipsum, spam
        return False
    return True
```

```python title="Stage 2: a learned classifier, trained on a reference set"
# Positive class: a corpus you trust (curated references, well-edited text).
# Negative class: a random sample of raw crawl.
# A fastText or small transformer classifier costs microseconds per document.
clf = fasttext.train_supervised("quality.train", dim=64, epoch=5,
                                wordNgrams=2, minCount=3)

def quality_score(text):
    labels, probs = clf.predict(text.replace("\n", " "), k=1)
    return probs[0] if labels[0] == "__label__high" else 1 - probs[0]
```

```python title="Stage 3: perplexity under a reference model"
# Text that a small reference model finds very surprising is usually broken
# (encoding errors, machine translation artefacts, random tokens).
# Text it finds trivially predictable is usually boilerplate.
# Keep the middle band; the thresholds are corpus-specific and must be tuned
# by inspecting samples at each percentile.
```

:::warning Filtering has a bias cost
Every quality filter encodes a judgement about what good text looks like. A
classifier trained with an encyclopaedia as the positive class will
systematically downweight dialects, informal registers, and non-Western
sources --- reducing measured perplexity while narrowing what the model can
handle.

The practical mitigations: sample and *read* 100 documents at every filter
threshold before adopting it; report retention rates by language and source;
and keep a deliberately unfiltered holdout to measure what you lost.
:::

## Mixture design

```python title="A mixture is a set of weights, and it is a hyperparameter"
MIXTURE = {
    "web_filtered":  0.50,
    "code":          0.15,
    "books":         0.12,
    "academic":      0.10,
    "reference":     0.05,
    "multilingual":  0.05,
    "instructions":  0.03,
}
# Each source is upsampled or downsampled to hit its weight. Sources smaller
# than their weight get repeated — which is where epoch effects come in.
```

| Question | Practical answer |
|---|---|
| How many epochs? | up to ~4 repetitions is close to fresh data; beyond that returns fall sharply |
| Upsample a small high-quality source? | yes, modestly (2--4×); heavy upsampling causes memorisation |
| Code in a non-code model? | yes --- consistently improves reasoning benchmarks |
| Order matters? | yes --- later data has more influence; curricula that end on high-quality data measurably help |
| How to choose weights? | small-scale proxy runs; weights transfer reasonably across scale |

@tbl: Mixture rules of thumb. The last row is what makes this tractable: you can tune a mixture on 100M-parameter proxy runs and carry the weights to a much larger model.

## Contamination

Benchmark data in your training set makes evaluation meaningless, and it gets
in through ordinary web text --- benchmark questions are discussed, quoted and
reposted constantly.

```python title="Contamination check, n-gram overlap"
def contamination_rate(corpus_ngrams: set, benchmark_docs, n=13):
    """Fraction of benchmark items sharing a long n-gram with the corpus."""
    hits = 0
    for doc in benchmark_docs:
        toks = doc.split()
        grams = {" ".join(toks[i:i+n]) for i in range(max(0, len(toks)-n+1))}
        if grams & corpus_ngrams:
            hits += 1
    return hits / len(benchmark_docs)
```

Thirteen tokens is the usual threshold: long enough that an accidental match
is rare, short enough to catch paraphrased reposts. Run this for every
benchmark you intend to report, *before* training, and remove the matching
corpus documents. Report the contamination rate alongside the score --- a
benchmark number without one is not interpretable.

:::pitfall Contamination through the back door
Even with a clean corpus, contamination arrives via: synthetic data generated
by a model that saw the benchmark; instruction data scraped from sites that
discuss benchmarks; and evaluation sets derived from the same public sources
as your training data. The n-gram check catches the first-order case only.
Where it matters, use a private evaluation set that has never been published
--- which is the only genuinely robust answer.
:::

## Synthetic data

```python title="Generate, then filter — the filtering is the valuable half"
def synth_batch(seeds, model, n_per_seed=4):
    out = []
    for seed in seeds:
        cands = [model.generate(PROMPT.format(seed=seed), temperature=1.0)
                 for _ in range(n_per_seed)]
        for c in cands:
            if not schema_valid(c):            # 1. structurally valid
                continue
            if not verify(c):                  # 2. checkable: run the code,
                continue                       #    check the arithmetic
            if near_duplicate(c, out):         # 3. adds diversity
                continue
            out.append(c)
    return out
```

The generation step is easy and the filtering step is where the quality comes
from. The strongest signal available is **verifiability**: if the task has a
checkable answer --- code that must run, arithmetic that must be right, a
schema that must validate --- filter on it and the quality ceiling rises
sharply.

:::warning Model collapse
Training repeatedly on a model's own unfiltered output narrows the
distribution: tails disappear, diversity falls, and quality degrades across
generations. The mitigations are real-data anchoring (keep a substantial
fraction of human data in the mixture), verification-based filtering, and
explicit diversity measurement (distinct n-grams, embedding-space coverage)
tracked across generations.
:::

:::practice The task
Take a corpus of at least a million documents. (a) Measure the exact-duplicate
rate, then the near-duplicate rate with MinHash at thresholds 0.7, 0.8 and 0.9;
read 20 pairs at each threshold and judge whether they should be merged.
(b) Build the three-stage quality filter and report retention by source.
(c) Sample 100 rejected documents and read them --- count how many were
rejected wrongly. (d) Run the contamination check against two public
benchmarks. (e) Train two small models on the raw and curated corpora with
identical compute and compare.

**You have this skill when** you can state your corpus's duplicate rate,
retention rate by source, and contamination rate for every benchmark you
report.
:::

:::exercise
1. Implement exact dedup with normalisation and measure how much extra it
   catches over raw hashing.
2. Show that MinHash with 128 permutations estimates Jaccard similarity to
   within about 0.09 (the standard error is $1/\sqrt{128}$).
3. † Build the LSH index and measure the candidate-pair count against a
   brute-force $O(n^2)$ comparison on 100,000 documents.
4. Train the quality classifier and plot its score distribution by source.
   Choose a threshold by reading samples, not by picking a round number.
5. Measure retention by language and identify which the filter penalises.
6. † Run 13-gram contamination against a benchmark, then against a paraphrased
   version of it. Report the detection rate for each.
7. Generate synthetic data with and without verification filtering, train on
   each, and compare both quality and output diversity.
:::

:::recap
- Deduplicate first: exact hashing is nearly free, MinHash+LSH catches near
  duplicates in linear time, and duplicates across the train/eval boundary
  invalidate evaluation.
- Filter in stages --- heuristics, a learned classifier, perplexity bands ---
  and read samples at every threshold, because filters encode bias.
- A mixture is a hyperparameter tunable on small proxy runs; up to about four
  repetitions is close to fresh data.
- Check 13-gram contamination against every benchmark you report, and report
  the rate.
- Synthetic data is only as good as its filter; verifiability is the strongest
  signal, and unfiltered self-training collapses the distribution.
:::
