"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("master_levels")
def master_levels(p):
    """Where the work lives: root, leaves, or spread evenly."""
    cases = [
        ("a) leaves dominate", [6, 10, 16, 26], D.bad_bd,
         "T(n) = 4T(n/2) + n", "Θ(n²)"),
        ("b) evenly spread", [16, 16, 16, 16], D.node_bd,
         "T(n) = 2T(n/2) + n", "Θ(n log n)"),
        ("c) root dominates", [26, 16, 10, 6], D.ok_bd,
         "T(n) = 2T(n/2) + n²", "Θ(n²)"),
    ]
    colw = p.w / 3
    for ci, (title, bars, col, rec, ans) in enumerate(cases):
        x0 = ci * colw
        p.text(x0, p.h - 8, title, 7.2, col, SANS_SB, "l")
        y = p.h - 28
        for bi, b in enumerate(bars):
            w = b * 2.6
            p.c.saveState()
            p.c.setFillColor(col)
            p.c.roundRect(x0 + 24, y, w, 9, 1.4, stroke=0, fill=1)
            p.c.restoreState()
            p.text(x0 + 20, y + 1.6, "lvl %d" % bi, 6.0, D.faint, SANS, "r")
            y -= 14
        p.text(x0, y - 2, rec, 7.0, D.ink, MONO, "l")
        p.text(x0, y - 15, ans, 8.0, col, SANS_SB, "l")
    p.text(0, 4, "Compare the work at the root, n^log_b(a), with f(n). "
           "Whichever wins by a polynomial factor is the answer.",
           7.2, D.muted, SANS_I, "l")


@fig("interval_scheduling")
def interval_scheduling(p):
    """Earliest finish time is optimal; longest-first and earliest-start are not."""
    jobs = [(0, 3), (2, 5), (4, 7), (1, 9), (8, 11), (10, 13)]
    scale = (p.w - 120) / 14.0
    y = p.h - 22
    p.text(0, y + 14, "SIX JOBS", 7.0, D.muted, SANS_SB, "l")
    chosen = {0, 2, 4}
    for i, (s, f) in enumerate(jobs):
        yy = y - i * 15
        p.c.saveState()
        p.c.setFillColor(D.ok if i in chosen else D.dim)
        p.c.setStrokeColor(D.ok_bd if i in chosen else D.dim_bd)
        p.c.setLineWidth(0.6)
        p.c.roundRect(60 + s * scale, yy, (f - s) * scale, 11, 2, stroke=1, fill=1)
        p.c.restoreState()
        p.text(56, yy + 2.4, "job %d" % (i + 1), 6.6, D.muted, SANS, "r")
        p.text(64 + f * scale, yy + 2.4, "ends %d" % f, 6.2,
               D.ok_bd if i in chosen else D.faint, SANS, "l")
    yb = y - 6 * 15 - 4
    p.line(60, yb, 60 + 14 * scale, yb, D.faint, 0.6)
    for t in range(0, 15, 2):
        p.text(60 + t * scale, yb - 9, str(t), 6.0, D.faint, SANS, "c")
    p.text(0, yb - 26, "Greedy by earliest finish time picks jobs 1, 3, 5 "
           "— provably optimal.", 7.2, D.ok_bd, SANS_SB, "l")
    p.text(0, yb - 37, "Greedy by earliest start would pick job 1 then job 4 "
           "and stop at two.", 7.2, D.bad_bd, SANS, "l")


