# Mastering Pointer Manipulation: Reversal
@short: Reversing a List
@subtitle: Four lines, traced to death, until they are obvious
@tier: core
@prereq: Chapters 24 to 26
@blurb: Reversing a linked list is the most-asked linked list question there is, and the most instructive. Four lines, three pointers, and every single one of them matters. This chapter traces the loop on a three-node list showing every variable at every moment, explains exactly why the saved pointer is necessary, demonstrates what each wrong ordering actually produces, and then does it recursively.
@objectives:
- Reverse a singly linked list iteratively, and explain every line
- State the value of `prev`, `curr` and `nextNode` at every point of every iteration
- Explain precisely why `nextNode` must be saved before `curr->next` is changed
- Predict what each incorrect ordering of the four lines produces
- Reverse a list recursively, and say what that costs
- Reverse only part of a list

## The problem

:::definition Reverse a linked list
Turn `10 -> 20 -> 30 -> nullptr` into `30 -> 20 -> 10 -> nullptr`, in place,
without allocating any new nodes.

"In place" means the nodes stay where they are in memory; only the `next`
pointers change. The node holding 10 is still the same object at the same
address — it is simply no longer first.
:::

@fig: rev_before_after | 160 | Before and after. No node moves in memory and no node is created; every `next` pointer is turned around, and `head` ends up naming what used to be the last node.

## Why this is harder than reversing an array

In Chapter 6 we reversed an array with two pointers swapping inwards. That
worked because an array can be read from either end.

A singly linked list cannot. You can only go forwards, and the moment you turn
a node's `next` pointer around, **you have destroyed your only route to the rest
of the list**.

:::insight The difficulty, stated exactly
To reverse the link from node $A$ to node $B$, you must set `A->next` to point
at whatever came *before* $A$.

But `A->next` is currently the only thing in the entire program that knows where
$B$ is. Overwrite it, and $B$ and everything after it is unreachable.

**Therefore: before you overwrite `A->next`, you must save it somewhere.**

That single sentence is the whole algorithm. The three pointers are: where you
came from (`prev`), where you are (`curr`), and where you were going
(`nextNode`).
:::

## The code

```cpp title="Iterative reversal — the four lines" frag
Node* prev = nullptr;
Node* curr = head;

while (curr != nullptr) {
    Node* nextNode = curr->next;   // 1. SAVE the rest of the list
    curr->next = prev;             // 2. REVERSE this node's pointer
    prev = curr;                   // 3. prev moves forward
    curr = nextNode;               // 4. curr moves forward
}

head = prev;                       // prev is now the last node we saw
```

Four lines inside the loop. Learn what each one is *for*, not what order they
come in — the order then becomes forced.

@fig: rev_three_pointers | 170 | The three pointers at the moment the loop body begins. `prev` is the part already reversed, `curr` is the node being turned around now, and `nextNode` is the part not yet touched. The loop advances all three by one node each iteration.

## The complete trace

List: `10 -> 20 -> 30 -> nullptr`. We show every variable at the start and end
of every iteration, exactly as asked.

### Before the loop

| Variable | Value |
|---|---|
| `prev` | `nullptr` |
| `curr` | node(10) |
| the list | `10 -> 20 -> 30 -> nullptr` |

`prev` starts as `nullptr` because the node that ends up **last** must have
`next == nullptr` — and the first node we process is exactly the node that will
end up last. Starting `prev` at `nullptr` makes that happen automatically.

### Iteration 1 — `curr` is node(10)

@tbl: Iteration 1 line by line. After line 2, node(10) points at nothing, which is correct: it is destined to be the last node.
| Line | Statement | `prev` | `curr` | `nextNode` | Links now |
|---|---|---|---|---|---|
| — | at entry | `nullptr` | 10 | — | `10->20->30->∅` |
| 1 | `nextNode = curr->next` | `nullptr` | 10 | **20** | `10->20->30->∅` |
| 2 | `curr->next = prev` | `nullptr` | 10 | 20 | `10->∅`, `20->30->∅` |
| 3 | `prev = curr` | **10** | 10 | 20 | unchanged |
| 4 | `curr = nextNode` | 10 | **20** | 20 | unchanged |

