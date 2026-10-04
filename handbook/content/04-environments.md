# Environments, Packaging and Reproducibility
@short: Environments
@subtitle: Making "it works on my machine" into a fact about every machine
@tier: foundation
@prereq: Chapter 1
@blurb: The ML stack is the hardest dependency problem in mainstream software: compiled extensions, CUDA versions, a resolver-hostile package graph, and multi-gigabyte wheels. This chapter covers the modern toolchain that makes it tractable, and the four axes of reproducibility that determine whether your results survive contact with another machine.
@objectives:
- Use uv for environments and locking, and know what a lockfile guarantees
- Lay out a package that is installable, importable and testable
- Pin the CUDA/PyTorch stack without guessing
- Reproduce a result across machines, not just across runs
- Version data and models as deliberately as you version code

## The problem, stated precisely

Three months after publishing a result you rerun the script and get a
different number. There are exactly four places the difference can come from.

@fig: repro_axes | 118 | The four axes of reproducibility. Most teams control the first and none of the others, which is why "reproducible" usually means "reproducible this week, on this machine".

| Axis | Controlled by | Typical failure |
|---|---|---|
| **Code** | git commit | uncommitted local edits |
| **Environment** | lockfile + container | `pip install -U` between runs |
| **Data** | content hash / snapshot id | the table was appended to |
| **Randomness** | seeds + deterministic kernels | unseeded dataloader shuffle |

@tbl: Reproducibility is the conjunction of four things. Failing any one makes the other three worthless, which is why partial effort feels so unrewarding.

## uv, and why the toolchain changed

`pip` resolves dependencies greedily and one at a time; for a graph as
constrained as the ML stack it frequently produces an environment that
installs cleanly and does not work. `uv` (a Rust reimplementation of the
Python packaging toolchain) does a real resolution, caches aggressively, and
is typically 10–100× faster --- fast enough that recreating the
environment from scratch becomes the normal action rather than a last resort.

```bash title="The commands that replace six older tools"
uv init myproject && cd myproject   # pyproject.toml, .python-version, src/
uv add torch numpy polars           # resolve, install, and record in pyproject
uv add --dev pytest ruff mypy       # dev-only dependency group
uv sync                             # make .venv exactly match uv.lock
uv run pytest                       # run inside the env, no activation
uv lock --upgrade-package torch     # upgrade exactly one thing
uv python install 3.12              # uv manages interpreters too
```

Two properties matter. `uv sync` is *exact*: it removes packages that are not
in the lock as well as installing those that are, so a stale environment
cannot survive. And `uv run` needs no activation, which removes the entire
class of "wrong environment" errors --- including the one where CI activates
nothing and silently uses the system Python.

```toml title="pyproject.toml — the whole project definition in one file"
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = [
    "torch>=2.4,<3.0",
    "numpy>=1.26",
    "polars>=1.0",
    "pydantic>=2.7",
]

[dependency-groups]
dev = ["pytest>=8", "pytest-xdist", "ruff", "mypy", "hypothesis"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
lint.select = ["E", "F", "I", "UP", "B", "SIM", "NPY"]

[tool.pytest.ini_options]
addopts = "-q --strict-markers"
markers = ["slow: excluded from the default run"]
```

:::insight What a lockfile does and does not guarantee
A lockfile pins **versions and content hashes** of every package, direct and
transitive. It does *not* pin the compiler, the CUDA driver, the C library,
or the CPU's instruction set --- all of which affect numerics. A lockfile
makes the environment reproducible *on the same platform*. Crossing
platforms requires a container (Chapter 6).

Commit the lockfile. Always. An application without a committed lock is not
reproducible; a *library* omits it deliberately, because libraries must work
with whatever their consumers resolve.
:::

## The specific pain: PyTorch and CUDA

PyTorch wheels are built against a specific CUDA version and are served from
a separate index. The rule is: **the CUDA the wheel was built for must be
less than or equal to what your driver supports.** The driver is the
constraint; the toolkit is bundled in the wheel.

```toml title="Pinning the accelerator stack explicitly"
[project]
dependencies = ["torch==2.5.1", "torchvision==0.20.1"]

[tool.uv.sources]
torch = { index = "pytorch-cu124" }
torchvision = { index = "pytorch-cu124" }

[[tool.uv.index]]
name = "pytorch-cu124"
url = "https://download.pytorch.org/whl/cu124"
explicit = true            # only packages that name it are taken from here
```

```bash title="Diagnosing the stack, in order"
nvidia-smi                                   # driver version, CUDA capability
python -c "import torch; print(torch.__version__, torch.version.cuda)"
python -c "import torch; print(torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_capability())"
```

:::pitfall The three CUDA errors and what they actually mean
**`torch.cuda.is_available() == False` with a working `nvidia-smi`** ---
you installed the CPU wheel. Check `torch.version.cuda`; if it is `None`, the
index was wrong.

**"CUDA error: no kernel image is available for execution on the device"** ---
the wheel was not compiled for your GPU's compute capability. Common on very
new (or very old) hardware. Needs a different wheel or a source build.

**"CUDA out of memory" immediately at start-up** --- another process holds the
memory. `nvidia-smi` shows it; it is usually your own crashed run.
:::

## Package layout

