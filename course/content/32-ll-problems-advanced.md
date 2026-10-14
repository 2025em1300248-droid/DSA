# Advanced Linked List Problems
@short: Advanced List Problems
@subtitle: Four problems that combine everything
@tier: advanced
@prereq: Chapter 31
@blurb: The four hardest standard linked list questions. Reverse in k-groups needs the reversal loop under a counter; rotate needs a circular trick; sort list is merge sort without an array; and copy list with random pointer has a solution so neat it is worth the chapter on its own. None introduces a new primitive — they combine the ones you have.
@objectives:
- Reverse a list in groups of $k$, leaving a short final group alone
- Rotate a list right by $k$, using the make-it-circular trick
- Sort a list in $O(n \log n)$ time and $O(\log n)$ space with merge sort
- Explain why quicksort is a poor fit for linked lists and merge sort is ideal
- Deep-copy a list with random pointers in $O(1)$ extra space by interleaving

## 1. Reverse Nodes in k-Group

:::definition The problem
Reverse the nodes of a list $k$ at a time. If the number of remaining nodes is
fewer than $k$, leave them as they are.

`1->2->3->4->5` with $k = 2$ gives `2->1->4->3->5` — the final lone 5 is
untouched.
:::

**Think.** You already have the four-line reversal loop. Two new requirements:
run it over exactly $k$ nodes rather than the whole list, and check *before*
reversing that $k$ nodes remain.

@fig: lla_k_group | 190 | Reversing in groups of three. Each group is reversed by the ordinary loop, bounded by a counter; the group's old head becomes its tail and must be stitched onto the next group. The short final group is detected in advance and left alone.

:::insight The check must come first
After you reverse a group, you cannot tell how many nodes *were* in it — the
information is gone. So count $k$ nodes ahead **before** touching anything, and
if you cannot find $k$, return immediately with the remainder intact.

That is also what makes the function naturally recursive: reverse the first
group, then let the recursive call deal with everything after it, and attach the
result to the group's new tail — which is the node that used to be its head.
:::

```cpp title="Reverse Nodes in k-Group"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* reverseKGroup(Node* head, int k) {
    if (k <= 1 || head == nullptr) return head;

    Node* check = head;                       // are there k nodes left?
    for (int i = 0; i < k; ++i) {
        if (check == nullptr) return head;    // fewer than k - leave them alone
        check = check->next;
    }
    // `check` now points just past this group.
    Node* prev = nullptr;
    Node* curr = head;
    for (int i = 0; i < k; ++i) {             // the ordinary loop, k times
        Node* nxt = curr->next;
        curr->next = prev;
        prev = curr;
        curr = nxt;
    }
    // head is now this group's TAIL; attach the rest to it.
    head->next = reverseKGroup(curr, k);
    return prev;                              // prev is this group's new head
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
    Node* a = buildList({1, 2, 3, 4, 5});
    a = reverseKGroup(a, 2); printList(a); freeList(a);

    Node* b = buildList({1, 2, 3, 4, 5});
    b = reverseKGroup(b, 3); printList(b); freeList(b);

    Node* c = buildList({1, 2, 3});
    c = reverseKGroup(c, 5); printList(c); freeList(c);   // k > length

    Node* d = buildList({1, 2, 3, 4});
    d = reverseKGroup(d, 1); printList(d); freeList(d);   // k = 1: no change
    return 0;
}
```

```text nonum
2 -> 1 -> 4 -> 3 -> 5
3 -> 2 -> 1 -> 4 -> 5
1 -> 2 -> 3
1 -> 2 -> 3 -> 4
```

**Cost.** $O(n)$ time — each node is reversed once — and $O(n/k)$ stack from the
recursion. An iterative version with a dummy node gets it to $O(1)$ space; it is
longer, and worth writing as an exercise.

**Watch for.** `head->next = reverseKGroup(curr, k);` must come **after** the
reversal loop, because `head` has become the group's tail by then. Writing it
before gives a list that loses everything after the first group.

## 2. Rotate List

