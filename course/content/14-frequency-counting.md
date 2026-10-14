# Pattern 7: Frequency Counting
@short: Frequency Counting
@subtitle: Trading memory for time by remembering what you have seen
@tier: core
@prereq: Chapters 3 and 8
@blurb: Most $O(n^2)$ array solutions are quadratic for one reason: for each element they search the rest of the array for a partner. A frequency table removes that inner search entirely by remembering what has already gone past. This chapter covers the array counter and the hash map, when each is right, and the complement trick that makes Two Sum linear on unsorted data.
@objectives:
- Choose between a fixed-size count array and a hash map, with a reason
- Build a frequency table in one pass and use it to answer counting questions
- Solve unsorted Two Sum in $O(n)$ with the complement trick
- Find the majority element, the single number, and anagram pairs
- State the real cost of `std::unordered_map`, including when it is not $O(1)$
- Recognise when a `std::set` or `std::unordered_set` is enough

## The waste the pattern removes

Here is a quadratic solution, and the reason it is quadratic.

```cpp title="Does this array contain a duplicate? The slow way" frag
for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j)
        if (v[i] == v[j])
            std::cout << "duplicate";
```

The inner loop asks *"have I seen `v[i]` anywhere else?"* and answers it by
looking. But the information was available all along — we **had** already seen
those elements, we simply did not write anything down.

:::insight The trade, stated plainly
Spend $O(n)$ memory to remember what you have seen. In exchange, every
*"have I seen this?"* question becomes $O(1)$ instead of $O(n)$.

$O(n^2)$ time and $O(1)$ space becomes $O(n)$ time and $O(n)$ space. This is
the single most common optimisation in interview problems, and the single most
common follow-up is *"now do it without the extra space"* — which usually means
sorting (Chapter 15) or index marking (Chapter 13).
:::

@fig: fc_lookup | 150 | Replacing a search with a lookup. The nested loop re-scans the past for every element; the frequency table records it once and answers in constant time.

## Two tools

@fig: fc_two_tools | 158 | The two implementations. A count array is a direct index — fastest possible, but it needs one slot per possible value. A hash map handles any key at the cost of hashing and indirection.

:::definition Count array versus hash map
A **count array** is `std::vector<int> count(K, 0)`, where the value itself is
the index. Use it when the values are small non-negative integers, or
characters, and $K$ is manageable. Access is one address calculation: genuinely
$O(1)$, with a tiny constant.

A **hash map** is `std::unordered_map<Key, int>`. Use it when the keys are
large, negative, sparse, or not integers at all. Access is $O(1)$ *on average*,
with a much larger constant — a hash computation plus a pointer chase.

**Rule of thumb:** if you can index by the value directly, do. A count array is
typically 5–20 times faster than a hash map for the same job.
:::

| Situation | Reach for |
|---|---|
| lowercase letters | `std::vector<int> count(26, 0)` |
| any `char` | `std::vector<int> count(256, 0)` |
| digits, or values $0..1000$ | a count array of that size |
| values up to $10^9$, or negative | `std::unordered_map<int, int>` |
| strings, pairs, or custom types | `std::unordered_map<Key, int>` |
| you only need presence, not counts | `std::unordered_set` or a `vector<bool>` |

## Building and using a frequency table

```cpp title="One pass to build, then answer anything"
#include <iostream>
#include <unordered_map>
#include <vector>

int main() {
    std::vector<int> v = {4, 7, 4, 2, 7, 4};

    std::unordered_map<int, int> freq;
    for (int x : v) ++freq[x];          // operator[] creates a 0 if absent

    std::cout << "4 appears " << freq[4] << " times\n";
    std::cout << "9 appears " << freq[9] << " times\n";

    // Most frequent value, breaking ties by smaller value for determinism.
    int bestVal = 0, bestCount = 0;
    for (const auto& [value, count] : freq)
        if (count > bestCount || (count == bestCount && value < bestVal)) {
            bestVal = value;
            bestCount = count;
        }
    std::cout << "most frequent: " << bestVal << " (" << bestCount << ")\n";
    return 0;
}
```

```text nonum
4 appears 3 times
9 appears 0 times
most frequent: 4 (3)
```

:::pitfall `operator[]` inserts, even when you are only looking
`freq[9]` on a key that is absent **creates** the entry with value 0 and returns
a reference to it. So the map above now contains a 9, and `freq.size()` has
grown by one.

Usually harmless. Occasionally a real bug: inside a loop over a map while
checking keys, insertion can invalidate iterators, and in a `const` context it
will not compile at all.

