# GPU Algorithm Design
@short: GPU Algorithms
@subtitle: Tiling, coalescing, and why FlashAttention does more arithmetic
@tier: expert
@prereq: Chapters 3, 39
@blurb: A GPU changes the cost model so thoroughly that algorithms which are optimal on a CPU can be badly wrong on it. The unit of execution is a warp of threads that must agree on their branches; the unit of memory is a 128-byte transaction that must be requested by consecutive threads; and the scarce resource is bandwidth, not arithmetic. This chapter derives the design rules and works through FlashAttention as the canonical example.
@objectives:
- Describe the GPU execution and memory model accurately enough to reason about cost
- Apply the four rules: coalesce, tile, avoid divergence, occupy
- Compute arithmetic intensity and place a kernel on the roofline
- Derive FlashAttention as an IO-aware algorithm and explain online softmax
- Understand why fusion and quantisation are the main serving levers
- Know which algorithmic choices to reconsider on a GPU

## The execution model in one page

A GPU has thousands of simple cores arranged in streaming multiprocessors.
Threads execute in **warps** of 32 that share a program counter, so if
threads in a warp take different branches, both branches run with the
inactive threads masked --- the cost is the *sum* of the paths, not the
maximum.

| Level | Size (typical) | Latency | Shared by |
|---|---|---|---|
| Registers | 64 K per SM | 1 cycle | one thread |
| Shared memory / L1 | 100--228 KB per SM | ~30 cycles | one block |
| L2 | 40--60 MB | ~200 cycles | whole device |
| HBM | 40--192 GB | ~400 cycles | whole device |
| Host RAM over PCIe | TB | ~10 µs | everything |

@tbl: The GPU memory hierarchy. The ratio that matters: HBM bandwidth is 2--8 TB/s while compute is 100--1000 TFLOP/s, so the machine can do 100--500 FLOPs per byte fetched. A kernel with lower arithmetic intensity is bandwidth-bound, full stop.

## The four rules

**1. Coalesce.** Consecutive threads must read consecutive addresses, so the
hardware merges 32 requests into one transaction.

@fig: coalescing | 138 | Coalesced versus strided access. The arithmetic is identical; the memory traffic differs by 32x. This single property decides the performance of most memory-bound kernels.

This is why layout matters so much (Chapter 3): a kernel over a
`(batch, seq, dim)` tensor should have its fastest-varying thread index on
`dim`, and if your data is laid out the other way you must transpose it
first. It is also why `NHWC` beats `NCHW` for convolutions on tensor cores.

**2. Tile.** Load a block of data into shared memory once and reuse it many
times.

$$\text{naive matmul: } \Theta(n^3) \text{ HBM reads} \quad\longrightarrow\quad
\text{tiled with tile } b: \Theta(n^3/b + n^2)$$

Each element of a $b \times b$ tile is used $b$ times while resident. With
$b = 64$ that is a 64x reduction in memory traffic for identical arithmetic.
Every fast GEMM, convolution and attention kernel is tiled.

**3. Avoid divergence.** Within a warp, branches serialise. Replace
`if (x > 0) y = a; else y = b;` with arithmetic: `y = (x > 0) * a +
(x <= 0) * b`, or use predication. Data-dependent loop bounds are worse ---
if one thread iterates 100 times and its 31 neighbours iterate once, the warp
takes 100 iterations. This is why ragged workloads must be sorted or padded
into uniform buckets before a kernel runs.

**4. Occupy.** Each SM can host many warps concurrently and switches between
them for free, which is how it hides memory latency. Occupancy is limited by
registers per thread and shared memory per block. Using too much of either
reduces the number of resident warps, and past a point the SM has nothing to
run while waiting on memory. Maximum occupancy is not the goal --- a
register-heavy kernel with 50% occupancy often beats a lean one with 100% ---
but zero slack is fatal.

## The roofline

:::math Where your kernel lives
Plot achievable FLOP/s against arithmetic intensity $I$ (FLOPs per byte of
HBM traffic):
$$\text{attainable} = \min(\text{peak FLOP/s},\; I \times \text{bandwidth})$$
The ridge point is at $I^* = \text{peak FLOP/s} / \text{bandwidth}$, about
100--500 on modern accelerators.

- $I \ll I^*$: memory-bound. Reducing FLOPs does nothing; reduce bytes.
- $I \gg I^*$: compute-bound. Use tensor cores, lower precision, better
  tiling.

Elementwise ops have $I \approx 0.1$. LayerNorm and softmax, $I \approx 1$.
Attention during decoding, $I \approx 1$. Batched GEMM with large matrices,
$I = \Theta(n)$. This is why almost everything except the big matmuls is
memory-bound.
:::

## FlashAttention

Standard attention computes $S = QK^\top$ ($n \times n$), then
$P = \text{softmax}(S)$, then $O = PV$. For $n = 8192$ the score matrix is
268 million float16 values --- 537 MB --- written to HBM and read back twice.

@fig: flash_tiling | 168 | FlashAttention. The $n \times n$ score matrix is never materialised: $Q$, $K$ and $V$ are tiled so each block of scores is computed, consumed and discarded inside SRAM, with an online softmax carrying a running maximum and sum.

The obstacle is the softmax: it needs a global maximum and a global sum over
each row, and a tiled computation only sees part of a row at a time. The
resolution is the **online softmax**, which is a streaming algorithm
(Chapter 38) with a rescaling correction.

