# Arrays, Strides and the NumPy Memory Model
@short: Arrays and Strides
@subtitle: The one data structure you already use for everything
@tier: foundation
@prereq: Chapters 2--3
@blurb: The array is the simplest data structure and by far the most important one in machine learning: every tensor, every embedding table, every batch is an array. This chapter takes it seriously --- the dynamic array's growth policy, the stride arithmetic that makes views free, when an operation copies, and the handful of NumPy idioms that replace loops you should never write.
@objectives:
- Explain how an ndarray's shape, strides and dtype turn indexing into arithmetic
- Predict whether a NumPy operation returns a view or a copy, and why it matters
- Use fancy indexing, boolean masks and `argsort` / `argpartition` fluently
- Understand broadcasting as a stride-0 trick rather than as magic
- Implement a dynamic array and reason about its growth factor
- Recognise the array patterns that appear in every dataloader and inference path

## The array, precisely

An array is a contiguous block of memory holding $n$ equal-sized elements.
That definition buys you exactly one superpower: the address of element $i$
is $\text{base} + i \times \text{itemsize}$, computable in one multiply and
one add. No search, no indirection, no branch.

| Operation | Cost | Why |
|---|---|---|
| `a[i]` read or write | $\Theta(1)$ | address arithmetic |
| scan all elements | $\Theta(n)$, cache-friendly | one miss per 64 bytes |
| append (amortised) | $\Theta(1)$ | doubling, Chapter 2 |
| insert or delete at $i$ | $\Theta(n - i)$ | `memmove` of the tail |
| search unsorted | $\Theta(n)$ | no structure to exploit |
| search sorted | $\Theta(\log n)$ | binary search, Chapter 10 |

@tbl: The array's cost profile. Everything good follows from contiguity; everything bad follows from the fact that inserting in the middle must move the tail.

The `memmove` in row four is worth a note: it is not a Python loop, it is a
single vectorised instruction sequence running at tens of gigabytes per
second. Shifting ten thousand elements costs a few microseconds. This is why
"arrays are bad at insertion" is much weaker advice than it sounds.

## The dynamic array from scratch

Python's `list` is a dynamic array, and writing one makes its behaviour
concrete.

```python title="A dynamic array with an explicit growth policy"
class DynArray:
    def __init__(self, growth=2.0):
        self._buf = [None] * 1
        self._n = 0
        self._growth = growth
        self.copies = 0                  # instrumentation

    def __len__(self):
        return self._n

    def __getitem__(self, i):
        if not 0 <= i < self._n:
            raise IndexError(i)
        return self._buf[i]              # theta(1)

    def append(self, x):
        if self._n == len(self._buf):
            self._resize(max(1, int(len(self._buf) * self._growth)))
        self._buf[self._n] = x
        self._n += 1                     # theta(1) amortised

    def insert(self, i, x):
        self.append(None)                # make room
        for j in range(self._n - 1, i, -1):
            self._buf[j] = self._buf[j - 1]
        self._buf[i] = x                 # theta(n - i)

    def _resize(self, cap):
        new = [None] * cap
        for j in range(self._n):         # the expensive part
            new[j] = self._buf[j]
        self.copies += self._n
        self._buf = new
```

Run it with different growth factors and count `copies` after a million
appends. You will find roughly $2n$ copies at factor 2, $5n$ at factor 1.25,
and $n^2/2000$ at a fixed increment of 1000 --- the difference between linear
and quadratic, decided by one parameter.

:::perf What real implementations choose
CPython grows by roughly `n >> 3` extra slots (about 1.125x) for large lists,
prioritising memory over copy count. Go doubles up to 1024 elements then
uses 1.25x. C++ `std::vector` typically doubles; MSVC uses 1.5x so that
freed blocks can be coalesced and reused. Every one of these is a point on
the same memory--time curve, and all preserve $\Theta(1)$ amortised append.
:::

## Two dimensions: shape, strides, dtype

A NumPy array is not a nested list. It is a flat buffer plus a small header
that says how to interpret it.

@fig: ndarray_layout | 145 | An `ndarray` is a pointer to a flat buffer plus a shape and a stride vector. Indexing is a dot product between the index tuple and the strides, then a single memory read.

The rule is one line:

$$\text{address}(i_0, i_1, \ldots) = \text{base} + \sum_k i_k \cdot \text{strides}[k]$$

For a C-contiguous (row-major) $m \times n$ float32 array, `strides = (4n, 4)`:
moving one step along the last axis moves 4 bytes; moving one step along the
first axis skips a whole row. Fortran-contiguous (column-major, as in MATLAB
and R) is the transpose of that convention.

This is the whole secret behind NumPy's speed *and* behind the surprising
performance cliffs in Chapter 3. `A[i, :]` is a contiguous run; `A[:, j]` is
$m$ reads separated by $4n$ bytes. Same element count, different worlds.

## Views versus copies

