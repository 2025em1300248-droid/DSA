# How to Read This Book

You are holding a course, not a reference. It was written for one specific
person: somebody who can already write a `for` loop in some language, who has
heard the words "data structure" and felt a small chill, and who wants to
genuinely *understand* arrays and linked lists rather than memorise twenty
solutions and hope the interviewer picks one of them.

If that is you, read on. If you are already comfortable with pointers and
Big O, skip to Part III and start with the patterns.

## The promise

By the last page you will be able to look at an array or linked list problem
you have never seen before, and know **how to start**. Not because you have
seen it, but because you will recognise its shape. That is the whole game.

Every single idea in this book is introduced in the same order:

1. **A picture first.** You will see the memory before you see the code.
2. **An everyday analogy.** Something from the physical world that behaves
   the same way.
3. **A tiny example.** Three or four elements, never twenty.
4. **A hand trace.** We walk through it step by step, writing down the value
   of every variable at every moment.
5. **Then, and only then, the C++ code**, explained line by line.
6. **The common mistakes** — because knowing the five ways to get it wrong
   is more useful than knowing the one way to get it right.
7. **An exercise**, with the answer in Chapter 38.

## The rules I have set myself

:::insight The four promises
- **No unexplained words.** Every technical term is defined in plain English
  the first time it appears, and again in the glossary in Chapter 40.
- **No skipped steps.** If a line of code depends on an idea, that idea comes
  first — even if it means an extra page.
- **No cleverness before clarity.** You always see the obvious, slow solution
  before the fast, surprising one. The fast one is only impressive once you
  know what it is beating.
- **Nothing you cannot run.** Every program in this book compiles with
  `g++ -std=c++17` and produces exactly the output shown.
:::

## How the book is laid out

| Part | What it covers | Read it when |
|---|---|---|
| I | Data structures, memory, and Big O | First. Everything rests on it. |
| II | Arrays, `std::vector`, every basic operation | Straight after Part I |
| III | The ten array patterns | Once Part II feels comfortable |
| IV | Twenty-five array problems, graded | Alongside Part III |
| V | Pointers, the heap, `new` and `delete` | Before any linked list |
| VI | Linked lists built from nothing | After Part V, never before |
| VII | Linked list patterns and sixteen interview problems | After Part VI |
| VIII | Complexity comparison, and a method for unseen problems | Any time after Part VII |
| IX | Practice roadmap, answer key, mock interview, 30-day plan | Continuously |

## The symbols in the margin

Coloured boxes appear throughout. They always mean the same thing:

:::definition
A word is being given a precise meaning. These are worth re-reading.
:::

:::intuition
The *why* behind something, usually with an analogy. If a formal explanation
did not land, the intuition box is where to look.
:::

:::pitfall
A mistake that beginners make, with the reason it happens. I have made every
single one of these myself.
:::

:::perf
A note about speed or memory. Usually an explanation of why the obvious thing
is slower than it looks.
:::

:::interview
What an interviewer is actually listening for. These matter more than you
think — most candidates fail on communication, not on code.
:::

:::exercise
Something to do before reading on. Full answers are in Chapter 38.
:::

## How to actually study this

Reading a DSA book is almost useless. Here is what works:

1. **Read with a pen.** When a trace table appears, cover the answer column
   and fill it in yourself first.
2. **Type the code, do not copy it.** Typing forces you to read every
   character. Copying teaches your clipboard, not you.
3. **Break the code on purpose.** Change a `<` to a `<=`. Run it. Predict the
   bug before you see it. This single habit is worth fifty solved problems.
4. **Re-draw the diagrams from memory.** If you can draw the four pointer
   changes of a linked list insertion on a blank page, you know it. If you
   cannot, you have only recognised it.
5. **Do not move on when you are confused.** Confusion is information: it is
   telling you a prerequisite is missing. Go back one section.

:::note A word about speed
If a chapter takes you three days, that is normal and it is fine. This
material is not difficult because you are slow; it is difficult because it is
the first time anybody has asked you to hold a picture of memory in your head
while reading code. That skill is built, not born. Chapter 40 contains a
thirty-day plan if you would like a schedule to follow.
:::

Let us begin.
