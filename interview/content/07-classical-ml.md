# Classical Machine Learning
@short: Classical ML
@subtitle: The algorithms, explained the way you would to a colleague
@tier: foundation
@prereq: none
@blurb: Your resume names scikit-learn, SVM and Random Forest, so all of this is mandatory. Every answer here is one or two sentences plus what it is good for --- that second part is what separates someone who has used the algorithm from someone who has read about it.
@objectives:
- Explain overfitting and the bias-variance trade in plain words
- Describe each algorithm in two sentences and say when to use it
- Justify why you chose Random Forest, and what you would try next
- Answer the cross-validation questions without reciting

## The core ideas

#### Q9.1 — Supervised vs unsupervised vs reinforcement learning?
Supervised: you show it examples with the right answers attached, and it
learns to produce them. Unsupervised: no answers, it just finds structure —
groups, patterns. Reinforcement: it tries things and learns from reward and
punishment.

#### Q9.2 — Classification vs regression?
Classification picks a category — will this customer churn, yes or no.
Regression predicts a number — how much will they spend.

#### Q9.3 — What is the bias-variance tradeoff?
Two different ways a model gets things wrong.

**Bias** is being too simple to capture the pattern — like drawing a straight
line through data that curves. It gets things wrong consistently.

**Variance** is being too sensitive to the exact examples you trained on —
it memorises instead of learning, so a slightly different dataset gives a very
different model.

Making a model more complex reduces one and increases the other. The best
model sits somewhere in between.

#### Q9.4 — Overfitting vs underfitting — how do you spot each?
Overfitting: scores brilliantly on the training data, badly on anything new.
It memorised.

Underfitting: scores badly on both. It never learned.

You spot them by always comparing the two numbers. Looking only at the
training score tells you nothing.

#### Q9.5 — How do you fix overfitting?
More data, if you can get it. Otherwise: make the model simpler, add a penalty
for complexity, stop training earlier, use cross-validation to catch it, and
for trees, limit how deep they're allowed to grow.

#### Q9.6 — What is regularisation? L1 vs L2?
A penalty added for having large weights, which pushes the model toward
simpler solutions.

L1 pushes some weights to exactly zero, so it effectively deletes features.
L2 shrinks all of them smoothly without removing any. Use L1 when you want
to find out which features matter; L2 when you just want to calm things down.

#### Q9.7 — What is cross-validation? Why k-fold?
Instead of one train/test split, you cut the data into five parts, train on
four and test on the fifth, then rotate so every part gets a turn being the
test set.

Why: one split can be lucky or unlucky. Five give you an average and a sense
of how much the number wobbles.

#### Q9.8 — What is stratified k-fold, and why would you need it for churn?
Stratified means each fold keeps the same mix of classes as the whole dataset.

With only 26.5% churners, a plain random split could easily hand you a fold
with very few churners in it — and then your recall number is measured on
almost nothing and bounces around meaninglessly.

#### Q9.9 — Train, validation, test — what's each for?
Train: the model learns from it. Validation: you use it to choose settings and
compare models. Test: you touch it **once**, at the very end, for an honest
final number.

The moment you start tuning against the test set, it stops being a test.

## The algorithms

#### Q9.10 — Explain linear regression.
It draws the straight line that sits closest to all your points, and uses that
line to predict. Simple, fast, and you can read exactly what it's doing from
the coefficients.

#### Q9.11 — Explain logistic regression. Is it linear?
It takes a straight-line calculation and squashes the result into a number
between 0 and 1, which you read as a probability.

Is it linear? The boundary it draws between the two classes is a straight
line. The output isn't — it curves, because of the squashing.

#### Q9.12 — Why not use linear regression for classification?
Because its output isn't bounded, so it'll happily predict a "probability" of
1.4 or −0.2, which is meaningless. The squashed version doesn't have that
problem.

#### Q9.13 — Explain decision trees. How do they split?
A tree of yes/no questions. "Is the contract month-to-month? Yes → is tenure
under 6 months? Yes → likely to churn."

At each step it tries every possible question and picks the one that best
separates the classes. Left to grow fully, a tree will memorise the training
data completely.

#### Q9.14 — Gini vs entropy?
Two ways of measuring how mixed-up a group is. Entropy uses logarithms and
costs slightly more to compute. In practice they produce nearly identical
trees, so it rarely matters.

#### Q9.15 — Explain random forest. Why is it better than one tree?
Lots of trees, each trained on a different random sample of the data and
allowed to look at only a random subset of the columns. Then they vote.

Why that helps: each tree is wrong in its own way, and when you average lots
of **differently** wrong answers, the errors largely cancel out. One tree
alone would memorise.

#### Q9.16 — Your churn model uses 300 trees. Why 300?
Adding more trees to a forest never makes it overfit — it just stabilises.
So you raise the number until the score stops improving, then stop paying for
the extra compute.

Be honest if 300 was a sensible default rather than something you tuned.
That's a perfectly fine answer.

#### Q9.17 — Bagging vs boosting?
Bagging builds lots of models in parallel on different samples and averages
them. It fixes the "too sensitive" problem.

