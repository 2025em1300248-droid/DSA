# Pattern 2: Two Pointers
@short: Two Pointers
@subtitle: Two indices, moving with purpose, turning O(n²) into O(n)
@tier: core
@prereq: Chapters 6 and 8
@blurb: The two-pointer pattern replaces a nested loop with two indices that between them cross the array only once. It comes in two shapes — pointers converging from the ends, and pointers chasing each other from the same end — and almost every $O(n)$ solution to a problem that "obviously" needs $O(n^2)$ is one of them. This chapter derives both shapes from brute force, and proves why nothing is missed.
@objectives:
- Recognise the two shapes: converging pointers and same-direction pointers
- Derive the converging solution to Two Sum on a sorted array, and justify it
- Check palindromes and reverse arrays with converging pointers
- Use a read pointer and a write pointer to filter an array in place
- Explain why the pattern is $O(n)$ even though it has two moving indices
- Know the precondition each shape needs, and what breaks without it

## The two shapes

@fig: tp_two_shapes | 160 | The two shapes of the pattern. **Converging**: one pointer at each end, moving towards each other, usually requiring sorted input. **Same direction**: both start at the left, one reads ahead while the other writes behind, requiring nothing.

:::definition The two-pointer pattern
Keep **two indices** into the array and move them according to a rule, so that
between them they traverse the array a constant number of times.

**Converging** (`left` at 0, `right` at $n-1$, moving inwards): used for pair
problems on sorted data, palindromes, reversal, and area problems. Usually
needs sorted or symmetric input.

**Same direction** (`slow`/`write` and `fast`/`read`, both starting at 0): used
for filtering, deduplication, compaction and partitioning. Needs nothing.
:::

How to recognise a two-pointer problem:

| Signal in the problem | Shape to reach for |
|---|---|
| sorted array, and you need a **pair** | converging |
| "is it a palindrome", "mirror", "reverse" | converging |
| "maximum area / water between two lines" | converging |
| "remove / keep / move elements in place" | same direction |
| "partition into two groups" | same direction |
| "$O(1)$ extra space" with an $O(n^2)$ obvious answer | one of the two |

## Shape 1: Converging pointers

### The motivating problem: Two Sum on a sorted array

:::definition The problem
Given a **sorted** array and a target, return the indices of two elements that
add to the target, or report that there is no such pair.

`{2, 7, 11, 15}`, target 9 → indices 0 and 1, because $2 + 7 = 9$.
:::

### Step 1: the brute force

Try every pair.

```cpp title="Brute force: try every pair" frag
for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j)
        if (v[i] + v[j] == target)
            std::cout << i << " " << j;    // found — but only after n²/2 tries
```

Correct, and $O(n^2)$: about $n^2/2$ pairs. For $n = 100{,}000$ that is
$5 \times 10^9$ comparisons — roughly a minute. Too slow.

### Step 2: find the waste

The brute force never uses the fact that the array is **sorted**. That is
always the sign that a better solution exists: an unused precondition is a
wasted asset.

### Step 3: the insight

Put `left` at the smallest element and `right` at the largest, and look at
their sum.

@fig: tp_two_sum | 170 | Two Sum by converging pointers. The sum is too small, so the only way to increase it is to raise the smaller end; the sum is too large, so the only way to decrease it is to lower the larger end. Each comparison eliminates an entire row or column of the brute-force table.

:::insight Why moving a pointer discards nothing
Suppose `v[left] + v[right] < target`.

Consider every pair that uses `left`: its partner can be anything from
`left+1` to `right`. The **largest** such sum is `v[left] + v[right]`, because
`v[right]` is the largest remaining element. That largest sum is already too
small — so **no pair using `left` can ever reach the target.** `left` is
eliminated entirely, and we advance it.

The mirror argument applies when the sum is too large: `right`'s best partner
is `v[left]`, the smallest remaining, and if even that overshoots, no pair using
`right` can work.

Each step removes one element from consideration for good, so after at most $n$
steps we have either found the answer or ruled out every pair. **One pass
covers $n^2/2$ possibilities**, and that is the whole magic of the pattern.
:::

