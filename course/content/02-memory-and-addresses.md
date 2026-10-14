# Memory, Variables and Addresses
@short: Memory and Addresses
@subtitle: What is really happening when you write int x = 42;
@tier: foundation
@prereq: Chapter 1
@blurb: Everything in this book — array indexing, pointer arithmetic, why insertion shifts elements, why a linked list node can live anywhere — is a consequence of how memory works. This chapter builds that picture from a single bit up to a block of integers, using nothing but diagrams and three tiny C++ programs you can run yourself.
@objectives:
- Explain what a bit, a byte and an address are, in plain words
- Say exactly what the computer does when it reads the line `int x = 42;`
- Use `sizeof` and `&` to see the size and address of any variable
- Read a memory diagram and work out the address of any element in a block
- Explain why values stored side by side can be reached by calculation
- Describe the difference between a variable's *name*, its *address*, and its *value*

## The smallest thing there is

A computer stores everything — numbers, letters, pictures, this sentence — as
switches that are either off or on. One switch is called a **bit**, and its
value is written as $0$ or $1$.

One bit is not very useful. You can say yes or no with it and nothing more. So
bits are grouped into eights.

:::definition Bit and byte
A **bit** is one switch: $0$ or $1$.

A **byte** is a group of 8 bits. Because each of the 8 bits can be $0$ or $1$,
one byte has $2^8 = 256$ possible patterns, so a byte can represent any whole
number from $0$ to $255$.

The byte is the unit the computer actually works in. When we talk about memory,
we count bytes.
:::

@fig: mem_bit_byte | 108 | One bit is a switch. Eight bits make a byte, and a byte has 256 possible patterns — enough for a small number or a single character of English text.

256 is not a lot. You cannot store the number 1,000,000 in one byte. So for
bigger numbers the computer uses **several bytes together**. In C++, the type
`int` normally uses **4 bytes** — that is 32 bits, which gives
$2^{32} \approx 4.3$ billion patterns, enough to hold any whole number from
about $-2$ billion to $+2$ billion.

| C++ type | Typical size | What it can hold |
|---|---|---|
| `bool` | 1 byte | `true` or `false` |
| `char` | 1 byte | One character, e.g. `'A'` |
| `int` | 4 bytes | Whole numbers, about $\pm 2$ billion |
| `long long` | 8 bytes | Whole numbers, about $\pm 9 \times 10^{18}$ |
| `float` | 4 bytes | Decimal numbers, ~7 digits of precision |
| `double` | 8 bytes | Decimal numbers, ~15 digits of precision |
| a pointer | 8 bytes | An address (on a 64-bit machine) |

:::note "Typical" size
The C++ standard does not force these sizes; it only sets minimums. On every
machine you are likely to use in 2026, the table above is correct. If you ever
need certainty, `sizeof(int)` tells you the truth on *your* machine, and we
use it in the first program below.
:::

## Memory is a numbered street

Now picture the computer's memory — its RAM — as an extremely long street of
houses, where **each house holds exactly one byte**, and the houses are
numbered $0, 1, 2, 3, \dots$ with no gaps.

:::definition Address
The number of a byte in memory is called its **address**. It is just a
position: "the 1,000th byte". Addresses start at $0$ and go up by $1$ for each
byte.

The crucial property: **if the processor knows an address, it can read that
byte immediately** — it does not have to walk past the other bytes to get
there. Address 4 and address 4,000,000,000 take the same amount of time.
:::

@fig: mem_street | 126 | Memory, byte by byte. Each small box is one byte with its own address. A four-byte int occupies four consecutive boxes, and we name the whole group by the address of its first byte.

Look carefully at the picture. An `int` is 4 bytes, so it occupies **four
houses in a row**, say addresses 1000, 1001, 1002 and 1003. When we say "the
int lives at address 1000" we mean "it starts at 1000 and continues for
`sizeof(int)` bytes".

That phrase — *starts here and continues for this many bytes* — is the single
most important idea in this chapter. Hold on to it.

## What a variable actually is

Now we can answer the question properly.

```cpp title="The simplest C++ program that has anything in memory"
#include <iostream>

int main() {
    int x = 42;
    std::cout << x << "\n";
    return 0;
}
```

Output:

```text nonum
42
```

What happened when the computer ran line 4?

1. The compiler decided *"this function needs 4 bytes of space for a variable
   called `x`"*, and set aside four consecutive bytes somewhere. Say those
   bytes turn out to be at addresses 1000–1003.
2. The pattern of bits meaning 42 was written into those four bytes.
3. The name `x` was recorded — **in the compiler, not in memory** — as "the
   `int` that lives at address 1000".

That third point surprises people, so let us say it loudly:

:::insight The name is not stored anywhere
The word `x` does not exist while your program runs. It exists only while your
program is being *compiled*. The compiler translates every use of `x` into
"the 4 bytes at address 1000" and then throws the name away.

