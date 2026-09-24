"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("ml_pipeline_cost")
def ml_pipeline_cost(p):
    """Where algorithmic cost actually lives in an ML system."""
    stages = [
        ("Ingest\n& dedup", "hashing, LSH,\nsketches", "violet"),
        ("Tokenize", "tries, automata,\nheaps", "violet"),
        ("Sample\n& batch", "alias tables,\nreservoirs", "teal"),
        ("Train", "graphs, scans,\nall-reduce", "teal"),
        ("Index", "HNSW, IVF-PQ,\nk-d trees", "hi"),
        ("Serve", "beam search,\npaged KV cache", "hi"),
    ]
    n = len(stages)
    gap = 9.0
    w = (p.w - gap * (n - 1)) / n
    y = 62
    h = 34
    for i, (name, sub, kind) in enumerate(stages):
        x = i * (w + gap)
        p.box(x, y, w, h, None, kind, radius=3)
        lines = name.split("\n")
        for j, ln in enumerate(lines):
            p.text(x + w / 2, y + h / 2 + (5.5 if len(lines) > 1 else 0) - j * 9.5 - 3,
                   ln, 8.4, D.ink, SANS_SB, "c")
        for j, ln in enumerate(sub.split("\n")):
            p.text(x + w / 2, y - 11 - j * 8.4, ln, 6.8, D.muted, SANS, "c")
        if i < n - 1:
            p.arrow(x + w + 1, y + h / 2, x + w + gap - 1, y + h / 2, lw=0.8,
                    head=3.0)
    p.text(0, y + h + 15, "DATA PATH", 7.2, D.muted, SANS_SB, "l")
    p.line(0, y + h + 10, p.w, y + h + 10, D.faint, 0.5)
    p.text(0, 6, "The structures below each stage are not optional extras — "
                 "they are the stage.", 7.4, D.muted, SANS_I, "l")


@fig("latency_budget")
def latency_budget(p):
    """A 300 ms RAG budget, broken down."""
    rows = [
        ("Embed the query", 12, "teal"),
        ("Vector search over 50M chunks", 18, "hi"),
        ("Rerank top 100 with a cross-encoder", 45, "hi"),
        ("Prompt assembly + tokenization", 4, "teal"),
        ("Prefill 4k tokens", 70, "violet"),
        ("Decode 200 tokens", 140, "violet"),
    ]
    total = sum(r[1] for r in rows)
    x0 = 190
    bw = p.w - x0 - 44
    y = 108
    for name, ms, kind in rows:
        p.text(x0 - 8, y, name, 7.8, D.ink, SANS, "r")
        fc, sc = {"teal": (D.teal, D.teal_bd), "hi": (D.hi, D.hi_bd),
                  "violet": (D.violet, D.violet_bd)}[kind]
        c = p.c
        c.saveState()
        c.setFillColor(D.dim)
        c.roundRect(x0, y - 2.5, bw, 10.5, 1.6, stroke=0, fill=1)
        c.setFillColor(sc)
        c.roundRect(x0, y - 2.5, max(3, bw * ms / 150.0), 10.5, 1.6, stroke=0, fill=1)
        c.restoreState()
        p.text(p.w, y, "%d ms" % ms, 7.4, D.muted, MONO, "r")
        y -= 17
    p.line(x0, y + 9, p.w, y + 9, D.faint, 0.5)
    p.text(x0 - 8, y - 3, "Total", 8.2, D.ink, SANS_SB, "r")
    p.text(p.w, y - 3, "%d ms" % total, 8.2, D.ink, MONO, "r")
    p.text(x0, y - 20,
           "Every bar is an algorithm choice. None of them is model quality.",
           7.4, D.muted, SANS_I, "l")


