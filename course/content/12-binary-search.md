# Pattern 5: Binary Search
@short: Binary Search
@subtitle: Twenty steps to find one item among a million
@tier: core
@prereq: Chapters 3 and 4
@blurb: Binary search is the highest-value algorithm in this book: four lines of code that turn a million comparisons into twenty. It is also the algorithm most people write *almost* correctly — the off-by-one that loops forever, the overflow that appears only on huge inputs, the variant that finds *an* answer rather than the *first* one. This chapter writes it once, proves why it terminates, and then derives the two variants you actually need in interviews.
@objectives:
- Implement binary search correctly, and say why each line is as it is
- State the loop invariant and use it to prove the algorithm cannot miss an element
- Explain why `mid = lo + (hi - lo) / 2` and not `(lo + hi) / 2`
- Avoid the infinite loop and the off-by-one, and know which variant causes which
- Find the **first** and **last** occurrence of a repeated value
- Recognise "binary search on the answer", where the array is not what you search
- Use `std::lower_bound` and `std::upper_bound` correctly

## The guessing game

I am thinking of a number from 1 to 1000. You may ask "is it higher or lower
than $x$?" How many questions do you need?

If you guess 1, then 2, then 3, you may need 1000 questions. If you always
guess the **middle**, each answer eliminates half the remaining possibilities,
and you need at most 10 — because $2^{10} = 1024 > 1000$.

:::definition Binary search
Given a **sorted** array, repeatedly compare the target with the middle element
of the region still under consideration, and discard the half that cannot
contain it.

Each comparison halves the search space, so the number of comparisons is
$\lceil \log_2 n \rceil$.
:::

@fig: bs_halving | 160 | Searching for 23 in a sorted array of 10. Three comparisons settle it. On a million elements it would be twenty, and on a billion, thirty.

| $n$ | Linear search (worst) | Binary search (worst) |
|---:|---:|---:|
| 100 | 100 | 7 |
| 10,000 | 10,000 | 14 |
| 1,000,000 | 1,000,000 | 20 |
| 1,000,000,000 | 1,000,000,000 | 30 |

That last row is the one to remember. A billion elements, thirty comparisons.

## The code, line by line

```cpp title="Binary search — the canonical form"
#include <iostream>
#include <vector>

// Returns an index of target, or -1 if it is absent. v must be sorted.
int binarySearch(const std::vector<int>& v, int target) {
    int lo = 0, hi = (int)v.size() - 1;      // inclusive bounds: [lo, hi]
    while (lo <= hi) {                       // while the region is non-empty
        int mid = lo + (hi - lo) / 2;        // midpoint, overflow-safe
        if (v[mid] == target) return mid;
        if (v[mid] < target) lo = mid + 1;   // target must be to the RIGHT
        else                 hi = mid - 1;   // target must be to the LEFT
    }
    return -1;
}

int main() {
    std::vector<int> v = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
    std::cout << binarySearch(v, 23) << "\n";
    std::cout << binarySearch(v, 2)  << "\n";
    std::cout << binarySearch(v, 91) << "\n";
    std::cout << binarySearch(v, 50) << "\n";
    std::cout << binarySearch({}, 1) << "\n";
    return 0;
}
```

```text nonum
5
0
9
-1
-1
```

Now the five decisions in that function, each of which has a wrong alternative
that *almost* works.

### Decision 1: `hi = size() - 1`, and the bounds are inclusive

The region under consideration is `v[lo .. hi]` **including both ends**. That
choice forces the other decisions, so make it consciously and stick to it. (The
alternative — half-open `[lo, hi)` with `hi = size()` — is equally valid, and
mixing the two is how people produce bugs.)

### Decision 2: `while (lo <= hi)`

With inclusive bounds, `lo == hi` describes a region containing **one**
element, which still has to be examined. Writing `while (lo < hi)` skips it, so
searching for the only element in a one-element array returns $-1$.

### Decision 3: `mid = lo + (hi - lo) / 2`

The natural `(lo + hi) / 2` is correct mathematics and wrong code.

:::pitfall The overflow that took nine years to find
If `lo` and `hi` are both near `INT_MAX`, `lo + hi` overflows. Signed overflow
in C++ is undefined behaviour; in practice you get a large negative number, and
`v[mid]` reads far outside the array.

