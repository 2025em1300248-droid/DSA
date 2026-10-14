# Quizzes and Exercises
@short: Quizzes and Exercises
@subtitle: Multiple choice, trace the code, find the bug, write the code
@tier: practice
@prereq: the chapters each set covers
@blurb: Five kinds of exercise, because they test different things. Multiple choice checks recall; tracing checks whether you can simulate code rather than recognise it; bug-hunting checks whether you know where bugs live; writing checks production; and complexity analysis checks the skill interviews ask about most directly. All answers are in Chapter 38.
@objectives:
- Check your recall of every core fact in the book
- Simulate unfamiliar code by hand without running it
- Find bugs by reading, in code that compiles and runs
- Write correct code from a specification, including the edge cases
- Determine complexity from code you have not seen

## How to use this chapter

:::checklist Rules that make these worth doing
1. **No compiler** for sets A, B and C. The point is to simulate, not to observe.
2. **Write the trace down.** A trace held in your head is a guess.
3. **Predict before running** in sets D and E. Then run, and compare.
4. **Mark what you got wrong** and re-do only those, three days later.
5. The answers are in Chapter 38, with explanations. Read the explanation even
   when you were right — several of them say something the question did not.
:::

## Set A — Multiple choice

**A1.** An array of `double` starts at address 2000. At what address does
element 4 begin?
 **A** 2004  **B** 2016  **C** 2032  **D** it cannot be determined

**A2.** `std::vector<int> v;` then ten `push_back` calls. On libstdc++, what is
`v.capacity()`?
 **A** 10  **B** 12  **C** 16  **D** 20

**A3.** Which is **not** a reason array indexing is $O(1)$?
 **A** elements are the same size  **B** elements are contiguous
 **C** the array knows its own length  **D** the base address is known

**A4.** `v.insert(v.begin(), x)` inside a loop running $n$ times is:
 **A** $O(n)$  **B** $O(n \log n)$  **C** $O(n^2)$  **D** amortised $O(n)$

**A5.** Binary search on a `std::list` performs $O(\log n)$ comparisons. Its
total time is:
 **A** $O(\log n)$  **B** $O(n)$  **C** $O(n \log n)$  **D** $O(1)$

**A6.** In a singly linked list, deleting a node you hold a pointer to is:
 **A** $O(1)$  **B** $O(n)$  **C** $O(\log n)$  **D** impossible

**A7.** What does `delete p;` do to the variable `p`?
 **A** sets it to `nullptr`  **B** sets it to 0  **C** leaves it unchanged
 **D** undefined

**A8.** A sliding window with a `while` loop inside a `for` loop is:
 **A** always $O(n^2)$  **B** $O(n)$, because `left` advances at most $n$ times in
 total  **C** $O(n \log n)$  **D** it depends on the data

**A9.** Kadane's algorithm initialised with `best = 0` fails on:
 **A** an empty array  **B** an all-negative array  **C** a sorted array
 **D** an array with one element

**A10.** `std::unordered_map` lookup is:
 **A** $O(1)$ always  **B** $O(1)$ average, $O(n)$ worst  **C** $O(\log n)$
 **D** $O(n)$

**A11.** Reversing a linked list and forgetting `head = prev;` produces:
 **A** a crash  **B** an infinite loop  **C** a one-element list
 **D** the original list

**A12.** In Floyd's cycle detection, phase 2 moves:
 **A** both pointers one step  **B** slow one, fast two
 **C** both two steps  **D** only the slow pointer

**A13.** A dummy node is placed on the stack rather than the heap because:
 **A** it is faster  **B** it cannot then be deleted by mistake, and needs no
 cleanup  **C** heap nodes cannot be dummies  **D** it uses less memory

**A14.** Which traversal of a 2-D array is faster, and why?
 **A** column-major, fewer cache lines  **B** row-major, sequential memory
 **C** identical, same complexity  **D** depends on the compiler

**A15.** The three-reversal rotation works because:
 **A** reversal is its own inverse  **B** $(AB)^R = B^R A^R$
 **C** $k \bmod n = k$  **D** reversal is $O(n)$

## Set B — Trace the code

Write down every variable after every iteration. No compiler.

**B1.** What is printed?

