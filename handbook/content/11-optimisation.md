# Optimisation: How Models Actually Learn
@short: Optimisation
@subtitle: Gradient descent and the four modifications that make it work
@tier: foundation
@prereq: Chapter 8
@blurb: Every model you train is a call to an optimiser, and the difference between a run that converges in six hours and one that diverges at step 300 is usually three hyperparameters. This chapter derives gradient descent, then builds up through momentum, adaptive rates and decoupled weight decay to AdamW, and finishes with the schedules and the diagnostics.
@objectives:
- Explain what gradient descent does and what the learning rate controls
- Derive momentum, RMSProp and Adam, and say what each fixes
- Choose a learning-rate schedule and warmup with reasons
- Compute the memory cost of an optimiser state
- Diagnose divergence, plateaus and instability from the loss curve

## Gradient descent, and the one parameter

$$\theta_{t+1} = \theta_t - \eta \nabla_\theta L(\theta_t)$$

The gradient points uphill; we step downhill. The learning rate $\eta$ is the
step size, and it is the single most important hyperparameter in machine
learning.

How large can it be? For a quadratic with curvature $\lambda$ (the largest
eigenvalue of the Hessian), gradient descent converges if and only if

$$\eta < \frac{2}{\lambda_{\max}}$$

and diverges above it. That is the entire theory of "the learning rate was too
high": you exceeded a bound set by the curvature of the loss surface, and
since curvature varies over training, a fixed rate is always wrong somewhere.

@fig: optimiser_behaviour | 150 | The three regimes. Too small: slow but monotone. Just right: fast. Too large: oscillation that grows, because each step overshoots by more than it gained. The right-hand panel shows what each looks like in the loss curve you will actually see.

:::intuition Why the loss curve shape tells you which regime you are in
- **Smooth, slow decrease**: learning rate too small. You are wasting compute.
- **Fast decrease, then noisy plateau**: converged to the noise floor of your
  batch size. Decay the rate or increase the batch.
- **Decrease then sudden spike to `nan`**: rate exceeded $2/\lambda$ as
  curvature grew. Add warmup and clip gradients.
- **Immediately flat**: not an optimisation problem. A bug --- detached
  gradients, wrong loss, frozen parameters (Chapter 27).
- **Sawtooth**: the schedule is restarting, or your data is not shuffled and
  the model is seeing epoch boundaries.
:::

## Stochastic gradient descent

Computing the exact gradient needs the whole dataset. SGD estimates it from a
minibatch:

$$\nabla L \approx \frac{1}{B}\sum_{i \in \text{batch}} \nabla \ell_i$$

This estimate is unbiased, with variance proportional to $1/B$ (Chapter 9).
The noise is not purely a cost: it helps escape sharp minima and acts as
implicit regularisation, which is part of why very large batches sometimes
generalise worse without a learning-rate adjustment.

| Batch size | Gradient noise | Steps/epoch | GPU utilisation |
|---|---|---|---|
| 1 | very high | $n$ | terrible (memory-bound) |
| 32--256 | moderate | $n/B$ | good |
| 4096+ | low | few | excellent, but needs LR scaling |

@tbl: The batch-size trade. Larger batches raise arithmetic intensity (Chapter 7) and so GPU efficiency, but reduce the number of update steps, which is what actually drives learning. The linear scaling rule --- multiply the learning rate by the same factor as the batch --- holds up to a few thousand, then breaks.

## Momentum: fixing the ravine

Loss surfaces are typically ill-conditioned: steep in some directions, nearly
flat in others. Plain SGD oscillates across the steep directions while
crawling along the flat one.

Momentum accumulates an exponentially weighted average of past gradients:

$$v_{t} = \beta v_{t-1} + \nabla L(\theta_t), \qquad \theta_{t+1} = \theta_t - \eta v_t$$

Oscillating components alternate sign and cancel; the consistent component
accumulates. With $\beta = 0.9$ the effective step along a consistent
direction is roughly $1/(1-\beta) = 10$ times larger.

## Adaptive rates: RMSProp

