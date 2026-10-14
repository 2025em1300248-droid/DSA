# The Array
@short: The Array
@subtitle: A row of boxes in a straight line, and everything that follows from it
@tier: foundation
@prereq: Chapters 2 and 3
@blurb: An array is the simplest data structure there is, and the one every other structure borrows from. This chapter takes it completely apart: how it sits in memory, why indexing starts at zero (there is a real reason), what the compiler does when you write `arr[3]`, how to walk an array safely, and what actually happens when you walk off the end of one.
@objectives:
- Declare, initialise and use a C-style array in C++
- Explain what `arr[3]` compiles into, in terms of addresses
- Give the real reason indexing starts at 0, not 1
- Traverse an array three different ways and say when each is appropriate
- Explain what an out-of-bounds access does, and why it is worse than a crash
- State the cost of access, update, search and traversal, and justify each

## The picture that never changes

Here is an array. Memorise this picture; we will draw it two hundred more
times.

@fig: arr_anatomy | 170 | The anatomy of an array. Four things to keep separate: the **index** (a position label), the **value** (what is stored there), the **address** (where in memory it lives), and the **base** (where the whole block starts).

```cpp title="That picture, as C++"
int arr[4] = {10, 20, 30, 40};
```

Read the declaration from the inside out:

- `arr` is the name.
- `[4]` means **four elements**, decided now and fixed forever.
- `int` means each element is an `int`, so each takes 4 bytes.
- `= {10, 20, 30, 40}` fills them in, in order.

The compiler reserves $4 \times 4 = 16$ consecutive bytes and remembers that
`arr` names the first of them.

:::definition Array
An **array** is a fixed number of elements of the *same type*, stored in one
unbroken block of memory, in order.

Three words carry all the weight:

**Fixed** — the length is decided when the array is created and never changes.

**Same type** — so every element is the same number of bytes, which is what
makes the address formula work.

**Unbroken** — no gaps, nothing else in between. This is the guarantee
Chapter 2 said separate variables do not give you.
:::

## Why indexing starts at zero

Beginners find this arbitrary and annoying. It is neither. Here is the real
reason.

Recall the address formula from Chapter 2:

$$\text{address}(i) = B + i \times S$$

where $B$ is the base address and $S$ is the size of one element. Now ask:
*what is the address of the first element?* It is $B$ itself — the block starts
there. For the formula to give $B$, we need $i \times S = 0$, so $i = 0$.

:::insight The index is not a count, it is a distance
`arr[i]` does not mean "the $i$-th element". It means **"the element $i$ steps
from the start"**.

`arr[0]` is "zero steps from the start" — the first element.
`arr[3]` is "three steps from the start" — the fourth element.

Once you read `[i]` as an *offset* rather than a *count*, zero-based indexing
stops being a quirk and becomes the only sensible choice.
:::

@fig: arr_zero_index | 150 | Index as distance. The index is the number of element-widths you move from the base, which is why the first element is at offset 0 and why the last of $n$ elements is at $n-1$.

This immediately gives you the rule you will use in every loop you ever write:

:::definition The last index
An array of $n$ elements has valid indices $0, 1, 2, \dots, n-1$.

The last valid index is $n - 1$, **not** $n$. Index $n$ is one past the end and
is not yours to touch.
:::

If you remember nothing else from this chapter, remember `n - 1`. Off-by-one
errors at the end of arrays are, by a wide margin, the most common bug in all
of programming.

## What `arr[3]` actually compiles into

When you write `arr[3]`, the compiler does not search. It emits roughly:

1. Take the base address $B$ (it knows this).
2. Multiply 3 by `sizeof(int)`, which is 4, giving 12.
3. Add: $B + 12$.
4. Read the 4 bytes there.

One multiply, one add, one read. **The same work regardless of the index and
regardless of the array's length.**

@fig: arr_access | 140 | Accessing element 3. No element is examined on the way; the address is computed and read directly. This is why array access is $O(1)$.

:::definition Random access
**Random access** means you can reach any element in the same, fixed amount of
time, in any order — "random" here means "arbitrary", not "unpredictable".

Arrays have random access. Linked lists do not, and that single difference
drives half the decisions in this book.
:::

