# Deep Learning
@short: Deep Learning
@subtitle: Enough internals to debug it, not just to call it
@tier: core
@prereq: Chapters 4, 8
@blurb: You can use deep learning productively without being able to derive it, but you cannot debug it that way --- and debugging is the job. This chapter covers the architecture knowledge, the training mechanics and the failure modes that let you look at a loss curve and form a hypothesis rather than a superstition.
@objectives:
- Implement a transformer block from scratch and predict every tensor shape
- Write a training loop and debug it when the loss does not move
- Know the modern architectural components and what problem each one solves
- Use mixed precision, checkpointing and compilation correctly

## What this is for

The difference between an engineer who can use PyTorch and one who can
*debug* PyTorch is worth a level. The second one looks at a flat loss curve
and says "check the learning rate, then check whether the labels are shuffled
relative to the inputs, then overfit a single batch" --- and is right within
three tries.

## The capabilities

:::checklist ESSENTIAL --- frameworks
- PyTorch fluently: `nn.Module`, autograd, `DataLoader`, devices, `state_dict`
- Writing a training loop by hand before reaching for a framework wrapper
- `torch.compile`, what it does (graph capture, fusion, kernel selection),
  and why graph breaks cost you the benefit
- Mixed precision: `bf16` as the default for training where supported, `fp16`
  with a gradient scaler where not, and why `bf16` is preferred (same
  exponent range as fp32, so no scaler)
- Debugging: `detect_anomaly`, hooks, `torch.profiler`, and reading a trace
- Hugging Face `transformers`, `datasets`, `accelerate`, `peft`, `trl` --- the
  practical ecosystem
- JAX at AWARENESS level: `jit`, `vmap`, `pmap`, functional style. Dominant
  in some labs and on TPUs, a minority elsewhere
:::

:::checklist ESSENTIAL --- architectures
- The transformer, completely: embeddings, positional information,
  scaled dot-product attention, multi-head attention, the feed-forward block,
  residual connections, normalisation, the output head
- Modern components and the problem each solves:
  - **RoPE** (rotary position embeddings) --- relative position, extrapolates
    better than learned absolute
  - **RMSNorm** instead of LayerNorm --- cheaper, no mean subtraction
  - **Pre-norm** instead of post-norm --- trains stably at depth
  - **SwiGLU** feed-forward --- better quality per parameter than ReLU MLP
  - **GQA / MQA** (grouped/multi-query attention) --- shrinks the KV cache
    by 4--8x, which is why long context is affordable
  - **MoE** (mixture of experts) --- more parameters at constant compute per
    token; brings routing and load-balancing problems
- CNNs: convolution, pooling, receptive field, residual blocks. Still the
  right tool for many vision problems
- Encoder-only (BERT-style, still the best choice for classification and
  embeddings), decoder-only (GPT-style), encoder--decoder (translation,
  speech)
- Diffusion models conceptually: forward noising, reverse denoising,
  classifier-free guidance, samplers
- State-space models (Mamba and successors) at AWARENESS level --- linear-time
  sequence modelling, a real alternative for very long sequences
:::

:::checklist ESSENTIAL --- training mechanics
- Loss functions and when each applies: cross-entropy, focal, contrastive
  (InfoNCE), triplet, cosine
- Optimisers: AdamW as the default, and what decoupled weight decay changed.
  Awareness of second-order and matrix-preconditioned optimisers (Shampoo,
  Muon) which have begun to show real wall-clock wins at scale
- Learning-rate schedules: warmup then cosine decay is the default; why
  warmup exists (early steps have unreliable second-moment estimates)
- Batch size and learning rate scaling; gradient accumulation to simulate a
  large batch
- Gradient clipping, and what a clipping event tells you
- Regularisation: dropout, weight decay, label smoothing, early stopping,
  data augmentation
- Initialisation and why it matters at depth
- Transfer learning and fine-tuning: which layers to freeze, discriminative
  learning rates
