# Statistics: Estimation, Intervals and Tests
@short: Statistics
@subtitle: Knowing whether the number you just measured means anything
@tier: foundation
@prereq: Chapter 9
@blurb: An ML engineer produces numbers all day and the hard part is not producing them but deciding which differences are real. This chapter covers the statistical machinery that question needs --- confidence intervals, the bootstrap, paired tests, power, and multiple comparisons --- with the emphasis on the mistakes that actually get made rather than the ones textbooks warn about.
@objectives:
- Attach an interval to every metric you report, and know what it means
- Bootstrap an interval for any statistic, including ones with no formula
- Use paired tests, which are far more powerful on the same evaluation set
- Compute the sample size needed before running the experiment
- Recognise multiple comparisons, p-hacking and Simpson's paradox in your own work

## A number without an interval is not a result

You evaluate two systems on 200 examples. A scores 0.82, B scores 0.85.
Is B better?

The standard error of an observed proportion $p$ from $n$ samples is
$\sqrt{p(1-p)/n}$. At $p = 0.85$, $n = 200$, that is 0.025,
so a 95% interval is roughly $0.85 \pm 0.05$. The two intervals overlap
substantially. **You have not measured a difference.**

```python title="The interval that should accompany every reported metric"
import numpy as np
from scipy import stats

def proportion_ci(successes, n, conf=0.95):
    """Wilson interval — correct near 0 and 1, where the normal one is not."""
    return stats.binomtest(successes, n).proportion_ci(conf, method="wilson")

def mean_ci(xs, conf=0.95):
    xs = np.asarray(xs)
    se = xs.std(ddof=1) / np.sqrt(len(xs))
    t = stats.t.ppf((1 + conf) / 2, df=len(xs) - 1)
    return xs.mean() - t * se, xs.mean() + t * se
```

Use Wilson rather than the textbook normal interval: at $p = 0.98$ with
$n = 100$, the normal interval runs to 1.007, which is not a probability. The
Wilson interval is correct at the boundaries and costs nothing.

@fig: interval_shrink | 140 | Two systems, 200 examples each. B scores three points higher, and the 95% intervals overlap across most of their width --- so the data does not order them. The fix is more data, or (far cheaper) a paired comparison on the same items.

:::insight What a confidence interval actually says
Not "there is a 95% probability the true value is in this interval" ---
the true value is a fixed number, not a random one. It says: *the procedure
that generated this interval covers the true value 95% of the time
across repeated experiments.*

In practice the useful reading is operational: if the intervals of two systems
overlap substantially, you cannot order them from this data. If you need to
order them, get more data or use a paired test, which is usually the better
answer.
:::

## The bootstrap: intervals for anything

Many statistics have no closed-form interval: the median, a p95 latency,
recall@10, the ratio of two metrics, the output of a scoring pipeline. The
bootstrap gives you an interval for all of them with fifteen lines and no
mathematics.

The idea: your sample is your best estimate of the population, so resample
*from your sample*, with replacement, many times, and look at how much the
statistic moves.

```python title="A bootstrap that works for any statistic"
def bootstrap_ci(data, statistic, n_boot=10_000, conf=0.95, seed=0):
    rng = np.random.default_rng(seed)
    data = np.asarray(data)
    n = len(data)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        boots[i] = statistic(data[rng.integers(0, n, n)])
    lo, hi = np.percentile(boots, [(1 - conf) / 2 * 100, (1 + conf) / 2 * 100])
    return statistic(data), lo, hi

bootstrap_ci(latencies, lambda x: np.percentile(x, 95))
bootstrap_ci(scores,    np.median)
bootstrap_ci(pairs,     lambda x: recall_at_k(x, 10))
```

:::warning What the bootstrap cannot fix
It cannot repair a **biased** sample --- resampling a skewed evaluation set
gives you a precise estimate of the wrong thing. It is unreliable for
**extreme quantiles** with small $n$ (a p99 from 200 points is mostly noise
whatever you do). And it assumes examples are **independent**: if your
evaluation set contains near-duplicates, or multiple questions about the same
document, the naive bootstrap gives intervals that are too narrow. In that
case resample *clusters*, not rows.
:::

## Paired comparison: use the same examples

This is the single highest-leverage statistical technique in ML evaluation,
and it is routinely skipped.

If you evaluate A and B on the *same* examples, compare them *per example*.
Example difficulty is then differenced away, and the variance you are testing
against collapses.

```python title="Paired beats unpaired by a large factor"
# Unpaired: is mean(a) different from mean(b)?
stats.ttest_ind(a_scores, b_scores)

# Paired: is the mean of (a - b) different from zero?
stats.ttest_rel(a_scores, b_scores)

# Distribution-free version, for non-normal per-example scores:
stats.wilcoxon(a_scores, b_scores)

# For binary outcomes, McNemar's test on the disagreement counts:
#            B correct   B wrong
#  A correct     n00        n01
#  A wrong       n10        n11
# Only n01 and n10 carry information. Everything else is shared difficulty.
from statsmodels.stats.contingency_tables import mcnemar
mcnemar([[n00, n01], [n10, n11]], exact=True)
```

:::insight Why this matters so much in practice
Suppose per-example scores have standard deviation 0.4 (examples differ
wildly in difficulty) but the per-example *difference* between two systems has
standard deviation 0.1 (they usually agree). The paired test's standard error
is four times smaller, so it needs **sixteen times fewer examples** for the
same power.