@fig("dp_grid")
def dp_grid(p):
    """A DP table is a DAG: each cell depends on a fixed set of earlier cells."""
    cw, ch = 30, 20
    cols, rows = 7, 4
    x0 = 46
    y0 = p.h - 20
    vals = [[1] * cols for _ in range(rows)]
    for r in range(1, rows):
        for c in range(1, cols):
            vals[r][c] = vals[r - 1][c] + vals[r][c - 1]
    hot = {(2, 4)}
    dep = {(1, 4), (2, 3)}
    for r in range(rows):
        for c in range(cols):
            k = "hi" if (r, c) in hot else ("teal" if (r, c) in dep else
                                            ("dim" if r == 0 or c == 0 else ""))
            p.box(x0 + c * cw, y0 - (r + 1) * ch, cw - 2, ch - 2,
                  str(vals[r][c]), k, size=6.8, radius=1)
    p.arrow(x0 + 4 * cw + 14, y0 - 2 * ch + 2, x0 + 4 * cw + 14,
            y0 - 3 * ch + 20, D.hi_bd, 0.9, head=3)
    p.arrow(x0 + 3 * cw + 28, y0 - 3 * ch + 9, x0 + 4 * cw + 1,
            y0 - 3 * ch + 9, D.hi_bd, 0.9, head=3)
    p.text(0, y0 - 2.5 * ch, "dp[i][j] =", 7.2, D.ink, MONO, "l")
    p.text(0, y0 - 3.4 * ch, "dp[i-1][j]", 7.0, D.teal_bd, MONO, "l")
    p.text(0, y0 - 4.2 * ch, "+ dp[i][j-1]", 7.0, D.teal_bd, MONO, "l")
    p.text(x0, y0 - (rows + 1) * ch - 6,
           "Fill in any order that respects the dependencies. Row by row works; "
           "so does column by column.", 7.2, D.muted, SANS_I, "l")
    p.text(x0, y0 - (rows + 1) * ch - 18,
           "Only the previous row is ever needed → Θ(n) memory, not "
           "Θ(mn).", 7.2, D.node_bd, SANS_SB, "l")


