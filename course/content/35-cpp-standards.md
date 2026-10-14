# C++ Implementation Standards
@short: C++ Standards
@subtitle: The habits that make DSA code correct, readable and interview-ready
@tier: reference
@prereq: Chapters 21 and 22
@blurb: Every piece of code in this book follows the same small set of rules. They are not style preferences — each one prevents a specific bug or answers a specific question an interviewer will ask. This chapter collects them, with the reason for each, and ends with a checklist to run over any solution before you call it finished.
@objectives:
- Write function signatures that say whether the input will be modified
- Choose between by-value, by-reference and by-pointer parameters correctly
- Use `std::vector` idiomatically, and know which operations are expensive
- Write memory-safe code with `new` and `delete`, and verify it
- Name things so that the code needs fewer comments
- Run a pre-submission checklist over any solution

## 1. Signatures say what the function does

The parameter list is documentation that the compiler enforces. Use it.

```cpp title="Four signatures, four promises" frag
int  sum(const std::vector<int>& v);          // reads it, cannot modify, no copy
void sortInPlace(std::vector<int>& v);        // modifies the caller's vector
std::vector<int> sorted(std::vector<int> v);  // takes a copy, leaves the original
int  maxOf(int a, int b);                     // small types by value: cheapest
```

:::definition The rule
| Parameter | Use when |
|---|---|
| `const T&` | you read a container or large object and do not modify it |
| `T&` | you modify the caller's object |
| `T` (by value) | the type is small (`int`, `double`, a pointer) **or** you genuinely want a copy |
| `T*` | the argument may be absent (`nullptr`), or you must reseat it |

Passing a `std::vector` **by value** copies every element: $O(n)$ time and
$O(n)$ memory on every call. It is sometimes exactly what you want — Chapter 15
takes a vector by value precisely in order to sort a copy — but it should be a
decision, never an accident.
:::

:::interview State it out loud
*"I'll take this as `const std::vector<int>&` so we don't copy it, and because
the function doesn't modify the input."*

One sentence, and you have demonstrated that you know the difference. If the
function *does* modify its input, say that too — an interviewer will often ask
"does this change the caller's data?" and you want to have answered already.
:::

## 2. Use std::vector, and know what is expensive

```cpp title="Vector habits worth having" frag
std::vector<int> v;
v.reserve(n);                     // one allocation when you know the size

for (int x : v) { }               // read-only traversal
for (int& x : v) { x *= 2; }      // modifying traversal: note the &
for (const auto& s : words) { }   // non-trivial elements: avoid the copy

v.push_back(x);                   // amortised O(1)
v.pop_back();                     // O(1)
v.insert(v.begin(), x);           // O(n) - usually a mistake inside a loop
v.erase(v.begin());               // O(n) - likewise
```

@tbl: The operations whose cost surprises people. Each of these looks like one statement and contains a loop.
| Looks cheap | Really costs | Instead |
|---|---|---|
| `v.insert(v.begin(), x)` in a loop | $O(n^2)$ | build forwards, then `std::reverse` |
| `v.erase(it)` in a loop | $O(n^2)$ | the erase–remove idiom |
| `f(std::vector<int> v)` | $O(n)$ per call | `const std::vector<int>&` |
| `s = s + c` in a loop | $O(n^2)$ | `s += c`, or `s.reserve` first |
| `v[i]` with `i` from `size() - 1` on an empty vector | wraps to a huge number | `(int)v.size() - 1` |

:::pitfall The unsigned comparison, once more
`v.size()` is unsigned. These two lines behave differently on an empty vector:

```cpp nonum frag
for (int i = 0; i < (int)v.size() - 1; ++i) { }   // OK  -1, loop does not run
for (size_t i = 0; i < v.size() - 1; ++i) { }     // BAD huge number, runs forever
```

This book casts to `int` at every comparison. It is slightly verbose and it
removes the problem. The alternative — `i + 1 < v.size()` — never subtracts at
all and is arguably better; use either, consistently.
:::

## 3. One consistent Node definition

Every linked list chapter in this book uses exactly this, unchanged:

```cpp title="The Node struct used throughout" frag
struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};
```

