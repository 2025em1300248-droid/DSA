# What a Linked List Is, and Why It Exists
@short: The Linked List Idea
@subtitle: Giving up calculation to buy cheap insertion
@tier: foundation
@prereq: Chapters 21 and 22
@blurb: A linked list is what you get when you refuse to keep your data in one block. Every property it has — good and bad — follows from that one decision. This chapter builds the idea from the array's weakness, defines node, head, tail and nullptr precisely, draws the memory, and sets out the trade-off against arrays that the rest of Part VI depends on.
@objectives:
- Explain why linked lists exist, starting from what arrays are bad at
- Define node, data, next, head, tail and nullptr, and point to each in a diagram
- Explain why a linked list does not need contiguous memory
- State the cost of every basic linked list operation, and justify it
- Compare arrays and linked lists honestly, including where the list loses
- Recognise the three variants: singly, doubly and circular

## The array's weakness, restated

Chapter 6 established the cost table for arrays. Two rows were bad:

| Operation | Array | Why |
|---|---|---|
| Insert at the front | $O(n)$ | every element shifts right |
| Delete from the front | $O(n)$ | every element shifts left |

And the reason, exactly, was this: **the array promises that its elements sit
side by side with no gaps.** Keeping that promise after an insertion means
moving everything.

:::insight The question that produces the linked list
*"What if we simply stopped making that promise?"*

Let each value live wherever there happens to be room. Then inserting is just
creating a new value somewhere — nothing has to move, because nothing was
guaranteed to be anywhere in particular.

But now we have a new problem: if the values are scattered, **how do we find
the next one?**

The answer is the entire idea: **store the address of the next value alongside
each value.** Each piece carries a signpost to the one after it.
:::

@fig: ll_array_vs_list | 190 | The same five values, two ways. The array keeps a promise about position and pays for it on every insertion. The linked list keeps no promise about position and pays for it on every lookup.

## The node

:::definition Node
A **node** is one piece of a linked list. It holds two things:

- **data** — the value being stored;
- **next** — a pointer to the following node, or `nullptr` if there is none.

A node is an object on the heap. It knows nothing about the list as a whole: it
does not know its own position, how many nodes follow it, or what came before
it. All it knows is its value and where to go next.
:::

@fig: ll_node | 150 | One node, labelled. The left half holds the value; the right half holds the address of the next node. The arrow is a drawing of what that address means.

That is deliberately minimal, and the minimalism is the source of both the
strengths and the limitations. A node cannot tell you its index, because it does
not have one.

## The list

:::definition Head, tail and nullptr
The **head** is a pointer to the first node. It is not itself a node — it is a
variable, usually on the stack, holding the address of the first node.

**The head is the list.** If you lose it, every node becomes unreachable and the
whole list is leaked. That is why so much linked list code is careful never to
move `head` itself, and uses a separate `curr` to walk.

The **tail** is the last node — the one whose `next` is `nullptr`. Some
implementations also keep a `tail` pointer so that appending is $O(1)$ instead
of $O(n)$.

**`nullptr` in `next` means "nothing follows"**. It is how a traversal knows
when to stop, and it is the only thing distinguishing the end of the list from a
node that continues.

An **empty list** is `head == nullptr`. Not a list with one empty node — no
nodes at all.
:::

@fig: ll_anatomy | 180 | A complete three-node list, fully labelled. Four things to keep distinct: the head pointer (a variable), the nodes (heap objects), the data fields, and the next pointers — with `nullptr` marking the end.

:::pitfall `head` is a pointer, not a node
A persistent beginner confusion:

```cpp nonum skip
head->data        // OK  the value in the FIRST NODE
head.data         // BAD does not compile - head is a pointer
```

And a more subtle one: `head` and `head->next` are both `Node*`. They are the
same *type*. What differs is which node they point at. Once that clicks, every
traversal becomes obvious; until it does, nothing will.
:::

## Why contiguity is not needed

@fig: ll_scattered | 176 | The same list in memory. The nodes are at unrelated addresses, in an order that has nothing to do with the list order — node 3 sits before node 1 in memory. The `next` pointers are the only thing defining the sequence.

:::insight Order in memory is not order in the list
In an array, element 3 is *physically* after element 2. The order is the layout.

In a linked list, the order is the **pointers**, and nothing else. The second
node of the list could be at a lower address than the first; it makes no
difference whatsoever to how the list behaves.

This has two consequences, one good and one bad:

**Good.** New nodes can be created anywhere there is a free four-or-sixteen
bytes. You never need a large contiguous block, so a linked list cannot fail
because memory is fragmented — and inserting never disturbs anything.

**Bad.** There is no address formula. To reach node $i$ you must follow $i$
pointers. And each of those jumps is likely to be a **cache miss**, because the
processor cannot predict where the next node will be. This is why linked lists
are usually slower in practice than their complexity suggests — see Chapter 33.
:::

## Reaching the $i$-th element

@fig: ll_traverse_cost | 160 | Reaching index 3. The array computes an address; the list follows three pointers, each one a separate memory access to an unpredictable location.

This is the trade in its sharpest form:

| | Array | Linked list |
|---|---|---|
| Reach index $i$ | compute $B + i \times S$ | follow $i$ pointers |
| Cost | $O(1)$ | $O(i)$, so $O(n)$ |

Everything else about the two structures follows from this one difference and
its mirror image on insertion.

## The complete comparison

