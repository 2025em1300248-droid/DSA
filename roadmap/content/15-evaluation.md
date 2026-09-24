# Evaluation
@short: Evaluation
@subtitle: The scarcest skill in applied AI, and the most learnable
@tier: core
@prereq: Chapters 4, 11
@blurb: Almost every team building on foundation models is bottlenecked by the same thing: they cannot tell whether a change made the system better. Evaluation is unglamorous, it is rarely taught, and engineers who can build an honest harness are scarce out of all proportion to how hard the skill actually is. If you read one chapter of this map, read this one.
@objectives:
- Build a golden set that is representative, adversarial and maintained
- Write graders --- rule-based, model-based and human --- and validate them
- Make claims with statistical honesty, including at small sample sizes
- Run eval-driven development as a working loop rather than an aspiration
- Monitor quality in production, not only before deployment

## Why this is the bottleneck

A team without an evaluation harness can still ship. What they cannot do is
*improve reliably*. Every change becomes a judgement call, regressions are
discovered by users, and after three months nobody can say which of the
forty prompt revisions helped. The symptom is a system that plateaus early
and then oscillates.

The reason this skill is scarce is that it feels like overhead. It is not:
it is the thing that converts effort into progress.

## The loop

@fig: eval_loop | 150 | Eval-driven development. The return arrow is the part that compounds: every production failure becomes a permanent test case, so the same regression cannot happen twice.

## The capabilities

:::checklist ESSENTIAL --- datasets
- Build a **golden set**: 100--1,000 examples with known-good outputs or
  known-correct judgements. Start at 50 if you must; 50 is infinitely better
  than zero
- Make it representative of real traffic, which means sampling from real
  traffic rather than inventing examples
- Include the hard cases deliberately: ambiguous inputs, adversarial inputs,
  out-of-scope questions that should be declined, edge cases, and examples
  where the right answer is "I do not know"
- Maintain it: every production failure becomes a test case, permanently
- Version it, and treat a change to the eval set as a change requiring
  review --- otherwise you can improve your score by weakening your test
- Keep a second held-out set you do not iterate against, to catch overfitting
  to the first one
:::

:::checklist ESSENTIAL --- graders
- **Rule-based** where possible: exact match, regex, schema validity, code
  that runs, numerical tolerance, latency threshold. Cheap, deterministic,
  and the strongest grader when the task permits it
- **Reference-based**: ROUGE, BLEU, BERTScore, embedding similarity. Weak
  proxies for quality; use them as regression alarms, not as quality measures
- **LLM-as-judge**: a model scores the output against a rubric. Now the
  standard for open-ended tasks, with real caveats:
  - Write a *rubric*, not "rate 1--10". Specific criteria with definitions
  - Pairwise comparison is more reliable than absolute scoring
  - Randomise position: judges have a position bias
  - Known biases: length, verbosity, self-preference toward the judge's own
    model family, and sensitivity to formatting
  - **Validate the judge against human labels.** Measure agreement. A judge
    you have not validated is a number generator
  - Use a different model as judge than the one under test where you can
- **Human evaluation** as ground truth: clear guidelines, multiple
  annotators, measured inter-annotator agreement, adjudication
:::

:::checklist ESSENTIAL --- statistics
- Report a confidence interval with every number. Bootstrap is easy and
  distribution-free
- Paired comparisons where possible: run both systems on the same examples
  and test the *difference*, which has far lower variance than comparing two
  independent means
- Know how many examples you need. To detect a 5-point difference in a
  proportion near 0.8 with reasonable power you need a few hundred paired
  examples; for 1 point you need thousands. Compute this before claiming
- Correct for multiple comparisons: evaluating twenty prompts on one set will
  produce a winner by chance
- Watch for a non-stationary judge: model updates change the grader, so pin
  versions and re-baseline when you cannot
:::

:::checklist CORE --- what to measure
| Layer | Measure |
|---|---|
| Component | retrieval recall@$k$, tool-call validity, schema compliance, classifier accuracy |
| Output | correctness, faithfulness, relevance, completeness, tone, format |
| Behaviour | refusal appropriateness, abstention, instruction-following, safety |
| Operational | p50/p95 latency, cost per request, error rate, throughput |
| Business | task completion, escalation rate, user edits, thumbs-down rate |

