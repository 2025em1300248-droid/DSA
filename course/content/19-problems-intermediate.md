# Intermediate Array Problems
@short: Intermediate Problems
@subtitle: Ten problems where the good solution is not the obvious one
@tier: practice
@prereq: Chapter 18
@blurb: These are the problems that interviews are actually built from. Each has an obvious $O(n^2)$ solution and a linear one that requires an idea, and in every case the idea is one of the ten patterns. Work through them with the derivations covered up; the goal is to reach the point where you can *find* the idea, not recall it.
@objectives:
- Solve the ten standard intermediate array problems
- Derive each linear solution from its brute force
- Apply Boyer–Moore voting, Dutch National Flag, and Floyd's cycle detection to arrays
- Build prefix and suffix products without using division
- Explain why merging two sorted arrays in place must work backwards
- Choose correctly between hashing, sorting and two pointers under stated constraints

## 1. Two Sum

**Problem.** Return the **indices** of two elements summing to a target. Exactly
one solution exists; you may not use an element twice.

**Think.** Brute force is every pair, $O(n^2)$. The improvement: you are not
searching for *any* partner, you are searching for a *specific* one, namely
$target - x$. That is a lookup, not a search. Covered in Chapter 14.

**Cost.** $O(n)$ time, $O(n)$ space.

**Watch for.** Look up before inserting, or an element pairs with itself. If the
array were sorted and *values* were wanted instead of indices, two pointers
would give $O(1)$ space — be ready to say that.

## 2. Best Time to Buy and Sell Stock

**Problem.** One buy and one later sell. Maximise the profit; 0 if no profitable
trade exists.

**Think.** Brute force tries every pair of days, $O(n^2)$. The insight: when
considering selling on day $i$, the only thing that matters about the past is
the **cheapest price so far**. Carry it. Covered in Chapter 16.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** You must buy before you sell, so update the running minimum
*and* the running best in the right order. Returning a negative profit when the
prices only fall — 0 is usually correct, but confirm.

## 3. Maximum sub-array sum

**Problem.** Largest sum of any contiguous non-empty sub-array.

**Think.** Kadane: ask *"what is the best sub-array ending here?"* Covered in
Chapter 16.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Initialising to 0 breaks all-negative input.

## 4. Majority element

**Problem.** One value appears **more than** $n/2$ times. Find it. You may
assume it exists.

**Think.** A frequency map is $O(n)$ time and $O(n)$ space. Sorting puts the
majority at the middle, $O(n \log n)$ and $O(1)$ space. Both are fine answers.
The $O(n)$ time *and* $O(1)$ space answer is Boyer–Moore voting, and it is
beautiful.

@fig: pi_boyer_moore | 168 | Boyer–Moore voting. Think of each element as a vote, and of two differing votes as cancelling each other out. Because the majority has more than half the votes, it cannot be fully cancelled by all the others combined — so whatever survives must be it.

:::insight Why the voting algorithm works
Keep a `candidate` and a `count`. On each element: if `count` is 0, adopt the
element as the new candidate; then add 1 if it matches the candidate and
subtract 1 if it does not.

The pairing argument: every decrement pairs one majority element with one
non-majority element and removes both from consideration. There are fewer than
$n/2$ non-majority elements and more than $n/2$ majority ones, so the
non-majority elements run out first. Whatever is left standing is the majority.

**This only works if a majority genuinely exists.** With `{1, 2, 3}` it returns
some arbitrary value. If existence is not guaranteed, do a second pass to verify
the candidate really does appear more than $n/2$ times — and say so unprompted.
:::

```cpp title="Boyer-Moore majority vote, with verification"
#include <iostream>
#include <vector>

// Returns the majority element, or -1 if there is none.
int majorityElement(const std::vector<int>& v) {
    int candidate = 0, count = 0;
    for (int x : v) {                       // pass 1: find the survivor
        if (count == 0) candidate = x;
        count += (x == candidate) ? 1 : -1;
    }
    int freq = 0;                           // pass 2: verify it
    for (int x : v) if (x == candidate) ++freq;
    return freq > (int)v.size() / 2 ? candidate : -1;
}

int main() {
    std::cout << majorityElement({3, 2, 3})             << "\n";
    std::cout << majorityElement({2, 2, 1, 1, 1, 2, 2}) << "\n";
    std::cout << majorityElement({1, 2, 3})             << "\n";  // none
    std::cout << majorityElement({7})                   << "\n";
    return 0;
}
```

