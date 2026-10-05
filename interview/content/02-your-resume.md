# Defending Your Resume
@short: Your Resume
@subtitle: The questions that attack your own numbers
@tier: foundation
@prereq: none
@blurb: These go straight at the specific figures you wrote down. A good interviewer will find every one of them, and most candidates have never rehearsed a single one. Read this chapter before anything else in the book --- it is the one that decides interviews.
@objectives:
- Raise your weakest number yourself, before they do
- Know exactly where every percentage on your resume came from
- Explain what your detection scores actually mean
- Say "I don't have a number for that" without it hurting you

## The churn accuracy question

#### Q2.1 — Your churn model gets 76% accuracy. What's the base rate?
This is the dangerous one. In that dataset, 5,174 out of 7,043 customers did
not churn. So a model that just says "nobody will ever churn" is right 73.5%
of the time, without doing anything at all. Yours gets 76%. It beats doing
nothing by about two and a half points.

**Say it before they do.** "76% sounds alright until you know that always
guessing 'no' gets you 73.5%. Accuracy was the wrong thing to measure. What
actually matters is how many of the real churners I caught."

Getting in front of this turns your weakest number into your best moment in
the interview. If they find it first, you're defending. If you raise it, you
look like someone who checks their own work.

#### Q2.2 — Then why is accuracy on your resume?
"Because that's the number the run actually recorded, and I wasn't going to
put something on my resume that I couldn't show you in MLflow."

That answer is worth more than a better number would have been. It says you
don't invent things.

#### Q2.3 — What should you have measured instead?
How many churners you caught (recall), how many of your churn predictions
were right (precision), and the two combined (F1). Plus the ranking quality
curves, ROC-AUC and PR-AUC.

For churn, catching them matters most. Missing a churner loses you the whole
customer. A false alarm costs you one discount offer. So you'd pick the cutoff
based on that cost difference, not leave it at the default 0.5.

## The business percentages

#### Q2.4 — Your resume says safety compliance rose 45%. How was that measured?
Know exactly where that number came from — whose baseline, over what period,
counted how. If it came from the client's own audit reports, say so plainly:
"That's the facility's figure from their audit reports, not something I
measured myself."

Attributing it honestly is completely fine. Implying you calculated it is not.

#### Q2.5 — And the 25% audit-efficiency and 40% verification-time figures?
Same rule. Before the interview, go through all four percentages and label
each one: measured by me, reported by the client, or an estimate. Then say
which when asked.

If you can't source one, take it off the resume. One number you can defend is
worth more than four you can't.

## The detection scores

#### Q2.6 — 0.841 mAP50 — what does that actually mean?
In plain terms: it's a score out of 1 for how well the model finds things,
averaged across your six classes.

For each class, you check every box the model drew. A box counts as correct
if it overlaps the real object by at least half. You score the class on how
many it found and how many it got wrong, then average across all six classes.

0.841 is a solid score for an industrial safety-gear dataset.

#### Q2.7 — Why is your mAP50-95 only 0.467 when mAP50 is 0.841?
Because the second number is much stricter about box placement. The first
only asks "did you overlap the object by half?" The second asks the same
question at steadily tighter overlaps, all the way up to near-perfect.

So: your model finds the right objects, but the boxes it draws are a bit
loose. That's expected with small items like goggles and gloves, and with
hand-drawn labels that aren't pixel-perfect either.

#### Q2.8 — Which safety-gear class performed worst, and why?
Have the per-class numbers in your head. It's usually goggles and gloves:
they're the smallest things in the frame, they get hidden behind hands and
heads most often, and there were fewer examples of them.

The fix: more pictures of them, a higher input resolution, or cutting the
image into tiles so small objects appear bigger.

#### Q2.9 — Why YOLOv8m and not the small or large version?
Because of what you measured on your hardware. "The small one missed the
little items. The large one couldn't keep up across all the cameras on our
GPU. Medium was the point where getting more accurate stopped being worth the
extra time per frame."

Any answer that's a measured trade-off is a good answer.

