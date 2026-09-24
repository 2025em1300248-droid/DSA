# How to Use This Map

This is not a list of technologies. Lists of technologies go stale in a year
and, worse, they encourage the wrong behaviour: collecting tool names instead
of building capability. This is a list of **capabilities** --- things you must
be able to *do* --- with the tools named only where a specific tool has become
the default and knowing it saves you time.

## What each chapter contains

| Section | What it gives you |
|---|---|
| `WHAT THIS IS FOR` | Why the skill exists, in one paragraph, with the failure it prevents |
| `THE CAPABILITIES` | A checklist of concrete, testable things you should be able to do |
| `THE TOOLS` | What the field has actually standardised on, and what is still contested |
| `HOW TO TELL YOU HAVE IT` | A task you can attempt; if you cannot, you do not have the skill |
| `COMMON PITFALL` | What people get wrong here, repeatedly |
| `TIME TO COMPETENCE` | An honest estimate at roughly 12 hours a week |

Each capability is tagged with the level it belongs to:

:::note The four tiers used throughout
**ESSENTIAL** --- every AI/ML engineering role expects this. Not having it
will end an interview.

**CORE** --- expected in most roles; the difference between junior and mid.

**SPECIALIST** --- deep in one column of the role map; how you become the
person others ask.

**AWARENESS** --- you need to know it exists, what it is for, and when to go
and learn it. You do not need to be able to do it today.
:::

## An honest caveat about currency

Concepts in this map are durable: attention, retrieval, evaluation,
quantisation, distributed training, the economics of inference. The *tooling*
around them moves faster than any document can. Where a specific library is
named it is because it had become the default at the time of writing (2026);
before committing a quarter of your learning time to any named tool, check
that it is still the one people reach for. The capability outlives the tool,
which is why the capability is what this map is organised around.

Where a claim depends on hardware, pricing or a vendor, treat the numbers as
orders of magnitude to reason with, not as quotes.

## How to actually use it

**Do not read it front to back and then start.** Read Chapter 1, pick the
role you are aiming at, then read Chapter 22 and choose a track. From that
point on the map is a reference: you read a chapter when its track week
arrives, and you come back to Chapter 24 monthly to re-score yourself.

**Build while you read.** Every chapter has a `HOW TO TELL YOU HAVE IT`
section containing a task. Those tasks are the point. Reading a chapter
without attempting its task produces recognition, which feels like knowledge
and disappears in a fortnight.

**Score yourself honestly.** Chapter 24 has a rubric with five levels per
area. Most people score themselves one level too high on things they have
read about and one level too low on things they have shipped. The correction
is to ask "what did I build with this, alone, that broke and that I fixed?"

:::insight The single highest-leverage thing in this document
If you take one thing: **learn to evaluate**. Chapter 15. Almost every team
building on foundation models is bottlenecked not by modelling skill but by
the inability to tell whether a change made things better. Engineers who can
build an honest evaluation harness are, right now, scarce out of proportion
to how hard the skill is.
:::