@fig("two_curves")
def two_curves(p):
    """The same task, two algorithms: the crossover that decides a project."""
    x0, y0 = 34, 22
    w, h = p.w - 90, p.h - 46
    p.axes(x0, y0, w, h, "dataset size n →", "time")
    p.plot(x0, y0, w, h, lambda t: 0.0016 * t * t, xmax=100, ymax=16,
           color=D.bad_bd, lw=1.4, label="O(n²)  brute force")
    p.plot(x0, y0, w, h, lambda t: 0.06 * t, xmax=100, ymax=16,
           color=D.node_bd, lw=1.4, label="O(n) sketch")
    p.plot(x0, y0, w, h, lambda t: 0.0 if t <= 0 else 0.02 * t * (0.6 + 0.5),
           xmax=100, ymax=16, color=D.ok_bd, lw=1.2, dashed=True,
           label="O(n log n) index")
    p.line(x0 + w * 0.29, y0, x0 + w * 0.29, y0 + h * 0.62, D.faint, 0.6,
           dashed=True)
    p.text(x0 + w * 0.29, y0 - 11, "laptop-sized data", 6.8, D.muted, SANS_I, "c")
    p.text(x0 + w * 0.75, y0 - 11, "production-sized data", 6.8, D.muted, SANS_I, "c")


@fig("bigo_definition")
def bigo_definition(p):
    """f(n) = O(g(n)): eventually dominated by a constant multiple of g."""
    x0, y0 = 30, 26
    w, h = p.w - 140, p.h - 52
    p.axes(x0, y0, w, h, "n →", "cost")
    p.plot(x0, y0, w, h, lambda t: 2.6 * t + 34 + 9 * (t ** 0.5) * (1 + 0.28 *
           __import__("math").sin(t / 3.1)), xmax=100, ymax=420,
           color=D.node_bd, lw=1.5, label="f(n)  the real cost")
    p.plot(x0, y0, w, h, lambda t: 4.0 * t, xmax=100, ymax=420,
           color=D.bad_bd, lw=1.3, dashed=True, label="c·g(n)")
    p.plot(x0, y0, w, h, lambda t: 1.0 * t, xmax=100, ymax=420,
           color=D.faint, lw=1.0, dashed=True, label="g(n) = n")
    nx = x0 + w * 0.30
    p.line(nx, y0, nx, y0 + h * 0.85, D.hi_bd, 0.8, dashed=True)
    p.text(nx, y0 - 12, "n₀", 8, D.hi_bd, SANS_SB, "c")
    p.text(x0 + 6, y0 + h - 8,
           "beyond n₀ the dashed red line is never crossed", 7.2,
           D.muted, SANS_I, "l")


@fig("growth_curves")
def growth_curves(p):
    """The growth hierarchy, on a scale where you can see all of it."""
    import math
    x0, y0 = 30, 26
    w, h = p.w - 136, p.h - 46
    p.axes(x0, y0, w, h, "n \u2192", "operations")
    curves = [
        (lambda t: min(2 ** (t / 3.2), 3000), "O(2\u207f)", D.bad_bd, False),
        (lambda t: t * t / 5.0, "O(n\u00b2)", D.hi_bd, False),
        (lambda t: t * math.log2(t + 2), "O(n log n)", D.violet_bd, False),
        (lambda t: t, "O(n)", D.node_bd, False),
        (lambda t: 5 * t ** 0.5, "O(\u221an)", D.teal_bd, True),
        (lambda t: 4 * math.log2(t + 2), "O(log n)", D.ok_bd, False),
        (lambda t: 1.0, "O(1)", D.muted, False),
    ]
    ly = y0 + h - 2
    for fn, lab, col, dash in curves:
        p.plot(x0, y0, w, h, fn, xmax=42, ymax=240, color=col, lw=1.3,
               dashed=dash)
        p.line(x0 + w + 14, ly - 2.6, x0 + w + 30, ly - 2.6, col, 1.6,
               dashed=dash)
        p.text(x0 + w + 35, ly - 5.4, lab, 7.6, col, SANS_SB, "l")
        ly -= 15


