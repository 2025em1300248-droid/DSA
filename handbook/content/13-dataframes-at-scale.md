# Dataframes at Scale
@short: Dataframes
@subtitle: Polars, Arrow and the memory model underneath
@tier: core
@prereq: Chapter 7
@blurb: pandas taught a generation how to think about tabular data and is the wrong tool for most of what that generation now does. This chapter explains why --- the memory model, the copy semantics, the single-threaded execution --- and teaches the replacement: Arrow-backed, lazily evaluated, query-optimised dataframes that handle data larger than memory.
@objectives:
- Explain Arrow's memory layout and why zero-copy interop matters
- Write Polars expressions, including the lazy API and its optimisations
- Process datasets larger than RAM by streaming
- Choose correctly between Polars, DuckDB, pandas and Spark
- Recognise the four pandas habits that do not transfer

## Why the tooling changed

| | pandas | Polars / Arrow |
|---|---|---|
| Memory layout | NumPy blocks, object dtype for strings | Arrow columnar, native strings |
| Strings | Python objects, ~50 bytes overhead each | contiguous bytes + offsets |
| Nulls | `NaN` for floats, `None` for objects | a separate validity bitmap, uniform |
| Execution | eager, single-threaded | lazy, multi-threaded, optimised |
| Larger than RAM | no | streaming engine |
| Copy semantics | ambiguous (the infamous `SettingWithCopyWarning`) | explicit, immutable |

@tbl: The differences are structural, not cosmetic. String handling alone typically accounts for a 5--10× memory difference on real data.

:::insight Arrow is a memory format, not a library
Apache Arrow specifies how a column sits in memory: a contiguous data buffer,
a validity bitmap, and for variable-length types an offsets array. Because the
*format* is standardised, a DataFrame can move between Polars, DuckDB, PyArrow
and a Parquet reader **without serialising or copying** --- they all point at
the same bytes.

That is why `duckdb.sql(...).pl()` is free, and why `df.to_pandas()` is not
(pandas needs its own block layout, so it copies). Chaining Arrow-native tools
costs nothing; leaving the ecosystem costs a full copy.
:::

## Polars: expressions

The central idea is that you describe *what* you want as an expression, and
the engine decides how to compute it --- in parallel, and only for the columns
you touched.

```python title="The expression API, which is the whole language"
import polars as pl

df = pl.read_parquet("events.parquet")

out = (
    df
    .filter(pl.col("event_type") == "purchase")
    .with_columns([
        (pl.col("amount") * pl.col("quantity")).alias("total"),
        pl.col("event_time").dt.truncate("1d").alias("day"),
        pl.col("amount").log1p().alias("log_amount"),
    ])
    .group_by(["user_id", "day"])
    .agg([
        pl.len().alias("n"),
        pl.col("total").sum().alias("spend"),
        pl.col("total").mean().alias("avg_spend"),
        pl.col("sku").n_unique().alias("distinct_skus"),
        pl.col("total").filter(pl.col("total") > 100).count().alias("n_large"),
    ])
    .sort(["user_id", "day"])
)
```

Every expression inside `agg` runs in parallel across cores, and conditional
aggregation (`pl.col(...).filter(...)` inside `agg`) needs no separate pass.

```python title="Window functions, matching Chapter 12's SQL"
df.with_columns([
    pl.col("amount").sum().over("user_id").alias("user_total"),
    pl.col("amount").rank("ordinal", descending=True)
      .over("user_id").alias("rank_in_user"),
    pl.col("amount").rolling_mean_by("event_time", window_size="30d")
      .over("user_id").alias("avg_30d"),
    (pl.col("event_time") - pl.col("event_time").shift(1).over("user_id"))
      .alias("gap"),
])
```

## Lazy evaluation: where the speed comes from

```python title="Scan, don't read"
lf = pl.scan_parquet("s3://bucket/events/*.parquet")     # nothing read yet

q = (
    lf.filter(pl.col("day") >= pl.date(2026, 1, 1))      # predicate
      .select(["user_id", "amount", "day"])              # projection
      .group_by("user_id")
      .agg(pl.col("amount").sum())
)

print(q.explain())        # see the optimised plan before running it
result = q.collect()      # now it runs, reading only what it needs
```

