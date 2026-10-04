# Training at Scale
@short: Training at Scale
@subtitle: What changes when one GPU is no longer enough
@tier: advanced
@prereq: Chapter 23
@blurb: Scaling from one GPU to many is not a configuration change; it is a different set of constraints. Memory is partitioned, communication becomes a first-class cost, and failures become routine. This chapter covers the memory arithmetic, the four parallelism axes, what each one costs in communication, and how to choose a configuration for a given model and cluster.
@objectives:
- Compute a training job's memory requirement before launching it
- Explain data, tensor, pipeline and sequence parallelism and their costs
- Configure FSDP or ZeRO correctly for a given model and cluster
- Diagnose a slow distributed job using the roofline of communication
- Handle the failure modes that appear only at scale

## The memory arithmetic

Do this before requesting the cluster.

```python title="Every byte, accounted for"
def training_memory_gb(n_params, batch, seq, dim, layers,
                       optimizer="adamw", precision="bf16",
                       zero_stage=0, world=1, checkpointing=False):
    P = n_params
    # --- model state (Chapter 11) ---
    weights = 2 * P                       # bf16
    grads   = 2 * P                       # bf16
    master  = 4 * P                       # fp32 master copy
    opt     = 8 * P if optimizer == "adamw" else 4 * P    # m and v, fp32

    sharded = {0: (weights, grads, master + opt),
               1: (weights, grads, (master + opt) / world),
               2: (weights, grads / world, (master + opt) / world),
               3: (weights / world, grads / world, (master + opt) / world)}
    w, g, o = sharded[zero_stage]
    state = w + g + o

    # --- activations ---
    per_layer = batch * seq * dim * 2 * 12           # ~12 tensors/layer, bf16
    acts = per_layer * (layers ** 0.5 if checkpointing else layers)
    attn = batch * layers * seq * seq * 2 * 2        # 0 with FlashAttention
    return (state + acts) / 1e9

print(training_memory_gb(7e9, batch=4, seq=4096, dim=4096, layers=32))
```

| Item | Bytes per parameter | 7B model |
|---|---|---|
| bf16 weights | 2 | 14 GB |
| bf16 gradients | 2 | 14 GB |
| fp32 master weights | 4 | 28 GB |
| Adam $m$, $v$ (fp32) | 8 | 56 GB |
| **Model state total** | **16** | **112 GB** |
| Activations (batch 4, seq 4096) | — | ~25 GB |

@tbl: A 7B model needs about 137 GB to train, which does not fit on an 80 GB device. This single table is why every technique in this chapter exists.

## The four axes

@fig: parallelism_axes | 132 | The four ways to split a training job. They are composable: a large run typically uses data parallelism across nodes, tensor parallelism within a node, and pipeline parallelism across a few node groups.

**Data parallel (DP).** Every device holds the whole model and a different
slice of the batch. Gradients are all-reduced each step. Communication:
$2P$ bytes per step (ring all-reduce is bandwidth-optimal). Simple, and the
first thing to try.

**ZeRO / FSDP.** Data parallel, but the model state is *sharded* across
devices and gathered just in time. Stage 1 shards the optimiser state, stage 2
also the gradients, stage 3 also the parameters. Stage 3 reduces per-device
state from $16P$ to $16P/N$ at the cost of gathering parameters twice per step
(forward and backward).

**Tensor parallel (TP).** Split individual matrices across devices. An
attention head or an MLP column block goes on each device, and the results are
combined with an all-reduce *inside every layer*. Communication is frequent
and latency-sensitive, so TP belongs **within a node**, over NVLink, never
across a slower network.

**Pipeline parallel (PP).** Different layers on different devices. Activations
are passed forward and gradients backward. Cheap in bandwidth but introduces
a *bubble* --- devices idle while waiting for the pipeline to fill:

$$\text{bubble fraction} = \frac{p - 1}{m + p - 1}$$

for $p$ stages and $m$ micro-batches. With $p = 8$ and $m = 8$ that is
47% wasted; with $m = 64$ it is 10%. Always use many micro-batches.

**Sequence / context parallel.** Split the *sequence* across devices. The
only way to train on sequences too long for one device's activation memory,
and it requires communication inside attention (ring attention).

| Axis | Splits | Communication per step | Place it |
|---|---|---|---|
| Data | the batch | $2P$ all-reduce | across nodes |
| ZeRO-3 / FSDP | model state | $3P$ (gather ×2, reduce ×1) | across nodes |
| Tensor | matrices | $O(\text{layers} \times b s d)$ all-reduce | inside a node |
| Pipeline | layers | activations at boundaries only | across node groups |
| Sequence | the sequence | attention-internal | inside a node |

@tbl: The axes and their costs. The placement column is the practical rule: put the chattiest parallelism on the fastest interconnect.

## FSDP in practice

```python title="A working FSDP configuration"
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from functools import partial

model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,       # = ZeRO-3
    auto_wrap_policy=partial(transformer_auto_wrap_policy,
                             transformer_layer_cls={Block}),
    mixed_precision=MixedPrecision(param_dtype=torch.bfloat16,
                                   reduce_dtype=torch.float32,   # see below
                                   buffer_dtype=torch.bfloat16),
    device_id=torch.cuda.current_device(),
    limit_all_gathers=True,            # bounds peak memory
    use_orig_params=True,              # needed for torch.compile
)
```

