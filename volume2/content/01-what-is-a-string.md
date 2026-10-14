# What a String Really Is
@short: What Is a String?
@subtitle: An array of small integers, with a convention attached
@tier: foundation
@prereq: Volume 1, Chapters 2 and 4
@blurb: Every surprising thing a C++ string does — why `strlen` is $O(n)$, why comparing with `==` works on one type and not another, why a character can be negative — follows from one fact: a string is an array of small integers. This chapter establishes that fact precisely, and then everything else in Part I is a consequence.
@objectives:
- State what a `char` is, in terms of bytes and numbers
- Explain the difference between a C-style string and a `std::string`
- Say why the null terminator exists and what it costs
- Explain why `strlen` is $O(n)$ and `std::string::size()` is $O(1)$
- Avoid the three classic C-string traps
- Decide which string type to use, and why the answer is almost always the same

## A string is an array

Volume 1 established that an array is a block of equal-sized elements laid out
contiguously. A string is exactly that, with one extra rule about what the
elements mean.

:::definition Character and string
A **`char`** is a one-byte integer. On every machine you will use it holds a
value from $-128$ to $127$ (signed) or $0$ to $255$ (unsigned), and a
**character encoding** says which number stands for which symbol.

A **string** is an array of `char`. Nothing else. The "textness" is a
convention layered on top of an ordinary array of small numbers.
:::

@fig: str_is_array | 168 | A string is an array of bytes. The top row is what you see; the middle row is what is stored; the bottom row is the address of each byte. Every string operation in this book is an array operation on the middle row.

```cpp title="A string is an array of numbers — proof"
#include <iostream>
#include <string>

int main() {
    std::string s = "Cat";

    std::cout << "characters: ";
    for (char c : s) std::cout << c << " ";
    std::cout << "\n";

    std::cout << "as numbers: ";
    for (char c : s) std::cout << (int)c << " ";
    std::cout << "\n";

    std::cout << "sizeof(char) = " << sizeof(char) << " byte\n";
    std::cout << "s.size()     = " << s.size() << "\n";
    return 0;
}
```

```text nonum
characters: C a t 
as numbers: 67 97 116 
sizeof(char) = 1 byte
s.size()     = 3
```

`'C'` **is** 67. Not "represents" 67 — in the type system it is a one-byte
integer whose value is 67, and `std::cout` prints it as a letter only because
the stream knows the type is `char`. Cast to `int` and the stream prints the
number instead.

:::insight Why this matters immediately
Because it means **you can do arithmetic on characters**, and that one fact is
the basis of the frequency tables used in half the problems in this book.

```cpp nonum frag
int index = c - 'a';     // 'a' -> 0, 'b' -> 1, ... 'z' -> 25
char back  = 'a' + 3;    // 'd'
bool digit = (c >= '0' && c <= '9');
```
Chapter 4 does this properly. For now, just notice that none of it would be
possible if a character were a special opaque thing rather than a number.
:::

## The two kinds of string in C++

C++ inherited one string type from C and added its own. They behave very
differently, and knowing which you are holding prevents a specific family of
bugs.

### C-style strings: `char*` and the null terminator

A C-style string is a raw array of `char` ending with a byte of value 0, called
the **null terminator** and written `'\0'`.

@fig: str_null_terminator | 160 | A C-style string. The length is not stored anywhere — it is discovered by scanning forwards until a zero byte appears. That single design decision is why so many C string functions are $O(n)$.

:::definition The null terminator
`'\0'` is the `char` whose value is 0. It is **not** the digit `'0'`, which is
48.

A C-style string is "everything from here up to but not including the first
zero byte". Its length is therefore not stored — it must be measured by
walking.
:::

```cpp title="C-style strings, and the cost of not storing a length"
#include <cstring>
#include <iostream>

int main() {
    const char* s = "Cat";          // 4 bytes in memory: 'C' 'a' 't' '\0'

    std::cout << "strlen(s) = " << std::strlen(s) << "\n";   // walks to find 0

    char buf[4] = {'C', 'a', 't', '\0'};
    std::cout << "buf       = " << buf << "\n";

    // The terminator is a real byte you can look at.
    std::cout << "(int)s[3] = " << (int)s[3] << "\n";
    std::cout << "'0' is    = " << (int)'0' << "\n";
    return 0;
}
```

