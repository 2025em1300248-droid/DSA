# Distributed Algorithms: All-Reduce, Sharding, Consistent Hashing
@short: Distributed
@subtitle: Algorithms whose cost is measured in messages
@tier: expert
@prereq: Chapters 16, 39
@blurb: Once a computation spans machines, the dominant cost is communication, and the algorithms that matter are the ones that minimise bytes on the wire. This chapter derives ring all-reduce --- whose communication cost is independent of the number of workers, a genuinely surprising result --- then covers the sharding and placement algorithms that hold a distributed training or serving system together.
@objectives:
- Model communication cost with latency and bandwidth terms
- Derive ring all-reduce and prove its bandwidth optimality
- Choose among data, tensor, pipeline and expert parallelism by their communication patterns
- Implement consistent hashing with virtual nodes and bounded loads
- Understand gradient compression and asynchronous updates, and their costs
- Reason about stragglers, fault tolerance and checkpointing

## The cost model

A message of $N$ bytes between two nodes costs approximately
$$T = \alpha + \frac{N}{\beta}$$
with $\alpha$ the latency (1--10 µs within a node over NVLink, 5--100 µs
across a network) and $\beta$ the bandwidth (400--900 GB/s NVLink, 10--50
GB/s InfiniBand, 1--10 GB/s Ethernet).

Two regimes follow. For small messages, latency dominates and you should
minimise the *number* of messages --- batch them. For large messages,
bandwidth dominates and you should minimise *bytes*. Gradient all-reduce is
firmly in the second regime.

## Ring all-reduce

Every data-parallel worker holds a gradient vector of $N$ bytes; all must end
with the sum. The naive designs are bad: a central parameter server receives
$PN$ bytes on one link, and naive all-to-all sends $P^2$ messages.

@fig: ring_allreduce | 155 | Ring all-reduce. Reduce-scatter leaves each worker with one fully reduced chunk; all-gather circulates those chunks. Each worker sends $2(P-1)/P \times N$ bytes regardless of $P$.

:::math The derivation
Arrange $P$ workers in a ring and split the gradient into $P$ chunks of
$N/P$ bytes.

*Reduce-scatter*, $P-1$ steps. In step $s$, worker $i$ sends chunk
$(i - s) \bmod P$ to worker $i+1$ and adds the chunk it receives into its
own. After $P-1$ steps, worker $i$ holds the fully reduced chunk
$(i+1) \bmod P$. Bytes sent per worker: $(P-1) \cdot N/P$.

*All-gather*, $P-1$ steps. Each worker passes its completed chunk around the
ring. Bytes sent per worker: $(P-1) \cdot N/P$.

Total per worker: $\dfrac{2(P-1)}{P} N \to 2N$ as $P$ grows.

**This is independent of $P$.** Doubling the cluster does not increase the
bytes each worker sends. The latency term does grow --- $2(P-1)\alpha$ ---
which is why very large clusters use hierarchical or tree-based reductions
that trade a little bandwidth for logarithmic latency.
:::

```python title="Ring all-reduce, explicitly"
def ring_allreduce(local, rank, world, send_recv):
    """local: list of P chunks. send_recv(chunk, to, frm) -> received chunk."""
    P = world
    for s in range(P - 1):                       # reduce-scatter
        send_idx = (rank - s) % P
        recv_idx = (rank - s - 1) % P
        got = send_recv(local[send_idx], (rank + 1) % P, (rank - 1) % P)
        local[recv_idx] = [a + b for a, b in zip(local[recv_idx], got)]
    for s in range(P - 1):                       # all-gather
        send_idx = (rank - s + 1) % P
        recv_idx = (rank - s) % P
        got = send_recv(local[send_idx], (rank + 1) % P, (rank - 1) % P)
        local[recv_idx] = got
    return local
```

