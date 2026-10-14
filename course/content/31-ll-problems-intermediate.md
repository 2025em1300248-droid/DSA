# Essential Linked List Problems II
@short: Intermediate List Problems
@subtitle: Six problems that combine two patterns each
@tier: practice
@prereq: Chapter 30
@blurb: These six are built from the pieces of Chapter 30. Palindrome is find-middle plus reverse; reorder is find-middle plus reverse plus merge. The skill being tested here is decomposition — seeing that an unfamiliar problem is two familiar ones stacked — and that is exactly the skill Chapter 34 turns into a method.
@objectives:
- Solve palindrome, intersection, add two numbers, remove duplicates, delete node and reorder
- Decompose a problem into steps you have already solved
- Explain the two-pointer trick for intersection, and why the lengths cancel
- Handle carries correctly when adding numbers stored as lists
- Explain the delete-without-the-head trick, and when it is illegal

## 1. Palindrome Linked List

**Statement.** Is the list the same read forwards and backwards?

**Think.** With an array this is trivial — two pointers from the ends. A singly
linked list cannot walk backwards, so the obvious approaches are: copy the
values into a vector ($O(n)$ space), or use recursion ($O(n)$ stack).

The $O(1)$-space answer is a decomposition:

:::insight Three steps you have already written
1. Find the **middle** (fast and slow) — Chapter 29.
2. **Reverse** the second half — Chapter 28.
3. Compare the two halves node by node.

No new technique is involved. That is the point: hard list problems are usually
two easy ones in sequence.
:::

@fig: ll_palindrome | 184 | Palindrome by decomposition. Find the middle, reverse the second half, then walk the two halves in step. The comparison stops when the shorter half runs out, which handles odd lengths with no special case.

```cpp title="Palindrome Linked List, O(1) space"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* reverseList(Node* head) {
    Node* prev = nullptr;
    while (head != nullptr) {
        Node* nxt = head->next;
        head->next = prev;
        prev = head;
        head = nxt;
    }
    return prev;
}

bool isPalindrome(Node* head) {
    if (head == nullptr || head->next == nullptr) return true;

    Node* slow = head;                  // 1. find the first middle
    Node* fast = head->next;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    Node* second = reverseList(slow->next);   // 2. reverse the second half

    bool ok = true;                     // 3. compare
    Node* a = head;
    Node* b = second;
    while (b != nullptr) {              // the second half is never longer
        if (a->data != b->data) { ok = false; break; }
        a = a->next;
        b = b->next;
    }
    slow->next = reverseList(second);   // 4. put the list back as we found it
    return ok;
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
    Node* a = buildList({1, 2, 2, 1});
    std::cout << isPalindrome(a) << " ";  printList(a);   // restored
    Node* b = buildList({1, 2, 3, 2, 1});
    std::cout << isPalindrome(b) << " ";  printList(b);
    Node* c = buildList({1, 2, 3});
    std::cout << isPalindrome(c) << " ";  printList(c);
    Node* d = buildList({7});
    std::cout << isPalindrome(d) << "\n";
    freeList(a); freeList(b); freeList(c); freeList(d);
    return 0;
}
```

```text nonum
1 1 -> 2 -> 2 -> 1
1 1 -> 2 -> 3 -> 2 -> 1
0 1 -> 2 -> 3
1
```

**Cost.** $O(n)$ time, $O(1)$ space.

:::insight Step 4 is the one that marks you out
Most candidates stop after step 3 with the list left reversed in the middle —
the function answered the question and silently corrupted its input.

Restoring it costs three lines and is the difference between a function and a
booby trap. If an interviewer does not ask about it, raise it yourself:
*"this mutates the list, so I'll restore it before returning — unless you would
rather I used $O(n)$ space and left the input alone."*
:::

## 2. Intersection of Two Linked Lists

**Statement.** Two lists may share a common tail. Return the first shared node,
or `nullptr`. They intersect by **identity**, not by value.

**Think.** Brute force is every pair: $O(n \cdot m)$. A hash set of one list's
nodes is $O(n + m)$ time and $O(n)$ space. The $O(1)$-space answer is lovely.

