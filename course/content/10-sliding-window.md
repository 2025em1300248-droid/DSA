# Pattern 3: Sliding Window
@short: Sliding Window
@subtitle: A sub-array that grows and shrinks instead of being rebuilt
@tier: core
@prereq: Chapter 9
@blurb: Whenever a problem asks about *contiguous* sub-arrays, the brute force rebuilds every one of them from scratch — and almost all of that work is re-reading elements it has already read. A sliding window keeps one sub-array and edits it at the edges, which turns $O(n^2)$ or $O(n^3)$ into $O(n)$. This chapter covers both kinds, fixed-size and variable-size, and the single question that tells you which one you need.
@objectives:
- Recognise a sliding-window problem from the word "contiguous" or "sub-array"
- Implement a fixed-size window with the add-one / remove-one update
- Implement a variable-size window with the grow-while-valid, shrink-while-invalid loop
- Explain why the variable window is $O(n)$ despite having a loop inside a loop
- Solve: maximum sum of $k$ elements, longest sub-array with sum $\le$ target,
  longest sub-string without repeats, minimum window that reaches a sum
- Say precisely when the pattern breaks, and what to use instead

## The waste the pattern removes

Take a concrete problem.

:::definition Maximum sum of any $k$ consecutive elements
Given `{2, 1, 5, 1, 3, 2}` and $k = 3$, the sums of the four possible windows
are $2{+}1{+}5 = 8$, $1{+}5{+}1 = 7$, $5{+}1{+}3 = 9$, $1{+}3{+}2 = 6$.
The answer is 9.
:::

The obvious solution computes each window's sum from scratch:

```cpp title="Brute force: recompute every window" frag
int best = INT_MIN;
for (int i = 0; i + k <= n; ++i) {
    int sum = 0;
    for (int j = i; j < i + k; ++j) sum += v[j];   // k additions, every time
    best = std::max(best, sum);
}
```

That is $O(n \cdot k)$. Now look at what it is doing.

@fig: sw_overlap | 150 | Consecutive windows overlap almost entirely. Going from one window to the next, $k-2$ of the $k$ elements are unchanged — yet the brute force re-adds all $k$ of them. The sliding window edits only the two ends.

:::insight The whole pattern in one sentence
Two neighbouring windows share all but **two** elements, so the second sum can
be obtained from the first with **one addition and one subtraction** instead of
$k$ additions.

$$\text{sum}_{\text{new}} = \text{sum}_{\text{old}} + v[\text{incoming}] - v[\text{outgoing}]$$

Nothing else about the pattern is hard. Everything else is bookkeeping about
*when* to move each edge.
:::

## Kind 1: Fixed-size window

@fig: sw_fixed | 158 | A fixed window of size 3 moving across the array. Each step adds the element entering on the right and subtracts the one leaving on the left — two operations, not $k$.

### The trace

`{2, 1, 5, 1, 3, 2}`, $k = 3$.

@tbl: Each step is one addition and one subtraction, regardless of how large $k$ is.
| Step | Window | Enters | Leaves | `sum` | `best` |
|---|---|---|---|---|---|
| build | `2 1 5` | — | — | 8 | 8 |
| 1 | `1 5 1` | 1 | 2 | $8 + 1 - 2 = 7$ | 8 |
| 2 | `5 1 3` | 3 | 1 | $7 + 3 - 1 = 9$ | 9 |
| 3 | `1 3 2` | 2 | 5 | $9 + 2 - 5 = 6$ | 9 |

```cpp title="Maximum sum of k consecutive elements, O(n)"
#include <algorithm>
#include <climits>
#include <iostream>
#include <vector>

long long maxSumOfK(const std::vector<int>& v, int k) {
    int n = (int)v.size();
    if (k <= 0 || k > n) return 0;          // no valid window exists

    long long sum = 0;
    for (int i = 0; i < k; ++i) sum += v[i];   // build the first window
    long long best = sum;

    for (int i = k; i < n; ++i) {
        sum += v[i];                           // the element entering, on the right
        sum -= v[i - k];                       // the element leaving, on the left
        best = std::max(best, sum);
    }
    return best;
}

int main() {
    std::cout << maxSumOfK({2, 1, 5, 1, 3, 2}, 3) << "\n";
    std::cout << maxSumOfK({-3, -1, -4, -1}, 2)   << "\n";
    std::cout << maxSumOfK({5}, 1)                << "\n";
    std::cout << maxSumOfK({1, 2}, 5)             << "\n";
    return 0;
}
```

```text nonum
9
-4
5
0
```

$O(n)$ time, $O(1)$ space, down from $O(n \cdot k)$.

:::pitfall The index of the outgoing element
When `i` is the index entering the window, the element leaving is at
`i - k` — **not** `i - k + 1`, and not `i - k - 1`.