```text nonum
3
2
-1
7
```

**Cost.** $O(n)$ time, $O(1)$ space, two passes.

**Next.** All values appearing more than $n/3$ times. There can be at most two,
and the algorithm generalises to two candidates and two counters.

## 5. Sort an array of 0s, 1s and 2s

**Problem.** Sort an array containing only the values 0, 1 and 2, in one pass
with $O(1)$ space.

**Think.** Counting the three values and rewriting is two passes and perfectly
acceptable. One pass requires the **Dutch National Flag** algorithm, which is
three pointers rather than two.

@fig: pi_dutch_flag | 172 | The Dutch National Flag partition. Three boundaries divide the array into four regions: settled 0s, settled 1s, unexamined, and settled 2s. The unexamined region shrinks to nothing, and each element is placed in one step.

:::insight The three-region invariant
- `v[0 .. low-1]` are all 0
- `v[low .. mid-1]` are all 1
- `v[mid .. high]` is unexamined
- `v[high+1 .. n-1]` are all 2

Look at `v[mid]`:
- **0** → swap it into the 0 region: `swap(v[low], v[mid]); ++low; ++mid;`
- **1** → it is already in the right region: `++mid;`
- **2** → swap it into the 2 region: `swap(v[mid], v[high]); --high;`

The asymmetry matters. After swapping with `low`, the incoming element is
known to be a 1 (it came from the 1 region), so `mid` can advance. After
swapping with `high`, the incoming element has **never been examined**, so
`mid` must stay put and look at it next time.

Getting that asymmetry right is the entire problem.
:::

```cpp title="Dutch National Flag: one pass, O(1) space"
#include <iostream>
#include <vector>

void sortColours(std::vector<int>& v) {
    int low = 0, mid = 0, high = (int)v.size() - 1;
    while (mid <= high) {
        if (v[mid] == 0)      { std::swap(v[low], v[mid]); ++low; ++mid; }
        else if (v[mid] == 1) { ++mid; }
        else                  { std::swap(v[mid], v[high]); --high; }
    }
}

int main() {
    std::vector<int> v = {2, 0, 2, 1, 1, 0};
    sortColours(v);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> w = {2, 0, 1};
    sortColours(w);
    for (int x : w) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> z = {0, 0, 0};
    sortColours(z);
    for (int x : z) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
0 0 1 1 2 2 
0 1 2 
0 0 0 
```

**Cost.** $O(n)$ / $O(1)$, one pass.

**Watch for.** `while (mid <= high)`, not `<`. And do **not** advance `mid`
after swapping with `high`.

## 6. Merge two sorted arrays in place

**Problem.** `a` has $m$ real elements followed by $n$ empty slots; `b` has $n$
elements. Merge `b` into `a`, sorted, in place.

**Think.** Merging from the front would overwrite elements of `a` that have not
been placed yet. The fix is to fill from the **back**, where the slots are
already empty.

@fig: pi_merge_back | 168 | Merging backwards. The spare slots are at the end, so writing the **largest** remaining element each time never overwrites anything that still matters.

```cpp title="Merge b into a, filling from the back"
#include <iostream>
#include <vector>

void merge(std::vector<int>& a, int m, const std::vector<int>& b, int n) {
    int i = m - 1, j = n - 1, w = m + n - 1;   // w: the last empty slot
    while (j >= 0) {                            // while b has elements left
        if (i >= 0 && a[i] > b[j]) a[w--] = a[i--];
        else                       a[w--] = b[j--];
    }
    // No tail loop for a: anything left in a is already in the right place.
}

int main() {
    std::vector<int> a = {1, 2, 3, 0, 0, 0};
    std::vector<int> b = {2, 5, 6};
    merge(a, 3, b, 3);
    for (int x : a) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> c = {0};
    std::vector<int> d = {1};
    merge(c, 0, d, 1);                          // a is empty
    for (int x : c) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
1 2 2 3 5 6 
1 
```

**Cost.** $O(m + n)$ time, $O(1)$ space.

**Watch for.** The loop condition is `j >= 0`, not `i >= 0 && j >= 0`. If `a`
runs out first, the rest of `b` must still be copied; if `b` runs out first, the
rest of `a` is already in place and needs no work. That asymmetry is why there is
only one tail case.

