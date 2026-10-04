# The Modern Component Library
@short: Modern Components
@subtitle: RoPE, RMSNorm, SwiGLU, GQA, MoE --- what each replaced and why
@tier: advanced
@prereq: Chapter 25
@blurb: The transformer of Chapter 25 is the 2019 model. Every component has since been replaced by something measurably better, and each replacement has a specific reason. This chapter covers the five that matter, so you can read a modern model definition and know what every line is doing.
@objectives:
- Explain rotary position embeddings and why they extrapolate
- Justify RMSNorm and the removal of biases
- Derive SwiGLU's dimension adjustment
- Compute the KV-cache saving from grouped-query attention
- Understand mixture-of-experts routing and its failure modes

## What changed, and why

| Component | 2019 | Now | Reason |
|---|---|---|---|
| Position | learned absolute | **RoPE** | relative, extrapolates, no parameters |
| Normalisation | LayerNorm | **RMSNorm** | ~10% faster, no accuracy cost |
| Activation | GELU, 4× width | **SwiGLU**, 8/3× width | better loss at equal parameters |
| Attention | MHA | **GQA** | 4--8× smaller KV cache |
| Biases | everywhere | **none** | no benefit, fewer parameters |
| FFN | dense | **MoE** (sometimes) | more parameters, same FLOPs |

@tbl: Six changes, each independently validated. Together they account for a substantial share of the gap between a 2019 model and a current one at the same parameter count.

## RoPE: rotary position embeddings

Learned absolute position embeddings have two problems: they cost $T_{\max}
\times d$ parameters, and they simply do not exist beyond $T_{\max}$, so the
model cannot process a longer sequence at all.

RoPE instead *rotates* the query and key vectors by an angle proportional to
position. Take each pair of adjacent dimensions as a 2-D vector and rotate it
by $m\theta_i$ where $m$ is the position:

$$\theta_i = 10000^{-2i/d}, \qquad i = 0, 1, \ldots, d/2 - 1$$

```python title="RoPE, complete"
def rope_frequencies(dim, max_T, base=10000.0, device="cuda"):
    inv = 1.0 / (base ** (torch.arange(0, dim, 2, device=device) / dim))
    t = torch.arange(max_T, device=device)
    freqs = torch.outer(t, inv)                       # (T, dim/2)
    return torch.cos(freqs), torch.sin(freqs)

def apply_rope(x, cos, sin):
    """x: (B, H, T, D). Rotate each adjacent pair of dimensions."""
    x1, x2 = x[..., 0::2], x[..., 1::2]
    cos = cos[None, None, : x.shape[2], :]
    sin = sin[None, None, : x.shape[2], :]
    return torch.stack([x1 * cos - x2 * sin,
                        x1 * sin + x2 * cos], dim=-1).flatten(-2)
```

:::math Why rotation gives relative position for free
The dot product of two rotated vectors depends only on the *difference* of
their angles. Writing $R_m$ for rotation by $m\theta$:

$$(R_m q) \cdot (R_n k) = q^\top R_m^\top R_n k = q^\top R_{n-m} k$$

because rotation matrices are orthogonal and compose by adding angles. So the
attention score between positions $m$ and $n$ depends on $n - m$ alone ---
exactly the relative-position property you want --- while the implementation
only ever touches absolute positions. No extra parameters, no $T\times T$ bias
matrix, and the pattern is defined for any position.
:::

**Extending context.** Because $\theta$ is a continuous function of position,
you can rescale it. *Position interpolation* divides positions by a factor
$s$, compressing a longer sequence into the trained angular range. *NTK-aware
scaling* and *YaRN* scale the base $10000$ instead, and per frequency band,
which preserves high-frequency (local) resolution while extending the
low-frequency (global) range. This is how a 4k-context model is extended to
32k or 128k with a short fine-tune rather than retraining.

## RMSNorm

$$\text{LayerNorm}(x) = \gamma \odot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta$$
$$\text{RMSNorm}(x) = \gamma \odot \frac{x}{\sqrt{\frac{1}{d}\sum_i x_i^2 + \epsilon}}$$

