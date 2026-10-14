# Static Arrays, Dynamic Arrays and std::vector
@short: Vectors and Capacity
@subtitle: How a fixed-size block pretends to grow, and what that costs
@tier: foundation
@prereq: Chapter 4
@blurb: A raw array cannot grow — the memory after it belongs to somebody else. `std::vector` gets around this by moving the whole block when it runs out of room, and the way it does that produces the most frequently misunderstood phrase in data structures: *amortised constant time*. This chapter explains size versus capacity, why vectors double instead of growing by one, and exactly what `push_back` costs.
@objectives:
- Explain why a static array cannot grow, in terms of memory
- Use `std::vector` for its common operations and know the cost of each
- Tell `size()` from `capacity()` and predict both after a sequence of pushes
- Explain amortised $O(1)$ and why `push_back` deserves that description
- Explain why doubling is used instead of adding a fixed amount
- Avoid the two classic vector bugs: iterator invalidation and `[]` past the end

## The problem with a fixed size

In Chapter 4 we wrote `int arr[4]`. Suppose we now want a fifth element.

We cannot simply use `arr[4]`. The bytes immediately after the array are not
ours — they belong to another variable, or to nothing in particular, and
writing there is the undefined behaviour we were warned about.

:::insight Why an array cannot grow
Growing would mean claiming the memory immediately after the block. But nothing
reserved that memory for you, and something else is probably already using it.

There is no way to "extend" a block in place. The only option is to **find a
bigger empty block somewhere else and copy everything into it** — and that is
precisely what a dynamic array does.
:::

@fig: vec_cannot_grow | 140 | Why growing in place is impossible. The bytes after an array belong to whatever the compiler put there. To get more room you must move house, not knock through a wall.

:::definition Static array vs dynamic array
A **static array** has a size fixed when it is created. `int arr[4];` is one.
It cannot grow or shrink, ever.

A **dynamic array** can change size while the program runs. It works by owning
a block, tracking how much of it is used, and — when the block fills up —
allocating a bigger one and copying everything across.

In C++, the dynamic array is `std::vector`. In Java it is `ArrayList`, in
Python it is `list`, in C# it is `List<T>`. They are the same idea everywhere.
:::

## Meeting std::vector

```cpp title="The vector operations you will use constantly"
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v;              // empty
    std::vector<int> w = {1, 2, 3};  // from a list
    std::vector<int> z(5, 7);        // five copies of 7

    v.push_back(10);                 // add to the end
    v.push_back(20);
    v.push_back(30);

    std::cout << "v has " << v.size() << " elements\n";
    std::cout << "first = " << v.front() << ", last = " << v.back() << "\n";
    std::cout << "v[1]  = " << v[1] << "\n";

    v.pop_back();                    // remove the last one
    std::cout << "after pop_back, size = " << v.size() << "\n";
    std::cout << "is w empty? " << (w.empty() ? "yes" : "no") << "\n";
    std::cout << "z[4] = " << z[4] << "\n";
    return 0;
}
```

```text
v has 3 elements
first = 10, last = 30
v[1]  = 20
after pop_back, size = 2
is w empty? no
z[4] = 7
```

The crucial point: **`v[1]` on a vector is exactly as fast as `arr[1]` on a raw
array.** A vector is not a linked list in disguise. Internally it holds a
pointer to one contiguous block, so indexing is still $B + i \times S$ — one
multiply, one add. You lose nothing by using it.

## Size versus capacity

Here is the idea that makes everything else make sense.

:::definition size and capacity
**`size()`** is how many elements you have actually put in.

**`capacity()`** is how many the current block could hold before a bigger one
is needed.

Always `size() <= capacity()`. The difference is empty space the vector is
holding in reserve so that the next few `push_back` calls are cheap.
:::

@fig: vec_size_capacity | 150 | Size and capacity. The vector owns the whole block; `size` is the filled part, `capacity` is the whole thing. The spare room at the end is what makes most `push_back` calls free of copying.

Let us watch it happen.

```cpp title="Watching capacity grow"
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v;
    std::cout << "size  capacity\n";
    std::cout << v.size() << "     " << v.capacity() << "\n";
    for (int i = 1; i <= 9; ++i) {
        v.push_back(i);
        std::cout << v.size() << "     " << v.capacity() << "\n";
    }
    return 0;
}
```

On g++ (libstdc++) this prints:

```text
size  capacity
0     0
1     1
2     2
3     4
4     4
5     8
6     8
7     8
8     8
9     16
```

Look at the capacity column: 0, 1, 2, 4, 4, 8, 8, 8, 8, 16. It **doubles**, and
only at the moments where the old block was full.

:::note Capacity growth is not standardised
The C++ standard requires `push_back` to be amortised $O(1)$ but does not
dictate the growth factor. libstdc++ (g++) doubles; MSVC grows by about 1.5×.
Your numbers may differ in detail — the *shape* will not.
:::

## What happens when the block is full

