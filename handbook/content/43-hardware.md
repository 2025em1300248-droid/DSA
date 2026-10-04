# Hardware and Where the Time Goes
@short: Hardware
@subtitle: The roofline, the memory hierarchy, and reading a profile
@tier: advanced
@prereq: Chapter 7
@blurb: Every performance problem in machine learning is one of three things: not enough parallelism, too many bytes moved, or waiting for something else. This chapter gives you the model that tells you which, the profiling workflow that confirms it, and enough GPU architecture to know what is worth optimising and what is not.
@objectives:
- Explain the GPU memory hierarchy and its bandwidth ratios
- Place any operation on the roofline and predict its ceiling
- Explain why kernel fusion and FlashAttention work
- Read a profile and attribute time correctly
- Decide when a custom kernel is worth writing --- usually it is not

## The memory hierarchy

@fig: gpu_hierarchy | 168 | The hierarchy on a modern accelerator. Each level is roughly an order of magnitude smaller and an order of magnitude faster than the one below. Almost all performance work is moving data up this diagram and keeping it there.

| Level | Size | Bandwidth | Latency | Managed by |
|---|---|---|---|---|
| Registers | ~256 KB/SM | ~100 TB/s | ~1 cycle | the compiler |
| Shared memory / L1 | ~228 KB/SM | ~30 TB/s | ~30 cycles | **you** |
| L2 cache | ~50 MB | ~10 TB/s | ~200 cycles | the hardware |
| HBM (device memory) | 80--192 GB | 3--8 TB/s | ~500 cycles | you, via allocation |
| Host RAM over PCIe | TB | ~60 GB/s | ~10 µs | you, explicitly |
| NVMe | TB | ~7 GB/s | ~100 µs | you, explicitly |

@tbl: Representative figures for a current data-centre GPU; exact numbers vary by generation. The two ratios worth memorising are that shared memory is about 10× HBM bandwidth, and that PCIe is about 50× slower than HBM --- which is why a `.cpu()` call inside a training loop is catastrophic.

:::hardware The arithmetic that governs everything
A modern accelerator does roughly 1000 TFLOP/s of bf16 matmul and moves about
3 TB/s from HBM. That is a ridge point of about **330 FLOP per byte**
(Chapter 7).

Almost nothing naive reaches it:
- Elementwise add: 1 FLOP per 12 bytes → intensity 0.08.
- Softmax: a few FLOPs per 4 bytes → intensity ~1.
- Matrix--vector: intensity ~1.
- Matrix--matrix, large: intensity in the hundreds or thousands.

So the hardware is designed for one operation --- large matrix multiply ---
and everything else is a tax. The whole art of ML systems engineering is
arranging for as much of the work as possible to be that one operation, and
for everything else to happen *while the data is already close*.
:::

## The roofline, used

$$\text{attainable FLOP/s} = \min\big(\text{peak FLOP/s},\; \text{bandwidth} \times I\big)$$

```python title="Place an operation on the roofline before optimising it"
def roofline(flops, bytes_moved, peak_tflops=1000, bw_tbs=3.0):
    I = flops / bytes_moved
    ridge = peak_tflops * 1e12 / (bw_tbs * 1e12)
    attainable = min(peak_tflops * 1e12, bw_tbs * 1e12 * I)
    return dict(intensity=round(I, 2), ridge=round(ridge, 1),
                bound="compute" if I > ridge else "memory",
                ceiling_tflops=round(attainable / 1e12, 1),
                min_time_us=round(flops / attainable * 1e6, 1))

# A 4096x4096 bf16 matmul against a batch of 1:
print(roofline(2*4096*4096*1, 4096*4096*2))     # memory-bound, 0.3% of peak
# The same weights against a batch of 2048:
print(roofline(2*4096*4096*2048, 4096*4096*2 + 2*4096*2048*2))
```

:::insight The question to ask before any optimisation
**"Is this operation above or below the ridge point?"**

