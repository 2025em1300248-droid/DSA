# Foundational Array Problems
@short: Foundational Problems
@subtitle: Eleven problems that should become automatic
@tier: practice
@prereq: Part III
@blurb: These eleven problems are the vocabulary of array work. None is hard once you see it, and every one of them appears inside harder problems later, so the goal here is not merely to solve them but to make them *automatic* — to reach the point where "find the second largest" produces a correct one-pass solution without conscious thought.
@objectives:
- Solve all eleven foundational problems correctly, including their edge cases
- Recognise which pattern from Part III each one uses
- Give the brute force, the optimisation, and the reason for the optimisation
- Handle empty arrays, single elements, all-equal input and negative numbers
- Explain the XOR trick, and why it gives $O(1)$ space

## How these are presented

Every problem follows the same six headings. Read **Think** before looking at
the code, and try to finish the derivation yourself.

| Heading | What it contains |
|---|---|
| **Problem** | the precise statement, including what the awkward inputs should do |
| **Think** | brute force, then the observation that improves it |
| **Code** | complete, compilable C++ with its real output |
| **Cost** | time and auxiliary space, with the reason |
| **Watch for** | the specific mistakes this problem invites |
| **Next** | a closely related problem to try alone |

@fig: pf_map | 164 | The eleven problems and the pattern each one rests on. Four of the ten patterns cover all of them, which is the point of having learned the patterns first.

## 1. Largest element

**Problem.** Return the largest value. Empty input has no answer — decide
whether to throw or to return a sentinel, and say which.

**Think.** One pass, one variable. The only decision is the initial value, and
it must be a real element so that all-negative arrays work.

**Code.** See Chapter 8. **Cost.** $O(n)$ / $O(1)$.

**Watch for.** `int best = 0;` fails on `{-5, -2}`.

**Next.** Largest *and* smallest in one pass, using $\lceil 3n/2 \rceil$
comparisons instead of $2n$ — compare elements in pairs first.

## 2. Second-largest element

**Problem.** Return the second-largest **distinct** value, or report that there
is none. `{5, 5, 4}` → 4. `{7, 7, 7}` → none.

**Think.** Covered fully in Chapter 8. The two ideas: carry `best` and
`second`; demote before you promote.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Using `INT_MIN` as the "none" marker when `INT_MIN` could be a
real value. Use a wider accumulator type.

**Next.** $k$-th largest distinct value for small $k$. At what $k$ does this
approach stop being sensible, and what replaces it?

## 3. Check whether an array is sorted

**Problem.** Return whether the array is non-decreasing. Empty and
single-element arrays are sorted.

**Think.** Compare each element with its predecessor; one violation is enough.
Covered in Chapter 8.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Starting the loop at `i = 0` and reading `v[-1]`. Deciding
whether equal neighbours are allowed — `{2, 2}` is sorted under
"non-decreasing" and not under "strictly increasing". Ask.

**Next.** Check whether an array is a **rotated** sorted array, such as
`{3, 4, 5, 1, 2}`. How many "descents" may there be, and where?

## 4. Reverse an array

**Problem.** Reverse in place.

**Think.** Converging two pointers, swapping and stepping inwards. Covered in
Chapter 6.

**Cost.** $O(n)$ / $O(1)$ — exactly $\lfloor n/2 \rfloor$ swaps.

**Watch for.** Looping to `n` instead of `n/2`, which reverses twice and
changes nothing.

**Next.** Reverse only a given range `[i, j]`. This is the building block of
the rotation trick in Chapter 13.

## 5. Remove duplicates from a sorted array

**Problem.** Remove repeats in place, keeping order; return the new length.

**Think.** Sorted input means duplicates are adjacent, so you only compare with
the last value you kept. Write pointer. Covered in Chapter 6.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Assuming it works on unsorted data — it does not.

**Next.** Allow each value to appear at most **twice**. Compare against
`v[w - 2]`, and think carefully about where `w` starts.

## 6. Move zeroes to the end

**Problem.** Move all zeroes to the end, preserving the order of the non-zero
values, in place.

**Think.** Write pointer: compact the non-zeroes, then pad. Covered in
Chapter 6.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Swapping the non-zeroes into place changes which elements move
but not the complexity; both are acceptable, and you should be able to compare
them.