:::perf Overlapping communication with computation
Gradients become available layer by layer during the backward pass, so the
all-reduce for layer $\ell$ can start while layer $\ell-1$ is still
computing. Bucketing (group small tensors into ~25 MB buckets to amortise
latency) plus overlap hides most of the communication behind computation.
This is what `DistributedDataParallel` does with its gradient hooks, and it
is why DDP scales better than a manual "compute everything, then all-reduce"
loop --- the algorithm is the same, the *schedule* is not.
:::

## The four parallelisms

| Strategy | Splits | Communicates | Per step | Best when |
|---|---|---|---|---|
| Data parallel | the batch | all gradients | $2N$ per worker | model fits on one device |
| Tensor parallel | each matrix | activations | 2 all-reduces per layer | model too big for one device; fast interconnect |
| Pipeline parallel | the layers | boundary activations | small | many devices, slower interconnect |
| Expert parallel (MoE) | the experts | routed tokens | all-to-all | sparse models |
| ZeRO / FSDP | optimiser state, then params | params on demand | $\approx 1.5\times$ data parallel | memory-bound, want data-parallel simplicity |

@tbl: Parallelism strategies. Real systems compose them --- "3D parallelism" is tensor within a node, pipeline across nodes, data across replicas --- chosen so that the highest-volume communication rides the fastest link.

:::insight Pipeline bubbles are a scheduling problem
Splitting $L$ layers across $S$ stages means stage $s$ is idle until stage
$s-1$ produces its first output. With $M$ micro-batches the bubble fraction
is $(S-1)/(M + S - 1)$: with $S = 8$ and $M = 8$ that is 47% idle. Raising
$M$ to 64 drops it to 10%. Interleaved (virtual-stage) schedules and
zero-bubble variants reduce it further by reordering forward and backward
work --- which is a job-shop scheduling problem over a DAG (Chapter 24),
solved once and compiled into the runtime.
:::

## Sharding and placement

@fig: consistent_hashing | 138 | Consistent hashing. Shards and keys are placed on a ring and each key belongs to the next shard clockwise, so adding a shard moves only the keys in one arc.

```python title="Consistent hashing with virtual nodes"
import bisect, hashlib

class ConsistentHash:
    def __init__(self, nodes=(), vnodes=150):
        self.vnodes = vnodes
        self.ring = []          # sorted hashes
        self.owner = {}         # hash -> node
        for n in nodes:
            self.add(n)

    def _h(self, key):
        return int.from_bytes(
            hashlib.blake2b(str(key).encode(), digest_size=8).digest(), "big")

    def add(self, node):
        for i in range(self.vnodes):
            h = self._h(f"{node}#{i}")
            bisect.insort(self.ring, h)
            self.owner[h] = node

    def remove(self, node):
        for i in range(self.vnodes):
            h = self._h(f"{node}#{i}")
            idx = bisect.bisect_left(self.ring, h)
            if idx < len(self.ring) and self.ring[idx] == h:
                self.ring.pop(idx)
                del self.owner[h]

    def lookup(self, key):
        if not self.ring:
            return None
        h = self._h(key)
        idx = bisect.bisect_right(self.ring, h) % len(self.ring)
        return self.owner[self.ring[idx]]
```

Virtual nodes are what make it usable: with one point per shard the load
imbalance is large (the arcs have very different lengths), and with $v$
points the standard deviation of load falls as $1/\sqrt v$. $v = 100$--$200$
brings imbalance to a few percent.

*Bounded-load* consistent hashing adds a cap: if a key's target shard is
already above $(1+\varepsilon)$ times the average load, walk clockwise to the
next one. This gives a hard load bound while still moving only $O(1/N)$ keys
on a membership change, and it is what modern load balancers implement.

:::ml Where sharding shows up
Sharded vector indexes (route a query to the shards whose centroids match),
distributed KV caches keyed by conversation id (so a follow-up turn lands on
the machine holding its prefix cache --- Chapter 36), embedding tables split
by id across parameter servers, and model replicas behind a router that must
keep a session sticky. In every case the requirement is the same: stable
placement under membership change.
:::

