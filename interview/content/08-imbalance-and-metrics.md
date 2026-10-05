# Imbalanced Data and Metrics
@short: Imbalance and Metrics
@subtitle: The most reliably asked block in the whole interview
@tier: foundation
@prereq: Chapter 7
@blurb: Your resume lists imbalanced data handling and your churn set is 26.5% minority, so this is coming. Know precision and recall cold --- which way round they go, and which one matters for each of your projects. These are the questions where a confident wrong answer does real damage.
@objectives:
- Explain why accuracy misleads, using your own numbers
- Say precision and recall correctly, every time
- Choose the right metric for each of your four projects
- Describe SMOTE and the mistake everybody makes with it

## Imbalanced data

#### Q10.1 — What is class imbalance, and why is it a problem?
When one outcome is much rarer than the other. The problem is that a model can
score brilliantly by simply never predicting the rare one — and the rare one
is almost always the thing you care about.

#### Q10.2 — Your churn data is 26.5% minority. Is that even imbalanced?
Mildly. Roughly one in four, which is a long way from fraud detection at one
in a thousand. So heavy resampling probably isn't needed.

The real problem isn't the imbalance — it's that accuracy was the wrong metric
at **any** level of imbalance. Saying that shows judgement rather than
reaching for SMOTE by reflex.

#### Q10.3 — Which metrics do you use instead of accuracy?
Precision, recall and F1 on the class you care about, plus the ranking curves.
When the rare class is genuinely rare, the precision-recall curve is more
informative than the ROC curve.

#### Q10.4 — What is oversampling? What is undersampling?
Oversampling: make more copies of the rare class so the model sees it more.
Risk — it can memorise those copies.

Undersampling: throw away some of the common class. Risk — you're deleting
real data.

#### Q10.5 — What is SMOTE?
Instead of duplicating rare examples, it invents new ones in between existing
rare examples. So you get variety rather than copies.

#### Q10.6 — What's the biggest mistake people make with SMOTE?
Running it **before** splitting into train and test. Then synthetic points
based on your test examples end up in training, your score looks wonderful,
and it's meaningless.

Resample inside the training fold only. Always.

#### Q10.7 — What is `class_weight='balanced'`?
It tells the model that mistakes on the rare class cost more, so it stops
ignoring them. One line of code, no new data invented.

Try this before SMOTE. It's simpler and it usually works.

#### Q10.8 — How does threshold tuning help?
The 0.5 cutoff is arbitrary — nothing special happens there. Moving it lets
you catch more of the rare class at the cost of more false alarms, or the
other way round.

You pick the point based on what each kind of mistake actually costs.

#### Q10.9 — For churn, which error is worse?
Missing a churner. That loses you the whole customer. A false alarm costs you
one unnecessary discount offer.

So you tune for catching them, and you say so.

#### Q10.10 — How does imbalance show up in object detection?
Two ways. Between your classes — far fewer goggles than helmets in the
footage. And within every single image, where the vast majority of the picture
is background and only a small part is an object.

#### Q10.11 — What is focal loss?
A tweak that makes the model pay less attention to examples it's already
getting easily right, so training focuses on the hard ones. Built specifically
for the background-versus-object imbalance in detection.

#### Q10.12 — What is a confusion matrix, and how do you read one?
A small table showing four numbers: correctly caught, correctly ignored,
false alarms, and misses.

Read it before any single summary number, because it tells you **which**
mistake the model is making. Two models with identical accuracy can be making
completely different errors.

## The metrics

#### Q11.1 — Define precision and recall.
**Precision**: of everything I flagged, how much was actually right?
**Recall**: of everything that was actually there, how much did I catch?

#### Q11.2 — How do you remember which is which?
Precision's bottom number is **your predictions**. Recall's bottom number is
**reality**.

Or: precision is "when I shout, am I right?" Recall is "do I shout every time
I should?"

#### Q11.3 — What is F1 score? Why the harmonic mean?
A single number combining precision and recall. It uses the harmonic mean
rather than a plain average because that punishes being lopsided — you can't
score well by maxing one and ignoring the other.

#### Q11.4 — When do you optimise precision over recall?
When false alarms are expensive. A spam filter that bins real emails is worse
than one that lets a few spams through.

Optimise recall when **missing** things is expensive — disease screening, fire
detection, churn.

#### Q11.5 — For your fire detector, which matters more?
Recall, clearly. A missed fire is catastrophic; a false alarm costs one wasted
email. So you'd deliberately run a low confidence threshold and accept
reviewing some false positives.

