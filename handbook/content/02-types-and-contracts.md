# Types, Contracts and Validation
@short: Types and Contracts
@subtitle: Making the shape of your data a fact rather than a hope
@tier: foundation
@prereq: Chapter 1
@blurb: ML code fails in a characteristic way: something has the wrong shape, the wrong dtype, or a missing key, and you find out four hours into a training run. Type annotations, runtime validation and shape contracts move those failures to the moment they are introduced. This chapter shows where each tool belongs and where it does not.
@objectives:
- Annotate code so a type checker catches real bugs, not decorate it
- Validate at system boundaries with Pydantic and trust the interior
- Encode tensor shape contracts so mismatches fail immediately
- Use `Protocol` for structural typing instead of inheritance hierarchies
- Know the specific limits of static typing in numerical code

## The failure this prevents

```python
def train(config):
    for epoch in range(config["epochs"]):
        ...
        if epoch % config["eval_every"] == 0:      # KeyError, 3 hours in
            evaluate(model)
```

The config came from a YAML file. Someone renamed `eval_every` to
`eval_interval` in one of four config files. Nothing caught it, because a
dict has no shape. Three GPU-hours are gone.

Every tool in this chapter exists to convert that class of runtime surprise
into an error at the earliest possible moment: at edit time (the type
checker), at start-up (validation), or at the first tensor operation (shape
contracts).

@fig: validation_boundary | 126 | Validate once, at the boundary. Everything inside the boundary works with typed objects whose invariants are already guaranteed, so interior functions need no defensive checks.

## Annotations that earn their keep

An annotation is worth writing when it removes ambiguity a reader would
otherwise have to resolve by reading the implementation.

```python title="Annotations that carry information"
from collections.abc import Iterable, Iterator, Callable
from pathlib import Path

def load_shards(root: Path, pattern: str = "*.parquet") -> Iterator[Path]:
    """Yields shard paths in deterministic order."""
    yield from sorted(root.rglob(pattern))

def topk(
    scores: dict[str, float],
    k: int = 10,
    key: Callable[[float], float] = lambda s: s,
) -> list[tuple[str, float]]:
    ...

# Accept the widest type you can use; return the narrowest you can promise.
def mean(xs: Iterable[float]) -> float: ...        # not list[float]
def shards(root: Path) -> list[Path]: ...          # not Iterable[Path]
```

That last rule --- **accept broadly, return narrowly** --- is the one that
makes annotated code pleasant rather than restrictive. A function taking
`Iterable[float]` works with a list, a generator, a NumPy array or a set. A
function returning `list[Path]` lets the caller index and re-iterate.

| Annotation | Means | Use when |
|---|---|---|
| `list[str]` | a list, mutable, re-iterable | you return one |
| `Sequence[str]` | indexable, sized, not mutated | you accept one and only read |
| `Iterable[str]` | can be iterated once | you accept and consume |
| `Iterator[str]` | a generator or iterator | you return a lazy stream |
| `Mapping[str, int]` | read-only dict-like | you accept and only look up |
| `str \| None` | optional | absence is meaningful |
| `Any` | checking disabled | genuinely dynamic, rare |

@tbl: Choosing a collection annotation. `Any` silently disables checking for everything it touches, including downstream --- reach for it only when the alternative is a lie.

:::pitfall `Optional` is not a default
```python
def f(x: str | None) -> int:
    return len(x)          # type checker: "str | None" has no len
```
The annotation is correct and the code is wrong: you must handle the `None`.
This is the single highest-value thing a type checker does --- roughly a
third of the real bugs it finds in ML code are unguarded `None`s from
functions that return "the result, or nothing".
:::

## Running the checker

Annotations do nothing unless something reads them.

```toml title="pyproject.toml — a strictness ratchet that works"
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = false          # start permissive
exclude = ["notebooks/"]

[[tool.mypy.overrides]]
module = "mypackage.core.*"            # then ratchet, module by module
disallow_untyped_defs = true
strict_equality = true
```

