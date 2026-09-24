# Decoding Algorithms
@short: Decoding
@subtitle: Greedy, beam, nucleus, speculative and constrained
@tier: expert
@prereq: Chapters 13, 20, 34
@blurb: A language model produces a probability distribution over the next token. Turning a sequence of such distributions into text is a search problem, and the algorithm you choose changes latency, cost, and what the model appears to be capable of. This chapter treats decoding as what it is --- search with a bounded budget --- and covers the algorithms that a serving system actually runs.
@objectives:
- Distinguish the search objective from the sampling objective and know when each is right
- Implement beam search with length normalisation and early stopping
- Implement top-$k$, top-$p$ and min-$p$ sampling efficiently
- Explain speculative decoding and prove that it preserves the output distribution
- Implement constrained decoding with a finite automaton over tokens
- Reason about the cost of each method in tokens, memory and latency

## Decoding is bounded search

At each step the model gives $p(x_t \mid x_{<t})$ over a vocabulary of
$V \approx 10^5$. Generating $T$ tokens means choosing a path through a tree
with $V^T$ leaves. Every decoding algorithm is a policy for exploring a
vanishing fraction of it.

| Algorithm | Explores | Objective | Cost per token |
|---|---|---|---|
| Greedy | 1 path | locally most likely | 1 forward pass |
| Beam search | $b$ paths | approximately most likely sequence | $b$ (batched) |
| Pure sampling | 1 random path | a sample from the model | 1 |
| Top-$k$ / top-$p$ | 1 truncated-random path | a sample from a truncated model | 1 |
| Speculative | 1 path, verified | *identical* to the base method | $\approx 1/\gamma$ |
| Constrained | 1 path in a language | best/sample within a grammar | 1 + mask |

@tbl: Decoding algorithms. Only speculative decoding changes the cost without changing the output distribution; everything else is a different objective.

:::insight Likelihood is not quality
Beam search maximises sequence log-probability, and for open-ended
generation that is the wrong objective: the highest-probability continuation
of almost any prompt is bland, repetitive, and often degenerate. Humans do
not produce maximum-likelihood text --- real text sits in a band of moderate
surprisal. This is why sampling methods dominate for chat and creative
generation, while beam search remains standard for translation, speech
recognition and constrained tasks where a single correct answer exists.
:::

## Beam search

@fig: beam_search | 150 | Beam search with width 2. At each step all $b \times V$ continuations are scored and the best $b$ are kept --- a bounded-width breadth-first search with a priority queue.

```python title="Beam search with length normalisation"
import numpy as np

def beam_search(step_fn, start, eos, beam=4, max_len=64, alpha=0.7):
    """step_fn(tokens) -> log-probability vector over the vocabulary."""
    beams = [(0.0, [start], None)]           # (logprob, tokens, state)
    finished = []
    for _ in range(max_len):
        cands = []
        for score, toks, state in beams:
            logp = step_fn(toks)             # (V,) log-probabilities
            top = np.argpartition(-logp, beam)[:beam]     # theta(V)
            for t in top:
                cands.append((score + float(logp[t]), toks + [int(t)], state))
        cands.sort(key=lambda c: -c[0])
        beams = []
        for score, toks, state in cands[:beam]:
            if toks[-1] == eos:
                lp = ((5 + len(toks)) / 6) ** alpha       # GNMT penalty
                finished.append((score / lp, toks))
            else:
                beams.append((score, toks, state))
        if not beams:
            break
        # early stop: no unfinished beam can beat the best finished one
        if finished and beams[0][0] < max(f[0] for f in finished):
            break
    if not finished:
        finished = [(s, t) for s, t, _ in beams]
    return max(finished)[1]
```

**Why length normalisation.** Log-probabilities are negative, so every extra
token lowers the score and raw beam search is systematically biased toward
short outputs. Dividing by $((5+|y|)/6)^\alpha$ with $\alpha \in [0.6, 1.0]$
is the standard correction.

**Why only top-$b$ per beam.** Expanding all $b \times V$ candidates and
sorting is $\Theta(bV \log(bV))$; since at most $b$ continuations of any one
beam can survive, taking each beam's top $b$ first reduces it to
$\Theta(bV)$ (Chapter 13).

:::pitfall Beam search's failure modes
Larger beams often produce *worse* output --- the "beam search curse". With
$b = 100$ a translation model tends to emit empty or very short strings,
because those genuinely have higher probability under the model. Beam search
also amplifies repetition, since repeated text is high-probability. Standard
patches: length normalisation, coverage penalties, $n$-gram blocking, and
diverse beam search. All of them are admissions that the objective is wrong.
:::

## Sampling: top-$k$, top-$p$, min-$p$

