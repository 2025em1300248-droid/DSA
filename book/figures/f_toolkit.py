"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("stack_queue")
def stack_queue(p):
    """LIFO and FIFO, and the one-line difference between DFS and BFS."""
    cw, ch = 46, 19
    x = 0
    y = p.h - 40
    p.text(x, y + 30, "STACK — LIFO", 7.6, D.teal_bd, SANS_SB, "l")
    for i, v in enumerate(["a", "b", "c", "d"]):
        p.box(x, y - i * (ch + 2), cw, ch, v, "teal" if i == 0 else "dim",
              radius=2)
    p.arrow(x + cw + 26, y + ch / 2, x + cw + 6, y + ch / 2, D.teal_bd, 1.0,
            head=3.4)
    p.text(x + cw + 30, y + ch / 2 - 2.6, "push / pop here", 7.0, D.teal_bd,
           SANS, "l")
    p.text(x, y - 4 * (ch + 2) - 8, "depth-first search", 7.0, D.muted, SANS_I, "l")

    x2 = 218
    p.text(x2, y + 30, "QUEUE — FIFO", 7.6, D.node_bd, SANS_SB, "l")
    for i, v in enumerate(["a", "b", "c", "d"]):
        p.box(x2 + i * (34), y, 32, ch, v, "" if i else "hi", radius=2, size=7.4)
    p.arrow(x2 + 16, y + ch + 16, x2 + 16, y + ch + 3, D.hi_bd, 1.0, head=3.2)
    p.text(x2 + 20, y + ch + 13, "pop left", 7.0, D.hi_bd, SANS, "l")
    p.arrow(x2 + 4 * 34 + 20, y + ch / 2, x2 + 4 * 34 - 2, y + ch / 2,
            D.node_bd, 1.0, head=3.2)
    p.text(x2 + 4 * 34 + 24, y + ch / 2 - 2.6, "push", 7.0, D.node_bd, SANS, "l")
    p.text(x2, y - 14, "breadth-first search", 7.0, D.muted, SANS_I, "l")
    p.text(x2, y - 30, "list.pop(0) is Θ(n); deque.popleft() is Θ(1)",
           7.2, D.bad_bd, SANS_SB, "l")


@fig("ring_buffer")
def ring_buffer(p):
    """A replay buffer: fixed memory, O(1) push, oldest evicted."""
    import math
    cx, cy, r = 92, p.h / 2 - 4, 46
    n = 10
    head, tail = 3, 8
    for i in range(n):
        a = math.pi / 2 - i * 2 * math.pi / n
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        filled = (tail - head) % n
        idx = (i - head) % n
        kind = "teal" if idx < filled else "dim"
        p.circle(x, y, 9.5, str(i), kind, size=6.8)
    ah = math.pi / 2 - head * 2 * math.pi / n
    at = math.pi / 2 - tail * 2 * math.pi / n
    p.text(cx + (r + 22) * math.cos(ah), cy + (r + 22) * math.sin(ah) - 2,
           "head", 6.8, D.hi_bd, SANS_SB, "c")
    p.text(cx + (r + 22) * math.cos(at), cy + (r + 22) * math.sin(at) - 2,
           "tail", 6.8, D.node_bd, SANS_SB, "c")
    p.text(cx, cy - 3, "capacity 10", 6.8, D.muted, SANS_I, "c")

    x0 = 198
    lines = [
        ("push(x)", "buf[tail] = x; tail = (tail+1) % N", "Θ(1)"),
        ("full?", "overwrite oldest — no allocation ever", "Θ(1)"),
        ("sample(k)", "k random indices into the live range", "Θ(k)"),
        ("memory", "exactly N slots, forever", "Θ(N)"),
    ]
    y = p.h - 26
    for a, b, c in lines:
        p.text(x0, y, a, 7.4, D.ink, MONO, "l")
        p.text(x0 + 56, y, b, 7.2, D.muted, SANS, "l")
        p.text(p.w, y, c, 7.2, D.teal_bd, SANS_SB, "r")
        y -= 17
    p.text(x0, y - 4, "This is the DQN replay buffer, the streaming-metrics",
           7.0, D.muted, SANS_I, "l")
    p.text(x0, y - 13, "window, and the token ring in a decoding server.",
           7.0, D.muted, SANS_I, "l")


