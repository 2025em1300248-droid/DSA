# Containers and the Deployment Boundary
@short: Containers
@subtitle: Shipping the environment, not just the code
@tier: foundation
@prereq: Chapter 4
@blurb: A lockfile pins your Python packages; a container pins everything else --- the C library, the CUDA runtime, the system tools, the file layout. For ML this is not optional, because the parts a lockfile cannot reach are precisely the parts that break. This chapter covers building images that are small, cached and reproducible, and the GPU-specific details.
@objectives:
- Write a Dockerfile whose layers cache correctly
- Build GPU images that are 4 GB rather than 14 GB
- Use multi-stage builds to keep build tools out of the runtime image
- Handle model weights: baked in, mounted, or fetched at start-up
- Debug a container that works locally and fails in the cluster

## What a container actually is

Not a virtual machine. A container is a normal Linux process with three
kernel features applied: **namespaces** (it sees its own filesystem, network,
process table), **cgroups** (it is limited to some CPU and memory), and a
**layered filesystem** (its root directory is a stack of read-only layers
plus one writable layer on top).

That third feature is the one that determines your build times, so it is
worth understanding precisely.

@fig: image_layers | 190 | An image is a stack of layers, each the diff produced by one Dockerfile instruction. A layer is rebuilt if its instruction or any input changed --- and every layer above it is then rebuilt too. Ordering instructions from least to most frequently changed is the whole optimisation.

## The Dockerfile that caches correctly

```dockerfile title="Ordered so that a code change rebuilds one layer"
FROM python:3.12-slim-bookworm AS base

# 1. System packages: change ~never
RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. The package manager: changes rarely
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# 3. Dependencies: change weekly. Copy ONLY the files that define them.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 4. Your code: changes hourly. Last.
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "myproject.serve"]
```

Step 3 is the trick and it is worth stating explicitly: copying *only*
`pyproject.toml` and `uv.lock` before installing means the expensive install
layer is invalidated only when dependencies actually change. Copy the whole
source tree first and every one-character code edit reinstalls PyTorch.

The `--mount=type=cache` lines persist the package cache *between builds*
without putting it in the image. On a dependency change this turns a
four-minute rebuild into twenty seconds.

| Instruction | Changes | Position |
|---|---|---|
| `FROM` | almost never | first |
| `apt-get install` | monthly | early |
| tool binaries | monthly | early |
| `COPY pyproject.toml uv.lock` | weekly | middle |
| `uv sync` | weekly | middle |
| `COPY src/` | hourly | last |
| model weights | per release | see below |

@tbl: Layer ordering. The rule is monotonic: least frequently changed first. Every layer below a change is reused from cache; every layer above is rebuilt.

## Multi-stage builds

Compilers, headers and build tools are needed to build and are dead weight at
runtime. Multi-stage builds keep them out.

```dockerfile title="Build stage discarded; only the venv is carried forward"
FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ ./src/
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
RUN useradd -m -u 1000 app                      # do not run as root
COPY --from=builder --chown=app:app /app /app
WORKDIR /app
USER app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["python", "-m", "myproject.serve"]
```

`build-essential` alone is about 400 MB. A typical multi-stage ML image lands
at 1–2 GB against 4–5 GB single-stage.

## GPU images

```dockerfile title="A CUDA runtime image, not a devel image"
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04
#                        ^^^^^^^ not "devel": saves ~6 GB

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-venv curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

```bash title="Running with GPUs"
docker run --gpus all --rm -it myimage:latest
docker run --gpus '"device=0,1"' --rm -it myimage:latest   # specific devices
docker run --gpus all --shm-size=8g myimage:latest         # PyTorch DataLoader
```

:::pitfall Three GPU container failures, in order of frequency
**`--shm-size` too small.** The default 64 MB is far below what PyTorch
DataLoader workers need for shared memory. Symptom: "DataLoader worker
(pid N) is killed by signal: Bus error". Fix: `--shm-size=8g`.

**The driver is on the host, the toolkit is in the image.** You never install
a driver in a container. The host driver must be new enough for the image's
CUDA version; if it is not, you get "CUDA driver version is insufficient".

**`devel` instead of `runtime` base image.** `devel` carries the full toolkit
including `nvcc`, headers and static libraries: roughly 6 GB you do not need
unless you compile kernels at build time. Compile in a `devel` builder stage,
copy the artefacts into a `runtime` stage.
:::

## Model weights: three strategies

| Strategy | Image size | Start-up | Rollback | Use when |
|---|---|---|---|---|
| **Baked into the image** | + model size | instant | image tag | model is small; atomic deploys matter |
| **Mounted volume** | small | instant | swap the mount | weights change independently |
| **Fetched at start-up** | small | + download | env var | large models, many replicas |

@tbl: Model-weight strategies. Baking is the most reproducible --- the image tag identifies code *and* weights together --- and becomes impractical above a few gigabytes because every deploy pushes and pulls that much.

```python title="Fetch-at-start-up, with the details that matter"
import os, hashlib
from pathlib import Path