## 7. Find the duplicate number

**Problem.** $n+1$ values, each in $1 \dots n$, with exactly one value repeated.
Find it **without modifying the array** and in $O(1)$ space.

**Think.** Sorting modifies. A hash set uses $O(n)$. The constraints are
deliberately ruling out every easy answer, which is a signal that an unusual
idea is wanted.

:::insight The array is a linked list in disguise
Read `v[i]` as *"the next index after $i$"*. Starting from index 0 and
following $i \to v[i]$ gives a sequence. Because every value is in $1 \dots n$,
the sequence can never leave the array — so it must eventually repeat, which
means it contains a **cycle**.

The duplicated value is exactly the index that two different positions point to,
which makes it the **entry point of the cycle**.

So this is cycle detection, and Floyd's tortoise-and-hare algorithm finds the
entry point in $O(n)$ time and $O(1)$ space. The same algorithm appears for real
linked lists in Chapter 30; here it is being applied to an array that merely
behaves like one.
:::

@fig: pi_duplicate_cycle | 176 | The array read as a linked list. Index $i$ points to index `v[i]`. Two positions holding the same value point to the same place, which creates a cycle whose entrance is the duplicated number.

```cpp title="Find the duplicate with Floyd's cycle detection"
#include <iostream>
#include <vector>

int findDuplicate(const std::vector<int>& v) {
    int slow = v[0], fast = v[0];
    do {                                 // phase 1: find a meeting point
        slow = v[slow];
        fast = v[v[fast]];
    } while (slow != fast);

    slow = v[0];                         // phase 2: find the cycle entrance
    while (slow != fast) {
        slow = v[slow];
        fast = v[fast];
    }
    return slow;
}

int main() {
    std::cout << findDuplicate({1, 3, 4, 2, 2}) << "\n";
    std::cout << findDuplicate({3, 1, 3, 4, 2}) << "\n";
    std::cout << findDuplicate({2, 2, 2, 2, 2}) << "\n";
    return 0;
}
```

```text nonum
2
3
2
```

**Cost.** $O(n)$ time, $O(1)$ space, array unmodified.

**Watch for.** Phase 2 is **not** optional, and both pointers move at the *same*
speed in it. Chapter 30 proves why that finds the entrance.

## 8. Product of array except self

**Problem.** Return an array where `out[i]` is the product of every element
except `v[i]`. **Division is not allowed**, and the answer must be $O(n)$.

**Think.** Division would make it trivial — but it fails when any element is 0,
which is exactly why the problem forbids it.

:::insight Split the product in two
Everything except `v[i]` is *everything to the left of $i$* multiplied by
*everything to the right of $i$*.

Both are prefix products — one built left to right, one built right to left.
Chapter 11's idea, with multiplication instead of addition.

The trick that gets it to $O(1)$ extra space: write the left products into the
output array during the first pass, then sweep right to left carrying a single
running product and multiply it in. No second array is needed.
:::

@fig: pi_product_except | 170 | Prefix and suffix products. Each output cell is the product of everything before it times the product of everything after it — two passes, no division, and the zeroes take care of themselves.

```cpp title="Product except self, O(n) time, O(1) extra space"
#include <iostream>
#include <vector>

std::vector<long long> productExceptSelf(const std::vector<int>& v) {
    int n = (int)v.size();
    std::vector<long long> out(n, 1);

    long long left = 1;                      // pass 1: products of the left
    for (int i = 0; i < n; ++i) {
        out[i] = left;
        left *= v[i];
    }
    long long right = 1;                     // pass 2: multiply in the right
    for (int i = n - 1; i >= 0; --i) {
        out[i] *= right;
        right *= v[i];
    }
    return out;
}

int main() {
    for (long long x : productExceptSelf({1, 2, 3, 4})) std::cout << x << " ";
    std::cout << "\n";
    for (long long x : productExceptSelf({-1, 1, 0, -3, 3})) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
24 12 8 6 
0 0 9 0 0 
```

**Cost.** $O(n)$ time; $O(1)$ extra space, not counting the output.

**Watch for.** Note how the zero case works out with no special handling: the
single 0 contributes to every other cell's product and is itself excluded. A
division-based solution would need an explicit count of zeroes and three
branches.

