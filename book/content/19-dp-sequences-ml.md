# Dynamic Programming II: Sequence Algorithms in Machine Learning
@short: DP on Sequences
@subtitle: Edit distance, DTW, Viterbi and CTC are one algorithm in four costumes
@tier: advanced
@prereq: Chapter 18
@blurb: Four algorithms that look unrelated --- spell-check distance, time-series alignment, hidden Markov decoding and the loss function of a speech model --- are the same dynamic program with different semirings and different allowed moves. Seeing that unity is worth more than learning them separately, and this chapter builds all four from the same template.
@objectives:
- Implement edit distance with traceback and its linear-memory variant
- Implement dynamic time warping with a band constraint
- Implement the Viterbi algorithm and see why it is edit distance in log-space
- Understand the CTC forward--backward algorithm and what it sums over
- Recognise the max-plus and sum-product structure shared by all of them
- Apply these to real tasks: WER, alignment, sequence labelling, forced alignment

## One template, four algorithms

Every algorithm in this chapter fills a table indexed by a position in each
of two sequences (or by time and state), where

$$dp[i][j] = \bigoplus_{\text{moves } m} \Big( dp[\text{prev}(i,j,m)] \otimes \text{cost}(i,j,m) \Big)$$

The four differ only in three choices: the set of allowed moves, the
combining operator $\oplus$ (min, max, or sum), and the accumulating operator
$\otimes$ (plus, or multiply).

@cols: 18,8,16,28,26
| Algorithm | $\oplus$ | $\otimes$ | Moves | Answers |
|---|---|---|---|---|
| Edit distance | min | $+$ | insert, delete, substitute | fewest edits |
| DTW | min | $+$ | right, down, diagonal (no skips) | best alignment cost |
| Viterbi | max | $\times$ (or max, $+$ in log) | state transitions | most likely path |
| Forward algorithm | $\sum$ | $\times$ | state transitions | total probability |
| CTC loss | $\sum$ | $\times$ | stay, advance, skip blank | probability of a label sequence |

@tbl: The same recursion with different algebra. In algebraic terms each row is the same computation over a different *semiring*; min-plus gives shortest paths, max-times gives most-likely paths, sum-times gives total probability.

:::insight Why this matters practically
Once you see the template, implementing a new variant is a matter of
changing two operators and the move set --- not designing a new algorithm.
It also tells you immediately what the complexity is ($\Theta(\text{states} \times
\text{moves})$), how to band or prune it, and how to make it numerically
stable (work in log-space, use `logsumexp` for the sum case).
:::

## Edit distance

:::definition Levenshtein distance
The minimum number of single-character insertions, deletions and
substitutions that transform string $A$ into string $B$.
:::

**State.** `dp[i][j]` = the edit distance between `A[:i]` and `B[:j]`.

**Recurrence.**
$$dp[i][j] = \min\begin{cases} dp[i-1][j] + 1 & \text{delete } A_i \\ dp[i][j-1] + 1 & \text{insert } B_j \\ dp[i-1][j-1] + [A_i \ne B_j] & \text{match or substitute} \end{cases}$$

**Base cases.** `dp[i][0] = i`, `dp[0][j] = j`.

@fig: edit_distance | 172 | The edit-distance table for KITTEN and SITTING. Each cell is the minimum over three neighbours; the highlighted cells are the traceback path, which is the edit script itself.

```python title="Edit distance with traceback"
def edit_distance(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = dp[i - 1][j - 1] + (a[i - 1] != b[j - 1])
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, sub)

    ops, i, j = [], n, m                       # traceback from the corner
    while i or j:
        if i and j and dp[i][j] == dp[i-1][j-1] + (a[i-1] != b[j-1]):
            ops.append(("match" if a[i-1] == b[j-1] else "sub", a[i-1], b[j-1]))
            i, j = i - 1, j - 1
        elif i and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(("del", a[i - 1], None)); i -= 1
        else:
            ops.append(("ins", None, b[j - 1])); j -= 1
    return dp[n][m], ops[::-1]
```

