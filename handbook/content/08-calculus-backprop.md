# Calculus and Backpropagation, Derived
@short: Backpropagation
@subtitle: Deriving the algorithm, then implementing it in eighty lines
@tier: foundation
@prereq: Chapter 7
@blurb: Backpropagation is the chain rule applied to a computational graph in a particular order. Once you have derived it once and written it once, a whole class of training bugs becomes diagnosable by inspection. This chapter derives the vector-Jacobian product, builds a working autograd engine, and connects every piece to what PyTorch is doing.
@objectives:
- Derive the chain rule in vector form and know why reverse mode is chosen
- Implement a working reverse-mode autograd engine from scratch
- Compute gradients of the layers you use: linear, softmax, cross-entropy, layer norm
- Explain gradient vanishing and explosion in terms of Jacobian products
- Trade memory for compute with gradient checkpointing

## Derivatives, restated for many variables

For $f: \mathbb{R}^n \to \mathbb{R}$, the **gradient** $\nabla f$ collects the
partial derivatives and points in the direction of steepest increase. For
$f: \mathbb{R}^n \to \mathbb{R}^m$, the **Jacobian** $J$ is the $m \times n$
matrix $J_{ij} = \partial f_i / \partial x_j$.

The chain rule for composition $y = g(f(x))$ is a matrix product:

$$J_{y/x} = J_{g} \, J_{f}$$

For a network this is a long chain,
$J = J_L J_{L-1} \cdots J_1$, and the only question is what order to multiply
it in. Matrix multiplication is associative, so both ends are available.

:::insight Why reverse mode, in one line of arithmetic
A network with layer widths all equal to $d$ and $L$ layers has Jacobians of
size $d \times d$, except the last, which is $1 \times d$ because the loss is
a scalar.

**Forward mode** multiplies left to right: $(J_L (J_{L-1} (\cdots J_1)))$ ---
every product is $d \times d$ by $d \times d$, costing $O(Ld^3)$.

**Reverse mode** multiplies right to left starting from the scalar:
$((( J_L) J_{L-1}) \cdots J_1)$ --- every product is $1 \times d$ by
$d \times d$, costing $O(Ld^2)$.

A factor of $d$, which for $d = 4096$ is four thousand. This is the entire
reason backpropagation exists, and the reason it needs one backward pass per
*output* (cheap: one scalar loss) rather than one per *input* (expensive:
billions of parameters).
:::

@fig: backprop_flow | 118 | Forward pass stores activations; backward pass consumes them in reverse. Each node receives the gradient of the loss with respect to its output and produces the gradient with respect to its inputs --- a vector-Jacobian product, never a materialised Jacobian.

## The VJP: what every backward function actually computes

No framework ever builds a Jacobian. It computes $v^\top J$ for the incoming
gradient $v$ --- the **vector--Jacobian product** --- because that is all the
chain rule needs and it is far cheaper.

```python title="Three layers, derived"
# Linear: y = x W + b,   x:(B,n)  W:(n,m)  b:(m,)  y:(B,m)
#   dL/dx = dL/dy @ W.T          (B,m)(m,n) -> (B,n)
#   dL/dW = x.T @ dL/dy          (n,B)(B,m) -> (n,m)
#   dL/db = dL/dy.sum(axis=0)    sum over the batch, because b broadcast

# ReLU: y = max(x, 0)
#   dL/dx = dL/dy * (x > 0)      the gradient is gated, not scaled

# Softmax + cross-entropy, fused:  L = -log p_target
#   dL/dz = p - onehot(target)   ← the whole derivation collapses to this
```

That last line is worth dwelling on. Derived separately, softmax's Jacobian is
$\text{diag}(p) - pp^\top$, a dense $V \times V$ matrix for a vocabulary of
size $V$ --- which for $V = 128{,}000$ is 16 billion entries. Composed with
cross-entropy it collapses to $p - y$, a single vector subtraction. This is
why every framework fuses them, and why you should never apply softmax
yourself before `cross_entropy`.