RMSNorm drops the mean subtraction and the bias. Empirically the re-centring
contributes nothing --- the scaling is what stabilises training --- and
removing it saves one pass over the data and two parameter tensors.

```python title="RMSNorm, with the fp32 detail that matters"
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        dtype = x.dtype
        x = x.float()                                   # compute in fp32:
        x = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return (x.to(dtype)) * self.weight              # the sum of squares
                                                        # overflows in fp16
```

## SwiGLU

$$\text{SwiGLU}(x) = \big(\text{Swish}(xW_1) \odot xW_3\big)W_2, \qquad \text{Swish}(z) = z\,\sigma(z)$$

A *gated* activation: one branch produces a value, the other produces a
multiplicative gate. The gate lets the network suppress or pass information
per-dimension, which a pointwise activation cannot.

```python title="SwiGLU and the 2/3 adjustment"
class SwiGLU(nn.Module):
    def __init__(self, dim, mult=4, multiple_of=256):
        super().__init__()
        # Three matrices instead of two, so shrink the hidden width by 2/3
        # to keep the parameter count equal to a GELU MLP of width mult*dim.
        hidden = int(2 * mult * dim / 3)
        hidden = multiple_of * ((hidden + multiple_of - 1) // multiple_of)
        self.w1 = nn.Linear(dim, hidden, bias=False)    # gate branch
        self.w3 = nn.Linear(dim, hidden, bias=False)    # value branch
        self.w2 = nn.Linear(hidden, dim, bias=False)    # projection back

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))
```

The $2/3$ is the whole trick: a GELU MLP has $2 \cdot 4d^2 = 8d^2$ parameters;
SwiGLU has $3dh$, so setting $h = \frac{2}{3}\cdot 4d$ gives $8d^2$ again. The
comparison is therefore at equal parameters and equal FLOPs, and SwiGLU wins
by a consistent, small margin. Rounding $h$ to a multiple of 256 is for
hardware alignment.

## Grouped-query attention

@fig: gqa | 128 | MHA, GQA and MQA. Query heads are unchanged; what varies is how many distinct key/value heads they share. The KV cache --- which dominates inference memory --- shrinks by the sharing factor.

The KV cache stores $K$ and $V$ for every past token, at every layer:

$$\text{cache bytes} = 2 \times L \times T \times n_{kv} \times d_{head} \times \text{bytes}$$

```python title="What GQA saves, concretely"
# 70B-class model: L=80, d=8192, head_dim=128, T=8192, bf16, batch 1
#
#  MHA  (n_kv = 64):  2*80*8192*64*128*2 = 21.5 GB   ← per sequence
#  GQA  (n_kv =  8):  2*80*8192* 8*128*2 =  2.7 GB
#  MQA  (n_kv =  1):  2*80*8192* 1*128*2 =  0.34 GB
#
# At batch 32, MHA needs 687 GB of cache. This is why GQA exists.
```

```python title="Implementation: repeat the KV heads to match the queries"
def repeat_kv(x, n_rep):
    """(B, n_kv, T, D) -> (B, n_kv * n_rep, T, D)"""
    B, n_kv, T, D = x.shape
    if n_rep == 1:
        return x
    return (x[:, :, None]
             .expand(B, n_kv, n_rep, T, D)
             .reshape(B, n_kv * n_rep, T, D))

k = repeat_kv(k, self.n_heads // self.n_kv_heads)
v = repeat_kv(v, self.n_heads // self.n_kv_heads)
```

Quality loss from GQA at 8 KV heads is small --- typically within noise on
most benchmarks --- while the memory saving is 8×. MQA (one KV head) is
measurably worse but still used where memory is the binding constraint.

## Mixture of experts

Replace the MLP with $E$ parallel MLPs and a router that sends each *token* to
the top $k$ of them. Parameters scale with $E$; FLOPs scale with $k$.