## 9. Sub-array sum equals K

**Problem.** Count contiguous sub-arrays summing to exactly $K$. Values may be
negative.

**Think.** Prefix sums plus a hash map. The negatives rule out a sliding window.
Covered in Chapter 11.

**Cost.** $O(n)$ time, $O(n)$ space.

**Watch for.** Seed the map with `{0: 1}`; look up before inserting.

## 10. Longest sub-array with a given sum

**Problem.** Return the **length** of the longest contiguous sub-array summing to
$K$.

**Think.** Same prefix-sum idea, but the map stores *where* a prefix value was
first seen rather than how many times.

:::insight Keep the earliest occurrence only
For a *count* you want every occurrence. For the *longest* you want the
**earliest**, because an earlier start makes a longer sub-array.

So insert into the map only if the prefix value is not already there. One `if`
is the difference between the two problems.
:::

```cpp title="Longest sub-array with sum exactly K"
#include <algorithm>
#include <iostream>
#include <unordered_map>
#include <vector>

int longestSubarrayWithSum(const std::vector<int>& v, long long k) {
    std::unordered_map<long long, int> firstSeen;   // prefix value -> index
    firstSeen[0] = -1;                              // empty prefix, before index 0
    long long running = 0;
    int best = 0;
    for (int i = 0; i < (int)v.size(); ++i) {
        running += v[i];
        auto it = firstSeen.find(running - k);
        if (it != firstSeen.end())
            best = std::max(best, i - it->second);
        if (firstSeen.find(running) == firstSeen.end())
            firstSeen[running] = i;                 // EARLIEST occurrence only
    }
    return best;
}

int main() {
    std::cout << longestSubarrayWithSum({1, 2, 3, 1, 1, 1, 1}, 3) << "\n";
    std::cout << longestSubarrayWithSum({-1, 1, 1, -1, 2}, 2)     << "\n";
    std::cout << longestSubarrayWithSum({1, 2, 3}, 100)           << "\n";
    return 0;
}
```

```text nonum
3
5
0
```

**Cost.** $O(n)$ time, $O(n)$ space.

**Watch for.** `firstSeen[0] = -1`, not 0 — the empty prefix sits *before* index
0, and using 0 makes every length one too short.

## The whole set, at a glance

@tbl: The ten intermediate problems. Note how many of them have an $O(n^2)$ answer that is correct and a linear answer that needs one specific idea.
| # | Problem | Brute force | Best | Idea |
|---|---|---|---|---|
| 1 | Two Sum | $O(n^2)$ | $O(n)$ | complement lookup |
| 2 | Buy and sell stock | $O(n^2)$ | $O(n)$ | running minimum |
| 3 | Max sub-array sum | $O(n^2)$ | $O(n)$ | Kadane |
| 4 | Majority element | $O(n^2)$ | $O(n)$, $O(1)$ sp. | Boyer–Moore voting |
| 5 | Sort 0s, 1s, 2s | $O(n \log n)$ | $O(n)$ one pass | Dutch flag, 3 pointers |
| 6 | Merge sorted in place | $O((m{+}n)\log) $ | $O(m+n)$ | fill from the back |
| 7 | Find the duplicate | $O(n^2)$ | $O(n)$, $O(1)$ sp. | Floyd's cycle detection |
| 8 | Product except self | $O(n^2)$ | $O(n)$ | prefix × suffix |
| 9 | Sub-array sum = K | $O(n^2)$ | $O(n)$ | prefix + hash map |
| 10 | Longest sub-array sum K | $O(n^2)$ | $O(n)$ | prefix + earliest index |

:::exercise Consolidate
1. For each of the ten, state the brute force and the single observation that
   improves it, without looking.
2. Problems 4 and 7 both achieve $O(1)$ space by a non-obvious argument. Write
   out both arguments in your own words.
3. Why does problem 6 fail when filled from the front? Construct a small input
   that breaks it.
4. Problem 8 forbids division. Write the division-based solution anyway, then
   list every input that breaks it.
5. Problems 9 and 10 differ by one `if`. State exactly which, and why.
6. Three Sum: find all distinct triples summing to zero. Which two patterns
   combine, and what is the complexity?
7. Problem 5 generalises to $k$ distinct values. At what $k$ does the
   three-pointer approach stop being practical, and what replaces it?
:::