`lo + (hi - lo) / 2` is algebraically identical — $lo + \frac{hi - lo}{2} =
\frac{lo + hi}{2}$ — but `hi - lo` is at most the array length, so nothing can
overflow.

This bug sat undetected in the Java standard library's binary search, and in
the binary search of the standard reference textbook, for about nine years. It
only shows up on arrays of more than a billion elements, which nobody had in
1986. Write it the safe way out of habit.
:::

### Decision 4: `mid + 1` and `mid - 1`, never plain `mid`

We have just established that `v[mid]` is not the target. Leaving `mid` inside
the region means it may be examined again — and if the region never shrinks,
the loop never ends.

:::pitfall The infinite loop
```cpp nonum frag
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (v[mid] == target) break;
    if (v[mid] < target) lo = mid;      // BUG: should be mid + 1
    else                 hi = mid;      // BUG: should be mid - 1
}
```
With `lo = 0, hi = 1`, `mid` is 0. If `v[0] < target` we set `lo = 0` — which is
what it already was. Same `lo`, same `hi`, same `mid`, forever.

**The test that catches it:** run your binary search on a **two-element** array
searching for the larger element. Almost every binary search bug shows up at
$n = 2$, and the test takes ten seconds to write.
:::

### Decision 5: integer division rounds down

`(hi - lo) / 2` truncates, so `mid` is the **left** of the two middles when the
region has even length. That is not arbitrary: combined with `lo = mid + 1` it
guarantees the region strictly shrinks every iteration, which is the
termination proof. We will see in a moment that one variant needs the *other*
rounding, and why.

## Why it cannot miss an element

:::definition The loop invariant
**If the target is in the array at all, it is inside `v[lo .. hi]`.**

This is true at the start, because `[0, n-1]` is the whole array. Each step
preserves it: if `v[mid] < target`, then by sortedness every element at index
$\le mid$ is also $< target$, so the target cannot be there, and discarding
`[lo, mid]` cannot discard it. The mirror argument covers the other branch.

When the loop ends, `lo > hi`, so the region is empty. The invariant then says
the target is inside an empty region — which is only possible if it was never
in the array. Hence `return -1` is correct.
:::

An invariant plus a decreasing quantity is how you *prove* a loop, and it is
worth saying out loud in an interview: *"the invariant is that the answer, if it
exists, is in `[lo, hi]`; each iteration halves that range, so it terminates in
$\log n$ steps."*

@fig: bs_invariant | 150 | The invariant in pictures. The shaded region is everywhere the target could still be. It only ever shrinks, it never loses the target, and when it becomes empty the answer is settled.

## Variant: first and last occurrence

Plain binary search returns *an* index of the target. With duplicates, which
one it returns is unpredictable.

:::definition The problem
In `{5, 7, 7, 7, 8, 8, 10}`, the value 7 occupies indices 1, 2 and 3. Find the
**first** and the **last** index, or $-1$ if absent.
:::

The fix is small but subtle: **when you find the target, do not stop.** Record
it and keep searching in the half that could hold an earlier (or later)
occurrence.

@fig: bs_first_last | 164 | Finding the first and last occurrence. On a match, the first-occurrence search continues leftwards and the last-occurrence search continues rightwards. The recorded answer is overwritten only by a better one.

```cpp title="First and last occurrence of a value"
#include <iostream>
#include <vector>

int firstOccurrence(const std::vector<int>& v, int target) {
    int lo = 0, hi = (int)v.size() - 1, answer = -1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (v[mid] == target) {
            answer = mid;                // record it...
            hi = mid - 1;                // ...then keep looking LEFT
        } else if (v[mid] < target) {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return answer;
}

int lastOccurrence(const std::vector<int>& v, int target) {
    int lo = 0, hi = (int)v.size() - 1, answer = -1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (v[mid] == target) {
            answer = mid;                // record it...
            lo = mid + 1;                // ...then keep looking RIGHT
        } else if (v[mid] < target) {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return answer;
}

int main() {
    std::vector<int> v = {5, 7, 7, 7, 8, 8, 10};
    std::cout << firstOccurrence(v, 7) << " " << lastOccurrence(v, 7) << "\n";
    std::cout << firstOccurrence(v, 8) << " " << lastOccurrence(v, 8) << "\n";
    std::cout << firstOccurrence(v, 5) << " " << lastOccurrence(v, 5) << "\n";
    std::cout << firstOccurrence(v, 9) << " " << lastOccurrence(v, 9) << "\n";
    // count of a value, in O(log n)
    int f = firstOccurrence(v, 7), l = lastOccurrence(v, 7);
    std::cout << "count of 7 = " << (f == -1 ? 0 : l - f + 1) << "\n";
    return 0;
}
```