@fig: vec_realloc | 165 | A reallocation, step by step. The vector asks for a block twice as large, copies every existing element across, destroys the old block, and only then stores the new value. That one push costs $O(n)$; the pushes either side of it cost $O(1)$.

When `size() == capacity()` and you call `push_back`:

1. Allocate a new block, usually twice as large.
2. Copy (or move) all $n$ existing elements into it.
3. Free the old block.
4. Put the new element at the end.

Step 2 is $O(n)$. So **some** `push_back` calls are expensive. The question is
how expensive they are *on average*, and the answer is the pleasant surprise of
this chapter.

## Amortised O(1), explained properly

:::definition Amortised complexity
**Amortised** cost is the average cost per operation over a long sequence,
when occasional expensive operations are paid for by many cheap ones.

It is *not* the same as "average case". Average case assumes random input;
amortised makes no assumption about input at all — it is an arithmetic fact
about the total work of a sequence.
:::

Here is the arithmetic. Push $n$ elements into an empty vector that doubles.
Reallocations happen at sizes $1, 2, 4, 8, \dots$ up to $n$, and the copying
work at each is equal to the size at that moment:

$$1 + 2 + 4 + 8 + \cdots + \frac{n}{2} + n < 2n$$

That sum is a geometric series, and it is **less than $2n$** no matter how
large $n$ is. Add the $n$ cheap writes themselves and the total work for $n$
pushes is under $3n$ — which is $O(n)$ for the whole sequence, and therefore
$O(1)$ **per push on average**.

@fig: vec_amortized | 160 | The cost of each individual `push_back`. The spikes are the reallocations, and they get rarer exactly as fast as they get more expensive. The running average (the flat line) never rises.

:::intuition Why doubling, and not "grow by 10"?
Suppose the vector grew by a fixed 10 slots instead of doubling. Reallocations
would happen at sizes 10, 20, 30, 40, …, and the copying work would be

$$10 + 20 + 30 + \cdots + n \;=\; \frac{n(n+10)}{20} \;=\; O(n^2)$$

Pushing a million elements would do about $5 \times 10^{10}$ copies instead of
about two million. The whole structure would be unusable.

**Doubling works because the gaps between expensive operations grow at the same
rate as the expense.** Each reallocation costs twice as much as the last one,
but you get twice as long before the next one. Those two effects cancel
exactly, and that cancellation is what "amortised $O(1)$" means.
:::

:::interview Say this, not that
**Weak:** "`push_back` is $O(1)$."
**Weak:** "`push_back` is $O(n)$ because it sometimes copies."

**Strong:** *"`push_back` is amortised $O(1)$. Most calls just write into spare
capacity. When the block is full it reallocates and copies, which is $O(n)$ for
that one call — but because capacity doubles, that happens only
$\log n$ times, and the total copying over $n$ pushes is under $2n$. So the
average is constant, though any individual call may not be."*

That paragraph is a genuinely common interview question, and most candidates
answer it with one of the two weak versions.
:::

## reserve: skipping the copying entirely

If you know roughly how many elements you will add, you can ask for the
capacity in advance.

```cpp title="reserve avoids every reallocation"
#include <iostream>
#include <vector>

int main() {
    std::vector<int> slow;
    std::vector<int> fast;
    fast.reserve(1000);              // one allocation, right now

    for (int i = 0; i < 1000; ++i) slow.push_back(i);
    for (int i = 0; i < 1000; ++i) fast.push_back(i);

    std::cout << "slow: size " << slow.size()
              << ", capacity " << slow.capacity() << "\n";
    std::cout << "fast: size " << fast.size()
              << ", capacity " << fast.capacity() << "\n";
    return 0;
}
```

```text
slow: size 1000, capacity 1024
fast: size 1000, capacity 1000
```

`slow` reallocated about 10 times and copied roughly 2,000 elements along the
way. `fast` allocated once and copied nothing. Both are $O(n)$ overall, but the
constant factor differs by a lot, and `reserve` is free to write.

:::pitfall `reserve` is not `resize`
`v.reserve(100)` sets capacity to at least 100 and leaves `size()` **unchanged**
— the vector is still empty, and `v[0]` is undefined behaviour.

`v.resize(100)` sets `size()` to 100 and value-initialises the new elements to
0, so `v[0]` is valid and equal to 0.

Using `reserve` and then `v[i] = x` is a genuine bug that often appears to work,
because the memory exists — it is just not officially yours yet.
:::

## The full cost table

@tbl: `std::vector` operations and what each really costs. Note that the two $O(n)$ rows are the same weakness a raw array has, for the same reason: contiguity must be preserved.
| Operation | Cost | What happens |
|---|---|---|
| `v[i]`, `v.at(i)` | $O(1)$ | address arithmetic |
| `v.front()`, `v.back()` | $O(1)$ | the ends are known |
| `v.size()`, `v.empty()` | $O(1)$ | a stored counter |
| `v.push_back(x)` | $O(1)$ amortised | write; occasionally reallocate |
| `v.pop_back()` | $O(1)$ | decrement the counter |
| `v.insert(v.begin(), x)` | $O(n)$ | every element shifts right |
| `v.insert(pos, x)` | $O(n - i)$, so $O(n)$ | elements after `pos` shift |
| `v.erase(v.begin())` | $O(n)$ | every element shifts left |
| `v.erase(pos)` | $O(n - i)$, so $O(n)$ | elements after `pos` shift |
| `v.clear()` | $O(n)$ | destroys elements; capacity kept |
| `std::find(...)` | $O(n)$ | a linear scan |
| `std::sort(...)` | $O(n \log n)$ | introsort |

