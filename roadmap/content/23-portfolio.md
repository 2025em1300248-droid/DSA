# A Portfolio That Signals Competence
@short: Portfolio
@subtitle: What to build, and how to write it up so it is believed
@tier: practice
@prereq: Chapter 22
@blurb: Most portfolios are indistinguishable from tutorials, which is why they do not work. This chapter describes what a project has to contain to be evidence of engineering ability, gives six project specifications at increasing difficulty, and shows how to write them up so a reviewer with four minutes reaches the right conclusion.
@objectives:
- Understand what a reviewer is actually checking for in four minutes
- Build three projects that are evidence rather than imitation
- Write a README that makes the evidence legible

## What a reviewer is checking

A hiring manager spends about four minutes on a portfolio project. They are
not reading your model code. They are looking for evidence of six things:

:::checklist The six signals
1. **Does it run?** Clear setup, pinned dependencies, and it works on a
   machine that is not yours.
2. **Is it tested?** Any tests at all put you ahead of most candidates.
   Tests of the data logic put you well ahead.
3. **Is the evaluation honest?** A held-out set, a stated baseline, an
   interval or a significance statement, and at least one place where you say
   what did not work.
4. **Did you make decisions?** A trade-off named and resolved, with the
   reasoning visible.
5. **Can you write?** The README is the sample of your communication that
   gets read.
6. **Is it yours?** Not a tutorial with the dataset swapped.
:::

:::pitfall Why the standard portfolio fails
Titanic, MNIST, IMDB sentiment, "chat with your PDF". These are all
*tutorial completions*. They demonstrate that you can follow instructions,
which was never in question. The signal is zero because there is no decision
in them --- every choice was made by the tutorial author.

Adding a Streamlit front end does not fix this. The problem is not
presentation, it is that no judgement was exercised.
:::

## Six projects

Each specification below has a decision embedded in it that the project
cannot be completed without making.

**1. An evaluation harness for an LLM feature.** Pick a task. Build a golden
set of 150--300 labelled cases, including adversarial and edge cases. Implement
three grader types (exact/programmatic, similarity, LLM-as-judge). Validate
the judge against human labels and report the agreement rate. Wire it into CI
so a regression fails a build. Write up which grader disagreed with you and
what you did about it.
*The decision*: what counts as correct, and how you know your grader knows.

**2. A RAG system with per-stage measurement.** A corpus of at least 5,000
documents. Measure retrieval recall@k separately from answer quality. Compare
at least three configurations (dense only; hybrid; hybrid plus reranker) with
numbers. Report latency and cost per query alongside quality.
*The decision*: where the failures actually are --- and the answer must come
from your own measurements, not from a blog post.

**3. A tabular model in production form.** A real dataset with temporal
structure. Point-in-time-correct features, a time-based split, calibration,
a threshold chosen from an explicit cost matrix, SHAP explanations, a served
endpoint, and monitoring with drift detection.
*The decision*: the operating threshold, justified in the currency of the
problem rather than by maximising F1.

**4. An agent with a failure taxonomy.** A multi-step task with three or more
tools. Step budget, token budget, timeout. Trajectory-level evaluation over at
least 50 tasks. Then the part that matters: categorise every failure, count
the categories, fix the largest one, and show the before-and-after numbers.
*The decision*: which failure mode to spend your effort on.

**5. An inference cost reduction.** Take a working LLM feature. Measure
baseline cost and p95 latency. Apply at least three techniques from Chapter 16
--- caching, batching, quantisation, model routing, speculative decoding.
Report the cost curve and the quality change at each step.
*The decision*: how much quality you are willing to trade for how much cost,
stated up front.

**6. A fine-tune with a real baseline.** Pick a task where a strong prompted
baseline exists. Establish that baseline properly. Then fine-tune --- LoRA or
QLoRA --- and show whether you beat it, on a held-out set, with the cost of
both approaches stated.
*The decision*: whether fine-tuning was worth it. "No" is a perfectly good
result and a rarer, more credible write-up than yet another claimed win.

:::insight Three is the right number
Three projects at this depth beat ten shallow ones, and beat one enormous one.
Three demonstrates range; depth demonstrates ability; more than three
demonstrates that you did not know when to stop.

Pick them to span your target role: for an AI engineer, projects 1, 2 and 4;
for an ML engineer, 3, 6 and 1; for an inference or platform role, 5, 3 and 2.
:::

## The write-up

A reviewer's four minutes are spent on the README. Structure it so the first
screen answers the question they are actually asking.

:::checklist README structure
**Problem** (2 sentences). What decision does this system support, and what
happened before it existed.

**Result** (1 short table). The headline numbers against a named baseline,
with the metric defined.

**Approach** (1 paragraph plus one diagram). What you built. One image.

**Trade-offs** (3--5 bullets). What you chose and what you gave up. This is
the section that separates a portfolio from a tutorial.

**What did not work** (3 bullets). The most credible section in any write-up.
Reviewers read it first once they know it is there.

**Evaluation** (short section). Dataset, split, metrics, intervals. State the
sample size. State whether the difference is significant.

**Run it** (a code block). Two commands, maximum.

**Limitations** (3 bullets). Where it breaks and what you would do next.
:::

```md
## Result

| Configuration          | Recall@10 | Answer acc. | p95 latency | $/1k queries |
|------------------------|----------:|------------:|------------:|-------------:|
| Dense only (baseline)  |      0.61 |        0.58 |       340ms |         1.20 |
| + BM25 hybrid          |      0.78 |        0.67 |       390ms |         1.25 |
| + cross-encoder rerank |      0.89 |        0.74 |       720ms |         2.10 |

n = 240 held-out questions; answer accuracy graded by a judge validated at
0.91 agreement with human labels on a 60-item sample.
```

:::note What this table does
It names a baseline, separates retrieval from generation, shows the cost of
each quality gain, and states how the grader was validated. A reviewer who
reads only this block already knows you can do the job. Everything below it
is confirmation.
:::

:::warning Things that actively hurt
- Claimed accuracy with no baseline and no split description.
- A notebook as the only artefact.
- `requirements.txt` with no versions.
- A demo link that is down. Better no link than a dead one.
- "State of the art" anywhere in the text.
- Screenshots of a chat interface used as evidence of quality.
:::

## Where the projects live

Public repository, one per project, each with the README above. A short
write-up per project on a personal page or a blog, aimed at an engineer rather
than a recruiter. Do not build a portfolio *website* --- reviewers read
repositories. Time spent on the site is time not spent on the third project.

:::recap
- Reviewers check six things in four minutes: it runs, it is tested, the
  evaluation is honest, decisions were made, you can write, it is yours.
- Tutorial completions signal nothing because no judgement was exercised.
- Build three projects spanning your target role, each containing a real
  decision.
- The README carries the signal: problem, result table, approach,
  trade-offs, what did not work, evaluation, run it, limitations.
- "What did not work" is the most credible section you can write.
:::
