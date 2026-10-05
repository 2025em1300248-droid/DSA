# What to Ask Them, and the Final Checklist
@short: Asking and Checklist
@subtitle: The last twenty minutes, and the morning before
@tier: reference
@prereq: none
@blurb: Turning up with no questions reads as no interest, and it is the easiest thing in the whole interview to get right. Then the checklist --- short, practical, and worth re-reading on the morning itself.
@objectives:
- Ask three or four questions that tell you something real
- Know which questions reveal a weak team
- Walk in with your numbers memorised
- Fix the two things that would undermine you before anyone sees them

## Questions to ask them

Ask three or four. Pick ones you actually want the answer to — it shows.

#### Q31.1 — What does the first 90 days look like in this role?
Tests whether they have a plan for you. Vagueness here is a genuine warning
sign: it usually means nobody has thought about what you'll do.

#### Q31.2 — Is this role closer to building models or to deploying and maintaining them?
The single most useful question you can ask. The job title almost never tells
you, and the daily work is completely different.

#### Q31.3 — What's already in production, and what's still at notebook stage?
Tells you whether you'll be building infrastructure from scratch or working
inside something that already exists. Both are fine — but you want to know
which.

#### Q31.4 — How do you measure whether a model is working once it's live?
A strong team has a concrete answer here. A weak one says "we check accuracy,"
which tells you a great deal about how mature they actually are.

#### Q31.5 — Who labels your data, and how is label quality handled?
Nearly every real ML problem turns out to be a data problem. Their answer
reveals whether they've encountered that yet.

#### Q31.6 — What does your path from a trained model to serving traffic look like?
Signals how much of the MLOps work you'd own versus inherit.

#### Q31.7 — How big is the team, and who would I be learning from?
You want to know whether there's anyone senior to review your work. As a
junior this matters more than which framework they use.

#### Q31.8 — How are priorities decided between exploring and shipping?
Reveals whether the team gets room to try things or is purely delivery-driven.

#### Q31.9 — What's the biggest technical challenge the team is facing right now?
Gets you a genuine, unrehearsed answer — and gives you something concrete to
respond to, which turns the end of an interview into a conversation.

#### Q31.10 — How does code review work here?
A team without review is a team where you won't improve. Worth knowing before
you join rather than after.

#### Q31.11 — What would make someone unsuccessful in this role?
More revealing than asking what success looks like. People answer this one
honestly, and you learn what actually goes wrong there.

#### Q31.12 — Is there support for continuing my M.Sc. alongside this role?
Ask it directly. Far better to surface a conflict now than six months in.

#### Q31.13 — What are the next steps, and when should I expect to hear back?
Always close with this. It sets a timeline and gives you a legitimate reason
to follow up.

## Before you walk in

#### Q32.1 — Fix the two stale READMEs.
The churn project lists CI/CD as future work when the workflow actually
exists. The fire detection README describes an older design with email alerts
as future work, when the code is YOLOv5 with threaded email already working.

If an interviewer reads either before talking to you, your resume looks
inflated when it is in fact accurate. **This is the highest-value hour of
preparation available to you.**

#### Q32.2 — Check your CI workflow's trigger branch.
If the file says it runs on `main` and your default branch is `master`, the
pipeline has never run. Verify it before you claim it.

#### Q32.3 — Know your numbers cold.
0.841 and 0.467 for the two detection scores. Five safety-gear classes. 7,043
records, 26.5% churners, 73.5% baseline, 76% accuracy. 800-character chunks
with 150 overlap. 384-dimension embeddings. 300 trees.

These should come out without hesitation. Hesitating on your own numbers
suggests you didn't produce them.

#### Q32.4 — Pre-empt the churn metric.
Raise the 73.5% baseline yourself, before they ask.

It converts your weakest number into evidence of judgement. It is the single
highest-leverage thing in this entire book.

#### Q32.5 — Know which business percentages you can source.
45% compliance, 25% audit efficiency, 25% visibility, 40% verification time.

For each one, decide now: measured by you, reported by the client, or an
estimate. Then say which when asked. If you can't source one, take it off the
resume rather than defend it live.

#### Q32.6 — Test that each repo runs from clean.
Clone into a fresh folder and follow your own README exactly. Interviewers do
try this, and discovering a broken setup while they're watching is avoidable.

#### Q32.7 — Have one story ready for each prompt.
Failure, conflict, deadline, proudest achievement, hardest bug. One rehearsed
story each, drawn from your four projects. Chapter 1 has the candidates.

#### Q32.8 — Prepare three questions for them.
Pick from the list above and adapt at least one to the specific company. A
generic question is better than none; a specific one is much better than both.

#### Q32.9 — Say "I don't know" when you don't.
Then say how you'd find out.

Every experienced interviewer prefers that to a confident fabrication. And
fabrication is the one failure they will not forgive, because it makes
everything else you said unreliable.

#### Q32.10 — Stop talking after the short answer.
Answer in two or three sentences and let them follow up.

Over-explaining is how candidates walk into territory they can't defend. The
silence after a short answer is not awkward — it's them deciding what to ask
next, which means you're in control of the conversation.

:::insight The three things that matter most
If you only do three things from this entire book:

**One.** Fix the two READMEs and check the CI branch. One hour.

**Two.** Rehearse raising the 73.5% churn baseline yourself until it feels
natural. Ten minutes.

**Three.** Record yourself giving the SafeSight and churn overviews, and cut
both to under sixty seconds. Thirty minutes.

That is under two hours, and it addresses the three things most likely to
decide the outcome.
:::

:::recap
- Ask three or four questions, and ask the model-building-versus-deploying
  one.
- "How do you measure whether a model is working live?" tells you how mature
  they are.
- Fix the stale READMEs and check the CI trigger branch. One hour, highest
  value.
- Know your numbers without hesitating.
- Raise the 73.5% baseline yourself.
- "I don't know, here's how I'd find out" beats invention every time.
- Answer in two or three sentences, then stop.
:::
