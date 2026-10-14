"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


# ---------------------------------------------------------------- traversal
@fig("trav_running_state")
def trav_running_state(p):
    """A notebook travelling beside the loop."""
    cw = 32
    x0, y = 30, p.h - 56
    vals = [3, 9, 2, 9, 1, 7, 4]
    kinds = ["ok", "ok", "ok", "hi"] + ["dim"] * 3
    p.cells(x0, y, vals, cw=cw, ch=22, kinds=kinds, index=False, size=8.2)
    p.pointer(x0 + 3 * cw + cw / 2, y + 22, "i")
    p.brace(x0, x0 + 3 * cw, y - 5, "already seen", up=False)
    p.brace(x0 + 4 * cw, x0 + 7 * cw, y - 5, "not yet read", up=False)
    bx = x0 + 7 * cw + 26
    p.box(bx, y - 14, 112, 50, None, "teal", radius=3)
    p.text(bx + 56, y + 27, "THE NOTEBOOK", 6.8, D.teal_bd, SANS_SB, "c")
    p.text(bx + 10, y + 16, "best   = 9", 8.0, D.ink, MONO, "l")
    p.text(bx + 10, y + 4, "count  = 4", 8.0, D.ink, MONO, "l")
    p.text(bx + 10, y - 8, "sum    = 23", 8.0, D.ink, MONO, "l")
    p.text(x0, y - 36, "the loop may never look back — so everything it still needs must be in the notebook",
           7.0, D.ink, SANS_SB, "l")


@fig("trav_second_largest")
def trav_second_largest(p):
    """Three cases, and the demote-before-promote rule."""
    W, H = 118, 30
    y = p.h - 40
    cases = [
        ("x > best", "teal", ["second = best", "best   = x"], "demote, THEN promote"),
        ("second < x < best", "hi", ["second = x"], "only second changes"),
        ("x == best", "dim", ["(nothing)"], "a duplicate is not a runner-up"),
    ]
    for i, (title, kind, lines, note) in enumerate(cases):
        x = 8 + i * 134
        p.box(x, y, W, H, None, kind, radius=3)
        p.text(x + W / 2, y + H / 2 - 3, title, 8.0, D.ink, MONO_B, "c")
        for j, ln in enumerate(lines):
            p.text(x + 6, y - 14 - j * 11, ln, 7.4, D.ink, MONO, "l")
        p.text(x + 6, y - 14 - len(lines) * 11 - 4, note, 6.5, D.muted,
               SANS_I, "l")
    p.box(8, 8, p.w - 16, 26, None, "bad", radius=3)
    p.text(20, 18, "best = x;  second = best;    ✗   both end up equal to x",
           7.8, D.bad_bd, MONO, "l")
    p.text(20, 8, "second = best;  best = x;    ✓   the old champion survives",
           7.8, D.ok_bd, MONO, "l")


@fig("trav_consecutive")
def trav_consecutive(p):
    """current resets, best does not."""
    cw = 40
    x0, y = 62, p.h - 46
    vals = [1, 1, 0, 1, 1, 1]
    cur = [1, 2, 0, 1, 2, 3]
    best = [1, 2, 2, 2, 2, 3]
    p.cells(x0, y, vals, cw=cw, ch=22, index=False, size=8.6,
            kinds=["ok" if v else "bad" for v in vals])
    for i in range(6):
        p.text(x0 + i * cw + cw / 2, y - 14, str(cur[i]), 7.6,
               D.hi_bd if cur[i] else D.bad_bd, MONO_B, "c")
        p.text(x0 + i * cw + cw / 2, y - 28, str(best[i]), 7.6, D.ok_bd,
               MONO_B, "c")
    p.text(x0 - 8, y + 8, "value", 7.0, D.muted, SANS_SB, "r")
    p.text(x0 - 8, y - 14, "current", 7.0, D.hi_bd, SANS_SB, "r")
    p.text(x0 - 8, y - 28, "best", 7.0, D.ok_bd, SANS_SB, "r")
    p.arrow(x0 + 2 * cw + cw / 2, y - 40, x0 + 2 * cw + cw / 2, y - 32,
            D.bad_bd, 0.9, head=3)
    p.text(x0 + 2 * cw + cw / 2, y - 50, "the 0 resets current —", 6.8,
           D.bad_bd, SANS, "c")
    p.text(x0 + 2 * cw + cw / 2, y - 59, "but best survives it", 6.8,
           D.bad_bd, SANS, "c")


# ------------------------------------------------------------- two pointers
@fig("tp_two_shapes")
def tp_two_shapes(p):
    """Converging versus same-direction."""
    cw = 32
    for row, (title, kind, note) in enumerate([
            ("CONVERGING  —  from both ends, inwards", "hi",
             "pair sums on sorted data, palindromes, reversal, areas"),
            ("SAME DIRECTION  —  one reads, one writes", "ok",
             "filtering, deduplication, compaction, partitioning")]):
        y = p.h - 50 - row * 80
        x0 = 54
        p.text(x0 - 46, y + 44, title, 7.4,
               D.hi_bd if row == 0 else D.ok_bd, SANS_SB, "l")
        p.cells(x0, y, [""] * 8, cw=cw, ch=20, kinds=["dim"] * 8, index=False)
        if row == 0:
            p.pointer(x0 + cw / 2, y + 20, "left")
            p.pointer(x0 + 7 * cw + cw / 2, y + 20, "right")
            p.arrow(x0 + cw, y - 8, x0 + 3 * cw, y - 8, D.hi_bd, 0.9, head=3.2)
            p.arrow(x0 + 7 * cw, y - 8, x0 + 5 * cw, y - 8, D.hi_bd, 0.9,
                    head=3.2)
        else:
            p.pointer(x0 + 2 * cw + cw / 2, y + 20, "write")
            p.pointer(x0 + 5 * cw + cw / 2, y + 20, "read")
            p.arrow(x0 + 2 * cw + cw / 2, y - 8, x0 + 4 * cw, y - 8, D.ok_bd,
                    0.9, head=3.2)
            p.arrow(x0 + 5 * cw + cw / 2, y - 8, x0 + 7 * cw, y - 8, D.ok_bd,
                    0.9, head=3.2)
        p.text(x0 - 46, y - 24, note, 6.8, D.muted, SANS_I, "l")