### The trace

`{2, 7, 11, 15}`, target 9.

@tbl: Each row eliminates one element permanently. Three comparisons replace the six the brute force would make — and on a large array, $n$ replaces $n^2/2$.
| `left` | `right` | `v[left]` | `v[right]` | sum | vs target | Action |
|---|---|---|---|---|---|---|
| 0 | 3 | 2 | 15 | 17 | too big | `--right` |
| 0 | 2 | 2 | 11 | 13 | too big | `--right` |
| 0 | 1 | 2 | 7 | 9 | equal | found: (0, 1) |

```cpp title="Two Sum on a sorted array, O(n)"
#include <iostream>
#include <vector>

// Returns {i, j} with i < j and v[i] + v[j] == target, or {-1, -1}.
std::pair<int, int> twoSumSorted(const std::vector<int>& v, int target) {
    int left = 0, right = (int)v.size() - 1;
    while (left < right) {
        long long sum = (long long)v[left] + v[right];   // no overflow
        if (sum == target) return {left, right};
        if (sum < target) ++left;      // need a bigger sum
        else              --right;     // need a smaller sum
    }
    return {-1, -1};
}

int main() {
    std::vector<int> v = {2, 7, 11, 15};
    auto [i, j] = twoSumSorted(v, 9);
    std::cout << i << " " << j << "\n";

    auto [a, b] = twoSumSorted(v, 100);
    std::cout << a << " " << b << "\n";

    std::vector<int> neg = {-8, -3, 0, 4, 9};
    auto [c, d] = twoSumSorted(neg, 1);
    std::cout << c << " " << d << "\n";
    return 0;
}
```

```text nonum
0 1
-1 -1
0 4
```

$O(n)$ time, $O(1)$ space — down from $O(n^2)$.

:::pitfall The precondition is not optional
On **unsorted** input this returns wrong answers confidently. `{7, 2, 11}` with
target 9 moves `right` first and misses the pair entirely.

If the input is unsorted you have two choices: sort it first
($O(n \log n)$, but the original indices are lost unless you track them), or use
a hash map ($O(n)$ time, $O(n)$ space — Chapter 14). Which is right depends on
whether the problem wants indices or values, and whether extra space is allowed.
State that trade-off out loud; it is half of what the question is testing.
:::

### Palindrome check

The same shape, with equality instead of a sum.

```cpp title="Is this a palindrome?"
#include <iostream>
#include <string>
#include <vector>

bool isPalindrome(const std::string& s) {
    int left = 0, right = (int)s.size() - 1;
    while (left < right) {
        if (s[left] != s[right]) return false;
        ++left;
        --right;
    }
    return true;
}

int main() {
    std::cout << isPalindrome("racecar") << "\n";   // odd length
    std::cout << isPalindrome("abba")    << "\n";   // even length
    std::cout << isPalindrome("abc")     << "\n";
    std::cout << isPalindrome("")        << "\n";   // vacuously true
    std::cout << isPalindrome("x")       << "\n";
    return 0;
}
```

```text nonum
1
1
0
1
1
```

:::pitfall `while (left <= right)` here is a real bug, not a harmless one
In Chapter 6's reversal, `<=` merely swapped the middle element with itself —
wasteful but harmless.

Here it is different in kind. With `<=`, an odd-length string ends by comparing
`s[mid]` with `s[mid]`, which is always equal, so the function still returns the
right answer — and you conclude the bug is harmless. But change the comparison
to a *case-insensitive* or *skip-punctuation* variant, as the real LeetCode
problem does, and the middle character gets processed twice, which can throw off
an index you are also advancing.

The habit to build: `left < right` means *"there are still at least two distinct
positions to compare"*, which is exactly the condition you want. Use it and the
question never arises.
:::

### Container with most water

A harder converging problem, included because the greedy argument is the same
one, one level deeper.

:::definition The problem
Each element is the height of a vertical line. Choosing two lines, the water
held between them is $\min(h_i, h_j) \times (j - i)$ — the shorter line sets
the depth, and the distance sets the width. Find the maximum.
:::

