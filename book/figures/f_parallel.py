"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("parallel_scan")
def parallel_scan(p):
    """Blelloch scan: an up-sweep of partial sums, then a down-sweep."""
    vals = [3, 1, 7, 0, 4, 1, 6, 3]
    n = len(vals)
    cw = 38
    y = p.h - 30
    p.text(0, p.h - 10, "UP-SWEEP (reduce): pairwise sums, log n levels", 7.0,
           D.node_bd, SANS_SB, "l")
    levels = [vals,
              [None, 4, None, 7, None, 5, None, 9],
              [None, None, None, 11, None, None, None, 14],
              [None, None, None, None, None, None, None, 25]]
    for li, level in enumerate(levels):
        for i, v in enumerate(level):
            if v is None:
                continue
            p.box(i * cw, y - li * 22, cw - 4, 16, str(v),
                  "teal" if li == 0 else "hi", size=6.8, radius=1)
        if li:
            for i, v in enumerate(level):
                if v is None:
                    continue
                prev = i - (1 << (li - 1))
                p.line(prev * cw + (cw - 4) / 2, y - (li - 1) * 22,
                       i * cw + (cw - 4) / 2, y - li * 22 + 16, D.arrow, 0.5)
    ydown = y - 4 * 22 - 10
    p.text(0, ydown + 14, "DOWN-SWEEP: push prefixes back down", 7.0,
           D.ok_bd, SANS_SB, "l")
    out = [0, 3, 4, 11, 11, 15, 16, 22]
    for i, v in enumerate(out):
        p.box(i * cw, ydown - 10, cw - 4, 16, str(v), "ok", size=6.8, radius=1)
    p.text(0, ydown - 32, "exclusive prefix sum", 6.8, D.muted, SANS_I, "l")
    p.text(0, 4, "Θ(n) total work, Θ(log n) depth — the "
           "primitive behind compaction, sorting, histograms and ragged "
           "offsets.", 7.0, D.muted, SANS_I, "l")


@fig("ring_allreduce")
def ring_allreduce(p):
    """Ring all-reduce: 2(P-1)/P x the parameter size, whatever P is."""
    import math
    cx, cy, r = 84, p.h / 2 - 2, 44
    P = 5
    pts = []
    for i in range(P):
        a = math.pi / 2 - i * 2 * math.pi / P
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        pts.append((x, y))
        p.circle(x, y, 13, "w%d" % i, "teal", size=7.0)
    for i in range(P):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % P]
        p.arrow(x1, y1, x2, y2, D.node_bd, 1.0, head=3.4, shrink=15)
    p.text(cx, cy - 4, "one hop", 6.4, D.muted, SANS_I, "c")
    p.text(cx, cy - 13, "per step", 6.4, D.muted, SANS_I, "c")

    x0 = 160
    lines = [
        ("Phase 1 — reduce-scatter", True),
        ("P−1 steps; each worker sends one", False),
        ("of P chunks to its neighbour and", False),
        ("accumulates the one it receives.", False),
        ("", False),
        ("Phase 2 — all-gather", True),
        ("P−1 steps; the fully reduced", False),
        ("chunks circulate once more.", False),
        ("", False),
        ("Bytes sent per worker: 2(P−1)/P · N", True),
        ("— independent of P. Bandwidth-optimal.", True),
    ]
    y = p.h - 14
    for text, bold in lines:
        p.text(x0, y, text, 7.0, D.node_bd if bold else D.ink,
               SANS_SB if bold else SANS, "l")
        y -= 11.5


@fig("coalescing")
def coalescing(p):
    """Coalesced versus strided access from a warp of 32 threads."""
    cw = 10
    y = p.h - 40
    p.text(0, y + 26, "COALESCED: 32 consecutive threads → one 128-byte "
           "transaction", 7.0, D.ok_bd, SANS_SB, "l")
    for i in range(32):
        p.box(i * cw, y, cw - 1.2, 15, None, "ok", radius=0.6, lw=0.35)
    p.brace(0, 32 * cw - 2, y - 4, "1 memory transaction")

    y2 = y - 56
    p.text(0, y2 + 26, "STRIDED: thread i reads element 32i → 32 separate "
           "transactions", 7.0, D.bad_bd, SANS_SB, "l")
    for i in range(32):
        p.box(i * cw, y2, cw - 1.2, 15, None, "bad" if i % 8 == 0 else "dim",
              radius=0.6, lw=0.35)
    p.text(32 * cw + 8, y2 + 4, "32× the traffic", 7.0, D.bad_bd,
           SANS_SB, "l")
    p.text(0, 6, "Identical arithmetic. On a memory-bound kernel this is the "
           "entire performance difference.", 7.0, D.muted, SANS_I, "l")