Different parameters need different step sizes --- an embedding row for a rare
token gets a gradient once in ten thousand steps, a layer-norm gain gets one
every step. RMSProp scales each parameter's step by a running estimate of its
gradient magnitude:

$$s_t = \rho s_{t-1} + (1-\rho)(\nabla L)^2, \qquad \theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{s_t} + \epsilon}\nabla L$$

Parameters with consistently large gradients get smaller steps, and vice
versa. The effect is to make the learning rate roughly scale-free.

## Adam: both at once, plus bias correction

```python title="Adam, complete — every line of the real algorithm"
class Adam:
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8):
        self.p = params
        self.lr, (self.b1, self.b2), self.eps = lr, betas, eps
        self.m = [np.zeros_like(p) for p in params]   # 1st moment (momentum)
        self.v = [np.zeros_like(p) for p in params]   # 2nd moment (RMSProp)
        self.t = 0

    def step(self, grads):
        self.t += 1
        for i, (p, g) in enumerate(zip(self.p, grads)):
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g * g
            m_hat = self.m[i] / (1 - self.b1 ** self.t)   # bias correction
            v_hat = self.v[i] / (1 - self.b2 ** self.t)
            p -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
```

The bias correction is the piece people omit and then wonder why early steps
are tiny. $m$ and $v$ start at zero, so for small $t$ they underestimate the
true moments by a factor of $(1 - \beta^t)$. With $\beta_2 = 0.999$, at step 1
the raw $v$ is a thousandth of its correct size; dividing by
$1 - 0.999^1 = 0.001$ restores it.

:::pitfall Adam and weight decay are not what you think
L2 regularisation adds $\lambda\theta$ to the gradient. Inside Adam, that term
is then divided by $\sqrt{v}$ --- so parameters with large gradients get
*less* regularisation, which is backwards from the intent.

AdamW **decouples** it, applying the decay directly to the parameter:

```python
p -= self.lr * (m_hat / (np.sqrt(v_hat) + self.eps) + wd * p)   # AdamW
```

This is not a minor detail. It is why AdamW is the default for transformers
and why `torch.optim.Adam(..., weight_decay=...)` gives materially worse
results than `torch.optim.AdamW`. Use AdamW.
:::

:::perf What the optimiser state costs you
Adam stores two extra tensors per parameter. In mixed-precision training the
full accounting per parameter is:

| Item | Bytes (bf16 training) |
|---|---|
| bf16 weight | 2 |
| bf16 gradient | 2 |
| fp32 master weight | 4 |
| Adam $m$ (fp32) | 4 |
| Adam $v$ (fp32) | 4 |
| **total** | **16** |

So a 7B model needs about **112 GB** for parameters, gradients and optimiser
state alone --- before activations. That single number explains ZeRO, FSDP and
8-bit optimisers (Chapter 28). SGD with momentum needs 8 bytes instead of 16,
which is occasionally the deciding factor.
:::

## Schedules and warmup

```python title="The schedule that is the default for good reasons"
import math

def lr_at(step, base_lr, warmup, total, min_ratio=0.1):
    if step < warmup:                       # linear warmup
        return base_lr * step / warmup
    progress = (step - warmup) / max(1, total - warmup)
    cosine = 0.5 * (1 + math.cos(math.pi * progress))
    return base_lr * (min_ratio + (1 - min_ratio) * cosine)
```

**Warmup** exists because Adam's second-moment estimate is unreliable in the
first few hundred steps: $v$ is based on almost no data, so the effective step
size is erratic exactly when the parameters are most fragile. Linear warmup
over 1--5% of training removes an entire class of early divergence. It is
close to free and you should always use it.

**Cosine decay** anneals towards a small rate so late training refines rather
than bounces. It outperforms step decay in most settings and has one fewer
hyperparameter.

:::warning Cosine schedules need the total step count in advance
If you set `total` and then stop early, you stop at a high learning rate and
your final checkpoint is worse than the curve suggested it should be. If you
train longer than `total`, the rate goes negative. Either commit to the length
or use a schedule that does not need it (inverse square root, or
warmup-stable-decay, which holds a constant rate and anneals only at the end
--- convenient when you may want to continue training later).
:::