@fig("lru_cache")
def lru_cache(p):
    """Hash map plus doubly linked list gives O(1) LRU."""
    y2 = 34
    xs = [86, 164, 242, 320]
    labels = ["k9", "k3", "k7", "k1"]
    p.text(0, p.h - 10, "HASH MAP", 7.0, D.violet_bd, SANS_SB, "l")
    p.text(0, p.h - 20, "key \u2192 node", 6.8, D.muted, SANS, "l")
    for i, k in enumerate(["k1", "k7", "k3", "k9"]):
        p.box(0, p.h - 40 - i * 15, 32, 13, k, "violet", size=6.6, radius=1.5)
    p.text(0, y2 - 12, "\u0398(1) lookup", 6.8, D.violet_bd, SANS, "l")

    p.text(xs[0], p.h - 10, "RECENCY LIST (doubly linked)", 7.0, D.node_bd,
           SANS_SB, "l")
    for i, (x, k) in enumerate(zip(xs, labels)):
        p.box(x, y2, 58, 26, k, "teal" if i == 0 else ("bad" if i == 3 else "dim"),
              radius=2, sub="node")
        if i < 3:
            p.arrow(x + 59, y2 + 18, xs[i + 1] - 1, y2 + 18, D.arrow, 0.8, head=3)
            p.arrow(xs[i + 1] - 1, y2 + 8, x + 59, y2 + 8, D.faint, 0.8, head=3)
    p.line(33, p.h - 33, xs[3] + 29, y2 + 27, D.violet_bd, 0.45, dashed=True)
    p.line(33, p.h - 78, xs[0] + 29, y2 + 27, D.violet_bd, 0.45, dashed=True)
    p.text(xs[0] + 29, y2 + 36, "most recent", 6.8, D.teal_bd, SANS_SB, "c")
    p.text(xs[3] + 29, y2 + 36, "evict next", 6.8, D.bad_bd, SANS_SB, "c")
    p.text(xs[0], y2 - 12, "get(k): the map finds the node; unlink and relink "
           "at the front \u2014 all \u0398(1), no scan.", 7.0, D.muted, SANS_I, "l")


@fig("hash_chaining")
def hash_chaining(p):
    """Separate chaining: buckets of linked entries."""
    bh = 17
    n = 8
    x0 = 0
    y = p.h - 24
    p.text(0, y + 12, "BUCKETS", 7.0, D.faint, SANS_SB, "l")
    chains = {1: ["cat"], 3: ["dog", "emu"], 4: ["ant"], 6: ["owl", "bee", "fox"]}
    for i in range(n):
        p.box(x0, y - i * (bh + 3), 26, bh, str(i), "dim", size=6.8, radius=1)
        items = chains.get(i, [])
        for j, it in enumerate(items):
            bx = x0 + 34 + j * 52
            p.box(bx, y - i * (bh + 3), 44, bh, it, "teal", size=6.8, radius=2)
            p.arrow(bx - 7, y - i * (bh + 3) + bh / 2, bx - 1,
                    y - i * (bh + 3) + bh / 2, D.arrow, 0.7, head=2.6)
    p.text(230, y - 6, "load factor α = n / buckets", 7.4, D.ink, SANS_SB, "l")
    p.text(230, y - 22, "expected chain length = α", 7.2, D.muted, SANS, "l")
    p.text(230, y - 36, "expected probes ≈ 1 + α/2", 7.2, D.muted, SANS, "l")
    p.text(230, y - 58, "Resize when α exceeds ~0.75", 7.2, D.hi_bd, SANS_SB, "l")
    p.text(230, y - 72, "→ amortised Θ(1), like the dynamic array", 7.2,
           D.muted, SANS_I, "l")
    p.text(230, y - 94, "Worst case: every key in one bucket → Θ(n).",
           7.2, D.bad_bd, SANS, "l")


@fig("open_addressing")
def open_addressing(p):
    """Linear probing keeps everything in one cache-friendly array."""
    vals = ["", "ant", "cat", "dog", "emu", "", "", "owl", "", ""]
    kinds = ["dim", "teal", "teal", "hi", "hi", "dim", "dim", "teal", "dim", "dim"]
    y = p.h - 40
    p.cells(0, y, vals, cw=36, ch=20, kinds=kinds, size=6.8, font=SANS)
    p.pointer(3 * 36 + 18, y + 20, "h(‘emu’) = 3", height=16)
    p.arrow(3 * 36 + 18, y - 14, 4 * 36 + 18, y - 14, D.hi_bd, 0.9, head=3)
    p.text(4 * 36 + 26, y - 17, "occupied → probe the next slot", 7.2,
           D.hi_bd, SANS, "l")
    p.text(0, 22, "One contiguous array: a probe sequence is a cache-line scan, "
           "not a pointer chase.", 7.2, D.muted, SANS_I, "l")
    p.text(0, 10, "Deletion needs a tombstone, and clustering makes "
           "performance collapse above α ≈ 0.8.", 7.2, D.muted, SANS_I, "l")


