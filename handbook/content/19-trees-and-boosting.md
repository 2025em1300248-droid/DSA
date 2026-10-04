# Trees and Gradient Boosting
@short: Trees and Boosting
@subtitle: Still the right answer on tabular data, and why
@tier: core
@prereq: Chapter 17
@blurb: Gradient-boosted decision trees remain the strongest general method for tabular data, and the gap over neural networks on structured problems has not closed. This chapter builds a tree, then boosting, then the three engineering ideas --- histogram splitting, leaf-wise growth, ordered target statistics --- that make the modern implementations fast, and finishes with how to tune them without wasting a week.
@objectives:
- Implement a decision tree and understand what a split optimises
- Derive gradient boosting as functional gradient descent
- Explain histogram binning and why it changed the runtime
- Tune XGBoost, LightGBM or CatBoost in the right order
- Know why GBDTs beat neural networks on tabular data

## A tree, from scratch

A decision tree partitions feature space with axis-aligned splits and predicts
a constant in each region. Training is greedy: at each node, choose the
(feature, threshold) pair that most reduces the loss.

```python title="The core of every tree implementation"
import numpy as np

def best_split(X, g, h, lam=1.0, gamma=0.0):
    """
    Gradient-boosting split finder.
    g, h : first and second derivatives of the loss w.r.t. this node's
           prediction, per sample. For squared loss g = pred - y, h = 1.
    Returns (gain, feature, threshold).
    """
    G, H = g.sum(), h.sum()
    parent = G * G / (H + lam)
    best = (0.0, None, None)
    for j in range(X.shape[1]):
        order = np.argsort(X[:, j])
        gl = hl = 0.0
        for i in range(len(order) - 1):
            k = order[i]
            gl += g[k]; hl += h[k]
            if X[order[i], j] == X[order[i + 1], j]:
                continue                       # cannot split between equals
            gr, hr = G - gl, H - hl
            gain = 0.5 * (gl*gl/(hl+lam) + gr*gr/(hr+lam) - parent) - gamma
            if gain > best[0]:
                thr = 0.5 * (X[order[i], j] + X[order[i+1], j])
                best = (gain, j, thr)
    return best

def leaf_value(g, h, lam=1.0):
    return -g.sum() / (h.sum() + lam)          # the Newton step
```

Two things in that listing are the whole of modern boosting. The gain formula
is the *reduction in a second-order Taylor approximation of the loss*, and the
leaf value is the Newton step that minimises it. Everything else --- which
loss, which regularisation --- enters only through $g$ and $h$.

:::math Where the gain formula comes from
Expand the loss around the current prediction $\hat y$ to second order:

$$L \approx \sum_i \left[ g_i f(x_i) + \tfrac{1}{2} h_i f(x_i)^2 \right] + \tfrac{1}{2}\lambda \sum_j w_j^2$$

For a tree, $f$ is constant $w_j$ on leaf $j$, so the sum over samples becomes
a sum over leaves. Minimising a quadratic in $w_j$ gives

$$w_j^* = -\frac{G_j}{H_j + \lambda}, \qquad L^* = -\frac{1}{2}\sum_j \frac{G_j^2}{H_j + \lambda}$$

The gain from splitting one leaf into two is the difference of $L^*$ before
and after, which is exactly the expression in the code. Any twice-differentiable
loss plugs straight in --- which is why a single implementation handles
regression, classification, ranking and survival.
:::

## Boosting: functional gradient descent

$$F_0(x) = \text{constant}, \qquad F_{m}(x) = F_{m-1}(x) + \eta\, f_m(x)$$

where $f_m$ is a tree fitted to the *gradients* of the loss with respect to
the current predictions. This is gradient descent, but in function space
rather than parameter space: each tree is one step, and $\eta$ (the learning
rate, called `eta` or `learning_rate`) is the step size.

@fig: boosting_rounds | 156 | Boosting on a one-dimensional problem. Each round fits a small tree to the current residuals and adds a shrunken version of it. The ensemble approaches the target from below; shrinkage is what keeps it from overshooting.

:::pitfall Bagging and boosting are opposites
**Random forest** (bagging) trains deep, overfitting trees *independently* on
bootstrap samples and averages them. It reduces variance; it cannot reduce
bias. More trees never hurt.

**Gradient boosting** trains shallow, underfitting trees *sequentially*, each
correcting the last. It reduces bias; it can overfit. More trees eventually
hurt, which is why early stopping is mandatory.

Using random-forest intuitions on a boosted model --- "deeper trees are fine,
more trees are free" --- produces badly overfitted boosted models. The
correct boosted tree is shallow (depth 3--8).
:::

## The three engineering ideas

