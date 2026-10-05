# SQL, C++ and MongoDB
@short: SQL, C++, Mongo
@subtitle: The database round, and the language you listed
@tier: foundation
@prereq: none
@blurb: Almost every data or ML interview includes a live SQL question, so practise writing it rather than recognising it. C++ and MongoDB are on your resume, which makes them fair game --- keep those answers short and do not overclaim depth.
@objectives:
- Write the common SQL patterns without looking them up
- Explain joins, grouping and window functions in plain words
- Answer C++ questions honestly without inflating your experience
- Say when you would pick MongoDB over a normal database

## SQL: the basics

#### Q4.1 — What are the main join types?
A join glues two tables together on a matching column.

**Inner** keeps only rows that exist in both. **Left** keeps everything from
the left table, filling blanks where there's no match. **Right** does the
same from the other side. **Full outer** keeps everything from both. **Cross**
pairs every row with every row, which is almost never what you want.

#### Q4.2 — `WHERE` vs `HAVING`?
`WHERE` filters individual rows before they're grouped. `HAVING` filters the
groups after they've been totalled up. "Only customers in Mumbai" is `WHERE`;
"only groups with more than five orders" is `HAVING`.

#### Q4.3 — What does `GROUP BY` do?
Squashes all the rows that share a value into one row, so you can total or
average over each group. One row per contract type, say, instead of one row
per customer.

#### Q4.4 — Name the aggregate functions.
`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. One catch: `COUNT(column)` skips blanks,
`COUNT(*)` counts every row.

#### Q4.5 — `DELETE` vs `TRUNCATE` vs `DROP`?
`DELETE` removes the rows you pick and can be undone. `TRUNCATE` empties the
whole table quickly. `DROP` removes the table itself.

#### Q4.6 — Primary key vs unique key?
Both stop duplicates. A primary key can never be blank and there's only one
per table. A unique key can be blank and you can have several.

#### Q4.7 — What is a foreign key?
A column pointing at another table's primary key. It stops you from, say,
creating an order for a customer who doesn't exist.

#### Q4.8 — What is an index, and what does it cost?
Like the index at the back of a book — it lets the database find rows without
reading every page. The cost is that writing becomes slower and it takes up
space, so you don't index everything.

#### Q4.9 — Clustered vs non-clustered index?
A clustered index decides the actual physical order the rows are stored in, so
there's only one. A non-clustered index is a separate lookup list pointing at
the rows.

#### Q4.10 — `UNION` vs `UNION ALL`?
`UNION` stacks two result sets and removes duplicates, which means it has to
sort. `UNION ALL` just stacks them and is faster. Use `ALL` unless you
actually need the deduplication.

#### Q4.11 — Subquery vs CTE?
Both are a query nested inside another. A CTE — the `WITH x AS (...)` form —
gets a name, so it's readable and you can refer to it more than once.

## SQL: the parts that get asked live

#### Q4.12 — What are window functions?
Calculations across a group of rows that **don't** collapse them into one row.
So you can show each employee alongside their rank in their department, with
every employee still listed.

`ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)`.

#### Q4.13 — `ROW_NUMBER` vs `RANK` vs `DENSE_RANK`?
With a tie: `ROW_NUMBER` gives 1, 2, 3 — it just numbers them. `RANK` gives
1, 1, 3 — ties share a place and then it skips. `DENSE_RANK` gives 1, 1, 2 —
ties share and it doesn't skip.

#### Q4.14 — Find the second-highest salary.
`SELECT MAX(salary) FROM emp WHERE salary < (SELECT MAX(salary) FROM emp)`.
Or use `DENSE_RANK() = 2`, which handles ties the way most people mean.

#### Q4.15 — Find duplicate rows.
`SELECT col, COUNT(*) FROM t GROUP BY col HAVING COUNT(*) > 1`. Group by the
thing, keep the groups bigger than one.

#### Q4.16 — How do you handle blanks (NULLs)?
Test them with `IS NULL` or `IS NOT NULL`. Replace them with
`COALESCE(col, 0)`.

The trap: a blank is not equal to anything, including another blank. So
`NULL = NULL` is not true, which is why you can't use `=` to test for it.

#### Q4.17 — What is normalisation? Name the first three forms.
Splitting data across tables so nothing is stored twice. First form: one value
per cell, no lists crammed into a field. Second: every column depends on the
whole key, not part of it. Third: no column depends on another non-key column.

#### Q4.18 — When would you denormalise?
When you read far more than you write, and joining tables every time costs
more than storing a bit of duplicate data. Common in analytics.

#### Q4.19 — What are ACID properties?
The four guarantees a database gives a transaction: it either fully happens or
not at all, it leaves the data valid, parallel transactions don't corrupt each
other, and once it's confirmed it survives a crash.

#### Q4.20 — What does `EXPLAIN` tell you?
The plan the database is about to follow — which indexes it'll use, what order
it'll join in, how many rows it expects. It's the first thing you look at when
a query is slow.

#### Q4.21 — `DISTINCT` vs `GROUP BY`?
Both remove duplicates. `GROUP BY` also lets you calculate something per
group, which `DISTINCT` can't.

#### Q4.22 — Get the churn rate by contract type from your telecom table.
```sql
SELECT contract,
       AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0 END) AS rate
