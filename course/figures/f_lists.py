"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


# ------------------------------------------------------------- ch 23: idea
@fig("ll_array_vs_list")
def ll_array_vs_list(p):
    """The same five values, two ways."""
    cw = 42
    x0 = 70
    y = p.h - 44
    p.text(0, y + 28, "ARRAY", 8.0, D.node_bd, SANS_SB, "l")
    p.text(0, y + 18, "one block", 6.6, D.muted, SANS_I, "l")
    p.cells(x0, y, [10, 20, 30, 40, 50], cw=cw, ch=22, index=True, size=8.4)
    p.text(x0 + 5 * cw + 12, y + 14, "index 3 → one calculation", 6.8,
           D.ok_bd, SANS, "l")
    p.text(x0 + 5 * cw + 12, y + 4, "insert at front → 5 shifts", 6.8,
           D.bad_bd, SANS, "l")

    y2 = y - 76
    p.text(0, y2 + 36, "LINKED LIST", 8.0, D.violet_bd, SANS_SB, "l")
    p.text(0, y2 + 26, "scattered", 6.6, D.muted, SANS_I, "l")
    chain(p, x0, y2, [10, 20, 30, 40], w=44, h=22, gap=22, size=8.2)
    head_arrow(p, x0, y2, 22, w=44)
    p.text(x0 + 4 * 66 + 10, y2 + 14, "index 3 → walk 3 links", 6.8,
           D.bad_bd, SANS, "l")
    p.text(x0 + 4 * 66 + 10, y2 + 4, "insert at front → 2 writes", 6.8,
           D.ok_bd, SANS, "l")
    p.text(0, 4, "each structure is excellent at exactly what the other is bad at",
           7.0, D.ink, SANS_SB, "l")


@fig("ll_node")
def ll_node(p):
    """One node, labelled."""
    x, y = 140, p.h - 76
    node(p, x, y, 10, w=120, h=46, size=16)
    p.text(x + 34, y + 56, "data", 8.2, D.ok_bd, SANS_SB, "c")
    p.text(x + 94, y + 56, "next", 8.2, D.violet_bd, SANS_SB, "c")
    p.text(x + 34, y - 13, "the value", 6.8, D.muted, SANS_I, "c")
    p.text(x + 94, y - 13, "the address of", 6.8, D.muted, SANS_I, "c")
    p.text(x + 94, y - 22, "the next node", 6.8, D.muted, SANS_I, "c")
    p.arrow(x + 94, y + 23, x + 168, y + 23, D.violet_bd, 1.1, head=4)
    p.text(x + 184, y + 20, "…", 12, D.faint, SANS, "l")
    p.text(x + 130, y + 30, "the arrow is a drawing", 6.6, D.muted, SANS_I, "l")
    p.text(x + 130, y + 21, "of what that address means", 6.6, D.muted,
           SANS_I, "l")
    p.text(10, 8, "a node knows its value and where to go next — "
           "nothing about its position or the list as a whole",
           6.9, D.ink, SANS_SB, "l")


@fig("ll_anatomy")
def ll_anatomy(p):
    """A full three-node list, fully labelled."""
    y = p.h - 72
    xs = chain(p, 86, y, [10, 20, 30], w=58, h=26, gap=34, size=9.4)
    head_arrow(p, 86, y, 26, up=26, w=58)
    p.text(40, y + 36, "a VARIABLE,", 6.8, D.node_bd, SANS_SB, "l")
    p.text(40, y + 27, "not a node", 6.8, D.muted, SANS_I, "l")
    for i, x in enumerate(xs):
        p.text(x + 16, y - 12, "node %d" % i, 6.4, D.faint, SANS, "c")
    p.brace(xs[0], xs[0] + 58 * 0.56, y - 22, "data", up=False)
    p.brace(xs[0] + 58 * 0.56, xs[0] + 58, y - 22, "next", up=False)
    p.text(xs[2] + 72, y - 14, "nullptr = nothing follows", 6.8, D.muted,
           SANS_I, "c")
    p.text(10, 10, "head is a pointer · the nodes are heap objects · "
           "nullptr marks the end", 7.0, D.ink, SANS_SB, "l")


@fig("ll_scattered")
def ll_scattered(p):
    """Memory order has nothing to do with list order."""
    cw = 15
    n = 24
    x0, y = 24, p.h - 46
    slots = {3: ("30", "hi"), 9: ("10", "ok"), 15: ("40", "teal"),
             20: ("20", "violet")}
    kinds = ["dim"] * n
    vals = [""] * n
    for s, (v, k) in slots.items():
        for j in range(2):
            kinds[s + j] = k
        vals[s] = v
    p.cells(x0, y, vals, cw=cw, ch=20, kinds=kinds, index=False, size=7.2)
    for i in range(0, n, 4):
        p.text(x0 + i * cw + cw / 2, y - 10, str(2000 + i * 8), 5.4, D.faint,
               MONO, "c")
    p.text(x0, y - 22, "addresses increase left to right", 6.4, D.faint,
           SANS_I, "l")
    order = [9, 20, 3, 15]
    for a, b in zip(order, order[1:]):
        ax = x0 + a * cw + cw
        bx = x0 + b * cw + cw / 2
        p.curve(ax, y + 20, bx, y + 20, bulge=16 if bx > ax else -16,
                color=D.violet_bd, lw=0.95)
    p.arrow(x0 + 9 * cw + cw / 2, y + 44, x0 + 9 * cw + cw / 2, y + 22,
            D.node_bd, 1.0, head=3.4)
    p.text(x0 + 9 * cw + cw / 2, y + 48, "head", 7.2, D.node_bd, SANS_SB, "c")
    p.text(x0, 6, "list order is 10 → 20 → 30 → 40, and the addresses go "
           "the other way — the pointers are the only order there is",
           6.9, D.ink, SANS_SB, "l")