@fig("edit_distance")
def edit_distance(p):
    """The three-way recurrence, and the traceback that recovers the alignment."""
    a, b = "KITTEN", "SITTING"
    n, m = len(a), len(b)
    D_ = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D_[i][0] = i
    for j in range(m + 1):
        D_[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            D_[i][j] = min(D_[i - 1][j] + 1, D_[i][j - 1] + 1,
                           D_[i - 1][j - 1] + cost)
    cw, ch = 22, 16
    x0, y0 = 40, p.h - 24
    path = {(6, 7), (5, 6), (4, 5), (3, 4), (2, 3), (1, 2), (0, 1), (0, 0),
            (1, 1)}
    for j in range(m + 1):
        if j:
            p.text(x0 + j * cw + cw / 2, y0 + 6, b[j - 1], 7.0, D.node_bd,
                   SANS_SB, "c")
    for i in range(n + 1):
        if i:
            p.text(x0 - 6, y0 - i * ch - ch / 2 - 2, a[i - 1], 7.0, D.node_bd,
                   SANS_SB, "r")
        for j in range(m + 1):
            k = "hi" if (i, j) in path else ("dim" if i == 0 or j == 0 else "")
            p.box(x0 + j * cw, y0 - (i + 1) * ch, cw - 1.5, ch - 1.5,
                  str(D_[i][j]), k, size=6.4, radius=0.8)
    p.text(x0 + (m + 1) * cw + 12, y0 - 2 * ch,
           "d(KITTEN, SITTING) = 3", 7.6, D.ink, SANS_SB, "l")
    p.text(x0 + (m + 1) * cw + 12, y0 - 3 * ch, "substitute K→S", 6.9,
           D.muted, SANS, "l")
    p.text(x0 + (m + 1) * cw + 12, y0 - 3.8 * ch, "substitute E→I", 6.9,
           D.muted, SANS, "l")
    p.text(x0 + (m + 1) * cw + 12, y0 - 4.6 * ch, "insert G", 6.9, D.muted,
           SANS, "l")
    p.text(0, 4, "Highlighted cells are the traceback path — the edit "
           "script, recovered by walking backwards from the corner.", 7.2,
           D.muted, SANS_I, "l")


@fig("viterbi_lattice")
def viterbi_lattice(p):
    """Viterbi: the best path to each state, extended one step at a time."""
    states = ["A", "B", "C"]
    T = 5
    colw = (p.w - 90) / (T - 1)
    y0 = p.h - 34
    rowh = 28
    best = {(0, 0), (1, 1), (2, 1), (3, 2), (4, 2)}
    for t in range(T):
        for s in range(3):
            x = 40 + t * colw
            y = y0 - s * rowh
            if t:
                for ps in range(3):
                    on = (t - 1, ps) in best and (t, s) in best
                    p.line(40 + (t - 1) * colw + 10, y0 - ps * rowh, x - 10, y,
                           D.hi_bd if on else D.dim_bd, 1.5 if on else 0.35)
    for t in range(T):
        for s in range(3):
            x = 40 + t * colw
            y = y0 - s * rowh
            p.circle(x, y, 10, states[s], "hi" if (t, s) in best else "",
                     size=7.0)
        p.text(40 + t * colw, y0 + 18, "t=%d" % t, 6.6, D.muted, SANS, "c")
    p.text(0, y0, "states", 7.0, D.muted, SANS_SB, "r")
    p.text(0, 6, "At each step keep only the best path INTO each state: "
           "Θ(T·S²) instead of Θ(S^T).", 7.2, D.node_bd,
           SANS_SB, "l")


@fig("reservoir")
def reservoir(p):
    """Reservoir sampling: uniform k from an unknown-length stream, O(k) memory."""
    y = p.h - 30
    p.text(0, y + 22, "STREAM OF UNKNOWN LENGTH", 7.0, D.muted, SANS_SB, "l")
    for i in range(12):
        p.box(i * 30, y, 28, 17, str(i + 1), "teal" if i < 4 else "dim",
              size=6.8, radius=1)
    p.text(12 * 30 + 6, y + 4, "…", 9, D.faint, SANS, "l")
    p.brace(0, 4 * 30 - 2, y - 4, "fill the reservoir", up=False)

    y2 = y - 62
    p.text(0, y2 + 26, "RESERVOIR (k = 4)", 7.0, D.hi_bd, SANS_SB, "l")
    for i, v in enumerate([1, 7, 3, 4]):
        p.box(i * 34, y2, 32, 18, str(v), "hi", size=7.0, radius=1.5)
    p.text(4 * 34 + 14, y2 + 5,
           "item i (i > k) replaces a random slot with probability k/i", 7.0,
           D.ink, SANS, "l")
    p.text(4 * 34 + 14, y2 - 6,
           "every item ends up in the reservoir with probability exactly k/n",
           7.0, D.muted, SANS_I, "l")
    p.text(0, 4, "One pass, Θ(k) memory, no need to know n in advance "
           "— the right tool for sampling a dataset you are still writing.",
           7.2, D.muted, SANS_I, "l")


@fig("nqueens_prune")
def nqueens_prune(p):
    """Backtracking prunes whole subtrees; the saving is the algorithm."""
    import math
    root = (p.w * 0.5, p.h - 16)
    p.circle(root[0], root[1], 8, "", "", size=6)
    level1 = [(p.w * 0.5 + (i - 1.5) * 76, p.h - 54) for i in range(4)]
    dead = {1, 3}
    for i, (x, y) in enumerate(level1):
        p.line(root[0], root[1] - 8, x, y + 8, D.arrow, 0.7)
        p.circle(x, y, 8, "q%d" % (i + 1), "bad" if i in dead else "", size=6)
        if i in dead:
            p.text(x, y - 20, "conflict:", 6.4, D.bad_bd, SANS_SB, "c")
            p.text(x, y - 29, "prune", 6.4, D.bad_bd, SANS_SB, "c")
            p.c.saveState()
            p.c.setStrokeColor(D.bad_bd)
            p.c.setLineWidth(0.9)
            p.c.setDash(2, 2)
            p.c.line(x - 26, y - 34, x + 26, y - 34)
            p.c.restoreState()
        else:
            for j in range(3):
                cx = x + (j - 1) * 24
                cy = y - 34
                p.line(x, y - 8, cx, cy + 6, D.arrow, 0.6)
                p.circle(cx, cy, 6, "", "ok" if (i == 0 and j == 1) else "",
                         size=5)
    p.text(0, 6, "Two of four subtrees are cut at depth 1. For 8 queens this "
           "turns 16.7 million placements into about 2,000 explored nodes.",
           7.2, D.muted, SANS_I, "l")


@fig("dtw_path")
def dtw_path(p):
    """DTW aligns two series of different lengths by warping the time axis."""
    import math
    n, m = 12, 9
    cw = 13
    x0, y0 = 118, p.h - 16
    path = [(0, 0), (1, 0), (2, 1), (3, 2), (4, 2), (5, 3), (6, 4), (7, 5),
            (8, 6), (9, 6), (10, 7), (11, 8)]
    pset = set(path)
    for i in range(n):
        for j in range(m):
            k = "hi" if (i, j) in pset else "dim"
            p.box(x0 + i * cw, y0 - (j + 1) * cw, cw - 1.2, cw - 1.2, None, k,
                  radius=0.6, lw=0.35)
    p.text(x0 + n * cw / 2, y0 + 4, "series A (length 12)", 6.8, D.muted, SANS, "c")
    p.text(x0 - 6, y0 - m * cw / 2, "series B", 6.8, D.muted, SANS, "r")
    p.text(x0 - 6, y0 - m * cw / 2 - 9, "(length 9)", 6.8, D.muted, SANS, "r")

    ax = 0
    for i, s in enumerate([0.2, 0.5, 0.9, 1.0, 0.7, 0.3, 0.1, 0.3, 0.7, 0.9,
                           0.5, 0.2]):
        p.c.saveState()
        p.c.setFillColor(D.teal_bd)
        p.c.rect(ax + i * 7, 12, 5, 2 + s * 26, stroke=0, fill=1)
        p.c.restoreState()
    for i, s in enumerate([0.3, 0.8, 1.0, 0.6, 0.2, 0.2, 0.6, 1.0, 0.4]):
        p.c.saveState()
        p.c.setFillColor(D.violet_bd)
        p.c.rect(ax + i * 7, 52, 5, 2 + s * 26, stroke=0, fill=1)
        p.c.restoreState()
    p.text(0, 2, "same shape,", 6.6, D.muted, SANS_I, "l")
    p.text(0, 44, "different pace", 6.6, D.muted, SANS_I, "l")
    p.text(x0 + n * cw + 10, y0 - 20, "Each step is →, ↑ or ↗.",
           7.0, D.ink, SANS, "l")
    p.text(x0 + n * cw + 10, y0 - 32, "Θ(nm) time; a Sakoe–Chiba", 7.0,
           D.muted, SANS, "l")
    p.text(x0 + n * cw + 10, y0 - 42, "band makes it Θ(nw).", 7.0, D.muted,
           SANS, "l")


@fig("ctc_lattice")
def ctc_lattice(p):
    """CTC sums over every alignment of a label sequence to T frames."""
    labels = ["ε", "c", "ε", "a", "ε", "t", "ε"]
    T = 6
    colw = (p.w - 150) / (T - 1)
    y0 = p.h - 20
    rowh = 17
    valid = {(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 4),
             (4, 4), (4, 5), (5, 5), (5, 6)}
    for t in range(T):
        for s in range(len(labels)):
            x = 54 + t * colw
            y = y0 - s * rowh
            on = (t, s) in valid
            p.circle(x, y, 6.2, "", "hi" if on else "dim", size=5.6)
            if t < T - 1:
                for ds in (0, 1, 2):
                    if s + ds < len(labels) and on and (t + 1, s + ds) in valid:
                        p.line(x + 6.2, y, 54 + (t + 1) * colw - 6.2,
                               y0 - (s + ds) * rowh, D.hi_bd, 0.7)
    for s, lab in enumerate(labels):
        p.text(44, y0 - s * rowh - 2.4, lab, 6.8, D.muted, SANS_SB, "r")
    for t in range(T):
        p.text(54 + t * colw, y0 + 10, "t%d" % (t + 1), 6.4, D.faint, SANS, "c")
    x1 = 54 + (T - 1) * colw + 26
    for i, line in enumerate([
            "Target: c a t.  Insert blanks (ε)",
            "between and around every label.",
            "",
            "Any monotone path from top-left to",
            "bottom-right spells ‘cat’ after",
            "collapsing repeats and dropping ε.",
            "",
            "CTC loss sums the probability of ALL",
            "such paths: forward–backward DP,",
            "Θ(T·S) instead of exponentially many."]):
        p.text(x1, y0 - i * 11, line, 6.9,
               D.node_bd if line.startswith("Θ") else D.ink, SANS, "l")
