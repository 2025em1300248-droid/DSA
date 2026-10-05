# Your Four Projects
@short: Your Projects
@subtitle: Every claim here has to survive a follow-up
@tier: core
@prereq: Chapter 2
@blurb: This is where they will spend the longest, and it is where an inflated claim collapses fastest --- because the next question is always an implementation detail of whatever you just said. Read this chapter and Chapter 2 together; between them they cover everything that can go wrong.
@objectives:
- Give a 60-second overview of each project that invites the right follow-up
- Name your own contribution precisely, without absorbing the team's work
- Volunteer each project's weakness before they find it
- Say what you would build next, concretely

## SafeSight

#### Q26.1 — Give me a 60-second overview of SafeSight.
"It's a workplace safety platform for industrial sites. A YOLOv8 model watches
the CCTV feeds and spots workers plus five types of safety equipment, scoring
0.841 on the standard detection metric. Every violation gets logged with a
timestamp and an evidence photo, so there's an audit trail. Then a second part
looks up which safety regulation was actually broken and shows the supervisor
the specific clause, not just an alert. There's a dashboard on top showing it
live."

#### Q26.2 — What problem does it solve that a human can't?
Coverage. A safety officer can watch one area for part of a shift. The system
watches every camera continuously and produces the evidence trail that an
audit actually requires.

It's not that it's smarter than a person — it's that it never looks away and
it writes everything down.

#### Q26.3 — What was your specific contribution?
Answer precisely. Name the parts you built, name what you integrated, and name
what already existed before you joined.

Do not absorb the team's work. The next question is always a detail of
whatever you claimed, and if you claimed something you didn't build, that's
where it falls apart.

#### Q26.4 — Where did the training data come from, and how was it annotated?
Know the answer: public datasets, client footage, or both. Who annotated it.
Roughly how many images. How the classes were defined.

If it was a public dataset, say so. Using public data is completely fine.
Being vague about where your data came from is not.

#### Q26.5 — What was the hardest technical problem?
Working out **which worker** a piece of safety equipment belongs to when
several people overlap in frame — and keeping that association stable as they
move.

Explain how you did it (checking whether the item's box sits inside the
person's box) and be honest about where it still fails (two people standing
close together).

#### Q26.6 — How do you avoid logging the same violation hundreds of times?
Tracking plus a cooldown. One tracked worker without a helmet becomes **one**
event with a duration, not one event per frame.

Without this the audit log is unusable — thirty seconds of footage would
generate hundreds of entries for the same person standing still.

#### Q26.7 — How does the assistant know which rule applies?
The violation type becomes a search query. Chunks of the safety manual come
back ranked by relevance. The graph then checks whether a retrieved rule
actually governs this situation, and searches differently if none of them do.
Then it answers with the clause cited.

#### Q26.8 — What if it retrieves the wrong regulation?
Then a supervisor sees a citation that doesn't fit the situation.

That's exactly why it **cites rather than decides** — the human verifies
before anything is enforced. Being clear that the model assists and doesn't
have authority is the right answer for a safety system, and saying it
unprompted is a strong signal.

#### Q26.9 — How many cameras could it handle, and what was the bottleneck?
Know your real number and which resource ran out first — GPU throughput, video
decoding, or network bandwidth.

Then mention frame skipping: safety compliance doesn't need thirty frames a
second. Running at three to five multiplies how many cameras one machine
handles.

#### Q26.10 — What was the latency from violation to alert?
Have a figure and say what it includes — the detection, the tracking, the rule
lookup, and the delivery. An unqualified number invites exactly one follow-up.

#### Q26.11 — How did you validate it with actual users?
Describe the supervisor feedback and what changed because of it.

If the honest answer is that it was a pilot with limited feedback, say that.
"We had limited user feedback in the pilot window" is fine. Inventing user
research is not.

#### Q26.12 — What are its privacy implications?
It's continuous video surveillance of identifiable people at work. That's
significant and you should raise it yourself.