@fig("ll_traverse_cost")
def ll_traverse_cost(p):
    """Compute versus walk."""
    cw = 40
    x0, y = 64, p.h - 38
    p.text(0, y + 6, "ARRAY", 7.4, D.ok_bd, SANS_SB, "l")
    p.cells(x0, y, [10, 20, 30, 40], cw=cw, ch=20, index=True, size=8,
            kinds=["dim", "dim", "dim", "ok"])
    p.arrow(x0 + 3 * cw + cw / 2, y + 36, x0 + 3 * cw + cw / 2, y + 22,
            D.ok_bd, 1.1, head=3.6)
    p.text(x0 + 4 * cw + 14, y + 5, "one address calculation  →  O(1)", 6.9,
           D.ok_bd, SANS_SB, "l")

    y2 = y - 62
    p.text(0, y2 + 6, "LIST", 7.4, D.bad_bd, SANS_SB, "l")
    xs = chain(p, x0, y2, [10, 20, 30, 40], w=42, h=20, gap=20, size=8,
               kinds=["dim", "dim", "dim", "bad"])
    head_arrow(p, x0, y2, 20, up=18, w=42)
    for i in range(3):
        p.text(xs[i] + 42 + 10, y2 + 24, str(i + 1), 6.4, D.bad_bd, SANS_SB, "c")
    p.text(xs[3] + 60, y2 + 5, "three pointer hops  →  O(n)", 6.9, D.bad_bd,
           SANS_SB, "l")
    p.text(0, y2 - 18, "and each hop is a jump to an unpredictable address — "
           "usually a cache miss", 6.8, D.muted, SANS_I, "l")


@fig("ll_variants")
def ll_variants(p):
    """Singly, doubly, circular."""
    y0 = p.h - 34
    # singly
    p.text(0, y0 + 4, "SINGLY", 7.2, D.node_bd, SANS_SB, "l")
    chain(p, 76, y0 - 12, [10, 20, 30], w=48, h=20, gap=26, size=8)
    p.text(76, y0 - 28, "one pointer · forwards only · smallest", 6.5,
           D.muted, SANS_I, "l")

    # doubly
    y1 = y0 - 62
    p.text(0, y1 + 4, "DOUBLY", 7.2, D.violet_bd, SANS_SB, "l")
    xs = []
    for i, v in enumerate([10, 20, 30]):
        x = 76 + i * 74
        xs.append(x)
        p.box(x, y1 - 12, 48, 20, None, "violet", radius=1.8)
        p.text(x + 24, y1 - 5, str(v), 8, D.ink, MONO, "c")
    for i in range(2):
        p.arrow(xs[i] + 48, y1 - 3, xs[i + 1], y1 - 3, D.violet_bd, 0.9, head=3)
        p.arrow(xs[i + 1], y1 - 11, xs[i] + 48, y1 - 11, D.faint, 0.9, head=3)
    p.text(76, y1 - 28, "two pointers · both ways · O(1) delete of a held node",
           6.5, D.muted, SANS_I, "l")

    # circular
    y2 = y1 - 62
    p.text(0, y2 + 4, "CIRCULAR", 7.2, D.teal_bd, SANS_SB, "l")
    xs = []
    for i, v in enumerate([10, 20, 30]):
        x = 76 + i * 74
        xs.append(x)
        p.box(x, y2 - 12, 48, 20, None, "teal", radius=1.8)
        p.text(x + 24, y2 - 5, str(v), 8, D.ink, MONO, "c")
    for i in range(2):
        p.arrow(xs[i] + 48, y2 - 2, xs[i + 1], y2 - 2, D.teal_bd, 0.9, head=3)
    p.curve(xs[2] + 48, y2 - 8, xs[0], y2 - 8, bulge=-20, color=D.teal_bd,
            lw=1.0)
    p.text(76, y2 - 34, "no nullptr at all · the last points back to the first",
           6.5, D.muted, SANS_I, "l")


# -------------------------------------------------------- ch 24: building
@fig("ll_node_anatomy")
def ll_node_anatomy(p):
    """The struct mapped onto the object it builds."""
    lines = [("struct Node {", "a new type grouping two values"),
             ("    int data;", "the value stored here"),
             ("    Node* next;", "a POINTER to the next node"),
             ("    Node(int value) {", "the constructor — runs on new"),
             ("        data = value;", "store what was passed in"),
             ("        next = nullptr;", "so it is never garbage"),
             ("    }", ""),
             ("};", "the semicolon is required")]
    y = p.h - 22
    for i, (code, note) in enumerate(lines):
        yy = y - i * 14
        p.text(10, yy, code, 7.6, D.ink, MONO, "l")
        if note:
            p.text(150, yy, "— " + note, 6.3, D.muted, SANS_I, "l")
    x = 310
    ny = p.h - 74
    node(p, x, ny, 10, w=86, h=34, size=12)
    p.text(x + 43, ny + 42, "new Node(10)", 7.6, D.ok_bd, MONO_B, "c")
    p.text(x + 24, ny - 11, "data", 6.6, D.muted, SANS_SB, "c")
    p.text(x + 67, ny - 11, "next", 6.6, D.muted, SANS_SB, "c")
    null_cap(p, x + 90, ny, 34)
    p.text(x + 43, ny - 26, "one actual object", 6.6, D.muted, SANS_I, "c")
    p.text(x + 43, ny - 35, "on the heap", 6.6, D.muted, SANS_I, "c")
    p.text(10, 6, "the struct is a blueprint · new builds one object from it",
           7.0, D.ink, SANS_SB, "l")


