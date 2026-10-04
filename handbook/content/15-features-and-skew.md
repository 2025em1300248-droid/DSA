# Features, Stores and Encoding
@short: Features
@subtitle: Building representations that survive the trip to production
@tier: core
@prereq: Chapter 14
@blurb: Feature engineering is dead for unstructured data and very much alive for tabular data, where it remains the largest single lever on model quality. This chapter covers the encodings that work, the ones that leak, the infrastructure that keeps training and serving consistent, and how to tell whether a feature is earning its place.
@objectives:
- Encode categorical, numeric, temporal and text features correctly
- Apply target encoding without leaking, using out-of-fold estimates
- Decide whether you need a feature store, and what it actually solves
- Measure feature importance in a way that survives correlated inputs
- Handle high-cardinality and unseen categories at serving time

## Categorical encoding

| Encoding | Cardinality | Leaks? | Notes |
|---|---|---|---|
| One-hot | low (< 50) | no | explodes dimensionality; fine for linear models |
| Ordinal / label | any | no | implies an order; fine for trees, wrong for linear |
| Target (mean) | high | **yes, without care** | powerful; see below |
| Count / frequency | high | mildly | cheap and surprisingly strong |
| Hashing | unbounded | no | fixed width, collisions, no vocabulary to ship |
| Learned embedding | high | no | needs a neural model and enough data |
| Native categorical | high | no | LightGBM/CatBoost handle it directly --- prefer this |

@tbl: For gradient-boosted trees, native categorical support usually beats anything you do by hand. Reach for manual encoding when your model cannot take categories, or when cardinality is in the millions.

:::pitfall Target encoding leaks by construction
Replacing a category with the mean label of that category uses the label. If
you compute it over the whole training set, every row's own label contributes
to its own feature --- which is leakage, and it is severe for rare categories
where the row *is* most of its own mean.

The fix is out-of-fold encoding: compute each row's encoding from folds that
exclude it.
```python
from sklearn.model_selection import KFold
import numpy as np

def target_encode_oof(x, y, n_splits=5, smoothing=20, seed=0):
    prior = y.mean()
    out = np.full(len(x), prior, dtype=float)
    for tr, va in KFold(n_splits, shuffle=True, random_state=seed).split(x):
        stats = {}
        for c in np.unique(x[tr]):
            m = x[tr] == c
            n, mean = m.sum(), y[tr][m].mean()
            stats[c] = (n * mean + smoothing * prior) / (n + smoothing)
        out[va] = [stats.get(c, prior) for c in x[va]]
    return out
```
The `smoothing` term shrinks rare categories towards the global mean, which is
what stops a category seen twice from carrying a confident encoding. At
serving time, use the encoding fitted on *all* the training data --- the
out-of-fold version exists only to avoid training on your own label.
:::

## Numeric features

```python title="Transformations, and when each is right"
import numpy as np

x_log    = np.log1p(x)                      # right-skewed, non-negative
x_clip   = np.clip(x, *np.percentile(x, [1, 99]))   # outliers, keeps order
x_rank   = rankdata(x) / len(x)             # fully distribution-free
x_bin    = np.digitize(x, np.quantile(x, np.linspace(0, 1, 11)))  # non-linear

# Standardise for linear models, neural nets, and anything distance-based.
# Do NOT bother for trees: they are invariant to monotone transforms.
x_std = (x - mu_train) / (sd_train + 1e-8)  # statistics from TRAIN only
```

The last line is the one people get wrong. `mu` and `sd` must come from the
training split and be *shipped with the model*, because serving sees one row
at a time and cannot compute a mean.

```python title="Ratios and differences are where the signal usually is"
df = df.with_columns([
    (pl.col("amount") / pl.col("avg_amount_30d")).alias("amount_vs_typical"),
    (pl.col("amount") - pl.col("amount").shift(1).over("user")).alias("delta"),
    (pl.col("event_time") - pl.col("account_created")).dt.total_days()
        .alias("account_age_days"),
    (pl.col("n_events_7d") / pl.col("n_events_30d")).alias("recency_ratio"),
])
```

Trees can only split on axis-aligned thresholds, so a ratio that matters must
be handed to them explicitly --- a tree cannot discover $a/b$ from $a$ and $b$
without a great many splits. This is the largest single source of easy gains
in tabular modelling.

## Temporal features

```python title="Cyclical encoding, and why the naive version is wrong"
# Hour 23 and hour 0 are adjacent. As a raw integer they are 23 apart.
hour = df["event_time"].dt.hour()
df = df.with_columns([
    (2 * np.pi * hour / 24).sin().alias("hour_sin"),
    (2 * np.pi * hour / 24).cos().alias("hour_cos"),
])
# Also: day of week, day of month, is_weekend, is_holiday, days_since_last,
# and — usually the strongest — time since the entity's previous event.
```

:::warning Time zones and the reproducibility of "yesterday"
Store everything in UTC. Derive local-time features explicitly from a stored
time zone per entity. A pipeline that uses the *server's* local time produces
different features depending on where it runs, and different features again
after a daylight-saving transition --- a bug that appears twice a year and is
extremely hard to reproduce.
:::

