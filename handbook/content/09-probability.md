# Probability for Engineers
@short: Probability
@subtitle: The dozen results you actually reach for
@tier: foundation
@prereq: none
@blurb: Machine learning is applied probability, but only a small part of probability is applied. This chapter covers the part: the distributions you meet, expectation and variance as tools rather than definitions, Bayes' rule in its practical form, maximum likelihood as the source of every loss function you use, and the sampling results that make evaluation possible.
@objectives:
- Recognise which distribution a quantity follows, and why it matters
- Use expectation and variance to reason about estimators and gradients
- Apply Bayes' rule to the base-rate problems that recur in ML
- Derive cross-entropy and MSE as maximum likelihood under stated assumptions
- Know why the central limit theorem underwrites every confidence interval

## The distributions, and what each one is for

| Distribution | Models | Where it appears |
|---|---|---|
| Bernoulli$(p)$ | one yes/no trial | binary classification output |
| Categorical$(\mathbf{p})$ | one choice of $K$ | next-token prediction |
| Binomial$(n, p)$ | successes in $n$ trials | A/B test conversions |
| Poisson$(\lambda)$ | events in a fixed window | request arrivals, error counts |
| Normal$(\mu, \sigma^2)$ | sums of many small effects | weight init, noise, CLT |
| Exponential$(\lambda)$ | waiting time between events | latency tails (poorly) |
| Log-normal | products of many effects | latency (well), file sizes |
| Beta$(\alpha, \beta)$ | uncertainty about a probability | conjugate prior for rates |
| Dirichlet$(\boldsymbol{\alpha})$ | uncertainty about a categorical | topic models, mixtures |
| Gumbel | maximum of many samples | the Gumbel-max sampling trick |

@tbl: Ten distributions cover the overwhelming majority of ML work. Note the latency row: response times are approximately log-normal, not exponential and certainly not normal, which is why the mean is a poor summary and p50/p95/p99 are reported instead.

:::intuition Why normal distributions are everywhere, and where they are not
The central limit theorem says that the sum of many independent contributions
--- whatever their individual distributions --- tends to a normal. That is why
measurement noise, weight initialisations and sample means are normal-ish.

It is also why **latency is not**. Latency is a *maximum* over dependent
stages (the slowest shard, the slowest retry), and maxima follow extreme-value
distributions with heavy right tails. Averaging latencies loses exactly the
information you need. Report percentiles.
:::

## Expectation and variance as tools

$$\mathbb{E}[X] = \sum_x x \, p(x), \qquad \text{Var}(X) = \mathbb{E}[X^2] - \mathbb{E}[X]^2$$

Four properties do almost all the work:

$$\mathbb{E}[aX + b] = a\mathbb{E}[X] + b \qquad \text{(always)}$$
$$\mathbb{E}[X + Y] = \mathbb{E}[X] + \mathbb{E}[Y] \qquad \text{(always, even if dependent)}$$
$$\text{Var}(aX) = a^2 \text{Var}(X) \qquad \text{(always)}$$
$$\text{Var}(X + Y) = \text{Var}(X) + \text{Var}(Y) \qquad \text{(only if independent)}$$

The last one is the one to watch. It is why averaging $n$ independent
measurements reduces the standard error by $\sqrt{n}$ --- and why averaging
$n$ *correlated* measurements does not, which is the single most common
statistical error in ML evaluation.

```python title="The variance of a mean, and why it matters for batch size"
# For a batch of B independent examples, the gradient estimate is a mean:
#   Var(g_batch) = Var(g_single) / B
# So the gradient NOISE scales as 1/sqrt(B). Doubling the batch reduces
# noise by 1.41x — which is why the "linear scaling rule" pairs a 2x batch
# with a 2x learning rate only up to a point, then breaks down.
```

@fig: variance_of_mean | 132 | Standard error against sample size. The $1/\sqrt{n}$ shape is why the first hundred evaluation examples buy you far more than the next nine hundred, and why halving your error bar costs four times the data.

