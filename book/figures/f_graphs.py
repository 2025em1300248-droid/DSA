"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


G_NODES = {"A": (0, 2), "B": (1, 2), "C": (2, 2), "D": (0, 1), "E": (1, 1),
           "F": (2, 1)}
G_EDGES = [("A", "B"), ("A", "D"), ("B", "C"), ("B", "E"), ("C", "F"),
           ("D", "E"), ("E", "F")]


def _layout(p, ox, oy, sx=48, sy=40, r=10, kinds=None, labels=True):
    pos = {}
    for k, (cx, cy) in G_NODES.items():
        pos[k] = (ox + cx * sx, oy + cy * sy)
    for a, b in G_EDGES:
        p.line(pos[a][0], pos[a][1], pos[b][0], pos[b][1], D.arrow, 0.8)
    for k, (x, y) in pos.items():
        p.circle(x, y, r, k if labels else "", (kinds or {}).get(k, ""), size=7.4)
    return pos


@fig("graph_representations")
def graph_representations(p):
    """Three encodings of one graph, with very different cost profiles."""
    _layout(p, 16, 18, sx=44, sy=36, r=9.5)
    p.text(16, p.h - 8, "THE GRAPH", 7.0, D.muted, SANS_SB, "l")

    x1 = 126
    p.text(x1, p.h - 8, "ADJACENCY MATRIX", 7.0, D.muted, SANS_SB, "l")
    keys = list(G_NODES)
    idx = {k: i for i, k in enumerate(keys)}
    adj = [[0] * 6 for _ in range(6)]
    for a, b in G_EDGES:
        adj[idx[a]][idx[b]] = adj[idx[b]][idx[a]] = 1
    p.grid_matrix(x1 + 12, p.h - 18, 6, 6, cw=13, ch=12,
                  values=lambda r, c: adj[r][c] or "",
                  kinds=lambda r, c: "teal" if adj[r][c] else "dim",
                  labels_r=keys, labels_c=keys, size=6.0)
    p.text(x1, p.h - 104, "Θ(V²) memory, Θ(1) edge test", 6.8,
           D.muted, SANS, "l")

    x2 = 244
    p.text(x2, p.h - 8, "ADJACENCY LIST", 7.0, D.muted, SANS_SB, "l")
    nbr = {k: [] for k in keys}
    for a, b in G_EDGES:
        nbr[a].append(b); nbr[b].append(a)
    y = p.h - 22
    for k in keys:
        p.box(x2, y, 16, 12, k, "teal", size=6.4, radius=1)
        p.text(x2 + 22, y + 2.6, "→ " + " ".join(nbr[k]), 6.6, D.ink,
               MONO, "l")
        y -= 15
    p.text(x2, y - 2, "Θ(V + E) memory", 6.8, D.muted, SANS, "l")
    p.text(x2, y - 12, "Θ(deg) to enumerate neighbours", 6.8, D.muted,
           SANS, "l")
    p.text(x2, y - 26, "CSR: two flat arrays", 6.8, D.node_bd, SANS_SB, "l")
    p.text(x2, y - 36, "indptr + indices — the GPU format", 6.8, D.muted,
           SANS, "l")


@fig("bfs_dfs")
def bfs_dfs(p):
    """One skeleton, two frontiers, two completely different orders."""
    order_b = {"A": 1, "B": 2, "D": 3, "C": 4, "E": 5, "F": 6}
    order_d = {"A": 1, "B": 2, "C": 3, "F": 4, "E": 5, "D": 6}

    def draw(ox, kind, order, col):
        pos = {}
        for k, (cx, cy) in G_NODES.items():
            pos[k] = (ox + cx * 44, 24 + cy * 34)
        for a, b in G_EDGES:
            p.line(pos[a][0], pos[a][1], pos[b][0], pos[b][1], D.arrow, 0.8)
        for k, (x, y) in pos.items():
            p.circle(x, y, 10, k, kind, size=7.4)
            p.text(x - 13, y + 8, str(order[k]), 6.0, col, SANS_SB, "r")
        return pos

    p.text(22, p.h - 8, "BFS \u2014 queue", 7.4, D.node_bd, SANS_SB, "l")
    draw(34, "teal", order_b, D.node_bd)
    p.text(202, p.h - 8, "DFS \u2014 stack", 7.4, D.violet_bd, SANS_SB, "l")
    draw(214, "violet", order_d, D.violet_bd)
    p.text(10, 4, "frontier.popleft() \u2192 shortest paths in an unweighted "
           "graph.      frontier.pop() \u2192 cycle detection, topological order.",
           7.0, D.muted, SANS_I, "l")