#### Q11.6 — What is accuracy, and when is it misleading?
How often you were right overall. It misleads whenever one outcome is much
more common than the other — your 76% against a 73.5% baseline is the textbook
example.

#### Q11.7 — What is specificity?
Of everything that genuinely wasn't there, how much did you correctly leave
alone. It's recall, measured on the negative class.

#### Q11.8 — What is an ROC curve? What is AUC?
As you move the cutoff from strict to lenient, you catch more real cases but
also raise more false alarms. The ROC curve plots that trade-off.

AUC is the area underneath it, which works out to: if you picked one real case
and one non-case at random, how often does the model score the real one
higher? 0.5 is coin-flipping; 1.0 is perfect.

#### Q11.9 — ROC-AUC vs PR-AUC?
When the thing you're looking for is rare, ROC-AUC flatters the model, because
false alarms are being divided by an enormous number of negatives and so look
tiny.

PR-AUC only looks at the rare class, so it tells the truth. Use it when
positives are rare.

#### Q11.10 — What is log loss?
It scores not just whether you were right but how confident you were. Being
confidently wrong is punished heavily. Use it when the actual probability
matters, not just the yes/no.

#### Q11.11 — What regression metrics do you know?
Mean absolute error, mean squared error, root mean squared error, R-squared,
and mean absolute percentage error.

#### Q11.12 — MAE vs RMSE — when do you pick which?
RMSE squares the errors first, so one enormous mistake hurts far more than
several small ones. Use it when big misses are disproportionately bad.

MAE is in the natural units of your data and isn't thrown off by a single
outlier.

#### Q11.13 — What is R-squared? Can it be negative?
The fraction of the variation your model explains. Yes, it can be negative —
that means your model is doing worse than simply always predicting the
average.

#### Q11.14 — What is adjusted R-squared?
R-squared with a penalty for the number of columns you used, so adding useless
features doesn't inflate it.

#### Q11.15 — What is IoU?
How much a predicted box and the true box overlap, divided by the total area
they cover between them. 1.0 is perfect overlap, 0 is none. It's how you
decide whether a detection counts as correct.

#### Q11.16 — What is mAP, and what does mAP50-95 mean?
mAP is the overall detection score: for each class you measure how well it
finds objects across all confidence levels, then average across classes.

mAP50 counts a box as correct if it overlaps by at least half. mAP50-95 repeats
that at steadily stricter overlap requirements and averages — so it also grades
how tightly your boxes fit.

#### Q11.17 — What is a precision-recall curve, and how do you use it?
It shows what precision you'd get at each level of recall as you move the
cutoff. You use it to **pick the operating point**, not just to produce a
number. That's the part people forget.

#### Q11.18 — What is model calibration?
Whether a predicted 0.8 really means that eight out of ten such cases turn out
positive. Check it by bucketing predictions and comparing to what actually
happened.

Random forests are often badly calibrated — they're reluctant to say 0.95 or
0.05 because they're averaging votes.

#### Q11.19 — What is a baseline, and why must you always report one?
The simplest possible predictor — always guess the most common answer. Without
it, a metric is meaningless.

That's exactly the lesson of your 76% against 73.5%. A number with no baseline
isn't a result.

#### Q11.20 — What are BLEU, ROUGE and perplexity used for?
BLEU for translation, ROUGE for summarisation — both compare generated text
against a reference. Perplexity measures how surprised a language model is by
text; lower is better.

#### Q11.21 — How do you evaluate a RAG system?
Split it in two and measure separately.

**Did it find the right passage?** Measure how often the correct passage
appears in the top results.

**Did it answer well from that passage?** Measure whether the answer is
actually supported by the retrieved text, and whether it made anything up.

Measuring only the final answer means you can't tell which half broke.

:::practice The two to drill
Precision and recall. Say them out loud until "of what I flagged" and "of what
was there" come instantly. Then do the mapping for all four of your projects:
fire is recall, churn is recall, document QA is precision of the retrieval,
PPE is both with per-class numbers.
:::

:::recap
- Accuracy misleads whenever one class dominates — always quote the baseline.
- Precision is "when I flag it, am I right"; recall is "do I catch everything".
- Fire and churn both need recall. Say so and say why.
- Resample inside the training fold only, or your score is fiction.
- Try `class_weight='balanced'` before SMOTE.
- Read the confusion matrix before any single number.
- The precision-recall curve is for choosing your cutoff, not just reporting.
:::
