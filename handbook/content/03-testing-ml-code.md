# Testing Machine Learning Code
@short: Testing ML Code
@subtitle: What to assert when the output is a probability distribution
@tier: foundation
@prereq: Chapter 2
@blurb: "You cannot test ML code because the output is stochastic" is false, and believing it is why so much ML code has no tests. The stochastic part is one thin layer; everything around it --- data handling, shapes, invariants, serialisation, serving --- is ordinary software and tests exactly like ordinary software. This chapter shows what to assert at each layer.
@objectives:
- Test data transformations, which is where most real bugs are
- Write model tests that are deterministic and fast
- Use the four ML-specific test patterns: overfit-one-batch, invariance, gradient, serialisation
- Build fixtures that make tests fast enough to run on every commit
- Separate tests from evaluation, which are different things

## The layers, and what is testable at each

@fig: ml_test_pyramid | 142 | The ML testing pyramid. The base is ordinary software with ordinary tests; only the thin apex is stochastic, and even that has deterministic properties worth asserting.

| Layer | Example | Deterministic? | Test style |
|---|---|---|---|
| Data transforms | tokenise, normalise, join | yes | ordinary unit tests |
| Feature logic | windows, aggregations | yes | unit + property tests |
| Model plumbing | shapes, masks, dtypes | yes | unit tests, fixed seed |
| Training step | loss decreases | yes given a seed | smoke tests |
| Learned behaviour | accuracy on a set | no | *evaluation*, not tests |
| Serving | latency, schema, errors | yes | integration tests |

@tbl: Only one row is genuinely untestable in the unit-test sense --- and it is not a test, it is evaluation (Chapter 37). Everything else is normal.

:::insight Tests and evaluation answer different questions
A **test** asks "does the code do what the code is supposed to do?" and must
be deterministic, fast and binary. An **evaluation** asks "is the model good
enough?" and is statistical, slow and continuous. Putting
`assert accuracy > 0.87` in your test suite conflates them: the suite becomes
flaky, slow and eventually ignored. Keep model quality in an evaluation
harness with its own reporting, and keep the test suite green.
:::

## Start with the data code

Most ML bugs are data bugs, and data code is completely ordinary.

```python title="Tests for a tokeniser wrapper — unglamorous and high value"
import pytest

def test_roundtrip_preserves_text():
    for s in ["hello world", "", "  spaces  ", "émoji 🙂", "a" * 10_000]:
        assert tok.decode(tok.encode(s)) == s

def test_truncation_respects_max_length():
    ids = tok.encode("word " * 5000, max_length=512, truncation=True)
    assert len(ids) == 512

def test_special_tokens_not_splittable():
    ids = tok.encode("<|endoftext|>")
    assert len(ids) == 1

@pytest.mark.parametrize("text", ["", " ", "\n", "\x00", "𝕳𝖊𝖑𝖑𝖔"])
def test_degenerate_inputs_do_not_crash(text):
    assert isinstance(tok.encode(text), list)

def test_batch_equals_individual():
    texts = ["a b c", "d e", "f"]
    batched = tok(texts, padding=True)["input_ids"]
    for i, t in enumerate(texts):
        unpadded = [x for x in batched[i] if x != tok.pad_token_id]
        assert unpadded == tok.encode(t)
```

That last test --- batched equals individual --- catches a genuinely common
and genuinely destructive bug: padding or truncation behaving differently in
batch mode, so your model sees different inputs at training and serving time.

## Property-based testing

For data transforms, stating a *property* beats enumerating examples, because
the framework generates the examples --- including the ones you would never
have thought of.

```python title="Hypothesis finds the inputs you did not consider"
from hypothesis import given, strategies as st

@given(st.lists(st.floats(-1e6, 1e6, allow_nan=False), min_size=1))
def test_normalise_is_idempotent(xs):
    once = normalise(xs)
    assert normalise(once) == pytest.approx(once, abs=1e-6)

@given(st.lists(st.integers(0, 1000), min_size=1), st.integers(1, 100))
def test_batching_preserves_all_items(xs, n):
    assert [x for b in batched(iter(xs), n) for x in b] == xs

@given(st.text())
def test_clean_is_idempotent(s):
    assert clean(clean(s)) == clean(s)
```

