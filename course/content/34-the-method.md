# How to Solve Any DSA Problem
@short: The Method
@subtitle: A seventeen-step procedure for problems you have never seen
@tier: core
@prereq: Parts III and VII
@blurb: The goal of this book is not that you can solve the problems in it — it is that you can solve the ones that are not. This chapter gives a repeatable procedure, applies it end to end to a problem you have not been shown, and explains what each step is actually protecting you from. Follow it mechanically at first; it becomes instinct faster than you expect.
@objectives:
- Apply a seventeen-step method to an unfamiliar problem
- Restate a problem precisely, and ask the questions worth asking
- Reach a working brute force before attempting to be clever
- Find the bottleneck, and match it to a pattern
- Trace, test and cost your solution before declaring it finished
- Know what each step prevents, so you can skip steps knowingly rather than by accident

## The method

@fig: method_flow | 200 | The seventeen steps in four phases. Most candidates begin at step 12 and fail at step 14. The first four steps take two minutes and prevent most of the ways an interview goes wrong.

:::checklist The seventeen steps
**Understand (steps 1–3)**
1. Restate the problem in your own words, in one plain sentence.
2. Say exactly what the input is and what the output is, including types and the
   awkward values each may take.
3. Work one tiny example by hand, on paper. Three to five elements, never more.

**Reach something that works (steps 4–7)**
4. Identify the simplest thing that could possibly work, however slow.
5. Describe that brute force out loud, in one sentence.
6. State its time and space complexity.
7. Name the **bottleneck** — the one operation making it slow.

**Improve it (steps 8–11)**
8. Match the bottleneck to a pattern. (The table below does this for you.)
9. Develop the improved approach step by step, saying what each step buys.
10. Trace the new approach on your tiny example, as a table.
11. Write pseudocode — structure only, no syntax.

**Finish properly (steps 12–17)**
12. Write clean C++.
13. Explain the lines that are not obvious, as you write them.
14. Test the edge cases: empty, one element, all equal, negatives, duplicates,
    the largest allowed input.
15. State the final time and space complexity.
16. Say what commonly goes wrong in this solution.
17. Name a related problem that uses the same idea.
:::

:::insight What each phase protects you from
**Understand** prevents the worst outcome: a correct solution to the wrong
problem. It costs two minutes and it is the step candidates skip most often.

**Reach something that works** prevents the second-worst: twenty minutes of
silence followed by nothing. A slow solution is worth far more than an elegant
idea you did not finish, and it gives the interviewer something to discuss.

**Improve it** is the part being assessed. Note that it comes *after* a working
solution, not instead of one.

**Finish properly** is where most of the remaining marks are. Untested code with
an unknown complexity is not a finished answer.
:::

## The bottleneck-to-pattern table

Step 8 is the one that feels like magic. It is not — it is a lookup.

@tbl: Step 8 made mechanical. Find the bottleneck in the left column, read the pattern in the right.
| The brute force is slow because… | Reach for | Chapter |
|---|---|---|
| it searches the array again for each element | a hash map or set | 14 |
| it compares every pair | two pointers (if sorted) | 9 |
| it recomputes the sum of overlapping ranges | sliding window or prefix sums | 10, 11 |
| it scans a sorted array linearly | binary search | 12 |
| it re-derives "the best so far" each time | a running variable — Kadane's shape | 8, 16 |
| it uses a second array | a write pointer, or index marking | 13 |
| it needs order that the input lacks | sort first | 15 |
| it walks the list repeatedly to find a position | fast/slow, or a fixed gap | 29 |
| it needs to know what came before in a list | a dummy node, or `prev`/`curr` | 26, 29 |
| it needs to detect repetition with no memory | Floyd's cycle detection | 29 |
| it asks "the minimum X such that…" | binary search on the answer | 12 |

:::interview The two sentences that most improve an answer
**At step 2:** *"Before I start — can the input be empty? Are there duplicates?
Can the values be negative? Should I return the index or the value?"*

**At step 6:** *"This brute force is $O(n^2)$ time and $O(1)$ space. Shall I code
it first, or go straight to optimising?"*

The first shows you know where bugs come from. The second shows you know what
you have, and hands the interviewer a decision — which is always welcome.
:::

## The method applied, end to end

Here is a problem that has not appeared in this book.

> **Problem.** Given an array of integers, return the length of the longest
> sub-array in which the difference between the largest and smallest element is
> at most $k$.

Work through it with me, and notice that the solution is never guessed.

### 1. Restate it

*"Find the longest run of neighbouring elements that are all within $k$ of each
other."*

### 2. Input and output

- **Input:** `std::vector<int> v`, and an integer `k`.
- **Output:** one integer — a length, not the sub-array itself.
- **Awkward values:** empty array → 0. $k = 0$ → the longest run of equal
  values. Negative values are fine; negative $k$ makes no sub-array valid except
  possibly none, so I will ask, and assume $k \ge 0$.

