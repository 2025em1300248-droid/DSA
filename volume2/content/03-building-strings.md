# Building Strings Without Quadratic Blowups
@short: Building Strings
@subtitle: The single most common accidental O(n²) in string code
@tier: core
@prereq: Chapter 2
@blurb: Concatenating in a loop is the string equivalent of inserting at the front of a vector: it looks like one cheap statement and it is secretly a full copy. This chapter measures the difference, explains exactly where the copies come from, and gives the four safe ways to build a string.
@objectives:
- Explain why `s = s + t` in a loop is $O(n^2)$ and `s += t` is $O(n)$
- Use `reserve` when the final length is known
- Build strings from pieces with `+=`, `append`, or an output buffer
- Reverse, repeat and join strings without hidden copies
- Recognise the same quadratic shape in other containers

## The two-line difference that changes the complexity

```cpp title="Two loops that look alike and are not"
#include <iostream>
#include <string>

int main() {
    std::string slow;
    for (int i = 0; i < 5; ++i)
        slow = slow + "ab";        // builds a NEW string every time

    std::string fast;
    for (int i = 0; i < 5; ++i)
        fast += "ab";              // appends in place

    std::cout << slow << "\n" << fast << "\n";
    std::cout << (slow == fast ? "same result" : "different") << "\n";
    return 0;
}
```

```text nonum
ababababab
ababababab
same result
```

Same answer. Very different cost.

:::insight Where the copies come from
`s = s + t` is three operations:

1. **Build a new string** large enough for `s` and `t` together.
2. **Copy** all of `s` into it, then all of `t`.
3. **Assign** that temporary back to `s`, destroying the old contents.

Step 2 copies the *whole* accumulated string. Do that $n$ times and the total
work is

$$1 + 2 + 3 + \cdots + n = \frac{n(n+1)}{2} = O(n^2)$$

`s += t` is one operation: write `t`'s characters into `s`'s spare capacity,
growing the block only when it fills. That is Volume 1's amortised argument
exactly — the total over $n$ appends is $O(n)$.
:::

@fig: str_concat_cost | 186 | Why `s = s + t` is quadratic. Each iteration allocates a new buffer and copies everything accumulated so far; the shaded area is the total copying. `s += t` writes into spare capacity and copies nothing until the block fills.

## Measuring it

Complexity arguments are more convincing with a number attached.

```cpp title="The same work, timed" norun
#include <chrono>
#include <iostream>
#include <string>

int main() {
    const int N = 40000;

    auto t0 = std::chrono::steady_clock::now();
    std::string slow;
    for (int i = 0; i < N; ++i) slow = slow + "ab";
    auto t1 = std::chrono::steady_clock::now();

    std::string fast;
    for (int i = 0; i < N; ++i) fast += "ab";
    auto t2 = std::chrono::steady_clock::now();

    std::string reserved;
    reserved.reserve(2 * N);
    for (int i = 0; i < N; ++i) reserved += "ab";
    auto t3 = std::chrono::steady_clock::now();

    using ms = std::chrono::duration<double, std::milli>;
    std::cout << "s = s + t   " << ms(t1 - t0).count() << " ms\n";
    std::cout << "s += t      " << ms(t2 - t1).count() << " ms\n";
    std::cout << "+ reserve   " << ms(t3 - t2).count() << " ms\n";
    std::cout << (slow == fast && fast == reserved ? "all equal\n" : "differ\n");
    return 0;
}
```

Compiled with `g++ -std=c++17 -O2` and run three times on the machine that
built this book, at $N = 40{,}000$:

```text nonum
s = s + t   44.2 ms      44.7 ms      38.6 ms
s += t      0.170 ms     0.161 ms     0.239 ms
+ reserve   0.130 ms     0.127 ms     0.212 ms
all equal
```

:::perf What those numbers say
**`s = s + t` is roughly 200–260× slower** than `s += t` at this size — and the
gap *widens* as $N$ grows, because one is quadratic and the other linear.
Double $N$ and the first takes four times as long while the second takes twice.
That multiplier is the thing to take away; the absolute milliseconds are not.

**`reserve` buys a further 1.2–1.3× here** by removing the reallocations. Note
how much smaller that is than the first effect: it is a **constant-factor** win,
not a complexity win, and the difference between those two kinds of improvement
is most of what Big O is for. It is still free to write when you know the size.

Your numbers will differ — these are one machine, one compiler, one afternoon,
and the run-to-run spread above (0.161 to 0.239 ms on identical work) shows how
noisy small timings are. The **ratio** is the stable part, and it is what the
complexity argument predicts.
:::

## The four safe ways to build

