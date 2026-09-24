# Problem Set I: Foundations
@short: Problems I
@subtitle: Thirty graded problems with complete solutions
@tier: practice
@prereq: Chapters 1--21
@blurb: Problems for Parts I through IV, graded from straightforward to hard, each with a full solution and an explanation of why the solution has the shape it does. Attempt each one before reading its solution; the value is entirely in the attempt, and a failed attempt followed by a solution teaches far more than a solution alone.
@objectives:
- Apply the patterns of Chapter 44 to unfamiliar problems
- Recognise which technique a problem wants from its constraints
- Write correct boundary handling on the first attempt
- Build a reusable test harness habit

:::practice How to work through this
Give each problem twenty minutes before looking. Write the brute force
first, always. When you read a solution, close the book and reimplement it
from memory the next day --- that second pass is where the learning is.
Problems marked $\dagger$ are the ones most likely to appear in an
interview.
:::

## Arrays, hashing and windows

### P1. Two sum $\dagger$

Given an array and a target, return indices of two numbers summing to the
target. Unsorted, one solution guaranteed.

:::solution
Brute force is $\Theta(n^2)$. The waste: for each `x` we rescan for
`target - x`. A hash map makes that lookup $\Theta(1)$.

```python
def two_sum(a, target):
    seen = {}
    for i, x in enumerate(a):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i                 # store AFTER checking: handles x + x
    return None
```
$\Theta(n)$ time, $\Theta(n)$ space. Storing after the check is what makes
`target = 2x` with a single `x` correctly return nothing.
:::

### P2. Longest substring without repeating characters $\dagger$

:::solution
Variable window with a hash map of last positions. The left edge jumps
rather than crawling.

```python
def longest_unique(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1          # jump past the previous occurrence
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```
$\Theta(n)$. The `last[ch] >= left` guard matters: a character seen *before*
the window started must not move the left edge backwards.
:::

### P3. Subarrays summing to $k$, with negatives

:::solution
A sliding window is wrong here (the sum is not monotone in the window).
Prefix sums plus a hash map, pattern 18.

```python
from collections import defaultdict

def count_subarrays(a, k):
    seen = defaultdict(int)
    seen[0] = 1                       # the empty prefix
    s, count = 0, 0
    for x in a:
        s += x
        count += seen[s - k]
        seen[s] += 1
    return count
```
$\Theta(n)$. The `seen[0] = 1` initialisation accounts for subarrays that
start at index 0.
:::

### P4. Product of array except self

No division allowed, $\Theta(n)$ time.

:::solution
Two passes: prefix products left to right, then suffix products right to
left, multiplied in place.

```python
def product_except_self(a):
    n = len(a)
    out = [1] * n
    pre = 1
    for i in range(n):
        out[i] = pre
        pre *= a[i]
    suf = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suf
        suf *= a[i]
    return out
```
$\Theta(n)$ time, $\Theta(1)$ extra beyond the output. Avoiding division is
not pedantry: it makes the solution correct when the array contains zeros.
:::

### P5. Maximum subarray sum (Kadane) $\dagger$

:::solution
Linear DP: `best_ending_here` either extends the previous run or restarts.

```python
def max_subarray(a):
    if not a:
        return 0
    cur = best = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)         # extend, or start fresh at x
        best = max(best, cur)
    return best
```
$\Theta(n)$, $\Theta(1)$. The recurrence is
$f(i) = \max(a_i,\ f(i-1) + a_i)$ --- pattern 26.
:::

### P6. Sliding-window maximum $\dagger$

Maximum of every window of size $k$, in $\Theta(n)$.

:::solution
Monotonic deque of indices with decreasing values (pattern 8).

```python
from collections import deque

def window_max(a, k):
    dq, out = deque(), []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x:
            dq.pop()                       # x dominates everything smaller
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                   # expired
        if i >= k - 1:
            out.append(a[dq[0]])
    return out
```
Each index is pushed and popped once: $\Theta(n)$.
:::

### P7. Group anagrams

:::solution
Canonical key. Sorting each word is $\Theta(m \log m)$; a 26-element count
tuple is $\Theta(m)$ and faster for long words.

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        key = [0] * 26
        for ch in w:
            key[ord(ch) - 97] += 1
        groups[tuple(key)].append(w)
    return list(groups.values())
