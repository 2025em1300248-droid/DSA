# Inference and Serving
@short: Inference and Serving
@subtitle: Where quality meets the bill
@tier: advanced
@prereq: Chapters 11, 5
@blurb: Serving a model well is now a discipline in its own right, and it is where an enormous amount of money is either saved or wasted. The governing fact is that token generation is memory-bandwidth bound, not compute bound, and almost every serving optimisation follows from that single observation.
@objectives:
- Explain why decoding is bandwidth-bound and what follows from it
- Compute the memory budget for a serving deployment
- Use batching, quantisation, caching and speculative decoding appropriately
- Choose between an API and self-hosting on defensible economics

## The governing fact

Generating one token requires reading every weight the model uses from
memory. For a 7-billion-parameter model in fp16 that is 14 GB read per token.
The arithmetic performed is about 14 GFLOPs. On a device with 2 TB/s of
bandwidth and 500 TFLOP/s of compute, the read takes 7 ms and the arithmetic
takes 0.03 ms. **Decoding is roughly two hundred times memory-bound.**

Every serving technique below is an attack on that ratio: read fewer bytes
per token, or amortise the read over more tokens.

## The cost ladder

@fig: cost_ladder | 172 | Relative cost per million served tokens for the same task at the same quality bar. Two orders of magnitude separate the top and bottom rows, and none of it is model-quality work.

## The capabilities

:::checklist CORE --- the fundamentals
- Prefill versus decode: prefill processes the prompt in parallel and is
  compute-bound; decode generates one token at a time and is bandwidth-bound.
  They have opposite bottlenecks, which is why some systems run them on
  separate hardware
- Time to first token (dominated by prefill and queueing) versus time per
  output token (dominated by bandwidth). Users perceive them differently, so
  measure and budget them separately
- **Continuous batching**: the single largest throughput lever. Because
  decode is bandwidth-bound, serving 32 sequences costs little more than
  serving one --- the weights are read once either way
- **KV cache** memory: $4 \cdot B \cdot S \cdot L \cdot H_{kv} \cdot d_h$
  bytes in fp16. Compute it for your model and context length; it usually
  bounds your batch size and therefore your throughput
- **Paged attention**: store the KV cache in fixed-size blocks with a
  per-request block table, eliminating fragmentation and enabling sharing
- **Prefix caching**: shared system prompts and multi-turn history are
  recomputed for nothing otherwise; hit rates of 50--90% are typical on chat
  traffic
:::

:::checklist CORE --- making it cheaper
- **Quantisation**: int8 and fp8 weights halve or quarter the bytes read per
  token, which on a bandwidth-bound workload is close to a proportional
  speedup. Know the families --- GPTQ, AWQ, GGUF for CPU/edge --- and always
  measure the quality cost on your own evaluation set rather than trusting a
  published number
- **KV cache quantisation**, which extends context or batch at a small
  quality cost
- **Speculative decoding**: a small draft model proposes several tokens and
  the large model verifies them in one pass. Provably preserves the output
  distribution, so it is safe to enable by default. Variants use $n$-gram
  lookup from the prompt or extra prediction heads instead of a draft model
- **Structured and constrained decoding** for guaranteed-valid output, at
  negligible runtime cost
- **Distillation** to a task-specific small model, which is the largest
  saving available when the task is narrow
- **Routing**: classify the request and send easy traffic to a small model
- **Semantic caching** of whole responses, with care about correctness
:::

:::checklist CORE --- operations
- Serving engines: vLLM and SGLang are the common open-source choices;
  TensorRT-LLM where you are on NVIDIA and want the last ten per cent;
  llama.cpp for CPU and edge
- Autoscaling on GPUs, where cold start is minutes and spot interruption is
  routine
- Load balancing with session affinity so a follow-up turn lands on the
  machine holding its prefix cache
- Queueing and admission control; shedding load gracefully under overload
- Timeouts, retries with backoff and jitter, circuit breakers, and a fallback
  model
- Streaming responses, because perceived latency is mostly time to first
  token
- Observability: tokens per second, queue depth, cache hit rate, GPU
  utilisation, cost per request
:::

:::checklist CORE --- the build-or-buy decision
| Favours an API | Favours self-hosting |
|---|---|
| Low or spiky volume | High steady volume |
| You need frontier quality | A small model suffices |
| Small team, no GPU operations experience | You have platform engineering |
| Requirements still changing | Requirements stable |
| No data-residency constraint | Data cannot leave your boundary |
| Latency budget is generous | You need tight tail latency control |

The honest break-even is usually higher than people expect: below roughly a
sustained few hundred million tokens a month, an API is normally cheaper once
engineering time is counted.
:::

:::checklist AWARENESS
- Disaggregated serving: prefill and decode on separate hardware pools
- Multi-LoRA serving: many adapters against one base model
- Edge and on-device inference, and the quantisation that makes it possible
- Compilation stacks: TensorRT, torch.compile with inductor, ONNX Runtime
:::

## How to tell you have it

:::practice The task
Serve an open-weights model yourself.
1. Compute the KV cache size and the maximum batch size on paper first.
2. Deploy with vLLM or SGLang. Measure tokens per second at batch sizes 1, 8,
   32 and 64, and plot throughput against latency.
3. Enable prefix caching; measure the hit rate and the time-to-first-token
   change on a workload with a shared system prompt.
4. Quantise to int8. Measure the throughput gain *and* the quality change on
   your evaluation set. Report both.
5. Enable speculative decoding; measure the acceptance rate and the net
   speedup.
6. Compute cost per million tokens for your deployment and compare with an
   API at the same quality. State the break-even volume.
:::

:::pitfall The four serving mistakes
1. **Optimising the model when the bottleneck is elsewhere.** Measure
   queueing, prefill and decode separately before touching anything.
2. **Batch size one.** The most common cause of terrible economics; it wastes
   almost all of the hardware.
3. **Quantising without an eval.** The quality cost is task-dependent and
   sometimes large; a published benchmark number is not evidence for your
   task.
4. **Self-hosting at low volume.** GPU idle time and engineering hours
   dominate; the spreadsheet usually says otherwise than the instinct does.
:::

:::note Time to competence
**4--6 weeks** for the CORE list with access to a GPU. The memory arithmetic
is an afternoon and prevents most of the wasted effort.
:::

:::recap
- Decoding is memory-bandwidth bound; every serving optimisation reduces
  bytes read per token or amortises the read over more tokens.
- Continuous batching is the largest throughput lever; KV cache size bounds
  the batch and therefore the throughput.
- Paged attention removes fragmentation; prefix caching removes recomputation
  of shared prompts.
- Quantisation buys close to proportional speedup on this workload; always
  measure the quality cost yourself.
- Speculative decoding preserves the output distribution exactly.
- Prefill and decode have opposite bottlenecks; measure and budget TTFT and
  TPOT separately.
- The API-versus-self-hosting break-even is higher than instinct suggests.
:::