*Below* (memory-bound): extra arithmetic is free. Fuse operations, recompute
instead of storing, use a cheaper precision --- anything that moves fewer
bytes. Reducing FLOPs will do nothing.

*Above* (compute-bound): bytes are free. Use tensor cores, improve tiling,
raise occupancy. Reducing bytes will do nothing.

Optimising the wrong side of the ridge is the single most common waste of
effort in performance work, and the roofline calculation that prevents it
takes two minutes.
:::

## Fusion

Each separate kernel reads its input from HBM and writes its output back. A
chain of elementwise operations therefore pays the memory cost once per
operation, for arithmetic that is almost free.

```python title="Five kernels become one"
# Unfused: 5 kernels, 5 round trips to HBM
x = x + bias            # read x, read bias, write x
x = x * scale           # read x, write x
x = torch.tanh(x)       # read x, write x
x = x * mask            # read x, read mask, write x
x = x + residual        # read x, read residual, write x

# Fused: 1 kernel, 1 round trip. Same FLOPs; ~5x faster because it was
# memory-bound all along.
x = torch.compile(fused_fn)(x, bias, scale, mask, residual)
```

`torch.compile` does this automatically, which is most of where its speedup
comes from. The remaining manual cases are the ones where a fusion needs an
algorithmic change --- which is what FlashAttention is.

## FlashAttention

Naive attention materialises the $T \times T$ score matrix in HBM: $O(T^2)$
memory, and three full round trips (write scores, read for softmax, read for
the value multiply). At $T = 8192$ that matrix alone is 128 MB per head.

FlashAttention never writes it. It tiles the computation so that a block of
queries and a block of keys are loaded into **shared memory**, the partial
attention is computed there, and an *online softmax* update keeps a running
maximum and sum so the result is exact without ever seeing the whole row.

```python title="The online softmax recurrence, which is the whole trick"
# Processing blocks of keys one at a time, maintaining:
#   m  = running maximum of the logits seen so far
#   l  = running sum of exp(logit - m)
#   o  = running weighted sum of values
#
# For a new block with max m_new:
#   m'  = max(m, m_new)
#   l'  = l * exp(m - m') + l_new * exp(m_new - m')
#   o'  = o * exp(m - m') + o_new * exp(m_new - m')
#
# The exp(m - m') rescaling corrects the earlier partial results for the
# new maximum. The final result is numerically identical to computing
# softmax over the whole row at once.
```

| | Naive | FlashAttention |
|---|---|---|
| HBM traffic | $O(T^2)$ | $O(T^2 d / M)$, $M$ = shared memory |
| Peak memory | $O(T^2)$ | $O(T)$ |
| FLOPs | $O(T^2 d)$ | $O(T^2 d)$ --- **the same, plus recomputation** |
| Speedup at $T=8192$ | 1× | 2--4× |

@tbl: FlashAttention performs *more* arithmetic (it recomputes attention in the backward pass) and is several times faster, because attention was memory-bound. This is the roofline argument made concrete, and it is the clearest demonstration in the field that FLOPs are the wrong thing to count.

## Reading a profile

```python title="Profile, then attribute"
from torch.profiler import profile, ProfilerActivity, schedule

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=schedule(wait=1, warmup=2, active=4),
    record_shapes=True, with_stack=True,
) as prof:
    for _ in range(7):
        train_step(); prof.step()

print(prof.key_averages().table(sort_by="self_cuda_time_total", row_limit=25))
```

| Observation | Meaning | Action |
|---|---|---|
| Many small kernels, low GPU utilisation | launch overhead dominates | fuse; `torch.compile`; CUDA graphs |
| Large gaps between kernels | the CPU cannot keep up | more dataloader workers; remove `.item()` |
| `aten::copy_` high in the list | device transfers | keep tensors on device; pin memory |
| `cudaStreamSynchronize` prominent | a forced sync | find the `.item()`/`.cpu()` causing it |
| One kernel dominates and is a matmul | you are compute-bound | this is the good case; check it uses tensor cores |
| `Memcpy DtoH` in the inner loop | logging a tensor | accumulate on device, sync once per N steps |