:::

:::checklist CORE --- efficiency
- Gradient checkpointing: trade compute for activation memory, roughly
  $\sqrt{L}$ memory for one extra forward pass
- FlashAttention and why an algorithm that does *more* arithmetic is faster
  (it moves far less data)
- Quantisation-aware training and post-training quantisation
- Knowledge distillation from a large teacher to a small student
- Profiling to find whether you are compute-bound, memory-bound or
  input-bound --- and the arithmetic to tell in advance
:::

## The debugging playbook

:::checklist When the loss does not move
1. **Overfit a single batch.** If the model cannot drive the loss to zero on
   four examples, the bug is in the model or the loss, not the data or the
   schedule. This is the single most valuable diagnostic in deep learning.
2. **Check the learning rate** by sweeping over orders of magnitude. Wrong by
   100x is the most common single cause.
3. **Check the label alignment.** Shuffled inputs relative to labels produces
   a loss that sits exactly at the entropy of the label distribution.
4. **Check the loss reduction and masking.** A mean over padded positions
   quietly scales your gradient by the padding fraction.
5. **Print shapes at every step.** A broadcast that should have been an error
   frequently is not.
6. **Check the data with your eyes.** Decode a batch back to text or images
   after the collate function, not before.
:::

:::checklist When the loss diverges or produces NaN
1. Lower the learning rate; add or lengthen warmup.
2. Add gradient clipping and log the pre-clip norm --- a spike tells you when.
3. Check for `fp16` overflow; prefer `bf16`.
4. Look for division by a near-zero quantity: a variance, a norm, a softmax
   denominator. Add epsilon inside the square root, not outside.
5. Check for a corrupt example: sort the batch losses and inspect the worst.
6. Check the initialisation scale at depth.
:::

:::pitfall The silent ones, which are worse
**Train/eval mode.** Forgetting `model.eval()` leaves dropout and batch-norm
in training mode; evaluation numbers are wrong and nothing errors.

**`zero_grad()` omitted.** Gradients accumulate across steps. The model still
trains, badly, and you will blame the learning rate.

**Non-determinism blamed on the model.** Unseeded dataloader workers, a
non-deterministic kernel, or float reduction order. Fix the seeds before
concluding anything about a change.

**Evaluating on data the model saw.** The most expensive silent bug; see
Chapter 7.
:::

## How to tell you have it

:::practice The task
Implement a decoder-only transformer from scratch in PyTorch --- no
`nn.Transformer`, no Hugging Face. Include RoPE, RMSNorm, pre-norm, SwiGLU
and grouped-query attention. Then:
1. Predict every intermediate shape on paper before running it.
2. Overfit 64 tokens to near-zero loss.
3. Train it on a small corpus to a sensible perplexity.
4. Add gradient checkpointing and measure the memory and time change.
5. Add `torch.compile` and measure the speedup; count the graph breaks.
6. Deliberately introduce each of the six "loss does not move" bugs above and
   confirm you can identify each one from the symptom alone.

Step 6 is the one that builds the skill.
:::

:::note Time to competence
**8--12 weeks** for ESSENTIAL at 12 hours a week, assuming the mathematics
from Chapter 4 is solid. The from-scratch transformer is worth two weeks on
its own and pays back permanently.
:::

:::recap
- PyTorch is the default; know `torch.compile`, mixed precision (prefer
  `bf16`), and the profiler.
- Know the modern transformer components by the problem each solves: RoPE,
  RMSNorm, pre-norm, SwiGLU, GQA, MoE.
- AdamW, warmup then cosine, gradient clipping, and scaling the learning rate
  with the batch.
- Overfitting a single batch is the highest-value diagnostic; the six-step
  playbook resolves most "loss does not move" cases.
- The silent bugs --- `eval()` mode, missing `zero_grad`, unseeded
  non-determinism, contaminated evaluation --- cost more than the loud ones.
:::
