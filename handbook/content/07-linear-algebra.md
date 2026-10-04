# Linear Algebra as Data Movement
@short: Linear Algebra
@subtitle: Why a matrix multiply is fast and a matrix--vector product is not
@tier: foundation
@prereq: none
@blurb: Linear algebra taught as mathematics gives you the identities. Linear algebra taught as data movement gives you something more useful: the ability to predict, before writing any code, how fast an operation will run and why. This chapter builds both, starting from what a matrix actually does and ending at the arithmetic-intensity argument that explains most of modern ML systems engineering.
@objectives:
- Read a matrix as a linear map, a change of basis, and a table of data
- Compute the FLOPs and bytes of any operation you write
- Explain why batch size changes the performance regime, not just the speed
- Use the four decompositions that appear in practice
- Recognise the shape errors that broadcasting hides

## A matrix is three things at once

The same object, read three ways, and you need all three.

**As a linear map.** $A \in \mathbb{R}^{m \times n}$ takes a vector in
$\mathbb{R}^n$ to one in $\mathbb{R}^m$. Column $j$ of $A$ is where the $j$-th
basis vector lands. That single sentence explains matrix--vector
multiplication: $Ax$ is the combination of $A$'s columns weighted by $x$'s
entries.

$$Ax = x_1 a_1 + x_2 a_2 + \cdots + x_n a_n$$

**As a change of basis.** If $A$ is square and invertible, it re-expresses a
vector in different coordinates. This is what an embedding layer, a
projection head and a rotation all are.

**As a table of data.** A batch of $B$ examples with $d$ features is a $B
\times d$ matrix. This reading is the one that makes shapes concrete, and it
is where the errors live.

:::insight The one convention that removes shape confusion
Write every tensor's shape next to it and read a matrix product
left to right as a *contraction over the shared dimension*:
$(B \times d) \cdot (d \times h) \to (B \times h)$. The inner dimensions must
match and they disappear; the outer ones survive. Every shape error is a
violation of that sentence.
:::

## The cost model: FLOPs and bytes

Here is the calculation that determines the performance of everything you
will write.

For $C = AB$ with $A \in \mathbb{R}^{m \times k}$ and
$B \in \mathbb{R}^{k \times n}$: each of the $mn$ output entries is a dot
product of length $k$, costing $k$ multiplies and $k-1$ adds. So

$$\text{FLOPs} = 2mnk, \qquad \text{bytes} = 2(mk + kn + mn) \;\text{ in bf16}$$

The ratio of these two numbers is the **arithmetic intensity**: FLOPs
performed per byte moved.

$$I = \frac{2mnk}{2(mk + kn + mn)}$$

@fig: arithmetic_intensity | 150 | The roofline. Below the ridge point an operation is limited by memory bandwidth and the extra FLOPs are free; above it, by compute. Almost every optimisation in ML systems is an attempt to move an operation rightwards.

Work two cases with real numbers, on hardware with roughly 1000 TFLOP/s of
bf16 compute and 3 TB/s of memory bandwidth --- a ridge point of about
330 FLOP/byte.

| Operation | Shapes | FLOPs | Bytes (bf16) | Intensity | Regime |
|---|---|---|---|---|---|
| Matrix--vector | $(4096{\times}4096)(4096{\times}1)$ | 34 M | 34 MB | **1.0** | memory-bound |
| Small batch | $(4096{\times}4096)(4096{\times}8)$ | 268 M | 34 MB | 7.9 | memory-bound |
| Large batch | $(4096{\times}4096)(4096{\times}2048)$ | 69 G | 67 MB | **1024** | compute-bound |

@tbl: The same weight matrix, three batch sizes. The weights are read once regardless of batch size, so intensity grows roughly linearly with batch until the ridge point is crossed. This single table explains continuous batching, why token generation is slow, and why training is efficient and inference is not.

:::hardware The consequence you meet every day
Generating one token at a time is a matrix--vector product: intensity 1, so
the GPU is at roughly 0.3% of its peak FLOPs and is simply waiting on
memory. Batching 64 requests together multiplies the work by 64 and the time
by almost nothing, because the weights --- which dominate the bytes --- are
read once for the whole batch.