:::insight Why consistency matters more than elegance
A reader who has seen this struct once never has to read it again. Changing the
field names between chapters — `data` to `val`, `next` to `link` — would cost
the reader attention on every single example for no benefit.

The same applies to your own code and to an interview: pick the names the
problem gives you (LeetCode uses `ListNode` with `val` and `next`) and keep them.
Renaming the interviewer's types is a small, needless friction.
:::

## 4. Memory rules

:::checklist The six memory rules this book follows
1. Every `new` has exactly one matching `delete`, and `new[]` matches `delete[]`.
2. **Unlink before you free.** Reroute the pointers, then destroy the node.
3. **Save `next` before deleting.** `temp = curr; curr = curr->next; delete temp;`
4. After freeing a list, set `head = nullptr`.
5. After `delete p`, set `p = nullptr` — `delete nullptr` is a no-op, so double
   frees become harmless.
6. Verify with `-fsanitize=address,undefined`, every time.
:::

```bash nonum
g++ -std=c++17 -Wall -Wextra -fsanitize=address,undefined -g prog.cpp -o prog
./prog
```

`-Wall -Wextra` catches unused variables, signed/unsigned comparisons and
uninitialised reads at compile time. The sanitizers catch out-of-bounds access,
leaks and use-after-free at run time, with the exact line. Between them they
find most of what this book warns about, and they cost nothing to turn on.

:::note In an interview you will not run anything
Which is precisely why the rules above are worth making automatic. Nobody will
tell you that you leaked a node; they will simply notice.

Saying *"and I'd free the removed node here"* while writing the deletion is the
cheapest credibility in the whole process.
:::

## 5. Naming

```cpp title="Names that remove the need for comments" frag
// Vague
int n, m, t;
Node* p;
for (int i = 0; i < x; ++i) { }

// Clear
int rows, cols, target;
Node* curr;
for (int row = 0; row < rows; ++row) { }
```

The conventions this book uses, which are close to universal:

| Name | Means |
|---|---|
| `i`, `j`, `k` | loop indices — these are fine, and clearer than alternatives |
| `n`, `m` | sizes of the first and second input |
| `left`, `right` | converging two pointers |
| `read`, `write` | same-direction two pointers |
| `slow`, `fast` | two-speed pointers |
| `prev`, `curr`, `nextNode` | list traversal and reversal |
| `head`, `tail`, `dummy` | list anchors |
| `best`, `current` | a running answer and a running candidate |
| `target` | the value being searched for |

Note `nextNode` rather than `next`: `next` is also a standard library function
(`std::next`), and shadowing it is legal but confusing.

## 6. Say whether the function modifies its input

Make this explicit in three places: the signature, a one-line comment, and out
loud.

```cpp title="Three ways to express the same operation" frag
// Modifies v in place. Returns nothing.
void reverseInPlace(std::vector<int>& v);

// Returns a reversed copy. v is untouched.
std::vector<int> reversed(const std::vector<int>& v);

// Modifies the list and returns the new head. The old head is now the tail.
Node* reverseList(Node* head);
```

That third comment is worth the line. "Returns the new head" is the single most
common thing people forget about list reversal, and writing it down makes it
impossible to forget.

## 7. Handle edge cases explicitly, or show that they fall out

Two acceptable approaches, and one unacceptable one.

```cpp title="Explicit, implicit, and absent" frag
// A. Explicit: state the case and handle it.
int largest(const std::vector<int>& v) {
    if (v.empty()) throw std::invalid_argument("empty");
    // ...
}

// B. Implicit, with a comment saying why: the structure handles it.
void printList(Node* head) {
    // An empty list prints nothing: the loop simply never runs.
    for (Node* curr = head; curr != nullptr; curr = curr->next) { }
}

// C. Absent: the case is simply not considered.
int largestBad(const std::vector<int>& v) {
    int best = v[0];                 // undefined behaviour on an empty vector
    // ...
}
```

B is the best when it is available — an edge case that falls out of the
structure cannot be forgotten. A is correct when it is not. **C is never
acceptable**, even when the problem statement promises a non-empty input; say
*"the problem guarantees non-empty, so I'll rely on that"* rather than silently
relying on it.

