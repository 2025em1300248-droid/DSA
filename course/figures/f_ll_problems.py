"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


@fig("pat_dummy")
def pat_dummy(p):
    """A fake node in front removes the special case."""
    y = p.h - 50
    p.text(0, y + 30, "WITHOUT A DUMMY", 7.2, D.bad_bd, SANS_SB, "l")
    xs = chain(p, 108, y, [10, 20, 30], w=46, h=22, gap=24, size=8.4,
               kinds=["bad", "dim", "dim"])
    head_arrow(p, 108, y, 22, up=16, w=46)
    p.text(xs[0] - 8, y - 12, "no predecessor  →  its own branch", 6.7,
           D.bad_bd, SANS_SB, "l")

    y2 = y - 72
    p.text(0, y2 + 30, "WITH A DUMMY", 7.2, D.ok_bd, SANS_SB, "l")
    node(p, 108, y2, "—", kind="teal", w=46, h=22, size=8.4)
    p.arrow(108 + 46 * 0.78, y2 + 11, 108 + 70 - 2, y2 + 11, D.arrow, 0.95,
            head=3.4)
    xs2 = chain(p, 108 + 70, y2, [10, 20, 30], w=46, h=22, gap=24, size=8.4,
                kinds=["ok", "dim", "dim"])
    p.text(108 + 23, y2 + 28, "dummy", 6.8, D.teal_bd, SANS_SB, "c")
    p.text(108 + 23, y2 - 12, "on the stack", 6.4, D.muted, SANS_I, "c")
    p.text(xs2[0] - 8, y2 - 24, "now every real node has a predecessor  →  one uniform loop",
           6.9, D.ok_bd, SANS_SB, "l")
    p.text(0, y2 - 40, "return dummy.next — correct even if every node was deleted",
           7.0, D.ink, MONO, "l")


@fig("pat_fast_slow")
def pat_fast_slow(p):
    """Two speeds."""
    y0 = p.h - 34
    vals = [1, 2, 3, 4, 5]
    for step in range(4):
        y = y0 - step * 36
        s, f = step, min(2 * step, 5)
        kinds = ["dim"] * 5
        if s < 5:
            kinds[s] = "ok"
        if f < 5:
            kinds[f] = "hi"
        xs = chain(p, 96, y, vals, w=40, h=20, gap=20, size=8, kinds=kinds)
        if s < 5:
            p.text(xs[s] + 11, y - 11, "slow", 6.2, D.ok_bd, SANS_SB, "c")
        if f < 5:
            p.text(xs[f] + 11, y + 22, "fast", 6.2, D.hi_bd, SANS_SB, "c")
        else:
            p.text(xs[4] + 54, y + 6, "fast is past the end", 6.6, D.hi_bd,
                   SANS, "l")
        p.text(80, y + 6, "%d" % step, 6.4, D.faint, MONO, "r")
    p.text(16, y0 - 4 * 36 + 10,
           "fast covers twice the ground, so slow lands exactly halfway",
           7.0, D.ink, SANS_SB, "l")


@fig("pat_gap")
def pat_gap(p):
    """Send one pointer k ahead, then move together."""
    y0 = p.h - 36
    vals = [10, 20, 30, 40, 50]
    rows = [(0, 2, "lead moves k = 2 ahead"),
            (1, 3, "now both move together"),
            (2, 4, "the gap never changes"),
            (3, 5, "lead off the end → trail is k from it")]
    for r, (t, l, note) in enumerate(rows):
        y = y0 - r * 34
        kinds = ["dim"] * 5
        if t < 5:
            kinds[t] = "ok"
        if l < 5:
            kinds[l] = "hi"
        xs = chain(p, 92, y, vals, w=40, h=20, gap=20, size=8, kinds=kinds)
        if t < 5:
            p.text(xs[t] + 11, y - 11, "trail", 6.2, D.ok_bd, SANS_SB, "c")
        if l < 5:
            p.text(xs[l] + 11, y + 22, "lead", 6.2, D.hi_bd, SANS_SB, "c")
        p.text(xs[4] + 54, y + 6, note, 6.5, D.muted, SANS, "l")
    p.text(16, y0 - 4 * 34 + 8,
           "one pass, O(1) space, and the length is never needed",
           7.0, D.ok_bd, SANS_SB, "l")


