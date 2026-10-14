# Pattern 6: In-Place Modification
@short: In-Place Modification
@subtitle: Rearranging an array using only the array
@tier: core
@prereq: Chapters 6 and 9
@blurb: "Solve it in $O(1)$ extra space" is one of the most common follow-up questions an interviewer asks, and it is never about saving memory — it is about whether you can see that the array already contains everywhere you need to put things. This chapter collects the four techniques: the write pointer, the swap, the reversal trick, and the genuinely clever one of storing extra information inside the values themselves.
@objectives:
- Say precisely what "in place" and "$O(1)$ auxiliary space" mean
- Use a write pointer to filter, compact or partition in one pass
- Rotate an array by $k$ positions using three reversals, and explain why it works
- Use the array's own indices as a lookup table
- Encode a second piece of information inside an element without losing the first
- Recognise when in-place is impossible and say so

## What "in place" means

:::definition In place
An algorithm is **in place** if it uses $O(1)$ auxiliary space — a fixed number
of extra variables, no matter how large the input.

A handful of `int`s is in place. A second array of size $n$ is not. A
`std::vector` you `push_back` into $n$ times is not.

The *input itself* does not count against you: you are allowed to modify it, and
you are allowed to use it as workspace. That permission is the whole trick.
:::

@fig: ip_what_counts | 140 | What counts as auxiliary space. The input is free; a constant number of variables is free; anything that grows with $n$ is not. Recursion depth counts, which catches people out.

Three techniques, in increasing order of cleverness.

## Technique 1: The write pointer

You have met this in Chapters 6 and 9. It is the workhorse, and it solves any
problem of the form *"keep some elements, discard the rest, preserve order"*.

```cpp title="The general shape — keep what the predicate accepts" frag
int write = 0;
for (int read = 0; read < n; ++read)
    if (keep(v[read]))
        v[write++] = v[read];
// v[0 .. write-1] is the answer; write is its length
```

Specialise `keep` and you get a family of problems:

| Problem | `keep(x)` is |
|---|---|
| Remove all occurrences of `val` | `x != val` |
| Remove duplicates from a sorted array | `x != v[write - 1]` |
| Move zeroes to the end | `x != 0`, then pad with zeroes |
| Keep only even numbers | `x % 2 == 0` |
| Compact out every `nullptr` | `x != nullptr` |

All of them are $O(n)$ time, $O(1)$ space, one pass. If you recognise the shape,
you have solved them all at once.

## Technique 2: The reversal trick for rotation

:::definition The problem
Rotate an array right by $k$ positions. `{1,2,3,4,5,6,7}` with $k = 3$ becomes
`{5,6,7,1,2,3,4}` — the last three elements move to the front.
:::

### The approaches that do not satisfy the constraint

**Use a second array.** Copy each element to its new index
$(i + k) \bmod n$. $O(n)$ time, but $O(n)$ space — rejected.

**Rotate by one, $k$ times.** $O(1)$ space, but $O(n \cdot k)$ time, which for
$k \approx n$ is $O(n^2)$ — rejected.

We want both $O(n)$ time and $O(1)$ space, and the solution is one of the
prettiest ideas in elementary algorithms.

### The insight

@fig: ip_rotate | 180 | Rotation by three reversals. Reversing the whole array puts the right block at the front, but both blocks are now backwards. Reversing each block separately repairs them. Three passes, no extra memory.

:::insight Why reversing three times rotates
Write the array as two blocks: $A$ (the first $n-k$ elements) and $B$ (the last
$k$). You currently have $AB$ and you want $BA$.

Reversing the whole array gives $(AB)^R$, and reversing a concatenation
reverses the order of the parts as well as each part: $(AB)^R = B^R A^R$.

So after one reversal you have $B^R A^R$ — the blocks are in the right order,
each one backwards. Reverse the first $k$ elements to turn $B^R$ into $B$, and
reverse the remaining $n-k$ to turn $A^R$ into $A$. Result: $BA$.

Three reversals, $n/2 + k/2 + (n-k)/2 = n$ swaps in total. $O(n)$ time, $O(1)$
space.
:::

### The trace

`{1,2,3,4,5,6,7}`, $k = 3$.

@tbl: The three reversals. After step 1 the blocks are in the right places and the wrong order internally; steps 2 and 3 fix each block.
| Step | Action | Array |
|---|---|---|
| start | — | `1 2 3 4 5 6 7` |
| 1 | reverse all | `7 6 5 4 3 2 1` |
| 2 | reverse first $k = 3$ | `5 6 7 4 3 2 1` |
| 3 | reverse last $n - k = 4$ | `5 6 7 1 2 3 4` |