Because indexing is stride arithmetic, an enormous number of operations can
be implemented by *changing the header and reusing the buffer*. Those are
views: $\Theta(1)$ time, zero memory. Everything else must copy: $\Theta(n)$
time and memory.

@fig: strides_views | 140 | Which array expressions are free and which are not. Anything expressible as "same buffer, different shape and strides" costs nothing; anything else allocates.

:::insight The one question to ask
"Can the result be described by a new (offset, shape, strides) triple over
the same buffer?" If yes, it is a view and it is free. Basic slicing,
transpose, `reshape` on contiguous data, and broadcasting all pass this test.
Fancy indexing, boolean masking, and `reshape` across a transpose do not.
:::

```python title="Views bite, and views save"
import numpy as np
a = np.arange(12).reshape(3, 4)

b = a[1:, :2]          # VIEW  -> writing to b writes to a
b[0, 0] = 999
assert a[1, 0] == 999

c = a[[0, 2]]          # COPY  (fancy indexing)
c[0, 0] = -1
assert a[0, 0] == 0

print(a.T.flags["C_CONTIGUOUS"])       # False: a view with swapped strides
print(a[::2].base is a)                # True: slicing keeps the parent alive
```

:::pitfall Two production bugs that come from views
**Silent aliasing.** A dataloader does `batch = buffer[i:i+B]` and hands the
view to a worker that normalises it in place. The next batch overlaps and
sees pre-normalised data. Symptoms: loss that depends on `num_workers`.
Use `.copy()` at the boundary.

**Accidental memory retention.** `small = big_array[:10]` keeps the *entire*
`big_array` buffer alive, because the view holds a reference to the base. If
`big_array` was 8 GB, you still have 8 GB. `small = big_array[:10].copy()`
releases it.
:::

## Fancy indexing, masks, and the argsort family

These four idioms replace almost every explicit loop you would otherwise
write over a batch.

```python title="The idioms worth memorising"
import numpy as np
scores = np.random.rand(1_000_000).astype(np.float32)

# 1. boolean mask: select by predicate.  theta(n), allocates.
keep = scores[scores > 0.9]

# 2. fancy index: gather by position.  theta(len(idx)).
idx = np.array([7, 3, 99, 3])
picked = scores[idx]                       # duplicates allowed

# 3. full ordering when you need ranks
order = np.argsort(-scores)[:10]           # theta(n log n)

# 4. partial ordering when you only need the top k  <- almost always this
top = np.argpartition(-scores, 10)[:10]    # theta(n), 10-40x faster
top = top[np.argsort(-scores[top])]        # then sort just those 10

# 5. scatter-add: the primitive behind embedding-gradient accumulation
grads = np.zeros(1000, dtype=np.float32)
np.add.at(grads, idx, 1.0)                 # note: slow; see bincount below
counts = np.bincount(idx, minlength=1000)  # the fast path for this case
```

:::ml Gather and scatter are the two primitives of deep learning
An embedding lookup is a gather: `table[token_ids]`, a fancy index producing
a `(B, L, d)` tensor from a `(V, d)` table. Its backward pass is a scatter-add
into the same table, which is why sparse gradients and `EmbeddingBag` exist.
Attention's KV cache read is a gather. A `Dataset`'s `__getitem__` over
shuffled indices is a gather. Recognising an operation as gather or scatter
tells you immediately whether it is random-access (slow, bandwidth-bound) or
sequential.
:::

## Broadcasting is a stride trick

Broadcasting looks like magic and is not. When NumPy needs an axis of length
1 to act as length $n$, it sets that axis's stride to **zero**. Every index
along it maps to the same memory. No data is copied and no memory is
allocated.

```python title="Broadcasting, demystified"
import numpy as np
a = np.arange(3).reshape(3, 1)     # shape (3,1) strides (8,8)
b = np.arange(4).reshape(1, 4)     # shape (1,4) strides (32,8)
print(a + b)                       # shape (3,4): a's axis1 stride -> 0

v = np.broadcast_to(a, (3, 4))
print(v.strides)                   # (8, 0)  <- the zero is the whole trick
print(v.base is a)                 # True: no allocation
```

The rules follow directly: align shapes from the right; an axis matches if
the lengths are equal or one of them is 1; a length-1 axis is stretched by
giving it stride 0.

:::pitfall The broadcast that eats your memory
Broadcasting is free only while it stays virtual. The moment you materialise
the result it is fully allocated. `(x[:, None] - y[None, :]) ** 2` on two
vectors of length 50,000 creates a $50{,}000^2$ float32 array: 10 GB. The
identity $\|x - y\|^2 = \|x\|^2 - 2x^\top y + \|y\|^2$ computes the same
pairwise distances with one matrix multiply and two $\Theta(n)$ vectors. This
is the single most common out-of-memory bug in retrieval code.
:::

## Contiguity, and when to pay for it

```python title="When to force a copy"
import numpy as np
A = np.random.rand(4096, 4096).astype(np.float32)

s1 = A.T.sum(axis=0)                       # strided reads, slow
B  = np.ascontiguousarray(A.T)             # one big memmove
s2 = B.sum(axis=0)                         # sequential reads, fast
```