@fig("flash_tiling")
def flash_tiling(p):
    """FlashAttention: tile Q, K, V so the n x n matrix never reaches HBM."""
    cell = 13
    n = 8
    x0 = 26
    y0 = p.h - 24
    p.text(0, p.h - 10, "STANDARD: materialise the full n×n scores in HBM",
           7.0, D.bad_bd, SANS_SB, "l")
    for r in range(n):
        for c in range(n):
            p.box(x0 + c * cell, y0 - (r + 1) * cell, cell - 1, cell - 1,
                  None, "bad", radius=0.5, lw=0.3)
    p.text(x0 + n * cell + 10, y0 - n * cell / 2,
           "O(n²) writes + O(n²) reads", 7.0, D.bad_bd, SANS, "l")

    x1 = 216
    p.text(x1 - 4, p.h - 10, "FLASH: one tile at a time, in SRAM", 7.0,
           D.ok_bd, SANS_SB, "l")
    bs = 4
    for r in range(n):
        for c in range(n):
            hot = (r // bs == 1 and c // bs == 0)
            p.box(x1 + c * cell, y0 - (r + 1) * cell, cell - 1, cell - 1,
                  None, "ok" if hot else "dim", radius=0.5, lw=0.3)
    for b in range(2):
        p.c.saveState()
        p.c.setStrokeColor(D.ok_bd)
        p.c.setLineWidth(0.8)
        p.c.rect(x1 + b * bs * cell - 1, y0 - n * cell - 1,
                 bs * cell, n * cell, stroke=1, fill=0)
        p.c.restoreState()
    p.text(x1, y0 - n * cell - 14, "online softmax keeps a running max and "
           "sum,", 6.9, D.ok_bd, SANS, "l")
    p.text(x1, y0 - n * cell - 24, "so no tile ever needs the others.", 6.9,
           D.ok_bd, SANS, "l")
    p.text(0, 4, "More FLOPs, far fewer bytes moved — and the wall-clock "
           "time falls by 2–4× (Chapter 3).", 7.0, D.muted, SANS_I, "l")


@fig("consistent_hashing")
def consistent_hashing(p):
    """Consistent hashing: adding a shard moves only 1/N of the keys."""
    import math
    cx, cy, r = 92, p.h / 2 - 4, 46
    p.c.saveState()
    p.c.setStrokeColor(D.dim_bd)
    p.c.setLineWidth(1.0)
    p.c.circle(cx, cy, r, stroke=1, fill=0)
    p.c.restoreState()
    shards = [(0.05, "S1"), (0.28, "S2"), (0.55, "S3"), (0.80, "S4")]
    for t, name in shards:
        a = math.pi / 2 - t * 2 * math.pi
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        p.circle(x, y, 8, name, "teal", size=6.0)
    keys = [0.12, 0.18, 0.35, 0.47, 0.62, 0.70, 0.88, 0.95]
    for t in keys:
        a = math.pi / 2 - t * 2 * math.pi
        x, y = cx + (r - 13) * math.cos(a), cy + (r - 13) * math.sin(a)
        p.c.saveState()
        p.c.setFillColor(D.hi_bd)
        p.c.circle(x, y, 2.1, stroke=0, fill=1)
        p.c.restoreState()
    a = math.pi / 2 - 0.42 * 2 * math.pi
    x, y = cx + r * math.cos(a), cy + r * math.sin(a)
    p.circle(x, y, 8, "S5", "hi", size=6.0)
    p.text(cx, cy - 3, "keys map clockwise", 6.4, D.muted, SANS_I, "c")
    p.text(cx, cy - 12, "to the next shard", 6.4, D.muted, SANS_I, "c")

    x0 = 176
    lines = [("Adding S5 moves only the keys", False),
             ("between S2 and S5 — about 1/N.", True),
             ("", False),
             ("hash(key) % N would move", False),
             ("(N−1)/N of every key.", True),
             ("", False),
             ("Virtual nodes (100–200 per shard)", False),
             ("reduce load imbalance to 1/√v.", True)]
    y = p.h - 16
    for text, bold in lines:
        p.text(x0, y, text, 7.0, D.node_bd if bold else D.ink,
               SANS_SB if bold else SANS, "l")
        y -= 12


@fig("dataloader_pipeline")
def dataloader_pipeline(p):
    """The input pipeline as a chain of queues: find the slowest stage."""
    stages = [("read\nshards", 0.35, "dim"), ("decode", 0.85, "bad"),
              ("augment", 0.55, "hi"), ("collate", 0.25, "dim"),
              ("H2D copy", 0.30, "dim"), ("GPU step", 0.60, "teal")]
    n = len(stages)
    gap = 26
    w = (p.w - gap * (n - 1)) / n
    y = p.h - 54
    for i, (name, load, kind) in enumerate(stages):
        x = i * (w + gap)
        p.box(x, y, w, 34, None, kind, radius=3)
        for j, ln in enumerate(name.split("\n")):
            p.text(x + w / 2, y + 20 - j * 9.5, ln, 7.2, D.ink, SANS_SB, "c")
        p.bar(x, y - 16, w, 6, load)
        p.text(x + w / 2, y - 26, "%.0f%% busy" % (load * 100), 6.4,
               D.bad_bd if load > 0.8 else D.muted, SANS_SB, "c")
        if i < n - 1:
            p.text(x + w + gap / 2, y + 14, "▸", 9, D.faint, SANS, "c")
            p.text(x + w + gap / 2, y + 2, "queue", 5.6, D.faint, SANS, "c")
    p.text(0, p.h - 10, "THE INPUT PIPELINE", 7.2, D.muted, SANS_SB, "l")
    p.text(0, 16, "The GPU is 60% busy, so the job is input-bound. Decode is "
           "the bottleneck at 85% — nothing else matters until it moves.",
           7.0, D.bad_bd, SANS_SB, "l")
    p.text(0, 4, "Prefetch depth hides jitter; it cannot raise the throughput "
           "of the slowest stage.", 7.0, D.muted, SANS_I, "l")
