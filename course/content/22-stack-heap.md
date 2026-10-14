# The Stack, the Heap, new and delete
@short: Stack, Heap, new/delete
@subtitle: Where objects live, who owns them, and how memory leaks
@tier: foundation
@prereq: Chapter 21
@blurb: Every linked list node you will ever create lives on the heap, which means you are responsible for its life and its death. This chapter explains the two regions of memory, what `new` and `delete` really do, what a memory leak is and why it is invisible, and the three bugs — leak, dangling pointer, double free — that heap code invites. It ends with the ownership rules this book follows.
@objectives:
- Describe what lives on the stack and what lives on the heap, and why
- Use `new` and `delete`, and `new[]` and `delete[]`, correctly
- Explain what a memory leak is and why the program keeps working anyway
- Recognise dangling pointers, double frees and use-after-free
- State who owns a heap object, and what ownership obliges you to do
- Know what smart pointers do, and why this book still uses raw pointers

## Two regions

Chapter 2 previewed this. Now we do it properly.

@fig: mem_two_regions | 180 | The two regions of a running program. The stack holds one frame per active function call and is cleaned up automatically. The heap holds whatever you asked for with `new` and stays until you say otherwise.

:::definition The stack
The **stack** holds the local variables of every function currently running.
Each call pushes a **frame** containing its parameters and locals; each return
pops that frame and the memory is reclaimed immediately.

**Advantages:** no cost to manage, impossible to leak, very fast (the next
frame is already in cache).

**Limits:** the size must be known at compile time, the object dies when the
function returns, and the whole stack is small — typically 1 to 8 MB. Too many
nested calls, or one huge local array, produces a **stack overflow**.
:::

:::definition The heap
The **heap** is a large pool of memory you request from at run time with `new`
and return with `delete`.

**Advantages:** the size can be decided while the program runs, the object
lives exactly as long as you want, and the space is large — effectively all
available RAM.

**Limits:** allocation is comparatively slow, the objects are scattered (bad
for cache), and **you** must return the memory. If you forget, it is lost until
the program exits.
:::

```cpp title="Where things live"
#include <iostream>

int main() {
    int onStack = 42;                 // stack: dies at the end of main
    int arr[3] = {1, 2, 3};           // stack: 12 bytes, size fixed at compile time

    int* onHeap = new int(42);        // heap: lives until we delete it
    int* heapArr = new int[3]{1, 2, 3};  // heap: size could have been a variable

    std::cout << onStack << " " << arr[1] << "\n";
    std::cout << *onHeap << " " << heapArr[1] << "\n";

    delete onHeap;                    // give the single object back
    delete[] heapArr;                 // give the ARRAY back - note the []
    return 0;
}
```

```text nonum
42 2
42 2
```

## What new actually does

:::definition new and delete
`new T(args)` does three things:
1. asks the system for `sizeof(T)` bytes of heap memory;
2. constructs a `T` in those bytes using `args`;
3. returns a `T*` — the address of that object.

`delete p` does two things, in the opposite order:
1. destroys the object that `p` points at;
2. returns its bytes to the system.

`delete` does **not** change `p`. After `delete p`, the variable `p` still holds
the same address, but the object there is gone. That is what makes a dangling
pointer so easy to create.
:::

@fig: mem_new_delete | 170 | What `new` and `delete` do, in order. Note the last panel: `delete` frees the object but leaves the pointer holding the old address, which is why setting it to `nullptr` afterwards is a habit worth having.

:::pitfall `delete` and `delete[]` are not interchangeable
```cpp nonum frag
int* one = new int(5);
int* many = new int[5];

delete one;       // OK 
delete[] many;    // OK 

delete many;      // BAD undefined behaviour
delete[] one;     // BAD undefined behaviour
```
`new[]` records how many objects it made so that `delete[]` can destroy all of
them. Using plain `delete` on an array destroys only the first and corrupts the
allocator's bookkeeping.

The rule is mechanical: **`new` pairs with `delete`; `new[]` pairs with
`delete[]`.** Match them at the moment you write the `new`, and you will never
get it wrong.
:::

## Memory leaks

:::definition Memory leak
A **leak** is heap memory that is no longer reachable — you have lost every
pointer to it — and has not been given back.

The memory cannot be reused, because the program still "owns" it; and it cannot
be freed, because nothing knows where it is. It is lost for the lifetime of the
process.
:::