## Gradient compression, asynchrony, and stragglers

**Compression.** All-reduce moves $2N$ bytes per worker per step; shrinking
$N$ helps directly. Options: fp16 or bf16 gradients (2x, essentially free),
1-bit / sign SGD with error feedback (32x, needs the error-feedback term or
it does not converge), top-$k$ sparsification (100x, but the indices cost
almost as much as the values unless you exploit structure), and low-rank
factorisation (PowerSGD). All of them change the optimisation, so they must
be evaluated on convergence, not only on throughput.

**Asynchrony.** Asynchronous SGD removes the barrier entirely, at the cost of
stale gradients. It works at modest staleness and degrades badly beyond it.
Most large-scale training is synchronous, because reproducibility and
convergence are worth more than the tail-latency saving.

**Stragglers.** One slow worker stalls a synchronous step. Mitigations:
backup workers (start $P+b$ and use the first $P$ results), bounded-staleness
protocols, and simply detecting the sick node. At scale, hardware failure is
routine --- the practical answer is frequent asynchronous checkpointing so
that a failed step costs minutes, not hours.

:::pitfall Checkpointing is a distributed algorithm too
A naive checkpoint stops every worker, gathers all state to rank 0, and
writes it: $\Theta(PN)$ bytes through one node, and every worker idle for the
duration. The right design is *sharded* checkpointing --- each worker writes
its own shard in parallel to object storage --- plus *asynchronous* writes
(copy state to host memory, then write in the background) and a manifest that
records the shard layout so the checkpoint can be loaded onto a different
number of workers. Getting this wrong can cost 10% of total training time.
:::

:::exercise
1. Derive the total bytes sent by naive parameter-server all-reduce, tree
   all-reduce and ring all-reduce for $P = 8, 64, 512$ and $N = 1$ GB.
   Include the latency term.
2. Implement `ring_allreduce` over multiprocessing pipes and verify the
   result matches a serial sum. Measure the bytes sent.
3. For a 7B model in bf16 with 8-way data parallelism, compute the
   all-reduce time at 400 GB/s and at 25 GB/s. What fraction of a 200 ms
   step is that?
4. Compute the pipeline bubble fraction for $S \in \{4, 8, 16\}$ and
   $M \in \{S, 4S, 16S\}$. Plot it.
5. Implement consistent hashing and measure the fraction of keys that move
   when a shard is added, for $v \in \{1, 10, 100, 500\}$. Also measure load
   imbalance.
6. Implement bounded-load consistent hashing and show it caps load at
   $(1+\varepsilon)$ times the mean while keeping key movement low.
7. Implement 1-bit compression with and without error feedback on a small
   training job and compare convergence.
8. Design the checkpointing scheme for a 70B model on 512 GPUs with a 5%
   overhead budget. State the sharding, the write path and the recovery path.
:::

:::recap
- Communication costs $\alpha + N/\beta$: minimise message *count* when small,
  *bytes* when large.
- Ring all-reduce sends $2(P-1)/P \cdot N$ bytes per worker --- independent of
  $P$ --- and is bandwidth-optimal; its latency term grows with $P$, which
  hierarchical schemes address.
- Bucketing and overlapping communication with the backward pass is a
  scheduling change that matters as much as the algorithm.
- Data, tensor, pipeline and expert parallelism differ in what they
  communicate; compose them so the heaviest traffic uses the fastest link.
- Pipeline bubbles are $(S-1)/(M+S-1)$ and are reduced by more micro-batches
  and better schedules.
- Consistent hashing with 100--200 virtual nodes gives stable placement with
  few-percent imbalance; bounded-load variants cap it hard.
- Gradient compression, asynchrony and straggler mitigation all trade
  convergence or reproducibility for speed; sharded asynchronous
  checkpointing is not optional at scale.
:::
