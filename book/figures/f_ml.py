"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("curse_dimensions")
def curse_dimensions(p):
    """In high dimensions, all distances concentrate and space is empty."""
    import math
    x0, y0 = 32, 26
    w, h = 150, p.h - 52
    p.axes(x0, y0, w, h, "dimension d", "relative contrast")
    p.plot(x0, y0, w, h, lambda d: 1.0 / math.sqrt(max(d, 1)) * 3.0,
           xmax=100, ymax=3.2, color=D.bad_bd, lw=1.4)
    p.text(x0 + 8, y0 + h - 8, "(d_max − d_min) / d_min → 0", 7.0,
           D.bad_bd, SANS_SB, "l")

    x1 = 226
    rows = [("d", "fraction of a unit cube within 0.1 of its surface"),
            ("2", "36%"), ("10", "89%"), ("50", "99.5%"), ("100", "99.997%")]
    y = p.h - 16
    for i, (a, b) in enumerate(rows):
        p.text(x1, y, a, 6.9, D.faint if i == 0 else D.ink,
               SANS_SB if i == 0 else MONO, "l")
        p.text(x1 + 22, y, b, 6.9, D.faint if i == 0 else D.muted,
               SANS_SB if i == 0 else SANS, "l")
        if i == 0:
            p.line(x1, y - 5, p.w, y - 5, D.faint, 0.5)
        y -= 14
    p.text(x1, y - 4, "Everything is near the boundary, so a tree's", 6.9,
           D.muted, SANS_I, "l")
    p.text(x1, y - 14, "pruning test almost never fires: k-d trees", 6.9,
           D.muted, SANS_I, "l")
    p.text(x1, y - 24, "degrade to a full scan above d ≈ 20.", 6.9,
           D.muted, SANS_I, "l")


@fig("ivf_pq")
def ivf_pq(p):
    """IVF partitions the space; PQ compresses each residual vector."""
    import math, random
    rng = random.Random(7)
    cy = p.h - 56
    cx = 60
    centroids = [(cx - 28, cy + 22), (cx + 26, cy + 26), (cx + 22, cy - 22),
                 (cx - 30, cy - 24)]
    for i, (px, py) in enumerate(centroids):
        for _ in range(26):
            a = rng.uniform(0, 6.283)
            d = rng.uniform(0, 19)
            p.c.saveState()
            p.c.setFillColor(D.teal_bd if i == 1 else D.dim_bd)
            p.c.circle(px + d * math.cos(a), py + d * math.sin(a), 1.2,
                       stroke=0, fill=1)
            p.c.restoreState()
        p.circle(px, py, 5, "", "hi" if i == 1 else "", size=5)
    p.text(0, p.h - 10, "IVF \u2014 cluster into nlist cells", 7.2,
           D.node_bd, SANS_SB, "l")
    x0 = 148
    for i, line in enumerate([
            "Build: k-means over a sample \u2192 nlist centroids;",
            "assign every vector to its nearest cell.",
            "",
            "Query: find the nprobe nearest centroids, then",
            "scan only those cells.",
            "",
            "nlist = \u221an, nprobe = 8\u201332 typically scans",
            "about 1% of the database."]):
        p.text(x0, p.h - 14 - i * 11, line, 6.9,
               D.node_bd if i == 6 else D.ink,
               SANS_SB if i == 6 else SANS, "l")
    p.line(0, p.h - 116, p.w, p.h - 116, D.dim_bd, 0.5)

    y = 74
    p.text(0, y + 26, "PQ \u2014 split d = 128 into m = 8 sub-vectors of 16 dims",
           7.2, D.violet_bd, SANS_SB, "l")
    sub = 25
    for i in range(8):
        p.box(i * sub, y, sub - 3, 15, None, "violet" if i < 3 else "dim",
              radius=1)
    p.text(8 * sub + 8, y + 4, "128 float32 = 512 bytes", 6.9, D.muted,
           SANS, "l")
    y2 = 26
    for i in range(8):
        p.box(i * sub, y2, sub - 3, 15, "c%d" % i,
              "violet" if i < 3 else "dim", size=5.8, radius=1)
    p.text(8 * sub + 8, y2 + 4, "8 codes of 8 bits = 8 bytes  (64\u00d7 smaller)",
           6.9, D.violet_bd, SANS_SB, "l")
    for i in range(0, 8, 2):
        p.arrow(i * sub + (sub - 3) / 2, y - 3, i * sub + (sub - 3) / 2,
                y2 + 18, D.violet_bd, 0.7, head=2.6)
    p.text(0, 8, "Each sub-vector is replaced by the index of its nearest of "
           "256 centroids. Distances come from a precomputed", 6.9, D.ink,
           SANS, "l")
    p.text(0, -2, "8\u00d7256 lookup table: 8 table reads and 8 adds per "
           "candidate, with no multiplications at all.", 6.9, D.ink, SANS, "l")


