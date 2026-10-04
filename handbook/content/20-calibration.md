# Calibration, Thresholds and Costs
@short: Calibration
@subtitle: Turning a score into a decision that is worth making
@tier: core
@prereq: Chapter 10
@blurb: A model outputs a number. A business needs a decision. Everything between the two --- whether the number means what it claims, where to put the threshold, what an error costs --- is where most of the realised value of a model is won or lost, and it is the part most often skipped. This chapter covers it properly.
@objectives:
- Test whether your model's probabilities are calibrated, and fix them if not
- Choose a threshold from an explicit cost matrix rather than by maximising F1
- Choose the right metric for imbalanced problems
- Handle class imbalance without breaking calibration
- Design the decision policy, including the option to abstain

## Calibration: does 0.8 mean 0.8?

A model is **calibrated** if, among all predictions of 0.8, about 80% are
positive. Ranking metrics like AUC are entirely blind to this: a model can
rank perfectly and be wildly miscalibrated, because AUC depends only on
order.

```python title="Measuring calibration"
from sklearn.calibration import calibration_curve
import numpy as np

def ece(y_true, y_prob, n_bins=15):
    """Expected calibration error: mean |accuracy - confidence| over bins."""
    bins = np.linspace(0, 1, n_bins + 1)
    idx = np.digitize(y_prob, bins[1:-1])
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.sum() == 0:
            continue
        total += m.mean() * abs(y_true[m].mean() - y_prob[m].mean())
    return total

print(f"ECE = {ece(y_val, p_val):.4f}")        # < 0.02 is good, > 0.10 is bad
frac_pos, mean_pred = calibration_curve(y_val, p_val, n_bins=15)
```

@fig: calibration_curve | 148 | Reliability diagrams. The diagonal is perfect calibration. A random forest cannot reach the extremes --- averaging votes keeps it away from 0 and 1 --- so its curve is steeper than the diagonal and it is *under*-confident at the ends. A modern neural network sits below the diagonal: over-confident. Logistic regression is close to calibrated by construction, because that is exactly what its loss optimises.

| Model | Typical calibration | Why |
|---|---|---|
| Logistic regression | good | log loss *is* a proper scoring rule for probabilities |
| Gradient boosting (log loss) | usually fair | strong shrinkage pulls predictions towards the middle |
| Random forest | under-confident near 0 and 1 | averaging votes cannot reach the extremes |
| SVM | uncalibrated (not a probability) | the decision value is a margin, not a probability |
| Neural network | over-confident | trained to near-zero loss on the training set |

@tbl: Calibration by model family. Two directions, not one: ensembles of the averaging kind are *under*-confident at the extremes, while networks trained to near-zero training loss are *over*-confident. Note the SVM row: `decision_function` is not a probability, and treating it as one is a category error.

```python title="Two fixes, both fitted on held-out data"
from sklearn.calibration import CalibratedClassifierCV

# Platt scaling: fit a 1-D logistic regression on the model's scores.
# Two parameters. Right when the miscalibration is sigmoid-shaped.
cal = CalibratedClassifierCV(model, method="sigmoid", cv="prefit")

# Isotonic regression: fit a free monotone function.
# More flexible, needs ~1000+ calibration samples or it overfits.
cal = CalibratedClassifierCV(model, method="isotonic", cv="prefit")

cal.fit(X_calib, y_calib)      # a split used for NOTHING else
```

:::warning Calibrate on data the model has not seen
Fitting the calibrator on training predictions calibrates against the model's
*memorised* confidence, which is much higher than its confidence on new data.
The result is a calibrator that makes things worse.

Use a dedicated calibration split, or `cv=5` (which does it out of fold).
And recalibrate after any change to the base rate --- calibration is a
property of the model *and the population*, not of the model alone.
:::

## Thresholds: from probability to decision

:::pitfall 0.5 is almost never the right threshold
0.5 is the optimal threshold only when a false positive and a false negative
cost exactly the same and the classes are balanced. Neither is typically true.

Maximising F1 is not the answer either: F1 encodes the assumption that
precision and recall are equally important, which is a statement about costs
that you almost certainly have not checked.
:::

The right procedure is to write down what errors cost and optimise that.

```python title="Threshold from a cost matrix — the whole method"
import numpy as np

# Fraud detection, in the currency of the problem:
COST_FN = 500.0     # a missed fraud: we refund the customer
COST_FP =  15.0     # a false alarm: manual review, some customer annoyance
VALUE_TP = 500.0    # a caught fraud: the loss avoided

def expected_value(y_true, y_prob, t):
    pred = y_prob >= t
    tp = ((pred == 1) & (y_true == 1)).sum()
    fp = ((pred == 1) & (y_true == 0)).sum()
    fn = ((pred == 0) & (y_true == 1)).sum()
    return VALUE_TP * tp - COST_FP * fp - COST_FN * fn

ts = np.linspace(0.01, 0.99, 99)
vals = [expected_value(y_val, p_val, t) for t in ts]
best = ts[int(np.argmax(vals))]
print(f"optimal threshold {best:.2f}, expected value {max(vals):,.0f}")
```

:::insight The analytic answer, and what it tells you
For a calibrated model, the expected-value-optimal threshold is

$$t^* = \frac{C_{FP}}{C_{FP} + C_{FN}}$$

With $C_{FP} = 15$ and $C_{FN} = 500$, that is $t^* = 0.029$ --- flag anything
above a 3% chance of fraud. Nowhere near 0.5.