This is not an implementation detail. It is the reason inference servers
exist, the reason `vLLM` batches continuously, and the reason speculative
decoding works at all (Chapter 40).
:::

## The operations, and their costs

```python title="Know these four costs by heart"
import numpy as np
A = np.random.randn(1024, 1024).astype(np.float32)
x = np.random.randn(1024).astype(np.float32)
B = np.random.randn(1024, 1024).astype(np.float32)

A @ x        # matvec:   2 m n      FLOPs, ~m n  bytes  → memory-bound
A @ B        # matmul:   2 m n k    FLOPs, ~m n  bytes  → compute-bound
A * B        # elementwise: m n     FLOPs, 3 m n bytes  → always memory-bound
A.sum(axis=0)  # reduction: m n     FLOPs,  m n  bytes  → memory-bound
```

Elementwise operations are *always* memory-bound: one FLOP per three values
touched, an intensity of about 1/6. This is why kernel fusion matters so much
--- ten fused elementwise ops cost almost exactly what one costs, because the
data is read once and kept in registers. It is the entire argument for
`torch.compile`.

## Norms, projections and similarity

```python title="The geometry you use in retrieval"
def cosine(a, b):
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

# If vectors are L2-normalised, cosine similarity IS the dot product,
# and the ranking by cosine equals the ranking by (negative) L2 distance:
#   ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a·b = 2 - 2 a·b
A = A / np.linalg.norm(A, axis=1, keepdims=True)
scores = A @ q                      # one matmul ranks the whole corpus
```

That identity is why every vector database normalises on ingest: it converts
a distance computation into a matrix multiply, which is the one operation
hardware is good at.

| Norm | Definition | Used for |
|---|---|---|
| $\|x\|_1$ | $\sum_i \lvert x_i \rvert$ | sparsity-inducing regularisation |
| $\|x\|_2$ | $\sqrt{\sum_i x_i^2}$ | distance, gradient clipping |
| $\|x\|_\infty$ | $\max_i \lvert x_i \rvert$ | worst-case bounds, quantisation range |
| $\|A\|_F$ | $\sqrt{\sum_{ij} A_{ij}^2}$ | weight-change magnitude |

@tbl: The four norms that appear in ML code. Gradient clipping uses the global $\ell_2$ norm across all parameters, not per-tensor --- a distinction that changes training dynamics.

## Four decompositions that matter

**Eigendecomposition** $A = Q \Lambda Q^{-1}$, for square $A$. Symmetric
matrices give orthogonal $Q$ and real eigenvalues. Where you meet it: the
Hessian's eigenvalues determine the maximum stable learning rate; a
covariance matrix's eigenvectors are the principal components.

**SVD** $A = U \Sigma V^\top$, for any matrix. The singular values $\sigma_i$
are the gains along orthogonal directions. Truncating to the top $r$ gives the
best rank-$r$ approximation in Frobenius norm (Eckart--Young).

```python title="SVD is the theory behind LoRA"
U, S, Vt = np.linalg.svd(W, full_matrices=False)
W_r = (U[:, :r] * S[:r]) @ Vt[:r]          # best rank-r approximation
# A weight update Delta_W that is genuinely low-rank can be stored as
# B @ A with B: (d, r), A: (r, d)  —  2 d r params instead of d^2.
# For d = 4096, r = 16: 131k instead of 16.8M — a 128x reduction.
```

**QR** $A = QR$. Numerically stable least squares; used inside iterative
eigensolvers.

**Cholesky** $A = LL^\top$ for positive-definite $A$. Twice as fast as LU,
and the standard way to sample from a multivariate Gaussian or invert a
Gram matrix in Gaussian processes.

:::math Why the softmax denominator is a sum of exponentials
Softmax is the unique function mapping real scores to a probability
distribution that is (a) monotone in each score, (b) invariant to adding a
constant to all scores, and (c) consistent with the exponential family. Fact
(b) is what makes the numerically stable implementation valid:

