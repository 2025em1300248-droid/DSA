# What a Forward Pass Costs
@short: The Forward Pass
@subtitle: Prefill, decode, the KV cache, and where the money goes
@tier: core
@prereq: Chapters 7, 26
@blurb: An API call has two phases with completely different performance characteristics, and almost every inference decision follows from that split. This chapter works through prefill and decode, the KV cache, how batching changes the economics, and how to compute latency and cost for a workload before you build it.
@objectives:
- Distinguish prefill from decode and explain why they behave differently
- Compute KV-cache size and the maximum batch it permits
- Derive time-to-first-token and time-per-output-token from hardware numbers
- Explain why output tokens cost several times more than input tokens
- Build a cost model for a workload before implementing it

## Two phases, two regimes

@fig: prefill_decode | 165 | Prefill processes the whole prompt in one parallel pass --- compute-bound, high GPU utilisation. Decode produces one token at a time, each a matrix--vector product against the full weights --- memory-bound, and the GPU is mostly idle waiting on memory.

**Prefill.** All $T$ prompt tokens go through the model at once. Every matmul
is $(T \times d)\cdot(d \times d)$ with $T$ in the hundreds or thousands:
arithmetic intensity is high (Chapter 7), the GPU is compute-bound, and
utilisation is good. Cost is $O(T)$ in FLOPs for the linear layers and
$O(T^2)$ for attention.

**Decode.** One token at a time. Each step is $(1 \times d)\cdot(d \times d)$
--- a matrix--vector product with arithmetic intensity about 1. The GPU reads
the entire weight matrix to produce one token, and spends nearly all of its
time waiting on memory.

| | Prefill | Decode |
|---|---|---|
| Tokens per pass | all of them | 1 |
| Regime | compute-bound | **memory-bound** |
| GPU utilisation | 40--70% | 1--10% at batch 1 |
| Scales with | prompt length | output length |
| Batching helps | modestly | **enormously** |
| Determines | time to first token | tokens per second |

@tbl: The two phases. Every serving technique in Chapter 40 is an attempt to improve the right-hand column, because that is where the idle silicon is.

## The decode arithmetic

```python title="Time per output token, from first principles"
# At batch 1, each decode step must read every weight from HBM:
#
#     t_step ≈ (bytes of weights) / (memory bandwidth)
#
# 70B model, bf16 weights = 140 GB
# HBM bandwidth (one 80 GB device class) ≈ 3.3 TB/s
#
#     t_step ≈ 140 / 3300 = 42 ms  ->  ~24 tokens/second
#
# The FLOPs are 2 * 70e9 = 140 GFLOP per token. At ~1000 TFLOP/s that is
# 0.14 ms of compute. So the device is doing useful arithmetic for about
# 0.3% of the step. The other 99.7% is waiting on memory.
```

:::insight Why batching is close to free during decode
The weights are read once per *step*, not once per *sequence*. Serving 32
requests concurrently reads the same 140 GB and produces 32 tokens instead of
one.

Throughput therefore rises almost linearly with batch size until either
(a) the KV cache exhausts memory, or (b) arithmetic intensity crosses the
ridge point and the operation becomes compute-bound. For a 70B model at
bf16 that crossover is in the hundreds.

This is the entire economic basis of inference serving: an idle GPU serving
one user is doing 0.3% useful work, and the job of a serving stack is to
find enough concurrent work to fill it.
:::

## The KV cache

Without a cache, generating token $n$ would recompute $K$ and $V$ for all
$n-1$ previous tokens --- $O(n^2)$ total work. Caching them makes generation
$O(n)$, at the cost of memory that grows with every token.

$$\text{cache bytes} = 2 \times L \times T \times n_{kv} \times d_{head} \times \text{bytes/elem}$$

```python title="Cache size, and the batch it allows"
def kv_cache_gb(layers, n_kv_heads, head_dim, seq, batch=1, bytes_per=2):
    return 2 * layers * n_kv_heads * head_dim * seq * batch * bytes_per / 1e9

# 70B-class, GQA with 8 KV heads, head_dim 128, 80 layers:
print(kv_cache_gb(80, 8, 128, 8192))        # 2.68 GB per sequence

# On a device with 80 GB, after 140 GB of weights... which does not fit.
# Two devices, 160 GB total, weights 140 GB -> 20 GB left:
print(20 / kv_cache_gb(80, 8, 128, 8192))   # ~7 concurrent sequences
```

That number --- seven --- is the real constraint on a serving deployment, and
it is why every technique that shrinks the KV cache (GQA, quantised cache,
paged attention, prefix sharing) translates directly into throughput.

## Latency, decomposed

$$\text{TTFT} = \text{queue} + \text{prefill}(T_{in}) + \text{overhead}$$
$$\text{total} = \text{TTFT} + T_{out} \times \text{TPOT}$$

