# Advanced Array Problems
@short: Advanced Problems
@subtitle: Four problems that reward thinking and punish memorisation
@tier: advanced
@prereq: Chapter 19
@blurb: These four are the ones that separate candidates. Each has a short solution that looks obvious once seen and is almost impossible to guess — and in every case there is a derivation that makes it inevitable rather than magical. Trapping Rain Water in particular is worth an hour of your life, because the reasoning behind its two-pointer solution is the most transferable argument in this book.
@objectives:
- Search a rotated sorted array in $O(\log n)$ by deciding which half is sorted
- Find the first and last position of a value with two modified binary searches
- Solve Trapping Rain Water four ways, and derive the two-pointer argument
- Solve maximum product sub-array, and say why it needs two running values
- Explain, for each, why the obvious solution fails and what replaces it

## 1. Search in a rotated sorted array

:::definition The problem
A sorted array was rotated at some unknown pivot: `{4,5,6,7,0,1,2}`. Find a
target in $O(\log n)$. All values are distinct.
:::

**Why the obvious thing fails.** Plain binary search compares the target with
`v[mid]` and concludes which side to go. Here that conclusion is invalid: the
array is not sorted, so `v[mid] < target` tells you nothing about where the
target is.

:::insight One half is always properly sorted
Cut a rotated sorted array anywhere. The rotation point lies in exactly one of
the two halves — so **the other half is an ordinary sorted array**.

Which one? Compare `v[lo]` with `v[mid]`:
- `v[lo] <= v[mid]` → the **left** half is sorted.
- otherwise → the **right** half is sorted.

Once you know which half is sorted, you can test membership in it reliably,
because within a sorted range a simple range check is exact:
*is `v[lo] <= target < v[mid]`?*

- **Yes** → the target is in the sorted half; search there.
- **No** → it can only be in the other half; search there instead.

Either way, half the array is eliminated, so the whole thing is $O(\log n)$.
:::

@fig: pa_rotated | 176 | A rotated sorted array cut at the midpoint. Whichever side does not contain the rotation point is a plain sorted range, and inside a sorted range a range check settles the question exactly.

```cpp title="Search in a rotated sorted array, O(log n)"
#include <iostream>
#include <vector>

int searchRotated(const std::vector<int>& v, int target) {
    int lo = 0, hi = (int)v.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (v[mid] == target) return mid;

        if (v[lo] <= v[mid]) {                        // LEFT half is sorted
            if (v[lo] <= target && target < v[mid]) hi = mid - 1;
            else                                    lo = mid + 1;
        } else {                                      // RIGHT half is sorted
            if (v[mid] < target && target <= v[hi])  lo = mid + 1;
            else                                     hi = mid - 1;
        }
    }
    return -1;
}

int main() {
    std::vector<int> v = {4, 5, 6, 7, 0, 1, 2};
    std::cout << searchRotated(v, 0) << "\n";
    std::cout << searchRotated(v, 4) << "\n";
    std::cout << searchRotated(v, 3) << "\n";
    std::cout << searchRotated({1}, 1)    << "\n";
    std::cout << searchRotated({3, 1}, 1) << "\n";
    return 0;
}
```

```text nonum
4
0
-1
0
1
```

**Cost.** $O(\log n)$ time, $O(1)$ space.

:::pitfall The three details that break this
**`v[lo] <= v[mid]`, not `<`.** When `lo == mid` (a two-element range) the two
are equal, and `<` would send you down the wrong branch. Test `{3, 1}` searching
for 1 — it is the smallest input that catches this.

**The range checks must use the right endpoints.** The left-sorted branch checks
against `v[lo]` and `v[mid]`; the right-sorted branch checks against `v[mid]`
and `v[hi]`. Mixing them up produces code that works on half the inputs.

**Duplicates break the whole argument.** With `{1,1,1,0,1}`, `v[lo] == v[mid]`
tells you nothing about which half is sorted. The standard fix is: when
`v[lo] == v[mid] == v[hi]`, increment `lo` and decrement `hi` and try again —
which degrades the worst case to $O(n)$. If the problem allows duplicates, say
this out loud; it is the point of the variant.
:::

**Next.** Find the **minimum** of a rotated sorted array in $O(\log n)$. The
same "which half is sorted" question, with a simpler answer.

## 2. First and last position of an element

**Problem.** In a sorted array with duplicates, return the first and last index
of a target, or `{-1, -1}`.

**Think.** Covered in Chapter 12: on a match, record the index and keep
searching — leftwards for the first, rightwards for the last.

**Cost.** $O(\log n)$ for both, $O(1)$ space.

**Watch for.** Scanning outwards from a match found by plain binary search is
tempting and is $O(n)$ in the worst case — on an array that is entirely the
target value, it scans everything. Two modified binary searches stay logarithmic
whatever the input.

