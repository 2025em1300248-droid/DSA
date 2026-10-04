# When Not to Use Machine Learning
@short: When Not To
@subtitle: The judgement that saves the most time, and a closing synthesis
@tier: reference
@prereq: none
@blurb: This book has spent forty-six chapters on how to build these systems. The final skill is knowing when not to --- recognising, before the work starts, that rules are sufficient, that the data cannot support the claim, or that the problem is organisational rather than technical. It closes with a synthesis of the principles that recur throughout.
@objectives:
- Recognise the five situations where ML is the wrong tool
- Estimate the noise floor before committing to an accuracy target
- Choose the simplest sufficient solution and defend it
- Distinguish technical problems from organisational ones
- Carry the book's recurring principles into work it does not cover

## Five situations where the answer is no

@fig: decision_tree_ml | 172 | The decision. Most proposals terminate at one of the first three branches, and each of those terminations saves months.

**1. The rules are known, stable and expressible.**

```python
# Someone proposes a model to decide which orders need manual review.
# The actual policy, obtained by asking:
def needs_review(order):
    return (order.total > 10_000
            or order.country in HIGH_RISK
            or order.is_first_purchase and order.total > 500
            or order.payment_method == "wire")
```

Four lines. Auditable, instant, free, explainable to a regulator, and
changeable in a minute when the policy changes. A model would be worse on
every one of those axes and no better on accuracy, because the rules *are* the
ground truth.

Use ML when the rules are unknown, too numerous to enumerate, or change faster
than you can rewrite them. Not before.

**2. There is not enough data.**

| Labelled examples | Realistic |
|---|---|
| < 100 | rules, or a prompted foundation model with few-shot examples |
| 100--1,000 | a prompted model; fine-tuning only for narrow format tasks |
| 1,000--10,000 | regularised linear models, GBDTs |
| 10,000--100,000 | GBDTs, small neural models, fine-tuning |
| > 100,000 | anything |

@tbl: What each data regime supports. The top row is where most proposals actually sit, and it is also where a foundation model with a good prompt is genuinely strong --- which is a change from a few years ago and worth checking before concluding "not enough data".

**3. The required accuracy is below the noise floor.**

```python title="Estimate the ceiling before promising anything"
def noise_floor(labels_a, labels_b):
    """Have two annotators label the same 200 cases independently.
       Their agreement bounds what any model can achieve."""
    agreement = (labels_a == labels_b).mean()
    kappa = cohens_kappa(labels_a, labels_b)
    return dict(human_agreement=agreement, kappa=kappa,
                practical_ceiling=agreement)

# If two careful humans agree 82% of the time, a model cannot be
# meaningfully "95% accurate" — there is no consistent signal to learn.
# A stakeholder asking for 95% is asking for something that does not exist,
# and the useful response is to show them this number.
```

**4. No decision changes.**

If the output goes on a dashboard nobody acts on, accuracy is irrelevant.
Ask what happens differently when the number is 0.9 instead of 0.3. If the
answer is "nothing", stop.

**5. The real problem is organisational.**

A forecasting model will not fix a planning process that ignores forecasts. A
churn model will not help if nobody owns retention. A recommendation system
will not fix a catalogue with no metadata. These projects fail at launch for
reasons that were visible at the start, and the technical work was never the
constraint.

:::warning The accuracy conversation to have on day one
Stakeholder: *"We need it to be 99% accurate."*

The response: *"Two of your own experts agree with each other 82% of the time
on these cases. 99% does not exist here. What we can do is catch 70% of them
with 5% false alarms --- here is what that means for your queue. Is that worth
building?"*

This conversation is uncomfortable once and saves months. Having it after six
months of work is considerably more uncomfortable.
:::

## The simplest sufficient solution

| Approach | Build time | Interpretable | Maintenance | Try it when |
|---|---|---|---|---|
| Rules | hours | fully | low | the policy is known |
| SQL aggregate / heuristic | hours | fully | low | a threshold on a known quantity |
| Prompted foundation model | days | partly | low | language in, language out |
| Regularised linear model | days | fully | low | tabular, few samples |
| GBDT | days | partly | moderate | tabular, enough data |
| Fine-tuned model | weeks | no | high | style or format, consistently |
| Custom architecture | months | no | very high | essentially never |

@tbl: Try these in order and stop at the first that clears the pre-agreed bar. Every row below your stopping point is cost you did not have to pay --- in build time, in maintenance, and in the explanation you will owe someone later.

