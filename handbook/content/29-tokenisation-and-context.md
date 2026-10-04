# Tokenisation, Context and Cost
@short: Tokenisation
@subtitle: The unit of everything, and the bill it generates
@tier: core
@prereq: Chapter 25
@blurb: Tokens are the atoms of a language model: what it reads, what it writes, what you pay for, and what limits how much it can see. Almost every surprising LLM behaviour --- arithmetic errors, bad character counting, inflated bills on non-English text --- traces back to tokenisation. This chapter covers how it works and what follows from it.
@objectives:
- Explain BPE and implement a trainer
- Predict token counts and costs before running anything
- Diagnose the failure modes tokenisation causes
- Reason about context windows and what actually fits
- Budget a context window deliberately rather than by accident

## Byte-pair encoding

BPE starts from bytes and repeatedly merges the most frequent adjacent pair,
building a vocabulary of subword units. Frequent words become single tokens;
rare words decompose into pieces; nothing is ever out-of-vocabulary because
the base alphabet is the 256 bytes.

```python title="A complete BPE trainer"
from collections import Counter

def train_bpe(corpus: bytes, vocab_size: int = 1000):
    ids = list(corpus)                                  # start from raw bytes
    merges, next_id = {}, 256

    while next_id < vocab_size:
        pairs = Counter(zip(ids, ids[1:]))
        if not pairs:
            break
        best, count = pairs.most_common(1)[0]
        if count < 2:
            break
        merges[best] = next_id

        out, i = [], 0                                  # apply the merge
        while i < len(ids):
            if i + 1 < len(ids) and (ids[i], ids[i + 1]) == best:
                out.append(next_id); i += 2
            else:
                out.append(ids[i]); i += 1
        ids = out
        next_id += 1

    return merges

def encode(text: str, merges: dict) -> list[int]:
    ids = list(text.encode("utf-8"))
    for pair, new_id in merges.items():                 # insertion order = rank
        out, i = [], 0
        while i < len(ids):
            if i + 1 < len(ids) and (ids[i], ids[i + 1]) == pair:
                out.append(new_id); i += 2
            else:
                out.append(ids[i]); i += 1
        ids = out
    return ids
```

Real implementations differ in three ways: they pre-split on a regex so merges
never cross word or whitespace boundaries, they apply merges by rank using a
priority queue rather than looping over all merges, and they add special
tokens outside the merge process.

@fig: tokenisation | 158 | The same content, tokenised. English prose is about 4 characters per token; code is denser in tokens because of punctuation and indentation; languages not well represented in the training corpus can cost several times more tokens for the same meaning --- and you pay per token.

## What this costs you

| Content | Chars/token | Tokens per 1000 chars |
|---|---|---|
| English prose | ~4.0 | 250 |
| Python code | ~3.0 | 330 |
| JSON with long keys | ~2.5 | 400 |
| German, Spanish, French | ~3.0 | 330 |
| Chinese, Japanese | ~1.5 | 660 |
| Hindi, Thai, Burmese | ~1.0 | 1000+ |
| Base64 / random hex | ~1.5 | 660 |
| UUIDs | ~1.0 | 1000 |

@tbl: Measured with a modern ~100k-vocabulary tokeniser; numbers vary by a few tens of percent between tokenisers. Note the equity consequence: the same document costs four times as much to process in Hindi as in English, and consumes four times the context window.

```python title="Always measure; never estimate from character count"
import tiktoken
enc = tiktoken.get_encoding("o200k_base")

def cost_estimate(text, in_price_per_m, out_price_per_m, expected_out=500):
    n_in = len(enc.encode(text))
    return (n_in * in_price_per_m + expected_out * out_price_per_m) / 1e6

# Before shipping ANY pipeline:
#   tokens per request x requests per day x price = the monthly bill.
# This calculation has killed more feature proposals than any evaluation.
```

## The failure modes tokenisation causes

:::pitfall Five behaviours that are tokenisation, not reasoning
**Arithmetic.** "1234 + 5678" may tokenise as `123|4| +| 56|78`. The model
never sees the digits aligned by place value, so multi-digit arithmetic is
genuinely hard for it in a way it is not for you. Newer tokenisers split
digits individually, which measurably improves arithmetic.

**Character counting.** "How many r's in strawberry?" fails because
`straw|berry` contains no character-level information. The model has never
observed the letters as separate units.

**Reversing strings.** Same cause. The model would have to have memorised the
reversal of each token.

