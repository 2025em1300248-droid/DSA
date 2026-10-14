# What a Data Structure Really Is
@short: What Is a Data Structure?
@subtitle: Why the arrangement of your data decides the speed of your program
@tier: foundation
@blurb: Before arrays, before pointers, before a single line of C++, there is one idea to settle: a data structure is a *decision about arrangement*, and that decision — made once, early — fixes what your program can do quickly for the rest of its life. This chapter builds that idea from a kitchen drawer up to a formal definition, and shows you the two arrangements this book is about.
@objectives:
- Say in your own words what a data structure is and why anybody needs one
- Explain why *where* data sits in memory changes how fast you can use it
- Describe the two fundamental arrangements: one block, or many linked pieces
- Read the shape of a problem and guess which arrangement suits it
- Understand what "operation" means and why we count operations at all

## Start with a drawer

Imagine two kitchen drawers.

The first drawer is a mess. Forks, knives, spoons, a bottle opener and three
batteries, all thrown in together. The second drawer has a cutlery tray:
forks in one slot, knives in the next, spoons in the third.

Both drawers hold the same objects. The same forks, the same knives. Nothing
has been added and nothing removed. Yet one of them is obviously better, and
if I ask you *why*, you will say something like "because in the second one
you can **find** things".

That is the whole subject. You have just explained data structures.

:::definition Data structure
A **data structure** is a way of arranging data in a computer's memory, chosen
so that the operations you care about are fast.

Two parts matter in that sentence. *Arranging* — the data is laid out in some
specific shape. *The operations you care about* — different jobs want
different shapes. There is no best drawer, only a drawer that is best for what
you do most.
:::

Notice what the definition does **not** say. It does not say a data structure
makes your data smaller, or more correct, or prettier. It changes exactly one
thing: **how much work it takes to do something with the data.**

@fig: ds_drawer | 136 | Two drawers, identical contents. The arrangement is the only difference, and the arrangement is everything: finding a fork in the left drawer means searching the whole drawer; in the right one you go straight to the slot.

## What "data" means here

Let us be careful, because "data" is one of those words that sounds obvious
and then turns out to be vague.

:::definition Data
**Data** is any collection of values your program is holding on to. A list of
exam marks. The names of everybody in a class. The pixels of a photograph. The
moves played so far in a chess game.

In this book, data will almost always be a group of numbers, because numbers
keep the diagrams short. Everything you learn applies identically to names,
records, or anything else.
:::

So the subject of this book is: *you have a group of values; how should you
lay them out so your program can work with them quickly?*

## Why arrangement changes speed at all

Here is the part that trips up beginners, so we will go slowly.

A computer's memory is not magic. It is a very long row of numbered boxes.
Each box holds a small amount of information, and each box has a number — its
**address** — the way houses on a street have numbers. (Chapter 2 does this
properly; for now the picture is enough.)

@fig: ds_memory_street | 118 | Memory as a street of numbered houses. The processor can jump to any house instantly if it knows the number. What it cannot do is know a number it was never told.

The processor is very good at one thing: *"go to address 4,000 and tell me
what is there."* That takes the same tiny amount of time no matter which
address you name. Address 8 and address 8,000,000 cost the same.

But the processor is only good at that when it **knows the address**. And
whether it knows the address depends entirely on how you arranged the data.

Two arrangements are possible, and they lead to two completely different
worlds:

:::insight The two arrangements, and the whole book
**Arrangement 1 — one solid block.** Put all the values side by side in
memory, with no gaps. Now, if you know where the block starts, you can
*calculate* the address of value number 7 with a tiny piece of arithmetic. No
searching. This is an **array**, and it is Parts II–IV.

**Arrangement 2 — scattered pieces, each holding a signpost.** Put each value
wherever there is room, and have each piece store the address of the next
piece. Now you cannot calculate anything; you must follow the signposts one by
one. But you can add a new piece anywhere without disturbing anything else.
This is a **linked list**, and it is Parts V–VII.

Everything else in this book — every strength, every weakness, every
interview question — comes from these two sentences.
:::

@fig: ds_two_shapes | 182 | The two arrangements side by side. Top: an array, one unbroken block, so element 3's address is pure arithmetic. Bottom: a linked list, scattered across memory, where the only way to reach element 3 is to walk from the front.

Look at the two pictures and ask yourself two questions.

**"How do I get the 3rd element?"** In the array you compute an address and
jump — one step. In the linked list you start at the front and follow three
signposts — three steps. With a million elements it would be one step versus a
million steps. The array wins enormously.

**"How do I insert a new value at the front?"** In the array, every existing
value has to shuffle one place to the right to make room — with a million
elements that is a million moves. In the linked list you make one new piece
and point it at the old front — one step. The linked list wins enormously.

Neither structure is better. They are better at *different questions*. Learning
which question you are being asked is the skill.

## What we mean by an "operation"

I keep saying "fast" and "steps". Let us make that precise enough to be useful
without being precise enough to be painful.

:::definition Operation
An **operation** is one thing you ask a data structure to do: *get the element
at position 5*, *insert the value 42 at the front*, *find out whether 99 is in
here*, *delete the last element*.