:::insight The most expensive mistake in applied ML
It is not choosing the wrong model. It is building a model at all for a
problem that did not need one, and then maintaining it for years: retraining,
monitoring, drift investigations, on-call, and the recurring explanation of
why it did something.

A rule costs its author an afternoon and almost nothing thereafter. The
comparison is not build-time against build-time; it is build-time against the
*lifetime* cost of an ML system, which is several times larger and never
ends.
:::

## What carries across

The techniques in this book will date. These will not.

:::checklist The principles that recurred in every part
**Measure before you optimise.** Chapter 1's profiler, Chapter 7's roofline,
Chapter 37's golden set, Chapter 43's attribution. Every chapter's advice was
"find out which thing is the problem first", because the intuition is wrong
often enough to be unreliable.

**Bytes moved, not operations performed.** The memory hierarchy decided
NumPy's strides, columnar storage, kernel fusion, FlashAttention, GQA and why
decode is slow. One principle, six chapters apart.

**The gap between what you measured and what you want.** Empirical versus
expected loss, offline versus online metrics, the judge versus the human, the
development set versus production. Every evaluation question is this gap,
examined from a different side.

**Validate at the boundary, trust the interior.** Pydantic at the edge,
schemas on tool arguments, authorisation at the tool, point-in-time
correctness at ingest. The same architecture at four scales.

**Make failure bounded rather than impossible.** Budgets in the agent loop,
canaries in deployment, least privilege under injection, verification in
multi-step tasks. You cannot prevent failure in a probabilistic system; you
can make it cheap.

**Honest reporting beats favourable reporting.** Intervals, paired tests,
what regressed, what you broke, what it does not do. This is also the thing
that most reliably distinguishes a senior engineer, which is not a
coincidence.

**The simplest thing that clears the bar.** Linear baseline before the GBDT,
prompting before fine-tuning, BM25 before the vector database, a rule before
the model.
:::

:::insight A closing note on how to keep learning
Separate the three layers, as Chapter 21 of the *Skill Map* puts it:
**principles** last decades, **techniques** last years, **tools** last months.
This book is mostly the first two, which is why it should remain useful after
its library versions do not.

When something new arrives --- and it will, faster than this book can be
revised --- the questions are the same ones you have been asking throughout.
What does it actually compute? What does it cost in bytes and in FLOPs, and
which side of the ridge does that put it on? What does it assume about the
data? How would I measure whether it helped, and how many samples would that
take? What does it do when it fails?

An engineer who asks those five questions does not need to be told what the
next technique is. That is the thing worth having, and it is what the
forty-six chapters before this one were for.
:::

:::practice The final task
Take the three most recent ML projects in your organisation --- including ones
you did not work on. For each: (a) run the seven scoping questions from
Chapter 46; (b) estimate the noise floor from annotator agreement if labels
are human-generated; (c) identify the simplest approach from the table above
that would have cleared the bar; (d) estimate the lifetime cost of what was
actually built against that alternative; (e) write one page on what you would
do differently.

Then do the same for the project you are about to start.

**You have this skill when** you can decline a project convincingly, and when
the projects you do take on are ones you can still defend a year later.
:::

:::exercise
1. Find a model in your organisation that could be replaced by fewer than
   twenty lines of rules. Measure both.
2. Estimate the noise floor for a labelling task of yours with two independent
   annotators on 200 cases.
3. † Compute the three-year total cost of ownership of one deployed model:
   build, retraining, monitoring, incidents, on-call and explanation. Compare
   it to the rule-based alternative.
4. Take a dashboard metric and trace it to a decision. If there is none, say
   what should change.
5. Find a project that failed for organisational reasons. What was visible at
   kickoff?
6. † For a problem of yours, build the solution at three rungs of the table
   above. Report accuracy, build time and projected maintenance for each, and
   state where you would stop.
7. Apply the five closing questions to a technique released in the last six
   months. Would you adopt it?
:::

:::recap
- Five situations where the answer is no: the rules are known, the data is
  insufficient, the target is below the noise floor, no decision changes, or
  the problem is organisational.
- Estimate the noise floor from annotator agreement before promising an
  accuracy, and have that conversation on day one.
- Try approaches in order of cost and stop at the first that clears a
  pre-agreed bar.
- The lifetime cost of an ML system is several times its build cost and never
  ends; a rule's is close to zero.
- What carries across: measure first, count bytes, mind the gap between what
  you measured and what you want, validate at the boundary, bound failure
  rather than preventing it, report honestly, and prefer the simplest
  sufficient thing.
- When something new arrives, ask: what does it compute, what does it cost,
  what does it assume, how would I measure it, and what happens when it fails?
:::