In production you would write `std::equal_range`, which returns both bounds in
one call.

## 3. Trapping Rain Water

:::definition The problem
Each element is the height of a bar of width 1. After rain, how much water is
trapped between the bars?

`{0,1,0,2,1,0,1,3,2,1,2,1}` → **6** units.
:::

@fig: pa_rain_water | 186 | Trapping Rain Water. Above each bar, the water level is set by the **shorter** of the tallest bar to its left and the tallest bar to its right. Subtract the bar's own height and you have that column's contribution.

### Step 1: solve one column

Forget the whole array. Ask about a single position $i$: how much water sits
**directly above bar $i$**?

Water at $i$ is held in by the tallest bar somewhere to its left and the tallest
bar somewhere to its right. The water level is the **lower** of those two — the
shorter wall is where it would spill over. So:

$$\text{water}[i] = \max\big(0,\; \min(\text{maxLeft}[i],\, \text{maxRight}[i]) - h[i]\big)$$

The $\max(0, \cdot)$ handles the case where the bar is itself the tallest, so
nothing sits on it.

**That formula is the entire problem.** Everything that follows is about
computing it efficiently.

### Step 2: four implementations

**A. Brute force — $O(n^2)$.** For each $i$, scan left for the maximum, scan
right for the maximum, apply the formula.

**B. Precomputed arrays — $O(n)$ time, $O(n)$ space.** The scans repeat work, so
precompute `maxLeft` and `maxRight` with two passes — prefix maxima, exactly
Chapter 11's idea with `max` instead of `+`.

**C. Two pointers — $O(n)$ time, $O(1)$ space.** The clever one, below.

**D. Monotonic stack — $O(n)$ time, $O(n)$ space.** Fills the water in
horizontal layers instead of vertical columns. Correct and elegant; it is not
simpler, and the two-pointer argument generalises better.

```cpp title="B — precomputed prefix maxima, the clearest O(n) solution"
#include <algorithm>
#include <iostream>
#include <vector>

long long trapTwoArrays(const std::vector<int>& h) {
    int n = (int)h.size();
    if (n < 3) return 0;                       // need a wall on each side
    std::vector<int> maxLeft(n), maxRight(n);

    maxLeft[0] = h[0];
    for (int i = 1; i < n; ++i) maxLeft[i] = std::max(maxLeft[i - 1], h[i]);

    maxRight[n - 1] = h[n - 1];
    for (int i = n - 2; i >= 0; --i) maxRight[i] = std::max(maxRight[i + 1], h[i]);

    long long total = 0;
    for (int i = 0; i < n; ++i)
        total += std::min(maxLeft[i], maxRight[i]) - h[i];
    return total;
}

int main() {
    std::cout << trapTwoArrays({0,1,0,2,1,0,1,3,2,1,2,1}) << "\n";
    std::cout << trapTwoArrays({4,2,0,3,2,5})             << "\n";
    std::cout << trapTwoArrays({3,2,1})                   << "\n";
    std::cout << trapTwoArrays({})                        << "\n";
    return 0;
}
```

```text nonum
6
9
0
0
```

Note that the final loop needs no `std::max(0, ...)`: since `maxLeft[i]` and
`maxRight[i]` both include `h[i]` itself, their minimum is never below `h[i]`.
Spotting that is a small thing, and noticing *why* it is safe is the kind of
reasoning that makes code trustworthy.

### Step 3: removing the two arrays

:::insight Why two pointers suffice
Put `left` at 0 and `right` at $n-1$, and carry `maxLeft` and `maxRight` as
running values — but only of the parts already seen.

The problem: at `left`, you know `maxLeft` exactly, but you only know a *lower
bound* on the true maximum to the right. Normally that is not enough.

Here is the resolution. Suppose `maxLeft < maxRight`. The true maximum to the
right of `left` is at least `maxRight`, hence strictly greater than `maxLeft`.
So $\min(\text{true left max}, \text{true right max})$ is `maxLeft` — the
right-hand side cannot be the limiting wall, whatever else is out there.

**The shorter side is always the one you know exactly.** So process that side,
and the uncertainty about the other side never matters.

That is the same argument as "container with most water" in Chapter 9, and it is
worth recognising as a reusable move: *when one of two unknowns cannot possibly
be the binding constraint, you can act on the other with certainty.*
:::