@fig("tp_two_sum")
def tp_two_sum(p):
    """Each comparison eliminates a whole family of pairs."""
    cw = 50
    x0 = 86
    vals = [2, 7, 11, 15]
    steps = [(0, 3, "2 + 15 = 17  >  9", "too big → move right in"),
             (0, 2, "2 + 11 = 13  >  9", "too big → move right in"),
             (0, 1, "2 +  7 =  9  =  9", "found: indices 0 and 1")]
    for r, (l, rt, calc, note) in enumerate(steps):
        y = p.h - 38 - r * 46
        kinds = ["dim"] * 4
        for i in range(l, rt + 1):
            kinds[i] = ""
        kinds[l] = kinds[rt] = "ok" if r == 2 else "hi"
        p.cells(x0, y, vals, cw=cw, ch=22, kinds=kinds, index=True, size=8.6)
        p.pointer(x0 + l * cw + cw / 2, y + 22, "L")
        p.pointer(x0 + rt * cw + cw / 2, y + 22, "R")
        p.text(x0 + 4 * cw + 14, y + 12, calc, 7.4, D.ink, MONO, "l")
        p.text(x0 + 4 * cw + 14, y + 2, note, 6.8,
               D.ok_bd if r == 2 else D.muted, SANS_I, "l")
    p.text(0, 4, "moving L past an element rules out every pair that used it — "
           "n steps cover n²/2 pairs", 7.0, D.hi_bd, SANS_SB, "l")


@fig("tp_water")
def tp_water(p):
    """Move the shorter wall."""
    hs = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    cw, unit = 34, 11
    x0, y0 = 56, 36
    for i, h in enumerate(hs):
        k = "hi" if i in (1, 8) else "dim"
        p.box(x0 + i * cw + cw / 2 - 5, y0, 10, h * unit, None, k, radius=1,
              lw=0.6)
        p.text(x0 + i * cw + cw / 2, y0 - 11, str(i), 6.2, D.faint, SANS, "c")
    # water between 1 and 8
    p.box(x0 + 1 * cw + cw / 2 + 5, y0, 7 * cw - 10, 7 * unit, None, "teal",
          radius=0, lw=0.4)
    p.text(x0 + 4.5 * cw, y0 + 3.4 * unit, "area = 7 × 7 = 49", 8.0,
           D.teal_bd, SANS_SB, "c")
    p.pointer(x0 + 1 * cw + cw / 2, y0 + 8 * unit, "left")
    p.pointer(x0 + 8 * cw + cw / 2, y0 + 7 * unit, "right")
    p.text(0, p.h - 12, "the SHORTER wall caps the depth — moving the taller one in can only lose width",
           7.0, D.ink, SANS_SB, "l")


@fig("tp_read_write")
def tp_read_write(p):
    """write trails read by exactly the number discarded."""
    cw = 40
    x0, y = 64, p.h - 46
    vals = [3, 2, 2, 3, 4]
    after = [2, 2, 4, 3, 4]
    p.cells(x0, y, vals, cw=cw, ch=22, index=True, size=8.4,
            kinds=["bad", "ok", "ok", "bad", "ok"])
    p.text(x0 - 8, y + 8, "input", 6.9, D.muted, SANS_SB, "r")
    p.text(x0 + 5 * cw + 12, y + 8, "remove every 3", 6.9, D.bad_bd, SANS, "l")
    y2 = y - 50
    p.cells(x0, y2, after, cw=cw, ch=22, index=True, size=8.4,
            kinds=["ok", "ok", "ok", "dim", "dim"])
    p.pointer(x0 + 3 * cw + cw / 2, y2 + 22, "write = 3")
    p.brace(x0, x0 + 3 * cw, y2 - 6, "the answer: v[0 .. write-1]", up=False)
    p.brace(x0 + 3 * cw, x0 + 5 * cw, y2 - 6, "leftover — ignored", up=False)
    p.text(x0, y2 - 30, "write <= read always holds, so nothing is overwritten before it is read",
           7.0, D.ok_bd, SANS_SB, "l")


# ----------------------------------------------------------- sliding window
@fig("sw_overlap")
def sw_overlap(p):
    """Neighbouring windows share all but two elements."""
    cw = 44
    x0, y = 70, p.h - 44
    vals = [2, 1, 5, 1, 3, 2]
    for r in range(2):
        yy = y - r * 42
        here = set(range(r, r + 3))
        shared = set(range(0, 3)) & set(range(1, 4))     # the overlap
        kinds = ["dim"] * 6
        for i in here:
            kinds[i] = "teal" if i in shared else "hi"
        p.cells(x0, yy, vals, cw=cw, ch=22, kinds=kinds, index=False, size=8.6)
        p.text(x0 - 8, yy + 8, "window %d" % (r + 1), 6.9, D.muted, SANS_SB, "r")
        p.brace(x0 + r * cw, x0 + (r + 3) * cw, yy + 23,
                "sum = %d" % sum(vals[r:r + 3]), up=True)
    p.text(x0, y - 2 * 42 - 6,
           "the two shaded cells are in BOTH windows — the brute force re-adds them anyway",
           6.9, D.muted, SANS_I, "l")
    p.box(x0, y - 2 * 42 - 32, p.w - x0 - 10, 20, None, "ok", radius=3)
    p.text(x0 + 10, y - 2 * 42 - 26,
           "new sum  =  old sum  +  incoming  −  outgoing", 8.2, D.ink,
           MONO_B, "l")


