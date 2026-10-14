# Deletion
@short: Deletion
@subtitle: Unlink, then free — and never in the other order
@tier: core
@prereq: Chapters 25 and 22
@blurb: Deletion is insertion in reverse plus one extra obligation: the removed node must be given back to the heap, exactly once, and not before you have finished reading from it. This chapter covers deleting the first node, the last, a position, and a value, with the memory discipline that keeps every one of them leak-free.
@objectives:
- Delete the first node, the last node, a node at a position, and by value
- State the order rule for deletion: unlink first, then free
- Explain why singly linked deletion needs the **predecessor**, not the node
- Handle the empty list, the single-node list, and deleting the head
- Free a whole list without leaking and without use-after-free
- Recognise the three deletion bugs: leak, dangling, double free

## The two rules

@fig: del_order_rule | 186 | The order rule for deletion. Unlink the node by rerouting its predecessor around it, and only then `delete` it. Deleting first leaves `prev->next` pointing at freed memory, and the next traversal walks into it.

:::insight The two rules of deletion
**Rule 1 — unlink before you free.** Reroute `prev->next` past the doomed node
*first*. Only when nothing points at it may you `delete` it.

**Rule 2 — you need the predecessor, not the node.** To unlink node $X$ you must
change $X$'s predecessor's `next`. A singly linked list cannot go backwards, so
you must either walk with a trailing `prev` pointer, or stop one node early.

Rule 2 is why every deletion function below looks more complicated than its
insertion counterpart.
:::

## 1. Delete the first node

@fig: del_front | 168 | Deleting the first node. Save the head, move `head` on by one, then free what you saved. Three lines, $O(1)$, and the one-node list falls out correctly because `head->next` is already `nullptr`.

```cpp title="Delete the first node — O(1)"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

void deleteFront(Node*& head) {
    if (head == nullptr) return;    // nothing to delete
    Node* doomed = head;            // 1. remember it
    head = head->next;              // 2. unlink: head skips past it
    delete doomed;                  // 3. now free it
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* head = buildList({10, 20, 30});
    deleteFront(head);
    printList(head);
    deleteFront(head);
    deleteFront(head);
    printList(head);                 // now empty
    deleteFront(head);               // deleting from empty is harmless
    printList(head);
    freeList(head);
    return 0;
}
```

```text nonum
20 -> 30
(empty)
(empty)
```

:::pitfall The two ways to get these three lines wrong
```cpp nonum frag
delete head;             // BAD freed first...
head = head->next;       //   ...then read through the freed pointer
```
Classic use-after-free. It often appears to work, because the bytes still hold
the old value.

```cpp nonum frag
head = head->next;       // BAD unlinked...
// ...and never freed: the old first node is now unreachable
```
A leak. No error, no crash, and invisible until you run AddressSanitizer.

**Save, unlink, free — in that order.** It is three lines because it needs to be
three lines.
:::

## 2. Delete the last node

@fig: del_back | 184 | Deleting the last node. You must stop on the **second-to-last** node, because that is the node whose `next` must become `nullptr`. The single-node list is a genuine special case, because there is no second-to-last node.

```cpp title="Delete the last node — O(n)"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

void deleteBack(Node*& head) {
    if (head == nullptr) return;              // empty: nothing to do
    if (head->next == nullptr) {              // SPECIAL CASE: exactly one node
        delete head;
        head = nullptr;                       // the list is now empty
        return;
    }
    Node* prev = head;
    while (prev->next->next != nullptr)       // stop on the SECOND-TO-LAST
        prev = prev->next;
    delete prev->next;                        // free the last node
    prev->next = nullptr;                     // and mark the new end
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}

int main() {
    Node* head = buildList({10, 20, 30});
    deleteBack(head);
    printList(head);
    deleteBack(head);
    printList(head);
    deleteBack(head);                         // down to empty
    printList(head);
    deleteBack(head);                         // and again: harmless
    printList(head);
    return 0;
}
```

```text nonum
10 -> 20
10
(empty)
(empty)
```

:::insight `prev->next->next != nullptr` — read it slowly
We need the node *before* the last one. Equivalently: the node whose
**grandchild** does not exist.

- `prev->next == nullptr` would stop on the last node — too far, and then
  `prev->next = nullptr` would do nothing useful.
- `prev->next->next == nullptr` stops one earlier, on exactly the node we must
  modify.

This is Chapter 25's principle again: *to modify a node, stop on it.* Here the
node to modify is the second-to-last, so the condition looks one step further
ahead.

The single-node case must be handled separately precisely because `head->next`
is already `nullptr`, so `prev->next->next` would dereference null.
:::

