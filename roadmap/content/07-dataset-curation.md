# Dataset Curation for Modern Models
@short: Dataset Curation
@subtitle: The skill that improved models more than architecture did
@tier: core
@prereq: Chapter 6
@blurb: Over the last several years the largest reliable gains in model quality have come from better data rather than better architectures. Deduplication, filtering, mixture design, synthetic generation and contamination control are now engineering disciplines with known techniques. This chapter covers them at the level a practitioner needs.
@objectives:
- Deduplicate a corpus exactly and approximately, at scale
- Design and measure a data mixture rather than guessing one
- Generate and validate synthetic data without collapsing the distribution
- Detect and report benchmark contamination
- Run a labelling operation that produces measurable agreement

## What this is for

Three results have become consensus and should shape how you spend time:
deduplicated data trains better models per token; filtered data beats more
data past a point; and mixture proportions matter as much as total volume.
All three are data-engineering work, not modelling work.

## The capabilities

:::checklist CORE --- deduplication
- Exact dedup with content hashing, and why you store a 16-byte digest
  rather than the document
- Near-duplicate detection with MinHash and LSH: shingling, signature length,
  banding, and choosing $(b, r)$ for a target similarity threshold
- SimHash and Hamming-distance blocking for cosine-style similarity
- Clustering candidate pairs with union--find, and capping cluster size so
  transitive chaining does not merge an entire topic
- Granularity: document-level versus paragraph- or line-level, and the
  tradeoff (line-level removes far more boilerplate and risks fragmenting
  documents)
- Which copy to keep --- often a bigger quality lever than the threshold
:::

:::checklist CORE --- filtering and quality
- Heuristic filters: length, symbol ratio, repetition, language
  identification, perplexity under a reference model
- Classifier-based filtering: train a small model to score "is this like my
  high-quality reference set?" and threshold on it
- The boilerplate problem: navigation text, licence blocks, cookie notices
- Toxicity, PII and licence filtering, and the fact that each filter has a
  measurable cost in recall of useful content
- Measuring the effect of a filter *by training something*, not by inspection
:::

:::checklist CORE --- mixture and curriculum
- Domain mixture as an explicit, versioned artefact: proportions per source
- Upsampling and downsampling policies, and epoch counts per source
- Measuring mixture effects with small proxy models before committing compute
- Curriculum: ordering by difficulty or quality, and honest scepticism about
  how much it helps
:::

:::checklist CORE --- synthetic data
- Generation patterns: instruction synthesis, self-instruct style expansion,
  distillation from a stronger model, back-translation, programmatic
  generation with verifiable answers
- Verification: the highest-value synthetic data is data where correctness
  can be *checked* (code that runs, maths with a known answer, format that
  parses)
- Diversity control: temperature, seed prompts, persona conditioning, and
  measuring coverage rather than assuming it
- Model collapse: training repeatedly on your own outputs narrows the
  distribution. Mitigate by anchoring to real data, by filtering
  aggressively, and by measuring diversity explicitly
- Licensing and terms-of-service constraints on distilling from a commercial
  model --- this is a real legal question, not a formality
:::

:::checklist CORE --- contamination
- Detect test-set leakage into training data with $n$-gram hashing plus an
  exact check, or a suffix array for arbitrary-length matching
- Report coverage per test example, not just a binary flag
- Decide and state whether you matched tokens or characters; the numbers are
  not comparable otherwise
- Re-evaluate on a decontaminated subset and report both numbers
:::

:::checklist CORE --- labelling
- Writing annotation guidelines that two people interpret the same way ---
  this is harder and more valuable than it sounds
- Inter-annotator agreement: Cohen's/Fleiss' kappa, Krippendorff's alpha, and
  what an acceptable value is for your task
- Adjudication of disagreements, and treating disagreement as signal about
  the guidelines rather than about the annotators
- Active learning: label where the model is uncertain or where disagreement
  is high
- Weak supervision and programmatic labelling as a first pass
- LLM-assisted labelling with human verification --- now the default for many
  tasks, with the caveat that the model's biases become the dataset's biases
:::

## How to tell you have it

:::practice The task
Take a corpus of at least a million documents. Then:
1. Report the exact-duplicate rate and the near-duplicate rate at Jaccard
   0.8, with the $(b, r)$ you chose and why.
2. Apply three filters and report, for each, how many documents it removed
   and a sample of twenty it removed --- half of which you should read.
3. Build a held-out evaluation set and check it for contamination against the
   training corpus. Report coverage.
4. Train the same small model on the raw and the curated corpus and report
   the difference with a confidence interval.

Step 4 is the whole point. Curation claims without a trained comparison are
opinions.
:::

:::pitfall Four curation mistakes with expensive consequences
**Deduplicating after splitting.** Near-duplicates spread across train and
test inflate every metric. Deduplicate first, split second.

**Filtering without reading.** Every filter removes things you did not intend
to remove. Read a random sample of what each filter kills, every time.

**Transitive over-merging.** Near-duplicate is not a transitive relation; a
chain of 0.85-similar documents can merge an entire topic into one cluster.
Cap cluster size.

**Synthetic data without verification.** Generating a million examples from a
model and training on them without checking correctness amplifies the
generator's errors and narrows the distribution simultaneously.
:::

:::note Time to competence
**4--6 weeks** to be able to run the pipeline above at moderate scale.
Deduplication mechanics are a week; the judgement about filters and mixtures
takes longer and is learned by training models and comparing.
:::

:::recap
- Data curation has produced larger reliable gains than architecture work;
  treat it as a primary skill.
- Dedup exactly with hashes and approximately with MinHash/LSH plus
  union--find; cap cluster size and decide granularity deliberately.
- Filter with heuristics and classifiers, and always read a sample of what
  each filter removed.
- Mixture proportions are a versioned artefact; measure them with proxy
  models.
- Synthetic data is most valuable where correctness is checkable; guard
  against collapse by anchoring to real data and measuring diversity.
- Check contamination, report coverage, and state token versus character
  matching.
- Labelling quality is a guidelines problem measured by inter-annotator
  agreement.
:::