```cpp title="B1" nonum frag
std::vector<int> v = {4, 2, 7, 1};
int best = v[0], second = -1000;
for (int i = 1; i < 4; ++i) {
    if (v[i] > best) { second = best; best = v[i]; }
    else if (v[i] > second) second = v[i];
}
std::cout << best << " " << second;
```

**B2.** What is the final content of `v`?

```cpp title="B2" nonum frag
std::vector<int> v = {0, 1, 0, 3, 0};
int w = 0;
for (int r = 0; r < 5; ++r)
    if (v[r] != 0) v[w++] = v[r];
while (w < 5) v[w++] = 0;
```

**B3.** How many iterations, and what is returned?

```cpp title="B3" nonum frag
std::vector<int> v = {1, 3, 5, 7, 9, 11};
int lo = 0, hi = 5, target = 9, steps = 0;
while (lo <= hi) {
    ++steps;
    int mid = lo + (hi - lo) / 2;
    if (v[mid] == target) break;
    if (v[mid] < target) lo = mid + 1; else hi = mid - 1;
}
std::cout << steps;
```

**B4.** What is `best` at the end?

```cpp title="B4" nonum frag
std::vector<int> v = {-2, 3, -1, 4, -5};
long long endingHere = v[0], best = v[0];
for (int i = 1; i < 5; ++i) {
    endingHere = std::max((long long)v[i], endingHere + v[i]);
    best = std::max(best, endingHere);
}
```

**B5.** Trace `prev`, `curr` and `nextNode` for the list `1 -> 2 -> 3`. What
does the list look like after each iteration?

```cpp title="B5" nonum frag
Node* prev = nullptr;
Node* curr = head;
while (curr) {
    Node* nextNode = curr->next;
    curr->next = prev;
    prev = curr;
    curr = nextNode;
}
```

**B6.** For `{2, 1, 5, 1, 3, 2}` with target 7, what is returned?

```cpp title="B6" nonum frag
long long sum = 0;
int left = 0, best = 0;
for (int right = 0; right < 6; ++right) {
    sum += v[right];
    while (sum > 7 && left <= right) { sum -= v[left]; ++left; }
    best = std::max(best, right - left + 1);
}
```

**B7.** What does this print for the list `1 -> 2 -> 3 -> 4 -> 5`?

```cpp title="B7" nonum frag
Node* slow = head;
Node* fast = head->next;
while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }
std::cout << slow->data;
```

## Set C — Find the bug

Every one of these compiles and runs. Each contains exactly one bug.

**C1.**
```cpp title="C1" nonum
int sumAll(const std::vector<int>& v) {
    int total = 0;
    for (int i = 0; i <= (int)v.size(); ++i) total += v[i];
    return total;
}
```

**C2.**
```cpp title="C2" nonum
int largest(const std::vector<int>& v) {
    int best = 0;
    for (int x : v) if (x > best) best = x;
    return best;
}
```

**C3.**
```cpp title="C3" nonum
void reverse(std::vector<int>& v) {
    for (int i = 0; i < (int)v.size(); ++i)
        std::swap(v[i], v[v.size() - 1 - i]);
}
```

**C4.**
```cpp title="C4" nonum
int binarySearch(const std::vector<int>& v, int target) {
    int lo = 0, hi = (int)v.size() - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (v[mid] == target) return mid;
        if (v[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}
```

**C5.**
```cpp title="C5" nonum
void deleteFront(Node*& head) {
    if (!head) return;
    delete head;
    head = head->next;
}
```

**C6.**
```cpp title="C6" nonum
void insertAfter(Node* node, int value) {
    Node* fresh = new Node(value);
    node->next = fresh;
    fresh->next = node->next;
}
```

**C7.**
```cpp title="C7" nonum
int maxConsecutiveOnes(const std::vector<int>& v) {
    int current = 0, best = 0;
    for (int x : v) {
        if (x == 1) ++current;
        else { best = std::max(best, current); current = 0; }
    }
    return best;
}
```

**C8.**
```cpp title="C8" nonum
void transpose(std::vector<std::vector<int>>& g) {
    int n = (int)g.size();
    for (int r = 0; r < n; ++r)
        for (int c = 0; c < n; ++c)
            std::swap(g[r][c], g[c][r]);
}
```