```python title="The three truncation schemes"
import numpy as np

def top_k_filter(logits, k):
    if k <= 0 or k >= len(logits):
        return logits
    kth = np.partition(logits, -k)[-k]                  # theta(V)
    return np.where(logits < kth, -np.inf, logits)

def top_p_filter(logits, p):
    order = np.argsort(-logits)                          # theta(V log V)
    probs = np.exp(logits[order] - logits[order].max())
    probs /= probs.sum()
    cum = np.cumsum(probs)
    cutoff = int(np.searchsorted(cum, p) + 1)            # smallest set >= p
    out = np.full_like(logits, -np.inf)
    out[order[:cutoff]] = logits[order[:cutoff]]
    return out

def min_p_filter(logits, min_p):
    """Keep tokens whose probability is at least min_p * max probability.
    Adapts to the distribution's sharpness, unlike a fixed k or p."""
    m = logits.max()
    thresh = m + np.log(min_p)
    return np.where(logits < thresh, -np.inf, logits)

def sample(logits, temperature=1.0, rng=np.random):
    z = logits / max(temperature, 1e-6)
    g = -np.log(-np.log(rng.random(z.shape) + 1e-20) + 1e-20)   # Gumbel
    return int(np.argmax(z + g))
```

| Method | Truncates to | Adapts to sharpness? | Cost |
|---|---|---|---|
| Temperature | nothing | --- | $\Theta(V)$ |
| Top-$k$ | fixed count | no | $\Theta(V)$ with `partition` |
| Top-$p$ (nucleus) | smallest set with mass $\ge p$ | yes | $\Theta(V \log V)$ sort |
| Min-$p$ | tokens above $p \cdot p_{\max}$ | yes | $\Theta(V)$ |
| Typical / $\eta$ | tokens near the entropy | yes | $\Theta(V \log V)$ |

@tbl: Truncation schemes. Top-$p$ is the default in most APIs; min-$p$ gives similar behaviour at $\Theta(V)$ instead of $\Theta(V \log V)$, which matters when $V = 10^5$ and you decode a thousand tokens per second per stream.

:::perf Decoding overhead is not negligible
At $V = 128{,}000$, a full sort per token costs roughly 2 million
comparisons. Multiply by 100 tokens per second per stream and 64 concurrent
streams and the sampler is consuming real CPU. Production servers keep this
on the GPU (`torch.topk` plus a masked softmax) and prefer $\Theta(V)$
schemes. Repetition penalties, which need a scan over the generated prefix,
are another silent cost --- keep a set of emitted tokens rather than
rescanning.
:::

## Speculative decoding

Generating one token requires reading every model weight from memory
(Chapter 3), so decoding is bandwidth-bound and the GPU's arithmetic units
are nearly idle. Speculative decoding exploits that: use a small draft model
to guess several tokens, then verify them all in *one* forward pass of the
large model.

@fig: speculative_decoding | 155 | Speculative decoding. A cheap draft model proposes $\gamma$ tokens; one parallel pass of the target model scores all of them; a modified rejection-sampling rule accepts a prefix and resamples at the first rejection.

```python title="Speculative decoding, the acceptance rule"
import numpy as np

def speculative_step(target_logprobs, draft_logprobs, draft_tokens, rng):
    """target_logprobs, draft_logprobs: (gamma+1, V) from one parallel pass.
    Returns the accepted tokens. Output distribution == target model's."""
    accepted = []
    for i, t in enumerate(draft_tokens):
        p = np.exp(target_logprobs[i, t])         # target prob of the draft
        q = np.exp(draft_logprobs[i, t])          # draft prob of the draft
        if rng.random() < min(1.0, p / q):
            accepted.append(t)                    # accept
        else:
            resid = np.maximum(np.exp(target_logprobs[i])
                               - np.exp(draft_logprobs[i]), 0.0)
            resid /= resid.sum()                  # the corrected residual
            accepted.append(int(rng.choice(len(resid), p=resid)))
            return accepted                       # stop at first rejection
    bonus = int(np.argmax(target_logprobs[len(draft_tokens)]))
    accepted.append(bonus)                        # free extra token
    return accepted
```

:::math Why the output distribution is exactly preserved
Consider one position with target distribution $p$ and draft $q$. The draft
proposes $x \sim q$; we accept with probability $\min(1, p(x)/q(x))$. The
probability of emitting $x$ by acceptance is
$q(x)\min(1, p(x)/q(x)) = \min(q(x), p(x))$.
The probability of rejecting is $1 - \sum_y \min(q(y), p(y))$, and on
rejection we sample from the normalised residual
$\frac{\max(p - q, 0)}{\sum_y \max(p(y) - q(y), 0)}$, whose normaliser equals
that same rejection probability. So the total probability of emitting $x$ is
$$\min(q(x), p(x)) + \max(p(x) - q(x), 0) = p(x)$$
exactly. The draft model affects *speed only* --- never the distribution.
This is why speculative decoding is safe to enable by default, unlike every
other acceleration in this chapter.
:::