**Cost.** $O(n)$ time, $O(1)$ space. This is a weakness of the singly linked
list: even with a `tail` pointer, deleting the last node is $O(n)$, because you
still have to *find* the new tail. A **doubly** linked list makes it $O(1)$,
which is one of the main reasons that variant exists (Chapter 27).

## 3. Delete at a position

```cpp title="Delete the node at index pos"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

bool deleteAt(Node*& head, int pos) {
    if (head == nullptr || pos < 0) return false;

    if (pos == 0) {                      // the head itself changes
        Node* doomed = head;
        head = head->next;
        delete doomed;
        return true;
    }
    Node* prev = head;                   // walk to the node BEFORE pos
    for (int i = 0; i < pos - 1; ++i) {
        if (prev->next == nullptr) return false;   // pos is past the end
        prev = prev->next;
    }
    if (prev->next == nullptr) return false;       // nothing at pos

    Node* doomed = prev->next;
    prev->next = doomed->next;           // 1. unlink: skip over it
    delete doomed;                       // 2. then free
    return true;
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* head = buildList({10, 20, 30, 40, 50});
    deleteAt(head, 2);                   // remove 30
    printList(head);
    deleteAt(head, 0);                   // remove the head
    printList(head);
    deleteAt(head, 2);                   // remove the last
    printList(head);
    std::cout << "pos 9: " << (deleteAt(head, 9) ? "ok" : "rejected") << "\n";
    freeList(head);
    return 0;
}
```

```text nonum
10 -> 20 -> 40 -> 50
20 -> 40 -> 50
20 -> 40
pos 9: rejected
```

@fig: del_position | 184 | Deleting at index 2. `prev` stops on index 1; the node at index 2 is unlinked by pointing `prev->next` at its successor, and only then freed.

## 4. Delete by value

The version you will actually be asked for, and it shows the `prev`/`curr`
walking pattern clearly.

```cpp title="Delete the first node holding a value"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// Removes the FIRST node equal to value. Returns whether one was found.
bool deleteValue(Node*& head, int value) {
    if (head == nullptr) return false;

    if (head->data == value) {           // the head matches
        Node* doomed = head;
        head = head->next;
        delete doomed;
        return true;
    }
    Node* prev = head;
    Node* curr = head->next;             // curr is always prev->next
    while (curr != nullptr) {
        if (curr->data == value) {
            prev->next = curr->next;     // 1. unlink
            delete curr;                 // 2. free
            return true;
        }
        prev = curr;                     // advance BOTH, keeping them adjacent
        curr = curr->next;
    }
    return false;                        // not present
}

// Removes EVERY node equal to value. Returns how many were removed.
int deleteAllValues(Node*& head, int value) {
    int removed = 0;
    while (head != nullptr && head->data == value) {   // strip matching heads
        Node* doomed = head;
        head = head->next;
        delete doomed;
        ++removed;
    }
    if (head == nullptr) return removed;

    Node* prev = head;
    while (prev->next != nullptr) {
        if (prev->next->data == value) {
            Node* doomed = prev->next;
            prev->next = doomed->next;
            delete doomed;
            ++removed;
            // do NOT advance prev - the new prev->next has not been checked
        } else {
            prev = prev->next;
        }
    }
    return removed;
}

void printList(Node* head) {
    for (Node* c = head; c; c = c->next) std::cout << c->data << (c->next ? " -> " : "\n");
    if (!head) std::cout << "(empty)\n";
}
Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* head = buildList({10, 20, 30, 20});
    std::cout << deleteValue(head, 20) << " ";
    printList(head);
    std::cout << deleteValue(head, 99) << " ";
    printList(head);

    Node* h2 = buildList({7, 7, 1, 7, 2, 7, 7});
    std::cout << "removed " << deleteAllValues(h2, 7) << ": ";
    printList(h2);

    Node* h3 = buildList({5, 5, 5});
    std::cout << "removed " << deleteAllValues(h3, 5) << ": ";
    printList(h3);

    freeList(head);
    freeList(h2);
    freeList(h3);
    return 0;
}
```

```text nonum
1 10 -> 30 -> 20
0 10 -> 30 -> 20
removed 5: 1 -> 2
removed 3: (empty)
```

@fig: del_prev_curr | 180 | The `prev`/`curr` pair. They move together, always adjacent, so that the moment `curr` matches, `prev` is already the node that must be rerouted. This is the standard walking shape for any operation that must modify a node's predecessor.

:::pitfall Advancing `prev` after a deletion
In `deleteAllValues`, look at the comment: after removing a node, **`prev` must
not advance**.

The new `prev->next` is a node that has never been examined. Advancing past it
skips it, so `{7, 7}` would lose only the first 7 — exactly the array bug from
Chapter 6, in a new costume.

