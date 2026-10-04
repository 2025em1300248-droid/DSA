# Explaining a Model
@short: Explanation
@subtitle: Attribution methods, what they mean, and what they do not
@tier: core
@prereq: Chapter 19
@blurb: "Why did the model do that?" is asked by regulators, by stakeholders, by the person whose loan was declined, and --- most usefully --- by you, when debugging. The available methods answer subtly different questions, and using one to answer another is the source of most bad explanations. This chapter covers what each method computes and when to trust it.
@objectives:
- Distinguish global from local explanation, and correlation from causation
- Use SHAP correctly, including its assumptions and its cost
- Read partial dependence and ICE plots without over-reading them
- Choose an inherently interpretable model when that is the right call
- Explain a prediction to a non-technical person without lying

## Four different questions

@fig: explanation_map | 150 | The explanation landscape. Methods differ along two axes --- whether they describe the whole model or one prediction, and whether they describe the model or the world. Most bad explanations come from reading a point in one quadrant as if it were in another.

| Question | Method | Answers about |
|---|---|---|
| Which features does the model rely on overall? | permutation importance, mean \|SHAP\| | the model |
| Why this prediction? | SHAP, LIME, counterfactuals | the model |
| How does the output change with feature $j$? | PDP, ALE, ICE | the model |
| What would change the outcome for this person? | counterfactual | the model, actionably |
| What would happen if we intervened? | a causal model, an experiment | **the world** |

@tbl: The critical line is the last row. No attribution method answers a causal question, no matter how it is phrased in the meeting.

:::warning The error that matters most
"SHAP says income is the biggest driver, so raising incomes would reduce
defaults."

SHAP describes **the model's function**, not the world. If income is a proxy
for something unmeasured, the model uses it and SHAP reports it, and an
intervention on income changes nothing. The only way to answer an
interventional question is an intervention --- an experiment, or a causal
model with assumptions you have stated and defended.

State this out loud when presenting attributions. It is the difference between
a useful explanation and an expensive mistake.
:::

## SHAP

SHAP assigns each feature a contribution to the difference between this
prediction and the average prediction, using the Shapley value from
cooperative game theory: the average marginal contribution of a feature over
all orderings in which features could be added.

$$f(x) = \mathbb{E}[f(X)] + \sum_{j} \phi_j$$

The additivity is what makes it useful: the contributions sum exactly to the
prediction, so an explanation is complete rather than indicative.

```python title="SHAP in practice"
import shap

explainer = shap.TreeExplainer(model)          # exact and fast for trees
sv = explainer(X_val)                          # (n_samples, n_features)

shap.plots.bar(sv)                             # global: mean |SHAP|
shap.plots.beeswarm(sv)                        # global: direction + magnitude
shap.plots.waterfall(sv[0])                    # local: one prediction
shap.plots.scatter(sv[:, "income"], color=sv)  # one feature's effect + interaction

# Verify additivity — this should hold to floating-point tolerance:
assert np.allclose(sv.values.sum(1) + sv.base_values, model.predict(X_val))
```

| Explainer | Model | Cost | Exact? |
|---|---|---|---|
| `TreeExplainer` | trees, GBDT | fast, polynomial | yes |
| `LinearExplainer` | linear | trivial | yes |
| `DeepExplainer` | neural nets | moderate | approximate |
| `KernelExplainer` | anything | very slow | approximate |
| `PermutationExplainer` | anything | slow | approximate |

@tbl: SHAP explainers. `TreeExplainer` is exact and fast, which is a large part of why SHAP became standard in tabular ML. `KernelExplainer` on a large model is often impractical --- budget seconds per prediction.

:::pitfall Three ways SHAP misleads
**Correlated features split credit.** Two nearly identical features each get
about half the attribution, so both look unimportant. Group them, or drop one.

**The background distribution is a choice.** SHAP explains relative to a
baseline $\mathbb{E}[f(X)]$, and changing the background sample changes every
number. Use a representative sample --- not the training set if the serving
population differs.

**Interventional versus conditional.** The default (`TreeExplainer` with
`feature_perturbation="interventional"`) breaks feature correlations, which
can evaluate the model at combinations that cannot exist --- an 18-year-old
with 30 years of employment. The conditional variant respects correlations but
spreads credit to features the model never used. Neither is "right"; know
which you are using.
:::

## Partial dependence, ICE and ALE

```python title="Three views of one feature"
from sklearn.inspection import PartialDependenceDisplay

# PDP: average prediction as feature j is varied, holding others fixed.
# ICE: the same curve for each individual row, not averaged.
PartialDependenceDisplay.from_estimator(
    model, X_val, features=["income", "age", ("income", "age")],
    kind="both",           # PDP line over the ICE spaghetti
)
```

The PDP averages away heterogeneity, so a feature that helps half the
population and harms the other half shows a flat PDP. The ICE curves reveal
this immediately, which is why you should always plot both.

