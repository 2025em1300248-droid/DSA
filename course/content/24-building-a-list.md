# Building a Linked List From Scratch
@short: Building a List
@subtitle: Every line, every symbol, explained
@tier: foundation
@prereq: Chapter 23
@blurb: We now write the `Node` struct that the rest of this book uses, and explain every single symbol in it — `struct`, `Node*`, the constructor, `nullptr`, and the difference between a node and a pointer to a node. Then we create nodes, connect them, walk the list, count it, search it, update it, and free it, drawing the memory at every step.
@objectives:
- Explain every line and symbol of the `Node` definition
- Distinguish a node from a pointer to a node, and say why it matters
- Create nodes on the heap and connect them into a list
- Traverse a list correctly, and explain why `curr` is used rather than `head`
- Count, search and update nodes
- Free an entire list without leaking and without using a freed pointer

## The Node definition

Here it is. Every linked list in this book uses exactly this.

```cpp title="The Node struct — used unchanged for the rest of the book" nonum
struct Node {
    int data;
    Node* next;

    Node(int value) {
        data = value;
        next = nullptr;
    }
};
```

Six lines. We will spend the next two pages on them, because every later
chapter assumes you understand all six completely.

@fig: ll_node_anatomy | 176 | The `Node` definition mapped onto the object it creates. The struct is a *blueprint*; `new Node(10)` uses the blueprint to build one actual object on the heap.

### `struct Node {`

:::definition struct
A **struct** defines a new type by grouping several values together under one
name.

After this definition, `Node` is a type, exactly like `int` is a type. You can
declare variables of it, make pointers to it, and allocate it with `new`.

(In C++, `struct` and `class` are the same thing with one difference: a
`struct`'s members are public by default and a `class`'s are private. For a
plain data holder like this, `struct` is the conventional choice.)
:::

The `{` opens the list of members, and the matching `};` at the end closes it.
**That semicolon is required** — leaving it off produces a confusing error on
whatever line comes next, which is a classic five-minute waste.

### `int data;`

The value this node stores. It is an ordinary `int`, living inside the node
object. If you wanted a list of strings you would write `std::string data;`
instead, and nothing else about the structure would change.

The name `data` is conventional, not required. LeetCode calls it `val`, and
some books call it `info`. Pick one and stay with it.

### `Node* next;`

The important one. Read it as **"`next` is a pointer to a `Node`"**.

:::insight A node contains a pointer, not a node
`Node* next;` could not be `Node next;` — and the reason is worth understanding
rather than accepting.

If a `Node` contained a `Node`, that inner `Node` would contain another `Node`,
and so on forever. The type would have infinite size, and the compiler rejects
it outright.

A **pointer** to a `Node` is always the same size (8 bytes on a 64-bit machine)
no matter what it points at — because it holds only an address. So the struct's
size is settled: 4 bytes for `data`, 8 for `next`, plus padding. Finite,
and the recursion lives in the *data*, not in the *type*.

This is why every self-referential structure in programming — lists, trees,
graphs — is built from pointers. It is not a style choice; it is the only thing
that can work.
:::

Note also that `Node*` is usable *inside* the definition of `Node` itself, even
though `Node` is not finished yet. That is allowed precisely because the
compiler does not need to know how big a `Node` is to know how big a `Node*` is.

### `Node(int value) { ... }`

:::definition Constructor
A **constructor** is a function that runs automatically when an object is
created. It has the same name as the type and no return type at all — not even
`void`.

`Node(int value)` says: *"to make a Node, you must supply one `int`"*. So
`new Node(10)` calls it with `value = 10`.

Its job here is to leave the new object in a sensible state: `data` set to the
supplied value, and `next` set to `nullptr`.
:::

:::pitfall Without the constructor, `next` is garbage
```cpp nonum skip
struct Node {
    int data;
    Node* next;
};

Node* n = new Node;      // no constructor: next contains random bytes
if (n->next == nullptr)  // almost certainly false, and meaningless
```
An uninitialised pointer does not contain `nullptr` — it contains whatever was
in those 8 bytes before. Following it is undefined behaviour, and the bug
appears as a random crash much later in the traversal.

The constructor makes that impossible. **Write it every time.**

The modern form uses an initialiser list, which is slightly more efficient and
is what you will see in production code:
```cpp nonum skip
Node(int value) : data(value), next(nullptr) {}
```
The two versions are equivalent for `int` and `Node*`. This book uses the
assignment form because it reads more plainly for a beginner; use either.
:::

### Node versus pointer-to-Node

This distinction causes more confusion than anything else in Part VI.

@fig: ll_node_vs_ptr | 160 | A node and a pointer to a node. The node is the object with the two fields; the pointer is an 8-byte variable holding its address. Three `Node*` variables can all point at the same single node.

| | `Node n(10);` | `Node* p = new Node(10);` |
|---|---|---|
| What it is | an object | a pointer to an object |
| Where it lives | the stack | the pointer on the stack, the object on the heap |
| Lifetime | until the enclosing block ends | until you `delete` it |
| Access a member | `n.data` | `p->data` |
| Can be `nullptr` | no | yes |
| Used in this book | almost never | always |