**Histogram binning (LightGBM, XGBoost `hist`).** Instead of considering every
distinct value as a threshold, bucket each feature into 256 bins once, up
front. Split finding then scans 256 candidates instead of $n$, and the
histograms of a node's two children can be computed by subtraction from the
parent (compute the smaller child, subtract). This took training from
$O(n \log n)$ per split to $O(\#\text{bins})$ and is why modern GBDTs train on
tens of millions of rows in minutes.

**Leaf-wise growth (LightGBM).** Grow the leaf with the highest gain rather
than growing level by level. Reaches a lower loss for the same number of
leaves --- and overfits more easily, which is why `num_leaves` must be
controlled rather than `max_depth`.

**Ordered target statistics (CatBoost).** Target encoding computed using only
each row's *predecessors* in a random permutation, which removes the leakage
of Chapter 15 by construction. This is why CatBoost handles high-cardinality
categoricals well with no manual encoding.

| | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| Growth | level-wise (or lossguide) | leaf-wise | symmetric (oblivious) |
| Categoricals | needs encoding | native | native, ordered TS |
| Speed | fast | fastest | slower to train |
| Overfit resistance | good | needs care | best default |
| Best for | the default, robust | large data, wide features | many categoricals, small data |

@tbl: Choosing an implementation. All three are excellent; the differences matter mainly at the extremes of data size and cardinality.

## Tuning, in the right order

```python title="Tune these in order; stop when the gain is inside the noise"
params = {
    # 1. Set low and leave it. Let n_estimators find itself.
    "learning_rate": 0.05,
    "n_estimators": 5000,
    "early_stopping_rounds": 100,

    # 2. Capacity. The single most important knob after the learning rate.
    "num_leaves": 31,            # LightGBM; try 15, 31, 63, 127
    "max_depth": -1,             # let num_leaves control it
    "min_child_samples": 20,     # raise to 100+ on noisy data

    # 3. Randomisation. Nearly always helps.
    "subsample": 0.8, "subsample_freq": 1,
    "colsample_bytree": 0.8,

    # 4. Explicit regularisation. Last, and usually small gains.
    "reg_lambda": 1.0, "reg_alpha": 0.0,
}
```

:::perf The efficient tuning strategy
Do **not** grid-search. Use Optuna with 50--100 trials and a pruner:

```python
import optuna

def objective(trial):
    p = dict(
        learning_rate=0.05,
        num_leaves=trial.suggest_int("num_leaves", 15, 255, log=True),
        min_child_samples=trial.suggest_int("min_child_samples", 5, 300, log=True),
        subsample=trial.suggest_float("subsample", 0.5, 1.0),
        colsample_bytree=trial.suggest_float("colsample_bytree", 0.4, 1.0),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 30.0, log=True),
    )
    return cv_score(p)

study = optuna.create_study(direction="maximize",
                            pruner=optuna.pruners.MedianPruner())
study.optimize(objective, n_trials=100)
```

Then, once only, lower the learning rate by 5× and raise
`n_estimators` correspondingly for the final model. That last step reliably
buys a small improvement and costs one fit.
:::

## Why GBDTs still beat neural networks on tabular data

:::insight Four structural reasons
1. **Tabular features are heterogeneous.** Age, country, log-revenue and a
   binary flag have no shared geometry. Neural networks assume a metric space;
   trees do not care.
2. **The target is often piecewise constant in the features.** Business rules,
   thresholds and tiers are exactly what axis-aligned splits represent, and
   exactly what smooth networks approximate badly.
3. **Irrelevant features are free.** A tree simply never splits on them. A
   dense network multiplies every input by a weight and must learn to ignore
   it, which costs samples.
4. **No tuning cliff.** A GBDT with default parameters is usually within a few
   percent of its tuned self. A tabular neural network with default parameters
   is usually much worse, and the tuning is harder.

Where networks do win on tabular data: very large datasets (tens of millions
of rows) with high-cardinality categoricals that benefit from learned
embeddings, and any setting where the tabular features must be fused with
text or images in one model.
:::

:::practice The task
On a tabular dataset with at least 100,000 rows: (a) implement the split
finder above and verify your tree matches sklearn's on a small problem;
(b) fit a random forest and a GBDT with the *same* tree depth and compare ---
observe that deep helps one and hurts the other; (c) run Optuna for 100 trials
and plot the best score against trial number to see where the gains stop;
(d) compare LightGBM native categoricals against one-hot and target encoding;
(e) fit a tabular neural network and report the honest comparison, including
tuning time.

**You have this skill when** you can get within 1% of a well-tuned GBDT in
under an hour, and explain which knob mattered.
:::

:::exercise
1. Derive the leaf value $-G/(H+\lambda)$ from the second-order expansion.
2. Show that for squared loss $g = \hat y - y$ and $h = 1$, and that the gain
   formula reduces to variance reduction.
3. † Implement histogram binning and measure the split-finding speedup against
   exact splitting at $n = 10^6$.
4. Demonstrate the child-subtraction trick and confirm it gives identical
   histograms to computing both children directly.
5. Fit a boosted model with 10,000 trees and no early stopping. Plot train and
   validation loss and identify the overfitting point.
6. † Construct a dataset with a high-cardinality categorical where ordinary
   target encoding leaks and CatBoost's ordered statistics do not. Quantify.
7. Fit a GBDT to $y = 2x + 1$ and predict outside the training range. Explain
   the result and state when this disqualifies trees.
:::

:::recap
- A boosted tree's split gain is the reduction in a second-order approximation
  of the loss; the leaf value is the Newton step. Any twice-differentiable
  loss plugs in through $g$ and $h$.
- Boosting is gradient descent in function space; the learning rate is the
  step size and early stopping is mandatory.
- Bagging and boosting are opposites: deep independent trees versus shallow
  sequential ones.
- Histogram binning, leaf-wise growth and ordered target statistics are the
  three ideas behind the modern implementations.
- Tune in order: learning rate and early stopping, then capacity, then
  subsampling, then explicit regularisation --- with Optuna, not a grid.
- GBDTs beat networks on tabular data because features are heterogeneous,
  targets are often piecewise constant, irrelevant features are free, and
  there is no tuning cliff.
:::
