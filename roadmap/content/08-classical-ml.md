# Classical Machine Learning
@short: Classical ML
@subtitle: Still the right answer for most business problems, and still interviewed
@tier: core
@prereq: Chapters 4, 6
@blurb: Gradient-boosted trees remain the strongest method for tabular data, which is what most organisations actually have. Classical ML is also where the discipline of honest evaluation was developed, and those habits transfer directly to foundation-model work. Skipping this layer is the most common gap in engineers who learned ML after 2022.
@objectives:
- Choose and tune the right classical model for a tabular problem
- Design a validation scheme that does not lie to you
- Select and interpret metrics appropriate to the decision being made
- Calibrate probabilities and explain model behaviour to a non-specialist

## What this is for

If the data is a table of tens of thousands to tens of millions of rows with
heterogeneous columns --- which describes fraud, churn, pricing, credit,
forecasting, ranking features and most of what a business measures --- a
gradient-boosted tree will usually beat a neural network, train in minutes
rather than hours, need no normalisation, handle missing values natively, and
be explainable. That is not nostalgia; it is repeatedly reproduced.

## The capabilities

:::checklist ESSENTIAL --- models
- Linear and logistic regression, with regularisation, as the baseline you
  must beat and the model you can always explain
- Gradient-boosted trees: XGBoost, LightGBM, CatBoost. Know the differences
  --- LightGBM's leaf-wise growth and histogram binning, CatBoost's ordered
  target statistics for categoricals
- Random forests, and why boosting usually beats bagging on tabular data
- $k$-NN, $k$-means, DBSCAN/HDBSCAN, and hierarchical clustering
- PCA and UMAP for dimensionality reduction and visualisation, with the
  caveat that UMAP distances between clusters are not meaningful
- Isolation Forest and similar for anomaly detection
:::

:::checklist ESSENTIAL --- validation
- Train/validation/test discipline, and never touching test until the end
- $k$-fold, stratified $k$-fold, group $k$-fold, and time-series splits ---
  choosing the right one is most of the skill
- Nested cross-validation when you are selecting hyperparameters *and*
  estimating performance
- Preventing the four leakages from Chapter 6, structurally
- The habit of a fixed, versioned holdout that predates any modelling
:::

:::checklist ESSENTIAL --- metrics
- Classification: accuracy (rarely the right choice), precision, recall, F1,
  ROC AUC, PR AUC. Know that PR AUC is the right one under heavy imbalance
- Choosing an operating point from a cost matrix rather than from a default
  0.5 threshold
- Calibration: reliability diagrams, Brier score, Platt scaling, isotonic
  regression --- essential whenever the probability itself is used in a
  downstream decision
- Regression: MAE, RMSE, MAPE and its failure at small values, quantile loss
  for intervals
- Ranking: NDCG, MRR, MAP, recall@$k$ --- and knowing which matches the
  product
- Reporting a confidence interval with every number
:::

:::checklist CORE --- practice
- Feature engineering for tabular data: target encoding done inside the fold,
  interactions, binning, cyclical encodings for time
- Class imbalance: class weights, threshold tuning, and honest scepticism
  about SMOTE (it frequently does nothing once the threshold is tuned)
- Hyperparameter search: random search beats grid; Optuna's Bayesian search
  beats random; early stopping on a validation fold is non-negotiable
- Interpretability: SHAP values, permutation importance, partial dependence.
  Know that tree feature importances are biased toward high-cardinality
  features
- Model selection under a latency or memory budget, not just a metric
:::

:::checklist AWARENESS
- Causal inference: uplift modelling, propensity scores, difference-in-
  differences. The question "does this feature cause the outcome" is
  different from "does it predict it", and businesses usually want the first
- Survival analysis for time-to-event problems
- Conformal prediction for distribution-free prediction intervals --- a
  genuinely useful, underused technique
:::

## Tabular or deep?

| Situation | Choose | Why |
|---|---|---|
| Tabular, < 10M rows | GBDT | faster, better, explainable, no preprocessing |
| Tabular, very high cardinality categoricals | GBDT (CatBoost) or embeddings + MLP | depends on interaction depth needed |
| Tabular + text or image columns | embed the unstructured column, then GBDT | hybrid beats both pure approaches |
| Images, audio, text | deep | the inductive biases matter |
| Sequences with long dependencies | deep | |
| Very small data (< 1000 rows) | linear or GBDT with heavy regularisation | deep overfits |
| Need a probability you will act on | anything, then calibrate | calibration is a separate step |

@tbl: The choice, stated plainly. The hybrid row is underused: embedding a free-text column with a small model and feeding the vector to a GBDT is often the strongest and cheapest option.

:::insight Why this chapter still matters if you want to do LLM work
The evaluation discipline transfers wholesale. Golden sets, held-out data,
confidence intervals, threshold selection from a cost matrix, calibration,
the refusal to trust a single number --- all of it was developed here and all
of it is exactly what foundation-model teams are currently missing. Engineers
who learned evaluation on tabular problems are noticeably better at
evaluating LLM systems.
:::

## How to tell you have it

:::practice The task
Take an imbalanced tabular dataset with a temporal component. Then:
1. Build a baseline (majority class, then logistic regression) and write down
   its number before doing anything else.
2. Design the validation scheme and justify it in two sentences. If the data
   has time, you must not use random $k$-fold.
3. Train a GBDT, tune with Optuna and early stopping.
4. Select a threshold from an explicit cost matrix, not from 0.5.
5. Calibrate and produce a reliability diagram.
6. Report the improvement over baseline with a bootstrap confidence interval.
7. Explain the top five features to somebody non-technical using SHAP, and
   have them tell you whether the explanation is plausible.

Step 7 catches leakage more often than any test does.
:::

:::pitfall The five that recur
1. **Accuracy on imbalanced data.** 99% accuracy on a 1% positive rate is the
   majority-class baseline.
2. **Random split on time-series data.** The model learns from the future.
3. **Target encoding fitted outside the fold.** Leakage, and a dramatic
   offline improvement that vanishes in production.
4. **Trusting tree feature importances.** They are biased; use permutation
   importance or SHAP.
5. **Uncalibrated probabilities used in a decision rule.** A model that ranks
   perfectly can still produce probabilities that are systematically wrong,
   and expected-value calculations built on them will be wrong too.
:::

:::note Time to competence
**6--8 weeks** for ESSENTIAL and CORE with real datasets. The validation and
metric material is the part that transfers everywhere and deserves the larger
share of the time.
:::

:::recap
- GBDT is still the default for tabular data: faster, stronger, explainable,
  and tolerant of missing values and raw categoricals.
- The validation scheme is most of the skill; choose it from the structure of
  the data (time, groups, imbalance).
- Choose metrics from the decision, choose the threshold from a cost matrix,
  and calibrate whenever the probability is acted on.
- Embedding an unstructured column and feeding it to a GBDT is an underused,
  strong hybrid.
- The evaluation discipline learned here is precisely what foundation-model
  teams most often lack.
:::