```
myproject/
  pyproject.toml
  uv.lock                   ← committed
  src/
    myproject/
      __init__.py
      config.py             ← Pydantic models, Chapter 2
      data/                 ← loading, transforms
      models/               ← architectures
      train.py
      serve.py
  tests/
    conftest.py
    test_data.py
  configs/
    base.yaml
  scripts/                  ← one-off, not importable, not shipped
```

The `src/` layout is not cosmetic. Without it, `import myproject` inside the
project directory picks up the *source tree* rather than the installed
package, so your tests silently never exercise the thing you ship --- missing
`__init__.py` files, files omitted from the wheel, and packaging bugs
generally all pass locally and fail on install. With `src/`, the only way to
import is to install (`uv pip install -e .`), so tests exercise the real
artefact.

## Reproducing randomness

```python title="Seeding everything that generates randomness"
import os, random, numpy as np, torch

def set_seed(seed: int, deterministic: bool = False) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.benchmark = False
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

def seed_worker(worker_id: int) -> None:     # DataLoader workers fork!
    s = torch.initial_seed() % 2**32
    np.random.seed(s); random.seed(s)

loader = DataLoader(ds, num_workers=8, worker_init_fn=seed_worker,
                    generator=torch.Generator().manual_seed(0))
```

The `worker_init_fn` is the line everybody misses. DataLoader workers are
separate processes; each inherits the parent's NumPy seed, so without this
**all eight workers generate the identical "random" augmentations**. This has
silently degraded a great many published results.

:::warning Determinism costs throughput
`use_deterministic_algorithms(True)` disables the fastest kernels for several
operations and typically costs 10–30%. Run deterministically to
*debug* and to *test*; run normally to train, and control reproducibility at
the level of the reported metric rather than the bit pattern. A result that
only holds bit-exactly is a result you do not understand.
:::

## Versioning data and models

Code has git. Data and models need an equivalent, and the shape of the answer
is always the same: **store bytes in object storage, store an immutable
pointer in git.**

```python title="A run manifest — the minimum viable provenance record"
import subprocess, json, hashlib, sys, torch, platform

def manifest(cfg) -> dict:
    return {
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain"], text=True).strip()),
        "config_sha256": hashlib.sha256(
            json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16],
        "data_snapshot": cfg["data"]["snapshot_id"],
        "lock_sha256": hashlib.sha256(
            open("uv.lock", "rb").read()).hexdigest()[:16],
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "platform": platform.platform(),
    }
```

Write this next to every checkpoint. It is forty lines, it costs nothing, and
it is the difference between "we cannot reproduce that" and "that run had
uncommitted changes and data snapshot 2026-03-11".

| Concern | Tool | Records |
|---|---|---|
| Large files in git | `git-lfs` | pointer in git, bytes on a server |
| Dataset versions | DVC, LakeFS, Delta/Iceberg | snapshot id, content hash |
| Experiment runs | MLflow, W&B | params, metrics, artefacts |
| Model registry | MLflow, SageMaker | version, stage, lineage |
| Everything, crudely | a JSON manifest per run | the table above |

@tbl: Provenance tooling. The last row is not a joke --- a disciplined manifest plus object storage covers most of what small teams need, and is the fallback when the tool is unavailable.

:::practice The task
Convert a project of yours to uv: `pyproject.toml`, a committed `uv.lock`,
a `src/` layout, and a pinned CUDA-specific torch. Then prove reproducibility:
(a) delete `.venv`, run `uv sync`, rerun, and confirm the metric matches;
(b) on a second machine (or a container), do the same and record the
difference; (c) add `set_seed` including `worker_init_fn` and show that
without it your eight dataloader workers produce identical augmentations.

**You have this skill when** a colleague can clone, run two commands, and get
your number --- and when you can explain any residual difference by naming
which of the four axes it came from.
:::

:::exercise
1. Create two environments that both "install cleanly" but where one fails at
   import because of a binary incompatibility. Explain what pip did.
2. Explain why `uv sync` removing packages is a feature, with an example of
   the bug it prevents.
3. † Take a project without `src/` layout, delete an `__init__.py`, and
   show that tests still pass locally while the built wheel is broken.
4. Write the `set_seed` function and empirically demonstrate the
   `worker_init_fn` bug with `num_workers=4`.
5. Measure the throughput cost of `use_deterministic_algorithms(True)` on one
   of your training steps.
6. † Produce two runs, identical in code, environment and seed, that
   differ in the third decimal place of the final metric. Explain the source.
7. Design a data-versioning scheme for a table that receives 10 million rows
   a day and must support "train exactly on what existed at 2026-03-01".
:::

:::recap
- Reproducibility has four axes --- code, environment, data, randomness ---
  and failing any one nullifies the others.
- uv replaces the older toolchain; `uv sync` is exact and `uv run` removes
  activation errors. Commit the lockfile for applications, not for libraries.
- A lockfile pins packages, not the platform; crossing machines needs a
  container.
- Pin torch to an explicit CUDA index; the driver version is the constraint.
- Use a `src/` layout so tests exercise the installed artefact.
- Seed Python, NumPy, torch *and* DataLoader workers; the worker seed is the
  one people miss.
- Determinism costs throughput: use it for debugging and tests, not training.
- Write a run manifest next to every checkpoint.
:::