:::insight Why swapping to the other list equalises the lengths
Let list A have length $a$ before the shared part and list B have length $b$,
with a shared tail of length $c$.

Walk pointer `pa` along A; when it reaches the end, send it to the head of B.
Walk `pb` along B; when it reaches the end, send it to the head of A.

`pa` travels $a + c$ then $b$ — a total of $a + b + c$ before reaching the
intersection. `pb` travels $b + c$ then $a$ — also $a + b + c$. **They arrive at
the same node at the same step**, because each has walked the length of both
lists.

If there is no intersection, both reach `nullptr` after $a + b$ steps, and the
loop ends with the correct answer of `nullptr`.
:::

@fig: ll_intersection | 186 | The length-equalising walk. Each pointer walks its own list and then the other, so both cover exactly $a + b + c$ nodes and meet at the intersection — or at `nullptr` together if there is none.

```cpp title="Intersection of two lists, O(1) space"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* getIntersection(Node* headA, Node* headB) {
    if (headA == nullptr || headB == nullptr) return nullptr;
    Node* pa = headA;
    Node* pb = headB;
    while (pa != pb) {                        // compare NODES
        pa = (pa == nullptr) ? headB : pa->next;   // swap lists at the end
        pb = (pb == nullptr) ? headA : pb->next;
    }
    return pa;                                // the node, or nullptr
}

int main() {
    Node* shared = new Node(8);
    shared->next = new Node(10);

    Node* a = new Node(1);                    // 1 -> 2 -> 8 -> 10
    a->next = new Node(2);
    a->next->next = shared;

    Node* b = new Node(5);                    // 5 -> 8 -> 10
    b->next = shared;

    Node* hit = getIntersection(a, b);
    std::cout << (hit ? hit->data : -1) << "\n";

    Node* c = new Node(99);                   // no intersection
    std::cout << (getIntersection(a, c) == nullptr ? "none" : "?") << "\n";

    delete a->next; delete a;                 // free without double-deleting
    delete b;
    delete shared->next; delete shared;
    delete c;
    return 0;
}
```

```text nonum
8
none
```

:::pitfall Two traps in this problem
**Identity, not value.** Two nodes both holding 8 are not an intersection. The
loop compares `pa != pb`, which compares addresses.

**The `nullptr` swap must happen on the pointer itself, not on its `next`.**
Writing `pa = pa->next ? pa->next : headB;` skips the `nullptr` step, so the two
pointers travel different distances and the no-intersection case loops forever.
The version above lets each pointer *become* `nullptr` for one step, which is
what makes the counts match and the loop terminate.
:::

## 3. Add Two Numbers

**Statement.** Two numbers are stored as lists, **least significant digit
first**. Return their sum in the same form. `2->4->3` is 342; `5->6->4` is 465;
the answer is `7->0->8`, which is 807.

**Think.** This is primary-school addition. Walk both lists together, add the
digits plus the carry, write the units digit and keep the tens as the new carry.

@fig: ll_add_numbers | 180 | Adding two numbers digit by digit. Least-significant-first storage is exactly the order you add in, which is why the problem is posed that way. The carry survives past the end of both lists.

```cpp title="Add Two Numbers"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* addTwoNumbers(Node* a, Node* b) {
    Node dummy(0);
    Node* tail = &dummy;
    int carry = 0;

    // One loop handles both lists and the final carry.
    while (a != nullptr || b != nullptr || carry != 0) {
        int sum = carry;
        if (a != nullptr) { sum += a->data; a = a->next; }
        if (b != nullptr) { sum += b->data; b = b->next; }
        carry = sum / 10;
        tail->next = new Node(sum % 10);
        tail = tail->next;
    }
    return dummy.next;
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
    Node* a = buildList({2, 4, 3});          // 342
    Node* b = buildList({5, 6, 4});          // 465
    Node* s = addTwoNumbers(a, b);
    printList(s);                            // 807
    freeList(a); freeList(b); freeList(s);

    Node* c = buildList({9, 9, 9});          // 999
    Node* d = buildList({1});                // 1
    Node* t = addTwoNumbers(c, d);
    printList(t);                            // 1000
    freeList(c); freeList(d); freeList(t);

    Node* e = buildList({0});
    Node* f = buildList({0});
    Node* u = addTwoNumbers(e, f);
    printList(u);
    freeList(e); freeList(f); freeList(u);
    return 0;
}
```

