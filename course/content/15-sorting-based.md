# Pattern 8: Sorting-Based Approaches
@short: Sorting First
@subtitle: When $O(n \log n)$ of preparation makes the rest trivial
@tier: core
@prereq: Chapters 9 and 12
@blurb: Sorting is not a pattern in itself — it is an *enabler*. Once an array is sorted, duplicates are adjacent, binary search becomes available, two pointers work, and "closest pair" questions collapse to neighbouring comparisons. This chapter is about recognising when paying $O(n \log n)$ up front is the right move, and when it is a mistake that destroys information you needed.
@objectives:
- Use `std::sort` correctly, including with custom comparators
- Explain what sorting *gives* you: adjacency, monotonicity, searchability
- Decide between sorting, hashing, and a direct scan, with reasons
- Sort pairs and structures without losing the association between fields
- Recognise when sorting destroys the answer (original indices, stability)
- Know the cost and the guarantees of `std::sort`, `std::stable_sort` and `std::nth_element`

## What sorting buys you

:::definition The three gifts of a sorted array
**Adjacency.** Equal values become neighbours, so duplicate detection is a
single pass comparing `v[i]` with `v[i-1]` — no memory needed.

**Monotonicity.** The array only goes up, so two pointers from the ends behave
predictably (Chapter 9) and binary search becomes available (Chapter 12).

**Locality of closeness.** The numerically nearest value to `v[i]` is `v[i-1]`
or `v[i+1]`. Nothing far away can be closer. This turns many "closest pair"
questions from $O(n^2)$ into $O(n \log n)$.
:::

@fig: sort_gifts | 170 | What sorting gives you. In the unsorted array the duplicates, the closest pair and the median are all invisible without searching. In the sorted array each is a local observation.

The cost is $O(n \log n)$ and, usually, the loss of the original order. Both of
those matter, and the rest of the chapter is about weighing them.

## Using std::sort

```cpp title="Sorting: ascending, descending, and by a custom rule"
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<int> v = {5, 2, 9, 1, 7};

    std::sort(v.begin(), v.end());                       // ascending
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    std::sort(v.begin(), v.end(), std::greater<int>());  // descending
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    // Custom rule: by distance from 6, nearest first.
    // 5 and 7 are both 1 away, so the comparator needs a tie-break -
    // without one, std::sort may order them either way. See the pitfall below.
    std::sort(v.begin(), v.end(), [](int a, int b) {
        int da = std::abs(a - 6), db = std::abs(b - 6);
        if (da != db) return da < db;
        return a < b;
    });
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    // Sorting strings by length, then alphabetically.
    std::vector<std::string> words = {"pear", "fig", "apple", "kiwi"};
    std::sort(words.begin(), words.end(),
              [](const std::string& a, const std::string& b) {
                  if (a.size() != b.size()) return a.size() < b.size();
                  return a < b;
              });
    for (const auto& w : words) std::cout << w << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
1 2 5 7 9 
9 7 5 2 1 
5 7 9 2 1 
fig kiwi pear apple 
```

:::pitfall The comparator must be a *strict* ordering
`std::sort` requires its comparator to return `false` when the two arguments are
equivalent. Writing `<=` instead of `<` breaks that rule, and the result is not
a wrong order — it is undefined behaviour, which in practice means `std::sort`
reads outside the array and crashes, sometimes only on large inputs.

```cpp nonum frag
std::sort(v.begin(), v.end(), [](int a, int b) { return a <= b; });  // ✗
std::sort(v.begin(), v.end(), [](int a, int b) { return a <  b; });  // ✓
```
The same applies inside multi-key comparators: compare the first key, and only
if it ties, move to the next — exactly as the `words` comparator above does.
Never write `return a.size() <= b.size()`.
:::

## Sorting structures without losing the association

A common beginner error is sorting one array and forgetting that a second array
was lined up with it.

```cpp title="Keep related fields together — sort the pairs, not the parts"
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Student {
    std::string name;
    int score;
};

int main() {
    std::vector<Student> students = {{"Ana", 72}, {"Ben", 91}, {"Cy", 72}};

    // Highest score first; ties broken alphabetically for determinism.
    std::sort(students.begin(), students.end(),
              [](const Student& a, const Student& b) {
                  if (a.score != b.score) return a.score > b.score;
                  return a.name < b.name;
              });
    for (const auto& s : students)
        std::cout << s.name << ":" << s.score << " ";
    std::cout << "\n";

    // When you must keep original positions, sort (value, index) pairs.
    std::vector<int> v = {40, 10, 30};
    std::vector<std::pair<int, int>> indexed;
    for (int i = 0; i < (int)v.size(); ++i) indexed.push_back({v[i], i});
    std::sort(indexed.begin(), indexed.end());
    for (const auto& [value, idx] : indexed)
        std::cout << value << "(was at " << idx << ") ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
Ben:91 Ana:72 Cy:72 
10(was at 1) 30(was at 2) 40(was at 0) 
```