:::warning Three FSDP configuration errors
**No auto-wrap policy.** Without it FSDP wraps the whole model as one unit, so
it gathers *every* parameter before the forward pass --- exactly what
sharding was supposed to avoid. Always wrap per transformer block.

**`reduce_dtype=bfloat16`.** Gradient reduction in bf16 loses precision
proportional to the number of ranks, and at 512 ranks it is measurable. Reduce
in fp32; it costs bandwidth and is almost always worth it.

**Saving the wrong state dict.** `model.state_dict()` under FSDP returns
*shards*. Use `FullStateDictConfig(offload_to_cpu=True, rank0_only=True)` and
a `state_dict_type` context, or you will save 8 partial checkpoints and
discover it at load time.
:::

## Diagnosing a slow distributed job

```python title="Compute the communication floor before blaming the code"
# Ring all-reduce moves 2(N-1)/N * P bytes per device, ~2P for large N.
#
#   7B params, bf16 gradients = 14 GB
#   InfiniBand at 200 Gb/s    = 25 GB/s
#   -> ~1.1 s per all-reduce
#
# If your step takes 1.4 s of compute, communication is 44% overhead
# unless it is OVERLAPPED with the backward pass (FSDP does this by default:
# it reduces each layer's gradients while the next layer is still computing).
#
# If measured step time >> compute + max(0, comm - overlap), look for:
#   - a straggler rank (uneven data, thermal throttling, a slow disk)
#   - a synchronisation inside the loop (.item(), Chapter 22)
#   - gradient reduction not overlapping (wrapping policy too coarse)
```

| Symptom | Likely cause |
|---|---|
| Scaling efficiency < 70% at 8 GPUs | communication not overlapping |
| One rank consistently slower | data skew, or hardware; check per-rank step time |
| Throughput falls as nodes are added | crossed a network boundary; check topology |
| Memory fine at 8, OOM at 64 | per-rank batch held constant; global batch grew |
| Frequent NCCL timeouts | a straggler exceeding the timeout, not a deadlock |

@tbl: Distributed performance problems. The first is most common, and is usually a wrapping-policy or bucket-size issue rather than anything in your code.

## Failures at scale

:::insight At 1000 GPUs, failure is the normal case
With a mean time between failures of one week per node, a 128-node job fails
roughly every 80 minutes. Long training runs are therefore built around
failure rather than hoping to avoid it:

- **Checkpoint frequently** (every 10--30 minutes), asynchronously, to local
  NVMe first and object storage second.
- **Make restarts automatic.** The job should resume from the latest complete
  checkpoint without a human.
- **Use elastic training** where supported, so the job continues on fewer
  nodes rather than dying.
- **Monitor per-rank throughput**, not just the aggregate. A straggler slows
  everyone and shows up in the aggregate only as mild disappointment.
- **Keep the last three checkpoints.** The most recent one is sometimes the
  one written during the failure.
:::

:::practice The task
(a) Compute the memory requirement for a model you would like to train, by
hand, then verify with `torch.cuda.max_memory_allocated()`. (b) Run the same
model with DDP, FSDP-SHARD_GRAD_OP and FSDP-FULL_SHARD, and record memory and
throughput for each. (c) Measure scaling efficiency at 1, 2, 4 and 8 GPUs and
identify where it falls below 80%. (d) Remove the auto-wrap policy and
measure the memory difference. (e) Compute the pipeline bubble for your
configuration and verify it against measured utilisation.

**You have this skill when** you can size a run --- devices, parallelism
configuration, expected throughput --- before submitting it, and be right
within about 20%.
:::

:::exercise
1. Derive the 16-bytes-per-parameter figure and state what changes with an
   8-bit optimiser.
2. Show that ring all-reduce moves $2(N-1)P/N$ bytes per device and is
   bandwidth-optimal.
3. † Measure the actual all-reduce bandwidth on your cluster and compare to
   the specification. Explain the gap.
4. Derive the pipeline bubble formula and compute the micro-batch count needed
   to keep it below 10% for 16 stages.
5. Run FSDP with `reduce_dtype` bf16 and fp32 at 8 ranks and measure the
   gradient difference.
6. † Simulate a straggler by adding a delay on one rank and measure the effect
   on aggregate throughput. Explain the shape of the curve.
7. Design a checkpointing strategy for a 1000-GPU, 30-day run. State the
   frequency, the storage, and the expected lost work per failure.
:::

:::recap
- Training memory is $16P$ bytes of model state plus activations; a 7B model
  needs ~137 GB, which is why sharding exists.
- Four axes: data (all-reduce $2P$), ZeRO/FSDP (shards state), tensor
  (in-layer all-reduce, keep it inside a node), pipeline (cheap bandwidth,
  bubble $\frac{p-1}{m+p-1}$), sequence (for very long contexts).
- Put the chattiest parallelism on the fastest interconnect.
- FSDP needs a per-block auto-wrap policy, fp32 gradient reduction, and the
  right state-dict configuration.
- Compute the communication floor before blaming your code; most scaling
  losses are failed overlap.
- At scale, failure is routine: checkpoint often, restart automatically,
  monitor per-rank throughput.
:::
