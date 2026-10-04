# The Learning Problem
@short: The Learning Problem
@subtitle: Generalisation, and the decomposition that explains every model failure
@tier: foundation
@prereq: Chapter 10
@blurb: Before any algorithm: what is a model actually doing, and why should it work on data it has never seen? This chapter builds the answer --- the bias--variance decomposition, the role of capacity, what regularisation really does, and how to set up an evaluation that will not lie to you. Every later chapter is an instance of what is here.
@objectives:
- State precisely what generalisation is and what makes it possible
- Decompose error into bias, variance and noise, and diagnose which dominates
- Design splits that answer the question you are actually asking
- Explain regularisation as a constraint on the hypothesis space
- Recognise double descent and why "more capacity overfits" is incomplete

## What a model is trying to do

You have samples $(x_i, y_i)$ drawn from an unknown distribution $\mathcal{D}$.
You want a function $f$ minimising the **expected** loss on *new* draws:

$$R(f) = \mathbb{E}_{(x,y) \sim \mathcal{D}}[\ell(f(x), y)]$$

You cannot compute that. You can compute the **empirical** loss on your sample:

$$\hat{R}(f) = \frac{1}{n}\sum_{i=1}^{n} \ell(f(x_i), y_i)$$

Everything in machine learning is about the gap between these two numbers. A
model that drives $\hat R$ to zero by memorising tells you nothing about $R$.

:::insight Why generalisation is possible at all
Nothing forces an arbitrary function fitted to $n$ points to do anything
sensible elsewhere --- there are infinitely many functions agreeing on your
data and disagreeing everywhere else. Learning works only because we restrict
the hypothesis space to functions with *structure*: smooth, low-degree,
sparse, compositional.

That restriction is called **inductive bias**, and every model is a bet about
what structure the world has. A convolution bets on translation invariance;
a tree bets on axis-aligned piecewise-constant structure; a transformer bets
that the relevant context is retrievable by content. Choosing a model class
*is* choosing a prior.
:::

## The decomposition

For squared loss, expected error at a point $x$ decomposes exactly:

$$\text{error}(x) \;=\; \text{bias}(x)^2 \;+\; \text{variance}(x) \;+\; \sigma^2$$

$$\text{bias}(x) = \mathbb{E}[f(x)] - f^*(x), \qquad \text{variance}(x) = \mathbb{E}\big[(f(x) - \mathbb{E}[f(x)])^2\big]$$

Here $f$ is the model fitted to one training sample and the expectation runs
over *which sample you drew*; $f^*$ is the truth and $\sigma^2$ is the label
noise.

- **Bias**: error from your model class being unable to represent $f^*$.
  Systematic. Unaffected by more data.
- **Variance**: error from sensitivity to which particular sample you drew.
  Reduced by more data, by averaging, by regularisation.
- **Noise**: irreducible. The label is not a deterministic function of the
  features.

@fig: bias_variance | 162 | Error against model capacity. The classical picture on the left --- the U-shape --- is the one everyone is taught. The right-hand region is the modern one: past the interpolation threshold, test error can fall again.

:::intuition Diagnosing which one you have, in thirty seconds
Plot training error and validation error against training-set size.

- **Both high, converged, close together** → high bias. The model class is too
  simple. More data will not help. Add capacity or features.
- **Training low, validation much higher, gap not closing** → high variance.
  More data *will* help. So will regularisation and simplification.
- **Both low and close** → you are done, or you have leakage. Check leakage.
- **Validation below training** → you have a bug, almost certainly a
  distribution difference between the splits (or dropout still on at eval).

This one plot --- the learning curve --- answers "should I collect more data?"
which is usually the most expensive question in the project.
:::

## Splits that answer the right question

| Split | Answers | Use when |
|---|---|---|
| Random | "does it work on more of the same?" | i.i.d. data, no time, no groups |
| Temporal | "will it work next month?" | any data with time — the default |
| Group / entity | "will it work on a new user?" | repeated measurements per entity |
| Stratified | as random, with rare classes preserved | class imbalance |
| Nested CV | "how good is my model *selection*?" | small data, many hyperparameters |

@tbl: Choosing a split. A random split on temporal data is the most common evaluation error in applied ML, and it always flatters the model.

```python title="Three splits, and how differently they score"
from sklearn.model_selection import (train_test_split, TimeSeriesSplit,
                                     GroupKFold)

# Random — optimistic on temporal data
Xtr, Xte = train_test_split(X, test_size=0.2, random_state=0)

# Temporal — the honest one when time exists
for tr, te in TimeSeriesSplit(n_splits=5).split(X):
    ...

# Group — the honest one when entities repeat
for tr, te in GroupKFold(n_splits=5).split(X, y, groups=user_ids):
    ...
```

