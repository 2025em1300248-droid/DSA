# Data Engineering for ML
@short: Data Engineering
@subtitle: Thirty per cent of the hours, and most of the bugs that reach production
@tier: core
@prereq: Chapter 3
@blurb: Every model is a function of its data, and most model failures are data failures wearing a modelling costume. This chapter covers the data skills an ML or AI engineer is actually expected to have --- not the full data-engineering role, but the substantial overlap that you will be held responsible for.
@objectives:
- Write SQL that a data engineer would not rewrite
- Choose and use the modern dataframe and columnar tooling correctly
- Build a pipeline that is idempotent, observable and backfillable
- Prevent leakage and train--serve skew structurally rather than by vigilance

## What this is for

The three most expensive bugs in applied ML are all data bugs:

- **Leakage**: information from the future, or from the label, reaches the
  features. The offline metric is excellent and the production metric is not.
- **Train--serve skew**: the feature computed at training time is not the
  feature computed at serving time. Nothing errors; the model is just wrong.
- **Silent distribution change**: an upstream system starts sending nulls, or
  a unit changes from cents to dollars, and no test catches it.

None of these is detectable by looking at the model.

## The capabilities

:::checklist ESSENTIAL --- SQL
- Joins of every kind, and predicting which produces duplicate rows
- Window functions: `ROW_NUMBER`, `LAG`, `LEAD`, running aggregates,
  partitioned ranking. This is the single most useful SQL skill for ML work
- CTEs, and structuring a long query so it can be read
- Aggregation with `GROUP BY`, `HAVING`, `FILTER`
- Reading a query plan and explaining why something is slow
- Point-in-time correct joins --- the as-of join that prevents leakage
:::

:::checklist ESSENTIAL --- dataframes and formats
- `pandas` fluently, including the traps: `SettingWithCopyWarning`, silent
  dtype promotion to `object`, index alignment surprises
- `polars` or `duckdb` for anything that strains pandas. Both are
  substantially faster, use less memory and have saner semantics; DuckDB in
  particular lets you run SQL directly over Parquet files with no server
- Parquet and Arrow: columnar layout, predicate and projection pushdown,
  compression, row groups, and why columnar is right for training data
- Memory-mapped arrays for datasets larger than RAM
- Partitioning schemes, and why `date=2026-01-01/` directories make queries
  cheap
:::

:::checklist CORE --- pipelines
- An orchestrator: Airflow, Dagster or Prefect. Dagster's asset model maps
  particularly well onto ML dependencies; Airflow is the most widely deployed
- Idempotency: rerunning a task must produce the same result, not duplicate
  rows
- Backfills, and designing partitions so that a backfill is possible at all
- Data contracts and schema enforcement at boundaries
- Incremental processing rather than full recomputation
- `dbt` if your organisation has a warehouse
:::

:::checklist CORE --- data quality
- Validation as code: Great Expectations, `pandera`, or plain assertions that
  run in the pipeline and fail loudly
- The checks that matter: row counts within expected bounds, null rates,
  cardinality, range, referential integrity, freshness
- Distribution monitoring on *inputs*, not only on outputs
- Knowing the difference between a broken pipeline and a changed world, and
  alerting differently for each
:::

:::checklist CORE --- feature engineering and serving
- Feature stores conceptually: offline store for training scans, online store
  for point lookups, and one definition shared between them
- Point-in-time correctness --- computing a feature as it was at the label's
  timestamp, not as it is now
- Why train--serve skew arises: two implementations of one feature, one in
  batch SQL and one in a streaming service
- Windowed aggregates, and stating the window semantics precisely
:::

:::checklist AWARENESS
- Streaming: Kafka, Flink, and when a real-time feature is genuinely needed
  (usually less often than proposed)
- Lakehouse table formats: Iceberg, Delta Lake, Hudi --- time travel, schema
  evolution, ACID on object storage
- CDC (change data capture) from operational databases
:::

## The tools

| Job | Reach for | When |
|---|---|---|
| Ad-hoc analysis, < 1 GB | pandas | familiarity wins |
| 1--100 GB on one machine | Polars or DuckDB | 5--50x faster, far less memory |
| SQL over files, no server | DuckDB | genuinely excellent; use it more |
| > 1 TB, cluster | Spark, Ray Data, BigQuery | distributed is a cost, not a default |
| Orchestration | Dagster, Airflow, Prefect | Dagster for asset-shaped ML work |
| Validation | pandera, Great Expectations | run it in the pipeline, not in a notebook |
| Storage | Parquet on object storage | plus Iceberg/Delta if you need ACID |
| Feature store | Feast, or your platform's | or a well-disciplined table; the discipline is the hard part |

@tbl: Data tooling by scale. The most common mistake is reaching for a cluster at a scale where one machine with DuckDB would be faster and far simpler.

:::insight The pandas-to-Polars transition is worth making
Not for fashion: Polars has a lazy API that optimises the whole query,
a columnar engine that parallelises across cores by default, and semantics
without pandas' index surprises. DuckDB does the same job through SQL and
reads Parquet directly. For a dataset that makes pandas swap, either one
typically turns a job that did not finish into one that takes ninety
seconds. Learn one; keep pandas for small interactive work and for the
enormous ecosystem that expects it.
:::

## How to tell you have it

:::practice The task
Build a small feature pipeline end to end:
1. Raw events in Parquet, partitioned by date.
2. A point-in-time-correct join producing `(entity, label_time, label,
   features)` where every feature uses only data strictly before
   `label_time`.
3. Validation that fails the run if null rates or ranges move.
4. An online path that recomputes the same features from the same definition
   for a single entity at serving time.
5. A test that asserts the training-time and serving-time features agree for
   a sample of entities.

Step 5 is the one that matters and the one nearly everybody skips.
:::

:::pitfall Leakage, in the four shapes it actually takes
1. **Target leakage.** A feature computed after the label event, such as
   "number of support tickets" for a churn label.
2. **Temporal leakage.** Random train/test split on time-series data. Always
   split by time.
3. **Group leakage.** The same user, patient or document appears in both
   splits. Split by group.
4. **Preprocessing leakage.** Scaling, imputation or feature selection fitted
   on the full dataset before splitting. Fit inside the fold.

Each produces an offline metric that is too good and a production metric that
is disappointing --- and the gap is never attributed to the right cause.
:::

:::note Time to competence
**6--8 weeks** for the ESSENTIAL and CORE lists, assuming you are writing SQL
weekly. The point-in-time join is the single highest-value thing in the
chapter and deserves a full week on its own.
:::

:::recap
- Data bugs --- leakage, train--serve skew, silent distribution change --- are
  the most expensive failures in applied ML and are invisible from the model
  side.
- ESSENTIAL: SQL with window functions and as-of joins; pandas plus Polars or
  DuckDB; Parquet and Arrow.
- CORE: an orchestrator, idempotency, backfills, validation as code that
  fails the run, feature definitions shared between training and serving.
- Reach for a cluster only when one machine with DuckDB or Polars has
  genuinely failed.
- Leakage has four shapes; all four are prevented structurally by splitting
  and fitting correctly, not by care.
:::
