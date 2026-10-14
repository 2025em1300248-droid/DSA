# The Complete Answer Key
@short: Answer Key
@subtitle: Every exercise, answered and explained
@tier: reference
@prereq: attempt the exercise first
@blurb: Answers to Chapter 37's five sets and to the exercises at the end of every chapter. Each answer explains *why*, not merely *what* — several say something the question did not ask, because the interesting part of an exercise is usually just past its edge. Read the explanation even when you were right.
@objectives:
- Check your work against a worked answer
- Understand the reasoning behind each answer, not just the result
- Find the chapter to revisit when an answer surprises you

:::warning Read this only after attempting
An answer you read is worth perhaps a tenth of an answer you found. If you have
not spent twenty minutes on the exercise, go back; the hint in Chapter 36 will
usually restart you without finishing the job.
:::

## Chapter 37, Set A — Multiple choice

**A1 — C.** 2032. A `double` is 8 bytes, so element 4 is at
$2000 + 4 \times 8 = 2032$. The formula $B + i \times S$ needs only the base and
the element size, which is why **D** is wrong.

**A2 — C.** 16. Capacity doubles at 1, 2, 4, 8, 16. After ten pushes the last
doubling (from 8) has already happened, so the capacity is 16 with `size() == 10`.

**A3 — C.** Knowing the length is useful for bounds checking but plays no part
in the address calculation. The other three are exactly the preconditions of
$B + i \times S$.

**A4 — C.** $O(n^2)$. Each front insertion shifts every existing element, so
the total is $1 + 2 + \cdots + n = n(n+1)/2$.

**A5 — B.** $O(n)$. The comparisons are logarithmic but reaching the middle of
a list requires walking there. This is the cleanest illustration that binary
search is an *array* algorithm.

**A6 — B.** $O(n)$. You need the node's predecessor to unlink it, and finding
it means walking from the head. In a **doubly** linked list it would be $O(1)$,
which is the main reason that variant exists.

**A7 — C.** leaves it unchanged. `delete` destroys the object and frees the
memory; the pointer still holds the old address. That is why `p = nullptr;`
afterwards is a habit worth having.

**A8 — B.** `left` only ever increases and never exceeds $n$, so the inner
loop's body executes at most $n$ times **across the whole run**, not per
iteration. The same accounting as amortised analysis.

**A9 — B.** an all-negative array. With `best = 0` the answer for
`{-3, -1, -7}` comes out as 0 — the sum of the empty sub-array. Correct only if
the empty sub-array is allowed, which is why you should ask.

**A10 — B.** Average $O(1)$; worst case $O(n)$ when every key collides. The
constant factor also matters: a hash plus an indirection is far slower than a
count array's single address calculation.

**A11 — C.** a one-element list. Every `next` is correctly reversed, but `head`
still names the original first node — which is now the tail, with
`next == nullptr`. Printing from it gives one element.

**A12 — A.** both pointers one step. Keeping `fast` at double speed is the
classic error and finds the wrong node. The proof $F = nL - a$ requires equal
speeds.

**A13 — B.** A stack dummy is destroyed automatically, so it cannot leak, and
`delete &dummy` would be undefined behaviour — which the loop's structure
naturally never attempts.

**A14 — B.** row-major. Row-major reads consecutive addresses, so one 64-byte
cache line supplies 16 `int`s and the prefetcher keeps ahead. Column-major jumps
a whole row each step. Same complexity, commonly 3–6× the time.

**A15 — B.** $(AB)^R = B^R A^R$. Reversing a concatenation reverses the order
of the parts as well as each part, which puts the two blocks in the right places
(backwards); reversing each block individually then repairs them.

## Chapter 37, Set B — Trace the code

**B1 — prints `7 4`.**

| `i` | `v[i]` | branch | `best` | `second` |
|---|---|---|---|---|
| start | — | — | 4 | $-1000$ |
| 1 | 2 | middle | 4 | 2 |
| 2 | 7 | new best | 7 | 4 |
| 3 | 1 | neither | 7 | 4 |

Note row 2: the old champion 4 is demoted into `second` **before** `best`
changes. Reversing those two lines would give `7 7`.

**B2 — `{1, 3, 0, 0, 0}`.** The first pass compacts the two non-zeroes to
indices 0 and 1, leaving `w = 2`; the second pass fills indices 2, 3 and 4 with
zeroes. The relative order of 1 and 3 is preserved, which is the requirement.

**B3 — 2 iterations.** Iteration 1: `mid = 2`, `v[2] = 5 < 9`, so `lo = 3`.
Iteration 2: `mid = 4`, `v[4] = 9`, found. Linear search would have taken five
comparisons.

**B4 — `best = 6`.**

| `i` | `v[i]` | `endingHere` | `best` |
|---|---|---|---|
| 0 | $-2$ | $-2$ | $-2$ |
| 1 | 3 | 3 (restart) | 3 |
| 2 | $-1$ | 2 (extend) | 3 |
| 3 | 4 | 6 (extend) | 6 |
| 4 | $-5$ | 1 (extend) | 6 |

The best sub-array is `{3, -1, 4}`. Row 1 restarts because the running sum
$-2$ was negative.

**B5 — the list becomes `3 -> 2 -> 1`.**

| iteration | `prev` | `curr` | `nextNode` | links after |
|---|---|---|---|---|
| start | `nullptr` | 1 | — | `1->2->3->∅` |
| 1 | 1 | 2 | 2 | `1->∅`, `2->3->∅` |
| 2 | 2 | 3 | 3 | `2->1->∅`, `3->∅` |
| 3 | 3 | `nullptr` | `nullptr` | `3->2->1->∅` |

The caller must then set `head = prev`.

**B6 — returns 3.** The longest window with sum at most 7 is `5 1 1`… no: trace
carefully. At `right = 3` the window is `1 5 1` with sum 7, length 3. At
`right = 4` the sum reaches 10 and two elements are dropped, leaving length 2.
At `right = 5` the window is `1 3 2` with sum 6, length 3. The answer is 3.

**B7 — prints 3.** With `fast` starting at `head->next`, `slow` lands on the
**first** middle. For an odd length both middles coincide, so the answer is the
same as starting `fast` at `head` — the difference only shows on even lengths.

## Chapter 37, Set C — Find the bug

**C1 — `i <= v.size()` reads one past the end.** The last valid index is
`size() - 1`. It usually adds a garbage value rather than crashing, which is
worse. Fix: `i < (int)v.size()`.

**C2 — `best` starts at 0.** On `{-5, -2, -9}` the function returns 0, a value
not in the array. Fix: start from `v[0]` after checking the array is non-empty.

**C3 — every pair is swapped twice.** The loop runs to `size()`, so after
swapping $(0, 3)$ it later swaps $(3, 0)$ back. The array is returned unchanged.
Fix: loop to `size() / 2`, or use converging pointers with `left < right`.

**C4 — `while (lo < hi)` misses the one-element region.** When `lo == hi` there
is still one unexamined element. Searching a one-element array for its own value
returns $-1$. Fix: `lo <= hi`.

**C5 — use after free.** `head->next` is read after `head` has been deleted.
Fix: save it first — `Node* d = head; head = head->next; delete d;`.

