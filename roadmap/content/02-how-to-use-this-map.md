# The Stack, and Where the Hours Actually Go
@short: The Stack
@subtitle: What the job is made of, versus what courses teach
@tier: foundation
@prereq: Chapter 1
@blurb: Before the capability lists, two orienting pictures: the layered stack that every role sits on, and an honest account of where a working engineer's hours go. Both differ sharply from the shape of a typical curriculum, and the gap explains most of the difficulty people have converting study into a job.
@objectives:
- Hold the seven-layer stack in your head and locate any new skill within it
- Understand why the two largest time sinks are the two least taught
- Recognise the difference between a portfolio that signals competence and one that does not

## The stack

@fig: skill_stack | 215 | The layers. Nothing above works reliably if a layer below is missing, and interviews probe the bottom two far more than candidates expect.

Read it bottom-up. The property that makes this a *stack* rather than a list
is that weakness low down does not stay contained:

- Weak **Python and engineering** shows up as an unmaintainable pipeline, a
  notebook that cannot be rerun, a subtly non-deterministic result.
- Weak **data** shows up as a model that scores well offline and fails in
  production, which is usually leakage or train--serve skew.
- Weak **modelling** shows up as reaching for a deep model where a
  gradient-boosted tree would have been better, faster and explainable.
- Weak **production** shows up as a demo that never ships.
- Weak **judgement** shows up as a technically excellent solution to the
  wrong problem.

## Where the hours go

@fig: time_allocation | 145 | Illustrative proportions, but the shape is not controversial. The two rows that dominate real work --- data and evaluation --- are the two that almost no curriculum teaches.

This gap is the single best explanation for why people who have completed
several courses still struggle in interviews and first jobs. They have spent
65% of their study time on the 15% of the job that is modelling, and have no
practice at all in the 50% that is data and evaluation.

:::insight The corrective
For every model you train, make yourself do three things you would rather
skip: build the evaluation set *first*, write down the baseline before you
start, and deploy it somewhere, however crudely. Those three habits convert
study into the shape of the job.
:::

## What "knowing" a skill means here

Throughout this map, a capability is written as something you can do without
help, on a problem you have not seen. That is a deliberately high bar, and it
is the bar interviews use.

| Claim | What it actually requires |
|---|---|
| "I know PyTorch" | You can write a training loop from scratch, debug a NaN, and explain why your GPU is at 40% utilisation |
| "I know RAG" | You can measure retrieval recall separately from answer quality and say which one is broken |
| "I know fine-tuning" | You can say why you are *not* fine-tuning for this problem, and be right |
| "I know Kubernetes" | You can debug a pod that is stuck pending because a GPU node selector is wrong |
| "I know SQL" | You can read a query plan and explain why a join is slow |
| "I know evaluation" | You can construct a golden set, a grader, and a significance test for a 3% claimed improvement |

@tbl: The gap between a CV line and a capability. Every row is a question that gets asked.

:::pitfall The tutorial ceiling
There is a level you can reach entirely by following tutorials, and it is
higher than it used to be --- you can build an impressive-looking RAG
application without understanding any of it. The ceiling is sharp and it
arrives the first time something goes wrong in a way the tutorial did not
cover. The exit from the ceiling is always the same: build something with no
tutorial for it, and debug it yourself.
:::

:::recap
- The stack has seven layers; weakness low down leaks upward as
  production incidents rather than staying contained.
- Data work and evaluation dominate real hours and are barely taught; modelling
  is a minority of the work and most of the curriculum.
- Fix the gap with three habits: eval set first, baseline written down,
  deploy it somewhere.
- A capability means doing it unaided on an unfamiliar problem, which is the
  bar interviews use.
:::
