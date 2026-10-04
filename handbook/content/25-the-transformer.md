# The Transformer, Built From Scratch
@short: The Transformer
@subtitle: Two hundred lines, and every one of them explained
@tier: core
@prereq: Chapter 24
@blurb: You do not understand the transformer until you have written one. This chapter builds a complete decoder-only model --- attention, masking, the feed-forward block, normalisation placement, the residual stream --- explains why each choice is made, and ends with the parameter and FLOP accounting that lets you size a model before training it.
@objectives:
- Implement multi-head causal self-attention correctly, including the mask
- Explain the residual stream as the model's working memory
- Justify pre-norm over post-norm and RMSNorm over LayerNorm
- Count parameters and FLOPs for any configuration
- Debug the five bugs that every from-scratch implementation has

## The architecture

@fig: transformer_block | 172 | One decoder block. The residual stream runs straight down the middle, untouched; each sublayer reads a normalised copy of it, computes something, and adds the result back. Everything else is detail.

```python title="Multi-head causal self-attention"
import math, torch, torch.nn as nn, torch.nn.functional as F

class CausalSelfAttention(nn.Module):
    def __init__(self, dim, n_heads, dropout=0.0):
        super().__init__()
        assert dim % n_heads == 0
        self.n_heads, self.head_dim = n_heads, dim // n_heads
        self.qkv  = nn.Linear(dim, 3 * dim, bias=False)   # fused projection
        self.proj = nn.Linear(dim, dim, bias=False)
        self.dropout = dropout

    def forward(self, x):                       # x: (B, T, C)
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)   # each (B, T, C)
        # (B, T, C) -> (B, n_heads, T, head_dim)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        # Fused, memory-efficient, and handles the causal mask internally.
        out = F.scaled_dot_product_attention(
            q, k, v, is_causal=True,
            dropout_p=self.dropout if self.training else 0.0)

        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(out)
```

```python title="The same thing written out, so you can see the mask"
    def _manual(self, q, k, v, T):
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)   # (B,H,T,T)
        mask = torch.ones(T, T, dtype=torch.bool, device=q.device).tril()
        att = att.masked_fill(~mask, float("-inf"))   # -inf BEFORE softmax
        att = F.softmax(att, dim=-1)
        return att @ v                                # (B,H,T,head_dim)
```

:::pitfall The mask must be applied before the softmax
Masking *after* the softmax --- zeroing the disallowed entries --- leaves the
remaining weights not summing to one, so every position is scaled by an
arbitrary factor that depends on its position. The model trains, badly, and
the bug is invisible in the loss shape.

Setting masked logits to $-\infty$ before the softmax makes their
$e^{-\infty} = 0$ contribution exact and leaves the surviving weights
correctly normalised. Use `float("-inf")`, not a large negative number: in
fp16, $-10^9$ overflows to $-\infty$ anyway, but in bf16 a large finite value
can leave a nonzero weight.
:::

```python title="The block, and the model"
class MLP(nn.Module):
    def __init__(self, dim, mult=4):
        super().__init__()
        self.fc   = nn.Linear(dim, mult * dim, bias=False)
        self.proj = nn.Linear(mult * dim, dim, bias=False)

    def forward(self, x):
        return self.proj(F.gelu(self.fc(x)))

class Block(nn.Module):
    def __init__(self, dim, n_heads):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(dim), nn.LayerNorm(dim)
        self.attn, self.mlp = CausalSelfAttention(dim, n_heads), MLP(dim)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))     # PRE-norm: normalise the input,
        x = x + self.mlp(self.ln2(x))      # not the output
        return x

class GPT(nn.Module):
    def __init__(self, vocab, dim, n_layers, n_heads, max_T):
        super().__init__()
        self.tok = nn.Embedding(vocab, dim)
        self.pos = nn.Embedding(max_T, dim)
        self.blocks = nn.ModuleList(Block(dim, n_heads) for _ in range(n_layers))
        self.ln_f = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, vocab, bias=False)
        self.head.weight = self.tok.weight          # weight tying

        self.apply(self._init)
        for n, p in self.named_parameters():        # scaled residual init
            if n.endswith("proj.weight"):
                nn.init.normal_(p, std=0.02 / math.sqrt(2 * n_layers))

    def _init(self, m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if getattr(m, "bias", None) is not None:
                nn.init.zeros_(m.bias)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        for blk in self.blocks:
            x = blk(x)
        logits = self.head(self.ln_f(x))
        if targets is None:
            return logits
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)),
                               targets.view(-1), ignore_index=-100)
        return logits, loss
```

## The residual stream

:::insight The single most useful way to think about a transformer
The residual connections form an uninterrupted path from the embedding to the
output: $x \to x + a_1 \to x + a_1 + m_1 \to \cdots$. Nothing ever overwrites
it; every sublayer only *adds*.

Read this as a **working memory** that each sublayer reads from and writes to.
Attention moves information between positions; the MLP transforms information
at a position. The stream itself is a shared bus, and the model's depth is
the number of read-modify-write cycles available.

Three practical consequences follow. Gradients flow to every layer along the
identity path (Chapter 8). Layers can be skipped or reordered with surprisingly
little damage, because each writes an increment rather than a replacement. And
interpretability work reads the stream at each layer to see what has
accumulated so far.
:::

## Pre-norm, and the initialisation that goes with it

**Post-norm** (the original): `x = LayerNorm(x + Sublayer(x))`. The
normalisation sits *on* the residual path, so the gradient is rescaled at
every layer. Deep post-norm models need careful warmup and frequently diverge.

