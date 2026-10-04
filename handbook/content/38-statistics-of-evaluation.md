# The Statistics of Evaluation
@short: Eval Statistics
@subtitle: How many examples, how big an effect, and whether to believe it
@tier: advanced
@prereq: Chapters 10, 37
@blurb: Evaluation numbers are estimates, and treating them as measurements is how teams ship regressions and chase noise. This chapter is the statistical layer under Chapter 37: sizing a set before you build it, handling the dependence that real evaluation data has, correcting for repeated testing, and reporting in a way that survives scrutiny.
@objectives:
- Size an evaluation set for the effect you need to detect
- Handle clustered and non-independent cases correctly
- Correct for the many comparisons an iterating team actually makes
- Account for grader error in your intervals
- Report results so a sceptical reader can check them

## Sizing, before you build the set

```python title="Work out the size first; building 1000 cases is expensive"
import math
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

def n_unpaired(p_base, p_target, alpha=0.05, power=0.80):
    return NormalIndPower().solve_power(
        effect_size=proportion_effectsize(p_target, p_base),
        alpha=alpha, power=power, ratio=1.0)

def n_paired(delta, sd_diff=0.10, alpha=0.05, power=0.80):
    """delta: the accuracy difference you want to detect.
       sd_diff: sd of the per-case difference — measure it from a pilot."""
    z_a, z_b = 1.959964, 0.841621
    return math.ceil(((z_a + z_b) * sd_diff / delta) ** 2)

print(n_unpaired(0.82, 0.85))     # ≈ 1200 per group
print(n_paired(0.03))             # ≈ 88 cases, evaluated twice
```

:::insight Measure `sd_diff` from a pilot rather than guessing
The paired sample size depends entirely on how much the two systems disagree
*per case*. Run both on 50 cases, compute the standard deviation of the
per-case difference, and plug it in. For systems that mostly agree it is
around 0.1; for systems that differ substantially it can be 0.3, and the
required $n$ is then nine times larger.

The pilot costs an hour and prevents the two usual outcomes: a set too small
to detect anything, or ten times more labelling than the question needed.
:::

## Dependence: the error that inflates confidence

Evaluation sets are rarely independent. Five questions about one document,
thirty paraphrases of one intent, a hundred cases generated from ten
templates --- in each case the effective sample size is far below the row
count.

```python title="Cluster bootstrap: resample groups, not rows"
import numpy as np

def cluster_bootstrap_ci(scores, groups, n_boot=10_000, conf=0.95, seed=0):
    rng = np.random.default_rng(seed)
    scores, groups = np.asarray(scores), np.asarray(groups)
    uniq = np.unique(groups)
    index = {g: np.flatnonzero(groups == g) for g in uniq}

    boots = np.empty(n_boot)
    for i in range(n_boot):
        picked = rng.choice(uniq, len(uniq), replace=True)   # resample CLUSTERS
        idx = np.concatenate([index[g] for g in picked])
        boots[i] = scores[idx].mean()
    lo, hi = np.percentile(boots, [(1-conf)/2*100, (1+conf)/2*100])
    return scores.mean(), lo, hi
```

| Set | Rows | Per cluster | Intra-cluster $\rho$ | Interval is wider by |
|---|---|---|---|---|
| 5 questions × 40 documents | 200 | 5 | 0.3 | 1.5× |
| 5 questions × 40 documents | 200 | 5 | 0.7 | 1.9× |
| 10 paraphrases × 30 intents | 300 | 10 | 0.5 | 2.3× |
| independent cases | 200 | 1 | — | 1.0× |

@tbl: The widening factor is $\sqrt{1 + (m-1)\rho}$ for $m$ cases per cluster and intra-cluster correlation $\rho$ --- the *design effect*. Ignoring clustering can halve the reported interval, which is exactly how a team concludes a difference is significant when it is not. Estimate $\rho$ from your own set; it is usually between 0.3 and 0.8 for questions about the same document.