```text nonum
7 -> 0 -> 8
0 -> 0 -> 0 -> 1
0
```

:::insight The loop condition does three jobs
```cpp nonum skip
while (a != nullptr || b != nullptr || carry != 0)
```
`||`, not `&&`. The lists may be different lengths, so the loop must continue
while **either** has digits left. And `carry != 0` keeps it going one more
round after both are exhausted — which is what turns 999 + 1 into 1000 rather
than 000.

Writing this as three separate loops (both lists, then the rest of A, then the
rest of B, then the carry) is correct and four times as long. One condition
covering every case is worth reaching for.
:::

**Cost.** $O(\max(n, m))$ time; $O(\max(n, m))$ for the output list.

**Variation.** If the digits are stored **most** significant first, you cannot
add left to right. Either reverse both lists, add, and reverse the answer; or
push the digits onto two stacks and pop. Say which you would do and why.

## 4. Remove Duplicates from a Sorted List

**Statement.** Each value should appear once. The list is sorted.

**Think.** Sorted means duplicates are adjacent, so compare each node with the
next. No `prev` is needed, because you delete `curr->next` rather than `curr`.

```cpp title="Remove duplicates from a sorted list"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* deleteDuplicates(Node* head) {
    Node* curr = head;
    while (curr != nullptr && curr->next != nullptr) {
        if (curr->data == curr->next->data) {
            Node* doomed = curr->next;
            curr->next = doomed->next;     // unlink
            delete doomed;                 // then free
            // do NOT advance: the new curr->next is unexamined
        } else {
            curr = curr->next;
        }
    }
    return head;
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
    Node* a = buildList({1, 1, 2, 3, 3});
    printList(deleteDuplicates(a)); freeList(a);
    Node* b = buildList({5, 5, 5});
    printList(deleteDuplicates(b)); freeList(b);
    Node* c = buildList({1, 2, 3});
    printList(deleteDuplicates(c)); freeList(c);
    return 0;
}
```

```text nonum
1 -> 2 -> 3
5
1 -> 2 -> 3
```

**Cost.** $O(n)$ time, $O(1)$ space.

**Watch for.** Not advancing `curr` after a deletion — the same rule as
Chapter 26. `{5,5,5}` is the test that catches it.

**Variation.** "Remove *all* nodes that have duplicates" (so `1->1->2` becomes
just `2`) is genuinely harder: the head may be deleted, so you need a dummy node
and a `prev`. Try it.

## 5. Delete a Node, given only that node

**Statement.** You are given a pointer to a node to delete — **not** the head.
The node is guaranteed not to be the last.

**Think.** You cannot reach the predecessor, so you cannot unlink this node.

:::insight Delete the next node instead, and steal its value
Copy the *next* node's data into this node, then delete the *next* node.

The node you were asked to remove physically survives, but its value is gone and
the list reads exactly as if it had been deleted. From outside, the result is
indistinguishable.
:::

@fig: ll_delete_node | 176 | Deleting a node without its predecessor. The value from the following node is copied in, and that following node is unlinked and freed instead. The list ends up correct even though a different object was destroyed.

```cpp title="Delete a node given only that node" frag
void deleteNode(Node* node) {
    Node* doomed = node->next;     // guaranteed non-null by the problem
    node->data = doomed->data;     // steal its value
    node->next = doomed->next;     // unlink it
    delete doomed;                 // and free it
}
```

**Cost.** $O(1)$ time and space.

:::warning When this trick is illegal
**It cannot delete the last node.** There is no next node to steal from, which
is why the problem states the guarantee.

**It invalidates other pointers.** Anyone else holding a pointer to the
following node now holds a dangling pointer — the node they expected has been
freed, and its value has moved into a different object.

**It copies the data.** For an `int` that is free. For a large object it may be
expensive, and for a non-copyable one it is impossible.