@fig("sw_fixed")
def sw_fixed(p):
    """A window of 3 stepping along."""
    cw = 42
    x0, y0 = 70, p.h - 32
    vals = [2, 1, 5, 1, 3, 2]
    sums = [8, 7, 9, 6]
    for r in range(4):
        y = y0 - r * 32
        kinds = ["hi" if r <= i < r + 3 else "dim" for i in range(6)]
        p.cells(x0, y, vals, cw=cw, ch=20, kinds=kinds, index=False, size=8.2)
        p.text(x0 + 6 * cw + 12, y + 6, "sum = %d" % sums[r], 7.6,
               D.ok_bd if sums[r] == 9 else D.muted, MONO_B, "l")
        if r:
            p.text(x0 + 6 * cw + 72, y + 6, "+%d  −%d" % (vals[r + 2], vals[r - 1]),
                   7.0, D.hi_bd, MONO, "l")
    p.text(x0, y0 - 4 * 32 + 2, "one addition and one subtraction per step — never k additions",
           7.2, D.ink, SANS_SB, "l")


@fig("sw_variable")
def sw_variable(p):
    """Grow, shrink, record."""
    cw = 40
    x0, y0 = 72, p.h - 30
    vals = [2, 1, 5, 1, 3, 2]
    rows = [(0, 0, 2, "grow"), (0, 1, 3, "grow"), (0, 2, 8, "grow"),
            (1, 3, 7, "grow, then shrink once"),
            (3, 4, 4, "grow, then shrink twice"),
            (3, 5, 6, "grow")]
    for r, (l, rt, sm, note) in enumerate(rows):
        y = y0 - r * 27
        kinds = ["hi" if l <= i <= rt else "dim" for i in range(6)]
        p.cells(x0, y, vals, cw=cw, ch=18, kinds=kinds, index=False, size=7.8)
        p.text(x0 - 8, y + 5, "r=%d" % rt, 6.4, D.muted, MONO, "r")
        p.text(x0 + 6 * cw + 10, y + 5, "sum %-2d   %s" % (sm, note), 6.8,
               D.muted, SANS, "l")
    p.text(x0, y0 - 6 * 27 - 4,
           "right advances 6 times; left advances 3 times in total — not 3 times per step",
           7.0, D.ok_bd, SANS_SB, "l")
    p.text(x0, y0 - 6 * 27 - 15,
           "that total bound is why the inner while loop does not make it quadratic",
           6.8, D.muted, SANS_I, "l")


# --------------------------------------------------------------- prefix sums
@fig("ps_build")
def ps_build(p):
    """Each prefix entry is the previous plus one element."""
    cw = 48
    x0, y = 62, p.h - 56
    vals = [3, 1, 4, 1, 5]
    pre = [0, 3, 4, 8, 9, 14]
    p.cells(x0 + cw / 2, y, vals, cw=cw, ch=22, index=False, size=8.6)
    p.text(x0 + cw / 2 - 8, y + 8, "v", 8.0, D.ink, MONO_B, "r")
    y2 = y - 44
    p.cells(x0, y2, pre, cw=cw, ch=22, index=False, size=8.6,
            kinds=["teal"] + ["ok"] * 5)
    p.text(x0 - 8, y2 + 8, "prefix", 8.0, D.ok_bd, MONO_B, "r")
    for i in range(5):
        p.arrow(x0 + i * cw + cw / 2, y2 + 22, x0 + (i + 1) * cw + cw / 2,
                y2 + 22, D.faint, 0.7, head=2.6)
        p.text(x0 + (i + 0.5) * cw + cw / 2, y2 + 25, "+%d" % vals[i], 6.0,
               D.muted, SANS, "c")
    for i in range(6):
        p.text(x0 + i * cw + cw / 2, y2 - 12, str(i), 6.4, D.faint, SANS, "c")
    p.text(x0, y2 - 28, "prefix[0] = 0 — the sum of no elements. That leading zero removes every edge case.",
           6.9, D.teal_bd, SANS_SB, "l")


@fig("ps_range")
def ps_range(p):
    """sum(i,j) = prefix[j+1] - prefix[i]."""
    cw = 48
    x0, y = 62, p.h - 48
    pre = [0, 3, 4, 8, 9, 14]
    kinds = ["hi", "dim", "dim", "dim", "ok", "dim"]
    p.cells(x0, y, pre, cw=cw, ch=22, kinds=kinds, index=False, size=8.6)
    for i in range(6):
        p.text(x0 + i * cw + cw / 2, y - 12, "prefix[%d]" % i, 6.0, D.faint,
               MONO, "c")
    p.pointer(x0 + cw / 2, y + 22, "i = 1")
    p.pointer(x0 + 4 * cw + cw / 2, y + 22, "j+1 = 4")
    p.box(30, 12, p.w - 60, 30, None, "ok", radius=3)
    p.text(44, 26, "sum(1, 3)  =  prefix[4] − prefix[1]  =  9 − 3  =  6",
           8.4, D.ink, MONO_B, "l")
    p.text(44, 15, "that is v[1] + v[2] + v[3] = 1 + 4 + 1 — the shared part cancels exactly",
           6.6, D.muted, SANS_I, "l")


@fig("ps_subarray_k")
def ps_subarray_k(p):
    """running - K is the prefix we need to have seen."""
    cw = 54
    x0, y = 76, p.h - 46
    vals = [1, 2, 3]
    run = [1, 3, 6]
    p.cells(x0, y, vals, cw=cw, ch=22, index=False, size=8.6)
    for i in range(3):
        p.text(x0 + i * cw + cw / 2, y - 13, "running %d" % run[i], 6.6,
               D.muted, MONO, "c")
    p.pointer(x0 + 2 * cw + cw / 2, y + 22, "here")
    p.box(26, 48, p.w - 52, 26, None, "hi", radius=3)
    p.text(40, 57, "a sub-array ending here sums to K   ⟺   some earlier prefix = running − K",
           7.6, D.ink, SANS_SB, "l")
    p.box(26, 10, p.w - 52, 32, None, "ok", radius=3)
    p.text(40, 28, "running = 6,  K = 3   →   look up 3 in the map", 8.0,
           D.ink, MONO, "l")
    p.text(40, 17, "the map says prefix 3 occurred once  →  one sub-array, namely {3}",
           6.8, D.muted, SANS_I, "l")


