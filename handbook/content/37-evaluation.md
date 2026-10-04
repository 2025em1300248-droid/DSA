# Evaluation
@short: Evaluation
@subtitle: The skill that is scarcest, and the one that makes everything else work
@tier: core
@prereq: Chapter 10
@blurb: Most teams building on foundation models cannot tell whether a change helped. That single gap caps the quality of everything downstream: you cannot improve what you cannot measure, and you cannot ship confidently what you have not measured. This chapter builds an evaluation system from the golden set upward.
@objectives:
- Build and maintain a golden set that reflects real usage
- Choose the right grader for each task, cheapest first
- Validate an LLM judge against human labels before trusting it
- Wire evaluation into CI so regressions cannot merge
- Evaluate components as well as end-to-end behaviour

## The golden set

@fig: eval_system | 168 | The evaluation system. Production traffic feeds the golden set, the golden set gates deployment, and failures in production return to the golden set. The loop is the point; a static evaluation set decays.

:::checklist What a usable golden set contains
- **100--1000 cases.** Below 100 you cannot detect anything under about ten
  points (Chapter 10). Above 1000 the marginal case buys little.
- **Drawn from real traffic**, not invented. Invented cases test what you
  imagined; real ones test what happens.
- **Stratified by case type**, with counts you choose deliberately --- not the
  natural frequency, which buries the hard cases.
- **Hard cases over-represented.** Ambiguous inputs, multi-part questions,
  out-of-scope requests, adversarial inputs.
- **Cases that should be refused**, with the expected refusal.
- **Expected outputs or a grading rubric** --- written before you see the
  model's answer, or you will rationalise.
- **Versioned in git**, alongside the code it evaluates.
:::

```python title="A case, with everything needed to grade it"
{
  "id": "refund-policy-partial-0042",
  "input": "Can I return a used blender after 40 days?",
  "category": "policy_lookup",
  "difficulty": "hard",            # the window is 30 days, but used is 14
  "expected": {
      "must_contain": ["14 days", "used"],
      "must_not_contain": ["30 days"],
      "should_refuse": false,
      "must_cite": ["returns-policy#used-items"]
  },
  "rubric": "States the 14-day used-item window, does not quote the 30-day "
            "new-item window as if it applied, and cites the used-items "
            "section.",
  "source": "production-2026-03-14",
  "added_because": "model quoted the 30-day window for a used item"
}
```

The `added_because` field is what keeps the set honest: every case should
exist for a reason, and most of them should be production failures.

## Graders, cheapest first

| Grader | Cost | Reliability | Use for |
|---|---|---|---|
| Exact match | free | perfect | classification, extraction with a fixed answer |
| Schema / regex | free | perfect | format, identifiers, structure |
| Programmatic check | free | perfect | code that runs, SQL that matches, arithmetic |
| Fuzzy / embedding similarity | cheap | moderate | paraphrase tolerance --- but set the threshold by hand |
| **LLM judge** | moderate | good *if validated* | open-ended quality, faithfulness, tone |
| Human | expensive | the reference | judge validation, and final sign-off |

@tbl: Always use the cheapest grader that can answer the question. Teams reach for an LLM judge on tasks a regex would grade perfectly, and then spend their budget on grading rather than on improving.

```python title="A composite grader"
def grade(case, output):
    e = case["expected"]
    checks = {}
    checks["contains"] = all(s.lower() in output.lower()
                             for s in e.get("must_contain", []))
    checks["excludes"] = not any(s.lower() in output.lower()
                                 for s in e.get("must_not_contain", []))
    checks["refusal"] = (is_refusal(output) == e.get("should_refuse", False))
    checks["cited"] = all(c in extract_citations(output)
                          for c in e.get("must_cite", []))
    if case.get("rubric"):
        checks["rubric"] = judge(case["input"], output, case["rubric"])
    return all(checks.values()), checks      # keep the per-check breakdown
```

Returning the per-check breakdown is what makes a failing run actionable: you
learn *which* property broke, not merely that the score fell.

## LLM judges

```python title="A judge prompt with the properties that make it reliable"
JUDGE = """\
You are grading one response against a rubric. Be strict.

<question>{question}</question>
<response>{response}</response>
<rubric>{rubric}</rubric>

Work through the rubric point by point, then give a verdict.

Respond in this exact format:
ANALYSIS: <one sentence per rubric point>
VERDICT: PASS or FAIL
"""
```

:::checklist Six properties of a judge you can trust
1. **A written rubric**, not "is this good?". Vague prompts give vague
   judgements and poor agreement.
2. **Reasoning before the verdict.** Field order is generation order
   (Chapter 32); a verdict emitted first is not grounded in anything.
3. **Binary or a short ordinal scale.** Judges cannot distinguish 7 from 8 on
   a ten-point scale; the extra resolution is noise.
4. **Pairwise where possible.** "Which is better, A or B?" is markedly more
   reliable than absolute scoring --- the same asymmetry as Chapter 36.
5. **Randomised order** in pairwise comparison. Judges have a position bias;
   run both orders and discard inconsistent pairs.
6. **Validated against humans** before use. Without this the judge is an
   unmeasured instrument.
:::