```text nonum
strlen(s) = 3
buf       = Cat
(int)s[3] = 0
'0' is    = 48
```

:::perf Why `strlen` is $O(n)$, and why it matters
`strlen` cannot know the length without looking, so it walks until it finds the
zero byte. That is $O(n)$ **every time you call it**.

The classic disaster:
```cpp nonum frag
for (int i = 0; i < (int)std::strlen(p); ++i)    // strlen runs EVERY iteration
    process(p[i]);
```
The loop condition re-measures the string on every pass, so an $O(n)$ loop
becomes $O(n^2)$. On a one-megabyte string that is $10^{12}$ byte reads —
hours instead of milliseconds.

The fix is to measure once:
```cpp nonum frag
int len = (int)std::strlen(p);
for (int i = 0; i < len; ++i) process(p[i]);
```
Compilers sometimes hoist the call out for you. Sometimes they cannot, because
the loop body might modify the string. Do not rely on it.
:::

### `std::string`: a vector that knows it holds text

```cpp title="std::string stores its own length"
#include <iostream>
#include <string>

int main() {
    std::string s = "Cat";

    std::cout << "size()  = " << s.size() << "\n";      // O(1): a stored counter
    std::cout << "empty() = " << s.empty() << "\n";
    s += " food";                                       // grows like a vector
    std::cout << "now     = " << s << " (" << s.size() << ")\n";

    std::string t = "Cat";
    std::cout << "s == t  = " << (s == t) << "\n";      // compares CONTENTS
    std::cout << "t == \"Cat\" = " << (t == "Cat") << "\n";
    return 0;
}
```

```text nonum
size()  = 3
empty() = 0
now     = Cat food (8)
s == t  = 0
t == "Cat" = 1
```

:::insight `std::string` is `std::vector<char>` with text conveniences
Everything Volume 1 Chapter 5 said about `std::vector` applies unchanged:

- it owns one contiguous block;
- `size()` is a stored counter, so $O(1)$;
- `capacity()` is the block size, and `push_back` / `+=` is amortised $O(1)$;
- growing past the capacity reallocates and **invalidates every pointer,
  reference and iterator** into it;
- indexing `s[i]` is the same address arithmetic, so $O(1)$.

The additions are: `==` compares contents rather than addresses, there are
text-shaped members (`substr`, `find`, `append`), and it keeps a hidden null
terminator at the end so that `c_str()` can hand a C-style pointer to old APIs
for free.
:::

@fig: str_two_types | 180 | The two string types. The C-style version is a bare pointer to bytes, with the length encoded as a sentinel. `std::string` carries a length and a capacity beside the data, which is why it can answer `size()` instantly and grow safely.

## Comparing them

@tbl: `std::string` versus C-style strings. The last row is the one that decides it in practice.
| | `const char*` | `std::string` |
|---|---|---|
| Length | $O(n)$ via `strlen` | $O(1)$, stored |
| Can grow | no | yes, amortised $O(1)$ |
| `==` compares | **addresses** | contents |
| `<` compares | addresses (meaningless) | lexicographic order |
| Memory management | yours | automatic |
| Copying | copies a pointer only | copies the characters |
| Passing to a function | `const char*` | `const std::string&` |
| Works with STL algorithms | with pointers | naturally |
| Risk of buffer overrun | high | low |

**Use `std::string`.** Reach for `const char*` only when an existing API
demands it, and convert with `.c_str()` at that boundary.

## The three C-string traps

:::warning These compile, run, and are wrong
**Comparing with `==`.**
```cpp nonum frag
const char* a = "cat";
const char* b = "cat";
if (a == b) { }          // compares ADDRESSES, not text
```
Whether this is true depends on whether the compiler merged the two identical
literals — it often does, which is worse, because the bug then appears only
when the strings come from somewhere else. Use `std::strcmp(a, b) == 0`, or
use `std::string` and stop thinking about it.

