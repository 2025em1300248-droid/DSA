# Reference: Plan, Checklist, Glossary
@short: Reference
@subtitle: A thirty-day plan, the formula sheets, and every term defined
@tier: reference
@prereq: none — use this throughout
@blurb: The part of the book to keep open. A thirty-day study plan that assumes about ninety minutes a day, the pattern and complexity sheets condensed to a page each, a revision checklist to run before an interview, and a glossary of every technical term this book uses.
@objectives:
- Follow a day-by-day plan through the whole book
- Recall any pattern or complexity from a one-page summary
- Run a final revision check before an interview
- Look up any term used anywhere in this book

## The thirty-day plan

Each day is about ninety minutes: roughly forty of reading and fifty of
problems. If you have less time, take sixty days and halve each day — do **not**
skip the problem half, which is where the learning is.

@fig: ref_plan | 196 | The thirty days by theme. Note that the two review days and the four buffer days are not optional padding — spaced repetition is doing a large part of the work.

@tbl: Week 1 — foundations and arrays. By the end you can write any basic array operation without thinking.
| Day | Read | Do |
|---|---|---|
| 1 | Chapters 1–2 | Ch 1 and 2 exercises; run the `sizeof`/`&` programs yourself |
| 2 | Chapter 3 | Ch 3 complexity drills; Exercise set E in Chapter 37 |
| 3 | Chapters 4–5 | Roadmap Level 1, problems 1–8 |
| 4 | Chapter 6 | Roadmap Level 2, problems 9–12; trace each by hand first |
| 5 | Chapter 7 | Problem 18; write spiral traversal for a $3\times5$ grid |
| 6 | Chapters 8–9 | Problems 19–21; set B of Chapter 37 |
| 7 | **Review** | Re-solve problems 1–12 from blank paper. No notes. |

@tbl: Week 2 — the array patterns. The goal is naming the pattern before coding, every time.
| Day | Read | Do |
|---|---|---|
| 8 | Chapter 10 | Problems 22–23; write the fixed and variable window from scratch |
| 9 | Chapter 11 | Problem 24; sub-array sum equals K |
| 10 | Chapter 12 | Problems 25–26; binary search, then first/last occurrence |
| 11 | Chapter 13 | Problem 27; rotate by three reversals |
| 12 | Chapter 14 | Problems 20, 28, 29 |
| 13 | Chapters 15–16 | Problems 30–32 |
| 14 | **Review** | Chapter 37 sets A and C. Re-solve anything you got wrong. |

@tbl: Week 3 — pointers and linked lists. The slowest week for most people; do not rush it.
| Day | Read | Do |
|---|---|---|
| 15 | Chapters 17, 21 | Problems 33–34; the Chapter 21 pointer exercises |
| 16 | Chapter 22 | Build and free a list; verify with `-fsanitize=address` |
| 17 | Chapters 23–24 | Problems 13–14; build, print, count, search |
| 18 | Chapter 25 | Problem 15; all four insertions |
| 19 | Chapter 26 | Problems 16–17; all four deletions, no leaks |
| 20 | Chapter 27 | Doubly linked insert and delete; the circular traversal |
| 21 | **Review** | Re-solve every list operation from blank paper. |

@tbl: Week 4 — list problems and the harder array problems.
| Day | Read | Do |
|---|---|---|
| 22 | Chapter 28 | Problem 44; reverse iteratively, then recursively, then trace both |
| 23 | Chapter 29 | Problems 45–48 |
| 24 | Chapter 30 | Problem 49; the six core list problems |
| 25 | Chapter 31 | Problems 50–53 |
| 26 | Chapters 18–19 | Problems 35–43 |
| 27 | Chapter 20 | Problems 54–57 |
| 28 | Chapter 32 | Problems 63–66 |

@tbl: The last two days, plus how to use the buffer.
| Day | Read | Do |
|---|---|---|
| 29 | Chapters 33–35 | The complexity showdown; run the Chapter 35 checklist over old code |
| 30 | Chapters 34, 39 | One full mock interview, recorded, from Chapter 39 |
| Buffer | — | Four spare days. Use them on whatever you needed a hint for. |

:::insight Why the review days matter more than the reading days
Days 7, 14 and 21 ask you to re-solve from a blank page. That feels like
repetition and is not — it is **retrieval practice**, and the evidence that it
beats re-reading is overwhelming.

If you are short of time, cut a reading day. Never cut a review day.
:::

## Pattern summary sheet

