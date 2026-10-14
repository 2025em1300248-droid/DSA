# Characters as Numbers
@short: Chars as Numbers
@subtitle: Arithmetic on letters, and the 26-slot table it buys you
@tier: core
@prereq: Chapter 1
@blurb: Because a character is an integer, you can subtract one from another — and that single operation turns "count the letters" from a hash-map problem into an array-index problem, which is five to twenty times faster. This chapter establishes the arithmetic, builds the frequency table that half of Part VI depends on, and sets out exactly when the small-array version is safe.
@objectives:
- Map characters to small indices with `c - 'a'` and back again
- Classify characters as letters, digits or whitespace, safely
- Change case with arithmetic and with the standard functions
- Build a 26- or 128-entry frequency table and know when each is correct
- Explain why a count array beats a hash map for text, and by how much
- Avoid the signed-`char` bug that makes frequency tables read out of bounds

## The arithmetic

ASCII assigns consecutive codes to consecutive letters and digits. That is the
whole basis of the technique.

@fig: chr_ascii_map | 176 | The three consecutive runs that matter. Digits occupy 48–57, capitals 65–90 and lowercase 97–122. Because each run is consecutive, subtracting the run's first code turns a character into a 0-based index.

:::definition Character to index
For a lowercase letter `c`, the expression `c - 'a'` gives a number from 0 to
25: `'a' - 'a'` is 0, `'b' - 'a'` is 1, and so on.

Going back is the same step reversed: `char('a' + i)`.

This works because the letters are consecutive in ASCII. It would **not** work
for an alphabet whose letters were scattered through the code table, which is
one reason the technique is for ASCII text and not for arbitrary Unicode.
:::

```cpp title="The core conversions"
#include <iostream>
#include <string>

int main() {
    char c = 'f';
    std::cout << "index of 'f': " << (c - 'a') << "\n";
    std::cout << "letter 3:     " << char('a' + 3) << "\n";

    char d = '7';
    std::cout << "digit value:  " << (d - '0') << "\n";

    std::cout << "'a' = " << (int)'a' << ", 'A' = " << (int)'A'
              << ", gap = " << ('a' - 'A') << "\n";

    // Case change by arithmetic
    std::cout << char('d' - 32) << char('D' + 32) << "\n";
    return 0;
}
```

```text nonum
index of 'f': 5
letter 3:     d
digit value:  7
'a' = 97, 'A' = 65, gap = 32
Dd
```

The gap between a capital and its lowercase form is exactly 32 in ASCII, which
is why `c - 32` uppercases and `c + 32` lowercases. It is a cute trick and you
should **not** use it — the standard functions below say what they mean, handle
non-letters correctly, and cost nothing extra.

## Classifying characters

```cpp title="Classification, by hand and by the standard library"
#include <cctype>
#include <iostream>
#include <string>

int main() {
    std::string s = "a1 B!";

    std::cout << "char  alpha digit space upper lower\n";
    for (char c : s) {
        unsigned char u = (unsigned char)c;     // see the pitfall below
        std::cout << "'" << c << "'      "
                  << (std::isalpha(u) ? 1 : 0) << "     "
                  << (std::isdigit(u) ? 1 : 0) << "     "
                  << (std::isspace(u) ? 1 : 0) << "     "
                  << (std::isupper(u) ? 1 : 0) << "     "
                  << (std::islower(u) ? 1 : 0) << "\n";
    }

    std::cout << (char)std::tolower('Q') << (char)std::toupper('q') << "\n";
    return 0;
}
```

```text nonum
char  alpha digit space upper lower
'a'      1     0     0     0     1
'1'      0     1     0     0     0
' '      0     0     1     0     0
'B'      1     0     0     1     0
'!'      0     0     0     0     0
qQ
```

Read the table one row at a time. `'a'` is a letter and lowercase; `'1'` is a
digit and nothing else; a space is whitespace only; `'B'` is a letter and
uppercase; `'!'` is none of the five. The last line is `tolower('Q')` followed
by `toupper('q')`, and both need the `(char)` cast — these functions return
`int`, so without it you would see `113 81`.