Look carefully at line 2. The list has just been **split in two**: node(10) now
points at `nullptr`, and `20 -> 30` is a separate chain. The *only* thing still
holding on to that second chain is `nextNode`.

@fig: rev_iteration1 | 178 | Iteration 1. After line 2 the list is temporarily in two pieces. `nextNode` is the only pointer to the second piece — which is precisely why it had to be saved on line 1.

### Iteration 2 — `curr` is node(20)

| Line | Statement | `prev` | `curr` | `nextNode` | Links now |
|---|---|---|---|---|---|
| — | at entry | 10 | 20 | 20 | `10->∅`, `20->30->∅` |
| 1 | `nextNode = curr->next` | 10 | 20 | **30** | unchanged |
| 2 | `curr->next = prev` | 10 | 20 | 30 | `20->10->∅`, `30->∅` |
| 3 | `prev = curr` | **20** | 20 | 30 | unchanged |
| 4 | `curr = nextNode` | 20 | **30** | 30 | unchanged |

The reversed portion is growing: `20 -> 10 -> nullptr`. `prev` always points at
the **head of the reversed portion so far**.

@fig: rev_iteration2 | 178 | Iteration 2. The reversed chain `20 -> 10` is being built behind `prev`, and the untouched remainder sits ahead of `curr`.

### Iteration 3 — `curr` is node(30)

| Line | Statement | `prev` | `curr` | `nextNode` | Links now |
|---|---|---|---|---|---|
| — | at entry | 20 | 30 | 30 | `20->10->∅`, `30->∅` |
| 1 | `nextNode = curr->next` | 20 | 30 | **`nullptr`** | unchanged |
| 2 | `curr->next = prev` | 20 | 30 | `nullptr` | `30->20->10->∅` |
| 3 | `prev = curr` | **30** | 30 | `nullptr` | unchanged |
| 4 | `curr = nextNode` | 30 | **`nullptr`** | `nullptr` | unchanged |

### The loop ends

`curr` is `nullptr`, so the condition fails. The list is fully reversed, and
`prev` points at node(30) — the new first node.

```cpp nonum frag
head = prev;      // without this line, head still names node(10),
                  // which is now the LAST node: head would be a one-node list
```

:::pitfall Forgetting `head = prev;`
This is the most common way to get reversal "nearly right". Every pointer is
correctly turned around, but `head` still names the old first node — which is
now the tail.

**The symptom:** the function appears to delete everything but one element.
Printing gives `10` instead of `30 -> 20 -> 10`. If you see that exact symptom,
you have forgotten the last line.
:::

@fig: rev_final | 160 | The end state. `curr` has fallen off the end, and `prev` has been left pointing at the last node processed — which is the new head.

## Why `nextNode` must be saved first

We have now seen it happen; here it is as an argument.

:::insight The necessity of line 1
At the moment line 2 runs, `curr->next` is overwritten.

Before that instant, the only pointer in the whole program to the unreversed
remainder of the list is `curr->next` itself. `prev` points backwards.
`head` points at the original first node, which is behind us. Nothing else
exists.

So overwriting `curr->next` without first copying it elsewhere makes the entire
remainder unreachable: a leak, and a reversal that produces a list of length 1.

`nextNode` is a lifeline thrown ahead before the rope behind is cut.
:::

@fig: rev_why_save | 170 | What happens without `nextNode`. Overwriting `curr->next` severs the only connection to the rest of the list; nodes 20 and 30 are still on the heap, with nothing pointing at them.

## What each wrong ordering actually produces

The brief way to learn this is to try it. Here is what each mistake gives you on
`10 -> 20 -> 30`.

### Mistake A: reverse before saving

```cpp nonum frag
curr->next = prev;              // BAD the rest of the list is now unreachable
Node* nextNode = curr->next;    //   this reads prev, not the next node!
prev = curr;
curr = nextNode;
```

