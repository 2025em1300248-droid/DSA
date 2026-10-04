# Debugging a Model That Will Not Learn
@short: Debugging Training
@subtitle: A diagnostic procedure, ordered by how often each cause occurs
@tier: core
@prereq: Chapter 23
@blurb: The loss is flat, or it is `nan`, or it is fine and the model is useless. This chapter is a procedure: a set of checks in the order that finds the problem fastest, with the signature of each failure so you can recognise it rather than search for it. It is the most practically valuable chapter in this part.
@objectives:
- Run the four-step triage that localises any training failure
- Recognise a dozen failure signatures on sight
- Use the overfit-one-batch test as the central diagnostic
- Instrument a model to make failures visible rather than mysterious
- Distinguish optimisation failures from data failures from evaluation failures

## Triage, in order

@fig: debug_tree | 182 | The diagnostic order. Each branch is chosen to eliminate the largest share of possible causes per unit of effort. Do not skip step 1, however obvious it seems.

:::checklist The four steps, in this order, every time
**1. Can it overfit eight examples?** Train on one fixed batch until the loss
approaches zero. If it cannot, the bug is in the model or the loss and no
amount of data or tuning will fix it. This eliminates roughly 60% of
causes in about thirty seconds.

**2. Is the data what you think?** Print five raw examples. Decode the
tokenised inputs *back to text*. Print the labels alongside. Check the shapes,
the dtypes, the ranges, the class balance. A surprising share of "the model
will not learn" is "the labels are shuffled relative to the inputs".

**3. Are the gradients flowing?** Check every parameter has a non-zero
gradient, and look at the gradient norm per layer. A layer with zero gradient
is disconnected; a layer with $10^{-9}$ is effectively frozen.

**4. Only now, tune.** Learning rate, schedule, batch size, capacity. Tuning
before steps 1--3 wastes hours on a problem that is not optimisation.
:::

## Signatures

| Signature | Cause | Check |
|---|---|---|
| Loss flat at $\ln(C)$ from step 0 | model output is constant | is the last layer connected? is the input all zeros? |
| Loss flat, gradients zero | `detach()`, `no_grad`, or `requires_grad=False` | `[n for n,p in m.named_parameters() if p.grad is None]` |
| Loss decreases then `nan` | LR too high, or a division by zero | log gradient norm; look for the spike before |
| Loss `nan` from step 1 | `inf` in the input, or `log(0)` | `assert torch.isfinite(x).all()` |
| Loss decreases very slowly | LR too low, or bad initialisation | LR range test (Chapter 11) |
| Train loss falls, val loss rises | overfitting | regularise, or get more data |
| Both fall, val metric flat | the metric is not the loss | check the metric's implementation |
| Val loss *below* train loss | dropout still on at eval, or split skew | `model.eval()`; compare distributions |
| Loss falls to ~0 immediately | label leakage, or a label/input off-by-one | inspect examples; leakage report (Ch 14) |
| Loss sawtooths at epoch boundaries | data not shuffled | `shuffle=True`; check the sampler |
| Works at batch 8, diverges at 512 | LR not scaled with batch | linear scaling rule plus warmup |
| Fine on one GPU, wrong on many | gradient sync or a seed issue | compare single-GPU loss for 100 steps |

@tbl: Failure signatures. The first four cover about half of all cases in practice.

## Instrumentation

```python title="Put this in every model you write"
@torch.no_grad()
def diagnose(model, loss):
    stats = {}
    for name, p in model.named_parameters():
        if p.grad is None:
            stats[f"{name}/grad"] = float("nan")          # DISCONNECTED
            continue
        stats[f"{name}/grad_norm"] = p.grad.norm().item()
        stats[f"{name}/weight_norm"] = p.norm().item()
        stats[f"{name}/grad_to_weight"] = (
            p.grad.norm() / (p.norm() + 1e-12)).item()    # want ~1e-3
    stats["loss"] = loss.item()
    return stats

def check_activations(model, x):
    """Hook every module and report dead or exploding activations."""
    out = {}
    def hook(name):
        def fn(_m, _i, o):
            t = o[0] if isinstance(o, tuple) else o
            if torch.is_tensor(t) and t.is_floating_point():
                out[name] = dict(mean=t.mean().item(), std=t.std().item(),
                                 zeros=(t == 0).float().mean().item(),
                                 finite=torch.isfinite(t).all().item())
        return fn
    handles = [m.register_forward_hook(hook(n))
               for n, m in model.named_modules() if not list(m.children())]
    model(x)
    for h in handles:
        h.remove()
    return out
```

