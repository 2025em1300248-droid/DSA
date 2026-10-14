# The Linked List Patterns
@short: Linked List Patterns
@subtitle: Six techniques that between them solve almost every list problem
@tier: core
@prereq: Part VI
@blurb: Linked list problems have far fewer patterns than array problems, and they repeat relentlessly. Learn the dummy node, the two speeds, pointer reversal, the gap, Floyd's cycle algorithm and merge-and-split, and you have the tools for every problem in Chapters 30 to 32 — including the ones you have not seen.
@objectives:
- Use a dummy node to remove every head-is-special branch
- Use fast and slow pointers to find the middle in one pass
- Use a fixed gap between two pointers to find the $k$-th node from the end
- Apply Floyd's cycle detection, and **prove** why phase 2 finds the entrance
- Merge two sorted lists, and split one list into two
- Choose recursion knowingly, given its $O(n)$ stack cost

## Pattern 1: The dummy node

This is the single most useful trick in linked list programming, and Part VI has
been building the case for it.

:::definition The problem it solves
Almost every list operation needs a node's **predecessor**. Every node has one
except the head, so every function ends up with a separate branch for the head
— doubling the code and hiding most of the bugs.
:::

:::insight Give the head a predecessor
Create one extra node, on the stack, whose `next` is the real head:

```cpp nonum frag
Node dummy(0);
dummy.next = head;
```

Now **every** real node has a predecessor, including the first. The special case
disappears, because there is no longer a special case to handle.

At the end, the answer is `dummy.next` — which is automatically correct even if
the original head was deleted, and even if the list is now empty.
:::

@fig: pat_dummy | 180 | The dummy node. One fake node in front means the real head is no longer exceptional; every node can be reached as `prev->next` for some `prev`, so one uniform loop handles everything.

### The same function, with and without

```cpp title="Remove every node equal to val — the two versions"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// WITHOUT a dummy: two loops, one of which exists only for the head.
Node* removeAllPlain(Node* head, int val) {
    while (head != nullptr && head->data == val) {   // branch 1: the head
        Node* doomed = head;
        head = head->next;
        delete doomed;
    }
    if (head == nullptr) return nullptr;
    Node* prev = head;                                // branch 2: everything else
    while (prev->next != nullptr) {
        if (prev->next->data == val) {
            Node* doomed = prev->next;
            prev->next = doomed->next;
            delete doomed;
        } else {
            prev = prev->next;
        }
    }
    return head;
}

// WITH a dummy: one loop, no special case at all.
Node* removeAllDummy(Node* head, int val) {
    Node dummy(0);
    dummy.next = head;
    Node* prev = &dummy;
    while (prev->next != nullptr) {
        if (prev->next->data == val) {
            Node* doomed = prev->next;
            prev->next = doomed->next;
            delete doomed;
        } else {
            prev = prev->next;
        }
    }
    return dummy.next;          // correct even if every node was removed
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
    Node* a = buildList({7, 7, 1, 7, 2, 7});
    a = removeAllPlain(a, 7);  printList(a);  freeList(a);

    Node* b = buildList({7, 7, 1, 7, 2, 7});
    b = removeAllDummy(b, 7);  printList(b);  freeList(b);

    Node* c = buildList({7, 7, 7});          // everything removed
    c = removeAllDummy(c, 7);  printList(c);  freeList(c);
    return 0;
}
```

```text nonum
1 -> 2
1 -> 2
(empty)
```

Same answers, and the second function is half the length with one loop instead
of two. Count the `delete`s: the dummy version has one, the plain version has
two, which is one fewer place to get wrong.

:::pitfall Three details about dummy nodes
**Put it on the stack.** `Node dummy(0);` is a local object; it is destroyed
automatically. `new Node(0)` would need deleting, and forgetting is a leak.

**Return `dummy.next`, never `head`.** After the loop, `head` may name a node
that has been deleted. `dummy.next` is always the current first node.

**Never delete the dummy itself.** It is a stack object; `delete &dummy` is
undefined behaviour. The loop condition `prev->next != nullptr` naturally never
offers it for deletion, because nothing points *to* it.
:::

:::interview Reach for it immediately
Whenever a problem might change, delete or insert before the **first** node —
remove nth from end, remove duplicates, merge two lists, partition, add two
numbers — start by writing the dummy. It costs one line and removes a whole
category of bug.

Interviewers recognise it instantly as a sign that you have written list code
before.
:::

## Pattern 2: Fast and slow pointers

:::definition The two-speed walk
Move one pointer one node at a time and another two nodes at a time. When the
fast pointer reaches the end, the slow one is at the **middle**.

Why: the fast pointer covers twice the distance, so when it has travelled $n$
the slow one has travelled $n/2$.
:::