**Next.** Move all instances of a given value to the **front** instead, with the
rest in order.

## 7. Rotate an array by k

**Problem.** Rotate right by $k$ in place. $k$ may exceed $n$.

**Think.** Three reversals, because $(AB)^R = B^R A^R$. Covered in Chapter 13.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Forgetting `k %= n`, which reads past the end.

**Next.** Rotate a **matrix** by 90° — Chapter 17 uses the same
decompose-into-known-operations tactic.

## 8. Union of two sorted arrays

**Problem.** Return the sorted union of two sorted arrays, without duplicates.

**Think.** Two pointers, one per array, always advancing the one with the
smaller front value. Covered in Chapter 15.

**Cost.** $O(n + m)$ time, $O(n + m)$ for the output.

**Watch for.** Duplicates within one array as well as across both; the
`out.back() != x` guard handles both at once. And do not forget the two
tail loops — when one array runs out, the other still has elements.

**Next.** The **intersection**, and the **difference** $A \setminus B$. All
three are the same loop with different branches.

## 9. Missing number

**Problem.** An array holds $n$ distinct values from the range $0 \dots n$, so
exactly one is missing. Find it. `{3, 0, 1}` → 2.

**Think.** Sorting is $O(n \log n)$; a seen-array is $O(n)$ space. Both work.
But there are two $O(n)$-time, $O(1)$-space solutions, and they are worth
knowing because the same tricks reappear.

@fig: pf_missing | 160 | Two ways to find the missing number. The sum method subtracts what is present from what should be present. The XOR method cancels every value that appears in both lists, leaving only the one that does not.

:::insight The sum trick and the XOR trick
**Sum.** The numbers $0 \dots n$ add up to $n(n+1)/2$. Subtract the actual sum
and the difference is the missing value. Simple, but the expected sum can
overflow `int` for large $n$ — use `long long`.

**XOR.** Exclusive-or has two properties that make it ideal:
$x \oplus x = 0$ and $x \oplus 0 = x$. So if you XOR together *all* the indices
$0 \dots n$ **and** all the array values, every number that appears in both
cancels to zero, and only the missing one survives.

XOR cannot overflow, which makes it the more robust answer — and it is the key
to problem 11 as well.
:::

```cpp title="Missing number, two ways"
#include <iostream>
#include <vector>

int missingBySum(const std::vector<int>& v) {
    long long n = (long long)v.size();
    long long expected = n * (n + 1) / 2;     // 0 + 1 + ... + n
    long long actual = 0;
    for (int x : v) actual += x;
    return (int)(expected - actual);
}

int missingByXor(const std::vector<int>& v) {
    int result = (int)v.size();               // start with n itself
    for (int i = 0; i < (int)v.size(); ++i)
        result ^= i ^ v[i];                   // every present value cancels
    return result;
}

int main() {
    std::vector<int> v = {3, 0, 1};
    std::cout << missingBySum(v) << " " << missingByXor(v) << "\n";
    std::vector<int> w = {0, 1};
    std::cout << missingBySum(w) << " " << missingByXor(w) << "\n";
    std::vector<int> z = {1};                 // 0 is missing
    std::cout << missingBySum(z) << " " << missingByXor(z) << "\n";
    return 0;
}
```

```text nonum
2 2
2 2
0 0
```

**Cost.** $O(n)$ / $O(1)$ for both.

**Watch for.** Overflow in the sum version. Forgetting that the range is
$0 \dots n$ inclusive, which is $n+1$ possible values for $n$ array slots —
that asymmetry is the whole problem.

**Next.** Two numbers are missing from $1 \dots n$. The sum alone is no longer
enough; what second equation do you need?

## 10. Maximum consecutive ones

**Problem.** Longest run of 1s in a binary array.

**Think.** Current-run and best-run. Covered in Chapter 8.

**Cost.** $O(n)$ / $O(1)$.

**Watch for.** Updating `best` only when the run ends, which loses a run that
reaches the end of the array.

**Next.** Allow flipping at most one 0 — that becomes a sliding window
(Chapter 10), and generalises to $k$ flips with no extra difficulty.

## 11. Single number