@fig("autograd_dag")
def autograd_dag(p):
    """A computation graph is a DAG; backprop is a reverse topological sweep."""
    top = p.h - 30
    nodes = {
        "x": (16, top), "W": (16, top - 30), "b": (16, top - 60),
        "matmul": (104, top - 15), "add": (188, top - 30),
        "relu": (256, top - 30), "loss": (324, top - 30),
    }
    edges = [("x", "matmul"), ("W", "matmul"), ("matmul", "add"),
             ("b", "add"), ("add", "relu"), ("relu", "loss")]
    for a, b in edges:
        ax, ay = nodes[a]; bx, by = nodes[b]
        p.arrow(ax + 21, ay, bx - 23, by, D.arrow, 0.9, head=3.2)
    leaf = {"x", "W", "b"}
    for k, (x, y) in nodes.items():
        p.box(x - 22, y - 9, 44, 18, k, "teal" if k in leaf else
              ("bad" if k == "loss" else ""), size=6.8, radius=2)
    p.text(0, p.h - 10, "FORWARD: topological order", 7.2, D.node_bd,
           SANS_SB, "l")
    yb = 24
    p.arrow(346, yb, 8, yb, D.hi_bd, 1.6, head=5)
    p.text(346, yb + 8, "BACKWARD: the exact reverse order \u2014 each node's "
           "vjp runs once, after all of its consumers", 7.2, D.hi_bd,
           SANS_SB, "r")
    p.text(0, 6, "The stored activations are what the reverse sweep needs; "
           "checkpointing trades some of them for recomputation.", 7.0,
           D.muted, SANS_I, "l")


@fig("dijkstra_step")
def dijkstra_step(p):
    """Settle the closest unsettled vertex, then relax its edges."""
    pos = {"S": (16, 60), "A": (96, 96), "B": (96, 24), "C": (186, 96),
           "D": (186, 24), "T": (272, 60)}
    edges = [("S", "A", 4), ("S", "B", 2), ("A", "C", 5), ("B", "A", 1),
             ("B", "D", 8), ("C", "T", 3), ("D", "T", 2), ("C", "D", 2)]
    dist = {"S": 0, "A": 3, "B": 2, "C": 8, "D": 10, "T": 11}
    settled = {"S", "B", "A"}
    for a, b, w in edges:
        ax, ay = pos[a]; bx, by = pos[b]
        p.arrow(ax, ay, bx, by, D.arrow, 0.8, head=3, shrink=12,
                label=str(w), label_off=6)
    for k, (x, y) in pos.items():
        p.circle(x, y, 12, k, "ok" if k in settled else "", size=7.6)
        p.text(x, y - 22, "d=%d" % dist[k], 6.6,
               D.ok_bd if k in settled else D.muted, SANS_SB, "c")
    p.text(0, p.h - 8, "green = settled (distance final)", 7.0, D.ok_bd,
           SANS_SB, "l")
    x0 = 300
    steps = ["1  pop the closest unsettled vertex",
             "2  relax every edge leaving it",
             "3  repeat",
             "",
             "Correct only with non-negative weights:",
             "a settled distance must never improve."]
    for i, line in enumerate(steps):
        p.text(x0, p.h - 22 - i * 12, line, 6.9,
               D.bad_bd if i >= 4 else D.ink, SANS, "l")


@fig("pagerank_flow")
def pagerank_flow(p):
    """PageRank as a random surfer: rank flows along edges and pools."""
    pos = {"a": (30, 84), "b": (110, 108), "c": (110, 52), "d": (196, 84),
           "e": (270, 84)}
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("d", "e"),
             ("e", "d"), ("c", "b")]
    ranks = {"a": 0.10, "b": 0.16, "c": 0.13, "d": 0.34, "e": 0.27}
    for a, b in edges:
        ax, ay = pos[a]; bx, by = pos[b]
        p.arrow(ax, ay, bx, by, D.arrow, 0.8, head=3.2, shrink=16)
    for k, (x, y) in pos.items():
        r = 8 + ranks[k] * 42
        p.circle(x, y, r, k, "violet", size=7.4)
        p.text(x, y - r - 11, "%.2f" % ranks[k], 6.6, D.violet_bd, SANS_SB, "c")
    x0 = 316
    lines = ["r = α Pᵀ r + (1−α)/N",
             "",
             "Power iteration:",
             "one sparse mat-vec",
             "per step, Θ(E).",
             "",
             "α = 0.85 → about",
             "50 iterations."]
    for i, line in enumerate(lines):
        p.text(x0, p.h - 18 - i * 12, line, 6.9,
               D.node_bd if i == 0 else D.ink, SANS_SB if i == 0 else SANS, "l")