**Pre-norm** (everything modern): `x = x + Sublayer(LayerNorm(x))`. The
residual path is clean, the gradient reaches layer 1 unmolested, and training
is dramatically more stable. The cost is that the stream's magnitude grows
with depth, which is why a final `ln_f` is needed before the output head.

The `0.02/sqrt(2 * n_layers)` initialisation on the output projections is the
matching piece: each of the $2L$ sublayers adds a contribution to the stream,
and scaling their initial magnitude by $1/\sqrt{2L}$ keeps the stream's
variance roughly constant at initialisation regardless of depth.

## Parameter and FLOP accounting

```python title="Count before you train"
def gpt_params(vocab, dim, n_layers, max_T, mult=4, tied=True):
    embed = vocab * dim + max_T * dim
    attn  = n_layers * (3 * dim * dim + dim * dim)      # qkv + out proj
    mlp   = n_layers * (2 * mult * dim * dim)
    norms = n_layers * 2 * 2 * dim + 2 * dim
    head  = 0 if tied else vocab * dim
    return embed + attn + mlp + norms + head

# GPT-2 small: vocab 50257, dim 768, layers 12, max_T 1024
print(f"{gpt_params(50257, 768, 12, 1024)/1e6:.1f}M")     # ≈ 124M ✓
```

Per layer the parameter count is $12d^2$ --- $4d^2$ for attention and $8d^2$
for the MLP --- so the MLP holds two-thirds of the model.

$$\text{FLOPs per token (forward)} \approx 2N + 2 L T d$$

where $N$ is the non-embedding parameter count; the second term is attention's
quadratic part. Backward costs about twice forward, so

$$\text{total training FLOPs} \approx 6 N D$$

for $D$ training tokens --- the standard estimate, and accurate to within
about 10% when $T \ll d \cdot 12$.

| Model | dim | layers | heads | Params |
|---|---|---|---|---|
| GPT-2 small | 768 | 12 | 12 | 124M |
| GPT-2 medium | 1024 | 24 | 16 | 355M |
| GPT-2 large | 1280 | 36 | 20 | 774M |
| 7B class | 4096 | 32 | 32 | 6.6B |
| 70B class | 8192 | 80 | 64 | 65B |

@tbl: Standard configurations, counted with the formula above (`mult=4`, tied embeddings). The GPT-2 rows match the published counts exactly. The bottom two rows are the *dense, GELU* equivalents --- production models at those sizes use SwiGLU (a 2/3 width adjustment) and grouped-query attention, which shifts the totals by a few percent. Note the pattern: `head_dim` stays at 64--128, and aspect ratios far from this train worse for the same parameter count.

## The five bugs every from-scratch transformer has

:::warning Check each of these explicitly
1. **Off-by-one in the labels.** The target for position $t$ is token $t+1$.
   Get it wrong and the model learns the identity function; the loss falls to
   near zero and generation is nonsense. Test: after overfitting one batch,
   generate and check it is not echoing the input.
2. **Mask applied after softmax.** See the pitfall above.
3. **Positional embedding added after the first block** rather than before.
   The model still trains and is much worse.
4. **`view` instead of `reshape` after `transpose`** --- or forgetting
   `.contiguous()`. Raises, or silently reinterprets the strides.
5. **Weight tying without matching initialisation scale.** Tying the embedding
   to the output head is standard and saves $Vd$ parameters, but the two want
   different initial scales; initialise once, after tying.
:::

:::practice The task
Type the model above (do not copy it). Then: (a) overfit a batch of 8
sequences to loss below 0.05; (b) introduce each of the five bugs in turn and
record the signature of each in the loss curve and in generated text;
(c) verify your parameter count against the formula and against
`sum(p.numel() for p in model.parameters())`; (d) compare
`scaled_dot_product_attention` with your manual implementation for numerical
equality and for memory use at $T = 4096$; (e) train post-norm and pre-norm
versions at 24 layers and compare stability.

**You have this skill when** you can write the whole model on a blank page and
your parameter count matches the formula exactly.
:::

:::exercise
1. Derive the $12d^2$ per-layer parameter count and state what it omits.
2. Show that attention's FLOPs are $O(T^2 d)$ and find the $T$ at which they
   equal the MLP's, for $d = 4096$.
3. † Implement attention without `F.scaled_dot_product_attention` and measure
   peak memory at $T$ = 1024, 4096, 16384. Explain the scaling and why
   FlashAttention changes it.
4. Break the label alignment by one and plot the loss. Explain the value it
   converges to.
5. Mask after the softmax instead of before, and measure the resulting
   per-position scaling factor.
6. † Train a 24-layer post-norm and pre-norm model with identical
   hyperparameters. Report how many steps of warmup each needs to be stable.
7. Verify the $6ND$ estimate against a measured FLOP count from the profiler.
:::

:::recap
- Multi-head attention is a fused QKV projection, a reshape into heads, scaled
  dot-product attention with a causal mask, and an output projection.
- The mask must set logits to $-\infty$ *before* the softmax.
- The residual stream is the model's working memory: attention moves
  information across positions, the MLP transforms it at a position, and
  nothing overwrites.
- Pre-norm keeps the residual path clean and is why deep models train;
  scale the output projections by $1/\sqrt{2L}$ to match.
- Per layer: $12d^2$ parameters, two-thirds in the MLP. Training FLOPs
  $\approx 6ND$.
- The five recurring bugs: label off-by-one, mask after softmax, misplaced
  positional embedding, stride mistakes after transpose, tied-weight
  initialisation.
:::
