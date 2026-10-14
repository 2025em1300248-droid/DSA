# Beyond ASCII
@short: Beyond ASCII
@subtitle: What "the length of a string" actually means
@tier: core
@prereq: Chapters 1 and 4
@blurb: Every technique in the previous four chapters assumed one character is one byte. For most of the world's text that is false. This chapter explains what UTF-8 really stores, why `s.size()` is not the number of letters, and — most usefully for an interview — exactly which of your habits stay correct on arbitrary bytes and which quietly break.
@objectives:
- Explain what a code point is, and how UTF-8 encodes one in one to four bytes
- Say why `s.size()`, `s[i]` and `reverse` mean something different for UTF-8
- Identify the byte-wise operations that remain correct on UTF-8 input
- Count characters, rather than bytes, in UTF-8 text
- State the input assumption out loud when you solve a string problem

## Why this chapter exists

You will almost certainly never be asked to handle Unicode in a coding
interview. Problem statements say *"consists of lowercase English letters"*
precisely so that you do not have to.

So why spend a chapter on it? Two reasons, and the second is the real one.

**Because the assumption should be conscious.** When you write
`std::vector<int> count(26)`, you are asserting something about the input. An
interviewer who asks *"what if the input were arbitrary text?"* is checking
whether you knew you had made an assumption. "I assumed ASCII because the
constraints say so; if it were arbitrary text I would need a different table"
is a good answer. A blank look is not.

**Because this is where the production bugs live.** The gap between
"characters" and "bytes" is one of the most common sources of real defects in
real software: truncated names, mangled emoji, off-by-one slicing, a password
field that rejects a valid password. Knowing where the seam is makes you better
at the job the interview is for.

## Code points and bytes

:::definition Three different things
A **character** is what a reader sees: `A`, `é`, `日`, `🙂`.

A **code point** is the number Unicode assigns to it: `A` is U+0041 (65), `é`
is U+00E9 (233), `日` is U+65E5 (26,085), `🙂` is U+1F642 (128,578). There are
over a million possible code points.

A **byte** is what a `std::string` stores. An *encoding* decides how a code
point becomes bytes. UTF-8 is the encoding essentially all modern text uses.
:::

UTF-8 uses one to four bytes per code point, and the first byte tells you how
many follow.

@fig: utf8_encoding | 196 | How UTF-8 lays out a code point. ASCII characters keep their single byte unchanged, which is why UTF-8 is backward compatible. Larger code points use a lead byte whose high bits give the length, followed by continuation bytes that all begin `10`.

@tbl: The four UTF-8 forms. Note that no continuation byte can be mistaken for a lead byte, which is what makes the encoding self-synchronising.
| Code points | Bytes | Lead byte | Continuations |
|---|---|---|---|
| U+0000 – U+007F | 1 | `0xxxxxxx` | — |
| U+0080 – U+07FF | 2 | `110xxxxx` | one `10xxxxxx` |
| U+0800 – U+FFFF | 3 | `1110xxxx` | two `10xxxxxx` |
| U+10000 – U+10FFFF | 4 | `11110xxx` | three `10xxxxxx` |

Two consequences matter:

**ASCII is unchanged.** Any byte below 128 is exactly the ASCII character it
always was. A pure-ASCII string is byte-for-byte identical in UTF-8, so all of
Chapter 4 still applies to ASCII input.

**Every byte is unambiguous.** A continuation byte always starts with `10`, and
no lead byte does. So from any position you can tell whether you are at the
start of a character, and walk backwards to find one. That is why UTF-8 is
safe to search and split on ASCII delimiters.

## What `size()` tells you

```cpp title="Bytes are not characters"
#include <iostream>
#include <string>

int main() {
    std::string ascii = "hello";
    std::string accent = "café";          // the e-acute is two bytes
    std::string kanji = "\u65e5\u672c";      // two characters, three bytes each
    std::string emoji = "\U0001f642";          // one character, four bytes

    std::cout << ascii.size()  << " " << accent.size() << " "
              << kanji.size()  << " " << emoji.size()  << "\n";

    // Indexing gives a byte, not a character.
    std::cout << (int)(unsigned char)accent[3] << " "
              << (int)(unsigned char)accent[4] << "\n";
    return 0;
}
```

```text nonum
5 5 6 4
195 169
```

