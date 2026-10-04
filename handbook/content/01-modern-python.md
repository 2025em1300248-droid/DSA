# Modern Python for ML Engineers
@short: Modern Python
@subtitle: The language features that separate a script from a system
@tier: foundation
@prereq: none
@blurb: Most ML code is written by people who learned Python well enough to stop learning it. The features they skipped --- the data model, iterators and generators, context managers, dataclasses, the descriptor protocol --- are exactly the ones that make the difference between code that runs once and code a team can own. This chapter covers them through the problems they solve.
@objectives:
- Use the data model deliberately rather than by accident
- Write generators that process data larger than memory
- Manage resources correctly with context managers
- Choose between dataclasses, NamedTuples, TypedDicts and Pydantic models
- Recognise and avoid the four mutable-state traps that bite ML code
- Profile before optimising, and know what the profile is telling you

## The data model is the language

Python's design is unusual: almost every piece of syntax is a call to a
method you can define. `len(x)` calls `x.__len__()`. `x[i]` calls
`x.__getitem__(i)`. `for y in x` calls `x.__iter__()`. This is the *data
model*, and understanding it converts Python from a collection of special
cases into one rule applied consistently.

Here is why it matters in practice. Suppose you have a dataset of 40 million
records on disk and you want it to behave like a list.

```python title="A dataset that behaves like a built-in sequence"
import numpy as np

class MemmapDataset:
    """A dataset backed by a memory-mapped array on disk."""

    def __init__(self, path, dim):
        self._x = np.memmap(path, dtype=np.float32, mode="r").reshape(-1, dim)

    def __len__(self):
        return self._x.shape[0]

    def __getitem__(self, i):
        if isinstance(i, slice):          # slicing returns a view, not a copy
            return self._x[i]
        return self._x[i]

    def __repr__(self):
        return f"MemmapDataset(n={len(self)}, dim={self._x.shape[1]})"
```

Three methods, and now `len(ds)`, `ds[5]`, `ds[10:20]`, `for row in ds`,
`reversed(ds)` and `random.choice(ds)` all work --- because every one of them
is defined in terms of `__len__` and `__getitem__`. You did not implement
iteration; you got it. This is the payoff of the data model: implement the
protocol, inherit the ecosystem.

:::insight Protocols, not inheritance
Python's abstractions are *structural*. Anything with `__len__` and
`__getitem__` is a sequence; anything with `__iter__` is iterable; anything
with `__enter__` and `__exit__` is a context manager. PyTorch's `Dataset`
requires exactly the two methods above --- it is not magic, it is the
sequence protocol. When a library says "pass anything list-like", this is
what it means.
:::

## Iterators and generators: the memory argument

The single most common performance bug in data code is materialising a list
that did not need to exist.

```python
# Reads the whole file into memory, then builds a second list of the same size
lines = open("corpus.jsonl").readlines()
records = [json.loads(line) for line in lines]
```

For a 40 GB corpus this fails. The generator version is a one-character
change in spirit and a complete change in behaviour:

```python title="Streaming: constant memory regardless of file size"
def records(path):
    with open(path) as f:
        for line in f:                  # file objects are already iterators
            yield json.loads(line)

for rec in records("corpus.jsonl"):     # peak memory: one record
    ...
```

A generator function returns an object that computes values on demand. Each
`yield` suspends the function, preserving its entire local state, and resumes
where it left off on the next `next()` call.

@fig: generator_pipeline | 92 | A generator pipeline. Each stage pulls one item from the stage before it, so memory is the size of one item multiplied by the number of stages --- not the size of the data.

Generators compose, which is what makes them powerful:

```python title="A three-stage pipeline in constant memory"
def read(path):
    with open(path) as f:
        yield from (json.loads(l) for l in f)

def clean(recs):
    for r in recs:
        text = r["text"].strip()
        if 50 <= len(text) <= 100_000:
            yield {**r, "text": text}

def batched(it, n):
    batch = []
    for x in it:
        batch.append(x)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch

for batch in batched(clean(read("corpus.jsonl")), 256):
    train_step(batch)
```

Nothing is read until the `for` loop asks for it, and no intermediate list
ever exists. This exact pattern --- read, transform, batch --- is the shape
of every data loader you will write.

:::pitfall Generators are single-use
```python
g = records("corpus.jsonl")
n = sum(1 for _ in g)        # consumes the generator
first = next(g)              # StopIteration: it is empty now
```
A list can be iterated many times; a generator cannot. If you need two
passes, either call the generator function twice (re-reading the file) or
materialise deliberately. The bug is silent when the second pass is inside a
library: `len(list(g))` followed by passing `g` to a trainer gives you an
epoch over zero examples.
:::

## `itertools` and the standard toolkit

A surprising fraction of hand-written loops are already in the standard
library, implemented in C.

