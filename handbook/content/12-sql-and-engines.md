# SQL and How Query Engines Think
@short: SQL and Engines
@subtitle: Writing queries that finish, and knowing why the slow one was slow
@tier: foundation
@prereq: none
@blurb: SQL is the most-used interface to data in existence and most ML engineers write it at roughly the level needed to get a result, not the level needed to get a result quickly or correctly. This chapter covers the constructs that matter --- window functions, the join family, correct temporal logic --- and then the execution model that explains every performance surprise.
@objectives:
- Write window functions fluently, which is most of what analytics SQL is
- Choose the right join and predict its cost
- Get temporal queries right, including the as-of join ML pipelines depend on
- Read an EXPLAIN plan and act on it
- Know when columnar storage changes the answer

## Window functions

If you learn one thing beyond `SELECT ... WHERE`, learn these. A window
function computes over a set of rows *related to the current row* without
collapsing them, which is exactly what feature engineering needs.

```sql title="The five patterns that cover most feature work"
SELECT
  user_id, event_time, amount,

  -- 1. Rank within a group
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC) AS recency,

  -- 2. Previous value (lag) — deltas, session gaps
  LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_time,

  -- 3. Running aggregate — cumulative spend
  SUM(amount) OVER (PARTITION BY user_id ORDER BY event_time
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_spend,

  -- 4. Trailing window — the shape almost every ML feature has
  AVG(amount) OVER (PARTITION BY user_id ORDER BY event_time
                    RANGE BETWEEN INTERVAL '30 days' PRECEDING
                              AND INTERVAL '1 second' PRECEDING) AS avg_30d,

  -- 5. Share of group total
  amount / SUM(amount) OVER (PARTITION BY user_id) AS share
FROM transactions;
```

:::warning `ROWS` versus `RANGE`, and the leakage it causes
`ROWS BETWEEN 30 PRECEDING AND CURRENT ROW` means *thirty rows*.
`RANGE BETWEEN INTERVAL '30 days' PRECEDING AND CURRENT ROW` means *thirty
days*. These are wildly different for irregular event streams.

And note `AND INTERVAL '1 second' PRECEDING` rather than `AND CURRENT ROW` in
pattern 4. Including the current row puts the label's own transaction into its
own feature --- textbook target leakage, and it produces a model with
suspiciously excellent offline metrics that fails completely in production.
Chapter 14 covers this properly; the SQL detail is that **the window must end
strictly before the prediction time.**
:::

## Joins: the family and the costs

| Join | Keeps | Typical cost | Watch for |
|---|---|---|---|
| `INNER` | matched rows only | hash: $O(n+m)$ | silently dropped rows |
| `LEFT` | all left, nulls right | hash: $O(n+m)$ | null-handling downstream |
| `FULL OUTER` | everything | hash: $O(n+m)$ | rarely what you meant |
| `CROSS` | every pair | $O(nm)$ | accidental, via a missing condition |
| `SEMI` (`EXISTS`) | left rows with a match | cheaper than inner | the right way to filter |
| `ANTI` (`NOT EXISTS`) | left rows without | cheaper than `NOT IN` | `NOT IN` + nulls is a trap |
| `ASOF` | nearest earlier match | sort-merge | the ML join (see below) |

@tbl: The join family. Use `EXISTS`/`NOT EXISTS` for existence checks rather than `IN`/`NOT IN` on a subquery: they short-circuit, and `NOT IN` returns *no rows at all* if the subquery contains a single NULL.

:::pitfall The join that multiplies your rows
```sql
SELECT o.order_id, o.total, i.sku
FROM orders o JOIN order_items i USING (order_id);
-- 1M orders, 3 items each -> 3M rows. Now:
SELECT SUM(o.total) FROM orders o JOIN order_items i USING (order_id);
-- The total is 3x too high.
```
Joining one-to-many and then aggregating the *one* side triple-counts it. The
symptom is a metric that is a suspiciously round multiple of the right answer.
Aggregate the many side first, then join.
:::

## The as-of join: the one ML needs

You have events (predictions to make) and a slowly-changing feature table.
For each event you need the feature value **as it was at that moment** --- not
the current value, which is the future.

```sql title="As-of join, portable version"
SELECT e.event_id, e.event_time, f.score
FROM events e
LEFT JOIN LATERAL (
    SELECT score
    FROM features f
    WHERE f.entity_id = e.entity_id
      AND f.valid_from <= e.event_time        -- strictly not the future
    ORDER BY f.valid_from DESC
    LIMIT 1
) f ON TRUE;
```

```sql title="DuckDB and several modern engines have it natively"
SELECT e.event_id, f.score
FROM events e
ASOF LEFT JOIN features f
  ON e.entity_id = f.entity_id AND e.event_time >= f.valid_from;
```

This single operation is the difference between a training set that reflects
reality and one that quietly contains the future. Chapter 14 builds the full
pipeline around it.

## How the engine executes your query

@fig: query_pipeline | 126 | What the engine does with your SQL. The optimiser is free to reorder joins and push predicates down; understanding which rewrites it can and cannot perform is what makes a query fast.

The optimiser's main moves:

**Predicate pushdown.** A `WHERE` filter is moved as early as possible ---
ideally into the storage layer so rows are never read. This is why a filter on
a partition column can make a query a hundred times faster and a filter on a
computed expression cannot.