(`\u65e5` is C++'s *universal character name*: it means "the character with
code point U+65E5" and is exactly equivalent to typing the character itself.
This book writes the non-Latin characters that way so that every listing stays
printable in the book's monospace font.)

`"café"` has four characters and `size()` reports **5**. The `é` is the two
bytes 195 and 169, and neither of them is a character on its own. `accent[3]`
is not `é`; it is half of it.

:::pitfall Three operations that break on UTF-8
```cpp nonum frag
std::string sub = s.substr(0, 10);        // may cut a character in half
std::reverse(s.begin(), s.end());         // scrambles multi-byte characters
int letters = (int)s.size();              // counts bytes, not letters
```
**`substr`** by a byte count can split a multi-byte character, producing a
string that is not valid UTF-8. This is the bug behind every truncated name
that ends in a black diamond.

**`reverse`** reverses bytes. The continuation bytes end up before their lead
byte, so each multi-byte character becomes garbage. Reversing `"café"`
byte-wise does not give `"éfac"`.

**`size()`** is a byte count. For a length limit, a progress bar, or anything a
user sees, it is the wrong number.

None of these is a compiler error. They are all silently wrong on exactly the
inputs you did not test.
:::

## What still works

This is the practically useful half of the chapter.

:::insight Byte-wise logic is safe for ASCII targets
Because no multi-byte sequence contains a byte below 128, searching UTF-8 text
for an **ASCII** substring with byte comparison is correct. A byte equal to
`','` really is a comma, never part of a larger character.

So these remain correct on arbitrary UTF-8 input:

- `s.find("abc")`, and splitting on `,` or a space or a newline
- equality and `==` between two strings (identical characters means identical
  bytes, for text in the normal, already-normalised form)
- `std::sort` on bytes, if you only need *a* consistent order and not
  alphabetical order for a human
- counting with a **256-entry** table — every byte value is a valid index

And these are not:

- `count(26)` indexed by `c - 'a'` — reads out of bounds on any byte ≥ 128
- `isalpha`, `toupper`, `tolower` — they know nothing about `é`, and plain
  `char` makes them undefined behaviour as well
- anything that counts, slices, or reverses characters
:::

So Volume 1's two-pointer and sliding-window machinery is *structurally* fine
on UTF-8: the indices just address bytes. What breaks is any step inside the
window that assumes a byte is a character.

## Counting characters

Counting code points needs only one rule: **a character starts at every byte
that is not a continuation byte.** A continuation byte is one whose top two
bits are `10`, which is the test `(b & 0xC0) == 0x80`.

```cpp title="Counting characters rather than bytes"
#include <iostream>
#include <string>

// Number of UTF-8 code points. Assumes s is valid UTF-8.
int countChars(const std::string& s) {
    int count = 0;
    for (unsigned char b : s)
        if ((b & 0xC0) != 0x80) ++count;   // skip continuation bytes
    return count;
}

int main() {
    std::string s = "café \u65e5\u672c \U0001f642";
    std::cout << "bytes:      " << s.size()     << "\n";
    std::cout << "characters: " << countChars(s) << "\n";
    std::cout << "empty:      " << countChars("") << "\n";
    std::cout << "ascii:      " << countChars("hello") << "\n";
    return 0;
}
```

```text nonum
bytes:      17
characters: 9
empty:      0
ascii:      5
```

Nine characters: `c a f é` space `日 本` space `🙂`. Seventeen bytes: three for
`caf`, two for `é`, three each for the two kanji, four for the emoji, and one
for each of the two spaces — $3+2+3+3+4+2 = 17$. One pass, $O(n)$ in the byte
length, no allocation — and on pure ASCII input it returns exactly `size()`.

:::note Even code points are not quite "characters"
`countChars` counts code points, which is the right answer far more often than
`size()` is, but not always the answer a reader would give.

Some visible characters are built from several code points: `é` can be stored
either as the single U+00E9 or as `e` followed by a combining acute accent,
and a family emoji can be five code points joined by invisible connectors. A
reader counts one character; `countChars` counts two, or five.

Getting *that* right needs a Unicode library (ICU, or C++20's `std::format`
and friends for some of it). It is firmly outside this course. What is inside
this course is knowing that the layers exist: bytes, then code points, then
what a reader perceives — and saying which one a problem means.
:::

## The habit to build

@tbl: What to assume, and what to say. The right-hand column is what makes it an answer rather than a guess.
| The constraints say | Use | Say out loud |
|---|---|---|
| lowercase English letters | `vector<int>(26)`, `c-'a'` | "26 entries, because the input is lowercase" |
| ASCII / printable | `vector<int>(128)` or `(256)` | "128 entries indexed by the byte" |
| nothing about the alphabet | `vector<int>(256)` or a map | "I'll index by byte so any input is safe" |
| arbitrary Unicode text | decode first, then a map | "I'd iterate code points, not bytes" |

:::interview Answering "what if the input were Unicode?"
A short, honest answer that shows you know where the seam is:

> *"My solution indexes a 26-entry array by `c - 'a'`, which assumes lowercase
> ASCII — that's what the constraints give me. If the input were arbitrary
> UTF-8, two things change. The table has to become a hash map keyed by code
> point, because the alphabet is no longer small or dense. And anywhere I
> treat one byte as one character — the length, slicing, reversing — I'd need
> to decode UTF-8 first, since a character can be one to four bytes. The
> two-pointer structure itself still works; it's the per-character steps
> inside it that break."*

That is a complete answer in four sentences, and you do not need to have
memorised a single encoding table to give it. Note what it does **not** claim:
it does not promise this question will be asked. Interview content varies by
role, level, team and location, and this is simply a question that is
reasonable to be ready for.
:::

:::recap Chapter 5 in six lines
- A character, a code point and a byte are three different things;
  `std::string` stores bytes.
- UTF-8 uses one to four bytes per code point, and keeps ASCII byte-identical.
- A continuation byte always begins `10`, so `(b & 0xC0) == 0x80` detects one
  and the encoding is safe to scan from any position.
- `size()`, `s[i]`, `substr` and `reverse` all work in bytes, so they break on
  multi-byte characters — silently.
- Searching for ASCII substrings, splitting on ASCII delimiters, equality and
  a 256-entry count table all stay correct on arbitrary UTF-8.
- Say your input assumption out loud. That is the part the question is
  actually about.
:::

:::exercise Practise
1. How many bytes does `"héllo"` occupy in UTF-8? How many characters?
2. Why does `std::reverse` on a UTF-8 string produce invalid output, when
   reversing a pure-ASCII string is fine?
3. Give a byte value that can only be a continuation byte, and one that can
   only be a lead byte. How do you tell them apart in one expression?
4. Is `s.find(",")` correct on UTF-8 input? Justify your answer using the
   table of the four UTF-8 forms.
5. Why is `count(26)` indexed by `c - 'a'` actively dangerous on UTF-8 input,
   rather than merely wrong?
6. Write `truncateChars(const std::string& s, int k)` returning the first $k$
   *characters* of a valid UTF-8 string without splitting one in half.
7. You are asked to reverse the words of a sentence that may contain accented
   letters. Which parts of your usual solution are still correct, and which
   are not?
:::
