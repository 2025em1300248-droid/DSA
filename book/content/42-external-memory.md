# External Memory and the Data Loading Pipeline
@short: Data Pipelines
@subtitle: The part of training that is not the model, and usually the bottleneck
@tier: expert
@prereq: Chapters 31, 39
@blurb: A surprising fraction of training jobs are limited by their input pipeline rather than by the accelerator, and the fix is almost never a bigger machine. This chapter covers external-memory algorithms, the storage layouts that make sequential reading possible, and how to diagnose and fix an input-bound job.
@objectives:
- Apply the external-memory model to sorting, joining and shuffling
- Implement external merge sort and external joins
- Choose a storage layout and shard size for a training corpus
- Diagnose an input-bound training job and find the limiting stage
- Implement correct sharding, shuffling and resumption for a dataloader
- Understand prefetching, pinned memory and overlap

## External-memory algorithms, briefly

Chapter 31 introduced the model: $M$ items in memory, blocks of $B$ items,
cost measured in block transfers. Three algorithms cover most needs.

**External merge sort.** Read $M$ items, sort in memory, write a run; repeat;
then $k$-way merge the runs with a heap (Chapter 13). With $k = M/B$ merge
fan-in, the number of passes is $\lceil \log_{M/B}(n/M) \rceil + 1$ --- which
for realistic values is 2. Sorting a terabyte with 100 GB of RAM is two
passes over the data, not more.

```python title="External merge sort"
import heapq, os, pickle, tempfile

def external_sort(iterable, key=None, chunk=1_000_000, tmpdir=None):
    tmpdir = tmpdir or tempfile.mkdtemp()
    runs, buf = [], []
    def flush():
        buf.sort(key=key)
        path = os.path.join(tmpdir, f"run{len(runs)}.pkl")
        with open(path, "wb") as fh:
            for item in buf:
                pickle.dump(item, fh)
        runs.append(path)
        buf.clear()
    for item in iterable:
        buf.append(item)
        if len(buf) >= chunk:
            flush()
    if buf:
        flush()

    def reader(path):
        with open(path, "rb") as fh:
            while True:
                try:
                    yield pickle.load(fh)
                except EOFError:
                    return
    yield from heapq.merge(*[reader(r) for r in runs], key=key)
```

**External join.** To join two datasets neither of which fits in memory:
*sort-merge* (sort both by key, then one linear pass --- best when the output
must be sorted or the inputs already are) or *hash join* (partition both by
`hash(key) % k` into $k$ buckets small enough to fit, then hash-join each
pair --- usually faster). Both are two passes.

**External shuffle.** Chapter 21: scatter records into $m$ random files, then
shuffle each in memory. Two passes, and a genuinely uniform shuffle --- unlike
a buffered shuffle, which only randomises within a window.

## Storage layout for training data

| Layout | Read pattern | Random access | Good for |
|---|---|---|---|
| Many small files | random, one open per sample | yes | nothing at scale |
| Tar shards (WebDataset) | sequential within a shard | shard-level only | streaming from object storage |
| TFRecord / RecordIO | sequential | with an index | TensorFlow pipelines |
| Parquet | columnar, sequential per column | row-group level | tabular, feature stores |
| Arrow / memory-mapped | zero-copy, OS-paged | yes | local NVMe, repeated epochs |
| Raw binary + offsets | fully sequential | yes | tokenised text (one `uint16` array) |

@tbl: Storage layouts. The last row is what large-language-model pipelines actually use: the entire tokenised corpus as one flat array of token ids, memory-mapped, with document boundaries in a separate offsets array --- the ragged layout of Chapter 4.

:::pitfall The small-files problem
One million JPEGs in a directory is a catastrophe on any networked or object
store: each file costs a metadata lookup plus a round trip, so you get
hundreds of files per second instead of hundreds of megabytes per second.
Aggregate into shards of 100 MB to 1 GB --- large enough to amortise the
round trip, small enough that a worker can hold one and that the shard count
exceeds the worker count by a healthy factor (aim for at least $10\times$
`world_size` $\times$ `num_workers`, or some workers will idle).
:::

```python title="Tokenised corpus as one memory-mapped array"
import numpy as np

class PackedTextDataset:
    """The standard LLM pretraining layout: one flat uint16 token array."""

    def __init__(self, path, seq_len=2048):
        self.tokens = np.memmap(path, dtype=np.uint16, mode="r")
        self.seq_len = seq_len
        self.n = (len(self.tokens) - 1) // seq_len

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        lo = i * self.seq_len
        x = np.asarray(self.tokens[lo:lo + self.seq_len], dtype=np.int64)
        y = np.asarray(self.tokens[lo + 1:lo + 1 + self.seq_len], dtype=np.int64)
        return x, y                       # no decode, no parse, no copy
```

No JSON parsing, no per-example allocation, and the OS page cache handles
readahead. Sequences are packed end-to-end with document separators, which
wastes nothing on padding (Chapter 4) at the cost of some cross-document
attention --- a tradeoff essentially every pretraining pipeline accepts.

## Diagnosing an input-bound job

@fig: dataloader_pipeline | 145 | An input pipeline is a chain of stages joined by queues. Throughput is set by the slowest stage; everything else is idle capacity, and prefetching only hides jitter.

The diagnostic procedure, in order:

1. **Measure GPU utilisation over time.** Steady 95%+ means you are
   compute-bound; sawtooth or a low average means you are input-bound.
2. **Time the loader alone.** Iterate the dataloader with no model step. If
   that alone is slower than your step time, the loader is the ceiling.