```python title="A usable latency model"
def latency_ms(n_in, n_out, params_b=70, tp=2, bw_tbs=3.3, tflops=800):
    weights_gb = params_b * 2 / tp                 # per device, bf16
    prefill_flops = 2 * params_b * 1e9 * n_in
    prefill_ms = prefill_flops / (tflops * 1e12 * tp * 0.45) * 1000  # 45% MFU
    tpot_ms = weights_gb / (bw_tbs * 1000) * 1000
    return dict(ttft=round(prefill_ms, 1),
                tpot=round(tpot_ms, 1),
                total=round(prefill_ms + n_out * tpot_ms, 1))

print(latency_ms(n_in=2000, n_out=500))
```

| Input | Output | TTFT | TPOT | Total |
|---|---|---|---|---|
| 500 | 100 | ~0.2 s | ~21 ms | ~2.3 s |
| 2000 | 500 | ~0.8 s | ~21 ms | ~11 s |
| 8000 | 2000 | ~3.2 s | ~21 ms | ~45 s |
| 100000 | 500 | ~40 s | ~21 ms | ~50 s |

@tbl: Illustrative latencies for a 70B-class model at batch 1 on two devices. The last row is the one people do not anticipate: a very long prompt makes time-to-first-token dominate, which is why prompt caching matters so much for long system prompts.

## Why output tokens cost more

Providers typically price output at 2--5× input. This is not margin
policy; it reflects cost.

- **Input** is processed in a large parallel batch: high utilisation, so the
  per-token GPU-second cost is low.
- **Output** is generated one token at a time in a memory-bound regime with
  poor utilisation, so each token occupies far more GPU-time.
- **Output also extends the KV cache**, which occupies memory for the whole
  remaining request and reduces how many other requests can be served
  concurrently.

:::perf The three optimisations that follow directly
1. **Shorten outputs.** A prompt that asks for a JSON object rather than a
   prose explanation can cut cost by 5--10×. This is the single largest
   lever in most applications and it is free.
2. **Cache prefixes.** A long fixed system prompt is prefilled every call
   unless the provider or serving stack caches it. Prompt caching typically
   cuts both TTFT and input cost by a large factor.
3. **Batch.** If you control the serving stack, concurrency is what turns a
   0.3%-utilised GPU into a useful one.
:::

```python title="The cost model to build before writing the feature"
def monthly_cost(reqs_per_day, in_tok, out_tok, in_price, out_price,
                 cache_hit_rate=0.0, cached_discount=0.9):
    effective_in = in_tok * (1 - cache_hit_rate * cached_discount)
    per_req = (effective_in * in_price + out_tok * out_price) / 1e6
    return per_req * reqs_per_day * 30

# 100k requests/day, 3000 in, 500 out, $3/M in, $15/M out:
print(monthly_cost(100_000, 3000, 500, 3.0, 15.0))              # ~$49,500
print(monthly_cost(100_000, 3000, 500, 3.0, 15.0, cache_hit_rate=0.8))
                                                                 # ~$30,100
```

:::warning Run this calculation before building, not after
A feature that costs $49,500 a month is a different decision from one that
costs $5,000, and the difference is usually output length, a smaller model for
the easy majority of requests, and prompt caching --- all of which are far
cheaper to design in than to retrofit. Chapter 40 covers the full ladder.
:::

:::practice The task
For a model you have access to: (a) measure TTFT against input length for
100, 1000, 10000 tokens and fit the linear model; (b) measure tokens per second
at batch 1, 4, 16, 64 and find where throughput stops scaling; (c) compute the
KV-cache size for your configuration and predict the maximum batch, then
verify it by OOM; (d) rewrite one prompt to produce structured output instead
of prose and measure the cost change; (e) build the monthly cost model for a
real feature and present it.

**You have this skill when** you can quote a feature's monthly bill and p95
latency from the prompt template and the traffic estimate, before any code
exists.
:::

:::exercise
1. Explain why prefill is compute-bound and decode is memory-bound, in terms
   of arithmetic intensity.
2. Compute decode tokens per second for a 7B and a 70B model on the same
   hardware. Explain the ratio.
3. † Measure throughput against batch size and identify the point where the
   KV cache, not compute, becomes the limit.
4. Compute the KV cache for a 100k-token context and state what fraction of
   device memory it occupies.
5. Show that generating without a KV cache is $O(n^2)$ and measure the
   difference at $n = 512$.
6. † Measure the effect of prompt caching on TTFT and cost for a 4000-token
   system prompt across 100 calls.
7. Take a production prompt and reduce its output tokens by 5× without
   losing information. Report the cost change.
:::

:::recap
- Prefill is parallel and compute-bound; decode is one token at a time and
  memory-bound, with the GPU under 10% utilised at batch 1.
- Decode time per token is roughly weight bytes divided by memory bandwidth.
- Batching is nearly free during decode because the weights are read once per
  step, not once per sequence --- this is why serving stacks exist.
- The KV cache grows linearly with context and batch, and is usually what
  limits concurrency.
- TTFT is set by prompt length; total latency by output length.
- Output tokens cost more because they are generated inefficiently and hold
  cache memory; shortening outputs is the largest free saving.
- Build the cost model before building the feature.
:::
