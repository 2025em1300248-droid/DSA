# Pointers, References and Dereferencing
@short: Pointers
@subtitle: A variable whose value is an address
@tier: foundation
@prereq: Chapter 2
@blurb: Almost nobody struggles with linked lists. They struggle with pointers, and then meet linked lists before anybody has explained pointers properly. This chapter does that: what a pointer is, what `&` and `*` really do, why `nullptr` exists, how `->` differs from `.`, and the exact difference between passing by value, by reference and by pointer. Nothing here is advanced, and nothing after it works without it.
@objectives:
- Say what a pointer stores, in one sentence
- Use `&` and `*` correctly, and explain why they are opposites
- Read any pointer declaration out loud
- Explain `nullptr`, and what happens when you dereference it
- Use `->` on a pointer to a struct, and say why `.` would not compile
- Choose between passing by value, by reference and by pointer, with a reason
- Recognise a dangling pointer and an uninitialised pointer

## The one-sentence definition

:::definition Pointer
A **pointer** is a variable whose value is a memory address.

That is the whole idea. A normal `int` variable holds a number like 42. A
pointer holds a number like 1000, and that number is understood as *"the place
where something lives"*.
:::

@fig: ptr_what_is | 165 | A variable and a pointer to it. `x` holds 42 and lives at address 1000. `p` holds 1000 and lives somewhere else entirely. The arrow in every diagram in this book means "the value in this box is the address of that box".

```cpp title="Your first pointer" norun
#include <iostream>

int main() {
    int x = 42;
    int* p = &x;          // p holds the ADDRESS of x

    std::cout << "x  = " << x  << "\n";   // 42       - the value
    std::cout << "&x = " << &x << "\n";   // 0x...    - where x lives
    std::cout << "p  = " << p  << "\n";   // the same address
    std::cout << "*p = " << *p << "\n";   // 42       - follow p, read what is there
    return 0;
}
```

A possible run:

```text nonum
x  = 42
&x = 0x7ffd3b2a1c4c
p  = 0x7ffd3b2a1c4c
*p = 42
```

`p` and `&x` print the same thing, because that is exactly what `p` was set to.
And `*p` prints 42, because following the address leads to `x`.

## The two operators

Everything about pointers is these two symbols, and they are **opposites**.

:::definition `&` and `*`
`&x` — the **address-of** operator. Read it as *"the address of x"*. It takes a
variable and gives you where it lives.

`*p` — the **dereference** operator. Read it as *"the thing at p"*. It takes an
address and gives you the variable there.

They undo each other: `*(&x)` is just `x`.
:::

@fig: ptr_operators | 150 | The two operators as a round trip. `&` goes from a variable to its address; `*` goes from an address back to the variable. Applying one and then the other returns you to where you started.

:::pitfall `*` means two different things
```cpp nonum frag
int* p = &x;      // in a DECLARATION: "p is a pointer to int"
*p = 99;          // in an EXPRESSION:  "the thing at p"
```
Same character, unrelated jobs. In a declaration it is part of the type. In an
expression it is the dereference operator.

This is genuinely confusing and there is no trick — you simply learn to ask
*"am I declaring something, or doing something?"*

One more wrinkle. These two declarations are identical:
```cpp nonum frag
int* a;
int *b;
```
The space means nothing. This book writes `int* p` because it groups the `*`
with the type, which is how you should *think* about it. But beware:
```cpp nonum frag
int* a, b;        // a is int*, b is a plain int. The * applies to a only.
```
Declare one pointer per line and the problem never arises.
:::

## Dereferencing changes the original

This is the point of pointers, so it deserves its own demonstration.

```cpp title="Writing through a pointer"
#include <iostream>

int main() {
    int x = 42;
    int* p = &x;

    *p = 99;                   // write 99 to WHEREVER p points - that is x

    std::cout << "x  = " << x  << "\n";
    std::cout << "*p = " << *p << "\n";
    return 0;
}
```