**Projection pushdown.** Only the columns you reference are read. On columnar
storage this is the difference between reading 3 columns and 200.

**Join reordering.** The optimiser picks an order based on estimated
cardinalities. Bad statistics produce bad orders, which is the single most
common cause of a query that used to be fast becoming slow.

```sql title="Three rewrites that defeat the optimiser"
-- 1. A function on the column prevents index use and pushdown
WHERE DATE(event_time) = '2026-03-01'          -- bad
WHERE event_time >= '2026-03-01'
  AND event_time <  '2026-03-02'               -- good, sargable

-- 2. Implicit casts do the same
WHERE user_id = '12345'                        -- bad if user_id is BIGINT

-- 3. OR across columns often forces a full scan
WHERE a = 1 OR b = 2                           -- consider UNION of two scans
```

```sql title="Reading a plan"
EXPLAIN ANALYZE SELECT ...;
-- Look for, in order of severity:
--   Seq Scan on a big table with a selective filter -> missing index/partition
--   rows=1 (actual rows=4200000)                    -> stale statistics
--   Nested Loop with a large outer                  -> bad join order
--   Sort ... external merge Disk: 2GB               -> raise work_mem
--   Hash Join ... Batches: 64                       -> hash table spilled
```

The number to fixate on is the ratio of *estimated* to *actual* rows. A
hundredfold underestimate means every decision made downstream of it was made
on false information.

## Row storage versus columnar

| | Row store (Postgres, MySQL) | Columnar (Parquet, DuckDB, ClickHouse) |
|---|---|---|
| Layout | all of row 1, then row 2 | all of column A, then column B |
| `SELECT * WHERE id = 5` | one page read | reads every column's file |
| `SELECT AVG(x) FROM t` | reads every column of every row | reads one column |
| Compression | poor (mixed types adjacent) | excellent (like values adjacent) |
| Best for | transactions, point lookups | analytics, ML feature extraction |

@tbl: The layout decides the workload. Columnar formats compress 5--10× better because adjacent values have the same type and often similar magnitudes, which is also why dictionary and run-length encoding work so well on them.

:::insight Why ML pipelines are columnar
Feature extraction reads a few columns from hundreds, over billions of rows.
That is the exact workload columnar storage is designed for, and the speedup
over a row store is often two orders of magnitude --- it is a *bytes read*
argument, the same one as Chapter 7's.

Partitioning by date on top of that means a query for one month reads one
month's files. Partition pruning plus projection pushdown routinely turns a
2 TB scan into a 4 GB one.
:::

```python title="DuckDB: a columnar engine in your process"
import duckdb

duckdb.sql("""
    SELECT user_id,
           COUNT(*)  AS n_events,
           AVG(amount) AS avg_amount
    FROM 's3://bucket/events/year=2026/month=*/*.parquet'
    WHERE event_type = 'purchase'
    GROUP BY user_id
""").df()                       # straight to a DataFrame, no server, no copy
```

No cluster, no server, no loading step. For datasets up to a few hundred
gigabytes this beats a Spark cluster on both latency and total cost, and it is
one `pip install`. Reach for distributed compute when a single machine
genuinely cannot hold the working set --- which is a much higher bar than most
teams assume.

:::practice The task
On a dataset of at least ten million rows: (a) write a query producing a
30-day trailing average feature per entity, with the window ending strictly
before the event time; (b) write the same feature with the window *including*
the current row, train a model on each, and compare the offline metrics ---
observe the leakage; (c) write an as-of join both ways (LATERAL and native)
and compare plans; (d) take your slowest query, read `EXPLAIN ANALYZE`, find
the largest estimate/actual ratio, and fix it; (e) convert the table to
partitioned Parquet and measure the scan volume before and after.

**You have this skill when** you can write a leak-free point-in-time feature
query from memory, and when a slow query sends you to the plan rather than to
guesswork.
:::

:::exercise
1. Write a query that finds, per user, the time since their previous event and
   flags sessions with gaps over 30 minutes.
2. Demonstrate the `NOT IN` NULL trap: build a subquery containing one NULL
   and show the outer query returns zero rows.
3. † Construct the one-to-many double-counting bug on real data, show the
   inflated sum, and fix it two different ways.
4. Write an as-of join without `LATERAL` or `ASOF` (window functions only) and
   compare its plan and runtime.
5. Take a query with `DATE(col) = ...` and rewrite it sargably. Measure both.
6. † Find a query where the optimiser's row estimate is off by more than
   100×. Run `ANALYZE` and re-check. Explain what changed.
7. Store the same 10M-row table as CSV, row-store and partitioned Parquet.
   Measure size and the time for a single-column aggregate on each.
:::

:::recap
- Window functions are most of feature engineering; `ROWS` counts rows,
  `RANGE` counts time, and the window must end strictly before the prediction
  time.
- Use `EXISTS`/`NOT EXISTS` over `IN`/`NOT IN`; `NOT IN` with a NULL returns
  nothing.
- Aggregating after a one-to-many join multiplies your totals.
- The as-of join is the ML join: the feature value as of the event time, never
  the current one.
- The optimiser pushes predicates and projections down and reorders joins;
  functions on columns and implicit casts defeat it.
- In a plan, the estimated/actual row ratio is the number that matters.
- Columnar storage plus partitioning is a bytes-read optimisation, and DuckDB
  puts it in your process with no cluster.
:::