CACHE = Path(os.environ.get("MODEL_CACHE", "/models"))

def ensure_weights(uri: str, sha256: str) -> Path:
    dest = CACHE / sha256[:16]
    if dest.exists():
        return dest                       # shared volume across replicas
    tmp = dest.with_suffix(".partial")    # atomic: download then rename
    download(uri, tmp)
    digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
    if digest != sha256:
        tmp.unlink()
        raise RuntimeError(f"checksum mismatch: {digest} != {sha256}")
    tmp.rename(dest)
    return dest
```

Three properties make this safe: the cache key is the content hash (so a
changed model gets a new path), the download is atomic (a crash mid-download
does not leave a corrupt file that looks valid), and the checksum is verified
(so a truncated transfer fails loudly instead of producing garbage
predictions).

## Reproducibility inside the image

```dockerfile
FROM python:3.12-slim-bookworm            # never :latest, never bare :3.12
```

An unpinned base tag means your image changes underneath you. Pin to a
specific minor version, and for real reproducibility pin the digest:

```dockerfile
FROM python:3.12-slim-bookworm@sha256:1e1b3c1a...
```

:::insight The container is the reproducibility boundary
A lockfile pins Python packages. The container pins the C library, the CUDA
runtime, system tools, locale, timezone and file layout. These are exactly
the things that differ between your laptop and the cluster, and exactly the
things that produce "works locally, fails in prod".

That is why the container --- not the lockfile --- is the artefact you
promote from staging to production. Build once, tag by git SHA, and deploy
the same bytes everywhere.
:::

## Debugging "works locally, fails in the cluster"

```bash title="The checklist, in the order that finds it fastest"
docker run --rm -it --entrypoint bash myimage:tag   # get a shell in the image
docker history myimage:tag                          # which layer is huge?
docker run --rm myimage:tag env                     # env differs in the cluster
kubectl logs <pod> --previous                       # logs from the crashed run
kubectl describe pod <pod>                          # OOMKilled? ImagePullBackOff?
kubectl exec -it <pod> -- bash                      # the live container
```

| Symptom | Almost always |
|---|---|
| `Exit code 137` | OOMKilled --- memory limit below actual use |
| `Exit code 139` | segfault --- usually a binary/CUDA mismatch |
| `Bus error` in DataLoader | `--shm-size` too small |
| `ImagePullBackOff` | wrong tag, or missing registry credentials |
| `CrashLoopBackOff` | check `logs --previous`; usually a config error |
| Works locally, not in CI | an env var, a mounted secret, or `:latest` drift |

@tbl: The six failures that cover most of it. Note that the first three are environment problems, not code problems --- which is the point of this chapter.

:::practice The task
Containerise a training script. (a) Write a Dockerfile with correct layer
ordering and prove it: change one line of source and time the rebuild.
(b) Convert it to multi-stage and record the size reduction. (c) Build a GPU
variant on a `runtime` base and run it with `--gpus all --shm-size=8g`.
(d) Deliberately set `--shm-size=64m` and observe the DataLoader bus error.
(e) Implement fetch-at-start-up with checksum verification, and demonstrate
that a corrupted download fails rather than serving garbage.

**You have this skill when** a source-only change rebuilds in under ten
seconds, your GPU image is under 4 GB, and you can name the cause of an exit
code 137 without looking it up.
:::

:::exercise
1. Reverse the `COPY` order in the Dockerfile above and measure the rebuild
   time difference for a one-character code change.
2. Use `docker history` on an image of yours and identify the three largest
   layers. Remove one.
3. † Build the same image on two machines and show the digests differ.
   Then make them identical (hint: pinned digests, `SOURCE_DATE_EPOCH`,
   reproducible builds).
4. Explain why you never install an NVIDIA driver inside a container, and
   what the container toolkit actually does at `docker run` time.
5. Construct a container that is OOMKilled and confirm exit code 137. Then
   compute the memory it actually needs and set the limit correctly.
6. † Implement the three weight strategies for one model and measure
   image size, cold-start latency and rollback time for each.
7. Argue for and against running the same image for training and serving.
:::

:::recap
- A container is a process with namespaces, cgroups and a layered filesystem;
  the layers determine your build times.
- Order Dockerfile instructions least- to most-frequently-changed, and copy
  only the dependency files before installing.
- Multi-stage builds drop build tools from the runtime image, typically
  halving it or better.
- Use CUDA `runtime` base images, not `devel`; the driver stays on the host;
  set `--shm-size` for DataLoader workers.
- Bake small models, mount or fetch large ones --- fetch atomically and verify
  the checksum.
- Pin base image tags, ideally by digest; the container, not the lockfile, is
  the artefact you promote.
- Exit 137 is OOM, 139 is a segfault, a DataLoader bus error is shared memory.
:::