Concretely: detecting a 3-point difference unpaired needs about 1200 examples
*per system*; paired, it needs about 90 --- the same examples scored twice.
This is why you always
evaluate both systems on the same fixed golden set (Chapter 37).
:::

## Power: how many examples do you need?

Compute this *before* the experiment, not after.

```python title="Sample size for a proportion difference"
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

n = NormalIndPower().solve_power(
    effect_size=proportion_effectsize(0.85, 0.82),  # what you care about
    alpha=0.05,                                      # false-positive rate
    power=0.80,                                      # 1 - false-negative rate
    ratio=1.0,
)
print(f"{n:.0f} per group")        # ≈ 1200 per group for a 3-point difference
```

Four quantities are locked together: effect size, $\alpha$, power, and $n$.
Fix any three and the fourth is determined. The number usually surprises
people --- detecting small differences is expensive, which is itself a useful
finding: if you cannot afford the sample size, you cannot make the claim, and
you should choose a bigger intervention.

| Detectable difference | Unpaired $n$ per group | Paired $n$ (sd of difference 0.10) |
|---|---|---|
| 10 points (0.75 vs 0.85) | ~125 | ~10 |
| 5 points (0.80 vs 0.85) | ~450 | ~32 |
| 3 points (0.82 vs 0.85) | ~1200 | ~90 |
| 1 point (0.84 vs 0.85) | ~10300 | ~790 |

@tbl: Sample sizes at $\alpha = 0.05$, power 0.80, computed with the arcsine effect size. The paired column assumes per-example differences with standard deviation 0.10, which is typical when two systems mostly agree. The last row is the reason "we improved by a point" is usually unverified.

## Three ways to fool yourself

:::pitfall Multiple comparisons
Test 20 hypotheses at $\alpha = 0.05$ and you expect one false positive. Try
20 prompt variants, keep the best, report its score --- and you have done
exactly this without noticing.

Corrections: **Bonferroni** ($\alpha/m$, simple and conservative) or
**Benjamini--Hochberg** (controls false discovery rate, far less
conservative and the right default for screening many variants). Better
still: hold out a separate confirmation set and re-test only the winner on it.
:::

:::pitfall Optional stopping
Checking the result each day and stopping when it becomes significant inflates
the false-positive rate dramatically --- to roughly 30% for daily checks
over two weeks at $\alpha = 0.05$. Fix the sample size in advance, or use a
method designed for continuous monitoring (sequential tests, always-valid
p-values).
:::

:::pitfall Simpson's paradox
| Segment | A | B |
|---|---|---|
| Short queries (90% of traffic) | 0.80 (900/1125) | 0.78 (78/100) |
| Long queries (10%) | 0.50 (50/100) | 0.48 (540/1125) |
| **Overall** | **0.775** | **0.504** |

A wins in *both* segments and loses overall, because the two systems received
different traffic mixes. Whenever you compare over non-randomised traffic,
segment first. This is not a curiosity; it is the normal outcome of comparing
a new model on new traffic against an old model on old traffic.
:::

## Reporting

```
Recall@10: 0.847  [0.821, 0.871]   n = 1000, Wilson 95% CI
vs baseline 0.812 [0.785, 0.837]
Paired difference: +0.035 [+0.018, +0.052], McNemar p = 0.0003
```

Three properties make this a result rather than a number: an interval, the
sample size, and a *paired* comparison against a named baseline. Anything
less is a measurement whose reliability the reader cannot assess.

:::practice The task
Take an evaluation you have run. (a) Add Wilson intervals to every reported
proportion. (b) Bootstrap an interval for a statistic that has no formula ---
p95 latency or a ranking metric. (c) Re-run your last A/B comparison as a
paired test and compare the p-value to the unpaired one. (d) Compute, before
your next experiment, the sample size needed to detect the smallest difference
you would act on. (e) Segment one comparison by traffic type and check for
Simpson's paradox.

**You have this skill when** you never report a metric without an interval,
and when someone says "we improved 1%" your first question is the sample
size.
:::

:::exercise
1. Compute the normal and Wilson intervals for 98/100 successes. Explain the
   difference.
2. Bootstrap a 95% interval for the median of 50 samples from a
   log-normal, and compare it to the interval for the mean.
3. † Construct an evaluation set with clusters (five questions per
   document) and show the naive bootstrap gives intervals that are too narrow.
   Fix it with a cluster bootstrap.
4. Simulate paired and unpaired comparisons where the per-example correlation
   is 0.9 and measure the sample size ratio needed for equal power.
5. Simulate optional stopping: run 1000 null experiments, checking daily for
   14 days, and report the observed false-positive rate.
6. † Construct a Simpson's paradox from real-looking data of your own,
   and state what randomisation would have prevented it.
7. You ran 20 prompt variants and the best scored 0.86 against a 0.82
   baseline on $n = 300$. What can you actually conclude, and what would you
   do next?
:::

:::recap
- Report an interval with every metric; use Wilson for proportions.
- The bootstrap gives an interval for any statistic, but cannot fix bias and
  needs cluster resampling when examples are not independent.
- Paired tests on the same examples difference away example difficulty and
  typically need an order of magnitude fewer samples.
- Compute power before the experiment: detecting a one-point difference
  unpaired needs tens of thousands of examples.
- Multiple comparisons, optional stopping and Simpson's paradox are the three
  ways honest people fool themselves; each has a specific remedy.
- A result is a point estimate, an interval, a sample size and a named
  baseline.
:::
