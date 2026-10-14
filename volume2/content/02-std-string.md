# std::string: Every Operation and What It Costs
@short: std::string
@subtitle: The members you need, and the three that are secretly linear
@tier: foundation
@prereq: Chapter 1
@blurb: `std::string` has over a hundred member functions. You need about fifteen of them, and you need to know which three will quietly turn your linear algorithm into a quadratic one. This chapter is the working set: what each does, what it costs, and the exact traps that come with `substr`, `find` and `erase`.
@objectives:
- Use the fifteen `std::string` members that cover almost all interview work
- State the cost of each, and say which allocate
- Avoid the `npos` trap when `find` fails
- Explain why `substr` inside a loop is usually a mistake
- Use `string_view` where it genuinely helps, and know when it is dangerous
- Convert between strings and numbers safely

## The working set

@tbl: The members worth memorising. The cost column is the reason to memorise them — three of these are the usual cause of accidental $O(n^2)$.
| Member | What it does | Cost | Allocates? |
|---|---|---|---|
| `s.size()` / `s.length()` | number of characters | $O(1)$ | no |
| `s.empty()` | is it zero-length | $O(1)$ | no |
| `s[i]` | character at `i`, unchecked | $O(1)$ | no |
| `s.at(i)` | character at `i`, throws if out of range | $O(1)$ | no |
| `s.front()` / `s.back()` | first / last character | $O(1)$ | no |
| `s.push_back(c)` / `s += c` | append one character | $O(1)$ amortised | sometimes |
| `s += t` / `s.append(t)` | append a string | $O(\lvert t \rvert)$ amortised | sometimes |
| `s.pop_back()` | remove the last character | $O(1)$ | no |
| `s.substr(i, n)` | **copy** of `n` characters from `i` | $O(n)$ | **yes** |
| `s.find(t)` | first index of `t`, or `npos` | $O(\lvert s \rvert \cdot \lvert t \rvert)$ | no |
| `s.insert(i, t)` | insert at `i` | $O(\lvert s \rvert + \lvert t \rvert)$ | maybe |
| `s.erase(i, n)` | remove `n` characters at `i` | $O(\lvert s \rvert)$ | no |
| `s.compare(t)` / `==` / `<` | lexicographic comparison | $O(\min)$ | no |
| `s.c_str()` | null-terminated `const char*` | $O(1)$ | no |
| `std::reverse(s.begin(), s.end())` | reverse in place | $O(n)$ | no |

```cpp title="The working set, demonstrated"
#include <algorithm>
#include <iostream>
#include <string>

int main() {
    std::string s = "interview";

    std::cout << s.size() << " " << s.front() << s.back() << "\n";
    std::cout << s.substr(0, 5) << " | " << s.substr(5) << "\n";
    std::cout << s.find("view") << " " << s.find("zzz") << "\n";

    std::string t = s;                     // a full copy: O(n)
    std::reverse(t.begin(), t.end());
    std::cout << t << "\n";

    t.erase(0, 4);                         // drop the first four
    std::cout << t << "\n";

    t.insert(0, ">> ");
    std::cout << t << "\n";

    std::cout << (std::string("abc") < std::string("abd")) << "\n";
    return 0;
}
```

```text nonum
9 iw
inter | view
5 18446744073709551615
weivretni
retni
>> retni
1
```

Look at the second number on line three. `s.find("zzz")` did not return $-1$; it
returned 18,446,744,073,709,551,615. That is `std::string::npos`, and it is the
subject of the next section.

## The npos trap

:::warning `find` does not return $-1$
`std::string::npos` is the largest value of `size_t` — an **unsigned** type.
Printed as a number it looks absurd; compared as a signed integer it behaves
unpredictably.

```cpp nonum frag
if (s.find("x") == std::string::npos) { }  // OK — the only correct test
if (s.find("x") == -1)              { }    // compiles, and is a trap
if ((int)s.find("x") == -1)         { }    // works by accident; do not rely on it
if (s.find("x") >= 0)               { }    // ALWAYS true: it is unsigned
```

