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
