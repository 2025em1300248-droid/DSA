# The Coding Round
@short: Coding Round
@subtitle: Twenty things you should be able to write without an IDE
@tier: foundation
@prereq: none
@blurb: A screening round will ask you to write code in a shared document with no autocomplete. These are the patterns that come up. Practise writing them rather than recognising them --- the gap between those two is much bigger than people expect.
@objectives:
- State time and space complexity for anything you write
- Write the standard patterns from memory
- Explain your approach before you start typing
- Know the Python-specific answers that save you time

## Complexity

#### Q30.1 — What are time and space complexity?
How much longer the code takes, and how much more memory it uses, as the input
gets bigger. Written in big-O, which describes the growth rather than the exact
number.

Always state both. Saying "this is O(n) time and O(1) space" unprompted scores
points.

#### Q30.2 — Give the complexity of common operations.
Looking up a list by position: instant. Searching an unsorted list: you have
to check everything. Searching a sorted list with binary search: halves each
step, so very fast. Dictionary lookup: instant on average. Sorting: n log n.

#### Q30.3 — Reverse a string.
`s[::-1]`. If they want the manual version, two pointers swapping inward from
both ends.

#### Q30.4 — Check a palindrome.
`s == s[::-1]`. The manual version uses two pointers from each end moving
inward, which uses no extra memory.

#### Q30.5 — Find duplicates in a list.
Walk through it keeping a set of what you've already seen. If something's
already in the set, it's a duplicate.

One pass, and the set lookup is instant.

#### Q30.6 — Two-sum.
For each number, check whether `target − number` is already in a dictionary of
what you've seen. If it is, you've found the pair. If not, record this number
and move on.

One pass instead of checking every pair against every other pair.

#### Q30.7 — FizzBuzz.
Loop from 1 to n. Divisible by 15 print FizzBuzz, by 3 print Fizz, by 5 print
Buzz, otherwise the number.

Check 15 first. Checking 3 first means you never reach the FizzBuzz case —
that's the whole trick of the question.

#### Q30.8 — Fibonacci — iterative, recursive, memoised?
Plain recursion recomputes the same values enormously many times — don't offer
it.

Iterative with two variables is the right answer: one pass, barely any memory.
Memoised recursion caches results and is also fine.

#### Q30.9 — Reverse a linked list.
Three pointers — previous, current, next. Walk along, pointing each node
backwards as you go.

One pass, no extra memory.

#### Q30.10 — Detect a cycle in a linked list.
Two pointers, one moving one step at a time and one moving two. If there's a
loop, the fast one eventually laps the slow one and they meet. If there isn't,
the fast one hits the end.

#### Q30.11 — Find the maximum subarray sum.
Walk through keeping a running total. Whenever the running total goes
negative, reset it to zero — because a negative prefix can only hurt. Track
the best total you've seen.

One pass.

#### Q30.12 — Sort a dictionary by value.
`sorted(d.items(), key=lambda kv: kv[1], reverse=True)`.

#### Q30.13 — Count word frequencies in a string.
`collections.Counter(text.lower().split())`, then `.most_common(n)`.

#### Q30.14 — Binary search — write it.
Two bounds, low and high. Look at the middle. If it's too small, move the low
bound up past it. If too big, move the high bound down. Repeat until they
cross.

Requires a sorted list — say that, because it's half the point.

#### Q30.15 — Explain recursion and its risk in Python.
A function calling itself, working towards a base case where it stops.

The risk: Python caps how deep it'll go at about a thousand levels. Go deeper
and it crashes. So for anything with large input, use a loop.

#### Q30.16 — Stack vs queue?
A stack is last in, first out — like a pile of plates. A queue is first in,
first out — like a queue of people.

In Python use `collections.deque` for both; it's fast at either end, whereas a
list is slow at the front.

#### Q30.17 — What is dynamic programming?
Breaking a problem into smaller versions of itself, and **saving the answers**
so you never solve the same sub-problem twice.

That's the whole idea. The Fibonacci example above is the simplest case.

#### Q30.18 — BFS vs DFS?
Breadth-first explores level by level using a queue — it finds the shortest
path in an unweighted graph.

Depth-first goes as deep as it can before backtracking, using a stack or
recursion.

#### Q30.19 — Find the k largest elements.
`heapq.nlargest(k, arr)`.

If they want the reasoning: keep a heap of size k, and for each new element,
if it's bigger than the smallest in the heap, swap it in. That way you never
sort the whole list.

#### Q30.20 — How would you process a 10 GB CSV on a laptop?
Read it in chunks rather than all at once, aggregating as you go. Only load
the columns you actually need, and use smaller number types where you can.

Or use a tool built for it — Polars or DuckDB will handle it directly without
you managing the chunking.

:::practice How to behave in the round
Say your approach out loud **before** you type. "I'll use a dictionary to
record what I've seen, so it's one pass instead of nested loops." Then write
it.

If you get stuck, say what you're stuck on. An interviewer will almost always
nudge you, and watching you reason is most of what they're assessing.
:::

:::recap
- State time and space complexity unprompted.
- Say your approach before you type it.
- Two pointers, a set of seen values, and a dictionary lookup cover a
  surprising share of these.
- Check 15 first in FizzBuzz.
- Binary search needs a sorted list — say so.
- Python's recursion depth is limited to about a thousand.
- For a huge CSV: chunks, fewer columns, or a different tool.
:::
