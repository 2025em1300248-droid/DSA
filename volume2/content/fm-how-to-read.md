# How to Read This Book

This is Volume 2 of a course that starts at absolute zero and ends at
interview competence. Volume 1 — *Arrays & Linked Lists* — taught what a byte
is, what a pointer is, how to read Big O, and how to manipulate the two
simplest structures. This volume assumes you have that and nothing more.

## What Volume 1 left you with

If any of the following is shaky, go back before continuing. Each is used here
without re-explanation.

| From Volume 1 | Where | Why it is needed here |
|---|---|---|
| Memory as numbered bytes | Ch 2 | a string is bytes |
| Big O, and $\sim 10^8$ ops/second | Ch 3 | every cost claim in this book |
| `std::vector`, size vs capacity | Ch 5 | `std::string` behaves identically |
| Amortised $O(1)$ `push_back` | Ch 5 | why building a string forwards is linear |
| The write-pointer scan | Ch 6, 13 | in-place string work |
| Two pointers, converging and same-direction | Ch 9 | completed here |
| The sliding window, both kinds | Ch 10 | four shapes, developed here |
| Prefix sums | Ch 11 | generalised here |
| Frequency counting | Ch 14 | hashing proper, here |

:::note On the overlap, honestly
Four of those rows are patterns Volume 1 already introduced. This volume does
**not** repeat them. It does three things instead:

**Applies them to text**, where the alphabet is small and fixed, which changes
which implementation is right.

**Completes them.** Volume 1 gave the variable window as grow-shrink-record.
Here you get the four distinct shapes, the proof that each is linear, and the
precise condition that tells them apart.

**Combines them.** Most real problems need two patterns at once — a window
*plus* a count, a prefix *plus* a hash map. That combination is the subject of
Part VI.

Where a reminder is genuinely useful you will find a short *Recall* box, never
a full re-teaching.
:::

## How every concept is presented

The sequence never varies, and it is the same as Volume 1's:

1. **Why the concept exists** — what goes wrong without it.
2. **An everyday analogy.**
3. **The intuition**, in plain English.
4. **The terminology**, introduced only after the idea.
5. **A diagram**, where a picture helps.
6. **A tiny worked example**, three to five elements.
7. **A hand trace**, written as a table.
8. **The brute force**, and why it is not enough.
9. **The optimised version, derived** — never presented finished.
10. **C++17 code**, complete and compilable.
11. **The real output**, produced by running it.
12. **Time and auxiliary space**, with the reason.
13. **Edge cases** — empty, one element, all equal, the awkward one.
14. **The mistakes people actually make.**
15. **Practice**, with the answers in Chapter 24.

## The boxes

:::definition
A term is being given a precise meaning.
:::

:::intuition
The *why*, usually by analogy. Look here when a formal explanation did not land.
:::

:::pitfall
A specific mistake, and the reason it happens.
:::

:::perf
A note about real speed, as opposed to complexity. These two differ more in
string code than anywhere else in the course.
:::

:::interview
What an interviewer is listening for. Communication is assessed as heavily as
code; this is the part almost nobody rehearses.
:::

:::exercise
Do this before reading on. Answers in Chapter 24.
:::

## How to study it

The same four habits that worked for Volume 1:

1. **Cover the trace column** and fill it in yourself before reading it.
2. **Type the code, do not paste it.**
3. **Break it deliberately.** Change a `<` to `<=`; predict the bug before you
   run it.
4. **Re-solve from a blank page** three days later. Reading a solution is worth
   about a tenth of finding one.

:::warning One thing specific to this volume
String problems are where off-by-one errors live. Of the thirty problems in
Part VI, more than half have an edge case involving the empty string, a
single character, or a window that is briefly invalid.

Test `""` and `"a"` on every single function you write here. It takes ten
seconds and it will catch more bugs than any amount of re-reading.
:::