Mitigations: keep only the violation frames rather than all footage, restrict
who can see them, set a retention limit, and tell workers the system exists.

Raising this before they do is one of the strongest maturity signals available
to you.

#### Q26.13 — What would you build next?
Better detection on goggles and gloves specifically. Low-light robustness.
Per-camera monitoring so you know when one degrades. And an evaluation set for
the **rule-matching half**, which currently has no measurement at all.

#### Q26.14 — Why is there no accuracy number for the RAG half?
Because you didn't build an evaluation set for it. Own that directly.

Then describe the one you'd build: fifty violation-to-clause pairs, measuring
how often the right clause comes back and whether the answer is actually
supported by it. That's a day's work and you know exactly what it looks like.

#### Q26.15 — If I asked you to halve the cost of this system, what would you do?
Lower the frame rate. Drop to a smaller model and measure what accuracy you
lose. Only run detection when motion is detected. Reduce the number precision.
Batch across cameras. Use a smaller local language model.

Then say which of those costs accuracy and which is free. Frame rate and
motion gating are nearly free; a smaller model is not.

## DocuMind

#### Q27.1 — Describe DocuMind in 30 seconds.
"A document question-answering tool. You upload PDFs, it splits them up and
indexes them, then you ask questions in plain English. Llama 3 runs locally
through Ollama and answers in under two and a half seconds, showing you which
passages it used."

#### Q27.2 — Why build it locally instead of using a hosted model?
Privacy and cost. The documents never leave the machine, and there's no
per-question bill.

For confidential material that's the right trade, and privacy is the argument
to lead with.

#### Q27.3 — What's the ingestion pipeline exactly?
Load the PDF, pull the text out, split it into 800-character chunks with 150
characters of overlap, turn each chunk into numbers, add them to the FAISS
index, and save the index along with the chunk text and page references.

#### Q27.4 — What is the 2.5 seconds measuring?
Be precise. Is it the whole thing or just the search? Warm or cold? What size
document? What hardware?

Say "end to end on my machine with the index already loaded." Qualifying it is
more credible than the bare number, and an unqualified latency figure invites
exactly one follow-up.

#### Q27.5 — What dominates that latency?
Generating the answer, not finding the passages. Searching a few thousand
vectors takes milliseconds; the model writing out the answer is nearly all of
it.

Knowing where the time goes is the actual point of the question.

#### Q27.6 — How do you ensure answers are traceable?
Every chunk carries its source file and page. Those go into the prompt. The
model is told to reference them. And the interface shows the retrieved
passages so the user can check for themselves.

#### Q27.7 — What happens if the answer isn't in the document?
The prompt tells it to say so rather than guess.

Test this explicitly — it's the single most important behaviour in a document
QA tool and the easiest one to get wrong. A tool that invents a plausible
answer for a question the document doesn't address is worse than useless.

#### Q27.8 — How would you handle a 500-page PDF?
In principle it already works, because you only retrieve a few passages
regardless of document size.

What changes: ingestion takes longer, the index gets bigger, and chunking by
section starts to beat chunking by character count. Mention batching the
embedding step so it doesn't take forever.

#### Q27.9 — What about tables, scanned pages and images?
Scanned pages need OCR first — there's no text to extract. Tables come out
scrambled without a layout-aware parser, because the columns get interleaved.

Be honest that this is a current limitation. Claiming it handles everything is
one PDF away from being disproved.

#### Q27.10 — How would you support multiple documents and ask across them?
Store a document identifier with each chunk, let the user search within one
document or across all of them, and cite which document each passage came
from.

Also worth saying: this is where you'd outgrow FAISS, because it can't filter
by metadata natively.

#### Q27.11 — How do you know the answers are good?
Honest answer: there's no formal evaluation yet.

Then describe one — thirty to fifty real questions with the expected source
passage, measuring how often retrieval finds it and whether the answer is
actually supported. Having the plan ready is most of the credit.