$\Theta(nm)$ time and memory. The memory drops to $\Theta(\min(n,m))$ with a
rolling row --- but then the traceback is gone, which is where Hirschberg's
algorithm (Chapter 18) earns its keep.

:::ml Word error rate is edit distance
WER, the standard metric for speech recognition, is Levenshtein distance
between the reference and hypothesis *word* sequences, divided by the
reference length. The traceback gives the per-word alignment, which is what
lets you report substitutions, insertions and deletions separately and
attribute errors to specific words. The same computation with weights tuned
per operation gives the alignment used for translation post-editing effort.
:::

:::pitfall Edit distance at scale is quadratic and nobody can fix it
Under the Strong Exponential Time Hypothesis, edit distance cannot be
computed in $\Theta(n^{2-\varepsilon})$. So for long sequences you must
approximate: band the DP (only compute cells within $|i - j| \le w$, giving
$\Theta(nw)$ and an exact answer whenever the true distance is $\le w$),
filter with a cheap bound first (length difference, or a $q$-gram count
bound), or use bit-parallel algorithms (Myers' algorithm computes exact
Levenshtein in $\Theta(nm/64)$ using bitwise operations on machine words ---
a 64x constant-factor win that is very much worth having).
:::

## Dynamic time warping

DTW aligns two sequences that have the same shape but different pacing: two
utterances of the same word, two sensor traces of the same gesture, two
time series with different sampling.

@fig: dtw_path | 150 | DTW's cost matrix and the warping path. Only monotone moves are allowed, which preserves ordering; the path may stretch one series against the other.

```python title="DTW with a Sakoe-Chiba band"
import numpy as np

def dtw(a, b, band=None):
    n, m = len(a), len(b)
    band = band if band is not None else max(n, m)
    INF = float("inf")
    prev = np.full(m + 1, INF)
    prev[0] = 0.0
    for i in range(1, n + 1):
        cur = np.full(m + 1, INF)
        lo = max(1, i - band)
        hi = min(m, i + band)
        for j in range(lo, hi + 1):
            cost = abs(a[i - 1] - b[j - 1])
            cur[j] = cost + min(prev[j],        # insert in b
                                cur[j - 1],     # insert in a
                                prev[j - 1])    # align
        prev = cur
    return prev[m]
```

The band is not just an optimisation. Unconstrained DTW can produce
pathological alignments that map one point of $A$ onto half of $B$; the
Sakoe--Chiba band (allow $|i - j| \le w$) or the Itakura parallelogram
restricts the warp to something physically plausible and reduces the cost to
$\Theta(nw)$.

:::ml DTW in practice
DTW is the classical distance for time-series $k$-NN classification, and it
still competes with deep models on small datasets. It is used for gesture
recognition, for aligning sensor streams with different clocks, and ---
importantly --- as `soft-DTW`, a differentiable relaxation that replaces
`min` with `softmin` so it can be used as a training loss for sequence
prediction. That relaxation is a change of the $\oplus$ operator in this
chapter's template, nothing more.
:::

## Viterbi: the most likely state sequence

A hidden Markov model has states $S$, transition probabilities $A_{ij}$,
emission probabilities $B_j(o)$ and an observation sequence $o_1 \ldots o_T$.
The Viterbi algorithm finds the state sequence maximising the joint
probability.

@fig: viterbi_lattice | 138 | The Viterbi lattice. At every time step and every state, keep only the best path into that state --- $\Theta(T S^2)$ instead of $S^T$ paths.

**State.** $\delta_t(j)$ = the probability of the most likely path that ends
in state $j$ at time $t$.

**Recurrence.** $\delta_t(j) = \max_i \big( \delta_{t-1}(i) \cdot A_{ij} \big)
\cdot B_j(o_t)$.

