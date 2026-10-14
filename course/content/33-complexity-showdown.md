# Arrays versus Linked Lists: The Complete Picture
@short: The Complexity Showdown
@subtitle: Every operation, every condition, stated precisely
@tier: reference
@prereq: Parts II and VI
@blurb: This is the chapter to re-read before an interview. It states the cost of every operation on both structures **with the conditions attached** — because "linked list insertion is $O(1)$" is false as usually quoted, and knowing exactly when it is true is what the question is testing. It ends with the part the complexity tables hide: what actually happens on real hardware.
@objectives:
- State the cost of every operation on both structures, with its precondition
- Explain *why* array indexing is $O(1)$ and list indexing is $O(n)$
- Give the precise conditions under which linked list insertion is $O(1)$
- Separate the cost of **navigation** from the cost of **modification**
- Explain why arrays usually win in practice despite the tables
- Choose the right structure for a stated workload, and defend it

## The master table

@tbl: Every operation, both structures, with the condition each cost depends on. The condition column is the one most people omit, and it is where the real answer lives.
| Operation | Array / vector | Singly linked | Doubly linked | Condition |
|---|---|---|---|---|
| Access by index $i$ | $O(1)$ | $O(i)$ | $O(i)$ | — |
| Access the first element | $O(1)$ | $O(1)$ | $O(1)$ | — |
| Access the last element | $O(1)$ | $O(n)$ | $O(1)$ | list needs a tail pointer |
| Search (unsorted) | $O(n)$ | $O(n)$ | $O(n)$ | — |
| Search (sorted) | $O(\log n)$ | $O(n)$ | $O(n)$ | binary search needs random access |
| Insert at the front | $O(n)$ | $O(1)$ | $O(1)$ | — |
| Insert at the back | $O(1)$ amortised | $O(n)$ / $O(1)$ | $O(1)$ | $O(1)$ only with a tail pointer |
| Insert at index $i$ | $O(n - i)$ | $O(i)$ | $O(i)$ | both are $O(n)$ in the worst case |
| Insert given a pointer/iterator | $O(n)$ | $O(1)$ | $O(1)$ | **the list's real advantage** |
| Delete the first element | $O(n)$ | $O(1)$ | $O(1)$ | — |
| Delete the last element | $O(1)$ | $O(n)$ | $O(1)$ | doubly needs a tail pointer |
| Delete at index $i$ | $O(n - i)$ | $O(i)$ | $O(i)$ | — |
| Delete given a pointer | $O(n)$ | $O(n)$ | $O(1)$ | singly must find the predecessor |
| Traverse everything | $O(n)$ | $O(n)$ | $O(n)$ | very different constants |
| Splice a whole range | $O(n)$ | $O(1)$ | $O(1)$ | given pointers to both ends |
| Memory per `int` element | 4 bytes | ~16–32 bytes | ~24–40 bytes | including allocator overhead |
| Needs contiguous memory | yes | no | no | — |
| Iterators survive insertion | no | yes | yes | vectors reallocate |

Read the table twice. The first reading says "they trade off". The second
reading, with the condition column, says something sharper — which is the next
section.

## The single idea behind all of it

@fig: cmp_navigate_modify | 180 | Navigation versus modification. An array pays nothing to navigate and everything to modify; a linked list pays everything to navigate and nothing to modify. Each operation's true cost is the sum of the two.

:::insight Separate navigation from modification
Every operation is really **two** operations: *get to the right place*, then *do
the thing*.

| | Navigate to position $i$ | Modify once there |
|---|---|---|
| **Array** | $O(1)$ — compute the address | $O(n)$ — shift everything after |
| **Linked list** | $O(n)$ — follow $i$ pointers | $O(1)$ — two pointer writes |

Now every row of the master table falls out of this one table:

- *Insert at index $i$* needs both, so it is $O(n)$ for **both** structures. The
  array walks no distance and shifts $n-i$ elements; the list walks $i$ nodes and
  shifts nothing. Same complexity, opposite work.
- *Insert given a pointer* needs only the modification, so the list is $O(1)$
  and the array is still $O(n)$. **This is the list's genuine advantage, and it
  is the only row where it wins outright.**