**C9.**
```cpp title="C9" nonum
std::pair<int,int> twoSum(const std::vector<int>& v, int target) {
    std::unordered_map<int,int> seen;
    for (int i = 0; i < (int)v.size(); ++i) {
        seen[v[i]] = i;
        auto it = seen.find(target - v[i]);
        if (it != seen.end()) return {it->second, i};
    }
    return {-1, -1};
}
```

**C10.**
```cpp title="C10" nonum
void rotateRight(std::vector<int>& v, int k) {
    int n = (int)v.size();
    std::reverse(v.begin(), v.end());
    std::reverse(v.begin(), v.begin() + k);
    std::reverse(v.begin() + k, v.end());
}
```

## Set D — Write the code

Specifications only. Write the function, handle the edge cases, state the
complexity.

**D1.** `int countPairs(const std::vector<int>& v, int target)` — the number of
index pairs $(i, j)$ with $i < j$ and `v[i] + v[j] == target`. $O(n)$ expected.

**D2.** `bool isRotatedSorted(const std::vector<int>& v)` — whether the array is
a sorted array rotated some number of positions. `{3,4,5,1,2}` is; `{3,1,4}` is
not. $O(n)$.

**D3.** `int longestEqualRun(const std::vector<int>& v)` — the length of the
longest run of equal neighbouring values. $O(n)$, $O(1)$ space.

**D4.** `std::vector<int> mergeIntervals(std::vector<std::pair<int,int>> in)` —
merge overlapping intervals. State what you sort by, and why.

**D5.** `Node* removeDuplicatesUnsorted(Node* head)` — remove duplicate values
from an **unsorted** list, keeping the first occurrence. State the two
approaches and their costs.

**D6.** `bool isCircular(Node* head)` — whether a list is circular (the last node
points at the head). Not merely whether it has a cycle. $O(n)$, $O(1)$ space.

**D7.** `Node* swapPairs(Node* head)` — swap every two adjacent nodes:
`1->2->3->4` becomes `2->1->4->3`. Swap the **nodes**, not the values.

**D8.** `int maxSubarraySumCircular(const std::vector<int>& v)` — maximum
sub-array sum where the sub-array may wrap around. State the edge case that
catches people.

## Set E — Complexity analysis

For each, state the time complexity, the auxiliary space complexity, and what
$n$ is.

**E1.**
```cpp title="E1" nonum frag
for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; j += 2)
        work();
```

**E2.**
```cpp title="E2" nonum frag
for (int i = 1; i < n; i *= 3)
    for (int j = 0; j < i; ++j)
        work();
```

**E3.**
```cpp title="E3" nonum
int f(std::vector<int> v) {          // note: by value
    std::sort(v.begin(), v.end());
    return v.empty() ? 0 : v[0];
}
```

**E4.**
```cpp title="E4" nonum
int g(const std::vector<int>& v) {
    int c = 0;
    for (int x : v)
        if (std::binary_search(v.begin(), v.end(), x * 2)) ++c;
    return c;
}
```

**E5.**
```cpp title="E5" nonum
void h(Node* head) {
    for (Node* a = head; a; a = a->next)
        for (Node* b = head; b; b = b->next)
            if (a->data == b->data) std::cout << a->data;
}
```

**E6.**
```cpp title="E6" nonum
int rec(int n) {
    if (n <= 1) return 1;
    return rec(n - 1) + rec(n - 1);
}
```

**E7.**
```cpp title="E7" nonum
std::vector<int> k(const std::vector<int>& v) {
    std::vector<int> out;
    for (int x : v) out.insert(out.begin(), x);
    return out;
}
```

**E8.**
```cpp title="E8" nonum frag
std::unordered_map<int,int> freq;
for (int x : v) ++freq[x];
for (const auto& [key, count] : freq)
    std::cout << key << count;
```

:::insight What each set is really testing
**A** — whether the facts are available instantly. In an interview you will not
have time to derive that `erase` at the front is $O(n)$.

**B** — whether you can *simulate* code. Most debugging is simulation, and most
people try to pattern-match instead.

**C** — whether you know where bugs live. Every bug in set C is one this book
warned about, which is the point: the warnings are a map.

**D** — whether you can produce, not just recognise. This is the only set that
measures what an interview measures.

**E** — the single skill asked about most directly, and the easiest to practise.
:::

Answers, with explanations, are in Chapter 38.