@fig: tp_water | 170 | Container with most water. Starting at the widest possible pair, every later pair is narrower — so the only way to do better is a taller shortest line, which means moving the shorter wall inwards.

:::insight Why you always move the shorter wall
Start with the widest pair: `left = 0`, `right = n-1`. Any other pair is
narrower, so to beat the current area a future pair must be **taller**.

The area is limited by the shorter wall. If you move the **taller** wall
inwards, the width shrinks and the height is still capped by the same short
wall, so the area cannot improve — that move is pure loss.

Moving the **shorter** wall inwards also shrinks the width, but it is the only
move that can possibly raise the cap. So it is the only move worth making, and
every pair involving the discarded short wall is correctly eliminated.
:::

```cpp title="Container with most water, O(n)"
#include <algorithm>
#include <iostream>
#include <vector>

int maxArea(const std::vector<int>& h) {
    int left = 0, right = (int)h.size() - 1, best = 0;
    while (left < right) {
        int width = right - left;
        int depth = std::min(h[left], h[right]);
        best = std::max(best, width * depth);
        if (h[left] < h[right]) ++left;    // move the SHORTER wall
        else                    --right;
    }
    return best;
}

int main() {
    std::cout << maxArea({1, 8, 6, 2, 5, 4, 8, 3, 7}) << "\n";
    std::cout << maxArea({1, 1})                      << "\n";
    std::cout << maxArea({4, 3, 2, 1, 4})             << "\n";
    return 0;
}
```

```text nonum
49
1
16
```

Brute force is $O(n^2)$; this is $O(n)$ time and $O(1)$ space.

## Shape 2: Same-direction pointers

Here both pointers start on the left. One runs ahead reading; the other lags
behind writing. You have already used this in Chapter 6 — now we name it.

@fig: tp_read_write | 158 | The read/write pair. `read` visits every element; `write` only advances when something is kept. The gap between them is exactly the number of elements discarded so far.

:::definition The read/write (slow/fast) shape
`read` scans every element. For each one, decide **keep or discard**. On keep,
copy it to `write` and advance `write`. On discard, do nothing.

At the end, `v[0 .. write-1]` is the filtered array, and `write` is its length.
Everything from `write` onwards is leftover rubbish you simply ignore.
:::

### Remove all occurrences of a value

```cpp title="Remove every occurrence of val, in place"
#include <iostream>
#include <vector>

// Returns the new length k; v[0..k-1] holds the kept elements.
int removeElement(std::vector<int>& v, int val) {
    int write = 0;
    for (int read = 0; read < (int)v.size(); ++read)
        if (v[read] != val)
            v[write++] = v[read];
    return write;
}

int main() {
    std::vector<int> v = {3, 2, 2, 3, 4};
    int k = removeElement(v, 3);
    std::cout << "k = " << k << " -> ";
    for (int i = 0; i < k; ++i) std::cout << v[i] << " ";
    std::cout << "\n";

    std::vector<int> all = {7, 7, 7};
    std::cout << "all removed -> " << removeElement(all, 7) << "\n";

    std::vector<int> none = {1, 2, 3};
    std::cout << "none removed -> " << removeElement(none, 9) << "\n";
    return 0;
}
```

```text nonum
k = 3 -> 2 2 4 
all removed -> 0
none removed -> 3
```

$O(n)$ time, $O(1)$ space, one pass. Compare with the `erase`-in-a-loop version
of Chapter 5, which is $O(n^2)$ for the same job.

:::insight Why `write` never overtakes `read`
`write` advances only when `read` advances, and `read` advances every
iteration. So `write <= read` always holds, which means `v[write] = v[read]`
never writes to a position `read` has not already passed.

That is the safety proof for every algorithm of this shape, and it is worth
being able to state. It is also why the pattern needs no extra array: the space
freed by the discarded elements is exactly the space the kept ones move into.
:::

### Partition: evens before odds