**C6 — the order is reversed, so `fresh->next` points at `fresh`.** After
`node->next = fresh`, the expression `node->next` *is* `fresh`. The result is a
self-referential node, and every later traversal hangs. Fix: set `fresh->next`
first.

**C7 — `best` is only updated when a run ends.** On `{1, 1, 1}` the run never
ends, so the function returns 0. Fix: update `best` inside the `if (x == 1)`
branch, which also removes the need for a correction after the loop.

**C8 — the whole matrix is transposed twice.** Swapping $(r, c)$ and then later
$(c, r)$ restores the original. Fix: start the inner loop at `c = r + 1` so each
pair is visited once.

**C9 — it inserts before looking up.** With `v = {3, 2, 4}` and target 6, at
`i = 0` the map already holds `3 → 0`; the complement of 3 is 3, and it returns
$(0, 0)$ — one element used twice. Fix: look up first, then insert.

**C10 — `k` is not reduced modulo `n`.** If `k >= n`, `v.begin() + k` is past
the end and the behaviour is undefined. Fix: `k %= n;` first, and handle
`k == 0`.

## Chapter 37, Set D — Write the code

**D1 — count pairs summing to a target.** Walk once with a frequency map; for
each `x`, add `freq[target - x]` to the count *before* inserting `x`. That
counts each pair exactly once and handles duplicates correctly. $O(n)$ expected
time, $O(n)$ space. The sorted two-pointer alternative is $O(n \log n)$ with
$O(1)$ space, and needs care to count duplicate pairs.

**D2 — is it a rotated sorted array?** Count the "descents" — positions where
`v[i] > v[i+1]` — and also compare the last element with the first. A rotated
sorted array has **at most one** descent, and if it has exactly one then
`v.back() <= v.front()` must hold. Zero descents means it is already sorted,
which counts as a rotation by 0. $O(n)$, $O(1)$.

**D3 — longest run of equal values.** The current-run/best-run shape from
Chapter 8: reset `current` to 1 when `v[i] != v[i-1]`, otherwise increment, and
update `best` every step. An empty array returns 0; one element returns 1.
$O(n)$, $O(1)$.

**D4 — merge intervals.** Sort by **start**. Then walk, keeping the current
merged interval; if the next interval's start is at most the current end, extend
the end to the maximum of the two, otherwise emit and begin a new one. Sorting
by start is what guarantees that anything overlapping the current interval comes
next. $O(n \log n)$.

**D5 — remove duplicates from an unsorted list.** Either a hash set of seen
values in one pass ($O(n)$ time, $O(n)$ space), or a nested loop removing later
duplicates of each node ($O(n^2)$ time, $O(1)$ space). State both and the
trade-off; which is right depends on whether extra space is allowed.

**D6 — is the list circular?** Floyd's detection finds *a* cycle; this question
is narrower. Walk from `head->next` and check whether you return to `head`; if
you reach `nullptr` first, it is not circular. A list with a cycle that does not
include the head is **not** circular by this definition, and your code should
reflect that. $O(n)$, $O(1)$.

**D7 — swap pairs.** Use a dummy node, since the head changes. Each step
rewires three pointers: `prev->next = second`, `first->next = second->next`,
`second->next = first`; then advance `prev` to `first`. Stop when fewer than two
nodes remain. $O(n)$, $O(1)$.

**D8 — maximum circular sub-array sum.** The answer is either a normal Kadane
result, or `total - minSubarraySum` (the wrapping case, where the elements left
out form a contiguous minimum). **The edge case:** if every element is negative,
`total - min` is 0, which corresponds to taking nothing — so return the plain
Kadane answer in that case. Detect it by checking whether the maximum is
negative.

## Chapter 37, Set E — Complexity analysis

**E1 — $O(n^2)$ time, $O(1)$ space.** The inner loop runs $n/2$ times, so the
total is $n^2/2$ — and the constant $\frac{1}{2}$ is dropped. A common mistake
is to answer $O(n)$ because of the `j += 2`.

**E2 — $O(n)$ time, $O(1)$ space.** The outer loop takes $i = 1, 3, 9, \dots$,
and the inner runs $i$ times, so the total is $1 + 3 + 9 + \cdots + n$. That
geometric series sums to about $3n/2$. Deeply nested is not the same as
quadratic.

**E3 — $O(n \log n)$ time, $O(n)$ space.** The parameter is taken **by value**,
so the whole vector is copied on entry: that is the $O(n)$ space, and it is easy
to miss.

**E4 — $O(n \log n)$ time, $O(1)$ space.** Also note a correctness problem:
`binary_search` requires a sorted range, and nothing here guarantees one. The
complexity is unaffected; the answer is meaningless. Spotting that is worth more
than the complexity.

**E5 — $O(n^2)$ time, $O(1)$ space**, where $n$ is the number of nodes. Both
loops traverse the whole list.

**E6 — $O(2^n)$ time, $O(n)$ space.** Each call makes two calls on $n-1$, so the
call count doubles with each increment of $n$. The space is the recursion depth,
which is $n$, not $2^n$ — only one root-to-leaf path exists at a time.

**E7 — $O(n^2)$ time, $O(n)$ space.** `insert` at the beginning shifts
everything already placed. This whole function is `std::reverse` written
quadratically; building forwards and reversing once is $O(n)$.

**E8 — $O(n)$ time, $O(n)$ space.** Building the map is $n$ insertions at
average $O(1)$; iterating it visits at most $n$ distinct keys.

## Part I — Chapters 1 to 3

### Chapter 1 — What a data structure really is

1. **Array.** "Skip to track 47" is access by index, which is $O(1)$ for an
   array and $O(n)$ for a list; reordering is rare, so the list's advantage
   never gets used.
2. **Linked list**, in principle — insertion in the middle is cheap. In practice
   real editors use a *gap buffer* or a *rope*, because a list of individual
   characters wastes enormous memory and destroys cache performance. Both halves
   of that answer are worth giving.
3. Because every value takes the same amount of room and they are packed with no
   gaps, you can work out where the 7th one begins by multiplying — you never
   have to look at the first six.
4. **Insertion at the front.** Everything already there must physically move one
   place along, because the values are required to stay packed together with no
   gaps.
5. The array gives instant access to a *bucket*; the lists let each bucket hold
   several items that happen to collide, growing and shrinking without
   disturbing the other buckets. Neither property alone is enough.

### Chapter 2 — Memory and addresses

1. $2^{16} = 65{,}536$. Each of the 16 bits doubles the number of patterns.
2. $2000 + 6 \times 8 = 2048$. $S = 8$ because a `double` is 8 bytes.
3. The **name** is a label you write in your source code and the compiler throws
   away. The **address** is which numbered byte the value starts at. The
   **value** is what is stored in those bytes.
4. The addresses change between runs (address space layout randomisation) but
   the *difference* between two locals in the same frame usually does not.
5. It reports the exact line of the out-of-bounds access, the size of the object
   and how far past it you went — none of which the plain build mentions at all.
6. Because an array is one object with a guaranteed layout, while three
   variables are three separate objects the compiler may place, reorder, pad or
   keep entirely in registers.

### Chapter 3 — Big O