```text nonum
x  = 99
*p = 99
```

We never mentioned `x` on the line that changed it. We changed the thing at
address `p`, and that thing *is* `x`. This is how a function can modify a
variable belonging to its caller, and it is how a linked list node can be
rewired without copying anything.

## nullptr: a pointer to nothing

:::definition nullptr
`nullptr` is a special pointer value meaning **"this points at nothing"**.

It is not address 0 in any meaningful sense, and it is not an uninitialised
pointer. It is a deliberate, checkable marker for *absent*.

Use it for: the end of a linked list; a function that may fail to find
something; an optional reference to an object that might not exist.
:::

```cpp title="nullptr, and checking before you follow"
#include <iostream>

int main() {
    int* p = nullptr;

    if (p == nullptr) std::cout << "p points at nothing\n";
    if (!p)           std::cout << "and this is the same check\n";

    int x = 7;
    p = &x;                            // now it points somewhere real
    if (p) std::cout << "*p = " << *p << "\n";
    return 0;
}
```

```text nonum
p points at nothing
and this is the same check
*p = 7
```

A pointer converts to `bool` as *"do I point at something?"*, so `if (p)` and
`if (p != nullptr)` are the same. Both are common; pick one and be consistent.

:::warning Dereferencing nullptr
```cpp nonum frag
int* p = nullptr;
std::cout << *p;        // undefined behaviour - typically a crash
```
Following a pointer to nothing is undefined behaviour. In practice you get a
segmentation fault, which at least tells you immediately.

**The rule that prevents it:** before you write `*p` or `p->something`, satisfy
yourself that `p` is not null. In linked list code this becomes the habit of
writing `while (curr != nullptr)` rather than `while (true)`, and it is why
Chapters 25 and 26 check for the empty list before touching anything.
:::

:::note Use `nullptr`, not `NULL` or `0`
`NULL` is inherited from C and is really the integer 0 in disguise, which means
it can select the wrong overload and produce surprising errors.

`nullptr` has its own type and cannot be confused with an integer. It has been
the correct choice since C++11. This book uses it everywhere, and so should you.
:::

## Pointers to structs, and the arrow

A pointer can point to anything, including a struct.

```cpp title="The arrow operator"
#include <iostream>
#include <string>

struct Point {
    int x;
    int y;
};

int main() {
    Point a{3, 4};
    Point* p = &a;

    std::cout << a.x << " " << a.y << "\n";        // on the object: dot
    std::cout << (*p).x << " " << (*p).y << "\n";  // dereference, then dot
    std::cout << p->x << " " << p->y << "\n";      // shorthand for the above

    p->x = 10;                                     // writes through the pointer
    std::cout << a.x << "\n";
    return 0;
}
```

```text nonum
3 4
3 4
3 4
10
```

:::definition `.` versus `->`
`a.x` — `a` **is** the object. Use the dot.

`p->x` — `p` is a **pointer** to the object. Use the arrow.

`p->x` is exactly shorthand for `(*p).x`: dereference, then take the member. The
brackets are required in the long form because `.` binds tighter than `*`, so
`*p.x` would try to take `.x` of the pointer and fail to compile.

Writing `p.x` on a pointer is a compile error, and the error message says
something like *"request for member 'x' in 'p', which is of pointer type"*. When
you see that, the fix is always the same: change the dot to an arrow.
:::

@fig: ptr_arrow | 160 | Dot versus arrow. The dot reads a member of an object you are holding; the arrow walks the pointer first and then reads the member. Every linked list traversal in this book is a chain of arrows.

This is the operator you will use most in Part VI. `node->next` means *"go to the
node, and read its `next` field"*, and `node->next->next` means *"go two nodes
along"*.

## References: an alias, not a pointer

C++ has a second way to refer to an existing object.

