# The Five-Level Practice Roadmap
@short: The Practice Roadmap
@subtitle: What to solve, in what order, and how to know you are ready
@tier: practice
@prereq: none — use this from day one
@blurb: Knowing which problems to solve, in which order, is worth more than any individual solution. This roadmap orders every problem in the book into five levels, states the prerequisite skills for each, gives a hint before each solution, and tells you the signal that you are ready to move on. Work it in order; the levels are built so that nothing in one depends on anything in a later one.
@objectives:
- Follow a problem order where nothing depends on material you have not met
- Know the prerequisite skills for each level before starting it
- Use the hints to get unstuck without reading a solution
- Identify the problems worth revisiting, and when
- Recognise the signal that you are ready for the next level

## How to use this

@fig: road_levels | 186 | The five levels. Each is defined by what you must already be able to do, and each has an exit signal — a thing you can check — rather than a number of problems solved.

:::checklist The rules of the roadmap
1. **Do them in order.** Nothing at a level needs material from a later one.
2. **Attempt before reading.** Give every problem 20 minutes of honest effort
   before looking at the hint, and 40 before the solution.
3. **Use the hint, not the solution.** The hint is one sentence; it restarts your
   thinking without finishing it for you.
4. **Re-solve, do not re-read.** A problem you read a solution for is not solved.
   Mark it and come back in three days with a blank page.
5. **Move on at the signal, not at the count.** The exit signal for each level is
   stated. Solving thirty problems badly is worse than solving ten properly.
:::

## Level 1 — Absolute beginner

**Prerequisites:** you can write a `for` loop and a function in C++.

**Read first:** Chapters 1–4.

**Goal:** be comfortable walking an array and reasoning about indices.

@tbl: Level 1. None of these needs a pattern — they need correct loop bounds and attention to edge cases.
| # | Problem | Chapter | Hint |
|---|---|---|---|
| 1 | Print an array forwards and backwards | 4 | the backwards loop starts at `n-1` and ends at `>= 0` |
| 2 | Sum and average | 6 | accumulate in `long long`; cast before dividing |
| 3 | Largest element | 8 | start `best` from `v[0]`, never from 0 |
| 4 | Count occurrences of a value | 6 | one pass, one counter |
| 5 | Check whether an array is sorted | 8 | start the loop at `i = 1`, compare with `i-1` |
| 6 | Reverse an array in place | 6 | two pointers, `left < right` |
| 7 | Find the index of a value, or $-1$ | 4 | $-1$ works as "absent" because 0 is a valid index |
| 8 | Second-largest distinct value | 8 | demote before you promote |

**Exit signal.** You can write any of these, first time, without a compiler
error, and you test the empty array without being told to.

## Level 2 — Basic operations

**Prerequisites:** Level 1, plus Chapters 5–7 and 21–22.

**Goal:** operations that change a structure, and the memory discipline that
goes with them.

@tbl: Level 2. The array half is about shifting; the list half is about pointers and about not leaking.
| # | Problem | Chapter | Hint |
|---|---|---|---|
| 9 | Insert into an array at a position | 6 | copy **backwards**, from the far end |
| 10 | Delete from an array at a position | 6 | copy **forwards**, towards the hole |
| 11 | Remove duplicates from a sorted array | 6 | a write pointer, comparing with the last kept |
| 12 | Move zeroes to the end | 6 | compact the non-zeroes, then pad |
| 13 | Build a linked list from a vector | 24 | keep a `tail` pointer or it is $O(n^2)$ |
| 14 | Print and count a linked list | 24 | walk with `curr`; `head` never moves |
| 15 | Insert at the front and back of a list | 25 | front needs `Node*&`; back needs `curr->next != nullptr` |
| 16 | Delete the first and last node | 26 | the last needs the **second-to-last** node |
| 17 | Free a whole list with no leaks | 22, 24 | save `next`, advance, **then** delete |
| 18 | Transpose a square matrix | 7 | inner loop starts at `c = r + 1` |