```cpp title="Four ways, all linear"
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> parts = {"one", "two", "three"};

    // 1. += in a loop
    std::string a;
    for (const std::string& p : parts) a += p + ",";
    if (!a.empty()) a.pop_back();

    // 2. reserve first, when the length is known or estimable
    size_t total = 0;
    for (const std::string& p : parts) total += p.size() + 1;
    std::string b;
    b.reserve(total);
    for (const std::string& p : parts) b += p + ",";
    if (!b.empty()) b.pop_back();

    // 3. append, which avoids building the temporary "p + ,"
    std::string c;
    for (const std::string& p : parts) { c.append(p); c.push_back(','); }
    if (!c.empty()) c.pop_back();

    // 4. a stringstream, when mixing types
    std::ostringstream oss;
    for (size_t i = 0; i < parts.size(); ++i) {
        if (i) oss << ',';
        oss << parts[i];
    }
    std::string d = oss.str();

    std::cout << a << "\n" << b << "\n" << c << "\n" << d << "\n";
    std::cout << (a == b && b == c && c == d ? "identical\n" : "differ\n");
    return 0;
}
```

```text nonum
one,two,three
one,two,three
one,two,three
one,two,three
identical
```

:::insight Which to use
**`+=` in a loop** is the default. It is linear, it reads clearly, and it is
what an interviewer expects.

**`reserve` first** when you can compute or bound the final length. Free
speed, one extra line.

**`append` / `push_back`** when you would otherwise build a temporary just to
append it. Note version 1 above writes `a += p + ","`, which *does* build a
small temporary each pass — harmless for short pieces, avoidable with version 3.

**`std::ostringstream`** when mixing numbers and text, where it beats manual
`to_string` calls for readability. It is somewhat slower than `+=`; use it for
clarity, not for speed.

What **not** to use: `s = s + t` in a loop, ever.
:::

## The same shape, elsewhere

:::pitfall Quadratic accumulation is not unique to strings
The pattern — *rebuild the whole accumulated thing each iteration* — appears
across containers, and it always has the same fix.

| Quadratic | Linear |
|---|---|
| `s = s + t` | `s += t` |
| `v.insert(v.begin(), x)` in a loop | `v.push_back(x)`, then `std::reverse` |
| `v = concat(v, w)` returning a new vector | `v.insert(v.end(), w.begin(), w.end())` |
| `s = c + s` (prepending) | build reversed with `+=`, then reverse once |
| `s.erase(0, 1)` in a loop | advance an index, or use a write pointer |

The last two are worth a second look. **Prepending** is the string version of
Volume 1's front-insertion problem: every prepend shifts everything right. If
you need to build a string backwards, append forwards and reverse once at the
end — one extra $O(n)$ pass instead of $n$ shifts.
:::

```cpp title="Building backwards, the right way"
#include <algorithm>
#include <iostream>
#include <string>

// Converts a non-negative integer to its decimal digits.
std::string toDecimal(int n) {
    if (n == 0) return "0";
    std::string out;
    while (n > 0) {
        out += char('0' + n % 10);   // digits come out BACKWARDS
        n /= 10;
    }
    std::reverse(out.begin(), out.end());   // one pass to fix it
    return out;
}

int main() {
    std::cout << toDecimal(0) << " " << toDecimal(7) << " "
              << toDecimal(12345) << "\n";
    return 0;
}
```

```text nonum
0 7 12345
```

The digits are produced least-significant-first, which is the wrong order. The
tempting fix — `out = char('0' + n % 10) + out` — prepends, and is quadratic.
Appending and reversing once is $O(d)$ for $d$ digits, and the reverse is a
single extra pass.

:::interview Say the word "amortised"
If you write `s += c` in a loop and the interviewer asks what it costs, the
full answer is:

> *"Each `+=` is amortised $O(1)$ — it writes into spare capacity, and when the
> block fills it doubles, which copies everything but happens only $\log n$
> times. So building the whole string is $O(n)$. If I knew the final length I'd
> `reserve` it and avoid the reallocations entirely, though that is a constant
> factor rather than a complexity change."*

That is Volume 1's Chapter 5 argument applied to a new container, which is
exactly what the interviewer is checking.
:::

:::recap Chapter 3 in five lines
- `s = s + t` rebuilds and copies everything each pass: $O(n^2)$ over a loop.
- `s += t` appends into spare capacity: amortised $O(1)$ each, $O(n)$ total.
- `reserve` removes the reallocations — a constant-factor win, free to write.
- Prepending is quadratic; append forwards and reverse once instead.
- The same quadratic-accumulation shape appears in vectors; the fix is always
  "mutate in place rather than rebuild".
:::

:::exercise Practise
1. Work out the exact number of characters copied when `s = s + "ab"` runs 1,000
   times, starting from an empty string.
2. Rewrite the loop below to be linear. What is the one-character change?
3. Write `repeat(s, k)` returning `s` concatenated `k` times, in
   $O(k \cdot \lvert s \rvert)$ with exactly one allocation.
4. Write `join(parts, sep)` that joins a vector of strings with a separator,
   with no trailing separator and one allocation. What should it return for an
   empty vector?
5. `toDecimal` builds backwards and reverses. Write the prepending version,
   state its complexity, and say at roughly what size you would notice.
6. Why is `std::ostringstream` slower than `+=` even though both are $O(n)$?
7. Name a container operation outside this chapter with the same quadratic
   accumulation shape, and give its linear fix.
:::

```cpp title="For exercise 2 — make this linear" nonum frag
std::string out;
for (int i = 0; i < 1000; ++i)
    out = out + "x";
```
