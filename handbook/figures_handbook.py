"""Diagrams for the teaching volume."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


# --------------------------------------------------------------------------
# Part I — The Engineering Foundation
# --------------------------------------------------------------------------
@fig("generator_pipeline")
def generator_pipeline(p):
    """Pull-based streaming: memory is one item per stage."""
    stages = [("corpus.jsonl", "dim", "40 GB on disk"),
              ("read()", "teal", "1 line"),
              ("clean()", "teal", "1 record"),
              ("batched(256)", "violet", "256 records"),
              ("train step", "hi", "1 batch")]
    n = len(stages)
    gap = 9.0
    bw = (p.w - gap * (n - 1)) / n
    y = p.h - 44
    for i, (label, kind, note) in enumerate(stages):
        x = i * (bw + gap)
        p.box(x, y, bw, 26, label, kind, size=7.4, radius=3)
        p.text(x + bw / 2, y - 12, note, 6.6, D.muted, SANS, "c")
        if i:
            p.arrow(x - gap + 1, y + 13, x - 1.5, y + 13, D.arrow, 0.9, head=3.2)
    # the pull direction
    p.arrow(p.w - 6, y + 36, 6, y + 36, D.violet_bd, 0.9, head=3.4, dashed=True)
    p.text(p.w / 2, y + 40, "each stage pulls one item from the one before it",
           6.9, D.violet_bd, SANS_I, "c")
    p.line(0, 12, p.w, 12, D.faint, 0.5, dashed=True)
    p.text(0, 2, "Peak memory = one item per stage. The 40 GB file is never "
           "in RAM.", 7.0, D.muted, SANS_I, "l")


@fig("validation_boundary")
def validation_boundary(p):
    """Validate once at the edge; trust the interior."""
    p.box(0, 8, p.w, p.h - 22, None, "dim", radius=5)
    p.text(p.w / 2, p.h - 22, "your process", 7.0, D.faint, SANS_I, "c")
    inner_x, inner_w = 116, p.w - 232
    p.box(inner_x, 30, inner_w, p.h - 72, None, "white", radius=4)
    p.text(inner_x + inner_w / 2, p.h - 54, "TRUSTED INTERIOR", 7.4,
           D.node_bd, SANS_SB, "c")
    p.text(inner_x + inner_w / 2, p.h - 70,
           "typed objects · invariants hold", 6.9, D.muted, SANS, "c")
    p.text(inner_x + inner_w / 2, p.h - 86,
           "no defensive checks needed", 6.9, D.muted, SANS, "c")

    srcs = [("HTTP body", p.h - 44), ("config.yaml", p.h - 68),
            ("model output", p.h - 92)]
    for label, y in srcs:
        p.box(6, y, 82, 19, label, "bad", size=7.0, radius=3)
        p.arrow(90, y + 9.5, inner_x - 3, y + 9.5, D.bad_bd, 0.9, head=3.2)
        p.text((90 + inner_x) / 2, y + 12.5, "validate", 6.4, D.bad_bd,
               SANS_SB, "c")
    outs = [("DB write", p.h - 44), ("API response", p.h - 68)]
    for label, y in outs:
        p.box(p.w - 88, y, 82, 19, label, "ok", size=7.0, radius=3)
        p.arrow(inner_x + inner_w + 3, y + 9.5, p.w - 91, y + 9.5, D.ok_bd,
                0.9, head=3.2)
    p.text(0, 0, "One validation layer, not one per function.", 7.0, D.muted,
           SANS_I, "l")


@fig("ml_test_pyramid")
def ml_test_pyramid(p):
    """What is testable, and how much of it there is."""
    rows = [("Learned behaviour", "accuracy, quality", "bad", 0.42,
             "evaluation, not tests"),
            ("Training step", "loss decreases on 8 examples", "hi", 0.57,
             "smoke test, seeded"),
            ("Model plumbing", "shapes, masks, dtypes, save/load", "violet", 0.71,
             "unit tests, seeded"),
            ("Feature + data logic", "joins, windows, tokenisation", "teal", 0.86,
             "unit + property tests"),
            ("Plain software", "config, I/O, serving, schemas", "ok", 1.00,
             "ordinary unit tests")]
    col = p.w * 0.50
    y = p.h - 24
    for name, ex, kind, frac, style in rows:
        w = col * frac
        x = (col - w) / 2
        p.box(x, y, w, 20, None, kind, radius=2.5)
        p.text(x + w / 2, y + 7, name, 7.2, D.ink, SANS_SB, "c")
        p.text(col + 14, y + 11, ex, 6.9, D.ink, SANS, "l")
        p.text(col + 14, y + 2, style, 6.6, D.muted, SANS_I, "l")
        y -= 25
    p.line(col + 6, y + 22, col + 6, p.h - 4, D.faint, 0.5)
    p.text(0, 2, "Only the top row is stochastic — and it belongs in an "
           "evaluation harness, not in CI.", 7.0, D.muted, SANS_I, "l")


@fig("repro_axes")
def repro_axes(p):
    """Four independent axes; all four must be pinned."""
    axes = [("CODE", "git commit sha", "uncommitted local edits", "teal"),
            ("ENVIRONMENT", "uv.lock + image digest", "pip install -U between runs",
             "violet"),
            ("DATA", "snapshot id / content hash", "the table was appended to", "hi"),
            ("RANDOMNESS", "seeds + deterministic kernels",
             "unseeded dataloader shuffle", "ok")]
    p.text(p.w / 2, p.h - 10, "REPRODUCIBLE  =  all four, simultaneously",
           8.0, D.node_bd, SANS_SB, "c")
    bw = (p.w - 3 * 10) / 4
    y = 44
    for i, (name, pin, fail, kind) in enumerate(axes):
        x = i * (bw + 10)
        p.box(x, y, bw, 54, None, kind, radius=3)
        p.text(x + bw / 2, y + 40, name, 7.6, D.ink, SANS_SB, "c")
        p.text(x + bw / 2, y + 27, "pinned by", 6.4, D.faint, SANS, "c")
        for k, ln in enumerate(_wrap(pin, 22)):
            p.text(x + bw / 2, y + 16 - k * 8.5, ln, 6.8, D.ink, SANS, "c")
        for k, ln in enumerate(_wrap("fails when: " + fail, 26)):
            p.text(x + bw / 2, y - 11 - k * 8.5, ln, 6.6, D.bad_bd, SANS_I, "c")
    p.text(0, 2, "Fail any one and the other three buy you nothing.", 7.0,
           D.muted, SANS_I, "l")


@fig("git_model")
def git_model(p):
    """Commits, branches and HEAD, drawn as what they are."""
    xs = [26, 96, 166, 236]
    y = p.h - 54
    labels = ["c1", "c2", "c3", "c4"]
    for i, x in enumerate(xs):
        p.circle(x, y, 13, labels[i], "teal" if i < 3 else "hi", size=7.6)
        if i:
            p.arrow(x - 13, y, xs[i - 1] + 13, y, D.arrow, 0.9, head=3.2)
    p.text(p.w / 2 - 40, y + 26, "parent pointers run backwards", 6.8,
           D.muted, SANS_I, "c")
    # a side branch
    p.circle(236, y - 44, 13, "c5", "violet", size=7.6)
    p.arrow(230, y - 33, 172, y - 10, D.arrow, 0.9, head=3.2)

    p.box(300, y - 8, 66, 17, "main", "solid", size=7.2, radius=3)
    p.arrow(298, y + 1, 251, y + 1, D.node_bd, 1.0, head=3.2)
    p.box(300, y - 52, 66, 17, "feature", "violet", size=7.2, radius=3)
    p.arrow(298, y - 43, 251, y - 43, D.violet_bd, 1.0, head=3.2)
    p.box(300, y + 30, 66, 17, "HEAD", "bad", size=7.2, radius=3)
    p.arrow(333, y + 28, 333, y + 11, D.bad_bd, 1.0, head=3.2)

    p.text(0, 28, "A commit is an immutable snapshot.  A branch is a 40-byte "
           "file holding one hash.", 7.2, D.ink, SANS, "l")
    p.text(0, 17, "HEAD is a label pointing at a label — which is why "
           "“detached HEAD” is a coherent idea.", 7.2, D.ink, SANS, "l")
    p.text(0, 3, "git commit moves a branch forward.  git checkout moves HEAD. "
           "Nothing is copied.", 7.0, D.muted, SANS_I, "l")


@fig("image_layers")
def image_layers(p):
    """Layer caching: the rebuild boundary."""
    layers = [("COPY src/", "hourly", "bad", 16),
              ("uv sync (project)", "weekly", "hi", 18),
              ("uv sync (deps)", "weekly", "hi", 28),
              ("COPY pyproject.toml uv.lock", "weekly", "hi", 16),
              ("COPY uv binary", "monthly", "teal", 16),
              ("apt-get install", "monthly", "teal", 20),
              ("FROM python:3.12-slim", "never", "dim", 24)]
    y = 26
    xw = p.w * 0.54
    for name, freq, kind, h in layers[::-1]:
        p.box(0, y, xw, h, None, kind, radius=2)
        p.text(8, y + h / 2 - 3, name, 7.2, D.ink, SANS, "l")
        p.text(xw - 8, y + h / 2 - 3, freq, 6.6, D.muted, SANS_I, "r")
        y += h + 2
    p.text(0, y + 3, "layer size \u2248 box height", 6.6, D.faint, SANS_I, "l")

    bx = xw + 22
    p.line(bx - 8, 26, bx - 8, y - 2, D.faint, 0.5)
    p.box(bx, y - 40, p.w - bx, 34, None, "bad", radius=3)
    p.text(bx + 8, y - 16, "edit one line of src/", 7.2, D.ink, SANS_SB, "l")
    p.text(bx + 8, y - 27, "\u2192 1 layer rebuilt, ~3 s", 7.0, D.bad_bd, SANS, "l")
    p.box(bx, y - 88, p.w - bx, 34, None, "hi", radius=3)
    p.text(bx + 8, y - 64, "add one dependency", 7.2, D.ink, SANS_SB, "l")
    p.text(bx + 8, y - 75, "\u2192 4 layers rebuilt, ~40 s", 7.0, D.hi_bd, SANS, "l")
    p.text(bx, 46, "Everything BELOW a changed", 6.8, D.muted, SANS_I, "l")
    p.text(bx, 37, "layer is reused; everything", 6.8, D.muted, SANS_I, "l")
    p.text(bx, 28, "above is rebuilt. Hence the", 6.8, D.muted, SANS_I, "l")
    p.text(bx, 19, "ordering.", 6.8, D.muted, SANS_I, "l")


# --------------------------------------------------------------------------
# Part II — The Mathematics You Actually Use
# --------------------------------------------------------------------------
@fig("arithmetic_intensity")
def arithmetic_intensity(p):
    """The roofline, with the operations placed on it."""
    x0, y0 = 46, 40
    w, h = p.w - 78, p.h - 76
    p.line(x0, y0, x0 + w, y0, D.faint, 0.7)
    p.line(x0, y0, x0, y0 + h, D.faint, 0.7)
    p.text(x0 + w / 2, y0 - 14, "arithmetic intensity   FLOP / byte   "
           "(log scale)", 7.0, D.muted, SANS, "c")
    p.text(x0 - 40, y0 + h + 8, "attainable FLOP/s", 7.0, D.muted, SANS, "l")

    ridge = 0.56
    p.line(x0, y0, x0 + w * ridge, y0 + h * 0.84, D.node_bd, 1.5)
    p.line(x0 + w * ridge, y0 + h * 0.84, x0 + w, y0 + h * 0.84, D.node_bd, 1.5)
    p.line(x0 + w * ridge, y0, x0 + w * ridge, y0 + h * 0.84, D.faint, 0.6,
           dashed=True)
    p.text(x0 + w * ridge + 5, y0 + 5, "ridge \u2248 330", 6.8, D.muted,
           SANS, "l")

    p.text(x0 + w * 0.05, y0 + h * 0.90, "MEMORY-BOUND", 7.2, D.bad_bd,
           SANS_SB, "l")
    p.text(x0 + w * 0.05, y0 + h * 0.80, "slope set by bandwidth;", 6.7,
           D.muted, SANS_I, "l")
    p.text(x0 + w * 0.05, y0 + h * 0.71, "extra FLOPs are free", 6.7,
           D.muted, SANS_I, "l")
    p.text(x0 + w * 0.62, y0 + h * 0.60, "COMPUTE-BOUND", 7.2, D.ok_bd,
           SANS_SB, "l")
    p.text(x0 + w * 0.62, y0 + h * 0.50, "ceiling is peak FLOP/s;", 6.7,
           D.muted, SANS_I, "l")
    p.text(x0 + w * 0.62, y0 + h * 0.41, "fewer bytes are free", 6.7,
           D.muted, SANS_I, "l")

    pts = [(0.055, "matvec, B=1", "bad", 8, 6), (0.25, "B=8", "hi", 8, -12),
           (0.80, "matmul, B=2048", "ok", -8, 9)]
    for fx, label, kind, dx, dy in pts:
        yy = y0 + h * (0.84 * min(fx / ridge, 1.0))
        p.circle(x0 + w * fx, yy, 4.0, None, kind, lw=1.0)
        p.text(x0 + w * fx + dx, yy + dy, label, 6.9, D.ink, SANS_SB,
               "l" if dx > 0 else "r")
    p.text(0, 2, "Almost every systems optimisation in ML is an attempt to "
           "move an operation to the right.", 7.0, D.muted, SANS_I, "l")


@fig("backprop_flow")
def backprop_flow(p):
    """Forward stores, backward consumes."""
    names = ["x", "h\u2081 = xW\u2081", "a\u2081 = relu(h\u2081)",
             "h\u2082 = a\u2081W\u2082", "L"]
    n = len(names)
    gap = 12
    bw = (p.w - gap * (n - 1)) / n
    yf = p.h - 34
    for i, nm in enumerate(names):
        x = i * (bw + gap)
        kind = "dim" if i == 0 else ("bad" if i == n - 1 else "teal")
        p.box(x, yf, bw, 24, nm, kind, size=7.4, radius=3)
        if i:
            p.arrow(x - gap + 1, yf + 12, x - 1.5, yf + 12, D.node_bd, 1.0,
                    head=3.2)
    p.text(p.w / 2, yf + 30, "FORWARD  \u2014  store every activation", 7.4,
           D.node_bd, SANS_SB, "c")

    yb = yf - 44
    for i in range(n):
        x = i * (bw + gap)
        p.box(x, yb, bw, 22, "\u2202L/\u2202" + names[i].split(" ")[0],
              "violet", size=7.0, radius=3)
        if i < n - 1:
            p.arrow(x + bw + gap - 1, yb + 11, x + bw + 1.5, yb + 11,
                    D.violet_bd, 1.0, head=3.2)
        p.line(x + bw / 2, yf - 2, x + bw / 2, yb + 24, D.faint, 0.5,
               dashed=True)
    p.text(p.w / 2, yb - 12, "BACKWARD  \u2014  each node applies its local "
           "vector\u2013Jacobian product", 7.4, D.violet_bd, SANS_SB, "c")
    p.text(0, 2, "The dashed links are why activation memory dominates: the "
           "backward pass needs the forward values.", 7.0, D.muted, SANS_I, "l")


@fig("variance_of_mean")
def variance_of_mean(p):
    """Half-width of a 95% interval against n, for a metric near 0.5."""
    import math
    x0, y0 = 46, 32
    w, h = p.w - 150, p.h - 54
    NMIN, NMAX, YMAX = 50.0, 4000.0, 0.145

    def hw(n):
        return 1.96 * math.sqrt(0.25 / n)

    def fx(n):
        return x0 + w * (n - NMIN) / (NMAX - NMIN)

    def fy(v):
        return y0 + h * v / YMAX

    p.line(x0, y0, x0 + w, y0, D.faint, 0.8)
    p.line(x0, y0, x0, y0 + h, D.faint, 0.8)
    p.text(x0 + w / 2, y0 - 13, "evaluation set size   n", 7.0, D.muted,
           SANS, "c")
    p.text(x0 - 42, y0 + h + 4, "half-width of the 95% interval", 7.0,
           D.muted, SANS, "l")
    p.plot(x0, y0, w, h, lambda t: hw(max(NMIN + t * (NMAX - NMIN), 1.0)),
           xmax=1.0, ymax=YMAX, color=D.node_bd, lw=1.5)

    for nn, side in ((100, 1), (400, 1), (1000, 1), (4000, -1)):
        px, py = fx(nn), fy(hw(nn))
        p.circle(px, py, 3.6, None, "hi", lw=0.9)
        p.text(px + 8 * side, py + 6, "n=%d   \u00b1%.3f" % (nn, hw(nn)),
               6.8, D.ink, SANS_SB, "l" if side > 0 else "r")
    for v in (0.05, 0.10):
        p.line(x0, fy(v), x0 + w, fy(v), D.faint, 0.4, dashed=True)
        p.text(x0 - 4, fy(v) - 2.5, "%.2f" % v, 6.6, D.faint, SANS, "r")
    p.text(0, 2, "Halving the interval costs four times the labelling. The "
           "first few hundred examples are the cheap ones.", 7.0, D.muted,
           SANS_I, "l")


@fig("interval_shrink")
def interval_shrink(p):
    """Two systems whose intervals overlap: not a measured difference."""
    rows = [("System A", 0.82, 0.055, "dim"), ("System B", 0.85, 0.050, "teal")]
    x0 = 78
    w = p.w - x0 - 30
    lo_v, hi_v = 0.70, 0.95

    def px(v):
        return x0 + w * (v - lo_v) / (hi_v - lo_v)

    ytop, ybot = p.h - 22, 46
    ov_lo = max(rows[0][1] - rows[0][2], rows[1][1] - rows[1][2])
    ov_hi = min(rows[0][1] + rows[0][2], rows[1][1] + rows[1][2])
    p.box(px(ov_lo), ybot + 20, px(ov_hi) - px(ov_lo), ytop - ybot - 20,
          None, "bad", radius=2)

    y = ytop - 16
    for name, m, hw, kind in rows:
        p.text(x0 - 10, y - 3, name, 7.4, D.ink, SANS_SB, "r")
        p.line(px(m - hw), y, px(m + hw), y, D.node_bd, 1.4)
        p.line(px(m - hw), y - 4.5, px(m - hw), y + 4.5, D.node_bd, 1.4)
        p.line(px(m + hw), y - 4.5, px(m + hw), y + 4.5, D.node_bd, 1.4)
        p.circle(px(m), y, 4.0, None, kind, lw=1.1)
        p.text(px(m + hw) + 6, y - 3, "%.2f" % m, 7.0, D.ink, SANS_SB, "l")
        y -= 34
    p.text((px(ov_lo) + px(ov_hi)) / 2, ybot + 9, "the intervals overlap here",
           6.9, D.bad_bd, SANS_I, "c")

    p.line(px(lo_v), ybot, px(hi_v), ybot, D.faint, 0.7)
    for v in (0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
        p.line(px(v), ybot - 4, px(v), ybot, D.faint, 0.7)
        p.text(px(v), ybot - 14, "%.2f" % v, 6.6, D.muted, SANS, "c")
    p.text(0, 2, "n = 200 each, unpaired. This is not a measured difference "
           "\u2014 paired on the same items, it may well be.", 7.0, D.muted,
           SANS_I, "l")


@fig("optimiser_behaviour")
def optimiser_behaviour(p):
    """Three learning-rate regimes, as the loss curves you actually see."""
    import math
    panes = [
        ("\u03b7 too small", "dim", D.arrow,
         lambda t: 1.00 - 0.34 * t, "slow, monotone \u2014 wasting compute"),
        ("\u03b7 about right", "ok", D.ok_bd,
         lambda t: 0.10 + 0.90 * math.exp(-4.4 * t), "fast, then a noise floor"),
        ("\u03b7 too large", "bad", D.bad_bd,
         lambda t: 0.36 + 0.30 * t + (0.07 + 0.26 * t) * math.sin(20 * t),
         "oscillation that grows"),
    ]
    gap = 18
    pw = (p.w - 2 * gap) / 3
    y0 = 36
    h = p.h - 68
    for i, (title, kind, col, fn, note) in enumerate(panes):
        x = i * (pw + gap) + 14
        iw = pw - 14
        p.line(x, y0, x + iw, y0, D.faint, 0.7)
        p.line(x, y0, x, y0 + h, D.faint, 0.7)
        p.plot(x, y0, iw, h, fn, xmax=1.0, ymax=1.06, color=col, lw=1.4)
        p.label_chip(x, p.h - 13, title, kind, size=7.0)
        p.text(x + iw / 2, y0 - 12, note, 6.8, D.muted, SANS_I, "c")
        if i == 0:
            p.text(x - 3, y0 + h - 4, "loss", 6.6, D.faint, SANS, "r")
        p.text(x + iw, y0 - 22, "steps \u2192", 6.6, D.faint, SANS, "r")
    p.text(0, 2, "Matching a curve to one of these three shapes is the first "
           "step of every training diagnosis.", 7.0, D.muted, SANS_I, "l")


# --------------------------------------------------------------------------
# Part III — Data
# --------------------------------------------------------------------------
@fig("query_pipeline")
def query_pipeline(p):
    """SQL text to executed plan."""
    stages = [("SQL text", "dim"), ("parse", "dim"), ("logical plan", "teal"),
              ("OPTIMISER", "violet"), ("physical plan", "teal"),
              ("execute", "ok")]
    gap = 7
    bw = (p.w - gap * (len(stages) - 1)) / len(stages)
    y = p.h - 30
    for i, (nm, kind) in enumerate(stages):
        x = i * (bw + gap)
        p.box(x, y, bw, 22, nm, kind, size=7.0, radius=3)
        if i:
            p.arrow(x - gap + 1, y + 11, x - 1.5, y + 11, D.arrow, 0.9, head=3.0)

    ox = 3 * (bw + gap)
    moves = [("predicate pushdown", "filter rows in the storage layer"),
             ("projection pushdown", "read 3 columns, not 200"),
             ("join reordering", "smallest intermediate first"),
             ("statistics", "\u2190 bad estimates ruin all three")]
    by = y - 20
    p.box(ox - 14, by - 4 * 15 - 4, p.w - ox + 14, 4 * 15 + 6, None, "violet",
          radius=3)
    for k, (nm, note) in enumerate(moves):
        yy = by - 12 - k * 15
        p.text(ox - 6, yy, "\u2022 " + nm, 7.0, D.ink, SANS_SB, "l")
        p.text(ox + 88, yy, note, 6.8, D.muted, SANS, "l")
    p.line(ox + bw / 2, y - 2, ox + bw / 2, by + 2, D.violet_bd, 0.8,
           dashed=True)
    p.text(0, 2, "The optimiser is where all the performance is. Anything that "
           "blocks a rewrite \u2014 a function on a column, an implicit cast "
           "\u2014 costs you orders of magnitude.", 6.9, D.muted, SANS_I, "l")


@fig("lazy_pipeline")
def lazy_pipeline(p):
    """Eager versus lazy execution."""
    half = (p.w - 24) / 2
    for side, (title, kind, rows, total) in enumerate([
        ("EAGER  \u2014  read_parquet()", "bad",
         [("read all columns, all rows", "240 GB"),
          ("filter  (in memory)", "18 GB"),
          ("select 3 columns", "1.1 GB"),
          ("group_by + agg", "40 MB")], "240 GB read"),
        ("LAZY  \u2014  scan_parquet()", "ok",
         [("build plan  (nothing read)", "0 B"),
          ("optimise: push filter + columns", "0 B"),
          ("read matching row groups only", "4.2 GB"),
          ("group_by + agg, streamed", "40 MB")], "4.2 GB read"),
    ]):
        x = side * (half + 24)
        p.box(x, p.h - 22, half, 18, title, kind, size=7.2, radius=3)
        yy = p.h - 46
        for nm, sz in rows:
            p.box(x, yy, half, 19, None, "dim", radius=2)
            p.text(x + 7, yy + 6, nm, 6.9, D.ink, SANS, "l")
            p.text(x + half - 7, yy + 6, sz, 6.9, D.muted, SANS_SB, "r")
            yy -= 22
        p.box(x, yy - 4, half, 18, total, kind, size=7.4, radius=3)
    p.text(0, 2, "Same query, same answer. The plan decides how many bytes "
           "leave the disk.", 7.0, D.muted, SANS_I, "l")


@fig("leakage_timeline")
def leakage_timeline(p):
    """Point-in-time correctness on one axis."""
    ax = p.h - 34
    p.line(0, ax, p.w, ax, D.arrow, 1.0)
    p.arrow(p.w - 14, ax, p.w, ax, D.arrow, 1.0, head=4)
    p.text(p.w, ax - 12, "time \u2192", 6.8, D.muted, SANS_I, "r")

    tp, tl = p.w * 0.52, p.w * 0.80
    for x, lab, col in ((tp, "prediction time", D.node_bd),
                        (tl, "label known", D.ok_bd)):
        p.line(x, ax - 6, x, ax + 6, col, 1.2)
        p.text(x, ax + 11, lab, 7.0, col, SANS_SB, "c")

    p.box(0, ax - 34, tp - 2, 20, None, "ok", radius=2)
    p.text((tp - 2) / 2, ax - 27, "FEATURE WINDOW  \u2014  legal", 7.2,
           D.ok_bd, SANS_SB, "c")
    p.box(tp + 2, ax - 34, p.w - tp - 2, 20, None, "bad", radius=2)
    p.text((tp + p.w) / 2, ax - 27, "THE FUTURE  \u2014  using any of this is "
           "leakage", 7.2, D.bad_bd, SANS_SB, "c")

    notes = [("\u2713  events ingested before the prediction", D.ok_bd, 0.10),
             ("\u2717  aggregates over the whole table", D.bad_bd, 0.56),
             ("\u2717  label-derived fields (refund_amount)", D.bad_bd, 0.56)]
    yy = ax - 46
    for txt, col, fx in notes:
        p.text(p.w * fx, yy, txt, 6.9, col, SANS, "l")
        yy -= 11
    p.text(0, 2, "A feature may use data whose INGEST time \u2014 not its "
           "event time \u2014 precedes the prediction.", 7.0, D.muted,
           SANS_I, "l")


@fig("feature_store")
def feature_store(p):
    """One definition, two materialisations."""
    cx = p.w / 2
    p.box(cx - 92, p.h - 30, 184, 24, "ONE FEATURE DEFINITION", "violet",
          size=7.6, radius=3)
    p.text(cx, p.h - 40, "spend_30d = sum(amount) over 30 days", 6.9,
           D.muted, SANS_I, "c")

    lx, rx, bw = 6, p.w - 178, 172
    y = p.h - 108
    p.box(lx, y, bw, 52, None, "teal", radius=3)
    p.text(lx + bw / 2, y + 38, "OFFLINE STORE", 7.4, D.ink, SANS_SB, "c")
    p.text(lx + bw / 2, y + 26, "Parquet, partitioned", 6.8, D.muted, SANS, "c")
    p.text(lx + bw / 2, y + 14, "10M past moments,", 6.8, D.ink, SANS, "c")
    p.text(lx + bw / 2, y + 4, "point-in-time correct", 6.8, D.ink, SANS, "c")

    p.box(rx, y, bw, 52, None, "hi", radius=3)
    p.text(rx + bw / 2, y + 38, "ONLINE STORE", 7.4, D.ink, SANS_SB, "c")
    p.text(rx + bw / 2, y + 26, "Redis / DynamoDB", 6.8, D.muted, SANS, "c")
    p.text(rx + bw / 2, y + 14, "one key lookup,", 6.8, D.ink, SANS, "c")
    p.text(rx + bw / 2, y + 4, "sub-millisecond", 6.8, D.ink, SANS, "c")

    p.arrow(cx - 20, p.h - 48, lx + bw / 2, y + 56, D.violet_bd, 0.9, head=3.2)
    p.arrow(cx + 20, p.h - 48, rx + bw / 2, y + 56, D.violet_bd, 0.9, head=3.2)
    p.text(lx + bw / 2, y - 12, "training", 7.0, D.teal_bd, SANS_SB, "c")
    p.text(rx + bw / 2, y - 12, "serving", 7.0, D.hi_bd, SANS_SB, "c")
    p.text(0, 2, "Skew is removed structurally: there is only one definition "
           "to disagree with itself.", 7.0, D.muted, SANS_I, "l")


@fig("dedup_pipeline")
def dedup_pipeline(p):
    """The deduplication ladder."""
    rows = [("exact hash", "identical after normalisation", "O(n)",
             "minutes", "teal", "the bulk"),
            ("MinHash + LSH", "Jaccard > 0.8 on 5-grams", "O(n)",
             "tens of minutes", "violet", "the long tail"),
            ("suffix array", "shared substrings > 50 tokens", "O(n log n)",
             "hours", "hi", "partial overlaps")]
    p.text(8, p.h - 14, "STAGE", 6.6, D.faint, SANS_SB, "l")
    p.text(128, p.h - 14, "CATCHES", 6.6, D.faint, SANS_SB, "l")
    p.text(274, p.h - 14, "COST", 6.6, D.faint, SANS_SB, "l")
    p.text(p.w - 6, p.h - 14, "RUNTIME / 1M DOCS", 6.6, D.faint, SANS_SB, "r")
    y = p.h - 50
    for nm, catches, cost, rt, kind, share in rows:
        p.box(0, y, p.w, 26, None, kind, radius=3)
        p.text(8, y + 15, nm, 7.4, D.ink, SANS_SB, "l")
        p.text(8, y + 5, "removes " + share, 6.5, D.muted, SANS_I, "l")
        p.text(128, y + 10, catches, 6.9, D.ink, SANS, "l")
        p.text(274, y + 10, cost, 6.9, D.ink, MONO, "l")
        p.text(p.w - 6, y + 10, rt, 6.9, D.muted, SANS, "r")
        y -= 31
    p.text(0, y + 18, "Run them in this order: each stage is cheaper per "
           "document than the next and shrinks its input.", 7.0, D.ink,
           SANS, "l")
    p.text(0, 2, "Duplicates that straddle the train/eval split do not just "
           "waste compute \u2014 they invalidate the evaluation.", 7.0,
           D.muted, SANS_I, "l")


# --------------------------------------------------------------------------
# Part IV — Classical Machine Learning
# --------------------------------------------------------------------------
@fig("bias_variance")
def bias_variance(p):
    """Classical U, then the modern second descent."""
    import math
    x0, y0 = 40, 40
    w, h = p.w - 56, p.h - 72
    thr = 0.52

    def total(t):
        if t < thr:
            bias = 0.95 * math.exp(-5.0 * t)
            var = 0.10 + 1.30 * (t / thr) ** 3
            return 0.12 + bias + var * 0.78
        u = (t - thr) / (1 - thr)
        return 0.12 + 1.02 * math.exp(-2.6 * u) + 0.26

    p.line(x0, y0, x0 + w, y0, D.faint, 0.8)
    p.line(x0, y0, x0, y0 + h, D.faint, 0.8)
    p.text(x0 + w / 2, y0 - 13, "model capacity \u2192", 7.0, D.muted, SANS, "c")
    p.text(x0 - 36, y0 + h + 3, "test error", 7.0, D.muted, SANS, "l")

    p.plot(x0, y0, w, h, lambda t: 0.12 + 0.95 * math.exp(-5.0 * t),
           xmax=thr, ymax=1.85, color=D.teal_bd, lw=1.0, dashed=True)
    p.plot(x0, y0, w * thr, h, lambda t: (0.10 + 1.30 * (t / thr) ** 3) * 0.78,
           xmax=thr, ymax=1.85, color=D.violet_bd, lw=1.0, dashed=True)
    p.plot(x0, y0, w, h, total, xmax=1.0, ymax=1.85, color=D.node_bd, lw=1.6)

    p.line(x0 + w * thr, y0, x0 + w * thr, y0 + h * 0.96, D.bad_bd, 0.8,
           dashed=True)
    p.text(x0 + w * thr, y0 + h * 0.99, "interpolation threshold", 6.8,
           D.bad_bd, SANS_SB, "c")
    p.text(x0 + w * 0.06, y0 + h * 0.20, "bias", 6.9, D.teal_bd, SANS_SB, "l")
    p.text(x0 + w * 0.30, y0 + h * 0.06, "variance", 6.9, D.violet_bd,
           SANS_SB, "l")
    p.text(x0 + w * 0.22, y0 + h * 0.74, "classical regime", 7.0, D.ink,
           SANS_SB, "c")
    p.text(x0 + w * 0.78, y0 + h * 0.74, "modern regime", 7.0, D.ink,
           SANS_SB, "c")
    p.text(0, 2, "Left of the threshold the U-curve governs. Right of it, "
           "more capacity can help again.", 7.0, D.muted, SANS_I, "l")


@fig("regularisation_path")
def regularisation_path(p):
    """Lasso coefficients as the penalty falls."""
    import math
    x0, y0 = 40, 38
    w, h = p.w - 130, p.h - 62
    p.line(x0, y0, x0 + w, y0, D.faint, 0.8)
    p.line(x0, y0 + h / 2, x0 + w, y0 + h / 2, D.faint, 0.5, dashed=True)
    p.line(x0, y0, x0, y0 + h, D.faint, 0.8)
    p.text(x0 + w / 2, y0 - 13, "\u2190  larger penalty      "
           "log \u03b1      smaller penalty  \u2192", 7.0, D.muted, SANS, "c")
    p.text(x0 - 34, y0 + h + 3, "coefficient", 7.0, D.muted, SANS, "l")

    curves = [(0.10, 0.86, "tenure", D.node_bd),
              (0.26, 0.58, "log_income", D.teal_bd),
              (0.44, -0.50, "n_late_90d", D.bad_bd),
              (0.58, 0.30, "utilisation", D.violet_bd),
              (0.62, -0.22, "credit_limit", D.faint)]
    for enter, final, name, col in curves:
        def f(t, e=enter, fv=final):
            if t < e:
                return 0.5
            u = (t - e) / max(1e-6, 1 - e)
            return 0.5 + 0.5 * fv * (1 - math.exp(-3.4 * u))
        p.plot(x0, y0, w, h, f, xmax=1.0, ymax=1.0, color=col, lw=1.3)
        yy = y0 + h * (0.5 + 0.5 * final * 0.965)
        p.text(x0 + w + 5, yy - 2.5, name, 6.9, col, SANS_SB, "l")
        p.circle(x0 + w * enter, y0 + h * 0.5, 2.6, None, "white", lw=0.8)
    p.text(x0 + 4, y0 + h * 0.5 + 6, "coefficients enter here", 6.6, D.faint,
           SANS_I, "l")
    p.text(0, 2, "Order of entry is a feature ranking. A coefficient that "
           "enters and pushes another down is collinear with it.", 7.0,
           D.muted, SANS_I, "l")


@fig("boosting_rounds")
def boosting_rounds(p):
    """Successive rounds approaching a step target."""
    import math
    panes = [("after 1 tree", 1), ("after 5 trees", 5), ("after 50 trees", 50)]
    gap = 16
    pw = (p.w - 2 * gap) / 3

    def target(t):
        return 0.20 + (0.62 if t > 0.55 else 0.0) + (0.14 if t > 0.25 else 0.0)

    def approx(t, m):
        return 0.20 + (1 - math.exp(-0.12 * m)) * (target(t) - 0.20)

    for i, (title, m) in enumerate(panes):
        x = i * (pw + gap)
        iw = pw - 14
        y0, h = 34, p.h - 62
        p.line(x, y0, x + iw, y0, D.faint, 0.7)
        p.line(x, y0, x, y0 + h, D.faint, 0.7)
        p.plot(x, y0, iw, h, target, xmax=1.0, ymax=1.0, color=D.faint,
               lw=1.6, dashed=True)
        p.plot(x, y0, iw, h, lambda t, mm=m: approx(t, mm), xmax=1.0,
               ymax=1.0, color=D.node_bd, lw=1.5)
        p.label_chip(x, p.h - 13, title, "teal" if i < 2 else "ok", size=7.0)
    p.text(0, 16, "dashed = the target function      solid = the ensemble so far",
           7.0, D.muted, SANS_I, "l")
    p.text(0, 2, "Each round fits a shallow tree to the current residuals and "
           "adds a shrunken copy of it.", 7.0, D.muted, SANS_I, "l")


@fig("calibration_curve")
def calibration_curve(p):
    """Reliability diagram for three model families."""
    import math
    x0, y0 = 42, 38
    side = min(p.w * 0.46, p.h - 62)
    p.line(x0, y0, x0 + side, y0, D.faint, 0.8)
    p.line(x0, y0, x0, y0 + side, D.faint, 0.8)
    p.line(x0, y0, x0 + side, y0 + side, D.faint, 0.9, dashed=True)
    p.text(x0 + side / 2, y0 - 13, "predicted probability", 7.0, D.muted,
           SANS, "c")
    p.text(x0 - 36, y0 + side + 3, "observed frequency", 7.0, D.muted, SANS, "l")
    p.text(x0 + side * 0.72, y0 + side * 0.60, "perfect", 6.6, D.faint,
           SANS_I, "l")

    curves = [("random forest", D.violet_bd,
               lambda t: min(1.0, max(0.0, 0.5 + 1.38 * (t - 0.5)))),
              ("neural network", D.bad_bd,
               lambda t: max(0.0, t - 0.17 * math.sin(math.pi * t))),
              ("logistic regression", D.ok_bd,
               lambda t: t + 0.02 * math.sin(3 * math.pi * t))]
    for name, col, f in curves:
        p.plot(x0, y0, side, side, f, xmax=1.0, ymax=1.0, color=col, lw=1.4)

    lx = x0 + side + 26
    yy = y0 + side - 6
    for name, col, _ in curves:
        p.line(lx, yy + 3, lx + 14, yy + 3, col, 1.6)
        p.text(lx + 19, yy, name, 7.0, D.ink, SANS_SB, "l")
        yy -= 14
    p.text(lx, yy - 6, "steeper than the diagonal", 6.8, D.muted, SANS_I, "l")
    p.text(lx, yy - 15, "\u2192 under-confident at the ends", 6.8, D.muted,
           SANS_I, "l")
    p.text(lx, yy - 30, "below the diagonal", 6.8, D.muted, SANS_I, "l")
    p.text(lx, yy - 39, "\u2192 over-confident", 6.8, D.muted, SANS_I, "l")
    p.text(0, 2, "AUC cannot see any of this: it depends only on the ordering "
           "of the scores.", 7.0, D.muted, SANS_I, "l")


@fig("explanation_map")
def explanation_map(p):
    """Two axes: scope, and model versus world."""
    x0, y0 = 60, 40
    w, h = p.w - 96, p.h - 66
    p.line(x0, y0 + h / 2, x0 + w, y0 + h / 2, D.faint, 0.7)
    p.line(x0 + w / 2, y0, x0 + w / 2, y0 + h, D.faint, 0.7)
    p.text(x0 + w / 2, y0 - 13, "describes the MODEL   \u2502   "
           "describes the WORLD", 7.0, D.muted, SANS, "c")
    p.text(x0 - 52, y0 + h - 6, "GLOBAL", 7.0, D.muted, SANS_SB, "l")
    p.text(x0 - 52, y0 + 6, "LOCAL", 7.0, D.muted, SANS_SB, "l")

    cells = [(0, 1, "permutation importance\nmean |SHAP|\nPDP  \u00b7  ALE", "teal"),
             (1, 1, "a causal model\nwith stated assumptions", "hi"),
             (0, 0, "SHAP  \u00b7  LIME\nICE\ncounterfactuals", "violet"),
             (1, 0, "a randomised experiment\n(the only real answer)", "ok")]
    for cx, cy, txt, kind in cells:
        bx = x0 + cx * (w / 2) + 5
        by = y0 + cy * (h / 2) + 5
        p.box(bx, by, w / 2 - 10, h / 2 - 10, None, kind, radius=3)
        lines = txt.split("\n")
        for k, ln in enumerate(lines):
            p.text(bx + (w / 2 - 10) / 2,
                   by + (h / 2 - 10) / 2 + (len(lines) - 1) * 5 - k * 10 - 3,
                   ln, 6.9, D.ink, SANS, "c")
    p.text(0, 2, "Reading a left-hand cell as if it were a right-hand one is "
           "the most expensive mistake in this chapter.", 7.0, D.muted,
           SANS_I, "l")


# --------------------------------------------------------------------------
# Part V — Deep Learning
# --------------------------------------------------------------------------
@fig("autograd_graph")
def autograd_graph(p):
    """Leaves, intermediates, grad_fn, and the two ways to cut it."""
    nodes = [(10, "x", "dim", "leaf\nrequires_grad=False"),
             (10, "W", "teal", "leaf\nrequires_grad=True"),
             (110, "h = x @ W", "violet", "grad_fn=MmBackward"),
             (216, "a = relu(h)", "violet", "grad_fn=ReluBackward"),
             (322, "loss", "bad", "grad_fn=MeanBackward")]
    y_hi, y_lo = p.h - 40, p.h - 76
    pos = {}
    for i, (x, label, kind, note) in enumerate(nodes):
        y = y_hi if i != 1 else y_lo
        w = 82 if i else 44
        p.box(x, y, w, 22, label, kind, size=7.4, radius=3)
        pos[label] = (x, y, w)
        for k, ln in enumerate(note.split("\n")):
            p.text(x + w / 2, y - 11 - k * 9, ln, 6.4, D.muted, SANS_I, "c")
    p.arrow(54, y_hi + 11, 108, y_hi + 11, D.arrow, 0.9, head=3.0)
    p.arrow(54, y_lo + 11, 130, y_hi - 1, D.arrow, 0.9, head=3.0)
    p.arrow(194, y_hi + 11, 214, y_hi + 11, D.arrow, 0.9, head=3.0)
    p.arrow(300, y_hi + 11, 320, y_hi + 11, D.arrow, 0.9, head=3.0)

    yb = p.h - 116
    p.arrow(p.w - 8, yb, 8, yb, D.violet_bd, 1.1, head=4, dashed=True)
    p.text(p.w / 2, yb + 5, "backward(): reverse topological order, "
           "accumulating into .grad", 7.0, D.violet_bd, SANS_SB, "c")

    p.text(0, 30, "no_grad()    the graph is never built \u2014 saves memory "
           "and time", 7.0, D.ink, SANS, "l")
    p.text(0, 19, "detach()     the graph is built, then this edge is cut",
           7.0, D.ink, SANS, "l")
    p.text(0, 2, "A tensor with a grad_fn keeps its whole history alive. "
           "Appending losses to a list without .item() leaks the epoch.",
           7.0, D.muted, SANS_I, "l")


@fig("training_signals")
def training_signals(p):
    """Six curves, three panes."""
    import math
    gap = 14
    pw = (p.w - 2 * gap) / 3
    y0, h = 46, p.h - 78
    panes = [
        ("loss", [("train", D.node_bd, lambda t: 0.12 + 0.88 * math.exp(-4 * t)),
                  ("val", D.bad_bd, lambda t: 0.22 + 0.80 * math.exp(-4.4 * t)
                   + 0.18 * max(0.0, t - 0.68))],
         "val turning up = overfitting"),
        ("gradient norm", [("pre-clip", D.violet_bd,
                            lambda t: 0.30 + 0.16 * math.sin(26 * t) *
                            math.exp(-1.2 * t) + (0.55 if 0.62 < t < 0.66 else 0.0))],
         "a spike precedes every divergence"),
        ("update ratio", [("healthy 1e-3", D.ok_bd, lambda t: 0.52 - 0.08 * t),
                          ("a frozen layer", D.faint, lambda t: 0.06)],
         "per layer, |\u0394w| / |w|"),
    ]
    for i, (title, curves, note) in enumerate(panes):
        x = i * (pw + gap)
        iw = pw - 10
        p.line(x, y0, x + iw, y0, D.faint, 0.7)
        p.line(x, y0, x, y0 + h, D.faint, 0.7)
        for name, col, f in curves:
            p.plot(x, y0, iw, h, f, xmax=1.0, ymax=1.08, color=col, lw=1.3)
        p.label_chip(x, p.h - 13, title, "teal", size=7.0)
        p.text(x + iw / 2, y0 - 12, note, 6.7, D.muted, SANS_I, "c")
        yy = y0 - 24
        for name, col, _ in curves:
            p.line(x, yy + 3, x + 10, yy + 3, col, 1.4)
            p.text(x + 14, yy, name, 6.6, D.ink, SANS, "l")
            yy -= 10
    p.text(0, 2, "Also log the learning rate and the throughput. Loss alone "
           "says something is wrong, never what.", 7.0, D.muted, SANS_I, "l")


@fig("architecture_bets")
def architecture_bets(p):
    """What each family sees when it looks at position 5."""
    rows = [("MLP", "dim", [1] * 9, "no structure at all;\nmust learn every invariance"),
            ("Convolution", "teal", [0, 0, 1, 1, 1, 0, 0, 0, 0],
             "a fixed local window;\nsame weights everywhere"),
            ("Recurrence", "hi", [.25, .35, .5, .7, 1, 0, 0, 0, 0],
             "a compressed running state;\nolder inputs fade"),
            ("Attention", "violet", [.3, .1, .9, .15, 1, .05, .4, .1, .2],
             "every position, weighted\nby content")]
    cw = 20
    x0 = 92
    y = p.h - 36
    p.text(x0 + 4 * cw + cw / 2, p.h - 12, "\u2193  computing the output at "
           "position 5", 6.9, D.muted, SANS_I, "c")
    for name, kind, weights, note in rows:
        p.text(x0 - 10, y + 6, name, 7.4, D.ink, SANS_SB, "r")
        for j, w in enumerate(weights):
            if w <= 0:
                p.box(x0 + j * cw, y, cw - 3, 16, None, "white", radius=2)
            else:
                p.box(x0 + j * cw, y, cw - 3, 16, None, kind, radius=2)
                p.text(x0 + j * cw + (cw - 3) / 2, y + 5,
                       "%.0f" % (w * 100) if w < 1 else "\u25cf", 6.0,
                       D.muted if w < 1 else D.ink, SANS, "c")
        for k, ln in enumerate(note.split("\n")):
            p.text(x0 + 9 * cw + 8, y + 10 - k * 9, ln, 6.6, D.muted,
                   SANS_I, "l")
        y -= 30
    p.text(0, 2, "Shaded = this input influences the output. The numbers are "
           "relative weights; a dot means full weight.", 7.0, D.muted,
           SANS_I, "l")


@fig("transformer_block")
def transformer_block(p):
    """The residual stream, and what hangs off it."""
    cx = 118
    top, bot = p.h - 16, 20
    p.line(cx, bot, cx, top, D.node_bd, 2.2)
    p.text(cx, top + 2, "residual stream", 7.0, D.node_bd, SANS_SB, "c")

    def junction(y, label, sub, kind):
        p.circle(cx, y, 7.5, "+", "white", size=8.0, lw=1.2)
        bx = cx + 54
        p.box(bx, y - 15, 200, 30, None, kind, radius=3)
        p.text(bx + 100, y + 3, label, 7.4, D.ink, SANS_SB, "c")
        p.text(bx + 100, y - 8, sub, 6.7, D.muted, SANS, "c")
        p.arrow(cx + 8, y + 12, bx - 2, y + 8, D.arrow, 0.9, head=3.0)
        p.arrow(bx - 2, y - 8, cx + 8, y - 4, D.arrow, 0.9, head=3.0)
        p.text(cx + 14, y + 16, "read", 6.2, D.faint, SANS_I, "l")
        p.text(cx + 14, y - 16, "add back", 6.2, D.faint, SANS_I, "l")

    junction(p.h - 52, "RMSNorm \u2192 Attention",
             "moves information ACROSS positions", "violet")
    junction(p.h - 118, "RMSNorm \u2192 SwiGLU",
             "transforms information AT a position", "teal")
    p.box(cx - 62, 24, 124, 22, "\u00d7 N layers", "dim", size=7.2,
          radius=3)
    p.text(0, 2, "Nothing overwrites the stream \u2014 every sublayer reads a "
           "normalised copy and adds an increment back.", 7.0, D.muted,
           SANS_I, "l")


@fig("gqa")
def gqa(p):
    """MHA, GQA, MQA side by side."""
    variants = [("MHA", 8, 8, "21.5 GB", "teal"),
                ("GQA, 4\u00d7 sharing", 8, 2, "5.4 GB", "violet"),
                ("MQA, 8\u00d7 sharing", 8, 1, "2.7 GB", "hi")]
    gap = 22
    pw = (p.w - 2 * gap) / 3
    qw = 15
    for i, (name, nq, nkv, cache, kind) in enumerate(variants):
        x = i * (pw + gap)
        p.label_chip(x, p.h - 14, name, kind, size=7.2)
        yq = p.h - 44
        for j in range(nq):
            p.box(x + j * (qw + 2), yq, qw, 14, None, "dim", radius=2)
        p.text(x, yq - 11, "%d query heads" % nq, 6.6, D.muted, SANS, "l")

        ykv = yq - 44
        share = nq // nkv
        for j in range(nkv):
            bw = (qw + 2) * share - 2
            p.box(x + j * (qw + 2) * share, ykv, bw, 14, None, kind, radius=2)
        p.text(x, ykv - 11, "%d KV head%s" % (nkv, "" if nkv == 1 else "s"),
               6.6, D.muted, SANS, "l")
        for j in range(nq):
            p.line(x + j * (qw + 2) + qw / 2, yq - 1,
                   x + (j // share) * (qw + 2) * share +
                   ((qw + 2) * share - 2) / 2, ykv + 15, D.faint, 0.5)
        p.text(x, ykv - 26, "cache: " + cache, 7.0, D.ink, SANS_SB, "l")
    p.text(0, 2, "Eight query heads shown for legibility; the cache figures "
           "are a 70B-class model at 8k context, batch 1, scaled by the same "
           "sharing factors.", 6.9, D.muted, SANS_I, "l")


@fig("debug_tree")
def debug_tree(p):
    """The triage order."""
    steps = [("1", "Can it overfit 8 examples?",
              "no \u2192 the bug is in the MODEL or the LOSS",
              "detached graph \u00b7 wrong mask \u00b7 frozen layer \u00b7 "
              "double softmax", "bad"),
             ("2", "Is the data what you think?",
              "no \u2192 decode the tokens back to text",
              "shuffled labels \u00b7 off-by-one \u00b7 wrong dtype \u00b7 "
              "all-zero inputs", "hi"),
             ("3", "Are gradients flowing?",
              "no \u2192 find the disconnected parameter",
              "p.grad is None \u00b7 grad norm < 1e-8 \u00b7 dead ReLUs",
              "violet"),
             ("4", "Only now: tune.",
              "learning rate \u00b7 schedule \u00b7 batch \u00b7 capacity",
              "tuning before steps 1\u20133 wastes hours", "ok")]
    y = p.h - 40
    for num, q, verdict, examples, kind in steps:
        p.box(0, y, p.w, 34, None, kind, radius=3)
        p.circle(18, y + 17, 11, num, "white", size=8.0, lw=1.0)
        p.text(36, y + 21, q, 7.6, D.ink, SANS_SB, "l")
        p.text(36, y + 10, verdict, 6.9, D.ink, SANS, "l")
        p.text(36, y + 1, examples, 6.6, D.muted, SANS_I, "l")
        if y > 60:
            p.arrow(p.w / 2, y - 2, p.w / 2, y - 8, D.arrow, 0.9, head=3.4)
        y -= 42
    p.text(0, 2, "Roughly 60% of \u201cit will not learn\u201d is caught by "
           "step 1, in about thirty seconds.", 7.0, D.muted, SANS_I, "l")


@fig("parallelism_axes")
def parallelism_axes(p):
    """Four axes, what each splits, and where to put it."""
    axes = [("DATA", "teal", "each device: whole model,\ndifferent batch slice",
             "all-reduce 2P per step", "across nodes"),
            ("ZeRO / FSDP", "violet", "model state sharded,\ngathered just in time",
             "gather \u00d72 + reduce \u00d71", "across nodes"),
            ("TENSOR", "hi", "each matrix split\nacross devices",
             "all-reduce INSIDE every layer", "inside a node"),
            ("PIPELINE", "ok", "different layers on\ndifferent devices",
             "activations at boundaries", "across node groups")]
    bw = (p.w - 3 * 8) / 4
    y = p.h - 96
    for i, (name, kind, what, comm, where) in enumerate(axes):
        x = i * (bw + 8)
        p.box(x, y, bw, 86, None, kind, radius=3)
        p.text(x + bw / 2, y + 72, name, 7.6, D.ink, SANS_SB, "c")
        for k, ln in enumerate(what.split("\n")):
            p.text(x + bw / 2, y + 56 - k * 9, ln, 6.6, D.ink, SANS, "c")
        p.line(x + 8, y + 34, x + bw - 8, y + 34, D.faint, 0.5)
        p.text(x + bw / 2, y + 23, "COMMUNICATION", 6.0, D.faint, SANS_SB, "c")
        for k, ln in enumerate(_wrap(comm, 24)):
            p.text(x + bw / 2, y + 13 - k * 8.5, ln, 6.5, D.ink, SANS, "c")
        p.text(x + bw / 2, y - 12, where, 6.9, D.muted, SANS_I, "c")
    p.text(p.w / 2, y - 26, "put the chattiest parallelism on the fastest "
           "interconnect", 7.2, D.node_bd, SANS_SB, "c")
    p.text(0, 2, "They compose: a large run is typically DATA across nodes, "
           "TENSOR inside a node, PIPELINE across node groups.", 7.0,
           D.muted, SANS_I, "l")


# --------------------------------------------------------------------------
# Part VI — Foundation Models
# --------------------------------------------------------------------------
@fig("tokenisation")
def tokenisation(p):
    """The same meaning, different token counts."""
    rows = [("English prose", "The refund window is thirty days.", 4.0, "teal"),
            ("Python code", 'if x is None: raise ValueError("x")', 3.0, "violet"),
            ("JSON", '{"customer_id": "CUST-004218"}', 2.5, "hi"),
            ("Chinese / Japanese", "\u9000\u6b3e\u671f\u9650\u4e3a\u4e09\u5341\u5929\u3002", 1.5, "bad"),
            ("Hindi / Thai", "\u0935\u093e\u092a\u0938\u0940 \u0915\u0940 \u0905\u0935\u0927\u093f \u0924\u0940\u0938 \u0926\u093f\u0928", 1.0, "bad")]
    lx, bx = 108, 250
    y = p.h - 30
    p.text(6, p.h - 14, "CONTENT TYPE", 6.5, D.faint, SANS_SB, "l")
    p.text(lx + 4, p.h - 14, "chars / token", 6.5, D.faint, SANS_SB, "l")
    p.text(bx, p.h - 14, "tokens per 1000 characters", 6.5, D.faint, SANS_SB, "l")
    maxt = 1000
    for name, sample, cpt, kind in rows:
        toks = int(1000 / cpt)
        p.text(6, y + 7, name, 7.2, D.ink, SANS_SB, "l")
        p.text(6, y - 2, sample[:34], 6.3, D.muted, MONO, "l")
        p.text(lx + 30, y + 3, "%.1f" % cpt, 7.2, D.ink, SANS, "r")
        bw = (p.w - bx) * toks / maxt
        p.box(bx, y, max(bw, 2), 13, None, kind, radius=2)
        p.text(bx + max(bw, 2) + 5, y + 3, "%d" % toks, 6.8, D.ink, SANS_SB, "l")
        y -= 24
    p.text(0, 2, "You pay per token and the context window is counted in "
           "tokens, so the same document costs four times as much in some "
           "languages.", 6.9, D.muted, SANS_I, "l")


@fig("prefill_decode")
def prefill_decode(p):
    """Two phases, two regimes."""
    half = (p.w - 26) / 2
    panes = [("PREFILL", "teal", [
                  ("all T prompt tokens at once", None),
                  ("matmul  (T\u00d7d)\u00b7(d\u00d7d)", None),
                  ("arithmetic intensity: HIGH", None),
                  ("COMPUTE-BOUND", "ok"),
                  ("GPU utilisation 40\u201370%", None),
                  ("sets time-to-first-token", None)]),
              ("DECODE", "hi", [
                  ("one token per step", None),
                  ("matvec  (1\u00d7d)\u00b7(d\u00d7d)", None),
                  ("arithmetic intensity: \u2248 1", None),
                  ("MEMORY-BOUND", "bad"),
                  ("GPU utilisation 1\u201310% at batch 1", None),
                  ("sets tokens per second", None)])]
    for i, (title, kind, lines) in enumerate(panes):
        x = i * (half + 26)
        p.box(x, p.h - 26, half, 22, title, kind, size=8.0, radius=3)
        y = p.h - 48
        for text, hl in lines:
            if hl:
                p.box(x + 6, y - 3, half - 12, 15, None, hl, radius=2)
                p.text(x + half / 2, y + 2, text, 7.2, D.ink, SANS_SB, "c")
            else:
                p.text(x + 10, y + 2, "\u00b7  " + text, 6.9, D.ink, SANS, "l")
            y -= 19
    p.text(0, 16, "Batching helps prefill modestly and decode enormously \u2014 "
           "the weights are read once per STEP, not once per sequence.", 7.0,
           D.ink, SANS, "l")
    p.text(0, 2, "At batch 1 a decode step does useful arithmetic about 0.3% of "
           "the time. Serving stacks exist to fill the rest.", 7.0, D.muted,
           SANS_I, "l")


@fig("prompt_loop")
def prompt_loop(p):
    """The development loop, with the failure log at its centre."""
    steps = [("write / edit\nthe prompt", "teal"),
             ("run the\neval set", "violet"),
             ("read the\nfailures", "hi"),
             ("add them to\nthe eval set", "ok")]
    bw = (p.w - 3 * 30) / 4
    y = p.h - 56
    for i, (label, kind) in enumerate(steps):
        x = i * (bw + 30)
        p.box(x, y, bw, 42, None, kind, radius=3)
        for k, ln in enumerate(label.split("\n")):
            p.text(x + bw / 2, y + 26 - k * 11, ln, 7.2, D.ink, SANS_SB, "c")
        if i:
            p.arrow(x - 28, y + 21, x - 3, y + 21, D.arrow, 1.0, head=3.4)
    # the loop back
    p.line(p.w - bw / 2, y - 3, p.w - bw / 2, y - 16, D.arrow, 1.0)
    p.line(p.w - bw / 2, y - 16, bw / 2, y - 16, D.arrow, 1.0)
    p.arrow(bw / 2, y - 16, bw / 2, y - 3, D.arrow, 1.0, head=3.4)
    p.text(p.w / 2, y - 26, "every production failure becomes an eval case",
           7.0, D.node_bd, SANS_SB, "c")
    p.text(0, 2, "Without the eval set, every step after the first is "
           "guesswork \u2014 and most apparent improvements are inside the "
           "confidence interval.", 6.9, D.muted, SANS_I, "l")


@fig("constrained_decoding")
def constrained_decoding(p):
    """Masking illegal tokens before the softmax."""
    p.text(0, p.h - 12, 'generated so far:   {"category": "', 7.4, D.ink,
           MONO, "l")
    toks = [("bill", True), ("ship", True), ("prod", True), ("acc", True),
            ("other", True), ("The", False), ("\u00a0  42", False),
            ("maybe", False), ("</", False)]
    cw = (p.w - 60) / len(toks)
    y = p.h - 46
    for i, (t, legal) in enumerate(toks):
        x = i * cw
        p.box(x, y, cw - 4, 18, t, "ok" if legal else "dim", size=6.8, radius=2)
        p.text(x + (cw - 4) / 2, y - 11, "\u2713" if legal else "\u2717",
               7.4, D.ok_bd if legal else D.bad_bd, SANS_SB, "c")
    p.text(p.w - 44, y + 5, "logits", 6.8, D.muted, SANS_I, "l")

    y2 = y - 40
    for i, (t, legal) in enumerate(toks):
        x = i * cw
        if legal:
            p.box(x, y2, cw - 4, 18, t, "ok", size=6.8, radius=2)
        else:
            p.box(x, y2, cw - 4, 18, "\u2212\u221e", "bad", size=7.0, radius=2)
    p.text(p.w - 44, y2 + 5, "masked", 6.8, D.muted, SANS_I, "l")
    p.arrow(p.w / 2, y - 16, p.w / 2, y2 + 22, D.arrow, 1.0, head=3.4)
    p.text(p.w / 2 + 8, y - 28, "the grammar\u2019s legal set for this state",
           6.8, D.muted, SANS_I, "l")
    p.text(0, 14, "softmax over the masked logits \u2192 illegal tokens have "
           "probability exactly zero", 7.2, D.node_bd, SANS_SB, "l")
    p.text(0, 2, "Invalid output becomes impossible rather than unlikely. The "
           "mask is cached per state, so the cost is negligible.", 6.9,
           D.muted, SANS_I, "l")


@fig("hybrid_retrieval")
def hybrid_retrieval(p):
    """Two retrievers, fusion, reranking."""
    p.box(0, p.h - 26, 84, 22, "query", "dim", size=7.4, radius=3)
    p.box(104, p.h - 14, 118, 20, "BM25  (lexical)", "teal", size=7.2, radius=3)
    p.box(104, p.h - 40, 118, 20, "dense  (embedding)", "violet", size=7.2,
          radius=3)
    p.text(226, p.h - 8, "exact terms, codes, names", 6.5, D.muted, SANS_I, "l")
    p.text(226, p.h - 34, "paraphrase, meaning", 6.5, D.muted, SANS_I, "l")
    p.arrow(86, p.h - 15, 102, p.h - 4, D.arrow, 0.9, head=3.0)
    p.arrow(86, p.h - 15, 102, p.h - 30, D.arrow, 0.9, head=3.0)

    y = p.h - 78
    p.box(70, y, 180, 22, "reciprocal rank fusion", "hi", size=7.4, radius=3)
    p.text(256, y + 7, "100 candidates", 6.8, D.muted, SANS_I, "l")
    p.arrow(163, p.h - 14, 163, y + 24, D.arrow, 0.9, head=3.0)

    y2 = y - 34
    p.box(70, y2, 180, 22, "cross-encoder rerank", "ok", size=7.4, radius=3)
    p.text(256, y2 + 7, "top 8", 6.8, D.muted, SANS_I, "l")
    p.arrow(160, y - 2, 160, y2 + 24, D.arrow, 0.9, head=3.0)

    p.text(0, 20, "cost per document rises at each stage; the candidate set "
           "shrinks to match", 7.0, D.ink, SANS, "l")
    p.text(0, 2, "A dense-only retriever fails exact-string queries silently, "
           "returning plausible and wrong passages.", 6.9, D.muted, SANS_I, "l")


@fig("rag_pipeline")
def rag_pipeline(p):
    """Seven stages, seven metrics."""
    stages = [("parse", "extraction fidelity", "dim"),
              ("chunk", "boundary quality", "dim"),
              ("index", "coverage", "dim"),
              ("retrieve", "recall@k", "bad"),
              ("rerank", "precision@k", "violet"),
              ("generate", "faithfulness", "bad"),
              ("cite", "citation accuracy", "teal")]
    gap = 4
    bw = (p.w - gap * (len(stages) - 1)) / len(stages)
    y = p.h - 40
    for i, (name, metric, kind) in enumerate(stages):
        x = i * (bw + gap)
        p.box(x, y, bw, 24, name, kind, size=7.0, radius=3)
        for k, ln in enumerate(_wrap(metric, 13)):
            p.text(x + bw / 2, y - 11 - k * 8.5, ln, 6.3, D.muted, SANS_I, "c")
        if i:
            p.arrow(x - gap + 0.5, y + 12, x - 1, y + 12, D.arrow, 0.8, head=2.6)
    p.text(p.w / 2, p.h - 12, "INGEST  \u2502  QUERY TIME", 6.6, D.faint,
           SANS_SB, "c")
    p.line(3 * (bw + gap) - gap / 2, y - 30, 3 * (bw + gap) - gap / 2,
           p.h - 6, D.faint, 0.6, dashed=True)

    y2 = y - 48
    rows = [("recall low, correctness low", "fix RETRIEVAL", "bad"),
            ("recall high, correctness low", "fix GENERATION", "violet"),
            ("correct but unfaithful", "it used parametric knowledge", "hi"),
            ("refusals high, recall high", "the prompt is too conservative", "teal")]
    for i, (pattern, verdict, kind) in enumerate(rows):
        yy = y2 - i * 15
        p.box(0, yy, p.w, 13, None, kind, radius=2)
        p.text(8, yy + 3.5, pattern, 6.8, D.ink, SANS, "l")
        p.text(p.w - 8, yy + 3.5, verdict, 6.8, D.ink, SANS_SB, "r")
    p.text(0, 2, "An end-to-end score alone cannot be debugged: any of the "
           "seven stages could be responsible.", 6.9, D.muted, SANS_I, "l")


@fig("adaptation_ladder_hb")
def adaptation_ladder_hb(p):
    """Rungs, with effort and what each fixes."""
    rungs = [("prompt + few-shot", "hours", "format, tone", "teal", 0.14),
             ("structured output + tools", "days", "validity, actions", "teal", 0.26),
             ("retrieval", "days\u2013weeks", "missing knowledge", "violet", 0.42),
             ("LoRA fine-tune", "1\u20132 weeks", "persistent style, domain", "hi", 0.60),
             ("full fine-tune", "weeks", "deep behaviour change", "hi", 0.76),
             ("preference optimisation", "weeks", "subjective quality", "bad", 0.88),
             ("pre-training", "months", "a new base capability", "bad", 1.00)]
    nx, barx, barw = 122, 136, 86
    ex, fx = 234, 288
    p.text(nx, p.h - 13, "RUNG", 6.4, D.faint, SANS_SB, "r")
    p.text(barx, p.h - 13, "RELATIVE EFFORT", 6.4, D.faint, SANS_SB, "l")
    p.text(ex, p.h - 13, "TIME", 6.4, D.faint, SANS_SB, "l")
    p.text(fx, p.h - 13, "WHAT IT FIXES", 6.4, D.faint, SANS_SB, "l")
    p.line(0, p.h - 18, p.w, p.h - 18, D.faint, 0.5)

    y = 28
    for name, effort, fixes, kind, frac in rungs:
        p.text(nx, y + 4, name, 7.1, D.ink, SANS_SB, "r")
        p.box(barx, y, max(barw * frac, 3), 13, None, kind, radius=2)
        p.text(ex, y + 4, effort, 6.8, D.muted, SANS, "l")
        p.text(fx, y + 4, fixes, 6.8, D.ink, SANS, "l")
        y += 19
    p.arrow(barx - 4, 26, barx - 4, y - 6, D.node_bd, 1.0, head=3.4)
    p.text(0, 14, "\u2191  each rung costs roughly 10\u00d7 the one below, and "
           "most teams climb at least one too far", 7.0, D.node_bd, SANS_SB, "l")
    p.text(0, 2, "Climb only when the rung below has been measured, not merely "
           "attempted.", 6.9, D.muted, SANS_I, "l")


@fig("rlhf_pipeline")
def rlhf_pipeline(p):
    """Three stages, and where DPO cuts across."""
    stages = [("1  SFT", "teal", "demonstrations",
               "a policy worth\nimproving"),
              ("2  REWARD MODEL", "violet", "preference pairs",
               "Bradley\u2013Terry on\nscore differences"),
              ("3  PPO", "hi", "prompts",
               "maximise reward,\nKL leash to ref")]
    gap = 14
    bw = (p.w - 2 * gap) / 3
    y = p.h - 86
    for i, (name, kind, inp, what) in enumerate(stages):
        x = i * (bw + gap)
        p.box(x, y, bw, 62, None, kind, radius=3)
        p.text(x + bw / 2, y + 46, name, 7.8, D.ink, SANS_SB, "c")
        p.text(x + bw / 2, y + 34, "input: " + inp, 6.6, D.muted, SANS_I, "c")
        for k, ln in enumerate(what.split("\n")):
            p.text(x + bw / 2, y + 18 - k * 10, ln, 6.9, D.ink, SANS, "c")
        if i:
            p.arrow(x - gap + 1, y + 31, x - 2, y + 31, D.arrow, 1.0, head=3.4)
    p.text(p.w / 2, p.h - 14, "CLASSICAL RLHF \u2014 four models in memory, "
           "unstable, gameable", 7.4, D.ink, SANS_SB, "c")

    yd = y - 34
    p.box(bw + gap, yd, bw * 2 + gap, 22, None, "ok", radius=3)
    p.text(bw + gap + (bw * 2 + gap) / 2, yd + 7,
           "DPO replaces BOTH of these with one supervised loss", 7.2,
           D.ok_bd, SANS_SB, "c")
    p.text(0, 2, "GRPO keeps stage 3 but drops the value model, using a "
           "group-relative baseline \u2014 and pairs with verifiable rewards.",
           6.9, D.muted, SANS_I, "l")


# --------------------------------------------------------------------------
# Part VII — Making It Real
# --------------------------------------------------------------------------
@fig("eval_system")
def eval_system(p):
    """The loop: production feeds the set, the set gates production."""
    boxes = [("PRODUCTION", "dim", 6, p.h - 34, 96, 26),
             ("failure log", "bad", 128, p.h - 34, 96, 26),
             ("GOLDEN SET", "teal", 250, p.h - 34, p.w - 256, 26),
             ("graders", "violet", 250, p.h - 78, p.w - 256, 26),
             ("CI gate", "ok", 128, p.h - 78, 96, 26),
             ("deploy", "hi", 6, p.h - 78, 96, 26)]
    for label, kind, x, y, w, h in boxes:
        p.box(x, y, w, h, label, kind, size=7.4, radius=3)
    p.arrow(104, p.h - 21, 126, p.h - 21, D.arrow, 1.0, head=3.2)
    p.arrow(226, p.h - 21, 248, p.h - 21, D.arrow, 1.0, head=3.2)
    p.arrow(p.w - 3, p.h - 36, p.w - 3, p.h - 50, D.arrow, 1.0, head=3.2)
    p.arrow(248, p.h - 65, 226, p.h - 65, D.arrow, 1.0, head=3.2)
    p.arrow(126, p.h - 65, 104, p.h - 65, D.arrow, 1.0, head=3.2)
    p.arrow(54, p.h - 80, 54, p.h - 36, D.arrow, 1.0, head=3.2)
    p.text(115, p.h - 12, "every failure", 6.4, D.muted, SANS_I, "c")
    p.text(115, p.h - 92, "pass / block", 6.4, D.muted, SANS_I, "c")

    y2 = p.h - 110
    notes = ["100\u20131000 real cases, stratified, hard ones over-represented",
             "cheapest grader that answers the question; judges validated "
             "against humans",
             "merge blocked on a 3-point regression; safety blocked on ANY "
             "regression"]
    for i, n in enumerate(notes):
        p.text(0, y2 - i * 11, "\u00b7  " + n, 6.9, D.ink, SANS, "l")
    p.text(0, 2, "A static evaluation set decays. The loop is the point.",
           7.0, D.muted, SANS_I, "l")


@fig("eval_uncertainty")
def eval_uncertainty(p):
    """Three sources of uncertainty, stacking."""
    layers = [("sampling", "which cases you happened to draw", 0.30, "teal"),
              ("+ clustering", "how many are really independent", 0.58, "violet"),
              ("+ grader error", "whether the label itself is right", 1.00, "bad")]
    cx = p.w * 0.46
    y = p.h - 40
    for name, note, frac, kind in layers:
        half = (p.w * 0.40) * frac / 2
        p.line(cx - half, y, cx + half, y, D.node_bd, 1.5)
        p.line(cx - half, y - 5, cx - half, y + 5, D.node_bd, 1.5)
        p.line(cx + half, y - 5, cx + half, y + 5, D.node_bd, 1.5)
        p.circle(cx, y, 3.4, None, kind, lw=1.0)
        p.text(cx - half - 8, y - 3, name, 7.2, D.ink, SANS_SB, "r")
        p.text(cx + p.w * 0.21, y - 3, note, 6.8, D.muted, SANS_I, "l")
        y -= 34
    p.text(cx, p.h - 14, "the true value is somewhere in here", 6.8, D.faint,
           SANS_I, "c")
    p.text(0, 14, "A naive binomial interval reports only the first row \u2014 "
           "often half the real width.", 7.0, D.ink, SANS, "l")
    p.text(0, 2, "Grader error largely cancels in a PAIRED comparison, unless "
           "it correlates with what changed.", 7.0, D.muted, SANS_I, "l")


@fig("agent_reliability")
def agent_reliability(p):
    """Task success against step count."""
    x0, y0 = 40, 36
    w, h = p.w - 118, p.h - 58
    p.line(x0, y0, x0 + w, y0, D.faint, 0.8)
    p.line(x0, y0, x0, y0 + h, D.faint, 0.8)
    p.text(x0 + w / 2, y0 - 13, "steps in the task", 7.0, D.muted, SANS, "c")
    p.text(x0 - 32, y0 + h + 3, "task success", 7.0, D.muted, SANS, "l")
    NMAX = 20
    for r, col, lab in ((0.90, D.bad_bd, "r = 0.90"), (0.95, D.hi_bd, "r = 0.95"),
                        (0.99, D.violet_bd, "r = 0.99"),
                        (0.999, D.ok_bd, "r = 0.999")):
        p.plot(x0, y0, w, h, lambda t, rr=r: rr ** max(t * NMAX, 1e-9),
               xmax=1.0, ymax=1.0, color=col, lw=1.4)
        p.text(x0 + w + 5, y0 + h * (r ** NMAX) - 2.5, lab, 6.9, col,
               SANS_SB, "l")
    for n in (5, 10, 20):
        p.line(x0 + w * n / NMAX, y0, x0 + w * n / NMAX, y0 + h, D.faint, 0.4,
               dashed=True)
        p.text(x0 + w * n / NMAX, y0 - 5, str(n), 6.6, D.muted, SANS, "c")
    p.text(0, 2, "Nothing about the loop changes this curve. Only shortening "
           "the task, raising per-step reliability, or verifying each step "
           "does.", 6.9, D.muted, SANS_I, "l")


@fig("continuous_batching")
def continuous_batching(p):
    """Static versus continuous batching occupancy."""
    rows, cols = 5, 24
    lens = [5, 13, 8, 20, 4]
    cw = (p.w - 56) / cols
    rh, rgap = 8.0, 2.4
    panel_h = rows * (rh + rgap)

    for panel, (title, kind) in enumerate([("STATIC batching", "bad"),
                                           ("CONTINUOUS batching", "ok")]):
        top = p.h - 14 - panel * (panel_h + 30)
        p.label_chip(0, top, title, kind, size=7.0)
        note = ("hairlines = idle GPU, waiting for the longest sequence"
                if panel == 0 else
                "a new request enters the instant a slot frees")
        p.text(108, top + 1, note, 6.6,
               D.bad_bd if panel == 0 else D.ok_bd, SANS_I, "l")
        for r in range(rows):
            y = top - 14 - r * (rh + rgap)
            p.text(50, y + 1.2, "slot %d" % (r + 1), 6.2, D.muted, SANS, "r")
            if panel == 0:
                for c in range(cols):
                    if c < lens[r]:
                        p.box(56 + c * cw, y, cw - 1.1, rh, None, "teal",
                              radius=1)
                    else:
                        p.line(56 + c * cw, y + rh / 2,
                               56 + (c + 1) * cw - 1.1, y + rh / 2,
                               D.faint, 0.6)
            else:
                c, seq = 0, 0
                while c < cols:
                    ln = lens[(r + seq) % rows]
                    kk = ["teal", "violet", "hi", "ok", "dim"][seq % 5]
                    for j in range(min(ln, cols - c)):
                        p.box(56 + (c + j) * cw, y, cw - 1.1, rh, None, kk,
                              radius=1)
                    c += ln
                    seq += 1
    p.text(0, 2, "Same hardware, same model, identical outputs. Typically "
           "2\u20134\u00d7 the throughput.", 7.0, D.muted, SANS_I, "l")


@fig("deployment_stages")
def deployment_stages(p):
    """The deployment ladder."""
    stages = [("offline eval", "0%", "quality regressions", "dim", 0.12),
              ("SHADOW", "100% mirrored", "skew, latency, crashes", "teal", 0.40),
              ("CANARY", "1\u20135%", "real-world quality, rare inputs", "violet", 0.58),
              ("progressive", "5 \u2192 50%", "load-dependent problems", "hi", 0.80),
              ("full", "100%", "\u2014", "ok", 1.00)]
    bh = 22
    y = 30
    for name, traffic, catches, kind, frac in stages:
        p.box(0, y, (p.w * 0.30) * frac, bh, None, kind, radius=2)
        p.text(6, y + 7, name, 7.2, D.ink, SANS_SB, "l")
        p.text(p.w * 0.33, y + 7, traffic, 6.9, D.muted, SANS, "l")
        p.text(p.w * 0.55, y + 7, catches, 6.9, D.ink, SANS, "l")
        y += bh + 4
    p.text(p.w * 0.33, 18, "USER EXPOSURE", 6.4, D.faint, SANS_SB, "l")
    p.text(p.w * 0.55, 18, "WHAT IT CATCHES", 6.4, D.faint, SANS_SB, "l")
    p.arrow(-6, 30, -6, y - 4, D.node_bd, 1.0, head=3.4) if False else None
    p.text(0, y + 4, "\u2191  exposure and required evidence both rise",
           7.0, D.node_bd, SANS_SB, "l")
    p.text(0, 2, "Shadow is the stage most often skipped and the one that "
           "catches the most \u2014 identical live traffic, zero user risk.",
           6.9, D.muted, SANS_I, "l")


@fig("gpu_hierarchy")
def gpu_hierarchy(p):
    """Size and bandwidth across the hierarchy."""
    levels = [("registers", "256 KB", "100 TB/s", "ok", 0.12),
              ("shared memory / L1", "228 KB", "30 TB/s", "teal", 0.22),
              ("L2 cache", "50 MB", "10 TB/s", "violet", 0.38),
              ("HBM", "80\u2013192 GB", "3\u20138 TB/s", "hi", 0.62),
              ("host RAM over PCIe", "TB", "60 GB/s", "bad", 0.84),
              ("NVMe", "TB", "7 GB/s", "bad", 1.00)]
    bh = 20
    y = 28
    for name, size, bw, kind, frac in levels:
        w = (p.w * 0.34) * frac
        p.box(0, y, w, bh, None, kind, radius=2)
        p.text(6, y + 6, name, 7.1, D.ink, SANS_SB, "l")
        p.text(p.w * 0.38, y + 6, size, 6.9, D.muted, SANS, "l")
        p.text(p.w * 0.56, y + 6, bw, 6.9, D.ink, MONO, "l")
        y += bh + 3
    p.text(p.w * 0.38, 16, "SIZE", 6.4, D.faint, SANS_SB, "l")
    p.text(p.w * 0.56, 16, "BANDWIDTH", 6.4, D.faint, SANS_SB, "l")
    p.text(p.w * 0.78, 16, "\u2191 bigger / slower", 6.4, D.faint, SANS_I, "l")
    p.text(0, y + 4, "shared memory is ~10\u00d7 HBM; PCIe is ~50\u00d7 "
           "slower than HBM", 7.0, D.node_bd, SANS_SB, "l")
    p.text(0, 2, "Almost all performance work is moving data up this diagram "
           "and keeping it there.", 6.9, D.muted, SANS_I, "l")


# --------------------------------------------------------------------------
# Part VIII — Judgement
# --------------------------------------------------------------------------
@fig("injection_surface")
def injection_surface(p):
    """The trust boundary, and what crosses it."""
    p.box(0, 30, p.w * 0.46, p.h - 50, None, "bad", radius=4)
    p.text(p.w * 0.23, p.h - 26, "UNTRUSTED", 7.6, D.bad_bd, SANS_SB, "c")
    p.text(p.w * 0.23, p.h - 38, "anything you do not control", 6.6, D.muted,
           SANS_I, "c")
    items = ["user messages", "retrieved documents", "fetched web pages",
             "tool results", "uploaded files", "emails, calendar invites",
             "code comments", "stored memory"]
    for i, it in enumerate(items):
        p.text(10, p.h - 56 - i * 11, "\u00b7 " + it, 6.9, D.ink, SANS, "l")

    bx = p.w * 0.54
    p.box(bx, 30, p.w - bx, p.h - 50, None, "ok", radius=4)
    p.text(bx + (p.w - bx) / 2, p.h - 26, "PRIVILEGED", 7.6, D.ok_bd,
           SANS_SB, "c")
    p.text(bx + (p.w - bx) / 2, p.h - 38, "what an injection must not reach",
           6.6, D.muted, SANS_I, "c")
    caps = ["write tools", "outbound network", "secrets and credentials",
            "other users\u2019 data", "money movement", "irreversible actions"]
    for i, it in enumerate(caps):
        p.text(bx + 10, p.h - 56 - i * 11, "\u00b7 " + it, 6.9, D.ink, SANS, "l")

    mx = p.w * 0.50
    p.line(mx, 26, mx, p.h - 16, D.node_bd, 1.6, dashed=True)
    p.text(mx, p.h - 10, "THE BOUNDARY", 7.0, D.node_bd, SANS_SB, "c")
    p.text(mx, 19, "only schema-validated data crosses", 6.8, D.node_bd,
           SANS_SB, "c")
    p.text(0, 11, "You cannot keep instructions out of the left-hand box. You "
           "can ensure one that gets through reaches nothing on the right.",
           7.0, D.ink, SANS, "l")
    p.text(0, 2, "Authorise at the tool, using the USER\u2019s permissions "
           "\u2014 never the model\u2019s request.", 6.9, D.muted, SANS_I, "l")


@fig("scoping_questions")
def scoping_questions(p):
    """Seven questions, and what each one kills."""
    qs = [("1", "What decision changes?", "nothing \u2192 stop here", "bad"),
          ("2", "What happens today?", "that is your baseline, not zero", "bad"),
          ("3", "What does an error cost?", "sets the threshold, and the design",
           "bad"),
          ("4", "How accurate to be worth using?",
           "agree it BEFORE building", "hi"),
          ("5", "Was the data made by today\u2019s process?",
           "then you model the process, not the truth", "hi"),
          ("6", "Who acts on it, and will they trust it?",
           "involve them now, not at launch", "violet"),
          ("7", "What is the fallback?", "design it before the model", "teal")]
    y = p.h - 34
    for num, q, note, kind in qs:
        p.box(0, y, p.w, 20, None, kind, radius=2)
        p.circle(13, y + 10, 8, num, "white", size=7.2, lw=0.9)
        p.text(28, y + 6.5, q, 7.3, D.ink, SANS_SB, "l")
        p.text(p.w - 8, y + 6.5, note, 6.8, D.muted, SANS_I, "r")
        y -= 24
    p.text(0, 2, "A project that cannot answer the first three should not "
           "start, however good the data is.", 7.0, D.muted, SANS_I, "l")


@fig("decision_tree_ml")
def decision_tree_ml(p):
    """Where most proposals terminate."""
    nodes = [("Are the rules known and stable?", "write the rules", 0),
             ("Do you have \u2265 1000 labelled examples?",
              "prompt a foundation model, or collect data", 1),
             ("Is the target above the noise floor?",
              "renegotiate the target", 2),
             ("Does a decision actually change?", "stop \u2014 no value", 3),
             ("Is the blocker technical, not organisational?",
              "fix the process first", 4)]
    y = p.h - 30
    for q, no, i in nodes:
        p.box(0, y, p.w * 0.54, 22, None, "dim", radius=3)
        p.text(10, y + 7, q, 7.2, D.ink, SANS_SB, "l")
        p.box(p.w * 0.60, y, p.w * 0.40, 22, None, "bad", radius=3)
        p.text(p.w * 0.62, y + 7, "no \u2192 " + no, 6.9, D.bad_bd, SANS, "l")
        p.arrow(p.w * 0.55, y + 11, p.w * 0.595, y + 11, D.bad_bd, 0.9, head=3.0)
        if i < len(nodes) - 1:
            p.arrow(p.w * 0.27, y - 1, p.w * 0.27, y - 9, D.arrow, 0.9, head=3.0)
            p.text(p.w * 0.29, y - 9, "yes", 6.3, D.muted, SANS_I, "l")
        y -= 32
    p.box(0, y - 4, p.w * 0.54, 22, "build the simplest sufficient model", "ok",
          size=7.4, radius=3)
    p.arrow(p.w * 0.27, y + 21, p.w * 0.27, y + 19, D.ok_bd, 0.9, head=3.0)
    p.text(0, 2, "Most proposals terminate at one of the first three "
           "branches, and each termination saves months.", 7.0, D.muted,
           SANS_I, "l")


def _wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n:
            out.append(line); line = w
        else:
            line = (line + " " + w).strip()
    out.append(line)
    return out
