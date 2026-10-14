"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


@fig("pf_map")
def pf_map(p):
    """Eleven problems, four patterns."""
    groups = [
        ("LINEAR TRAVERSAL", "teal",
         ["largest", "second largest", "is sorted", "max consecutive ones"]),
        ("TWO POINTERS", "hi",
         ["reverse", "union of sorted"]),
        ("WRITE POINTER", "ok",
         ["remove duplicates", "move zeroes", "rotate by k"]),
        ("ARITHMETIC IDENTITY", "violet",
         ["missing number", "single number"]),
    ]
    x = 8
    for title, kind, items in groups:
        w = 96
        p.box(x, p.h - 30, w, 20, None, kind, radius=3)
        p.text(x + w / 2, p.h - 24, title, 6.4, D.ink, SANS_SB, "c")
        for i, it in enumerate(items):
            p.box(x + 6, p.h - 56 - i * 22, w - 12, 17, it, "white", size=6.6,
                  radius=2, lw=0.5)
        x += w + 7
    p.text(8, 10, "four of the ten patterns cover every foundational problem — "
           "which is why the patterns came first", 7.0, D.ink, SANS_SB, "l")


@fig("pf_missing")
def pf_missing(p):
    """Sum and XOR, side by side."""
    cw = 34
    x0 = 80
    y = p.h - 40
    p.text(x0 - 72, y + 24, "SUM", 7.6, D.hi_bd, SANS_SB, "l")
    p.cells(x0, y, [0, 1, 2, 3], cw=cw, ch=20, kinds=["dim"] * 4, index=False,
            size=8)
    p.text(x0 + 4 * cw + 10, y + 6, "should be 0+1+2+3 = 6", 6.9, D.muted,
           SANS, "l")
    y2 = y - 26
    p.cells(x0, y2, [3, 0, 1, ""], cw=cw, ch=20,
            kinds=["hi", "hi", "hi", "bad"], index=False, size=8)
    p.text(x0 + 4 * cw + 10, y2 + 6, "actually 3+0+1 = 4", 6.9, D.muted,
           SANS, "l")
    p.text(x0, y2 - 14, "6 − 4 = 2    (watch for overflow)", 7.4, D.hi_bd,
           MONO_B, "l")

    y3 = y2 - 48
    p.text(x0 - 72, y3 + 24, "XOR", 7.6, D.ok_bd, SANS_SB, "l")
    p.text(x0, y3 + 14, "0 ⊕ 1 ⊕ 2 ⊕ 3    ⊕    3 ⊕ 0 ⊕ 1", 8.2, D.ink,
           MONO, "l")
    p.text(x0, y3 + 2, "   ↑ the indices          ↑ the values", 6.4, D.faint,
           MONO, "l")
    p.text(x0, y3 - 14, "every value present twice cancels  →  only 2 survives",
           7.2, D.ok_bd, SANS_SB, "l")
    p.text(x0, y3 - 25, "cannot overflow, which makes it the safer answer",
           6.8, D.muted, SANS_I, "l")


@fig("pf_xor")
def pf_xor(p):
    """Pairs cancel because XOR is commutative."""
    cw = 40
    x0 = 96
    y = p.h - 38
    p.cells(x0, y, [4, 1, 2, 1, 2], cw=cw, ch=22,
            kinds=["ok", "hi", "teal", "hi", "teal"], index=False, size=8.6)
    p.text(x0 - 8, y + 7, "as given", 6.8, D.muted, SANS_SB, "r")
    y2 = y - 40
    p.cells(x0, y2, [1, 1, 2, 2, 4], cw=cw, ch=22,
            kinds=["hi", "hi", "teal", "teal", "ok"], index=False, size=8.6)
    p.text(x0 - 8, y2 + 7, "regrouped", 6.8, D.muted, SANS_SB, "r")
    p.brace(x0, x0 + 2 * cw, y2 - 4, "= 0", up=False)
    p.brace(x0 + 2 * cw, x0 + 4 * cw, y2 - 4, "= 0", up=False)
    p.arrow(x0 + 4 * cw + cw / 2, y2 - 6, x0 + 4 * cw + cw / 2, y2 - 20,
            D.ok_bd, 1.0, head=3.2)
    p.text(x0 + 4 * cw + cw / 2, y2 - 30, "survives", 7.0, D.ok_bd, SANS_SB, "c")
    p.text(x0 - 40, y2 - 46,
           "regrouping is allowed because XOR is commutative and associative",
           7.0, D.ink, SANS_SB, "l")
    p.text(x0 - 40, y2 - 57,
           "x ⊕ x = 0   and   x ⊕ 0 = x   —  those two facts are the whole trick",
           6.8, D.muted, MONO, "l")


