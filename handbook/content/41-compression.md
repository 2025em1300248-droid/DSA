# Quantisation, Pruning and Distillation
@short: Compression
@subtitle: Making a model smaller without making it worse
@tier: advanced
@prereq: Chapter 40
@blurb: Three ways to shrink a model, with different trade-offs and very different amounts of work. Quantisation is nearly free and should usually be your first move; distillation gives the largest gains and costs the most. This chapter covers how each works, what it costs in quality, and how to measure that honestly.
@objectives:
- Explain quantisation formats and choose between them
- Apply post-training quantisation and know when QAT is needed
- Understand why outlier channels make LLM quantisation hard
- Distil a large model into a small one for a specific task
- Measure compression quality loss with intervals, not anecdotes

## Quantisation

Store weights (and sometimes activations) in fewer bits. Memory falls
proportionally, and because decode is memory-bound (Chapter 30), **throughput
rises by roughly the same factor.**

$$q = \text{round}\!\left(\frac{x}{s}\right) + z, \qquad \hat{x} = s\,(q - z)$$

where $s$ is the scale and $z$ the zero point. Everything interesting is in
how $s$ is chosen and over what group of values.

| Format | Bits | Memory vs fp16 | Typical quality loss | Notes |
|---|---|---|---|---|
| fp16 / bf16 | 16 | 1.0× | baseline | the reference |
| fp8 (e4m3) | 8 | 0.5× | negligible | needs recent hardware; often free |
| int8 | 8 | 0.5× | very small with per-channel scales | widely supported |
| int4 (GPTQ / AWQ) | 4 | 0.25× | small, task-dependent | the practical floor for most uses |
| NF4 (QLoRA) | 4 | 0.25× | small | normal-distribution-optimal levels |
| int3 and below | ≤3 | 0.19× | substantial | research territory |

@tbl: Quantisation formats. The step from 16 to 8 bits is nearly free on supported hardware; 8 to 4 is where measurement becomes mandatory; below 4 bits, quality loss is real and task-dependent.

:::math Granularity is what makes quantisation work
**Per-tensor**: one scale for the whole matrix. Simple, and poor --- a single
large value forces a scale that destroys the resolution of everything else.

**Per-channel**: one scale per output channel. Much better, standard for int8.

**Per-group**: one scale per group of 64 or 128 weights along the input
dimension. Standard for int4, and the reason int4 works at all.

The storage overhead is small: at group size 128 with fp16 scales, the extra
cost is $16/128 = 0.125$ bits per weight. That is a rounding error against
the 12 bits saved.
:::

:::pitfall Outlier channels are why LLM quantisation is hard
Transformer activations contain a small number of channels --- often fewer
than 1% --- whose magnitudes are 10 to 100 times everything else, and they
are consistently the *same* channels across inputs.

Quantising naively, those outliers set the scale and the remaining 99% of
values collapse into a handful of levels. This is why early int8 attempts on
large models failed badly while working fine on smaller ones.

The three fixes, all now standard:
- **LLM.int8()**: keep the outlier channels in fp16 and quantise the rest.
- **SmoothQuant**: migrate the difficulty from activations into weights by
  rescaling, since weights are easier to quantise.
- **AWQ**: identify the salient weight channels (by activation magnitude) and
  protect them with per-channel scaling.
:::

```python title="Post-training quantisation with a calibration set"
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained("your/model")
model.quantize(
    tokenizer,
    quant_config=dict(w_bit=4, q_group_size=128, zero_point=True,
                      version="GEMM"),
    calib_data=calibration_texts,     # 128-512 samples FROM YOUR DOMAIN
)
```

The calibration set matters more than people expect: it determines the scales,
so calibrating a code model on web text produces worse quantisation than
calibrating it on code. Use 128--512 samples from your actual traffic.

**Quantisation-aware training** simulates quantisation during training so the
weights adapt to it. It recovers most of the loss at 4 bits and below, and
costs a training run --- worth it only when post-training quantisation has
been measured and found insufficient.

## Pruning

| Type | What it removes | Speedup | Notes |
|---|---|---|---|
| Unstructured | individual weights | **none without special hardware** | high sparsity possible, rarely useful |
| 2:4 structured | 2 of every 4 weights | ~1.5--2× on supported GPUs | the practical option |
| Channel / head | whole channels or attention heads | proportional, real | needs fine-tuning after |
| Layer | whole transformer blocks | proportional, real | surprisingly effective at modest ratios |

@tbl: Pruning types. The first row is the trap: 90% unstructured sparsity sounds impressive and runs at exactly the same speed as the dense model on ordinary hardware, because the matmul kernel cannot exploit an irregular pattern.

:::insight Why pruning is less used than quantisation
Quantisation gives a guaranteed memory reduction with no change to the
computation's shape, so every kernel benefits immediately. Pruning gives a
speedup only when the sparsity pattern matches what the hardware supports,
and usually requires fine-tuning afterwards to recover quality.

For most teams the order is: quantise first, measure, and only consider
structured pruning if you still need more. Layer pruning is the exception
worth knowing: dropping a few of the least-important middle blocks and
briefly fine-tuning often costs remarkably little.
:::

## Distillation

