# Pattern 1: Linear Traversal
@short: Linear Traversal
@subtitle: One pass, carrying everything you need to know with you
@tier: core
@prereq: Chapter 6
@blurb: The humblest pattern and the one you will use most. The skill is not writing the loop — you can already do that — it is working out what to **carry** as you go, so that a problem which looks like it needs two or three passes needs only one. This chapter builds that skill on five problems and ends with the question to ask yourself whenever you are tempted to loop twice.
@objectives:
- Recognise when a problem needs nothing more than one pass
- Design the *running state*: the few variables that must travel with the loop
- Convert an obvious two-pass solution into a one-pass one
- Handle the awkward cases: empty input, all-equal input, one element
- Solve largest, second-largest, is-sorted, max consecutive ones, and
  single-pass counting
- Know when an early exit is valuable and when it changes nothing

## When to use it

:::definition The linear traversal pattern
Visit each element once, in order, maintaining a small amount of **running
state** — a few variables that summarise everything seen so far.

Use it when the answer depends on **every** element, and when what you need to
remember about the past is small and fixed.
:::

How to recognise it in a problem statement:

| Words in the problem | What they mean |
|---|---|
| "find the maximum / minimum / sum" | one pass, one or two variables |
| "count how many …" | one pass, a counter |
| "check whether all / any …" | one pass, possibly with an early exit |
| "the longest run of …" | one pass, a current-run and a best-run variable |
| "the first element that …" | one pass with an early return |

If the answer depends on **pairs** of elements, this pattern is not enough and
you want Chapter 9 or Chapter 14 instead.

## The idea: running state

@fig: trav_running_state | 150 | Running state. The loop moves left to right; the small box of variables beside it holds everything the algorithm still needs to know. When the loop ends, the answer is in that box.

Here is the mental model. You are walking along the array with a notebook that
has room for only two or three lines. At each element you may update the
notebook, but you can never go back and look at the array again.

**What must be written in the notebook?** That question *is* the algorithm.
Answer it and the code writes itself.

## Problem 1: Largest element

**Notebook:** one line — the largest so far.

```cpp title="Largest element"
#include <iostream>
#include <stdexcept>
#include <vector>

int largest(const std::vector<int>& v) {
    if (v.empty()) throw std::invalid_argument("no largest in an empty array");
    int best = v[0];                 // start from a real element
    for (int i = 1; i < (int)v.size(); ++i)
        if (v[i] > best) best = v[i];
    return best;
}

int main() {
    std::cout << largest({3, 9, 2, 9, 1}) << "\n";
    std::cout << largest({-5, -2, -8})    << "\n";
    std::cout << largest({42})            << "\n";
    return 0;
}
```

```text nonum
9
-2
42
```

$O(n)$ time, $O(1)$ space. The all-negative case is the one that catches people
who start `best` at 0.

## Problem 2: Second-largest element

Now the notebook needs two lines, and the updates get interesting.

:::definition The problem, stated precisely
Return the second-largest **distinct** value. In `{5, 5, 4}` the answer is 4,
not 5. If there is no second distinct value — as in `{7, 7, 7}` or `{7}` —
report that.

Beginners skip this paragraph and lose the problem on it. *"Second largest"* is
ambiguous until you decide what duplicates mean, and in an interview you should
ask.
:::

### The obvious approach, and why we improve on it

Sort descending and take the first element different from the front: correct,
and $O(n \log n)$. Or find the maximum, then scan again for the largest value
below it: correct, $O(n)$, two passes.

Both work. One pass is better, and the thinking that gets you there is the
point.

### The one-pass idea

Carry two values: `best` and `second`. For each element $x$ there are exactly
three cases, and getting their **order** right is the whole problem.

@fig: trav_second_largest | 162 | The three cases for the second-largest. A new champion pushes the old champion down into second place — which is why `second = best` must happen *before* `best = x`.

### The trace

Input `{2, 9, 4, 9, 7}`. `LOW` stands for "nothing yet".

@tbl: Tracing second-largest. Watch row 4: a value equal to `best` must change nothing, which is what makes the answer *distinct*.
| `x` | Case | `best` before | `second` before | `best` after | `second` after |
|---|---|---|---|---|---|
| 2 | new best | LOW | LOW | 2 | LOW |
| 9 | new best | 2 | LOW | 9 | 2 |
| 4 | middle | 9 | 2 | 9 | 4 |
| 9 | equal to best | 9 | 4 | 9 | 4 |
| 7 | middle | 9 | 4 | 9 | 7 |