**A** $O(n)$ time, $O(1)$ space — two sequential loops add, they do not multiply.
**B** $O(n \log n)$ — the outer loop runs $\log_2 n$ times, the inner $n$ times.
**C** $O(n)$ time and $O(n)$ space — the by-value parameter is one copy and
`copy` is a second.
**D** $O(n^3)$ — the triangular version of a triple loop is $n^3/6$, and the
constant is dropped.
**E** $O(n^2)$ — `insert` at the beginning shifts everything, $n$ times.

6. $O(n^2)$. The $50n$ term is larger while $n^2/1000 < 50n$, that is
   $n < 50{,}000$. So for every input below fifty thousand the "dominant" term is
   not dominant at all — which is why Big O is a statement about scaling, not a
   prediction for a particular input.
7. $O(1)$, $O(\log n)$, $O(n)$ and $O(n \log n)$ are comfortable ($10^6$ and
   $2 \times 10^7$ operations). $O(n^2)$ is $10^{12}$ — about three hours. Not
   acceptable.

## Part II — Chapters 4 to 7

### Chapter 4 — The array

1. Last index 5; `sizeof(arr)` is 24 bytes.
2. $3000 + 5 \times 8 = 3040$.
3. `for (int i = n - 1; i >= 0; --i)`. The condition must be `>= 0`, not `> 0`,
   or element 0 is never printed.
4. Because the index says how far to move from the beginning, and the first
   element is where the beginning already is — you move nothing.
5. The sanitizer names the line, the array, its size and the offset read. The
   plain build prints a plausible-looking number and exits successfully.
6. `i <= n` reads `arr[n]`, one past the end.
7. Because the bytes immediately after the block were never reserved for it and
   are probably in use by something else. Growing means finding a bigger free
   block elsewhere and copying — which is what `std::vector` does.

### Chapter 5 — Vectors and capacity

1. Seven reallocations (at 1, 2, 4, 8, 16, 32, 64), ending with capacity 128.
2. $1 + 2 + 4 + 8 = 15$ copies for 16 pushes, and $15 < 32$. The series is
   always under $2n$.
3. Most pushes are free because there is spare room. Occasionally the vector
   runs out and has to move everything, which is expensive — but because the
   capacity doubles, those moves get rarer exactly as fast as they get bigger,
   so the *average* cost per push stays constant.
4. It prints `0`, then reads `v[0]` on an empty vector — undefined behaviour.
   `reserve` sets capacity, not size.
5. It is building the reverse of `in`. Write
   `std::vector<int> out(in.rbegin(), in.rend());`, or push forwards and call
   `std::reverse`. Either is $O(n)$.
6. Yes. The series becomes $1 + 1.5 + 1.5^2 + \cdots$, which is still geometric
   and still sums to a constant multiple of $n$. Any growth **factor** greater
   than 1 works; a growth **increment** does not.
7. Because you will probably refill it, and keeping the block avoids
   reallocating. It wastes memory when you clear a huge vector and never reuse
   it — then use the swap idiom: `std::vector<int>().swap(v);`.

### Chapter 6 — Core array operations

1. Inserting at index 0 of `{1,2,3}`: `v[3]=v[2]`, `v[2]=v[1]`, `v[1]=v[0]`,
   `v[0]=5` — three moves. At index 3: zero moves.
2. Copying forwards from the insertion point gives `{1,2,2,2}` — every slot
   becomes a copy of the first one moved, because each read happens after the
   write that destroyed it.
3. Scan for the value, then shift everything after it left and `pop_back`. With
   two occurrences it removes only the first, and the function should say so in
   its name or its documentation.
4. Compare `v[r]` with `v[w - 2]`, and start `w` at `min(2, n)` so the first two
   elements are always kept.
5. Walk from the **right** with a write pointer starting at `n - 1`, copying
   non-zeroes; then fill the remaining front slots with zeroes.
6. The loop runs the full length, so each pair is swapped twice and the array is
   unchanged. `{1,2,3,4}` comes back as `{1,2,3,4}`.
7. $1000 \times 100{,}000 = 10^8$ operations. Build one frequency map in $O(n)$
   and answer each query in $O(1)$: $O(n + q)$ total, at the cost of $O(k)$
   space for the distinct values.
8. Deduplicate **first**. Moving zeroes first would scatter the duplicates away
   from each other, and the deduplication step depends on duplicates being
   adjacent.

### Chapter 7 — 2-D arrays

1. Flat index $3 \times 8 + 6 = 30$; address $4000 + 30 \times 4 = 4120$.
2. $r = 30 / 7 = 4$, $c = 30 \bmod 7 = 2$.
3. Sum the first and last rows entirely, then the first and last columns
   excluding their first and last elements — otherwise the four corners are
   counted twice.
4. `c = r + 1` visits each unordered pair once. `c = r` would swap the diagonal
   element with itself, which is harmless but pointless. `c = 0` swaps every
   pair twice and leaves the matrix unchanged.
5. Compare `g[r][c]` with `g[c][r]` for `c > r` only — $n(n-1)/2$ comparisons.
6. Both are $\Theta(R \cdot C)$. The difference is a **constant factor** of
   roughly 3–6×, caused by cache behaviour, which Big O deliberately ignores.
7. Row $r$ has $r + 1$ entries; `tri[r][0] = tri[r][r] = 1`, and for
   $0 < c < r$, `tri[r][c] = tri[r-1][c-1] + tri[r-1][c]`.

## Part III — Chapters 8 to 17

### Chapter 8 — Linear traversal

1. Three variables (`best`, `second`, `third`), updated in strict descending
   order: shift `second` into `third`, then `best` into `second`, then set
   `best`. The order is the whole difficulty, exactly as with two.
2. Compare `v[i]` with both neighbours for `0 < i < n-1`. The two ends have only
   one neighbour each and so can never qualify — state that explicitly rather
   than letting it happen by accident.
3. Carry two booleans, `couldBeAscending` and `couldBeDescending`, and clear
   whichever a violation rules out. `{3,3,3}` satisfies both under
   non-strict comparison, so it is sorted in either direction.
4. Running state: `currentValue`, `currentLength`, `bestValue`, `bestLength`.
   Reset the current pair when the value changes.
5. A sliding window where the window is invalid once it contains two zeroes —
   Chapter 10. One pass is possible; it is not a pure linear traversal, which is
   why the exercise says to come back.
6. You cannot compare an element with the average until you have seen every
   element, and the last one can change the average. A **running total** can be
   compared against as you go, because it depends only on the past.
7. It needs to know about the future as well as the past, so one pass with a
   fixed notebook is not enough. Prefix maxima and suffix minima (Chapter 11)
   make it two passes and $O(n)$.

### Chapter 9 — Two pointers

1. `{1,3,4,6,8,11}`, target 10: $(0,5) \to 12$ too big; $(0,4) \to 9$ too small;
   $(1,4) \to 11$ too big; $(1,3) \to 9$ too small; $(2,3) \to 10$ found. Five
   iterations, replacing 15 brute-force pairs.
2. On a match, record it and move **both** pointers, then skip past any
   duplicates of the values just used — `while (left < right && v[left] ==
   v[left-1]) ++left;` and the mirror on the right.
3. Advance `left` past non-letters and retreat `right` past non-letters before
   each comparison, then compare lowercased. Both skips must happen before the
   comparison, not after.