```cpp title="Three ways to leak, all of which run perfectly"
#include <iostream>

void leak1() {
    int* p = new int(42);
    // no delete - the pointer dies with the function, the memory does not
}

void leak2() {
    int* p = new int(1);
    p = new int(2);          // the first object is now unreachable
    delete p;                // frees only the second
}

void leak3(bool bad) {
    int* p = new int(3);
    if (bad) return;         // the early return skips the delete
    delete p;
}

int main() {
    for (int i = 0; i < 3; ++i) { leak1(); leak2(); leak3(true); }
    std::cout << "no crash, no error, no warning\n";
    return 0;
}
```

```text nonum
no crash, no error, no warning
```

@fig: mem_leak | 200 | A leak. The pointer variable lived on the stack and vanished when the function returned; the object it pointed to is still on the heap, and now nothing in the program knows where it is.

:::warning Why leaks are so dangerous
Notice that the program above ran correctly and printed exactly what it should.
**A leak produces no error.** There is no crash, no exception, no compiler
warning.

The symptom appears much later: a long-running process gradually consumes more
memory until the machine starts swapping, or the allocator fails. In a program
that runs for a second, you will never notice. In a server that runs for a
month, it is fatal.

The tool that finds them:
```bash nonum
g++ -std=c++17 -fsanitize=address -g prog.cpp -o prog && ./prog
```
AddressSanitizer reports every leak at exit, with the stack trace of the `new`
that created it. Valgrind (`valgrind --leak-check=full ./prog`) does the same.
Run one of them on every linked list exercise in Part VI — the whole point of
those exercises is memory discipline, and this is how you check it.
:::

## The other two heap bugs

:::warning Dangling pointers and double frees
**Use after free.**
```cpp nonum frag
int* p = new int(42);
delete p;
std::cout << *p;        // undefined behaviour - the object is gone
```
Very often this still prints 42, because the bytes have not been reused yet.
Then one day another allocation claims them and the value changes under you.

**Double free.**
```cpp nonum frag
int* p = new int(42);
delete p;
delete p;               // undefined behaviour - usually a crash, often worse
```

**The habit that prevents both:**
```cpp nonum frag
delete p;
p = nullptr;            // now a second delete is harmless, and *p crashes loudly
```
`delete nullptr` is explicitly defined to do nothing, so nulling after deleting
makes double frees safe. And dereferencing `nullptr` crashes *immediately and
visibly*, which is far better than reading stale data for an hour.
:::

@fig: mem_dangling | 160 | A dangling pointer. After `delete`, the object is gone but the pointer still holds its address. Setting the pointer to `nullptr` turns a silent, intermittent bug into an immediate, obvious one.

## Ownership

The concept that makes heap code manageable.

:::definition Ownership
The **owner** of a heap object is the piece of code responsible for deleting it.

Every heap object must have **exactly one** owner. Zero owners is a leak. Two
owners is a double free.

Other code may hold pointers to the object and use it — those are
*non-owning*, or *observing*, pointers. They must not delete, and they must not
outlive the owner.
:::

In a linked list, this is simple and absolute:

:::insight Ownership in a linked list
**The list owns its nodes.** Each node is created with `new` when it is inserted
and destroyed with `delete` when it is removed. When the whole list is
destroyed, every remaining node is deleted.

Pointers you hold temporarily while traversing — `curr`, `prev`, `temp` — are
**non-owning**. They look at nodes; they never delete them. The only exception
is the `temp` you deliberately set aside *in order to* delete it, and that is
always two lines long:

```cpp nonum frag
Node* doomed = curr;        // remember the node we are about to orphan
curr = curr->next;          // move past it
delete doomed;              // now destroy it
```
Reversing those lines — deleting before moving — reads `curr->next` through a
freed pointer. That specific bug is the subject of Chapter 26, and it is worth
arriving there having already seen it.
:::

```cpp title="A list that owns and frees its nodes"
#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};

int main() {
    // Build 10 -> 20 -> 30 on the heap.
    Node* head = new Node(10);
    head->next = new Node(20);
    head->next->next = new Node(30);

    for (Node* curr = head; curr != nullptr; curr = curr->next)
        std::cout << curr->data << " ";
    std::cout << "\n";

    // Destroy every node. Three nodes created, three deleted.
    Node* curr = head;
    while (curr != nullptr) {
        Node* doomed = curr;        // hold on to it
        curr = curr->next;          // step past it FIRST
        delete doomed;              // now it is safe to destroy
    }
    head = nullptr;                 // the list is empty, say so
    std::cout << "all nodes freed\n";
    return 0;
}
```