- *Access by index* needs only the navigation, so the array is $O(1)$ and the
  list is $O(n)$.

If you remember one thing from this chapter, remember this table rather than the
big one.
:::

## Why array indexing is O(1): the exact reason

Three facts, and the conclusion follows:

1. **Elements are the same type**, so each occupies the same number of bytes $S$.
2. **They are contiguous**, with no gaps.
3. Therefore element $i$ begins at $B + i \times S$, where $B$ is the base.

That expression is one multiplication and one addition, regardless of $i$ and
regardless of $n$. The processor performs it in a single instruction — on x86,
the address mode `[base + index*4]` does it for free as part of the load.

:::insight Remove any of the three facts and it breaks
- **Different sizes?** Then element $i$'s offset depends on the sizes of
  elements $0$ through $i-1$, and you must examine them: $O(i)$.
- **Gaps?** Then the formula gives a wrong address.
- **Scattered?** Then there is no formula at all — which is exactly the linked
  list case.

A linked list fails all three. Its "elements" are nodes of equal size, but they
are not contiguous and not in order, so no arithmetic can find them. The only
route to node $i$ is through nodes $0 \dots i-1$, and each step is one
dereference: $O(i)$, and $O(n)$ in the worst case.
:::

@fig: cmp_why_o1 | 172 | Why one is a calculation and the other is a walk. The array's three guarantees produce an address formula; the linked list offers no guarantee about location, so it offers no formula.

## The claim people get wrong

:::warning "Linked lists have O(1) insertion" — as usually said, this is false
What is true: **given a pointer to the node you are inserting after**, insertion
is $O(1)$.

What is false: inserting at an arbitrary position is $O(1)$. Finding that
position is $O(i)$, and $O(i) + O(1) = O(i)$.

So for "insert at index 500 of a 1000-element structure":
- **Array:** 0 steps to navigate, 500 elements shifted. $O(n)$.
- **List:** 500 steps to navigate, 2 pointer writes. $O(n)$.

**Both are $O(n)$.** The list is not faster here. In fact it is usually *slower*,
because 500 pointer dereferences across scattered memory cost far more than 500
contiguous `memmove`d integers — a point the next section makes concrete.
:::

:::interview The precise sentence
When asked to compare the two, say this:

> *"A linked list gives $O(1)$ insertion and deletion **when you already hold a
> pointer to the position**. Getting that pointer is $O(n)$ unless you obtained
> it some other way — from an iterator you were keeping, or from a hash map.
> An array gives $O(1)$ access by index but $O(n)$ modification. So the real
> question is whether the workload supplies you with positions, or asks you to
> find them."*

Then give the examples where a list genuinely wins:
- **LRU cache** — a hash map hands you the node pointer; you unlink it in
  $O(1)$. An array could not.
- **`std::list::splice`** — moving a range of any length between lists is four
  pointer writes, because nothing is copied.
- **Stable iterators** — pointers into a list survive insertions; pointers into
  a vector do not.
:::

## What the tables hide: real hardware

@fig: cmp_cache | 184 | Why the same complexity is not the same speed. Traversing an array reads consecutive memory, which the processor prefetches in 64-byte lines. Traversing a list is a chain of dependent jumps to unpredictable addresses, and each one may stall for hundreds of cycles.

:::perf The constant factor is roughly 10×, and it is not a detail
Both traversals are $O(n)$. On real hardware they are not close.

**Array traversal.** Elements are 4 bytes and a cache line is 64, so one memory
fetch delivers 16 elements. The prefetcher sees the sequential pattern and loads
the next line before you ask. Effective cost: a fraction of a cycle per element.

**List traversal.** Each node is somewhere else, so each step is a fresh fetch,
and — worse — the address of the *next* fetch is not known until the current one
completes. The loads cannot be overlapped. This is a **dependent load chain**,
and it is the slowest pattern in computing. A cache miss costs roughly 100–300
cycles; the arithmetic it is waiting for costs 1.

Add the memory: a node holding one `int` typically occupies 32 bytes once
allocator bookkeeping is counted — **eight times** the payload. Eight times the
memory means one-eighth of your data fits in cache.