:::math Online softmax
Process a row in blocks. Maintain the running maximum $m$ and running sum
$\ell$ and output accumulator $O$. On seeing block $j$ with scores $s^{(j)}$:
$$m_{\text{new}} = \max(m, \max_i s^{(j)}_i), \qquad
\alpha = e^{m - m_{\text{new}}}$$
$$\ell_{\text{new}} = \alpha\,\ell + \sum_i e^{s^{(j)}_i - m_{\text{new}}},
\qquad
O_{\text{new}} = \alpha\,O + \big(e^{s^{(j)} - m_{\text{new}}}\big) V^{(j)}$$
The factor $\alpha$ rescales everything accumulated so far to the new
maximum. At the end, divide $O$ by $\ell$. The result is *exactly* the
softmax --- this is not an approximation --- and it never needs more than one
block of scores in memory at a time.
:::

```python title="Online softmax attention, the algorithm (not the kernel)"
import numpy as np

def flash_attention(Q, K, V, block=64):
    """Mathematically identical to softmax(QK^T)V, with O(n) memory."""
    n, d = Q.shape
    O = np.zeros((n, d), dtype=np.float32)
    for i in range(0, n, block):                 # tile over queries
        q = Q[i:i + block]
        m = np.full((len(q), 1), -np.inf, dtype=np.float32)
        l = np.zeros((len(q), 1), dtype=np.float32)
        acc = np.zeros((len(q), d), dtype=np.float32)
        for j in range(0, n, block):             # tile over keys/values
            k, v = K[j:j + block], V[j:j + block]
            s = q @ k.T / np.sqrt(d)             # the tile, stays in SRAM
            m_new = np.maximum(m, s.max(axis=1, keepdims=True))
            alpha = np.exp(m - m_new)            # rescale what we have
            pexp = np.exp(s - m_new)
            l = alpha * l + pexp.sum(axis=1, keepdims=True)
            acc = alpha * acc + pexp @ v
            m = m_new
        O[i:i + block] = acc / l
    return O
```

:::insight The lesson that generalises beyond attention
FlashAttention performs *more* floating-point operations than the standard
implementation --- the rescaling is extra work, and the backward pass
recomputes the scores rather than storing them --- and it is two to four
times faster, with memory linear rather than quadratic in sequence length.

The reason is Chapter 3's thesis in its strongest form: on this hardware,
the cost of an algorithm is the bytes it moves, and an algorithm that trades
arithmetic for locality wins. When you are optimising a kernel, count HBM
traffic, not FLOPs.
:::

## What to reconsider on a GPU

| CPU intuition | GPU reality |
|---|---|
| Fewer operations is better | Fewer *bytes moved* is better |
| Branches are cheap | Divergent branches serialise the warp |
| Recomputation is waste | Recomputation is often cheaper than storing |
| Linked structures are fine | Pointer chasing has no parallelism |
| Sorting is $\Theta(n \log n)$ | Radix sort is $\Theta(kn)$ and branch-free |
| `if` inside a loop is free | Sort or bucket first so warps are uniform |
| Small kernels are fine | Launch overhead is ~5 µs; fuse them |
| Dynamic shapes are fine | They trigger recompilation and sync points |

@tbl: Eight inversions. Each has produced a real production regression in code written with CPU habits.

:::ml The three levers in serving, in order
1. **Batching.** Decoding is memory-bound (Chapter 36), so processing 32
   sequences costs barely more than one --- the weights are read once
   either way. Continuous batching is the single largest throughput lever.
2. **Quantisation.** Weights in int8 or fp8 halve or quarter the bytes read
   per token. Since decoding is bandwidth-bound, that is close to a
   proportional speedup.
3. **Fusion.** Each unfused elementwise operation is a full read and write of
   the activation tensor. Fusing a chain of ten into one kernel removes
   eighteen of the twenty HBM round trips. This is what `torch.compile`,
   Triton and TensorRT are for.

Notice that none of these reduces the arithmetic. All three reduce bytes
moved.
:::

:::exercise
1. Write a coalesced and a strided CUDA (or Triton, or CuPy) kernel that sum
   an array, and measure the bandwidth of each.
2. Implement naive and tiled matrix multiplication and measure the achieved
   FLOP/s. Compute the HBM traffic of each and confirm the $b$-fold
   reduction.
3. Place five kernels on a roofline plot for your device: vector add,
   softmax, LayerNorm, a $4096^3$ GEMM, and attention decoding at batch 1.
4. Implement `flash_attention` and verify it matches standard attention to
   float32 precision. Measure peak memory against sequence length for both.
5. Derive the online-softmax rescaling and prove it yields the exact softmax.
6. Construct a warp-divergent kernel (a data-dependent loop bound) and
   measure the slowdown against a sorted-input version.
7. Measure kernel launch overhead by timing $10^5$ trivial kernels, and
   compute how many fused operations it takes to amortise it.
8. Take a small model, apply `torch.compile`, and count the kernels before
   and after with a profiler. Attribute the speedup to fusion versus other
   effects.
:::

:::recap
- GPU threads run in warps of 32 sharing a program counter; divergent
  branches serialise.
- Consecutive threads must touch consecutive addresses, or memory traffic
  multiplies by up to 32.
- Tiling reuses loaded data from shared memory and is what makes GEMM,
  convolution and attention fast.
- Compute arithmetic intensity and place the kernel on the roofline before
  optimising; below the ridge point, only reducing bytes helps.
- FlashAttention never materialises the $n \times n$ scores, using an online
  softmax with a rescaling correction; it does more arithmetic and is several
  times faster.
- On a GPU, recomputation can be cheaper than storage, sorting is
  branch-free radix sort, and small kernels should be fused.
- The three serving levers --- batching, quantisation, fusion --- all reduce
  bytes moved, not operations.
:::