@fig("pi_boyer_moore")
def pi_boyer_moore(p):
    """Votes cancelling."""
    cw = 36
    x0 = 70
    vals = [2, 2, 1, 1, 1, 2, 2]
    cand = [2, 2, 2, 2, 1, 1, 2]
    cnt = [1, 2, 1, 0, 1, 0, 1]
    y = p.h - 40
    p.cells(x0, y, vals, cw=cw, ch=21, index=False, size=8.2,
            kinds=["hi" if v == 2 else "teal" for v in vals])
    for i in range(7):
        p.text(x0 + i * cw + cw / 2, y - 13, str(cand[i]), 7.4, D.muted,
               MONO, "c")
        p.text(x0 + i * cw + cw / 2, y - 26, str(cnt[i]), 7.4,
               D.bad_bd if cnt[i] == 0 else D.ink, MONO_B, "c")
    p.text(x0 - 8, y + 6, "value", 6.8, D.muted, SANS_SB, "r")
    p.text(x0 - 8, y - 13, "candidate", 6.8, D.muted, SANS_SB, "r")
    p.text(x0 - 8, y - 26, "count", 6.8, D.muted, SANS_SB, "r")
    p.text(x0, y - 44,
           "count 0 means every vote so far has been cancelled — adopt the next element",
           6.9, D.bad_bd, SANS_SB, "l")
    p.text(x0, y - 56,
           "the majority has more than half the votes, so it cannot be cancelled away",
           6.9, D.ok_bd, SANS_SB, "l")


@fig("pi_dutch_flag")
def pi_dutch_flag(p):
    """Four regions, three boundaries."""
    cw = 42
    x0 = 66
    y = p.h - 48
    vals = [0, 0, 1, 1, 2, 0, 1, 2]
    regions = ["ok", "ok", "hi", "hi", "dim", "dim", "violet", "violet"]
    p.cells(x0, y, ["0", "0", "1", "1", "?", "?", "2", "2"], cw=cw, ch=24,
            kinds=regions, index=False, size=8.6)
    p.brace(x0, x0 + 2 * cw, y + 26, "all 0s", up=True)
    p.brace(x0 + 2 * cw, x0 + 4 * cw, y + 26, "all 1s", up=True)
    p.brace(x0 + 4 * cw, x0 + 6 * cw, y + 26, "unexamined", up=True)
    p.brace(x0 + 6 * cw, x0 + 8 * cw, y + 26, "all 2s", up=True)
    p.pointer(x0 + 2 * cw + cw / 2, y - 40, "low")
    p.pointer(x0 + 4 * cw + cw / 2, y - 40, "mid")
    p.pointer(x0 + 5 * cw + cw / 2, y - 40, "high")
    p.text(x0 - 56, y - 62,
           "swap with low → the incoming element is a known 1, so mid may advance",
           6.9, D.ok_bd, SANS_SB, "l")
    p.text(x0 - 56, y - 73,
           "swap with high → the incoming element is unexamined, so mid must NOT advance",
           6.9, D.bad_bd, SANS_SB, "l")


