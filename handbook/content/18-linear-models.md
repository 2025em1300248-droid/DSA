# Linear Models, Properly Understood
@short: Linear Models
@subtitle: The baseline you must beat, and the machinery everything else reuses
@tier: foundation
@prereq: Chapter 17
@blurb: Linear and logistic regression are the models people skip on the way to something more interesting, and then rebuild badly later. They are the right baseline, they are interpretable in a way nothing else is, and every idea in them --- the normal equations, regularisation paths, the logit, the link function --- reappears throughout deep learning. This chapter covers them at the level that makes them useful.
@objectives:
- Solve least squares three ways and know which is numerically sound
- Read logistic regression coefficients correctly, in odds
- Use regularisation paths to select features and understand collinearity
- Apply generalised linear models to counts, rates and durations
- Know exactly when a linear model is the right final answer

## Least squares, three ways

Minimise $\|Xw - y\|_2^2$. The gradient is zero when

$$X^\top X w = X^\top y$$

the **normal equations**. Three ways to solve them, and the differences
matter.

```python title="Three solutions, in increasing order of trustworthiness"
import numpy as np

# 1. Explicit inverse — never do this.
w = np.linalg.inv(X.T @ X) @ X.T @ y

# 2. Solve the normal equations — better, but squares the condition number.
w = np.linalg.solve(X.T @ X, X.T @ y)

# 3. QR or SVD via lstsq — what every library actually uses.
w, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
```

:::math Why the explicit inverse is wrong
The **condition number** $\kappa(A)$ measures how much a relative error in the
input is amplified in the output. Forming $X^\top X$ squares it:

$$\kappa(X^\top X) = \kappa(X)^2$$

If $X$ has condition number $10^6$ --- entirely ordinary with correlated
features --- then $X^\top X$ has $10^{12}$, and in float64 (about 16 digits)
you have four digits of accuracy left. QR decomposition works with $X$
directly and keeps $\kappa(X)$.

This is not an academic point. It is why a regression on near-collinear
features can produce coefficients of $\pm 10^{7}$ that flip sign when you add
one row.
:::

## Ridge, lasso and the path

$$\text{ridge:} \;\; \min_w \|Xw - y\|_2^2 + \alpha\|w\|_2^2 \qquad w = (X^\top X + \alpha I)^{-1}X^\top y$$
$$\text{lasso:} \;\; \min_w \|Xw - y\|_2^2 + \alpha\|w\|_1 \qquad \text{(no closed form)}$$

Ridge's $+\alpha I$ is doing something concrete: it adds $\alpha$ to every
eigenvalue of $X^\top X$, so the matrix is always invertible and the condition
number improves. Ridge is a numerical fix as much as a statistical one.

```python title="The regularisation path tells you about your features"
from sklearn.linear_model import lasso_path
import numpy as np

alphas, coefs, _ = lasso_path(X_scaled, y, n_alphas=100)
# coefs: (n_features, n_alphas). Plot each row against log(alpha).
# Read it as: features whose coefficients survive longest as alpha grows
# are the ones carrying independent signal.

order = np.argsort(-(coefs != 0).sum(axis=1))
for i in order[:10]:
    entry = alphas[(coefs[i] != 0).argmax()]
    print(f"{FEATURES[i]:<30} enters at alpha={entry:.4g}")
```

@fig: regularisation_path | 158 | A lasso path. Each line is one coefficient as the penalty falls. Features entering early carry independent signal; features that enter late and immediately push another coefficient down are collinear with it. This plot is a feature-selection tool and a collinearity diagnostic in one.

:::pitfall Scaling is not optional for regularised models
Both penalties act on the coefficient magnitudes, and a coefficient's
magnitude depends on its feature's units. A feature measured in millimetres
gets a coefficient a thousand times smaller than the same feature in metres
--- and is therefore penalised a millionfold less.

Always standardise before ridge or lasso. Do it inside a `Pipeline` so the
statistics are fitted on the training fold only:
```python
Pipeline([("scale", StandardScaler()), ("model", Lasso(alpha=0.01))])
```
Unregularised OLS is genuinely scale-invariant in its predictions, which is
why this trap catches people who learned OLS first.
:::

## Logistic regression, read correctly

$$\log\frac{p}{1-p} = w^\top x + b \qquad\Longleftrightarrow\qquad p = \sigma(w^\top x + b)$$

The model is linear in the **log-odds**, not in the probability. This is the
source of every misreading.

```python title="Interpreting a coefficient"
# coefficient w_j = 0.693 for a standardised feature
# exp(0.693) = 2.0
#
# CORRECT: "a one-standard-deviation increase in x_j doubles the ODDS,
#           holding the other features fixed"
#
# WRONG:   "it doubles the probability"
#
# The probability change depends on where you start:
#   p = 0.01 -> odds 0.0101 -> 0.0202 -> p = 0.0198   (+0.98 points)
#   p = 0.50 -> odds 1.00   -> 2.00   -> p = 0.667    (+16.7 points)
#   p = 0.90 -> odds 9.00   -> 18.0   -> p = 0.947    (+4.7 points)
```

