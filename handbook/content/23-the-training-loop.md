# The Training Loop
@short: The Training Loop
@subtitle: Every line, and why it is there
@tier: core
@prereq: Chapter 22
@blurb: The training loop is twenty lines that everybody copies and few can defend line by line. This chapter writes one properly --- with gradient accumulation, clipping, scheduling, EMA, checkpointing and logging --- and explains what each piece buys, what breaks without it, and how to make it fast.
@objectives:
- Write a correct, complete training loop from memory
- Use gradient accumulation to simulate large batches
- Checkpoint so that a killed job resumes exactly, not approximately
- Log the six quantities that actually diagnose training
- Make the input pipeline stop being the bottleneck

## The loop

```python title="A complete training step, with every line justified"
model.train()
opt.zero_grad(set_to_none=True)          # None frees memory; 0.0 does not

for step, batch in enumerate(loader):
    # --- forward -----------------------------------------------------
    with autocast("cuda", dtype=torch.bfloat16):
        out = model(batch["input_ids"])
        loss = criterion(out, batch["labels"]) / ACCUM   # scale for accumulation

    # --- backward ----------------------------------------------------
    loss.backward()                       # accumulates into .grad

    if (step + 1) % ACCUM != 0:
        continue                          # keep accumulating

    # --- clip, step, schedule ----------------------------------------
    gnorm = torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_NORM)
    opt.step()
    sched.step()                          # per STEP, not per epoch
    opt.zero_grad(set_to_none=True)
    if ema is not None:
        ema.update(model)

    # --- observe -----------------------------------------------------
    if optim_step % LOG_EVERY == 0:
        log(loss=loss.item() * ACCUM, lr=sched.get_last_lr()[0],
            gnorm=gnorm.item(), step=optim_step)
```

| Line | Why | What breaks without it |
|---|---|---|
| `set_to_none=True` | frees gradient buffers | ~4 bytes/param wasted; slightly slower |
| `/ ACCUM` | keeps the loss scale constant | effective LR scales with ACCUM |
| `clip_grad_norm_` | bounds a bad batch's influence | one outlier batch can diverge the run |
| `sched.step()` per step | schedules are defined in steps | warmup finishes in one epoch instead of 500 steps |
| `ema.update` | averages weights over recent steps | noisier final checkpoint |
| `gnorm` logging | the earliest divergence signal | you find out from `nan` |

@tbl: Every line earns its place. The `/ ACCUM` line is the one most often omitted, and it silently multiplies your effective learning rate by the accumulation factor.

## Gradient accumulation

Simulates a batch of `B × ACCUM` on hardware that fits only `B`. The gradient
you get is *identical* to the large-batch gradient --- except for one thing.

:::pitfall Batch normalisation breaks under accumulation
BatchNorm computes statistics over the *micro*-batch, so accumulating four
steps of 8 gives you BatchNorm statistics from batches of 8, not 32. The
gradients differ from a true batch of 32.

LayerNorm, RMSNorm and GroupNorm are per-sample and unaffected --- which is
one more reason transformers use them. If you must use BatchNorm with
accumulation, use `SyncBatchNorm` or accept the difference and document it.
:::

```python title="Effective batch size, stated explicitly"
effective_batch = micro_batch * ACCUM * world_size
# Log this. Every hyperparameter that "stopped working after we scaled up"
# is usually a change in this number that nobody wrote down.
```

## Checkpointing that actually resumes

```python title="A checkpoint that restores the run, not just the weights"
def save(path, model, opt, sched, scaler, step, epoch, rng_state):
    tmp = f"{path}.tmp"
    torch.save({
        "model": model.state_dict(),
        "optimizer": opt.state_dict(),      # momentum and variance
        "scheduler": sched.state_dict(),    # where in the schedule
        "scaler": scaler.state_dict(),      # fp16 scale factor
        "step": step, "epoch": epoch,
        "torch_rng": torch.get_rng_state(),
        "cuda_rng": torch.cuda.get_rng_state_all(),
        "numpy_rng": np.random.get_state(),
        "python_rng": random.getstate(),
        "config": CONFIG,                   # so you know what this was
    }, tmp)
    os.replace(tmp, path)                   # atomic: never a half-written file
```

:::warning Saving only `model.state_dict()` is not a checkpoint
Resuming from weights alone restarts Adam's moments at zero and the scheduler
at step zero. The result is a visible loss spike, a warmup you did not intend,
and a run that no longer matches the one you were continuing.

Save all six: model, optimiser, scheduler, scaler, step counter and RNG
states. And write to a temporary file then `os.replace`, because a job killed
mid-`torch.save` otherwise leaves a corrupt file where your last good
checkpoint was.
:::

## What to log

@fig: training_signals | 152 | The six curves that diagnose training. Loss alone tells you almost nothing about *why*; these together localise the problem to optimisation, data, or architecture.