@fig("pi_merge_back")
def pi_merge_back(p):
    """Fill from the back, into the empty slots."""
    cw = 36
    x0 = 76
    y = p.h - 36
    p.cells(x0, y, [1, 2, 3, "", "", ""], cw=cw, ch=20,
            kinds=["ok"] * 3 + ["dim"] * 3, index=False, size=8)
    p.text(x0 - 8, y + 6, "a", 8.0, D.ink, MONO_B, "r")
    p.brace(x0 + 3 * cw, x0 + 6 * cw, y + 21, "spare slots — already empty",
            up=True)
    y2 = y - 40
    p.cells(x0, y2, [2, 5, 6], cw=cw, ch=20, kinds=["teal"] * 3, index=False,
            size=8)
    p.text(x0 - 8, y2 + 6, "b", 8.0, D.ink, MONO_B, "r")
    y3 = y2 - 40
    p.cells(x0, y3, [1, 2, 3, "", "", 6], cw=cw, ch=20,
            kinds=["ok"] * 3 + ["dim"] * 2 + ["teal"], index=False, size=8)
    p.pointer(x0 + 5 * cw + cw / 2, y3 + 20, "w")
    p.text(x0 + 6 * cw + 10, y3 + 6, "the LARGEST remaining", 6.8, D.muted,
           SANS, "l")
    p.text(x0 + 6 * cw + 10, y3 - 4, "goes into the last slot", 6.8, D.muted,
           SANS, "l")
    p.text(x0 - 40, y3 - 22,
           "filling forwards would overwrite elements of a that have not been placed yet",
           6.9, D.bad_bd, SANS_SB, "l")


@fig("pi_duplicate_cycle")
def pi_duplicate_cycle(p):
    """The array as a functional graph."""
    import math
    cw = 40
    x0 = 70
    y = p.h - 34
    vals = [1, 3, 4, 2, 2]
    p.cells(x0, y, vals, cw=cw, ch=20, kinds=["dim", "dim", "hi", "dim", "hi"],
            index=True, size=8)
    p.text(x0 - 8, y + 6, "v", 8.0, D.ink, MONO_B, "r")
    p.text(x0 + 5 * cw + 10, y + 6, "read v[i] as \"next index\"", 6.8,
           D.muted, SANS_I, "l")

    cx, cy, r = 150, 46, 30
    nodes = [0, 1, 3, 2, 4]
    pos = {}
    for i, idx in enumerate(nodes):
        a = math.pi / 2 - i * 2 * math.pi / 5
        pos[idx] = (cx + r * math.cos(a), cy + r * math.sin(a))
    edges = [(0, 1), (1, 3), (3, 2), (2, 4), (4, 2)]
    for a, b in edges:
        if a == b:
            continue
        p.arrow(pos[a][0], pos[a][1], pos[b][0], pos[b][1], D.arrow, 0.85,
                head=3.0, shrink=11)
    for idx, (px, py) in pos.items():
        p.circle(px, py, 9.5, str(idx), "ok" if idx == 2 else "dim", size=7.4)
    p.text(cx + r + 26, cy + 6, "index 2 is entered from", 6.8, D.ok_bd,
           SANS_SB, "l")
    p.text(cx + r + 26, cy - 4, "two places — because the", 6.8, D.muted,
           SANS, "l")
    p.text(cx + r + 26, cy - 14, "value 2 appears twice", 6.8, D.muted,
           SANS, "l")
    p.text(cx + r + 26, cy - 28, "so the duplicate is the", 6.8, D.ok_bd,
           SANS_SB, "l")
    p.text(cx + r + 26, cy - 38, "entrance to the cycle", 6.8, D.ok_bd,
           SANS_SB, "l")


