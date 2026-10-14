# Insertion
@short: Insertion
@subtitle: Four places to insert, and the order of the pointer changes
@tier: core
@prereq: Chapter 24
@blurb: Every insertion is two or three pointer assignments, and the only thing that can go wrong is doing them in the wrong order — which silently loses the rest of the list. This chapter draws each insertion before coding it, states the order rule that makes all of them correct, and handles every empty-list and one-node case explicitly.
@objectives:
- Insert at the front, at the back, at a position, and after a given node
- State the order rule: connect the new node forwards before rewiring backwards
- Draw the before, during and after state of each insertion
- Handle the empty list and the single-node list in every case
- Explain why inserting at the front is $O(1)$ and at the back is $O(n)$
- Recognise the lost-list bug from its symptom

## The rule that makes every insertion correct

Before any code, here is the principle. It is short, it is the whole chapter,
and it is worth memorising.

:::insight The order rule
**Point the new node at the rest of the list *first*. Only then point the
previous node at the new node.**

Do it the other way round and the only pointer to the rest of the list is
overwritten, so the remainder is orphaned — unreachable and leaked.

In code: `node->next = X;` comes **before** `prev->next = node;` — always.
:::

@fig: ins_order_rule | 186 | The order rule. On the left, the new node is connected forwards first, so nothing is ever unreachable. On the right, rewiring backwards first overwrites the only pointer to the tail, and 20 and 30 are lost.

If you understand that diagram, every insertion in this chapter is a corollary.

## 1. Insert at the front

:::definition The operation
Make a new node the first node of the list. The old first node becomes the
second.
:::

@fig: ins_front | 170 | Inserting 5 at the front. Two assignments: the new node points at the old head, and then `head` points at the new node. The empty list needs no special case, because `head` being `nullptr` is exactly what the new node should point at.

```cpp title="Insert at the front — O(1)"
#include <iostream>
#include <vector>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// head is passed BY REFERENCE, because we are going to change it.
void insertFront(Node*& head, int value) {
    Node* node = new Node(value);
    node->next = head;      // 1. the new node points at the old first node
    head = node;            // 2. head now names the new node
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* head = nullptr;
    printList(head);
    insertFront(head, 30);
    insertFront(head, 20);
    insertFront(head, 10);
    printList(head);
    freeList(head);
    return 0;
}
```

```text nonum
(empty)
10 -> 20 -> 30
```

**Cost.** $O(1)$ time, $O(1)$ space. Nothing is traversed; two assignments.

:::pitfall `Node*& head` — the ampersand is not optional
```cpp nonum
void insertFront(Node* head, int value) {   // BAD no ampersand
    Node* node = new Node(value);
    node->next = head;
    head = node;                            // changes only the local copy
}
```
Without the `&`, `head` is a **copy** of the caller's pointer (Chapter 21). The
function builds the node, links it correctly, and then assigns to its own local
variable. The caller's `head` is unchanged, the new node is unreachable, and you
have a leak plus a list that did not grow.

The symptom is distinctive: the function appears to do nothing at all. Whenever
an insertion silently fails to happen, check for a missing `&`.

Two alternatives you will meet:
- `Node** head` — a pointer to the pointer, used in C and in some C++ code. Then
  you write `*head = node;`.
- `Node* insertFront(Node* head, int value)` — return the new head and make the
  caller write `head = insertFront(head, 10);`. This is common on LeetCode.

All three work. Pick one per codebase. This book uses `Node*&`.
:::

Notice that the empty list required no special case: when `head` is `nullptr`,
`node->next = head` sets the new node's `next` to `nullptr`, which is exactly
right for a one-node list.

## 2. Insert at the back

:::definition The operation
Append a new node after the current last node.
:::

@fig: ins_back | 180 | Appending 40. The list must be walked to find the last node — the one whose `next` is `nullptr` — and only then can the new node be attached. The empty list is the one genuine special case, because there is no last node to attach to.

```cpp title="Insert at the back — O(n) without a tail pointer"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

void insertBack(Node*& head, int value) {
    Node* node = new Node(value);
    if (head == nullptr) {       // SPECIAL CASE: the empty list
        head = node;
        return;
    }
    Node* curr = head;
    while (curr->next != nullptr)   // walk to the LAST node, not past it
        curr = curr->next;
    curr->next = node;
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* head = nullptr;
    insertBack(head, 10);            // into an empty list
    insertBack(head, 20);
    insertBack(head, 30);
    printList(head);
    freeList(head);
    return 0;
}
```

