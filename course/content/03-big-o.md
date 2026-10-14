# Big O From Absolute Zero
@short: Big O Notation
@subtitle: How to say "this gets slow when the input grows" in one symbol
@tier: foundation
@prereq: Chapter 2
@blurb: Big O is not mathematics for its own sake; it is a vocabulary for a single practical question — *what happens to my program when the input gets ten times bigger?* This chapter builds the notation from counting lines of code, explains every rule (including the two that look like cheating), and ends with a recipe you can apply to any C++ function on sight.
@objectives:
- Count the operations a piece of C++ code performs, as a function of input size
- Explain why we drop constants and keep only the fastest-growing term
- Recognise $O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$ and $O(2^n)$ on sight
- Explain why nested loops usually give $O(n^2)$ and why halving gives $O(\log n)$
- Distinguish best case, average case and worst case, and know which one we quote
- Measure space complexity and tell auxiliary space from total space
- Read the complexity of unfamiliar code using a four-step recipe

## The question Big O answers

You have written two programs that both do the job. One is 40 lines, one is 8
lines. Which should you use?

You cannot answer by timing them, because the answer would depend on your
laptop, your compiler, how warm your processor is, and what else is running.
Run the same test tomorrow and you get a different number.

So we ask a better question — one whose answer is the same on every machine
that has ever existed:

:::insight The only question that matters
**If I make the input ten times bigger, how much more work does this do?**

If the answer is "ten times more work", the program scales well. If it is "a
hundred times more work", it scales badly. If it is "no extra work at all",
the program is wonderful.

Big O is just a compact way of writing that answer.
:::

## Counting steps, slowly

Let us count. Here is a function that adds up an array of $n$ numbers.

```cpp title="Summing an array"
int sum(const std::vector<int>& v) {
    int total = 0;                      // 1 step
    for (int i = 0; i < v.size(); ++i) { //  the loop runs n times
        total += v[i];                  // 1 step, n times  -> n steps
    }
    return total;                       // 1 step
}
```

Count the steps for an array of $n$ numbers:

- `total = 0` happens once. That is **1** step.
- The body `total += v[i]` happens once per element. That is **$n$** steps.
- `return total` happens once. That is **1** step.
- The loop bookkeeping (`i < v.size()` and `++i`) is roughly 2 more steps per
  iteration, so **$2n$**.

Total: $3n + 2$ steps.

Now do the same for a function that returns the first element:

```cpp title="Getting the first element"
int first(const std::vector<int>& v) {
    return v[0];                        // 1 step, always
}
```

Total: $1$ step. Not $1$ step per element — **one step, full stop**, whether
the array has 5 elements or 5 billion.

@fig: bigo_counting | 150 | Two functions, counted. The first does work proportional to the size of the input; the second does a fixed amount of work. That difference — proportional versus fixed — is the only thing Big O records.

## The two rules that look like cheating

We said `sum` takes $3n + 2$ steps. Big O throws away almost all of that and
writes simply $O(n)$. Two rules do the throwing:

:::definition Rule 1 — drop the constants
$3n$ becomes $n$. $100n$ also becomes $n$. We do not care about the multiplier.
:::

:::definition Rule 2 — keep only the fastest-growing term
$n^2 + 500n + 9000$ becomes $n^2$. Everything except the biggest term is
discarded.
:::

These look like vandalism. They are not. Here is why each is justified.

**Why dropping constants is fair.** The constant depends on things we are not
trying to measure: your processor, your compiler's optimiser, whether the data
is in cache. A $3n$ algorithm on a slow machine and a $30n$ algorithm on a fast
machine can take exactly the same wall-clock time. What *cannot* change is that
both of them do ten times more work when $n$ gets ten times bigger. That shared,
machine-independent fact is what we are recording.

**Why dropping smaller terms is fair.** Because for large $n$ they stop
mattering — not approximately, but overwhelmingly.

| $n$ | $n^2$ | $500n$ | $9000$ | $500n + 9000$ as % of total |
|---:|---:|---:|---:|---:|
| 10 | 100 | 5,000 | 9,000 | 99.3% |
| 100 | 10,000 | 50,000 | 9,000 | 85.5% |
| 1,000 | 1,000,000 | 500,000 | 9,000 | 33.7% |
| 10,000 | 100,000,000 | 5,000,000 | 9,000 | 4.8% |
| 1,000,000 | $10^{12}$ | $5 \times 10^8$ | 9,000 | 0.05% |