| Need | Use | Not |
|---|---|---|
| Fixed-size chunks | `itertools.batched(it, n)` (3.12+) | a manual accumulator |
| Flatten nested lists | `itertools.chain.from_iterable` | nested comprehension |
| Sliding pairs | `itertools.pairwise` | `zip(x, x[1:])` (copies) |
| Cartesian product | `itertools.product` | nested loops |
| Deduplicate, keep order | `dict.fromkeys(it)` | a set plus a list |
| Group sorted runs | `itertools.groupby` | manual state |
| Take the first *n* | `itertools.islice(it, n)` | `list(it)[:n]` |
| Count occurrences | `collections.Counter` | a manual dict |
| Fixed-size history | `collections.deque(maxlen=k)` | list plus `pop(0)` |

@tbl: The right-hand column is not merely uglier --- several entries are asymptotically worse. `list(it)[:n]` consumes the entire iterator; `list.pop(0)` is $O(n)$ per call, making a rolling window $O(n^2)$.

## Context managers: the resource problem

Anything you open must be closed, including on the exception path. The
`with` statement guarantees this, and writing your own is four lines.

```python title="A context manager for timed, labelled sections"
import time
from contextlib import contextmanager

@contextmanager
def timed(label):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - t0:.3f}s")

with timed("forward"):
    out = model(batch)
```

The `try/finally` is the whole point: the timing prints even if the forward
pass raises. Without it, an exception skips your cleanup and you leak a file
handle, a CUDA stream, a database connection or a lock.

:::ml Context managers you will meet constantly
`torch.no_grad()` disables gradient tracking. `torch.autocast("cuda")`
switches to mixed precision. `model.eval()` is *not* one, which is exactly
why people forget to switch back --- a recurring evaluation bug. Wrap it:
```python
@contextmanager
def evaluating(model):
    was_training = model.training
    model.eval()
    try:
        yield model
    finally:
        model.train(was_training)
```
:::

## Structuring data: four options and when to use each

ML code moves records around constantly. Python gives you four reasonable
containers and one bad habit.

```python title="The same record, four ways"
from dataclasses import dataclass, field
from typing import NamedTuple, TypedDict
from pydantic import BaseModel

# 1. The bad habit: a bare dict
rec = {"id": "a1", "text": "hello", "score": 0.9}   # no schema, no checking

# 2. NamedTuple — immutable, tuple-compatible, tiny
class Row(NamedTuple):
    id: str
    text: str
    score: float = 0.0

# 3. dataclass — mutable, the default choice for internal objects
@dataclass(slots=True)
class Example:
    id: str
    text: str
    score: float = 0.0
    tags: list[str] = field(default_factory=list)   # never `tags: list = []`

# 4. Pydantic — validates and coerces at the boundary
class Request(BaseModel):
    id: str
    text: str
    score: float = 0.0
```

| Container | Mutable | Validates | Cost | Use for |
|---|---|---|---|---|
| `dict` | yes | no | lowest | genuinely dynamic keys only |
| `NamedTuple` | no | no | very low | small records, tuple unpacking |
| `dataclass(slots=True)` | yes | no | low | internal objects, the default |
| `TypedDict` | yes | static only | none | typing an existing dict shape |
| Pydantic `BaseModel` | yes | at runtime | ~5–20µs | anything crossing a boundary |

@tbl: Choosing a container. The rule: Pydantic at every boundary (API request, config file, LLM output), dataclasses inside. Validation at the edge means the interior can trust its inputs.

:::pitfall The mutable default argument
```python
def add_tag(tags=[]):        # evaluated ONCE, at definition time
    tags.append("x")
    return tags

add_tag()   # ['x']
add_tag()   # ['x', 'x']  ← shared across every call
```
The same trap appears in dataclasses (`tags: list = []` is a `ValueError` in
modern Python precisely because of this) and in class attributes. Use
`None` plus a check, or `field(default_factory=list)`.
:::

## Equality, hashing and identity

Three distinct notions that people conflate, with a real consequence in
caching code.

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b        # True  — equal contents (__eq__)
a is b        # False — different objects (identity)
hash(a)       # TypeError — lists are unhashable because they are mutable
```

The rule that matters: **objects used as dict keys or set members must have
`__hash__` consistent with `__eq__`, and must not change while stored.**
`@dataclass(frozen=True)` gives you both correctly; a plain `@dataclass` gives
you `__eq__` and sets `__hash__ = None`, making it unhashable --- which is the
right default, because a mutable key is a bug waiting to happen.

:::warning Floating-point keys
`hash(0.1 + 0.2) != hash(0.3)` because `0.1 + 0.2 == 0.30000000000000004`.
Never key a cache on a computed float. Round to a fixed number of decimals
and key on the string, or quantise to an integer.
:::

## Where Python is slow, and what to do

Python's interpreter overhead is roughly 50–100× a compiled
language per operation. This matters far less than people assume, because in
ML code almost all the time is inside NumPy, PyTorch or a database --- all
compiled. It matters enormously in the places where it does apply: per-row
loops over data.

```python title="Three ways to normalise a million rows"
import numpy as np
x = np.random.randn(1_000_000, 64).astype(np.float32)