@fig("amortized_append")
def amortized_append(p):
    """Doubling: rare expensive copies, cheap on average."""
    x0, y0 = 34, 40
    w = p.w - 60
    h = p.h - 66
    p.axes(x0, y0, w, h, "append number →", "cost of that append")
    n = 34
    bw = w / n
    for i in range(1, n + 1):
        grow = (i & (i - 1)) == 0 and i > 1
        cost = i if grow else 1
        bh = min(h, (cost / 32.0) * h * 0.92 + 3)
        c = p.c
        c.saveState()
        c.setFillColor(D.hi_bd if grow else D.node)
        c.setStrokeColor(D.hi_bd if grow else D.node_bd)
        c.setLineWidth(0.4)
        c.rect(x0 + (i - 1) * bw + 0.8, y0, bw - 1.6, bh, stroke=1, fill=1)
        c.restoreState()
        if grow:
            p.text(x0 + (i - 1) * bw + bw / 2, y0 + bh + 3, "copy %d" % i, 5.6,
                   D.hi_bd, SANS, "c")
    p.line(x0, y0 + h * 0.10, x0 + w, y0 + h * 0.10, D.ok_bd, 1.1, dashed=True)
    p.text(x0 + w, y0 + h * 0.10 - 11, "amortised cost ≈ 3", 7.0,
           D.ok_bd, SANS_SB, "r")
    p.text(x0, y0 - 24, "Capacity doubles at 2, 4, 8, 16, 32 — each copy is "
           "paid for by the cheap appends before it.", 7.2, D.muted, SANS_I, "l")


@fig("memory_pyramid")
def memory_pyramid(p):
    """The memory hierarchy with honest latency numbers."""
    rows = [
        ("Register", "~0.3 ns", "1 cycle", "few KB", 0.16, D.ok_bd),
        ("L1 cache", "~1 ns", "4 cycles", "32-64 KB", 0.28, D.teal_bd),
        ("L2 cache", "~4 ns", "14 cycles", "1-2 MB", 0.42, D.node_bd),
        ("L3 cache", "~15 ns", "50 cycles", "16-96 MB", 0.58, D.violet_bd),
        ("DRAM", "~90 ns", "300 cycles", "16 GB-2 TB", 0.76, D.hi_bd),
        ("NVMe SSD", "~80 µs", "250,000 cycles", "1-30 TB", 0.92, D.bad_bd),
    ]
    y = p.h - 22
    cx = p.w * 0.30
    for name, lat, cyc, cap, frac, col in rows:
        wdt = 40 + frac * 190
        c = p.c
        c.saveState()
        c.setFillColor(col)
        c.setStrokeColor(col)
        c.roundRect(cx - wdt / 2, y - 16, wdt, 15, 2, stroke=0, fill=1)
        c.restoreState()
        p.text(cx, y - 12.5, name, 7.6, D.white, SANS_SB, "c")
        p.text(cx + wdt / 2 + 12, y - 12.5, lat, 7.4, D.ink, MONO, "l")
        p.text(cx + wdt / 2 + 66, y - 12.5, cyc, 7.0, D.muted, SANS, "l")
        p.text(p.w, y - 12.5, cap, 7.0, D.muted, SANS, "r")
        y -= 19
    p.text(cx + 130, p.h - 6, "latency", 6.6, D.faint, SANS_SB, "l")
    p.text(p.w, p.h - 6, "typical capacity", 6.6, D.faint, SANS_SB, "r")
    p.text(0, 4, "One DRAM miss costs about as much as 300 additions. "
           "This single fact reshapes most data-structure choices.",
           7.2, D.muted, SANS_I, "l")


@fig("cache_line")
def cache_line(p):
    """Why sequential access is free and random access is not."""
    cw, ch = 20, 17
    y = p.h - 40
    p.text(0, y + ch + 8, "ONE 64-BYTE CACHE LINE = 16 float32 values", 7.2,
           D.muted, SANS_SB, "l")
    for i in range(16):
        p.box(i * cw, y, cw - 1.2, ch, None, "teal" if i == 0 else "dim",
              radius=1)
        p.text(i * cw + (cw - 1.2) / 2, y + ch / 2 - 2.6, str(i), 6.2,
               D.muted, MONO, "c")
    p.arrow(cw / 2, y - 6, cw / 2, y - 18, D.teal_bd, 1.0, head=3.2)
    p.text(cw / 2 + 4, y - 26, "you asked for x[0] — the other 15 arrive free",
           7.2, D.teal_bd, SANS, "l")

    y2 = 36
    p.text(0, y2 + ch + 8, "RANDOM ACCESS: every touch is a new line", 7.2,
           D.muted, SANS_SB, "l")
    hits = {2, 7, 11, 14}
    for i in range(16):
        p.box(i * cw, y2, cw - 1.2, ch, None, "bad" if i in hits else "dim",
              radius=1)
    for i in sorted(hits):
        p.arrow(i * cw + (cw - 1.2) / 2, y2 - 16, i * cw + (cw - 1.2) / 2,
                y2 - 3, D.bad_bd, 0.8, head=2.8)
    p.text(16 * cw + 10, y2 + ch / 2 - 3, "4 misses ≈ 1200 cycles wasted",
           7.2, D.bad_bd, SANS, "l")