@tbl: Reading a profile. The first two rows together account for most disappointing GPU utilisation in practice, and neither is fixed by a faster model.

:::perf Check tensor-core utilisation before anything clever
```bash
nsys profile -o trace python train.py          # timeline
ncu --set full -k <kernel> python train.py     # one kernel in detail
```
If your matmuls are not using tensor cores you are leaving roughly 8× on the
table, and the cause is usually mundane: fp32 instead of bf16, or a dimension
that is not a multiple of 8 (or 16 for fp8). Padding a hidden dimension from
4090 to 4096 can be worth a large fraction of peak.
:::

## Writing a custom kernel

```python title="Triton: a custom kernel without CUDA"
import triton, triton.language as tl

@triton.jit
def fused_scale_relu(x_ptr, out_ptr, scale, n, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    offs = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offs < n
    x = tl.load(x_ptr + offs, mask=mask)       # one read from HBM
    y = tl.maximum(x * scale, 0.0)             # all arithmetic in registers
    tl.store(out_ptr + offs, y, mask=mask)     # one write
```

:::warning Almost never write a custom kernel
In order, try: `torch.compile`; an existing fused operator
(`F.scaled_dot_product_attention`, `torch.addmm`, fused optimisers); a
library (FlashAttention, xFormers, Liger); *then* Triton; and CUDA only if
Triton cannot express it.

A custom kernel is justified when you have profiled, the operation is a clear
bottleneck, no library covers it, and you have a specific fusion or memory
pattern in mind that the compiler cannot find. That is a rare combination, and
the maintenance cost --- correctness across shapes, dtypes and hardware
generations --- is permanent.
:::

:::practice The task
(a) Compute the roofline position of five operations in your model and predict
which are memory-bound; (b) profile and confirm; (c) find a chain of
elementwise operations and fuse it with `torch.compile`, measuring the speedup
against your prediction; (d) compare naive attention against
`scaled_dot_product_attention` at $T$ = 1024, 4096, 16384 for both time and
peak memory; (e) find a `.item()` or `.cpu()` in an inner loop and measure its
cost; (f) pad a hidden dimension to a multiple of 8 and measure the tensor-core
effect.

**You have this skill when** you can look at a profile and say, within a
minute, whether the next hour is best spent on memory traffic, on parallelism,
or on the input pipeline.
:::

:::exercise
1. Compute the ridge point for hardware you have access to, and verify it by
   measuring FLOP/s against batch size.
2. Place softmax, layer norm, GELU and a large matmul on the roofline. Predict
   the speedup from fusing the first three.
3. † Implement the online softmax recurrence and show it gives bit-identical
   results to a full-row softmax.
4. Measure attention time and peak memory at four sequence lengths, naive and
   flash. Fit the scaling.
5. Find the largest `cudaStreamSynchronize` in a profile of yours and remove
   its cause. Report the throughput change.
6. † Write a Triton kernel fusing three elementwise operations and compare
   against `torch.compile`. Was it worth it?
7. Run the same matmul at hidden dimensions 4090 and 4096 and explain the
   difference.
:::

:::recap
- The hierarchy spans five orders of magnitude in bandwidth; shared memory is
  ~10× HBM and PCIe is ~50× slower.
- The ridge point is around 330 FLOP/byte; only large matmuls are above it.
- Ask whether an operation is above or below the ridge *before* optimising;
  below it, extra arithmetic is free and bytes are everything.
- Fusion works because elementwise chains are memory-bound; `torch.compile`
  does most of it automatically.
- FlashAttention does *more* FLOPs and is several times faster, by tiling into
  shared memory with an online softmax --- the clearest proof that FLOPs are
  the wrong thing to count.
- In a profile, many small kernels means launch overhead; gaps mean the CPU or
  the dataloader; `copy_` and `synchronize` mean an accidental transfer.
- Try compile, fused operators and libraries before Triton, and CUDA almost
  never.
:::