At $n = 10$ the $n^2$ term is a rounding error. At $n = 1{,}000{,}000$ it is
essentially the whole cost. Big O describes what happens **as $n$ grows**, and
in that limit only the fastest-growing term survives.

:::pitfall What this means in practice
Big O deliberately ignores small inputs. An $O(n^2)$ algorithm can easily beat
an $O(n \log n)$ one for $n = 20$ — this is exactly why real sorting libraries
switch to insertion sort for tiny arrays.

So: Big O is a statement about **scaling**, not a promise about any particular
input. Use it to choose between designs; use a real measurement to tune a
specific case.
:::

## The definition, in English and then in symbols

:::definition Big O
We say an algorithm is $O(g(n))$ if, **once $n$ gets large enough**, its step
count is **at most** some fixed multiple of $g(n)$.

Formally: $f(n) = O(g(n))$ if there exist constants $c > 0$ and $n_0$ such that
$f(n) \le c \cdot g(n)$ for all $n \ge n_0$.

In English: *"beyond some point, $g$ is an upper boundary for how fast this
grows, if we are allowed to scale $g$ up by a constant."*
:::

@fig: bigo_definition | 150 | What the definition is saying. We may stretch $g(n)$ vertically by any constant $c$ we like, and we may ignore everything to the left of some threshold $n_0$. All that must be true is that beyond that point the stretched $g$ stays above $f$.

You will rarely use the formal definition. It is here so that when somebody
says "but Big O is only an upper bound", you know what they mean: $O(n)$ code
is *also* technically $O(n^2)$, in the same way that somebody 170 cm tall is
"at most 3 metres tall". True, but unhelpful. By convention we always quote the
**tightest** bound we can.

## The six complexities you must know on sight

@fig: bigo_growth | 168 | The growth hierarchy. Each curve eventually and permanently overtakes everything below it. The only question that matters for a given algorithm is which band it lives in.

Here they are, from best to worst, each with the mental image that makes it
stick.

### $O(1)$ — constant time

The work does not depend on $n$ at all.

```cpp nonum frag
int x = v[500];      // one address calculation, one read
v.push_back(9);      // amortised O(1) - see Chapter 5
```

**Image:** looking up a word when you already know the page number.

### $O(\log n)$ — logarithmic time

Each step throws away **half** of what is left.

**Image:** the guessing game. "I am thinking of a number from 1 to 1000." If
you always guess the middle, you need at most 10 questions, because
$2^{10} = 1024 > 1000$.

:::definition What $\log n$ means here
$\log_2 n$ is the answer to: *"how many times can I halve $n$ before I reach
1?"* For $n = 1000$ it is about 10. For $n = 1{,}000{,}000$ it is about 20.
For $n = 1{,}000{,}000{,}000$ it is about 30.

In computer science $\log$ always means $\log_2$ unless stated otherwise, and
because constants are dropped, the base does not actually matter.
:::

That table is the whole reason logarithmic algorithms feel like magic: a
billion-element array needs only about 30 steps.

### $O(n)$ — linear time

You touch every element a fixed number of times.

```cpp nonum frag
for (int x : v) total += x;     // one pass
```

**Image:** reading every page of a book once.

### $O(n \log n)$ — linearithmic time

You do a logarithmic amount of work for each of $n$ elements, or you split the
problem in half repeatedly and do linear work at each level.

**Image:** sorting. This is the best any comparison-based sort can do, and
`std::sort` achieves it.

### $O(n^2)$ — quadratic time

For each element, you look at every element.

```cpp nonum frag
for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
        if (v[i] + v[j] == target) { /* ... */ }
```

**Image:** everybody in a room shaking hands with everybody.

### $O(2^n)$ — exponential time

Every extra element **doubles** the work.

**Image:** trying every possible subset. At $n = 50$ there are
$2^{50} \approx 10^{15}$ subsets — about 11 days of work if you can check a
billion per second. At $n = 60$ it is 30 years.

### What these mean in real seconds

Assume a machine doing 100 million simple operations per second — roughly
right for ordinary C++.

