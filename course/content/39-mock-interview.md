# The Mock Interview
@short: Mock Interview
@subtitle: Four rounds, with what the interviewer is actually listening for
@tier: practice
@prereq: Parts I to VIII
@blurb: Four complete interview rounds, each with the problem, a realistic transcript of a strong answer, and a commentary on what earned the marks. The commentary matters more than the solutions — in a coding interview, roughly half the assessment is about how you communicate while solving, and that half is almost never practised.
@objectives:
- Know what an interviewer is assessing, beyond whether the code works
- Structure an answer out loud, from clarification to complexity
- Handle a hint, a follow-up and a bug without losing composure
- Recognise the five behaviours that cost candidates offers
- Run a realistic mock session on your own

## What is actually being assessed

@fig: mock_rubric | 176 | A typical rubric. Correct code is necessary and is roughly a third of the score. The other two thirds are things you can practise independently of the problems.

:::insight The four categories, and what each looks like
**Problem solving (≈35%).** Did you reach a working solution? Did you improve
it? Did you find the optimisation yourself, or need the hint?

**Coding (≈30%).** Is the code correct, readable and complete? Are the edge
cases handled? Would it compile?

**Communication (≈20%).** Did you clarify before coding? Did you think out loud?
Could the interviewer follow your reasoning? Did you take hints gracefully?

**Verification (≈15%).** Did you test it yourself? Did you state the complexity
unprompted? Did you find your own bug, or did the interviewer have to?

Most candidates practise only the first two. The last two are easier to improve
and are where offers are most often lost.
:::

## Round 1 — Warm-up (15 minutes)

> **Interviewer.** Given an array of integers, move all the zeroes to the end
> while keeping the order of the non-zero elements. Do it in place.

:::note A strong answer, as a transcript
**Candidate.** *Let me make sure I have it. Input is a vector of ints, I rearrange
it in place so every zero is at the end, and the non-zero elements keep their
relative order. Output is nothing — the input is modified. Is that right?*

**Interviewer.** Yes.

**Candidate.** *A couple of questions. Can the array be empty? And does the order
of the zeroes among themselves matter?*

**Interviewer.** It can be empty. The zeroes are all identical, so no.

**Candidate.** *Then let me try a small example. `{0, 1, 0, 3, 12}` should become
`{1, 3, 12, 0, 0}`.*

*The brute force would be: for each zero, shift everything after it left by one.
That is $O(n)$ per zero, so $O(n^2)$ in the worst case — an array of all zeroes.*

*The waste is that I move the same elements repeatedly. Instead I can use a write
pointer: walk through with a read pointer, and every time I see a non-zero, write
it at the write position and advance it. At the end, everything from the write
position onwards becomes zero. That is one pass to compact and one to pad, so
$O(n)$ time and $O(1)$ space.*

**Interviewer.** Go ahead.