To look without inserting:
```cpp nonum frag
auto it = freq.find(9);
int c = (it == freq.end()) ? 0 : it->second;
// or, more briefly:
int c2 = freq.count(9) ? freq.at(9) : 0;
```
Note the tie-break in the program above. Iteration order over an
`unordered_map` is unspecified, so without a deterministic rule the "most
frequent" answer could differ between runs or compilers. Interviewers notice
when you handle that.
:::

## The complement trick: Two Sum, unsorted

Chapter 9 solved Two Sum on **sorted** input with two pointers. Here the array
is unsorted and we must return the original indices, so sorting would destroy
the answer.

:::insight Ask for the partner, not for the pair
For each element $x$, the partner you need is exactly $target - x$ — its
**complement**. There is no searching to do: you know precisely what you want.

So the question becomes *"have I already seen $target - x$?"*, which a hash map
answers in $O(1)$.

Crucially, you check the map **before** inserting the current element. That way
an element can never pair with itself, and the stored index is always strictly
earlier.
:::

@fig: fc_two_sum | 164 | Two Sum by complement. At each element, compute what is missing and ask the map whether it has already gone past. One pass, no sorting, original indices preserved.

### The trace

`{2, 7, 11, 15}`, target 9.

@tbl: Each row does one lookup and one insert. The pair is found the moment the second member arrives.
| `i` | `v[i]` | complement | in map? | map afterwards |
|---|---|---|---|---|
| 0 | 2 | 7 | no | `{2→0}` |
| 1 | 7 | 2 | **yes, at 0** | return (0, 1) |

```cpp title="Two Sum on unsorted data, O(n)"
#include <iostream>
#include <unordered_map>
#include <vector>

std::pair<int, int> twoSum(const std::vector<int>& v, int target) {
    std::unordered_map<int, int> seen;       // value -> index
    for (int i = 0; i < (int)v.size(); ++i) {
        int complement = target - v[i];
        auto it = seen.find(complement);
        if (it != seen.end()) return {it->second, i};   // look up FIRST
        seen[v[i]] = i;                                 // then insert
    }
    return {-1, -1};
}

int main() {
    auto [a, b] = twoSum({2, 7, 11, 15}, 9);
    std::cout << a << " " << b << "\n";

    auto [c, d] = twoSum({3, 2, 4}, 6);
    std::cout << c << " " << d << "\n";

    auto [e, f] = twoSum({3, 3}, 6);        // duplicates are fine
    std::cout << e << " " << f << "\n";

    auto [g, h] = twoSum({1, 2}, 100);
    std::cout << g << " " << h << "\n";
    return 0;
}
```

```text nonum
0 1
1 2
0 1
-1 -1
```

:::pitfall Inserting before looking up
With `{3, 2, 4}` and target 6, inserting first means that at $i = 0$ the map
already contains `3 → 0`; the complement of 3 is 3, the lookup succeeds, and you
return `(0, 0)` — one element used twice.

**Look up, then insert.** The same rule appeared in Chapter 11 for sub-array
sums, and it will appear again. It is worth recognising as a rule rather than
rediscovering it each time.
:::

@tbl: Two Sum, three ways. The right answer depends on whether indices are required and whether extra space is allowed — which is why a good candidate asks before coding.
| Approach | Time | Space | Needs sorted? | Returns original indices? |
|---|---|---|---|---|
| Brute force | $O(n^2)$ | $O(1)$ | no | yes |
| Sort, then two pointers | $O(n \log n)$ | $O(1)$ or $O(n)$ | sorts it | only with extra bookkeeping |
| Hash map | $O(n)$ | $O(n)$ | no | yes |

## Counting with a plain array: anagrams

```cpp title="Are two strings anagrams of each other?"
#include <iostream>
#include <string>
#include <vector>

bool areAnagrams(const std::string& a, const std::string& b) {
    if (a.size() != b.size()) return false;    // cheap rejection first
    std::vector<int> count(26, 0);
    for (char c : a) ++count[c - 'a'];         // add for a...
    for (char c : b) --count[c - 'a'];         // ...subtract for b
    for (int x : count)
        if (x != 0) return false;              // anything left over means no
    return true;
}

int main() {
    std::cout << areAnagrams("listen", "silent") << "\n";
    std::cout << areAnagrams("hello",  "world")  << "\n";
    std::cout << areAnagrams("a",      "ab")     << "\n";
    std::cout << areAnagrams("",       "")       << "\n";
    return 0;
}
```

```text nonum
1
0
0
1
```

Three things worth copying from this function:

**`c - 'a'` maps a letter to 0..25.** Characters are small integers; `'c' - 'a'`
is 2. This is the cheapest possible frequency table.

**One array, not two.** Adding for the first string and subtracting for the
second means the array ends as all zeroes exactly when the strings match. Two
arrays and a comparison would also work and would need twice the memory and a
second loop.