@fig("ps_2d")
def ps_2d(p):
    """Inclusion-exclusion on a rectangle."""
    cw, ch = 30, 22
    x0, y0 = 60, p.h - 36
    R = C = 4
    for r in range(R):
        for c in range(C):
            inside = 1 <= r <= 2 and 1 <= c <= 2
            p.box(x0 + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5, None,
                  "ok" if inside else "dim", radius=0.8, lw=0.4)
    p.text(x0 + 1.5 * cw + cw / 2 - cw, y0 - 1.5 * ch + ch / 2,
           "wanted", 7.0, D.ok_bd, SANS_SB, "c")
    p.brace(x0, x0 + 3 * cw, y0 - 3 * ch - 4, "big rectangle  P[r2+1][c2+1]",
            up=False)
    terms = [("+", "P[r2+1][c2+1]", "everything up to the far corner", "ok"),
             ("−", "P[r1][c2+1]", "the strip above", "bad"),
             ("−", "P[r2+1][c1]", "the strip to the left", "bad"),
             ("+", "P[r1][c1]", "the corner removed twice — put it back", "hi")]
    bx = 186
    for i, (sign, expr, note, k) in enumerate(terms):
        yy = y0 - i * 22
        p.box(bx, yy - 6, 14, 15, sign, k, size=8.4, radius=2)
        p.text(bx + 20, yy, expr, 7.6, D.ink, MONO, "l")
        p.text(bx + 110, yy, note, 6.5, D.muted, SANS_I, "l")
    p.text(x0, 6, "four reads, whatever the size of the rectangle  →  O(1) per query",
           7.0, D.ink, SANS_SB, "l")


# ------------------------------------------------------------ binary search
@fig("bs_halving")
def bs_halving(p):
    """Three comparisons on ten elements."""
    cw = 36
    x0 = 50
    vals = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    steps = [(0, 9, 4, "v[4]=16 < 23  →  go right"),
             (5, 9, 7, "v[7]=56 > 23  →  go left"),
             (5, 6, 5, "v[5]=23  →  found at index 5")]
    y0 = p.h - 34
    for r, (lo, hi, mid, note) in enumerate(steps):
        y = y0 - r * 40
        kinds = ["dim"] * 10
        for i in range(lo, hi + 1):
            kinds[i] = ""
        kinds[mid] = "ok" if r == 2 else "hi"
        p.cells(x0, y, vals, cw=cw, ch=20, kinds=kinds, index=(r == 0),
                size=7.6)
        p.pointer(x0 + mid * cw + cw / 2, y + 20, "mid")
        p.text(x0, y - 12, note, 6.9, D.ok_bd if r == 2 else D.muted,
               SANS_SB if r == 2 else SANS, "l")
    p.text(x0, y0 - 3 * 40 + 6,
           "3 comparisons for 10 elements; 20 for a million; 30 for a billion",
           7.2, D.ink, SANS_SB, "l")


@fig("bs_invariant")
def bs_invariant(p):
    """The shaded region only shrinks and never loses the target."""
    cw = 30
    x0 = 56
    y0 = p.h - 30
    regions = [(0, 11), (6, 11), (6, 8), (8, 8)]
    for r, (lo, hi) in enumerate(regions):
        y = y0 - r * 30
        kinds = ["hi" if lo <= i <= hi else "dim" for i in range(12)]
        if r == 3:
            kinds[8] = "ok"
        p.cells(x0, y, [""] * 12, cw=cw, ch=18, kinds=kinds, index=False)
        p.text(x0 - 8, y + 5, "step %d" % r, 6.6, D.muted, SANS, "r")
        p.text(x0 + 12 * cw + 10, y + 5,
               "[lo, hi] = [%d, %d]" % (lo, hi), 6.8, D.muted, MONO, "l")
    p.text(x0, y0 - 4 * 30 + 4,
           "invariant: if the target exists, it is inside the shaded region",
           7.2, D.hi_bd, SANS_SB, "l")
    p.text(x0, y0 - 4 * 30 - 7,
           "the region halves each step, so it empties in log₂n steps — and an empty region means absent",
           6.8, D.muted, SANS_I, "l")


@fig("bs_first_last")
def bs_first_last(p):
    """On a match, keep going."""
    cw = 40
    x0 = 60
    vals = [5, 7, 7, 7, 8, 8, 10]
    for col, (title, idx, arrow, colour) in enumerate([
            ("FIRST occurrence of 7", 1, "keep searching LEFT", D.teal_bd),
            ("LAST occurrence of 7", 3, "keep searching RIGHT", D.violet_bd)]):
        y = p.h - 40 - col * 72
        kinds = ["teal" if v == 7 else "dim" for v in vals]
        kinds[idx] = "ok"
        p.cells(x0, y, vals, cw=cw, ch=21, kinds=kinds, index=True, size=8.2)
        p.text(x0 - 8, y + 6, title, 7.0, colour, SANS_SB, "r")
        p.pointer(x0 + idx * cw + cw / 2, y + 21, "answer")
        p.text(x0 + 7 * cw + 12, y + 6, arrow, 6.9, colour, SANS, "l")
        p.text(x0 + 7 * cw + 12, y - 4, "after recording the match", 6.5,
               D.muted, SANS_I, "l")
    p.text(x0 - 48, 6,
           "two searches give the count in O(log n):  last − first + 1",
           7.2, D.ink, SANS_SB, "l")