## Bayes' rule, in the form you will use

$$P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}, \qquad P(E) = \sum_{h} P(E \mid h) P(h)$$

The version worth memorising is the odds form, because it isolates the two
things that matter:

$$\frac{P(H \mid E)}{P(\neg H \mid E)} \;=\; \frac{P(H)}{P(\neg H)} \;\times\; \frac{P(E \mid H)}{P(E \mid \neg H)}$$

$$\text{posterior odds} \;=\; \text{prior odds} \;\times\; \text{likelihood ratio}$$

:::pitfall The base-rate problem, in ML terms
Your fraud classifier has 99% precision and 99% recall on a balanced
test set. Fraud occurs in 0.1% of real transactions. What fraction of
flagged transactions are actually fraud?

Prior odds: $0.001 / 0.999 \approx 1{:}999$. Likelihood ratio:
$0.99 / 0.01 = 99$. Posterior odds: $99{:}999$, so precision in production is
about **9%** --- ninety-one false positives for every nine catches.

Nothing is wrong with the model. The evaluation set's class balance did not
match production, and a metric measured under one base rate does not transfer
to another. This is why you evaluate on production-representative data, and
why precision should always be reported with the prevalence it was measured
at.
:::

## Maximum likelihood: where your loss functions come from

Every standard loss is the negative log-likelihood of some assumed noise
model. Knowing which one tells you when the loss is wrong for your problem.

**Gaussian noise gives MSE.** Assume $y = f(x) + \varepsilon$ with
$\varepsilon \sim \mathcal{N}(0, \sigma^2)$. Then

$$-\log p(y \mid x) = \frac{(y - f(x))^2}{2\sigma^2} + \log \sigma\sqrt{2\pi}$$

Maximising likelihood over the dataset is minimising $\sum (y_i - f(x_i))^2$.
So **using MSE asserts that your errors are Gaussian and homoscedastic.** If
they are heavy-tailed, MSE lets a handful of outliers dominate --- which is
exactly when Huber loss is the right answer.

**Categorical gives cross-entropy.** With $p_\theta(y \mid x)$ a categorical
distribution,

$$-\log p_\theta(y \mid x) = -\sum_k y_k \log p_k = \text{cross-entropy}$$

Language-model training *is* maximum likelihood over the next token, and
nothing more. Perplexity is just $\exp$ of the mean cross-entropy, so a
perplexity of 10 means the model is, on average, as uncertain as if choosing
uniformly among 10 tokens.

**Bernoulli gives binary cross-entropy.** Same derivation, $K = 2$.

:::insight Choosing a loss is choosing a noise model
"Which loss should I use?" is really "what do I believe about the errors?"

- Symmetric, light-tailed errors → MSE.
- Heavy-tailed errors or outliers → Huber, or MAE (which is the MLE under
  Laplace noise, and estimates the median rather than the mean).
- Counts → Poisson loss, not MSE on the raw counts.
- Asymmetric costs → a weighted or quantile loss; pinball loss at quantile
  $\tau$ estimates the $\tau$-th quantile directly.
- Skewed positive targets → model $\log y$, but remember that
  $\mathbb{E}[e^{z}] \neq e^{\mathbb{E}[z]}$ when you transform
  back.
:::

## Entropy, cross-entropy and KL

$$H(p) = -\sum_x p(x) \log p(x) \qquad \text{(bits/nats of surprise)}$$
$$H(p, q) = -\sum_x p(x) \log q(x) \qquad \text{(cost of coding } p \text{ with } q)$$
$$D_{KL}(p \,\|\, q) = H(p,q) - H(p) \ge 0$$

Three facts that get used:

**KL is not symmetric.** $D_{KL}(p\|q)$ heavily penalises $q$ being small
where $p$ is large (mode-covering); $D_{KL}(q\|p)$ penalises $q$ being large
where $p$ is small (mode-seeking). The choice determines whether a fitted
distribution spreads over all modes or collapses to one --- which is exactly
the distinction between forward and reverse KL in distillation and in RLHF.

**Minimising cross-entropy is minimising KL** to the data distribution, since
$H(p)$ does not depend on your parameters.

**KL appears as a leash.** In RLHF and DPO the objective includes
$-\beta D_{KL}(\pi_\theta \| \pi_{\text{ref}})$, which is what stops the model
drifting arbitrarily far from the reference while chasing reward
(Chapter 36).

## Sampling and estimation

```python title="Monte Carlo: the estimator behind every eval number"
# Any expectation can be estimated by sampling:
#   E[f(X)] ≈ (1/n) sum f(x_i),  with standard error  sd(f) / sqrt(n)
import numpy as np

def mc_estimate(f, sampler, n=10_000, seed=0):
    rng = np.random.default_rng(seed)
    vals = np.array([f(sampler(rng)) for _ in range(n)])
    return vals.mean(), vals.std(ddof=1) / np.sqrt(n)     # estimate, std error
```

The $1/\sqrt{n}$ is unavoidable and it is why evaluation sets have the sizes
they do. To halve an error bar you need four times the data. For a metric
around 0.5, a 95% interval of $\pm 0.03$ needs roughly 1000 examples;
$\pm 0.01$ needs about 9600. Chapter 38 makes this precise.

:::practice The task
(a) Simulate the fraud base-rate example and confirm the 9% precision
numerically. (b) Fit the same regression with MSE and with Huber loss on data
containing 2% outliers, and compare the fitted slopes. (c) Estimate a
metric by Monte Carlo at $n = 100, 1000, 10000$ and verify the error bar
shrinks as $1/\sqrt{n}$. (d) Compute forward and reverse KL between a bimodal
$p$ and the best single Gaussian $q$, and show that the two minimisers differ
--- one straddles both modes, one picks a mode.

**You have this skill when** you can look at a proposed loss function and
state what it assumes about the errors, and look at a reported metric and
state how many samples it needs to be trusted to the precision claimed.
:::

:::exercise
1. Derive $\text{Var}(X) = \mathbb{E}[X^2] - \mathbb{E}[X]^2$ from the
   definition.
2. Show that averaging $n$ perfectly correlated measurements does not reduce
   the standard error at all. Relate this to evaluating on near-duplicate
   examples.
3. † Your classifier has 95% recall and 95% specificity.
   Plot production precision against prevalence from 0.01% to 50%.
   At what prevalence does precision reach 90%?
4. Derive MAE as maximum likelihood under Laplace noise, and show it estimates
   the conditional median.
5. Show that perplexity equals $\exp$ of mean cross-entropy, and compute the
   perplexity of a uniform distribution over 50,000 tokens.
6. † Fit a single Gaussian to a two-component mixture by minimising
   forward KL and then reverse KL. Plot both. Explain the difference in one
   sentence.
7. Generate latency samples from a log-normal and compare mean, median and
   p99. Explain why an SLA on the mean is close to meaningless.
:::

:::recap
- Ten distributions cover most ML work; latency is log-normal, not normal ---
  report percentiles.
- Variances add only for *independent* variables; correlated evaluation
  examples do not shrink your error bar.
- Bayes in odds form isolates prior odds from the likelihood ratio, and
  explains why a good classifier has poor production precision on a rare
  class.
- Every standard loss is a negative log-likelihood: MSE assumes Gaussian
  errors, MAE assumes Laplace and estimates the median, cross-entropy assumes
  categorical.
- KL is asymmetric; forward KL is mode-covering, reverse is mode-seeking, and
  the choice matters in distillation and RLHF.
- Monte Carlo error falls as $1/\sqrt{n}$: halving an error bar costs four
  times the data.
:::