@fig("hnsw_layers")
def hnsw_layers(p):
    """HNSW: sparse long-range layers above a dense base layer."""
    import random
    rng = random.Random(11)
    layers = [(p.h - 26, 4, "layer 2 — sparse, long hops"),
              (p.h - 76, 9, "layer 1"),
              (p.h - 126, 18, "layer 0 — every vector")]
    xs_prev = None
    for y, count, label in layers:
        xs = [28 + i * ((p.w - 150) / max(1, count - 1)) for i in range(count)]
        for i in range(count - 1):
            p.line(xs[i], y, xs[i + 1], y, D.dim_bd, 0.5)
        if count > 3:
            for _ in range(count // 2):
                a, b = rng.randrange(count), rng.randrange(count)
                if abs(a - b) > 1:
                    p.curve(xs[a], y, xs[b], y, bulge=7, color=D.dim_bd,
                            lw=0.4, arrow=False)
        for i, x in enumerate(xs):
            hot = (count == 4 and i == 1) or (count == 9 and i == 3) or \
                  (count == 18 and i == 7)
            p.circle(x, y, 4.5, "", "hi" if hot else "", size=5)
        p.text(p.w, y - 2, label, 6.8, D.muted, SANS, "r")
        xs_prev = xs
    p.arrow(28 + 1 * ((p.w - 150) / 3), p.h - 32, 28 + 3 * ((p.w - 150) / 8),
            p.h - 70, D.hi_bd, 1.0, head=3.2)
    p.arrow(28 + 3 * ((p.w - 150) / 8), p.h - 82, 28 + 7 * ((p.w - 150) / 17),
            p.h - 120, D.hi_bd, 1.0, head=3.2)
    p.text(0, 6, "Enter at the top, greedily descend to the closest node, "
           "drop a layer, repeat: Θ(log n) hops.", 7.0, D.muted, SANS_I, "l")


@fig("alias_table")
def alias_table(p):
    """The alias method: O(1) sampling from any discrete distribution."""
    probs = [0.50, 0.20, 0.20, 0.10]
    n = len(probs)
    cw = 40
    base = p.h - 108
    p.text(0, p.h - 10, "ORIGINAL PROBABILITIES", 7.0, D.muted, SANS_SB, "l")
    for i, q in enumerate(probs):
        h = q * 80
        p.c.saveState()
        p.c.setFillColor(D.teal)
        p.c.setStrokeColor(D.teal_bd)
        p.c.setLineWidth(0.6)
        p.c.rect(i * cw, base, cw - 7, h, stroke=1, fill=1)
        p.c.restoreState()
        p.text(i * cw + (cw - 7) / 2, base - 10, "%.2f" % q, 6.4, D.muted,
               MONO, "c")
    p.line(0, base + 0.25 * 80, n * cw - 7, base + 0.25 * 80, D.bad_bd, 0.8,
           dashed=True)
    p.text(n * cw + 2, base + 0.25 * 80 - 2, "1/n", 6.4, D.bad_bd, SANS_SB, "l")

    x0 = 196
    p.text(x0, p.h - 10, "ALIAS TABLE \u2014 every column has height 1/n",
           7.0, D.hi_bd, SANS_SB, "l")
    cols = [(1.0, ""), (0.8, "\u21920"), (0.8, "\u21920"), (0.4, "\u21920")]
    cw2 = 34
    for i, (frac, alias) in enumerate(cols):
        p.c.saveState()
        p.c.setFillColor(D.teal)
        p.c.setStrokeColor(D.teal_bd)
        p.c.setLineWidth(0.6)
        p.c.rect(x0 + i * cw2, base, cw2 - 7, frac * 50, stroke=1, fill=1)
        if frac < 1.0:
            p.c.setFillColor(D.hi)
            p.c.setStrokeColor(D.hi_bd)
            p.c.rect(x0 + i * cw2, base + frac * 50, cw2 - 7,
                     (1 - frac) * 50, stroke=1, fill=1)
        p.c.restoreState()
        p.text(x0 + i * cw2 + (cw2 - 7) / 2, base - 10, str(i), 6.4, D.muted,
               MONO, "c")
        if alias:
            p.text(x0 + i * cw2 + (cw2 - 7) / 2, base + 52, alias, 6.0,
                   D.hi_bd, SANS_SB, "c")
    p.text(x0 + 4 * cw2 + 6, base + 20, "orange = alias", 6.4, D.hi_bd,
           SANS, "l")
    p.text(0, 26, "sample:  i = randint(n);  u = random()", 7.2, D.ink,
           MONO, "l")
    p.text(0, 14, "         return i if u < prob[i] else alias[i]", 7.2,
           D.ink, MONO, "l")
    p.text(0, 0, "\u0398(n) to build, \u0398(1) per sample, forever \u2014 "
           "the right structure when weights are static.", 7.0, D.hi_bd,
           SANS_SB, "l")


@fig("beam_search")
def beam_search(p):
    """Beam search keeps the b best partial sequences at every step."""
    cols = 4
    colw = (p.w - 130) / (cols - 1)
    y0 = p.h - 24
    rows = 4
    rowh = 26
    kept = {(0, 0), (1, 0), (1, 1), (2, 0), (2, 2), (3, 1), (3, 2)}
    labels = {(0, 0): "The", (1, 0): "cat", (1, 1): "dog",
              (2, 0): "sat", (2, 2): "ran", (3, 1): "on", (3, 2): "fast"}
    for t in range(cols):
        for s in range(rows):
            x = 34 + t * colw
            y = y0 - s * rowh
            on = (t, s) in kept
            if not on and t > 0:
                p.circle(x, y, 7, "", "dim", size=5)
                continue
            if on:
                p.circle(x, y, 9, labels.get((t, s), ""), "hi", size=6.2)
    for (t, s) in sorted(kept):
        if t == cols - 1:
            continue
        for (t2, s2) in sorted(kept):
            if t2 == t + 1:
                p.line(34 + t * colw + 9, y0 - s * rowh,
                       34 + t2 * colw - 9, y0 - s2 * rowh, D.hi_bd, 0.7)
    for t in range(cols):
        p.text(34 + t * colw, y0 + 14, "step %d" % t, 6.6, D.muted, SANS, "c")
    p.text(p.w, y0 - 20, "beam width b = 2", 7.2, D.hi_bd, SANS_SB, "r")
    p.text(p.w, y0 - 34, "expand b×V candidates,", 6.9, D.muted, SANS, "r")
    p.text(p.w, y0 - 46, "keep the best b.", 6.9, D.muted, SANS, "r")
    p.text(p.w, y0 - 62, "Θ(T·b·V) — not Θ(V^T).",
           6.9, D.node_bd, SANS_SB, "r")
    p.text(0, 4, "Greedy is b = 1. Exhaustive is b = V^T. Beam search is the "
           "bounded-memory middle.", 7.0, D.muted, SANS_I, "l")


@fig("speculative_decoding")
def speculative_decoding(p):
    """Draft k tokens cheaply, verify them all in one target-model pass."""
    y = p.h - 28
    cw = 44
    draft = ["The", "cat", "sat", "on", "a"]
    accept = [True, True, True, False, False]
    p.text(0, y + 24, "DRAFT MODEL — k = 5 cheap autoregressive steps",
           7.2, D.violet_bd, SANS_SB, "l")
    for i, t in enumerate(draft):
        p.box(i * cw, y, cw - 4, 18, t, "violet", size=7.0, radius=2)
        if i:
            p.arrow(i * cw - 5, y + 9, i * cw - 1, y + 9, D.violet_bd, 0.7,
                    head=2.6)
    y2 = y - 52
    p.text(0, y2 + 26, "TARGET MODEL — ONE parallel forward pass over "
           "all 5", 7.2, D.node_bd, SANS_SB, "l")
    for i, t in enumerate(draft):
        p.box(i * cw, y2, cw - 4, 18, t, "ok" if accept[i] else "bad",
              size=7.0, radius=2)
        p.arrow(i * cw + (cw - 4) / 2, y + 0, i * cw + (cw - 4) / 2, y2 + 20,
                D.faint, 0.6, head=2.4)
    p.box(3 * cw, y2 - 28, cw - 4, 18, "in", "hi", size=7.0, radius=2)
    p.arrow(3 * cw + 20, y2 - 4, 3 * cw + 20, y2 - 10, D.hi_bd, 0.8, head=3)
    p.text(4 * cw + 8, y2 - 24, "first rejection → resample from the "
           "corrected distribution", 6.9, D.hi_bd, SANS, "l")
    p.text(0, 6, "Accepted 3 + 1 resampled = 4 tokens for the cost of one "
           "target pass plus 5 cheap ones. Output distribution is "
           "provably unchanged.", 6.9, D.muted, SANS_I, "l")


@fig("paged_attention")
def paged_attention(p):
    """Paged KV cache: logical sequences mapped to physical blocks."""
    bw, bh = 30, 18
    y = p.h - 30
    p.text(0, y + 22, "LOGICAL: two sequences", 7.0, D.muted, SANS_SB, "l")
    seqs = [("req A", ["t1", "t2", "t3", "t4", "t5"], "teal"),
            ("req B", ["u1", "u2", "u3"], "violet")]
    logical_pos = {}
    for r, (name, toks, kind) in enumerate(seqs):
        yy = y - r * 26
        p.text(-4, yy + 5, name, 6.8, D.ink, SANS_SB, "r")
        for i, t in enumerate(toks):
            x = 42 + i * bw
            p.box(x, yy, bw - 3, bh, t, kind, size=6.2, radius=1)
            logical_pos[t] = (x + (bw - 3) / 2, yy)

    y2 = 34
    p.text(0, y2 + 26, "PHYSICAL: a pool of fixed-size blocks", 7.0, D.muted,
           SANS_SB, "l")
    layout = ["u1", "u2", None, "t1", "t2", None, "t3", "t4", "u3", None,
              "t5", None]
    for i, t in enumerate(layout):
        x = i * bw
        kind = "dim"
        if t and t.startswith("t"):
            kind = "teal"
        elif t:
            kind = "violet"
        p.box(x, y2, bw - 3, bh, t or "", kind, size=6.2, radius=1)
        if t and t in logical_pos:
            lx, ly = logical_pos[t]
            p.line(lx, ly, x + (bw - 3) / 2, y2 + bh, D.faint, 0.35, dashed=True)
    p.text(0, 12, "A block table per request maps logical positions to "
           "physical blocks — exactly OS virtual memory.", 7.0, D.ink,
           SANS, "l")
    p.text(0, 2, "No contiguity requirement → no fragmentation waste, and "
           "shared prefixes can share blocks.", 7.0, D.node_bd, SANS_SB, "l")


@fig("histogram_split")
def histogram_split(p):
    """Histogram-based split finding: 256 bins instead of n thresholds."""
    import math
    x0, y0 = 20, 40
    w, h = 190, p.h - 70
    bins = [3, 7, 12, 19, 28, 34, 30, 22, 15, 9, 5, 2]
    mx = max(bins)
    bw = w / len(bins)
    for i, b in enumerate(bins):
        p.c.saveState()
        p.c.setFillColor(D.teal if i < 6 else D.violet)
        p.c.setStrokeColor(D.teal_bd if i < 6 else D.violet_bd)
        p.c.setLineWidth(0.5)
        p.c.rect(x0 + i * bw, y0, bw - 1.5, b / mx * h, stroke=1, fill=1)
        p.c.restoreState()
    p.line(x0 + 6 * bw - 1, y0 - 8, x0 + 6 * bw - 1, y0 + h, D.bad_bd, 1.2,
           dashed=True)
    p.text(x0 + 6 * bw, y0 - 18, "best split", 6.8, D.bad_bd, SANS_SB, "c")
    p.axes(x0, y0, w, h, "feature value →", "count")
    x1 = 236
    lines = ["Pre-bin every feature once:",
             "Θ(n log n) at the start,",
             "then Θ(#bins) per split.",
             "",
             "Naive exact splitting is",
             "Θ(n) per feature per node.",
             "",
             "Histogram subtraction:",
             "hist(right) = hist(parent)",
             "             − hist(left)",
             "— half the work, free."]
    for i, line in enumerate(lines):
        p.text(x1, p.h - 16 - i * 11, line, 6.9,
               D.node_bd if line.startswith(("Histogram", "—")) else D.ink,
               SANS_SB if line.startswith(("Histogram", "—")) else SANS, "l")


@fig("tdigest")
def tdigest(p):
    """t-digest: fine centroids at the tails, coarse in the middle."""
    x0, y0 = 26, 32
    w, h = p.w - 64, p.h - 60
    p.axes(x0, y0, w, h, "quantile q", "centroid size")
    p.plot(x0, y0, w, h, lambda q: 4.0 * q * (1.0 - q) + 0.02,
           xmax=1.0, ymax=1.1, color=D.node_bd, lw=1.5)
    for q in (0.01, 0.05, 0.2, 0.5, 0.8, 0.95, 0.99):
        size = 4.0 * q * (1 - q) + 0.02
        p.c.saveState()
        p.c.setFillColor(D.hi_bd)
        p.c.circle(x0 + q * w, y0 + (size / 1.1) * h, 2.4, stroke=0, fill=1)
        p.c.restoreState()
    p.text(x0 + w / 2, y0 + 8, "coarse in the middle \u2014 few centroids, "
           "low memory", 6.9, D.muted, SANS_I, "c")
    p.text(x0 + 4, y0 + h * 0.18, "tiny centroids", 6.9, D.hi_bd, SANS_SB, "l")
    p.text(x0 + 4, y0 + h * 0.18 - 10, "near q = 0", 6.9, D.hi_bd, SANS_SB, "l")
    p.text(x0 + w - 4, y0 + h * 0.18, "and near q = 1", 6.9, D.hi_bd,
           SANS_SB, "r")
    p.text(x0 + w - 4, y0 + h * 0.18 - 10, "\u2192 p99 stays accurate", 6.9,
           D.hi_bd, SANS_SB, "r")
    p.text(0, 4, "Merging two digests merges centroid lists \u2014 so p99 "
           "across a fleet is a tree reduction, not a global sort.", 7.0,
           D.muted, SANS_I, "l")
