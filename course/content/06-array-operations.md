# The Core Array Operations
@short: Array Operations
@subtitle: Twelve operations, each traced by hand before it is coded
@tier: core
@prereq: Chapters 4 and 5
@blurb: This is the workshop chapter. Twelve operations — insert, delete, reverse, min and max, sum, count, remove duplicates, move zeroes and the rest — each one drawn, traced step by step, coded in C++, costed, and followed by the mistakes people actually make. Everything in Parts III and IV is built from these.
@objectives:
- Implement every basic array operation correctly, including the edge cases
- Explain what happens *internally* during an insertion and a deletion
- Trace an algorithm by hand using a table of variable values
- Reverse an array in place with two pointers
- Remove duplicates from a sorted array in one pass, in place
- Move all zeroes to the end while preserving the order of the rest
- State and justify the cost of each operation

## How to read this chapter

Every operation below follows the same six steps:

1. **What it must do** — stated precisely, including the awkward cases.
2. **The picture** — before and after.
3. **The trace** — a table showing every variable at every step.
4. **The code** — complete, compilable C++.
5. **The cost** — time and auxiliary space, with the reason.
6. **The mistakes** — what goes wrong and why.

Do the traces yourself with a pen before reading the code. The trace is where
understanding happens; the code is just a transcript of it.

## 1. Access and update

Covered in Chapter 4, repeated here for completeness.

```cpp title="Access and update are the same operation" frag
int x = v[3];        // read  the 4 bytes at B + 3*S
v[3] = 99;           // write the 4 bytes at B + 3*S
```

Both are $O(1)$ time, $O(1)$ space. The only hazard is the index being out of
range, which C++ will not tell you about.

## 2. Traversal

```cpp title="Visit every element once"
#include <iostream>
#include <vector>

void printAll(const std::vector<int>& v) {
    for (int i = 0; i < (int)v.size(); ++i)
        std::cout << v[i] << (i + 1 < (int)v.size() ? ", " : "\n");
}

int main() {
    std::vector<int> v = {10, 20, 30, 40};
    printAll(v);
    return 0;
}
```

```text nonum
10, 20, 30, 40
```

$O(n)$ time, $O(1)$ space. Note the condition `i + 1 < (int)v.size()` — it
prints the separator for every element except the last, without ever
subtracting from an unsigned value.

## 3. Searching

### Linear search — unsorted data

Covered in Chapter 4. $O(n)$ worst case. Works on any array.

### A first taste of binary search — sorted data

If the array is sorted, you can do far better by discarding half the
candidates at every step.

```cpp title="Binary search (full treatment in Chapter 12)"
#include <iostream>
#include <vector>

int binarySearch(const std::vector<int>& v, int target) {
    int lo = 0, hi = (int)v.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;      // never overflows
        if (v[mid] == target) return mid;
        if (v[mid] < target) lo = mid + 1; // answer is to the right
        else                 hi = mid - 1; // answer is to the left
    }
    return -1;
}

int main() {
    std::vector<int> v = {10, 20, 30, 40, 50, 60, 70};
    std::cout << binarySearch(v, 50) << "\n";
    std::cout << binarySearch(v, 35) << "\n";
    return 0;
}
```

```text nonum
4
-1
```

$O(\log n)$ time. The array **must** be sorted — on unsorted data it returns
confident nonsense. Chapter 12 explains every line, including why `mid` is
written that way.

## 4. Insertion

:::definition The insertion problem
Given an array with $n$ used slots (and room for at least one more), insert
value $x$ at index $p$, so that everything previously at index $p$ and beyond
moves one place to the right.
:::

@fig: op_insert | 168 | Inserting 99 at index 2. The elements from index 2 to the end must each move one place right, and they must be moved **from the back**, or each one overwrites the next.

The direction of the shifting loop is the whole difficulty.

:::insight Why we shift from the right, not the left
Suppose we tried to make room by going left to right, starting at index 2:

`v[3] = v[2]` — fine, 30 is now in two places.
`v[4] = v[3]` — but `v[3]` is no longer 40, we just overwrote it with 30.

Everything after the insertion point becomes a copy of the same value. The fix
is to copy **backwards**, starting from the last element, so that every slot is
read before anything overwrites it.
:::

### The trace

Insert `99` at index 2 into `{10, 20, 30, 40, 50}` (which has room for 6).