:::checklist The six, in priority order
1. **Training loss**, per optimiser step (not per epoch --- too coarse).
2. **Validation loss**, on a fixed subset, frequently enough to see divergence.
3. **Gradient norm**, pre-clipping. A spike precedes every divergence.
4. **Learning rate**, so you can see the schedule doing what you think.
5. **Parameter update ratio**: $\|\Delta w\| / \|w\|$ per layer. Should be
   around $10^{-3}$. Much smaller means a layer is not learning; much larger
   means it is about to blow up.
6. **Throughput** (tokens or samples per second), so a regression in the input
   pipeline is visible immediately.
:::

```python title="The update ratio, which almost nobody logs and everybody should"
@torch.no_grad()
def update_ratios(model, prev):
    out = {}
    for name, p in model.named_parameters():
        if p.grad is None:
            continue
        out[name] = ((p - prev[name]).norm() / (p.norm() + 1e-12)).item()
    return out
# Healthy: ~1e-3. Below 1e-5: that layer is frozen in practice.
# Above 1e-2: reduce the learning rate before it diverges.
```

## Making the loop fast

```python title="In order of how much they usually buy"
# 1. Compile the model (often 1.3–2x, one line)
model = torch.compile(model)              # mode="max-autotune" for more

# 2. Fixed shapes — avoid recompilation and fragmentation
loader = DataLoader(ds, batch_size=B, drop_last=True)

# 3. Fused optimiser
opt = torch.optim.AdamW(params, lr=lr, fused=True)

# 4. Enable TF32 for fp32 matmuls (Ampere and later)
torch.set_float32_matmul_precision("high")

# 5. Channels-last for convolutional models
model = model.to(memory_format=torch.channels_last)
```

:::perf Find the bottleneck before optimising it
```python
with torch.profiler.profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=3),
    on_trace_ready=torch.profiler.tensorboard_trace_handler("./tb"),
) as prof:
    for _ in range(5):
        train_step(); prof.step()
```
The decisive test is simpler than the profiler: replace the dataloader with a
single pre-loaded batch repeated. If throughput jumps, your bottleneck is the
input pipeline --- which it is, far more often than people expect. Fix it with
more workers, `pin_memory`, pre-tokenised data, or a faster format before
touching the model.
:::

## Exponential moving average

```python title="EMA: a free accuracy improvement, most of the time"
class EMA:
    def __init__(self, model, decay=0.999):
        self.decay = decay
        self.shadow = {k: v.detach().clone().float()
                       for k, v in model.state_dict().items()
                       if v.dtype.is_floating_point}

    @torch.no_grad()
    def update(self, model):
        for k, v in model.state_dict().items():
            if k in self.shadow:
                self.shadow[k].mul_(self.decay).add_(v.float(), alpha=1 - self.decay)
```

EMA averages the weights over roughly the last $1/(1-\text{decay})$ steps ---
1000 steps at decay 0.999. Because SGD bounces around the minimum rather than
sitting in it, the average is usually in a better place than any individual
point. It costs one extra copy of the weights and typically buys a small but
consistent improvement. Evaluate both and keep the better.

:::practice The task
Write the loop from memory, then check it against this chapter. Then:
(a) train with `ACCUM=4` and with a true batch of `4B`, and confirm the loss
curves match; (b) remove the `/ ACCUM` and observe the effective learning-rate
change; (c) kill the job at step 5000 and resume --- plot the loss across the
boundary and confirm there is no spike; (d) log update ratios per layer and
find the layer with the lowest; (e) replace the dataloader with a repeated
batch and measure the throughput difference.

**You have this skill when** a resumed run is indistinguishable from an
uninterrupted one, and when you can tell from the curves alone whether a
problem is optimisation, data or architecture.
:::

:::exercise
1. Show that accumulation without `/ ACCUM` multiplies the effective learning
   rate by `ACCUM`, for SGD. Is the same true for Adam? Explain.
2. Demonstrate the BatchNorm-under-accumulation discrepancy numerically.
3. † Resume from a weights-only checkpoint and from a full one. Plot both loss
   curves across the resume boundary.
4. Log gradient norms for 5000 steps and find the batches that trigger
   clipping. Inspect them.
5. Implement update-ratio logging and identify a layer with a ratio below
   $10^{-5}$. Diagnose why.
6. † Measure the speedup from `torch.compile` on your model, and find an
   operation that causes a graph break. Remove it.
7. Compare final validation metrics with and without EMA, across three seeds.
:::

:::recap
- `set_to_none=True`, dividing the loss by the accumulation factor, clipping,
  stepping the scheduler per optimiser step: every line has a failure mode
  attached.
- Accumulation reproduces a large-batch gradient exactly, except for
  BatchNorm.
- A checkpoint is model, optimiser, scheduler, scaler, step and RNG state ---
  written atomically.
- Log six things: train loss, val loss, gradient norm, learning rate,
  per-layer update ratio, throughput.
- `torch.compile`, fixed shapes, a fused optimiser and TF32 are the cheap
  speedups; but check the input pipeline first, with a repeated batch.
- EMA costs one weight copy and usually helps.
:::
