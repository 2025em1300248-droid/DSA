# Doubly and Circular Linked Lists
@short: Doubly and Circular
@subtitle: One more pointer, and one missing nullptr
@tier: core
@prereq: Chapter 26
@blurb: Two variations, each solving one specific weakness of the singly linked list. A doubly linked list adds a `prev` pointer, which makes backwards traversal possible and deletion of a held node $O(1)$. A circular list removes the final `nullptr`, which suits anything that goes round. Both change every loop condition you have learned, and this chapter is mostly about getting those right.
@objectives:
- Define a doubly linked node and keep both pointers consistent
- Insert and delete in a doubly linked list, and count the pointer updates
- Explain why deleting a held node is $O(1)$ doubly and $O(n)$ singly
- Write the correct traversal loop for a circular list
- Build a circular doubly linked list, which is what `std::list` actually is
- Decide which variant a problem needs

## The doubly linked node

```cpp title="A node that points both ways" frag
struct DNode {
    int data;
    DNode* next;
    DNode* prev;
    DNode(int value) { data = value; next = nullptr; prev = nullptr; }
};
```

@fig: dll_anatomy | 180 | A doubly linked list. Every link exists twice, once in each direction, and the invariant is that they always agree: if `a->next == b` then `b->prev == a`. The first node's `prev` and the last node's `next` are both `nullptr`.

:::definition The doubly linked invariant
For every pair of adjacent nodes $a$ and $b$:

$$a \rightarrow \text{next} = b \quad\Leftrightarrow\quad b \rightarrow \text{prev} = a$$

Every operation must leave this true. That is the entire difficulty of a doubly
linked list: there are twice as many pointers to update, and updating only one
side produces a list that traverses correctly forwards and corrupts going
backwards — a bug that can hide for a long time.

**Check both directions when you test.** Print the list forwards and backwards
and compare; if they are not mirror images, an update was missed.
:::

## Insertion in a doubly linked list

@fig: dll_insert | 190 | Inserting into a doubly linked list. Four pointers change, not two: the new node's `next` and `prev`, the predecessor's `next`, and the successor's `prev`. The order still follows the rule — connect the new node to its neighbours first.

```cpp title="Insert at the front and after a node"
#include <iostream>

struct DNode {
    int data;
    DNode* next;
    DNode* prev;
    DNode(int value) { data = value; next = nullptr; prev = nullptr; }
};

void insertFront(DNode*& head, int value) {
    DNode* node = new DNode(value);
    node->next = head;                       // 1. new node forwards
    if (head != nullptr) head->prev = node;  // 2. old head points back
    head = node;                             // 3. head moves
    // node->prev stays nullptr - it is the first node
}

// Insert after a node you already hold. O(1), no walking.
void insertAfter(DNode* node, int value) {
    if (node == nullptr) return;
    DNode* fresh = new DNode(value);
    fresh->next = node->next;                // 1. forwards
    fresh->prev = node;                       // 2. backwards
    if (node->next != nullptr)
        node->next->prev = fresh;             // 3. the successor points back
    node->next = fresh;                       // 4. the predecessor points on
}

void printForward(DNode* head) {
    for (DNode* c = head; c; c = c->next) std::cout << c->data << (c->next ? " <-> " : "\n");
    if (!head) std::cout << "(empty)\n";
}

void printBackward(DNode* head) {
    if (head == nullptr) { std::cout << "(empty)\n"; return; }
    DNode* tail = head;
    while (tail->next != nullptr) tail = tail->next;      // walk to the end
    for (DNode* c = tail; c; c = c->prev) std::cout << c->data << (c->prev ? " <-> " : "\n");
}

void freeList(DNode* head) { while (head) { DNode* d = head; head = head->next; delete d; } }

int main() {
    DNode* head = nullptr;
    insertFront(head, 30);
    insertFront(head, 20);
    insertFront(head, 10);
    printForward(head);
    printBackward(head);                     // must be the exact mirror

    insertAfter(head->next, 25);             // after the node holding 20
    printForward(head);
    printBackward(head);
    freeList(head);
    return 0;
}
```

```text nonum
10 <-> 20 <-> 30
30 <-> 20 <-> 10
10 <-> 20 <-> 25 <-> 30
30 <-> 25 <-> 20 <-> 10
```

Printing both directions and checking they mirror is the test that catches a
missed `prev` update. Make it a habit.

## Deletion: the reason doubly linked lists exist

@fig: dll_delete | 180 | Deleting a node you hold, in $O(1)$. Because the node knows its own predecessor, you can reroute both neighbours around it without walking anywhere. In a singly linked list this is $O(n)$, because finding the predecessor means starting from the head.