## Gradient clipping

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

Clip by the **global** norm across all parameters, not per tensor: per-tensor
clipping changes the gradient *direction*, global clipping only its length.
A max norm of 1.0 is the standard choice for transformers. Log the pre-clip
norm --- a sudden spike is the signature of a bad batch, and a persistently
clipped norm means your learning rate is too high for the data.

## Finding the learning rate

```python title="The LR range test: ten minutes, and it works"
lrs, losses = [], []
lr = 1e-7
for batch in islice(loader, 200):
    for g in opt.param_groups:
        g["lr"] = lr
    loss = train_step(batch)
    lrs.append(lr); losses.append(loss)
    lr *= 1.1                      # exponential sweep over ~4 orders
# Plot loss vs log(lr). Pick roughly one tenth of the value where the
# curve reaches its steepest downward slope — NOT the minimum, which is
# already in the unstable region.
```

| Model type | Typical starting LR (AdamW) |
|---|---|
| Transformer pretraining (100M--1B) | 3e-4 to 1e-3 |
| Transformer pretraining (7B+) | 1e-4 to 3e-4 |
| Full fine-tuning | 1e-5 to 5e-5 |
| LoRA fine-tuning | 1e-4 to 3e-4 |
| Vision CNN (SGD + momentum) | 0.1 with batch 256 |

@tbl: Starting points, not answers. Note that larger models want *smaller* rates --- the curvature grows with width --- and that LoRA tolerates rates about ten times higher than full fine-tuning because far fewer parameters move.

:::practice The task
On a small model: (a) run an LR range test and pick a rate from the curve;
(b) train with that rate, with $10\times$ it, and with $0.1\times$ it, and
match each loss curve to a regime from the intuition box; (c) train with and
without warmup at the highest stable rate and show the difference in the first
500 steps; (d) implement Adam from the listing above and check it against
`torch.optim.Adam` to within floating-point tolerance; (e) compute your
model's optimiser memory by hand and confirm it with
`torch.cuda.max_memory_allocated()`.

**You have this skill when** you can look at a loss curve and name the cause,
and when you can predict your run's peak memory before launching it.
:::

:::exercise
1. Derive the $\eta < 2/\lambda$ stability bound for gradient descent on
   $L(\theta) = \frac{1}{2}\lambda\theta^2$.
2. Show that momentum with $\beta$ gives an effective step
   $1/(1-\beta)$ times larger along a constant gradient direction.
3. † Implement Adam without bias correction and plot the effective step
   size over the first 1000 steps against the corrected version.
4. Demonstrate the Adam-versus-AdamW difference empirically on a small model
   with weight decay 0.1.
5. Compute the optimiser memory for a 1.5B-parameter model in bf16 with Adam,
   then with 8-bit Adam, then with SGD+momentum.
6. † Train with a cosine schedule set for 10,000 steps but stop at 5000.
   Compare the final loss to a run scheduled for 5000 steps. Explain.
7. Log pre-clip gradient norms for 2000 steps and identify the batches that
   trigger clipping. What do they have in common?
:::

:::recap
- The learning rate is bounded by curvature: $\eta < 2/\lambda_{\max}$, and
  exceeding it is what divergence is.
- SGD's minibatch noise scales as $1/B$; larger batches are more efficient per
  FLOP but give fewer update steps.
- Momentum cancels oscillation and amplifies consistent directions; adaptive
  methods give each parameter its own scale; Adam is both plus bias
  correction.
- Use AdamW, not Adam with `weight_decay` --- the coupling is genuinely
  harmful.
- Adam costs 16 bytes per parameter in mixed precision; this number drives
  ZeRO, FSDP and 8-bit optimisers.
- Warmup fixes Adam's unreliable early second moment; cosine decay needs the
  total step count committed in advance.
- Clip by global norm, log the pre-clip value, and find your rate with a
  range test rather than by guessing.
:::