# 1. Python loop:                ~4.0 s
out = np.empty_like(x)
for i in range(len(x)):
    out[i] = x[i] / np.linalg.norm(x[i])

# 2. Vectorised:                 ~0.09 s   (45x)
out = x / np.linalg.norm(x, axis=1, keepdims=True)

# 3. Vectorised, in place:       ~0.05 s   (80x, and half the memory)
np.divide(x, np.linalg.norm(x, axis=1, keepdims=True), out=x)
```

The rule is not "never write a loop". It is: **the loop body should do a lot
of work.** A loop over 1000 batches is fine; a loop over 40 million rows is
not.

:::perf Profile before you optimise, every time
```bash
python -m cProfile -o prof.out train.py
python -c "import pstats; pstats.Stats('prof.out').sort_stats('cumtime').print_stats(20)"
```
Better still, `py-spy top --pid <pid>` attaches to a running process with no
code changes and no restart, which is the only practical option for a job
that has been training for six hours. The profile is almost never where you
guessed --- in ML code it is usually data loading, tokenisation, or a
`.cpu()` call forcing a GPU synchronisation inside a loop.
:::

## The features worth adopting immediately

```python title="Modern Python that is worth the habit change"
# Structural pattern matching (3.10+) — clean dispatch on shape
match response:
    case {"type": "tool_call", "name": str(name), "args": dict(args)}:
        run_tool(name, args)
    case {"type": "text", "content": str(text)}:
        emit(text)
    case _:
        raise ValueError(f"unknown response: {response}")

# The walrus operator — compute once, test, and keep
while (chunk := stream.read(8192)):
    process(chunk)

# f-string debugging (3.8+) — prints "loss=0.3412"
print(f"{loss=:.4f}")

# Built-in generics (3.9+) — no typing.List, no typing.Dict
def top_k(scores: dict[str, float], k: int) -> list[tuple[str, float]]: ...

# The union operator (3.10+)
def load(path: str | Path, dtype: np.dtype | None = None) -> np.ndarray: ...

# pathlib over os.path, always
from pathlib import Path
for p in Path("data").rglob("*.jsonl"):
    print(p.stem, p.stat().st_size)
```

:::practice The task
Take a script you have written that loads data with `pd.read_csv` and loops
over rows with `iterrows`. Rewrite it three ways: (a) as a generator pipeline
that never holds more than one batch, (b) vectorised with NumPy, (c) using
Polars' lazy API. Time all three on a file of at least a million rows and
write down the ratios. Then rewrite the record type as a frozen dataclass and
observe what `slots=True` does to memory (`sys.getsizeof` plus
`pympler.asizeof`).

**You have this skill when** you can take an arbitrary row-wise script and
state, before running it, which of the three rewrites will help and by roughly
how much.
:::

:::exercise
1. Implement `MemmapDataset.__iter__` explicitly and explain why the class
   works with `for` even without it.
2. Write a generator that yields fixed-size token blocks from a stream of
   variable-length documents, packing documents end to end with a separator
   --- the standard pre-training data format. Handle the final partial block.
3. † Implement `chunked_shuffle(it, buffer)` which yields items in
   approximately random order using a fixed-size reservoir, then measure how
   far the output is from uniform for buffer sizes 10, 1000 and 100000.
4. Write a context manager `temporary_seed(seed)` that sets Python, NumPy and
   PyTorch seeds and restores all three states on exit. Prove it restores
   them.
5. † Construct a case where `@dataclass(frozen=True)` objects used as
   dict keys silently misbehave because one field is a NumPy array. Explain
   and fix.
6. Profile a training script with `py-spy` and produce a flame graph. Identify
   the top three costs and state which are Python-bound and which are not.
7. Show that `itertools.islice(gen, 5)` consumes exactly five items from
   `gen`, and that `list(gen)[:5]` consumes all of them.
:::

:::recap
- The data model is one rule applied uniformly: implement the protocol and
  the ecosystem works with your object.
- Generators give constant memory and compose into pipelines; they are
  single-use, which is the bug to watch for.
- `itertools` and `collections` replace most hand-written loops, sometimes
  changing the asymptotics.
- Context managers exist for the exception path; that is the entire point.
- Pydantic at the boundary, dataclasses inside, `NamedTuple` for small
  immutable records, bare dicts almost never.
- `__hash__` must agree with `__eq__` and must not change while the object is
  stored; never key on a computed float.
- Python is slow per operation and irrelevant when the loop body is large;
  profile with `cProfile` or `py-spy` before changing anything.
:::