4. Sort, then for each `i` run two pointers on `i+1 .. n-1` looking for
   `-v[i]`. The outer loop is $n$ and each inner scan is $O(n)$, so $O(n^2)$ —
   not $O(n^3)$, because the inner search is linear rather than quadratic. Skip
   duplicates at every level.
5. No such input exists. Moving the taller wall keeps the same (or a smaller)
   minimum height while reducing the width, so the area cannot increase.
6. Start at both ends of the input and fill the output from the **back**,
   because the largest square is always at one end or the other — the most
   negative or the most positive value.
7. Converging pointers that each skip forward to the next vowel, then swap.
8. Moving a pointer inwards is justified only by knowing that every pair using
   it is now impossible, and that conclusion depends on the remaining elements
   being bounded by the current one — which is exactly what sortedness provides
   and what unsorted data does not.

### Chapter 10 — Sliding window

1. With target 9, row 2's sum of 8 is unchanged, but at `right = 3` the sum of 9
   is no longer over the target, so nothing shrinks and the window `2 1 5 1` has
   length 4. The answer becomes 4.
2. The shape is the same; the shrink condition becomes "while the window is
   still **valid**", and you record the length *inside* the shrink loop rather
   than after it — because for a minimum you want the smallest valid window, not
   the largest.
3. Track the running sum and divide only once at the end, or compare sums
   directly since all windows have the same size. Dividing inside the loop costs
   a division per step and introduces floating-point error.
4. The window state is the number of zeroes it contains; it is invalid when that
   count exceeds 1. Shrink from the left until it is 1 again.
5. Change the constant 1 to $k$. Nothing else.
6. The state is a map from character to count; the window is invalid when the
   map has more than two entries. Erase a key when its count reaches zero, or
   the size test is wrong.
7. `{5, -3, 4}` with target 5: the window `5 -3 4` sums to 6 and is invalid, but
   shrinking from the left gives `-3 4` = 1, which is valid — so the sum did not
   decrease monotonically as the window shrank, and the shrink rule's assumption
   fails.
8. A fixed window of `s1.size()`, with two 26-entry count arrays compared each
   step. Comparing two 26-entry arrays is $O(1)$, so the whole thing is $O(n)$;
   maintaining a single "number of matching letters" counter removes even that.

### Chapter 11 — Prefix sums

1. `{0, 5, 3, 10, 11}`. Sum of `v[1..3]` is $11 - 5 = 6$.
2. So that `sum(0, j)` is `prefix[j+1] - prefix[0]` with `prefix[0] = 0`. Without
   the extra entry, any range starting at index 0 needs a special case.
3. Store the **earliest** index at which each prefix value occurred, and never
   overwrite it — an earlier start gives a longer sub-array. Seed the map with
   `{0: -1}`.
4. Only the parity of each prefix matters, so there are two classes. Count how
   many prefixes are even and how many odd; the answer is
   $\binom{e}{2} + \binom{o}{2}$ where $e$ includes the empty prefix.
5. Map 0 to $-1$, then the sub-arrays with equal counts are exactly those with
   sum 0 — the previous exercise's machinery with $K = 0$.
6. With $K = 0$ and input `{0}`: inserting first puts `0 → 1` in the map, then
   the lookup for `running - 0 = 0` finds it and counts the single element twice
   over — once legitimately and once against itself.
7. All ones: `P[r][c] = r × c`. The middle $2 \times 2$ is
   $P[3][3] - P[1][3] - P[3][1] + P[1][1] = 9 - 3 - 3 + 1 = 4$. Correct.
8. Changing `v[i]` invalidates every prefix entry from $i+1$ onwards, so a
   rebuild is $O(n)$ per update. With frequent updates, a Fenwick tree or
   segment tree gives $O(\log n)$ for both update and query.

### Chapter 12 — Binary search

1. `{1,3,5,7,9,11}` for 11: `mid=2` (5 < 11, lo=3); `mid=4` (9 < 11, lo=5);
   `mid=5` (11, found). Three comparisons.
2. Searching for 6: `mid=2` (5<6, lo=3); `mid=4` (9>6, hi=3); `mid=3` (7>6,
   hi=2). Now `lo=3 > hi=2`, the loop ends. Note that `lo` is the index where 6
   *would* be inserted — which is exactly what `lower_bound` returns.
3. With `hi = size()` and `while (lo < hi)`: the right branch becomes `hi = mid`
   (not `mid - 1`), because `hi` is now exclusive. The left branch stays
   `lo = mid + 1`. Both conventions are correct; mixing them is not.
4. After a match at `mid`, any earlier occurrence must be strictly left of
   `mid`, so `hi = mid - 1` is right. `hi = mid` would leave `mid` in the region
   and, on a two-element array of equal values, loop forever.
5. Find which half is sorted by comparing `v[lo]` with `v[mid]`, then test
   whether the target lies within that sorted half's range; search there if so,
   the other half if not.
6. The test is "is `v[mid] < v[mid+1]`?" — if yes the peak is to the right, if no
   it is at `mid` or to the left. Binary search needs only a **monotonic
   predicate**, not a sorted array, and this is the cleanest demonstration of
   that.
7. Candidates are speeds 1 to `max(piles)`. The test is "can all piles be eaten
   in $H$ hours at speed $k$?", computed by summing $\lceil p_i / k \rceil$. It
   is monotonic because a larger speed never takes more time.
8. The comparisons are logarithmic, but a list cannot jump to its middle — each
   "jump" is a walk of up to $n/2$ nodes, so the walking dominates.

### Chapter 13 — In-place modification

1. Rotating left by 2 is rotating right by $n - 2 = 3$: reverse all, reverse the
   first 3, reverse the last 2. Equivalently, reverse the first 2, reverse the
   last 3, then reverse all.
2. `v.begin() + 5` on a 3-element vector is past the end; `std::reverse` on that
   range is undefined behaviour.
3. Use the sign-marking trick: the slot that is already negative when you reach
   it identifies the duplicate, and the slot that is still positive after the
   pass identifies the missing value.
4. The answer must be in $1..n+1$, because $n$ slots cannot contain more than
   $n$ distinct positive integers — so if $1..n$ are all present the answer is
   $n+1$. Place each value $x$ in $1..n$ into slot $x-1$ by swapping, then scan
   for the first slot whose value is wrong.
5. Dutch National Flag — `low`, `mid`, `high`. See Chapter 19.
6. You must remember every value seen so far, and the number of distinct values
   can be $n$. Any structure holding that is $O(n)$. Sorting would allow $O(1)$
   space but destroys the required order.
7. `abs(0) - 1` is $-1$, which is not a valid index. Shift the mapping: use
   index $|v| $ rather than $|v| - 1$ with an array one larger, or mark with a
   sentinel value that cannot occur.
8. Filling from the front overwrites elements of `a` that have not been placed
   yet. Filling from the back writes only into the spare slots, which by
   definition hold nothing that matters.

### Chapter 14 — Frequency counting

1. Two passes with a 256-entry count array: one to count, one to find the first
   character whose count is 1. $O(n)$ time, $O(1)$ space.