@fig("ll_node_vs_ptr")
def ll_node_vs_ptr(p):
    """Three pointers, one node."""
    y = p.h - 60
    node(p, 230, y, 10, w=96, h=38, size=13)
    p.text(278, y + 46, "ONE node — a heap object", 7.4, D.ok_bd, SANS_SB, "c")
    p.text(278, y - 14, "28 bytes or so, holding data and next", 6.6,
           D.muted, SANS_I, "c")
    for i, (name, dy) in enumerate([("head", 34), ("curr", 6), ("p", -22)]):
        p.box(34, y + dy, 76, 22, None, "violet", radius=2)
        p.text(72, y + dy + 7, "3000", 7.6, D.violet_bd, MONO_B, "c")
        p.text(118, y + dy + 7, name, 7.6, D.ink, MONO_B, "l")
        p.arrow(152, y + dy + 11, 226, y + 19, D.violet_bd, 0.85, head=3)
    p.text(34, y - 44, "THREE Node* variables — 8 bytes each, on the stack",
           7.4, D.violet_bd, SANS_SB, "l")
    p.text(34, y - 56, "they all hold the same address, so they all name "
           "the same single node", 6.7, D.muted, SANS_I, "l")


@fig("ll_build_steps")
def ll_build_steps(p):
    """One node, then two, then three."""
    rows = [("new Node(10)", [10]),
            ("head->next = new Node(20)", [10, 20]),
            ("head->next->next = new Node(30)", [10, 20, 30])]
    y0 = p.h - 46
    for r, (code, vals) in enumerate(rows):
        y = y0 - r * 56
        p.text(0, y + 26, code, 7.2, D.ok_bd, MONO, "l")
        kinds = ["dim"] * (len(vals) - 1) + ["ok"]
        chain(p, 76, y, vals, w=48, h=22, gap=26, size=8.4, kinds=kinds)
        head_arrow(p, 76, y, 22, up=16, w=48)
    p.text(0, y0 - 3 * 56 + 22,
           "at every step the last node's next is nullptr — "
           "so the list is valid the whole way through",
           6.9, D.ink, SANS_SB, "l")


@fig("ll_traverse_steps")
def ll_traverse_steps(p):
    """curr walks; head does not."""
    y0 = p.h - 42
    for step in range(4):
        y = y0 - step * 42
        kinds = ["ok" if i < step else ("hi" if i == step else "dim")
                 for i in range(3)]
        xs = chain(p, 92, y, [10, 20, 30], w=46, h=20, gap=24, size=8,
                   kinds=kinds)
        head_arrow(p, 92, y, 20, up=14, w=46)
        if step < 3:
            p.pointer(xs[step] + 46 * 0.56 / 2 + 22, y + 20, "curr")
        else:
            p.text(xs[2] + 92, y + 6, "curr = nullptr  →  loop ends", 6.9,
                   D.bad_bd, SANS_SB, "l")
        if step < 3:
            p.text(xs[2] + 92, y + 6, "print %d" % [10, 20, 30][step], 6.9,
                   D.muted, SANS, "l")
    p.text(0, y0 - 4 * 42 + 16,
           "head never moves — it is the list's identity. curr does the walking.",
           7.0, D.ink, SANS_SB, "l")


@fig("ll_free")
def ll_free(p):
    """Save next, advance, then delete."""
    y = p.h - 56
    steps = [("1. doomed = curr", "ok", "remember the node"),
             ("2. curr = curr->next", "hi", "step past it FIRST"),
             ("3. delete doomed", "bad", "now it is safe to destroy")]
    xs = chain(p, 90, y, [10, 20, 30], w=48, h=22, gap=26, size=8.4,
               kinds=["bad", "hi", "dim"])
    p.pointer(xs[0] + 14, y + 22, "doomed")
    p.pointer(xs[1] + 14, y + 22, "curr")
    head_arrow(p, 90, y, 22, up=44, w=48)
    for i, (code, kind, note) in enumerate(steps):
        yy = y - 42 - i * 22
        p.box(16, yy, 150, 18, None, kind, radius=2)
        p.text(24, yy + 6, code, 7.2, D.ink, MONO, "l")
        p.text(176, yy + 6, note, 6.8, D.muted, SANS_I, "l")
    p.text(16, y - 42 - 3 * 22 - 6,
           "reversing steps 2 and 3 reads curr->next through a freed pointer",
           7.0, D.bad_bd, SANS_SB, "l")


# ---------------------------------------------- ch 25/26: insert and delete
@fig("ins_order_rule")
def ins_order_rule(p):
    """Forwards first, or lose the tail."""
    for col, (title, ok, note) in enumerate([
            ("CORRECT  —  forwards first", True,
             "node->next = prev->next;   then   prev->next = node;"),
            ("WRONG  —  backwards first", False,
             "prev->next = node;   then   node->next = prev->next;")]):
        x0 = 8 + col * 210
        y = p.h - 48
        p.text(x0, y + 44, title, 7.2, D.ok_bd if ok else D.bad_bd,
               SANS_SB, "l")
        xs = chain(p, x0, y, [10, 20], w=40, h=20, gap=18, size=7.6,
                   kinds=["dim", "dim"], end=None)
        p.text(x0 + 2 * 58 + 2, y + 6, "30", 7.6, D.faint, MONO, "l")
        # the new node, below
        nx = x0 + 22
        node(p, nx, y - 36, 15, w=40, h=20, kind="ok", size=7.6)
        if ok:
            p.arrow(nx + 40 * 0.78, y - 26, xs[1] - 2, y + 4, D.ok_bd, 1.0,
                    head=3.2)
            p.arrow(xs[0] + 40 * 0.78, y + 8, nx + 12, y - 14, D.ok_bd, 1.0,
                    head=3.2)
            p.text(x0, y - 52, "nothing is ever unreachable", 6.7, D.ok_bd,
                   SANS_SB, "l")
        else:
            p.arrow(xs[0] + 40 * 0.78, y + 8, nx + 12, y - 14, D.bad_bd, 1.0,
                    head=3.2)
            p.arrow(nx + 40 * 0.78, y - 26, nx + 12, y - 30, D.bad_bd, 1.0,
                    head=3.2)
            p.text(xs[1], y + 24, "20, 30", 7.0, D.bad_bd, SANS_SB, "l")
            p.text(xs[1], y + 15, "LOST", 7.0, D.bad_bd, SANS_SB, "l")
            p.text(x0, y - 52, "the only pointer to the tail was overwritten",
                   6.7, D.bad_bd, SANS_SB, "l")
        p.text(x0, y - 66, note, 6.2, D.muted, MONO, "l")