Derive it rather than memorising it: after adding `v[i]`, the window covers
`i-k+1 .. i`, which is $k$ elements. The element that was in the previous window
but is not in this one is the one just before the new left edge, namely
`i - k`. Deriving it takes five seconds and you will never get it wrong again.
:::

## Kind 2: Variable-size window

Fixed windows are the easy half. The interesting problems let the window
**choose** its own size.

:::definition The shape of a variable window
Both edges start at 0. Then, for each position of the right edge:

1. **Grow:** add `v[right]` to the window.
2. **Shrink:** while the window is *invalid*, remove `v[left]` and advance
   `left`.
3. **Record:** the window is now valid, so update the answer.

The condition that defines "invalid" is the whole problem. Everything else is
the same three lines every time.
:::

@fig: sw_variable | 172 | The grow–shrink loop. The right edge advances once per iteration; the left edge chases it, moving only as far as it must to restore validity. Neither edge ever moves backwards.

### Problem: longest sub-array with sum at most a target

```cpp title="Longest contiguous sub-array with sum <= target"
#include <algorithm>
#include <iostream>
#include <vector>

// All values must be non-negative - see the pitfall below.
int longestAtMost(const std::vector<int>& v, long long target) {
    long long sum = 0;
    int left = 0, best = 0;
    for (int right = 0; right < (int)v.size(); ++right) {
        sum += v[right];                       // 1. grow
        while (sum > target && left <= right) {
            sum -= v[left];                    // 2. shrink while invalid
            ++left;
        }
        best = std::max(best, right - left + 1);  // 3. record
    }
    return best;
}

int main() {
    std::cout << longestAtMost({2, 1, 5, 1, 3, 2}, 8) << "\n";
    std::cout << longestAtMost({4, 4, 4}, 3)          << "\n";
    std::cout << longestAtMost({1, 1, 1}, 100)        << "\n";
    return 0;
}
```

```text nonum
3
0
3
```

### The trace

`{2, 1, 5, 1, 3, 2}`, target 8. The crucial habit: record `sum` and `left`
after **every individual edge movement**, not once per iteration. The state
carries across iterations, and that is where careless traces go wrong.

@tbl: Each row is one value of `right`. The arrows inside a `sum` cell show the shrinking steps, one per removed element. Note that `left` moves twice in a single iteration at `right = 4`, and not at all in three of the six.
| `right` | enters | `sum` | shrink steps | `left` | window | length | `best` |
|---|---|---|---|---|---|---|---|
| 0 | 2 | 2 | none | 0 | `2` | 1 | 1 |
| 1 | 1 | 3 | none | 0 | `2 1` | 2 | 2 |
| 2 | 5 | 8 | none — 8 is not $>$ 8 | 0 | `2 1 5` | 3 | **3** |
| 3 | 1 | 9 → 7 | drop `2` | 1 | `1 5 1` | 3 | 3 |
| 4 | 3 | 10 → 9 → 4 | drop `1`, then `5` | 3 | `1 3` | 2 | 3 |
| 5 | 2 | 6 | none | 3 | `1 3 2` | 3 | 3 |

The answer is 3, which matches the program. Three rows of that table repay
study:

**Row 2.** The sum is exactly 8 and the condition is `sum > target`, so nothing
shrinks. If the problem had said "strictly less than", this row would shrink and
the answer would change. The comparison operator *is* the specification.

**Row 4.** `left` moves twice in one iteration. This is why the inner loop is a
`while` and not an `if` — a single element entering can invalidate the window by
more than one element's worth.

**Rows 0, 1 and 5.** `left` does not move at all. Over the whole run `left`
advanced 3 times and `right` advanced 6 times: nine movements for six elements,
which is the linear behaviour the next section proves.

## Why the variable window is O(n)

There is a `while` loop inside a `for` loop. That *looks* quadratic.

:::insight The amortised argument
Count how many times `++left` can ever execute, across the whole run.

`left` starts at 0, only increases, and never exceeds $n$. So **over the entire
algorithm**, the inner `while` body runs at most $n$ times in total — not $n$
times per iteration.

The outer loop runs $n$ times. Total work: at most $2n$ steps. $O(n)$.

This is the same accounting as amortised analysis in Chapter 5: a particular
iteration may be expensive, but the total across all iterations is bounded.
Being able to give this argument out loud is the difference between "I think
it's linear" and a convincing answer.
:::

## Problem: longest sub-string without repeating characters

The canonical variable-window problem, and the one most often asked.

:::definition The problem
Find the length of the longest sub-string with no repeated character.
`"abcabcbb"` → 3, from `"abc"`. `"bbbbb"` → 1. `"pwwkew"` → 3, from `"wke"`.
:::