A variable is nothing but **a name the compiler gives to an address**, plus a
type that says how many bytes to read there and how to interpret them.
:::

@fig: mem_variable | 150 | What `int x = 42;` actually creates. The name lives in the compiler, the value lives in memory, and the address is the bridge between them. Three different things that beginners often merge into one.

Three separate things, and you must be able to tell them apart:

| Thing | Example | Where it lives |
|---|---|---|
| The **name** | `x` | In the compiler only |
| The **address** | 1000 | A number; you can print it |
| The **value** | 42 | In the bytes at that address |

## Seeing it for yourself

C++ gives you two operators that let you look at all of this directly.

- `sizeof(thing)` — how many **bytes** does this type or variable occupy?
- `&variable` — the **address** of this variable. Read `&` out loud as
  "address of".

```cpp title="Looking at memory directly" norun
#include <iostream>

int main() {
    int x = 42;
    char c = 'A';
    double d = 3.14;

    std::cout << "sizeof(int)    = " << sizeof(int)    << " bytes\n";
    std::cout << "sizeof(char)   = " << sizeof(char)   << " bytes\n";
    std::cout << "sizeof(double) = " << sizeof(double) << " bytes\n\n";

    std::cout << "value of x   = " << x  << "\n";
    std::cout << "address of x = " << &x << "\n";
    std::cout << "address of c = " << (void*)&c << "\n";
    std::cout << "address of d = " << &d << "\n";
    return 0;
}
```

A possible output (your addresses will be different — that is fine and
expected):

```text nonum
sizeof(int)    = 4 bytes
sizeof(char)   = 1 bytes
sizeof(double) = 8 bytes

value of x   = 42
address of x = 0x7ffd4b2a3c5c
address of c = 0x7ffd4b2a3c5b
address of d = 0x7ffd4b2a3c50
```

Line by line, the parts that matter:

- **Line 8** — `sizeof(int)` gives `4`. This is not a guess; it is your
  machine answering.
- **Line 13** — `&x` is the address of `x`. It prints as something like
  `0x7ffd4b2a3c5c`. The `0x` prefix means the number is written in
  **hexadecimal** (base 16) because addresses are long and hex is shorter. You
  never need to do hex arithmetic in this book; just read it as "some big
  number".
- **Line 14** — `(void*)&c`. Without the `(void*)`, `std::cout` would see a
  `char*` and try to print the *text* starting at that address instead of the
  address itself. Casting to `void*` says "treat this as a plain address".
  This is a C++ quirk, not a concept — do not let it worry you.

:::pitfall Addresses change on every run
If you run that program twice you will get different addresses. Modern
operating systems deliberately move programs around in memory each time they
start, for security. The *relationships* between addresses stay the same; the
absolute numbers do not. Never write code that depends on a specific address.
:::

## Two variables, side by side? Not necessarily

Here is where beginners get an incorrect mental picture. If you write:

```cpp nonum frag
int a = 10;
int b = 20;
int c = 30;
```

you might assume `a`, `b` and `c` sit next to each other in memory in that
order. **They might. They might not.** The compiler is free to arrange
separate variables however it likes — reordered, with gaps between them for
alignment, or kept entirely in processor registers and never written to memory
at all.

This matters enormously, because it is exactly the problem an array solves.

:::insight Why arrays exist, in one sentence
Three separate `int` variables give you no guarantee about where they are. An
array of three `int`s gives you a **promise**: these values are in one block,
in order, with no gaps.

That promise is the entire reason arrays are fast, and it is the subject of
Chapter 4.
:::

@fig: mem_three_vs_array | 160 | Three separate variables versus an array of three. On the left the compiler may place them anywhere, in any order. On the right the language guarantees one contiguous block — and a guarantee is something you can calculate with.

## Address arithmetic: the pay-off

Because an array is a guaranteed block, you can compute where any element is
without looking at memory at all. Here is the rule, and it is worth
memorising because it explains half of this book:

:::definition The address formula
If an array starts at address $B$ and each element takes $S$ bytes, then
element number $i$ (counting from $0$) lives at address

$$\text{address}(i) = B + i \times S$$

Nothing is searched. It is one multiplication and one addition — a fixed,
tiny amount of work no matter how large $i$ is or how long the array is.
:::

Let us check it with a real program.

```cpp title="Seeing the address formula with your own eyes" norun
#include <iostream>

int main() {
    int arr[5] = {10, 20, 30, 40, 50};

    std::cout << "element size = " << sizeof(arr[0]) << " bytes\n\n";
    for (int i = 0; i < 5; ++i) {
        std::cout << "arr[" << i << "] = " << arr[i]
                  << "   at address " << &arr[i] << "\n";
    }
    return 0;
}
```

A possible output:

```text nonum
element size = 4 bytes

arr[0] = 10   at address 0x7ffe8c3b1a40
arr[1] = 20   at address 0x7ffe8c3b1a44
arr[2] = 30   at address 0x7ffe8c3b1a48
arr[3] = 40   at address 0x7ffe8c3b1a4c
arr[4] = 50   at address 0x7ffe8c3b1a50
```

Look at the last two hexadecimal digits: `40`, `44`, `48`, `4c`, `50`. In
hexadecimal those go up by 4 each time (`4c` is 76 in ordinary numbers, and
`50` is 80). Exactly four bytes apart, exactly as the formula promises,
exactly `sizeof(int)`.

@fig: mem_address_formula | 150 | The address formula in action. Element 3 of this array is found by one multiplication and one addition — never by looking at elements 0, 1 and 2 first.

:::intuition An analogy for the formula
A hotel corridor where every room is the same width. If room 0 is at the start
of the corridor and each room is 4 metres wide, you know room 37 is 148 metres
along without walking past rooms 1 to 36.

Now imagine a corridor where rooms are different sizes and scattered across
several buildings. To find room 37 you have to ask at room 0, which tells you
where room 1 is, and so on. That is a linked list, and that is why it is
slower to reach a position — and faster to add a room.
:::

## Where memory comes from: a first look

Not all memory is the same. There are two places your data can live, and the
difference becomes critical in Part VI. For now, a one-paragraph preview.

:::definition The stack and the heap
The **stack** is memory the compiler manages for you automatically. Local
variables like `int x = 42;` live here. It is fast, and it is cleaned up for
you the moment the function ends. The catch: the size must be known when the
program is compiled, and it is small — typically 1–8 MB in total.

The **heap** is memory you ask for while the program is running, with `new`
(and give back with `delete`). It can be large and its size can be decided at
run time. The catch: **you** are responsible for giving it back, and if you
forget, the memory is lost until the program exits.

Every linked list node you will ever create lives on the heap. Chapter 22
covers this properly.
:::

@fig: mem_stack_heap | 152 | The two regions. Local variables are automatic and short-lived; anything created with `new` lives until you say otherwise. Every node of every linked list in this book is a heap object.

## Common misunderstandings

:::pitfall Four things that are not true
**"A variable is a box."** It is closer to a *label stuck on a stretch of
bytes*. The distinction matters as soon as two labels refer to the same bytes,
which is what references and pointers do.

**"`int` is always 4 bytes."** Overwhelmingly common, not guaranteed. Use
`sizeof` when it matters.

**"Address 1000 is slower to reach than address 8."** No. Reading any single
address costs the same. (Reading many *nearby* addresses is faster than many
*scattered* ones, for cache reasons — but that is a refinement, not a
contradiction. Chapter 33 revisits it.)

**"Declaring a variable sets it to 0."** In C++, a local variable you do not
initialise contains **whatever bytes happened to be there already**. Reading it
is undefined behaviour and a classic source of bugs that appear and disappear
at random. Always initialise.
:::

```cpp title="The uninitialised-variable trap"
#include <iostream>

int main() {
    int good = 0;        // explicitly initialised - always 0
    int bad;             // uninitialised - contains leftover bytes
    std::cout << good << "\n";
    std::cout << bad  << "\n";   // could print 0, 32767, -1094795586, anything
    return 0;
}
```

The dangerous part is that `bad` very often prints `0` on a simple test,
which convinces you the code is fine. Then it prints garbage the day you
demonstrate it to somebody.

## What you should take away

:::recap Chapter 2 in seven lines
- A **bit** is one switch; a **byte** is 8 bits; memory is a long row of
  numbered bytes.
- An **address** is the number of a byte. The processor reaches any address in
  the same tiny time.
- A multi-byte value like an `int` occupies **consecutive** bytes, and we name
  it by the address of its first byte.
- A **variable** is a name the compiler gives to an address, plus a type that
  says how many bytes and how to read them.
- `sizeof` tells you the byte count; `&` tells you the address.
- Separate variables have **no guaranteed arrangement**; an array does, and
  that guarantee is what makes indexing fast.
- $\text{address}(i) = B + i \times S$ — the formula behind every array access
  in this book.
:::

:::exercise Before you go on
1. How many distinct patterns can 2 bytes represent? Show your working.
2. An array of `double` starts at address 2000. At what address does element 6
   begin? Which formula did you use, and what was $S$?
3. Explain, to somebody who has never programmed, the difference between a
   variable's *name*, its *address*, and its *value*.
4. Write a program that prints `&x` and `&y` for two `int` locals. Run it
   three times. Do the addresses change between runs? Does the *difference*
   between them change?
5. Why can the compiler put three separate `int` variables anywhere it likes,
   but not three elements of an `int` array?
6. A student says "my linked list is slow because its nodes are at high memory
   addresses". Using this chapter, explain why that reasoning is wrong, and
   suggest the real reason linked lists are slower to traverse.
:::