#### Q27.12 — What would you add next?
A reranker first — best quality improvement per hour of work. Then hybrid
keyword search, conversational follow-ups, streaming output, and an evaluation
harness.

Picking the reranker and saying why shows you can prioritise.

## Fire detection

#### Q28.1 — Describe the fire detection project.
"A YOLOv5 single-class fire detector built with PyTorch and OpenCV. It runs on
a webcam, a video file or still images. When it detects fire it emails an
annotated frame as evidence — and the emailing happens on a separate thread so
the video never stalls."

#### Q28.2 — Why single-class rather than fire plus smoke?
Because that's what the data supported — the config is one class, "fire".

Adding smoke needs smoke annotations. And smoke is usually the **earlier**
signal, so that's the honest next step rather than a limitation you're hiding.

#### Q28.3 — Why YOLOv5 here but YOLOv8 at Infosys?
A real answer is fine: v5 is what the project started on and had more examples
available at the time.

Then note the actual architectural difference — v5 uses preset box shapes, v8
doesn't — so it's clear you know it isn't just a version number.

#### Q28.4 — What's your accuracy?
Don't invent one. "I tested it on held-out data but I don't have a number I'd
stand behind on a resume, so I left it off."

Then say what you **would** report: the detection score, and more importantly
recall at your chosen threshold — because for fire, recall is the number that
matters.

#### Q28.5 — What confidence threshold, and why?
Low. Recall dominates everything here. A missed fire is catastrophic; a false
alarm costs one email.

Say plainly that you'd rather review false positives than miss an event.

#### Q28.6 — How do you suppress false alarms then?
Require the detection to appear across several consecutive frames before
alerting.

It's cheap, and it removes most single-frame flickers without raising the
threshold — so you keep your recall.

#### Q28.7 — What triggers a false positive in practice?
Sunsets. Orange high-visibility clothing. Welding sparks. Headlights. Screens
and monitors.

Fix by adding those as **negative examples** in training. This question is
specifically checking whether you actually watched your model's output or just
read the metric.

#### Q28.8 — Explain the threading. What breaks without it?
Sending an email takes a couple of seconds. If that happens inside the loop
that reads video frames, nothing reads frames during it — so the buffer fills
and you drop frames or process stale ones.

A worker thread handles the email while OpenCV keeps reading. This is your
best concrete engineering story in the whole project set: specific problem,
you diagnosed it, clean fix.

#### Q28.9 — What if 100 detections fire at once?
Without a limit you'd spawn a hundred threads and spam the inbox.

The fix is a queue with one sender and a cooldown per event. Say whether you
implemented it — identifying the flaw is worth more than pretending it isn't
there.

#### Q28.10 — How are the SMTP credentials handled?
Environment variables, or a `.env` file excluded from Git. Never committed.

Check that's actually true of your repository before anyone clones it.

#### Q28.11 — How would you productionise this?
Multiple camera feeds. Confirmation across frames. Tiered alerts with
acknowledgement and escalation if nobody responds. Edge hardware so it runs
near the cameras.

And integration **alongside** certified smoke and heat sensors — never instead
of them.

#### Q28.12 — Would you trust this as a building's fire alarm?
No, and say so plainly.

It's a supplementary early-warning layer. Life safety requires certified
sensors with certification behind them. Claiming otherwise is the wrong answer
in every room you'll ever be in.

## Churn pipeline

#### Q29.1 — Describe the churn project.
"A production-shaped ML pipeline. A Random Forest on a 7,043-record telecom
dataset, tracked in MLflow with automatic promotion of the best run, served
through FastAPI, containerised with the UI via Docker Compose, built in GitHub
Actions and deployed on Railway. The point of it was the pipeline, not the
model."

That last sentence is important. It sets the frame before they find the
accuracy number.

#### Q29.2 — What's the dataset?
The IBM telecom churn dataset from Kaggle — 7,043 rows, 1,869 churners, 5,174
who stayed.