@fig("bs_answer_space")
def bs_answer_space(p):
    """Binary searching a monotonic predicate."""
    cw = 26
    x0 = 40
    y = p.h - 54
    n = 13
    kinds = ["bad" if i < 7 else "ok" for i in range(n)]
    kinds[7] = "hi"
    p.cells(x0, y, ["F"] * 7 + ["T"] * 6, cw=cw, ch=22, kinds=kinds,
            index=False, size=8)
    for i in range(n):
        p.text(x0 + i * cw + cw / 2, y - 11, str(i + 1), 6.2, D.faint, SANS, "c")
    p.brace(x0, x0 + 7 * cw, y + 23, "test says NO", up=True)
    p.brace(x0 + 7 * cw, x0 + n * cw, y + 23, "test says YES", up=True)
    p.pointer(x0 + 7 * cw + cw / 2, y - 32, "the boundary — the answer")
    p.text(x0, y - 52, "the candidates are every possible ANSWER, not the array",
           7.2, D.ink, SANS_SB, "l")
    p.text(x0, y - 63, "all that is required is that once the test turns true, it stays true",
           6.8, D.muted, SANS_I, "l")


# ---------------------------------------------------------------- in place
@fig("ip_what_counts")
def ip_what_counts(p):
    """Free, free, not free."""
    items = [("the INPUT array", "free — you may modify it", "ok"),
             ("a few int variables", "free — O(1), whatever n is", "ok"),
             ("a second array of n", "NOT free — O(n)", "bad"),
             ("n nested recursive calls", "NOT free — the stack is memory", "bad")]
    y = p.h - 26
    for i, (what, verdict, kind) in enumerate(items):
        yy = y - i * 28
        p.box(10, yy, 150, 20, what, kind, size=7.4, radius=2)
        p.text(172, yy + 6, verdict, 7.2,
               D.ok_bd if kind == "ok" else D.bad_bd, SANS_SB, "l")
    p.text(10, y - 4 * 28 - 2,
           "\"in place\" = O(1) AUXILIARY space — the input itself is not counted",
           7.2, D.ink, SANS_SB, "l")


@fig("ip_rotate")
def ip_rotate(p):
    """Three reversals."""
    cw = 40
    x0 = 76
    rows = [("start", [1, 2, 3, 4, 5, 6, 7], ["dim"] * 4 + ["hi"] * 3, "A = 1..4,  B = 5..7"),
            ("reverse all", [7, 6, 5, 4, 3, 2, 1], ["hi"] * 3 + ["dim"] * 4, "now Bᴿ Aᴿ — right order, each backwards"),
            ("reverse first 3", [5, 6, 7, 4, 3, 2, 1], ["ok"] * 3 + ["dim"] * 4, "Bᴿ becomes B"),
            ("reverse last 4", [5, 6, 7, 1, 2, 3, 4], ["ok"] * 3 + ["ok"] * 4, "Aᴿ becomes A  →  B A")]
    y0 = p.h - 34
    for r, (label, vals, kinds, note) in enumerate(rows):
        y = y0 - r * 36
        p.cells(x0, y, vals, cw=cw, ch=21, kinds=kinds, index=False, size=8.2)
        p.text(x0 - 8, y + 6, label, 6.8, D.muted, SANS_SB, "r")
        p.text(x0 + 7 * cw + 10, y + 6, note, 6.6, D.muted, SANS_I, "l")
    p.box(x0 - 60, 8, p.w - (x0 - 60) - 8, 22, None, "ok", radius=3)
    p.text(x0 - 48, 16, "(A B)ᴿ  =  Bᴿ Aᴿ      —  n/2 + k/2 + (n−k)/2  =  n swaps in all",
           8.0, D.ink, MONO, "l")


@fig("ip_index_marking")
def ip_index_marking(p):
    """The sign bit as a visited flag."""
    cw = 38
    x0 = 70
    y0 = p.h - 36
    rows = [("input", [4, 3, 2, 7, 8, 2, 3, 1], None),
            ("saw 4 → mark slot 3", [4, 3, 2, -7, 8, 2, 3, 1], 3),
            ("saw 3 → mark slot 2", [4, 3, -2, -7, 8, 2, 3, 1], 2),
            ("saw 2 → mark slot 1", [4, -3, -2, -7, 8, 2, 3, 1], 1)]
    for r, (label, vals, mark) in enumerate(rows):
        y = y0 - r * 30
        kinds = ["bad" if isinstance(v, int) and v < 0 else "dim"
                 for v in vals]
        if mark is not None:
            kinds[mark] = "hi"
        p.cells(x0, y, vals, cw=cw, ch=19, kinds=kinds, index=(r == 0),
                size=7.6)
        p.text(x0 - 8, y + 5, label, 6.6, D.muted, SANS, "r")
    p.text(x0, y0 - 4 * 30 + 4,
           "a slot already negative means that value has been seen before — a duplicate",
           7.0, D.bad_bd, SANS_SB, "l")
    p.text(x0, y0 - 4 * 30 - 7,
           "the magnitude still holds the original value, so nothing is lost",
           6.8, D.muted, SANS_I, "l")