@tbl: Shifting right, from the back. Each row moves one element and nothing is ever overwritten before it is read.
| Step | `i` | Action | Array afterwards |
|---|---|---|---|
| start | — | — | `10 20 30 40 50 _` |
| 1 | 4 | `v[5] = v[4]` | `10 20 30 40 50 50` |
| 2 | 3 | `v[4] = v[3]` | `10 20 30 40 40 50` |
| 3 | 2 | `v[3] = v[2]` | `10 20 30 30 40 50` |
| 4 | — | `v[2] = 99` | `10 20 99 30 40 50` |

```cpp title="Insertion into a vector, written by hand"
#include <iostream>
#include <vector>

// Insert x at index p. Everything from p onwards shifts right.
void insertAt(std::vector<int>& v, int p, int x) {
    if (p < 0 || p > (int)v.size()) return;    // p == size() means "append"
    v.push_back(0);                            // make one more slot
    for (int i = (int)v.size() - 2; i >= p; --i)
        v[i + 1] = v[i];                       // copy BACKWARDS
    v[p] = x;
}

int main() {
    std::vector<int> v = {10, 20, 30, 40, 50};
    insertAt(v, 2, 99);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    insertAt(v, 0, 7);                         // at the front: worst case
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
10 20 99 30 40 50 
7 10 20 99 30 40 50 
```

**Cost.** The loop runs from the end down to `p`, so it performs $n - p$ moves.

- Inserting at the **end** ($p = n$): 0 moves, $O(1)$.
- Inserting at the **front** ($p = 0$): $n$ moves, $O(n)$.
- Worst case: $O(n)$.

:::insight The deep reason insertion is expensive
It is not that copying is slow. It is that **contiguity is a promise the array
must keep**. The elements have to stay side by side with no gaps, so making
room anywhere except the end forces everything after it to move.

A linked list makes no such promise, which is exactly why it can insert in
$O(1)$ — and exactly why it cannot index in $O(1)$. You cannot have both.
:::

In real code you would write `v.insert(v.begin() + p, x)`, which does precisely
this and is also $O(n)$. We wrote it by hand so you can see that the library is
not hiding anything clever.

## 5. Deletion

:::definition The deletion problem
Remove the element at index $p$, closing the gap so the remaining elements are
still contiguous, and reduce the size by one.
:::

@fig: op_delete | 160 | Deleting index 1. Everything after the hole moves one place left, and this time the loop must run **forwards** — the opposite of insertion, for the same reason.

:::insight Why deletion shifts forwards
We are moving things *left*, into a slot we have already finished with. Going
left to right, `v[1] = v[2]` reads `v[2]` before anything has touched it, then
`v[2] = v[3]`, and so on. Each read happens before the corresponding write.

Insertion moves right and must go backwards; deletion moves left and must go
forwards. Both rules come from the same principle: **read a slot before you
overwrite it**.
:::

### The trace

Delete index 1 from `{10, 20, 30, 40, 50}`.

| Step | `i` | Action | Array afterwards |
|---|---|---|---|
| start | — | — | `10 20 30 40 50` |
| 1 | 1 | `v[1] = v[2]` | `10 30 30 40 50` |
| 2 | 2 | `v[2] = v[3]` | `10 30 40 40 50` |
| 3 | 3 | `v[3] = v[4]` | `10 30 40 50 50` |
| 4 | — | `pop_back()` | `10 30 40 50` |

```cpp title="Deletion from a vector, written by hand"
#include <iostream>
#include <vector>

void deleteAt(std::vector<int>& v, int p) {
    if (p < 0 || p >= (int)v.size()) return;   // nothing to delete
    for (int i = p; i + 1 < (int)v.size(); ++i)
        v[i] = v[i + 1];                       // copy FORWARDS
    v.pop_back();                              // drop the duplicated tail
}

int main() {
    std::vector<int> v = {10, 20, 30, 40, 50};
    deleteAt(v, 1);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    deleteAt(v, (int)v.size() - 1);            // last element: cheapest
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
10 30 40 50 
10 30 40 
```

**Cost.** $n - p - 1$ moves. Deleting the last element is $O(1)$; deleting the
first is $O(n)$. Worst case $O(n)$, $O(1)$ space.

:::pitfall Deleting while looping forwards
```cpp nonum frag
for (int i = 0; i < (int)v.size(); ++i)
    if (v[i] == 0) deleteAt(v, i);      // BUG
```
After deleting index `i`, a new element has slid into position `i` — and then
`++i` skips it. Given `{0, 0, 1}` this removes only one zero.

