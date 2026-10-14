# Pattern 4: Prefix Sums
@short: Prefix Sums
@subtitle: Pay O(n) once so every range question afterwards costs O(1)
@tier: core
@prereq: Chapters 3 and 10
@blurb: A prefix sum array stores the running total up to each position. From it, the sum of any range comes out as a single subtraction — which turns a stream of range queries from $O(n)$ each into $O(1)$ each, and turns the sub-array-sum problems that sliding windows cannot handle into one-pass hash-map problems. This is the clearest time-for-space trade in the book.
@objectives:
- Build a prefix sum array and explain the off-by-one that the extra leading zero removes
- Answer any range-sum query in $O(1)$
- Explain when prefix sums beat a sliding window, and why
- Solve "sub-array sum equals K" in $O(n)$ with a hash map
- Use the same idea for counts, not just sums
- Extend prefix sums to two dimensions

## The problem it solves

You are given an array and then asked, many times: *what is the sum of the
elements from index $i$ to index $j$?*

The obvious answer loops from $i$ to $j$: $O(j - i)$ per query, so $O(n)$ in the
worst case. With $q$ queries that is $O(n \cdot q)$. For $n = 10^5$ and
$q = 10^5$ that is $10^{10}$ operations — far too slow.

:::insight The trade
Spend $O(n)$ time and $O(n)$ space **once**, up front. Every query afterwards
costs $O(1)$.

Total: $O(n + q)$ instead of $O(n \cdot q)$. For the numbers above, $2 \times
10^5$ instead of $10^{10}$ — fifty thousand times less work.

This shape — *precompute once, answer cheaply forever* — is one of the most
valuable ideas in algorithms, and prefix sums are its simplest instance.
:::

## Building the array

:::definition Prefix sum
`prefix[i]` is the sum of the first $i$ elements, that is
`v[0] + v[1] + ... + v[i-1]`.

Note that `prefix` has $n + 1$ entries, and `prefix[0] = 0` — the sum of no
elements. That leading zero looks like a detail. It is the difference between
code with an edge case and code without one.
:::

@fig: ps_build | 158 | Building the prefix array. Each entry is the previous entry plus one element, so the whole array is built in one pass. The leading zero means `prefix[i]` can always be read as "everything strictly before index $i$".

```cpp title="Building prefix sums"
#include <iostream>
#include <vector>

std::vector<long long> buildPrefix(const std::vector<int>& v) {
    std::vector<long long> prefix(v.size() + 1, 0);   // n+1 entries, p[0] = 0
    for (int i = 0; i < (int)v.size(); ++i)
        prefix[i + 1] = prefix[i] + v[i];
    return prefix;
}

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5};
    auto p = buildPrefix(v);
    for (long long x : p) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
0 3 4 8 9 14 
```

Read the output against the input: `0`, then $3$, then $3{+}1 = 4$, then
$3{+}1{+}4 = 8$, then $9$, then $14$. Each entry is the total of everything
before that point.

## The range-sum formula

@fig: ps_range | 155 | The range-sum subtraction. The sum of `v[i..j]` is everything up to and including $j$, minus everything strictly before $i$. The overlapping part cancels exactly.

:::definition Range sum in O(1)
$$\text{sum}(i, j) \;=\; \text{prefix}[j+1] - \text{prefix}[i]$$

for the inclusive range `v[i..j]`.

**Why it works:** `prefix[j+1]` is everything up to and including index $j$.
`prefix[i]` is everything strictly before index $i$. Subtracting removes
precisely the part you did not ask for.
:::

```cpp title="Range sum queries in O(1) each"
#include <iostream>
#include <vector>

class RangeSum {
public:
    explicit RangeSum(const std::vector<int>& v) : prefix(v.size() + 1, 0) {
        for (int i = 0; i < (int)v.size(); ++i)
            prefix[i + 1] = prefix[i] + v[i];
    }
    // Inclusive sum of v[i..j]. O(1).
    long long query(int i, int j) const { return prefix[j + 1] - prefix[i]; }

private:
    std::vector<long long> prefix;
};

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5};
    RangeSum rs(v);
    std::cout << rs.query(1, 3) << "\n";   // 1 + 4 + 1
    std::cout << rs.query(0, 4) << "\n";   // everything
    std::cout << rs.query(2, 2) << "\n";   // a single element
    std::cout << rs.query(0, 0) << "\n";
    return 0;
}
```

```text nonum
6
14
4
3
```

Check `query(2, 2)`: `prefix[3] - prefix[2]` is $8 - 4 = 4$, which is `v[2]`.
A single-element range works with no special case, and that is the leading zero
earning its place.

:::pitfall The version without the leading zero
A very common alternative defines `prefix[i]` as the sum **up to and
including** `v[i]`, with `prefix[0] = v[0]`. The range formula then becomes

$$\text{sum}(i, j) = \text{prefix}[j] - \text{prefix}[i-1]$$

which is wrong when $i = 0$, because `prefix[-1]` does not exist. You must write