```cpp title="Access and update are both O(1)"
#include <iostream>

int main() {
    int arr[4] = {10, 20, 30, 40};

    std::cout << "arr[0] = " << arr[0] << "\n";   // access
    std::cout << "arr[3] = " << arr[3] << "\n";

    arr[2] = 99;                                   // update, also O(1)
    std::cout << "after arr[2] = 99: " << arr[2] << "\n";
    return 0;
}
```

```text nonum
arr[0] = 10
arr[3] = 40
after arr[2] = 99: 99
```

Updating is the same operation as accessing, with the read replaced by a
write. Same address calculation, same cost: $O(1)$.

## Declaring arrays: the forms you will meet

```cpp title="Five ways to make an array, and what each gives you"
#include <iostream>

int main() {
    int a[5] = {1, 2, 3, 4, 5};   // all five given
    int b[5] = {1, 2};            // rest filled with 0  -> 1 2 0 0 0
    int c[5] = {};                // all zeros           -> 0 0 0 0 0
    int d[]  = {7, 8, 9};         // size deduced as 3
    int e[3];                     // UNINITIALISED - contains garbage

    std::cout << b[4] << " " << c[0] << " " << sizeof(d) / sizeof(d[0]) << "\n";
    (void)a; (void)e;
    return 0;
}
```

```text nonum
0 0 3
```

Three things to take from that program:

- **`int b[5] = {1, 2};` zero-fills the rest.** Partial initialisation is
  complete initialisation in C++; the elements you leave out become 0.
- **`int e[3];` does not.** It contains whatever was in those bytes before.
  This is the single most common source of "it worked on my machine" bugs.
- **`sizeof(d) / sizeof(d[0])`** gives the number of elements: total bytes
  divided by bytes per element. It works here, but see the warning below.

:::pitfall `sizeof` stops working the moment you pass the array to a function
```cpp nonum
void f(int arr[]) {
    // sizeof(arr) is the size of a POINTER (8), not of the array
    std::cout << sizeof(arr) << "\n";   // prints 8, always
}
```
When you pass a C-style array to a function, it **decays to a pointer** — only
the address survives, the length is thrown away. That is why every C-style
array function must take the length as a second parameter:

```cpp nonum
void f(int arr[], int n) { /* now we know how far we may go */ }
```

This is one of the main reasons to prefer `std::vector`, which is Chapter 5.
:::

## Traversal: visiting every element

**Traversal** means visiting each element exactly once, in order. It is the
most common thing anybody ever does with an array.

```cpp title="Three ways to traverse, all O(n)"
#include <iostream>
#include <vector>

int main() {
    int arr[5] = {10, 20, 30, 40, 50};
    int n = 5;

    // 1. Index loop - use when you need to know WHERE you are
    for (int i = 0; i < n; ++i)
        std::cout << "index " << i << " holds " << arr[i] << "\n";

    // 2. Range-based for - use when you only need the VALUES
    for (int value : arr)
        std::cout << value << " ";
    std::cout << "\n";

    // 3. Range-based for by reference - use when you want to MODIFY
    for (int& value : arr)
        value *= 2;
    for (int value : arr)
        std::cout << value << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
index 0 holds 10
index 1 holds 20
index 2 holds 30
index 3 holds 40
index 4 holds 50
10 20 30 40 50 
20 40 60 80 100 
```

@fig: arr_traverse | 140 | A traversal in progress. Each step reads one element and moves on. Five elements, five reads, and the cost grows exactly in step with the length — the definition of $O(n)$.

The third loop deserves a closer look, because the `&` is doing real work.

:::insight `int value` copies; `int& value` is the element itself
In `for (int value : arr)`, each iteration makes a **copy** of the element.
Changing `value` changes the copy, and the array is untouched.

In `for (int& value : arr)`, `value` is a **reference** — another name for the
actual element. Changing it changes the array.

Forgetting the `&` and wondering why your modifications vanished is a rite of
passage. Chapter 21 explains references properly; for now, the rule is: **`&`
if you want to change it, no `&` if you only want to read it.**
:::

Complexity of traversal: you do $O(1)$ work $n$ times, so $O(n)$ time and
$O(1)$ auxiliary space. Nothing was copied, nothing was allocated.

## Searching: the first real algorithm

Suppose you want to know whether 30 is in the array, and where.

