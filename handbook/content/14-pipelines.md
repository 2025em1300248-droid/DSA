# Pipelines That Do Not Lie
@short: Pipelines
@subtitle: Point-in-time correctness, validation, idempotence and backfill
@tier: core
@prereq: Chapter 12
@blurb: The most damaging bugs in machine learning are not in the model. They are in the pipeline that produced the training data, and they show up as excellent offline metrics followed by a disappointing launch. This chapter covers the four properties a data pipeline needs --- point-in-time correctness, validation, idempotence and replayability --- and how to build each one.
@objectives:
- Build point-in-time-correct features and prove they have no leakage
- Validate data at every stage and fail loudly on schema or distribution drift
- Write idempotent tasks so a rerun is always safe
- Backfill history without corrupting the present
- Detect and fix train--serve skew

## Leakage: the failure this chapter exists to prevent

@fig: leakage_timeline | 120 | Point-in-time correctness. The feature window must close strictly before the prediction time; anything between prediction and label is the future. Every leakage bug is a violation of this picture.

:::pitfall The five leaks, in order of how often they happen
**1. Future aggregates.** A feature computed over the whole table --- "average
order value per user" --- includes orders placed after the prediction time.
Offline AUC 0.95, production 0.71.

**2. Label-derived features.** A field that is only populated once the outcome
is known: `refund_amount`, `closed_date`, `resolution_code`. It is
overwhelmingly predictive and completely unavailable at prediction time.

**3. Random splits on temporal data.** A random train/test split lets the
model learn from the future for some rows. Always split by time when the
data has time.

**4. Preprocessing before splitting.** Fitting a scaler, an imputer, a target
encoder or a vocabulary on the full dataset leaks test statistics into
training. Fit on train only, inside the pipeline.

**5. Entity leakage.** The same user appears in train and test with
near-duplicate rows. Split by entity, not by row.
:::

```python title="A leakage detector you can run on any dataset"
def leakage_report(df, label_col, time_col, threshold=0.95):
    """Flag single features that predict the label suspiciously well."""
    from sklearn.metrics import roc_auc_score
    out = []
    for c in df.columns:
        if c in (label_col, time_col) or not is_numeric(df[c]):
            continue
        s = df[c].fill_null(df[c].median())
        auc = roc_auc_score(df[label_col], s)
        auc = max(auc, 1 - auc)                  # direction-agnostic
        if auc > threshold:
            out.append((c, round(auc, 3)))
    return sorted(out, key=lambda t: -t[1])

# Any single feature with AUC > 0.95 is leakage until proven otherwise.
# Investigate every one. "It is just a very good feature" is almost never true.
```

## Point-in-time correctness, implemented

Three timestamps, and you must keep them distinct:

- **`event_time`** --- when the thing happened in the world.
- **`ingest_time`** --- when your system learned about it.
- **`prediction_time`** --- when the model has to decide.

A feature may use data with `ingest_time <= prediction_time`. Using
`event_time <= prediction_time` is wrong whenever data arrives late, which is
always.

```python title="The correct join, with the late-arrival subtlety"
# WRONG: uses events that happened before the prediction but arrived after it.
features = events.filter(pl.col("event_time") <= prediction_time)

# RIGHT: only what the system actually knew at prediction time.
features = events.filter(pl.col("ingest_time") <= prediction_time)
```

```python title="As-of join in Polars"
labels = labels.sort("prediction_time")
feats  = feats.sort("computed_at")

training = labels.join_asof(
    feats,
    left_on="prediction_time",
    right_on="computed_at",
    by="entity_id",
    strategy="backward",          # nearest value at or before — never after
)
```

:::insight The test that proves correctness
Take a historical prediction your production system actually made. Rebuild its
feature vector from your training pipeline, with `prediction_time` set to that
moment. **The two vectors must be identical, field for field.**

If they are not, you have skew, and the difference tells you exactly where.
Run this as an automated check over a sample of production predictions every
day. It catches leakage, skew and silent logic changes in one test, and it is
the highest-value test in the whole data stack.
:::

## Validation at every stage

```python title="Contracts enforced in the pipeline, not in a README"
import pandera.polars as pa

class EventSchema(pa.DataFrameModel):
    event_id:   str   = pa.Field(unique=True)
    user_id:    str   = pa.Field(nullable=False)
    amount:     float = pa.Field(ge=0, le=1_000_000)
    event_time: pa.DateTime = pa.Field(nullable=False)
    event_type: str   = pa.Field(isin=["view", "click", "purchase"])

    @pa.check("event_time")
    def not_in_future(cls, s):
        return s <= datetime.now(timezone.utc)

df = EventSchema.validate(df, lazy=True)     # collect ALL errors, not the first
```

Schema validation catches structural breakage. Distribution checks catch the
subtler kind:

```python title="Distribution drift: the checks that catch real incidents"
def check_batch(df, baseline):
    issues = []
    n = len(df)
    if n < baseline["n"] * 0.5:
        issues.append(f"row count collapsed: {n} vs ~{baseline['n']}")
    for col, stats in baseline["columns"].items():
        null_rate = df[col].null_count() / n
        if null_rate > stats["null_rate"] + 0.05:
            issues.append(f"{col}: nulls {null_rate:.1%} vs {stats['null_rate']:.1%}")
        if stats["kind"] == "numeric":
            m = df[col].mean()
            if abs(m - stats["mean"]) > 4 * stats["std"]:
                issues.append(f"{col}: mean {m:.3g} vs {stats['mean']:.3g}")
        else:
            new = set(df[col].unique()) - set(stats["categories"])
            if new:
                issues.append(f"{col}: unseen categories {sorted(new)[:5]}")
    return issues
```

The row-count check is the one that earns its keep: a silently half-empty
partition from a failed upstream job is the most common data incident there
is, and every downstream metric moves in a way that looks like a real effect.

## Idempotence and backfill

A task is **idempotent** if running it twice produces the same result as
running it once. Without this, every retry is a data corruption risk --- and
retries are guaranteed.

```python title="Idempotent by partition overwrite"
def process_day(day: date) -> None:
    out = f"s3://bucket/features/day={day}/"
    tmp = f"s3://bucket/_tmp/{day}-{uuid4()}/"

    result = transform(read_day(day))
    result.write_parquet(tmp)          # write somewhere else entirely
    atomic_replace(src=tmp, dst=out)   # then swap, in one operation
```

Three properties make this safe: the output partition is a pure function of
`day`, the write goes to a temporary location first, and the swap is atomic.
A crash at any point leaves either the old data or the new data, never half of
either.

| Pattern | Idempotent? | Note |
|---|---|---|
| `INSERT INTO` | no | duplicates on every retry |
| `INSERT ... ON CONFLICT DO UPDATE` | yes | needs a real key |
| `DELETE WHERE day = X; INSERT` | almost | a crash between them loses data |
| Write temp, atomic swap | yes | the right default |
| `MERGE` / Delta / Iceberg | yes | transactional, versioned |

@tbl: Write patterns. The third row is what most hand-rolled pipelines do, and it is the one that produces a missing day after an incident.

:::warning Backfilling with today's code
Recomputing history with the current feature logic gives you a training set
that no production system ever saw. If the logic changed on 2026-02-14, a
backfill silently applies the new definition to January.

Version your feature definitions and record which version produced each
partition. When you backfill, either backfill *everything* (so training and
serving agree on one definition) or keep the old definition for old
partitions. Doing neither creates a dataset that is internally inconsistent in
a way no test will find.
:::

## Train--serve skew

The same feature, computed by two different code paths, in two different
languages, at two different times. It will diverge.

| Cause | Detection | Fix |
|---|---|---|
| Two implementations | compare on shared inputs daily | one implementation, shared |
| Different data freshness | log feature age at serving | match the training lag |
| Different null handling | compare null rates | one explicit policy |
| Different category encoding | compare vocabularies | ship the vocabulary with the model |
| Different time zones | compare timestamps | UTC everywhere, always |

@tbl: The five skew sources. The structural fix for the first is to compute features once, in one place, and have both training and serving read from it --- which is what a feature store is (Chapter 15).

:::practice The task
Build a pipeline for a dataset with real timestamps: (a) implement
point-in-time-correct features using an as-of join on `ingest_time`; (b) run
the leakage detector and investigate every feature above 0.95 AUC; (c) add
schema validation with pandera and distribution checks with a stored baseline;
(d) make every task idempotent via temp-write-and-swap, and prove it by
killing a run halfway; (e) implement the skew test --- rebuild a production
prediction's features from the training pipeline and assert equality.

**You have this skill when** you can hand someone a training set and state,
with evidence, that every feature in it was knowable at prediction time.
:::

:::exercise
1. Construct a dataset with future-aggregate leakage, train a model, and
   report offline and (simulated) online metrics.
2. Show that fitting a `StandardScaler` before splitting changes the test
   score. Quantify the inflation.
3. † Build a case where `event_time` filtering is correct and `ingest_time`
   filtering is correct, and they differ. Which training set matches
   production?
4. Write the skew test and run it against 100 historical predictions. Report
   the fields that differ.
5. Kill an idempotent task mid-write and confirm the output partition is
   unchanged. Then do the same with `DELETE`-then-`INSERT`.
6. † Change a feature definition, backfill one month, and demonstrate the
   internal inconsistency it creates. Design a versioning scheme that
   prevents it.
7. List every timestamp in a pipeline of yours and classify each as event,
   ingest or prediction time. Find the one that is being used wrongly.
:::

:::recap
- The five leaks: future aggregates, label-derived fields, random splits on
  temporal data, preprocessing before splitting, entity leakage.
- Keep event, ingest and prediction time distinct; features may use only what
  was *ingested* before the prediction.
- Any single feature with AUC above 0.95 is leakage until proven otherwise.
- The definitive test: rebuild a historical production prediction's features
  from the training pipeline and require exact equality.
- Validate schema *and* distributions; the row-count check catches the most
  common incident there is.
- Make tasks idempotent by writing to a temporary location and swapping
  atomically.
- Backfilling with changed logic creates an internally inconsistent dataset;
  version feature definitions.
:::