Every node in a linked list is created with `new`, because it must outlive the
function that created it. The pointers (`head`, `curr`, `prev`) are stack
variables; the nodes are heap objects. Chapter 22's diagram, exactly.

## Building the smallest possible list

Start with one node, and build up.

```cpp title="One node, then two, then three"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

int main() {
    Node* head = new Node(10);       // one node; head->next is nullptr
    std::cout << head->data << "\n";
    std::cout << (head->next == nullptr ? "end of list" : "more") << "\n";

    head->next = new Node(20);       // attach a second node
    std::cout << head->next->data << "\n";

    head->next->next = new Node(30); // and a third
    std::cout << head->next->next->data << "\n";

    delete head->next->next;         // free from the back
    delete head->next;
    delete head;
    return 0;
}
```

```text nonum
10
end of list
20
30
```

@fig: ll_build_steps | 196 | Building the list one node at a time. At every step the final node's `next` is `nullptr`, so the list is always valid — you could traverse it correctly at any point in the middle of construction.

Read `head->next->next = new Node(30);` carefully, left to right:

1. `head` — the first node.
2. `head->next` — the second node.
3. `head->next->next` — the second node's `next` field.
4. `= new Node(30)` — make a third node and store its address there.

That chain of arrows is how all linked list code reads. It becomes automatic
sooner than you expect.

:::pitfall Freeing in the wrong order
```cpp nonum frag
delete head;
delete head->next;     // head is already freed - undefined behaviour
```
After `delete head`, reading `head->next` is a use-after-free. The address you
get back may be the right one, or rubbish; it is undefined either way.

This is why the free loop later in this chapter saves the next pointer
**before** deleting. It is the same "read before you overwrite" principle from
Chapter 6, applied to memory instead of array slots.
:::

## Traversing: the loop you will write a hundred times

```cpp title="Print every node"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

void printList(Node* head) {
    Node* curr = head;                   // a WALKER - head must not move
    while (curr != nullptr) {            // until we fall off the end
        std::cout << curr->data;
        if (curr->next != nullptr) std::cout << " -> ";
        curr = curr->next;               // step forward
    }
    std::cout << "\n";
}

int main() {
    Node* head = new Node(10);
    head->next = new Node(20);
    head->next->next = new Node(30);

    printList(head);
    printList(nullptr);                  // an empty list prints nothing

    delete head->next->next;
    delete head->next;
    delete head;
    return 0;
}
```

```text nonum
10 -> 20 -> 30

```

@fig: ll_traverse_steps | 180 | The traversal, step by step. `curr` moves along; `head` never does. When `curr` becomes `nullptr` the loop ends — and notice that it ends *after* the last node has been processed, not before.

:::insight Why `curr`, and not `head`
```cpp nonum frag
while (head != nullptr) {        // BAD destroys the list
    std::cout << head->data;
    head = head->next;
}
```
Inside the function this works and prints the right thing. But `head` was a
copy of the caller's pointer, so the caller still has its list — this time.

Write the same loop on a `head` you actually own, and after it runs `head` is
`nullptr`: you have walked it off the end and lost every node. The nodes are
still on the heap, unreachable. A complete leak, from one missing variable.

**The rule: `head` identifies the list, so it never moves. `curr` does the
walking.** Create a separate walker, always, even when it feels unnecessary.
:::

Note also that an empty list needs no special case: `curr` starts as `nullptr`,
the loop body never runs, and the function prints an empty line. Code where the
edge case falls out of the structure is better than code that tests for it.

## Counting, searching, updating

```cpp title="The three read-only operations"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

int length(Node* head) {
    int n = 0;
    for (Node* curr = head; curr != nullptr; curr = curr->next) ++n;
    return n;
}

// Returns the node holding target, or nullptr if absent.
Node* findNode(Node* head, int target) {
    for (Node* curr = head; curr != nullptr; curr = curr->next)
        if (curr->data == target) return curr;
    return nullptr;
}

// Returns the node at index i (0-based), or nullptr if i is out of range.
Node* nodeAt(Node* head, int i) {
    Node* curr = head;
    for (int k = 0; k < i && curr != nullptr; ++k) curr = curr->next;
    return curr;
}

int main() {
    Node* head = new Node(10);
    head->next = new Node(20);
    head->next->next = new Node(30);

    std::cout << "length  = " << length(head) << "\n";
    std::cout << "find 20 = " << (findNode(head, 20) ? "found" : "absent") << "\n";
    std::cout << "find 99 = " << (findNode(head, 99) ? "found" : "absent") << "\n";
    std::cout << "node[1] = " << nodeAt(head, 1)->data << "\n";
    std::cout << "node[9] = " << (nodeAt(head, 9) ? "exists" : "out of range") << "\n";

    Node* n = findNode(head, 20);        // updating is just a field assignment
    if (n) n->data = 99;
    std::cout << "after update, node[1] = " << nodeAt(head, 1)->data << "\n";

    while (head) { Node* doomed = head; head = head->next; delete doomed; }
    return 0;
}
```

```text nonum
length  = 3
find 20 = found
find 99 = absent
node[1] = 20
node[9] = out of range
after update, node[1] = 99
```