The copy costs one full pass over the data. If you will touch the
transposed array more than about twice, the copy pays for itself. This is
exactly the reasoning behind `contiguous()` calls in PyTorch code and behind
layout conversions (`NCHW` to `NHWC`) in inference engines: a one-off
$\Theta(n)$ cost to make every subsequent kernel run at full bandwidth.

:::perf The dtype is a bandwidth decision
Changing `float64` to `float32` halves every byte moved, and for a
memory-bound kernel that is a 2x speedup for free. `float16` or `bfloat16`
halves it again. `int8` again. This is why quantisation is such a large win
in serving even though it does not reduce the operation count at all
(Chapter 3), and it is why you should never let a pipeline silently promote
to `float64` --- which `np.mean` on an integer array will happily do.
:::

## The patterns that show up everywhere

| Pattern | Array expression | Where you meet it |
|---|---|---|
| Prefix sums | `np.cumsum(x)` | sampling by cumulative weight, IoU, ragged offsets |
| Run-length / grouping | `np.diff`, `np.searchsorted` | variable-length sequence batching |
| Ragged batch | values + offsets arrays | nested tensors, `EmbeddingBag`, CSR graphs |
| One-hot | `np.eye(V)[ids]` (never do this) | use a gather instead; $V$ is 50,000 |
| Sliding window | `stride_tricks.sliding_window_view` | n-gram features, conv without a copy |
| Top-k | `argpartition` then `argsort` | reranking, beam search, nucleus sampling |
| Masking | boolean mask or `np.where` | padding, attention masks, filtering |

@tbl: Seven array patterns that cover most of the non-model code in an ML system.

The *ragged* row deserves emphasis because it is the representation behind
a surprising number of systems. When sequences have different lengths, the
efficient layout is not a padded matrix but a flat `values` array plus an
`offsets` array where sequence $i$ occupies `values[offsets[i]:offsets[i+1]]`.
This is the CSR format for sparse matrices (Chapter 22), the layout of
PyTorch nested tensors, the layout of Arrow list columns, and the layout of
variable-length KV caches (Chapter 36). Padding to the maximum length wastes
memory in proportion to the length variance, which for real text is often
60--70%.

```python title="A ragged batch without padding"
import numpy as np
seqs = [[1, 2, 3], [4], [5, 6, 7, 8, 9]]

lengths = np.array([len(s) for s in seqs])
offsets = np.concatenate([[0], np.cumsum(lengths)])   # [0, 3, 4, 9]
values  = np.concatenate([np.asarray(s) for s in seqs])

# Mean of each sequence, no loop, no padding:
sums = np.add.reduceat(values, offsets[:-1])
means = sums / lengths
```

:::exercise
1. Instrument `DynArray` and plot total copies against $n$ for growth factors
   1.1, 1.5, 2.0 and for a fixed increment of 512. Fit the curves.
2. For a C-contiguous array of shape $(B, L, d)$ with float32 elements, give
   the strides. Which of `x[:, 0]`, `x[0]`, `x[..., 0]` is contiguous?
3. Write a function that decides, for a given NumPy expression, whether the
   result shares memory with its input. Verify with `np.shares_memory`.
4. Compute pairwise squared distances between two sets of 20,000
   128-dimensional vectors, first with broadcasting and then with the
   $\|x\|^2 - 2x^\top y + \|y\|^2$ identity. Compare peak memory and time.
5. Using only `sliding_window_view`, compute a 5-token moving average over a
   one-million-token array without allocating a copy. Verify the strides.
6. Given a ragged batch as `values` and `offsets`, write a vectorised
   function returning the maximum of each sequence. (Hint: `np.maximum.reduceat`.)
7. A colleague's dataloader returns `torch.from_numpy(buf[i:i+B])` where `buf`
   is a ring buffer that is overwritten by a background thread. Describe the
   failure mode precisely and give two fixes with different cost profiles.
:::

:::recap
- An array's power is that addressing is arithmetic: $\Theta(1)$ access,
  perfect spatial locality, vectorisable scans.
- Dynamic arrays give amortised $\Theta(1)$ append by growing geometrically;
  the growth factor trades memory against copy count.
- An ndarray is a buffer plus (shape, strides, dtype). Indexing is a dot
  product with the strides.
- An operation is a free view exactly when its result can be described by a
  new (offset, shape, strides) triple; otherwise it copies. Views cause
  aliasing bugs and retain their parent's memory.
- Broadcasting is implemented by setting a stride to zero, which is why it is
  free until you materialise the result --- and why materialising it is the
  most common OOM in retrieval code.
- Gather and scatter are the two access primitives of deep learning;
  recognising which one you are doing predicts its cost.
- Ragged (values + offsets) layouts beat padding whenever lengths vary, and
  are the basis of CSR, nested tensors and paged KV caches.
:::