@fig("ins_front")
def ins_front(p):
    """Two assignments."""
    y0 = p.h - 46
    rows = [("before", [10, 20, 30], None),
            ("1. node->next = head", [5, 10, 20, 30], 0),
            ("2. head = node", [5, 10, 20, 30], 0)]
    for r, (label, vals, newi) in enumerate(rows):
        y = y0 - r * 50
        kinds = ["ok" if i == newi else "dim" for i in range(len(vals))]
        chain(p, 110, y, vals, w=42, h=20, gap=22, size=8, kinds=kinds)
        p.text(102, y + 6, label, 6.8, D.muted, SANS_SB, "r")
        if r == 0:
            head_arrow(p, 110, y, 20, up=14, w=42)
        elif r == 1:
            head_arrow(p, 110 + 64, y, 20, up=14, w=42)
        else:
            head_arrow(p, 110, y, 20, up=14, w=42)
    p.text(16, y0 - 3 * 50 + 16, "O(1) — nothing is traversed, two assignments",
           7.0, D.ok_bd, SANS_SB, "l")
    p.text(16, y0 - 3 * 50 + 4,
           "the empty list needs no special case: node->next = nullptr is exactly right",
           6.7, D.muted, SANS_I, "l")


@fig("ins_back")
def ins_back(p):
    """Walk to the last node, then attach."""
    y = p.h - 48
    xs = chain(p, 86, y, [10, 20, 30], w=48, h=22, gap=28, size=8.4,
               kinds=["dim", "dim", "hi"])
    head_arrow(p, 86, y, 22, up=20, w=48)
    for i in range(2):
        p.text(xs[i] + 48 + 12, y + 28, str(i + 1), 6.4, D.faint, SANS_SB, "c")
    p.pointer(xs[2] + 14, y + 22, "curr stops HERE")
    p.text(16, y - 22, "while (curr->next != nullptr)   ✓   stops ON the last node",
           7.0, D.ok_bd, MONO, "l")
    p.text(16, y - 34, "while (curr != nullptr)         ✗   walks past it, then crashes",
           7.0, D.bad_bd, MONO, "l")
    y2 = y - 62
    chain(p, 86, y2, [10, 20, 30, 40], w=48, h=22, gap=28, size=8.4,
          kinds=["dim", "dim", "dim", "ok"])
    head_arrow(p, 86, y2, 22, up=16, w=48)
    p.text(16, y2 - 18, "O(n) — the walk dominates; a tail pointer makes it O(1)",
           7.0, D.ink, SANS_SB, "l")


@fig("ins_position")
def ins_position(p):
    """Walk to the node before, then the usual two assignments."""
    y = p.h - 48
    xs = chain(p, 80, y, [10, 20, 30], w=46, h=22, gap=26, size=8.4,
               kinds=["dim", "hi", "dim"])
    head_arrow(p, 80, y, 22, up=18, w=46)
    p.pointer(xs[1] + 13, y + 22, "prev  (index 1)")
    p.text(16, y - 20, "walk pos-1 = 1 step to reach the node BEFORE index 2",
           6.9, D.muted, SANS_I, "l")
    y2 = y - 56
    chain(p, 80, y2, [10, 20, 25, 30], w=46, h=22, gap=26, size=8.4,
          kinds=["dim", "dim", "ok", "dim"])
    head_arrow(p, 80, y2, 22, up=16, w=46)
    p.box(16, y2 - 40, p.w - 32, 30, None, "ok", radius=3)
    p.text(28, y2 - 20, "node->next = prev->next;        prev->next = node;",
           8.0, D.ink, MONO_B, "l")
    p.text(28, y2 - 31, "the same two lines as every other insertion — "
           "only the walking changes", 6.6, D.muted, SANS_I, "l")


@fig("ins_after")
def ins_after(p):
    """No walking at all."""
    y = p.h - 50
    xs = chain(p, 80, y, [10, 20, 30], w=48, h=22, gap=32, size=8.4,
               kinds=["dim", "hi", "dim"])
    p.pointer(xs[1] + 13, y + 22, "node — you already hold it")
    nx = xs[1] + 24
    node(p, nx, y - 44, 25, w=48, h=22, kind="ok", size=8.4)
    p.arrow(nx + 48 * 0.78, y - 34, xs[2] - 2, y + 6, D.ok_bd, 1.0, head=3.2)
    p.arrow(xs[1] + 48 * 0.78, y + 8, nx + 14, y - 20, D.ok_bd, 1.0, head=3.2)
    p.text(16, y - 62, "two assignments, no traversal  →  genuinely O(1)",
           7.2, D.ok_bd, SANS_SB, "l")
    p.text(16, y - 74, "an array would still have to shift every later element",
           6.8, D.muted, SANS_I, "l")