:::warning Pass `unsigned char` to the `is*` functions
This is the most common portability bug in C++ string code.

```cpp nonum frag
char c = text[i];
if (std::isalpha(c)) { }               // undefined behaviour for c > 127
if (std::isalpha((unsigned char)c)) { } // correct
```

`std::isalpha` and friends take an `int`, and the standard requires that value
to be representable as `unsigned char` or to equal `EOF`. Plain `char` is
**signed** on x86 and ARM Linux, so any byte above 127 — any accented letter,
any UTF-8 continuation byte — arrives as a negative number, which is neither.

In practice the implementation indexes a lookup table, so a negative argument
reads before the start of that table. It usually appears to work. It is still
undefined behaviour, and it is the kind that fails on the one input you did not
test.

**Always cast to `unsigned char` first.** Every example in this book does.
:::

## The frequency table

Here is the pay-off, and it is the single most used technique in Part VI.

:::definition A count array
When the alphabet is small and known, a character's own value can be its index
into a plain array of counts.

For lowercase English: `std::vector<int> count(26, 0)`, indexed by `c - 'a'`.
For arbitrary bytes: `std::vector<int> count(256, 0)`, indexed by
`(unsigned char)c`.

This is Volume 1's frequency-counting pattern with the hash map removed — and
removing it is worth a large constant factor.
:::

@fig: chr_count_array | 176 | A 26-slot count array. The character *is* the index, so counting is one increment at a computed address — no hashing, no pointer chasing, and the whole table fits in two cache lines.

```cpp title="Counting letters, two ways"
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

int main() {
    std::string s = "mississippi";

    // 1. Count array — the character is the index.
    std::vector<int> count(26, 0);
    for (char c : s) ++count[c - 'a'];

    std::cout << "array: ";
    for (int i = 0; i < 26; ++i)
        if (count[i]) std::cout << char('a' + i) << count[i] << " ";
    std::cout << "\n";

    // 2. Hash map — works for any character, costs more per access.
    std::unordered_map<char, int> freq;
    for (char c : s) ++freq[c];

    std::cout << "map:   ";
    for (char c = 'a'; c <= 'z'; ++c)            // iterate in a fixed order
        if (freq.count(c)) std::cout << c << freq[c] << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
array: i4 m1 p2 s4 
map:   i4 m1 p2 s4 
```

Notice the second loop. An `unordered_map` has **no defined iteration order**,
so printing by walking the map would give a different order on a different
compiler — and an output that changes between runs is not an output you can put
in a book or compare in a test. Iterating `'a'` to `'z'` and asking the map
makes it deterministic.

:::perf How much faster is the array?
Both are $O(n)$. The constant differs a lot:

**Count array:** one subtraction, one address calculation, one increment. The
26 integers are 104 bytes — two cache lines, resident the whole time.

**Hash map:** hash the key, mask it to a bucket, follow a pointer to a node,
compare the key, increment. The nodes are separately allocated and scattered,
so most accesses miss cache.

Compiled with `g++ -std=c++17 -O2` and run three times on the machine that
built this book, counting the characters of a 10-million character lowercase
string:

```text nonum
array 5.14 ms   map 32.0 ms
array 5.23 ms   map 32.5 ms
array 5.21 ms   map 31.9 ms
```

About **6×**. One machine, one compiler, one input shape — your ratio will
differ, and on a smaller alphabet or a warmer cache it may differ a lot. The
ordering is what you should carry away, not the number.

**The rule:** if the alphabet is small, known and dense, use an array. Reach for
a hash map when the keys are large, sparse, or not characters at all.
:::

## Choosing the table size