@fig("pat_floyd")
def pat_floyd(p):
    """Phase 1 and phase 2."""
    import math
    cx, cy, r = 250, p.h / 2 - 4, 44
    tail = [(70, cy), (118, cy), (166, cy)]
    for i, (px, py) in enumerate(tail):
        p.circle(px, py, 11, str(i + 1), "dim", size=7.4)
        nxt = tail[i + 1] if i + 1 < len(tail) else (cx - r, cy)
        p.arrow(px, py, nxt[0], nxt[1], D.arrow, 0.9, head=3, shrink=13)
    pos = []
    for i in range(5):
        a = math.pi - i * 2 * math.pi / 5
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(5):
        a, b = pos[i], pos[(i + 1) % 5]
        p.arrow(a[0], a[1], b[0], b[1], D.teal_bd, 0.9, head=3, shrink=13)
    for i, (px, py) in enumerate(pos):
        k = "ok" if i == 0 else ("hi" if i == 2 else "teal")
        p.circle(px, py, 11, str(i + 4), k, size=7.4)
    p.text(pos[0][0] - 24, pos[0][1] + 18, "entrance", 6.8, D.ok_bd,
           SANS_SB, "c")
    p.text(pos[2][0] + 6, pos[2][1] - 24, "they meet here", 6.8, D.hi_bd,
           SANS_SB, "c")
    p.text(10, p.h - 14, "PHASE 1: fast gains one node per step, so inside "
           "the cycle it must catch slow", 6.9, D.hi_bd, SANS_SB, "l")
    p.text(10, 8, "PHASE 2: restart one pointer at the head; both now move ONE "
           "step, and they meet at the entrance", 6.9, D.ok_bd, SANS_SB, "l")


@fig("pat_floyd_proof")
def pat_floyd_proof(p):
    """F = nL - a."""
    import math
    cx, cy, r = 268, p.h / 2, 42
    p.circle(70, cy, 10, "H", "dim", size=7.4)
    p.arrow(80, cy, cx - r - 2, cy, D.arrow, 1.0, head=3.4)
    p.brace(84, cx - r - 4, cy + 14, "F  —  head to entrance", up=True)
    for i in range(16):
        a0 = math.pi - i * 2 * math.pi / 16
        a1 = math.pi - (i + 1) * 2 * math.pi / 16
        p.line(cx + r * math.cos(a0), cy + r * math.sin(a0),
               cx + r * math.cos(a1), cy + r * math.sin(a1), D.teal_bd, 1.0)
    ent = (cx - r, cy)
    met = (cx + r * math.cos(math.pi - 5 * 2 * math.pi / 16),
           cy + r * math.sin(math.pi - 5 * 2 * math.pi / 16))
    p.circle(ent[0], ent[1], 9, None, "ok")
    p.circle(met[0], met[1], 9, None, "hi")
    p.text(ent[0] - 16, ent[1] + 14, "entrance", 6.6, D.ok_bd, SANS_SB, "c")
    p.text(met[0] + 4, met[1] - 20, "meeting point", 6.6, D.hi_bd, SANS_SB, "c")
    p.text(cx + 4, cy + 6, "a", 8.0, D.hi_bd, SERIF_I, "c")
    p.text(cx + 4, cy - 6, "L = cycle length", 6.4, D.muted, SANS_I, "c")
    lines = ["slow has walked   F + a",
             "fast has walked   F + a + nL",
             "fast walked twice as far:",
             "   2(F + a) = F + a + nL",
             "   F = nL − a"]
    for i, ln in enumerate(lines):
        p.text(10, p.h - 20 - i * 13, ln, 7.2,
               D.ok_bd if i == 4 else D.ink, MONO if i != 2 else SANS_I, "l")
    p.text(10, 6, "F steps from the meeting point = n whole laps minus a  →  "
           "lands exactly on the entrance", 6.9, D.ok_bd, SANS_SB, "l")


