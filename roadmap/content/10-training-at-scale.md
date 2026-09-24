# Training at Scale
@short: Training at Scale
@subtitle: When one GPU is not enough, and how to tell whether you need more
@tier: advanced
@prereq: Chapter 9
@blurb: Scaling a training job is mostly a memory-accounting exercise followed by a communication-cost exercise. Most engineers will never pretrain a foundation model, and most will eventually need multi-GPU training for fine-tuning or for a large classical workload. This chapter gives you the arithmetic and the decision procedure.
@objectives:
- Compute a training job's memory requirement before running it
- Choose among data, tensor, pipeline and expert parallelism from first principles
- Use FSDP or DeepSpeed correctly, and know what each stage shards
- Diagnose a scaling problem as compute, memory, communication or input bound

## The arithmetic you do first

:::math Memory for a $P$-parameter model, mixed precision with Adam
$$M \approx \underbrace{2P}_{\text{bf16 weights}} + \underbrace{2P}_{\text{grads}} + \underbrace{12P}_{\text{fp32 master} + m + v} = 16P \text{ bytes}$$
plus activations, which depend on batch size, sequence length and depth, and
plus workspace.

A 7-billion-parameter model therefore needs about **112 GB** before a single
activation is stored. That is why it does not fit on one 80 GB device and why
sharding exists. A 1-billion-parameter model needs 16 GB and fits
comfortably. Do this calculation *before* choosing a strategy; it usually
decides it.
:::

## The capabilities

:::checklist CORE --- parallelism
- **Data parallel (DDP)**: replicate the model, split the batch, all-reduce
  the gradients. Communication is $2(P-1)/P \times$ the parameter size per
  worker, independent of the worker count. Use when the model fits on one
  device
- **ZeRO / FSDP**: shard optimiser state (stage 1), then gradients (stage 2),
  then parameters (stage 3) across workers. Keeps the simplicity of data
  parallelism while removing its memory redundancy. This is the default for
  most people who need more than one GPU
- **Tensor parallel**: split each weight matrix across devices. Two
  all-reduces per layer, high volume --- only viable over a fast interconnect,
  so it stays inside a node
- **Pipeline parallel**: split the layers into stages. Only boundary
  activations cross the link, so it tolerates slow interconnects. Costs a
  bubble of $(S-1)/(M+S-1)$, reduced by more micro-batches
- **Expert parallel**: for MoE, distribute experts and route tokens with an
  all-to-all
- **3D parallelism**: compose them so the heaviest traffic uses the fastest
  link --- tensor within a node, pipeline across nodes, data across replicas
:::

:::checklist CORE --- mechanics
- `torchrun` and process groups; NCCL, and reading an NCCL error
- Overlapping communication with the backward pass, and gradient bucketing
- Activation checkpointing configured per layer or per block
- Sharded, asynchronous checkpointing --- gathering everything to rank zero is
  a serious and common mistake
- Mid-epoch resumption with correct dataloader state
- Cluster schedulers: Slurm in research settings, Kubernetes plus Ray or
  Kubeflow in industry
- Elastic and fault-tolerant training, because at scale hardware failure is
  routine rather than exceptional
:::

:::checklist CORE --- diagnosing a scaling problem
| Symptom | Likely cause | Check |
|---|---|---|
| GPU at 40%, CPU pegged | input pipeline | time the dataloader alone |
| GPU at 40%, CPU idle | I/O wait | storage throughput, shard size |
| Scales to 4 GPUs, not to 8 | communication bound | measure all-reduce time |
| One rank always last | straggler, unequal shards | per-rank step timing |
| Out of memory at a larger batch | activations | checkpointing, micro-batching |
| Throughput falls over time | memory fragmentation, leak | monitor allocator stats |
:::

:::checklist AWARENESS
- Scaling laws: the compute-optimal token-to-parameter relationship, and its
  practical inversion --- for models that will serve many tokens, training a
  smaller model on more data is usually the better economic choice
- Muon, Shampoo and other matrix-preconditioned optimisers
- FP8 training and its scaling and stability considerations
- Megatron-LM and the mechanics of large pretraining stacks
:::

:::insight The decision procedure, in order
1. Compute the memory requirement. If the model fits on one device with a
   usable batch size, use one device.
2. If it does not fit, first reduce: activation checkpointing, smaller
   micro-batch with accumulation, LoRA instead of full fine-tuning,
   8-bit optimiser states.
3. If it still does not fit, use **FSDP/ZeRO**. This covers the large
   majority of real needs.
4. Only if the model does not fit even sharded, or you are compute-bound
   across many nodes, reach for tensor and pipeline parallelism.

Most teams reach step 4 without seriously attempting step 2, and pay for it
in complexity and debugging time.
:::

## How to tell you have it

:::practice The task
Fine-tune a model that does not fit on your GPU.
1. Compute the memory requirement on paper first and state which components
   dominate.
2. Get it running with LoRA on one device; record throughput.
3. Get it running with FSDP on two or more devices; record throughput and the
   scaling efficiency.
4. Add activation checkpointing and quantify the memory/time trade.
5. Profile and state whether you are compute, memory, communication or input
   bound --- with a measurement, not a guess.
6. Kill a worker mid-run and resume from a checkpoint without losing more
   than one checkpoint interval.

Step 6 is the one that distinguishes people who have run real jobs.
:::

:::pitfall Distributed training's silent failures
**Different seeds per rank for the shuffle.** Ranks see overlapping data; the
effective epoch is wrong and nothing errors. Seed the shuffle identically and
shard the result; seed augmentation differently.

**Unequal shards.** If the dataset does not divide by the world size, a rank
finishes early and the collective hangs. Pad or drop explicitly.

**Metrics computed on rank zero only.** You report one shard's number.

**Checkpointing through rank zero.** It serialises the whole cluster and
scales badly; shard the checkpoint.
:::

:::note Time to competence
**4--6 weeks** for the CORE list given solid single-GPU training. The memory
arithmetic is an afternoon and prevents most of the wasted effort.
:::

:::recap
- Do the memory arithmetic first: roughly $16P$ bytes plus activations
  decides the strategy.
- Reduce before you distribute: checkpointing, accumulation, LoRA, 8-bit
  optimiser states.
- FSDP/ZeRO covers most real needs; tensor and pipeline parallelism are for
  when sharded data parallelism is genuinely insufficient.
- Ring all-reduce costs $2(P-1)/P \times N$ bytes per worker, independent of
  worker count; overlap it with the backward pass.
- Diagnose scaling problems by measurement: compute, memory, communication or
  input bound.
- The silent distributed failures are seeding, shard equality, rank-local
  metrics and centralised checkpointing.
:::