```python title="Viterbi in log-space"
import numpy as np

def viterbi(log_A, log_B, log_pi, obs):
    """log_A: (S,S)  log_B: (S,V)  log_pi: (S,)  obs: (T,) ints"""
    T, S = len(obs), log_A.shape[0]
    delta = log_pi + log_B[:, obs[0]]
    back = np.zeros((T, S), dtype=np.int32)
    for t in range(1, T):
        scores = delta[:, None] + log_A          # (S_prev, S_next)
        back[t] = np.argmax(scores, axis=0)
        delta = scores.max(axis=0) + log_B[:, obs[t]]
    path = np.zeros(T, dtype=np.int32)
    path[-1] = int(np.argmax(delta))
    for t in range(T - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path, float(delta.max())
```

Two things to note. Work in **log-space**: multiplying $T$ probabilities
underflows float64 after a few hundred steps. And the inner step is a matrix
operation --- `delta[:, None] + log_A` then a max --- so it vectorises, which
is why Viterbi over a 100-state model on a million frames is fast.

Replacing `max` with `logsumexp` turns Viterbi into the **forward
algorithm**, which computes the total probability of the observations rather
than the best path. Two operators, two algorithms.

:::ml Where Viterbi runs in modern systems
Part-of-speech tagging and named-entity recognition with a CRF output layer
use Viterbi for decoding: the neural network produces per-token emission
scores, the CRF adds learned transition scores, and Viterbi finds the best
tag sequence --- which is how BIO tagging schemes are kept consistent.
SentencePiece's Unigram tokenizer runs Viterbi over a segmentation lattice.
Forced alignment in speech --- mapping a known transcript onto audio
timestamps --- is Viterbi over an HMM built from the transcript.
:::

## CTC: summing over all alignments

Connectionist Temporal Classification solves a problem that has no
supervised alignment: the audio has $T$ frames, the transcript has $S$
characters, $T \gg S$, and nobody has labelled which frame corresponds to
which character.

@fig: ctc_lattice | 130 | The CTC lattice for the target "cat". Blanks are inserted between and around the labels; every monotone path through the lattice collapses to the target, and the loss is the total probability of all of them.

The construction: insert a blank symbol $\epsilon$ between every pair of
labels and at both ends, giving an extended sequence of length $2S + 1$.
A path through the lattice is valid if it moves only forward, may stay in a
state, and may skip a blank when moving between two *different* labels. The
collapse rule --- merge repeats, then delete blanks --- maps every valid path
to the target.

The CTC loss is $-\log$ of the *sum* over all valid paths, computed by the
forward algorithm in $\Theta(T \cdot S)$:

$$\alpha_t(s) = \big( \alpha_{t-1}(s) + \alpha_{t-1}(s-1) + [\text{skip allowed}] \, \alpha_{t-1}(s-2) \big) \cdot y_t^{(s)}$$

```python title="CTC forward pass in log-space (the core recursion)"
import numpy as np

def logsumexp(*xs):
    m = max(xs)
    return m + np.log(sum(np.exp(x - m) for x in xs)) if m > -np.inf else -np.inf

def ctc_log_prob(log_probs, target, blank=0):
    """log_probs: (T, V) log-softmax outputs. target: list of label ids."""
    ext = [blank]
    for lab in target:
        ext += [lab, blank]                       # eps l1 eps l2 eps ... eps
    S, T = len(ext), log_probs.shape[0]
    NEG = -np.inf
    a = np.full(S, NEG)
    a[0] = log_probs[0, ext[0]]
    if S > 1:
        a[1] = log_probs[0, ext[1]]
    for t in range(1, T):
        nxt = np.full(S, NEG)
        for s in range(S):
            best = a[s]
            if s > 0:
                best = logsumexp(best, a[s - 1])
            if s > 1 and ext[s] != blank and ext[s] != ext[s - 2]:
                best = logsumexp(best, a[s - 2])   # skip the blank
            nxt[s] = best + log_probs[t, ext[s]]
        a = nxt
    return logsumexp(a[S - 1], a[S - 2] if S > 1 else NEG)
```

