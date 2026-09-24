# Foundation Model Fundamentals
@short: LLM Fundamentals
@subtitle: What you must understand about the model you did not train
@tier: core
@prereq: Chapter 9
@blurb: Most AI engineers will never train a foundation model and will spend every day working with one. That requires a specific and slightly unusual body of knowledge: how tokenisation constrains you, what context windows really cost, how sampling parameters change behaviour, why structured output is a decoding problem, and where the model's failure modes come from.
@objectives:
- Reason about tokenisation, context length and cost as a single budget
- Choose sampling parameters deliberately rather than by superstition
- Get reliable structured output and tool calls
- Know the standard failure modes and which are fixable by prompting

## The capabilities

:::checklist ESSENTIAL --- tokenisation and context
- BPE and byte-level BPE; why the vocabulary is 50k--300k and what that
  implies
- Characters per token varies by language and content: roughly 4 for English
  prose, 3 for code, and often below 1.5 for languages poorly represented in
  the vocabulary. This is a cost and a capability difference, not a curiosity
- Why models are bad at character-level tasks (counting letters, reversing
  strings): they do not see characters
- Context windows: what "1M context" costs in latency and money, and that
  effective use degrades well before the stated limit
- The lost-in-the-middle effect: material at the start and end of a long
  context is used more reliably than material in the middle. Order your
  context accordingly
- Token budgeting: system prompt, retrieved context, conversation history,
  output reserve --- and an explicit policy for what gets dropped first
:::

:::checklist ESSENTIAL --- decoding and sampling
- Greedy, temperature, top-$k$, top-$p$ (nucleus), min-$p$: what each
  truncation does and when it matters
- Temperature 0 is not deterministic in practice on GPU (batch-dependent
  float reduction order), and you should not build on the assumption
- Beam search is for tasks with a single right answer (translation,
  transcription) and is actively bad for open-ended generation
- Repetition, frequency and presence penalties, and their side effects
- Stop sequences and why they need to be chosen carefully
- Structured output: JSON mode, schema-constrained decoding, and why
  constraining the *format* is safe while constraining the *content* can
  force a confident wrong answer where the model would have declined
:::

:::checklist ESSENTIAL --- prompting and context engineering
- The techniques that reliably help: clear role and task, explicit output
  format, few-shot examples chosen to cover the failure modes, decomposition
  into steps, giving the model permission to say it does not know
- Chain-of-thought, and that modern reasoning models do this internally ---
  telling them to "think step by step" can now *hurt*
- Prompt structure: put stable content first so prefix caching can hit it;
  put the question last
- Delimiters and explicit sectioning of untrusted content
- Self-consistency (sample $n$, take the majority) when correctness matters
  more than cost
- The discipline of versioning prompts like code, with an eval per version
:::

:::checklist ESSENTIAL --- tool use
- Function/tool calling: schema definition, the model's selection behaviour,
  parallel calls, and handling malformed arguments
- MCP (Model Context Protocol) as the emerging standard for exposing tools
  and resources to models across vendors
- Designing tools the model can actually use: few tools, unambiguous names,
  descriptions written for the model rather than for a developer, errors that
  tell the model how to recover
- Idempotency and confirmation for anything with side effects
:::

:::checklist CORE --- model selection and economics
- The tradeoff space: frontier API, open-weights hosted, open-weights
  self-hosted, small fine-tuned specialist
- Cost modelling in tokens: input versus output pricing, cached input
  discounts, and the fact that output tokens usually dominate cost while
  input tokens dominate latency-to-first-token
- Latency decomposition: time to first token (prefill, compute-bound, scales
  with prompt length) versus time per output token (decode, memory-bound,
  roughly constant)
- Routing: send easy traffic to a small model and hard traffic to a large
  one, with a classifier or a confidence signal
- Multimodal capability, and that a vision model's text performance is not
  the same as its base model's
:::

:::checklist AWARENESS
- Reasoning models and test-time compute: spending more tokens at inference
  to improve accuracy, and the fact that this is now a tunable rather than a
  fixed property
- Long-context architectures: sliding-window and sparse attention, and the
  serving consequences
- Model cards, evaluation claims and how to read a benchmark table
  sceptically
:::

## The standard failure modes

| Failure | Cause | Fixable by prompting? |
|---|---|---|
| Confident fabrication | no grounding, no incentive to abstain | Partly: give a "not in the context" option and require citation |
| Ignores part of a long context | attention dilution, lost-in-the-middle | Partly: shorten, reorder, chunk and iterate |
| Format drift over a long output | no constraint | No --- constrain decoding |
| Inconsistent across runs | sampling | Set temperature 0 *and* accept residual variation |
| Fails at counting or character edits | tokenisation | No --- give it a tool |
| Sycophancy: agrees with a wrong premise | post-training incentives | Partly: ask it to evaluate the premise first |
| Degrades on long multi-turn chats | context growth, contradictory history | Summarise and externalise memory |
| Prompt injection from retrieved content | no trust boundary | No --- this is an architecture problem, Chapter 19 |

@tbl: Failure modes and the honest assessment of whether better prompting fixes them. Four of the eight need an architectural change, which is the point.

:::insight The mental model that helps most
Treat the model as a very capable, very literal contractor with no memory
between jobs, who will confidently do the wrong thing rather than ask a
question, and who reads the middle of a long brief less carefully than the
ends. Every effective prompting technique is a consequence of that model:
be explicit, put the important thing where it will be read, give it
permission to decline, and check its work.
:::

## How to tell you have it

:::practice The task
Build an extraction service: unstructured documents in, a strict JSON schema
out, with 95%+ schema validity and a measured field-level accuracy.
1. Establish a baseline with a plain prompt and measure it.
2. Add schema-constrained decoding and measure the change in validity and in
   accuracy --- they can move in opposite directions.
3. Measure characters-per-token on your actual documents and compute cost per
   thousand documents for three models.
4. Measure time-to-first-token and time-per-output-token separately.
5. Add a routing rule sending short easy documents to a small model, and
   report the cost saving and the accuracy cost.
:::

:::pitfall Prompt engineering without measurement
The dominant failure in this area is iterating on prompts by reading outputs
and forming an impression. Impressions cannot detect a 3% regression, cannot
be compared across people, and cannot be defended in a review. Build the
evaluation harness (Chapter 15) before the third prompt revision, not after
the thirtieth.
:::

:::note Time to competence
**3--4 weeks** for ESSENTIAL if you are building daily. The economics and
latency material is often skipped and is what makes the difference between a
demo and a service.
:::

:::recap
- Tokenisation determines cost, multilingual capability and the tasks the
  model cannot do; measure characters-per-token on your own data.
- Context is a budget with an explicit drop policy; position matters because
  the middle is read less carefully.
- Choose sampling parameters deliberately; beam search is wrong for
  open-ended generation; temperature 0 is not truly deterministic.
- Constrain format, not content; a forced schema can turn an honest refusal
  into a confident error.
- Design tools for the model: few, unambiguous, with recoverable errors. MCP
  is the emerging cross-vendor standard.
- Half the standard failure modes are architectural, not prompt-fixable.
:::