Two fixes: do not increment when you delete (`if (...) deleteAt(v, i); else ++i;`),
or loop **backwards**, where removals never disturb the indices you have yet to
visit. The backwards loop is usually cleaner. Better still, use the write-pointer
pattern from operation 11 and do the whole job in $O(n)$.
:::

## 6. Reversing an array

:::definition The reversal problem
Turn `{10, 20, 30, 40, 50}` into `{50, 40, 30, 20, 10}`, using no second array.
:::

@fig: op_reverse | 158 | Reversing with two pointers. One starts at each end; they swap and step towards each other, and stop when they meet. Only $n/2$ swaps are needed because each swap fixes two positions.

This is your first **two-pointer** algorithm, and the pattern it introduces is
the subject of Chapter 9.

### The trace

| Step | `left` | `right` | Action | Array afterwards |
|---|---|---|---|---|
| start | 0 | 4 | — | `10 20 30 40 50` |
| 1 | 0 | 4 | swap | `50 20 30 40 10` |
| 2 | 1 | 3 | swap | `50 40 30 20 10` |
| 3 | 2 | 2 | `left == right`, stop | `50 40 30 20 10` |

```cpp title="Reversing in place with two pointers"
#include <iostream>
#include <vector>

void reverseArray(std::vector<int>& v) {
    int left = 0, right = (int)v.size() - 1;
    while (left < right) {
        std::swap(v[left], v[right]);
        ++left;
        --right;
    }
}

int main() {
    std::vector<int> odd = {10, 20, 30, 40, 50};
    reverseArray(odd);
    for (int x : odd) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> even = {1, 2, 3, 4};
    reverseArray(even);
    for (int x : even) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> one = {42};
    reverseArray(one);
    std::cout << one[0] << "\n";
    return 0;
}
```

```text nonum
50 40 30 20 10 
4 3 2 1 
42
```

**Cost.** $\lfloor n/2 \rfloor$ swaps: $O(n)$ time, $O(1)$ auxiliary space.

:::pitfall Three ways to get reversal wrong
**`while (left <= right)`** — when they are equal they point at the same middle
element, and swapping it with itself is harmless but pointless. Worse, if you
also `++left; --right;` the loop still terminates, so the bug is invisible here.
It becomes a real bug in the palindrome check of Chapter 9, where `<=` makes you
compare an element with itself and accept strings you should reject.

**Looping all the way across** — `for (i = 0; i < n; ++i) swap(v[i], v[n-1-i]);`
swaps every pair **twice**, returning the original array. A silent and very
confusing bug.

**Forgetting odd lengths** — with an odd count the middle element stays put, and
it should. Always test with both an odd and an even length, and with an empty
array.
:::

## 7. Minimum and maximum

```cpp title="One pass finds both"
#include <iostream>
#include <stdexcept>
#include <vector>

// Returns {min, max}. Throws if the array is empty - there is no answer.
std::pair<int, int> minMax(const std::vector<int>& v) {
    if (v.empty()) throw std::invalid_argument("empty array has no min or max");
    int lo = v[0], hi = v[0];           // start from a REAL element
    for (int i = 1; i < (int)v.size(); ++i) {
        if (v[i] < lo) lo = v[i];
        if (v[i] > hi) hi = v[i];
    }
    return {lo, hi};
}

int main() {
    std::vector<int> v = {7, -3, 12, 0, 5};
    auto [lo, hi] = minMax(v);
    std::cout << "min = " << lo << ", max = " << hi << "\n";

    std::vector<int> neg = {-9, -2, -40};
    auto [lo2, hi2] = minMax(neg);
    std::cout << "min = " << lo2 << ", max = " << hi2 << "\n";
    return 0;
}
```

```text nonum
min = -3, max = 12
min = -40, max = -2
```

Two details carry the whole operation.

**`lo` and `hi` both start at `v[0]`.** Not at 0, not at some number you hope is
big enough — at a value that is genuinely in the array. That guarantees the
answer is always an element that really exists.

**One loop finds both.** You do not need a pass for the minimum and another for
the maximum. Two independent `if` statements in the same pass cost one extra
comparison per element and save a whole traversal.

Trace it on `{7, -3, 12, 0, 5}` to see that nothing is missed:

@tbl: Tracing min and max in a single pass. Each row checks the current element against both running answers.
| `i` | `v[i]` | `v[i] < lo`? | `lo` | `v[i] > hi`? | `hi` |
|---|---|---|---|---|---|
| start | — | — | 7 | — | 7 |
| 1 | $-3$ | yes | $-3$ | no | 7 |
| 2 | 12 | no | $-3$ | yes | 12 |
| 3 | 0 | no | $-3$ | no | 12 |
| 4 | 5 | no | $-3$ | no | 12 |

:::insight Trace, do not stare
When code and expectation disagree, reading the code again almost never finds
the bug — you re-read what you *meant*, not what you wrote.

Build the table instead. A trace cannot deceive you, because it only records
what each line actually does. Every worked example in this book has one for
exactly this reason, and you should write one whenever you are stuck for more
than five minutes.
:::

:::pitfall Never initialise `lo` to 0
```cpp nonum frag
int lo = 0;                       // WRONG
for (int x : v) if (x < lo) lo = x;
```
On `{3, 5, 9}` this returns 0 — a value that is not in the array. The same bug
with `int hi = 0` breaks on all-negative input.

Initialise from `v[0]`, or from `INT_MAX` / `INT_MIN`, and handle the empty
array explicitly. Starting from a real element is safest, because it makes the
empty case impossible to forget.
:::

$O(n)$ time, $O(1)$ space, in exactly one pass.

## 8. Sum and average

```cpp title="Sum, average, and the overflow trap"
#include <iostream>
#include <vector>

long long sumOf(const std::vector<int>& v) {
    long long total = 0;             // long long, not int - see below
    for (int x : v) total += x;
    return total;
}

double averageOf(const std::vector<int>& v) {
    if (v.empty()) return 0.0;
    return (double)sumOf(v) / v.size();   // cast BEFORE dividing
}

int main() {
    std::vector<int> v = {10, 20, 30, 41};
    std::cout << "sum = " << sumOf(v) << "\n";
    std::cout << "avg = " << averageOf(v) << "\n";

    std::vector<int> big = {2000000000, 2000000000};
    std::cout << "big sum = " << sumOf(big) << "\n";
    return 0;
}
```

```text nonum
sum = 101
avg = 25.25
big sum = 4000000000
```

Two traps, both of which silently produce wrong numbers:

:::pitfall Overflow and integer division
**Overflow.** `int` holds up to about $2.1$ billion. Two elements of 2 billion
each overflow an `int` sum, and signed overflow is undefined behaviour — you may
get a negative number, or anything. Using `long long` for the accumulator costs
nothing and removes the problem.

**Integer division.** `sum / v.size()` with both operands integral discards the
fraction: $101 / 4$ becomes 25, not 25.25. Cast to `double` **before** dividing.
`(double)(sum / n)` is still wrong — it divides first, then converts the already
truncated result.
:::

$O(n)$ time, $O(1)$ space.

## 9. Counting occurrences

```cpp title="How many times does a value appear?"
#include <iostream>
#include <vector>

int countOf(const std::vector<int>& v, int target) {
    int count = 0;
    for (int x : v)
        if (x == target) ++count;
    return count;
}

int main() {
    std::vector<int> v = {1, 3, 7, 3, 3, 9};
    std::cout << countOf(v, 3) << "\n";
    std::cout << countOf(v, 5) << "\n";
    return 0;
}
```

```text nonum
3
0
```

$O(n)$ time, $O(1)$ space.

:::perf Counting many values at once
If you need the count of *every* value, do not call `countOf` once per value —
that is $O(n)$ per call and $O(n \cdot k)$ overall. Build a frequency table in
one pass instead:

```cpp nonum frag
std::unordered_map<int, int> freq;
for (int x : v) ++freq[x];          // one pass, O(n) total
```
This is the **frequency counting** pattern, and it is Chapter 14.
:::

## 10. Removing duplicates from a sorted array

:::definition The problem
Given a **sorted** array, remove the repeats so each value appears once, keeping
the order, using no extra array. Return the new length.
:::

The sortedness is the gift: **duplicates must be adjacent**. So you never have
to remember what you have seen — you only compare with the previous kept value.

@fig: op_dedupe | 168 | Removing duplicates with a write pointer. `w` marks where the next unique value goes; `r` reads across. They start together and `w` falls behind by exactly the number of duplicates skipped.

### The trace

Input `{1, 1, 2, 2, 2, 3}`.