```cpp title="Second largest in one pass"
#include <climits>
#include <iostream>
#include <vector>

// Returns the second-largest DISTINCT value, or INT_MIN if there is none.
int secondLargest(const std::vector<int>& v) {
    long long best = LLONG_MIN, second = LLONG_MIN;
    for (int x : v) {
        if (x > best) {
            second = best;           // the old champion is demoted FIRST
            best = x;
        } else if (x < best && x > second) {
            second = x;              // not a champion, but better than second
        }
        // x == best: a duplicate of the champion changes nothing
    }
    return second == LLONG_MIN ? INT_MIN : (int)second;
}

int main() {
    std::cout << secondLargest({2, 9, 4, 9, 7}) << "\n";
    std::cout << secondLargest({5, 5, 4})       << "\n";
    std::cout << (secondLargest({7, 7, 7}) == INT_MIN ? "none" : "?") << "\n";
    std::cout << (secondLargest({7}) == INT_MIN ? "none" : "?")       << "\n";
    return 0;
}
```

```text nonum
7
4
none
none
```

:::pitfall The three bugs in this problem
**Updating in the wrong order.** Writing `best = x;` before `second = best;`
loses the old champion — `second` just becomes `x` as well. Demote first, then
promote.

**Using `INT_MIN` as the sentinel for an `int`.** If the array genuinely
contains `INT_MIN`, the "none" answer and a real answer become
indistinguishable. Here the accumulators are `long long`, so `LLONG_MIN` is a
value no `int` input can ever be.

**Forgetting `x < best` in the `else if`.** Without it, a duplicate of the
champion satisfies `x > second` and wrongly becomes the second largest, so
`{5, 5, 4}` returns 5.
:::

## Problem 3: Is the array sorted?

**Notebook:** nothing at all — you only need the current element and the one
before it.

```cpp title="Is it sorted (non-decreasing)?"
#include <iostream>
#include <vector>

bool isSorted(const std::vector<int>& v) {
    for (int i = 1; i < (int)v.size(); ++i)
        if (v[i] < v[i - 1]) return false;   // one violation is enough
    return true;                             // empty and 1-element are sorted
}

int main() {
    std::cout << isSorted({1, 2, 2, 5}) << "\n";
    std::cout << isSorted({1, 3, 2})    << "\n";
    std::cout << isSorted({})           << "\n";
    std::cout << isSorted({9})          << "\n";
    return 0;
}
```

```text nonum
1
0
1
1
```

Two design points worth noticing:

**The loop starts at `i = 1`.** Comparing `v[i]` with `v[i-1]` at `i = 0` would
read `v[-1]`. Starting at 1 makes the out-of-bounds access impossible rather
than merely unlikely.

**An empty array is sorted, and so is a one-element array.** Both are
"vacuously true" — there is no pair out of order because there is no pair.
Returning `true` is correct, and the loop does it automatically by never
running. Edge cases that fall out of the structure are better than edge cases
you special-case.

:::insight Early exit changes the best case, not the complexity
`return false` on the first violation means `{9, 1, 1, 1, ... }` finishes in one
comparison. Lovely — but the **worst case** (a genuinely sorted array) still
examines everything, so it is still $O(n)$.

Early exits are worth having. They are not worth claiming a better complexity
for, and claiming one in an interview is a clear tell.
:::

## Problem 4: Maximum consecutive ones

:::definition The problem
Given an array of 0s and 1s, find the length of the longest unbroken run of 1s.
`{1, 1, 0, 1, 1, 1}` gives 3.
:::

**Notebook:** two lines — the current run, and the best run seen.

@fig: trav_consecutive | 152 | The current-run / best-run pair. The current run grows on a 1 and resets to zero on a 0; `best` only ever increases, so it survives the resets and holds the answer at the end.

### The trace

| `x` | `current` | `best` |
|---|---|---|
| start | 0 | 0 |
| 1 | 1 | 1 |
| 1 | 2 | 2 |
| 0 | 0 | 2 |
| 1 | 1 | 2 |
| 1 | 2 | 2 |
| 1 | 3 | 3 |

```cpp title="Longest run of 1s"
#include <algorithm>
#include <iostream>
#include <vector>

int maxConsecutiveOnes(const std::vector<int>& v) {
    int current = 0, best = 0;
    for (int x : v) {
        if (x == 1) {
            ++current;
            best = std::max(best, current);   // update INSIDE the run
        } else {
            current = 0;                      // the run is broken
        }
    }
    return best;
}

int main() {
    std::cout << maxConsecutiveOnes({1, 1, 0, 1, 1, 1}) << "\n";
    std::cout << maxConsecutiveOnes({0, 0, 0})          << "\n";
    std::cout << maxConsecutiveOnes({1, 1, 1})          << "\n";
    std::cout << maxConsecutiveOnes({})                 << "\n";
    return 0;
}
```

```text nonum
3
0
3
0
```