```cpp title="C — two pointers, O(n) time and O(1) space"
#include <iostream>
#include <vector>

long long trap(const std::vector<int>& h) {
    int left = 0, right = (int)h.size() - 1;
    int maxLeft = 0, maxRight = 0;
    long long total = 0;
    while (left < right) {
        if (h[left] < h[right]) {              // the left wall is the shorter
            if (h[left] >= maxLeft) maxLeft = h[left];
            else                    total += maxLeft - h[left];
            ++left;
        } else {                               // the right wall is the shorter
            if (h[right] >= maxRight) maxRight = h[right];
            else                      total += maxRight - h[right];
            --right;
        }
    }
    return total;
}

int main() {
    std::cout << trap({0,1,0,2,1,0,1,3,2,1,2,1}) << "\n";
    std::cout << trap({4,2,0,3,2,5})             << "\n";
    std::cout << trap({3,2,1})                   << "\n";
    std::cout << trap({2,0,2})                   << "\n";
    std::cout << trap({})                        << "\n";
    return 0;
}
```

```text nonum
6
9
0
2
0
```

@tbl: Trapping Rain Water, four ways. All four are worth being able to describe; the two-pointer version is the one to be able to write.
| Approach | Time | Space | Comment |
|---|---|---|---|
| A · rescan for each column | $O(n^2)$ | $O(1)$ | the honest starting point |
| B · two prefix-max arrays | $O(n)$ | $O(n)$ | clearest; derive this first |
| C · two pointers | $O(n)$ | $O(1)$ | the expected answer |
| D · monotonic stack | $O(n)$ | $O(n)$ | fills in horizontal layers |

:::interview How to present this problem
Do **not** jump to the two-pointer version. The strong performance is:

> *"For a single column, the water is $\min(\text{maxLeft}, \text{maxRight}) - h[i]$.
> Naively that is $O(n^2)$. I can precompute both maxima in two passes for
> $O(n)$ time and $O(n)$ space. And I can drop the arrays entirely with two
> pointers, because whichever side is shorter is the side whose maximum I know
> exactly — so its water is already determined."*

That shows the formula, the optimisation, and the insight, in that order. A
candidate who writes the two-pointer code immediately has either seen it before
or is guessing, and the interviewer cannot tell which.
:::

**Watch for.** `n < 3` returns 0 — you need a wall on each side of a gap. The
comparison `h[left] < h[right]` decides which side to process, and getting it
backwards produces answers that are right on symmetric inputs and wrong
otherwise.

## 4. Maximum product sub-array

**Problem.** Largest product of any contiguous non-empty sub-array.
`{2,3,-2,4}` → 6.

**Think.** Covered in Chapter 16. The key observation: a very negative running
product is an asset, because the next negative flips it to a large positive. So
carry both the maximum and the minimum product ending here, and swap them when
the current element is negative.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Zeroes reset both running values — the
`std::max(x, hi * x)` form handles this automatically. Overflow is real:
30 elements of value 10 overflow `int` easily; use `long long` and read the
constraints.

**Next.** Maximum product of a **non-contiguous** subsequence. It becomes a
different problem entirely — count the negatives and the zeroes. Try it.

## Where to go from here

@tbl: These four, and the natural follow-up each one leads to. Working the follow-ups is worth more than finding four new problems.
| Problem | Technique | Natural follow-up |
|---|---|---|
| Search rotated | binary search + which-half-is-sorted | minimum of a rotated array; rotated with duplicates |
| First/last position | two modified binary searches | count occurrences; `equal_range` |
| Trapping Rain Water | per-column formula, then two pointers | largest rectangle in a histogram |
| Max product sub-array | two running values | maximum circular sub-array sum |

:::recap Part IV in five lines
- Every problem here has an $O(n^2)$ solution that is correct. Say it first, then
  improve it.
- The improvement is always one of the ten patterns, not a new idea.
- Constraints are hints: "do not modify the array", "$O(1)$ space", "no
  division" each rule out the easy answer and point at the intended one.
- Derive the formula for a *single position* before worrying about the whole
  array — that is what makes Trapping Rain Water tractable.
- When one of two unknowns cannot be the binding constraint, you may act on the
  other with certainty. That one argument solves three problems in this book.
:::

:::exercise Practise
1. Trace `searchRotated({4,5,6,7,0,1,2}, 0)`. At each step, say which half is
   sorted and why.
2. Find the minimum of a rotated sorted array in $O(\log n)$. What is the
   comparison that drives it?
3. Write Trapping Rain Water approach A, then B, then C, in that order,
   testing each against the others on random inputs.
4. For `{4,2,0,3,2,5}`, compute the water above **each** column by hand using the
   formula, and check that they sum to 9.
5. Implement Trapping Rain Water with a monotonic stack. How do the layers it
   fills differ from the columns of the other three methods?
6. Why does `searchRotated` degrade to $O(n)$ when duplicates are allowed?
   Construct the worst case.
7. Largest rectangle in a histogram: for each bar, find how far it can extend
   left and right before hitting a shorter bar. Which of the four Trapping Rain
   Water approaches does this most resemble?
8. For maximum product sub-array, construct an input where the answer uses an
   even number of negatives and one where it must stop before a zero.
:::