:::pitfall Double softmax
```python
logits = model(x)
loss = F.cross_entropy(F.softmax(logits, dim=-1), y)   # WRONG
loss = F.cross_entropy(logits, y)                      # right
```
`cross_entropy` expects *logits* and applies log-softmax internally. Passing
probabilities applies softmax twice: gradients shrink by roughly an order of
magnitude, the model trains but plateaus early, and nothing errors. This is
one of the most common bugs in student code and it is invisible in the loss
curve's shape.
:::

## An autograd engine in eighty lines

```python title="Reverse-mode autograd, complete"
import numpy as np

class Tensor:
    def __init__(self, data, parents=(), op=""):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._backward = lambda: None       # local VJP, set by each op
        self._parents = set(parents)
        self._op = op

    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, (self, other), "+")
        def _backward():
            self.grad  += _unbroadcast(out.grad, self.data.shape)
            other.grad += _unbroadcast(out.grad, other.data.shape)
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, (self, other), "*")
        def _backward():
            self.grad  += _unbroadcast(other.data * out.grad, self.data.shape)
            other.grad += _unbroadcast(self.data * out.grad, other.data.shape)
        out._backward = _backward
        return out

    def __matmul__(self, other):
        out = Tensor(self.data @ other.data, (self, other), "@")
        def _backward():
            self.grad  += out.grad @ other.data.T
            other.grad += self.data.T @ out.grad
        out._backward = _backward
        return out

    def relu(self):
        out = Tensor(np.maximum(self.data, 0), (self,), "relu")
        def _backward():
            self.grad += (self.data > 0) * out.grad
        out._backward = _backward
        return out

    def sum(self):
        out = Tensor(self.data.sum(), (self,), "sum")
        def _backward():
            self.grad += np.ones_like(self.data) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        order, seen = [], set()
        def build(v):                      # topological sort of the DAG
            if v not in seen:
                seen.add(v)
                for parent in v._parents:
                    build(parent)
                order.append(v)
        build(self)
        self.grad = np.ones_like(self.data)     # dL/dL = 1
        for v in reversed(order):
            v._backward()

def _unbroadcast(grad, shape):
    """Sum a gradient back down to `shape`, undoing broadcasting."""
    while grad.ndim > len(shape):
        grad = grad.sum(axis=0)
    for i, s in enumerate(shape):
        if s == 1:
            grad = grad.sum(axis=i, keepdims=True)
    return grad
```

Four things in that listing are the whole of autograd, and they are the same
four in PyTorch:

1. Every operation records its **parents**, building a DAG as a side effect of
   the forward pass.
2. Every operation stores a **closure** that applies its local VJP.
3. `backward()` **topologically sorts** the DAG so a node is processed only
   after everything that consumes it.
4. Gradients **accumulate** (`+=`), because a tensor used twice receives two
   contributions. This is also why you must call `zero_grad()`.

```python title="Verify it against a numerical gradient"
def loss_of(W_data):
    return float(np.maximum(x.data @ W_data, 0).sum())

x = Tensor([[1.0, 2.0], [3.0, 4.0]])
W = Tensor([[0.5], [0.5]])
(x @ W).relu().sum().backward()

eps, numerical = 1e-6, np.zeros_like(W.data)
for i in range(W.data.size):
    up, dn = W.data.copy(), W.data.copy()
    up.flat[i] += eps
    dn.flat[i] -= eps
    numerical.flat[i] = (loss_of(up) - loss_of(dn)) / (2 * eps)

assert np.allclose(W.grad, numerical, atol=1e-5), (W.grad, numerical)
```

:::practice Do this before reading on
Type the engine above, run it, and check every gradient against central
differences. Then add `tanh`, `exp` and a `softmax_cross_entropy`. You will
never again be confused about what `.backward()` does, what `retain_graph`
means, or why `.detach()` stops gradients.
:::

## Vanishing and exploding gradients

The gradient reaching layer $k$ is a product of Jacobians:

$$\frac{\partial L}{\partial h_k} = \frac{\partial L}{\partial h_L} \prod_{i=k+1}^{L} J_i$$

A product of $L - k$ matrices. If their typical singular value is $\sigma$,
the magnitude scales like $\sigma^{L-k}$ --- exponential in depth. For
$\sigma = 0.9$ and 50 layers, $0.9^{50} \approx 0.005$; for $\sigma = 1.1$,
$1.1^{50} \approx 117$.

| Symptom | Cause | Fix |
|---|---|---|
| Early layers' gradients $\sim 10^{-8}$ | $\sigma < 1$ compounding | residual connections, normalisation |
| Loss becomes `nan` after a spike | $\sigma > 1$ compounding | gradient clipping, lower LR, warmup |
| Loss flat from step 0 | dead ReLUs, or double softmax | check activation statistics |
| Loss decreases then diverges | LR too high for the curvature | warmup + cosine schedule |

@tbl: Gradient pathologies by signature. Chapter 27 develops the full diagnostic procedure.

:::intuition Why residual connections fix this
A residual block computes $h_{k+1} = h_k + F(h_k)$, so its Jacobian is
$I + J_F$. The identity term means the gradient has a path that is multiplied
by exactly 1 at every layer:

$$\frac{\partial h_{k+1}}{\partial h_k} = I + \frac{\partial F}{\partial h_k}$$

Expanding the product over layers gives a sum of paths, one of which is the
pure identity. The gradient can no longer vanish exponentially, because at
least one route through the network is a straight line. This is the whole
reason networks got deeper than about twenty layers.
:::

## Gradient checkpointing

The backward pass needs the forward activations. For a transformer, storing
them is often the largest memory cost --- larger than the parameters.

Checkpointing stores only every $\sqrt{L}$-th activation and *recomputes* the
rest during the backward pass. Memory drops from $O(L)$ to $O(\sqrt{L})$ at a
cost of roughly 30% more compute.

```python
from torch.utils.checkpoint import checkpoint

def forward(self, x):
    for block in self.blocks:
        x = checkpoint(block, x, use_reentrant=False)   # recompute in backward
    return x
```

:::perf When checkpointing is the right trade
Use it when memory is the binding constraint on batch size, which it usually
is for large models. A 30% compute increase that lets you double the batch
size is often a net *speedup*, because the larger batch has higher arithmetic
intensity (Chapter 7) and better GPU utilisation. Measure tokens per second,
not step time.
:::

:::exercise
1. Derive $\partial L / \partial W$ for $y = xW + b$ from the definition and
   confirm the shapes.
2. Derive the softmax Jacobian $\text{diag}(p) - pp^\top$, then show it
   composes with cross-entropy to give $p - y$.
3. † Add `tanh`, `exp`, `log` and a fused softmax-cross-entropy to the
   engine, and gradient-check all four.
4. Implement the double-softmax bug in a small classifier and plot the
   gradient norms with and without it.
5. Show empirically that gradients accumulate: call `backward()` twice
   without zeroing and confirm the gradient doubles.
6. † Derive layer norm's backward pass. Explain why it contains two
   correction terms and what they do.
7. Measure memory and step time with and without checkpointing on a model of
   yours, and find the batch size where checkpointing becomes a net win.
:::

:::recap
- The chain rule for vectors is a product of Jacobians; reverse mode evaluates
  it right to left, costing $O(Ld^2)$ rather than $O(Ld^3)$.
- Frameworks compute vector--Jacobian products, never Jacobians.
- Softmax composed with cross-entropy collapses to $p - y$; never apply
  softmax before `cross_entropy`.
- Autograd is four ideas: record parents, store a local VJP closure,
  topologically sort, accumulate gradients.
- Vanishing and exploding gradients are a product of Jacobians behaving
  exponentially in depth; residual connections add an identity path that
  cannot vanish.
- Gradient checkpointing trades ~30% compute for $O(\sqrt{L})$ activation
  memory, and often pays for itself through a larger batch.
:::
