# Pattern 9: Kadane's Algorithm
@short: Kadane's Algorithm
@subtitle: The maximum sub-array sum in one pass, and the idea behind it
@tier: core
@prereq: Chapters 8 and 11
@blurb: Kadane's algorithm finds the largest sum of any contiguous sub-array in a single pass with two variables. It is four lines long, and almost nobody derives it on first encounter — but the idea behind it is simple enough to rediscover, and it generalises to a whole family of problems. This chapter derives it rather than presenting it, which is the only way it will stay in your memory.
@objectives:
- State the maximum sub-array problem precisely, including the all-negative case
- Derive Kadane's algorithm from the brute force by asking one question
- Explain the "extend or restart" decision and why it is always correct
- Trace the algorithm and recover the *indices* of the best sub-array, not just its sum
- Adapt it to the maximum **product** sub-array, and say why that needs a second variable
- Recognise the shape in problems that do not look like sub-array sums

## The problem

:::definition Maximum sub-array sum
Given an array, find the largest sum obtainable from any **contiguous**,
non-empty sub-array.

`{-2, 1, -3, 4, -1, 2, 1, -5, 4}` → **6**, from `{4, -1, 2, 1}`.

"Non-empty" matters: if the empty sub-array were allowed, an all-negative array
would answer 0, and most versions of the problem do not want that. Ask.
:::

@fig: kad_problem | 150 | The problem. Every contiguous stretch has a sum; we want the largest. The answer is rarely the whole array, and with all-negative input it is the single least-bad element.

## From brute force to the insight

### Attempt 1: every sub-array, summed from scratch — $O(n^3)$

```cpp title="All starts, all ends, sum each one" frag
int best = INT_MIN;
for (int i = 0; i < n; ++i)
    for (int j = i; j < n; ++j) {
        int sum = 0;
        for (int k = i; k <= j; ++k) sum += v[k];
        best = std::max(best, sum);
    }
```

### Attempt 2: extend the inner sum — $O(n^2)$

The innermost loop re-adds elements it already added. Carry the sum instead:

```cpp title="Grow the sum as j advances" frag
int best = INT_MIN;
for (int i = 0; i < n; ++i) {
    int sum = 0;
    for (int j = i; j < n; ++j) {
        sum += v[j];                 // extend by one element
        best = std::max(best, sum);
    }
}
```

Better. Still quadratic, because we restart from every possible $i$.

### Attempt 3: the question that removes the outer loop

Instead of asking *"what is the best sub-array overall?"*, ask a smaller
question at each position:

> **"What is the best sub-array that *ends exactly here*?"**

Call that `endingHere[i]`. If you knew it for every $i$, the answer would be the
largest of them — because every sub-array ends somewhere.

And `endingHere[i]` has a two-line answer:

:::insight Extend, or restart
A sub-array ending at $i$ either

- **extends** the best sub-array ending at $i-1$, giving
  `endingHere[i-1] + v[i]`, or
- **restarts** at $i$, giving just `v[i]`.

Those are the only two possibilities, so

$$\text{endingHere}[i] = \max\big(v[i],\; \text{endingHere}[i-1] + v[i]\big)$$

Now notice *when* restarting wins: exactly when `endingHere[i-1] < 0`. A
negative prefix can only drag down whatever follows it, so you drop it. A
non-negative prefix can only help, so you keep it.

**Kadane's algorithm in one sentence: carry the running sum forward, and throw
it away the moment it goes negative.**
:::

@fig: kad_extend_restart | 170 | The extend-or-restart decision at each element. When the running sum is negative it is a liability, so the next element starts fresh; otherwise it is an asset and the next element inherits it.

Each `endingHere[i]` depends only on the previous one, so we need a single
variable, not an array. That is the whole algorithm.

## The code

```cpp title="Kadane's algorithm"
#include <algorithm>
#include <climits>
#include <iostream>
#include <vector>

long long maxSubarraySum(const std::vector<int>& v) {
    if (v.empty()) return 0;
    long long endingHere = v[0];      // best sub-array ending at index 0
    long long best = v[0];            // best seen anywhere so far
    for (int i = 1; i < (int)v.size(); ++i) {
        endingHere = std::max((long long)v[i], endingHere + v[i]);  // extend or restart
        best = std::max(best, endingHere);                          // record
    }
    return best;
}

int main() {
    std::cout << maxSubarraySum({-2, 1, -3, 4, -1, 2, 1, -5, 4}) << "\n";
    std::cout << maxSubarraySum({-3, -1, -7})                    << "\n";
    std::cout << maxSubarraySum({5})                             << "\n";
    std::cout << maxSubarraySum({1, 2, 3})                       << "\n";
    return 0;
}
```