@fig("del_order_rule")
def del_order_rule(p):
    """Unlink, then free."""
    for col, (title, ok, lines) in enumerate([
            ("CORRECT  —  unlink first", True,
             ["prev->next = doomed->next;", "delete doomed;"]),
            ("WRONG  —  free first", False,
             ["delete doomed;", "prev->next = doomed->next;"])]):
        x0 = 8 + col * 210
        y = p.h - 48
        p.text(x0, y + 40, title, 7.2, D.ok_bd if ok else D.bad_bd,
               SANS_SB, "l")
        xs = chain(p, x0, y, [10, 20, 30], w=38, h=20, gap=16, size=7.4,
                   kinds=["dim", "bad", "dim"])
        if ok:
            p.curve(xs[0] + 38 * 0.78, y + 16, xs[2] + 6, y + 16, bulge=14,
                    color=D.ok_bd, lw=1.1)
            p.text(x0, y - 22, "nothing points at the doomed node", 6.7,
                   D.ok_bd, SANS_SB, "l")
            p.text(x0, y - 32, "when it is freed", 6.7, D.ok_bd, SANS_SB, "l")
        else:
            p.text(xs[1] + 4, y + 26, "freed", 6.6, D.bad_bd, SANS_SB, "l")
            p.text(x0, y - 22, "prev->next still points at freed", 6.7,
                   D.bad_bd, SANS_SB, "l")
            p.text(x0, y - 32, "memory — the next traversal walks in", 6.7,
                   D.bad_bd, SANS_SB, "l")
        for i, ln in enumerate(lines):
            p.text(x0, y - 50 - i * 12, ln, 6.9, D.ink, MONO, "l")


@fig("del_front")
def del_front(p):
    """Save, unlink, free."""
    y0 = p.h - 42
    rows = [("before", [10, 20, 30], 0, 0),
            ("head = head->next", [10, 20, 30], 0, 1),
            ("delete doomed", [20, 30], None, 0)]
    for r, (label, vals, doomed, headi) in enumerate(rows):
        y = y0 - r * 48
        kinds = ["bad" if i == doomed else "dim" for i in range(len(vals))]
        chain(p, 118, y, vals, w=44, h=20, gap=22, size=8, kinds=kinds)
        p.text(110, y + 6, label, 6.7, D.muted, SANS_SB, "r")
        head_arrow(p, 118 + headi * 66, y, 20, up=14, w=44)
        if r < 2 and doomed is not None:
            p.text(118 + 12, y - 11, "doomed", 6.2, D.bad_bd, SANS_SB, "c")
    p.text(16, y0 - 3 * 48 + 14,
           "O(1) · the one-node list works naturally, because head->next is already nullptr",
           6.9, D.ok_bd, SANS_SB, "l")


@fig("del_back")
def del_back(p):
    """Stop on the second-to-last."""
    y = p.h - 48
    xs = chain(p, 86, y, [10, 20, 30], w=48, h=22, gap=28, size=8.4,
               kinds=["dim", "hi", "bad"])
    head_arrow(p, 86, y, 22, up=20, w=48)
    p.pointer(xs[1] + 13, y + 22, "prev stops HERE")
    p.text(16, y - 22, "while (prev->next->next != nullptr)   — the node whose GRANDCHILD does not exist",
           6.8, D.ok_bd, MONO, "l")
    y2 = y - 52
    chain(p, 86, y2, [10, 20], w=48, h=22, gap=28, size=8.4,
          kinds=["dim", "dim"])
    head_arrow(p, 86, y2, 22, up=16, w=48)
    p.text(16, y2 - 20, "the single-node list is a genuine special case: "
           "there is no second-to-last node", 6.9, D.bad_bd, SANS_SB, "l")
    p.text(16, y2 - 32, "O(n) even with a tail pointer — you still have to FIND the new tail",
           6.9, D.muted, SANS_I, "l")


@fig("del_position")
def del_position(p):
    """prev stops one before."""
    y = p.h - 46
    xs = chain(p, 80, y, [10, 20, 30, 40], w=44, h=22, gap=24, size=8.4,
               kinds=["dim", "hi", "bad", "dim"])
    head_arrow(p, 80, y, 22, up=18, w=44)
    p.pointer(xs[1] + 12, y + 22, "prev")
    p.pointer(xs[2] + 12, y - 26, "doomed", color=D.bad_bd)
    p.curve(xs[1] + 44 * 0.78, y + 18, xs[3] + 4, y + 18, bulge=16,
            color=D.ok_bd, lw=1.1)
    p.text(16, y - 46, "prev->next = doomed->next;     then     delete doomed;",
           7.6, D.ink, MONO_B, "l")
    p.text(16, y - 58, "index 0 still needs its own branch, because the head has no predecessor",
           6.8, D.muted, SANS_I, "l")


@fig("del_prev_curr")
def del_prev_curr(p):
    """The pair that moves together."""
    y0 = p.h - 40
    for step in range(3):
        y = y0 - step * 44
        kinds = ["dim"] * 4
        kinds[step] = "teal"
        kinds[step + 1] = "hi"
        xs = chain(p, 96, y, [10, 20, 30, 20], w=44, h=20, gap=22, size=8,
                   kinds=kinds)
        p.pointer(xs[step] + 12, y + 20, "prev")
        p.text(xs[step + 1] + 12, y - 11, "curr", 6.4, D.hi_bd, SANS_SB, "c")
        if step == 2:
            p.text(xs[3] + 60, y + 6, "match — prev is already", 6.8,
                   D.ok_bd, SANS_SB, "l")
            p.text(xs[3] + 60, y - 4, "the node to reroute", 6.8, D.ok_bd,
                   SANS_SB, "l")
    p.text(16, y0 - 3 * 44 + 14,
           "they advance together and stay adjacent — so prev is never stale",
           7.0, D.ink, SANS_SB, "l")


# ------------------------------------------------- ch 27: doubly / circular
def _dnode(p, x, y, v, w=50, h=24, kind="violet", size=8.6):
    """A doubly linked node: prev | data | next."""
    third = w / 4.0
    p.box(x, y, third, h, None, "dim", radius=1.6)
    p.box(x + third, y, w - 2 * third, h, None, kind, radius=1.6)
    p.box(x + w - third, y, third, h, None, "dim", radius=1.6)
    p.text(x + w / 2, y + h / 2 - size * 0.35, str(v), size, D.ink, MONO, "c")
    p.circle(x + third / 2, y + h / 2, 1.8, None, "solid", lw=0.0)
    p.circle(x + w - third / 2, y + h / 2, 1.8, None, "solid", lw=0.0)
    return (x + third / 2, x + w - third / 2, y + h / 2)