```cpp nonum frag
long long sum = (i == 0) ? prefix[j] : prefix[j] - prefix[i - 1];
```

Both conventions are correct. The $n+1$ version needs no `if`, and an `if` you
never write is an `if` you cannot get wrong. Use the leading zero.
:::

## Where prefix sums beat sliding windows

Chapter 10 ended with a warning: sliding windows break when the array contains
negative numbers, because growing the window no longer increases the sum
monotonically.

Prefix sums do not care. They make no assumption about signs at all, because
they never rely on growing or shrinking anything.

### Sub-array sum equals K

:::definition The problem
Count the contiguous sub-arrays whose sum is exactly $K$. Values may be
negative.

`{1, 2, 3}` with $K = 3$ → 2 (the sub-arrays `{1,2}` and `{3}`).
`{1, -1, 0}` with $K = 0$ → 3 (the sub-arrays `{1,-1}`, `{1,-1,0}` and `{0}`).
:::

### From brute force to the insight

Brute force tries every $(i, j)$ pair: $O(n^2)$, and with a prefix array each
sum is $O(1)$, so $O(n^2)$ overall. Better than $O(n^3)$, still too slow.

Now the key rearrangement:

:::insight The rearrangement that makes it linear
A sub-array ending at index $j$ with sum $K$ means

$$\text{prefix}[j+1] - \text{prefix}[i] = K$$

Rearrange for the thing you are looking for:

$$\text{prefix}[i] = \text{prefix}[j+1] - K$$

So as you sweep $j$ from left to right, the question *"how many sub-arrays
ending here sum to $K$?"* becomes *"how many earlier prefix values equal
`current - K`?"*

That is a **lookup**, and a hash map answers it in $O(1)$. One pass, counting
prefix values as you go, and the whole problem is $O(n)$.
:::

@fig: ps_subarray_k | 170 | Sub-array sum equals K. At each position, the current running total is known; subtracting $K$ gives the earlier running total we would need to have seen. The hash map says how many times that value has occurred, and each occurrence is one qualifying sub-array.

### The trace

`{1, 2, 3}`, $K = 3$. `seen` maps a prefix value to how many times it has
occurred, and starts as `{0: 1}` — the empty prefix, which must be counted or
sub-arrays starting at index 0 are missed.

@tbl: Tracing sub-array sum equals K. The map is consulted *before* the current prefix is inserted, so a sub-array can never be matched against itself.
| `j` | `v[j]` | `running` | need `running - K` | found | `count` | `seen` afterwards |
|---|---|---|---|---|---|---|
| start | — | 0 | — | — | 0 | `{0:1}` |
| 0 | 1 | 1 | $1 - 3 = -2$ | 0 | 0 | `{0:1, 1:1}` |
| 1 | 2 | 3 | $3 - 3 = 0$ | 1 | 1 | `{0:1, 1:1, 3:1}` |
| 2 | 3 | 6 | $6 - 3 = 3$ | 1 | 2 | `{0:1, 1:1, 3:1, 6:1}` |

```cpp title="Sub-array sum equals K, O(n), works with negatives"
#include <iostream>
#include <unordered_map>
#include <vector>

int subarraySum(const std::vector<int>& v, int k) {
    std::unordered_map<long long, int> seen;
    seen[0] = 1;                        // the empty prefix, before any element
    long long running = 0;
    int count = 0;
    for (int x : v) {
        running += x;
        auto it = seen.find(running - k);
        if (it != seen.end()) count += it->second;   // look up BEFORE inserting
        ++seen[running];
    }
    return count;
}

int main() {
    std::cout << subarraySum({1, 2, 3}, 3)       << "\n";
    std::cout << subarraySum({1, 1, 1}, 2)       << "\n";
    std::cout << subarraySum({1, -1, 0}, 0)      << "\n";
    std::cout << subarraySum({3, 4, 7, 2}, 7)    << "\n";
    std::cout << subarraySum({1, 2, 3}, 100)     << "\n";
    return 0;
}
```

```text nonum
2
2
3
2
0
```

$O(n)$ time, $O(n)$ space. A sliding window cannot solve this at all once
negatives are allowed.

:::pitfall The two bugs that make this problem hard
**Forgetting `seen[0] = 1`.** Without it, any sub-array that starts at index 0
is missed, because the prefix it needs to subtract is the empty one.
`{3}` with $K = 3$ would return 0.

**Inserting before looking up.** If you write `++seen[running];` first and then
look up `running - k`, then when $K = 0$ the current prefix matches itself and
every position contributes a spurious count. Look up first, insert second.
:::

## Prefix counts, not just sums

The idea generalises to anything you can accumulate.

```cpp title="Prefix counts: how many even numbers in a range?"
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {4, 7, 2, 9, 6, 1};
    std::vector<int> evens(v.size() + 1, 0);
    for (int i = 0; i < (int)v.size(); ++i)
        evens[i + 1] = evens[i] + (v[i] % 2 == 0 ? 1 : 0);

    // evens in v[1..4] = 7, 2, 9, 6  ->  2 of them
    std::cout << evens[5] - evens[1] << "\n";
    // evens in the whole array
    std::cout << evens[6] - evens[0] << "\n";
    return 0;
}
```