@fig("pat_merge")
def pat_merge(p):
    """Take the smaller front, relink."""
    y = p.h - 34
    chain(p, 92, y, [1, 3, 5], w=42, h=20, gap=22, size=8,
          kinds=["hi", "dim", "dim"])
    p.text(84, y + 6, "a", 8.0, D.ink, MONO_B, "r")
    y2 = y - 40
    chain(p, 92, y2, [2, 4, 6], w=42, h=20, gap=22, size=8,
          kinds=["dim"] * 3)
    p.text(84, y2 + 6, "b", 8.0, D.ink, MONO_B, "r")
    y3 = y2 - 48
    node(p, 92, y3, "—", kind="teal", w=42, h=20, size=8)
    p.arrow(92 + 42 * 0.78, y3 + 10, 92 + 64 - 2, y3 + 10, D.arrow, 0.9,
            head=3.2)
    chain(p, 92 + 64, y3, [1, 2], w=42, h=20, gap=22, size=8,
          kinds=["ok", "ok"], end="open")
    p.text(84, y3 + 6, "out", 8.0, D.ok_bd, MONO_B, "r")
    p.text(92 + 21, y3 + 26, "dummy", 6.4, D.teal_bd, SANS_SB, "c")
    p.text(16, y3 - 20, "no new nodes — the next pointers of the existing nodes are rewired",
           7.0, D.ok_bd, SANS_SB, "l")
    p.text(16, y3 - 32, "tail->next = a ? a : b   attaches the whole remainder in one line",
           6.8, D.muted, MONO, "l")


@fig("ll_remove_cycle")
def ll_remove_cycle(p):
    """You need the node before the entrance."""
    import math
    cx, cy, r = 250, p.h / 2 - 2, 42
    p.circle(76, cy, 11, "1", "dim", size=7.4)
    p.arrow(87, cy, cx - r - 2, cy, D.arrow, 0.9, head=3.2)
    pos = []
    for i in range(4):
        a = math.pi - i * 2 * math.pi / 4
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(4):
        a, b = pos[i], pos[(i + 1) % 4]
        col = D.bad_bd if i == 3 else D.teal_bd
        p.arrow(a[0], a[1], b[0], b[1], col, 1.0, head=3.2, shrink=13)
    for i, (px, py) in enumerate(pos):
        k = "ok" if i == 0 else ("bad" if i == 3 else "teal")
        p.circle(px, py, 11, str(i + 2), k, size=7.4)
    p.text(pos[0][0] - 20, pos[0][1] + 16, "entrance", 6.7, D.ok_bd,
           SANS_SB, "c")
    p.text(pos[3][0] + 6, pos[3][1] - 20, "the LAST node of the loop", 6.7,
           D.bad_bd, SANS_SB, "c")
    p.text(pos[3][0] + 6, pos[3][1] - 29, "— set its next to nullptr", 6.7,
           D.bad_bd, SANS_SB, "c")
    p.text(10, 8, "finding the entrance is not enough; walk round to the node "
           "that points at it", 7.0, D.ink, SANS_SB, "l")


@fig("ll_remove_nth")
def ll_remove_nth(p):
    """Gap of n+1 from the dummy."""
    y = p.h - 48
    node(p, 56, y, "—", kind="teal", w=38, h=20, size=7.6)
    p.arrow(56 + 38 * 0.78, y + 10, 56 + 58 - 2, y + 10, D.arrow, 0.9, head=3)
    xs = chain(p, 56 + 58, y, [1, 2, 3, 4, 5], w=38, h=20, gap=20, size=7.8,
               kinds=["dim", "dim", "ok", "bad", "dim"])
    p.text(56 + 19, y + 24, "dummy", 6.4, D.teal_bd, SANS_SB, "c")
    p.pointer(xs[2] + 10, y + 20, "trail")
    p.text(xs[3] + 10, y - 11, "to delete", 6.2, D.bad_bd, SANS_SB, "c")
    p.text(xs[4] + 56, y + 6, "lead has run off", 6.6, D.hi_bd, SANS, "l")
    p.text(16, y - 30, "n = 2, so the gap is n + 1 = 3 — which leaves trail on the PREDECESSOR",
           6.9, D.ok_bd, SANS_SB, "l")
    p.text(16, y - 42, "starting trail at the dummy means even deleting the head needs no branch",
           6.8, D.muted, SANS_I, "l")