@fig: pat_fast_slow | 176 | Fast and slow. After three steps the fast pointer has run off the end and the slow one is exactly halfway. One pass, no length count, $O(1)$ space.

```cpp title="Find the middle in one pass"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// For an even length, returns the SECOND middle (1,2,3,4 -> 3).
Node* middleNode(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}

// For an even length, returns the FIRST middle (1,2,3,4 -> 2).
Node* firstMiddle(Node* head) {
    if (head == nullptr) return nullptr;
    Node* slow = head;
    Node* fast = head->next;             // the one-step head start does it
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}

Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* odd = buildList({1, 2, 3, 4, 5});
    std::cout << middleNode(odd)->data << " " << firstMiddle(odd)->data << "\n";
    Node* even = buildList({1, 2, 3, 4});
    std::cout << middleNode(even)->data << " " << firstMiddle(even)->data << "\n";
    Node* one = buildList({9});
    std::cout << middleNode(one)->data << "\n";
    freeList(odd); freeList(even); freeList(one);
    return 0;
}
```

```text nonum
3 3
3 2
9
```

:::pitfall The loop condition, and the order of its two tests
```cpp nonum skip
while (fast != nullptr && fast->next != nullptr)
```
Both tests are needed, and **in that order**:
- `fast != nullptr` guards the even-length case, where `fast` lands exactly on
  `nullptr`.
- `fast->next != nullptr` guards the odd-length case, where `fast` lands on the
  last node and `fast->next->next` would dereference null.

Short-circuit evaluation means the second test only runs if the first passed, so
writing them the other way round crashes on an even-length list.

Which middle you get for even lengths depends on where `fast` starts: `head`
gives the second middle, `head->next` gives the first. Problems care — "split
the list in half" usually wants the **first** middle so the two halves come out
right.
:::

## Pattern 3: The fixed gap

:::definition Two pointers $k$ apart
Advance one pointer $k$ nodes. Then move both one step at a time. When the
leading pointer reaches the end, the trailing one is exactly $k$ nodes from the
end.

This is how you find the $k$-th node from the end **in one pass**, without
knowing the length.
:::

@fig: pat_gap | 170 | The fixed gap. The lead pointer is sent $k$ nodes ahead; the two then move in lockstep, so the gap is preserved. When the lead falls off the end, the trailing pointer is $k$ from the end.

```cpp title="The k-th node from the end, one pass"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// Returns the k-th node from the end (k = 1 is the last), or nullptr.
Node* kthFromEnd(Node* head, int k) {
    Node* lead = head;
    for (int i = 0; i < k; ++i) {
        if (lead == nullptr) return nullptr;   // the list is shorter than k
        lead = lead->next;
    }
    Node* trail = head;
    while (lead != nullptr) {                  // keep the gap, move together
        lead = lead->next;
        trail = trail->next;
    }
    return trail;
}

Node* buildList(std::initializer_list<int> vs) {
    Node* head = nullptr; Node* tail = nullptr;
    for (int v : vs) { Node* n = new Node(v);
        if (!head) head = tail = n; else { tail->next = n; tail = n; } }
    return head;
}
void freeList(Node* head) { while (head) { Node* d = head; head = head->next; delete d; } }

int main() {
    Node* h = buildList({10, 20, 30, 40, 50});
    std::cout << kthFromEnd(h, 1)->data << "\n";    // the last
    std::cout << kthFromEnd(h, 2)->data << "\n";
    std::cout << kthFromEnd(h, 5)->data << "\n";    // the first
    std::cout << (kthFromEnd(h, 6) ? "found" : "too short") << "\n";
    freeList(h);
    return 0;
}
```

```text nonum
50
40
10
too short
```

$O(n)$ time, $O(1)$ space, **one pass**. The two-pass alternative — count the
length, then walk $n - k$ nodes — is equally $O(n)$ and is a perfectly good
answer; the one-pass version is what the question is usually fishing for.

## Pattern 4: Floyd's cycle detection

:::definition The problem
A list may have a cycle: some node's `next` points back to an earlier node.
Detect it, and find where the cycle begins, in $O(1)$ space.
:::

A hash set of visited nodes solves it in $O(n)$ space. Floyd's algorithm — the
"tortoise and hare" — does it in $O(1)$, and the proof is one of the most
satisfying short arguments in the subject.

@fig: pat_floyd | 190 | Floyd's algorithm. Phase 1: the fast pointer gains one node per step on the slow one, so inside the cycle it must eventually catch it. Phase 2: restarting one pointer at the head and moving both one step at a time makes them meet exactly at the cycle's entrance.

### Phase 1: is there a cycle?

Move `slow` by one and `fast` by two. If there is no cycle, `fast` falls off the
end. If there is, `fast` enters the cycle, and then **gains exactly one node per
step** on `slow` — so the distance between them shrinks by one each step and
must reach zero. They meet.