2. Put the **smaller** array into the set, then scan the larger one. The set's
   size is then $O(\min(n, m))$ rather than $O(n)$.
3. XOR works because $x \oplus x = 0$ and XOR is commutative and associative, so
   the pairs cancel in any order and only the lone value survives.
4. Either the sorted characters of the word, or a 26-entry count signature. The
   first is simpler; the second is faster for long words.
5. Boyer–Moore pairs off each majority element with a non-majority one; since
   the majority has more than half the votes, it cannot be fully cancelled.
   See Chapter 19.
6. `{3, 2, 4}` with target 6: inserting first means 3 is already in the map when
   you look for its complement 3, giving $(0, 0)$.
7. A hash map — a count array of $10^9$ entries is 4 GB, while the map holds at
   most $10^5$ entries.
8. Put every value in a set, then for each value `x` **only start counting if
   `x - 1` is absent**. That guarantee means each run is walked exactly once in
   total, so the whole thing is $O(n)$ rather than $O(n^2)$.

### Chapter 15 — Sorting first

1. Sort, then check for three equal neighbours — `v[i] == v[i+2]`. $O(n \log n)$
   time, $O(1)$ extra.
2. Remove the `out.back() != x` guards and always push. Equal elements from both
   arrays are then both kept.
3. Sort, fix `i`, two-pointer the remainder. The sort is $O(n \log n)$ and the
   loop is $n$ scans of $O(n)$, so $O(n^2)$ overall. Skip duplicates for `i`, and
   after each match skip duplicates for both inner pointers.
4. Separating the starts from the ends works because you only need to know *how
   many* meetings are active at each moment, not which ones. Sweep both sorted
   arrays together, incrementing on a start and decrementing on an end, and take
   the maximum.
5. The standard requires a *strict weak ordering*, meaning `comp(a, a)` must be
   false. `<=` violates it, and `std::sort` may then read outside the range —
   undefined behaviour, not merely a wrong order.
6. `std::sort` is $O(n \log n)$ and orders all $10^7$ elements; `nth_element` is
   $O(n)$ average and merely partitions around the median. The second does
   roughly a fifth of the work.
7. Sort with `a + b > b + a` as strings — `"9" + "5" = "95"` beats
   `"5" + "9" = "59"`, so 9 comes first. It looks wrong because it compares
   concatenations rather than values, and it is right for exactly that reason.
8. Two Sum returning indices. Sorting destroys the positions; use a hash map, or
   sort `(value, index)` pairs if $O(n)$ space is acceptable anyway.

### Chapter 16 — Kadane

1. `{5,-2,3}`: $5 \to 3 \to 6$, best 6, no restarts. `{-1,-2,-3}`:
   $-1 \to -2 \to -3$ — each step restarts, because the running sum is always
   negative; best is $-1$.
2. Initialise `endingHere` and `best` to 0 and use
   `endingHere = max(0, endingHere + v[i])`. Two lines.
3. Either the sub-array does not wrap (plain Kadane) or it does, in which case
   the excluded elements form a contiguous minimum — so the answer is
   `total - minSubarraySum`. **Edge case:** if every element is negative,
   `total - min` is 0, meaning "take nothing"; return the plain Kadane answer
   instead.
4. `endingHere` is the length of the increasing run ending at $i$; it restarts at
   1 whenever `v[i] <= v[i-1]`.
5. Two variables: the best including house $i$ and the best excluding it. The
   recurrence is `incl = excl + v[i]` and `excl = max(incl_prev, excl_prev)`.
6. The running product at the middle is $-6$, which a max-only Kadane would
   discard; multiplied by the final $-4$ it becomes 24, the answer.
7. Four running values: the best after buying once, after selling once, after
   buying twice, after selling twice — each updated from the previous.
8. The sub-problem is "the maximum sum of a sub-array ending exactly at $i$",
   and the recurrence is
   $\text{end}(i) = \max(v[i],\, \text{end}(i-1) + v[i])$. That is a dynamic
   program with one state variable and $O(1)$ memory.

### Chapter 17 — Matrix patterns

1. $(0,0) \to (2,0)$, $(0,2) \to (0,0)$, $(2,2) \to (0,2)$, giving
   $(r,c) \to (n-1-c,\, r)$. As two steps: transpose, then reverse each
   **column** — or reverse each row first, then transpose.
2. Rotate 90° twice, or equivalently reverse the order of the rows and then
   reverse each row.
3. On a $3 \times 5$ grid, after the top row and the right column are consumed,
   `top` becomes 1 and `right` becomes 3; the first guard matters on the final
   inner ring, when `top > bottom` and the bottom row would otherwise be
   re-traversed.
4. Use row 0 and column 0 as the marker arrays. The cell `g[0][0]` is shared by
   both, so it cannot record two independent facts — keep a separate boolean for
   whether column 0 itself must be cleared, and process row 0 and column 0 last.
5. At the top-left, a value smaller than the target could be anywhere to the
   right **or** below, and a larger value rules out nothing useful — so no
   comparison eliminates a whole row or column.
6. Depth-first search from each unvisited 1, marking cells as visited (or
   overwriting them with 0) as you go. Each cell is visited once, so it is
   $O(R \cdot C)$ in total however many islands there are.
7. A diagonal is a set of cells with constant $r - c$ (or constant $r + c$ for
   the anti-diagonal direction) — Chapter 7 gave both.
8. On $1000 \times 1000$: staircase is 2,000 steps; per-row binary search is
   $1000 \times 10 = 10{,}000$. Staircase wins. On $10 \times 100{,}000$:
   staircase is 100,010 steps; per-row binary search is
   $10 \times 17 = 170$. Binary search wins by a wide margin — the shape of the
   matrix decides.

## Part IV — Chapters 18 to 20

### Chapter 18 — Foundational problems

1. Write them, then test each on: `{}`, `{5}`, `{3,3,3}`, `{-1,-9,-4}`. Those
   four inputs catch most of the standard bugs.
2. 1–3 and 10 are linear traversal; 4 and 8 are two pointers; 5–7 are the write
   pointer and reversal; 9 and 11 are arithmetic identities.
3. Problems 5 (already requires sorted), 8 (already sorted) and 11 (sorting
   would put the pairs adjacent). For 11, sorting costs $O(n \log n)$ and the
   XOR answer is $O(n)$ with $O(1)$ space, so it is never worth it.
4. 9 (sum or XOR) and 11 (XOR).
5. One pass with a write pointer: keep an element if it differs from the last
   kept value **and** is non-zero; then pad with the zeroes you counted.
6. The sum $n(n+1)/2$ overflows a signed 32-bit `int` when $n(n+1)/2 > 2^{31}-1$,
   that is around $n = 65{,}535$. XOR has no equivalent limit — it never produces
   a value outside the range of its inputs.

### Chapter 19 — Intermediate problems

1. Work through each; the single observation is listed in Table 19.1's right-hand
   column.
2. **Boyer–Moore:** each decrement pairs one majority element with one
   non-majority element and removes both; the non-majority elements run out
   first because there are fewer than $n/2$ of them. **Floyd on an array:** the
   array defines a function $i \mapsto v[i]$ that never escapes $1..n$, so
   iterating it must cycle; two positions holding the same value point to the
   same place, which makes the duplicate the cycle's entrance.