@fig("dll_anatomy")
def dll_anatomy(p):
    """Every link exists twice."""
    y = p.h - 62
    w, gap = 58, 40
    xs, links = [], []
    for i, v in enumerate([10, 20, 30]):
        x = 80 + i * (w + gap)
        xs.append(x)
        links.append(_dnode(p, x, y, v, w=w, h=26))
    for i in range(2):
        p.arrow(links[i][1], links[i][2] + 4, xs[i + 1] - 2, links[i][2] + 4,
                D.violet_bd, 1.0, head=3.4)
        p.arrow(links[i + 1][0], links[i + 1][2] - 5, xs[i] + w + 2,
                links[i][2] - 5, D.teal_bd, 1.0, head=3.4)
    null_cap(p, links[2][1] + 5, y, 26)
    null_cap(p, xs[0] - 24, y, 26, label=None)
    p.text(xs[0] + 7, y + 32, "prev", 6.4, D.teal_bd, SANS_SB, "c")
    p.text(xs[0] + w / 2, y + 32, "data", 6.4, D.ink, SANS_SB, "c")
    p.text(xs[0] + w - 7, y + 32, "next", 6.4, D.violet_bd, SANS_SB, "c")
    p.box(30, 12, p.w - 60, 26, None, "ok", radius=3)
    p.text(44, 28, "the invariant:     a->next == b     ⟺     b->prev == a",
           8.4, D.ink, MONO_B, "l")
    p.text(44, 17, "every operation must leave this true in BOTH directions",
           6.6, D.muted, SANS_I, "l")


@fig("dll_insert")
def dll_insert(p):
    """Four pointers change, not two."""
    y = p.h - 58
    w, gap = 54, 56
    xs, links = [], []
    for i, v in enumerate([10, 30]):
        x = 92 + i * (w + gap)
        xs.append(x)
        links.append(_dnode(p, x, y, v, w=w, h=24, kind="dim"))
    nx = xs[0] + w + 3
    nl = _dnode(p, nx, y - 44, 20, w=w, h=24, kind="ok")
    pairs = [(links[0][1], links[0][2] + 3, nl[0] + 10, y - 44 + 20, "1"),
             (nl[0], nl[2], xs[0] + w - 6, y + 6, "2"),
             (nl[1], nl[2], xs[1] + 4, y + 6, "3"),
             (links[1][0], links[1][2] - 4, nx + w - 6, y - 44 + 10, "4")]
    for i, (ax, ay, bx, by, lab) in enumerate(pairs):
        p.arrow(ax, ay, bx, by, D.ok_bd if i < 2 else D.teal_bd, 0.95, head=3.2)
    p.text(16, y - 72, "1. fresh->next = node->next     3. node->next->prev = fresh",
           7.0, D.ink, MONO, "l")
    p.text(16, y - 83, "2. fresh->prev = node           4. node->next = fresh",
           7.0, D.ink, MONO, "l")
    p.text(16, y - 97, "four assignments instead of two — and missing one leaves "
           "the list correct forwards and broken backwards",
           6.7, D.bad_bd, SANS_SB, "l")


@fig("dll_delete")
def dll_delete(p):
    """O(1), because the node knows its predecessor."""
    y = p.h - 56
    w, gap = 56, 44
    xs, links = [], []
    for i, v in enumerate([10, 20, 30]):
        x = 76 + i * (w + gap)
        xs.append(x)
        links.append(_dnode(p, x, y, v, w=w, h=24,
                            kind="bad" if i == 1 else "dim"))
    p.pointer(xs[1] + w / 2, y + 24, "node — you hold it")
    p.curve(links[0][1], y + 20, xs[2] + 4, y + 20, bulge=16, color=D.ok_bd,
            lw=1.2)
    p.curve(links[2][0], y - 2, xs[0] + w - 6, y - 2, bulge=-16,
            color=D.teal_bd, lw=1.2)
    p.text(16, y - 34, "node->prev->next = node->next;    node->next->prev = node->prev;",
           7.4, D.ink, MONO, "l")
    p.text(16, y - 48, "no walking at all  →  O(1).  In a singly linked list "
           "you would have to find the predecessor: O(n).",
           6.9, D.ok_bd, SANS_SB, "l")
    p.text(16, y - 60, "this one fact is why LRU caches and std::list are doubly linked",
           6.8, D.muted, SANS_I, "l")


@fig("cll_shape")
def cll_shape(p):
    """No nullptr anywhere."""
    import math
    cx, cy, r = 130, p.h / 2 - 6, 50
    vals = [10, 20, 30, 40, 50]
    pos = []
    for i, v in enumerate(vals):
        a = math.pi / 2 - i * 2 * math.pi / len(vals)
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(len(vals)):
        a, b = pos[i], pos[(i + 1) % len(vals)]
        p.arrow(a[0], a[1], b[0], b[1], D.teal_bd, 0.95, head=3.2, shrink=14)
    for (px, py), v in zip(pos, vals):
        p.circle(px, py, 12, str(v), "teal", size=8)
    p.arrow(cx, cy + r + 30, cx, cy + r + 14, D.node_bd, 1.0, head=3.4)
    p.text(cx, cy + r + 33, "head", 7.2, D.node_bd, SANS_SB, "c")

    bx = 232
    p.text(bx, cy + 48, "while (curr != nullptr)", 7.8, D.bad_bd, MONO, "l")
    p.text(bx, cy + 37, "✗  there is no nullptr — this never ends", 6.8,
           D.bad_bd, SANS, "l")
    p.text(bx, cy + 14, "do {", 7.8, D.ok_bd, MONO, "l")
    p.text(bx, cy + 3, "    visit(curr);", 7.8, D.ok_bd, MONO, "l")
    p.text(bx, cy - 8, "    curr = curr->next;", 7.8, D.ok_bd, MONO, "l")
    p.text(bx, cy - 19, "} while (curr != head);", 7.8, D.ok_bd, MONO, "l")
    p.text(bx, cy - 34, "✓  stops when it comes back round", 6.8, D.ok_bd,
           SANS, "l")
    p.text(bx, cy - 48, "a do-while, because curr == head", 6.6, D.muted,
           SANS_I, "l")
    p.text(bx, cy - 57, "is already true at the start", 6.6, D.muted,
           SANS_I, "l")