The optimiser applies the same moves as a SQL engine: predicate pushdown into
the Parquet reader (row groups whose statistics exclude the range are skipped
entirely), projection pushdown (only three columns' pages are read), common
subexpression elimination, and slice pushdown. On partitioned data the
difference is routinely 10--100×.

```python title="Larger than memory: streaming"
(
    pl.scan_parquet("huge/*.parquet")
      .filter(pl.col("score") > 0.5)
      .group_by("category")
      .agg(pl.col("value").mean())
      .collect(engine="streaming")        # bounded memory, chunk at a time
)
```

@fig: lazy_pipeline | 152 | Eager versus lazy. The eager path materialises each intermediate; the lazy path builds a plan, optimises it, and then reads only the row groups and columns the plan needs.

## Choosing the tool

| Data size | Workload | Use |
|---|---|---|
| < 1 GB | anything | pandas is fine; Polars is faster |
| 1--50 GB | transforms, features | **Polars** (lazy) |
| 1--500 GB | SQL-shaped aggregation | **DuckDB** |
| 1--500 GB | complex Python per row | Polars + `map_batches` |
| > 1 TB | genuinely distributed | Spark, Ray Data, Daft |
| any | interop with sklearn/torch | Arrow → NumPy, zero copy |

@tbl: The honest sizing table. The "> 1 TB" row is much rarer than it seems --- a single machine with 512 GB of RAM and NVMe handles a surprising amount, and a Spark cluster costs more in engineering time than it saves in compute for anything below a few terabytes.

:::pitfall Four pandas habits that do not transfer
**`iterrows` / `apply(axis=1)`.** Per-row Python, roughly 1000× slower
than an expression. In Polars there is almost always an expression; when there
genuinely is not, use `map_batches` to process a whole column at once.

**Chained assignment.** `df[df.a > 1]["b"] = 0` may or may not modify `df` in
pandas. Polars dataframes are immutable, so the question does not arise ---
`with_columns` returns a new frame.

**Index gymnastics.** `set_index`, `reset_index`, `MultiIndex` and
`stack`/`unstack`. Polars has no index. Joins take explicit keys, which is
clearer and faster.

**`inplace=True`.** Rarely saves memory in pandas (it usually copies anyway)
and does not exist in Polars.
:::

## Getting data into a model

```python title="Zero-copy to NumPy and PyTorch"
import numpy as np, torch

X = df.select(FEATURES).to_numpy()          # zero copy for numeric columns
y = df["label"].to_numpy()
xb = torch.from_numpy(X)                    # also zero copy, shares memory

# For Arrow-native training paths, skip NumPy entirely:
tbl = df.to_arrow()                         # zero copy
```

The caveat: zero copy holds only when every selected column is a
fixed-width numeric type with no nulls. A null in an integer column forces a
cast to float (to get `NaN`), which copies. Materialise nulls deliberately ---
`fill_null` with an explicit sentinel and an indicator column --- rather than
letting a silent cast happen.

:::perf Measuring where the time goes
```python
import time
t0 = time.perf_counter()
out = q.collect()
print(f"{time.perf_counter()-t0:.2f}s, {out.estimated_size('mb'):.0f} MB")

print(q.explain(optimized=True))   # what the optimiser decided
print(q.profile()[1])              # per-node timings
```
`profile()` returns a frame of node timings. In practice the answer is almost
always one of: reading too many columns, reading too many row groups (the
filter is not pushing down), or a `map_batches` that fell back to Python.
:::

:::practice The task
Take a dataset of at least 20 GB in Parquet. (a) Write the same feature
computation three ways: pandas (if it fits), eager Polars, and lazy Polars
with `scan_parquet`; measure runtime and peak RSS for each. (b) Run
`q.explain()` and confirm predicate and projection pushdown appear. (c) Break
the pushdown deliberately (wrap the filter column in a function) and measure
the difference. (d) Process a dataset larger than RAM with
`engine="streaming"`. (e) Convert the result to NumPy and verify with
`np.shares_memory` whether the conversion copied.

**You have this skill when** your default for a new tabular job is
`scan_parquet` plus a lazy plan, and when you can say from the plan alone how
many bytes a query will read.
:::

:::exercise
1. Store one million strings in pandas with object dtype and in Polars, and
   compare memory.
2. Show that `duckdb.sql(...).pl()` does not copy and `.to_pandas()` does.
3. † Write a query where predicate pushdown skips most row groups, and confirm
   with the Parquet row-group statistics that it did.
4. Implement a 30-day trailing feature in Polars and check it against the SQL
   version from Chapter 12, row for row.
5. Time `apply(axis=1)` against the equivalent expression on a million rows.
   Report the ratio.
6. † Introduce a null into an integer column and demonstrate the silent cast
   to float on `to_numpy()`. Then handle it explicitly.
7. Take a job you currently run on Spark and estimate honestly whether DuckDB
   on one large machine would do it. State the crossover point.
:::

:::recap
- Arrow is a memory *format*; tools that share it interoperate without
  copying, and leaving it (to pandas) copies.
- Polars expressions describe what you want; the engine parallelises and
  optimises.
- Lazy scanning pushes predicates and projections into the Parquet reader,
  routinely 10--100× less data read.
- Streaming collection handles data larger than memory on one machine.
- Choose by size and shape: pandas under a gigabyte, Polars for transforms,
  DuckDB for SQL-shaped aggregation, distributed only above a terabyte.
- `iterrows`, chained assignment, index gymnastics and `inplace` do not
  transfer.
- Zero copy to NumPy requires fixed-width numerics with no nulls.
:::