```cpp title="Rotate right by k, in O(n) time and O(1) space"
#include <iostream>
#include <vector>

void reverseRange(std::vector<int>& v, int lo, int hi) {
    while (lo < hi) std::swap(v[lo++], v[hi--]);
}

void rotateRight(std::vector<int>& v, int k) {
    int n = (int)v.size();
    if (n == 0) return;
    k %= n;                              // k = 10 on 7 elements is k = 3
    if (k < 0) k += n;                   // tolerate a negative k
    reverseRange(v, 0, n - 1);           // 1. reverse everything
    reverseRange(v, 0, k - 1);           // 2. reverse the first k
    reverseRange(v, k, n - 1);           // 3. reverse the rest
}

int main() {
    std::vector<int> v = {1, 2, 3, 4, 5, 6, 7};
    rotateRight(v, 3);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> w = {1, 2, 3};
    rotateRight(w, 10);                  // 10 % 3 == 1
    for (int x : w) std::cout << x << " ";
    std::cout << "\n";

    std::vector<int> z = {1, 2, 3};
    rotateRight(z, 3);                   // a full turn changes nothing
    for (int x : z) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
5 6 7 1 2 3 4 
3 1 2 
1 2 3 
```

:::pitfall Forgetting `k %= n`
If $k \ge n$, `reverseRange(v, 0, k - 1)` reads past the end of the array —
undefined behaviour, and on a big enough $k$, a crash.

A rotation by $n$ is the identity, so only $k \bmod n$ matters. This one line
turns a function that works on the examples into a function that works.

Rotating **left** by $k$ is the same as rotating right by $n - k$. Ask which
direction is wanted; the problem statements are often ambiguous and
interviewers notice when you check.
:::

## Technique 3: Using indices as storage

Now the genuinely clever family. These problems share a precondition that looks
like a detail and is actually the whole solution:

> *the array contains $n$ values, each in the range $1$ to $n$.*

When you see that, the array has exactly as many **slots** as it has possible
**values** — so index $i$ can carry information about the value $i+1$. The array
becomes its own hash table, for free.

@fig: ip_index_marking | 164 | Using the sign bit as a visited mark. Seeing value $v$ means flipping the sign at index $|v| - 1$. A slot that is already negative says "this value has been seen before", and the original values are recoverable by taking absolute values.

### Find all duplicates in an array of 1..n

```cpp title="All duplicates, O(n) time, O(1) space"
#include <cmath>
#include <iostream>
#include <vector>

// v has n elements, each in [1, n]. Each value appears once or twice.
// Returns the values appearing twice. v is modified and then restored.
std::vector<int> findDuplicates(std::vector<int>& v) {
    std::vector<int> result;
    for (int i = 0; i < (int)v.size(); ++i) {
        int idx = std::abs(v[i]) - 1;       // the slot this value owns
        if (v[idx] < 0)
            result.push_back(std::abs(v[i]));   // already marked -> a duplicate
        else
            v[idx] = -v[idx];                   // mark it as seen
    }
    for (int& x : v) x = std::abs(x);           // tidy up after ourselves
    return result;
}

int main() {
    std::vector<int> v = {4, 3, 2, 7, 8, 2, 3, 1};
    for (int x : findDuplicates(v)) std::cout << x << " ";
    std::cout << "\n";
    for (int x : v) std::cout << x << " ";      // restored
    std::cout << "\n";

    std::vector<int> none = {1, 2, 3};
    std::cout << "duplicates: " << findDuplicates(none).size() << "\n";
    return 0;
}
```

```text nonum
2 3 
4 3 2 7 8 2 3 1 
duplicates: 0
```

The sign of `v[idx]` carries a boolean — *have I seen the value `idx + 1`?* —
without costing a single extra byte. The magnitude still carries the original
value, so nothing is lost.

:::insight Is the output vector not extra space?
A fair question, and the standard answer is: **space used purely to hold the
output does not count** against an in-place claim. The working space is $O(1)$;
the result has to go somewhere.

Say this explicitly in an interview. Candidates who notice the subtlety and
name the convention look considerably better than candidates who do not notice
it at all.
:::

### Encoding two values in one slot

A variation worth knowing, because it looks impossible until you see it.

:::definition The trick
To store a second value $b$ (where $0 \le b < n$) alongside an existing value
$a$ (also $< n$) in one slot, write $a + b \times n$.

Recover them with division and remainder: $a = x \bmod n$, $b = \lfloor x / n
\rfloor$.