Train a small *student* to reproduce a large *teacher*'s behaviour. This gives
the largest compression --- 10--50× is routine for a narrow task --- because
the student only has to be good at *your* task, not at everything.

```python title="Response distillation: simple, and usually enough"
# 1. Run the teacher over a large set of realistic inputs.
# 2. Filter: keep only outputs that pass verification or a judge.
# 3. Fine-tune the student on (input, teacher output) pairs — Chapter 35.
#
# The filtering step is what decides the result. Distilling unfiltered
# teacher output transfers the teacher's errors along with its skills.
```

```python title="Logit distillation: more signal per example, needs teacher access"
import torch.nn.functional as F

def distill_loss(student_logits, teacher_logits, labels, T=2.0, alpha=0.7):
    """Soft targets carry the teacher's uncertainty, which is the useful part:
       'this is a cat, but it could plausibly be a lynx' teaches more than
       the hard label 'cat'."""
    soft = F.kl_div(
        F.log_softmax(student_logits / T, dim=-1),
        F.softmax(teacher_logits / T, dim=-1),
        reduction="batchmean",
    ) * (T * T)                       # T^2 keeps the gradient scale constant
    hard = F.cross_entropy(student_logits, labels)
    return alpha * soft + (1 - alpha) * hard
```

| Approach | Needs | Transfer quality | Use when |
|---|---|---|---|
| Response (SFT on outputs) | API access only | good | the usual case |
| Logit / KD | teacher logits | better | same tokeniser, self-hosted teacher |
| Feature matching | internal activations | best | same architecture family |
| Preference distillation | teacher comparisons | good for subjective tasks | after response distillation |

@tbl: Distillation approaches by how much access to the teacher they need. Response distillation requires only an API and is where to start.

:::warning Distillation narrows the model deliberately
A distilled student matches the teacher *on the distribution it was distilled
on*, and is worse than its size would suggest everywhere else. That is the
trade, and it is usually the right one --- but it means your evaluation set
must cover the real input distribution, including the tails, or you will
discover the narrowing in production.

Also check the licence of the teacher: many model terms restrict using outputs
to train competing models.
:::

## Measuring compression honestly

```python title="The comparison that a compression claim needs"
def compression_report(base, compressed, eval_set, n_boot=10_000):
    rows = []
    for name, m in (("base", base), ("compressed", compressed)):
        scores = [grade(m(c.input), c.expected) for c in eval_set]
        mean, lo, hi = bootstrap_ci(scores, np.mean, n_boot)
        rows.append(dict(model=name, score=mean, ci=(lo, hi),
                         p50_latency=measure_latency(m, 0.50),
                         p95_latency=measure_latency(m, 0.95),
                         memory_gb=measure_memory(m),
                         throughput=measure_throughput(m)))
    rows.append(paired_test(base, compressed, eval_set))     # Chapter 37
    return rows
```

:::checklist Six things a compression claim must report
1. The evaluation set, its size, and its cluster count.
2. Both scores **with intervals**, and the paired difference.
3. Memory, throughput and p95 latency for both.
4. Performance on the **hardest stratum** separately --- compression damage
   concentrates there and is invisible in the mean.
5. Long-context behaviour separately: quantisation error accumulates over long
   sequences and short-prompt evaluation misses it.
6. The calibration data used, since it determines the result.
:::

:::practice The task
Take a model you serve. (a) Quantise to int8 and to int4 with AWQ or GPTQ,
calibrating on your own traffic; (b) measure quality with intervals, memory,
throughput and p95 latency for all three; (c) report the hardest stratum
separately and check whether the loss concentrates there; (d) evaluate at
short and long context and compare the degradation; (e) distil a small student
on 10,000 filtered teacher outputs for one narrow task and compare all four
models on cost per thousand requests; (f) calibrate int4 on the wrong domain
and show the quality difference.

**You have this skill when** you can state the exact quality cost of your
compression, with an interval, and show where it concentrates.
:::

:::exercise
1. Implement per-tensor, per-channel and per-group quantisation and compare
   reconstruction error on a real weight matrix.
2. Find the outlier channels in a transformer's activations. What fraction are
   they, and how much larger?
3. † Quantise with and without outlier handling and measure the quality gap.
   Explain the mechanism.
4. Show that 90% unstructured sparsity gives no speedup on your hardware, and
   that 2:4 sparsity does.
5. Prune the four least-important middle layers and measure quality before and
   after a short fine-tune.
6. † Distil a task-specific student at three sizes and plot quality against
   cost. Where is the knee?
7. Evaluate a 4-bit model at 1k and 32k context. Quantify the extra
   degradation at long context.
:::

:::recap
- Quantisation reduces memory proportionally, and because decode is
  memory-bound, throughput rises by about the same factor.
- Granularity is what makes it work: per-channel for int8, per-group for int4.
- Transformer activations have persistent outlier channels; LLM.int8(),
  SmoothQuant and AWQ all exist to handle them.
- Calibrate on your own domain, with 128--512 samples.
- Unstructured pruning gives no speedup on ordinary hardware; 2:4 and
  structural pruning do.
- Distillation gives the largest compression because the student only needs
  your task --- filter the teacher's outputs, and expect deliberate narrowing.
- Report both scores with intervals, the paired difference, the hardest
  stratum, and long-context behaviour separately.
:::