```cpp title="Move all even numbers before all odd ones"
#include <iostream>
#include <vector>

void partitionEvenOdd(std::vector<int>& v) {
    int write = 0;
    for (int read = 0; read < (int)v.size(); ++read)
        if (v[read] % 2 == 0)
            std::swap(v[write++], v[read]);
}

int main() {
    std::vector<int> v = {3, 1, 2, 4, 7, 6};
    partitionEvenOdd(v);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
2 4 6 1 7 3 
```

Note that `swap` is used rather than assignment, because nothing may be thrown
away — the odd numbers still have to end up somewhere. The evens keep their
relative order; the odds do not. If you need **both** groups to keep their
order, $O(1)$ space is no longer possible in one pass, and you need a second
array ($O(n)$ space) or a stable in-place algorithm that is $O(n \log n)$.
Knowing that limit exists is worth as much as knowing the algorithm.

## Why two moving pointers is still O(n)

A reasonable worry: there are two indices, so is this not $O(n^2)$?

No, and the reason is worth stating precisely.

:::insight The counting argument
In the **converging** shape, every iteration either increments `left` or
decrements `right`. The gap between them starts at $n-1$ and shrinks by at least
1 each time, so there can be at most $n-1$ iterations.

In the **same-direction** shape, `read` increments every iteration and never
goes back, so there are exactly $n$ iterations.

In both, the total number of index movements is bounded by a constant times
$n$. Two pointers are only $O(n^2)$ if one of them **restarts** — which is
precisely what the brute-force nested loop does.

*"Does any pointer ever go backwards or restart?"* If no, it is linear.
:::

## Cost summary

| Problem | Brute force | Two pointers | Precondition |
|---|---|---|---|
| Two Sum (sorted) | $O(n^2)$ | $O(n)$ | sorted |
| Palindrome | $O(n)$ | $O(n)$, $O(1)$ space | none |
| Reverse in place | — | $O(n)$, $O(1)$ space | none |
| Container with most water | $O(n^2)$ | $O(n)$ | none |
| Remove element | $O(n^2)$ with `erase` | $O(n)$ | none |
| Remove duplicates (sorted) | $O(n^2)$ | $O(n)$ | sorted |
| Partition even/odd | $O(n)$ with a copy | $O(n)$, $O(1)$ space | none |

:::recap Chapter 9 in six lines
- **Converging** pointers start at both ends and move inwards; **same-direction**
  pointers both start left, one reading and one writing.
- Converging works because each comparison eliminates an entire family of pairs
  — be ready to explain *which* family.
- Converging pair-sum problems need **sorted** input; without it the answers are
  silently wrong.
- `write <= read` always holds, which is why in-place filtering is safe.
- Use `left < right`, not `left <= right`, so the loop means "two distinct
  positions remain".
- Two pointers are $O(n)$ because neither ever restarts. A restart is what makes
  a nested loop quadratic.
:::

:::exercise Practise
1. Trace `twoSumSorted({1, 3, 4, 6, 8, 11}, 10)` by hand. How many iterations?
   How many pairs did the brute force avoid?
2. Modify Two Sum to return **all** distinct pairs summing to the target, not
   just the first. How do you skip duplicates without using extra space?
3. Write `isPalindrome` for a string, ignoring case and non-letters —
   `"A man, a plan, a canal: Panama"` is a palindrome. Which pointer moves, and
   when?
4. Three Sum: find all distinct triples summing to zero. (Hint: sort, fix one
   element, and run Two Sum on the rest. What is the complexity, and why is it
   not $O(n^3)$?)
5. For "container with most water", construct an input where moving the taller
   wall would find a better answer — or explain why no such input exists.
6. Squares of a sorted array: given `{-4, -1, 0, 3, 10}`, return the sorted
   squares. Sorting afterwards is $O(n \log n)$; two pointers make it $O(n)$.
   Where do the two pointers start, and why does the output get filled from the
   **back**?
7. Reverse only the vowels of a string, leaving everything else where it is.
8. Explain, in two sentences, why the converging shape would be useless on an
   unsorted array, using the elimination argument rather than an example.
:::