:::pitfall Updating `best` only when the run ends
```cpp nonum frag
for (int x : v) {
    if (x == 1) ++current;
    else { best = std::max(best, current); current = 0; }
}
return best;                                  // BUG
```
On `{1, 1, 1}` the run never ends, so `best` is never updated and the function
returns 0.

You can fix it with one more `best = std::max(best, current);` after the loop —
but updating inside the run, as in the correct version, means there is nothing
to remember and nothing to forget. **Prefer the version with no after-the-loop
correction**; code that needs a patch at the end usually has a cleaner shape
waiting to be found.
:::

This "current versus best" shape is the seed of the sliding window (Chapter 10)
and of Kadane's algorithm (Chapter 16). You have just met the idea that carries
both.

## Turning two passes into one

Here is the general move, and it is worth internalising.

Suppose you want the number of elements above the average. The obvious
solution is two passes: one to compute the average, one to count. That is fine
— it is still $O(n)$.

But sometimes the second pass can be folded in, and the question that reveals
it is:

:::insight The one-pass question
*"At the moment I reach element $i$, do I already know everything I need in
order to do the work for element $i$?"*

- **Yes** → fold the passes together.
- **No** → you genuinely need the earlier pass. Two passes is $2n$ steps, which
  is still $O(n)$, and clarity beats cleverness.

For counting-above-average the answer is **no**: you cannot know the average
until you have seen the last element. Two passes it is, and that is the right
answer.

For sum-and-maximum the answer is **yes**: both are running totals, so one pass
does both.
:::

```cpp title="One pass computing four things at once"
#include <iostream>
#include <vector>

struct Stats {
    long long sum = 0;
    int count = 0;
    int lo = 0, hi = 0;
};

Stats summarise(const std::vector<int>& v) {
    Stats s;
    if (v.empty()) return s;
    s.lo = s.hi = v[0];
    for (int x : v) {
        s.sum += x;
        ++s.count;
        if (x < s.lo) s.lo = x;
        if (x > s.hi) s.hi = x;
    }
    return s;
}

int main() {
    Stats s = summarise({4, -1, 9, 3});
    std::cout << "sum=" << s.sum << " n=" << s.count
              << " min=" << s.lo << " max=" << s.hi << "\n";
    return 0;
}
```

```text nonum
sum=15 n=4 min=-1 max=9
```

Four answers, one traversal, $O(1)$ space. Four separate loops would also be
$O(n)$ — but they would read the array four times, and on large data that is
four times the memory traffic.

## Cost summary

| Problem | Time | Space | Running state |
|---|---|---|---|
| Largest | $O(n)$ | $O(1)$ | `best` |
| Second largest | $O(n)$ | $O(1)$ | `best`, `second` |
| Is sorted | $O(n)$ | $O(1)$ | none |
| Max consecutive ones | $O(n)$ | $O(1)$ | `current`, `best` |
| Sum / min / max / count | $O(n)$ | $O(1)$ | four accumulators |

:::interview What this pattern is really testing
A linear-traversal question is never about the loop. It is about whether you:
- ask what "second largest" means when there are duplicates;
- test the empty array and the all-equal array without being prompted;
- initialise from a real element rather than from 0;
- notice that `{1, 1, 1}` never ends its run.

Interviewers use these problems precisely because the algorithm is trivial, so
nothing distracts from how carefully you think.
:::

:::recap Chapter 8 in five lines
- One pass, with a small fixed **running state**, solves any problem whose
  answer depends on a summary of everything seen so far.
- Designing the running state *is* the algorithm; write down the notebook
  before you write the loop.
- Demote before you promote when maintaining a top-two.
- Update `best` inside the run, not when the run ends, so the final run is not
  lost.
- Early exit improves the best case only; the complexity is unchanged.
:::

:::exercise Practise
1. Find the **third** largest distinct value in one pass. How many variables
   does the notebook need, and in what order must they be updated?
2. Count how many elements are strictly greater than both of their neighbours.
   What happens at the two ends?
3. Check whether an array is sorted in **either** direction (ascending or
   descending) in one pass. What should `{3, 3, 3}` return?
4. Find the longest run of **equal** values, and return both the value and the
   length. What is the running state now?
5. Given an array of 0s and 1s, find the longest run of 1s you could get if you
   were allowed to flip **one** 0 to a 1. (This is a genuine step up — try the
   one-pass version, and if it resists, read Chapter 10 and come back.)
6. Explain why counting elements above the average cannot be done in one pass,
   and name a quantity that *can* be compared against as you go.
7. Write a one-pass function returning the index of the first element that is
   larger than every element before it and smaller than every element after it.
   What makes this harder than it looks, and which pattern would make it easy?
:::
