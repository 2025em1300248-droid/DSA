# Hardware and Systems
@short: Hardware
@subtitle: Enough of the machine to explain a number you did not expect
@tier: advanced
@prereq: Chapters 5, 9
@blurb: You do not need to write CUDA to be an excellent ML engineer. You do need enough of the hardware model to compute a memory budget before starting a job, to explain why a kernel is slow, and to tell whether an optimisation can possibly help. This chapter is the minimum that pays for itself, plus the specialist extension.
@objectives:
- Compute memory and throughput budgets before running anything
- Place a workload on the roofline and decide what kind of optimisation helps
- Read a profile and identify the bottleneck
- Know what to learn if you want to go deeper into kernels

## The capabilities

:::checklist CORE --- the mental model
- The memory hierarchy on an accelerator: registers, shared memory/SRAM, L2,
  HBM, host memory over PCIe. Roughly an order of magnitude of latency and
  capacity between each
- Threads, warps and blocks; why divergent branches inside a warp serialise
- Coalesced memory access: consecutive threads must touch consecutive
  addresses or traffic multiplies
- Tiling: load a block into fast memory once and reuse it many times. This is
  what makes GEMM, convolution and attention fast
- **Arithmetic intensity** (FLOPs per byte moved) and the roofline: below the
  ridge point, only reducing bytes helps; above it, only reducing arithmetic
  helps. Compute it before optimising anything
- Why FlashAttention does *more* arithmetic and is several times faster
:::

:::checklist CORE --- the arithmetic you should be able to do on paper
- Model memory: $\approx 16P$ bytes for mixed-precision training with Adam
- KV cache: $4 \cdot B \cdot S \cdot L \cdot H_{kv} \cdot d_h$ bytes in fp16
- Training compute: $\approx 6PN$ FLOPs for $P$ parameters and $N$ tokens
- Inference: $\approx 2P$ FLOPs per token plus attention
- Communication: ring all-reduce sends $2(P-1)/P \times N$ bytes per worker
- Time estimate: $\max(\text{FLOPs}/\text{peak},\ \text{bytes}/\text{bandwidth})$,
  then divide by an achieved-efficiency factor of 0.3--0.6
:::

:::checklist CORE --- profiling
- `torch.profiler` with a trace viewer; Nsight Systems for the whole timeline
  and Nsight Compute for a single kernel
- Reading a timeline: gaps mean you are input-bound or synchronising; long
  memory-copy bars mean the transfer path is wrong
- Finding synchronisation points: `.item()`, `.cpu()`, `print` of a tensor,
  and data-dependent shapes such as `nonzero`
- Distinguishing compute-bound, memory-bound, input-bound and
  communication-bound with a measurement
:::

:::checklist CORE --- the practical levers
- Mixed precision, and preferring `bf16` where available
- `torch.compile`, and counting graph breaks
- Kernel fusion to remove intermediate round trips to HBM
- Choosing shapes that suit tensor cores (multiples of 8 or 16 in the
  relevant dimensions)
- Pinned memory and a separate copy stream for host-to-device transfer
- CUDA graphs for workloads with many small kernels
:::

:::checklist SPECIALIST --- if you want to go deeper
- **Triton**: a Python-embedded language for writing GPU kernels at a much
  gentler gradient than CUDA. This is the right entry point in 2026 and is
  enough to write a fused kernel that beats the framework's default
- CUDA C++ for the last increment of control
- Kernel autotuning, occupancy analysis, shared-memory bank conflicts
- Interconnect topology: NVLink within a node, InfiniBand or Ethernet
  between; why collective performance is topology-dependent
- TPUs and the XLA compilation model, if you work in that ecosystem
:::

:::insight Why this pays for an ordinary engineer
Not so you can write kernels. So that you can answer four questions without
running an experiment: *Will this fit?* *Is this optimisation capable of
helping?* *Which resource am I short of?* *Is this number plausible?* Being
able to answer those on paper saves days of speculative work per quarter, and
it is a small amount of material.
:::

## How to tell you have it

:::practice The tasks
1. For a model you use, compute on paper: training memory, KV cache at your
   context length, inference FLOPs per token, and the expected tokens per
   second on your hardware. Then measure all four and explain every gap
   larger than 2x.
2. Take a training loop at low GPU utilisation and find the bottleneck with a
   profile rather than a guess.
3. Compute the arithmetic intensity of five kernels you run and place them on
   the roofline for your device.
4. Write one fused kernel in Triton --- a fused bias-plus-activation is
   enough --- and measure it against the unfused PyTorch version.
:::

:::pitfall Optimising the wrong thing
The dominant failure here is spending a week on a kernel when the job was
input-bound, or quantising a model when the queue was the bottleneck. The
discipline is unvarying: measure, place it on the roofline, then decide what
class of optimisation can possibly help. An optimisation that reduces
arithmetic on a memory-bound kernel is guaranteed to do nothing, and you can
know that before you start.
:::

:::note Time to competence
**3--4 weeks** for CORE, which is the part with the high return.
**3--6 months** for the SPECIALIST list, and worth it only if you are aiming
at research engineering or ML platform work.
:::

:::recap
- Learn the hardware model to answer four questions on paper: will it fit,
  can this optimisation help, which resource is short, is this number
  plausible.
- Memorise the five formulas: training memory $16P$, KV cache, training
  compute $6PN$, inference $2P$ per token, all-reduce bytes.
- Compute arithmetic intensity and use the roofline before optimising.
- Profile to distinguish compute, memory, input and communication bound;
  hunt for synchronisation points.
- Triton is the right entry point for writing kernels; CUDA only if you need
  the last increment.
:::
