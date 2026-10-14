# The Complete Course

Fourteen volumes, from what a variable is to a mock Google on-site. This
chapter is the map: what every volume contains, why they are in this order, and
which parts you may safely postpone.

## The three tiers

Topics are grouped by how much they repay the time spent on them.

:::definition The tiers
**Tier 1 — core interview foundations.** The twenty-one topics that appear in
ordinary coding interviews across the industry. You need all of them. Nothing
in Tier 2 or 3 substitutes for a gap here.

**Tier 2 — important advanced topics.** Seventeen topics that appear in harder
rounds, in senior interviews, and as the second half of two-part questions.
Start these only once Tier 1 is solid.

**Tier 3 — specialised or competitive.** Ten topics that are genuinely
beautiful and genuinely rare in hiring. They are **not** prerequisites for
interview practice. Treat them as optional depth.
:::

### Tier 1 — core interview foundations

| # | Topic | Volume |
|---|---|---|
| 1 | Arrays | 1 |
| 2 | Linked lists | 1 |
| 3 | Big O and complexity | 1 |
| 4 | Strings | **2** |
| 5 | Hash maps and hash sets | **2** |
| 6 | Two pointers | 1, **2** |
| 7 | Sliding window | 1, **2** |
| 8 | Prefix sums | 1, **2** |
| 9 | Sorting | 3 |
| 10 | Binary search | 1, 3 |
| 11 | Intervals | 3 |
| 12 | Matrix problems | 1, 3 |
| 13 | Stacks | 4 |
| 14 | Queues and deques | 4 |
| 15 | Recursion | 5 |
| 16 | Backtracking | 5 |
| 17 | Binary trees | 6 |
| 18 | Binary search trees | 6 |
| 19 | Heaps and priority queues | 7 |
| 20 | Graphs: BFS and DFS | 8 |
| 21 | Greedy algorithms | 10 |
| 22 | Dynamic programming | 10 |
| 23 | Bit manipulation | 11 |
| 24 | Basic mathematical algorithms | 11 |

### Tier 2 — important advanced topics

| # | Topic | Volume |
|---|---|---|
| 25 | Tries | 7 |
| 26 | Union-find / disjoint set union | 7 |
| 27 | Topological sorting | 8 |
| 28 | Dijkstra's algorithm | 9 |
| 29 | Minimum spanning trees | 9 |
| 30 | Shortest-path algorithms generally | 9 |
| 31 | Advanced graph problem-solving | 9 |
| 32 | Strongly connected components | 9 |
| 33 | Bridges and articulation points | 9 |
| 34 | Monotonic stacks and queues | 4 |
| 35 | Advanced binary search | 3 |
| 36 | Advanced tree problems | 6 |
| 37 | Advanced dynamic programming | 13 |
| 38 | KMP and string matching | 12 |
| 39 | Range query structures | 12 |
| 40 | Segment trees | 12 |
| 41 | Fenwick trees | 12 |

### Tier 3 — specialised or competitive

| # | Topic | Volume | Where it is actually useful |
|---|---|---|---|
| 42 | Network flow | 13 | competitive programming; occasionally in matching or scheduling questions |
| 43 | Bipartite matching | 13 | assignment problems; some research and ads-infrastructure teams |
| 44 | Digit DP | 13 | competitive programming; essentially never in hiring |
| 45 | Advanced bitmask DP | 13 | competitive programming; very occasionally in small-$n$ optimisation rounds |
| 46 | Centroid decomposition | 13 | competitive programming only |
| 47 | Heavy-light decomposition | 13 | competitive programming only |
| 48 | Suffix arrays | 12 | bioinformatics, search infrastructure, some systems teams |
| 49 | Advanced number theory | 11 | cryptography roles; competitive programming |
| 50 | Computational geometry | 13 | graphics, mapping, robotics, autonomous-vehicle teams |
| 51 | Advanced combinatorics | 13 | competitive programming; probability-heavy roles |

:::warning Do not start here
Tier 3 is the part of this syllabus most likely to waste your time if taken
early. A candidate fluent in Tier 1 and competent in Tier 2 is in a much
stronger position than one who has read about heavy-light decomposition and is
shaky on binary search.

The honest rule: **begin interviewing when Tier 1 is solid.** Study Tier 2
alongside interviewing. Open Tier 3 only if a specific role, a competition, or
genuine curiosity calls for it.
:::

## The fourteen volumes

@fig: course_map | 212 | The fourteen volumes and what depends on what. The spine runs left to right; the dashed arrows are the places where a later volume genuinely needs an earlier one, as opposed to merely following it.