:::definition The problem
Rotate right by $k$: `1->2->3->4->5` with $k = 2$ becomes `4->5->1->2->3`.
$k$ may be larger than the list.
:::

**Think.** The naive approach moves the last node to the front, $k$ times:
$O(n \cdot k)$. Better: find the new head directly.

@fig: lla_rotate | 184 | Rotating by making the list circular. Join the tail to the head, walk to the node that should become the new tail, and cut there. Three steps, one pass each, and no nodes are created or destroyed.

:::insight Close the ring, then cut it in a different place
1. Walk to the tail, counting the length $n$ along the way.
2. Join `tail->next = head`, making it circular.
3. Reduce $k$ to $k \bmod n$ — a rotation by $n$ is the identity.
4. The new tail is $n - k - 1$ steps from the old head. Walk there.
5. The new head is `newTail->next`. Set `newTail->next = nullptr`.

Closing the ring removes all the awkward wrap-around arithmetic: once it is a
circle, rotating is just choosing where to cut.
:::

```cpp title="Rotate List right by k"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* rotateRight(Node* head, int k) {
    if (head == nullptr || head->next == nullptr || k == 0) return head;

    int n = 1;                            // 1. find the tail and the length
    Node* tail = head;
    while (tail->next != nullptr) { tail = tail->next; ++n; }

    tail->next = head;                    // 2. close the ring
    k %= n;                               // 3. only k mod n matters
    if (k == 0) { tail->next = nullptr; return head; }   // a whole turn

    Node* newTail = head;                 // 4. walk n-k-1 steps
    for (int i = 0; i < n - k - 1; ++i) newTail = newTail->next;

    Node* newHead = newTail->next;        // 5. cut
    newTail->next = nullptr;
    return newHead;
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
    Node* a = buildList({1, 2, 3, 4, 5});
    a = rotateRight(a, 2); printList(a); freeList(a);

    Node* b = buildList({1, 2, 3});
    b = rotateRight(b, 4); printList(b); freeList(b);     // 4 % 3 == 1

    Node* c = buildList({1, 2, 3});
    c = rotateRight(c, 3); printList(c); freeList(c);     // a whole turn

    Node* d = buildList({1});
    d = rotateRight(d, 99); printList(d); freeList(d);
    return 0;
}
```

```text nonum
4 -> 5 -> 1 -> 2 -> 3
3 -> 1 -> 2
1 -> 2 -> 3
1
```

**Cost.** $O(n)$ time, $O(1)$ space.

**Watch for.** `k %= n` — without it the walk runs off the end of the ring…
except that it cannot, because the ring has no end; instead it loops and gives
the wrong answer silently, which is worse. And the `k == 0` branch after the
modulo must restore `tail->next = nullptr`, or you return a circular list.

## 3. Sort List

:::definition The problem
Sort a linked list in $O(n \log n)$ time. The expected follow-up is $O(1)$ extra
space.
:::

**Think.** Which sorting algorithm suits a linked list?

:::insight Why merge sort, and not quicksort
**Quicksort** needs random access to pick a pivot well and to partition
efficiently. On a list, reaching the middle is $O(n)$, so a median-of-three
pivot is expensive and a first-element pivot degenerates to $O(n^2)$ on sorted
input.

**Merge sort** needs only: split in half, and merge two sorted sequences. Both
are natural on a list — splitting is fast-and-slow, and merging is relinking
with no extra array at all.

And here is the pleasing part: merge sort on an **array** needs $O(n)$ auxiliary
space for the merge buffer. On a **list** it needs none, because merging
rearranges pointers in place. The linked list is the one data structure on which
merge sort is strictly better behaved than on an array.

(The recursion still costs $O(\log n)$ stack. A bottom-up iterative merge sort
reaches true $O(1)$, and that is what `std::list::sort` does.)
:::

@fig: lla_sort | 192 | Merge sort on a list. Split with fast and slow, sort each half recursively, then merge by relinking. No auxiliary array exists at any point — the merge step only rewires `next` pointers.