FROM customers
GROUP BY contract
ORDER BY rate DESC;
```
Expect a resume-linked question exactly like this. The trick is turning
Yes/No into 1/0 so you can average it.

## C++

#### Q5.1 — Why is C++ used in ML at all?
Speed and control. PyTorch, OpenCV and the YOLO runtimes are all C++
underneath, with Python wrappers on top. You write Python; C++ does the work.

#### Q5.2 — C vs C++?
C++ adds classes, templates, exceptions and a big standard library on top of
C's simpler procedural core.

#### Q5.3 — What is a pointer? What is a reference?
A pointer holds the address of something. You can point it somewhere else, or
at nothing. A reference is another name for an existing thing — it's attached
once and can never be empty.

#### Q5.4 — Stack vs heap?
Stack memory is handled for you and disappears when the function ends — fast
and small. Heap memory you ask for and must give back yourself — bigger, and
it lasts until you release it.

#### Q5.5 — What causes a memory leak, and how do you avoid it?
Asking for heap memory and never giving it back. Avoid it by using smart
pointers, which release the memory automatically when nothing needs it any
more.

#### Q5.6 — What is RAII?
Tying a resource's lifetime to an object. When the object goes out of scope,
its cleanup runs automatically — so a file gets closed or memory gets freed
without you remembering to do it.

#### Q5.7 — What is the STL?
The standard library of ready-made containers (`vector`, `map`, `set`) and
algorithms (`sort`, `find`), so you aren't writing those yourself.

#### Q5.8 — `vector` vs array?
A vector grows and shrinks as you add things. A plain array is a fixed size
decided up front.

#### Q5.9 — `map` vs `unordered_map`?
`map` keeps things sorted and lookups take slightly longer.
`unordered_map` is a hash table — no order, but lookups are instant.

#### Q5.10 — Overloading vs overriding?
Overloading: several functions with the same name but different arguments,
and the compiler picks. Overriding: a child class replaces a method it
inherited, and the choice happens while the program runs.

#### Q5.11 — What is a virtual function?
A method where the version that runs is decided by what the object actually
is, not by what type the variable claims to be. It's what makes polymorphism
work.

#### Q5.12 — What are templates?
A way to write one function or class that works for any type, so you don't
write the same thing again for `int`, `float` and everything else.

#### Q5.13 — Pass by value vs by reference?
By value copies the whole argument. By reference hands over the original, so
nothing gets copied. Use a `const` reference for big things you only need to
read.

:::warning Keep the C++ answers short
You listed it, so you must be able to answer. But do not volunteer depth you
do not have. "I'm comfortable reading it and writing algorithmic code; I
haven't shipped a C++ system" closes the topic cleanly and honestly.
:::

## MongoDB

#### Q6.1 — What is MongoDB?
A database that stores documents instead of rows. Each document is basically a
JSON object, and two documents in the same place don't have to have the same
fields.

#### Q6.2 — SQL vs MongoDB — when do you pick which?
A normal database when your data is structured, has real relationships, and
you need those relationships enforced. MongoDB when your data is nested or its
shape keeps changing, or when you need to spread it across many machines.

Pick by the shape of your data, not by which one sounds more modern.

#### Q6.3 — Map the vocabulary: table, row, column?
Collection, document, field.

#### Q6.4 — What is BSON?
MongoDB's storage format — basically JSON in a binary form, with extra types
JSON doesn't have, like proper dates.

#### Q6.5 — What is `_id`?
The unique identifier every document must have. If you don't supply one,
MongoDB generates one.

#### Q6.6 — How do you query documents?
`db.users.find({ city: "Mumbai" })`. You pass a second argument if you only
want some of the fields back.

#### Q6.7 — What is the aggregation pipeline?
A series of stages that reshape your data step by step — filter, group, sort,
rename. It's MongoDB's version of `GROUP BY` and joins.

#### Q6.8 — Does MongoDB support joins?
Yes, with `$lookup` inside an aggregation, but it's heavier than a normal
database join. Often you nest the data inside the document instead.

#### Q6.9 — Embedding vs referencing?
Embed the child data inside the parent when you always read them together and
it stays small. Point at it from outside when it's large, shared by several
parents, or keeps growing.

#### Q6.10 — What is sharding? What is replication?
Sharding splits your data across several machines so you can hold more than
one machine can. Replication keeps copies on other machines so you don't lose
anything if one dies.

#### Q6.11 — Does MongoDB have transactions?
Yes, across multiple documents since version 4.0. A write to a single document
was always all-or-nothing anyway.

#### Q6.12 — What is indexing in MongoDB?
Same idea as SQL — a lookup structure that makes searches fast.
`db.c.createIndex({ email: 1 })`, and `.explain()` to check it's being used.

#### Q6.13 — What is the CAP theorem, and where does MongoDB sit?
When the network between your machines breaks, you have to choose: keep every
machine giving the same answer, or keep every machine answering at all. You
can't have both.

MongoDB chooses consistency by default — it would rather refuse than give you
stale data. You can tune that per query.

:::recap
- A join combines tables; `WHERE` filters rows, `HAVING` filters groups.
- Window functions calculate across rows without collapsing them — the most
  likely live SQL question.
- `NULL` is never equal to anything, including `NULL`.
- Keep C++ answers short and honest: reading and algorithms, not production.
- Pick MongoDB for nested or changing data shapes, not because it sounds
  modern.
:::