### 3. A tiny example

`v = {1, 5, 6, 7, 2}`, $k = 2$.

By hand: `{5, 6, 7}` has max $-$ min $= 2 \le 2$, length 3. Can I do better?
`{1, 5, 6, 7}` spans 6 — no. `{6, 7, 2}` spans 5 — no. **Answer: 3.**

### 4–5. The brute force

For every start $i$, extend to every end $j$, tracking the min and max of the
window as I go; whenever max $-$ min $\le k$, record the length.

### 6. Its complexity

$O(n^2)$ time — $n$ starts, each extending up to $n$ — and $O(1)$ space, because
the min and max are maintained incrementally.

### 7. The bottleneck

Every start re-examines elements that previous starts already examined. The work
on overlapping ranges is repeated.

### 8. Match it to a pattern

The table says: *recomputes over overlapping ranges* and *contiguous* →
**sliding window**.

A quick check against Chapter 10's preconditions:
- Must the answer be contiguous? **Yes** — it says sub-array.
- Is the property monotonic in window size? **Yes** — if a window is valid, every
  window inside it is also valid, because removing elements cannot increase the
  spread. That is exactly what the shrink rule needs.

Both hold, so a sliding window applies.

### 9. Develop it

Grow the window to the right. While `max - min > k`, shrink from the left. The
window is then valid; record its length.

One difficulty: **I need the max and min of the current window, and shrinking
from the left can remove the element that was the max.** A plain running maximum
cannot be undone.

@fig: method_worked | 186 | The worked problem. The window grows right and shrinks left as usual; the new part is needing the maximum and minimum of a window that shrinks, which a single running variable cannot provide.

Three ways to get the window's max and min:
- A **multiset**: $O(\log n)$ per insertion and removal → $O(n \log n)$ overall.
  Simple and correct.
- Two **monotonic deques**, one for the max and one for the min: $O(1)$
  amortised each → $O(n)$ overall. More machinery.
- Recompute on each shrink: back to $O(n^2)$. No.

I will state both of the first two, code the multiset version because it is
clearly correct, and mention the deque version as the optimum.

### 10. Trace it

`{1, 5, 6, 7, 2}`, $k = 2$.

@tbl: The trace. The window never shrinks further than it must, and `left` only moves forwards.
| `right` | window | min, max | spread | shrink? | `left` | length | `best` |
|---|---|---|---|---|---|---|---|
| 0 | `1` | 1, 1 | 0 | no | 0 | 1 | 1 |
| 1 | `1 5` | 1, 5 | 4 | yes → drop 1 | 1 | 1 | 1 |
| 2 | `5 6` | 5, 6 | 1 | no | 1 | 2 | 2 |
| 3 | `5 6 7` | 5, 7 | 2 | no | 1 | 3 | **3** |
| 4 | `5 6 7 2` | 2, 7 | 5 | yes → drop 5, 6, 7 | 4 | 1 | 3 |

Answer 3, matching the hand-worked example in step 3. That agreement is the
check — a trace that disagrees with your hand example means one of them is
wrong, and you have found it before writing any code.

### 11. Pseudocode

```text nonum
best = 0
left = 0
window = empty multiset
for right in 0 .. n-1:
    insert v[right] into window
    while (max(window) - min(window) > k):
        remove v[left] from window
        left = left + 1
    best = max(best, right - left + 1)
return best
```

### 12–13. The code

```cpp title="Longest sub-array with spread at most k"
#include <algorithm>
#include <iostream>
#include <set>
#include <vector>

int longestWithinK(const std::vector<int>& v, int k) {
    if (k < 0) return 0;                     // no sub-array can qualify
    std::multiset<int> window;               // multiset: duplicates allowed
    int left = 0, best = 0;

    for (int right = 0; right < (int)v.size(); ++right) {
        window.insert(v[right]);                       // grow

        while (!window.empty() &&
               *window.rbegin() - *window.begin() > k) {   // max - min
            window.erase(window.find(v[left]));        // erase ONE copy
            ++left;
        }
        best = std::max(best, right - left + 1);       // record
    }
    return best;
}

int main() {
    std::cout << longestWithinK({1, 5, 6, 7, 2}, 2) << "\n";
    std::cout << longestWithinK({1, 1, 1}, 0)       << "\n";
    std::cout << longestWithinK({8, 2, 4, 7}, 4)    << "\n";
    std::cout << longestWithinK({}, 5)              << "\n";
    std::cout << longestWithinK({4}, 0)             << "\n";
    std::cout << longestWithinK({1, 2, 3}, -1)      << "\n";
    return 0;
}
```

```text nonum
3
3
2
0
1
0
```

The two lines worth explaining as you write them:

**`window.erase(window.find(v[left]))`.** `erase(value)` on a multiset removes
**every** copy of that value. `erase(iterator)` removes exactly one. On
`{5, 5, 6}` the first form would delete both 5s and corrupt the window. This is a
real bug that compiles, runs, and gives wrong answers on inputs with duplicates.

**`*window.rbegin()` and `*window.begin()`.** A `std::multiset` is sorted, so the
first element is the minimum and the last is the maximum, both in $O(1)$.

### 14. Edge cases

Tested above: empty array → 0; one element → 1; all equal with $k = 0$ → 3;
negative $k$ → 0; no valid pair → the single-element answer. Also worth checking:
large values, where `max - min` could overflow `int` — with values near
$\pm 2^{31}$ the subtraction overflows, so a production version would use
`long long`.

### 15. Complexity

$O(n \log n)$ time — each element is inserted once and erased at most once, each
$O(\log n)$ — and $O(n)$ space for the multiset. The monotonic-deque version is
$O(n)$ time and $O(n)$ space.

### 16. What goes wrong

- `erase(value)` instead of `erase(iterator)` — removes all duplicates.
- Forgetting that shrinking may need to happen several times, so a `while`, not
  an `if`.
- Assuming a running max can be maintained with a single variable; it cannot
  survive a shrink.
- Overflow in `max - min` on extreme values.

### 17. A related problem

"Longest sub-array with at most $k$ distinct elements" — same window shape, with
a frequency map instead of a multiset. And "sliding window maximum" is exactly
the monotonic deque this problem's optimal version needs, in isolation.

:::insight What just happened
The solution was never guessed. It was **derived**:

- the word "sub-array" said contiguous;
- "contiguous plus repeated overlapping work" said sliding window;
- checking the monotonicity precondition confirmed it;
- the only genuine difficulty — max and min of a shrinking window — was isolated
  and then solved on its own;
- the trace agreed with the hand-worked example before any code was written.

That is the whole method. You will not always have a pattern for the bottleneck,
and then you think harder. But most of the time, you will.
:::

## Using the method under time pressure

You will not always have forty minutes.

:::checklist The compressed version — five minutes
1. Restate, and ask about empty, duplicates, negatives, return type.
2. Hand-work one small example.
3. State the brute force and its complexity out loud. Do not code it yet.
4. Name the bottleneck; look it up in the pattern table.
5. State the improved approach and its complexity, then code that.
6. Trace one example. Test empty and one element.
7. State the complexity and one thing that could go wrong.
:::

Steps 1, 3 and 7 are the ones never to skip. They take under a minute between
them and they are where most of the impression is formed.

## When the method does not produce an answer

Sometimes no pattern fits. Then:

1. **Solve a smaller version.** Can you do it for $n = 2$? For $n = 3$? A
   pattern in the small cases often reveals the general one.
2. **Solve a restricted version.** What if the values were sorted? All positive?
   Distinct? Solving the easier problem frequently shows the way, and it is a
   much better answer than nothing.
3. **Ask what you are not using.** Every stated constraint is a hint. "Values
   between 1 and n", "the array is sorted", "$O(1)$ space", "no division" — each
   rules out an easy answer and points at the intended one.
4. **Work backwards from the answer's shape.** If the answer must be $O(n)$,
   you get one pass; what could one pass possibly carry?
5. **Say what you are thinking.** Silence is the only genuinely bad outcome. An
   interviewer who hears "I'm looking for a way to avoid re-scanning the past,
   which usually means hashing" can help you; one who hears nothing cannot.

:::recap Chapter 34 in six lines
- Understand, then get something working, then improve it, then finish it.
  **In that order.**
- A slow working solution beats an elegant unfinished one, every time.
- Find the **bottleneck**, then look the bottleneck up in the pattern table.
- Trace before you code, and check the trace against your hand-worked example.
- Test empty, one element, all-equal, negatives and duplicates without being
  prompted.
- Every unused constraint in the problem statement is a hint about the intended
  solution.
:::

:::exercise Practise
1. Apply all seventeen steps, in writing, to: "find the two numbers in a sorted
   array that are closest to a target sum". Do not look anything up.
2. Apply them to: "given a linked list, remove every node whose value appears
   more than once". Which part is hardest, and why?
3. For each row of the bottleneck table, write down a problem from this book that
   it matches.
4. Take any problem from Chapter 20 and write out steps 1 to 7 only. Can you
   reach the bottleneck without recalling the solution?
5. Set a timer for five minutes and apply the compressed version to "longest
   sub-array with at most two distinct values". What did you have to leave out?
6. Rewrite the worked problem of this chapter using two monotonic deques for
   $O(n)$. Which steps of the method change?
7. Find a problem you cannot solve. Apply the five "when it does not work"
   tactics in order, writing down what each one yields.
:::
