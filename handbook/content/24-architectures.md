# Architectures and Why Attention Won
@short: Architectures
@subtitle: MLPs, convolutions, recurrence, attention --- and the trade each makes
@tier: core
@prereq: Chapter 23
@blurb: Four architectural families cover nearly everything, and each is a different bet about what structure the data has. Understanding those bets is what lets you choose an architecture rather than copy one, and it explains why attention displaced recurrence for sequences without displacing convolution for images.
@objectives:
- State the inductive bias of each architecture family
- Explain why RNNs lost to transformers, in terms of parallelism and gradients
- Compute the receptive field of a convolutional stack
- Choose an architecture from the structure of the data
- Recognise when a simpler family is sufficient

## The four families and their bets

| Family | Bet about the data | Parameters scale with | Parallel over sequence |
|---|---|---|---|
| MLP | nothing; any function | input size × width | n/a |
| Convolution | locality + translation invariance | kernel size only | yes |
| Recurrence | a Markov state suffices | hidden size only | **no** |
| Attention | relevance is content-addressable | model dim only | yes |

@tbl: Each family's inductive bias. The last column is what decided the outcome for sequences: it is a statement about hardware, not about modelling quality.

@fig: architecture_bets | 134 | The same sequence, seen by four architectures. The MLP sees a flat vector with no structure; the convolution sees a fixed local window; the RNN sees a compressed running state; attention sees every position, weighted by content.

## The MLP

$$h = \sigma(W_2\,\sigma(W_1 x + b_1) + b_2)$$

Universal approximation says a wide enough two-layer MLP can approximate any
continuous function on a compact set. This is true and nearly useless: it says
nothing about how many units, how much data, or whether gradient descent finds
the approximation.

What matters practically: an MLP has **no** structural prior, so it must learn
every invariance from data. For images that means learning separately that a
cat in the top-left and a cat in the bottom-right are both cats --- which is
why MLPs on images need vastly more data than convolutions.

MLPs remain essential as *components*: the feed-forward block inside every
transformer layer is an MLP, and it holds roughly two-thirds of the
parameters.

## Convolution

```python title="What a convolution actually computes"
# For each output position, a weighted sum over a local window,
# with the SAME weights at every position.
#   out[c_out, i, j] = sum over c_in, di, dj of
#                        W[c_out, c_in, di, dj] * x[c_in, i+di, j+dj]
#
# Two consequences:
#   1. Parameter count is independent of image size.
#   2. Translating the input translates the output (equivariance).
```

**Receptive field** is the crucial quantity: how much of the input influences
one output. For a stack of $L$ layers with kernel size $k$, stride 1 and
dilation 1:

$$R = 1 + L(k-1)$$

Ten layers of $3\times3$ gives $R = 21$ pixels. To see an entire
$224\times224$ image you need pooling (which multiplies the effective stride),
dilation (which multiplies the spacing), or a great many layers. This is
exactly the limitation attention removes: attention's receptive field is the
whole sequence in one layer.

| Variant | Purpose |
|---|---|
| Stride > 1 | downsample; grows receptive field geometrically |
| Dilation | grow receptive field without parameters or downsampling |
| Depthwise separable | $k^2 C + C^2$ instead of $k^2C^2$ parameters |
| 1×1 convolution | a per-position linear layer; channel mixing |
| Residual block | the identity path of Chapter 8 |

@tbl: Convolution variants. Depthwise separable convolutions are why efficient vision models are small: for $C = 256$, $k = 3$, they use about 9× fewer parameters per layer.

## Recurrence, and why it lost

$$h_t = \tanh(W_h h_{t-1} + W_x x_t + b)$$

Two fatal problems, and the second is the one that decided it.

**Vanishing gradients.** The gradient from step $T$ back to step $t$ passes
through $T-t$ Jacobian products (Chapter 8), so it vanishes or explodes
exponentially. LSTMs and GRUs mitigate this with gating --- an additive cell
state that is the same identity-path trick as a residual connection --- and
stretch the usable range to hundreds of steps rather than tens. It was never
enough for thousands.

**Sequential computation.** $h_t$ requires $h_{t-1}$. A sequence of length
1024 needs 1024 dependent steps, and there is nothing a GPU can do about it:
the hardware has tens of thousands of cores and the algorithm uses a handful
at a time.

:::insight The decisive argument was hardware utilisation
A transformer processes all positions of a training sequence **simultaneously**
--- one big matmul per layer, arithmetic intensity in the compute-bound regime
(Chapter 7). An RNN processes them one at a time, each step a small
matrix--vector product in the memory-bound regime.

On the same hardware and the same wall-clock budget, the transformer sees
one or two orders of magnitude more data. The architecture that trains on more
data wins, and it wins by enough that modelling niceties do not matter.