The second technique is the standard answer to *"sorting would lose the original
indices, which the problem wants"*. Pair each value with its index before
sorting, and the association survives.

## When sorting is the right move

### Closest pair of values

```cpp title="Smallest absolute difference between any two elements"
#include <algorithm>
#include <climits>
#include <iostream>
#include <vector>

int smallestDifference(std::vector<int> v) {     // by value: we will sort it
    if (v.size() < 2) return -1;
    std::sort(v.begin(), v.end());
    int best = INT_MAX;
    for (int i = 1; i < (int)v.size(); ++i)
        best = std::min(best, v[i] - v[i - 1]);  // only NEIGHBOURS can be closest
    return best;
}

int main() {
    std::cout << smallestDifference({40, 11, 7, 39, 100}) << "\n";
    std::cout << smallestDifference({5, 5})               << "\n";
    std::cout << smallestDifference({3})                  << "\n";
    return 0;
}
```

```text nonum
1
0
-1
```

Brute force is $O(n^2)$. Sorting makes it $O(n \log n)$, and the loop that
follows is $O(n)$ — dominated by the sort.

:::insight Why only neighbours matter
After sorting, suppose $i < j$ and they are not adjacent. Then there is some $k$
with $i < k < j$, and because the array is sorted,
$v[j] - v[i] \ge v[j] - v[k]$ and $v[j] - v[i] \ge v[k] - v[i]$.

So any non-adjacent pair is at least as far apart as some adjacent pair inside
it. **The minimum must be between neighbours**, and checking $n-1$ pairs
suffices instead of $n^2/2$.

Being able to give that argument is the difference between "I sorted it because
that usually helps" and understanding why the algorithm is correct.
:::

### Merging and intersecting sorted arrays

```cpp title="Union and intersection of two sorted arrays, in O(n + m)"
#include <iostream>
#include <vector>

std::vector<int> unionSorted(const std::vector<int>& a,
                             const std::vector<int>& b) {
    std::vector<int> out;
    int i = 0, j = 0;
    while (i < (int)a.size() && j < (int)b.size()) {
        if (a[i] < b[j])      { if (out.empty() || out.back() != a[i]) out.push_back(a[i]); ++i; }
        else if (b[j] < a[i]) { if (out.empty() || out.back() != b[j]) out.push_back(b[j]); ++j; }
        else                  { if (out.empty() || out.back() != a[i]) out.push_back(a[i]); ++i; ++j; }
    }
    while (i < (int)a.size()) { if (out.empty() || out.back() != a[i]) out.push_back(a[i]); ++i; }
    while (j < (int)b.size()) { if (out.empty() || out.back() != b[j]) out.push_back(b[j]); ++j; }
    return out;
}

std::vector<int> intersectSorted(const std::vector<int>& a,
                                 const std::vector<int>& b) {
    std::vector<int> out;
    int i = 0, j = 0;
    while (i < (int)a.size() && j < (int)b.size()) {
        if (a[i] < b[j])      ++i;
        else if (b[j] < a[i]) ++j;
        else {
            if (out.empty() || out.back() != a[i]) out.push_back(a[i]);
            ++i; ++j;
        }
    }
    return out;
}

int main() {
    std::vector<int> a = {1, 2, 2, 4, 6};
    std::vector<int> b = {2, 3, 4, 4, 9};
    for (int x : unionSorted(a, b))     std::cout << x << " ";
    std::cout << "\n";
    for (int x : intersectSorted(a, b)) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
1 2 3 4 6 9 
2 4 
```

@fig: sort_merge | 160 | Merging two sorted arrays. Two pointers advance independently, always taking the smaller front element. Each element is examined once, so the whole merge is $O(n + m)$ — and this is the core of merge sort.

The `out.back() != x` guard is how duplicates are suppressed, and it works
precisely because the output is being built in sorted order — the first gift of
sorting, used on the result rather than the input.

## When sorting is the wrong move

:::warning Three times you should not sort
**You need the original indices.** Two Sum must return positions in the input.
Sorting destroys them unless you pair values with indices first, which costs
$O(n)$ space — at which point a hash map is simpler and faster.

**Order within equal elements matters.** `std::sort` is **not stable**: equal
elements may be reordered. If you have already sorted by score and now sort by
name, the score order within each name is not preserved. Use `std::stable_sort`
($O(n \log n)$ guaranteed, but it allocates $O(n)$ memory).