```text nonum
10 -> 20 -> 30
```

:::insight `curr->next != nullptr`, not `curr != nullptr`
This is the single most common error in `insertBack`.

`while (curr != nullptr)` walks until `curr` falls **off** the end, leaving
`curr` as `nullptr`. Then `curr->next = node;` dereferences null and crashes.

`while (curr->next != nullptr)` stops **on** the last node, which is exactly the
node you need to modify.

The general principle: **to modify a node, you must stop on it, not past it.**
That is also why deletion needs a `prev` pointer, and why the dummy-node trick
of Chapter 29 exists.
:::

**Cost.** $O(n)$ time because of the walk, $O(1)$ space.

:::perf Keeping a tail pointer
If you store a `tail` pointer alongside `head`, appending becomes:
```cpp nonum
void insertBackFast(Node*& head, Node*& tail, int value) {
    Node* node = new Node(value);
    if (tail == nullptr) head = tail = node;    // the list was empty
    else { tail->next = node; tail = node; }
}
```
$O(1)$ instead of $O(n)$. Building an $n$-element list goes from $O(n^2)$ to
$O(n)$ — the difference between five seconds and instant at $n = 100{,}000$.

The cost is that **every** operation must now maintain `tail`: deleting the last
node must move it back, and clearing the list must null it. A `tail` pointer
that is sometimes stale is worse than no `tail` pointer, because the bug appears
far from the function that caused it.
:::

## 3. Insert at a position

:::definition The operation
Insert a new node so that it ends up at index `pos` (0-based). `pos == 0` means
the front; `pos == length` means the back; anything larger is an error.
:::

@fig: ins_position | 190 | Inserting 25 at index 2. Walk to the node *before* the target position, then perform the same two assignments as always — new node forwards first, predecessor afterwards.

The key realisation: once you hold the node *before* the insertion point, this
is the same two-line operation as every other insertion. All the work is in the
walking.

```cpp title="Insert at a given position"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// Returns true on success, false if pos is out of range.
bool insertAt(Node*& head, int pos, int value) {
    if (pos < 0) return false;
    if (pos == 0) {                      // the front: head itself changes
        Node* node = new Node(value);
        node->next = head;
        head = node;
        return true;
    }
    Node* prev = head;                   // walk to the node BEFORE pos
    for (int i = 0; i < pos - 1; ++i) {
        if (prev == nullptr) return false;   // ran off the end
        prev = prev->next;
    }
    if (prev == nullptr) return false;    // pos is beyond the end

    Node* node = new Node(value);
    node->next = prev->next;             // 1. forwards first
    prev->next = node;                   // 2. then backwards
    return true;
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* head = nullptr;
    insertAt(head, 0, 10);
    insertAt(head, 1, 20);
    insertAt(head, 2, 30);
    printList(head);

    insertAt(head, 1, 15);               // into the middle
    printList(head);

    insertAt(head, 0, 5);                // at the front
    printList(head);

    insertAt(head, 5, 40);               // at the very end
    printList(head);

    std::cout << "pos 99: " << (insertAt(head, 99, 1) ? "ok" : "rejected") << "\n";
    std::cout << "pos -1: " << (insertAt(head, -1, 1) ? "ok" : "rejected") << "\n";
    freeList(head);
    return 0;
}
```

```text nonum
10 -> 20 -> 30
10 -> 15 -> 20 -> 30
5 -> 10 -> 15 -> 20 -> 30
5 -> 10 -> 15 -> 20 -> 30 -> 40
pos 99: rejected
pos -1: rejected
```

:::pitfall The three range checks
Look at how much of that function is validation rather than work. That is
normal and correct.

**`pos == 0` is separate** because it is the only case that changes `head`
itself. Chapter 29's dummy-node trick exists precisely to remove this split.

**`prev == nullptr` inside the loop** catches a `pos` larger than the list.
Without it, the walk dereferences `nullptr`.

**`prev == nullptr` after the loop** catches `pos` exactly one past the end of
the walk. Both checks are needed; neither covers the other.

Beginners write the happy path and stop. The validation is what makes it work
on inputs you did not think of, and an interviewer is watching for exactly that.
:::

**Cost.** $O(pos)$ to walk, so $O(n)$ worst case; $O(1)$ space. Inserting at
index 0 is $O(1)$.

## 4. Insert after a given node