After the first iteration, `nextNode` is `prev`, which is `nullptr`. So `curr`
becomes `nullptr`, the loop ends immediately, and `head = prev` gives a
**one-node list containing 10**. Nodes 20 and 30 are leaked.

**Symptom:** reversal returns a single element.

### Mistake B: advance `curr` before saving `prev`

```cpp nonum frag
Node* nextNode = curr->next;
curr->next = prev;
curr = nextNode;                // BAD curr moved on...
prev = curr;                    //   ...so prev is now the SAME node as curr
```

`prev` and `curr` end up equal every iteration, so each node's `next` is set to
itself. The result is a node pointing at itself: an infinite loop the next time
anything traverses the list.

**Symptom:** printing hangs, repeating one value forever.

### Mistake C: forget `head = prev`

Covered above. **Symptom:** the list becomes one element long.

@fig: rev_wrong_orders | 190 | The three wrong orderings and what each produces. Each failure has a distinctive symptom, which is worth knowing: the symptom tells you which line is wrong.

:::insight Why the correct order is forced
Read the four lines as a dependency chain:

- Line 2 **destroys** `curr->next`, so anything needing it must come first →
  line 1 before line 2.
- Line 3 needs `curr` to still be the current node, so it must come before line
  4 moves `curr`.
- Line 4 needs `nextNode`, which line 1 set.

There is exactly one order satisfying all three constraints. It is not arbitrary
and it is not worth memorising — derive it from "what does each line destroy,
and who still needs that?" and you will reconstruct it correctly every time,
including under interview pressure.
:::

## The complete program

```cpp title="Iterative reversal, with every edge case"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

void reverseList(Node*& head) {
    Node* prev = nullptr;
    Node* curr = head;
    while (curr != nullptr) {
        Node* nextNode = curr->next;   // 1. save the rest
        curr->next = prev;             // 2. reverse this link
        prev = curr;                   // 3. prev catches up
        curr = nextNode;               // 4. curr moves on
    }
    head = prev;                       // prev is the new head
}

Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* a = buildList({10, 20, 30});
    reverseList(a);  printList(a);  freeList(a);

    Node* b = buildList({1, 2, 3, 4, 5});
    reverseList(b);  printList(b);  freeList(b);

    Node* c = buildList({42});          // one node
    reverseList(c);  printList(c);  freeList(c);

    Node* d = nullptr;                  // empty
    reverseList(d);  printList(d);
    return 0;
}
```

```text nonum
30 -> 20 -> 10
5 -> 4 -> 3 -> 2 -> 1
42
(empty)
```

**Cost.** $O(n)$ time — each node is visited once — and $O(1)$ space: three
pointer variables, regardless of list length.

Both the empty list and the one-node list work with no special case. On the
empty list, `curr` starts `nullptr`, the loop never runs, and `head = prev`
sets `head` to `nullptr`, which it already was. That is the sign of a
well-shaped loop.

## Recursive reversal

The same job, expressed differently. Worth knowing because interviewers ask for
it, and because the trade-off is instructive.

@fig: rev_recursive | 180 | Recursive reversal. The recursion walks to the very end to find the new head, then reverses each link on the way back out — `head->next->next = head` turns the arrow around.

```cpp title="Recursive reversal"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* reverseRecursive(Node* head) {
    // Base case: an empty list, or a single node, is already reversed.
    if (head == nullptr || head->next == nullptr) return head;

    // Reverse everything AFTER head. newHead is the last node of the original.
    Node* newHead = reverseRecursive(head->next);

    head->next->next = head;    // the node after head now points BACK at head
    head->next = nullptr;       // head becomes the new last node

    return newHead;             // the same new head is passed all the way up
}

Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* a = buildList({10, 20, 30});
    a = reverseRecursive(a);  printList(a);  freeList(a);

    Node* b = buildList({1});
    b = reverseRecursive(b);  printList(b);  freeList(b);

    printList(reverseRecursive(nullptr));
    return 0;
}
```