```cpp title="References compared with pointers" norun
#include <iostream>

int main() {
    int x = 42;

    int& r = x;         // r IS x - another name for the same bytes
    int* p = &x;        // p POINTS AT x - a separate variable holding an address

    r = 99;             // no star needed: r is x
    std::cout << x << "\n";

    *p = 7;             // star needed: follow the address first
    std::cout << x << " " << r << "\n";

    std::cout << &x << " == " << &r << "\n";   // the same address
    return 0;
}
```

A possible run:

```text nonum
99
7 7
0x7ffc1a2b3c4c == 0x7ffc1a2b3c4c
```

@fig: ptr_ref_vs_ptr | 162 | A reference and a pointer. The reference is a second label on the same bytes — there is no extra storage and no arrow to follow. The pointer is a separate variable whose contents happen to be an address.

@tbl: Reference versus pointer. The short version: a reference is simpler and safer, so prefer it; a pointer is more capable, so use it when you need absence or rebinding.
| | Reference `int&` | Pointer `int*` |
|---|---|---|
| Can be null | no | yes (`nullptr`) |
| Must be initialised | yes, always | no (and that is a hazard) |
| Can be reseated later | no, bound for life | yes |
| Syntax to use the value | `r` | `*p` |
| Syntax for a member | `r.x` | `p->x` |
| Pointer arithmetic | no | yes |
| Use it for | a parameter you will not rebind | optional things, linked structures |

:::insight When each one is right
Use a **reference** when the thing definitely exists and you will refer to that
same thing for the whole of its life. Function parameters are the main case.

Use a **pointer** when the thing might be absent (`nullptr`), or when you need
to change what you are referring to (walk a list), or when you are managing a
heap object.

A linked list node's `next` is a pointer and could not be a reference: it has to
be able to mean "nothing follows", and it has to be reassignable.
:::

## Passing to functions: three ways

This is the most practically important section in the chapter.

@fig: ptr_passing | 180 | The three ways to pass an argument. By value copies it, so changes are lost. By reference names the caller's variable, so changes stick. By pointer passes the address, so changes stick and the argument may be absent.

```cpp title="By value, by reference, by pointer"
#include <iostream>

void byValue(int n)     { n = 99; }      // changes a COPY - caller unaffected
void byReference(int& n){ n = 99; }      // changes the caller's variable
void byPointer(int* n)  { if (n) *n = 99; }   // same, but may be given nullptr

int main() {
    int a = 1, b = 1, c = 1;

    byValue(a);
    byReference(b);
    byPointer(&c);                       // note the & at the call site

    std::cout << a << " " << b << " " << c << "\n";

    byPointer(nullptr);                  // legal, and does nothing
    std::cout << "survived the nullptr call\n";
    return 0;
}
```

```text nonum
1 99 99
survived the nullptr call
```

`a` is unchanged because `byValue` received a copy. `b` and `c` changed because
both functions were given a way back to the original.

:::pitfall Copying large objects by accident
```cpp nonum frag
void process(std::vector<int> v);          // copies all n elements: O(n) per call
void process(const std::vector<int>& v);   // no copy, and cannot modify it
void process(std::vector<int>& v);         // no copy, and may modify it
```
The first version is a silent $O(n)$ cost on every call. For a vector of a
million integers, that is 4 MB copied each time.

**The rule this book follows:**
- small types (`int`, `double`, a pointer) → **by value**, it is cheapest;
- containers and structs you only read → **`const&`**;
- anything you intend to modify → **`&`**, or `*` if it may be absent.
:::

## Pointer arithmetic, and the link back to arrays

Pointers and arrays are more closely related than they look.