# ------------------------------------------------------ frequency counting
@fig("fc_lookup")
def fc_lookup(p):
    """A search replaced by a lookup."""
    cw = 26
    x0 = 44
    y = p.h - 40
    vals = [4, 7, 4, 2, 7, 4]
    p.text(x0 - 34, y + 26, "WITHOUT A TABLE", 7.2, D.bad_bd, SANS_SB, "l")
    p.cells(x0, y, vals, cw=cw, ch=18, kinds=["hi"] * 6, index=False, size=7.6)
    for i in range(5):
        p.curve(x0 + 5 * cw + cw / 2, y - 2, x0 + i * cw + cw / 2, y - 2,
                bulge=-8, color=D.bad_bd, lw=0.6, arrow=False)
    p.text(x0 + 6 * cw + 12, y + 5, "rescan the past", 6.8, D.bad_bd, SANS, "l")
    p.text(x0 + 6 * cw + 12, y - 5, "for every element → O(n²)", 6.6,
           D.muted, SANS_I, "l")

    y2 = y - 66
    p.text(x0 - 34, y2 + 42, "WITH A TABLE", 7.2, D.ok_bd, SANS_SB, "l")
    p.cells(x0, y2 + 20, vals, cw=cw, ch=18, kinds=["ok"] * 6, index=False,
            size=7.6)
    p.box(x0 + 6 * cw + 12, y2 - 4, 104, 44, None, "ok", radius=3)
    p.text(x0 + 6 * cw + 22, y2 + 28, "freq", 7.0, D.ok_bd, MONO_B, "l")
    for i, (k, c) in enumerate([("4", 3), ("7", 2), ("2", 1)]):
        p.text(x0 + 6 * cw + 22, y2 + 16 - i * 11, "%s → %d" % (k, c), 7.2,
               D.ink, MONO, "l")
    for i in range(6):
        p.arrow(x0 + i * cw + cw / 2, y2 + 18, x0 + 6 * cw + 16, y2 + 20,
                D.faint, 0.5, head=2.2)
    p.text(x0, y2 - 18, "one pass to build, then every question is a lookup → O(n)",
           7.0, D.ok_bd, SANS_SB, "l")


@fig("fc_two_tools")
def fc_two_tools(p):
    """Count array versus hash map."""
    cw = 24
    x0 = 24
    y = p.h - 46
    p.text(x0, y + 30, "COUNT ARRAY", 7.4, D.ok_bd, SANS_SB, "l")
    p.text(x0, y + 20, "the value IS the index", 6.6, D.muted, SANS_I, "l")
    p.cells(x0, y, [0, 1, 0, 2, 3, 0, 0, 2], cw=cw, ch=19, index=True,
            size=7.4, kinds=["ok"] * 8)
    p.text(x0, y - 22, "one address calculation", 6.7, D.ok_bd, SANS, "l")
    p.text(x0, y - 31, "needs a slot per possible value", 6.7, D.muted,
           SANS_I, "l")

    x1 = 232
    p.text(x1, y + 30, "HASH MAP", 7.4, D.violet_bd, SANS_SB, "l")
    p.text(x1, y + 20, "any key at all", 6.6, D.muted, SANS_I, "l")
    for i, (k, c) in enumerate([("1000000", 3), ("-45", 1), ("\"cat\"", 2)]):
        p.box(x1, y + 4 - i * 16, 110, 14, None, "violet", radius=2, lw=0.5)
        p.text(x1 + 6, y + 8 - i * 16, "%-9s → %d" % (k, c), 6.8, D.ink,
               MONO, "l")
    p.text(x1, y - 22, "hash, bucket, pointer chase", 6.7, D.violet_bd, SANS, "l")
    p.text(x1, y - 31, "O(1) average, large constant", 6.7, D.muted, SANS_I, "l")
    p.text(x0, 2, "if the value can be used as an index, use the array — typically 5–20× faster",
           7.0, D.ink, SANS_SB, "l")


@fig("fc_two_sum")
def fc_two_sum(p):
    """Ask for the complement."""
    cw = 48
    x0 = 72
    y = p.h - 44
    vals = [2, 7, 11, 15]
    p.cells(x0, y, vals, cw=cw, ch=22, kinds=["ok", "hi", "dim", "dim"],
            index=True, size=8.6)
    p.pointer(x0 + cw + cw / 2, y + 22, "i = 1")
    p.box(26, 46, p.w - 52, 24, None, "hi", radius=3)
    p.text(40, 54, "target 9,  current 7   →   the partner must be 9 − 7 = 2",
           8.0, D.ink, MONO, "l")
    p.box(26, 10, p.w - 52, 30, None, "ok", radius=3)
    p.text(40, 27, "map holds { 2 → index 0 }   →   found, return (0, 1)",
           8.0, D.ink, MONO, "l")
    p.text(40, 16, "look up BEFORE inserting, or an element pairs with itself",
           6.7, D.bad_bd, SANS_SB, "l")


# ------------------------------------------------------------ sorting-based
@fig("sort_gifts")
def sort_gifts(p):
    """What becomes visible once sorted."""
    cw = 32
    x0 = 56
    y = p.h - 40
    un = [40, 11, 7, 39, 100, 11]
    sr = [7, 11, 11, 39, 40, 100]
    p.text(x0 - 48, y + 26, "UNSORTED", 7.4, D.bad_bd, SANS_SB, "l")
    p.cells(x0, y, un, cw=cw, ch=20, kinds=["dim"] * 6, index=False, size=7.8)
    p.text(x0 + 6 * cw + 12, y + 6, "duplicates? closest pair? median?", 6.8,
           D.muted, SANS_I, "l")
    p.text(x0 + 6 * cw + 12, y - 4, "none of it is visible", 6.8, D.bad_bd,
           SANS, "l")

    y2 = y - 58
    p.text(x0 - 48, y2 + 26, "SORTED", 7.4, D.ok_bd, SANS_SB, "l")
    kinds = ["dim", "hi", "hi", "ok", "ok", "dim"]
    p.cells(x0, y2, sr, cw=cw, ch=20, kinds=kinds, index=False, size=7.8)
    p.brace(x0 + cw, x0 + 3 * cw, y2 + 21, "duplicates are adjacent", up=True)
    p.brace(x0 + 3 * cw, x0 + 5 * cw, y2 - 4, "closest pair is adjacent too",
            up=False)
    p.text(x0 + 6 * cw + 12, y2 + 6, "and binary search now works", 6.8,
           D.ok_bd, SANS, "l")
    p.text(x0 - 48, y2 - 30,
           "adjacency · monotonicity · local closeness — the three gifts, bought for O(n log n)",
           7.0, D.ink, SANS_SB, "l")