@tbl: What each complexity costs at realistic input sizes. The dashes are not "slow"; they are "will not finish".
| $n$ | $O(1)$ | $O(\log n)$ | $O(n)$ | $O(n \log n)$ | $O(n^2)$ | $O(2^n)$ |
|---:|---|---|---|---|---|---|
| 10 | instant | instant | instant | instant | instant | instant |
| 1,000 | instant | instant | instant | instant | 0.01 s | — |
| 100,000 | instant | instant | 0.001 s | 0.017 s | 100 s | — |
| 1,000,000 | instant | instant | 0.01 s | 0.2 s | 2.8 hours | — |
| 10,000,000 | instant | instant | 0.1 s | 2.3 s | 11.6 days | — |

:::interview The number to memorise
Interviewers expect you to know that **about $10^8$ simple operations per
second** is the right order of magnitude. From that single number you can
reason out loud: *"n is $10^5$, so $O(n^2)$ is $10^{10}$ operations, which is
about 100 seconds — too slow. I need at least $O(n \log n)$."*

Saying that sentence in an interview is worth more than knowing a clever trick.
:::

## Why nested loops give $O(n^2)$

This is asked constantly, so let us see it rather than assert it.

```cpp title="The classic quadratic pattern" frag
for (int i = 0; i < n; ++i) {        // outer: runs n times
    for (int j = 0; j < n; ++j) {    // inner: runs n times, for EACH i
        doSomething(v[i], v[j]);     // so this runs n x n times
    }
}
```

The inner loop does not run $n$ times in total. It runs $n$ times **for every
single value of `i`**, and `i` takes $n$ values. So the body executes
$n \times n = n^2$ times.

@fig: bigo_nested | 158 | Why nesting multiplies. Each row is one pass of the outer loop, and each row contains a full inner loop. Count the cells: $n$ rows of $n$ cells is $n^2$.

A common variation starts the inner loop at `i + 1`:

```cpp title="The triangular variation - still quadratic" frag
for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j)
        doSomething(v[i], v[j]);
```

Now the inner loop runs $n-1$ times, then $n-2$, then $n-3$, down to $0$.
Adding those up:

$$(n-1) + (n-2) + \cdots + 1 + 0 = \frac{n(n-1)}{2} = \frac{n^2 - n}{2}$$

Drop the constant $\frac{1}{2}$ and the smaller term $-n$, and you are left
with $n^2$. **It is still $O(n^2)$** — it does half the work of the full
version, but halving is a constant factor, and constants are dropped.

:::pitfall Nested loops are not automatically $O(n^2)$
Look at what the loops actually count, not at how deeply they nest.

```cpp nonum frag
for (int i = 0; i < n; ++i)
    for (int j = 0; j < 10; ++j)     // fixed 10, not n
        work();
```
This is $10n$ steps, which is $O(n)$. The inner loop does not depend on $n$.

Conversely, a *single* loop can be quadratic if its body is linear:
```cpp nonum frag
for (int i = 0; i < n; ++i)
    v.insert(v.begin(), i);          // each insert shifts n elements: O(n)
```
One loop, $O(n^2)$ total. **Always ask what the body costs.**
:::

## Why halving gives $O(\log n)$

Suppose you have $n$ items and each step throws away half.

| After this many steps | Items remaining |
|---:|---|
| 0 | $n$ |
| 1 | $n/2$ |
| 2 | $n/4$ |
| 3 | $n/8$ |
| $k$ | $n/2^k$ |

You stop when one item is left, so you want the $k$ where $n/2^k = 1$, that is
$2^k = n$, that is $k = \log_2 n$.

@fig: bigo_halving | 146 | Binary search on 16 elements. Four halvings reach a single element, and $\log_2 16 = 4$. Doubling the array to 32 elements adds exactly one more step, not 16 more.

:::intuition Why logarithms feel so powerful
Going from 1,000 to 1,000,000 elements multiplies a linear algorithm's work by
1,000. It multiplies a logarithmic algorithm's work by **two** (from about 10
steps to about 20).

This is why sorted data is worth so much, and why Chapter 12 spends a whole
chapter on binary search.
:::

## Best, average and worst case

The same algorithm can do different amounts of work on different inputs of the
same size. Searching an array for a value:

```cpp title="Linear search"
int find(const std::vector<int>& v, int target) {
    for (int i = 0; i < (int)v.size(); ++i)
        if (v[i] == target) return i;   // might happen immediately
    return -1;                          // or we check everything
}
```