@fig("row_col_access")
def row_col_access(p):
    """Row-major traversal streams; column-major traversal thrashes."""
    cell = 13
    rows, cols = 6, 10
    gap = 62
    x1 = 26
    x2 = x1 + cols * cell + gap

    def block(x, order, title, kind, note):
        p.text(x + cols * cell / 2, p.h - 12, title, 8.0, D.ink, SANS_SB, "c")
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c if order == "row" else c * rows + r
                k = kind if (idx < 12) else "dim"
                p.box(x + c * cell, p.h - 34 - r * cell, cell - 1, cell - 1,
                      None, k, radius=0.8, lw=0.4)
                if idx < 12:
                    p.text(x + c * cell + cell / 2 - 0.5,
                           p.h - 34 - r * cell + cell / 2 - 2.6, str(idx), 5.4,
                           D.ink, MONO, "c")
        p.text(x, p.h - 40 - rows * cell, note, 7.0, D.muted, SANS_I, "l")

    block(x1, "row", "for r: for c: A[r][c]", "teal",
          "first 12 touches lie in 1 cache line")
    block(x2, "col", "for c: for r: A[r][c]", "bad",
          "first 12 touches span 6 cache lines")
    p.text(0, 6, "Identical operation count. On a 4096×4096 float32 matrix the "
           "left loop runs 5–10× faster.", 7.4, D.muted, SANS_I, "l")


@fig("aos_soa")
def aos_soa(p):
    """Array-of-structs versus struct-of-arrays."""
    cw = 23
    y1 = p.h - 42
    p.text(0, y1 + 20, "ARRAY OF STRUCTS — one record per slot", 7.2,
           D.muted, SANS_SB, "l")
    fields = ["id", "x", "y", "z", "w"]
    kinds = {"id": "dim", "x": "teal", "y": "dim", "z": "dim", "w": "dim"}
    i = 0
    for rec in range(3):
        for f in fields:
            p.box(i * cw, y1, cw - 1.4, 16, f, kinds[f], size=6.6, radius=1)
            i += 1
        if rec < 2:
            p.line(i * cw - 0.7, y1 - 3, i * cw - 0.7, y1 + 19, D.faint, 0.5,
                   dashed=True)
    p.text(i * cw + 8, y1 + 4, "to sum all x, you", 6.8, D.bad_bd, SANS, "l")
    p.text(i * cw + 8, y1 - 3, "load 5× the bytes", 6.8, D.bad_bd, SANS, "l")

    y2 = 30
    p.text(0, y2 + 20, "STRUCT OF ARRAYS — one field per run", 7.2,
           D.muted, SANS_SB, "l")
    i = 0
    for f in fields[:3]:
        for rec in range(3):
            p.box(i * cw, y2, cw - 1.4, 16, f, "teal" if f == "x" else "dim",
                  size=6.6, radius=1)
            i += 1
        p.line(i * cw - 0.7, y2 - 3, i * cw - 0.7, y2 + 19, D.faint, 0.5,
               dashed=True)
    p.text(i * cw + 8, y2 + 4, "x values are contiguous:", 6.8, D.ok_bd, SANS, "l")
    p.text(i * cw + 8, y2 - 3, "streamable and vectorisable", 6.8, D.ok_bd, SANS, "l")