Two consequences follow. First, **calibration is a prerequisite for threshold
selection**: the formula is meaningless if 0.029 does not mean a 2.9%
chance. Second, the threshold is a *business* parameter, not a model
parameter, and it should be re-derived whenever the costs change --- without
retraining anything.
:::

## Metrics for imbalanced problems

| Metric | Use when | Do not use when |
|---|---|---|
| Accuracy | balanced, equal costs | almost ever, in practice |
| ROC-AUC | comparing rankers, balanced-ish | prevalence < ~5%: it looks great regardless |
| PR-AUC | rare positives | comparing across different base rates |
| Precision@k | you can only action $k$ items | the capacity is not fixed |
| Recall@precision=p | you have a precision floor (SLA) | no such constraint exists |
| Expected value | you know the costs | you genuinely do not know them |
| Brier / log loss | you need probabilities | you only need a ranking |

@tbl: Metric selection. Two rules do most of the work: ROC-AUC is misleadingly flattering when positives are rare, because the huge negative class makes the false-positive rate tiny; and if you can write down costs, expected value dominates every other choice because it measures the thing you care about.

```python title="Why AUC misleads on rare positives"
# 1,000,000 negatives, 1,000 positives (0.1% prevalence).
# A model flags 10,000 items and catches 500 of them.
#   Recall    = 500 / 1000        = 50%
#   Precision = 500 / 10000       = 5%      <- one useful alert in twenty
#   FPR       = 9500 / 1000000    = 0.95%   <- looks excellent
# ROC-AUC can exceed 0.95 here. The precision-recall curve tells the truth.
```

## Class imbalance: what to do and what it costs

| Approach | Effect on ranking | Effect on calibration |
|---|---|---|
| Do nothing, tune the threshold | best | preserved |
| `class_weight="balanced"` | usually slight gain | **destroyed** |
| Random undersampling | can help; loses data | destroyed (shifts base rate) |
| SMOTE / synthetic oversampling | rarely helps on tabular | destroyed |
| Focal loss | helps on extreme imbalance | distorted |

@tbl: Imbalance handling. The first row is the honest default and is right far more often than the literature suggests. Resampling changes the base rate, so probabilities no longer mean what they say --- which breaks the threshold formula above.

:::insight Prior correction, when you must resample
If you undersample negatives by a factor $r$, you can recover calibrated
probabilities analytically:

$$p_{\text{true}} = \frac{p_{\text{resampled}}}{p_{\text{resampled}} + (1 - p_{\text{resampled}})/r}$$

Apply this, then check the ECE. In most cases it is simpler not to resample at
all: modern GBDT implementations handle 1000:1 imbalance without complaint,
and the threshold does the work.
:::

## The decision policy

The output of this chapter is not a threshold --- it is a policy, and the
policy usually has three actions rather than two.

```python title="A three-way policy with an abstain band"
def decide(p, t_low=0.02, t_high=0.60):
    if p >= t_high:
        return "block"              # act automatically
    if p >= t_low:
        return "review"             # send to a human
    return "allow"                  # act automatically

# The review band is sized by the REVIEW CAPACITY, not by the model:
#   given 40 reviewers at 200 cases/day, capacity is 8,000/day,
#   so t_low is the quantile of p that yields 8,000 cases.
```

Abstention is usually the highest-value change available, because it lets the
model act confidently where it is confident and defer where it is not. It also
gives you a stream of human labels on exactly the ambiguous cases, which is
the best training data you can get (Chapter 37).

:::practice The task
On an imbalanced classification problem: (a) plot a reliability diagram and
compute ECE before and after Platt and isotonic calibration; (b) write down a
real cost matrix with your stakeholders and find the expected-value-optimal
threshold; compare it to 0.5 and to the F1-maximising threshold, in money;
(c) compare ROC-AUC and PR-AUC as you vary the prevalence by subsampling;
(d) train with and without `class_weight="balanced"` and measure the effect on
both ranking and calibration; (e) design a three-way policy sized to a real
review capacity.

**You have this skill when** your model ships with a threshold you can justify
in the currency of the problem, and a reliability diagram to back it up.
:::

:::exercise
1. Construct a model with AUC 1.0 and terrible calibration. Explain why AUC
   cannot see it.
2. Derive $t^* = C_{FP}/(C_{FP}+C_{FN})$ for a calibrated model.
3. † Fit isotonic calibration on 200 samples and on 5000, and show the
   overfitting on the smaller set.
4. Plot ROC-AUC and PR-AUC as prevalence falls from 50% to 0.1% by
   subsampling positives. Explain the divergence.
5. Show that `class_weight="balanced"` destroys calibration, then recover it
   with the prior-correction formula.
6. † Compute the expected value of a three-way policy against the best
   two-way policy, as a function of review capacity. Find the capacity at
   which review stops paying.
7. Your costs change (a false positive now costs 60 instead of 15). Update the
   deployed system correctly without retraining, and state what you changed.
:::

:::recap
- Calibration means the numbers mean what they say; AUC is blind to it.
- Boosted trees and neural networks are systematically over-confident; fix
  with Platt (sigmoid-shaped error) or isotonic (needs ~1000+ samples), fitted
  on held-out data.
- 0.5 is almost never the right threshold, and maximising F1 is an unexamined
  statement about costs. Use $t^* = C_{FP}/(C_{FP}+C_{FN})$.
- Calibration is a prerequisite for threshold selection.
- ROC-AUC flatters on rare positives; use PR-AUC or expected value.
- Resampling and class weighting destroy calibration; prefer tuning the
  threshold, or apply the prior correction.
- The deliverable is a decision policy, usually with an abstain band sized by
  human review capacity.
:::
