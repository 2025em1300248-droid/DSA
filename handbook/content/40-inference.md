# Inference and Serving
@short: Inference
@subtitle: Turning a 0.3%-utilised GPU into a useful one
@tier: advanced
@prereq: Chapter 30
@blurb: Serving is where the economics of an LLM product are decided. The techniques are all variations on one idea --- find more work for the memory-bound decode phase to do while it waits --- and together they routinely cut cost by an order of magnitude. This chapter covers them in the order you should apply them.
@objectives:
- Apply continuous batching and explain what it fixes
- Explain paged attention and prefix sharing, and what each saves
- Use speculative decoding and predict its speedup
- Choose a serving stack and configure it for your traffic
- Build a cost reduction ladder and measure each rung

## Continuous batching

Static batching waits for a full batch, runs it to completion, and starts the
next. Because sequences finish at different lengths, most of the batch sits
idle waiting for the longest one.

@fig: continuous_batching | 168 | Static versus continuous batching. In the static scheme the hairlines are GPU doing nothing: every slot waits for the longest sequence in the batch. Continuous batching admits a new request into a slot the moment one frees, which typically multiplies throughput by 2--4× with no quality change at all.

```python title="The scheduler loop, in outline"
def serve_loop(engine, queue, max_batch=256, max_tokens=8192):
    running = []
    while True:
        # Admit new requests into free slots, subject to KV-cache capacity.
        while queue and len(running) < max_batch and engine.free_blocks() > 0:
            running.append(engine.admit(queue.pop()))

        engine.step(running)                    # ONE decode step for all

        for r in list(running):                 # evict the finished ones
            if r.finished:
                engine.release(r)               # free its KV blocks NOW
                running.remove(r)
                yield r.result
```

The decisive detail is releasing the finished request's KV blocks immediately,
so the freed memory admits a new request on the very next iteration rather
than at the end of the batch.

## Paged attention

The KV cache is the scarce resource (Chapter 30). Naive allocation reserves
the *maximum* sequence length for every request, so a request that generates
50 tokens of a possible 4096 wastes 98% of its allocation.

Paged attention borrows virtual memory's idea: store the cache in fixed-size
blocks (typically 16 tokens) with a per-sequence block table, allocated on
demand.

```python title="What the block table buys"
# Naive:   reserve 4096 tokens per request.
#          100 requests x 4096 x 2 x L x n_kv x d_head x 2 bytes
#          — most of it never written to.
#
# Paged:   allocate 16-token blocks as the sequence grows.
#          Internal fragmentation is at most 15 tokens per sequence.
#
# Reported effect: 2–4x more concurrent sequences in the same memory,
# which is the same multiple on throughput.
```

**Prefix sharing** falls straight out of the block table. If a hundred
requests share the same 2000-token system prompt, they can point at the *same*
physical blocks. Copy-on-write handles the divergence when generations differ.

```python title="Structure prompts so the shared prefix is actually shared"
# GOOD — fixed content first, variable content last:
prompt = SYSTEM + TOOLS + FEW_SHOT + user_input

# BAD — a timestamp at the front invalidates the whole prefix:
prompt = f"[{datetime.now()}] " + SYSTEM + TOOLS + user_input
```

This is the same ordering rule as Chapter 31, and it is worth real money: a
shared 2000-token prefix across high traffic removes most of the prefill cost.

## Speculative decoding

Decode is memory-bound, so verifying several tokens costs almost the same as
generating one. Speculative decoding exploits this: a small *draft* model
proposes $k$ tokens, the large model verifies them all in a single forward
pass, and the accepted prefix is kept.

```python title="The algorithm, with the property that makes it safe"
def speculative_decode(target, draft, prompt, k=4, max_new=256):
    out = list(prompt)
    while len(out) - len(prompt) < max_new:
        # 1. Draft k tokens cheaply.
        drafted, q_probs = draft.generate(out, k)

        # 2. Verify ALL of them in ONE target forward pass.
        p_probs = target.forward(out + drafted)        # k+1 distributions

        # 3. Accept token i with probability min(1, p_i / q_i).
        n_accepted = 0
        for i, tok in enumerate(drafted):
            if random() < min(1.0, p_probs[i][tok] / q_probs[i][tok]):
                n_accepted += 1
            else:
                break
        out += drafted[:n_accepted]

        # 4. Sample one more from the corrected residual distribution.
        out.append(sample_residual(p_probs[n_accepted], q_probs[n_accepted]))
    return out
```

:::insight Why the output distribution is exactly unchanged
The accept/reject rule plus the residual-distribution resample is a rejection
sampler for the target distribution. The tokens you get are drawn from exactly
the distribution the large model would have produced on its own.

So speculative decoding is **not** an approximation. It is a pure latency
optimisation with no quality trade-off, which is unusual and is why it is
always worth trying.

The expected number of tokens accepted per target forward pass is
$\frac{1 - \alpha^{k+1}}{1 - \alpha}$ for acceptance rate $\alpha$ --- a
geometric sum, because acceptance stops at the first rejection. Dividing by
the draft overhead gives

$$\text{speedup} \approx \frac{1 - \alpha^{k+1}}{(1-\alpha)(1 + ck)}$$

where $c$ is the draft's cost relative to the target. With $\alpha = 0.7$,
$k = 4$ and a draft 20× cheaper, that is about 2.3×. The acceptance rate is
the whole game: a well-matched draft model (same tokeniser, same family,
trained on similar data) is what makes it work.
:::