@fig("pointer_chase")
def pointer_chase(p):
    """A linked list in memory: logical order versus physical order."""
    y = p.h - 40
    cw, gap = 40, 18
    p.text(0, y + 22, "LOGICAL VIEW", 7.2, D.muted, SANS_SB, "l")
    xs = []
    for i, v in enumerate(["A", "B", "C", "D"]):
        x = i * (cw + gap)
        p.box(x, y, cw, 18, v, "teal", radius=2)
        xs.append(x)
        if i < 3:
            p.arrow(x + cw + 1, y + 9, x + cw + gap - 1, y + 9, D.teal_bd,
                    0.9, head=3.2)

    y2 = 26
    p.text(0, y2 + 40, "PHYSICAL MEMORY", 7.2, D.muted, SANS_SB, "l")
    slots = 22
    sw = p.w / slots
    place = {3: "A", 14: "B", 7: "C", 19: "D"}
    for i in range(slots):
        v = place.get(i)
        p.box(i * sw, y2, sw - 1.2, 18, v, "teal" if v else "dim", size=6.6,
              radius=0.8, lw=0.4)
    order = [3, 14, 7, 19]
    for a, b in zip(order, order[1:]):
        p.curve(a * sw + sw / 2, y2 + 19, b * sw + sw / 2, y2 + 19,
                bulge=16 if b > a else -16, color=D.bad_bd, lw=0.8)
    p.text(0, 4, "Four logical steps, four cache misses, four TLB lookups — "
           "roughly 1200 wasted cycles for 4 useful ones.", 7.4, D.muted,
           SANS_I, "l")


@fig("ndarray_layout")
def ndarray_layout(p):
    """An ndarray is a pointer, a shape and a stride vector."""
    y = p.h - 34
    p.box(0, y - 4, 152, 30, None, "teal", radius=3)
    p.text(8, y + 14, "ndarray header", 7.4, D.teal_bd, SANS_SB, "l")
    p.text(8, y + 4, "shape=(2, 4)  strides=(16, 4)", 7.0, D.ink, MONO, "l")
    p.text(8, y - 5, "dtype=float32  data=0x7f…", 7.0, D.ink, MONO, "l")
    p.arrow(154, y + 10, 196, y + 10, D.teal_bd, 1.0, head=3.4)

    cw = 33
    x0 = 200
    vals = ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0"]
    p.cells(x0, y - 2, vals, cw=cw, ch=20, size=6.8, index=True,
            idx_labels=["+0", "+4", "+8", "+12", "+16", "+20", "+24", "+28"])
    p.text(x0, y + 26, "one contiguous buffer, 32 bytes", 6.8, D.muted, SANS, "l")

    y2 = 34
    p.text(0, y2 + 44, "LOGICAL VIEW  A[i, j] lives at  data + i·strides[0] + "
           "j·strides[1]", 7.2, D.muted, SANS_SB, "l")
    for i in range(2):
        for j in range(4):
            p.box(40 + j * 38, y2 + 20 - i * 20, 36, 18,
                  vals[i * 4 + j], "dim", size=7.0, radius=1)
        p.text(34, y2 + 26 - i * 20, "i=%d" % i, 6.8, D.muted, SANS, "r")
    for j in range(4):
        p.text(40 + j * 38 + 18, y2 + 44, "j=%d" % j, 6.8, D.muted, SANS, "c")
    p.text(210, y2 + 26, "A[1, 2] → 0 + 1·16 + 2·4 = byte 24 → 7.0",
           7.4, D.ink, MONO, "l")
    p.text(210, y2 + 10, "no search, no indirection: pure arithmetic",
           7.0, D.muted, SANS_I, "l")