```
$\Theta(\sum |w_i|)$.
:::

### P8. Longest consecutive sequence

Unsorted array; find the longest run of consecutive integers, in $\Theta(n)$.

:::solution
Sorting is $\Theta(n \log n)$. Instead, start a run only from a value with no
predecessor --- which makes the total work linear.

```python
def longest_consecutive(a):
    s, best = set(a), 0
    for x in s:
        if x - 1 in s:
            continue                    # not the start of a run
        y = x
        while y + 1 in s:
            y += 1
        best = max(best, y - x + 1)
    return best
```
The inner loop runs only for run starts, and each element is visited at most
twice overall: $\Theta(n)$.
:::

### P9. Minimum window substring $\dagger$

Shortest substring of $S$ containing every character of $T$ with
multiplicity.

:::solution
Variable window plus a counter, with a scalar `missing` so validity is
$\Theta(1)$ to check.

```python
from collections import Counter

def min_window(s, t):
    if not t or len(s) < len(t):
        return ""
    need = Counter(t)
    missing = len(t)
    best, left = (0, float("inf")), 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:                 # valid: try to shrink
            if right - left < best[1] - best[0]:
                best = (left, right)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return "" if best[1] == float("inf") else s[best[0]:best[1] + 1]
```
$\Theta(|S| + |T|)$. `need` going negative for surplus characters is the
trick that keeps `missing` correct.
:::

### P10. Merge intervals

:::solution
Sort by start, then sweep, extending the current interval while it overlaps.

```python
def merge_intervals(intervals):
    if not intervals:
        return []
    out = []
    for lo, hi in sorted(intervals):
        if out and lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out
```
$\Theta(n \log n)$, dominated by the sort. Sorting by start is what makes a
single pass sufficient.
:::

## Sorting, searching and selection

### P11. $k$-th largest element $\dagger$

:::solution
Three correct answers with different profiles.

```python
import heapq, random

def kth_largest_heap(a, k):                 # theta(n log k), theta(k) space
    h = []
    for x in a:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)
    return h[0]

def kth_largest_select(a, k):               # theta(n) expected, in place
    a = list(a)
    lo, hi, target = 0, len(a) - 1, len(a) - k
    while True:
        if lo == hi:
            return a[lo]
        p = random.randint(lo, hi)
        a[p], a[hi] = a[hi], a[p]
        pivot, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        if i == target:
            return a[i]
        lo, hi = (lo, i - 1) if target < i else (i + 1, hi)