The symptom is distinctive: consecutive duplicates are only partly removed. If
your output has one leftover of each run, this is why.
:::

:::insight Why the head needs a separate branch, every time
Every function in this chapter begins with a special case for the head, and the
reason is structural: **the head has no predecessor.** Every other node is
unlinked by modifying `prev->next`; the first node is unlinked by modifying
`head` itself, which is a different variable of a different kind.

That asymmetry is irritating, it doubles the number of branches, and it is where
most linked list bugs live.

It is also completely removable. Chapter 29 introduces the **dummy node**: a
fake node placed before the real head, so that every real node — including the
first — has a predecessor. With it, `deleteValue` loses its special case and
becomes a single uniform loop. It is the single most useful trick in linked list
programming, and it exists precisely because of the paragraph above.
:::

## Clearing the whole list

```cpp title="Free every node, exactly once"
void clearList(Node*& head) {
    Node* curr = head;
    while (curr != nullptr) {
        Node* doomed = curr;        // 1. remember
        curr = curr->next;          // 2. advance PAST it first
        delete doomed;              // 3. then free
    }
    head = nullptr;                 // 4. the list is empty - say so
}
```

Step 4 matters. Without it, `head` dangles: it holds the address of a freed
node, and the next `printList(head)` walks into freed memory. One line turns a
subtle bug into an impossible one.

## The three deletion bugs

@tbl: What each deletion bug looks like from the outside. The first is silent, the second is intermittent, and the third usually crashes — which makes the third the least dangerous.
| Bug | Cause | Symptom |
|---|---|---|
| **Leak** | unlinked but never `delete`d | nothing visible; memory grows; AddressSanitizer reports it |
| **Use after free** | `delete` before reading `next` | usually works, then fails later, seemingly at random |
| **Double free** | two `delete`s of one node | crash, or heap corruption |
| **Dangling head** | freed the nodes, left `head` set | the next traversal reads freed memory |

:::warning Check your work mechanically
```bash nonum
g++ -std=c++17 -fsanitize=address,undefined -g list.cpp -o list && ./list
```
Every program in this chapter passes that cleanly. If yours does not, the report
names the exact line of the `new` that leaked or the `delete` that was repeated.

Run it on every exercise in this chapter. Linked lists are the first place most
people meet manual memory management, and this is how you find out whether you
got it right.
:::

## Cost summary

@tbl: The four deletions. Only the front is $O(1)$, and that is the mirror image of insertion, where only the front and a held node were $O(1)$.
| Deletion | Walk needed | Time | Changes `head`? | Special cases |
|---|---|---|---|---|
| First node | none | $O(1)$ | yes | empty list |
| Last node | to the second-to-last | $O(n)$ | if one node | empty; exactly one node |
| At position $p$ | $p-1$ steps | $O(n)$ | if $p = 0$ | $p = 0$; $p$ out of range |
| By value | until found | $O(n)$ | if the head matches | head matches; not found |
| All of one value | the whole list | $O(n)$ | if heads match | runs of matches |
| Whole list | the whole list | $O(n)$ | yes | none |

:::recap Chapter 26 in six lines
- **Unlink first, then free.** Reroute `prev->next` before `delete`.
- To delete a node you need its **predecessor**, which is why deletion walks
  with `prev` and `curr` together.
- The head always needs its own branch, because it has no predecessor — and the
  dummy node of Chapter 29 removes that.
- When removing *all* matches, do **not** advance `prev` after a removal.
- After freeing a list, set `head = nullptr`.
- Compile every linked list exercise with `-fsanitize=address` and believe what
  it tells you.
:::

:::exercise Practise
1. Draw the three pointer states for `deleteFront` on `10 -> 20 -> 30`. Which
   line would be wrong to move, and what would happen?
2. Why does `deleteBack` need the **second-to-last** node? What would
   `while (prev->next != nullptr)` leave `prev` pointing at?
3. Write `deleteLastOccurrence(Node*& head, int value)`. How does it differ from
   deleting the first, and can it be done in one pass?
4. In `deleteAllValues`, what goes wrong if you advance `prev` after a removal?
   Give the smallest input that shows it.
5. Write `removeDuplicates(Node*& head)` for a **sorted** list, freeing the
   removed nodes. Which array problem is this?
6. Run every program in this chapter under `-fsanitize=address`. Then
   deliberately remove one `delete` and confirm the report names it.
7. Explain why deleting the last node is $O(n)$ even with a `tail` pointer. What
   exactly would a doubly linked list give you here?
8. Write `deleteFront` so that it **returns** the deleted value rather than
   discarding it. What should it return on an empty list, and what are the three
   reasonable designs?
:::