```text nonum
1 3
4 5
0 0
-1 -1
count of 7 = 3
```

That last line is the real pay-off. Counting occurrences by scanning is $O(n)$;
with two binary searches it is $O(\log n)$. On a sorted array of ten million
elements that is 46 comparisons instead of ten million.

## Binary search on the answer

Here is the idea that turns binary search from a lookup into a general
technique, and it is what separates a mid-level answer from a strong one.

:::insight You are not searching the array — you are searching a *decision*
Binary search needs only one thing: a range of candidate answers, and a
**yes/no test** whose answers are *monotonic* — false, false, false, true, true,
true — so that once it turns true it stays true.

The array itself need not exist. If you can ask *"is an answer of $x$ good
enough?"* and know that a larger $x$ is never worse, you can binary search for
the smallest good $x$ in $O(\log(\text{range}) \times \text{cost of the test})$.
:::

@fig: bs_answer_space | 152 | Binary searching a decision instead of an array. The candidates are all possible answers; the test splits them into a false region and a true region; binary search finds the boundary. The array is only used inside the test.

```cpp title="Integer square root by binary search on the answer"
#include <iostream>

// Largest x with x*x <= n. The test "x*x <= n" is false once and for all
// beyond the answer, which is exactly the monotonicity we need.
int integerSqrt(int n) {
    if (n < 2) return n;
    int lo = 1, hi = n / 2, answer = 1;
    while (lo <= hi) {
        long long mid = lo + (hi - lo) / 2;
        if (mid * mid <= (long long)n) {
            answer = (int)mid;           // good enough — try larger
            lo = (int)mid + 1;
        } else {
            hi = (int)mid - 1;           // too big — try smaller
        }
    }
    return answer;
}

int main() {
    std::cout << integerSqrt(16) << "\n";
    std::cout << integerSqrt(17) << "\n";
    std::cout << integerSqrt(1)  << "\n";
    std::cout << integerSqrt(0)  << "\n";
    std::cout << integerSqrt(2147395600) << "\n";
    return 0;
}
```

```text nonum
4
4
1
0
46340
```

No array was searched. The "array" was the conceptual list $1, 2, 3, \dots$ and
the test was `mid * mid <= n`.

:::interview The sentence that unlocks these problems
Whenever a problem asks for *"the minimum X such that …"* or *"the maximum X
such that …"*, ask yourself:

> *"If I guess a value of X, can I check in reasonable time whether it works?
> And if X works, does every larger X also work?"*

If both answers are yes, binary search the answer. This single observation
solves "minimum capacity to ship packages in D days", "split array largest
sum", "Koko eating bananas", "minimum days to make bouquets" and a dozen other
problems that look nothing like searching.
:::

## The standard library

You rarely need to hand-write binary search in production.

```cpp title="std::lower_bound, upper_bound, binary_search, equal_range"
#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {5, 7, 7, 7, 8, 8, 10};

    auto lb = std::lower_bound(v.begin(), v.end(), 7);   // FIRST >= 7
    auto ub = std::upper_bound(v.begin(), v.end(), 7);   // FIRST > 7

    std::cout << "lower_bound(7) index = " << (lb - v.begin()) << "\n";
    std::cout << "upper_bound(7) index = " << (ub - v.begin()) << "\n";
    std::cout << "count of 7           = " << (ub - lb) << "\n";
    std::cout << "contains 8?          = " << std::binary_search(v.begin(), v.end(), 8) << "\n";
    std::cout << "contains 9?          = " << std::binary_search(v.begin(), v.end(), 9) << "\n";

    // Where would 9 be inserted to keep the array sorted?
    std::cout << "insert 9 at index    = "
              << (std::lower_bound(v.begin(), v.end(), 9) - v.begin()) << "\n";
    return 0;
}
```