@tbl: Every pattern in the book, with its trigger and its cost. If you remember one page, make it this one.
| Pattern | Trigger in the problem | Time | Space | Chapter |
|---|---|---|---|---|
| Linear traversal | a summary of everything seen | $O(n)$ | $O(1)$ | 8 |
| Two pointers, converging | sorted array, a **pair** wanted | $O(n)$ | $O(1)$ | 9 |
| Two pointers, same direction | filter or compact in place | $O(n)$ | $O(1)$ | 9 |
| Sliding window, fixed | "every window of size $k$" | $O(n)$ | $O(1)$ | 10 |
| Sliding window, variable | "longest/shortest contiguous…" | $O(n)$ | $O(1)$ | 10 |
| Prefix sums | many range queries; sums with negatives | $O(n)$ build | $O(n)$ | 11 |
| Binary search | sorted array, or a monotonic test | $O(\log n)$ | $O(1)$ | 12 |
| Binary search on the answer | "minimum X such that…" | $O(\log R \cdot C)$ | $O(1)$ | 12 |
| In-place / index marking | "$O(1)$ space", values in $1..n$ | $O(n)$ | $O(1)$ | 13 |
| Frequency counting | "have I seen this?" | $O(n)$ | $O(n)$ | 14 |
| Sort first | closest pair, duplicates, grouping | $O(n \log n)$ | varies | 15 |
| Kadane | "maximum sub-array…" | $O(n)$ | $O(1)$ | 16 |
| Matrix boundaries | spiral, rotate, layer traversal | $O(RC)$ | $O(1)$ | 17 |
| Dummy node | the head may change | $O(1)$ extra | $O(1)$ | 29 |
| Fast and slow | middle, cycle, split in half | $O(n)$ | $O(1)$ | 29 |
| Fixed gap | "$k$-th from the end" | $O(n)$ | $O(1)$ | 29 |
| Floyd's algorithm | cycle detection or its entrance | $O(n)$ | $O(1)$ | 29 |
| Merge / split | sorted lists, sorting a list | $O(n)$ | $O(1)$ | 29 |
| Pointer reversal | reverse all or part of a list | $O(n)$ | $O(1)$ | 28 |

## Complexity summary sheet

@tbl: The growth hierarchy, with the input size each is still practical for at roughly $10^8$ operations per second.
| Complexity | Name | Practical up to | Typical source |
|---|---|---|---|
| $O(1)$ | constant | any $n$ | indexing, hash lookup, arithmetic |
| $O(\log n)$ | logarithmic | any $n$ | binary search, balanced tree |
| $O(n)$ | linear | $\sim 10^8$ | one pass |
| $O(n \log n)$ | linearithmic | $\sim 10^6$ | sorting, divide and conquer |
| $O(n^2)$ | quadratic | $\sim 10^4$ | nested loops over the input |
| $O(n^3)$ | cubic | $\sim 500$ | triple loops, naive matrix multiply |
| $O(2^n)$ | exponential | $\sim 25$ | all subsets |
| $O(n!)$ | factorial | $\sim 11$ | all permutations |

@tbl: Array and list operations at a glance — the condensed version of Chapter 33.
| Operation | Array | Singly linked | Doubly linked |
|---|---|---|---|
| Access index $i$ | $O(1)$ | $O(n)$ | $O(n)$ |
| Search unsorted | $O(n)$ | $O(n)$ | $O(n)$ |
| Search sorted | $O(\log n)$ | $O(n)$ | $O(n)$ |
| Insert front | $O(n)$ | $O(1)$ | $O(1)$ |
| Insert back | $O(1)$ am. | $O(n)$ / $O(1)$ with tail | $O(1)$ with tail |
| Insert at a held position | $O(n)$ | $O(1)$ | $O(1)$ |
| Delete front | $O(n)$ | $O(1)$ | $O(1)$ |
| Delete back | $O(1)$ | $O(n)$ | $O(1)$ with tail |
| Delete a held node | $O(n)$ | $O(n)$ | $O(1)$ |

## The revision checklist

:::checklist Run this the day before an interview
**Can you write these from memory, correctly, first time?**
Binary search · reverse a linked list · Kadane · the variable sliding window ·
the two-pointer Two Sum · merge two sorted lists · Floyd's cycle detection ·
the write-pointer filter.

**Can you state these without hesitating?**
Why `mid = lo + (hi-lo)/2` · why `push_back` is amortised $O(1)$ · why linked
list insertion is only $O(1)$ given a pointer · why binary search needs random
access · what `delete` does to the pointer · why the dummy node exists.

**Do you do these automatically?**
Ask about empty input and duplicates · state the brute force first · name the
complexity unprompted · test the empty and single-element cases · free what you
allocate · say whether you modified the input.

**Have you, in the last week?**
Recorded one mock · re-solved three problems from blank paper · run something
under `-fsanitize=address`.
:::

## Glossary

**Address.** The number identifying one byte of memory. Chapter 2.

**Amortised complexity.** The average cost per operation over a long sequence,
where occasional expensive operations are paid for by many cheap ones. Not the
same as average case. Chapter 5.

**Array.** A fixed number of same-typed elements in one contiguous block.
Chapter 4.

**Auxiliary space.** Memory an algorithm uses in addition to its input.
Recursion depth counts. Chapter 3.

**Base address.** The address of an array's first element; the $B$ in
$B + i \times S$. Chapter 2.

**Big O.** Notation for an upper bound on growth: $f(n) = O(g(n))$ if beyond some
point $f$ is at most a constant multiple of $g$. Chapter 3.

**Bit / byte.** A bit is one binary digit; a byte is eight of them, and is the
unit memory is addressed in. Chapter 2.

**Cache line.** The block of memory (typically 64 bytes) the processor fetches at
once. Why sequential access is far faster than scattered access. Chapters 7, 33.

