# Statistics
@short: Statistics
@subtitle: The dozen ideas you actually need, explained without the maths
@tier: foundation
@prereq: none
@blurb: Your BITS coursework lists statistical modelling, so this gets probed. Short definitions are enough --- nobody wants a derivation. The ones worth real care are p-values, confidence intervals and the ways a sample can lie to you, because those are where most people say something wrong.
@objectives:
- Define the common statistics without reaching for formulas
- Say what a p-value is and, more importantly, what it is not
- Name the ways a sample can mislead you
- Connect a statistics answer back to your own data

## Describing data

#### Q7.1 — Mean vs median vs mode — when do you use the median?
When a few extreme values would drag the average somewhere silly. If nine
people earn £30k and one earns £3 million, the average says £327k and the
median says £30k. The median describes the group better.

Income and response times are the classic cases.

#### Q7.2 — Variance vs standard deviation?
Both measure how spread out the data is. Standard deviation is the useful one
because it's in the same units as your data — if you're measuring heights in
centimetres, the standard deviation is in centimetres too.

#### Q7.3 — What is skewness? What is kurtosis?
Skewness is lopsidedness. A long tail stretching to the right is positive
skew — income does this. Kurtosis is about how heavy the tails are, meaning
how often you get extreme values.

#### Q7.4 — What is the normal distribution, and why is it everywhere?
The bell curve. It turns up constantly because when lots of small independent
things add together, the result tends to look like a bell curve regardless of
what the individual things looked like.

#### Q7.5 — State the Central Limit Theorem.
If you take lots of samples and average each one, those averages form a bell
curve — even if the original data looked nothing like one. That's what makes
confidence intervals possible at all.

#### Q7.6 — What is the law of large numbers?
The more you measure, the closer your average gets to the true average. It's
why a hundred coin flips lands nearer to 50/50 than ten flips does.

## Testing and uncertainty

#### Q7.7 — What is a p-value, in plain words?
It answers one question: **if there were really no effect, how often would I
see a result at least this striking by pure chance?** A small p-value means
"this would be a surprising fluke."

What it is **not**: the probability that there's no effect. That's the mistake
almost everyone makes, and interviewers listen for it.

#### Q7.8 — Type I vs Type II error?
Type I is a false alarm — you say something's there when it isn't. Type II is
a miss — you say nothing's there when it is.

In your fire detector, a Type I error is an unnecessary email. A Type II error
is a fire nobody was told about.

#### Q7.9 — What is a confidence interval?
A range of plausible values rather than a single number. "95% confidence"
means the method you used produces a range that contains the truth 95 times
out of 100.

It's about the method's track record, not about this one particular range —
that's the subtlety people get wrong.

#### Q7.10 — What is a hypothesis test? Name two.
A procedure for deciding whether your data is strange enough to stop believing
"nothing is going on." A t-test compares two averages. A chi-square test
checks whether two categories are related.

#### Q7.11 — T-test vs z-test?
Use a z-test when you have a lot of data or you already know the spread of the
whole population. Use a t-test when you have a small sample and you're
estimating the spread from that sample. In practice it's nearly always a
t-test.

#### Q7.12 — What is ANOVA?
A test for whether three or more groups have different averages. It exists so
you don't run lots of separate two-group tests, which would throw up false
positives just by chance.

#### Q7.13 — What is a chi-square test used for?
Checking whether two categorical things are related — like whether contract
type is connected to whether someone churns. Which is directly relevant to
your churn data.

#### Q7.14 — Correlation vs covariance?
Both describe whether two things move together. Covariance gives you the
direction but in awkward units. Correlation rescales it to between −1 and +1,
so you can compare across different measurements.

#### Q7.15 — Correlation vs causation — how do you establish causation?
Correlation alone never establishes it. To show cause you need to intervene —
run an experiment where you change one thing at random and see what happens.
Without that, you're guessing.

#### Q7.16 — What is Bayes' theorem?
A rule for updating what you believe when new evidence arrives. You start with
how likely something was, you see some evidence, and you end up with a revised
belief.

The classic example: a test that's 99% accurate for a disease only one in ten
thousand people have will still give you mostly false alarms, because there
are so many more healthy people to get wrong.

#### Q7.17 — Probability vs likelihood?
Probability goes forward: given the rules, how likely is this outcome?
Likelihood goes backward: given this outcome, which set of rules explains it
best?

#### Q7.18 — What is maximum likelihood estimation?
Picking the settings that make the data you actually saw as unsurprising as
possible. It's what logistic regression is doing when it trains.

## The ways data misleads

#### Q7.19 — What is an outlier, and how do you detect one?
A point that sits far from everything else. Find them with a box plot, or by
flagging anything more than about one and a half times the middle spread away
from the middle.

Don't just delete them. Fraud cases and equipment failures **are** the
outliers — they're often the thing you're trying to find.

#### Q7.20 — Population vs sample?
The population is everyone you want to describe. The sample is the subset you
actually measured. Every statistic you compute is from the sample and is only
a guess about the population.

#### Q7.21 — What is sampling bias? Give an example from your own work.
When your sample doesn't represent the thing you care about.

Your own example: if all your safety-gear training footage was filmed during
daytime shifts, the detector will quietly get worse at night — and your test
set, filmed the same way, won't warn you.

#### Q7.22 — Selection bias vs survivorship bias?
Selection bias: who ended up in your sample wasn't random. Survivorship bias:
you only see the ones that lasted.

The churn version: if you only study customers who are still around, you've
removed exactly the people you're trying to learn about.

#### Q7.23 — What is expected value?
The average outcome if you repeated something many times, weighted by how
likely each outcome is. You use it to put an actual number on a decision —
like whether a 10% chance of losing a customer justifies a discount offer.

#### Q7.24 — What does i.i.d. mean, and when is it violated?
It means every data point is independent of the others and drawn from the same
source. Most methods quietly assume it.

It's violated by anything with time in it — and by consecutive video frames,
which are nearly identical to each other. **That's why you must split video
data by clip, not by frame.** Split by frame and nearly identical pictures end
up in both training and testing, so your score comes out far too good.

:::practice The one to rehearse
Q7.7 — the p-value. Say it as: "If there was really no effect, how often would
I see something this striking by chance?" Then say what it isn't. Getting that
distinction right marks you out immediately.
:::

:::recap
- Use the median when extreme values would drag the average somewhere silly.
- A p-value is how surprising your result would be if nothing were going on —
  not the chance that nothing is going on.
- A confidence interval describes the method's track record, not one range.
- Correlation never proves cause; only an experiment does.
- Don't delete outliers blindly — they are often the thing you're looking for.
- Consecutive video frames are not independent, which is why you split by clip.
:::