When we say a data structure is fast, we always mean: *fast at some particular
operation*. Never fast in general.
:::

The operations we will care about, over and over, are these six:

| Operation | What it means | Everyday version |
|---|---|---|
| **Access** | Get the element at a known position | "Give me the 7th book on the shelf" |
| **Search** | Find whether a value is present, and where | "Is there a copy of *Dune* here?" |
| **Insert** | Add a new value at some position | "Squeeze this book in at position 3" |
| **Delete** | Remove the value at some position | "Take out the 3rd book and close the gap" |
| **Update** | Change the value at a known position | "Replace the 7th book with another one" |
| **Traverse** | Visit every element once, in order | "Read the title of every book" |

For every structure in this book we will fill in a table: what does each of
these six cost? Those tables are the entire practical content of data
structures. Everything else is explanation.

:::intuition Why we count steps instead of timing with a stopwatch
A stopwatch measures your laptop on a Tuesday. If you time the same program on
a faster machine, the number changes, but the *shape* of the answer does not:
if one method needed a million steps and another needed three, that stays true
on every machine ever built.

So we count steps, not seconds. Chapter 3 turns this into a proper notation.
:::

## A first look at the cost of a wrong choice

Let us make this concrete with a small story, because abstract claims are
unconvincing.

Suppose you are storing the names of students arriving at an exam hall, and
students arrive one at a time. You decide to keep the list **sorted
alphabetically at all times**, so you insert each new name into its correct
position.

With an array, every insertion in the middle means shifting everybody after
it. If 10,000 students arrive, the total work is roughly
$10{,}000 \times 10{,}000 / 2 = 50$ million small moves. On a modern machine
that is fast enough that you would not notice — perhaps a tenth of a second.

Now make it a million students. The work is not a hundred times larger; it is
ten thousand times larger — about 500 billion moves. Your program, which
seemed fine in testing, now takes several minutes. Nothing broke. No bug was
introduced. The arrangement simply did not scale.

:::insight The real lesson
Choosing the wrong data structure does not usually produce a *wrong* program.
It produces a program that is correct and unusably slow — and that is much
harder to notice, because it works perfectly on your small test data.
:::

This is why the subject matters, and it is why interviewers ask about it. They
are not testing whether you can write a loop. They are testing whether you can
predict what will happen when the input gets large.

## The map of this book

Here is where we are going, so you always know why you are reading something.

@fig: ds_roadmap | 206 | The road through this book. Each box depends on the ones before it, which is why the order matters: pointers before linked lists, memory before arrays, Big O before everything.

Notice that Part V — pointers and memory — sits *between* arrays and linked
lists. That placement is deliberate. Most people who struggle with linked
lists are not struggling with linked lists at all; they are struggling with
pointers, and nobody ever taught them pointers properly. We will not make that
mistake.

## Why arrays and linked lists first

There are dozens of data structures: stacks, queues, trees, graphs, hash
tables, heaps, tries. Why spend an entire book on two of them?

Because the other dozens are **built out of these two**.

- A **stack** and a **queue** are an array or a linked list with a rule about
  which end you are allowed to touch.
- A **hash table** is an array of buckets, where each bucket is usually a
  linked list.
- A **graph** is most often stored as an array of linked lists.
- A **tree** is a linked list where each node has two signposts instead of one.
- A **heap** is a tree pretending to be an array.

Learn these two properly and the rest of the subject is variations. Learn them
badly and every later structure will feel like magic.

:::interview Why interviewers love these two
Roughly a third of all coding-interview questions are array questions, and
linked list questions are the classic test of whether you can manipulate
pointers without losing your place. More importantly: these two structures are
where an interviewer can see you *think*, because the brute-force solution is
always obvious and the good solution never is.
:::

## What you should take away

:::recap Chapter 1 in six lines
- A data structure is an **arrangement** of data chosen to make certain
  operations fast.
- Memory is a long row of numbered boxes; the processor can jump to any box
  instantly **if it knows the number**.
- An **array** is one solid block, so positions can be *calculated*.
- A **linked list** is scattered pieces joined by signposts, so positions must
  be *walked to*.
- Arrays are fast at reaching a position; linked lists are fast at adding and
  removing pieces.
- There is no best structure, only a structure that fits the operations you
  perform most.
:::

:::exercise Before you go on
1. A music app stores your playlist. You mostly press "skip to track 47" and
   almost never reorder tracks. Which arrangement fits better, and why?
2. A text editor stores the characters of a document. You mostly type in the
   middle. Which arrangement fits better, and why?
3. In your own words, and without using the word "fast", explain why putting
   values side by side in memory lets you jump straight to the 7th one.
4. Name one operation an array is bad at, and say *why* it is bad at it in
   terms of memory, not in terms of Big O (which you have not met yet).
5. The chapter claimed "a hash table is an array of buckets, where each bucket
   is usually a linked list". Without knowing anything about hash tables,
   guess why both structures are needed instead of just one.
:::

Answers are in Chapter 38. Do not skip them — the answers explain reasoning
the chapter did not have room for.