@fig("sort_merge")
def sort_merge(p):
    """Two pointers walking two sorted arrays."""
    cw = 36
    x0 = 72
    a = [1, 2, 2, 4, 6]
    b = [2, 3, 4, 4, 9]
    y = p.h - 34
    p.cells(x0, y, a, cw=cw, ch=20, kinds=["ok", "ok", "dim", "dim", "dim"],
            index=False, size=8)
    p.text(x0 - 8, y + 6, "a", 8.0, D.ink, MONO_B, "r")
    p.pointer(x0 + 2 * cw + cw / 2, y + 20, "i")
    y2 = y - 46
    p.cells(x0, y2, b, cw=cw, ch=20, kinds=["ok", "dim", "dim", "dim", "dim"],
            index=False, size=8)
    p.text(x0 - 8, y2 + 6, "b", 8.0, D.ink, MONO_B, "r")
    p.pointer(x0 + cw + cw / 2, y2 + 20, "j")
    y3 = y2 - 42
    p.cells(x0, y3, [1, 2, 3, "", "", "", "", ""], cw=cw, ch=20,
            kinds=["ok"] * 3 + ["dim"] * 5, index=False, size=8)
    p.text(x0 - 8, y3 + 6, "out", 8.0, D.ok_bd, MONO_B, "r")
    p.text(x0 + 8 * cw + 10, y3 + 6, "always take the smaller front", 6.8,
           D.muted, SANS_I, "l")
    p.text(x0 - 48, y3 - 16,
           "each element is looked at once → O(n + m), and this is the heart of merge sort",
           7.0, D.ink, SANS_SB, "l")


# ------------------------------------------------------------------ kadane
@fig("kad_problem")
def kad_problem(p):
    """Every contiguous stretch has a sum; we want the biggest."""
    cw = 38
    x0 = 56
    vals = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    y = p.h - 34
    kinds = ["dim"] * 9
    for i in range(3, 7):
        kinds[i] = "ok"
    p.cells(x0, y, vals, cw=cw, ch=22, kinds=kinds, index=True, size=8.2)
    p.brace(x0 + 3 * cw, x0 + 7 * cw, y + 24, "sum 6 — the best there is",
            up=True)
    cands = [(0, 2, -4), (1, 3, 2), (5, 8, 2), (0, 8, 1)]
    for i, (lo, hi, s) in enumerate(cands):
        yy = y - 32 - i * 17
        p.line(x0 + lo * cw + 3, yy + 7, x0 + (hi + 1) * cw - 3, yy + 7,
               D.faint, 2.0)
        p.text(x0 + 9 * cw + 10, yy + 4, "sum %d" % s, 6.6, D.muted, MONO, "l")
    p.text(x0, y - 32 - 4 * 17 + 2,
           "a few of the 45 candidates — the brute force checks every one",
           6.8, D.muted, SANS_I, "l")


@fig("kad_extend_restart")
def kad_extend_restart(p):
    """The decision at each element."""
    y = p.h - 40
    p.box(14, y, 190, 36, None, "ok", radius=3)
    p.text(109, y + 23, "running sum ≥ 0", 8.0, D.ok_bd, SANS_SB, "c")
    p.text(109, y + 11, "an asset — EXTEND", 7.4, D.ink, SANS, "c")
    p.text(109, y + 1, "endingHere += v[i]", 7.0, D.muted, MONO, "c")

    p.box(216, y, 190, 36, None, "bad", radius=3)
    p.text(311, y + 23, "running sum < 0", 8.0, D.bad_bd, SANS_SB, "c")
    p.text(311, y + 11, "a liability — RESTART", 7.4, D.ink, SANS, "c")
    p.text(311, y + 1, "endingHere = v[i]", 7.0, D.muted, MONO, "c")

    cw = 38
    x0 = 56
    vals = [-2, 1, -3, 4, -1, 2, 1]
    end = [-2, 1, -2, 4, 3, 5, 6]
    restart = [False, True, False, True, False, False, False]
    y2 = y - 58
    p.cells(x0, y2, vals, cw=cw, ch=20, index=False, size=8,
            kinds=["bad" if r else "ok" for r in restart])
    for i in range(7):
        p.text(x0 + i * cw + cw / 2, y2 - 12, str(end[i]), 7.4,
               D.bad_bd if restart[i] else D.ok_bd, MONO_B, "c")
        if restart[i]:
            p.text(x0 + i * cw + cw / 2, y2 - 23, "restart", 5.8, D.bad_bd,
                   SANS_SB, "c")
    p.text(x0 - 8, y2 + 6, "v", 7.6, D.ink, MONO_B, "r")
    p.text(x0 - 8, y2 - 12, "ending", 6.8, D.muted, SANS_SB, "r")
    p.text(x0 - 8, y2 - 21, "here", 6.8, D.muted, SANS_SB, "r")
    p.text(x0, y2 - 38, "best = the largest value that row ever reaches  =  6",
           7.2, D.ink, SANS_SB, "l")