The window must stay free of duplicates. We need to know, in $O(1)$, whether
the incoming character is already inside — so we carry a count per character.

```cpp title="Longest substring without repeating characters"
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int longestUnique(const std::string& s) {
    std::vector<int> count(256, 0);            // how many of each char in window
    int left = 0, best = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        ++count[(unsigned char)s[right]];      // 1. grow
        while (count[(unsigned char)s[right]] > 1) {
            --count[(unsigned char)s[left]];   // 2. shrink until no duplicate
            ++left;
        }
        best = std::max(best, right - left + 1);  // 3. record
    }
    return best;
}

int main() {
    std::cout << longestUnique("abcabcbb") << "\n";
    std::cout << longestUnique("bbbbb")    << "\n";
    std::cout << longestUnique("pwwkew")   << "\n";
    std::cout << longestUnique("")         << "\n";
    return 0;
}
```

```text nonum
3
1
3
0
```

The shrink condition is worth reading twice: we shrink while **the character
that just arrived** appears more than once. We do not need to search the window
for any duplicate, because the window was duplicate-free before `s[right]`
arrived — so the only possible duplicate involves `s[right]`. Maintaining an
invariant like that, and then exploiting it, is the heart of window problems.

$O(n)$ time — each character enters once and leaves at most once. $O(1)$ space,
because the count array is a fixed 256 entries regardless of the input length.

## When the pattern does not apply

:::warning The non-negative requirement
`longestAtMost` relies on an assumption that is easy to miss: **growing the
window never decreases the sum, and shrinking never increases it.** That is only
true when every value is non-negative.

With negatives, `{5, -3, 4}` and target 5: the window `5` is valid, `5 -3` sums
to 2 and is also valid, and `5 -3 4` sums to 6 and is not — but shrinking from
the left gives `-3 4` = 1, which *is* valid and longer than you might have kept.
The monotonic relationship between window size and sum is gone, so the shrink
rule can no longer be trusted.

For sub-array-sum problems with negative numbers, use **prefix sums plus a hash
map** — which is exactly Chapter 11.
:::

Checklist for applying the pattern at all:

| Question | If no |
|---|---|
| Must the answer be **contiguous**? | not a window problem — think sorting or hashing |
| Does extending the window change the quantity **monotonically**? | prefix sums (Chapter 11) |
| Can you update the window state in $O(1)$ per edge move? | the window will not be $O(n)$ |

## Cost summary

| Problem | Brute force | Window | Space |
|---|---|---|---|
| Max sum of $k$ elements | $O(n \cdot k)$ | $O(n)$ | $O(1)$ |
| Longest sub-array, sum $\le$ target | $O(n^2)$ | $O(n)$ | $O(1)$ |
| Longest sub-string, no repeats | $O(n^2)$ or worse | $O(n)$ | $O(1)$ |
| Smallest window with sum $\ge$ target | $O(n^2)$ | $O(n)$ | $O(1)$ |
| Max consecutive ones with one flip | $O(n^2)$ | $O(n)$ | $O(1)$ |

:::recap Chapter 10 in six lines
- Neighbouring windows differ by two elements, so update at the edges instead of
  rebuilding.
- **Fixed size:** add `v[i]`, subtract `v[i-k]`, record. One addition, one
  subtraction.
- **Variable size:** grow by one, shrink while invalid, record. The "invalid"
  condition is the entire problem.
- The inner `while` does not make it quadratic: `left` advances at most $n$ times
  in total across the whole run.
- Keep the window state updatable in $O(1)$ — a running sum, a count array, a
  hash map.
- Non-negative values are a hidden precondition of sum-based windows. With
  negatives, use prefix sums.
:::

:::exercise Practise
1. Re-run the trace above with target 9 instead of 8. Which row changes first,
   and what is the new answer?
2. Find the **minimum** length of a contiguous sub-array whose sum is at least a
   target. Which part of the three-line shape changes, and which stays the same?
3. Find the average of every window of size $k$ and return the largest. Why must
   you avoid computing the average inside the loop?
4. Maximum consecutive ones if you may flip at most **one** zero. (Hint: the
   window is invalid when it contains two zeroes. What is the window state?)
5. Generalise exercise 4 to at most $k$ flips. How much of your code changes?
6. Longest sub-string with at most two distinct characters. What is the window
   state, and what is the shrink condition?
7. Explain, with a concrete three-element example, why `longestAtMost` is wrong
   when the array may contain negative numbers.
8. Permutation in a string: given `s1` and `s2`, does `s2` contain a permutation
   of `s1` as a sub-string? (Hint: a fixed window of size `s1.size()`, and a
   cheap way to compare two character-count arrays.)
:::