```cpp title="Linear search - check them one by one"
#include <iostream>
#include <vector>

// Returns the index of target, or -1 if it is not present.
int linearSearch(const std::vector<int>& v, int target) {
    for (int i = 0; i < (int)v.size(); ++i) {
        if (v[i] == target)
            return i;              // found it - stop immediately
    }
    return -1;                     // checked everything, not here
}

int main() {
    std::vector<int> v = {10, 20, 30, 40, 50};
    std::cout << linearSearch(v, 30) << "\n";
    std::cout << linearSearch(v, 99) << "\n";
    return 0;
}
```

```text nonum
2
-1
```

Three details that matter more than they look:

- **`const std::vector<int>&`** — the `&` avoids copying the whole vector on
  every call ($O(n)$ saved), and the `const` promises we will not modify it.
  This is the standard way to pass a container you only read.
- **`return -1`** — a conventional "not found" marker. It works because $-1$ is
  never a valid index. Returning `0` would be a bug: 0 is a perfectly good
  index.
- **`(int)v.size()`** — `size()` returns an *unsigned* type. Comparing a signed
  `int i` against it produces a compiler warning, and worse, if `v` is empty,
  `v.size() - 1` wraps around to a huge positive number instead of $-1$. The
  cast keeps the comparison honest. See the pitfall below.

:::pitfall The unsigned trap — a bug that looks impossible
```cpp nonum frag
std::vector<int> v;                      // empty, size() == 0
for (int i = 0; i < v.size() - 1; ++i)   // DISASTER
    std::cout << v[i];
```
`v.size()` is 0, and it is unsigned. `0 - 1` for an unsigned type is not $-1$;
it wraps to 18,446,744,073,709,551,615. The loop runs essentially forever,
reading memory it does not own.

Fixes: cast to `int` (`(int)v.size() - 1`), or restructure as
`i + 1 < v.size()`. The second is better because it never subtracts at all.
:::

Cost of linear search: best case $O(1)$ (first element), worst case $O(n)$
(last element or absent). We quote $O(n)$.

:::insight Why searching is slow even though access is fast
Accessing `arr[i]` is $O(1)$ — but only when you already **know** $i$.

Searching is the problem of *finding* $i$, and with unsorted data there is no
shortcut: the value you want could be anywhere, so you must be prepared to look
everywhere.

If the array is **sorted**, everything changes: binary search gets you to
$O(\log n)$. That is Chapter 12, and it is one of the highest-value chapters in
this book.
:::

## Going out of bounds

Here is the most important warning in Part II.

```cpp title="What C++ does when you walk off the end" norun
#include <iostream>

int main() {
    int arr[3] = {10, 20, 30};
    std::cout << arr[0] << " " << arr[1] << " " << arr[2] << "\n";
    std::cout << arr[5] << "\n";    // OUT OF BOUNDS - no error, no crash
    return 0;
}
```

A possible output:

```text nonum
10 20 30
32764
```

Read that again. The program **did not crash**. It did not print an error. It
printed a number — whatever happened to be in the 4 bytes 20 bytes past the
start of the array. Those bytes belong to something else entirely.

@fig: arr_bounds | 156 | Reading past the end. There is no fence at the end of an array — only more memory, belonging to other variables. `arr[5]` reads it cheerfully and tells you nothing is wrong.

:::warning Undefined behaviour
C++ does **not** check array bounds. Reading or writing outside an array is
*undefined behaviour*: the standard permits literally anything to happen.

In practice, one of these:
- You read a meaningless value, and your program silently produces wrong answers.
- You **write** over another variable, and a completely unrelated part of the
  program misbehaves — often minutes later, in code you never touched.
- You hit memory the operating system protects, and the program crashes.
- Nothing visible happens at all, until the day it does.

The crash is the *lucky* case, because at least you find out. Silent corruption
is the one that ruins a week.
:::

**Why does C++ not check?** Because the check would cost time on every single
access, and C++'s design principle is that you do not pay for what you did not
ask for. The language assumes you know what you are doing. The consequence is
that *you must* know what you are doing.

Three defences, in order of how much you should rely on them:

1. **Write the loop bound correctly.** `i < n`, never `i <= n`. This is the
   real defence.
2. **Use `std::vector::at()`** when you want a check. `v.at(5)` throws an
   exception instead of reading rubbish. It is slightly slower, which is why
   `v[5]` exists too.
