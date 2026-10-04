# Tensors, Devices and Autograd
@short: Tensors
@subtitle: What PyTorch is actually doing with your data
@tier: core
@prereq: Chapter 8
@blurb: A tensor is a pointer, a shape and a stride, and almost every PyTorch performance surprise and shape bug follows from that fact. This chapter builds the mental model --- storage, views, devices, dtypes, the autograd graph --- so that memory usage, silent copies and gradient behaviour stop being mysterious.
@objectives:
- Explain storage, stride and view, and predict when an operation copies
- Move data between devices without stalling the GPU
- Choose dtypes deliberately, including bf16 versus fp16
- Read and control the autograd graph: detach, no_grad, retain_graph
- Diagnose the four most common memory problems

## A tensor is a view over storage

```python title="Shape is metadata; storage is the bytes"
import torch
x = torch.arange(12).reshape(3, 4)

x.storage().data_ptr()   # the actual buffer
x.shape                  # (3, 4)
x.stride()               # (4, 1): step 4 elements for a row, 1 for a column
x.is_contiguous()        # True

y = x.T                  # a VIEW: same storage, stride (1, 4)
y.stride()               # (1, 4)
y.is_contiguous()        # False — reading a row of y walks the buffer in steps of 4
y.data_ptr() == x.data_ptr()   # True: nothing was copied

z = y.contiguous()       # NOW it copies, into a fresh buffer with stride (4, 1)
```

| Operation | Copies? | Notes |
|---|---|---|
| `reshape` | only if needed | `view` if contiguous, else a copy |
| `view` | never | raises if the stride does not permit it |
| `transpose`, `permute` | never | changes strides only |
| `squeeze`, `unsqueeze` | never | adds or removes a size-1 dimension |
| basic slicing `x[1:3]` | never | offset plus stride |
| fancy indexing `x[[0,2]]` | **always** | arbitrary gather |
| boolean mask `x[m]` | **always** | output size unknown until run |
| `.contiguous()`, `.clone()` | always | explicit |
| `.to("cuda")` | always | across devices |

@tbl: What copies. The important line is the boolean mask: its output shape is data-dependent, so it forces a synchronisation on GPU and breaks `torch.compile` graphs.

:::insight Why non-contiguous tensors matter
A matmul on a non-contiguous tensor works, but the kernel either does a
strided read (slow, poor cache behaviour) or copies first. When you see
`.contiguous()` scattered through a codebase, it is usually someone having
found this the hard way.

The practical rule: after a `permute` or `transpose` that feeds a matmul or a
`view`, an explicit `.contiguous()` is cheap insurance, and profiling will
tell you if it was needed.
:::

## Devices, and the synchronisation trap

```python title="The single most common training-loop slowdown"
for batch in loader:
    x = batch["x"].to("cuda", non_blocking=True)     # async, needs pinned memory
    loss = model(x)
    loss.backward(); opt.step(); opt.zero_grad()

    # THIS forces the CPU to wait for every queued kernel:
    running += loss.item()                            # .item() synchronises

    # Instead, accumulate on device and sync once per N steps:
    running += loss.detach()                          # stays on GPU
    if step % 50 == 0:
        print(running.item() / 50); running.zero_()
```

CUDA operations are queued asynchronously: the Python loop races ahead while
the GPU works. Anything that needs a *value* --- `.item()`, `.cpu()`,
`print(tensor)`, `float(t)`, a Python `if` on a tensor --- blocks until the
queue drains. One such call inside the inner loop can cost 20--40% of
throughput.

```python title="Pinned memory makes the transfer overlap"
loader = DataLoader(ds, batch_size=64, num_workers=8,
                    pin_memory=True,          # required for non_blocking=True
                    persistent_workers=True,  # do not respawn every epoch
                    prefetch_factor=4)
```

## Dtypes

| dtype | Bits | Range | Precision | Use |
|---|---|---|---|---|
| fp32 | 32 | ±3.4e38 | ~7 digits | master weights, reductions |
| **bf16** | 16 | ±3.4e38 | ~3 digits | **the default for training** |
| fp16 | 16 | ±65504 | ~3 digits | older hardware; needs loss scaling |
| fp8 (e4m3) | 8 | ±448 | ~2 digits | inference, some training |
| int8 | 8 | −128..127 | exact | quantised inference |

@tbl: bf16 has fp32's exponent range with fewer mantissa bits; fp16 has more precision but a range that gradients routinely underflow. That single difference is why bf16 won.

:::pitfall Why fp16 needs loss scaling and bf16 does not
fp16's smallest normal positive number is about $6\times10^{-5}$. Gradients
below that flush to zero, and in a deep network many do --- so training
silently stops learning in some layers.

The fix for fp16 is *loss scaling*: multiply the loss by a large constant
before `backward()` (so gradients land in representable range), then divide
the gradients before the optimiser step. `torch.cuda.amp.GradScaler` does this
with dynamic adjustment.

bf16 has the same exponent range as fp32, so gradients do not underflow, and
no scaling is needed. Use bf16 on any hardware that supports it.
:::