The ratchet matters. Turning on `--strict` across an existing codebase
produces four thousand errors and gets switched off within a week. Turning it
on for one module, fixing those, and adding the next module is a process that
finishes. `pyright` (the checker behind most editors) is faster and stricter
about inference; `mypy` has broader library support. Either is fine; running
neither is not.

## Validation at the boundary

Static typing checks your code. It cannot check *data* --- a JSON payload, a
YAML config, an LLM response. That needs runtime validation.

```python title="A config that cannot be silently wrong"
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class TrainConfig(BaseModel):
    model_config = {"extra": "forbid"}        # unknown keys are an error

    model_name: str
    epochs: int = Field(ge=1, le=1000)
    lr: float = Field(gt=0, lt=1)
    batch_size: int = Field(ge=1)
    precision: Literal["fp32", "bf16", "fp16"] = "bf16"
    eval_every: int = Field(default=500, ge=1)

    @field_validator("batch_size")
    @classmethod
    def power_of_two(cls, v: int) -> int:
        if v & (v - 1):
            raise ValueError(f"batch_size must be a power of 2, got {v}")
        return v

cfg = TrainConfig(**yaml.safe_load(open("config.yaml")))
```

`extra="forbid"` is the line that would have caught the renamed key. With it,
the typo fails in the first second of the run with a message naming the
offending field. Without it, Pydantic silently ignores unknown keys, which is
the same failure as the bare dict with extra ceremony.

:::insight Where the boundary is
Draw the boundary at every place data enters your process from somewhere you
do not control: HTTP request bodies, config files, command-line arguments,
database rows, message-queue payloads, and --- increasingly the important one
--- model output. Validate there, once. Inside the boundary, functions take
typed objects and do not re-check, because re-checking everywhere is how
codebases acquire a defensive-programming tax that nobody can remove later.
:::

```python title="Validating an LLM's structured output"
class Extraction(BaseModel):
    invoice_number: str = Field(pattern=r"^INV-\d{6}$")
    total: float = Field(ge=0)
    currency: Literal["USD", "EUR", "GBP"]
    line_items: list[str] = Field(min_length=1)

def extract(text: str, retries: int = 2) -> Extraction:
    for attempt in range(retries + 1):
        raw = call_model(EXTRACT_PROMPT.format(text=text))
        try:
            return Extraction.model_validate_json(raw)
        except ValidationError as e:
            if attempt == retries:
                raise
            # Feed the error back: models correct their own schema errors well
            text = f"{text}\n\nPrevious attempt was invalid:\n{e}"
    raise AssertionError("unreachable")
```

This pattern --- validate, and on failure hand the validation error back to
the model --- typically takes schema validity from about 85% to above
99%, and it is three lines. Chapter 32 develops it properly.

## Shape contracts

Python's type system cannot express "a tensor of shape (batch, seq, dim)",
which is the single most common source of bugs in model code. So encode it
another way.

```python title="Shape assertions as executable documentation"
def attention(q, k, v, mask=None):
    """
    q, k, v : (B, H, T, D)
    mask    : (B, 1, T, T) or None
    returns : (B, H, T, D)
    """
    B, H, T, D = q.shape
    assert k.shape == (B, H, T, D), f"k {tuple(k.shape)} != q {(B,H,T,D)}"
    assert v.shape == (B, H, T, D), f"v {tuple(v.shape)} != q {(B,H,T,D)}"

    scores = (q @ k.transpose(-2, -1)) / D**0.5       # (B, H, T, T)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))
    out = torch.softmax(scores, dim=-1) @ v            # (B, H, T, D)

    assert out.shape == (B, H, T, D)
    return out
```

Three conventions do most of the work: **a docstring stating every shape**, a
**trailing comment on every line that changes a shape**, and **assertions at
entry and exit**. Cost: microseconds. Benefit: a broadcast bug that would
otherwise train silently to a bad loss fails on the first batch with a message
that names the mismatch.