```text nonum
30 -> 20 -> 10
1
(empty)
```

:::insight The two lines in the middle, understood
Suppose the list is `10 -> 20 -> 30` and we are at `head = node(10)`.

The recursive call reverses the tail, leaving `30 -> 20` and returning
`newHead = node(30)`. But node(10) still points at node(20), and node(20) now
points at `nullptr` — so the picture is:

$$30 \to 20 \to \emptyset \qquad\text{and}\qquad 10 \to 20$$

Now: `head->next` is node(20). So `head->next->next = head` sets node(20)'s
`next` to node(10) — attaching 10 onto the end of the reversed part, giving
$30 \to 20 \to 10 \to 20$. Almost right, but node(10) still points at node(20),
which is a cycle.

`head->next = nullptr` cuts that, leaving $30 \to 20 \to 10 \to \emptyset$.

Both lines are needed, and in that order: the second destroys the `head->next`
that the first depends on.
:::

@tbl: Iterative versus recursive reversal. The complexity is the same; the space is not, and on long lists the difference is a crash.
| | Iterative | Recursive |
|---|---|---|
| Time | $O(n)$ | $O(n)$ |
| Auxiliary space | $O(1)$ | $O(n)$ — one stack frame per node |
| Fails on long lists | no | yes — stack overflow around $10^5$ nodes |
| Readability | explicit, slightly fiddly | shorter, but the two middle lines are subtle |
| Which to give first | **this one** | mention it as an alternative |

Interviewers often ask for both. Give the iterative version, state that it is
$O(1)$ space, then offer the recursive one and **immediately note that it is
$O(n)$ stack**. Volunteering that limitation is the part they are listening for.

## Reversing part of a list

A common follow-up: reverse only the nodes from position $m$ to position $n$.

:::insight How to attack it
It is the same four-line loop, run only over the sub-range, plus bookkeeping to
stitch the reversed middle back in.

You need to remember two nodes before you start: the node **before** position
$m$ (call it `beforeStart`) and the node that is **at** position $m$ (which will
end up as the tail of the reversed section).

After reversing the middle:
- `beforeStart->next` must point at the new head of the reversed section;
- the old start's `next` must point at whatever followed position $n$.

The awkward case is $m = 1$, where there is no `beforeStart` — which is exactly
the problem a **dummy node** solves. Chapter 29 introduces it, and then this
problem becomes straightforward. Try it now, notice the awkwardness, and read
Chapter 29 with the motivation that discomfort gives you.
:::

:::recap Chapter 28 in seven lines
- Reversal turns every `next` around; no node moves and none is created.
- Three pointers: `prev` (reversed so far), `curr` (being turned now),
  `nextNode` (not yet touched).
- Save `nextNode` **first**, because line 2 destroys the only route to the rest
  of the list.
- `prev` starts at `nullptr` so the first node correctly becomes the last.
- Finish with `head = prev;` — forgetting it leaves a one-element list.
- Each wrong ordering has a distinct symptom: one element, or an infinite loop.
- Iterative is $O(1)$ space; recursive is $O(n)$ stack and overflows on long
  lists.
:::

:::exercise Practise
1. Trace the loop on `1 -> 2 -> 3 -> 4` yourself, writing all three variables
   after every line. Do not look at the tables.
2. What is the value of `prev` after the loop ends, for a list of length $n$?
   For an empty list?
3. Run the reversal on an empty list and a one-node list by hand. Confirm no
   special case is needed.
4. Implement Mistake A deliberately and run it. Does the output match the
   symptom described?
5. Write `reverseList` so it **returns** the new head instead of taking
   `Node*&`. Which signature do you prefer, and which does LeetCode use?
6. Reverse only the first $k$ nodes of a list, leaving the rest alone. What do
   you need to remember before you start?
7. Write a function that checks whether a list is a palindrome by reversing its
   second half. What does it cost, and what should it do to the list afterwards?
8. In `reverseRecursive`, what happens if you swap the two middle lines? Predict
   first, then test.
:::