@fig("pi_product_except")
def pi_product_except(p):
    """Prefix times suffix."""
    cw = 54
    x0 = 92
    y = p.h - 40
    p.cells(x0, y, [1, 2, 3, 4], cw=cw, ch=22, index=True, size=8.6,
            kinds=["dim", "dim", "hi", "dim"])
    p.text(x0 - 8, y + 7, "v", 8.0, D.ink, MONO_B, "r")
    p.brace(x0, x0 + 2 * cw, y + 25, "left of index 2:  1 × 2 = 2", up=True)
    p.brace(x0 + 3 * cw, x0 + 4 * cw, y + 25, "right:  4", up=True)
    y2 = y - 40
    p.cells(x0, y2, [24, 12, 8, 6], cw=cw, ch=22, index=False, size=8.6,
            kinds=["ok", "ok", "hi", "ok"])
    p.text(x0 - 8, y2 + 7, "out", 8.0, D.ok_bd, MONO_B, "r")
    p.arrow(x0 + 2 * cw + cw / 2, y - 6, x0 + 2 * cw + cw / 2, y2 + 24,
            D.hi_bd, 1.0, head=3.2)
    p.text(x0 + 2 * cw + cw / 2 + 8, y - 22, "2 × 4 = 8", 7.4, D.hi_bd,
           MONO_B, "l")
    p.text(x0 - 60, y2 - 20,
           "no division — so a zero anywhere needs no special case at all",
           7.0, D.ink, SANS_SB, "l")


@fig("pa_rotated")
def pa_rotated(p):
    """One half is always properly sorted."""
    cw = 42
    x0 = 68
    vals = [4, 5, 6, 7, 0, 1, 2]
    y = p.h - 40
    p.cells(x0, y, vals, cw=cw, ch=22, index=True, size=8.6,
            kinds=["ok", "ok", "ok", "hi", "bad", "bad", "bad"])
    p.pointer(x0 + 3 * cw + cw / 2, y + 22, "mid")
    p.brace(x0, x0 + 4 * cw, y - 22, "4 5 6 7 — properly sorted", up=False)
    p.brace(x0 + 4 * cw, x0 + 7 * cw, y - 22, "contains the rotation point",
            up=False)
    p.box(26, 16, p.w - 52, 42, None, "ok", radius=3)
    p.text(40, 44, "v[lo] <= v[mid]   →   the LEFT half is sorted", 8.0,
           D.ink, MONO, "l")
    p.text(40, 32, "then: is v[lo] <= target < v[mid] ?", 7.6, D.muted,
           MONO, "l")
    p.text(40, 21, "yes → search the sorted half · no → it can only be in the other one",
           6.8, D.muted, SANS_I, "l")


@fig("pa_rain_water")
def pa_rain_water(p):
    """Water above each column."""
    h = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
    n = len(h)
    cw, unit = 29, 17
    x0, y0 = 46, 44
    maxl, maxr = [], []
    m = 0
    for x in h:
        m = max(m, x)
        maxl.append(m)
    m = 0
    for x in reversed(h):
        m = max(m, x)
        maxr.append(m)
    maxr.reverse()
    for i in range(n):
        level = min(maxl[i], maxr[i])
        if level > h[i]:
            p.box(x0 + i * cw, y0 + h[i] * unit, cw - 1.5,
                  (level - h[i]) * unit, None, "teal", radius=0, lw=0.4)
        if h[i]:
            p.box(x0 + i * cw, y0, cw - 1.5, h[i] * unit, None, "ink",
                  radius=0, lw=0.4)
        p.text(x0 + i * cw + cw / 2, y0 - 11, str(h[i]), 6.4, D.faint,
               MONO, "c")
    p.text(x0, y0 - 24, "bar heights", 6.6, D.muted, SANS_I, "l")
    p.text(x0 + n * cw + 8, y0 + 3 * unit, "6 units", 8.4, D.teal_bd,
           SANS_SB, "l")
    p.text(x0 + n * cw + 8, y0 + 3 * unit - 11, "of water", 7.0, D.muted,
           SANS, "l")
    p.box(26, p.h - 30, p.w - 52, 24, None, "hi", radius=3)
    p.text(40, p.h - 22, "water[i]  =  max(0,  min(maxLeft[i], maxRight[i])  −  h[i])",
           8.2, D.ink, MONO_B, "l")
