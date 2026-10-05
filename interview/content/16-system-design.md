# ML System Design
@short: System Design
@subtitle: Where structure matters more than detail
@tier: advanced
@prereq: Chapter 14
@blurb: These get asked at the senior end of a junior interview, and they are not really testing whether you know the answer. They are testing whether you have a structure --- whether you ask about the goal before designing anything. Say the structure out loud before you start.
@objectives:
- Open any design question with the same structure, out loud
- Design the three systems you have actually built
- Say where humans belong in the loop
- Raise fairness and privacy before they do

#### Q25.1 — How do you approach any ML system design question?
Say the structure first, then follow it:

What's the goal and what are the constraints. What exactly is being predicted,
and what's the label. Where does the data come from. What features. What's the
simplest baseline. Then the model. Then how you'd measure it offline. Then how
it gets served. Then how you'd monitor it. Then what happens when it fails.

Saying that out loud at the start is worth more than any individual answer,
because it shows you won't just start coding.

#### Q25.2 — Design a PPE compliance system from scratch.
You've built this, so use the real one.

Cameras feeding frames. Sample a few frames per second rather than all of
them. Detect people and safety items. Track people so identities stay stable.
Map each violation to the governing rule by retrieval. Store the event with an
evidence image. Dashboard and alerts on top. A human review loop at the end.

Mention frame skipping and per-camera monitoring — those are the details that
make it sound deployed rather than imagined.

#### Q25.3 — Design a churn prediction system.
Start by pinning down what churn actually **means** — no activity for thirty
days, or an explicit cancellation? And how far ahead are you predicting?

Then: features from usage, billing and support tickets. Train with a
time-based split. Optimise for catching churners at a threshold justified by
what a retention offer costs. Score weekly in batch. Feed the list to the
retention team. And measure whether the **campaign** worked, not just whether
the model scored well.

That last point is what separates a model from a system.

#### Q25.4 — Why is a time-based split essential for churn?
Because a random split lets the model learn from the future. It sees March
data while predicting February, which it will never be able to do live.

Train on earlier periods, test on later ones — the way it'll actually be used.

#### Q25.5 — Design a document QA system for 10 million documents.
An ingestion queue so uploads don't block. Layout-aware parsing. Chunking.
Embedding in batches. A managed vector store, split across machines, with
metadata and **access control**. Hybrid retrieval plus a reranker. The model
with citations. A cache. And an evaluation set with a way to capture user
feedback.

What actually changes at that scale is permissions, ingestion throughput and
cost — not the core idea. Say that.

#### Q25.6 — Design a real-time fire detection system for a building.
Multiple camera feeds. A deliberately low confidence threshold, because
missing a fire is far worse than a false alarm. **Confirmation across several
consecutive frames** before alerting, which kills most flickers. Tiered alerts
with evidence attached. Escalation if nobody acknowledges.

And then the important clause: it supplements physical smoke and heat sensors,
it never replaces them. Saying that unprompted is what shows judgement.

#### Q25.7 — How do you reduce false alarms without hurting recall?
Require the detection to persist over several frames. Ignore regions you know
are noisy — a window with sunset through it. Combine with another signal, like
an actual smoke sensor. And tier the alerts by confidence rather than using
one hard cutoff.

The point is you're not raising the threshold — that would cost you recall.
You're adding other evidence.

#### Q25.8 — Batch vs real-time inference — how do you decide?
By how fast the decision actually has to be made.

Churn scoring is fine weekly in batch. PPE and fire detection have to be
streaming. Batch is far cheaper and much simpler, so default to it unless
latency genuinely demands otherwise.

#### Q25.9 — How do you estimate the cost of an ML system?
Training compute, inference compute multiplied by how many requests you
expect, storage for data and models, and token costs if you're calling a
hosted model.

For your local Llama 3 setup, the point is that the per-request cost is zero
but the hardware cost is fixed and up front. That's a genuinely different
shape of bill.

#### Q25.10 — Where do humans belong in the loop?
Wherever an automated mistake is expensive. Enforcing a safety penalty.
Deleting something. Sending a retention offer that costs money.

Design the review queue as **part of the system**, not as an apology for the
model not being good enough.

#### Q25.11 — How do you handle a model that is accurate but unfair?
Measure per group, not in aggregate. An overall number can look fine while one
group is being badly served.

For PPE detection that means checking detection rates across skin tone,
clothing and lighting conditions — and treating a gap as a **bug with a data
fix**, not as an unfortunate property of the model.

#### Q25.12 — What does it mean for a model to be explainable?
Being able to say why it made a particular decision.

Methods: overall feature importance for the whole model; SHAP or LIME for one
specific prediction; and for image models, heatmaps showing which part of the
picture drove the answer.

#### Q25.13 — How would you explain your churn model's prediction to a business user?
Not as a probability. As reasons: "short tenure, month-to-month contract,
three support tickets last month."

A retention team can act on that. They cannot act on 0.73.

:::practice The opener
Rehearse Q25.1 until you can say the structure in fifteen seconds. In a design
question, starting with "let me check what we're optimising for and what the
constraints are" immediately changes how the interviewer sees you.
:::

:::recap
- Say the structure before you design anything: goal, label, data, baseline,
  model, metric, serving, monitoring, failure.
- Define what churn actually means before building a churn model.
- Fire detection supplements certified sensors; it never replaces them.
- Reduce false alarms with confirmation over time, not by raising the
  threshold.
- Measure fairness per group, and treat a gap as a bug with a data fix.
- Explain predictions as reasons, not probabilities.
:::