In real code this is a smell: it is a workaround for an API that should have
given you the predecessor, or for a singly linked list that should have been
doubly linked. As an interview answer it is exactly right; as a design, it is a
sign something upstream is wrong.
:::

## 6. Reorder List

**Statement.** Turn $L_0 \to L_1 \to \cdots \to L_{n-1}$ into
$L_0 \to L_{n-1} \to L_1 \to L_{n-2} \to \cdots$

**Think.** Three familiar steps again, in sequence.

@fig: ll_reorder | 190 | Reorder, in three steps. Split at the middle, reverse the second half, then interleave the two halves one node at a time. Every step is a function you have already written.

```cpp title="Reorder List"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

void reorderList(Node* head) {
    if (head == nullptr || head->next == nullptr) return;

    Node* slow = head;                   // 1. split at the first middle
    Node* fast = head->next;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    Node* second = slow->next;
    slow->next = nullptr;

    Node* prev = nullptr;                // 2. reverse the second half
    while (second != nullptr) {
        Node* nxt = second->next;
        second->next = prev;
        prev = second;
        second = nxt;
    }
    second = prev;

    Node* first = head;                  // 3. interleave
    while (second != nullptr) {
        Node* f = first->next;
        Node* s = second->next;
        first->next = second;
        second->next = f;
        first = f;
        second = s;
    }
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
    Node* a = buildList({1, 2, 3, 4});
    reorderList(a); printList(a); freeList(a);
    Node* b = buildList({1, 2, 3, 4, 5});
    reorderList(b); printList(b); freeList(b);
    Node* c = buildList({1, 2});
    reorderList(c); printList(c); freeList(c);
    return 0;
}
```

```text nonum
1 -> 4 -> 2 -> 3
1 -> 5 -> 2 -> 4 -> 3
1 -> 2
```

**Cost.** $O(n)$ time, $O(1)$ space.

**Watch for.** Splitting at the **first** middle (`fast = head->next`) so the
first half is never shorter than the second. The interleave loop then terminates
naturally when `second` runs out.

## The six, at a glance

@tbl: The six intermediate problems. Note the right-hand column: four of the six are built entirely from Chapter 30's problems.
| # | Problem | Built from | Time | Space |
|---|---|---|---|---|
| 1 | Palindrome | middle + reverse | $O(n)$ | $O(1)$ |
| 2 | Intersection | the two-walk trick | $O(n+m)$ | $O(1)$ |
| 3 | Add Two Numbers | dummy + carry | $O(\max(n,m))$ | output only |
| 4 | Remove duplicates (sorted) | adjacency | $O(n)$ | $O(1)$ |
| 5 | Delete a given node | the value-steal trick | $O(1)$ | $O(1)$ |
| 6 | Reorder List | middle + reverse + merge | $O(n)$ | $O(1)$ |

:::recap Chapter 31 in five lines
- Hard list problems are usually **two or three easy ones in sequence**. Look
  for the decomposition before looking for a new idea.
- Palindrome and reorder are both middle + reverse (+ merge).
- The intersection walk works because each pointer covers $a + b + c$ nodes.
- One loop with `||` and `carry != 0` handles every case of list addition.
- Restore any list you temporarily mutate, and say that you are doing it.
:::

:::exercise Practise
1. Solve palindrome with a vector of values instead. What is the space, and
   when is that the better answer?
2. For intersection, construct two lists that share a tail and verify by hand
   that both pointers travel $a + b + c$ steps.
3. Add two numbers stored **most** significant digit first. Give both
   approaches, and say which you prefer.
4. Write "remove all nodes that have duplicates" — `1->1->2->3->3` becomes `2`.
   Which pattern do you need, and why does the plain version not work?
5. Why can `deleteNode` not remove the last node? Design a list structure where
   it could.
6. For reorder, what happens if you split at the *second* middle instead? Trace
   `{1,2,3,4}`.
7. Rotate a list right by $k$: `1->2->3->4->5` with $k=2$ becomes
   `4->5->1->2->3`. (Hint: make it circular, then break it in the right place.)
:::