| Draft source | Acceptance | Notes |
|---|---|---|
| A small model of the same family | 0.6--0.8 | the standard choice |
| N-gram / prompt lookup | 0.3--0.5 | free; excellent for summarisation and code edits |
| Medusa / EAGLE heads | 0.7--0.85 | extra heads on the target; needs training |
| An unrelated small model | 0.2--0.4 | rarely worth it |

@tbl: Draft strategies. Prompt lookup --- drafting by copying from the input --- costs nothing and works remarkably well whenever the output quotes the input, which covers summarisation, editing, and structured extraction.

## The cost reduction ladder

```python title="Apply in this order; measure quality at every rung"
LADDER = [
    ("shorten the output",        "2-5x",  "free",       "none"),
    ("prompt caching",            "1.5-3x", "free",      "none"),
    ("continuous batching",       "2-4x",  "config",     "none"),
    ("paged attention",           "2-4x",  "config",     "none"),
    ("route easy requests small", "2-10x", "a day",      "measure it"),
    ("speculative decoding",      "1.5-2.5x", "a day",   "none"),
    ("quantise to int8/fp8",      "2x",    "a day",      "small"),
    ("quantise to int4",          "3-4x",  "days",       "measurable"),
    ("distil a small model",      "5-20x", "weeks",      "task-specific"),
]
# The first four are free and compose. Most teams can get 10x before
# touching the model at all.
```

:::perf Routing is the highest-leverage model-level change
Most traffic is easy. A classifier --- or a cheap model's own confidence ---
sends the easy majority to a small model and escalates the rest:

```python
def route(request):
    if cheap_model_confident(request):        # measured, not assumed
        return SMALL
    if request.requires_tools or request.long_context:
        return LARGE
    return MEDIUM
```

Measure the *escalation rate* and the *quality on the routed-small subset*
separately. A router that sends 70% of traffic to a model costing a tenth
as much cuts the bill by roughly 60%, and the only question that matters
is whether those 70% are served as well.
:::

## Choosing a stack

| Stack | Strength | Choose when |
|---|---|---|
| **vLLM** | paged attention, broad model support, mature | the default for self-hosting |
| **SGLang** | RadixAttention prefix caching, structured output | heavy prefix sharing, constrained decoding |
| TensorRT-LLM | peak throughput on NVIDIA | you can afford the build complexity |
| llama.cpp | CPU and Apple silicon, GGUF quantisation | local, edge, small deployments |
| Hosted API | zero operations | below the crossover volume |

@tbl: Serving stacks. The crossover with a hosted API is usually in the hundreds of millions of tokens per month; below that, self-hosting costs more in engineering time than it saves in compute.

```python title="A vLLM configuration with the parameters that matter"
from vllm import LLM, SamplingParams

llm = LLM(
    model="your/model",
    tensor_parallel_size=2,
    gpu_memory_utilization=0.92,      # the rest is the KV cache
    max_model_len=8192,               # smaller = more concurrent sequences
    enable_prefix_caching=True,       # free, if prompts share a prefix
    speculative_model="your/draft",   # if you have a matched draft
    num_speculative_tokens=4,
    quantization="fp8",               # on supported hardware
)
```

:::practice The task
Take a working LLM feature. (a) Measure baseline cost per thousand requests
and p95 latency. (b) Shorten the output format and re-measure --- report the
ratio. (c) Enable prompt caching and prefix-friendly ordering; re-measure.
(d) Self-host with continuous batching and paged attention; measure throughput
against batch size. (e) Add speculative decoding and report the measured
speedup against the formula's prediction. (f) Build a router and report the
escalation rate, the cost saving, and the quality on the routed-small subset.
Plot the cost curve and the quality at every rung.

**You have this skill when** you can cut an inference bill fivefold and show,
with intervals, that quality did not move.
:::

:::exercise
1. Simulate static and continuous batching with a realistic distribution of
   output lengths. Report the throughput ratio.
2. Compute the KV memory wasted by max-length preallocation for a traffic
   distribution of yours.
3. † Implement speculative decoding and verify empirically that the output
   distribution matches the target's over 10,000 samples.
4. Measure the acceptance rate for three draft models and relate it to the
   measured speedup via the formula.
5. Implement prompt-lookup drafting and measure its acceptance rate on a
   summarisation task.
6. † Build a router with a confidence threshold. Plot cost against quality as
   the threshold varies and choose an operating point.
7. Quantise a model to int8 and int4; report the quality change on your
   evaluation set with intervals, and the throughput gain for each.
:::

:::recap
- Continuous batching admits new requests into freed slots, typically 2--4×
  throughput at no quality cost.
- Paged attention stores the KV cache in small blocks, removing the waste of
  max-length preallocation and enabling prefix sharing.
- Order prompts fixed-content-first so prefixes can actually be shared.
- Speculative decoding drafts $k$ tokens and verifies them in one pass; the
  output distribution is provably unchanged, and acceptance rate decides the
  speedup.
- Apply the ladder in order: shorten outputs, cache prefixes, batch
  continuously, page the cache --- all free --- then route, speculate and
  quantise.
- Routing is the highest-leverage model-level change; measure quality on the
  routed-small subset separately.
- vLLM is the default self-hosting stack; below a few hundred million tokens a
  month, a hosted API is cheaper overall.
:::