Name it. Pretending a well-known public dataset is proprietary collapses
immediately.

#### Q29.3 — What features matter most?
Tenure, contract type (month-to-month dominates), monthly charges and payment
method.

Know your top features. Being unable to name them suggests you never looked at
the model you trained.

#### Q29.4 — Why Random Forest?
A strong default on tabular data: no scaling needed, handles mixed data types,
and gives you feature importance for free.

Then volunteer that gradient boosting would probably beat it, and that's what
you'd try next. Offering the better alternative unprompted is a good signal.

#### Q29.5 — What accuracy, and what's wrong with that number?
76%. And get in front of it: always guessing "no churn" gets 73.5%, so
accuracy was the wrong thing to measure. What matters is how many churners you
caught.

Say it before they do. This single move is the highest-leverage thing in your
whole interview.

#### Q29.6 — So is the model useless?
Not necessarily. It might rank customers usefully even if the thresholded
accuracy is unimpressive — and ranking is what a retention team actually
needs.

The honest answer is you can't tell, because you didn't log the ranking
metrics. That's a process failure, not a mystery, and saying it that way is
much better than defending the model.

#### Q29.7 — How would you fix it, concretely?
Log F1, ROC-AUC and PR-AUC. Set `class_weight='balanced'`. Tune the threshold
against what a missed churner costs versus a retention offer. Try gradient
boosting. Use stratified cross-validation instead of one split.

That's a couple of hours of work, and knowing it's a couple of hours is part
of the answer.

#### Q29.8 — How does the MLflow promotion work, and what's its flaw?
It compares runs on the logged score and promotes the winner.

The flaw: the logged score is accuracy, so it can promote a model that's worse
at the actual job. Naming your own design flaw is more impressive than hoping
it goes unnoticed.

#### Q29.9 — Walk me through what happens when I POST to `/predict`.
Pydantic validates the incoming JSON. The preprocessing pipeline transforms
it. The loaded model predicts. A probability and a label come back as JSON.

Be clear that the scaler and encoders are saved **inside** the pipeline file,
so training and serving transform the data identically. That's your defence
against train-serve skew.

#### Q29.10 — What does Docker Compose run here?
The FastAPI service and the Streamlit UI together, networked by service name,
so `docker compose up` gives a reviewer the whole thing in one command.

#### Q29.11 — What does the CI pipeline actually check?
Import checks and the Docker image build. That's it.

Don't inflate it. And check it triggers on your real default branch, or it has
never actually run.

#### Q29.12 — Your README says CI/CD is future work. Which is right?
The resume. The workflow file exists; the README is out of date. Fix it before
you send the resume anywhere.

#### Q29.13 — Why Railway rather than AWS?
Zero cost and zero operations for a portfolio service.

Then show you know the trade: no autoscaling story, cold starts on first
request, and with real traffic you'd move to a managed container service.

#### Q29.14 — What would you do differently if you rebuilt it?
Decide the metric **before** training. Log recall and PR-AUC. Use time-based
splits. Add real tests and a minimum-score gate in CI. Monitor for drift.

In other words: decide what "good" means first. That's the lesson, and it's
the right note to end on.

:::practice The rehearsal that matters
Record yourself giving the SafeSight overview (Q26.1) and the churn overview
(Q29.1). Both must be under sixty seconds and both must end somewhere you want
them to dig. Then rehearse Q29.5 until raising the 73.5% baseline yourself
feels completely natural.
:::

:::recap
- Lead the churn description with "the point of it was the pipeline, not the
  model."
- Raise the 73.5% baseline before they find it.
- Name your own contribution to SafeSight precisely — the follow-up is always
  a detail.
- Raise the surveillance privacy question yourself; it's a strong maturity
  signal.
- Say plainly that the fire detector is not a fire alarm.
- "I didn't build an evaluation set, and here's the one I'd build" is a good
  answer.
- Every project has one weakness. Volunteer it, with the fix attached.
:::