The vertical structure matters: an end-to-end number tells you *that*
something is wrong, and component metrics tell you *what*.
:::

:::checklist CORE --- in production
- Online evaluation: sample real traffic, grade it continuously, alert on
  drift in the grade distribution
- Implicit signals: user edits, retries, abandonment, escalation to a human,
  copy events. Often more honest than explicit thumbs
- Explicit feedback, with the knowledge that it is heavily biased toward
  extremes
- A/B testing with proper randomisation and sequential-testing discipline
- Shadow deployment: run the new system alongside, grade both, ship nothing
- Canary releases with automatic rollback on a metric regression
- Regression suites in CI: the eval runs on every change to prompt, model or
  retrieval configuration, and blocks the merge if it drops
:::

:::checklist CORE --- error analysis
- Read the failures. Fifty of them, by hand, personally. There is no
  substitute and there is no shortcut
- Cluster them into a taxonomy; count the clusters; fix the biggest one
- Re-cluster monthly, because the mix changes as you fix things
- Keep the taxonomy in the repository so the team shares a vocabulary for
  what is going wrong
:::

## Tools

| Job | Options |
|---|---|
| Harness and tracing | Braintrust, LangSmith, W&B Weave, Phoenix/Arize, OpenTelemetry-based tracing |
| Open-source frameworks | `promptfoo`, `deepeval`, `ragas` (RAG-specific), `inspect` |
| Academic benchmarks | MMLU, GPQA, HumanEval, SWE-bench, and their successors |
| Your own | A CSV, a grader function and a script. Genuinely fine to start |

@tbl: Evaluation tooling. The last row is not a joke: a versioned CSV plus a grading script plus a CI job outperforms an unused platform, and you can adopt a platform later without losing anything.

:::warning Public benchmarks measure the wrong thing for you
MMLU and its relatives are useful for comparing base models and useless for
telling you whether your system works. They are contaminated to an unknown
degree, they do not resemble your traffic, and improving on them does not
improve your product. Use them to choose a starting model; use your own
golden set for everything after that.
:::

## How to tell you have it

:::practice The task
Take any LLM feature, yours or somebody else's.
1. Sample 100 real inputs. If there is no real traffic, write 100 inputs and
   label where they came from.
2. Produce reference outputs or judgements for all 100.
3. Write three graders: one rule-based, one LLM-judge with a written rubric,
   one human protocol.
4. **Validate the judge**: have a human label 50 of them and report agreement
   with the judge. If agreement is poor, fix the rubric before trusting any
   number it produces.
5. Establish the baseline with a bootstrap confidence interval.
6. Make one change. Re-run. State whether the difference is significant,
   using a paired test.
7. Wire it into CI so the suite runs on every prompt change.
8. Read 20 failures by hand and write the taxonomy.

Step 4 is the one nearly everybody skips, and it is the one that makes the
rest of the numbers mean anything.
:::

:::pitfall The six evaluation failures
1. **Vibes.** Reading outputs and forming an impression. Cannot detect a 3%
   regression, cannot be compared across people.
2. **An unvalidated judge.** A number with no established relationship to
   quality.
3. **Evaluating on the set you tuned against.** Scores improve, quality does
   not.
4. **No confidence intervals.** Noise gets shipped as improvement.
5. **Only end-to-end metrics.** You know something is wrong, not what.
6. **A stale eval set.** It reflects last quarter's traffic and last
   quarter's failures.
:::

:::note Time to competence
**3--4 weeks** to build a good harness for one system, and it is the highest
return on investment in this entire map. Most of the skill is judgement about
what to measure, which you acquire by reading failures.
:::

:::recap
- Teams are bottlenecked by the inability to tell whether a change helped;
  evaluation is the fix and it is learnable in weeks.
- Build a versioned golden set from real traffic, including hard cases and
  cases that should be declined; grow it from every production failure.
- Prefer rule-based graders; use LLM judges with written rubrics, pairwise
  comparison, position randomisation, and validation against human labels.
- Report confidence intervals, use paired tests, and compute the sample size
  before claiming an improvement.
- Measure components as well as end-to-end, or you cannot localise a
  regression.
- Public benchmarks choose a base model; only your own set measures your
  system.
- Read fifty failures by hand and maintain a taxonomy. There is no substitute.
:::
