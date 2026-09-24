# Mathematics, and Exactly How Much
@short: Mathematics
@subtitle: The parts you will use, and the parts you can safely defer
@tier: foundation
@prereq: none
@blurb: The maths requirement for AI/ML engineering is widely overstated and widely understated at the same time. You do not need measure theory. You absolutely do need to be fluent in linear algebra as *shapes*, in probability as *uncertainty you must quantify*, and in optimisation as *why your loss is not going down*. This chapter separates the two lists honestly.
@objectives:
- Reason about tensor shapes, ranks and matrix operations without hesitation
- Use probability and statistics to make honest claims about model performance
- Understand gradients and optimisation well enough to debug training
- Know which mathematics you can defer indefinitely, and why

## What this is for

Three concrete failures that mathematics prevents, in ascending order of
frequency:

1. You cannot debug a shape error, so you guess at `transpose` and `reshape`
   until it runs --- and then the model trains on the wrong axis.
2. You report a 2% improvement that is noise, and the team ships it.
3. Your loss plateaus and you do not know whether the cause is the learning
   rate, the initialisation, the data, or a bug.

## The capabilities

:::checklist ESSENTIAL --- linear algebra
- Vectors, matrices, tensors as *shapes*: you can predict the output shape of
  any composition of operations before running it
- Matrix multiplication, transpose, broadcasting rules, batched matmul
- Dot products and cosine similarity, and why normalisation changes the
  ranking
- Norms: L1, L2, and what each does as a regulariser
- Eigenvalues and eigenvectors *conceptually*: PCA, spectral clustering, and
  what "the top singular vectors" means
- SVD and low-rank approximation --- this is literally what LoRA is
- Why numerical precision matters: fp32 vs bf16 vs fp16 range and precision,
  and where catastrophic cancellation appears
:::

:::checklist ESSENTIAL --- probability and statistics
- Distributions you will meet: Bernoulli, categorical, Gaussian, Poisson,
  log-normal, power law (and knowing that real data is usually the last two)
- Expectation, variance, covariance; the law of large numbers and the CLT as
  intuitions rather than proofs
- Conditional probability and Bayes' rule, fluently
- Maximum likelihood, and why cross-entropy *is* the negative log-likelihood
- KL divergence and entropy: they appear in distillation, in variational
  methods, in DPO, and in drift detection
- Confidence intervals and bootstrapping --- how you say "2% better" honestly
- Hypothesis testing and multiple-comparison correction: if you evaluate 20
  prompts you will find a winner by chance
- Sampling: with and without replacement, stratification, and how biased
  sampling silently invalidates an evaluation
:::

:::checklist ESSENTIAL --- calculus and optimisation
- Derivatives, partial derivatives, the chain rule --- because
  backpropagation is the chain rule applied to a graph
- Gradients and what a gradient step does geometrically
- Convexity, and why it matters that deep learning is not convex
- Gradient descent and its variants: momentum, Adam/AdamW, and what weight
  decay actually does
- Learning-rate schedules and warmup, and why a large batch needs a different
  learning rate
- Why gradients vanish and explode, and the standard mitigations:
  normalisation, residual connections, clipping, careful initialisation
:::

:::checklist CORE
- Information theory: entropy, cross-entropy, mutual information, perplexity
  --- and being able to explain why perplexity is $e^{\text{cross-entropy}}$
- Numerical methods: conditioning, stability, the log-sum-exp trick, why you
  work in log space
- Matrix calculus enough to read a paper's gradient derivation
- Experimental design: power analysis, A/B test sizing, sequential testing
  hazards, CUPED-style variance reduction
:::

:::checklist AWARENESS
- Convex optimisation theory, Lagrangians, duality
- Measure-theoretic probability
- Stochastic differential equations (relevant if you work on diffusion)
- Category theory, topology, and everything else occasionally claimed to be
  required. It is not.
:::

## The honest deferral list

| Often demanded | Actually needed for | Defer if |
|---|---|---|
| Measure theory | writing probability theory papers | you are building systems |
| Convex optimisation proofs | optimisation research | you use AdamW like everyone else |
| Manual backprop derivations | understanding, once | you have done it once by hand for a 2-layer net |
| Full SVD algorithms | numerical linear algebra research | you call `np.linalg.svd` |
| Real analysis | proofs | always, for engineering roles |

@tbl: Maths frequently listed as a prerequisite, and the honest assessment. Do the one row that says "once": derive backpropagation for a two-layer network by hand, once, and the rest of deep learning stops being magic.

:::insight The reframing that makes this tractable
Learn the mathematics *as debugging tools*, not as a course. Linear algebra
is how you reason about shapes. Probability is how you avoid claiming a
result you do not have. Optimisation is how you explain a flat loss curve.
Studied that way each topic has an immediate payoff, which is the only
reliable way adults retain mathematics.
:::

## How to tell you have it

:::practice The tasks
1. Given `x` of shape `(B, L, D)`, weights `(D, 4D)` and `(4D, D)`, and a
   reshape into `(B, L, H, D/H)`, write down every intermediate shape in a
   transformer block from memory, including the attention matrix.
2. Implement backpropagation by hand for a two-layer MLP --- no autograd ---
   and match PyTorch's gradients to within float tolerance.
3. Your model scores 0.842 and the baseline scores 0.826 on a 2,000-example
   test set. Compute a bootstrap confidence interval and state whether you
   would ship it. Then compute how large the test set must be for a 1%
   difference to be detectable.
4. Explain why `softmax` is implemented by subtracting the row maximum, and
   construct an input where the naive version returns `nan`.
:::

:::pitfall The three that actually bite
**Claiming an improvement that is noise.** The most common statistical
failure in applied ML, and the one that costs the most: teams ship changes
that do nothing and lose the ability to tell which past change helped.

**Evaluating many things and reporting the best.** Twenty prompts on one test
set will produce a 2-sigma winner by chance. Hold out a second set, or
correct for the comparisons.

**Trusting a metric without knowing its variance.** Report a confidence
interval alongside every headline number, every time. It changes decisions.
:::

:::note Time to competence
From a typical engineering degree: **4--6 weeks** to firm up the ESSENTIAL
lists. From no mathematical background: **3--4 months**, and it is worth
every hour. Learn it alongside the code, not before it.
:::

:::recap
- Linear algebra as shapes, probability as honest uncertainty, optimisation
  as training debugging. That framing is what makes it stick.
- ESSENTIAL: shapes and broadcasting, norms, SVD conceptually, distributions,
  Bayes, MLE and cross-entropy, KL, bootstrapping, significance, gradients,
  AdamW, schedules, vanishing/exploding gradients.
- Derive backprop by hand once; call `np.linalg.svd` forever after.
- Measure theory, real analysis and convex optimisation proofs are not
  required for engineering roles.
- The highest-value statistical habit is reporting a confidence interval with
  every number.
:::