@fig("ll_palindrome")
def ll_palindrome(p):
    """Middle, reverse, compare."""
    y0 = p.h - 34
    p.text(0, y0 + 6, "1. split", 7.0, D.muted, SANS_SB, "l")
    chain(p, 76, y0, [1, 2], w=36, h=19, gap=18, size=7.6, kinds=["ok"] * 2)
    chain(p, 76 + 2 * 54 + 16, y0, [2, 1], w=36, h=19, gap=18, size=7.6,
          kinds=["hi"] * 2)
    y1 = y0 - 40
    p.text(0, y1 + 6, "2. reverse", 7.0, D.muted, SANS_SB, "l")
    chain(p, 76, y1, [1, 2], w=36, h=19, gap=18, size=7.6, kinds=["ok"] * 2)
    chain(p, 76 + 2 * 54 + 16, y1, [1, 2], w=36, h=19, gap=18, size=7.6,
          kinds=["hi"] * 2)
    y2 = y1 - 44
    p.text(0, y2 + 6, "3. compare", 7.0, D.ok_bd, SANS_SB, "l")
    xs = chain(p, 76, y2, [1, 2], w=36, h=19, gap=18, size=7.6,
               kinds=["ok"] * 2)
    xs2 = chain(p, 76 + 2 * 54 + 16, y2, [1, 2], w=36, h=19, gap=18, size=7.6,
                kinds=["hi"] * 2)
    for a, b in zip(xs, xs2):
        p.curve(a + 18, y2 + 19, b + 18, y2 + 19, bulge=12, color=D.ok_bd,
                lw=0.8, arrow=False)
    p.text(0, y2 - 22, "4. reverse the second half again — "
           "leave the list exactly as you found it", 7.0, D.ink, SANS_SB, "l")
    p.text(0, y2 - 34, "nothing new is needed: find-middle and reverse are "
           "both functions you already have", 6.8, D.muted, SANS_I, "l")


@fig("ll_intersection")
def ll_intersection(p):
    """Each pointer walks a + b + c."""
    y = p.h - 46
    p.text(0, y + 24, "A", 8.0, D.ink, MONO_B, "l")
    xs = chain(p, 40, y, [1, 2], w=38, h=20, gap=18, size=7.8,
               kinds=["dim"] * 2, end=None)
    y2 = y - 48
    p.text(0, y2 + 6, "B", 8.0, D.ink, MONO_B, "l")
    xb = chain(p, 40, y2, [5], w=38, h=20, gap=18, size=7.8, kinds=["dim"],
               end=None)
    sx = 196
    xs3 = chain(p, sx, y - 24, [8, 10], w=38, h=20, gap=18, size=7.8,
                kinds=["ok"] * 2)
    p.arrow(xs[1] + 38 * 0.78, y + 10, sx - 2, y - 24 + 14, D.arrow, 0.9,
            head=3)
    p.arrow(xb[0] + 38 * 0.78, y2 + 10, sx - 2, y - 24 + 6, D.arrow, 0.9,
            head=3)
    p.brace(40, 40 + 2 * 56, y + 22, "a = 2", up=True)
    p.brace(40, 40 + 56, y2 - 4, "b = 1", up=False)
    p.brace(sx, sx + 2 * 56, y - 24 - 4, "c = 2 (shared)", up=False)
    p.box(16, 8, p.w - 32, 32, None, "ok", radius=3)
    p.text(30, 27, "pa walks  a + c  then  b     =  a + b + c", 7.6, D.ink,
           MONO, "l")
    p.text(30, 16, "pb walks  b + c  then  a     =  a + b + c   →  "
           "they arrive together", 7.6, D.ink, MONO, "l")


@fig("ll_add_numbers")
def ll_add_numbers(p):
    """Digit by digit, with the carry."""
    cw = 48
    x0 = 110
    y = p.h - 36
    chain(p, x0, y, [2, 4, 3], w=42, h=20, gap=22, size=8, kinds=["dim"] * 3)
    p.text(x0 - 8, y + 6, "342", 7.4, D.muted, MONO, "r")
    y2 = y - 34
    chain(p, x0, y2, [5, 6, 4], w=42, h=20, gap=22, size=8, kinds=["dim"] * 3)
    p.text(x0 - 8, y2 + 6, "465", 7.4, D.muted, MONO, "r")
    y3 = y2 - 44
    chain(p, x0, y3, [7, 0, 8], w=42, h=20, gap=22, size=8, kinds=["ok"] * 3)
    p.text(x0 - 8, y3 + 6, "807", 7.4, D.ok_bd, MONO, "r")
    sums = ["2+5=7", "4+6=10", "3+4+1=8"]
    carries = ["carry 0", "carry 1", "carry 0"]
    for i in range(3):
        cx = x0 + i * 64 + 21
        p.text(cx, y3 - 13, sums[i], 6.4, D.muted, MONO, "c")
        p.text(cx, y3 - 23, carries[i], 6.2, D.hi_bd, SANS_I, "c")
    p.text(16, y3 - 42, "least significant digit first — which is exactly the "
           "order you add in", 7.0, D.ink, SANS_SB, "l")
    p.text(16, y3 - 54, "the loop runs while EITHER list has digits OR a carry "
           "remains: 999 + 1 needs that last round", 6.8, D.muted, SANS_I, "l")