3. **Time each stage.** Read, decode, augment, collate, host-to-device copy.
   One will dominate.
4. **Check the queues.** A full queue upstream of a stage means that stage is
   the bottleneck; an empty one means the stage before it is.

| Symptom | Likely cause | Fix |
|---|---|---|
| Low GPU utilisation, high CPU | decode or augmentation | more workers; GPU decode (DALI, nvJPEG); cheaper augments |
| Low GPU and low CPU | I/O wait | larger shards; more prefetch; faster storage; compression |
| Sawtooth utilisation | insufficient prefetch | raise `prefetch_factor`; pinned memory; non-blocking copies |
| First batch slow, rest fast | cold page cache | warm the cache; use a persistent worker pool |
| Slows down over epochs | memory growth or fragmentation | check for accumulating Python objects in the dataset |
| One rank always last | unequal shards or a slow disk | balance shards; check that node |

@tbl: Input-pipeline diagnosis. Note that "buy a bigger GPU" appears nowhere.

```python title="A correct, resumable, shard-based loader"
import numpy as np

class ShardedIterator:
    """Deterministic, resumable, evenly divided across ranks and workers."""

    def __init__(self, shards, rank, world, num_workers, seed=0):
        self.shards = list(shards)
        self.rank, self.world = rank, world
        self.num_workers = max(1, num_workers)
        self.seed = seed

    def epoch_plan(self, epoch):
        rng = np.random.default_rng(self.seed + epoch)      # SAME on all ranks
        order = rng.permutation(len(self.shards))
        pad = (-len(order)) % (self.world * self.num_workers)
        if pad:
            order = np.concatenate([order, order[:pad]])    # equal-sized splits
        return order

    def for_worker(self, epoch, worker_id):
        order = self.epoch_plan(epoch)
        stride = self.world * self.num_workers
        offset = self.rank * self.num_workers + worker_id
        return [self.shards[i] for i in order[offset::stride]]

    def state(self, epoch, worker_id, shard_index, offset_in_shard):
        return dict(epoch=epoch, worker=worker_id,
                    shard_index=shard_index, offset=offset_in_shard)
```

Three properties this gets right, all of which are commonly wrong:
the shard permutation is identical on every rank so the split is disjoint;
the plan is padded so every worker gets the same number of shards and no
all-reduce hangs; and the state is small and explicit so a job can resume
mid-epoch after a preemption without replaying data.

:::ml The prefetch and copy path
The final stage is the host-to-device transfer, and it has its own rules:

- **Pinned (page-locked) host memory** lets the DMA engine copy without the
  CPU, roughly doubling PCIe throughput. `pin_memory=True`.
- **Non-blocking copies on a separate CUDA stream** overlap the transfer of
  batch $i+1$ with the compute of batch $i$. Without this the GPU idles
  during every transfer.
- **Prefetch depth** of 2--4 batches hides jitter. Deeper adds latency and
  memory without adding throughput --- it cannot make a slow stage fast.
- **Do the cheap work on the GPU.** Normalisation, augmentation and even
  JPEG decode are often better on the accelerator, where they are nearly
  free, than on a saturated CPU.
:::

:::perf An arithmetic check worth doing before anything else
A training step that processes a batch of 256 images at 224×224×3 bytes
consumes 38 MB of decoded data. At 10 steps per second that is 385 MB/s of
*decoded* pixels --- which, from JPEGs at roughly 10:1 compression, is 38
MB/s from storage but requires decoding 2,560 images per second. A CPU core
decodes perhaps 100 JPEGs per second, so you need 25 cores just for decode.
That single calculation predicts most input-bound jobs, and it takes a
minute.
:::

:::exercise
1. Implement external merge sort and sort a 10 GB file with a 1 GB memory
   limit. Count the passes and compare to the $\log_{M/B}$ prediction.
2. Implement a hash join and a sort-merge join over two 5 GB datasets and
   compare their I/O.
3. Pack a text corpus into a flat `uint16` array with an offsets file, and
   compare `PackedTextDataset` throughput to a JSON-lines loader.
4. Measure throughput for 100,000 small files versus 100 tar shards from
   local disk and from an object store.
5. Instrument a real dataloader to time each stage and produce the bar chart
   in this chapter's figure for your own pipeline.
6. Demonstrate the unequal-shard hang: run a two-process job where the shard
   count is not divisible by the world size, without padding.
7. Implement mid-epoch resumption and verify that resuming produces exactly
   the same remaining sample sequence as an uninterrupted run.
8. Measure host-to-device throughput with and without pinned memory, and with
   and without a separate copy stream. Report all four numbers.
:::

:::recap
- External sorting, joining and shuffling are all two-pass algorithms at
  realistic memory sizes; the fan-in $M/B$ is what keeps the pass count low.
- Aggregate training data into 100 MB--1 GB shards; the small-files pattern
  destroys throughput on any networked store.
- The standard LLM layout is one flat memory-mapped token array plus
  offsets, which removes parsing and allocation from the hot path entirely.
- Throughput is set by the slowest pipeline stage; prefetching hides jitter
  but cannot raise it. Diagnose by timing the loader alone and then each
  stage.
- A correct loader uses an identical shard permutation across ranks, pads to
  equal splits, and carries small explicit state for resumption.
- Pinned memory, a separate copy stream and modest prefetch depth are the
  transfer-path essentials; move cheap work onto the GPU.
- Do the decoded-bytes-per-second arithmetic before changing anything.
:::