$$\text{softmax}(z)_i = \frac{e^{z_i}}{\sum_j e^{z_j}} = \frac{e^{z_i - c}}{\sum_j e^{z_j - c}}$$

for any $c$. Taking $c = \max_j z_j$ makes the largest exponent zero and every
other one negative, so nothing overflows. Every framework does this; if you
write softmax yourself and skip it, you get `inf/inf = nan` for scores above
about 88 in fp32.
:::

## Broadcasting: the rules, and the bug

NumPy and PyTorch align shapes from the *right*, and a dimension of size 1
stretches to match.

```python
(3, 4) + (4,)      -> (3, 4)     ✓ row added to every row
(3, 4) + (3, 1)    -> (3, 4)     ✓ column added to every column
(3, 4) + (3,)      -> ERROR      ✗ 4 vs 3 at the last axis
(32, 1) - (32,)    -> (32, 32)   ✗✗ SILENT, and almost never intended
```

The third case errors loudly, which is fine. The fourth is the dangerous one:
a column vector minus a row vector is a full outer difference matrix, and it
is the most expensive silent bug in numerical code.

```python title="The one-line habit that prevents it"
def mse(pred, target):
    assert pred.shape == target.shape, f"{pred.shape} vs {target.shape}"
    return ((pred - target) ** 2).mean()
```

:::pitfall Where the `(n, 1)` comes from
You rarely write `(n, 1)` deliberately. It arrives from
`model(x)` on a single-output head, from `df[["col"]]` instead of
`df["col"]`, from `keepdims=True`, and from `y.reshape(-1, 1)` written for
sklearn. Then it meets a `(n,)` label array and the loss is quietly computed
over $n^2$ pairs. The loss still decreases --- it is just optimising the
wrong thing.
:::

:::practice The task
For one transformer layer with $d = 4096$, $h = 32$ heads, sequence length
$T = 2048$, batch $B$: (a) write down the FLOPs and bytes of every matmul as
a function of $B$; (b) compute the arithmetic intensity of each at $B = 1$ and
$B = 64$; (c) predict which are memory-bound on your hardware; (d) measure
with `torch.profiler` and compare. Then (e) implement a stable softmax and
find the input at which the naive version produces `nan`.

**You have this skill when** you can predict, within a factor of two and
before running anything, how long a layer will take at a given batch size ---
and say whether more FLOPs would be free.
:::

:::exercise
1. Show that $Ax$ is a weighted sum of $A$'s columns, and $x^\top A$ a
   weighted sum of its rows. State which is contiguous in row-major memory.
2. Compute the ridge point (FLOP/byte) of a GPU you have access to, from its
   published bandwidth and peak bf16 throughput.
3. † Derive the arithmetic intensity of attention as a function of
   sequence length, and explain from it why FlashAttention helps.
4. Verify Eckart--Young numerically: truncate an SVD at several ranks and
   compare to the best rank-$r$ approximation found by random search.
5. Show that for L2-normalised vectors, ranking by cosine and by Euclidean
   distance give the identical order. Then find a case where they differ
   without normalisation.
6. † Time `A @ B` for $B$ of width 1, 8, 64, 512, 4096. Plot
   FLOP/s against width and identify the ridge point empirically.
7. Construct four distinct ways an `(n, 1)` accidentally meets an `(n,)` in
   real code, and write the assertion that catches all four.
:::

:::recap
- A matrix is a linear map, a change of basis and a table of data; you need
  all three readings.
- FLOPs $= 2mnk$; bytes are the operands; their ratio is arithmetic intensity
  and it determines the regime.
- Matrix--vector is memory-bound, matrix--matrix is compute-bound; batching
  moves you from one to the other, which is the foundation of inference
  serving.
- Elementwise ops are always memory-bound, which is why fusion works.
- Normalised vectors turn cosine similarity into a matrix multiply.
- SVD gives the best low-rank approximation --- the theory behind LoRA.
- Softmax subtracts the max for stability; this is valid because softmax is
  shift-invariant.
- Broadcasting between $(n,1)$ and $(n,)$ silently produces an $n \times n$
  result; assert shape equality before every loss.
:::