```
Use the heap for streams and bounded memory, quickselect in memory, and
`np.argpartition` for arrays.
:::

### P12. Search in a rotated sorted array $\dagger$

:::solution
One half of any split is always sorted; decide which, then whether the
target lies inside it.

```python
def search_rotated(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:                 # left half is sorted
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                               # right half is sorted
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```
$\Theta(\log n)$. With duplicates the `a[lo] <= a[mid]` test becomes
ambiguous and the worst case degrades to $\Theta(n)$.
:::

### P13. Median of two sorted arrays

$\Theta(\log(\min(m,n)))$.

:::solution
Binary search the *partition point* of the smaller array so that the left
parts of both arrays together hold exactly half the elements.

```python
def median_two_sorted(a, b):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2               # elements taken from a
        j = half - i                     # elements taken from b
        a_left = a[i - 1] if i else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return max(a_left, b_left)
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
```
The infinities remove every boundary special case --- a sentinel technique
worth reusing.
:::

### P14. Koko eating bananas $\dagger$

Given pile sizes and $H$ hours, find the minimum eating rate that finishes
in time.

:::solution
Binary search on the answer (pattern 11). `feasible(rate)` is monotone.

```python
import math

def min_rate(piles, H):
    def hours(rate):
        return sum(math.ceil(p / rate) for p in piles)
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if hours(mid) <= H:
            hi = mid
        else:
            lo = mid + 1
    return lo
```
$\Theta(n \log(\max p))$. Recognising "minimum $x$ such that" is the whole
problem.
:::

### P15. Sort colours (Dutch national flag)

Three values, one pass, in place.

:::solution
Three pointers partition into `< 1`, `== 1`, `> 1`.

```python
def sort_colours(a):
    lo, i, hi = 0, 0, len(a) - 1
    while i <= hi:
        if a[i] == 0:
            a[lo], a[i] = a[i], a[lo]; lo += 1; i += 1
        elif a[i] == 2:
            a[hi], a[i] = a[i], a[hi]; hi -= 1   # do NOT advance i
        else:
            i += 1
    return a
```
Not advancing `i` after a swap with `hi` is the classic bug: the incoming
element has not been examined yet.
:::

### P16. Count inversions

:::solution
Merge sort with a counter (Chapter 16).

```python
def count_inversions(a):
    def sort_count(x):
        if len(x) <= 1:
            return x, 0
        m = len(x) // 2
        left, cl = sort_count(x[:m])
        right, cr = sort_count(x[m:])
        out, i, j, cross = [], 0, 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
                cross += len(left) - i
        out += left[i:] + right[j:]
        return out, cl + cr + cross
    return sort_count(list(a))[1]
```
$\Theta(n \log n)$. This is how Kendall's $\tau$ is computed efficiently.
:::

## Linked structures, stacks and heaps

### P17. Reverse a linked list in groups of $k$

:::solution
Reverse each group with the three-pointer idiom, reconnecting as you go.

```python
class ListNode:
    __slots__ = ("val", "next")
    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt

def reverse_k_group(head, k):
    def length(n):
        c = 0
        while n:
            c += 1
            n = n.next
        return c

    dummy = ListNode(0, head)
    prev_group, remaining = dummy, length(head)
    while remaining >= k:
        cur = prev_group.next
        nxt = cur.next
        for _ in range(k - 1):               # rotate nxt to the front
            cur.next = nxt.next
            nxt.next = prev_group.next
            prev_group.next = nxt
            nxt = cur.next
        prev_group = cur
        remaining -= k
    return dummy.next
```
$\Theta(n)$ time, $\Theta(1)$ space. The "rotate to front" formulation avoids
a separate reverse-and-splice step.
:::

### P18. LRU cache $\dagger$

:::solution
Hash map plus doubly linked list with sentinels --- the full implementation
is in Chapter 6. The two points an interviewer listens for: the map stores
*nodes*, not values, so splicing is $\Theta(1)$; and sentinels remove every
edge case.
:::

### P19. Implement a queue with two stacks

:::solution
Push onto `inbox`; when `outbox` is empty, pour everything across.

```python
class Queue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def pop(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())
        return self.outbox.pop()
```
Amortised $\Theta(1)$: each element is moved at most once. The potential
function $\Phi = |\text{inbox}|$ gives the proof (Chapter 2).
:::

### P20. Merge $k$ sorted lists $\dagger$

:::solution
Heap of size $k$ (pattern 15): $\Theta(N \log k)$.

```python
import heapq

def merge_k_sorted(lists):
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    out = []
    while h:
        val, li, idx = heapq.heappop(h)
        out.append(val)
        if idx + 1 < len(lists[li]):
            heapq.heappush(h, (lists[li][idx + 1], li, idx + 1))
    return out
```
Merging pairwise instead would be $\Theta(Nk)$; divide-and-conquer pairwise
merging is also $\Theta(N \log k)$ and uses no heap.
:::

### P21. Find the median of a data stream $\dagger$

:::solution
Two heaps, balanced (Chapter 13). `push` is $\Theta(\log n)$, `median` is
$\Theta(1)$.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo, self.hi = [], []            # max-heap (negated), min-heap

    def add(self, x):
        heapq.heappush(self.lo, -heapq.heappushpop(self.hi, x))
        if len(self.lo) > len(self.hi):
            heapq.heappush(self.hi, -heapq.heappop(self.lo))

    def median(self):
        if len(self.hi) > len(self.lo):
            return float(self.hi[0])
        return (self.hi[0] - self.lo[0]) / 2.0
```
:::

### P22. Task scheduler with cooldown

Given task counts and a cooldown $k$, find the minimum number of time slots.

:::solution
A closed form beats simulation. The most frequent task determines the
skeleton: $(\text{max} - 1)$ full frames of length $k+1$, plus the tasks
tying for the maximum.

```python
from collections import Counter

def least_interval(tasks, k):
    counts = Counter(tasks)
    mx = max(counts.values())
    ties = sum(1 for v in counts.values() if v == mx)
    return max(len(tasks), (mx - 1) * (k + 1) + ties)
```
$\Theta(n)$. The `max` with `len(tasks)` handles the case where there are
enough distinct tasks to fill every gap.
:::

## Trees and recursion

### P23. Validate a binary search tree $\dagger$

:::solution
The classic wrong answer compares each node only with its children. The
property is about entire subtrees, so carry bounds down.

```python
def is_bst(node, lo=float("-inf"), hi=float("inf")):
    if node is None:
        return True
    if not (lo < node.val < hi):
        return False
    return (is_bst(node.left, lo, node.val)
            and is_bst(node.right, node.val, hi))
```
$\Theta(n)$. An in-order traversal checking that values strictly increase is
an equally valid and equally short alternative.
:::

### P24. Lowest common ancestor

:::solution
If both targets are in different subtrees, the current node is the answer.

```python
def lca(node, p, q):
    if node is None or node is p or node is q:
        return node
    left = lca(node.left, p, q)
    right = lca(node.right, p, q)
    if left and right:
        return node                   # p and q split here
    return left or right
```
$\Theta(n)$. For repeated queries, preprocess with binary lifting for
$\Theta(\log n)$ per query.
:::

### P25. Serialise and deserialise a binary tree

:::solution
Pre-order with explicit null markers is sufficient and reconstructs the
shape exactly.

```python
def serialise(node, out=None):
    out = [] if out is None else out
    if node is None:
        out.append("#")
    else:
        out.append(str(node.val))
        serialise(node.left, out)
        serialise(node.right, out)
    return ",".join(out)

def deserialise(data, Node):
    it = iter(data.split(","))
    def build():
        tok = next(it)
        if tok == "#":
            return None
        node = Node(int(tok))
        node.left = build()
        node.right = build()
        return node
    return build()
```
$\Theta(n)$. Pre-order *without* null markers is not enough --- it does not
determine the shape.
:::

### P26. Diameter of a binary tree

:::solution
The answer at each node is `height(left) + height(right)`; compute heights
and the best diameter in one pass.

```python
def diameter(root):
    best = 0
    def height(node):
        nonlocal best
        if node is None:
            return 0
        l, r = height(node.left), height(node.right)
        best = max(best, l + r)
        return 1 + max(l, r)
    height(root)
    return best
```
$\Theta(n)$. Computing the height separately inside the recursion would be
$\Theta(n^2)$ --- a common mistake.
:::

## Dynamic programming and greedy

### P27. Coin change (minimum coins) $\dagger$

:::solution
Unbounded knapsack: iterate the amount *upwards*.

```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return -1 if dp[amount] == INF else dp[amount]
```
$\Theta(\text{amount} \times |\text{coins}|)$. Greedy is wrong for general
denominations --- `coins = [1, 3, 4]`, `amount = 6` gives 4+1+1 greedily and
3+3 optimally.
:::

### P28. 0/1 knapsack $\dagger$

:::solution
Rolling array, inner loop *descending* so each item is used once.

```python
def knapsack(weights, values, W):
    dp = [0] * (W + 1)
    for w, v in zip(weights, values):
        for c in range(W, w - 1, -1):     # DESCENDING
            dp[c] = max(dp[c], v + dp[c - w])
    return dp[W]
```
$\Theta(nW)$ time, $\Theta(W)$ space. Ascending would solve the unbounded
version instead.
:::

### P29. Longest increasing subsequence $\dagger$

:::solution
The $\Theta(n \log n)$ version maintains `tails[k]` = the smallest possible
tail of an increasing subsequence of length $k+1$.

```python
from bisect import bisect_left

def lis(a):
    tails = []
    for x in a:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```
`tails` is *not* an LIS --- it is a set of best-possible tails --- so
recovering the actual subsequence needs a parent array alongside it.
:::

### P30. Jump game II

Minimum jumps to reach the end, where `a[i]` is the maximum jump from `i`.

:::solution
Greedy with a BFS-level interpretation: each "level" is the set of indices
reachable in the same number of jumps.

```python
def min_jumps(a):
    jumps = end = farthest = 0
    for i in range(len(a) - 1):
        farthest = max(farthest, i + a[i])
        if i == end:                      # exhausted the current level
            jumps += 1
            end = farthest
    return jumps
```
$\Theta(n)$. Seeing it as BFS on an implicit graph explains why greedy is
correct here while it fails on the related "minimum coins" problem.
:::

:::recap
- Every solution above came from the same procedure: brute force, identify
  the waste, choose the structure that removes it.
- The most frequent waste in this set was a repeated scan, removed by a hash
  map, a window, or a prefix sum.
- The second most frequent was excess ordering: needing the best $k$ and
  computing a total order. Heaps and quickselect fixed it.
- Boundary handling --- storing after checking, sentinels, infinities, not
  advancing after a swap --- is where most incorrect submissions fail.
- Reimplement each solution from memory a day later. That is the exercise.
:::