@tbl: Trace of the two-pointer deduplication. `w` only advances when a genuinely new value is found.
| `r` | `v[r]` | `v[w-1]` | New? | Action | Array so far | `w` |
|---|---|---|---|---|---|---|
| start | — | — | — | keep `v[0]` | `1 . . . . .` | 1 |
| 1 | 1 | 1 | no | skip | `1 . . . . .` | 1 |
| 2 | 2 | 1 | yes | `v[1] = 2` | `1 2 . . . .` | 2 |
| 3 | 2 | 2 | no | skip | `1 2 . . . .` | 2 |
| 4 | 2 | 2 | no | skip | `1 2 . . . .` | 2 |
| 5 | 3 | 2 | yes | `v[2] = 3` | `1 2 3 . . .` | 3 |

Result: the first `w = 3` elements are `{1, 2, 3}`.

```cpp title="Remove duplicates from a sorted array, in place"
#include <iostream>
#include <vector>

// Returns the number of unique elements, which occupy v[0 .. k-1].
int removeDuplicates(std::vector<int>& v) {
    if (v.empty()) return 0;
    int w = 1;                                 // next write position
    for (int r = 1; r < (int)v.size(); ++r) {
        if (v[r] != v[w - 1]) {                // different from last kept
            v[w] = v[r];
            ++w;
        }
    }
    return w;
}

int main() {
    std::vector<int> v = {1, 1, 2, 2, 2, 3};
    int k = removeDuplicates(v);
    std::cout << "unique count = " << k << "\n";
    for (int i = 0; i < k; ++i) std::cout << v[i] << " ";
    std::cout << "\n";

    std::vector<int> all = {5, 5, 5, 5};
    std::cout << "all same -> " << removeDuplicates(all) << "\n";

    std::vector<int> empty;
    std::cout << "empty -> " << removeDuplicates(empty) << "\n";
    return 0;
}
```

```text nonum
unique count = 3
1 2 3 
all same -> 1
empty -> 0
```

**Cost.** One pass: $O(n)$ time, $O(1)$ auxiliary space. Compare that with the
obvious approach of calling `erase` for each duplicate, which is $O(n^2)$.

:::pitfall This only works on sorted input
On `{1, 2, 1}` the algorithm keeps all three, because the two 1s are not
adjacent. If the input is unsorted you must either sort first
($O(n \log n)$) or use a hash set ($O(n)$ time, $O(n)$ space). That is a
time–space trade-off exactly like the ones in Chapter 3.
:::

## 11. Moving zeroes to the end

:::definition The problem
Move every 0 to the end of the array while keeping the **relative order** of
the non-zero elements, in place. `{0, 1, 0, 3, 12}` becomes `{1, 3, 12, 0, 0}`.
:::

This is the same write-pointer idea as deduplication, and it is the cleanest
example of the **in-place modification** pattern of Chapter 13.

@fig: op_move_zeroes | 170 | Moving zeroes in two passes. The first pass compacts every non-zero value to the front using a write pointer; the second fills the remainder with zeroes. The order of the non-zero values is never disturbed.

### The trace

Input `{0, 1, 0, 3, 12}`.

| `r` | `v[r]` | Zero? | Action | Array | `w` |
|---|---|---|---|---|---|
| start | — | — | — | `0 1 0 3 12` | 0 |
| 0 | 0 | yes | skip | `0 1 0 3 12` | 0 |
| 1 | 1 | no | `v[0] = 1` | `1 1 0 3 12` | 1 |
| 2 | 0 | yes | skip | `1 1 0 3 12` | 1 |
| 3 | 3 | no | `v[1] = 3` | `1 3 0 3 12` | 2 |
| 4 | 12 | no | `v[2] = 12` | `1 3 12 3 12` | 3 |
| fill | — | — | `v[3] = v[4] = 0` | `1 3 12 0 0` | 3 |

```cpp title="Move zeroes to the end, order preserved"
#include <iostream>
#include <vector>

void moveZeroes(std::vector<int>& v) {
    int w = 0;                                  // next write position
    for (int r = 0; r < (int)v.size(); ++r)     // pass 1: compact non-zeroes
        if (v[r] != 0)
            v[w++] = v[r];
    while (w < (int)v.size())                   // pass 2: pad with zeroes
        v[w++] = 0;
}

int main() {
    std::vector<int> v = {0, 1, 0, 3, 12};
    moveZeroes(v);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> none = {1, 2, 3};
    moveZeroes(none);
    for (int x : none) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> allz = {0, 0, 0};
    moveZeroes(allz);
    for (int x : allz) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
1 3 12 0 0 
1 2 3 
0 0 0 
```