@fig("kad_product")
def kad_product(p):
    """A negative swaps largest and smallest."""
    cw = 54
    x0 = 92
    vals = [-2, 3, -4]
    hi = [-2, 3, 24]
    lo = [-2, -6, -12]
    y = p.h - 40
    p.cells(x0, y, vals, cw=cw, ch=22, index=False, size=8.6,
            kinds=["bad", "ok", "bad"])
    for i in range(3):
        p.text(x0 + i * cw + cw / 2, y - 14, str(hi[i]), 8.0, D.ok_bd,
               MONO_B, "c")
        p.text(x0 + i * cw + cw / 2, y - 28, str(lo[i]), 8.0, D.bad_bd,
               MONO_B, "c")
    p.text(x0 - 8, y + 6, "v", 7.6, D.ink, MONO_B, "r")
    p.text(x0 - 8, y - 14, "hi", 7.2, D.ok_bd, SANS_SB, "r")
    p.text(x0 - 8, y - 28, "lo", 7.2, D.bad_bd, SANS_SB, "r")
    p.arrow(x0 + 2 * cw + cw / 2 + 24, y - 24, x0 + 2 * cw + cw / 2 + 24,
            y - 12, D.violet_bd, 1.0, head=3.2)
    p.text(x0 + 2 * cw + cw / 2 + 30, y - 22, "−6 × −4 = 24", 7.2,
           D.violet_bd, SANS_SB, "l")
    p.text(x0 + 2 * cw + cw / 2 + 30, y - 32, "the worst value became the best",
           6.6, D.muted, SANS_I, "l")
    p.text(x0 - 80, 8,
           "with sums, a negative running total is useless — with products it is an asset in waiting",
           7.0, D.ink, SANS_SB, "l")


# ------------------------------------------------------------ matrix extras
@fig("mat_rotate")
def mat_rotate(p):
    """Transpose, then reverse each row."""
    cw, ch, n = 28, 21, 3
    grids = [("start", [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
             ("transpose", [[1, 4, 7], [2, 5, 8], [3, 6, 9]]),
             ("reverse rows", [[7, 4, 1], [8, 5, 2], [9, 6, 3]])]
    y0 = p.h - 42
    for i, (label, g) in enumerate(grids):
        x = 24 + i * 140
        p.text(x + n * cw / 2, y0 + 28, label, 7.2, D.muted, SANS_SB, "c")
        for r in range(n):
            for c in range(n):
                k = "ok" if i == 2 else ("teal" if r == c else "dim")
                p.box(x + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5,
                      str(g[r][c]), k, size=7.8, radius=1.2, font=MONO)
        if i < 2:
            p.arrow(x + n * cw + 12, y0 - ch, x + 140 - 14, y0 - ch, D.arrow,
                    1.0, head=3.6)
    p.text(24, y0 - n * ch - 14,
           "(r, c) → (c, r) → (c, n−1−r)    which is exactly a 90° clockwise turn",
           7.2, D.ink, MONO, "l")
    p.text(24, y0 - n * ch - 26,
           "both steps are things you can already write, and neither has an awkward boundary",
           6.8, D.muted, SANS_I, "l")


@fig("mat_spiral")
def mat_spiral(p):
    """Four shrinking boundaries."""
    cw, ch, n = 34, 26, 4
    x0 = 92
    y0 = p.h - 34
    order = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3),
             (3, 2), (3, 1), (3, 0), (2, 0), (1, 0),
             (1, 1), (1, 2), (2, 2), (2, 1)]
    ring = {}
    for i, (r, c) in enumerate(order):
        ring[(r, c)] = 0 if i < 12 else 1
    for r in range(n):
        for c in range(n):
            k = "hi" if ring[(r, c)] == 0 else "teal"
            p.box(x0 + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5,
                  str(order.index((r, c)) + 1), k, size=7.4, radius=1.2,
                  font=MONO)
    pts = [(x0 + c * cw + cw / 2 - 0.7, y0 - r * ch + ch / 2 - 0.7)
           for (r, c) in order]
    for a, b in zip(pts, pts[1:]):
        p.line(a[0], a[1], b[0], b[1], D.node_bd, 0.9)
    p.text(x0 + n * cw + 16, y0 - 4, "top → right →", 6.9, D.muted, SANS, "l")
    p.text(x0 + n * cw + 16, y0 - 14, "bottom → left,", 6.9, D.muted, SANS, "l")
    p.text(x0 + n * cw + 16, y0 - 24, "then inwards", 6.9, D.muted, SANS, "l")
    p.text(x0 - 76, y0 - n * ch - 12,
           "each pass consumes one edge and moves that boundary in by one",
           7.0, D.ink, SANS_SB, "l")
    p.text(x0 - 76, y0 - n * ch - 23,
           "the two guards matter only for a single remaining row or column",
           6.8, D.muted, SANS_I, "l")


@fig("mat_staircase")
def mat_staircase(p):
    """Start top-right; every comparison kills a row or a column."""
    cw, ch, n = 34, 24, 4
    x0 = 76
    y0 = p.h - 36
    g = [[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]]
    path = [(0, 3), (0, 2), (0, 1), (1, 1)]
    for r in range(n):
        for c in range(n):
            k = "ok" if (r, c) == (1, 1) else ("hi" if (r, c) in path else "dim")
            p.box(x0 + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5, str(g[r][c]),
                  k, size=7.6, radius=1.2, font=MONO)
    pts = [(x0 + c * cw + cw / 2, y0 - r * ch + ch / 2) for (r, c) in path]
    for a, b in zip(pts, pts[1:]):
        p.arrow(a[0], a[1], b[0], b[1], D.node_bd, 1.0, head=3.2, shrink=12)
    p.text(x0 + n * cw + 12, y0 + 2, "start here:", 6.9, D.hi_bd, SANS_SB, "l")
    p.text(x0 + n * cw + 12, y0 - 8, "biggest in its row,", 6.7, D.muted,
           SANS_I, "l")
    p.text(x0 + n * cw + 12, y0 - 17, "smallest in its column", 6.7, D.muted,
           SANS_I, "l")
    p.text(x0 - 60, y0 - n * ch - 12,
           "too big → drop the column (move left) · too small → drop the row (move down)",
           7.0, D.ink, SANS_SB, "l")
    p.text(x0 - 60, y0 - n * ch - 23,
           "at most R + C steps — on a 1000×1000 grid, 2,000 instead of a million",
           6.8, D.muted, SANS_I, "l")