All three are $O(n)$ and $O(1)$ space. Note what `nodeAt` makes vivid: **a
linked list has no index.** There is nothing to compute; you simply count your
way along. That function is the whole reason `list[i]` does not exist.

:::pitfall The `&& curr != nullptr` in `nodeAt`
Without it, asking for index 9 in a 3-node list would dereference `nullptr` on
the fourth step. The extra condition stops the walk at the end and lets the
function return `nullptr`, which the caller is then obliged to check.

The general rule, worth saying out loud every time: **before you follow a
pointer, know that it is not null.**
:::

## Building from an array, and freeing everything

Two utilities we will reuse in every later chapter.

```cpp title="Build a list from values, print it, and free it"
#include <iostream>
#include <vector>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// Builds a list from the values, in order. Returns the head.
Node* buildList(const std::vector<int>& values) {
    Node* head = nullptr;
    Node* tail = nullptr;                // tracks the last node: O(1) append
    for (int v : values) {
        Node* node = new Node(v);
        if (head == nullptr) head = tail = node;   // the first node
        else { tail->next = node; tail = node; }   // attach and advance
    }
    return head;
}

void printList(Node* head) {
    for (Node* curr = head; curr != nullptr; curr = curr->next)
        std::cout << curr->data << (curr->next ? " -> " : "\n");
    if (head == nullptr) std::cout << "(empty)\n";
}

// Deletes every node. The list must not be used afterwards.
void freeList(Node* head) {
    Node* curr = head;
    while (curr != nullptr) {
        Node* doomed = curr;        // 1. remember the node to destroy
        curr = curr->next;          // 2. step past it FIRST
        delete doomed;              // 3. now destroy it
    }
}

int main() {
    Node* head = buildList({1, 2, 3, 4, 5});
    printList(head);
    std::cout << "empty list: ";
    printList(nullptr);
    freeList(head);
    head = nullptr;                 // say that the list is gone
    std::cout << "freed\n";
    return 0;
}
```

```text nonum
1 -> 2 -> 3 -> 4 -> 5
empty list: (empty)
freed
```

@fig: ll_free | 170 | The free loop. The next pointer is read **before** the node is destroyed. Reversing those two lines reads a freed object, which is the most common linked list memory bug there is.

:::insight The tail pointer in `buildList`
Without `tail`, appending each new node would mean walking to the end of the
list every time — $O(n)$ per append, so $O(n^2)$ to build a list of $n$
elements.

Keeping `tail` makes each append $O(1)$, so building is $O(n)$. For 100,000
elements that is the difference between instant and about five seconds.

This is the first appearance of a theme: **a linked list operation is $O(1)$
exactly when you already hold the relevant node.** Keeping a `tail` pointer is
how you arrange to hold it.
:::

## Cost summary

@tbl: Everything in this chapter. Note that the only $O(1)$ operations are the ones where you already have the node in your hand.
| Operation | Time | Space | Note |
|---|---|---|---|
| Create one node | $O(1)$ | $O(1)$ | one `new` |
| Attach a node you hold | $O(1)$ | $O(1)$ | one assignment |
| Traverse / print | $O(n)$ | $O(1)$ | the standard `curr` loop |
| Length | $O(n)$ | $O(1)$ | no stored count unless you keep one |
| Search by value | $O(n)$ | $O(1)$ | no shortcut, even if sorted |
| Node at index $i$ | $O(i)$ | $O(1)$ | counting, not calculating |
| Update a node you hold | $O(1)$ | $O(1)$ | a field assignment |
| Build from $n$ values | $O(n)$ | $O(n)$ nodes | $O(n^2)$ without a tail pointer |
| Free the whole list | $O(n)$ | $O(1)$ | save `next` before deleting |

:::recap Chapter 24 in seven lines
- `Node* next;` must be a **pointer**, or the type would have infinite size.
- The constructor exists so that `next` is `nullptr` rather than garbage.
- A **node** is a heap object; a **`Node*`** is a stack variable holding its
  address.
- `head` identifies the list and never moves. `curr` walks.
- `while (curr != nullptr)` handles the empty list with no special case.
- Before following a pointer, know it is not null.
- When freeing: save `next`, step forward, **then** delete.
:::

:::exercise Practise
1. Write out, in English, what each of the six lines of the `Node` struct does.
2. Why can `Node` not contain a `Node` by value? Give the two-sentence answer.
3. Build a 4-node list holding 7, 14, 21, 28 without using `buildList`. Then
   print the third value using only arrows from `head`.
4. Write `sum(Node* head)` returning the total of all values, and `maxValue`
   returning the largest. What should each do on an empty list?
5. Write `nodeAtFromEnd(Node* head, int k)` returning the $k$-th node from the
   **end**. The obvious way takes two passes — write that first.
6. What is wrong with the loop below, and what does it leak?
7. Write `freeList` recursively. For what list length would it overflow a 1 MB
   stack, and what does that tell you about recursion on linked lists?
:::

```cpp title="For exercise 6 — find the bug" nonum frag
while (head != nullptr) {
    delete head;
    head = head->next;
}
```