@fig("gnn_sampling")
def gnn_sampling(p):
    """Neighbour explosion, and the sampling that contains it."""
    import math
    cx = 74
    cy = p.h / 2
    p.circle(cx, cy, 11, "v", "hi", size=7.6)
    n1 = []
    for i in range(6):
        a = math.pi * (0.5 - i / 5.0)
        x, y = cx + 44 * math.cos(a), cy + 44 * math.sin(a)
        n1.append((x, y))
        p.line(cx, cy, x, y, D.arrow, 0.6)
        p.circle(x, y, 7, "", "teal", size=6)
    for (x, y) in n1:
        for j in range(5):
            a = math.pi * (0.5 - j / 4.0)
            x2, y2 = x + 30 * math.cos(a), y + 30 * math.sin(a)
            p.line(x, y, x2, y2, D.dim_bd, 0.35)
            p.circle(x2, y2, 3.6, "", "dim", size=5)
    p.text(0, p.h - 8, "FULL 2-HOP NEIGHBOURHOOD", 7.0, D.bad_bd, SANS_SB, "l")
    p.text(0, 16, "average degree d → d^L nodes at depth L.", 7.0,
           D.bad_bd, SANS, "l")
    p.text(0, 6, "d = 100, L = 3 is a million nodes per example.", 7.0,
           D.bad_bd, SANS, "l")

    x0 = 250
    p.circle(x0, cy, 11, "v", "hi", size=7.6)
    for i in range(2):
        a = math.pi * (0.5 - i / 1.0) * 0.5
        x, y = x0 + 44 * math.cos(a), cy + 44 * math.sin(a)
        p.line(x0, cy, x, y, D.ok_bd, 0.9)
        p.circle(x, y, 7, "", "ok", size=6)
        for j in range(2):
            a2 = math.pi * (0.5 - j / 1.0) * 0.5
            x2, y2 = x + 30 * math.cos(a2), y + 30 * math.sin(a2)
            p.line(x, y, x2, y2, D.ok_bd, 0.8)
            p.circle(x2, y2, 4.4, "", "ok", size=5)
    p.text(x0 - 46, p.h - 8, "SAMPLED: 2 NEIGHBOURS PER HOP", 7.0, D.ok_bd,
           SANS_SB, "l")
    p.text(x0 - 46, 16, "bounded fan-out → constant work", 7.0,
           D.ok_bd, SANS, "l")
    p.text(x0 - 46, 6, "per example (GraphSAGE)", 7.0, D.ok_bd, SANS, "l")


@fig("bipartite_matching")
def bipartite_matching(p):
    """Augmenting paths: flip a path to grow the matching by one."""
    left = ["p1", "p2", "p3", "p4"]
    right = ["g1", "g2", "g3", "g4"]
    lx, rx = 60, 210
    ys = [p.h - 26 - i * 26 for i in range(4)]
    edges = [(0, 0), (0, 1), (1, 0), (1, 2), (2, 1), (2, 2), (3, 2), (3, 3)]
    matched = {(0, 1), (1, 0), (2, 2), (3, 3)}
    for a, b in edges:
        col = D.ok_bd if (a, b) in matched else D.dim_bd
        p.line(lx + 13, ys[a], rx - 13, ys[b], col, 1.6 if (a, b) in matched else 0.5)
    for i, name in enumerate(left):
        p.circle(lx, ys[i], 12, name, "teal", size=6.8)
    for i, name in enumerate(right):
        p.circle(rx, ys[i], 12, name, "violet", size=6.8)
    p.text(lx, p.h - 8, "predictions", 7.0, D.teal_bd, SANS_SB, "c")
    p.text(rx, p.h - 8, "ground truth", 7.0, D.violet_bd, SANS_SB, "c")
    x0 = 258
    lines = ["Green = current matching.",
             "",
             "Repeatedly find an augmenting path:",
             "unmatched → matched → unmatched …",
             "and flip every edge on it.",
             "",
             "Hopcroft–Karp: Θ(E√V).",
             "With costs: Hungarian, Θ(n³)."]
    for i, line in enumerate(lines):
        p.text(x0, p.h - 18 - i * 12, line, 6.9,
               D.node_bd if line.startswith(("Hopcroft", "With")) else D.ink,
               SANS_SB if line.startswith(("Hopcroft", "With")) else SANS, "l")


@fig("maxflow_cut")
def maxflow_cut(p):
    """Max-flow equals min-cut: the bottleneck is a set of edges."""
    pos = {"s": (24, 56), "a": (110, 92), "b": (110, 20), "c": (206, 92),
           "d": (206, 20), "t": (292, 56)}
    edges = [("s", "a", "3/3"), ("s", "b", "2/2"), ("a", "c", "2/3"),
             ("a", "d", "1/1"), ("b", "d", "2/4"), ("c", "t", "2/2"),
             ("d", "t", "3/3")]
    cut = {("a", "c"), ("a", "d"), ("b", "d")}
    for a, b, lab in edges:
        ax, ay = pos[a]; bx, by = pos[b]
        col = D.bad_bd if (a, b) in cut else D.arrow
        p.arrow(ax, ay, bx, by, col, 1.3 if (a, b) in cut else 0.8, head=3.2,
                shrink=13, label=lab, label_off=6)
    for k, (x, y) in pos.items():
        p.circle(x, y, 13, k, "hi" if k in ("s", "t") else "", size=7.4)
    p.c.saveState()
    p.c.setStrokeColor(D.bad_bd)
    p.c.setLineWidth(1.0)
    p.c.setDash(3, 3)
    p.c.line(150, 4, 168, p.h - 14)
    p.c.restoreState()
    p.text(159, p.h - 8, "cut", 7.0, D.bad_bd, SANS_SB, "c")
    p.text(0, 4, "Flow out of s is 5. The dashed cut has capacity 3+1+4 = 8 "
           "— not minimum; find the cut of capacity 5 as an exercise.",
           7.0, D.muted, SANS_I, "l")