Idempotence, order-preservation, length-preservation and
inverse-relationships are the four properties that cover most data code.
Hypothesis will find your empty list, your single element, your zero, your
duplicate key and your `-0.0` within seconds.

## The four ML-specific patterns

### 1. Overfit one batch

The highest-value test in all of deep learning, and it takes thirty seconds.

```python title="If a model cannot memorise eight examples, it is broken"
def test_model_can_overfit_one_batch():
    torch.manual_seed(0)
    model = TinyTransformer(vocab=128, dim=64, layers=2)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    x = torch.randint(0, 128, (8, 32))
    y = torch.randint(0, 128, (8, 32))

    losses = []
    for _ in range(300):
        loss = F.cross_entropy(model(x).flatten(0, 1), y.flatten())
        opt.zero_grad(); loss.backward(); opt.step()
        losses.append(loss.item())

    assert losses[-1] < 0.05, f"cannot overfit: {losses[0]:.3f} -> {losses[-1]:.3f}"
```

A model that cannot drive the loss to zero on eight fixed examples has a bug
--- a detached gradient, a wrong mask, a label misalignment, a frozen
parameter. This test finds all of them before you spend a night training.
Chapter 27 lists the diagnoses by signature.

### 2. Invariance and equivariance

Assert the symmetries the model is supposed to have.

```python
def test_padding_does_not_change_output():
    x = torch.randint(1, 100, (2, 10))
    short = model(x, attention_mask=torch.ones_like(x))
    padded_x = F.pad(x, (0, 20), value=0)
    mask = F.pad(torch.ones_like(x), (0, 20), value=0)
    long = model(padded_x, attention_mask=mask)[:, :10]
    assert torch.allclose(short, long, atol=1e-4)

def test_batch_order_does_not_matter():
    x = torch.randint(1, 100, (4, 10))
    a = model(x)
    b = model(x.flip(0)).flip(0)
    assert torch.allclose(a, b, atol=1e-5)
```

Padding invariance is violated constantly --- a wrong mask, a `mean` over
padded positions, a normalisation that includes pad tokens --- and the
failure is invisible in training loss while being catastrophic at serving
time where batch composition differs.

### 3. Gradient checks

```python title="Numerical gradient checking for a custom op"
def test_custom_op_gradient():
    x = torch.randn(4, 8, dtype=torch.double, requires_grad=True)
    assert torch.autograd.gradcheck(my_custom_op, (x,), eps=1e-6, atol=1e-4)

def test_all_parameters_receive_gradient():
    loss = F.cross_entropy(model(x).flatten(0, 1), y.flatten())
    loss.backward()
    dead = [n for n, p in model.named_parameters()
            if p.requires_grad and (p.grad is None or p.grad.abs().sum() == 0)]
    assert not dead, f"no gradient reached: {dead}"
```

The second test catches the layer you built, registered, and then forgot to
call --- which trains happily and contributes nothing.

### 4. Serialisation round-trip

```python
def test_save_load_is_exact():
    torch.save(model.state_dict(), tmp / "m.pt")
    clone = TinyTransformer(vocab=128, dim=64, layers=2)
    clone.load_state_dict(torch.load(tmp / "m.pt"))
    clone.eval(); model.eval()
    with torch.no_grad():
        assert torch.equal(model(x), clone(x))
```

If this fails you have state outside `state_dict` --- a buffer not registered,
a normalisation statistic held in a plain attribute, a tokeniser rebuilt with
a different vocabulary order. Every one of those produces a model that works
in your process and is wrong after deployment.

:::pitfall The three sources of test flakiness in ML
1. **Unseeded randomness.** Seed Python, NumPy and Torch in a fixture; make
   it `autouse=True` so nobody can forget.