It works because $a < n$ means $a$ never spills into the multiples-of-$n$ part.
Watch for overflow: use `long long` when $n^2$ might exceed `int`.
:::

```cpp title="Two values in one slot: in-place permutation"
#include <iostream>
#include <vector>

// v is a permutation of 0..n-1. Replace each v[i] with v[v[i]], in place.
void permuteInPlace(std::vector<int>& v) {
    int n = (int)v.size();
    for (int i = 0; i < n; ++i)
        v[i] += n * (v[v[i]] % n);      // old value in the remainder, new in the quotient
    for (int i = 0; i < n; ++i)
        v[i] /= n;                      // keep only the new value
}

int main() {
    std::vector<int> v = {0, 2, 1, 5, 3, 4};
    permuteInPlace(v);
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
0 1 2 4 5 3 
```

In the first loop, `v[v[i]] % n` extracts the *original* value at the target
slot even if that slot has already been updated — because the original is still
sitting in the remainder. That is the point of the encoding: the first pass can
read old values and write new ones simultaneously.

:::pitfall The two ways this trick bites
**Overflow.** `v[i] + n * something` can reach $n^2$. For $n = 100{,}000$ that
is $10^{10}$, well past `int`. Use `long long` or check the constraints.

**Negative numbers.** Both the sign trick and the encoding trick assume
non-negative values. A single negative element breaks `abs(v[i]) - 1` as an
index. Always check the stated range before reaching for either.
:::

## When in-place is impossible

Not every problem can be done in $O(1)$ space, and recognising that is as
valuable as finding a clever encoding.

| Problem | In place? | Why |
|---|---|---|
| Reverse an array | yes | swaps only |
| Rotate by $k$ | yes | three reversals |
| Remove duplicates (sorted) | yes | write pointer |
| Remove duplicates (unsorted, order kept) | **no** | you must remember every value seen: $O(n)$ |
| Merge two sorted arrays into a third | **no** | the output is $O(n)$ by definition |
| Stable partition, both groups ordered | **no** in $O(n)$ time | needs $O(n)$ space or $O(n \log n)$ time |
| Sort | yes, with heapsort or quicksort | but quicksort uses $O(\log n)$ stack |

:::interview How to handle the follow-up
When an interviewer says *"now do it in $O(1)$ space"*, they are asking one of
three questions, and your first job is to work out which:

1. **"Can you use a write pointer?"** — most of the time, this is it.
2. **"Have you spotted the 1..n constraint?"** — if the problem mentions a value
   range equal to the array length, index marking is intended.
3. **"Do you know this is impossible?"** — occasionally the honest answer is
   *"not without losing the order"* or *"not in linear time"*, and saying so with
   a reason beats inventing something broken.
:::

:::recap Chapter 13 in six lines
- In place means $O(1)$ **auxiliary** space; the input is free to use and to
  modify.
- A **write pointer** solves every keep-or-discard problem in one pass.
- Rotation by $k$ is three reversals, because $(AB)^R = B^R A^R$. Remember
  `k %= n`.
- When values are in $1..n$, the array has a slot per value: use **signs** as
  visited marks.
- $a + b \times n$ stores two values in one slot; recover with `% n` and `/ n`,
  and watch for overflow.
- Some problems genuinely need $O(n)$ space. Knowing which ones is part of the
  skill.
:::

:::exercise Practise
1. Rotate `{1,2,3,4,5}` **left** by 2 using three reversals. Which ranges do you
   reverse, and in what order?
2. Why does `rotateRight` need `k %= n`? What exactly goes wrong with
   `{1,2,3}` and $k = 5$ if you leave it out?
3. Given an array of $n$ values each in $1..n$ with exactly one missing and one
   duplicated, find both in $O(n)$ time and $O(1)$ space.
4. First missing positive: given an unsorted array, find the smallest positive
   integer not present, in $O(n)$ time and $O(1)$ space. (Hint: the answer is
   always in $1..n+1$ — why? Then put each value $x$ into slot $x-1$ by
   swapping.)
5. Sort an array containing only 0s, 1s and 2s in one pass with $O(1)$ space.
   (This is the Dutch National Flag problem; it needs **three** pointers.)
6. Explain why removing duplicates from an *unsorted* array while preserving
   order cannot be done in $O(1)$ space. What is the minimum you must remember?
7. The sign-marking trick fails if the array may contain 0. Why? Suggest a fix
   that still uses $O(1)$ space.
8. You are asked to merge two sorted arrays `a` (with $m$ real elements and $n$
   spare slots at the end) and `b` (with $n$ elements) into `a`, in place. Why
   does filling from the **front** fail, and what does filling from the **back**
   fix?
:::