```python title="Judge validation — do this before trusting any judge number"
def validate_judge(cases, human_labels, judge_fn):
    judge_labels = [judge_fn(c) for c in cases]
    agree = sum(a == b for a, b in zip(judge_labels, human_labels))
    n = len(cases)
    # Cohen's kappa: agreement corrected for chance.
    p_obs = agree / n
    p_j = sum(judge_labels) / n
    p_h = sum(human_labels) / n
    p_exp = p_j * p_h + (1 - p_j) * (1 - p_h)
    kappa = (p_obs - p_exp) / (1 - p_exp)
    return dict(agreement=p_obs, kappa=kappa,
                false_pass=sum(j and not h for j, h in zip(judge_labels, human_labels)) / n,
                false_fail=sum(h and not j for j, h in zip(judge_labels, human_labels)) / n)

# Target: agreement > 0.85 and kappa > 0.6 on at least 50 human-labelled cases.
# Below that, fix the rubric — do not adjust the threshold until it passes.
```

:::warning Judge biases that are real and measurable
**Position bias.** In pairwise comparison, judges favour one position. Run
both orders; if the verdicts disagree, the pair is a tie.

**Length bias.** Longer answers score higher at equal quality --- the same
effect as in Chapter 36. Check by plotting score against length.

**Self-preference.** A judge tends to prefer outputs from its own model
family. Use a different model as judge where you can.

**Over-leniency.** Judges pass borderline answers unless told to be strict and
given an explicit failure condition in the rubric.
:::

## Statistics

Everything in Chapter 10 applies, and two points bear repeating because they
are routinely ignored here.

```python title="Report an interval and use a paired test"
from scipy import stats
import numpy as np

def compare(baseline, candidate):
    b, c = np.array(baseline), np.array(candidate)      # per-case 0/1, same cases
    n01 = int(((b == 1) & (c == 0)).sum())              # baseline right, new wrong
    n10 = int(((b == 0) & (c == 1)).sum())              # new right, baseline wrong
    result = stats.binomtest(n10, n01 + n10, 0.5)       # exact McNemar
    return dict(baseline=b.mean(), candidate=c.mean(),
                delta=c.mean() - b.mean(),
                improved=n10, regressed=n01, p=result.pvalue)
```

The `regressed` count is the number people forget to look at. A change that
improves 40 cases and regresses 35 has a positive mean and is almost certainly
noise --- and the 35 regressions are real users with worse answers.

## Evaluation in CI

```yaml title="Gate the merge, not just the release"
- name: Fast evaluation
  run: |
    uv run python -m evals.run \
      --suite golden-fast --n 120 \
      --baseline artifacts/baseline.json \
      --fail-on-regression 0.03 \
      --fail-on-any-regression-in critical_safety
```

| Suite | Size | When | Gates |
|---|---|---|---|
| Smoke | 20 | every commit | obvious breakage |
| Fast | 100--150 | every PR | regressions over 3 points |
| Full | 500--1000 | nightly / pre-release | the release decision |
| Safety | 200 | every PR | **any** regression |
| Adversarial | 100 | weekly | injection, jailbreak (Chapter 44) |

@tbl: A five-suite ladder. The safety row is the one with a different rule: an average that stays flat while a safety case regresses is not acceptable, so that suite gates on *any* regression rather than on the mean.

:::insight Component evaluation localises the failure
End-to-end scores tell you *that* something broke. Component scores tell you
*what*.

For a RAG pipeline: recall@k for retrieval, faithfulness for generation,
citation accuracy for attribution (Chapter 34). For an agent: tool-selection
accuracy, argument validity, step count, task completion (Chapter 38 of the
Skill Map; here Chapter 32's loop). For a classifier: per-class precision and
recall, not just the macro average.

The rule: every stage that could independently fail gets its own number.
:::

:::practice The task
Build an evaluation system for something you run. (a) Assemble 150 cases from
real traffic, stratified, with hard cases over-represented and an
`added_because` on every one. (b) Implement the cheapest grader that works for
each category. (c) Write a judge for the open-ended cases, hand-label 60, and
report agreement and kappa --- iterate on the rubric until kappa exceeds 0.6.
(d) Wire the fast suite into CI with a regression gate. (e) Run a paired
comparison between two prompt versions and report improved, regressed and the
p-value. (f) Add component metrics so a failure names its stage.

**You have this skill when** a pull request that degrades quality cannot be
merged, and when a failing run tells you which component broke.
:::

:::exercise
1. Build a golden set from production logs and report its stratification.
   Which category is under-represented relative to its importance?
2. Replace an LLM judge with a programmatic check on one category. Measure the
   cost and reliability change.
3. † Measure your judge's position bias by running 100 pairwise comparisons in
   both orders. Report the inconsistency rate.
4. Plot judge score against response length. Quantify the length bias and
   correct for it.
5. Validate a judge against 60 human labels. Report agreement, kappa, false
   pass and false fail. Improve the rubric and repeat.
6. † Construct a change that improves the mean and regresses 30 cases. Show
   the paired test's verdict and argue whether to ship it.
7. Add component metrics to a pipeline of yours and find a case where the
   end-to-end score hides a component regression.
:::

:::recap
- A golden set is 100--1000 real, stratified cases with hard ones
  over-represented, expected outputs written before seeing the model's answer,
  and a reason recorded for each.
- Use the cheapest grader that answers the question; exact match and
  programmatic checks are free and perfect.
- An LLM judge needs a written rubric, reasoning before the verdict, a binary
  or short scale, pairwise where possible, randomised order, and validation
  against humans (agreement > 0.85, kappa > 0.6).
- Judges have position, length and self-preference biases, and are lenient by
  default.
- Report improved *and* regressed counts with a paired test, not just the
  mean.
- Gate merges with a fast suite; gate safety on any regression at all.
- Every stage that can independently fail gets its own metric.
:::