**Cost.** Two passes over the array, so $2n$ operations, which is $O(n)$ time
and $O(1)$ space.

:::insight A one-pass variation, and why it is not obviously better
You can do it in a single pass by swapping instead of copying:
```cpp nonum frag
int w = 0;
for (int r = 0; r < (int)v.size(); ++r)
    if (v[r] != 0) std::swap(v[w++], v[r]);
```
This is still $O(n)$ — it does not change the complexity, only the constant.
It performs *more* writes than the two-pass version when zeroes are rare (a
swap is three assignments), and fewer when zeroes are common.

Mention both in an interview. Knowing that two correct $O(n)$ solutions can
differ in real cost, and being able to say *why*, is what separates a good
answer from a complete one.
:::

## The complete cost table

@tbl: Every operation in this chapter. The pattern is clear: anything that touches one known position is $O(1)$; anything that must preserve contiguity across a change is $O(n)$.
| Operation | Time | Auxiliary space | Why |
|---|---|---|---|
| Access, update | $O(1)$ | $O(1)$ | address arithmetic |
| Traverse | $O(n)$ | $O(1)$ | $n$ elements |
| Linear search | $O(n)$ | $O(1)$ | could be anywhere |
| Binary search (sorted) | $O(\log n)$ | $O(1)$ | halves each step |
| Insert at end | $O(1)$ amortised | $O(1)$ | spare capacity |
| Insert at front/middle | $O(n)$ | $O(1)$ | shift right |
| Delete at end | $O(1)$ | $O(1)$ | drop the last |
| Delete at front/middle | $O(n)$ | $O(1)$ | shift left |
| Reverse | $O(n)$ | $O(1)$ | $n/2$ swaps |
| Min / max | $O(n)$ | $O(1)$ | one pass |
| Sum / average | $O(n)$ | $O(1)$ | one pass |
| Count occurrences | $O(n)$ | $O(1)$ | one pass |
| Remove duplicates (sorted) | $O(n)$ | $O(1)$ | write pointer |
| Move zeroes | $O(n)$ | $O(1)$ | write pointer |

:::recap Chapter 6 in six lines
- Insertion shifts **right** and must copy **backwards**; deletion shifts
  **left** and must copy **forwards**. Both rules come from "read before you
  overwrite".
- Anything at a known index is $O(1)$; anything that disturbs contiguity is
  $O(n)$.
- Two pointers moving towards each other reverse an array in $O(1)$ space.
- A **write pointer** trailing a **read pointer** compacts an array in one pass
  — it solves deduplication, zero-moving, filtering, and much of Chapter 13.
- Initialise min/max from a real element, accumulate sums in `long long`, and
  cast before dividing.
- Deleting inside a forward loop skips elements. Loop backwards, or use a write
  pointer.
:::

:::exercise Practise
1. Insert `5` at index 0 of `{1, 2, 3}` by hand, writing out every assignment in
   order. How many moves were there? Now insert at index 3 instead. How many?
2. Why must insertion copy backwards? Show what `{1, 2, 3, 4}` becomes if you
   copy forwards instead.
3. Write `deleteValue(v, x)` that removes the **first** occurrence of `x` and
   returns whether it found one. What should it do if `x` appears twice?
4. Modify `removeDuplicates` to keep **at most two** copies of each value.
   (Hint: compare against `v[w - 2]`, and think about what `w` must start at.)
5. Write `moveZeroes` so the zeroes go to the **front** instead, with the
   non-zero order preserved. Which pointer moves, and in which direction?
6. `countOf` is $O(n)$ per call. You must answer 1,000 count queries on a fixed
   array of 100,000 elements. What is the total cost as written, and how would
   you make it fast? What does your fix cost in space?
7. Combine operations 10 and 11: given a sorted array, remove the duplicates
   **and** move any zeroes to the end, in $O(n)$ with $O(1)$ space. In what
   order must you do the two steps, and why?
8. The two lines below are meant to reverse an array. Find the bug by tracing
   `{1, 2, 3, 4}`, not by staring at it.
:::

```cpp nonum frag
for (int i = 0; i < (int)v.size(); ++i)
    std::swap(v[i], v[v.size() - 1 - i]);
```