```cpp title="Sort List — merge sort, O(n log n)"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* mergeSorted(Node* a, Node* b) {
    Node dummy(0);
    Node* tail = &dummy;
    while (a != nullptr && b != nullptr) {
        if (a->data <= b->data) { tail->next = a; a = a->next; }
        else                    { tail->next = b; b = b->next; }
        tail = tail->next;
    }
    tail->next = (a != nullptr) ? a : b;
    return dummy.next;
}

Node* sortList(Node* head) {
    if (head == nullptr || head->next == nullptr) return head;   // 0 or 1 node

    Node* slow = head;                     // split at the FIRST middle
    Node* fast = head->next;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    Node* second = slow->next;
    slow->next = nullptr;                  // cut

    return mergeSorted(sortList(head), sortList(second));
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
    Node* a = buildList({4, 2, 1, 3});
    a = sortList(a); printList(a); freeList(a);

    Node* b = buildList({-1, 5, 3, 4, 0});
    b = sortList(b); printList(b); freeList(b);

    Node* c = buildList({2, 2, 1});
    c = sortList(c); printList(c); freeList(c);

    printList(sortList(nullptr));
    return 0;
}
```

```text nonum
1 -> 2 -> 3 -> 4
-1 -> 0 -> 3 -> 4 -> 5
1 -> 2 -> 2
(empty)
```

**Cost.** $O(n \log n)$ time, $O(\log n)$ stack.

**Watch for.** Splitting with `fast = head->next` (the first middle). Using
`fast = head` makes a two-node list split into two and zero nodes, so the
recursion never shrinks and you get infinite recursion. Test `{2, 1}`
specifically.

## 4. Copy List with Random Pointer

:::definition The problem
Each node has `next` **and** a `random` pointer that may point to any node in
the list, or to `nullptr`. Produce a deep copy: a completely separate list whose
structure matches exactly.
:::

**Think.** The difficulty: when you copy node $X$ and want to set its `random`,
the node it should point at may not have been created yet.

**The $O(n)$-space answer.** Build a hash map from each original node to its
copy in one pass, then fill in the `next` and `random` pointers in a second
pass using the map. Clear, correct, and the right first answer to give.

**The $O(1)$-space answer** is one of the neatest tricks in the subject.

@fig: lla_random_copy | 196 | Copying with interleaving. Each copy is spliced in directly after its original, so `original->next` *is* the copy. That makes every random pointer computable locally: the copy of `x->random` is simply `x->random->next`.

:::insight Interleaving makes the map unnecessary
**Step 1 — weave.** After every original node, insert its copy:
$A \to A' \to B \to B' \to C \to C'$.

**Step 2 — set the randoms.** For each original $X$, the copy of $X$ is
`X->next`, and the node $X$'s random points at — call it $Y$ — has its copy at
`Y->next`. So:
```cpp nonum skip
X->next->random = (X->random != nullptr) ? X->random->next : nullptr;
```
The interleaving *is* the map. Every lookup that needed a hash table is now a
single `->next`.

**Step 3 — unweave.** Separate the two lists, restoring the original's `next`
pointers and linking the copies to each other.

$O(n)$ time and $O(1)$ extra space, where the output list does not count.
:::