@tbl: Which table for which input. Getting this wrong is either a correctness bug or a waste of memory.
| Input | Table | Index |
|---|---|---|
| lowercase English only | `vector<int>(26)` | `c - 'a'` |
| upper and lower | `vector<int>(52)` | `islower(c) ? c-'a' : 26 + c-'A'` |
| letters and digits | `vector<int>(128)` | `(unsigned char)c` |
| any byte, any input | `vector<int>(256)` | `(unsigned char)c` |
| Unicode text | `unordered_map` | the code point — see Chapter 5 |

:::pitfall The 26-slot table is a promise about the input
```cpp nonum frag
std::vector<int> count(26, 0);
for (char c : text) ++count[c - 'a'];     // breaks on ' ', 'A', '!', or any digit
```
A space is 32, so `' ' - 'a'` is $-65$: the increment writes 65 integers before
the start of the array. That is memory corruption, it compiles cleanly, and it
usually does not crash.

Use 26 slots **only** when the problem states the input is lowercase letters —
and say so out loud when you write it:

> *"The constraints say lowercase English letters, so I'll use a 26-entry
> array rather than a hash map. If that assumption were wrong I'd move to 256
> entries, or a map."*

If the input is unconstrained, use 256 entries indexed by `(unsigned char)c`.
It costs one kilobyte and it cannot be made to read out of bounds.
:::

## Comparing two tables

The pattern behind anagram problems: build one table, subtract the other, and
check that nothing is left over.

```cpp title="Are two strings anagrams? One table, not two"
#include <iostream>
#include <string>
#include <vector>

bool isAnagram(const std::string& a, const std::string& b) {
    if (a.size() != b.size()) return false;        // cheap rejection first
    std::vector<int> count(256, 0);
    for (char c : a) ++count[(unsigned char)c];    // add for a
    for (char c : b) --count[(unsigned char)c];    // subtract for b
    for (int x : count) if (x != 0) return false;  // anything left over -> no
    return true;
}

int main() {
    std::cout << isAnagram("listen", "silent") << "\n";
    std::cout << isAnagram("rat", "car")       << "\n";
    std::cout << isAnagram("a", "ab")          << "\n";
    std::cout << isAnagram("", "")             << "\n";
    std::cout << isAnagram("aab", "abb")       << "\n";
    return 0;
}
```

```text nonum
1
0
0
1
0
```

Three details worth copying:

**The length check comes first.** It is $O(1)$ and rejects most negative cases
before any work.

**One table, not two.** Adding for the first string and subtracting for the
second means the array ends all-zero exactly when they match. Two tables and a
comparison would also work, with twice the memory and an extra loop.

**256 entries, not 26.** The signature takes arbitrary strings, so the
constraint that would justify 26 does not exist here.

$O(n)$ time; $O(1)$ space, because 256 is a constant that does not grow with the
input.

:::recap Chapter 4 in six lines
- A character is an integer, so `c - 'a'` is a 0-based index and
  `char('a' + i)` is the way back.
- Cast to `unsigned char` before calling `isalpha`, `tolower` or indexing a
  table.
- A count array indexed by the character beats a hash map by a large constant
  factor — measured at about 6× on this machine.
- 26 slots is a **promise about the input**; 256 slots is unconditionally safe.
- Add for one string and subtract for the other: all-zero means equal
  multisets.
- An `unordered_map` has no iteration order, so iterate a fixed range and query
  it when you need deterministic output.
:::

:::exercise Practise
1. What is `'z' - 'a'`? What is `char('a' + 25)`? What is `'9' - '0'`?
2. Write `isDigit(char)` without `cctype`. What is the correct comparison?
3. Why is `std::isalpha(c)` undefined behaviour for `char c = 200` on Linux?
   Write the fixed line.
4. A 26-entry table is indexed with `c - 'a'`. What happens for `c = ' '`, and
   why does it often not crash?
5. Write `firstUniqueChar(const std::string&)` returning the index of the first
   character that occurs once, or $-1$. How many passes do you need?
6. Modify `isAnagram` to ignore case and spaces. Which line changes?
7. Explain, in terms of memory, why a 26-entry array beats an `unordered_map`
   for counting letters — and name an input where the map would be the right
   choice.
:::