```cpp title="An array name is almost a pointer"
#include <iostream>

int main() {
    int arr[5] = {10, 20, 30, 40, 50};
    int* p = arr;                    // the array name converts to &arr[0]

    std::cout << *p << "\n";         // 10
    std::cout << *(p + 2) << "\n";   // 30 - two ELEMENTS along, not two bytes
    std::cout << p[2] << "\n";       // 30 - exactly the same thing
    std::cout << *(arr + 3) << "\n"; // 40 - and this works on the array too

    // Walking with a pointer instead of an index
    for (int* q = arr; q != arr + 5; ++q)
        std::cout << *q << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
10
30
30
40
10 20 30 40 50 
```

:::insight `arr[i]` *is* `*(arr + i)`
The subscript operator is defined as pointer arithmetic. `arr[2]` means
*"start at `arr`, move 2 elements, read"* — which is exactly
$B + i \times S$ from Chapter 2.

Adding 1 to an `int*` moves **4 bytes**, not 1. The compiler scales by
`sizeof(int)` automatically, which is why `p + 2` lands on element 2 rather than
somewhere in the middle of element 0.

A curiosity that follows: since `arr[i]` is `*(arr + i)` and addition
commutes, `2[arr]` is legal C++ and means `arr[2]`. Never write it. Knowing why
it works means you have understood the definition.
:::

## The three pointer bugs

:::warning The ones that will actually happen to you
**Uninitialised pointer.**
```cpp nonum frag
int* p;            // contains whatever bytes were there
*p = 42;           // writes 42 to a random address
```
It may crash, or it may silently corrupt something else. Always initialise —
to `nullptr` if you have nothing better.

**Dangling pointer** — pointing at something that no longer exists.
```cpp nonum frag
int* p;
{
    int local = 5;
    p = &local;
}                  // local is destroyed here
std::cout << *p;   // p now points at reclaimed memory
```
Very often this still prints 5, because nothing has reused the bytes yet. It
will fail later, somewhere else, for no visible reason. This is also what
happens to every pointer into a `std::vector` after it reallocates (Chapter 5),
and to every pointer to a node after you `delete` it (Chapter 22).

**Null dereference.**
```cpp nonum frag
Node* n = findNode(head, 42);   // returns nullptr when not found
std::cout << n->data;           // crash if it was not found
```
The fix is the habit: check before you follow.
:::

## What you should take away

:::recap Chapter 21 in seven lines
- A pointer is a **variable whose value is an address**.
- `&x` gives the address of `x`; `*p` gives the thing at `p`. They are
  opposites.
- `*` in a declaration is part of the type; `*` in an expression dereferences.
- `nullptr` means "points at nothing". Check it before you follow a pointer.
- `p->x` is `(*p).x`. Dot for objects, arrow for pointers.
- A **reference** is another name for an existing object: no null, no
  reseating, no star.
- Pass small things by value, read-only containers by `const&`, and things you
  will modify by `&` or `*`.
:::

:::exercise Practise
1. Write a program with `int x = 5;` and `int* p = &x;` that prints `x`, `&x`,
   `p`, `*p` and `&p`. Explain in words what each of the five is.
2. Predict the output of the snippet below the box, then run it.
3. Write `swap(int* a, int* b)` using pointers, then write it again using
   references. Which is easier to call, and which could be given `nullptr`?
4. Why does `p.x` fail to compile when `p` is a `Point*`? What is the exact
   fix?
5. Given `int arr[4]` and `int* p = arr;`, what is the difference between
   `p + 1` and `(char*)p + 1`? How many bytes does each move?
6. Explain the difference between a pointer that is `nullptr` and a pointer that
   is dangling. Which one is more dangerous, and why?
7. Write a function that takes a pointer to an `int` and sets it to 0 **only if**
   the pointer is not null. Why can this function not be written with a
   reference parameter?
8. Draw the memory diagram for `int x = 1; int* p = &x; int** pp = &p;`. What is
   `**pp`? Where would you need a pointer to a pointer in real code?
:::

```cpp title="For exercise 2 — predict before you run" nonum frag
int a = 1, b = 2;
int* p = &a;
*p = 10;
p = &b;
*p = 20;
std::cout << a << " " << b;
```
