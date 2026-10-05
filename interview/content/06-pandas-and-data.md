# Pandas, NumPy and Looking at Data
@short: Pandas and Data
@subtitle: The round where a live task catches people out
@tier: foundation
@prereq: none
@blurb: Your resume lists all of this, and it is the easiest place to be caught by a practical task. The two answers that matter most are the one about data leakage and the one about your own imputation choice --- both show whether you actually looked at your data or just ran code on it.
@objectives:
- Handle missing values with a reason, not a reflex
- Explain why vectorised code is faster in one sentence
- Describe your own EDA as an ordered process
- Spot data leakage before it reaches a model

## The basics

#### Q8.1 — DataFrame vs Series?
A Series is one column with labels. A DataFrame is a whole table made of
Series side by side.

#### Q8.2 — `loc` vs `iloc`?
`loc` picks by name — "give me the row called 'Mumbai'". `iloc` picks by
position — "give me the third row".

#### Q8.3 — How do you handle missing values?
First count them: `df.isna().sum()`. Then choose per column.

Drop the rows if there are very few. Fill them in if there are more — use the
middle value for skewed numbers, the most common value or an explicit
"Unknown" for categories. And if **being missing is itself informative**, add
a separate column recording that it was missing, because that fact may be the
signal.

#### Q8.4 — Which imputation did you use on the churn data, and why?
Be specific here — it's a good question for you. In that dataset, the
`TotalCharges` field is blank for brand-new customers who've been there zero
months. Those aren't randomly missing values; they're genuinely zero.

Knowing that detail is strong evidence you actually opened the data instead
of just running `fillna`.

#### Q8.5 — `merge` vs `join` vs `concat`?
`merge` combines two tables on matching columns, like SQL. `join` does the
same but on the row labels. `concat` just stacks tables on top of each other
or side by side.

#### Q8.6 — What does `groupby` do?
Split the rows into groups, do something to each group, put the answers back
together. `df.groupby('contract')['churn'].mean()` gives you the churn rate
for each contract type.

#### Q8.7 — `apply` vs vectorised operations?
`apply` runs your function once per row in Python, which is slow. A vectorised
operation hands the whole column to compiled code that does it in one go —
often fifty to a hundred times faster.

The rule: if you're writing `apply` on a big table, there's almost always a
built-in way that's much faster.

#### Q8.8 — What is a pivot table in pandas?
A cross-tabulation — rows down one side, categories across the top, a
calculation in each cell. `df.pivot_table(index=..., columns=...,
values=..., aggfunc=...)`.

#### Q8.9 — How do you find and drop duplicates?
`df.duplicated().sum()` to count them, `df.drop_duplicates()` to remove them.

#### Q8.10 — What does `df.describe()` give you, and what does it hide?
Count, average, spread, minimum, maximum and the quartiles for your number
columns.

What it hides matters more: it skips the text columns entirely, it tells you
nothing about where the missing values are, and it says nothing about the
**shape** of the data. Two completely different distributions can have the
same average and spread. Always plot as well.

## NumPy

#### Q8.11 — What is a NumPy array, and why is it faster than a list?
A solid block of memory where every item is the same type. That lets the
operation run in compiled code across the whole block, rather than Python
looping over items one at a time.

#### Q8.12 — What is broadcasting?
NumPy automatically stretching a smaller array to match a bigger one so the
shapes line up. Subtracting one row of averages from a whole table works
without you writing a loop.

#### Q8.13 — `reshape` vs `ravel` vs `transpose`?
`reshape` changes the dimensions, `ravel` flattens everything into one long
line, `transpose` swaps the axes round. Usually none of them copies the data —
you get a different view of the same memory.

#### Q8.14 — View vs copy in NumPy — why does it matter?
A view shares the same memory as the original. So if you change the view, you
have silently changed the original too.

That's a real source of bugs. Use `.copy()` when you actually mean to make an
independent one.

## Looking at the data

#### Q8.15 — What steps does your EDA actually follow?
Have an ordered answer ready — it's much better than listing plot types.

Shape and column types first. Then where the missing values are. Then how
balanced the target is. Then the distribution of each column on its own. Then
how each column relates to the target. Then outliers and a leakage check.

#### Q8.16 — Which plot for which question?
Histogram for the shape of one column. Box plot for spread and outliers.
Scatter for two numbers against each other. Bar chart for counting categories.
Heatmap for a grid of correlations. Line for anything over time.

#### Q8.17 — What is data leakage, and how do you catch it?
When information that wouldn't be available at prediction time sneaks into
training. The model scores brilliantly in testing and then fails completely in
the real world, because in the real world that information doesn't exist yet.

Catch it by asking of every single column: **would I actually know this
before the thing I'm predicting happens?** And by fitting your scalers and
encoders inside each training fold, not on the whole dataset before splitting.

#### Q8.18 — How do you encode categorical variables?
One-hot when there are only a few categories — one yes/no column each.
Ordinal numbering when the order is real, like small/medium/large. For
categories with hundreds of values, replace each with a summary number — but
fit that inside the training fold or you've just leaked the answer.

#### Q8.19 — Why scale features? Which models need it?
Because some models measure distance, and a column in rupees will dominate a
column measured 0 to 1 purely because the numbers are bigger.

Needed by: SVM, KNN, k-means, logistic regression, neural networks. Not needed
by trees and random forests — they only care about the order of values, not
the size.

#### Q8.20 — Standardisation vs normalisation?
Standardisation shifts and stretches so the average is 0 and the spread is 1.
Normalisation squashes everything into a fixed range, usually 0 to 1.

Standardise when the method expects roughly bell-shaped inputs. Normalise when
you need a hard range.

:::practice The leakage habit
Take the churn dataset and go column by column asking "would I know this
before the customer churned?" Write down any column where the answer is no or
unclear. That is the habit the question in Q8.17 is testing for, and doing it
once makes the answer sound lived rather than learned.
:::

:::recap
- Missing values deserve a reason per column, and "it's missing" can itself be
  a signal.
- Your `TotalCharges` answer is a genuinely strong one — it proves you looked.
- `apply` loops in Python; vectorised operations don't, which is the whole
  speed difference.
- A NumPy view shares memory with the original — changing it changes both.
- Describe your EDA as an ordered process, not a list of charts.
- Leakage is the one that fails a model in production; ask "would I know this
  yet?" of every column.
:::