```text nonum
6
-1
5
6
```

$O(n)$ time, $O(1)$ space.

### The trace

`{-2, 1, -3, 4, -1, 2, 1, -5, 4}`.

@tbl: Kadane traced. The decision column is the heart of it: a negative running sum is always abandoned, because carrying it forward can only make the next sub-array worse.
| `i` | `v[i]` | `endingHere + v[i]` | `v[i]` | decision | `endingHere` | `best` |
|---|---|---|---|---|---|---|
| 0 | $-2$ | — | — | start | $-2$ | $-2$ |
| 1 | 1 | $-1$ | 1 | **restart** | 1 | 1 |
| 2 | $-3$ | $-2$ | $-3$ | extend | $-2$ | 1 |
| 3 | 4 | 2 | 4 | **restart** | 4 | 4 |
| 4 | $-1$ | 3 | $-1$ | extend | 3 | 4 |
| 5 | 2 | 5 | 2 | extend | 5 | 5 |
| 6 | 1 | 6 | 1 | extend | 6 | **6** |
| 7 | $-5$ | 1 | $-5$ | extend | 1 | 6 |
| 8 | 4 | 5 | 4 | extend | 5 | 6 |

Look at rows 1 and 3. Both restart, and both do so because the previous
`endingHere` was negative. Look at row 7: `endingHere` drops from 6 to 1 but
stays positive, so it is kept — and `best` is unaffected, because `best` only
ever increases.

:::pitfall Initialising to 0 breaks all-negative input
```cpp nonum frag
long long endingHere = 0, best = 0;         // BUG for all-negative arrays
for (int x : v) {
    endingHere = std::max(0LL, endingHere + x);
    best = std::max(best, endingHere);
}
```
On `{-3, -1, -7}` this returns 0, which is the sum of the *empty* sub-array. If
the problem demands a non-empty sub-array, the answer should be $-1$.

Initialising both to `v[0]` and starting the loop at index 1 makes the
non-empty requirement automatic. If the empty sub-array *is* allowed, the
0-version is correct — so **ask which it is**, and say which you assumed.
:::

## Recovering the sub-array itself

Interviewers often follow up with *"now tell me where it is"*. Two extra
variables do it.

```cpp title="Kadane with indices"
#include <algorithm>
#include <iostream>
#include <vector>

struct Result { long long sum; int from; int to; };

Result maxSubarray(const std::vector<int>& v) {
    Result r{v[0], 0, 0};
    long long endingHere = v[0];
    int start = 0;                              // start of the current run
    for (int i = 1; i < (int)v.size(); ++i) {
        if (endingHere + v[i] < v[i]) {         // restarting
            endingHere = v[i];
            start = i;                          // the run begins here
        } else {
            endingHere += v[i];                 // extending
        }
        if (endingHere > r.sum) {               // a new overall best
            r.sum = endingHere;
            r.from = start;
            r.to = i;
        }
    }
    return r;
}

int main() {
    auto r = maxSubarray({-2, 1, -3, 4, -1, 2, 1, -5, 4});
    std::cout << "sum " << r.sum << " from index " << r.from
              << " to " << r.to << "\n";
    auto s = maxSubarray({-3, -1, -7});
    std::cout << "sum " << s.sum << " from index " << s.from
              << " to " << s.to << "\n";
    return 0;
}
```

```text nonum
sum 6 from index 3 to 6
sum -1 from index 1 to 1
```

The key detail: `start` is updated **only when restarting**, and `r.from` is
copied from it **only when a new best is found**. Updating `r.from` on every
extension would be wrong, and updating `start` on every element would make it
meaningless.

## The variation: maximum product sub-array

:::definition The problem
Same question, but with products. `{2, 3, -2, 4}` → **6**, from `{2, 3}`.
:::

Kadane does not transfer directly, and the reason is instructive.

:::insight Why products need two running values
With sums, a large running total is good and a negative one is bad. With
products, **a very negative running product is an asset**, because the next
negative number will flip it to a very large positive.

`{-2, 3, -4}`: the best product is $(-2) \times 3 \times (-4) = 24$, and the
running product was $-6$ at the middle. A Kadane that discards negatives would
throw away exactly the value it needs.

So you carry **both** the maximum and the minimum product ending here. On a
negative element the two swap roles, because multiplying by a negative turns the
largest into the smallest and vice versa.
:::