# ------------------------------------------------------- ch 28: reversal
@fig("rev_before_after")
def rev_before_after(p):
    """Same nodes, every arrow turned round."""
    y = p.h - 46
    chain(p, 94, y, [10, 20, 30], w=48, h=22, gap=28, size=8.6)
    head_arrow(p, 94, y, 22, up=16, w=48)
    p.text(86, y + 6, "before", 6.9, D.muted, SANS_SB, "r")
    y2 = y - 58
    chain(p, 94, y2, [30, 20, 10], w=48, h=22, gap=28, size=8.6,
          kinds=["ok"] * 3)
    head_arrow(p, 94, y2, 22, up=16, w=48)
    p.text(86, y2 + 6, "after", 6.9, D.muted, SANS_SB, "r")
    p.text(16, y2 - 20, "no node moves in memory and none is created — "
           "only the next pointers change", 7.0, D.ink, SANS_SB, "l")
    p.text(16, y2 - 32, "head ends up naming what used to be the last node",
           6.8, D.muted, SANS_I, "l")


def _rev_state(p, y, reversed_vals, curr_vals, prev_x=None, labels=True,
               w=44, gap=24):
    """Draw the reversed-so-far chain and the untouched remainder."""
    x0 = 70
    xs = []
    if reversed_vals:
        xs = chain(p, x0, y, reversed_vals, w=w, h=20, gap=gap, size=8,
                   kinds=["ok"] * len(reversed_vals))
    x1 = x0 + max(len(reversed_vals), 0) * (w + gap) + 24
    xs2 = []
    if curr_vals:
        xs2 = chain(p, x1, y, curr_vals, w=w, h=20, gap=gap, size=8,
                    kinds=["hi"] + ["dim"] * (len(curr_vals) - 1))
    return xs, xs2


@fig("rev_three_pointers")
def rev_three_pointers(p):
    """prev, curr, nextNode at the start of a body."""
    y = p.h - 54
    xs = chain(p, 54, y, [10], w=48, h=22, gap=30, size=8.6, kinds=["ok"])
    xs2 = chain(p, 164, y, [20, 30], w=48, h=22, gap=30, size=8.6,
                kinds=["hi", "dim"])
    p.pointer(xs[0] + 13, y + 22, "prev")
    p.pointer(xs2[0] + 13, y + 22, "curr")
    p.pointer(xs2[1] + 13, y + 22, "nextNode")
    p.text(54, y - 22, "already reversed", 6.7, D.ok_bd, SANS_SB, "l")
    p.text(164, y - 22, "being turned round now", 6.7, D.hi_bd, SANS_SB, "l")
    p.text(242, y - 32, "not yet touched", 6.7, D.muted, SANS_I, "l")
    p.box(30, 10, p.w - 60, 26, None, "dim", radius=3)
    p.text(44, 26, "prev = where we came from · curr = where we are · "
           "nextNode = where we were going", 7.4, D.ink, SANS_SB, "l")
    p.text(44, 15, "all three advance by one node each iteration", 6.6,
           D.muted, SANS_I, "l")


@fig("rev_iteration1")
def rev_iteration1(p):
    """After line 2 the list is in two pieces."""
    y = p.h - 40
    p.text(0, y + 20, "after line 1  —  nextNode saved", 7.2, D.muted,
           SANS_SB, "l")
    xs = chain(p, 70, y, [10, 20, 30], w=44, h=20, gap=24, size=8,
               kinds=["hi", "dim", "dim"])
    p.pointer(xs[0] + 12, y + 20, "curr")
    p.pointer(xs[1] + 12, y - 24, "nextNode", color=D.violet_bd)

    y2 = y - 72
    p.text(0, y2 + 24, "after line 2  —  curr->next = prev", 7.2, D.bad_bd,
           SANS_SB, "l")
    n1 = node(p, 70, y2, 10, "ok", w=44, h=20, size=8)
    null_cap(p, n1[0] + 4, y2, 20)
    xs2 = chain(p, 180, y2, [20, 30], w=44, h=20, gap=24, size=8,
                kinds=["dim", "dim"])
    p.pointer(70 + 12, y2 + 20, "curr")
    p.pointer(xs2[0] + 12, y2 - 24, "nextNode", color=D.violet_bd)
    p.text(0, y2 - 44, "the list is now in TWO pieces, and nextNode is the "
           "only pointer to the second one", 6.9, D.bad_bd, SANS_SB, "l")
    p.text(0, y2 - 56, "which is exactly why line 1 had to come first",
           6.8, D.muted, SANS_I, "l")


@fig("rev_iteration2")
def rev_iteration2(p):
    """The reversed chain grows behind prev."""
    y = p.h - 40
    p.text(0, y + 22, "start of iteration 2", 7.2, D.muted, SANS_SB, "l")
    n1 = node(p, 70, y, 10, "ok", w=44, h=20, size=8)
    null_cap(p, n1[0] + 4, y, 20)
    xs = chain(p, 180, y, [20, 30], w=44, h=20, gap=24, size=8,
               kinds=["hi", "dim"])
    p.pointer(70 + 12, y + 20, "prev")
    p.pointer(xs[0] + 12, y + 20, "curr")

    y2 = y - 70
    p.text(0, y2 + 22, "end of iteration 2", 7.2, D.ok_bd, SANS_SB, "l")
    xs2 = chain(p, 70, y2, [20, 10], w=44, h=20, gap=24, size=8,
                kinds=["ok", "ok"])
    xs3 = chain(p, 248, y2, [30], w=44, h=20, gap=24, size=8, kinds=["hi"])
    p.pointer(xs2[0] + 12, y2 + 20, "prev")
    p.pointer(xs3[0] + 12, y2 + 20, "curr")
    p.text(0, y2 - 26, "prev always points at the head of the reversed portion so far",
           7.0, D.ok_bd, SANS_SB, "l")