```cpp title="Delete a node you already hold — O(1)"
#include <iostream>

struct DNode {
    int data;
    DNode* next;
    DNode* prev;
    DNode(int value) { data = value; next = nullptr; prev = nullptr; }
};

// Unlink and free `node`. O(1) - no traversal at all.
void deleteNode(DNode*& head, DNode* node) {
    if (node == nullptr) return;

    if (node->prev != nullptr) node->prev->next = node->next;
    else                       head = node->next;        // it was the head

    if (node->next != nullptr) node->next->prev = node->prev;
    // if it was the tail, there is nothing after it to fix

    delete node;
}

DNode* buildD(std::initializer_list<int> vs) {
    DNode* head = nullptr; DNode* tail = nullptr;
    for (int v : vs) {
        DNode* n = new DNode(v);
        if (!head) head = tail = n;
        else { tail->next = n; n->prev = tail; tail = n; }
    }
    return head;
}
void printForward(DNode* head) {
    for (DNode* c = head; c; c = c->next) std::cout << c->data << (c->next ? " <-> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
void freeList(DNode* head) { while (head) { DNode* d = head; head = head->next; delete d; } }

int main() {
    DNode* head = buildD({10, 20, 30, 40});
    deleteNode(head, head->next);            // remove 20, a middle node
    printForward(head);
    deleteNode(head, head);                  // remove the head
    printForward(head);
    DNode* last = head; while (last->next) last = last->next;
    deleteNode(head, last);                  // remove the tail
    printForward(head);
    deleteNode(head, head);                  // the only node left
    printForward(head);
    freeList(head);
    return 0;
}
```

```text nonum
10 <-> 30 <-> 40
30 <-> 40
30
(empty)
```

:::insight The one genuine superpower
Compare the two signatures:

```cpp nonum skip
void deleteNode(Node*&  head, Node*  node);   // singly: must FIND the predecessor, O(n)
void deleteNode(DNode*& head, DNode* node);   // doubly: node->prev is right there, O(1)
```

That is the whole justification for the extra pointer. And it is not academic —
it is exactly what an **LRU cache** needs: when an entry is used, you must move
its node to the front, which means deleting it from the middle in $O(1)$. A hash
map gives you the node pointer; a doubly linked list lets you unlink it
immediately. Neither structure can do it alone.

If you ever wondered why `std::list` is doubly linked despite the memory cost,
this is why: `erase(iterator)` is $O(1)$, and it could not be otherwise.
:::

:::pitfall The two-branch shape
Both branches in `deleteNode` are necessary and are easy to half-write:

- `node->prev == nullptr` means the node is the **head**, so `head` must move.
- `node->next == nullptr` means the node is the **tail**, so there is no
  successor to fix.

A node that is both — the only node in the list — hits both branches, and the
list correctly becomes empty. Test that case; it is the one people forget.
:::

## Circular linked lists

:::definition Circular linked list
A list in which the last node's `next` points back to the **first** node instead
of to `nullptr`.

There is no end. Every node has a successor, and traversal must be stopped by a
condition other than reaching null.
:::

@fig: cll_shape | 180 | A circular list. Because the last node points back to the head, `while (curr != nullptr)` never terminates. The correct shape is a `do ... while (curr != head)`, which visits every node exactly once.

:::warning Every loop condition changes
```cpp nonum skip
while (curr != nullptr) { visit(curr); curr = curr->next; }   // BAD runs forever
```
There is no `nullptr` to find. The program hangs, or prints the same values
until you stop it.

The correct form is:
```cpp nonum frag
if (head != nullptr) {
    Node* walker = head;
    do {
        process(walker->data);
        walker = walker->next;
    } while (walker != head);        // stop when we come back round
}
```
A `do ... while` is required rather than a `while`, because `curr == head` is
true at the very start — a plain `while` would process nothing. And the
`if (head != nullptr)` is required because a `do` body always runs once, which
would dereference null on an empty list.
:::