@fig("strides_views")
def strides_views(p):
    """Transpose, slice and reshape as stride manipulations."""
    rows = [
        ("A", "(3, 4)", "(16, 4)", "the original, C-contiguous", "teal"),
        ("A.T", "(4, 3)", "(4, 16)", "swap shape and strides — free", "violet"),
        ("A[::2]", "(2, 4)", "(32, 4)", "double the row stride — free", "violet"),
        ("A[:, 1]", "(3,)", "(16,)", "offset the base pointer — free", "violet"),
        ("A.reshape(2,6)", "(2, 6)", "(24, 4)", "free only if contiguous", "hi"),
        ("A.T.reshape(-1)", "(12,)", "—", "must COPY: no stride works", "bad"),
    ]
    y = p.h - 16
    p.text(0, y, "expression", 6.8, D.faint, SANS_SB, "l")
    p.text(118, y, "shape", 6.8, D.faint, SANS_SB, "l")
    p.text(172, y, "strides (bytes)", 6.8, D.faint, SANS_SB, "l")
    p.text(258, y, "what happens", 6.8, D.faint, SANS_SB, "l")
    p.line(0, y - 5, p.w, y - 5, D.faint, 0.5)
    y -= 19
    for expr, shape, strides, note, kind in rows:
        fc, sc = {"teal": (D.teal, D.teal_bd), "violet": (D.violet, D.violet_bd),
                  "hi": (D.hi, D.hi_bd), "bad": (D.bad, D.bad_bd)}[kind]
        p.c.saveState()
        p.c.setFillColor(fc)
        p.c.roundRect(-3, y - 4, p.w + 6, 15, 2, stroke=0, fill=1)
        p.c.restoreState()
        p.text(0, y, expr, 7.2, D.ink, MONO, "l")
        p.text(118, y, shape, 7.0, D.muted, MONO, "l")
        p.text(172, y, strides, 7.0, D.muted, MONO, "l")
        p.text(258, y, note, 7.0, sc, SANS, "l")
        y -= 18


@fig("utf8_layout")
def utf8_layout(p):
    """One user-visible character is not one byte, and not one code point."""
    y = p.h - 40
    p.text(0, y + 24, "‘café’ IN UTF-8", 7.4, D.muted, SANS_SB, "l")
    groups = [("c", ["63"], "teal"), ("a", ["61"], "teal"), ("f", ["66"], "teal"),
              ("é", ["C3", "A9"], "hi")]
    x = 0
    for ch, bts, kind in groups:
        w = len(bts) * 30
        for i, b in enumerate(bts):
            p.box(x + i * 30, y, 28, 18, b, kind, size=7.0, font=MONO, radius=1)
        p.text(x + w / 2 - 1, y + 22, ch, 8.2, D.ink, SANS_SB, "c")
        p.brace(x, x + w - 2, y - 3, "%d byte%s" % (len(bts), "s" if len(bts) > 1 else ""))
        x += w + 8
    p.text(x + 10, y + 4, "4 characters, 5 bytes", 7.4, D.ink, SANS_SB, "l")

    y2 = 30
    p.text(0, y2 + 26, "A FAMILY EMOJI", 7.4, D.muted, SANS_SB, "l")
    parts = [("U+1F468", "man", "violet"), ("U+200D", "ZWJ", "dim"),
             ("U+1F469", "woman", "violet"), ("U+200D", "ZWJ", "dim"),
             ("U+1F467", "girl", "violet")]
    x = 0
    for cp, lab, kind in parts:
        p.box(x, y2, 58, 17, cp, kind, size=6.4, font=MONO, radius=1)
        p.text(x + 29, y2 - 9, lab, 6.4, D.muted, SANS, "c")
        x += 62
    p.text(x + 6, y2 + 4, "1 grapheme = 5 code points = 18 bytes", 7.2,
           D.bad_bd, SANS_SB, "l")
    p.text(0, 2, "len() answers a different question in every language. "
           "Decide which unit your algorithm means.", 7.2, D.muted, SANS_I, "l")


@fig("bpe_merge")
def bpe_merge(p):
    """One BPE merge step: the most frequent adjacent pair becomes a token."""
    y = p.h - 30
    steps = [
        (["l", "o", "w", "e", "r"], None, "start: characters"),
        (["l", "o", "w", "er"], (3, 4), "merge (e, r) → er   count 412"),
        (["l", "ow", "er"], (1, 2), "merge (o, w) → ow   count 287"),
        (["low", "er"], (0, 1), "merge (l, ow) → low  count 190"),
    ]
    for toks, pair, note in steps:
        x = 0
        for i, t in enumerate(toks):
            w = 16 + len(t) * 7
            hot = pair is not None and i in pair
            p.box(x, y, w, 16, t, "hi" if hot else "teal", size=7.4, radius=2)
            x += w + 5
        p.text(196, y + 4, note, 7.2, D.muted, SANS, "l")
        y -= 24
    p.text(0, y + 8, "Each step needs argmax over pair counts — a priority "
           "queue with lazy deletion (Chapter 14).", 7.2, D.muted, SANS_I, "l")