@fig("ll_delete_node")
def ll_delete_node(p):
    """Steal the next node's value."""
    y = p.h - 48
    xs = chain(p, 76, y, [1, 2, 3, 4], w=46, h=22, gap=24, size=8.4,
               kinds=["dim", "bad", "hi", "dim"])
    p.pointer(xs[1] + 13, y + 22, "node — all you are given")
    p.text(xs[2] + 13, y - 12, "its value is stolen", 6.3, D.hi_bd,
           SANS_SB, "c")
    y2 = y - 58
    chain(p, 76, y2, [1, 3, 4], w=46, h=22, gap=24, size=8.4,
          kinds=["dim", "ok", "dim"])
    p.text(16, y2 - 20, "the node you were given survives — but holding 3, so "
           "the list reads as if it had gone", 6.9, D.ok_bd, SANS_SB, "l")
    p.text(16, y2 - 32, "it cannot delete the LAST node, and it dangles anyone "
           "else's pointer to the next one", 6.8, D.bad_bd, SANS_SB, "l")


@fig("ll_reorder")
def ll_reorder(p):
    """Split, reverse, interleave."""
    y0 = p.h - 32
    p.text(0, y0 + 6, "1. split", 7.0, D.muted, SANS_SB, "l")
    chain(p, 76, y0, [1, 2], w=34, h=18, gap=16, size=7.4, kinds=["ok"] * 2)
    chain(p, 76 + 2 * 50 + 14, y0, [3, 4], w=34, h=18, gap=16, size=7.4,
          kinds=["hi"] * 2)
    y1 = y0 - 36
    p.text(0, y1 + 6, "2. reverse", 7.0, D.muted, SANS_SB, "l")
    chain(p, 76, y1, [1, 2], w=34, h=18, gap=16, size=7.4, kinds=["ok"] * 2)
    chain(p, 76 + 2 * 50 + 14, y1, [4, 3], w=34, h=18, gap=16, size=7.4,
          kinds=["hi"] * 2)
    y2 = y1 - 40
    p.text(0, y2 + 6, "3. interleave", 7.0, D.ok_bd, SANS_SB, "l")
    chain(p, 76, y2, [1, 4, 2, 3], w=34, h=18, gap=16, size=7.4,
          kinds=["ok", "hi", "ok", "hi"])
    p.text(0, y2 - 22, "three steps, each one a function from an earlier chapter",
           7.0, D.ink, SANS_SB, "l")
    p.text(0, y2 - 34, "split at the FIRST middle, so the first half is never "
           "the shorter one", 6.8, D.muted, SANS_I, "l")


@fig("lla_k_group")
def lla_k_group(p):
    """Reverse within groups; leave a short tail."""
    y = p.h - 38
    xs = chain(p, 64, y, [1, 2, 3, 4, 5, 6, 7], w=36, h=20, gap=16, size=7.8,
               kinds=["ok"] * 3 + ["hi"] * 3 + ["dim"])
    p.brace(xs[0], xs[2] + 36, y + 21, "group 1", up=True)
    p.brace(xs[3], xs[5] + 36, y + 21, "group 2", up=True)
    p.brace(xs[6], xs[6] + 36, y + 21, "only 1 left", up=True)
    y2 = y - 52
    chain(p, 64, y2, [3, 2, 1, 6, 5, 4, 7], w=36, h=20, gap=16, size=7.8,
          kinds=["ok"] * 3 + ["hi"] * 3 + ["dim"])
    p.text(16, y2 - 20, "count k nodes BEFORE reversing — afterwards the count "
           "is unrecoverable", 7.0, D.bad_bd, SANS_SB, "l")
    p.text(16, y2 - 32, "each group's old head becomes its tail, and must be "
           "stitched onto whatever follows", 6.8, D.muted, SANS_I, "l")