That last line is the dangerous one. An unsigned value is never negative, so
`>= 0` is a tautology and the compiler may warn, or may not. The guard never
fires and the code proceeds as though the substring was found.

**The rule:** compare against `std::string::npos`, always, and nothing else.
:::

```cpp title="Finding, the right way"
#include <iostream>
#include <string>
#include <vector>

// Returns every starting index of `needle` in `hay`.
std::vector<int> findAll(const std::string& hay, const std::string& needle) {
    std::vector<int> out;
    if (needle.empty()) return out;
    size_t pos = hay.find(needle);
    while (pos != std::string::npos) {
        out.push_back((int)pos);
        pos = hay.find(needle, pos + 1);   // continue from just after the hit
    }
    return out;
}

int main() {
    for (int i : findAll("abababa", "aba")) std::cout << i << " ";
    std::cout << "\n";
    std::cout << findAll("abc", "zz").size() << "\n";
    std::cout << findAll("abc", "").size() << "\n";
    return 0;
}
```

```text nonum
0 2 4 
0
0
```

Note that the hits **overlap**: `"aba"` occurs at 0, 2 and 4 in `"abababa"`.
Searching from `pos + 1` finds overlapping occurrences; searching from
`pos + needle.size()` would find only the non-overlapping ones. Which you want
depends on the problem, and interviewers do ask.

## substr: the convenience that costs a copy

:::pitfall `substr` allocates and copies
`s.substr(i, n)` builds a brand-new string of `n` characters. It is $O(n)$ time
and $O(n)$ memory, every call.

That is fine once. Inside a loop it is usually a mistake:

```cpp nonum frag
// Checking every substring of length k — O(n·k), with n allocations
for (int i = 0; i + k <= (int)s.size(); ++i) {
    std::string window = s.substr(i, k);     // copy!
    if (isInteresting(window)) { }
}
```

Nearly always, you do not need the copy — you need to *look at* those
characters. Three ways to avoid it:

**Work with indices.** Pass `i` and `k` instead of a substring.

**Use a rolling window state.** A count array updated at the edges, which is
Part V of this book.

**Use `std::string_view`**, which is a pointer and a length with no copy at all.
:::

```cpp title="Three ways to examine every window of length k"
#include <iostream>
#include <string>
#include <string_view>

int main() {
    std::string s = "abcde";
    int k = 3;

    std::cout << "copies:   ";
    for (int i = 0; i + k <= (int)s.size(); ++i)
        std::cout << s.substr(i, k) << " ";        // O(k) copy each time
    std::cout << "\n";

    std::cout << "indices:  ";
    for (int i = 0; i + k <= (int)s.size(); ++i) { // no copy at all
        for (int j = i; j < i + k; ++j) std::cout << s[j];
        std::cout << " ";
    }
    std::cout << "\n";

    std::cout << "views:    ";
    std::string_view sv(s);
    for (int i = 0; i + k <= (int)sv.size(); ++i)
        std::cout << sv.substr(i, k) << " ";       // O(1): pointer + length
    std::cout << "\n";
    return 0;
}
```

```text nonum
copies:   abc bcd cde 
indices:  abc bcd cde 
views:    abc bcd cde 
```

Same output; the first line performs three heap allocations and the third
performs none.

:::definition `std::string_view`
A `string_view` is **a pointer and a length**. It does not own characters, does
not copy them, and does not allocate. `substr` on a view is $O(1)$ — it just
moves the pointer and shortens the length.

Use it for read-only access to a range of an existing string.
:::

:::warning A view does not keep its string alive
```cpp nonum skip
std::string_view bad() {
    std::string local = "temporary";
    return local;              // the string dies; the view dangles
}
```
This is Volume 1's dangling-pointer problem wearing new clothes: the view
points into memory that no longer exists. The same happens if you take a view
of a string and then `push_back` onto that string, because the reallocation
moves the characters.