2. **Non-deterministic kernels.** `torch.use_deterministic_algorithms(True)`
   in tests, and accept the slowdown.
3. **Floating-point comparison with `==`.** Use `pytest.approx` or
   `torch.allclose` with an explicit tolerance. Different hardware gives
   different last bits; `bf16` gives different several-last bits.
:::

## Making the suite fast enough to actually run

A suite that takes eleven minutes is a suite that runs once a day.

```python title="conftest.py — the fixtures that buy the speed"
import pytest, torch, numpy as np, random

@pytest.fixture(autouse=True)
def deterministic():
    random.seed(0); np.random.seed(0); torch.manual_seed(0)

@pytest.fixture(scope="session")
def tiny_model():
    """Two layers, dim 64: exercises every code path, trains in ms."""
    return TinyTransformer(vocab=128, dim=64, layers=2)

@pytest.fixture(scope="session")
def sample_corpus(tmp_path_factory):
    p = tmp_path_factory.mktemp("data") / "corpus.jsonl"
    p.write_text("\n".join(json.dumps({"text": f"doc {i}"}) for i in range(100)))
    return p
```

| Technique | Effect |
|---|---|
| Tiny models (2 layers, dim 64) | same code paths, ~1000× faster |
| `scope="session"` fixtures | build expensive objects once |
| `pytest -n auto` (xdist) | near-linear speedup on many cores |
| `@pytest.mark.slow` plus `-m "not slow"` | fast suite by default |
| Synthetic fixtures over real files | no network, no disk, no drift |
| `--lf` / `--ff` while iterating | rerun failures first |

@tbl: Getting a suite under sixty seconds. The tiny-model trick is the important one: model *size* is almost never what a test is checking.

:::warning Do not test the framework
`assert torch.nn.Linear(4, 8)(x).shape == (2, 8)` tests PyTorch, not you.
Test *your* logic: your masking, your loss reduction, your data joins, your
config handling, your serialisation. A suite full of framework tests is slow,
brittle and finds nothing.
:::

:::practice The task
Take a model you have written and add: (a) an overfit-one-batch test that
runs in under thirty seconds, (b) a padding-invariance test, (c) an
all-parameters-receive-gradient test, (d) a save/load round-trip test, (e) a
Hypothesis property test for one data transform. Then deliberately break the
model five ways --- detach a tensor, invert a mask, freeze a layer, forget to
register a buffer, misalign labels by one --- and record which test catches
each.

**You have this skill when** every one of those five breakages is caught by a
named test in under a minute, and you can say which.
:::

:::exercise
1. Write the batch-equals-individual test for your tokeniser. If it passes
   immediately, make padding one-sided and watch it fail.
2. Use Hypothesis to find an input that breaks your text-cleaning function.
   Report the minimal failing case it shrinks to.
3. † Write a test that would have caught a label-alignment
   off-by-one in a causal language model. Explain why loss curves do not.
4. Add `torch.use_deterministic_algorithms(True)` and find which op in your
   model has no deterministic implementation.
5. Measure your suite's runtime, then apply three techniques from the table
   and measure again. Report the ratio.
6. † Write an integration test for a serving endpoint that asserts the
   response schema, a p95 latency bound and correct behaviour on malformed
   input --- without loading real model weights.
7. Argue the case for and against asserting a minimum accuracy in CI. Give
   the conditions under which it is right.
:::

:::recap
- Almost all ML code is ordinary code; only learned behaviour is stochastic,
  and that belongs in evaluation, not in the test suite.
- Data transforms carry most of the real bugs and test completely normally.
- Property-based testing covers the inputs you would not have written:
  idempotence, order- and length-preservation, inverses.
- The four ML-specific patterns: overfit one batch, invariance, gradient
  presence, serialisation round-trip.
- Flakiness comes from unseeded randomness, non-deterministic kernels and
  exact float comparison --- all three are fixable in a fixture.
- Tiny models plus session-scoped fixtures plus parallelism get a real suite
  under a minute.
- Do not test the framework.
:::