```text nonum
lower_bound(7) index = 1
upper_bound(7) index = 4
count of 7           = 3
contains 8?          = 1
contains 9?          = 0
insert 9 at index    = 6
```

@tbl: The standard library's binary searches. `lower_bound` is the one you will use most, because it answers both "where is it?" and "where would it go?" with the same call.
| Call | Returns | Use it for |
|---|---|---|
| `lower_bound(b, e, x)` | first element $\ge x$ | first occurrence; insertion point |
| `upper_bound(b, e, x)` | first element $> x$ | one past the last occurrence |
| `equal_range(b, e, x)` | both of the above | the whole run of equal values |
| `binary_search(b, e, x)` | `bool` | presence only; discards the position |

:::pitfall These are $O(\log n)$ only on random-access containers
On a `std::vector` or an array, `lower_bound` is $O(\log n)$.

On a `std::list` — a linked list — it still performs $O(\log n)$ *comparisons*,
but reaching the middle element requires walking, so the total is $O(n)$. The
algorithm is correct; the data structure cannot support it.

This is the cleanest illustration of the book's central trade-off: **binary
search is an array algorithm.** Chapter 33 returns to exactly why.
:::

## Cost summary

| Operation | Time | Space | Precondition |
|---|---|---|---|
| Binary search | $O(\log n)$ | $O(1)$ | sorted |
| First / last occurrence | $O(\log n)$ | $O(1)$ | sorted |
| Count occurrences | $O(\log n)$ | $O(1)$ | sorted |
| Insertion point | $O(\log n)$ | $O(1)$ | sorted |
| Binary search on the answer | $O(\log R \cdot C)$ | $O(1)$ | monotonic test |
| Sort, then binary search once | $O(n \log n)$ | depends | — |

That last row is a warning: if you will search only once, sorting first is
$O(n \log n)$, which is *worse* than a single $O(n)$ linear scan. Sorting pays
off when you will search many times.

:::recap Chapter 12 in seven lines
- Each comparison halves the region, so $n = 10^9$ needs 30 comparisons.
- Inclusive bounds `[lo, hi]` go with `while (lo <= hi)` and `mid ± 1`. Pick one
  convention and never mix.
- `mid = lo + (hi - lo) / 2` avoids an overflow that hid in standard libraries
  for nine years.
- `lo = mid` or `hi = mid` without the $\pm 1$ gives an infinite loop. Test with
  $n = 2$.
- The invariant — *the answer, if any, is in `[lo, hi]`* — is the proof, and
  worth stating aloud.
- On a match, record and continue to find the **first** or **last** occurrence.
- If a monotonic yes/no test exists, binary search the **answer**, not the array.
:::

:::exercise Practise
1. Trace `binarySearch({1,3,5,7,9,11}, 11)` by hand, writing `lo`, `hi` and
   `mid` each iteration. How many comparisons?
2. Run the same search for a value that is absent, say 6. Where does the loop
   stop, and what are `lo` and `hi` at that moment?
3. Write binary search with **half-open** bounds (`hi = size()`,
   `while (lo < hi)`). Which of the five decisions change?
4. In `firstOccurrence`, why is `hi = mid - 1` after a match correct, rather
   than `hi = mid`? What would `hi = mid` do on a two-element array of equal
   values?
5. Given a sorted array rotated at an unknown point, such as
   `{4,5,6,7,0,1,2}`, find a target in $O(\log n)$. (Hint: one half is always
   properly sorted — work out which, then decide whether the target lies in it.
   Full treatment in Chapter 20.)
6. Find the **peak** of an array that increases and then decreases, in
   $O(\log n)$. What is the monotonic test here? Note that the array is **not**
   sorted — which tells you something about what binary search really needs.
7. "Koko eating bananas": given piles of bananas and $H$ hours, find the
   smallest eating speed $k$ such that all piles can be finished in $H$ hours.
   What is the candidate range, what is the test, and why is it monotonic?
8. Explain why `std::lower_bound` on a `std::list` is $O(n)$ even though it
   makes only $O(\log n)$ comparisons.
:::