:::perf The single most common vector performance bug
```cpp nonum frag
// Removing all even numbers, the slow way
for (int i = 0; i < (int)v.size(); ) {
    if (v[i] % 2 == 0) v.erase(v.begin() + i);   // O(n) EACH TIME
    else ++i;
}
```
Each `erase` shifts everything after it, so removing $n/2$ elements costs
$O(n^2)$. On a vector of 100,000 this takes seconds.

The fix is the **erase–remove idiom**, which does it in one pass:
```cpp nonum frag
v.erase(std::remove_if(v.begin(), v.end(),
                       [](int x) { return x % 2 == 0; }),
        v.end());
```
`std::remove_if` shuffles the keepers to the front in $O(n)$ and returns where
the kept part ends; the single `erase` then chops the tail. Total: $O(n)$.

You will meet this idea again in Chapter 13 as the *in-place write-pointer*
pattern — it is the same trick, written by hand.
:::

## Iterator invalidation

:::warning The bug that is hard to see
When a vector reallocates, the old block is freed. Any pointer, reference or
iterator into the old block now points at memory that is no longer yours.

```cpp nonum frag
std::vector<int> v = {1, 2, 3};
int& first = v[0];        // a reference into the current block
v.push_back(4);           // MAY reallocate, freeing that block
std::cout << first;       // undefined behaviour
```

This code usually prints `1` and looks fine, because the freed memory has not
been reused yet. It will fail eventually, in production, under load.

**Rule:** after any operation that can change a vector's capacity
(`push_back`, `insert`, `resize`, `reserve`), treat every previously obtained
pointer, reference and iterator into it as invalid.
:::

## Raw array or vector?

@tbl: When to use which. In modern C++ the default should be `std::vector`, and the burden of proof is on the raw array.
| | C-style array | `std::vector` |
|---|---|---|
| Size fixed at compile time | yes | no |
| Can grow | no | yes |
| Knows its own length | no (decays to a pointer) | yes, `size()` |
| Bounds-checked option | no | yes, `at()` |
| Copyable with `=` | no | yes |
| Comparable with `==` | no (compares addresses) | yes (compares contents) |
| Works with `std::sort` etc. | yes, with pointers | yes, naturally |
| Indexing speed | $O(1)$ | $O(1)$, identical |
| Memory overhead | none | 3 pointers (24 bytes) plus spare capacity |

**Use `std::vector` unless you have a specific reason not to.** The indexing
cost is identical, you get the length for free, and you stop losing afternoons
to bugs the type system could have caught.

Everything this book teaches about arrays applies to both. Where the code says
`std::vector<int>& v`, you can mentally substitute `int arr[], int n` and
nothing conceptual changes.

## What you should take away

:::recap Chapter 5 in seven lines
- A static array cannot grow because the memory after it is not yours.
- A dynamic array grows by **allocating a bigger block and copying** — never in
  place.
- `size()` is what you have used; `capacity()` is what you could use before the
  next move.
- `push_back` is **amortised $O(1)$**: occasional $O(n)$ copies, paid for by the
  many cheap pushes between them.
- Doubling is essential; growing by a fixed amount would make the total $O(n^2)$.
- `insert` and `erase` away from the end are $O(n)$, exactly as for a raw array.
- Reallocation invalidates every iterator, pointer and reference into the vector.
:::

:::exercise Practise
1. A vector doubles from capacity 1. After 100 `push_back` calls, how many
   reallocations have happened, and what is the capacity?
2. Write out the total copying work for pushing 16 elements into a doubling
   vector. Confirm it is less than $2 \times 16$.
3. Explain, to somebody who has not read this chapter, why `push_back` is
   called amortised $O(1)$ rather than just $O(1)$.
4. What does snippet **(A)** below print, and why is its last line a bug?
5. Rewrite snippet **(B)** to be $O(n)$ instead of $O(n^2)$. (Hint: what are you
   actually trying to produce? There is a one-word answer and a one-line
   implementation.)
6. Suppose a vector grew by a factor of 1.5 instead of 2. Is `push_back` still
   amortised $O(1)$? Justify your answer with the series.
7. Why does `clear()` leave the capacity unchanged? When would that be
   helpful, and when would it waste memory?
:::

```cpp title="(A) reserve is not resize" nonum frag
std::vector<int> v;
v.reserve(5);
std::cout << v.size() << "\n";
std::cout << v[0] << "\n";
```

```cpp title="(B) quadratic, and it does not need to be" nonum frag
std::vector<int> out;
for (int x : in) out.insert(out.begin(), x);
```
