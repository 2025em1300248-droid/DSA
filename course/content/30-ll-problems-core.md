# Essential Linked List Problems I
@short: Core List Problems
@subtitle: The six that are asked most often
@tier: practice
@prereq: Chapter 29
@blurb: Six problems that between them account for a large share of all linked list interview questions. Each is solved with one of the patterns from Chapter 29, and each is presented the way you should present it: statement, approach, code, edge cases, cost, and the mistake it invites.
@objectives:
- Solve reverse, middle, cycle, cycle II, merge two sorted and remove nth from end
- Pick the right pattern for each from the problem statement alone
- Handle the empty list and the single-node list in every one
- Give the complexity and the space without being asked
- Recognise which of these appear as sub-steps in the harder problems later

## 1. Reverse Linked List

**Statement.** Reverse a singly linked list and return the new head.

**Pattern.** Pointer reversal — three pointers, four lines. Chapter 28 covers
every detail; this is the version with the LeetCode signature.

```cpp title="Reverse Linked List"
Node* reverseList(Node* head) {
    Node* prev = nullptr;
    Node* curr = head;
    while (curr != nullptr) {
        Node* nextNode = curr->next;
        curr->next = prev;
        prev = curr;
        curr = nextNode;
    }
    return prev;          // prev is the new head
}
```

**Edge cases.** Empty list returns `nullptr`; one node returns itself. Both work
with no special case.

**Cost.** $O(n)$ time, $O(1)$ space. The recursive version is $O(n)$ stack.

**Watch for.** Returning `head` instead of `prev`. Forgetting to save
`nextNode`.

**Appears inside.** Palindrome check, reorder list, reverse in k-groups, add two
numbers (one formulation). Learn it until it is automatic.

## 2. Middle of the Linked List

**Statement.** Return the middle node. For even lengths, return the second
middle.

**Pattern.** Fast and slow pointers.

```cpp title="Middle of the Linked List"
Node* middleNode(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}
```

**Edge cases.** Empty returns `nullptr`. One node returns itself.

**Cost.** $O(n)$ time, $O(1)$ space, one pass.

**Watch for.** The two-pass version (count, then walk $n/2$) is correct and
costs the same asymptotically — say so, then give the one-pass version as the
improvement.

**Appears inside.** Palindrome check, reorder list, sort list.

## 3. Linked List Cycle

**Statement.** Does the list contain a cycle?

**Pattern.** Floyd's algorithm, phase 1.

```cpp title="Linked List Cycle"
bool hasCycle(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;
}
```

**Cost.** $O(n)$ time, $O(1)$ space. The hash-set version is $O(n)$ space —
mention it, then improve on it.

**Watch for.** Comparing `slow->data == fast->data` instead of the pointers.

## 4. Linked List Cycle II

**Statement.** Return the node where the cycle begins, or `nullptr`.

**Pattern.** Floyd's algorithm, both phases. The proof ($F = nL - a$) is in
Chapter 29 and is worth being able to state.

```cpp title="Linked List Cycle II"
Node* detectCycle(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {
            slow = head;                 // phase 2
            while (slow != fast) {       // both move ONE step
                slow = slow->next;
                fast = fast->next;
            }
            return slow;
        }
    }
    return nullptr;
}
```

**Cost.** $O(n)$ time, $O(1)$ space.

**Watch for.** Leaving `fast` at double speed in phase 2.

**Related.** "Find the duplicate number" in Chapter 19 is this exact algorithm
applied to an array read as a linked list.

### Removing a cycle

A natural follow-up, and it needs one extra idea: to break the cycle you must
reach the node **just before** the entrance.

@fig: ll_remove_cycle | 176 | Removing a cycle. Finding the entrance is not enough; you need the last node of the loop — the one pointing back at the entrance — so that you can set its `next` to `nullptr`.

```cpp title="Detect, then remove, a cycle"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* detectCycle(Node* head) {
    Node* slow = head; Node* fast = head;
    while (fast && fast->next) {
        slow = slow->next; fast = fast->next->next;
        if (slow == fast) {
            slow = head;
            while (slow != fast) { slow = slow->next; fast = fast->next; }
            return slow;
        }
    }
    return nullptr;
}

// Breaks the cycle if there is one. Returns whether one was removed.
bool removeCycle(Node* head) {
    Node* start = detectCycle(head);
    if (start == nullptr) return false;
    Node* last = start;
    while (last->next != start)      // walk round to the node before the entrance
        last = last->next;
    last->next = nullptr;            // break it
    return true;
}

int main() {
    Node* a = new Node(1);
    a->next = new Node(2);
    a->next->next = new Node(3);
    a->next->next->next = new Node(4);
    a->next->next->next->next = a->next;     // 4 -> 2

    std::cout << "entrance: " << detectCycle(a)->data << "\n";
    std::cout << "removed:  " << removeCycle(a) << "\n";
    std::cout << "again:    " << removeCycle(a) << "\n";
    for (Node* c = a; c; c = c->next) std::cout << c->data << " ";
    std::cout << "\n";
    while (a) { Node* d = a; a = a->next; delete d; }
    return 0;
}
```

```text nonum
entrance: 2
removed:  1
again:    0
1 2 3 4 
```