:::definition The operation
You already hold a pointer to some node. Insert a new node directly after it.
:::

@fig: ins_after | 164 | Inserting after a node you already hold. No walking at all — two assignments, $O(1)$. This is the case where linked lists genuinely beat arrays, because an array would still shift everything.

```cpp title="Insert after a node — genuinely O(1)"
void insertAfter(Node* node, int value) {
    if (node == nullptr) return;         // nothing to insert after
    Node* fresh = new Node(value);
    fresh->next = node->next;            // 1. forwards first
    node->next = fresh;                  // 2. then backwards
}
```

Two assignments, no traversal, no `head` involved. $O(1)$ time and space.

:::insight This is the whole advantage, and its limit
**This** is what people mean by "linked lists have $O(1)$ insertion". Not
insertion at an arbitrary index — insertion *given a pointer*.

In an array, inserting after a known index still costs $O(n)$, because every
later element must shift. Here it is two writes regardless of list length.

But notice what the function cannot do: insert *before* a node. To do that you
would need the node's predecessor, and a singly linked list cannot go backwards.
That limitation is exactly what a doubly linked list removes, at the cost of one
extra pointer per node — Chapter 27.

**Insert-before, in a singly linked list, with only the node:** there is a
famous trick. Insert *after* the node, then **swap the two nodes' data**. The
structure ends up right, and no predecessor was needed. It works only when
copying the data is cheap and legitimate. The same trick solves "delete a node
given only that node" in Chapter 31.
:::

## All four, compared

@tbl: The four insertions. The pattern is clear: the two assignments never change; what changes is how much walking you must do to find the node to attach to.
| Insertion | Walk needed | Time | Changes `head`? | Special cases |
|---|---|---|---|---|
| At the front | none | $O(1)$ | yes | none — empty works naturally |
| At the back | to the last node | $O(n)$ | only if empty | the empty list |
| At position $p$ | $p-1$ steps | $O(p)$, $O(n)$ worst | only if $p = 0$ | $p = 0$; $p$ out of range |
| After a known node | none | $O(1)$ | no | a null node pointer |
| At the back, with a `tail` | none | $O(1)$ | only if empty | `tail` must be maintained everywhere |

## The symptom of getting the order wrong

:::warning What a lost list looks like
If you write the two assignments backwards:
```cpp nonum frag
prev->next = node;          // BAD backwards first
node->next = prev->next;    // now this is node itself!
```
the second line reads `prev->next`, which you have just set to `node` — so the
new node points at **itself**. The list now has a one-node cycle, and everything
that used to follow `prev` is unreachable.

The symptom: printing the list hangs forever, repeating the same value. If a
traversal ever fails to terminate, suspect a self-referential or cyclic `next`
pointer, and check the order of your assignments first.

Chapter 30 turns cycle detection into a problem of its own. Here it is a bug.
:::

:::recap Chapter 25 in six lines
- **Connect the new node forwards first, then rewire the predecessor.** Always.
- Front insertion is $O(1)$ and needs `Node*&` (or a returned head).
- Back insertion is $O(n)$ without a `tail` pointer, and $O(1)$ with one.
- Stop **on** the node you must modify (`curr->next != nullptr`), not past it.
- Insert-at-position is the same two lines, plus a walk and three range checks.
- Insert-after-a-known-node is the genuinely $O(1)$ case, and is the real
  advantage of a linked list.
:::

:::exercise Practise
1. Draw the before and after state for inserting 25 at index 2 of
   `10 -> 20 -> 30`. Number the pointer changes in the order they must happen.
2. Write `insertBack` keeping a `tail` pointer. Which other functions in this
   chapter would then need changing, and why?
3. Write `insertSorted(Node*& head, int value)` that inserts into a sorted list
   so it stays sorted. Which case needs `head` to change?
4. What happens if `insertAt` is called with `pos` equal to the list's length?
   Should it succeed? Check your implementation agrees with your answer.
5. Rewrite `insertFront` using `Node** head` instead of `Node*& head`. Which do
   you find clearer, and why do you think C code uses the first form?
6. Explain what `insertAfter(nullptr, 5)` should do, and what the version
   without the null check would do.
7. Implement insert-**before** given only a pointer to a node, using the
   data-swap trick. When is this trick unacceptable?
8. Build a list of 100,000 elements with `insertBack` and no `tail` pointer, and
   time it. Then add a `tail` pointer and time it again. Explain the ratio you
   observe.
:::