The backward pass mirrors it, and the gradient with respect to the network
outputs is $y_t^{(k)} - \frac{1}{p(\ell)}\sum_{s: \text{ext}[s]=k} \alpha_t(s)\beta_t(s)$
--- the difference between what the network predicted and the
alignment-marginalised target. This is the same forward--backward structure
as the Baum--Welch algorithm for HMMs, and the same structure as
backpropagation itself (Chapter 24).

:::insight Why sum-over-alignments rather than best alignment
Training against the single best alignment (Viterbi training) is simpler and
works less well: early in training the best alignment is essentially random,
and committing to it creates a feedback loop. Summing over all alignments
gives gradient signal to every plausible alignment weighted by its
probability, which is much better behaved. The same argument recurs
throughout ML --- marginalise when you can, maximise when you must.
:::

## The complexity summary

| Algorithm | Time | Memory | Banded / pruned |
|---|---|---|---|
| Edit distance | $\Theta(nm)$ | $\Theta(\min(n,m))$ rolling | $\Theta(nw)$ banded; $\Theta(nm/64)$ bit-parallel |
| LCS | $\Theta(nm)$ | $\Theta(\min(n,m))$ | Hunt--Szymanski $\Theta((r + n)\log n)$ |
| DTW | $\Theta(nm)$ | $\Theta(m)$ | $\Theta(nw)$ with a band; FastDTW $\Theta(n)$ approximate |
| Viterbi | $\Theta(T S^2)$ | $\Theta(TS)$ for traceback | beam-pruned $\Theta(T b S)$ |
| Forward--backward | $\Theta(T S^2)$ | $\Theta(TS)$ | same |
| CTC | $\Theta(T S)$ | $\Theta(TS)$ | prefix beam search for decoding |

@tbl: All of these are quadratic in the natural parameters, and all are banded or beam-pruned in production. Pruning is not a hack; it is the standard practice.

:::exercise
1. Modify `edit_distance` to support weighted operations (substitution cost
   depending on the character pair, as in a keyboard-distance model).
2. Implement the banded edit distance and verify that it returns the exact
   answer whenever the true distance is within the band, and a valid upper
   bound otherwise.
3. Implement Hirschberg's algorithm for LCS and verify that its memory is
   $\Theta(\min(n,m))$ while its output matches the quadratic version.
4. Implement DTW with and without a band on two 10,000-point series. Compare
   time and the resulting alignment. Construct a case where the unbanded
   alignment is pathological.
5. Implement the forward algorithm by changing one operator in `viterbi`,
   and check that its result equals the log-sum over all paths on a tiny
   model by brute force.
6. Verify `ctc_log_prob` against brute-force enumeration of all valid paths
   for $T = 6$ and target "ab".
7. Implement CTC greedy decoding (argmax per frame, then collapse) and CTC
   prefix beam search. Compare their outputs on a synthetic model.
8. Express the LCS recurrence in the semiring notation at the top of this
   chapter, naming $\oplus$, $\otimes$ and the move set.
:::

:::recap
- Edit distance, DTW, Viterbi, the forward algorithm and CTC are the same
  dynamic program with different semirings and move sets.
- Edit distance is $\Theta(nm)$ and provably cannot be much better; band it,
  filter first, or use bit-parallel Myers for a 64x constant.
- DTW aligns sequences with different pacing; a band is required for sane
  alignments as well as for speed. Soft-DTW makes it differentiable by
  replacing min with softmin.
- Viterbi keeps the best path into each state: $\Theta(TS^2)$. Work in
  log-space, and vectorise the inner step. Replacing max with logsumexp
  gives the forward algorithm.
- CTC sums over all monotone alignments of a blank-extended label sequence,
  which is why it trains without frame-level labels. Its gradient is the
  difference between prediction and alignment-marginalised target.
- Marginalise over alignments rather than committing to the best one when
  you can; it is better behaved during training.
:::