**Exit signal.** Every program you write in this level passes
`-fsanitize=address,undefined` with no report.

## Level 3 — Pattern recognition

**Prerequisites:** Level 2, plus Chapters 8–17.

**Goal:** given a problem, name the pattern before writing any code.

@tbl: Level 3. For each one, write down the pattern **before** you start. That habit is the whole point of this level.
| # | Problem | Pattern | Hint |
|---|---|---|---|
| 19 | Two Sum (sorted) | two pointers | the sum is too small → raise the small end |
| 20 | Two Sum (unsorted) | hash map | look up `target - x` before inserting `x` |
| 21 | Maximum consecutive ones | linear traversal | update `best` inside the run |
| 22 | Max sum of $k$ consecutive | fixed window | add the incoming, subtract `v[i-k]` |
| 23 | Longest sub-string, no repeats | variable window | shrink while the **new** character repeats |
| 24 | Range-sum queries | prefix sums | `prefix[j+1] - prefix[i]`; keep the leading zero |
| 25 | Binary search | binary search | `mid = lo + (hi-lo)/2`; test on $n = 2$ |
| 26 | First and last occurrence | binary search | on a match, record and keep going |
| 27 | Rotate an array by $k$ | three reversals | `k %= n` first |
| 28 | Contains duplicate | hash set | `insert().second` checks and inserts at once |
| 29 | Valid anagram | count array | add for one string, subtract for the other |
| 30 | Maximum sub-array sum | Kadane | extend or restart; initialise from `v[0]` |
| 31 | Buy and sell stock | running minimum | the only thing the past contributes is the cheapest price |
| 32 | Smallest absolute difference | sort first | after sorting, only neighbours can be closest |
| 33 | Spiral matrix | four boundaries | the two guards are for single rows and columns |
| 34 | Search a sorted matrix | staircase | start at the top-right corner |

**Exit signal.** Shown a problem you have not seen, you can state the pattern and
the complexity before writing a line — and be right more often than not.

## Level 4 — Intermediate interview problems

**Prerequisites:** Level 3, plus Chapters 23–31.

**Goal:** problems that combine two patterns, or need one specific insight.

@tbl: Level 4. The right-hand column is the insight, not the algorithm — read it only after twenty minutes.
| # | Problem | Chapter | Hint |
|---|---|---|---|
| 35 | Missing number | 18 | sum, or XOR the indices with the values |
| 36 | Single number | 18 | `x ^ x == 0`, and XOR is commutative |
| 37 | Majority element | 19 | pair off differing votes; a majority cannot be cancelled away |
| 38 | Sort 0s, 1s and 2s | 19 | three pointers; after swapping with `high`, do **not** advance `mid` |
| 39 | Merge sorted arrays in place | 19 | fill from the **back**, where the spare slots are |
| 40 | Product except self | 19 | prefix product × suffix product, no division |
| 41 | Sub-array sum equals K | 11 | `prefix[i] = running - K` is a hash lookup; seed with `{0:1}` |
| 42 | Longest sub-array with sum K | 19 | store the **earliest** index of each prefix value |
| 43 | Find the duplicate number | 19 | read the array as a linked list and use Floyd |
| 44 | Reverse a linked list | 28 | save `next` first; finish with `head = prev` |
| 45 | Middle of a list | 29 | fast moves two, slow moves one |
| 46 | Detect a cycle | 29 | the gap shrinks by exactly one per step |
| 47 | Cycle II — find the entrance | 29 | $F = nL - a$; both pointers move one step in phase 2 |
| 48 | Merge two sorted lists | 29 | a dummy node removes the first-node case |
| 49 | Remove nth from end | 30 | gap of $n+1$ from the dummy, so `trail` lands on the predecessor |
| 50 | Palindrome linked list | 31 | middle + reverse + compare, then restore |
| 51 | Intersection of two lists | 31 | each pointer walks $a + b + c$ |
| 52 | Add two numbers | 31 | one loop, running while either list has digits or a carry remains |
| 53 | Reorder list | 31 | split, reverse, interleave |