**You only need one element.** To find the median, or the $k$-th largest, a full
sort is wasteful. `std::nth_element` puts the $k$-th element in its final
position in **average $O(n)$** time, leaving everything else merely partitioned.
:::

```cpp title="nth_element: the k-th smallest without a full sort"
#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {7, 2, 9, 4, 1, 8, 3};
    int k = 2;                                   // 0-based: the 3rd smallest
    std::nth_element(v.begin(), v.begin() + k, v.end());
    std::cout << "3rd smallest = " << v[k] << "\n";

    // Everything before position k is <= v[k]; everything after is >= v[k].
    // The two halves are NOT individually sorted, and that is the saving.
    std::vector<int> w = {7, 2, 9, 4, 1, 8, 3};
    std::sort(w.begin(), w.end());
    std::cout << "check         = " << w[k] << "\n";
    return 0;
}
```

```text nonum
3rd smallest = 3
check         = 3
```

## Choosing between the three approaches

@tbl: The standard decision. Most array problems can be attacked all three ways, and interviewers are usually asking you to compare them rather than to pick one.
| | Sorting | Hashing | Direct scan |
|---|---|---|---|
| Time | $O(n \log n)$ | $O(n)$ average | $O(n)$ or $O(n^2)$ |
| Extra space | $O(1)$ to $O(n)$ | $O(n)$ | $O(1)$ |
| Keeps original order | no | yes | yes |
| Gives you order statistics | yes | no | no |
| Enables binary search after | yes | no | no |
| Worst-case guarantee | yes | no | yes |

:::interview Say all three
A strong answer to an array problem sounds like this:

> *"The brute force is $O(n^2)$. I could sort and use two pointers for
> $O(n \log n)$ with no extra space, or use a hash map for $O(n)$ time and
> $O(n)$ space. Since the problem asks for the original indices, the hash map
> is the better fit — but if memory were constrained I would sort pairs of
> (value, index) instead."*

That paragraph demonstrates all three patterns, the trade-off between them, and
attention to the specific requirement. It is a better answer than any single
piece of code.
:::

## What std::sort actually is

| Function | Complexity | Stable? | Extra memory |
|---|---|---|---|
| `std::sort` | $O(n \log n)$ worst case | no | $O(\log n)$ stack |
| `std::stable_sort` | $O(n \log n)$ | yes | $O(n)$ |
| `std::partial_sort` | $O(n \log k)$ | no | $O(1)$ |
| `std::nth_element` | $O(n)$ average | no | $O(1)$ |
| `std::is_sorted` | $O(n)$ | — | $O(1)$ |

`std::sort` is **introsort**: quicksort, which switches to heapsort if the
recursion gets too deep (so the worst case stays $O(n \log n)$ rather than
quicksort's $O(n^2)$), and to insertion sort for small ranges (because for
$n < 16$ the simpler algorithm's smaller constant wins). That design is itself a
lesson: Big O chooses the algorithm, and constants choose the special cases.

:::recap Chapter 15 in six lines
- Sorting gives **adjacency**, **monotonicity** and **local closeness** — then
  other patterns become available.
- It costs $O(n \log n)$ and usually the original order. Weigh both.
- After sorting, the closest pair is always adjacent, so one pass finishes the
  job.
- Comparators must be strict (`<`, never `<=`), or `std::sort` is undefined
  behaviour.
- To keep positions, sort `(value, index)` pairs; to keep ties in order, use
  `stable_sort`.
- For one order statistic, `nth_element` is $O(n)$ average — do not sort the
  whole array.
:::

:::exercise Practise
1. Given an array, find whether any value appears more than twice, using sorting
   and $O(1)$ extra space.
2. Merge two sorted arrays into one sorted array **keeping** duplicates. How
   does the code differ from `unionSorted`?
3. Three Sum: find all distinct triples summing to zero. Sort first; then for
   each $i$, run two pointers on the rest. Why is the total $O(n^2)$ and not
   $O(n^3)$? How do you skip duplicate triples?
4. Meeting rooms: given intervals $[s_i, e_i)$, find the minimum number of rooms
   needed. (Hint: sort the starts and the ends into two separate arrays and
   sweep. Why is it valid to separate them?)
5. Why is `[](int a, int b){ return a <= b; }` dangerous? What does the standard
   require of a comparator, and what actually happens when you break it?
6. You must find the median of $10^7$ numbers once. Compare `std::sort` with
   `std::nth_element` in both complexity and real work done.
7. Sort an array of strings so that concatenating them gives the largest
   possible number: `{3, 30, 34, 5, 9}` → `9534330`. What is the comparator?
   (This one is famous for having a comparator that looks wrong and is right.)
8. Give a problem where sorting makes the answer **impossible** to recover, and
   say what you would do instead.
:::