```text nonum
2
3
```

The same subtraction works for *any* quantity that adds up across a range:
counts of a particular value, counts matching a predicate, XOR totals (where
subtraction becomes XOR again), and products if there are no zeroes.

## Two-dimensional prefix sums

For grids, the same idea gives the sum of any rectangle in $O(1)$.

@fig: ps_2d | 168 | Inclusion–exclusion on a grid. Taking the big rectangle and removing the two overhanging strips subtracts their shared corner twice, so it has to be added back once. Four array reads, whatever the size of the rectangle.

:::definition The 2-D range formula
With `P[r][c]` the sum of the rectangle from $(0,0)$ to $(r-1, c-1)$, the sum of
the rectangle with corners $(r_1, c_1)$ and $(r_2, c_2)$ inclusive is

$$P[r_2{+}1][c_2{+}1] - P[r_1][c_2{+}1] - P[r_2{+}1][c_1] + P[r_1][c_1]$$

The final $+$ is **inclusion–exclusion**: the top-left region was removed twice,
once by each of the two subtractions, so it must be restored once.
:::

```cpp title="2-D prefix sums: any rectangle in O(1)"
#include <iostream>
#include <vector>

int main() {
    std::vector<std::vector<int>> g = {{1, 2, 3},
                                       {4, 5, 6},
                                       {7, 8, 9}};
    int R = 3, C = 3;
    std::vector<std::vector<long long>> P(R + 1, std::vector<long long>(C + 1, 0));
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c)
            P[r + 1][c + 1] = g[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c];

    auto rect = [&](int r1, int c1, int r2, int c2) {
        return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1];
    };

    std::cout << rect(0, 0, 2, 2) << "\n";   // whole grid: 45
    std::cout << rect(1, 1, 2, 2) << "\n";   // 5+6+8+9
    std::cout << rect(0, 0, 0, 0) << "\n";   // just g[0][0]
    return 0;
}
```

```text nonum
45
28
1
```

Building `P` is $O(R \cdot C)$; each query is $O(1)$, with four reads regardless
of the rectangle's size.

## Choosing between the three range techniques

@tbl: Which tool for which range problem. Read this table as a decision procedure when a problem mentions sub-arrays.
| Situation | Technique | Time | Space |
|---|---|---|---|
| Many range-sum queries, array never changes | prefix sums | $O(n)$ build, $O(1)$ query | $O(n)$ |
| Longest/shortest window, all values non-negative | sliding window | $O(n)$ | $O(1)$ |
| Count sub-arrays with an exact sum, values may be negative | prefix + hash map | $O(n)$ | $O(n)$ |
| Range sums **and** the array changes between queries | Fenwick / segment tree | $O(\log n)$ each | $O(n)$ |
| Maximum sub-array sum | Kadane (Chapter 16) | $O(n)$ | $O(1)$ |

The fourth row is outside this book; it is mentioned so you know that prefix
sums have a limit. **Prefix sums assume the array is frozen.** One update to
`v[i]` invalidates every prefix entry from $i$ onwards, so rebuilding is $O(n)$.
If updates are frequent, you need a different structure.

:::recap Chapter 11 in six lines
- `prefix[i]` is the sum of everything strictly before index $i$, and
  `prefix[0] = 0`.
- $\text{sum}(i, j) = \text{prefix}[j{+}1] - \text{prefix}[i]$ — one subtraction,
  $O(1)$.
- The leading zero removes the $i = 0$ special case. Always use it.
- Prefix sums work with negative numbers; sliding windows do not.
- "Sub-array sums to $K$" becomes "has prefix value $\text{current} - K$ been
  seen?" — a hash-map lookup, so $O(n)$.
- Seed the map with `{0: 1}`, and look up before you insert.
:::

:::exercise Practise
1. Build the prefix array for `{5, -2, 7, 1}` by hand. Then use it to find the
   sum of `v[1..3]`.
2. Why does `prefix` have $n+1$ entries rather than $n$? Give the specific query
   that breaks without the extra entry.
3. Find the **longest** sub-array with sum exactly $K$ (not the count). What
   must the hash map store instead of a count, and why do you keep only the
   *earliest* occurrence of each prefix value?
4. Count the sub-arrays with an **even** sum. (Hint: you do not need the sums
   themselves, only their parity. How many distinct prefix values are there
   then?)
5. Given an array of 0s and 1s, find the longest sub-array with equal numbers of
   each. (Hint: map 0 to $-1$, then find the longest sub-array with sum 0.)
6. Explain why `subarraySum` must look up before inserting, using $K = 0$ and
   the input `{0}` as your example.
7. Build a 2-D prefix array for a $3 \times 3$ grid of all 1s and use it to find
   the sum of the middle $2 \times 2$ square. Verify the inclusion–exclusion by
   hand.
8. An array changes between queries. Explain why prefix sums are the wrong tool,
   and state what the rebuild would cost.
:::