**Capacity.** How many elements a vector's current block could hold, as opposed
to how many it does hold. Chapter 5.

**Circular linked list.** One whose last node points back to the first, so there
is no `nullptr` terminator. Chapter 27.

**Contiguous.** Occupying consecutive addresses with no gaps. The property that
makes array indexing $O(1)$. Chapter 4.

**Constructor.** A function run automatically when an object is created; it has
the type's name and no return type. Chapter 24.

**Dangling pointer.** A pointer to memory that has been freed or to an object
that no longer exists. Chapters 21, 22.

**Dereference.** To follow a pointer and reach the thing it points at: `*p` or
`p->field`. Chapter 21.

**Doubly linked list.** One whose nodes have both `next` and `prev`, so it can be
walked in either direction and a held node deleted in $O(1)$. Chapter 27.

**Dummy node.** A placeholder node placed before the real head so that every real
node has a predecessor, removing head special cases. Chapter 29.

**Dynamic array.** An array that can grow by allocating a larger block and
copying. `std::vector`. Chapter 5.

**Floyd's cycle detection.** The tortoise-and-hare algorithm, which detects a
cycle and finds its entrance in $O(1)$ space. Chapter 29.

**Head.** The pointer to a linked list's first node. Not itself a node. Chapter
23.

**Heap.** The memory region you allocate from with `new` and must return with
`delete`. Chapter 22.

**In place.** Using $O(1)$ auxiliary space; the input may be modified and used as
workspace. Chapter 13.

**Invariant.** A property that is true before and after every iteration of a
loop, used to prove correctness. Chapter 12.

**Iterator invalidation.** When an operation (such as a vector reallocating)
makes existing pointers, references and iterators unusable. Chapter 5.

**Linked list.** A sequence of nodes, each holding a value and a pointer to the
next. Chapter 23.

**Memory leak.** Heap memory that is unreachable and has not been freed.
Produces no error of any kind. Chapter 22.

**Node.** One element of a linked structure: a value plus one or more pointers.
Chapter 23.

**`nullptr`.** The pointer value meaning "points at nothing". Chapter 21.

**Ownership.** Responsibility for deleting a heap object. Every object needs
exactly one owner. Chapter 22.

**Pointer.** A variable whose value is a memory address. Chapter 21.

**Prefix sum.** An array where entry $i$ is the sum of everything before index
$i$, allowing any range sum in $O(1)$. Chapter 11.

**RAII.** Tying a resource's lifetime to an object's lifetime so that the
destructor releases it. The idea behind `std::vector` and `std::unique_ptr`.
Chapter 22.

**Random access.** The ability to reach any element in the same constant time.
Arrays have it; linked lists do not. Chapter 4.

**Reference.** An alias for an existing object: `int& r = x;`. Cannot be null and
cannot be reseated. Chapter 21.

**Row-major order.** Storing a 2-D array one complete row after another, which is
what C++ does. Chapter 7.

**Sentinel.** A value or node used to mark a boundary, such as $-1$ for "not
found" or a dummy node for "before the head". Chapters 4, 29.

**Sliding window.** A sub-array whose two edges move forwards, so that
overlapping ranges are updated rather than recomputed. Chapter 10.

**Stack (memory).** The region holding local variables, managed automatically,
one frame per active call. Chapter 22.

**Stable sort.** One that preserves the relative order of equal elements.
`std::stable_sort`; `std::sort` is not stable. Chapter 15.

**Tail.** The last node of a linked list — the one whose `next` is `nullptr`.
Chapter 23.

**Two pointers.** Two indices moving with purpose, either converging from the
ends or chasing each other from the same end. Chapter 9.

**Undefined behaviour.** Something the standard places no requirements on, such
as reading past the end of an array. Anything at all may happen. Chapter 4.

**Use after free.** Reading or writing through a pointer whose object has been
deleted. Chapter 22.

**Write pointer.** The trailing index in a same-direction two-pointer scan,
marking where the next kept element goes. Chapters 6, 9, 13.

## Where to go next

This book covered two structures completely. The natural order after it:

@tbl: What each later structure borrows from this book. None of them is a fresh start.
| Next | Built from | Why now |
|---|---|---|
| Stacks and queues | an array or a list, with a rule about which end | trivial after Part VI |
| Hash tables | an array of buckets, each a linked list | you have both halves already |
| Trees | a node with two `next` pointers | Chapter 24's struct, extended |
| Heaps | a tree stored in an array | needs the index arithmetic of Chapter 7 |
| Graphs | an array of linked lists | the adjacency list is literally that |
| Recursion and backtracking | the call stack of Chapter 22 | you have met the cost already |
| Dynamic programming | Kadane, generalised | Chapter 16 was your first DP |

:::recap The last word
You began this book not knowing what a data structure was. You can now explain
why an array indexes in constant time and a linked list does not, reverse a
linked list on paper, recognise ten patterns on sight, and derive a solution to a
problem you have never seen.

The remaining work is repetition, and repetition is a schedule rather than a
talent. Pick a problem, set a timer, talk out loud, and compile it afterwards.

Good luck.
:::