**Rhyming and wordplay.** Requires phonetic or character structure that the
token boundary destroys.

**Trailing whitespace.** A prompt ending in a space tokenises differently from
one that does not, because " word" and "word" are different tokens. This
measurably degrades completions. Never end a prompt with a trailing space.
:::

:::insight The general rule
If a task requires manipulating text *below* the token level, the model is
working with the wrong primitive. Either give it a tool (a calculator, a
Python interpreter, a string function) or restructure the input so the
relevant units are separate tokens --- for example, spacing out digits or
letters. Prompting harder does not fix a representational limitation.
:::

## Context windows

The advertised context length is an upper bound on input plus output, not a
promise of uniform quality across it.

| Concern | Reality |
|---|---|
| Advertised length | input + output combined, not input alone |
| Effective length | quality often degrades well before the limit |
| Cost | linear in input tokens; attention compute is quadratic |
| Latency | prefill time grows with input length |
| Position of information | items in the middle are used least reliably |

@tbl: Five things the context number does not tell you. The last row --- the "lost in the middle" effect --- is robust across models: information at the start and end of a long context is retrieved more reliably than information in the middle.

```python title="A context budget, written down"
BUDGET = {
    "system":            400,     # fixed instructions
    "tools":           1_200,     # tool schemas, if any
    "few_shot":        1_500,     # 3 exemplars
    "retrieved":       8_000,     # 8 chunks x ~1000
    "history":         4_000,     # trimmed conversation
    "user":            1_000,
    "output_reserve":  2_000,     # MUST be reserved, not hoped for
}
assert sum(BUDGET.values()) <= MODEL_CONTEXT
```

:::warning Reserving output space is not optional
If input plus generated output exceeds the window, generation is truncated
mid-sentence --- or the request fails after you have already paid for the
prefill. Compute the reserve explicitly and enforce it before the call,
trimming the most compressible component (usually history, then retrieved
chunks) until it fits.
:::

## Managing a long conversation

| Strategy | Keeps | Loses | Use when |
|---|---|---|---|
| Truncate oldest | recent turns | early context | short tasks |
| Summarise older turns | the gist | detail, exact wording | long assistance |
| Retrieve from history | relevant turns | conversational flow | long-running agents |
| Hierarchical summary | a tree of summaries | fine detail | very long sessions |
| Externalise to a file | everything | nothing, if searchable | agents with tools |

@tbl: Context management strategies. The last is increasingly the right answer: write state to a file or database and let the model re-read what it needs, rather than trying to hold everything in the window.

:::practice The task
(a) Implement the BPE trainer above and train a 1000-token vocabulary on a
corpus of your own; inspect the first fifty merges. (b) Tokenise the same
paragraph in five languages and report the ratio. (c) Compute your
application's monthly token bill from measured counts. (d) Demonstrate three
of the five tokenisation failure modes, then fix each by restructuring the
input or adding a tool. (e) Build the context budget for a real prompt and add
an assertion that enforces it.

**You have this skill when** you can look at a prompt template and state its
token cost and its monthly bill at your expected traffic, before writing any
code.
:::

:::exercise
1. Train BPE on English and on code, and compare the resulting vocabularies.
2. Show that a trailing space changes the tokenisation of the following word,
   and measure the effect on a completion task.
3. † Construct an arithmetic task the model fails, then fix it by spacing the
   digits. Quantify the improvement over 100 problems.
4. Measure tokens per character for ten languages and relate the result to the
   cost of serving each market.
5. Place a fact at the start, middle and end of a 30k-token context and
   measure retrieval accuracy at each position.
6. † Implement hierarchical summarisation for a 200-turn conversation and
   measure information loss with a set of factual questions.
7. Write the budget enforcement code, including the trimming policy, and test
   it against an over-long input.
:::

:::recap
- BPE merges frequent adjacent pairs starting from bytes; nothing is ever
  out-of-vocabulary.
- English is ~4 characters per token; code, JSON and many non-Latin scripts
  are far denser, and you pay per token.
- Arithmetic, character counting, reversal, rhyming and trailing-whitespace
  failures are tokenisation artefacts, not reasoning failures --- fix them
  with tools or restructuring, not prompting.
- The context number is input plus output, quality degrades before the limit,
  and information in the middle is used least reliably.
- Budget the context explicitly, reserve output space, and prefer
  externalising state over stuffing the window.
:::