@fig("recursion_tree")
def recursion_tree(p):
    """Naive Fibonacci recomputes exponentially; memoisation collapses it."""
    import math
    r = 9
    lab = [("f5", 0), ("f4", -1), ("f3", -1), ("f3", -2), ("f2", -2),
           ("f2", -2), ("f1", -2)]
    positions = {
        "f5": (100, p.h - 18),
        "f4a": (58, p.h - 48), "f3a": (152, p.h - 48),
        "f3b": (30, p.h - 78), "f2a": (86, p.h - 78),
        "f2b": (128, p.h - 78), "f1a": (180, p.h - 78),
        "f2c": (12, p.h - 108), "f1b": (50, p.h - 108),
        "f1c": (74, p.h - 108), "f0a": (100, p.h - 108),
        "f1d": (116, p.h - 108), "f0b": (142, p.h - 108),
    }
    edges = [("f5", "f4a"), ("f5", "f3a"), ("f4a", "f3b"), ("f4a", "f2a"),
             ("f3a", "f2b"), ("f3a", "f1a"), ("f3b", "f2c"), ("f3b", "f1b"),
             ("f2a", "f1c"), ("f2a", "f0a"), ("f2b", "f1d"), ("f2b", "f0b")]
    for a, b in edges:
        ax, ay = positions[a]
        bx, by = positions[b]
        p.line(ax, ay - r, bx, by + r, D.faint, 0.6)
    dup = {"f3b", "f2b", "f2c", "f1b", "f1c", "f1d", "f0b", "f2a", "f1a", "f0a"}
    for k, (x, y) in positions.items():
        name = k[:2]
        p.circle(x, y, r, name, "bad" if k in dup else "teal", size=6.6)
    p.text(0, 12, "fib(5) naive: 15 calls, and fib(3) is computed twice. "
           "fib(40) makes 331 million calls.", 7.2, D.bad_bd, SANS, "l")

    x0 = 218
    y0 = p.h - 30
    p.text(x0, y0 + 18, "WITH MEMOISATION", 7.2, D.ok_bd, SANS_SB, "l")
    chain = ["f5", "f4", "f3", "f2", "f1", "f0"]
    for i, c in enumerate(chain):
        p.circle(x0 + i * 30, y0, 9, c, "ok", size=6.6)
        if i < len(chain) - 1:
            p.arrow(x0 + i * 30 + 9, y0, x0 + (i + 1) * 30 - 9, y0, D.ok_bd,
                    0.8, head=2.8)
    p.text(x0, y0 - 24, "each subproblem solved once: Θ(n)", 7.2, D.ok_bd,
           SANS, "l")
    p.text(x0, y0 - 38, "the recursion tree becomes a DAG", 7.2, D.muted,
           SANS_I, "l")


@fig("merge_sort")
def merge_sort(p):
    """Divide to singletons, then merge upward: log n levels of O(n) work."""
    levels = [
        [[38, 27, 43, 3, 9, 82, 10]],
        [[38, 27, 43, 3], [9, 82, 10]],
        [[38, 27], [43, 3], [9, 82], [10]],
        [[38], [27], [43], [3], [9], [82], [10]],
    ]
    cw = 20
    y = p.h - 22
    for li, level in enumerate(levels):
        x = 34
        for grp in level:
            for j, v in enumerate(grp):
                p.box(x + j * cw, y, cw - 1.5, 15, str(v),
                      "teal" if li == 0 else "dim", size=6.6, radius=1)
            x += len(grp) * cw + 13
        p.text(0, y + 4, "split", 6.6, D.faint, SANS_SB, "l")
        y -= 23
    merged = [
        [[3, 9, 10, 27, 38, 43, 82]],
        [[3, 27, 38, 43], [9, 10, 82]],
        [[27, 38], [3, 43], [9, 82], [10]],
    ]
    y -= 6
    for li, level in enumerate(reversed(merged)):
        x = 34
        for grp in level:
            for j, v in enumerate(grp):
                p.box(x + j * cw, y, cw - 1.5, 15, str(v), "ok", size=6.6,
                      radius=1)
            x += len(grp) * cw + 13
        p.text(0, y + 4, "merge", 6.6, D.ok_bd, SANS_SB, "l")
        y -= 23
    p.text(p.w - 2, p.h - 18, "Θ(log n) levels", 7.2, D.muted, SANS_SB, "r")
    p.text(p.w - 2, p.h - 30, "Θ(n) work per level", 7.2, D.muted, SANS, "r")
    p.text(p.w - 2, p.h - 42, "→ Θ(n log n)", 7.6, D.node_bd, SANS_SB, "r")