The largest probability effect is always at $p = 0.5$, which is the sigmoid's
steepest point --- and it is why a "strong" coefficient can look weak in a
population where the base rate is 1%.

:::warning Complete separation
If a feature perfectly separates the classes, the likelihood is maximised by
sending its coefficient to infinity. `sklearn` hides this because it
regularises by default (`C=1.0`); `statsmodels` will warn or fail to converge.

Symptoms: a coefficient in the hundreds, a standard error in the thousands,
and perfect training accuracy. Usually the cause is leakage --- a feature
derived from the label. Investigate before you regularise it away.
:::

## Generalised linear models

Linear regression assumes Gaussian errors (Chapter 9). When the target is a
count, a rate, or bounded, the GLM framework gives you the right model by
changing two things: the distribution and the link function.

| Target | Distribution | Link | Model |
|---|---|---|---|
| Continuous, symmetric | Gaussian | identity | linear regression |
| Binary | Bernoulli | logit | logistic regression |
| Count | Poisson | log | Poisson regression |
| Count, overdispersed | Negative binomial | log | NB regression |
| Rate (count / exposure) | Poisson + offset | log | rate model |
| Positive, skewed | Gamma | log | gamma regression |
| Proportion in (0,1) | Beta | logit | beta regression |

@tbl: The GLM family. The overdispersion row matters in practice: real counts almost always have variance exceeding the mean, which violates Poisson and produces standard errors that are far too small.

```python title="A rate model, with the offset that makes it a rate"
import statsmodels.api as sm

# Modelling clicks per impression: the exposure belongs in an offset,
# not as a feature, so the coefficient structure describes the RATE.
model = sm.GLM(clicks, X, family=sm.families.Poisson(),
               offset=np.log(impressions)).fit()

# Check for overdispersion before trusting the standard errors:
print(model.pearson_chi2 / model.df_resid)   # >> 1 means use NegativeBinomial
```

## When a linear model is the right final answer

:::insight The four cases, and they are not rare
1. **You need to explain every prediction to a regulator.** A linear model's
   explanation is exact and stable, not an approximation from an attribution
   method.
2. **Few samples relative to features.** With 200 rows, a regularised linear
   model frequently beats gradient boosting, because variance dominates and
   the strong inductive bias pays.
3. **The relationship genuinely is monotone and smooth.** Forcing a tree to
   approximate a straight line wastes capacity and extrapolates terribly.
4. **You need to extrapolate.** Trees predict a constant outside the training
   range. A linear model makes a defensible guess. This alone disqualifies
   trees for many forecasting problems.

And always, in every project: **fit one first**. It takes four minutes and
gives you the number the rest of the project must beat. A gradient-boosted
model that beats logistic regression by 0.3 points is telling you something
important about your features.
:::

:::practice The task
On a tabular dataset: (a) fit OLS three ways and compare coefficients on
deliberately collinear features; report the condition numbers; (b) plot a
lasso path and read off the feature ordering and the collinear pairs; (c) fit
logistic regression and state, in words, what your largest coefficient means
--- in odds --- then compute the probability change at base rates 1%, 10% and
50%; (d) construct complete separation and observe the coefficient blow-up;
(e) fit a Poisson model to count data, test for overdispersion, and refit with
negative binomial if needed.

**You have this skill when** your first commit on a new problem is a
regularised linear baseline with an honest evaluation, and you can read its
coefficients aloud correctly.
:::

:::exercise
1. Construct $X$ with condition number $10^8$ and compare `inv`, `solve` and
   `lstsq` against the known true coefficients.
2. Show that ridge adds $\alpha$ to every eigenvalue of $X^\top X$, and
   compute the resulting condition number.
3. † Fit lasso with and without standardisation on features with wildly
   different units. Explain the selected set in each case.
4. Derive the logistic loss as maximum likelihood under a Bernoulli
   assumption.
5. Plot the probability change from a fixed log-odds increment as a function
   of the base rate. Identify the maximum.
6. † Simulate overdispersed counts, fit Poisson, and show the standard errors
   are too small. Quantify the error in the coverage of the intervals.
7. Take a problem where you used gradient boosting and fit a regularised
   linear baseline. Report the gap, and decide whether it justified the
   complexity.
:::

:::recap
- Solve least squares with QR/SVD, not the explicit inverse: forming
  $X^\top X$ squares the condition number.
- Ridge's $+\alpha I$ is a numerical fix as well as a statistical one; lasso
  gives exact zeros because its constraint region has corners.
- Standardise before any penalised fit; the penalty acts on magnitudes and
  magnitudes depend on units.
- Logistic regression is linear in the log-odds: a coefficient multiplies the
  odds, and the probability effect depends on the base rate.
- Complete separation sends coefficients to infinity and usually indicates
  leakage.
- GLMs match the distribution to the target; check for overdispersion before
  trusting Poisson standard errors.
- Fit a linear baseline first, always. It is the number everything else must
  beat.
:::
