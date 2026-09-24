# What Changed, and What Is Now Obsolete
@short: What Changed
@subtitle: An honest account of what to learn now and what to stop learning
@tier: reference
@prereq: none
@blurb: Roadmaps written three years ago are actively misleading in places, and the parts that went stale are not the parts people expect. This chapter states plainly what became important recently, what became less important, and --- the part usually missing --- what did not change at all.
@objectives:
- Know which skills became scarce and valuable recently
- Stop spending time on material that has quietly stopped mattering
- Recognise the durable core that survives every cycle

## The shape of the change

@fig: what_changed | 152 | What the job asked for, by year. The left column has not disappeared --- it is still most of the work in most ML roles. The right column is what is newly scarce.

## What became important

:::checklist The genuinely new, in rough order of how scarce the skill is
**Evaluation as a first-class discipline.** The single largest gap in the
market. Teams can build LLM features and cannot tell whether a change helped.
Chapter 15.

**Inference cost and latency engineering.** When serving cost is a material
line item, the ability to cut it by an order of magnitude through batching,
caching, quantisation and routing is directly valuable. Chapter 16.

**Agents and tool use.** Reliability engineering for non-deterministic loops:
budgets, verification, failure taxonomies, sandboxing. Chapter 14.
MCP has emerged as a cross-vendor standard for exposing tools.

**Post-training.** LoRA and QLoRA made fine-tuning accessible; DPO and its
relatives made preference optimisation accessible without an RL stack; GRPO
and verifiable rewards made reasoning-style training tractable. Chapter 13.

**Retrieval done properly.** Not "put documents in a vector database" but
hybrid search, reranking, contextual chunking, and per-stage measurement.
Chapter 12.

**Data curation at scale.** Dedup, filtering, mixture design, synthetic
generation, contamination control. The largest reliable quality gains of
recent years came from here. Chapter 7.

**Prompt injection and LLM security.** A genuinely new vulnerability class
with no prompting-level fix. Chapter 19.

**Context engineering.** Managing what goes into a finite window --- ordering,
budgeting, compaction, externalising memory --- as a distinct skill from
prompt wording.
:::

## What became less important

:::checklist Things worth substantially less time than they were
**Hand-designing architectures.** The transformer and its standard variants
cover most of what practitioners need. Designing novel architectures is a
research activity, not an engineering one.

**Manual feature engineering for unstructured data.** Superseded by learned
representations. Still essential for *tabular* data, where it remains a core
skill.

**Classical NLP pipelines.** Separate tokenisers, POS taggers, parsers,
NER models, and the associated toolchain. A general model with a good prompt
or a small fine-tune covers most of it, and does so better.

**Grid search.** Random search dominates it, and Bayesian search
(Optuna and similar) dominates random. Grid search persists mostly in
tutorials.

**TensorFlow 1.x and Keras-first workflows.** TensorFlow still runs in
production and JAX is strong in research, but PyTorch is the default and the
one to learn first. Multi-framework fluency is no longer a baseline
requirement.

**Hand-writing training loops for everything.** Write one from scratch to
understand it; then use `accelerate`, `trl`, Lightning or similar.

**Building your own vector index.** Understand how they work --- it determines
your memory budget and recall --- but use FAISS or a vector database.

**Word2vec, GloVe and static embeddings.** Historically important;
contextual embeddings are better on essentially every task.
:::

:::warning Less important is not "safe to be ignorant of"
Everything in that list still appears in interviews and in legacy systems.
The claim is that it deserves less of your *learning* time, not that you
should be unable to discuss it. Knowing why static embeddings were superseded
is a two-minute answer that demonstrates understanding; being unable to
recognise word2vec suggests a gap.
:::

## What did not change

:::checklist The durable core
- **Software engineering.** Version control, testing, packaging, CI,
  reproducibility. More important now, not less, because AI systems are
  harder to make reproducible.
- **Data quality.** Leakage, train--serve skew, distribution shift. Identical
  failures, now with more expensive models on top.
- **Evaluation discipline.** Golden sets, held-out data, confidence
  intervals, calibration. The techniques transferred wholesale from classical
  ML to foundation models --- which is why people with a classical background
  are noticeably better at LLM evaluation.
- **Gradient-boosted trees on tabular data.** Still the right answer. Still
  winning. Still most of the ML in most companies.
- **The memory hierarchy.** Sequential beats random; bytes moved beats
  operations performed. FlashAttention is this principle, applied.
- **Problem framing.** What decision does this change; what happens today;
  what does an error cost.
- **Mathematics.** Linear algebra, probability, optimisation. Unchanged and
  unchanging.
- **Distributed systems.** Ring all-reduce's bandwidth optimality is a fact
  about topology, not about a framework.
:::

:::insight How to read a roadmap, including this one
Separate three categories every time: **principles** (memory hierarchy,
evaluation discipline, problem framing) which last decades; **techniques**
(LoRA, DPO, paged attention, hybrid retrieval) which last years; and
**tools** (a specific library or vendor) which last months. Spend your
learning time in that order of priority, and treat the tool layer as
something you pick up in a day when you need it.

A roadmap that is mostly tool names is telling you about its author's recent
month, not about the field.
:::

## Where the demand actually is

| Area | Supply of engineers | Demand | Comment |
|---|---|---|---|
| Building LLM demos | very high | saturated | the tutorial ceiling |
| LLM evaluation | very low | high | the clearest opportunity |
| Inference cost engineering | low | high and growing | directly measurable value |
| ML platform / infrastructure | low | high | persistently underserved |
| Data curation at scale | low | high | quiet, valuable, unglamorous |
| Classical ML in production | moderate | steady and large | undervalued by newcomers |
| Frontier research | very high | very low | extremely competitive |

@tbl: A qualitative read of the market. The pattern is consistent: demand is highest where the work is unglamorous and requires engineering rigour rather than novelty.

:::recap
- Newly scarce: evaluation, inference cost engineering, agent reliability,
  post-training, retrieval done properly, data curation, LLM security,
  context engineering.
- Worth less time now: novel architectures, manual features for unstructured
  data, classical NLP pipelines, grid search, TensorFlow-first workflows,
  building your own index, static embeddings.
- Unchanged: software engineering, data quality, evaluation discipline, GBDT
  on tabular data, the memory hierarchy, problem framing, mathematics,
  distributed systems.
- Separate principles from techniques from tools, and spend your time in that
  order.
- Demand is highest where the work is rigorous and unglamorous.
:::