```text nonum
10 20 30 
all nodes freed
```

Count them: three `new`s and three `delete`s. That balance is what you are
aiming for in every program in Part VI, and AddressSanitizer will tell you
whether you achieved it.

## Smart pointers, and why this book uses raw ones

Modern C++ rarely writes `new` and `delete` by hand.

```cpp title="The same object, managed automatically"
#include <iostream>
#include <memory>

int main() {
    std::unique_ptr<int> p = std::make_unique<int>(42);
    std::cout << *p << "\n";
    // no delete needed - p frees it when p goes out of scope
    return 0;
}
```

```text nonum
42
```

:::definition RAII
**Resource Acquisition Is Initialisation**: tie a resource's lifetime to an
object's lifetime, so that the destructor releases it automatically.

`std::unique_ptr` is a tiny object holding one pointer, whose destructor calls
`delete`. Because the destructor runs whenever the `unique_ptr` goes out of
scope — including when an exception unwinds the stack — the memory cannot leak.

This is why `std::vector` never leaks either: it owns its block, and its
destructor frees it.
:::

:::insight Why Part VI still uses raw pointers
In production code, a linked list node should be managed by a smart pointer or,
more sensibly, you should use `std::list` and not write one at all.

This book uses raw `new` and `delete` for three reasons:

1. **Every interview uses raw pointers.** The linked list questions in Chapter 30
   onwards are posed with `ListNode*`, universally.
2. **You cannot appreciate what RAII saves you from until you have done it by
   hand.** Learning `unique_ptr` first teaches you a tool; learning it second
   teaches you a relief.
3. **The pointer manipulation is the lesson.** `unique_ptr` would add move
   semantics to every reversal and obscure the three-line pointer dance that is
   the entire point.

So: raw pointers here, deliberately, with the discipline to match. In your own
projects, prefer the standard containers and smart pointers.
:::

## Cost summary

@tbl: Stack versus heap. Note that "slow" and "fast" here are relative — a heap allocation is perhaps 20–100 nanoseconds, which only matters when you do millions of them.
| | Stack | Heap |
|---|---|---|
| Allocation cost | essentially free | relatively slow |
| Size known at | compile time | run time |
| Lifetime | until the function returns | until you `delete` |
| Typical total size | 1–8 MB | all available RAM |
| Can leak | no | yes |
| Cache behaviour | excellent | scattered |
| Used for | locals, fixed arrays, the pointer itself | linked list nodes, `std::vector`'s block |

:::recap Chapter 22 in seven lines
- The **stack** is automatic, fast, small and short-lived; the **heap** is
  manual, large and lives as long as you choose.
- `new` allocates and constructs; `delete` destroys and frees. They must be
  balanced exactly.
- `new[]` pairs with `delete[]`, always.
- A **leak** is unreachable, unfreed memory. It produces no error at all — use
  `-fsanitize=address`.
- `delete` does not change the pointer. Set it to `nullptr` afterwards and two
  classes of bug disappear.
- Every heap object has **exactly one owner**; everybody else holds non-owning
  pointers.
- When deleting a list node: step past it **first**, then delete.
:::

:::exercise Practise
1. Which of these live on the stack and which on the heap?
   `int x;` · `int* p = new int;` · `std::vector<int> v;` · the elements inside
   `v` · `Node* head;` · the node `head` points to.
2. Write a program that leaks exactly 40 bytes. Compile it with
   `-fsanitize=address` and read the report.
3. Fix `leak2` and `leak3` from this chapter. For `leak3`, give two different
   fixes and say which you prefer.
4. What does `delete nullptr;` do? Why is that useful?
5. Build a list of five nodes and free it. Verify with AddressSanitizer that
   nothing leaks. Then deliberately break the free loop by deleting before
   advancing, and read the error it produces.
6. Why can a recursive function cause a stack overflow when an iterative one
   with the same complexity does not? Roughly how deep can recursion go with a
   1 MB stack and a 64-byte frame?
7. Rewrite the three-node list of this chapter using `std::unique_ptr`. What
   becomes easier, and what becomes harder?
8. Explain why the snippet below leaks, even though it contains a `delete`.
:::

```cpp title="For exercise 8 — one delete is not enough" nonum frag
Node* head = new Node(1);
head->next = new Node(2);
delete head;
```