```cpp title="Maximum product sub-array"
#include <algorithm>
#include <iostream>
#include <vector>

long long maxProduct(const std::vector<int>& v) {
    long long best = v[0], hi = v[0], lo = v[0];
    for (int i = 1; i < (int)v.size(); ++i) {
        long long x = v[i];
        if (x < 0) std::swap(hi, lo);          // a negative swaps the roles
        hi = std::max(x, hi * x);
        lo = std::min(x, lo * x);
        best = std::max(best, hi);
    }
    return best;
}

int main() {
    std::cout << maxProduct({2, 3, -2, 4})  << "\n";
    std::cout << maxProduct({-2, 0, -1})    << "\n";
    std::cout << maxProduct({-2, 3, -4})    << "\n";
    std::cout << maxProduct({-2})           << "\n";
    return 0;
}
```

```text nonum
6
0
24
-2
```

@fig: kad_product | 160 | Why the product version carries two values. A negative element exchanges the largest and smallest running products, so the "worst" value a moment ago becomes the best one now. Zeroes reset both.

Note that `{-2, 0, -1}` gives 0: a zero wipes out both running values, and the
`std::max(x, hi * x)` form handles it automatically by restarting at `x`.

## The family of problems this shape solves

@tbl: Kadane is one instance of a general shape — *the best thing ending here, from the best thing ending just before here*. Recognising the shape is more useful than memorising the four lines.
| Problem | What `endingHere` means |
|---|---|
| Maximum sub-array sum | best sum ending at $i$ |
| Maximum product sub-array | best and worst product ending at $i$ |
| Best time to buy and sell stock | best profit if we sell on day $i$ |
| Longest increasing run | length of the run ending at $i$ |
| Maximum circular sub-array sum | Kadane twice: max, and total minus min |
| House robber | best loot using houses up to $i$ |

:::insight The shape in general terms
Define a quantity that depends on **position $i$ and ends there**. Find a rule
expressing it from the value at $i-1$. Keep a single running variable, and a
separate `best`.

That is also the definition of one-dimensional dynamic programming — Kadane is
usually a student's first DP algorithm, taught before the name. If the DP
chapters of a later course feel sudden, come back and re-read this one.
:::

### Best time to buy and sell stock

The same shape, in different clothes.

```cpp title="Buy once, sell once, maximise the profit"
#include <algorithm>
#include <climits>
#include <iostream>
#include <vector>

int maxProfit(const std::vector<int>& price) {
    int cheapest = INT_MAX, best = 0;
    for (int p : price) {
        cheapest = std::min(cheapest, p);          // best day to have bought
        best = std::max(best, p - cheapest);       // profit if we sell today
    }
    return best;
}

int main() {
    std::cout << maxProfit({7, 1, 5, 3, 6, 4}) << "\n";
    std::cout << maxProfit({7, 6, 4, 3, 1})    << "\n";
    std::cout << maxProfit({2, 4, 1})          << "\n";
    return 0;
}
```

```text nonum
5
0
2
```

`best` is *"the best profit achievable selling on this day"* — which is exactly
`endingHere`. The running state is the cheapest price so far instead of a
running sum, but the structure is identical. Here 0 is the right initial value,
because you are allowed not to trade at all.

:::recap Chapter 16 in six lines
- Ask *"what is the best sub-array **ending here**?"* — that question removes the
  outer loop.
- `endingHere = max(v[i], endingHere + v[i])`: extend if the running sum helps,
  restart if it does not.
- Restarting happens exactly when the running sum has gone negative.
- Initialise from `v[0]`, not 0, unless the empty sub-array is explicitly
  allowed.
- To report the indices, update `start` only on a restart and copy it only on a
  new best.
- Products need **two** running values, because a negative element swaps the
  largest and smallest.
:::

:::exercise Practise
1. Trace Kadane on `{5, -2, 3}` and on `{-1, -2, -3}`. Which rows restart?
2. Modify Kadane to allow the empty sub-array (answer 0 for all-negative input).
   Which two lines change?
3. Maximum sum of a **circular** sub-array, where the sub-array may wrap around
   the end. (Hint: either it does not wrap — plain Kadane — or it does, in which
   case the elements *not* taken form a contiguous minimum sub-array. What is the
   edge case when every element is negative?)
4. Longest increasing contiguous run. What is `endingHere` here, and what is the
   restart condition?
5. House robber: maximise the sum of a subset with no two adjacent elements.
   Define `endingHere` carefully — you will need two variables.
6. Explain, with `{-2, 3, -4}`, why maximum product needs both `hi` and `lo`.
7. Buy and sell stock with **two** transactions allowed. What does the running
   state become?
8. Why is Kadane often called the simplest example of dynamic programming? State
   the sub-problem and the recurrence explicitly.
:::