@fig("sort_landscape")
def sort_landscape(p):
    """Choosing a sort: the decision is rarely 'which is fastest'."""
    rows = [
        ("Insertion", "Θ(n)", "Θ(n²)", "Θ(1)", "yes", "n < 32, nearly sorted", "ok"),
        ("Merge", "Θ(n log n)", "Θ(n log n)", "Θ(n)", "yes", "stability required, external", "teal"),
        ("Quick", "Θ(n log n)", "Θ(n²)", "Θ(log n)", "no", "in-memory, no stability need", "hi"),
        ("Heap", "Θ(n log n)", "Θ(n log n)", "Θ(1)", "no", "hard worst-case bound", "teal"),
        ("Timsort", "Θ(n)", "Θ(n log n)", "Θ(n)", "yes", "Python/Java default", "ok"),
        ("Counting", "Θ(n + k)", "Θ(n + k)", "Θ(k)", "yes", "small integer range", "violet"),
        ("Radix (LSD)", "Θ(d(n + b))", "Θ(d(n + b))", "Θ(n + b)", "yes", "fixed-width keys, GPU", "violet"),
    ]
    heads = ["algorithm", "best", "worst", "space", "stable", "when to choose it"]
    xs = [0, 62, 118, 178, 222, 258]
    y = p.h - 12
    for x, hd in zip(xs, heads):
        p.text(x, y, hd, 6.6, D.faint, SANS_SB, "l")
    p.line(0, y - 5, p.w, y - 5, D.faint, 0.5)
    y -= 18
    for r in rows:
        kind = r[-1]
        fc = {"ok": D.ok, "teal": D.teal, "hi": D.hi, "violet": D.violet}[kind]
        sc = {"ok": D.ok_bd, "teal": D.teal_bd, "hi": D.hi_bd,
              "violet": D.violet_bd}[kind]
        p.c.saveState()
        p.c.setFillColor(fc)
        p.c.roundRect(-3, y - 4, p.w + 6, 15, 2, stroke=0, fill=1)
        p.c.restoreState()
        p.text(xs[0], y, r[0], 7.2, D.ink, SANS_SB, "l")
        for x, v in zip(xs[1:], r[1:6]):
            p.text(x, y, v, 6.9, D.muted if x < xs[5] else sc, SANS, "l")
        y -= 18


@fig("binary_search_trace")
def binary_search_trace(p):
    """Each probe halves the interval; log2(n) probes suffice."""
    vals = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    cw = 30
    y = p.h - 34
    steps = [(0, 9, 4), (5, 9, 7), (5, 6, 5)]
    p.text(0, y + 22, "target = 23", 7.6, D.hi_bd, SANS_SB, "l")
    kinds = ["dim"] * len(vals)
    p.cells(0, y, vals, cw=cw, ch=19, kinds=kinds, size=7.0)
    yy = y - 26
    for lo, hi, mid in steps:
        for i in range(len(vals)):
            k = "dim" if not (lo <= i <= hi) else ("hi" if i == mid else "teal")
            p.box(i * cw, yy, cw - 1.5, 17, str(vals[i]), k, size=6.8, radius=1)
        p.text(len(vals) * cw + 10, yy + 4,
               "lo=%d hi=%d mid=%d → %s" %
               (lo, hi, mid, "found" if vals[mid] == 23 else
                ("go right" if vals[mid] < 23 else "go left")),
               7.0, D.muted, SANS, "l")
        yy -= 23
    p.text(0, yy + 6, "10 elements, 3 probes. A billion elements would take 30.",
           7.2, D.node_bd, SANS_SB, "l")


@fig("sliding_window")
def sliding_window(p):
    """The window expands on the right and contracts on the left."""
    vals = [2, 1, 5, 1, 3, 2, 4, 1]
    cw = 34
    y = p.h - 40
    p.text(0, y + 26, "longest window with sum ≤ 8", 7.6, D.ink, SANS_SB, "l")
    states = [(0, 2), (0, 4), (2, 5), (3, 6)]
    yy = y
    for lo, hi in states:
        for i, v in enumerate(vals):
            k = "teal" if lo <= i <= hi else "dim"
            p.box(i * cw, yy, cw - 2, 17, str(v), k, size=7.0, radius=1)
        tot = sum(vals[lo:hi + 1])
        p.text(len(vals) * cw + 10, yy + 4, "sum=%d  width=%d" % (tot, hi - lo + 1),
               7.0, D.muted, MONO, "l")
        p.text(lo * cw + (cw - 2) / 2, yy - 9, "L", 6.4, D.node_bd, SANS_SB, "c")
        p.text(hi * cw + (cw - 2) / 2, yy - 9, "R", 6.4, D.hi_bd, SANS_SB, "c")
        yy -= 30
    p.text(0, yy + 8, "Each index enters the window once and leaves once: "
           "Θ(n) total, not Θ(n²).", 7.2, D.muted, SANS_I, "l")