This also explains the modern revival of recurrence: state-space models
(Mamba, S4) reformulate the recurrence as a **parallel scan** --- associative,
therefore computable in $O(\log T)$ depth rather than $O(T)$ --- which
restores the training parallelism while keeping $O(1)$ memory per step at
inference. The trade is back on the table precisely because the parallelism
objection was answered.
:::

## Attention

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

Every position computes a *query*; every position exposes a *key* and a
*value*; the output at each position is a weighted average of all values,
weighted by query--key similarity.

Three properties follow:

**Constant path length.** Any position can influence any other in one layer.
No vanishing over distance.

**Full parallelism.** The whole thing is two matmuls and a softmax.

**Quadratic cost.** $QK^\top$ is $T \times T$: $O(T^2 d)$ FLOPs and, naively,
$O(T^2)$ memory. This is the price, and Chapters 25 and 40 cover what is done
about it.

:::math Why divide by $\sqrt{d_k}$
If $q$ and $k$ have independent components with mean 0 and variance 1, then

$$\text{Var}(q \cdot k) = \sum_{i=1}^{d_k} \text{Var}(q_i k_i) = d_k$$

so the dot product has standard deviation $\sqrt{d_k}$. For $d_k = 128$ that
is about 11, and a softmax over values with that spread is nearly one-hot: the
largest logit dominates, the gradient through the softmax is almost zero
everywhere, and learning stalls.

Dividing by $\sqrt{d_k}$ restores unit variance and keeps the softmax in its
responsive range. This is the whole derivation, and it is why the constant is
$\sqrt{d_k}$ and not something tuned.
:::

## Choosing

:::checklist Match the family to the structure
- **Fixed-size, unstructured feature vector** → MLP, or a GBDT (Chapter 19),
  which usually wins on tabular data.
- **Grid with local structure and translation invariance** → convolution.
  Still the efficient choice for images at small and medium scale; vision
  transformers overtake it given enough data.
- **Sequence where long-range content-based dependencies matter** →
  attention.
- **Very long sequences (100k+) where linear cost is required** →
  state-space or hybrid models.
- **Graph with explicit edges** → message passing (a convolution
  generalised to arbitrary neighbourhoods).
- **Streaming with strict $O(1)$ memory per step** → recurrence, or an SSM.
:::

:::warning Start smaller than you think
The default move --- a transformer --- is frequently wrong for small data. On
10,000 examples, a small convolutional model or a GBDT will typically beat a
transformer trained from scratch, because the transformer's weak inductive
bias must be paid for with data.

The reason transformers dominate is that they scale better *given enough
data*, not that they are better at every size. Fine-tuning a pretrained
transformer is a different proposition --- there the data was paid for by
somebody else.
:::

:::practice The task
On a sequence task: (a) implement a vanilla RNN, an LSTM and a single-layer
attention block; train all three and compare wall-clock time to a fixed loss;
(b) measure the gradient norm at step 1 with respect to input position 1 as
sequence length grows, for the RNN and for attention; (c) compute the
receptive field of a convolutional stack analytically and verify it
empirically by perturbing single input positions; (d) remove the
$\sqrt{d_k}$ scaling and plot the softmax entropy and the gradient magnitude.

**You have this skill when** you can state, for a new problem, which family
you would try and what its inductive bias assumes about the data.
:::

:::exercise
1. Count the parameters of a convolutional layer and an equivalent fully
   connected layer for a 224×224×3 input. Report the ratio.
2. Derive the receptive field formula for a stack with strides and dilations.
3. † Measure the gradient magnitude from step $T$ back to step 1 in an RNN and
   an LSTM, for $T$ from 10 to 1000. Plot both.
4. Show empirically that removing $\sqrt{d_k}$ collapses attention to
   near-one-hot as $d_k$ grows.
5. Implement depthwise separable convolution and verify the parameter
   reduction.
6. † Implement a parallel scan for a linear recurrence and show it gives the
   same result as the sequential version in $O(\log T)$ depth.
7. On a dataset of 10,000 examples, compare a small CNN, a from-scratch
   transformer and a fine-tuned pretrained transformer. Explain the ordering.
:::

:::recap
- Four families, four bets: MLP (none), convolution (locality and translation
  invariance), recurrence (a Markov state suffices), attention (relevance is
  content-addressable).
- Recurrence lost on hardware utilisation, not on modelling: sequential steps
  cannot fill a GPU.
- State-space models revive recurrence by making it a parallel scan.
- Attention gives constant path length and full parallelism at quadratic cost.
- The $\sqrt{d_k}$ divisor keeps the dot product at unit variance so the
  softmax stays responsive.
- Weak inductive bias must be paid for with data; at small scale, stronger
  priors win.
:::
