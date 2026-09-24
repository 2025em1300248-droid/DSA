# A Problem-Solving Framework
@short: Problem Solving
@subtitle: What to do in the ninety seconds after you read a problem
@tier: practice
@prereq: Parts I--VIII
@blurb: Knowing algorithms and being able to solve problems are different skills, and the second one is a procedure rather than a talent. This chapter gives you that procedure, the questions that turn a vague problem into a precise one, the signals that point to a structure, and the debugging discipline that makes your answer actually correct.
@objectives:
- Apply a five-step procedure to any unfamiliar problem
- Ask the clarifying questions that determine the whole solution
- Move systematically from a brute force to an optimal solution
- Recognise the signals that point to a particular data structure
- Verify a solution before running it, and debug it when it fails
- Communicate a solution the way a senior engineer does

## The procedure

@fig: solving_flow | 136 | The loop. Most people skip to step 5, produce something half-remembered, and get stuck. The first three steps take four minutes and make the rest tractable.

### Step 1: restate the problem

Write down, in your own words: what the input is (types, ranges, whether it
is sorted, whether values are distinct), what the output is (a value, an
index, all solutions, any solution), and what constraints apply
($n \le 10^5$ tells you $O(n \log n)$; $n \le 20$ tells you $2^n$ is fine).

:::checklist Questions that change the answer
- What is the size of $n$? And of the values?
- Is the input sorted? Can I sort it, or is order meaningful?
- Are there duplicates? Negative numbers? Zeros? Empty input?
- Am I optimising time or memory? Is there a latency bound?
- Can I modify the input in place?
- Is this a one-off query or will there be many? (Decides whether to build
  an index.)
- Does the data change between queries? (Decides static versus dynamic
  structure.)
- Does the answer need to be exact? (Decides whether a sketch is allowed.)
:::

The last three are the ones that distinguish a systems answer from an
exercise answer, and they are the ones interviewers at good companies are
actually listening for.

### Step 2: work an example by hand

Take a small instance --- five or six elements --- and solve it on paper. Then
take a slightly awkward one: empty, single element, all equal, already
sorted, reverse sorted.

This does three things at once. It forces you to understand the problem. It
usually reveals the structure of the answer. And it gives you your first
test case.

### Step 3: state the brute force

Say out loud what the exhaustive solution is and what it costs. "Try every
pair: $O(n^2)$." This is never wasted:

- It proves the problem is solvable and establishes correctness.
- It gives you something to test the fast version against.
- It exposes the waste that the fast version will eliminate.
- If you run out of time, you have a working answer.

### Step 4: find the waste

This is the creative step, and it has only a few shapes.

| What the brute force does | The waste | The fix |
|---|---|---|
| Recomputes the same subproblem | repeated work | memoisation / DP (Ch 18) |
| Rescans a prefix or window | repeated aggregation | prefix sums, sliding window (Ch 11) |
| Searches an unordered set | no structure to exploit | sort, then binary search (Ch 9, 10) |
| Searches a sorted set linearly | ignores order | binary search (Ch 10) |
| Keeps everything to find the best few | excess state | heap (Ch 13) |
| Re-derives reachability | repeated traversal | union--find or precomputed components (Ch 15) |
| Compares all pairs | most pairs are irrelevant | hashing, LSH, spatial index (Ch 7, 29, 33) |
| Explores doomed branches | hopeless subtrees | pruning, branch and bound (Ch 20) |
| Stores exact counts of everything | more precision than needed | sketch (Ch 28) |

@tbl: The nine sources of waste. Nearly every optimisation in this book is one of these rows.

### Step 5: choose the structure

@fig: pattern_triggers | 238 | The phrase-to-structure lookup. It is not a substitute for understanding, but it is a fast way to generate candidates to evaluate.

Once you know the waste, the structure follows: something that makes the
repeated operation cheap. Write the cost of the new solution *before* coding
it, and check it against the constraints. If the new cost still does not fit,
you have not found the real waste --- go back to step 4.

## Signals and what they mean

| Signal | Likely approach |
|---|---|
| $n \le 20$ | exponential is fine: bitmask DP, backtracking |
| $n \le 100$ | $O(n^3)$: Floyd--Warshall, interval DP, matrix chain |
| $n \le 5000$ | $O(n^2)$: pairwise DP, simple graph algorithms |
| $n \le 10^6$ | $O(n \log n)$: sort, heap, binary search, divide and conquer |
| $n \le 10^8$ | $O(n)$: one pass, hashing, two pointers, counting sort |
| $n > 10^9$ | sublinear or streaming: sketches, sampling, external memory |
| "$k$-th" or "top $k$" | heap or quickselect |
| "shortest / cheapest" | BFS, Dijkstra, DP |
| "how many ways" | DP, combinatorics |
| "can it be done in $X$?" | binary search over the answer, greedy check |
| "maximum / minimum such that" | binary search over the answer |
| "next greater / previous smaller" | monotonic stack |
| "in place, $O(1)$ memory" | two pointers, cyclic sort, bit tricks |
| "stream, cannot store it" | reservoir, sketch, one-pass statistic |