| Vol | Title | Covers |
|---|---|---|
| 1 | Arrays & Linked Lists | arrays, `std::vector`, linked lists, pointers and memory, Big O |
| **2** | **Strings, Hashing & the Window Patterns** | **strings, hash tables, prefix techniques, two pointers, sliding windows** |
| 3 | Sorting, Searching & Intervals | sorting algorithms, comparators, binary search in depth, binary search on the answer, intervals, matrix patterns |
| 4 | Stacks, Queues & Monotonic Structures | stacks, queues, deques, monotonic stacks and queues, expression evaluation |
| 5 | Recursion, Backtracking & Decision Trees | the call stack, recursion patterns, the backtracking template, pruning, decision trees |
| 6 | Binary Trees & Binary Search Trees | tree structure, the four traversals, BST invariants, construction, advanced tree problems |
| 7 | Heaps, Tries & Union-Find | binary heaps, `priority_queue`, top-K, tries, disjoint set union with both optimisations |
| 8 | Graphs: BFS, DFS & Topological Order | representations, traversal, connected components, cycle detection, bipartiteness, topological sort |
| 9 | Shortest Paths & Advanced Graphs | Dijkstra, Bellman-Ford, Floyd-Warshall, MSTs, SCCs, bridges and articulation points |
| 10 | Greedy Algorithms & Dynamic Programming | the exchange argument, the DP method, 1-D and 2-D DP, the classic DP family |
| 11 | Bits, Maths & Number Theory | bit manipulation, modular arithmetic, primes, GCD, combinatorics basics |
| 12 | Range Queries & String Algorithms | segment trees, Fenwick trees, sparse tables, KMP, Z-algorithm, Rabin-Karp, suffix arrays |
| 13 | Advanced DP & Specialised Algorithms | bitmask and digit DP, flows, matching, geometry, decomposition techniques |
| 14 | Interview Practice & Final Revision | mixed problem sets, timed practice, mock interviews, the full revision system |

### Why this order

:::insight The dependency reasoning
**Volume 2 before 3** because hashing and two pointers are needed to discuss
what sorting buys you.

**Volume 4 before 5** because a stack *is* what recursion uses, and seeing the
explicit version first makes the implicit one obvious.

**Volume 5 before 6** because every tree algorithm is a recursion, and
debugging a tree recursion while still learning recursion is two problems at
once.

**Volume 6 before 7** because a heap is a tree, and a trie is a tree.

**Volume 7 before 8** because union-find is the natural way into connectivity,
and priority queues are what Dijkstra is built on.

**Volume 10 late** because dynamic programming is the hardest Tier 1 topic and
benefits from everything before it — particularly recursion (Volume 5), which
is where DP actually comes from.

The one order you should *not* change: **do not start Volume 10 early.** More
people stall on dynamic programming than on any other topic, and almost always
because they met it before recursion was automatic.
:::

## Where this volume sits

You are at Volume 2 of 14. By the end of it you will have the four patterns
that, between them, account for a large share of easy and medium interview
problems: **hashing**, **prefix**, **two pointers** and **sliding window**.

That is not a small claim, and it is worth being precise about it: those four
patterns do not solve everything, and they solve almost nothing in Volumes 6
to 13. What they do is cover the ground where most people's practice begins,
and build the habit — *recognise the shape, then write the code* — that the
rest of the course depends on.

## A note on interview formats

Hiring processes differ by company, by role, by level, by team and by country,
and they change over time. This course teaches general software-engineering
problem solving, which is what coding rounds assess almost everywhere; it does
not teach a specific company's process.

:::warning What this book will not tell you
It will not tell you which questions a given company asks, how many rounds
there are, or what a particular bar is. That information changes, varies by
team, and is not something a textbook can responsibly assert.

For any specific employer, read **their own careers pages and the material
their recruiter sends you**, and treat everything else — including this book,
and including forum reports of question frequencies — as general preparation
rather than inside knowledge.

What is safe to say, and what this course is built on: coding rounds assess
whether you can take an unfamiliar problem, clarify it, reach a working
solution, improve it, reason about its cost, and explain yourself while doing
so. That is a skill, it is trainable, and the fourteen volumes train it.
:::

:::recap The map in five lines
- **Tier 1** is required; **Tier 2** is for harder rounds; **Tier 3** is
  optional depth and should not delay you.
- Fourteen volumes, ordered so that nothing depends on material you have not
  met.
- This is Volume 2: strings, hashing, prefix, two pointers, windows.
- Begin interviewing when Tier 1 is solid, and study Tier 2 alongside.
- Chapter 25 contains the sixteen-week plan that runs across the whole course.
:::