**ALE** (accumulated local effects) fixes the PDP's other problem: PDP varies
one feature while holding correlated features fixed, evaluating the model
off-distribution. ALE looks only at local changes within the data's actual
support, and is the better choice whenever features are strongly correlated.

## Counterfactuals: the explanation people actually want

"Your loan was declined because your debt-to-income ratio contributed
−0.23 to the log-odds" is not usable by the person receiving it. "Your
loan would have been approved with either £4,000 less debt or £6,000 more
annual income" is.

```python title="A counterfactual search with actionability constraints"
def counterfactual(model, x, target=1, mutable=None, max_changes=2):
    """Smallest change to mutable features that flips the prediction."""
    best = None
    for feats in combinations(mutable, r=max_changes):
        for delta in search_grid(feats):
            xp = apply(x, feats, delta)
            if not plausible(xp):            # respect real-world constraints
                continue
            if model.predict(xp) == target:
                cost = weighted_distance(x, xp)
                if best is None or cost < best[0]:
                    best = (cost, xp)
    return best
```

Two constraints separate a useful counterfactual from a useless one.
**Actionability**: only vary features the person can change --- not age, not
country of birth. **Plausibility**: the counterfactual must lie in the data
distribution; "reduce your age by 10 years" is technically a valid flip.

## Inherently interpretable models

Sometimes the right answer is not to explain a black box but to build
something that needs no explanation.

| Model | Interpretability | Typical cost vs GBDT |
|---|---|---|
| Linear / logistic | exact, additive | 0--10% on tabular |
| Decision tree (depth ≤ 4) | a readable flowchart | 5--20% |
| GAM / EBM | exact, per-feature curves | 0--5% |
| Rule list | a readable if-then list | 5--15% |
| Scorecard (binned + points) | an addable table | 5--15% |

@tbl: Interpretable alternatives. Explainable Boosting Machines (EBMs) are the notable modern entry: a generalised additive model with pairwise interactions, fitted by boosting, that is often within a few percent of a full GBDT while remaining exactly decomposable per feature.

:::insight When to choose interpretable over explained
Choose an inherently interpretable model when (a) a regulator requires a
reason code with legal force, (b) the model informs a decision a human must
sign off, (c) errors are expensive and you need to *audit* the logic, or
(d) the accuracy gap is small --- which on tabular data it often is.

An explanation of a black box is an approximation of a model. An interpretable
model *is* the explanation. When the explanation must be defended, the
difference matters.
:::

## Explaining to a person

:::checklist What actually works in a stakeholder meeting
- **Lead with the decision, not the score.** "We are declining this" before
  "the probability is 0.83".
- **Give three reasons, not fifteen.** The top three SHAP values, in the
  units of the feature: "six late payments in the last year", not
  "late_payment_count contributed +0.31".
- **Give the counterfactual.** "This would flip with no late payments in the
  next six months."
- **State the uncertainty.** "About one in six of these turn out fine."
- **Say what the model cannot see.** The honest limitation, stated
  unprompted, buys more trust than any chart.
- **Never present an attribution as a cause** unless you ran the experiment.
:::

:::practice The task
On a model of yours: (a) compute SHAP values and verify additivity;
(b) duplicate your strongest feature and re-run --- observe the credit split,
then fix it by grouping; (c) plot PDP and ICE for a feature you expect to be
heterogeneous, and confirm the PDP hides it; (d) compute ALE for a strongly
correlated feature and compare to PDP; (e) generate an actionable
counterfactual for five declined cases and check plausibility; (f) fit an EBM
and report the accuracy gap against your GBDT.

**You have this skill when** you can explain one prediction to a
non-technical person in three sentences, and correctly refuse to answer the
causal question they ask next.
:::

:::exercise
1. Verify SHAP additivity numerically and explain why it holds.
2. Duplicate a feature and show both SHAP values halve. Quantify the effect on
   the global bar chart.
3. † Change the SHAP background distribution to a different population and
   report how much each attribution moves.
4. Construct a dataset where the PDP is flat and the ICE curves are strongly
   split. Explain the mechanism.
5. Build a case where PDP evaluates the model on impossible feature
   combinations, and show ALE avoids it.
6. † Implement counterfactual search with actionability and plausibility
   constraints, and compare against unconstrained search on ten cases.
7. Fit an EBM and a GBDT on the same data. Report the gap and argue which you
   would deploy, given a regulatory requirement for reason codes.
:::

:::recap
- Explanation methods describe the *model*, not the world; no attribution
  answers a causal question.
- SHAP contributions sum exactly to the prediction; `TreeExplainer` is exact
  and fast.
- SHAP is confounded by correlated features, depends on the chosen background
  distribution, and has interventional and conditional variants that differ.
- Always plot ICE alongside PDP, and prefer ALE when features are correlated.
- Counterfactuals are what people can act on; constrain them to be actionable
  and plausible.
- An interpretable model *is* its explanation; EBMs often cost only a few
  percent.
- In a meeting: the decision, three reasons in feature units, a counterfactual,
  the uncertainty, and the limitation.
:::