**Candidate.** *(writes the function, saying "the write pointer only advances
when we keep something, so it never overtakes read — that's why this is safe")*

*Let me test it. `{0,1,0,3,12}`: read 0, skip. Read 1, write at 0. Read 0, skip.
Read 3, write at 1. Read 12, write at 2. So w is 3, and positions 3 and 4 become
zero: `{1,3,12,0,0}`. Correct.*

*Edge cases: empty array — the loops never run, which is right. All zeroes —
nothing is written in the first pass, and the second pass fills everything with
zero, which it already was. No zeroes at all — every element is copied onto
itself, which is wasteful but correct.*

*$O(n)$ time, $O(1)$ space. One variation: I could swap instead of copying, which
does it in a single pass — it's the same complexity, with more writes when zeroes
are rare and fewer when they're common.*
:::

:::insight What earned the marks
- **Restated and confirmed** before touching anything.
- **Asked two questions**, both of which genuinely affect the answer.
- **Gave the brute force and its complexity** before optimising.
- **Named the waste** rather than jumping to the answer.
- **Explained the invariant** (`write <= read`) while coding — the detail that
  shows the solution is understood rather than recalled.
- **Tested without being asked**, including the all-zeroes case.
- **Volunteered a variation** and compared it honestly.

That is about four minutes of talking and it is worth more than the code.
:::

## Round 2 — The standard question (25 minutes)

> **Interviewer.** Given a linked list, remove the nth node from the end and
> return the head.

:::note The transcript, with a hint
**Candidate.** *So the list is singly linked, n counts from the end with n=1
meaning the last node, and I return the head — which might change if n equals the
length. Can n be larger than the list?*

**Interviewer.** Assume n is valid.

**Candidate.** *The obvious approach is two passes: count the length L, then walk
to node L−n−1 and unlink the one after it. That is $O(n)$ time and $O(1)$ space,
and it is correct. Shall I write that, or try for one pass?*

**Interviewer.** Try one pass.

**Candidate.** *One pass means I cannot know the length in advance, so I need
something that reaches the end and tells me where I was n nodes ago. Two pointers
with a fixed gap: send one pointer n nodes ahead, then move both until the leader
falls off the end — the trailing one is then n from the end.*

*But I need the node **before** the one I'm deleting, so the gap should be n+1,
not n.*

*And if the node to delete is the head, there is no predecessor. Rather than
special-case that, I'll use a dummy node in front of the head, start both
pointers there, and return `dummy.next` at the end.*

**Interviewer.** Go ahead.

**Candidate.** *(writes it)* *Let me trace `1→2→3→4→5` with n=2. The lead moves 3
steps from the dummy, landing on node 3. Then both move: lead on 4, trail on 1;
lead on 5, trail on 2; lead is null, trail is on 3. So I delete trail->next, which
is node 4. `1→2→3→5`. Correct.*

*Now `1→2→3` with n=3 — deleting the head. Lead moves 4 steps: `dummy→1→2→3→null`.
So the loop does not run, and trail is still the dummy; `trail->next` is the head,
which is exactly what we delete. Returning `dummy.next` gives `2→3`. The dummy
earned its place.*

*$O(n)$ time, $O(1)$ space, one pass. And I free the removed node — if this were
a language with garbage collection I would not, but in C++ it leaks otherwise.*
:::

:::insight What earned the marks
- **Offered the two-pass solution first and asked** whether to proceed. That
  makes the interviewer a collaborator and guarantees something on the board.
- **Derived $n+1$** out loud from "I need the predecessor", rather than stating
  it as a remembered fact.
- **Introduced the dummy node with its reason**, not as a trick.
- **Traced the hard case** — deleting the head — not just the easy one.
- **Mentioned the `delete`**, and explained why it matters in C++ specifically.
:::

## Round 3 — The harder question (35 minutes)

> **Interviewer.** Given an array of heights, compute how much rain water is
> trapped between them.

:::note The transcript, including getting stuck
**Candidate.** *Each element is a bar of width 1, and I want the total water
above the bars. Let me take `{0,1,0,2,1,0,1,3,2,1,2,1}` — I believe the answer is
6, but let me work out part of it. Above index 2, which has height 0: to its left
the tallest is 1, to its right the tallest is 3. The water level is the smaller of
those, so 1, minus the bar's own height 0 — so 1 unit sits there.*

*That generalises. For any position i, the water is
`min(maxLeft, maxRight) - height[i]`, floored at zero.*

**Interviewer.** Good. How fast is that?

**Candidate.** *If I scan left and right for each position, it's $O(n^2)$. But
those scans repeat work — maxLeft at position i is just maxLeft at i−1 combined
with height[i]. So I can precompute both arrays in two passes and then sum in a
third. $O(n)$ time, $O(n)$ space.*

**Interviewer.** Can you do it in $O(1)$ space?

**Candidate.** *(pause)* *Let me think about that out loud. I'd want two pointers
from the ends, carrying running maxima — but the problem is that from the left I
only know the maximum of what I have **seen**, not the true maximum to the right.*

**Interviewer.** Do you always need the true maximum?

**Candidate.** *…No. If my running maxLeft is smaller than my running maxRight,
then the true maximum on the right is **at least** maxRight, which is bigger than
maxLeft — so the minimum of the two is maxLeft regardless of what else is out
there on the right. The shorter side is the one I know exactly.*

*So: move whichever pointer is at the shorter bar, and compute that position's
water using that side's running maximum. $O(n)$ time, $O(1)$ space.*

*(writes it, then traces the first four steps)*

*Edge cases: fewer than three bars traps nothing, since you need a wall on each
side. All equal heights traps nothing. A strictly increasing array traps nothing.*
:::

:::insight What earned the marks
- **Solved one position first.** That single move turns this problem from
  intimidating into routine, and it is the transferable lesson.
- **Did not panic at the $O(1)$ follow-up.** The pause was filled with a
  statement of the difficulty, which is what let the interviewer give a useful
  hint.
- **Took the hint and ran with it.** "Do you always need the true maximum?" is a
  large hint; the candidate supplied the actual argument, which is what is
  assessed.
- **Gave three degenerate cases** that trap nothing, showing the solution was
  reasoned about rather than memorised.

**Needing a hint is not a failure.** How you use it is the measurement.
:::

## Round 4 — The follow-up round (20 minutes)

Many interviews end with variations on what you have already built. These test
whether your solution was understood or recalled.

@tbl: Typical follow-ups, and what each is probing. Prepare for these as seriously as for the main problems.
| Follow-up | What it is testing |
|---|---|
| "Now do it in $O(1)$ space." | whether you know the in-place techniques |
| "What if the input doesn't fit in memory?" | whether you can think about streaming and external data |
| "What if it's called a million times?" | whether you spot that precomputation now pays |
| "What if the array is sorted?" | whether you notice binary search and two pointers become available |
| "What if there are duplicates?" | whether your algorithm's correctness depended on distinctness |
| "What if it must be thread-safe?" | whether you know what shared mutable state costs |
| "How would you test this?" | whether you think about edge cases systematically |
| "What breaks first if n grows 1000×?" | whether you can identify the real bottleneck |

:::interview Answering "how would you test this?"
Give a structure, not a list of examples:

> *"Three groups. **Degenerate inputs**: empty, one element, two elements.
> **Structural cases**: all equal, already sorted, reverse sorted, all
> negative, with duplicates. **Boundary cases**: the target at the first
> position, at the last, and absent; the maximum allowed n; values at
> `INT_MAX` and `INT_MIN` to check for overflow.*
> *Then a randomised test against the brute force — generate random arrays,
> run both, and compare. That catches the cases I did not think of."*

That last sentence is the one that lands. It is how real bugs are found, and
very few candidates mention it.
:::

## The five behaviours that cost offers

:::warning In roughly descending order of damage
**Silence.** Thinking without speaking for three minutes reads as being stuck,
and the interviewer cannot help. Narrate, even when the narration is *"I'm
trying to find a way to avoid re-scanning, which usually means hashing."*

**Coding before clarifying.** A correct solution to a misunderstood problem
scores almost nothing, and a single question would have prevented it.

**Optimising before anything works.** Twenty minutes chasing the elegant answer
and finishing with nothing on the board is the most common way strong candidates
fail.

**Defending a wrong answer.** When an interviewer says *"what about an empty
array?"*, they have found a bug. Check it; do not explain why it is fine.

**Claiming a complexity you have not verified.** Saying $O(n)$ for something
quadratic is worse than saying "I think this is $O(n)$ but let me count the
nested work". The second is honest and shows method.
:::

## How to run a mock on your own

:::checklist A realistic solo session
1. Pick a problem you have not solved, at Level 4 or 5 of Chapter 36.
2. Set a timer for 35 minutes.
3. **Talk out loud the whole time**, and record it. This is the part that feels
   silly and is the part that works.
4. Write the code on paper or in a plain text editor — no compiler, no
   autocomplete, no internet.
5. When the timer stops, stop.
6. Only then, type it in and compile. Count the compile errors; each one is a
   detail you did not have fully in mind.
7. Play back the recording. Note every silence longer than fifteen seconds, and
   whether you stated the complexity without prompting.
8. Write down one thing to do differently next time. Only one.
:::

Three of these a week for a month will change your interviews more than thirty
extra solved problems.

:::recap Chapter 39 in five lines
- Correct code is about a third of the assessment; communication and
  verification are another third and are rarely practised.
- Clarify, give the brute force, name the bottleneck, then optimise — in that
  order.
- Trace the **hard** case, not the easy one, and test before being asked.
- A hint is not a failure; what you do with it is the measurement.
- Record yourself. The silences are what you need to hear.
:::