#### Q2.10 — Why LangGraph for the rule assistant instead of plain LangChain?
Because the assistant isn't one step — it loops. It works out what kind of
violation happened, looks up candidate rules, checks whether those rules
actually apply, and goes back to look again if they don't.

A plain chain runs straight through once and can't go back. LangGraph lets you
build in the branch and the loop.

## The honest gaps

#### Q2.11 — Your fire detector has no accuracy number. Why not?
"I tested it on data it hadn't seen, but I don't have a number I'd be willing
to defend on a resume, so I left it off."

Leaving something out on purpose reads as discipline. Never invent one under
pressure — that's the one mistake they won't forgive.

#### Q2.12 — DocuMind answers in under 2.5 seconds. 2.5 seconds of what?
Know what that number includes. Is it the whole thing from question to answer,
or just the search part? Was the model running locally or hosted? Was it a
fresh start or already warmed up? How big was the document?

Say "that's end to end on my machine, with the index already loaded."
Qualifying it is more credible than the bare number.

#### Q2.13 — Why 800-character chunks with 150 overlap?
Big enough to hold one complete idea, small enough that the search stays
precise and you're not paying for text you don't need. The overlap means a
sentence that falls across a boundary still appears whole in one of the two
pieces.

Be honest if you picked it by feel rather than testing. Then say what test
you'd run: try 400, 800 and 1600 and measure which one retrieves the right
passage most often.

## The uncomfortable ones

#### Q2.14 — Your Infosys dates are three months. How much of SafeSight was yours?
Answer precisely. Name the parts you built, name what other people built, and
name what already existed before you arrived.

Claiming a whole team's system is the fastest way to fail this round, because
the very next question is always a detail of whatever you just claimed.

#### Q2.15 — Your README says CI/CD is future work but your resume claims a pipeline. Which is true?
The resume. The workflow file exists and it builds the image and runs the
import checks — the README is just out of date.

Then fix the README before you send the resume anywhere. And check the
workflow actually triggers on the branch you use, or it has never run once.

#### Q2.16 — You list C++ but every project is Python. Where did you use C++?
Give the real scope and don't inflate it. "Coursework and algorithm practice.
I'm comfortable reading it and writing algorithmic code in it. I haven't
shipped a C++ system in production."

That's a perfectly good answer. Pretending otherwise is not.

#### Q2.17 — You list MCP and A2A agents. Show me where.
If no project uses them, say: "That's from my coursework and reading, not
something I've shipped." Then be able to explain both properly.

A skill you can explain but haven't shipped is fine. One you can't explain is
a lie sitting on a page.

#### Q2.18 — Which of your projects are you least proud of?
Pick one and explain why technically. The churn project is the honest choice:
"The pipeline around it is the part I'd defend. The model itself needs a
cutoff tuned to what a missed churner actually costs the business."

#### Q2.19 — Walk me through the hardest bug you hit.
The fire detector's email alerts. Sending an email takes a couple of seconds,
and it was happening inside the loop that reads video frames — so the video
stalled every time it sent one. You moved the email onto a separate thread so
the video keeps running.

That's a good story: specific, you diagnosed it, you fixed it.

#### Q2.20 — If I clone your repo right now, will it run?
Know the answer before they ask. For each project: does it start from a clean
machine with one command, are the model weights and settings documented, does
the README describe what the code actually does?

If something's broken, say so first. They may well try it while you're
talking.

:::practice The hour that matters most
Go through your resume line by line and write one sentence next to every
number explaining where it came from. Any number where you can't write that
sentence should come off the resume. Then rehearse Q2.1 out loud until
raising the 73.5% baseline yourself feels natural.
:::

:::recap
- Raise the 73.5% churn baseline yourself. It is the single highest-value
  thing you can do in the whole interview.
- Label every business percentage as measured, client-reported, or estimated
  — and say which.
- mAP50 means "did it find the object"; mAP50-95 also grades how tightly the
  box fits.
- "I left it off because I couldn't defend the number" is a strong answer.
- Never claim more of a team project than you built — the follow-up is always
  an implementation detail.
- Fix the stale READMEs before you send the resume anywhere.
:::