:::pitfall Near-duplicates are clusters you did not notice
A set assembled from production logs usually contains many
near-identical queries. Deduplicate before computing intervals: embed the
inputs, cluster at high similarity (Chapter 16's MinHash works here too), and
treat each cluster as one unit. Teams are routinely surprised by how much
their 500-case set shrinks.
:::

## Multiple comparisons, as they actually occur

You do not run one test. Over a quarter you try fifty prompt variants, eight
retrieval configurations, three models and a dozen parameter settings ---
keeping the best at each step, measured on the same set.

```python title="Benjamini–Hochberg: the right default for screening"
def benjamini_hochberg(pvalues, fdr=0.10):
    """Returns the indices of the hypotheses to accept."""
    p = sorted((pv, i) for i, pv in enumerate(pvalues))
    m, keep = len(p), []
    for rank, (pv, i) in enumerate(p, start=1):
        if pv <= fdr * rank / m:
            keep = [j for _, j in p[:rank]]
    return keep
```

| Correction | Controls | Use when |
|---|---|---|
| None | nothing | you genuinely tested one hypothesis |
| Bonferroni ($\alpha/m$) | family-wise error | few tests, errors are costly |
| **Benjamini--Hochberg** | false discovery rate | screening many variants --- the usual case |
| Held-out confirmation set | everything | **the best answer when you can afford it** |

@tbl: The bottom row dominates the others. Select on a development set with no correction at all, then confirm the single winner on a set you have never optimised against. One number, one test, nothing to correct.

:::warning The development set wears out
Every decision made by looking at a set fits your system to it a little more.
After a few months of iteration, the development score overstates true
performance --- often by several points.

Three mitigations: keep a sealed confirmation set and touch it only at release
(and record how many times you have); refresh the development set from recent
production traffic each quarter; and track the *gap* between development and
confirmation scores over time, because a widening gap is the signal that
overfitting has set in.
:::

## Grader error propagates

If your judge agrees with humans 90% of the time, a measured score of 0.85
is not 0.85 under human grading, and the two systems you are comparing are
each measured through the same noisy instrument.

```python title="Propagating judge error into the interval"
def adjusted_interval(measured, n, judge_fpr, judge_fnr, conf=0.95):
    """Correct a measured rate for known judge error, and widen for its
       own uncertainty. judge_fpr/fnr come from Chapter 37's validation."""
    import math
    # Rogan-Gladen correction for a misclassified binary measurement.
    sens, spec = 1 - judge_fnr, 1 - judge_fpr
    true_rate = (measured + spec - 1) / max(sens + spec - 1, 1e-6)
    true_rate = min(max(true_rate, 0.0), 1.0)
    se = math.sqrt(measured * (1 - measured) / n) / max(sens + spec - 1, 1e-6)
    z = 1.96
    return true_rate, max(0.0, true_rate - z*se), min(1.0, true_rate + z*se)
```

@fig: eval_uncertainty | 160 | Three sources of uncertainty stack: sampling (which cases you drew), clustering (how many are really independent), and grader error (whether the label is right). Reporting only the first --- which is what a naive binomial interval does --- understates the real width substantially.

:::insight Judge error affects comparisons less than absolute scores
Good news for the common case: if both systems are graded by the *same* judge,
much of its bias is shared and cancels in the difference. A paired comparison
through an imperfect judge is considerably more trustworthy than either
absolute number.

The exception is a judge whose error correlates with what changed --- for
example, a length-biased judge evaluating a change that made outputs longer.
Then the bias does not cancel, it is the entire effect. Check the confound
before believing the result.
:::

## Reporting

```
Retrieval-augmented answer accuracy
  candidate   0.847   [0.806, 0.882]
  baseline    0.812   [0.769, 0.849]
  paired difference  +0.035  [+0.012, +0.058]

  n = 420 cases in 180 clusters (cluster bootstrap, 10k resamples)
  improved 58 / regressed 43 / unchanged 319   McNemar p = 0.021
  grader: LLM judge v4, agreement 0.91, kappa 0.78 on 80 human labels
  this is the 1st evaluation of this candidate on the confirmation set
```

:::checklist What a sceptical reader needs
- The point estimate **and** an interval, with the method named.
- The sample size **and** the cluster count.
- Improved, regressed and unchanged counts --- not just the mean.
- A paired test statistic.
- The grader, and its validation numbers.
- How many times this set has been used for this decision.
:::

:::practice The task
On a real evaluation: (a) run a 50-case pilot and compute `sd_diff`, then size
the full set properly; (b) identify the clusters in your set and compare naive
and cluster-bootstrap intervals --- report how much the interval widens;
(c) deduplicate near-identical cases and report how many effective cases you
actually have; (d) take the last ten comparisons your team made and apply
Benjamini--Hochberg; how many survive? (e) propagate your judge's measured
error into an interval; (f) write one result in the full reporting format.

**You have this skill when** you can say how many cases you need before
building the set, and when your reported intervals do not shrink under
scrutiny.
:::

:::exercise
1. Compute the sample size needed to detect a 2-point difference, paired and
   unpaired, and state the ratio.
2. Simulate a clustered evaluation set and show the naive interval's actual
   coverage is below 95%.
3. † Take a production-derived evaluation set, cluster it by embedding
   similarity, and report the effective sample size.
4. Simulate 50 null comparisons and show how many appear significant at
   $\alpha = 0.05$. Apply Bonferroni and Benjamini--Hochberg and compare.
5. Simulate development-set overfitting: select the best of 100 variants on a
   fixed set and measure the gap to a fresh set.
6. † Show that a shared imperfect judge cancels in a paired comparison, and
   construct a case where it does not.
7. Rewrite one of your team's recent evaluation claims in the full reporting
   format. What was missing?
:::

:::recap
- Size the set before building it, using `sd_diff` from a pilot rather than a
  guess.
- Evaluation cases are usually clustered; resample clusters, not rows, or your
  intervals are about half as wide as they should be.
- Near-duplicates from production logs are unnoticed clusters --- deduplicate
  first.
- Correct for multiple comparisons with Benjamini--Hochberg, or better, use a
  sealed confirmation set.
- Development sets wear out; track the development-to-confirmation gap.
- Grader error widens absolute intervals but largely cancels in paired
  comparisons, unless it correlates with the change.
- Report estimate, interval, method, n, clusters, improved/regressed counts,
  test statistic, grader validation, and how many times the set has been used.
:::
