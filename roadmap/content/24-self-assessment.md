# Self-Assessment
@short: Self-Assessment
@subtitle: A rubric for knowing where you actually are
@tier: reference
@prereq: none
@blurb: Self-assessment in this field is unreliable in a specific direction: people who have read a great deal overestimate themselves, and people who have shipped systems underestimate themselves. This rubric replaces "do I know X" with "can I do X, unaided, right now", which is the only question with a checkable answer.
@objectives:
- Place yourself honestly on a five-level scale per area
- Identify the one or two gaps worth closing next
- Re-assess on a schedule rather than by feel

## The levels

@fig: maturity | 162 | Five levels. The jump that matters for employment is 2 to 3: from following a path to handling a situation nobody prepared you for.

| Level | Name | Test |
|---|---|---|
| 1 | Aware | You can define the term and say why it matters |
| 2 | Guided | You can do it with documentation and an example open |
| 3 | Independent | You can do it unaided, and debug it when it fails |
| 4 | Fluent | You can choose between approaches and justify the choice with numbers |
| 5 | Authoritative | You can teach it, extend it, and know where the standard advice is wrong |

@tbl: The level scale. Note that level 3 requires debugging, not just building --- a system that works only when nothing goes wrong is level 2 evidence.

:::insight Use verbs, not nouns
"I know transformers" is unfalsifiable. "I can implement multi-head attention
from scratch, unaided, and explain why the scaling factor is 1/sqrt(d_k)" is
checkable in ten minutes. Every row below is phrased as something you either
can or cannot currently do. If you are unsure, the answer is no --- a skill you
are unsure about is not one you can rely on under pressure.
:::

## The rubric

Score each row 1--5. Be strict; the rubric is only useful if it is honest.

| # | Skill | Chapter |
|---|---|---|
| 1 | Write a tested, typed, packaged Python library others install | 3 |
| 2 | Use git properly: bisect, rebase, resolve a real conflict | 3 |
| 3 | Derive backprop for a 2-layer network by hand | 4 |
| 4 | Explain why a matrix--vector product is memory-bound | 4, 18 |
| 5 | Compute a bootstrap confidence interval and say what it means | 4, 15 |
| 6 | Solve a medium interview problem in 25 minutes, naming the pattern | 5 |
| 7 | Write correct SQL with window functions over a large table | 6 |
| 8 | Build a point-in-time-correct feature pipeline | 6 |
| 9 | Detect and fix train--serve skew | 6, 17 |
| 10 | Deduplicate and quality-filter a large text corpus | 7 |
| 11 | Beat a GBDT baseline on tabular data, or explain why you cannot | 8 |
| 12 | Calibrate a classifier and pick a threshold from a cost matrix | 8 |
| 13 | Implement a transformer block from scratch | 9 |
| 14 | Debug a model that trains but does not learn | 9 |
| 15 | Run a multi-GPU training job with FSDP and diagnose a stall | 10 |
| 16 | Estimate memory for a given model, batch size and optimiser | 10 |
| 17 | Explain KV cache size and how GQA changes it | 11, 16 |
| 18 | Build a RAG pipeline and measure each stage separately | 12 |
| 19 | Choose between prompting, RAG, fine-tuning and pre-training, with reasons | 13 |
| 20 | Run a LoRA fine-tune and beat a prompted baseline, or show you did not | 13 |
| 21 | Build an agent with budgets and a failure taxonomy | 14 |
| 22 | Build a golden set and validate an LLM judge against humans | 15 |
| 23 | Cut inference cost by 5x with quality measured at each step | 16 |
| 24 | Deploy a model with canary, monitoring and automatic rollback | 17 |
| 25 | Read a roofline chart and say whether a kernel is worth optimising | 18 |
| 26 | Demonstrate prompt injection on your own system and fix it architecturally | 19 |
| 27 | Explain a model's decision to a non-technical stakeholder | 20 |
| 28 | Tell a stakeholder their project should not use ML | 20 |

@tbl: Twenty-eight checkable skills. The chapter column points at the material for anything scoring below where you want it.

## Reading your scores

:::checklist What the totals mean --- as a rough guide only
- **Under 60**: foundations phase. Work Track C's early weeks. Do not skip
  to foundation models; it will not stick.
- **60--90**: junior-capable. You can contribute under supervision. Push two
  or three areas to level 3 and build the first portfolio project.
- **90--120**: mid-level. Depth in some areas, gaps in others. Fill the gaps
  that block your target role, ignore the rest for now.
- **120--140**: senior-capable in your specialisation. Your constraint is
  probably rows 27--28, not the technical rows.
- **Above 140**: verify with evidence. Every level 4 and 5 should correspond
  to something you have shipped or taught. If it does not, it is a 3.
:::

:::warning The two reliable biases
**Reading inflation.** Having read about FSDP thoroughly is level 1--2, not 4.
The test for 3 is "unaided, and debug it when it fails", and nothing you read
gets you there.

**Shipping deflation.** Having run something in production for a year while
feeling you never learned it properly is usually level 4. If you have
diagnosed its failures at 3am, you are past 3.

These two biases mean the loudest self-assessments are often the least
accurate ones.
:::

## Turning the rubric into a plan

1. Mark the five lowest rows that your **target role** actually needs.
   Use the role table in Chapter 1; an AI engineer does not need row 15 at
   level 4.
2. For each, write the concrete deliverable that would move it up one level.
   Not "study FSDP" --- "run a two-node FSDP job and fix one stall".
3. Schedule them. Two per month is a realistic rate alongside a job.
4. Re-score every three months, not more often. Skills move slowly and
   frequent re-scoring measures mood rather than ability.

:::insight The last two rows
Rows 27 and 28 --- explaining a decision to a stakeholder, and telling someone
not to use ML --- are scored lowest by almost everyone and are the two that
most reliably separate a senior engineer from a strong mid-level one. They are
also the fastest to improve, because the practice is free: explain your last
project to someone outside the field and watch where they stop following.
:::

:::recap
- Score skills by what you can do unaided, not by what you have read.
- Level 3 requires debugging, not just building.
- Twenty-eight checkable rows, each mapped to a chapter.
- Reading inflates scores; shipping deflates them. Correct for both.
- Turn the five lowest role-relevant rows into dated deliverables, and
  re-score quarterly, not weekly.
:::
