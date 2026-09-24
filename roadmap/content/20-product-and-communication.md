# Product Sense and Communication
@short: Product and Communication
@subtitle: The skills that decide whether the work mattered
@tier: core
@prereq: none
@blurb: The most common way for a technically excellent machine learning project to fail is for it to solve the wrong problem, or to solve the right one in a way nobody adopts. These are learnable skills with concrete practices, and they are the clearest difference between a mid-level engineer and a senior one.
@objectives:
- Frame a business problem as a machine learning problem, or decline to
- Choose a metric that a stakeholder and an engineer both understand
- Write a design document that gets a decision made
- Communicate uncertainty without either overclaiming or being useless

## Problem framing

:::checklist ESSENTIAL --- the questions to ask first
1. **What decision does this output change?** If the answer is "none", stop.
   A prediction nobody acts on has no value.
2. **What happens today?** There is always an incumbent: a rule, a human, a
   spreadsheet. That is your baseline, and it is often better than expected.
3. **What is the cost of each error type?** A false positive and a false
   negative are almost never equally expensive, and the ratio determines your
   metric and your threshold.
4. **What accuracy would be good enough to act on?** If nobody can answer
   this, the project has no success criterion.
5. **Is there enough of the right data, with labels, from the right
   distribution?** Ask before promising anything.
6. **What is the latency and cost budget?** These constrain the solution
   space more than accuracy usually does.
7. **How will it be wrong, and who is harmed?** Chapter 19.
:::

:::checklist ESSENTIAL --- when not to use machine learning
- A rule would work. Rules are explainable, testable, instant and free
- You cannot define success
- You do not have labels and cannot obtain them
- The cost of an error is catastrophic and unrecoverable
- The problem changes faster than you could retrain
- The data does not exist yet --- in which case the project is instrumentation,
  not modelling

Saying this clearly and early is a senior behaviour and is consistently
valued more than delivering a model nobody needed.
:::

## Metrics that connect

:::checklist ESSENTIAL
- Build the chain explicitly: model metric $\rightarrow$ product metric
  $\rightarrow$ business metric. If you cannot draw that chain, you cannot
  argue for the work
- Choose a single primary metric and a small set of guardrails (latency,
  cost, fairness, safety) that must not degrade
- Distinguish offline and online metrics, and expect them to disagree ---
  when they do, the online one is right and the gap is information
- Sanity-check magnitude: a claimed 40% improvement in a mature system is
  almost always a bug or a leak
- Present a confidence interval, always
:::

## Writing and speaking

:::checklist ESSENTIAL --- the design document
A one-to-three page document, written *before* the work, containing:
problem, current state, proposed approach, alternatives considered and why
rejected, success criteria, risks, and how you will know it failed. Its
purpose is to get a decision made and to be re-readable in a year.

The section people skip and should not is *alternatives considered*. It is
what turns a proposal into a defensible decision.
:::

:::checklist ESSENTIAL --- communicating results
- Lead with the conclusion and the decision you want. Then the evidence
- State uncertainty in terms of consequences: "we are confident it is between
  2% and 6% better, which at current volume is between X and Y" beats a
  p-value
- One chart per claim, with axes labelled and a confidence interval drawn
- Translate: "AUC 0.84" means nothing to most audiences; "catches 70% of
  fraud while flagging 2% of good transactions" means something
- Report the failures and limitations yourself, before somebody finds them.
  It is the fastest way to become trusted
:::

:::checklist CORE --- working with others
- With product: negotiate the accuracy/latency/cost triangle explicitly, and
  show them the frontier rather than a single point
- With engineering: agree the interface and the failure behaviour early ---
  what does the service return when the model is unavailable
- With legal and compliance: bring them in before the architecture is fixed,
  not at launch
- With annotators and domain experts: they know things the data does not
  encode; their disagreements are information about your guidelines
- Code review and design review given kindly and specifically
- Mentoring: the fastest way to consolidate your own knowledge
:::

:::checklist CORE --- staying current without drowning
- Read a small number of primary sources rather than a large number of
  summaries. Model and system cards, and the papers behind the tools you
  actually use
- Reproduce one technique a month, in code. Reading a paper produces
  recognition; implementing it produces capability
- Follow the release notes of the three or four libraries you depend on ---
  this is where genuinely useful changes appear
- Keep a written log of what you tried and what happened. It is the only
  defence against relearning the same lesson
- Deliberately ignore most of it. The volume of AI content is now far beyond
  what anyone can track, and the fraction that will matter in a year is small
:::

:::insight The single most valuable professional habit
Write down what you expect *before* you run the experiment. A one-line
prediction: "I expect this to improve recall by about 3% and to cost 20%
more latency." Then compare. Over a year this does two things: it calibrates
your intuition faster than anything else, and it makes you notice when a
result is surprising --- which is where the learning and most of the bugs
both live.
:::

## How to tell you have it

:::practice The tasks
1. Take a project you worked on and write, retrospectively, the one-page
   design document you should have written. Include the alternatives.
2. Take your best result and explain it in three sentences to somebody with
   no technical background. Have them tell you what decision they would make
   on the basis of it. If they cannot, rewrite.
3. Find a project in your organisation that should not use machine learning,
   and write the two-paragraph argument for the rule-based alternative.
4. For a model you own, draw the full chain from model metric to business
   metric with the arithmetic on each arrow.
:::

:::pitfall The four ways good work goes to waste
1. **Solving the wrong problem.** No decision changes as a result.
2. **Optimising an unconnected metric.** AUC improves, revenue does not, and
   nobody can explain why.
3. **Delivering without a handover.** No runbook, no documentation, no owner;
   it degrades and gets switched off.
4. **Overclaiming.** One overstated result costs more credibility than
   several good ones earn.
:::

:::note Time to competence
Continuous, and the fastest route is writing. One design document and one
written result summary per project, reviewed by somebody senior, improves
this faster than any reading.
:::

:::recap
- Ask what decision the output changes, what happens today, and what error
  costs, before anything technical.
- Be willing to say that machine learning is the wrong tool; it is a senior
  behaviour and it is valued.
- Draw the chain from model metric to business metric, pick one primary
  metric and explicit guardrails.
- Write a short design document before the work, including alternatives
  considered.
- Lead with the conclusion, express uncertainty in consequences, and report
  your own limitations first.
- Write down your expected result before running the experiment; nothing
  calibrates judgement faster.
:::