:::insight Why a two-speed chase always catches
Once both are inside the cycle, consider the gap from `slow` to `fast` measured
forwards around the loop. Each step, `slow` advances 1 and `fast` advances 2, so
the gap shrinks by exactly 1.

A gap that decreases by exactly 1 each step cannot skip over zero. So they
coincide within at most $L$ steps, where $L$ is the cycle length.

This is also why speed 3 would be a worse choice: the gap would shrink by 2 and
*could* skip zero, so it would need a divisibility argument to be correct.
Speeds 1 and 2 are the simple case, which is why the algorithm uses them.
:::

### Phase 2: where does the cycle start?

This is the part that looks like magic. It is not.

:::definition The proof
Let $F$ be the distance from the head to the cycle entrance, $a$ the distance
from the entrance to the meeting point (measured forwards round the cycle), and
$L$ the cycle length.

When they meet, `slow` has travelled $F + a$ and `fast` has travelled
$F + a + nL$ for some whole number $n \ge 1$ — the extra laps it made.

`fast` moved twice as far:
$$2(F + a) = F + a + nL$$
$$F + a = nL$$
$$F = nL - a$$

Now read that last line. $nL - a$ is *"go round the cycle $n$ times and come
back $a$ short"* — which, starting from the meeting point, lands exactly on the
entrance.

So: a pointer starting at the head and walking $F$ steps reaches the entrance.
A pointer starting at the meeting point and walking the same $F$ steps also
reaches the entrance. **Move both one step at a time, and they meet there.**
:::

@fig: pat_floyd_proof | 184 | The distances in Floyd's proof. $F = nL - a$ is the whole argument: from the meeting point, $F$ steps is some whole number of laps minus $a$, which lands on the entrance.

```cpp title="Detect a cycle, and find its entrance"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

bool hasCycle(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;      // compare NODES, not values
    }
    return false;
}

// Returns the first node of the cycle, or nullptr if there is none.
Node* cycleStart(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {                 // phase 1 found a meeting point
            slow = head;                    // phase 2: restart one at the head
            while (slow != fast) {          // both move ONE step now
                slow = slow->next;
                fast = fast->next;
            }
            return slow;
        }
    }
    return nullptr;
}

int main() {
    Node* a = new Node(1);
    a->next = new Node(2);
    a->next->next = new Node(3);
    a->next->next->next = new Node(4);
    a->next->next->next->next = a->next;      // 4 points back at 2

    std::cout << hasCycle(a) << "\n";
    std::cout << cycleStart(a)->data << "\n";

    Node* b = new Node(1);
    b->next = new Node(2);
    std::cout << hasCycle(b) << "\n";
    std::cout << (cycleStart(b) == nullptr ? "no cycle" : "?") << "\n";

    a->next->next->next->next = nullptr;      // break it before freeing
    while (a) { Node* d = a; a = a->next; delete d; }
    while (b) { Node* d = b; b = b->next; delete d; }
    return 0;
}
```

```text nonum
1
2
0
no cycle
```

:::pitfall Three things about cycle code
**Compare pointers, not values.** `slow == fast` compares addresses. `slow->data
== fast->data` would be true for any two nodes holding the same number.

**In phase 2, both pointers move one step.** Keeping `fast` at double speed is
the most common error, and it finds the wrong node.

**You cannot free a cyclic list with the normal loop.** It never terminates, and
it frees nodes twice. Break the cycle first, as the program above does, or the
AddressSanitizer report will be dramatic.
:::

## Pattern 5: Merge and split

Merging two sorted lists is the engine of merge sort on lists, and is worth
writing once properly.

@fig: pat_merge | 176 | Merging two sorted lists. A dummy node means there is no "is this the first output node?" case; `tail` always has somewhere to attach. Each step takes the smaller front node and advances that list.

```cpp title="Merge two sorted lists, and split one in half"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

// Merges two sorted lists by RELINKING - no new nodes are created.
Node* mergeSorted(Node* a, Node* b) {
    Node dummy(0);
    Node* tail = &dummy;
    while (a != nullptr && b != nullptr) {
        if (a->data <= b->data) { tail->next = a; a = a->next; }
        else                    { tail->next = b; b = b->next; }
        tail = tail->next;
    }
    tail->next = (a != nullptr) ? a : b;   // attach whatever is left, in one go
    return dummy.next;
}

// Splits the list in half; returns the head of the second half.
Node* splitHalf(Node* head) {
    if (head == nullptr || head->next == nullptr) return nullptr;
    Node* slow = head;
    Node* fast = head->next;               // the FIRST middle, so halves are even
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    Node* second = slow->next;
    slow->next = nullptr;                  // cut the first half loose
    return second;
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
    Node* a = buildList({1, 3, 5});
    Node* b = buildList({2, 4, 6, 8});
    Node* m = mergeSorted(a, b);
    printList(m);

    Node* second = splitHalf(m);
    printList(m);
    printList(second);

    freeList(m);
    freeList(second);

    Node* e = buildList({1, 2});
    printList(mergeSorted(e, nullptr));     // one side empty
    freeList(e);
    return 0;
}
```