@fig("lla_rotate")
def lla_rotate(p):
    """Close the ring, then cut elsewhere."""
    import math
    cx, cy, r = 112, p.h / 2 - 4, 44
    vals = [1, 2, 3, 4, 5]
    pos = []
    for i, v in enumerate(vals):
        a = math.pi / 2 - i * 2 * math.pi / 5
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(5):
        a, b = pos[i], pos[(i + 1) % 5]
        col = D.bad_bd if i == 2 else D.teal_bd
        p.arrow(a[0], a[1], b[0], b[1], col, 1.0, head=3.2, shrink=13)
    for (px, py), v in zip(pos, vals):
        p.circle(px, py, 12, str(v), "teal" if v != 3 else "bad", size=8)
    mx = (pos[2][0] + pos[3][0]) / 2
    my = (pos[2][1] + pos[3][1]) / 2
    p.line(mx - 7, my - 7, mx + 7, my + 7, D.bad_bd, 1.4)
    # push the label radially outward so it never lands on a node
    ux, uy = (mx - cx), (my - cy)
    nrm = (ux * ux + uy * uy) ** 0.5 or 1.0
    p.text(mx + ux / nrm * 26, my + uy / nrm * 26 - 3, "cut here", 6.8,
           D.bad_bd, SANS_SB, "c")
    steps = ["1. walk to the tail, counting n",
             "2. tail->next = head   (close the ring)",
             "3. k %= n",
             "4. walk n − k − 1 steps to the new tail",
             "5. newHead = newTail->next; newTail->next = nullptr"]
    for i, s in enumerate(steps):
        p.text(210, p.h - 24 - i * 15, s, 7.0, D.ink, MONO if i else MONO, "l")
    p.text(210, p.h - 24 - 5 * 15 - 6,
           "once it is a circle, rotating is just choosing where to cut",
           6.8, D.ok_bd, SANS_SB, "l")


@fig("lla_sort")
def lla_sort(p):
    """Merge sort on a list."""
    levels = [[[4, 2, 1, 3]], [[4, 2], [1, 3]], [[4], [2], [1], [3]],
              [[2, 4], [1, 3]], [[1, 2, 3, 4]]]
    labels = ["split", "split", "", "merge", "merge"]
    y0 = p.h - 24
    cw = 22
    for li, groups in enumerate(levels):
        y = y0 - li * 28
        total = sum(len(g) for g in groups) * cw + (len(groups) - 1) * 18
        x = (p.w - total) / 2 + 30
        for g in groups:
            kinds = ["ok" if li >= 3 else "dim"] * len(g)
            p.cells(x, y, g, cw=cw, ch=17, kinds=kinds, index=False, size=7.4)
            x += len(g) * cw + 18
        if labels[li]:
            p.text(36, y + 4, labels[li], 6.6, D.muted, SANS_SB, "r")
    p.text(16, y0 - 5 * 28 + 2,
           "splitting is fast-and-slow; merging is relinking — neither needs random access",
           7.0, D.ink, SANS_SB, "l")
    p.text(16, y0 - 5 * 28 - 10,
           "on an ARRAY, merge sort needs an O(n) buffer. On a list it needs none.",
           6.9, D.ok_bd, SANS_SB, "l")


@fig("lla_random_copy")
def lla_random_copy(p):
    """Interleaving replaces the hash map."""
    y = p.h - 42
    p.text(0, y + 24, "1. weave each copy in after its original", 7.0,
           D.muted, SANS_SB, "l")
    vals = ["A", "A'", "B", "B'", "C", "C'"]
    kinds = ["dim", "ok", "dim", "ok", "dim", "ok"]
    xs = chain(p, 46, y, vals, w=34, h=20, gap=14, size=7.6, kinds=kinds)
    y2 = y - 52
    p.text(0, y2 + 26, "2. every random becomes one arrow lookup", 7.0,
           D.ok_bd, SANS_SB, "l")
    p.box(16, y2 - 4, p.w - 32, 26, None, "ok", radius=3)
    p.text(30, y2 + 12, "X->next->random  =  X->random->next", 8.4, D.ink,
           MONO_B, "l")
    p.text(30, y2 + 1, "the copy of X is X->next, and the copy of X's target "
           "is that target's ->next", 6.6, D.muted, SANS_I, "l")
    p.text(0, y2 - 24, "3. unweave: restore the originals' next pointers and "
           "chain the copies together", 7.0, D.muted, SANS_SB, "l")
    p.text(0, y2 - 38, "the interleaving IS the map — O(1) space instead of a "
           "hash table", 7.0, D.ok_bd, SANS_SB, "l")