3. `a = {1,2,3,_,_,_}`, `b = {2,5,6}`. Filling forwards, the first comparison
   writes 1 into `a[0]` — which already held 1, so no harm yet; but at the second
   step `b[0] = 2` would be written into `a[1]`, destroying the 2 that has not
   been placed. Filling from the back writes only into slots that are empty.
4. `total = product of all; out[i] = total / v[i]`. It breaks on any input
   containing a zero (division by zero for that element, and every *other*
   element's answer is 0 rather than `total/v[i]`), and on two or more zeros,
   where every answer is 0. Handling it needs a zero count and three branches.
5. Problem 9 counts **every** occurrence of each prefix value; problem 10 keeps
   only the **earliest**. One `if` guards the insertion.
6. Sorting plus two pointers. $O(n \log n)$ for the sort plus $O(n^2)$ for the
   scans, so $O(n^2)$.
7. The three-pointer method handles exactly three values. For $k$ values you
   would need $k$ boundaries, which becomes unmanageable around $k = 4$; use
   counting sort ($O(n + k)$) instead, which is the natural generalisation.

### Chapter 20 — Advanced problems

1. `{4,5,6,7,0,1,2}` for 0: `mid=3` (7), `v[0]=4 <= 7` so the left half is
   sorted; is $4 \le 0 < 7$? No, so go right: `lo=4`. `mid=5` (1),
   `v[4]=0 <= 1` so the left half is sorted; is $0 \le 0 < 1$? Yes, so
   `hi=4`. `mid=4` (0) — found.
2. Compare `v[mid]` with `v[hi]`: if `v[mid] > v[hi]` the minimum is strictly
   right of `mid`, so `lo = mid + 1`; otherwise it is at `mid` or left, so
   `hi = mid`. Comparing with `v[lo]` instead fails on an unrotated array.
3. Writing all three and cross-checking on random inputs is the exercise; the
   agreement between them is the proof that you understood each.
4. `{4,2,0,3,2,5}`: maxLeft is `{4,4,4,4,4,5}` and maxRight is `{5,5,5,5,5,5}`,
   so the water is `{0,2,4,1,2,0}` — total 9.
5. The stack fills water in **horizontal layers** between a bar and the previous
   taller bar, rather than computing a vertical column at a time. Both reach 9;
   the intermediate quantities are completely different.
6. With all values equal, `v[lo] == v[mid] == v[hi]` gives no information about
   which half is sorted, so the only safe step is to shrink the range by one at
   each end — $O(n)$. The worst case is an array of identical values with the
   target absent.
7. It most resembles approach B: for each bar you need the nearest shorter bar on
   each side, which is a pair of precomputed arrays — classically built with a
   monotonic stack rather than prefix maxima.
8. Even negatives: `{-2, -3}` gives 6. Stopping before a zero: `{-2, 3, 0, 4}`
   gives 4, because the zero resets both running values and the best before it
   was 3.

## Part V — Chapters 21 and 22

### Chapter 21 — Pointers

1. `x` is the value 5; `&x` is where it lives; `p` holds that same address;
   `*p` follows it back to 5; `&p` is where the pointer variable itself lives.
2. Prints `10 20`. `*p = 10` writes through `p` into `a`; then `p` is reseated to
   `&b` and `*p = 20` writes into `b`.
3. The pointer version is called as `swap(&a, &b)` and can be passed `nullptr`;
   the reference version is called as `swap(a, b)` and cannot. The reference
   version is easier to call and impossible to misuse, so prefer it unless
   absence is meaningful.
4. `p` is a pointer, and `.` is for objects. Change it to `p->x`, which is
   `(*p).x`.
5. `p + 1` moves `sizeof(int)` = 4 bytes, because pointer arithmetic is scaled by
   the pointed-to type. `(char*)p + 1` moves exactly 1 byte.
6. A `nullptr` is explicitly, checkably invalid, and dereferencing it crashes
   immediately. A dangling pointer looks valid, often still reads the old value,
   and fails later and elsewhere — which makes it far more dangerous.
7. `void zeroIfNotNull(int* p) { if (p) *p = 0; }`. A reference cannot express
   "there may be nothing here" — a reference must always bind to an object.
8. `pp` holds the address of `p`, which holds the address of `x`; `**pp` is 1.
   You need a pointer to a pointer when a function must change the caller's
   pointer itself — which is exactly what `Node**` does in C-style linked list
   code, and what `Node*&` does more readably in C++.

### Chapter 22 — Stack, heap, new and delete

1. Stack: `int x`, `int* p` (the pointer), `std::vector<int> v` (the object),
   `Node* head` (the pointer). Heap: the `int` that `p` points at, `v`'s element
   block, and the node `head` points at.
2. `new int[10];` with no `delete[]` leaks 40 bytes; the sanitizer reports the
   size and the allocating line.
3. `leak2`: `delete p;` before reassigning. `leak3`: either `delete p;` before
   the early return, or restructure so there is a single exit — the second is
   better, because it cannot be forgotten when a third return is added later.
   Best of all: use `std::unique_ptr` and neither problem exists.
4. Nothing at all; it is explicitly defined as a no-op. That is what makes
   `delete p; p = nullptr;` safe against a second delete.
5. The sanitizer reports zero leaks for the correct version, and a
   heap-use-after-free with both stack traces for the broken one.
6. `delete head` frees only the first node. The second node is still allocated,
   and the only pointer to it was `head->next`, which has just been freed —
   so it is unreachable. Leaking 1 of 2 nodes.
7. Each recursive call pushes a frame; an iterative loop reuses one. 1 MB ÷ 64
   bytes ≈ 16,000 frames before overflow.
8. `std::unique_ptr<Node> head` with `std::unique_ptr<Node> next` inside each
   node. Easier: no `delete` anywhere, and no possible leak. Harder: moving
   nodes between lists requires `std::move`, reversal becomes noticeably more
   awkward, and destroying a long list recurses through the destructors and can
   overflow the stack — which is itself a good lesson.

## Part VI — Chapters 23 to 28

### Chapter 23 — The linked list idea

1. Four boxes, each split into data and next, with arrows between them, a `head`
   arrow into the first, and `nullptr` after the last.
2. `head->next->next->data` is 15. `head->next->next->next->next` is `nullptr` —
   the fourth node's `next`.
3. Binary search requires reaching the middle element in $O(1)$; a list requires
   $O(n)$ to reach it, so each "halving" costs a linear walk and the whole thing
   degenerates to $O(n)$.
4. 4 bytes of data plus 8 bytes of pointer is 12, but allocators round up and
   add bookkeeping — typically 32 bytes per node. So roughly 32 MB against the
   array's 4 MB: about **8×**.
5. Right: an LRU cache, where a hash map hands you node pointers and you unlink
   in $O(1)$. Wrong: anything you index into, or any large collection of small
   values you mostly scan.
6. `head = head->next;` in a loop without saving anything, or simply
   `head = nullptr;` while nodes are still allocated.
7. There is no `nullptr`, so the loop never terminates. Use
   `do { ... } while (curr != head);` guarded by a check that the list is
   non-empty.

### Chapter 24 — Building a list

1. `struct Node {` opens a new type; `int data;` is the stored value;
   `Node* next;` is a pointer to the following node; `Node(int value) {` is the
   constructor; the two assignments initialise both fields; `};` closes the type.
2. A `Node` containing a `Node` would contain another, forever, so its size could
   not be computed and the compiler rejects it. A pointer is a fixed 8 bytes
   whatever it points at, so the type's size is finite.
3. `head->next->next->data`.
4. Both should walk with `curr`. `sum` returns 0 for an empty list, which is the
   natural identity. `maxValue` has no answer for an empty list — throw, or
   return a flag, and say which you chose.
5. Two passes: count the length $n$, then walk $n - k$ nodes. The one-pass
   version is the fixed-gap pattern of Chapter 29.
6. `delete head;` runs before `head = head->next;`, so the second line reads
   through a freed pointer. It also leaks everything after the first node once
   the read returns rubbish.
7. `void freeList(Node* h) { if (!h) return; freeList(h->next); delete h; }`.
   It uses one frame per node, so it overflows at roughly 16,000 nodes with a
   1 MB stack — which is why list code is written iteratively.

### Chapter 25 — Insertion

1. `node->next = head->next->next` (the node holding 30), then
   `head->next->next = node`. Two changes, in that order.
2. `insertBack` becomes $O(1)$; `deleteBack`, `deleteValue` and any `clear` must
   now update `tail`, or it will dangle.
3. Walk with `prev` until `prev->next->data >= value`. The head case — inserting
   before the current first node — is the one that changes `head`, and a dummy
   node removes it.
4. It should succeed: `pos == length` means "append". Check that your loop's
   range tests allow it; many implementations reject it by accident.
5. `Node** head` requires `*head = node;` and calls like `insertFront(&head, 5)`.
   C has no references, so `**` is the only option there; C++ has both, and
   `Node*&` reads better.
6. Return without doing anything. Without the check it dereferences `nullptr`
   and crashes.
7. Insert a new node after `node`, then swap the two nodes' `data`. It is
   unacceptable when copying the data is expensive, when the data cannot be
   copied, or when another part of the program holds a pointer to the original
   node and expects its value to stay put.
8. Roughly a factor of $n/2$ — several seconds versus a few milliseconds at
   100,000 elements. Without the tail pointer the total work is
   $1 + 2 + \cdots + n = n^2/2$ pointer hops.

### Chapter 26 — Deletion

1. `doomed = head` · `head = head->next` · `delete doomed`. Moving the delete
   before the advance reads a freed pointer; removing the save leaks the node.
2. Because you must set the *second-to-last* node's `next` to `nullptr`.
   `while (prev->next != nullptr)` leaves `prev` on the **last** node, where
   setting `prev->next = nullptr` does nothing useful.
3. Walk the whole list keeping track of the last matching node's predecessor,
   then unlink after the walk. One pass is enough — you simply cannot act until
   you know there is nothing later.
4. On `{7, 7}`, removing the first 7 leaves `prev->next` pointing at the second
   7; advancing `prev` skips it. Output keeps one 7.
5. It is "remove duplicates from a sorted array" with pointers — compare each
   node with the next and unlink when equal.
6. The sanitizer reports a leak naming the `new` that created the node you
   stopped freeing.
7. A tail pointer tells you where the last node *is*, but after deleting it you
   need the new last node — which is the second-to-last, and finding that
   requires walking. A doubly linked list gives it as `tail->prev`, in $O(1)$.
8. Three designs: return a `bool` success flag and take the value by reference;
   throw on an empty list; or return `std::optional<int>`. The third is clearest
   in modern C++ and impossible to misuse.

### Chapter 27 — Doubly and circular

1. Six pointers: three `next` (the last being `nullptr`), three `prev` (the
   first being `nullptr`).
2. `insertBefore` needs the node's predecessor, which `prev` supplies directly. A
   singly linked list would have to walk from the head to find it: $O(n)$.
3. You cannot unlink it without the predecessor, so you must walk from the head:
   $O(n)$. Chapter 31's trick copies the next node's data instead and deletes
   *that* node, in $O(1)$ — but it cannot handle the last node.
4. For each node, check `node->next == nullptr || node->next->prev == node`, and
   the mirror with `prev`.
5. Walk to the tail and set `tail->next = head`; to undo, walk until
   `curr->next == head` and set it to `nullptr`. To detect circularity, walk from
   `head->next` and see whether you return to `head` before reaching `nullptr`.
6. Build a circular list of $n$ nodes; repeatedly advance $k-1$ nodes and delete
   the next, until one remains. $O(n k)$ with a list; $O(n)$ with the
   mathematical recurrence.
7. `std::list::erase` holds the node and both its neighbours, so it is four
   pointer writes. `std::vector::erase` must shift every later element.
   `operator[]` is not provided because it would be $O(n)$ and would invite
   people to write accidentally quadratic loops.
8. A judgement call: the overhead is 400% for a 4-byte payload, 25% for a 64-byte
   one, and under 5% for a 512-byte one. Somewhere above a few hundred bytes it
   stops being a consideration.

### Chapter 28 — Reversal

1. Four iterations; after each, `prev` is the head of the growing reversed chain.
2. `prev` is the last node processed, which is the original tail — the new head.
   For an empty list the loop never runs, so `prev` stays `nullptr`, which is
   correct.
3. Empty: the loop body never executes, `head = prev` sets `nullptr` to
   `nullptr`. One node: one iteration sets its `next` to `nullptr` (already
   true), and `head = prev` names the same node.
4. Yes: it returns a one-element list, because `nextNode` reads the value that
   line 2 just wrote, which is `prev` — `nullptr` on the first iteration.
5. `Node* reverseList(Node* head)` returning `prev` is LeetCode's signature and
   is the more common convention; `Node*&` is more convenient when you own the
   list variable. Know both.
6. The node that was $k$-th (it becomes the tail of the reversed part) and the
   node that was $(k{+}1)$-th (the rest), so that you can join them afterwards.
7. Find the middle, reverse the second half, compare, then reverse it back.
   $O(n)$ time, $O(1)$ space — and restoring the list is the part that marks out
   a careful answer.
8. Swapping them sets `head->next = nullptr` first, so `head->next->next` then
   dereferences `nullptr` and crashes.

## Part VII — Chapters 29 to 32

### Chapter 29 — The patterns

1. The entire head-handling branch — roughly six lines — disappears, leaving one
   loop.
2. A stack dummy is freed automatically when the function returns. A heap dummy
   must be deleted, and the natural `return dummy->next` path makes it very easy
   to forget, leaking one node per call.
3. Count the length first, then walk $\lfloor (n-1)/2 \rfloor$ nodes. It is
   clearer to read and takes two passes; the `head->next` trick is one pass and
   slightly cryptic. Both are defensible.
4. $k = 0$ has no meaningful answer — reject it, or define it as "one past the
   last", and say which. A negative $k$ should be rejected outright.
5. $F$ is head-to-entrance, $a$ is entrance-to-meeting-point measured forward
   round the cycle, $L$ is the cycle length.
6. With speed 2 the gap shrinks by exactly 1 per step, so it cannot skip zero.
   With speed 3 it shrinks by 2 and could step straight over zero, so correctness
   would depend on $L$ being even or on a divisibility argument.
7. Change `a->data <= b->data` to `a->data >= b->data`, assuming both inputs are
   themselves descending.
8. Typically around 10,000 to 100,000 depending on the frame size and the stack
   limit. Measuring it yourself is the point of the exercise.

### Chapter 30 — Core problems

1. Writing them from memory, with those three tests each, is the exercise.
2. The two-pass version counts then walks; it is marginally clearer. Give the
   one-pass version, because the question is usually asking for it, but mention
   that two passes is equally $O(n)$.
3. With $n$ larger than the list, the function above returns the head unchanged.
   That is a defensible choice; throwing or returning an error flag is also
   defensible. What is not defensible is dereferencing `nullptr`.
4. A hash set of visited node pointers: $O(n)$ time, $O(n)$ space. You would
   prefer it only if you also need to know *which* nodes were visited, or if the
   list is being modified concurrently and Floyd's invariant could break.
5. One at a time: merging lists of sizes $n, 2n, 3n, \dots$ costs $O(k^2 n)$.
   Divide and conquer pairs them up, giving $O(k n \log k)$.
6. `detectCycle` returns the head itself, because the entrance is the head and
   $F = 0$.
7. No. The meeting point is somewhere inside the cycle but not necessarily just
   before the entrance, so you still need phase 2 to locate the entrance and then
   a walk round to its predecessor.

### Chapter 31 — Intermediate problems

1. Copy the values into a vector and use converging pointers: $O(n)$ time,
   $O(n)$ space. Prefer it when the list must not be modified at all — for
   example if another thread is reading it.
2. Construct two lists sharing a tail and count the steps; both pointers reach
   the shared node after exactly $a + b + c$ moves.
3. Either reverse both lists, add, and reverse the result; or push both onto
   stacks and pop. The stack version does not modify the inputs, which is usually
   preferable.
4. You need a dummy node (the head itself may be removed) and a `prev` pointer.
   The plain version keeps one copy of each duplicated value; this one must
   remove all of them, so you must skip the whole run and link `prev` past it.
5. There is no next node to take a value from. A doubly linked list would allow
   it, because the node knows its predecessor.
6. Splitting at the second middle on `{1,2,3,4}` gives halves of 3 and 1, so the
   interleave runs out of second-half nodes early and leaves the list wrong.
7. Make it circular, walk to the node $n - (k \bmod n) - 1$ steps from the head,
   and cut there — Chapter 32.

### Chapter 32 — Advanced problems

1. Use a dummy node and a `groupPrev` pointer; for each group, find the $k$-th
   node, remember what follows it, reverse the group, then re-link. The pointer
   bookkeeping is the whole difficulty, which is why the recursive version is
   usually given first.
2. Remove the early `return head` when fewer than $k$ nodes remain, and reverse
   whatever is left.
3. `{1,2,3}` with $k = 7$: `n - k - 1` is $3 - 7 - 1 = -5$, so the walk loop does
   not run and the "new tail" is the head — producing a rotation by 2 rather than
   by 1. Silently wrong rather than crashing, because the list is circular at
   that moment.
4. Rotating left by $k$ is rotating right by $n - (k \bmod n)$.
5. Bottom-up merges runs of size 1, then 2, then 4, splicing them back together
   with a dummy node. It is harder because you must split and re-join explicitly
   at every pass rather than letting the recursion do it.
6. Choosing a good pivot and partitioning both require random access. Reaching
   the middle of a list is $O(n)$, so median-of-three is expensive, and a
   first-element pivot degenerates to $O(n^2)$ on sorted input.
7. The map version is two clear passes and $O(n)$ space; the interleaving version
   is three subtler passes and $O(1)$ space. Give the map version first.
8. The original list would be left interleaved with the copy — so the caller's
   list is corrupted. The test is `original intact`, comparing `a->next == b`
   after the call.

## Part VIII and IX — Chapters 33 to 36

### Chapter 33 — The complexity showdown

1. The condition column is the point; check it row by row.
2. Appending a million integers: **array** (amortised $O(1)$, cache-friendly).
   Deleting the front a million times: **list** $O(1)$ each, though a deque is
   better than both. Finding the median: **array**, because `nth_element` needs
   random access. A drag-and-drop playlist: **list**, if you hold iterators to
   the dragged items; otherwise an array is fine and simpler.
3. Each halving step requires reaching the middle element of the current range,
   which on a list means walking there — $O(n)$ per step rather than $O(1)$.
4. A hash map from key to list node, plus a doubly linked list of nodes in
   recency order. `get` is $O(1)$: the map finds the node, the list moves it to
   the front. `put` is $O(1)$: insert at the front and, if full, remove the tail.
   Neither structure can do it alone.
5. *"Do you already hold an iterator to the insertion point, or do you search for
   it each time?"* If they search, both structures are $O(n)$ and the vector is
   faster.
6. Vector: about 4 MB. List: about 32 MB with typical allocator overhead. Roughly
   **8×**.
7. The array's accesses are sequential, so one cache line supplies 16 elements
   and the prefetcher stays ahead. The list's accesses form a dependent chain —
   the address of the next load is unknown until the current one returns — so
   they cannot be overlapped, and each may stall for hundreds of cycles.
8. **Wins:** an LRU cache's eviction, or splicing a 10,000-element range between
   two lists in $O(1)$. **Does not win despite the table:** inserting at the
   front of a 1,000-element container of `int`, where `memmove` beats the
   allocation.

### Chapter 34 — The method

1–7. These are process exercises; what matters is that you wrote the steps down
rather than did them in your head. For step 8, the bottleneck table is the
lookup; for step 14, the edge-case checklist in Chapter 35 is the list to run.

For exercise 1 specifically: the bottleneck is "it compares every pair of a
sorted array", so the pattern is converging two pointers, and the answer is
$O(n)$ after the array is already sorted.

For exercise 2: the bottleneck is "it rescans the list for each node", so the
pattern is a hash set of seen values — $O(n)$ time and $O(n)$ space — with a
dummy node because the head may be removed. The hard part is that you must
delete nodes while walking, which means keeping `prev`.

### Chapter 35 — C++ standards

1. Any function taking a container by value that does not need a copy should be
   `const&`. In most people's early code that is most of them.
2. Typically: signed/unsigned comparison warnings, unused parameters, and —
   if you wrote any linked list code — at least one leak.
3. It almost always does: `for (int row = 0; row < rows; ++row)` needs no comment
   where `for (int i = 0; i < n; ++i)` might.
4. For example, above a list traversal: *"an empty list needs no special case —
   the loop simply never runs."*
5. `a ^= a` sets `a` to 0, and the rest of the sequence keeps it at 0. The value
   is destroyed. `std::swap(a, a)` is harmless.
6. Under a minute with practice. Items 2, 4 and 10 catch most real problems.
7. In a header it injects every name in `std` into every file that includes it.
   A concrete collision: a variable or function called `count`, `distance`,
   `size`, `data` or `begin` — all of which are both common identifiers and
   names in `std`.

### Chapter 36 — The roadmap

The roadmap has no exercises of its own; its "answers" are the exit signals.
If you cannot yet meet a level's exit signal, the problems to repeat are the
ones in that level you needed a hint for.