**Rule:** a `string_view` must not outlive the string it views, and the string
must not be modified while a view of it exists.

In interview code, `const std::string&` is simpler and almost always fast
enough. Use `string_view` when you are slicing a lot and can see the lifetime
clearly.
:::

## Numbers and strings

```cpp title="Converting both ways, safely"
#include <iostream>
#include <string>

int main() {
    std::string s = std::to_string(42);
    std::cout << s + "!" << "\n";

    int n = std::stoi("123");
    long long big = std::stoll("9000000000");
    double d = std::stod("3.5");
    std::cout << n + 1 << " " << big << " " << d << "\n";

    // stoi stops at the first non-digit and reports how far it got.
    size_t used = 0;
    int partial = std::stoi("45abc", &used);
    std::cout << partial << " (consumed " << used << " chars)\n";

    // Failure throws, so guard it.
    try {
        std::stoi("hello");
    } catch (const std::invalid_argument&) {
        std::cout << "not a number\n";
    }
    return 0;
}
```

```text nonum
42!
124 9000000000 3.5
45 (consumed 2 chars)
not a number
```

:::pitfall `stoi` throws; manual parsing does not
Two failure modes people hit:

**`std::stoi("hello")` throws `std::invalid_argument`.** An unguarded call
inside a loop over user input will terminate the program.

**`std::stoi("99999999999")` throws `std::out_of_range`.** It does not clamp or
wrap — it throws.

When a problem guarantees well-formed input, `stoi` is fine. When it does not,
either catch, or parse by hand:
```cpp nonum frag
long long value = 0;
for (char ch : s)
    if (ch >= '0' && ch <= '9')
        value = value * 10 + (ch - '0');
```
That loop is also what the "string to integer" interview problems want you to
write, so it is worth being able to produce from memory — including the
overflow check, which Chapter 19 covers.
:::

## Iterating

```cpp title="Four ways to walk a string"
#include <iostream>
#include <string>

int main() {
    std::string s = "abc";

    for (int i = 0; i < (int)s.size(); ++i) std::cout << s[i];      // index
    std::cout << " ";
    for (char c : s) std::cout << c;                                 // by value
    std::cout << " ";
    for (char& c : s) c = c + 1;                                     // by reference
    std::cout << s << " ";
    for (auto it = s.rbegin(); it != s.rend(); ++it) std::cout << *it;  // reverse
    std::cout << "\n";
    return 0;
}
```

```text nonum
abc abc bcd dcb
```

Use the index form when you need to know *where* you are — which, in window and
two-pointer problems, is most of the time. Use `for (char c : s)` when you only
need the values, and `for (char& c : s)` when you intend to modify.

:::recap Chapter 2 in six lines
- Fifteen members cover almost all interview work; the costs are what matter.
- `find` returns `std::string::npos` on failure — compare against that and
  nothing else.
- `substr` **copies**: $O(n)$ time and memory. Prefer indices or a rolling
  state inside loops.
- `string_view` is a pointer plus a length, so slicing is $O(1)$ — but it must
  not outlive or be invalidated by its string.
- `s + t` builds a new string; `s += t` appends in place. Chapter 3 is about
  that difference.
- `stoi` throws on bad input and on overflow; guard it or parse by hand.
:::

:::exercise Practise
1. What does `s.find("x")` return when `x` is absent? Write the only correct
   test for that, and two incorrect ones.
2. `s.substr(2)` and `s.substr(2, 3)` — what does each return for
   `s = "abcdef"`? What does each cost?
3. Rewrite the "every window of length k" loop so it performs zero allocations
   and still prints the same thing.
4. Write `findAll` so it returns only **non-overlapping** occurrences. Which
   single number changes?
5. Why is `if (s.find('x') >= 0)` always true? What should it be?
6. Write a function that returns `true` when a string is a valid non-negative
   integer, without using `stoi`. What should it do for `""`?
7. Give two concrete situations where a `std::string_view` would dangle.
:::