:::insight Reading activation statistics
- **std shrinking layer by layer** → signal is dying; check initialisation and
  normalisation placement.
- **std growing layer by layer** → will overflow; check residual scaling
  (Chapter 25) and normalisation.
- **zeros fraction > 0.9 after a ReLU** → dead units. Switch to GELU/SiLU, or
  lower the learning rate: dead ReLUs are usually caused by a large negative
  bias learned after a too-large step.
- **std ≈ 0 anywhere** → that layer outputs a constant and contributes
  nothing.
- **non-finite anywhere** → find the first layer where it appears; that is
  where the bug is, not where the `nan` surfaced.
:::

## The overfit test, in detail

```python title="The single most valuable half-minute in deep learning"
def overfit_one_batch(model, batch, steps=400, lr=1e-3):
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    first = None
    for i in range(steps):
        loss = model(**batch).loss
        opt.zero_grad(); loss.backward(); opt.step()
        if i == 0:
            first = loss.item()
    last = loss.item()
    print(f"{first:.4f} -> {last:.4f}")
    assert last < 0.05 * first, "cannot overfit: the bug is in the model"
    return last
```

| Result | Diagnosis |
|---|---|
| Falls to ~0 | model and loss are fine; the problem is data, scale or tuning |
| Falls to a plateau well above 0 | insufficient capacity, or a bottleneck layer |
| Does not fall at all | gradients not reaching parameters |
| Falls to 0 *instantly* | label leakage --- the input contains the answer |
| Falls, then rises | learning rate far too high even for one batch |

@tbl: How to read the overfit test. The fourth row is the one people misread as success.

:::warning The bug is usually not where the error is
A `nan` in the loss is reported at the loss. The `inf` that produced it
appeared eight layers earlier. Use `torch.autograd.set_detect_anomaly(True)`
to get a stack trace from the *forward* operation that produced the bad
value --- it is slow, so enable it only while debugging. Better still, hook
every module and assert finiteness, which localises it in one run.
:::

## Distributed-specific failures

| Symptom | Cause |
|---|---|
| Loss differs across ranks | data not sharded; each rank sees everything |
| Hang at the first backward | some rank has a parameter unused in the loss |
| Hang after N steps | ranks diverged in control flow (e.g. a data-dependent `if`) |
| Much worse than single-GPU | LR not scaled, or gradients summed instead of averaged |
| `NCCL timeout` | one rank is slower (data loading), or a real deadlock |

@tbl: Distributed failures. The universal first move is to reproduce on a single GPU: if it is wrong there too, it is not a distributed bug.

:::practice The task
Take a working model and break it seven ways, recording the signature of each
before fixing it: (1) `detach()` between the encoder and the loss; (2) labels
shifted by one; (3) learning rate ×100; (4) a `log` of a possibly-zero value;
(5) `model.eval()` never called during validation; (6) shuffle disabled;
(7) a layer built but never called in `forward`. For each, note which triage
step caught it and how long it took.

**You have this skill when** you diagnose all seven from the curves and the
instrumentation alone, without reading the diff.
:::

:::exercise
1. Explain why a classifier that outputs a constant has cross-entropy exactly
   $\ln C$, and compute it for $C = 1000$.
2. Build a model with a disconnected layer and write the check that finds it.
3. † Induce a `nan` eight layers deep and localise it with (a) anomaly
   detection and (b) forward hooks. Compare the time each takes.
4. Create dead ReLUs by using too high a learning rate, and show the zeros
   fraction rising. Fix it two ways.
5. Leave dropout on at evaluation and quantify the effect on validation loss.
6. † Reproduce the "works at batch 8, diverges at 512" failure and fix it with
   warmup plus linear LR scaling. Report the warmup length needed.
7. Construct a distributed hang from a rank-dependent branch, and explain what
   NCCL is waiting for.
:::

:::recap
- Triage in order: overfit eight examples, inspect the data, check gradients
  flow, and only then tune.
- A flat loss at $\ln C$ means a constant output; zero gradients mean a
  severed graph; `nan` after a decrease means the learning rate exceeded the
  curvature bound.
- Instrument every model with per-parameter gradient norms, grad-to-weight
  ratios, and activation statistics.
- Read activation std across depth: shrinking means dying signal, growing
  means impending overflow.
- Overfitting *instantly* is leakage, not success.
- The bug is usually several layers before where the error surfaces.
- For distributed failures, first reproduce on one GPU.
:::