**The length check comes first.** It costs $O(1)$ and eliminates most negative
cases immediately. Cheap rejections before expensive work is a habit worth
having.

$O(n)$ time, and $O(1)$ space — the count array is 26 entries whatever the
input length, which is a constant.

## Sets: when you only need "have I seen it?"

```cpp title="Has this array a duplicate? Does it contain a target?"
#include <iostream>
#include <unordered_set>
#include <vector>

bool hasDuplicate(const std::vector<int>& v) {
    std::unordered_set<int> seen;
    for (int x : v)
        if (!seen.insert(x).second)      // insert returns {iterator, inserted?}
            return true;                 // already present
    return false;
}

int main() {
    std::cout << hasDuplicate({1, 2, 3, 1}) << "\n";
    std::cout << hasDuplicate({1, 2, 3})    << "\n";
    std::cout << hasDuplicate({})           << "\n";
    return 0;
}
```

```text nonum
1
0
0
```

`insert` returns a pair whose `.second` is `true` if the element was new. That
gives you *check and insert* in one operation, instead of a `count` followed by
an `insert` — half the hashing work.

## What a hash map really costs

:::warning `unordered_map` is $O(1)$ **on average**, not always
The worst case for a single lookup is $O(n)$, when every key lands in the same
bucket. With adversarially chosen keys this is achievable, and competitive
programmers do exploit it.

Beyond complexity, the **constant factor** is large. Every access computes a
hash, indexes a bucket array, and follows a pointer chain — typically a cache
miss. A `std::vector<int>` lookup is a single address calculation.

Practical guidance:
- Prefer a **count array** whenever the value range allows it.
- `reserve()` the map if you know roughly how many keys there will be; it avoids
  rehashing, which is the same amortised story as Chapter 5.
- Do not use a map when a sorted array plus binary search would do and the data
  is static.
:::

@tbl: Choosing a container. The first column is almost always the right answer when it is available at all.
| | count array | `unordered_map` | `map` |
|---|---|---|---|
| Lookup | $O(1)$, tiny constant | $O(1)$ average, $O(n)$ worst | $O(\log n)$ |
| Memory | one slot per possible value | per stored key | per stored key |
| Keys allowed | small non-negative integers | anything hashable | anything orderable |
| Iterates in sorted order | yes, by index | no | yes |
| Good when | the range is small | the range is large or sparse | you need order |

## Cost summary

| Problem | Without counting | With counting |
|---|---|---|
| Contains duplicate | $O(n^2)$ | $O(n)$ time, $O(n)$ space |
| Two Sum (unsorted) | $O(n^2)$ | $O(n)$ time, $O(n)$ space |
| Most frequent element | $O(n^2)$ | $O(n)$ time, $O(n)$ space |
| Anagram check | $O(n \log n)$ by sorting | $O(n)$ time, $O(1)$ space |
| First non-repeating character | $O(n^2)$ | $O(n)$ time, $O(1)$ space |
| Intersection of two arrays | $O(n \cdot m)$ | $O(n + m)$ time, $O(n)$ space |

:::recap Chapter 14 in six lines
- A frequency table replaces *searching the past* with *looking it up*, turning
  $O(n^2)$ into $O(n)$.
- Use a **count array** when the value is usable as an index; it is far faster
  than a hash map.
- **Look up before you insert** — otherwise an element pairs with itself.
- `operator[]` on a map inserts a zero entry for a missing key. Use `find` to
  look without inserting.
- `unordered_map` is $O(1)$ **average** with a large constant, not a free
  lookup.
- The usual follow-up is "now in $O(1)$ space", which means sorting or index
  marking instead.
:::

:::exercise Practise
1. Find the first character in a string that appears exactly once. What size is
   your count array, and how many passes do you need?
2. Given two arrays, return their intersection without duplicates. What is the
   complexity, and which array should go into the set if their sizes differ a
   lot?
3. Single number: every value appears twice except one. Solve it with a hash
   map, then solve it again in $O(1)$ space using XOR. Why does XOR work?
4. Group a list of words into anagram groups. What makes a good map **key** for
   this, and what are the two standard choices?
5. Majority element — a value appearing more than $n/2$ times. Solve with a
   frequency map, then look up the Boyer–Moore voting algorithm and explain how
   it reaches $O(1)$ space.
6. Why must `twoSum` look up before inserting? Give a concrete input where the
   other order returns a wrong answer.
7. You must count the frequency of values in the range $0$ to $10^9$, but there
   are only $10^5$ elements. Which container, and why not the other one?
8. Longest consecutive sequence: given an unsorted array, find the length of the
   longest run of consecutive integers, in $O(n)$. (Hint: a set, and start
   counting only from values that have no predecessor in the set — why does
   that make it linear rather than quadratic?)
:::
