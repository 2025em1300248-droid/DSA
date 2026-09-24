# Five Jobs Behind One Job Title
@short: The Five Roles
@subtitle: Decide what you are aiming at before you learn anything
@tier: foundation
@prereq: none
@blurb: "AI/ML engineer" is now an umbrella over at least five jobs with materially different skill profiles, different interview loops and different salary bands. Choosing badly costs months. This chapter describes each one honestly --- what the day actually looks like, what is tested, and who should aim at it.
@objectives:
- Distinguish the five roles that share this title and what each is measured on
- Identify which skills transfer between them and which do not
- Choose a target role based on your starting point rather than on prestige
- Understand where hiring demand actually is, and where it is contested

## The map

@fig: role_map | 145 | The same job title, five different centres of gravity. The bars are rough weightings of where the hours go, not of what appears in the job description.

### AI Engineer

**The day.** You build products on top of foundation models you did not
train. Retrieval pipelines, agents, structured extraction, evaluation
harnesses, prompt and context engineering, guardrails, cost and latency
tuning. You touch model weights rarely and model *behaviour* constantly.

**What is tested.** Systems design for an LLM application, evaluation
design, debugging a bad RAG pipeline, API and product judgement. Increasingly:
"here is a failing agent, find out why."

**Who it suits.** Software engineers. This is the shortest transition in the
field --- three to four months of focused work --- because the foundation is
software engineering, not statistics. It is also where hiring volume has
grown fastest.

**The risk.** It is the easiest role to be shallow in. The market has many
people who can wire an API to a vector database; it has few who can tell you
whether the result is any good, and fewer who can make it cheap.

### ML Engineer

**The day.** You own models end to end: data, features, training, evaluation,
deployment, monitoring. Often the models are gradient-boosted trees over
tabular data, because that is what most businesses have. Ranking, fraud,
forecasting, churn, pricing, recommendation.

**What is tested.** Feature engineering and leakage, cross-validation design,
metric selection, class imbalance, a production incident postmortem,
sometimes a coding round on data manipulation.

**Who it suits.** Data scientists who want to own production, and software
engineers willing to learn statistics properly.

**The risk.** Under-rated by people chasing the frontier, and consequently
less crowded. A great deal of durable business value is here.

### ML Platform / Infrastructure Engineer

**The day.** You build the systems other ML people use: training clusters,
feature stores, model registries, serving infrastructure, GPU scheduling,
observability. You rarely train a model; you make training and serving fast,
cheap and reliable.

**What is tested.** Distributed systems, Kubernetes and scheduling,
performance profiling, storage and networking, reliability engineering.

**Who it suits.** Backend and infrastructure engineers. The ML-specific
content is learnable; the systems depth is not, quickly.

**The risk.** None much --- this is the most consistently underserved role in
the field and pays accordingly.

### Research Engineer

**The day.** You implement and scale ideas from papers, run training
experiments, write kernels, debug loss curves, build the tooling a research
team needs. You may co-author. You are measured on experimental throughput
and correctness, not on novelty.

**What is tested.** Deep learning internals, numerical debugging, reading and
reimplementing a paper, distributed training, sometimes CUDA or Triton.

**Who it suits.** People who genuinely enjoy the details: why the loss spiked
at step 40,000, why bf16 changed the result, why the third GPU is idle.

**The risk.** Concentrated in a small number of labs, so geographically and
organisationally narrow. Extremely competitive.

### Data Scientist (adjacent, and converging)

**The day.** Analysis, experimentation, causal questions, dashboards,
decision support. Increasingly also: building the evaluation sets that ML and
AI engineers depend on, which is a genuine convergence point.

**What is tested.** Statistics, experiment design, SQL, communication.

**Who it suits.** People whose comparative advantage is in the question
rather than the system.

## What transfers, and what does not

| From | To | Transfers | You must add |
|---|---|---|---|
| Software engineering | AI engineer | 70% | LLM behaviour, retrieval, evals, prompt/context design |
| Software engineering | ML engineer | 45% | statistics, feature engineering, metric design |
| Data science | ML engineer | 55% | engineering rigour, deployment, monitoring |
| Data science | AI engineer | 40% | software engineering, systems, evals at scale |
| Backend / infra | ML platform | 75% | GPU scheduling, training internals, ML-specific storage |
| ML engineer | Research engineer | 50% | deep learning internals, distributed training, kernels |
| Any | Any | --- | the foundations layer: Python, algorithms, systems, maths |

@tbl: Honest transfer rates between starting points and targets. The bottom row is the reason Part II of this map is not optional for anyone.

:::insight The advice that is actually load-bearing
Pick the role whose *failure modes* you find interesting. You will spend far
more time debugging than building, and the debugging is completely different
in each column: a bad eval set, a leaking feature, an idle GPU, a diverging
loss, an ambiguous business question. If one of those sounds like a puzzle
rather than a chore, that is your column.
:::

:::pitfall Three ways people choose badly
**Chasing the frontier.** Aiming at research engineer because it sounds
prestigious, from a background with no deep learning internals and no
systems depth. The transition is real but it is measured in years, not
months, and there is a far shorter path to working on interesting problems.

**Skipping the foundations layer.** Going straight to LLM tooling with weak
Python and no algorithms. This works until the first interview with a coding
round, or the first production incident, and then it does not.

**Optimising for the job title.** "AI engineer" pays well in 2026 partly
because of scarcity, and scarcity moves. The durable asset is the stack in
the next chapter, not the title on the offer letter.
:::

:::recap
- Five jobs share this title: AI engineer, ML engineer, ML platform, research
  engineer, data scientist. Their day-to-day work, interviews and required
  depth differ substantially.
- Software engineers convert fastest to AI engineering; backend engineers
  convert fastest to ML platform; data scientists convert fastest to ML
  engineering.
- Every path requires the foundations layer, which is the most common point
  of failure regardless of target.
- Choose by which failure modes you find interesting, because debugging is
  most of the work.
:::