## Feature stores: what they actually solve

@fig: feature_store | 132 | A feature store solves one problem: the same definition serving two access patterns. The offline store answers "what was this feature at these ten million past moments?"; the online store answers "what is it now, in five milliseconds?" --- from one definition.

```python title="A feature definition used by both paths"
@feature_view(entities=["user_id"], ttl="30d")
def user_spend_30d(events):
    return (
        events
        .filter(pl.col("event_type") == "purchase")
        .group_by_dynamic("event_time", every="1h", period="30d", by="user_id")
        .agg(pl.col("amount").sum().alias("spend_30d"))
    )

# Training: point-in-time correct join against the offline store
train = store.get_historical_features(entity_df=labels,
                                      features=["user_spend_30d:spend_30d"])

# Serving: a single key lookup against the online store, sub-millisecond
online = store.get_online_features(entities=[{"user_id": "u123"}],
                                   features=["user_spend_30d:spend_30d"])
```

:::insight Do you need one?
**No**, if you have fewer than about twenty features, one model, and batch
scoring. A well-tested shared Python module and a Parquet table do the job,
and a feature store adds operational surface for nothing.

**Yes**, when several models share features, when you serve online with
latency budgets, or when point-in-time correctness has already bitten you.
The value is not the storage --- it is the *single definition* with two
materialisations, which removes the train--serve skew structurally rather
than by discipline.

Between those, the pragmatic middle is: one shared library of feature
functions, a nightly job that materialises them to Parquet (offline) and Redis
(online), and the skew test from Chapter 14 running daily.
:::

## Which features are actually earning their place?

```python title="Permutation importance: the one that tells the truth"
from sklearn.inspection import permutation_importance

r = permutation_importance(model, X_val, y_val, n_repeats=10,
                           scoring="roc_auc", random_state=0)
for i in r.importances_mean.argsort()[::-1][:20]:
    print(f"{FEATURES[i]:<32} {r.importances_mean[i]:+.4f} "
          f"± {r.importances_std[i]:.4f}")
```

| Method | Measures | Trap |
|---|---|---|
| Tree split gain | training-time usage | biased towards high-cardinality features |
| Permutation | validation-set damage when shuffled | splits credit between correlated features |
| SHAP | per-prediction attribution | slow; still affected by correlation |
| Leave-one-out retrain | the honest answer | $n$ retrains |
| Grouped permutation | damage from removing a *group* | the fix for correlated features |

@tbl: Importance methods. Correlated features are the universal confounder: two duplicated features each show near-zero permutation importance because the model falls back on the other. Permute correlated features as a *group*.

:::pitfall Unseen categories at serving time
Your training vocabulary has 40,000 SKUs. Tomorrow a new SKU appears. What
happens?

- One-hot: an all-zero row, which may be fine or may be out of distribution.
- Label encoding: a `KeyError`, or worse, silently index 0 --- which means
  "the most common SKU", a confidently wrong prediction.
- Target encoding: must fall back to the prior. Make this explicit.
- Hashing: no problem at all; this is its main advantage.

Decide the policy, implement it once, and **test it** with a category that
does not exist. The number of production incidents caused by an unseen
category is not small.
:::

:::practice The task
On a tabular dataset: (a) build four encodings of a high-cardinality column
--- one-hot, frequency, out-of-fold target, hashing --- and compare validation
scores and fit time; (b) implement target encoding *with* leakage and show the
inflated offline score; (c) add five ratio and time-delta features and measure
the lift; (d) run permutation importance, then duplicate your strongest
feature and re-run to observe the credit-splitting; (e) send a row with an
unseen category through your serving path and record what happens.

**You have this skill when** you can state, for every feature in your model,
how it is computed at serving time and what happens when its inputs are
missing or new.
:::

:::exercise
1. Show numerically that naive target encoding gives a rare category an
   encoding equal to its own label.
2. Choose the smoothing parameter by cross-validation and plot score against
   it.
3. † Construct a dataset where a ratio feature is highly predictive and
   neither of its components is. Show a tree needs many splits to approximate
   it.
4. Demonstrate the hour-23/hour-0 problem with a linear model, then fix it
   with sine/cosine encoding.
5. Duplicate a feature and show both permutation importances collapse. Fix it
   with grouped permutation.
6. † Implement the offline/online split for one feature with Parquet and
   Redis, then run the Chapter 14 skew test against it.
7. Enumerate every failure mode of your serving path when a feature's upstream
   source returns null, and write the test for each.
:::

:::recap
- Prefer native categorical support in GBDTs over hand-rolled encoding.
- Target encoding leaks unless computed out of fold, with smoothing for rare
  categories.
- Standardisation statistics come from train only and ship with the model.
- Ratios and time-deltas are the largest easy gain in tabular modelling,
  because trees cannot construct them.
- Encode cyclical time with sine and cosine; store UTC and derive local time
  explicitly.
- A feature store's value is one definition with two materialisations; below
  about twenty features you do not need one.
- Permutation importance splits credit between correlated features; permute
  groups.
- Decide, implement and test the unseen-category policy before it happens in
  production.
:::