- **Best case:** the target is at index 0. One comparison. $O(1)$.
- **Worst case:** the target is at the end, or absent. $n$ comparisons. $O(n)$.
- **Average case:** if the target is present and equally likely to be anywhere,
  you check $n/2$ elements on average. Drop the constant: $O(n)$.

:::insight Which one do we quote?
**The worst case, almost always.** Three reasons:

1. It is a *guarantee*. "Never slower than this" is a useful promise; "usually
   fast" is not, because somebody will hand you the unusual input.
2. The worst case is often the common case in disguise — searching for
   something that is not there is the normal outcome of a search.
3. Average case requires assuming a distribution of inputs, and real inputs
   are rarely random.

When this book writes a bare complexity with no qualifier, it means the worst
case. Where the average differs importantly (quicksort, hash tables) it is
stated explicitly.
:::

@fig: bigo_cases | 128 | The three cases for linear search. The quoted complexity, $O(n)$, is the guarantee — the line nobody can push you above.

## Space complexity

Everything so far has been about *time*. The same notation measures *memory*.

:::definition Space complexity
**Space complexity** is how much memory an algorithm uses, as a function of the
input size $n$, using the same $O(\cdot)$ notation.

**Auxiliary space** is the memory an algorithm needs *in addition to* the
input. **Total space** includes the input itself.

When a problem says "solve this in $O(1)$ space", it always means **auxiliary**
space — you are allowed to have the input; you are not allowed to make a copy
of it.
:::

Three examples, all operating on an array of $n$ integers:

```cpp title="O(1) auxiliary space - a few variables, whatever n is"
int maxOf(const std::vector<int>& v) {
    int best = v[0];            // 1 int
    for (int x : v)             // 1 more int for the loop
        if (x > best) best = x;
    return best;
}
```
Two extra integers. Not $2n$ — two. $O(1)$ auxiliary space.

```cpp title="O(n) auxiliary space - a second array as big as the input"
std::vector<int> doubled(const std::vector<int>& v) {
    std::vector<int> out;
    out.reserve(v.size());      // n new ints
    for (int x : v) out.push_back(x * 2);
    return out;
}
```
The new vector grows with $n$. $O(n)$ auxiliary space.

```cpp title="O(n) space you did not ask for - recursion"
int sumTo(int n) {
    if (n == 0) return 0;
    return n + sumTo(n - 1);    // n nested calls, each one a stack frame
}
```
This looks like it uses no memory. It uses $O(n)$, because each of the $n$
pending calls keeps a frame on the call stack. For large $n$ it crashes with a
stack overflow. **Recursion depth is space.** Remember this when you meet the
recursive linked list reversal in Chapter 28.

@fig: bigo_space | 150 | Three shapes of space usage. A handful of variables is $O(1)$; a second array is $O(n)$; and a chain of $n$ pending recursive calls is also $O(n)$, even though no array appears anywhere in the code.

## Time–space trade-offs

Very often you can buy time with memory, or memory with time.

| Problem | Low memory | Low time |
|---|---|---|
| Does this array contain duplicates? | Sort it, then scan: $O(n \log n)$ time, $O(1)$ extra | Hash set: $O(n)$ time, $O(n)$ extra |
| Sum of elements from $i$ to $j$, asked many times | Loop each time: $O(n)$ per query, $O(1)$ extra | Prefix sums: $O(1)$ per query, $O(n)$ extra |
| Nth Fibonacci number | Recompute: exponential time, $O(n)$ stack | Memoise: $O(n)$ time, $O(n)$ space |

:::insight The trade-off is the real skill
Beginners look for "the fast solution". Experienced engineers ask "what am I
willing to spend?". In an interview, saying *"I can do this in $O(n)$ time if I
may use $O(n)$ extra space, or $O(n \log n)$ time with no extra space — which
would you prefer?"* is a strong answer by itself.
:::

## A recipe for reading any C++ function

Here is a procedure that works. Apply it mechanically until it becomes
instinct.

:::checklist How to find the complexity of code you have never seen
1. **Decide what $n$ is.** The length of the array? The value of a number? The
   number of nodes? Write it down — most mistakes happen here.
2. **Find the loops and the recursion.** Straight-line code with no loops is
   $O(1)$, however long it is.
3. **For each loop, ask two questions:** *how many times does it run?* and
   *what does one iteration cost?* Multiply them. A loop with `i++` from 0 to n
   runs $n$ times; a loop with `i *= 2` runs $\log n$ times; a loop whose bound
   depends on an outer loop needs a sum, as in the triangular example above.