:::warning Broadcasting hides shape bugs
```python
loss = ((pred - target) ** 2).mean()
# pred:   (32, 1)
# target: (32,)
# pred - target broadcasts to (32, 32) — a silent 32x error, no exception
```
This is the most expensive bug in this book. NumPy and PyTorch will
cheerfully broadcast a column against a row. The fix is mechanical: assert
`pred.shape == target.shape` before every loss computation. Do it everywhere.
:::

For stronger guarantees, `jaxtyping` puts shapes in the annotations and
checks them at runtime:

```python
from jaxtyping import Float, Int, jaxtyped
from typeguard import typechecked

@jaxtyped(typechecker=typechecked)
def attention(
    q: Float[Tensor, "b h t d"],
    k: Float[Tensor, "b h t d"],
    v: Float[Tensor, "b h t d"],
) -> Float[Tensor, "b h t d"]:
    ...
```

The named dimensions must be consistent across arguments, so passing a `k`
with a different sequence length fails immediately with a clear message.

## `Protocol`: structural typing

You often want "anything with these methods" without forcing callers to
inherit from your base class.

```python title="A retriever interface that third-party code can satisfy"
from typing import Protocol, runtime_checkable

@runtime_checkable
class Retriever(Protocol):
    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]: ...

class BM25(...):      # no inheritance from Retriever
    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]: ...

def rerank(r: Retriever, query: str) -> list[str]:   # accepts BM25 fine
    ...
```

This is the right shape for plug-in points: your users implement a method,
not a class hierarchy, and the checker still verifies the signature. It is
also how you type third-party objects you do not own.

:::practice The task
Take a training script of yours with a dict-based config. (a) Replace the
config with a Pydantic model using `extra="forbid"`, range constraints and at
least one custom validator. (b) Add mypy in permissive mode and fix the
errors in one module. (c) Add shape docstrings, per-line shape comments and
entry/exit assertions to your model's forward pass. (d) Deliberately
introduce a broadcasting bug and confirm your assertions catch it.

**You have this skill when** a config typo fails in the first second with a
message naming the field, and a shape bug fails on the first batch rather
than at the end of the epoch.
:::

:::exercise
1. Write annotations for a function that takes any iterable of records and
   returns a dict from string id to a list of floats. Justify each choice
   against the accept-broadly/return-narrowly rule.
2. Find a real `None`-related bug in your own code by running mypy over one
   module with `--strict-optional`.
3. † Write a Pydantic model for a nested config (optimiser, scheduler,
   data, logging) where the scheduler's valid fields depend on its `type`.
   Use a discriminated union.
4. Construct three shapes for `pred` and `target` where the MSE silently
   broadcasts, and compute the wrong value each produces.
5. Convert an abstract base class in your code to a `Protocol` and show that
   an unrelated class satisfies it.
6. † Add `jaxtyping` to one model file. Report how many latent shape
   inconsistencies it surfaced and how long the checks cost per step.
7. Explain why `extra="forbid"` is the correct default for configs but the
   wrong default for API request models you must keep backwards-compatible.
:::

:::recap
- Annotations pay for themselves when they remove ambiguity: accept broadly,
  return narrowly, and avoid `Any`.
- Run a checker, and ratchet strictness module by module rather than
  switching on `--strict` and giving up.
- Validate data at every boundary with Pydantic; `extra="forbid"` catches the
  renamed-key class of bug outright.
- Inside the boundary, trust the types --- do not re-validate everywhere.
- Shapes are not expressible in Python's type system: use docstrings,
  per-line comments and entry/exit assertions, or `jaxtyping` for real checks.
- Silent broadcasting between `(n, 1)` and `(n,)` is the most expensive
  routine bug in numerical code; assert shape equality before every loss.
- `Protocol` gives structural typing for plug-in points without inheritance.
:::