:::checklist The edge cases to check, every time
**Arrays:** empty · one element · two elements · all equal · all negative ·
already sorted · reverse sorted · duplicates · the maximum allowed size.

**Linked lists:** empty (`nullptr`) · one node · two nodes · the operation
targets the head · the operation targets the tail · the value is absent ·
duplicates · a cycle, if cycles are possible.
:::

## 8. Avoid cleverness before clarity

```cpp title="The same swap, three ways" frag
std::swap(a, b);                       // OK  clear, and optimal

int t = a; a = b; b = t;               // OK  fine, and obvious

a ^= b; b ^= a; a ^= b;                // BAD "clever": no faster, and
                                       //   silently wrong when a and b
                                       //   are the same object
```

The XOR swap is a classic example of a trick that is slower on modern hardware
(it creates a dependency chain the compiler cannot break), harder to read, and
broken in a case the obvious version handles. It exists in folklore and nowhere
else.

The same judgement applies to the genuinely useful tricks in this book — index
marking, the $a + b \times n$ encoding, the interleaved copy. Each of those buys
a real asymptotic improvement, which is what justifies the obscurity. **Earn the
cleverness**: if it does not change the complexity, write the plain version.

## 9. Make every example compilable

Every program in this book compiles with `g++ -std=c++17` and produces exactly
the output shown — that is checked mechanically, by a script that compiles each
block and diffs its real output against the book's text.

```cpp title="What a complete example needs" frag
#include <iostream>      // for std::cout
#include <vector>        // for std::vector
#include <algorithm>     // for std::sort, std::max, std::min, std::swap
#include <unordered_map> // for std::unordered_map
#include <string>        // for std::string
```

Two habits worth keeping:

**Include what you use.** Relying on one header to pull in another works until
it does not, and the failure appears on a different compiler.

**Do not write `using namespace std;`.** It is fine in a five-line exercise and a
genuine problem in anything larger — it drags in hundreds of names, and
`std::count`, `std::distance` and `std::size` collide with ordinary variable
names. Writing `std::` costs five characters and never surprises anyone. (In an
interview, do whatever the interviewer's template does.)

## 10. The pre-submission checklist

:::checklist Before you say "done"
1. Does it compile? Mentally walk the syntax: semicolons, braces, return
   statements on every path.
2. Does the empty input work?
3. Does a single-element input work?
4. Are all loop bounds right? Check every `<` versus `<=` against the last valid
   index.
5. Is every pointer checked before it is dereferenced?
6. Is every `new` matched by a `delete`?
7. Could any `int` overflow? Sums, products, `mid`, and `max - min`.
8. Is `size()` compared against a signed value anywhere?
9. If you modified the input, did you say so?
10. Can you state the time and space complexity without hesitating?
:::

Run it in your head in under a minute. Items 2, 4 and 10 catch most real
problems; item 6 is the one that matters in Part VI.

:::recap Chapter 35 in six lines
- The signature is documentation: `const&` to read, `&` to modify, by value for
  small types, `*` for optional.
- `insert`/`erase` at the front, and vectors passed by value, are the hidden
  $O(n)$s.
- Keep one `Node` definition and one set of names throughout.
- Unlink before freeing; save `next` before deleting; null the pointer
  afterwards; check with the sanitizers.
- Prefer edge cases that fall out of the structure over edge cases you
  special-case — and never over ones you ignore.
- Earn your cleverness: if it does not improve the complexity, write the plain
  version.
:::

:::exercise Practise
1. For each function you have written while reading this book, check the
   parameter against the rule in section 1. How many should change?
2. Compile three of your earlier solutions with
   `-Wall -Wextra -fsanitize=address,undefined`. What does it report?
3. Rewrite a function you wrote with vague names using the conventions in
   section 5. Does it need fewer comments?
4. Find a place in your own code where an edge case is handled implicitly. Add
   the one-line comment that says why it works.
5. Write the XOR swap and test it with `swap(a, a)`. What happens, and why?
6. Take any solution of yours and run the ten-item checklist. Time yourself.
7. Why is `using namespace std;` acceptable in a small exercise and not in a
   library header? Name a specific collision it could cause.
:::