4. **Watch for hidden costs in the body** — the table below lists the usual
   traps, every one of which looks like a single cheap statement.
5. **Add the parts, then simplify.** Sequential blocks add ($O(n) + O(n) = O(n)$);
   nested blocks multiply ($O(n) \times O(\log n) = O(n \log n)$). Then drop
   constants and lower-order terms.
:::

@tbl: Innocent-looking C++ that is not free. Every one of these is a single statement that hides a loop.
| Statement | Real cost | Why |
|---|---|---|
| `v.insert(v.begin(), x)` | $O(n)$ | every element shifts right |
| `v.erase(v.begin())` | $O(n)$ | every element shifts left |
| `s.substr(a, b)` | $O(b)$ | it copies the characters |
| `s1 + s2` (strings) | $O(\lvert s_1 \rvert + \lvert s_2 \rvert)$ | a new string is built |
| `std::find(v.begin(), v.end(), x)` | $O(n)$ | a linear scan |
| `f(std::vector<int> v)` | $O(n)$ per call | the vector is copied on entry |
| `m[key]` for `std::map` | $O(\log n)$ | a balanced tree walk |
| `m[key]` for `std::unordered_map` | $O(1)$ average | a hash lookup |

Let us run the recipe on an unfamiliar function.

```cpp title="Apply the recipe to this"
bool hasPairSum(std::vector<int> v, int target) {
    std::sort(v.begin(), v.end());
    for (int i = 0; i < (int)v.size(); ++i) {
        int need = target - v[i];
        if (std::binary_search(v.begin(), v.end(), need)) return true;
    }
    return false;
}
```

1. **$n$** is `v.size()`.
2. There is one loop, plus a sort, plus a call inside the loop.
3. The parameter is taken **by value**, so the vector is copied on entry:
   $O(n)$ time and $O(n)$ space. (A reference would avoid this, but then we
   could not sort it — a real design decision, not a mistake.)
4. `std::sort` is $O(n \log n)$.
5. The loop runs $n$ times; each iteration calls `binary_search`, which is
   $O(\log n)$. So the loop is $O(n \log n)$.
6. Total: $O(n) + O(n \log n) + O(n \log n) = O(n \log n)$ time,
   $O(n)$ auxiliary space (that copy).

:::exercise Complexity drills
State the time and auxiliary space complexity of each, and say what $n$ is.

```cpp nonum
// (a)
int f(std::vector<int>& v) {
    int s = 0;
    for (int i = 0; i < (int)v.size(); ++i) s += v[i];
    for (int i = 0; i < (int)v.size(); ++i) s -= v[i];
    return s;
}

// (b)
void g(int n) {
    for (int i = 1; i < n; i *= 2)
        for (int j = 0; j < n; ++j)
            std::cout << i << j;
}

// (c)
int h(std::vector<int> v) {        // note: by value
    std::vector<int> copy = v;
    return copy.size();
}

// (d)
void k(int n) {
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < i; ++j)
            for (int l = 0; l < j; ++l)
                work();
}

// (e)
int m(std::vector<int>& v) {
    std::vector<int> out;
    for (int x : v) out.insert(out.begin(), x);
    return out[0];
}
```

6. An algorithm takes $n^2 / 1000 + 50n$ steps. What is its Big O? For which
   values of $n$ is the $50n$ term actually the larger one? What does that tell
   you about trusting Big O for small inputs?
7. You need to process $n = 10^6$ items in under one second. Using the
   $10^8$-operations-per-second rule, which complexities are acceptable?
:::

## What you should take away

:::recap Chapter 3 in eight lines
- Big O answers one question: **how does the work grow as the input grows?**
- Drop constants, keep the fastest-growing term — both are justified by what
  happens for large $n$.
- The hierarchy: $O(1) < O(\log n) < O(n) < O(n \log n) < O(n^2) < O(2^n)$.
- Nested loops **multiply**; sequential blocks **add**.
- Halving each step gives $O(\log n)$ — about 20 steps for a million items.
- We quote the **worst case** unless we say otherwise, because it is a
  guarantee.
- **Auxiliary space** excludes the input. Recursion depth counts as space.
- About $10^8$ operations per second is the number to reason with out loud.
:::