**Problem.** Every value appears exactly twice except one, which appears once.
Find it. `{4, 1, 2, 1, 2}` → 4.

**Think.** A hash map solves it in $O(n)$ time and $O(n)$ space. The interviewer
will then ask for $O(1)$ space, and XOR is the answer.

:::insight Why XOR solves it in one line
XOR is **commutative** and **associative**, so the order of operations does not
matter. XOR-ing the whole array therefore groups the pairs however it likes, and
each pair becomes $x \oplus x = 0$. Everything cancels except the lonely value,
which ends XOR-ed with 0 and so survives unchanged.

$$4 \oplus 1 \oplus 2 \oplus 1 \oplus 2 = 4 \oplus (1 \oplus 1) \oplus (2 \oplus 2) = 4 \oplus 0 \oplus 0 = 4$$
:::

@fig: pf_xor | 150 | XOR cancellation. Rearranging the array so pairs sit together is allowed because XOR is commutative and associative — and once rearranged, every pair vanishes.

```cpp title="Single number in one line"
#include <iostream>
#include <vector>

int singleNumber(const std::vector<int>& v) {
    int result = 0;
    for (int x : v) result ^= x;     // pairs cancel; the lonely value survives
    return result;
}

int main() {
    std::cout << singleNumber({4, 1, 2, 1, 2}) << "\n";
    std::cout << singleNumber({2, 2, 7})       << "\n";
    std::cout << singleNumber({99})            << "\n";
    std::cout << singleNumber({-3, 5, 5})      << "\n";   // negatives are fine
    return 0;
}
```

```text nonum
4
7
99
-3
```

**Cost.** $O(n)$ time, $O(1)$ space.

**Watch for.** This works **only** when every other value appears exactly
*twice*. If the others appear three times, XOR no longer cancels them, and you
need a different technique (counting the bits set at each position, modulo 3).
Check the exact wording of the problem.

**Next.** Two values appear once and the rest twice. (Hint: XOR everything, find
any bit where the result is 1, and use that bit to split the array into two
groups — each containing one of the loners.)

## The whole set, at a glance

@tbl: The eleven foundational problems. Four patterns cover all of them, and every one is $O(n)$ or better with $O(1)$ space.
| # | Problem | Pattern | Time | Space |
|---|---|---|---|---|
| 1 | Largest element | linear traversal | $O(n)$ | $O(1)$ |
| 2 | Second largest | linear traversal | $O(n)$ | $O(1)$ |
| 3 | Is sorted | linear traversal | $O(n)$ | $O(1)$ |
| 4 | Reverse | two pointers | $O(n)$ | $O(1)$ |
| 5 | Remove duplicates (sorted) | write pointer | $O(n)$ | $O(1)$ |
| 6 | Move zeroes | write pointer | $O(n)$ | $O(1)$ |
| 7 | Rotate by $k$ | three reversals | $O(n)$ | $O(1)$ |
| 8 | Union of sorted arrays | two pointers | $O(n+m)$ | $O(n+m)$ out |
| 9 | Missing number | sum or XOR | $O(n)$ | $O(1)$ |
| 10 | Max consecutive ones | linear traversal | $O(n)$ | $O(1)$ |
| 11 | Single number | XOR | $O(n)$ | $O(1)$ |

:::interview What "foundational" means to an interviewer
Nobody will hire you for solving these. But everybody will *decline* to hire you
for getting one wrong — because an interviewer reads a bug in "reverse an array"
as a signal about everything you will write afterwards.

The bar here is not cleverness; it is **reliability**. You should be able to
write any of these, correctly, first time, while talking. That only comes from
writing them more than once.
:::

:::exercise Consolidate
1. Write all eleven from memory, with no reference, and test each one on: the
   empty array, one element, all elements equal, and all elements negative.
2. For each problem, name its pattern without looking at the table.
3. Which three could be solved by sorting first? For each, say what sorting
   costs you and whether it is ever worth it.
4. Which two use a mathematical identity rather than a traversal strategy?
5. Take problems 5 and 6 and write a single function that does both in one
   pass over a sorted array.
6. For problem 9, work out the largest $n$ for which `int` arithmetic is safe in
   the sum method. Does the XOR method have an equivalent limit?
:::