```python title="Mixed precision, correctly"
from torch.amp import autocast, GradScaler

scaler = GradScaler(enabled=(dtype == torch.float16))
for batch in loader:
    with autocast("cuda", dtype=torch.bfloat16):
        loss = model(batch)              # matmuls in bf16, reductions in fp32
    scaler.scale(loss).backward()        # no-op scaling for bf16
    scaler.unscale_(opt)                 # unscale before clipping
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True)
```

`autocast` does not cast everything. It keeps softmax, layer norm, and
reductions in fp32 because they are numerically sensitive, and casts matmuls
and convolutions to the low-precision type. This is why "just call `.bfloat16()`
on the model" is worse than autocast --- it casts the sensitive operations too.

## The autograd graph

@fig: autograd_graph | 150 | The graph PyTorch builds during the forward pass. Leaf tensors with `requires_grad=True` accumulate into `.grad`; intermediate nodes hold a `grad_fn`. `detach()` cuts an edge; `no_grad()` stops the graph being built at all.

```python title="Three ways to stop gradients, and they differ"
# 1. no_grad: do not build the graph at all. Saves memory AND time.
with torch.no_grad():
    val_loss = model(x_val)

# 2. detach: build the graph, then cut this edge.
target = teacher(x).detach()          # no gradient flows into the teacher

# 3. requires_grad_(False): freeze parameters.
for p in model.encoder.parameters():
    p.requires_grad_(False)
# Also remove them from the optimizer, or momentum will still move them:
opt = AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
```

| Symptom | Cause |
|---|---|
| `RuntimeError: backward through the graph a second time` | called `backward()` twice; use `retain_graph=True` or restructure |
| Memory grows every step | keeping a tensor with `grad_fn` in a list; `.detach()` or `.item()` it |
| Gradients are `None` | parameter not used in the loss, or `requires_grad=False` |
| `leaf Variable that requires grad is being used in an in-place operation` | `p += x` on a leaf; use `p.data` or `with torch.no_grad()` |
| Loss does not change | an accidental `detach()` between input and loss |

@tbl: Autograd errors and their causes. The second row is the classic memory leak: `losses.append(loss)` without `.item()` keeps the whole graph alive for every step of the epoch.

## The four memory problems

```python title="Diagnose before you guess"
print(torch.cuda.memory_summary())
print(f"allocated {torch.cuda.memory_allocated()/1e9:.2f} GB, "
      f"reserved {torch.cuda.memory_reserved()/1e9:.2f} GB")

# A precise picture of what is holding memory:
torch.cuda.memory._record_memory_history()
... # run a few steps
torch.cuda.memory._dump_snapshot("snap.pickle")   # view at pytorch.org/memory_viz
```

1. **Activation memory** dominates for large models. Fix with gradient
   checkpointing (Chapter 8) or a smaller batch.
2. **Fragmentation**: reserved memory far exceeds allocated. Fix with
   `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, or keep shapes
   constant.
3. **Graph retention**: a list of loss tensors, or a hidden state carried
   across steps without `.detach()`.
4. **The optimiser state**: 8 bytes per parameter for Adam's moments in fp32
   (Chapter 11). This is not a leak; it is arithmetic.

:::practice The task
(a) Build a non-contiguous tensor, time a matmul on it and on its contiguous
copy, and explain the gap. (b) Put a `.item()` inside a training loop and
measure the throughput cost; remove it and measure again. (c) Train the same
model in fp32, fp16 with a `GradScaler`, and bf16; compare step time, memory
and final loss. (d) Reproduce the graph-retention leak with
`losses.append(loss)` and fix it. (e) Record a memory snapshot and identify
the three largest allocations.

**You have this skill when** you can predict your model's peak memory before
launching, and when an OOM sends you to the snapshot rather than to
`batch_size //= 2`.
:::

:::exercise
1. For `x` of shape (2,3,4), give the strides of `x`, `x.transpose(0,2)` and
   `x.permute(1,0,2)`. Verify.
2. Find an operation for which `reshape` succeeds and `view` raises. Explain.
3. † Measure the throughput of a training loop with and without
   `pin_memory=True` plus `non_blocking=True`. Report the ratio and explain
   when it does not help.
4. Demonstrate fp16 gradient underflow: print the fraction of gradient
   elements that are exactly zero, with and without loss scaling.
5. Show that `model.bfloat16()` and `autocast(bfloat16)` give different
   results, and identify which operations differ.
6. † Freeze an encoder with `requires_grad_(False)` but leave it in the
   optimiser. Show the parameters still move, and explain why.
7. Use the memory profiler on a real training step and attribute every
   gigabyte to parameters, gradients, optimiser state or activations.
:::

:::recap
- A tensor is storage plus shape plus stride; transposes and slices are views,
  fancy indexing and masks copy.
- CUDA is asynchronous: `.item()`, `.cpu()` and printing force a
  synchronisation, and one in the inner loop can cost a third of throughput.
- bf16 is the default because it has fp32's exponent range; fp16 needs loss
  scaling to stop gradients underflowing.
- `autocast` keeps sensitive ops in fp32 --- casting the whole model is worse.
- `no_grad` prevents the graph, `detach` cuts an edge, `requires_grad_(False)`
  freezes parameters (and you must also remove them from the optimiser).
- The four memory problems are activations, fragmentation, graph retention and
  optimiser state; the snapshot tool tells you which.
:::