@fig("rev_final")
def rev_final(p):
    """curr falls off; prev is the new head."""
    y = p.h - 48
    xs = chain(p, 100, y, [30, 20, 10], w=48, h=22, gap=28, size=8.6,
               kinds=["ok"] * 3)
    p.pointer(xs[0] + 13, y + 22, "prev  —  the new head")
    p.text(xs[2] + 76, y + 6, "curr = nullptr", 7.6, D.bad_bd, MONO, "l")
    p.text(xs[2] + 76, y - 4, "loop ends", 6.8, D.muted, SANS_I, "l")
    p.box(30, 12, p.w - 60, 30, None, "ok", radius=3)
    p.text(44, 30, "head = prev;", 9.0, D.ink, MONO_B, "l")
    p.text(44, 19, "forget this and head still names node(10), which is now the "
           "LAST node — you get a one-element list", 6.5, D.bad_bd, SANS_SB, "l")


@fig("rev_why_save")
def rev_why_save(p):
    """Without nextNode, the tail is orphaned."""
    y = p.h - 50
    p.text(0, y + 24, "curr->next = prev;   with no saved pointer", 7.4,
           D.bad_bd, MONO, "l")
    n1 = node(p, 70, y, 10, "bad", w=46, h=22, size=8.4)
    null_cap(p, n1[0] + 4, y, 22)
    p.pointer(70 + 13, y + 22, "curr")
    xs = chain(p, 210, y, [20, 30], w=46, h=22, gap=26, size=8.4,
               kinds=["dim", "dim"])
    p.text(210, y + 34, "still on the heap", 6.8, D.bad_bd, SANS_SB, "l")
    p.text(210, y + 25, "nothing points here", 6.8, D.bad_bd, SANS_SB, "l")
    p.text(0, y - 28, "prev points backwards · head is behind us · "
           "curr->next has just been overwritten", 6.9, D.muted, SANS_I, "l")
    p.text(0, y - 42, "nextNode is a lifeline thrown ahead before the rope "
           "behind is cut", 7.2, D.ink, SANS_SB, "l")


@fig("rev_wrong_orders")
def rev_wrong_orders(p):
    """Three mistakes, three symptoms."""
    rows = [
        ("A. reverse before saving", "bad",
         "curr->next = prev;  nextNode = curr->next;",
         "nextNode becomes prev — loop ends at once",
         "SYMPTOM: a one-element list"),
        ("B. advance curr before prev", "bad",
         "curr = nextNode;  prev = curr;",
         "prev == curr, so each node points at itself",
         "SYMPTOM: printing hangs forever"),
        ("C. forget head = prev", "hi",
         "(every pointer correct, head left behind)",
         "head still names the old first node",
         "SYMPTOM: a one-element list"),
    ]
    y0 = p.h - 28
    for i, (title, kind, code, why, sym) in enumerate(rows):
        y = y0 - i * 56
        p.box(10, y - 6, 150, 20, None, kind, radius=2)
        p.text(18, y, title, 7.0, D.ink, SANS_SB, "l")
        p.text(172, y + 6, code, 6.6, D.ink, MONO, "l")
        p.text(172, y - 4, why, 6.5, D.muted, SANS_I, "l")
        p.text(172, y - 15, sym, 6.8, D.bad_bd, SANS_SB, "l")
    p.text(10, y0 - 3 * 56 + 6,
           "each failure has its own symptom — which is how you work out "
           "which line is wrong", 7.0, D.ink, SANS_SB, "l")


@fig("rev_recursive")
def rev_recursive(p):
    """Down to the end, then reverse on the way back."""
    y = p.h - 34
    for i, (call, vals) in enumerate([
            ("reverseRecursive(10)", [10, 20, 30]),
            ("reverseRecursive(20)", [20, 30]),
            ("reverseRecursive(30)", [30])]):
        yy = y - i * 26
        p.text(14 + i * 14, yy, call, 7.2, D.muted, MONO, "l")
        p.text(190, yy, "→ " + " ".join(str(v) for v in vals), 7.0, D.faint,
               MONO, "l")
    p.text(14 + 3 * 14, y - 3 * 26, "base case: return head", 7.2, D.ok_bd,
           MONO, "l")
    y2 = y - 4 * 26 - 14
    p.text(14, y2 + 14, "on the way back out, at head = node(10):", 7.2,
           D.ink, SANS_SB, "l")
    p.text(14, y2, "head->next->next = head;", 8.0, D.ok_bd, MONO_B, "l")
    p.text(190, y2, "node(20) now points BACK at node(10)", 6.7, D.muted,
           SANS_I, "l")
    p.text(14, y2 - 13, "head->next = nullptr;", 8.0, D.ok_bd, MONO_B, "l")
    p.text(190, y2 - 13, "cuts the cycle that would otherwise remain", 6.7,
           D.muted, SANS_I, "l")
    p.box(10, 8, p.w - 20, 24, None, "bad", radius=3)
    p.text(22, 24, "O(n) time — but O(n) STACK, one frame per node", 7.6,
           D.bad_bd, SANS_SB, "l")
    p.text(22, 13, "a list of 100,000 nodes overflows the stack; the iterative "
           "version uses three variables", 6.6, D.muted, SANS_I, "l")