```cpp title="A circular list, traversed correctly"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// Build a circular list; returns the head.
Node* buildCircular(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) {
        Node* n = new Node(v);
        if (!head) head = tail = n;
        else { tail->next = n; tail = n; }
    }
    if (tail) tail->next = head;            // close the ring
    return head;
}

void printCircular(Node* head) {
    if (head == nullptr) { std::cout << "(empty)\n"; return; }
    Node* curr = head;
    do {
        std::cout << curr->data << " ";
        curr = curr->next;
    } while (curr != head);
    std::cout << "\n";
}

int countCircular(Node* head) {
    if (head == nullptr) return 0;
    int n = 0;
    Node* curr = head;
    do { ++n; curr = curr->next; } while (curr != head);
    return n;
}

void freeCircular(Node* head) {
    if (head == nullptr) return;
    Node* curr = head->next;
    while (curr != head) {                  // free everything but the head
        Node* doomed = curr;
        curr = curr->next;
        delete doomed;
    }
    delete head;                            // then the head itself
}

int main() {
    Node* head = buildCircular({10, 20, 30});
    printCircular(head);
    std::cout << "count = " << countCircular(head) << "\n";

    // Walking twice round shows there is no end.
    Node* c = head;
    for (int i = 0; i < 7; ++i) { std::cout << c->data << " "; c = c->next; }
    std::cout << "\n";

    freeCircular(head);
    printCircular(nullptr);
    return 0;
}
```

```text nonum
10 20 30 
count = 3
10 20 30 10 20 30 10 
(empty)
```

Note `freeCircular`: breaking the ring correctly requires freeing everything
*except* the head first, then the head. Using the ordinary `freeList` loop on a
circular list would run forever, freeing nodes it had already freed.

:::insight Where circular lists are genuinely used
**Round-robin scheduling.** Each process gets a time slice; when the last one
finishes, you are already back at the first with no special case.

**Ring buffers.** A fixed set of slots reused endlessly — audio buffers,
network packet queues, replay buffers in reinforcement learning. (Though these
are usually implemented as a circular *array*, which gets the ring behaviour with
array cache performance.)

**The Josephus problem**, and anything else where you repeatedly go round
eliminating members.

**`std::list`** is a *circular doubly linked* list with one sentinel node. The
sentinel's `next` is the first element and its `prev` is the last, which means
`begin()`, `end()`, insertion and deletion all work with no null checks and no
special cases anywhere. It is the dummy-node trick of Chapter 29, taken to its
conclusion.
:::

## Choosing a variant

@tbl: The three variants compared. Note the last row: the extra memory of a doubly linked list is not small when the payload is a single `int`.
| | Singly | Doubly | Circular (singly) |
|---|---|---|---|
| Pointers per node | 1 | 2 | 1 |
| Traverse backwards | no | yes | no (but you can loop round) |
| Delete a held node | $O(n)$ | **$O(1)$** | $O(n)$ |
| Delete the last node | $O(n)$ | $O(1)$ with a tail | $O(n)$ |
| End-of-list test | `== nullptr` | `== nullptr` | `== head` |
| Empty-list test | `head == nullptr` | `head == nullptr` | `head == nullptr` |
| Memory for one `int` | 4 + 8 = 12 bytes | 4 + 16 = 20 bytes | 4 + 8 = 12 bytes |
| Typical use | the default; interviews | LRU caches, `std::list`, editors | round-robin, ring buffers |

:::recap Chapter 27 in six lines
- A doubly linked node adds `prev`, and the invariant is
  `a->next == b` $\Leftrightarrow$ `b->prev == a`.
- Doubly linked insertion and deletion update **four** pointers, not two. Test
  by printing both directions.
- Deleting a node you hold is $O(1)$ doubly and $O(n)$ singly. That single fact
  is why LRU caches and `std::list` use it.
- A circular list has no `nullptr`, so `while (curr != nullptr)` hangs. Use
  `do { ... } while (curr != head)`.
- Freeing a circular list must break the ring, or it frees nodes twice.
- `std::list` is a circular doubly linked list with a sentinel, which is how it
  avoids special cases entirely.
:::

:::exercise Practise
1. Draw a three-node doubly linked list and label all six pointers, including
   the two `nullptr`s.
2. Write `insertBefore(DNode* node, int value)` for a doubly linked list. Why is
   this impossible in $O(1)$ for a singly linked list?
3. Write `deleteNode` for a **singly** linked list taking only a `Node*`. What
   must you do, and what is the complexity? (Chapter 31 has a famous trick for
   this.)
4. Write a function that checks the doubly linked invariant holds for a whole
   list, returning `false` at the first violation.
5. Convert a singly linked list into a circular one, then back again. How do you
   detect that a list is already circular?
6. Solve the Josephus problem with a circular list: $n$ people in a ring, every
   $k$-th is removed, who is last? What does your solution cost?
7. Why is `std::list::erase(it)` $O(1)$ while `std::vector::erase(it)` is $O(n)$?
   Why is `std::list::operator[]` not provided at all?
8. A doubly linked list of one `int` per node uses 20 bytes for 4 bytes of data.
   At what payload size does the overhead stop mattering, in your judgement?
:::