Three things to notice. `removeCycle` is **idempotent**: calling it again
returns `0` because `detectCycle` now finds nothing, and the list is left alone.
The walk `while (last->next != start)` goes all the way round the loop, so it is
$O(L)$ where $L$ is the cycle length. And once the cycle is broken, the ordinary
free loop works again — which it did not before.

## 5. Merge Two Sorted Lists

**Statement.** Merge two sorted lists into one sorted list, by relinking.

**Pattern.** Dummy node plus merge.

```cpp title="Merge Two Sorted Lists"
Node* mergeTwoLists(Node* a, Node* b) {
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
```

**Edge cases.** Either list empty — handled by the final line, which attaches
the non-empty remainder (or `nullptr` if both are exhausted).

**Cost.** $O(n + m)$ time, $O(1)$ space. No nodes are created.

**Watch for.** `<=` rather than `<` keeps the merge **stable** — equal elements
from `a` come before equal elements from `b`. It matters for merge sort.

**Appears inside.** Sort list (Chapter 32), merge $k$ sorted lists.

## 6. Remove Nth Node From End

**Statement.** Remove the $n$-th node from the end and return the head.

**Pattern.** Fixed gap, plus a dummy node — because the node to remove might be
the head.

@fig: ll_remove_nth | 182 | Remove nth from end. The gap is set to $n+1$ *from the dummy*, so that the trailing pointer stops on the node **before** the one to delete — which is what you need in order to unlink it.

:::insight Why the gap is $n + 1$, and why the dummy matters
To delete a node you need its predecessor. So the trailing pointer must stop one
node *earlier* than the target, which means a gap of $n + 1$ rather than $n$.

Starting the trailing pointer at the dummy rather than the head means that even
when the target *is* the head, there is still a predecessor to work with. Without
the dummy you would need a separate branch for "remove the first node", and that
branch is where the bug would be.
:::

```cpp title="Remove the nth node from the end, one pass"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

Node* removeNthFromEnd(Node* head, int n) {
    Node dummy(0);
    dummy.next = head;
    Node* lead = &dummy;
    Node* trail = &dummy;

    for (int i = 0; i <= n; ++i) {        // n+1 steps: note the <=
        if (lead == nullptr) return head; // n is larger than the list
        lead = lead->next;
    }
    while (lead != nullptr) {             // move together, keeping the gap
        lead = lead->next;
        trail = trail->next;
    }
    Node* doomed = trail->next;           // trail is the predecessor
    trail->next = doomed->next;
    delete doomed;
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
    Node* a = buildList({1, 2, 3, 4, 5});
    a = removeNthFromEnd(a, 2);          // remove 4
    printList(a); freeList(a);

    Node* b = buildList({1, 2, 3});
    b = removeNthFromEnd(b, 3);          // remove the head
    printList(b); freeList(b);

    Node* c = buildList({1});
    c = removeNthFromEnd(c, 1);          // the list becomes empty
    printList(c); freeList(c);
    return 0;
}
```

```text nonum
1 -> 2 -> 3 -> 5
2 -> 3
(empty)
```

**Cost.** $O(n)$ time, $O(1)$ space, one pass.

**Watch for.** `i <= n` in the first loop, not `i < n`. Returning `dummy.next`,
not `head` — the third test case shows why: `head` has been deleted.

## The six, at a glance

@tbl: The six core problems. Four patterns cover all of them, and each appears again as a step inside the harder problems of Chapters 31 and 32.
| # | Problem | Pattern | Time | Space |
|---|---|---|---|---|
| 1 | Reverse Linked List | pointer reversal | $O(n)$ | $O(1)$ |
| 2 | Middle of the List | fast and slow | $O(n)$ | $O(1)$ |
| 3 | Linked List Cycle | Floyd phase 1 | $O(n)$ | $O(1)$ |
| 4 | Linked List Cycle II | Floyd both phases | $O(n)$ | $O(1)$ |
| 5 | Merge Two Sorted Lists | dummy + merge | $O(n+m)$ | $O(1)$ |
| 6 | Remove Nth From End | gap + dummy | $O(n)$ | $O(1)$ |

:::interview Every one of these is $O(1)$ space
That is not a coincidence — it is what linked list questions are *for*. An
interviewer asking a list question is almost always checking whether you can
manipulate pointers without allocating anything.

So if your solution builds a vector of nodes, or uses a hash set, expect the
follow-up *"now without the extra space"*. Give the $O(n)$-space version if it
comes to you first, say that it is $O(n)$ space, and then improve it. That
sequence — working solution, honest cost, improvement — is the whole performance.
:::

:::exercise Practise
1. Write all six from memory. Test each on: empty, one node, two nodes.
2. For problem 2, write the two-pass version and compare the code length. Which
   would you give first in an interview, and why?
3. For problem 6, what should happen if $n$ is larger than the list? What does
   the code above do? Is that the right choice?
4. Solve problem 3 with a hash set instead. What is the space, and when would
   you actually prefer it?
5. Merge **three** sorted lists. Compare merging them one at a time with a
   divide-and-conquer merge. What are the two complexities?
6. For problem 4, construct a list where the cycle is the entire list (the last
   node points at the head). What does `detectCycle` return?
7. Write `removeCycle` without first calling `detectCycle` — can you break the
   cycle using only the meeting point from phase 1? Why or why not?
:::
