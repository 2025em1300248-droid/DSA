# How to Learn From This Book

This is the teaching volume. The *Skill Map* tells you which competencies
matter and in what order; this book contains the competencies themselves,
each one built from the ground up.

## The shape of every chapter

Each chapter follows the same arc, because it is the arc that works.

**The problem first.** No chapter opens with a definition. It opens with
something that goes wrong, or costs too much, or cannot be explained --- and
the chapter's material is what resolves it. You retain an idea attached to a
problem; you forget an idea attached to nothing.

**Then the smallest correct version.** Every mechanism is built in its
simplest honest form before any optimisation. You will implement a hash-free
tokeniser before BPE, a single-head attention before multi-head, a
train--test split before cross-validation. The simple version is what you
will actually reason with when the complicated one breaks at 3am.

**Then what makes it real.** The simple version is never the production
version, and the gap between them is where the engineering lives. Every
chapter closes that gap explicitly.

**Then the failure modes.** Named, with symptoms. Most of the value in ten
years of experience is a catalogue of failures and their signatures; this
book hands you the catalogue directly.

:::insight Why the code is short
Every listing in this book is meant to be read in full, typed out, and run.
None of them is a framework. A forty-line implementation you understand
completely beats a four-line library call you do not, because when the
library call misbehaves --- and it will --- only the first gives you anywhere
to stand.
:::

## How to actually use it

**Type the code.** Not copy --- type. The difference in retention is large and
well documented, and typing forces you to read every line, which is where the
understanding is.

**Break things deliberately.** Several chapters ask you to introduce a bug and
observe its signature. Do these. Recognising a symptom in two seconds instead
of two hours is most of what senior engineers are paid for.

**Do the exercises marked with a dagger.** Each chapter's exercise set is
ordered by difficulty; the ones marked † are the ones that teach
something the prose could not.

**Read out of order once you have Part I and II.** Parts III through VIII are
largely independent. Follow whatever you need for the thing you are building.

:::note What this book assumes
Python fluency at the level of writing a few hundred lines comfortably, and
comfort with the command line. No mathematics beyond school algebra is
assumed --- Part II builds what it needs. No machine learning is assumed at
all.
:::

:::warning The one failure mode of technical books
Reading feels like learning and is not. Recognition --- "yes, I have seen
this" --- decays within weeks and gives no ability to produce. The
distinguishing test is whether you can write it on a blank page with the book
closed. Every chapter's exercises exist to force that test early, while the
material is still recoverable.
:::