```cpp title="Copy List with Random Pointer, O(1) extra space"
#include <iostream>

struct RNode {
    int data;
    RNode* next;
    RNode* random;
    RNode(int value) { data = value; next = nullptr; random = nullptr; }
};

RNode* copyRandomList(RNode* head) {
    if (head == nullptr) return nullptr;

    for (RNode* c = head; c != nullptr; ) {        // 1. weave copies in
        RNode* copy = new RNode(c->data);
        copy->next = c->next;
        c->next = copy;
        c = copy->next;                            // skip over the copy
    }
    for (RNode* c = head; c != nullptr; c = c->next->next)   // 2. set randoms
        c->next->random = (c->random != nullptr) ? c->random->next : nullptr;

    RNode dummy(0);                                // 3. unweave
    RNode* tail = &dummy;
    for (RNode* c = head; c != nullptr; ) {
        RNode* copy = c->next;
        c->next = copy->next;                      // restore the original
        tail->next = copy;                         // collect the copy
        tail = copy;
        c = c->next;
    }
    return dummy.next;
}

int main() {
    RNode* a = new RNode(7);
    RNode* b = new RNode(13);
    RNode* c = new RNode(11);
    a->next = b; b->next = c;
    a->random = nullptr;
    b->random = a;          // 13 -> 7
    c->random = a;          // 11 -> 7

    RNode* copy = copyRandomList(a);

    for (RNode* p = copy; p != nullptr; p = p->next) {
        std::cout << p->data << "(random ";
        std::cout << (p->random ? std::to_string(p->random->data) : "null");
        std::cout << ") ";
    }
    std::cout << "\n";

    // The copy must be a genuinely separate list.
    std::cout << "separate nodes: " << (copy != a) << "\n";
    std::cout << "original intact: " << (a->next == b && b->next == c) << "\n";
    std::cout << "copy's random points into the COPY: "
              << (copy->next->random != a) << "\n";

    while (copy) { RNode* d = copy; copy = copy->next; delete d; }
    delete a; delete b; delete c;
    return 0;
}
```

```text nonum
7(random null) 13(random 7) 11(random 7) 
separate nodes: 1
original intact: 1
copy's random points into the COPY: 1
```

**Cost.** $O(n)$ time, $O(1)$ extra space.

**Watch for.** Step 3 must restore the original list, not just extract the copy
— the problem requires the input to be unchanged. The three checks in `main`
test exactly the three things that can go wrong: shared nodes, a corrupted
original, and random pointers that still point into the original.

## The four, at a glance

@tbl: The four advanced problems and the ideas they rest on. Every technique here appeared earlier in the book; what is new is the combination.
| # | Problem | Key idea | Time | Space |
|---|---|---|---|---|
| 1 | Reverse in k-groups | count first, then the standard loop | $O(n)$ | $O(n/k)$ stack |
| 2 | Rotate List | close the ring, cut elsewhere | $O(n)$ | $O(1)$ |
| 3 | Sort List | merge sort — splitting and merging are both natural | $O(n \log n)$ | $O(\log n)$ |
| 4 | Copy with random | interleave, so the copy is always `->next` | $O(n)$ | $O(1)$ |

:::interview What these four are really testing
Not whether you have seen them. Whether, when you have not, you can:

- **decompose** — "this is reversal under a counter";
- **transform** — "if I make it circular, rotation becomes a cut";
- **choose** — "merge sort, because splitting and merging are cheap here";
- **substitute** — "interleaving gives me the map without the memory".

Each of those is a move you can practise. A candidate who says *"I don't know
this one, but it looks like reversal with a bound — let me try that"* is doing
better than one who recites a memorised solution to a different problem.
:::

:::recap Chapter 32 in five lines
- Check that $k$ nodes remain **before** reversing a group; afterwards the count
  is unrecoverable.
- Making a list circular turns rotation into choosing a cut point.
- Merge sort suits lists because splitting and merging need no random access and
  no auxiliary array.
- Splitting must use the **first** middle, or a two-node list recurses forever.
- Interleaving copies with originals replaces a hash map with a `->next`.
:::

:::exercise Practise
1. Write `reverseKGroup` iteratively with a dummy node, in $O(1)$ space.
2. Reverse in k-groups but leave the final short group reversed too. Which line
   changes?
3. For rotate, what goes wrong without `k %= n`? Trace `{1,2,3}` with $k = 7$.
4. Rotate **left** by $k$ instead. What is the relationship to rotating right?
5. Implement bottom-up iterative merge sort on a list, for true $O(1)$ space.
   Why is it harder than the recursive version?
6. Why does quicksort degrade on a linked list? Which specific step is expensive?
7. Solve "copy list with random pointer" with a hash map, then compare the two
   solutions on clarity and on space.
8. In the interleaving solution, what happens if you forget step 3's restoration
   of the original list? Write the test that would catch it.
:::