Boosting builds models one after another, each one focusing on what the
previous ones got wrong. It fixes the "too simple" problem.

#### Q9.18 — What is gradient boosting? Name an implementation.
Each new tree is trained specifically on the mistakes the current set of trees
is still making. XGBoost, LightGBM and CatBoost are the implementations.

On tabular data it usually beats random forest — worth saying you'd try it on
the churn problem.

#### Q9.19 — Explain SVM.
It finds the dividing line that leaves the widest possible gap between the two
classes. Only the points nearest the boundary matter — everything far away is
ignored.

#### Q9.20 — What is the kernel trick?
A way of drawing a curved boundary without actually doing the expensive work
of moving your data into a higher dimension. It gets the same answer much more
cheaply.

#### Q9.21 — What do C and gamma do in an SVM?
C controls how much you care about getting every training point right versus
keeping a wide clean gap. High C means fitting tightly, which risks
memorising.

Gamma controls how far each training point's influence reaches. High gamma
means each point only affects its immediate neighbourhood.

#### Q9.22 — Explain KNN. What's its weakness?
To classify something, look at the handful of training examples closest to it
and go with the majority.

Weaknesses: there's no training step, so all the cost is at prediction time
and it's slow on big data. It needs scaled features. And it falls apart when
you have many columns, because everything ends up roughly equally far from
everything else.

#### Q9.23 — Explain Naive Bayes. What's "naive" about it?
It uses Bayes' rule to work out which class is most likely given the features.

The naive part: it assumes every feature is independent of all the others,
which is almost never true. Oddly it works very well anyway, especially on
text.

#### Q9.24 — Explain k-means. How do you choose k?
Pick k starting points, assign every data point to its nearest one, move each
centre to the middle of its group, repeat until nothing moves.

Choose k by plotting how much the clusters improve as you add more — you look
for the point where the curve bends and extra clusters stop helping much.

#### Q9.25 — What are k-means' limitations?
You have to decide the number of groups up front. It assumes the groups are
roughly round and roughly the same size. It's sensitive to where you start.
And it cares about scale, so you must standardise first.

#### Q9.26 — What is hierarchical clustering? And DBSCAN?
Hierarchical repeatedly merges the two closest groups, building a tree you can
cut at any level.

DBSCAN groups by density — wherever points are packed closely together, that's
a cluster. It finds odd shapes, labels isolated points as noise, and you don't
have to pick the number of groups in advance.

#### Q9.27 — Explain PCA.
It finds the directions in which your data varies most, and describes each
point using just those few directions. You keep most of the information with
far fewer columns.

The cost: the new columns are blends of the old ones, so you can no longer say
"this is age" about any of them.

#### Q9.28 — What is the curse of dimensionality?
As you add more columns, your data spreads thinner and thinner, and the
distance between any two points starts looking about the same. Anything based
on "which points are nearest" stops working.

#### Q9.29 — Feature selection vs feature extraction?
Selection keeps some of your original columns and throws the rest away.
Extraction builds new columns out of combinations of the old ones, like PCA
does.

#### Q9.30 — What is feature importance in a random forest? What's the catch?
It measures how much each column helped separate the classes across all the
trees.

Two catches: it unfairly favours columns with lots of distinct values, and
when two columns say the same thing it splits the credit between them so both
look unimportant. Permutation importance or SHAP is more trustworthy.

#### Q9.31 — Hyperparameter vs parameter?
Parameters are what the model learns from the data. Hyperparameters are the
settings you choose before training — tree depth, learning rate, the number
of neighbours.

#### Q9.32 — How do you tune hyperparameters?
Try every combination if there are only a few. Try random combinations if
there are many — it's surprisingly more effective than a grid. Use a smarter
search like Optuna when each run is expensive.

Always tune against validation folds. Never against the test set.

#### Q9.33 — What is an ensemble? Name three ways to build one.
Combining several models so the group beats any individual. Bagging (average
many parallel models), boosting (build them in sequence fixing mistakes), and
stacking (train another model to decide how to combine them).

#### Q9.34 — What is the no-free-lunch theorem?
No single algorithm is best at everything. Which is why you benchmark a few
rather than assuming your favourite will win.

#### Q9.35 — How would you choose a model for a new tabular problem?
Start with something trivial as a baseline — predict the most common class.
Then logistic regression, because it's fast and you can read it. Then gradient
boosting, because it usually wins on tabular data.

Compare them on the same splits using a metric tied to what the business
actually cares about, not whichever number looks best.

:::practice The one to prepare
Q9.16 and Q9.4 together. You should be able to say why 300 trees is a safe
choice, and how you'd show whether your model is overfitting — comparing
training score against validation score. Those two are asked constantly.
:::

:::recap
- Bias is too simple, variance is too sensitive; complexity trades one for the
  other.
- Always compare training score against validation score — one alone tells you
  nothing.
- A random forest works because its trees are wrong in different ways.
- More trees never overfit a forest; more trees eventually hurt a boosted
  model.
- Stratified folds matter for churn because a plain split can leave you with
  almost no churners to measure.
- Tune against validation, never against test.
:::