**Expected speedup.** If the per-token acceptance rate is $\alpha$ and the
draft length is $\gamma$, the expected number of tokens per target pass is
$\frac{1 - \alpha^{\gamma+1}}{1 - \alpha}$. With $\alpha = 0.8$ and
$\gamma = 4$ that is 3.36 tokens per target pass; net speedup 2--3x once the
draft model's own cost is included. Variants replace the draft model with
$n$-gram lookup from the prompt (very cheap, high acceptance on
summarisation and code editing), with extra prediction heads (Medusa), or
with a tree of candidates verified at once.

## Constrained decoding

To guarantee valid JSON, a regular expression, or a value from a fixed set,
compile the constraint into a finite automaton over *tokens* and mask
everything that would leave its valid transitions.

```python title="Grammar-constrained decoding via token masks"
class FSAConstraint:
    def __init__(self, transitions, start, accepting, vocab_size):
        self.transitions = transitions          # state -> {token: next_state}
        self.state = start
        self.accepting = accepting
        self.V = vocab_size

    def mask(self):
        import numpy as np
        m = np.full(self.V, -np.inf, dtype=np.float32)
        allowed = self.transitions.get(self.state, {})
        if allowed:
            m[list(allowed.keys())] = 0.0
        return m                                 # add to logits before softmax

    def advance(self, token):
        self.state = self.transitions[self.state][token]

    def can_stop(self):
        return self.state in self.accepting
```

Two subtleties decide whether this works in practice.

**Token--character mismatch.** The grammar is over characters; the model
emits tokens, and a token may span a grammar boundary. The automaton must
therefore be built over *token* transitions, which means precomputing, for
each state, the set of tokens whose character expansion keeps the automaton
alive. This is a product construction between the tokenizer's trie
(Chapter 14) and the grammar's automaton, and it is precomputed once per
grammar.

**Dead ends.** If a valid prefix has no valid continuation, the decoder is
stuck. The automaton must be trimmed to its *co-accessible* states --- those
from which an accepting state is reachable --- before use. That trimming is a
reverse reachability computation on the automaton graph (Chapter 22).

:::ml What constrained decoding costs and does not cost
The mask is precomputed per state, so the runtime cost is one lookup and one
vector add per token: negligible. What it *does* cost is distributional
distortion --- renormalising over a subset changes the model's probabilities,
and the constrained output may be far less likely than the model's natural
output. If a model wants to say "I don't know" and your schema forbids it,
you get a confident wrong answer instead. Constrain the *format*, and be
careful about constraining the *content*.
:::

:::exercise
1. Implement beam search and show that increasing $b$ from 1 to 50 on a
   translation model first improves and then degrades quality. Plot it.
2. Show that without length normalisation, beam search's output length
   shrinks as $b$ grows. Quantify the effect.
3. Implement top-$k$, top-$p$ and min-$p$, and compare the number of
   surviving tokens per step on peaked versus flat distributions.
4. Measure the cost of the full sort in top-$p$ at $V = 128{,}000$ and
   compare to min-$p$. Extrapolate to 1000 tokens per second.
5. Implement the speculative acceptance rule and verify empirically that the
   output distribution matches direct sampling from the target, using a
   chi-squared test over a small vocabulary.
6. Derive the expected tokens per target pass and verify it by simulation for
   $\alpha \in \{0.5, 0.7, 0.9\}$ and $\gamma \in \{2, 4, 8\}$. Find the
   optimal $\gamma$ given a draft-to-target cost ratio of 0.1.
7. Implement $n$-gram (prompt-lookup) speculative decoding and measure its
   acceptance rate on a summarisation task versus a free-form chat task.
8. Build a token-level automaton for a small JSON schema and show that
   trimming non-co-accessible states is necessary by constructing a
   dead-end case.
:::

:::recap
- Decoding is bounded search over a $V^T$ tree; each algorithm is a policy
  for exploring a tiny fraction of it.
- Beam search approximates the most likely sequence and needs length
  normalisation; larger beams can make open-ended output worse, because
  likelihood is the wrong objective there.
- Top-$k$, top-$p$ and min-$p$ truncate before sampling; min-$p$ adapts to
  sharpness at $\Theta(V)$ rather than $\Theta(V \log V)$.
- Sampling via Gumbel-max avoids normalisation and vectorises.
- Speculative decoding provably preserves the target distribution, because
  the accept/residual rule sums to $p(x)$ exactly; it converts
  bandwidth-bound decoding into compute-bound verification.
- Constrained decoding masks logits using a token-level automaton built as a
  product of the tokenizer trie and the grammar; trim to co-accessible
  states or the decoder can get stuck.
:::
