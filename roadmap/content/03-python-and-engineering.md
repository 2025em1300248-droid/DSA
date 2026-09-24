# Python and Software Engineering
@short: Python and Engineering
@subtitle: The layer that decides whether anything you build survives contact with a team
@tier: foundation
@prereq: none
@blurb: Almost every AI/ML engineering interview has a coding round, almost every production incident traces back to engineering practice rather than modelling, and the single clearest signal separating a hobbyist from a hire is whether their code can be run by somebody else next month. This is the least glamorous chapter and the one with the highest expected value.
@objectives:
- Write modern, typed, tested, packaged Python that another engineer can run
- Profile and optimise a Python program rather than guessing
- Use git, CI and containers as a matter of course rather than as a chore
- Know which parts of the modern Python toolchain have actually standardised

## What this is for

Machine learning code has a specific failure mode: it works once, on one
machine, in one notebook, and then nobody --- including its author six weeks
later --- can reproduce the number. Every practice in this chapter exists to
prevent that.

## The capabilities

:::checklist ESSENTIAL --- modern Python
- Write idiomatic Python: comprehensions, generators, `dataclasses`, context
  managers, `pathlib`, f-strings, `enumerate`/`zip`/`itertools`
- Use type hints throughout and run a type checker (`mypy` or `pyright`) in CI
- Understand mutability, aliasing, and why a default argument of `[]` is a bug
- Know the cost of the core containers cold (see the DSA companion volume,
  Chapter 2): `in` on a list is linear, string `+=` in a loop is quadratic
- Use `logging` rather than `print`, with structured fields
- Write generators and iterators for data that does not fit in memory
- Handle errors deliberately: narrow `except`, custom exceptions, no bare
  `except: pass`
:::

:::checklist ESSENTIAL --- testing
- `pytest`: fixtures, parametrisation, `tmp_path`, monkeypatching
- Write a test *before* fixing a bug, so the bug cannot return
- Property-based testing with `hypothesis` for anything numerical or
  parsing-shaped --- it finds the empty input, the duplicate, the NaN
- Test ML code specifically: shape tests, a single-batch overfit test, a
  determinism test with a fixed seed, an invariance test
- Know what *not* to test: exact float equality, model accuracy in unit tests
:::

:::checklist ESSENTIAL --- tooling and environments
- `git` beyond the basics: interactive rebase is not needed, but branching,
  bisect, reflog and reading a diff are
- Dependency and environment management. `uv` has become the default for new
  projects (it is dramatically faster and handles Python versions too);
  `poetry`, `pip-tools` and `conda` all still exist in the wild and you should
  be able to read a project using any of them
- Lockfiles, and why an unpinned environment is an unreproducible result
- `ruff` for linting and formatting (it has largely absorbed `flake8`,
  `isort` and `black` for new projects)
- Docker: write a working, layer-cached Dockerfile for a Python service; know
  why CUDA base images are enormous and how to keep them from being worse
- `make` or `just` so that `make test` works on a fresh clone
- Pre-commit hooks, so that CI failures are rare rather than routine
:::

:::checklist CORE --- performance
- Profile before optimising: `cProfile`, `py-spy` (works on a running
  process), `scalene`, `line_profiler`, `torch.profiler`
- Know the three answers to "Python is slow": vectorise it (NumPy, Polars),
  move it out of the loop, or move it out of Python (Numba, Cython, Rust via
  PyO3, or a C++ extension)
- Concurrency: know when you need threads (I/O bound), processes (CPU bound)
  or `asyncio` (many concurrent network calls --- which describes almost all
  LLM application code)
- Memory: `tracemalloc`, `memory_profiler`, and the habit of asking how many
  bytes per element a structure costs
:::

:::checklist CORE --- engineering practice
- Write a design document before a non-trivial change: problem, options,
  choice, tradeoff, how you will know it worked
- Code review: give specific, kind, actionable review; receive it without
  defensiveness
- Configuration as data (`pydantic`, `hydra`, or plain typed dataclasses) so
  that experiments are described by a file rather than by edited constants
- Structure a repository so that a stranger can find things: `src/` layout,
  a runnable `README`, a single entry point per task
:::

:::checklist AWARENESS
- Rust or C++ sufficient to read a kernel or an extension module
- Bash sufficient to read someone's deployment script without fear
- The CPython object model, the GIL, and what free-threaded Python changes
:::

## The tools that have actually standardised

| Job | Default in 2026 | Also common | Notes |
|---|---|---|---|
| Environments and packaging | `uv` | `poetry`, `conda`, `pip` + `venv` | `uv` won new projects on speed; `conda` persists where CUDA and non-Python deps are entangled |
| Lint and format | `ruff` | `black` + `flake8` + `isort` | `ruff` replaced the trio for most new code |
| Type checking | `mypy`, `pyright` | --- | pick one and run it in CI |
| Testing | `pytest` | `unittest` | `hypothesis` for property tests |
| Data validation | `pydantic` v2 | `attrs`, dataclasses | also the schema layer for LLM structured output |
| Task runner | `make`, `just` | shell scripts | any is fine; having one is the point |
| Containers | Docker | Podman | CUDA images from NVIDIA NGC |
| CI | GitHub Actions | GitLab CI, Buildkite | run tests, lint, types on every PR |

@tbl: Where the toolchain has converged. Verify currency before committing study time --- the concepts (locked environments, typed config, fast linting) outlive the tools.

:::note Notebooks
Notebooks are excellent for exploration and terrible as the unit of delivery:
hidden state, unreviewable diffs, no tests, no imports. The professional
pattern is to explore in a notebook and then move anything you will run twice
into a module with a test, importing it back into the notebook. Tools like
`jupytext` and `nbstripout` make notebooks survivable in git; `papermill`
makes them parameterisable. None of that makes a notebook a deliverable.
:::

## How to tell you have it

:::practice The task
Take a script you wrote in a notebook. Convert it into a package with a
`pyproject.toml`, a locked environment, type hints, three `pytest` tests
(one of them a property test), a `Dockerfile`, a `Makefile` with `make test`
and `make run`, and a CI workflow that runs lint, types and tests. Then hand
the repository to somebody else and watch them try to run it without asking
you a question.

If they need to ask you a question, you have not finished.
:::

:::pitfall The four engineering failures that show up in ML code
1. **Notebook-only delivery.** Nothing is importable, nothing is tested, the
   result cannot be regenerated.
2. **Unpinned environments.** "It worked last month" is a dependency
   resolution, not a mystery.
3. **Hidden global state.** A module-level model, a mutable default, a
   `random` call without a seed. All three produce results that change
   without the code changing.
4. **Configuration by editing constants.** Experiment provenance becomes
   impossible, which makes every result unverifiable.
:::

:::note Time to competence
From "I can write Python scripts": **4--6 weeks** at 12 hours a week to reach
the ESSENTIAL list solidly. This is the cheapest block of hours in the whole
map and it raises the ceiling on everything above it.
:::

:::recap
- The failure mode this chapter prevents is the irreproducible result, and it
  is the most common failure in applied ML.
- ESSENTIAL: modern typed Python, `pytest` plus `hypothesis`, git, locked
  environments, `ruff`, Docker, a task runner, CI.
- CORE: profiling before optimising, the right concurrency model (usually
  `asyncio` for LLM application code), design documents, reviewable structure.
- Notebooks are for exploration; anything run twice moves into a tested
  module.
- The test of the skill is whether a stranger can clone and run your work
  without asking you anything.
:::