@tbl: Constraint and phrasing signals. The first block is the most useful: the bound on $n$ tells you the complexity class you are allowed, which narrows the technique before you have thought about the problem at all.

## Verification before execution

Running the code is the *last* check, not the first.

:::checklist Before you run it
1. **Trace your own example.** Step through the code on the instance from
   step 2. Most bugs surface here.
2. **Check the boundaries.** Empty, one element, two elements, all equal,
   maximum size. Off-by-one at both ends of every loop and slice.
3. **Check the invariant.** Every loop has one: "after iteration $i$, `dp[j]`
   holds …". State it and check it is preserved.
4. **Check integer and floating-point issues.** Overflow (in typed
   languages), division by zero, comparing floats for equality, and
   accumulating error in a long sum.
5. **Check the complexity you claimed.** Count the loops again. Look for a
   hidden $O(n)$ operation inside an $O(n)$ loop (`in` on a list, string
   concatenation, `insert(0, x)`).
:::

When it does fail, debug by **bisection, not by staring**: find the smallest
failing input (shrink it mechanically), then print the state at the midpoint
of the computation and decide which half is wrong. A property-based test that
compares against your brute force on random small inputs will find the bug in
seconds, and you already wrote the brute force in step 3.

```python title="The test harness worth writing every time"
import random

def test_against_brute(fast, brute, gen, trials=2000):
    for _ in range(trials):
        case = gen()
        got, want = fast(*case), brute(*case)
        if got != want:
            print("MISMATCH on", case, "got", got, "want", want)
            return case                     # return it for shrinking
    print("ok:", trials, "random cases agree")
    return None

gen = lambda: ([random.randint(-5, 5) for _ in range(random.randint(0, 8))],)
```

Small random inputs with a small value range --- `-5..5`, length `0..8` ---
find far more bugs than large ones, because they produce duplicates,
negatives, empties and ties, which is where the bugs live.

## Communicating a solution

The difference between a correct answer and a good one is largely how it is
presented.

1. **Restate the problem** to confirm the interpretation. Thirty seconds, and
   it has saved entire interviews.
2. **State the approach before coding.** "I will sort by finish time, then
   greedily take non-overlapping intervals; that is $O(n \log n)$ and optimal
   by an exchange argument."
3. **State the complexity up front**, in time *and* space.
4. **Write clean code**: named variables, one idea per line, no cleverness
   that needs a comment to justify.
5. **Test it out loud** on your example from step 2.
6. **Name the tradeoffs you did not take.** "A hash map would be $O(1)$
   lookup but 40 bytes per entry; at 200 million keys I would use a sorted
   array and `searchsorted` instead."

Point 6 is the one that distinguishes a senior engineer. It shows you chose
rather than defaulted.

:::ml How this applies at work, not just in interviews
The same five steps, with different emphasis. Step 1 becomes *measure*: what
is actually slow, at what $n$, and what is the budget? Step 3 becomes the
baseline you must beat, and you should keep it as a correctness oracle. Step
4 becomes profiling rather than reasoning --- the waste is often not where you
think. And step 6 becomes the design document: the alternatives considered
and why they were rejected, which is what makes a decision reviewable a year
later.
:::

:::exercise
1. Take any problem you have solved recently and write out all five steps
   retrospectively. Which one did you skip?
2. For each row of the constraint table, find a problem from Chapters 45--46
   that matches it.
3. Write a brute-force and an optimal solution to "longest substring without
   repeating characters" and run the test harness above on 5,000 random
   inputs.
4. Take a problem you have solved and list three clarifying questions whose
   answers would change your solution.
5. Deliberately introduce an off-by-one error in a binary search and find it
   using only the shrinking procedure. Time yourself.
6. Write the invariant for each loop in your last non-trivial function. If
   you cannot, that is where your next bug will be.
:::

:::recap
- Restate, work an example, state the brute force, find the waste, choose the
  structure. The first three steps take four minutes and make the rest
  tractable.
- The clarifying questions that matter most are about scale, mutability,
  query count and required exactness.
- The brute force is never wasted: it proves correctness, exposes the waste,
  and becomes your test oracle.
- Nearly every optimisation removes one of nine kinds of waste; find the
  waste and the structure follows.
- The bound on $n$ tells you the complexity class you are allowed before you
  have thought about the problem.
- Verify by tracing, boundaries, invariants and a recount of the complexity;
  debug by shrinking and bisection, not by staring.
- Communicate by stating the approach and complexity first, and by naming
  the tradeoffs you did not take.
:::