@tbl: Arrays versus singly linked lists. Read the whole table before concluding anything — the list wins two rows decisively and loses most of the others.
| Operation | Array / vector | Singly linked list |
|---|---|---|
| Access by index | $O(1)$ | $O(n)$ |
| Search for a value | $O(n)$ | $O(n)$ |
| Insert at the front | $O(n)$ | **$O(1)$** |
| Insert at the back | $O(1)$ amortised | $O(n)$, or $O(1)$ with a tail pointer |
| Insert after a node you already hold | $O(n)$ | **$O(1)$** |
| Delete from the front | $O(n)$ | **$O(1)$** |
| Delete a node you already hold | $O(n)$ | $O(n)$ singly; **$O(1)$** doubly |
| Memory per element | the value | the value + a pointer (often 2× or more) |
| Cache behaviour | excellent | poor |
| Needs one contiguous block | yes | no |
| Binary search possible | yes | no |

:::warning The row people misquote
"Insertion in a linked list is $O(1)$" is **only true if you already hold a
pointer to the node you are inserting after.**

If you have to *find* that position first, finding it is $O(n)$, and the total
is $O(n)$ — exactly the same as an array, which also does $O(n)$ work (shifting
instead of walking).

So the honest statement is: *a linked list is $O(1)$ for the **modification**
and $O(n)$ for the **navigation**; an array is $O(1)$ for the navigation and
$O(n)$ for the modification.* Which one wins depends entirely on whether you
already have a pointer.

Chapter 33 works this through properly. It is the single most common mistake in
interview answers about linked lists, and saying the precise version will
distinguish you.
:::

:::perf Why real code usually picks the array
Textbooks present this as a balanced trade. In practice, for most workloads,
`std::vector` wins — even for front insertions on small data — for three
reasons:

1. **Cache.** Walking an array reads memory sequentially, which the processor
   prefetches. Walking a list is a chain of dependent, unpredictable loads, and
   a cache miss costs roughly as much as a hundred arithmetic operations.
2. **Memory.** A node of one `int` costs 4 bytes of data plus 8 bytes of
   pointer plus allocator overhead — often 32 bytes for 4 bytes of payload.
3. **Allocation.** Every `new` has a cost; a vector amortises one allocation
   across many elements.

Linked lists genuinely win when: elements are large, you hold pointers directly
to nodes, you splice whole ranges between lists, or you need iterators that stay
valid across insertions. They are also the right *teaching* structure, because
pointer manipulation is the skill being built — and they remain a staple of
interviews.
:::

## The three variants

@fig: ll_variants | 190 | The three shapes. A singly linked list points forwards only; a doubly linked list points both ways at the cost of one more pointer per node; a circular list has no `nullptr` at all, because the last node points back to the first.

:::definition Singly, doubly and circular
**Singly linked.** Each node has one pointer, `next`. You can only move
forwards, and you can never get back. Smallest memory footprint. This is the
default, and Chapters 24 to 26 use it exclusively.

**Doubly linked.** Each node has `next` and `prev`. You can walk in either
direction, and you can delete a node you hold a pointer to in $O(1)$ — because
you can reach its predecessor. The cost is one extra pointer per node and twice
as many pointer updates on every operation. `std::list` is a doubly linked list.

**Circular.** The last node's `next` points back to the first instead of to
`nullptr`. Useful for round-robin scheduling and ring buffers. The hazard: every
loop condition that said `while (curr != nullptr)` now never terminates, and
must become `do { ... } while (curr != head)`.

Chapter 27 covers the latter two properly.
:::

## What is coming

| Chapter | What you will build |
|---|---|
| 24 | the `Node` struct, line by line; creating, connecting, traversing |
| 25 | insertion at the front, the back, a position, and around a given node |
| 26 | deletion of the first, the last, by position and by value, without leaking |
| 27 | doubly and circular lists |
| 28 | reversal — the single most important pointer exercise there is |
| 29–32 | the patterns, and sixteen interview problems |

:::recap Chapter 23 in six lines
- A linked list gives up contiguity, and with it the address formula, to make
  insertion and deletion cheap.
- A **node** holds data and a pointer to the next node; it knows nothing else.
- The **head** is a pointer to the first node, and losing it leaks the list.
  `head == nullptr` means empty.
- `nullptr` in `next` marks the end, and is how every traversal terminates.
- Order in the list is defined by pointers, not by addresses. Nodes may sit
  anywhere.
- "$O(1)$ insertion" is true only when you already hold the node to insert
  after. Finding it is $O(n)$.
:::

:::exercise Before you go on
1. Draw, by hand, a four-node list holding 5, 10, 15, 20 — including the head
   pointer and the `nullptr`. Label the data and next fields of each node.
2. In your drawing, what is `head->next->next->data`? What about
   `head->next->next->next->next`?
3. Why can a linked list not support binary search, even when the values are in
   sorted order?
4. An array of a million `int`s uses about 4 MB. Roughly how much would a singly
   linked list of the same million `int`s use on a 64-bit machine? Account for
   the pointer and some allocator overhead.
5. Give a concrete situation where a linked list is clearly the right choice,
   and one where it is clearly wrong. Justify each in one sentence.
6. The chapter says losing `head` leaks the whole list. Write the two lines of
   code that would cause that.
7. What goes wrong if you write `while (curr != nullptr)` to walk a **circular**
   list? What should it be instead?
:::