```python title="Top-k routing, with the load-balancing loss"
class MoE(nn.Module):
    def __init__(self, dim, n_experts=8, top_k=2):
        super().__init__()
        self.router = nn.Linear(dim, n_experts, bias=False)
        self.experts = nn.ModuleList(SwiGLU(dim) for _ in range(n_experts))
        self.top_k, self.n_experts = top_k, n_experts

    def forward(self, x):                            # x: (B, T, C)
        flat = x.view(-1, x.size(-1))                # (N, C)
        logits = self.router(flat)                   # (N, E)
        probs = F.softmax(logits, dim=-1)
        w, idx = probs.topk(self.top_k, dim=-1)      # (N, k)
        w = w / w.sum(-1, keepdim=True)

        out = torch.zeros_like(flat)
        for e, expert in enumerate(self.experts):
            sel, pos = (idx == e).nonzero(as_tuple=True)
            if sel.numel():
                out[sel] += w[sel, pos, None] * expert(flat[sel])

        # Load balancing: encourage uniform expert usage, or one expert
        # takes everything and the rest never receive a gradient.
        frac = torch.zeros(self.n_experts, device=x.device)
        frac.scatter_add_(0, idx.flatten(),
                          torch.ones_like(idx.flatten(), dtype=torch.float))
        frac = frac / idx.numel()
        aux = self.n_experts * (frac * probs.mean(0)).sum()
        return out.view_as(x), aux
```

:::pitfall Three ways MoE goes wrong
**Router collapse.** Without the auxiliary loss, the router converges to one
or two experts; the rest receive no gradient and are dead parameters. The
symptom is expert-usage entropy falling towards zero --- log it.

**Capacity overflow.** Real implementations cap tokens per expert for
efficiency. Tokens beyond the cap are *dropped* (they skip the MLP entirely),
which is invisible in the loss and degrades quality. Log the drop rate.

**Memory, not FLOPs, is the constraint.** An 8×7B MoE performs the FLOPs of a
13B dense model but must hold 47B parameters in memory. It is cheap to *run*
and expensive to *host* --- exactly inverted from a dense model, and a common
source of surprise in deployment planning.
:::

:::practice The task
Start from your Chapter 25 model and replace components one at a time,
measuring loss at fixed compute after each: (a) learned positions → RoPE, and
then test extrapolation beyond the trained length, with and without position
interpolation; (b) LayerNorm → RMSNorm, and measure the step-time change;
(c) GELU MLP → SwiGLU with the 2/3 adjustment, verifying the parameter count
is unchanged; (d) MHA → GQA at 8, 4 and 1 KV heads, measuring both loss and
KV-cache size; (e) add a small MoE layer and log expert-usage entropy with and
without the auxiliary loss.

**You have this skill when** you can read a modern model's config file and
predict its KV-cache size, parameter count and FLOPs per token.
:::

:::exercise
1. Prove $(R_m q)\cdot(R_n k) = q^\top R_{n-m} k$ for 2-D rotations.
2. Implement RoPE and show attention scores depend only on relative position.
3. † Extend a RoPE model beyond its trained context with (a) nothing,
   (b) position interpolation, (c) NTK-aware base scaling. Plot perplexity
   against length for all three.
4. Show that RMSNorm's sum of squares overflows in fp16 for a realistic
   activation magnitude, and that the fp32 cast fixes it.
5. Derive the 2/3 factor and verify the parameter counts match numerically.
6. † Compute KV-cache size for a model of your choice at MHA, GQA-8 and MQA,
   at batch 1 and batch 64. State the maximum batch that fits on one 80 GB
   device in each case.
7. Train a small MoE without the auxiliary loss and plot expert-usage entropy
   over training.
:::

:::recap
- RoPE rotates Q and K by a position-dependent angle; dot products then depend
  only on relative position, with no parameters and no length limit.
- Position interpolation and NTK/YaRN scaling extend context by rescaling the
  frequencies.
- RMSNorm drops mean subtraction and biases, and must compute in fp32.
- SwiGLU uses three matrices, so its hidden width is $\frac{2}{3}$ of the
  dense one to keep parameters equal.
- GQA shares KV heads across query heads and shrinks the KV cache by the
  sharing factor --- the dominant inference-memory saving.
- MoE scales parameters without scaling FLOPs; watch router collapse, token
  dropping, and the fact that memory becomes the binding constraint.
:::