**Exit signal.** You can solve any of these in 25 minutes, explaining as you go,
and you volunteer the complexity without being asked.

## Level 5 — Advanced interview problems

**Prerequisites:** Level 4, plus Chapters 20, 32 and 34.

**Goal:** problems where the insight is not guessable, so the method has to carry
you.

@tbl: Level 5. Apply the seventeen-step method of Chapter 34 to every one of these, in writing.
| # | Problem | Chapter | Hint |
|---|---|---|---|
| 54 | Search in a rotated sorted array | 20 | one half is always properly sorted — work out which |
| 55 | Minimum of a rotated sorted array | 20 | compare the middle with the right end |
| 56 | Trapping rain water | 20 | solve one column first; then two pointers, moving the shorter wall |
| 57 | Maximum product sub-array | 16 | carry both the max and the min; a negative swaps them |
| 58 | Three Sum | 15 | sort, fix one, two-pointer the rest; skip duplicates |
| 59 | Container with most water | 9 | move the shorter wall — it is the only move that can help |
| 60 | First missing positive | 13 | the answer is in $1..n+1$; put value $x$ into slot $x-1$ |
| 61 | Find all duplicates in $1..n$ | 13 | use the sign at index $\lvert v \rvert - 1$ as a visited mark |
| 62 | Longest consecutive sequence | 14 | only start counting from values with no predecessor in the set |
| 63 | Reverse nodes in k-groups | 32 | check that $k$ remain **before** reversing |
| 64 | Rotate list | 32 | close the ring, then cut elsewhere |
| 65 | Sort list | 32 | merge sort; split at the **first** middle |
| 66 | Copy list with random pointer | 32 | interleave each copy after its original |
| 67 | Binary search on the answer | 12 | "minimum X such that…" with a monotonic test |
| 68 | Largest rectangle in a histogram | 20 | for each bar, how far can it extend before a shorter one? |

**Exit signal.** Given an unseen problem of this difficulty, you can reach a
correct brute force in five minutes and name a plausible improvement in ten —
even when you do not finish.

## The problems worth revisiting

Not all problems repay repetition equally. These twelve do, because each
contains an idea that reappears everywhere.

@tbl: The twelve to re-solve from blank paper every few weeks. Between them they contain almost every idea in the book.
| Problem | The idea it contains |
|---|---|
| Reverse a linked list | pointer manipulation, in its purest form |
| Binary search | the invariant, and the off-by-one |
| Two Sum (both versions) | hashing versus two pointers, and the trade-off |
| Kadane's algorithm | "best ending here" — the seed of dynamic programming |
| Sliding window (variable) | grow, shrink, record — and the amortised argument |
| Prefix sums + hash map | precompute once, answer in $O(1)$ |
| Merge two sorted lists | relinking, and the dummy node |
| Floyd's cycle detection | a non-obvious $O(1)$-space argument you can prove |
| Remove nth from end | the gap, and why it is $n+1$ |
| Trapping rain water | solve one position, then optimise |
| Dutch national flag | three-way partitioning, and an asymmetric invariant |
| Merge sort on a list | divide and conquer with no auxiliary array |

:::insight The difference between solving and knowing
Solving a problem once means you found the idea with the problem in front of
you. Knowing it means you can reconstruct it from nothing.

The test is simple and uncomfortable: **a blank page and no notes.** Set a timer
for fifteen minutes, write the full solution, then compile it. Anything you
cannot do that way, you have read rather than learned.

Three days is roughly the right interval for the first repeat, then a week, then
a month. That spacing is doing most of the work.
:::

:::recap Chapter 36 in five lines
- Five levels, each defined by its prerequisites and its exit signal rather than
  a problem count.
- Attempt for twenty minutes, then a hint, then forty minutes, then the
  solution.
- At Level 3 the habit to build is **naming the pattern before coding**.
- At Level 5 the habit is **applying the method in writing**.
- Twelve problems repay re-solving from blank paper; the rest repay solving once
  properly.
:::