```text nonum
1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 8
1 -> 2 -> 3 -> 4
5 -> 6 -> 8
1 -> 2
```

:::insight Relinking, not copying
`mergeSorted` creates **no new nodes**. It rearranges the `next` pointers of
the nodes that already exist, which is why it is $O(1)$ space.

This is the structural advantage a linked list genuinely has over an array:
merging two sorted arrays needs an output array of size $n + m$, but merging two
sorted lists needs nothing. The same property makes `std::list::splice` $O(1)$
— moving a whole range between lists is four pointer updates, regardless of its
length.

Note also the single line `tail->next = (a != nullptr) ? a : b;`. With arrays
you would need two tail loops to copy the remainder. Here the remainder is
already a correctly-linked list, so one pointer attaches all of it.
:::

## Pattern 6: Recursion on lists

A list is a recursive structure: a node, followed by a smaller list. So every
list algorithm has a recursive form.

```cpp title="Three operations, recursively"
int length(Node* head) {
    if (head == nullptr) return 0;
    return 1 + length(head->next);
}

void printReverse(Node* head) {
    if (head == nullptr) return;
    printReverse(head->next);        // go all the way down first...
    std::cout << head->data << " ";  // ...then print on the way back out
}

Node* mergeRec(Node* a, Node* b) {
    if (a == nullptr) return b;
    if (b == nullptr) return a;
    if (a->data <= b->data) { a->next = mergeRec(a->next, b); return a; }
    else                    { b->next = mergeRec(a, b->next); return b; }
}
```

`printReverse` is the one worth studying: it prints a list backwards without
reversing it and without any extra data structure. The call stack *is* the
storage — which is precisely why it is $O(n)$ space, not $O(1)$.

:::warning Recursion depth is real
Every recursive list function uses one stack frame per node. With a typical
64-byte frame and a 1 MB stack, that is roughly **16,000 nodes** before a stack
overflow.

For an interview on a 5-node example, recursion is elegant and fine. For
production code on real data, it is a crash waiting for a big enough input.

**Say this out loud when you give a recursive answer.** "This is $O(n)$ stack,
so on a very long list I would use the iterative version" turns a liability into
evidence of judgement.
:::

## The pattern map

@tbl: The six patterns and the problems they unlock. Chapters 30 to 32 work through all of these.
| Pattern | Use it for | Cost |
|---|---|---|
| Dummy node | anything that may change the head | $O(1)$ extra |
| Fast and slow | middle, cycle detection, splitting in half | $O(1)$ |
| Fixed gap | $k$-th from the end, remove nth from end | $O(1)$ |
| Floyd's algorithm | cycle detection and cycle entrance | $O(1)$ |
| Merge / split | merge two sorted, sort a list, reorder | $O(1)$ |
| Recursion | reverse, merge, add two numbers | $O(n)$ stack |
| Pointer reversal | reverse, palindrome, reverse in k-groups | $O(1)$ |

:::recap Chapter 29 in six lines
- A **dummy node** gives the head a predecessor and deletes an entire class of
  special case. Return `dummy.next`.
- **Fast and slow** finds the middle in one pass; the loop condition needs both
  tests, in order.
- Starting `fast` at `head` gives the second middle; at `head->next`, the first.
- A **fixed gap** of $k$ finds the $k$-th from the end in one pass.
- **Floyd's** phase 2 works because $F = nL - a$; both pointers move one step in
  it.
- **Merging relinks** rather than copying, which is why it is $O(1)$ space —
  and why `splice` is $O(1)$.
:::

:::exercise Practise
1. Rewrite `deleteValue` from Chapter 26 using a dummy node. How many lines
   disappear?
2. Why must a dummy node live on the stack rather than the heap? What happens if
   you `new` it and forget to delete it?
3. Modify `middleNode` to return the first middle on even lengths without the
   `head->next` trick. Which is clearer?
4. In `kthFromEnd`, what should happen when $k = 0$? When $k$ is negative? Add
   the checks.
5. Write out Floyd's proof in your own words, defining $F$, $a$ and $L$ in a
   drawing.
6. Why is speed 2 used in Floyd's rather than speed 3? Give the gap argument.
7. Write `mergeSorted` so it produces a **descending** list. What changes?
8. Write `length` iteratively and recursively. At what list length does the
   recursive one crash on your machine? Measure it.
:::