**Forgetting room for the terminator.**
```cpp nonum frag
char buf[3];
std::strcpy(buf, "cat");   // needs FOUR bytes: c, a, t, '\0'
```
Writes one byte past the end. Undefined behaviour, and the classic source of
buffer-overflow security bugs.

**Assuming `char` is unsigned.**
```cpp nonum frag
char c = 200;            // on most platforms this is -56
int  i = c;              // -56, not 200
```
Plain `char` is signed on x86 and ARM Linux, so any byte above 127 reads as
negative. This bites the moment you index a frequency table with a non-ASCII
byte: `count[c]` with a negative `c` reads outside the array.

The fix is to cast explicitly: `count[(unsigned char)c]`. Every frequency
table in this book does that, and Chapter 5 explains exactly when it matters.
:::

## What a string costs

@tbl: `std::string` operations. Identical to `std::vector` except the final three rows, which are text-specific.
| Operation | Cost | Note |
|---|---|---|
| `s[i]`, `s.at(i)` | $O(1)$ | address arithmetic; `at` is bounds-checked |
| `s.size()`, `s.empty()` | $O(1)$ | a stored counter |
| `s.push_back(c)`, `s += c` | $O(1)$ amortised | doubles like a vector |
| `s += t` | $O(\lvert t \rvert)$ amortised | appends all of `t` |
| `s + t` | $O(\lvert s \rvert + \lvert t \rvert)$ | builds a **new** string |
| `s.insert(0, t)` | $O(\lvert s \rvert + \lvert t \rvert)$ | shifts everything right |
| `s.erase(0, k)` | $O(\lvert s \rvert)$ | shifts everything left |
| `s.substr(i, len)` | $O(len)$ | **copies** those characters |
| `s.find(t)` | $O(\lvert s \rvert \cdot \lvert t \rvert)$ worst case | naive search; Volume 12 improves it |
| `s == t` | $O(\min(\lvert s \rvert, \lvert t \rvert))$ | stops at the first difference |
| `std::strlen(p)` | $O(n)$ | walks to the terminator |

Three rows there are the subject of Chapter 3, because they are where
accidental $O(n^2)$ comes from: `s + t`, `insert(0, …)` and `substr` inside a
loop.

:::interview Say which type and why
A small thing that reads well: when you declare a string parameter, say why.

> *"I'll take it as `const std::string&` — by reference so we don't copy it,
> and `const` because we only read it."*

And if the interviewer's template hands you a `char*`, say that you would wrap
it rather than silently working with raw pointers. It takes four seconds and it
tells them you know the difference.
:::

:::recap Chapter 1 in six lines
- A `char` is a one-byte integer; a string is an array of them.
- Characters support arithmetic, which is the basis of every frequency table in
  this book.
- A C-style string stores no length; it is terminated by a zero byte, so
  `strlen` is $O(n)$.
- Calling `strlen` in a loop condition turns $O(n)$ into $O(n^2)$.
- `std::string` is `std::vector<char>` plus text conveniences: stored length,
  content comparison, automatic growth.
- Plain `char` is signed; cast to `unsigned char` before using it as an index.
:::

:::exercise Practise
1. What is `(int)'A'`? What is `(int)'a'`? What is `'a' - 'A'`, and why is that
   number useful?
2. How many bytes does the literal `"hello"` occupy in memory? Why is it not 5?
3. Write a loop that counts the characters of a `const char*` without calling
   `strlen`. What is its complexity?
4. Explain why the loop below is $O(n^2)$, and fix it.
5. Given `std::string s = "abc";`, what does `s + "d"` cost, and what does
   `s += "d"` cost? Why are they different?
6. Why does `a == b` on two `const char*` sometimes appear to work? Why is that
   worse than it never working?
7. On a machine with signed `char`, what does `count[c]` do when `c` holds the
   byte 200? Write the corrected line.
:::

```cpp title="For exercise 4 — why is this quadratic?" nonum frag
const char* p = "a long string";
for (int i = 0; i < (int)std::strlen(p); ++i)
    std::cout << p[i];
```