:::warning Three splits, not two
`train` fits parameters. `validation` selects hyperparameters and model
variants. `test` is touched **once**, at the end.

Every time you look at the test set and change something, it becomes part of
your training procedure. After twenty such decisions, your test score is an
optimistic estimate of a model selected to do well on that specific set. This
is the same multiple-comparisons problem as Chapter 10, and the discipline is
the only fix: lock the test set away, and if you must re-use it, report how
many times you have.
:::

## Regularisation

Every regulariser does the same thing: it shrinks the set of functions the
optimiser can reach, trading a little bias for a lot of variance.

| Method | Mechanism | Also does |
|---|---|---|
| L2 / weight decay | penalises $\|w\|_2^2$ | shrinks correlated weights together |
| L1 | penalises $\|w\|_1$ | selects features (exact zeros) |
| Early stopping | limits optimisation time | approximately L2 for linear models |
| Dropout | random unit deletion | approximates an ensemble |
| Data augmentation | enlarges the training set | encodes invariances you know about |
| Label smoothing | softens targets | improves calibration |
| Ensembling | averages models | reduces variance, never bias |
| More data | shrinks the feasible set | the best regulariser, if available |

@tbl: Regularisers and what they actually do. Note the last row: nothing beats more data, and much of the value of augmentation is that it is a cheap approximation to it.

```python title="Why L1 selects and L2 shrinks, geometrically"
# Minimising loss subject to ||w||_1 <= t: the constraint region is a diamond
# with corners ON the axes, so the optimum frequently lands on a corner —
# and a corner has coordinates that are exactly zero.
#
# Minimising subject to ||w||_2 <= t: the region is a sphere, which has no
# corners, so the optimum almost never has an exact zero.
#
# This is the entire explanation, and it generalises: the "sharpness" of the
# constraint set at the axes is what produces sparsity.
```

## Double descent, and why "more capacity overfits" is incomplete

The classical U-curve says test error rises once capacity passes the sweet
spot. That is true up to the **interpolation threshold** --- the capacity at
which the model can fit the training data exactly. Past it, test error often
falls again, sometimes below the classical minimum.

The reason is that among the many parameter settings that interpolate the
data, gradient descent finds one with small norm --- an implicit
regularisation. Very large models are therefore not "overfitting" in the
classical sense; they are in a different regime.

:::warning What this does and does not license
It licenses training models far larger than the classical picture suggests,
which is what modern deep learning does.

It does **not** license skipping evaluation, ignoring leakage, or assuming a
bigger model is automatically better on your tabular dataset with 8000 rows.
The interpolation threshold for a small structured dataset is reached early,
and in the classical regime the U-curve still holds --- which is why
gradient-boosted trees, with careful capacity control, still win there.
:::

:::practice The task
On a dataset of yours: (a) plot learning curves (train and validation error
against training-set size) and classify the regime; (b) score the same model
with random, temporal and group splits and report all three --- quantify the
optimism of the random split; (c) sweep an L1 penalty and plot the number of
non-zero coefficients against the penalty; (d) sweep model capacity well past
the point where training error hits zero, and look for double descent;
(e) count how many times you have looked at your test set this project, and be
honest about it.

**You have this skill when** you can look at a learning curve and say whether
more data will help, and when your reported test score comes from a set you
touched once.
:::

:::exercise
1. Derive the bias--variance decomposition for squared loss from the
   definition.
2. Fit polynomials of degree 1 to 20 on 30 noisy points and plot train and
   test error. Identify the classical U.
3. † Construct a dataset where a random split scores 0.95 and a temporal split
   scores 0.70, and explain the mechanism.
4. Show empirically that early stopping and L2 give similar solutions for
   linear regression. State the condition under which they coincide.
5. Demonstrate the L1/L2 geometry in two dimensions by plotting the constraint
   regions and the loss contours.
6. † Reproduce double descent on a small model: sweep width past the
   interpolation threshold and plot test error.
7. Simulate the test-set-reuse problem: select the best of 50 models on the
   test set and measure how much its score overstates fresh performance.
:::

:::recap
- Learning is about the gap between empirical and expected loss; it works only
  because we restrict the hypothesis space, and that restriction is the
  model's inductive bias.
- Error is bias plus variance plus noise; the learning curve tells you which
  dominates and therefore whether more data will help.
- Split by time when there is time, by group when entities repeat; a random
  split on temporal data always flatters.
- Three splits, not two --- and the test set is touched once.
- Every regulariser trades bias for variance; L1's sparsity comes from the
  corners of its constraint region.
- Past the interpolation threshold, test error can fall again --- but the
  classical regime still governs small structured datasets.
:::