3. **Turn on your compiler's sanitiser while developing:**
   `g++ -std=c++17 -fsanitize=address,undefined -g prog.cpp`. This catches
   out-of-bounds access at run time and prints exactly which line did it. Use
   it. It will find bugs you did not know you had.

```cpp title="at() checks, [] does not"
#include <iostream>
#include <stdexcept>
#include <vector>

int main() {
    std::vector<int> v = {10, 20, 30};
    try {
        std::cout << v.at(5) << "\n";       // throws
    } catch (const std::out_of_range& e) {
        std::cout << "caught: index was out of range\n";
    }
    return 0;
}
```

```text nonum
caught: index was out of range
```

## The cost table for arrays

Now we can fill in the table promised in Chapter 1.

@tbl: Cost of the six basic operations on an array of $n$ elements. Every entry in this table is explained by one fact: the elements are contiguous and the length is fixed.
| Operation | Cost | Why |
|---|---|---|
| Access `arr[i]` | $O(1)$ | one address calculation |
| Update `arr[i] = x` | $O(1)$ | the same calculation, then a write |
| Search (unsorted) | $O(n)$ | the value could be anywhere |
| Search (sorted) | $O(\log n)$ | binary search — Chapter 12 |
| Traverse | $O(n)$ | $n$ elements, $O(1)$ each |
| Insert at the end | — | impossible: the size is fixed |
| Insert in the middle | $O(n)$ | everything after it must shift right |
| Delete from the middle | $O(n)$ | everything after it must shift left |

Two of those rows need explaining, and they get a full treatment in Chapter 6.
The short version:

@fig: arr_shift | 160 | Why insertion and deletion cost $O(n)$. There is no spare room between elements, so making a gap means moving everything to the right of it. Closing a gap means moving everything back.

Notice that the last three rows are the array's weakness, and they are exactly
the operations a linked list is good at. That is not a coincidence — it is the
trade-off that the two structures exist to offer you.

## Common beginner mistakes

:::pitfall The five that catch everyone
**`i <= n` in the loop condition.** The last valid index is `n - 1`. Writing
`<=` reads one element past the end, every single time.

**Assuming `int arr[n]` works with a variable `n`.** Standard C++ requires the
size to be a compile-time constant. Some compilers allow variable-length arrays
as an extension; it is not portable. Use `std::vector` when the size is decided
at run time.

**Comparing arrays with `==`.** `a == b` compares the two *addresses*, not the
contents, and is almost always `false`. To compare contents, compare element by
element (or use `std::vector`, where `==` does the right thing).

**Expecting an array to remember its length inside a function.** It decays to a
pointer; pass the length too.

**Forgetting `&` in a range-based `for` when you intend to modify.** The loop
runs, the values change, and the array is unchanged.
:::

## What you should take away

:::recap Chapter 4 in seven lines
- An array is a **fixed number** of **same-typed** elements in **one unbroken
  block**.
- `arr[i]` means "$i$ element-widths from the start", which is why indexing
  begins at 0 and the last index is $n-1$.
- Access and update are $O(1)$: one multiply, one add, one memory operation.
- Traversal is $O(n)$ and uses $O(1)$ extra space.
- Searching unsorted data is $O(n)$; sorting changes everything (Chapter 12).
- C++ does **not** check bounds. Out-of-bounds access is undefined behaviour,
  and silent corruption is worse than a crash.
- Insertion and deletion in the middle are $O(n)$, because contiguity must be
  restored by shifting.
:::

:::exercise Practise
1. For `int arr[6]`, what is the last valid index? What is `sizeof(arr)` if an
   `int` is 4 bytes?
2. An array of `double` has base address 3000. What is the address of `arr[5]`?
3. Write a loop that prints an array **backwards**. What is the starting value
   of your index, and what is the loop condition? (This is where `<=` bugs
   live — be careful.)
4. Explain to a friend, in two sentences and without the word "offset", why
   `arr[0]` is the first element.
5. Compile and run the out-of-bounds program above with
   `-fsanitize=address,undefined`. What does it tell you that the plain
   compilation did not?
6. Why can an array not grow? Answer in terms of memory, not in terms of C++
   rules.
7. The function below has exactly one bug. Find it by reading, then compile it
   with `-fsanitize=address` and run it to confirm you were right.
:::

```cpp nonum
int sumAll(int arr[], int n) {
    int total = 0;
    for (int i = 0; i <= n; ++i)
        total += arr[i];
    return total;
}
```