**The practical consequence:** for small elements, `std::vector` beats
`std::list` at almost everything, *including* operations where the complexity
table says the list should win. Inserting at the front of a 1,000-element vector
means shifting 4 KB, which `memmove` does in a few hundred nanoseconds. Walking
1,000 list nodes to find a position costs more than that on its own.
:::

:::note When should you actually use `std::list`?
Rarely, and for specific reasons:

- Elements are **large or expensive to move**, so shifting them is genuinely
  costly.
- You **already hold iterators** to the positions you modify — the LRU-cache
  pattern.
- You need **iterator stability** across insertions and deletions.
- You **splice** whole ranges between containers frequently.

Otherwise: `std::vector`, even when the complexity table suggests otherwise.
Measure if it matters.

None of this diminishes the value of learning linked lists. They are the
foundation of trees, graphs, hash table buckets and allocators; they are the
standard vehicle for testing pointer skill; and they are the clearest possible
illustration of the trade-off this chapter is about.
:::

## Choosing, for a stated workload

@tbl: Workload-driven choice. In an interview, ask which of these the problem is before choosing — the question is often precisely that.
| Workload | Choose | Why |
|---|---|---|
| Random access by index, data mostly read | **array** | $O(1)$ access; cache-friendly |
| Append and iterate, nothing else | **array** | amortised $O(1)$ append, fast scans |
| Binary search needed | **array** | random access is a precondition |
| Insert and delete at the front only | either | list $O(1)$; a deque is better still |
| Insert and delete at **held** positions | **list** | $O(1)$ modification, no shifting |
| LRU cache | **hash map + doubly linked list** | map finds the node, list unlinks in $O(1)$ |
| Stable references across edits | **list** | vectors reallocate and invalidate |
| Huge elements, frequent reordering | **list** | relinking beats moving |
| Memory is tight | **array** | no per-element pointer overhead |
| Splicing ranges between containers | **list** | $O(1)$ regardless of range length |

## The questions to ask before choosing

:::checklist A decision procedure
1. **Do I need access by index?** Yes → array. Binary search also means yes.
2. **Where do insertions and deletions happen?** Only at the end → array. Only
   at the front → either, and a deque is better than both. Anywhere → ask
   question 3.
3. **Do I already hold a pointer to the position?** Yes → list genuinely wins.
   No → both are $O(n)$, so pick the array for its constant factor.
4. **Do references have to stay valid?** Yes → list.
5. **How big is an element?** Small → array, because overhead and cache dominate.
   Large → the list's no-copy advantage starts to matter.
6. **How large is $n$?** Below a few hundred, the constant factor decides
   everything and the array almost always wins.
:::

:::recap Chapter 33 in six lines
- Every operation is **navigate** then **modify**. Arrays are $O(1)$/$O(n)$;
  lists are $O(n)$/$O(1)$.
- Array indexing is $O(1)$ because equal sizes plus contiguity give an address
  formula. Lists have none of the three preconditions.
- "Lists have $O(1)$ insertion" is only true **given a pointer to the position**.
  At an arbitrary index, both structures are $O(n)$.
- Binary search needs random access, so it is an array algorithm — full stop.
- The constant factor is about 10×, from cache behaviour and per-node overhead.
  Equal complexity is not equal speed.
- In production, prefer `std::vector` unless you can name the specific reason
  not to.
:::

:::exercise Practise
1. Fill in the master table from memory, including the condition column. Check
   it against the chapter.
2. For each of these, say which structure wins and why: appending a million
   integers; deleting the front element a million times; finding the median;
   maintaining a playlist where tracks are dragged around by the user.
3. Why can a linked list not support binary search, even when sorted? Answer in
   terms of navigation cost, not in terms of "it has no indices".
4. Describe an LRU cache's two data structures and state the cost of `get` and
   `put`. Which part does each structure contribute?
5. A colleague says "I used a list because I insert in the middle a lot".
   What is the one question you should ask them?
6. Estimate the memory used by a `std::vector<int>` and a `std::list<int>`, each
   holding a million elements. What is the ratio?
7. Both traversals are $O(n)$. Explain, in terms of the processor, why one may
   be ten times slower.
8. Give a workload where the list genuinely wins on wall-clock time, and one
   where the complexity table says it should win but it does not.
:::
