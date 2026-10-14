"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


@fig("arr_anatomy")
def arr_anatomy(p):
    """The canonical array picture, fully labelled."""
    cw = 62
    x0 = (p.w - 4 * cw) / 2
    y = p.h - 72
    p.cells(x0, y, [10, 20, 30, 40], cw=cw, ch=28, index=False, size=10)
    for i in range(4):
        cx = x0 + i * cw + cw / 2
        p.text(cx, y + 34, str(i), 8.6, D.node_bd, SANS_SB, "c")
        p.text(cx, y - 14, str(1000 + 4 * i), 7.0, D.faint, MONO, "c")
    p.text(x0 - 10, y + 33, "index", 7.2, D.node_bd, SANS_SB, "r")
    p.text(x0 - 10, y + 11, "value", 7.2, D.ink, SANS_SB, "r")
    p.text(x0 - 10, y - 15, "address", 7.2, D.faint, SANS_SB, "r")
    p.brace(x0, x0 + 4 * cw, y + 46, "arr  —  one block of 16 bytes", up=True)
    p.arrow(x0 - 22, y - 34, x0 + 4, y - 4, D.hi_bd, 1.0, head=3.4)
    p.text(x0 - 24, y - 40, "base address B = 1000", 7.2, D.hi_bd, SANS_SB, "l")
    p.text(x0 + 4 * cw + 12, y + 12, "4 elements", 7.2, D.muted, SANS, "l")
    p.text(x0 + 4 * cw + 12, y + 2, "4 bytes each", 7.2, D.muted, SANS, "l")


@fig("arr_zero_index")
def arr_zero_index(p):
    """The index is a distance from the base, not a count."""
    cw = 56
    x0 = 46
    y = p.h - 56
    p.cells(x0, y, [10, 20, 30, 40, 50], cw=cw, ch=24, index=False, size=9,
            kinds=["", "", "", "hi", ""])
    for i in range(5):
        p.text(x0 + i * cw + cw / 2, y + 30, "[%d]" % i, 7.6,
               D.hi_bd if i == 3 else D.muted, SANS_SB, "c")
    # the distance arrow
    p.line(x0, y - 12, x0, y - 30, D.faint, 0.7)
    p.line(x0 + 3 * cw, y - 12, x0 + 3 * cw, y - 30, D.hi_bd, 0.7)
    p.arrow(x0, y - 22, x0 + 3 * cw, y - 22, D.hi_bd, 1.0, head=3.6)
    p.text(x0 + 1.5 * cw, y - 34, "3 element-widths from the base", 7.2,
           D.hi_bd, SANS_SB, "c")
    p.text(x0, y + 46, "the index answers: how far from the start?", 7.4,
           D.ink, SANS_SB, "l")
    p.text(x0 + 5 * cw + 10, y + 8, "last index", 7.0, D.muted, SANS_SB, "l")
    p.text(x0 + 5 * cw + 10, y - 2, "= n - 1 = 4", 7.4, D.bad_bd, MONO_B, "l")


@fig("arr_access")
def arr_access(p):
    """One calculation, one read — nothing is scanned."""
    cw = 58
    x0 = 56
    y = p.h - 56
    p.cells(x0, y, [10, 20, 30, 40, 50], cw=cw, ch=24, index=True, size=9,
            kinds=["dim", "dim", "dim", "hi", "dim"])
    p.text(x0 + 1.5 * cw, y + 36, "never looked at", 6.9, D.faint, SANS_I, "c")
    p.arrow(x0 + 3 * cw + cw / 2, y + 44, x0 + 3 * cw + cw / 2, y + 27,
            D.hi_bd, 1.1, head=3.8)
    p.text(x0 + 3 * cw + cw / 2, y + 48, "arr[3]", 8.4, D.hi_bd, MONO_B, "c")
    p.box(30, 10, p.w - 60, 26, None, "ok", radius=3)
    p.text(44, 20, "B + 3 × 4  =  1000 + 12  =  1012        →  read 4 bytes  →  40",
           8.2, D.ink, MONO, "l")


@fig("arr_traverse")
def arr_traverse(p):
    """Five reads, one per element."""
    cw = 40
    x0 = 70
    y0 = p.h - 30
    vals = [10, 20, 30, 40, 50]
    for step in range(5):
        y = y0 - step * 23
        kinds = ["ok" if i < step else ("hi" if i == step else "dim")
                 for i in range(5)]
        p.cells(x0, y, vals, cw=cw, ch=17, kinds=kinds, index=False, size=7.4)
        p.text(x0 - 8, y + 5, "i = %d" % step, 6.8, D.muted, MONO, "r")
        p.text(x0 + 5 * cw + 10, y + 5, "read %d" % vals[step], 6.8, D.hi_bd,
               SANS, "l")
    p.text(x0, y0 - 5 * 23 - 2, "5 elements, 5 reads  —  O(n)", 7.6, D.ink,
           SANS_SB, "l")


@fig("arr_bounds")
def arr_bounds(p):
    """There is no fence at the end of an array."""
    cw = 46
    x0 = 44
    y = p.h - 58
    vals = [10, 20, 30, "?", "?", "?"]
    kinds = ["", "", "", "dim", "dim", "bad"]
    p.cells(x0, y, vals, cw=cw, ch=24, kinds=kinds, index=True, size=8.6)
    p.brace(x0, x0 + 3 * cw, y + 28, "arr — the 3 elements you own", up=True)
    p.brace(x0 + 3 * cw, x0 + 6 * cw, y + 28,
            "other variables, or nothing in particular", up=True)
    p.arrow(x0 + 5 * cw + cw / 2, y - 30, x0 + 5 * cw + cw / 2, y - 6,
            D.bad_bd, 1.1, head=3.8)
    p.text(x0 + 5 * cw + cw / 2, y - 40, "arr[5]", 8.4, D.bad_bd, MONO_B, "c")
    p.text(x0, y - 56, "no error, no crash — just whatever those 4 bytes happened to contain",
           7.2, D.bad_bd, SANS_SB, "l")
    p.text(x0, y - 68, "and if you WRITE there, you have silently corrupted something else",
           7.0, D.muted, SANS_I, "l")


@fig("arr_shift")
def arr_shift(p):
    """Insertion makes a gap; deletion closes one."""
    cw = 38
    x0 = 66
    # insert
    y = p.h - 34
    p.text(0, y + 6, "INSERT 99", 7.2, D.hi_bd, SANS_SB, "l")
    p.text(0, y - 4, "at index 1", 6.6, D.muted, SANS_I, "l")
    p.cells(x0, y, [10, 20, 30, 40, ""], cw=cw, ch=18, index=False, size=7.6,
            kinds=["", "", "", "", "dim"])
    for i in range(1, 4):
        p.curve(x0 + i * cw + cw / 2, y + 19, x0 + (i + 1) * cw + cw / 2,
                y + 19, bulge=7, color=D.hi_bd, lw=0.8, label=None)
    p.text(x0 + 5 * cw + 12, y + 5, "3 elements shift right", 6.9, D.hi_bd,
           SANS, "l")
    y2 = y - 32
    p.cells(x0, y2, [10, 99, 20, 30, 40], cw=cw, ch=18, index=False, size=7.6,
            kinds=["", "ok", "", "", ""])
    p.text(x0 + 5 * cw + 12, y2 + 5, "now there is room", 6.9, D.ok_bd, SANS, "l")

    # delete
    y3 = y2 - 50
    p.text(0, y3 + 6, "DELETE", 7.2, D.bad_bd, SANS_SB, "l")
    p.text(0, y3 - 4, "index 1", 6.6, D.muted, SANS_I, "l")
    p.cells(x0, y3, [10, 20, 30, 40, 50], cw=cw, ch=18, index=False, size=7.6,
            kinds=["", "bad", "", "", ""])
    for i in range(2, 5):
        p.curve(x0 + i * cw + cw / 2, y3 + 19, x0 + (i - 1) * cw + cw / 2,
                y3 + 19, bulge=-7, color=D.bad_bd, lw=0.8)
    p.text(x0 + 5 * cw + 12, y3 + 5, "3 elements shift left", 6.9, D.bad_bd,
           SANS, "l")
    y4 = y3 - 32
    p.cells(x0, y4, [10, 30, 40, 50, ""], cw=cw, ch=18, index=False, size=7.6,
            kinds=["", "", "", "", "dim"])
    p.text(x0 + 5 * cw + 12, y4 + 5, "the gap is closed", 6.9, D.muted,
           SANS_I, "l")
    p.text(0, 2, "in the worst case every one of the n elements moves  →  O(n)",
           7.2, D.ink, SANS_SB, "l")


@fig("vec_cannot_grow")
def vec_cannot_grow(p):
    """The bytes after an array are already somebody's."""
    cw = 40
    x0 = 50
    y = p.h - 56
    p.cells(x0, y, [10, 20, 30, 40, "", "", ""], cw=cw, ch=22, index=False,
            size=8, kinds=["", "", "", "", "bad", "bad", "bad"])
    p.brace(x0, x0 + 4 * cw, y + 26, "your array — 4 elements", up=True)
    p.brace(x0 + 4 * cw, x0 + 7 * cw, y + 26, "already somebody else's", up=True)
    for i, lab in enumerate(["a local", "variable", "or junk"]):
        p.text(x0 + (4 + i) * cw + cw / 2, y + 7, lab, 6.0, D.bad_bd, SANS_I, "c")
    p.arrow(x0 + 4 * cw + cw / 2, y - 26, x0 + 4 * cw + cw / 2, y - 5,
            D.bad_bd, 1.1, head=3.6)
    p.text(x0 + 4 * cw + cw / 2, y - 36, "arr[4] = 50;   ✗", 8.0, D.bad_bd,
           MONO_B, "c")
    p.text(x0, y - 52, "there is no free space to expand into — the only way out is to move",
           7.2, D.ink, SANS_SB, "l")


@fig("vec_size_capacity")
def vec_size_capacity(p):
    """The filled part and the whole block."""
    cw = 38
    x0 = 52
    y = p.h - 60
    vals = [10, 20, 30, 40, 50, "", "", ""]
    kinds = ["ok"] * 5 + ["dim"] * 3
    p.cells(x0, y, vals, cw=cw, ch=24, index=True, size=8.4, kinds=kinds)
    p.brace(x0, x0 + 5 * cw, y + 28, "size() = 5  —  elements you have put in",
            up=True)
    p.brace(x0, x0 + 8 * cw, y - 22,
            "capacity() = 8  —  what this block could hold", up=False)
    p.text(x0 + 6.5 * cw, y + 10, "spare", 6.6, D.faint, SANS_I, "c")
    p.text(x0 + 6.5 * cw, y + 1, "room", 6.6, D.faint, SANS_I, "c")
    p.text(x0, y - 50, "the next 3 push_back calls just write into the spare room — no copying",
           7.2, D.ok_bd, SANS_SB, "l")


@fig("vec_realloc")
def vec_realloc(p):
    """Allocate bigger, copy across, free the old."""
    cw = 27
    x0 = 84
    y = p.h - 30
    p.text(0, y + 6, "1. full", 7.0, D.muted, SANS_SB, "l")
    p.cells(x0, y, [10, 20, 30, 40], cw=cw, ch=18, index=False, size=7.4,
            kinds=["ok"] * 4)
    p.text(x0 + 4 * cw + 8, y + 5, "size = capacity = 4", 6.6, D.muted,
           SANS_I, "l")

    y2 = y - 36
    p.text(0, y2 + 6, "2. allocate", 7.0, D.muted, SANS_SB, "l")
    p.cells(x0, y2, [""] * 8, cw=cw, ch=18, index=False, kinds=["dim"] * 8)
    p.text(x0 + 8 * cw + 8, y2 + 5, "twice as big", 6.6,
           D.muted, SANS_I, "l")

    y3 = y2 - 40
    p.text(0, y3 + 6, "3. copy", 7.0, D.hi_bd, SANS_SB, "l")
    p.cells(x0, y3, [10, 20, 30, 40, "", "", "", ""], cw=cw, ch=18,
            index=False, size=7.4, kinds=["hi"] * 4 + ["dim"] * 4)
    for i in range(4):
        p.arrow(x0 + i * cw + cw / 2, y2 - 2, x0 + i * cw + cw / 2, y3 + 20,
                D.hi_bd, 0.8, head=2.8)
    p.text(x0 + 8 * cw + 8, y3 + 5, "n copies → O(n)", 6.6,
           D.hi_bd, SANS_SB, "l")

    y4 = y3 - 36
    p.text(0, y4 + 6, "4. free + add", 7.0, D.ok_bd, SANS_SB, "l")
    p.cells(x0, y4, [10, 20, 30, 40, 50, "", "", ""], cw=cw, ch=18,
            index=False, size=7.4, kinds=["ok"] * 5 + ["dim"] * 3)
    p.text(x0 + 8 * cw + 10, y4 + 5, "old block released", 6.8, D.muted,
           SANS_I, "l")
    p.text(0, y4 - 16, "every pointer into the old block is now dangling",
           7.0, D.bad_bd, SANS_SB, "l")


@fig("vec_amortized")
def vec_amortized(p):
    """Cost of each individual push_back."""
    x0, y0, W, H = 36, 30, 320, p.h - 56
    p.axes(x0, y0, W, H, "push number", "cost of that one push")
    n = 33
    bw = W / n
    for i in range(1, n + 1):
        is_realloc = (i & (i - 1)) == 0 and i > 1      # powers of two
        h = (i / 32.0) * H * 0.88 if is_realloc else 3.0
        p.box(x0 + (i - 1) * bw + 0.8, y0, bw - 1.6, h, None,
              "bad" if is_realloc else "ok", radius=0.6, lw=0.3)
    p.line(x0, y0 + H * 0.13, x0 + W, y0 + H * 0.13, D.node_bd, 1.3,
           dashed=True)
    p.text(x0 + W + 6, y0 + H * 0.13 - 2.4, "running", 6.8, D.node_bd,
           SANS_SB, "l")
    p.text(x0 + W + 6, y0 + H * 0.13 - 11, "average", 6.8, D.node_bd,
           SANS_SB, "l")
    p.text(x0 + W + 6, y0 + H * 0.13 - 20, "— flat", 6.8, D.muted, SANS_I, "l")
    p.text(x0 + 2, y0 + H + 8,
           "spikes at 2, 4, 8, 16, 32 — twice as costly, but half as often",
           6.9, D.bad_bd, SANS_SB, "l")


def _rows(p, x0, cw, ch, y0, gap, rows):
    """Helper: a stack of labelled array snapshots."""
    for r, (label, vals, kinds, note) in enumerate(rows):
        y = y0 - r * gap
        p.cells(x0, y, vals, cw=cw, ch=ch, kinds=kinds, index=False, size=7.6)
        if label:
            p.text(x0 - 8, y + ch / 2 - 3, label, 6.8, D.muted, MONO, "r")
        if note:
            p.text(x0 + len(vals) * cw + 10, y + ch / 2 - 3, note, 6.8,
                   D.muted, SANS, "l")
    return y0 - (len(rows) - 1) * gap


@fig("op_insert")
def op_insert(p):
    """Insert 99 at index 2 by copying backwards."""
    cw, ch, x0 = 34, 18, 72
    y0 = p.h - 28
    B, H, O, K = "", "hi", "ok", "dim"
    rows = [
        ("start", [10, 20, 30, 40, 50, ""], [B]*5 + [K], "room for one more"),
        ("i = 4", [10, 20, 30, 40, 50, 50], [B]*4 + [H, H], "v[5] = v[4]"),
        ("i = 3", [10, 20, 30, 40, 40, 50], [B]*3 + [H, H, B], "v[4] = v[3]"),
        ("i = 2", [10, 20, 30, 30, 40, 50], [B]*2 + [H, H] + [B]*2, "v[3] = v[2]"),
        ("write", [10, 20, 99, 30, 40, 50], [B, B, O, B, B, B], "v[2] = 99"),
    ]
    last = _rows(p, x0, cw, ch, y0, 26, rows)
    p.text(x0, y0 + 22, "insert 99 at index 2  —  copy BACKWARDS, from the far end",
           7.4, D.ink, SANS_SB, "l")
    for i in range(6):
        p.text(x0 + i * cw + cw / 2, y0 + 12, str(i), 6.2, D.faint, SANS, "c")
    p.text(x0, last - 14, "3 elements moved; inserting at index 0 would move all n  →  O(n)",
           7.0, D.hi_bd, SANS_SB, "l")


@fig("op_delete")
def op_delete(p):
    """Delete index 1 by copying forwards."""
    cw, ch, x0 = 34, 18, 72
    y0 = p.h - 28
    B, H, R, K = "", "hi", "bad", "dim"
    rows = [
        ("start", [10, 20, 30, 40, 50], [B, R, B, B, B], "remove index 1"),
        ("i = 1", [10, 30, 30, 40, 50], [B, H, H, B, B], "v[1] = v[2]"),
        ("i = 2", [10, 30, 40, 40, 50], [B, B, H, H, B], "v[2] = v[3]"),
        ("i = 3", [10, 30, 40, 50, 50], [B, B, B, H, H], "v[3] = v[4]"),
        ("shrink", [10, 30, 40, 50, ""], [B, B, B, B, K], "pop_back()"),
    ]
    last = _rows(p, x0, cw, ch, y0, 26, rows)
    p.text(x0, y0 + 22, "delete index 1  —  copy FORWARDS, towards the hole",
           7.4, D.ink, SANS_SB, "l")
    for i in range(5):
        p.text(x0 + i * cw + cw / 2, y0 + 12, str(i), 6.2, D.faint, SANS, "c")
    p.text(x0, last - 14, "insertion goes backwards, deletion goes forwards — both so that every slot is read before it is overwritten",
           6.6, D.bad_bd, SANS_SB, "l")


@fig("op_reverse")
def op_reverse(p):
    """Two pointers walking inwards."""
    cw, ch, x0 = 46, 22, 86
    y0 = p.h - 42
    steps = [
        ([10, 20, 30, 40, 50], 0, 4, "swap v[0] and v[4]"),
        ([50, 20, 30, 40, 10], 1, 3, "swap v[1] and v[3]"),
        ([50, 40, 30, 20, 10], 2, 2, "left == right  →  stop"),
    ]
    for r, (vals, l, rt, note) in enumerate(steps):
        y = y0 - r * 44
        kinds = ["hi" if i in (l, rt) else ("ok" if (i < l or i > rt) else "")
                 for i in range(5)]
        if l == rt:
            kinds[l] = "ok"
        p.cells(x0, y, vals, cw=cw, ch=ch, kinds=kinds, index=False, size=8.4)
        if l != rt:
            p.pointer(x0 + l * cw + cw / 2, y + ch, "left")
            p.pointer(x0 + rt * cw + cw / 2, y + ch, "right")
            p.curve(x0 + l * cw + cw / 2, y - 3, x0 + rt * cw + cw / 2, y - 3,
                    bulge=-9, color=D.hi_bd, lw=0.9, arrow=False)
        else:
            p.pointer(x0 + l * cw + cw / 2, y + ch, "both")
        p.text(x0 + 5 * cw + 12, y + ch / 2 - 3, note, 6.9, D.muted, SANS, "l")
    p.text(x0, y0 - 2 * 44 - 22, "n/2 swaps, no second array  →  O(n) time, O(1) space",
           7.2, D.ok_bd, SANS_SB, "l")


@fig("op_dedupe")
def op_dedupe(p):
    """Write pointer trailing a read pointer."""
    cw, ch, x0 = 38, 19, 84
    y0 = p.h - 40
    steps = [
        ([1, 1, 2, 2, 2, 3], 1, 1, 1, "v[1] == v[0]  →  skip"),
        ([1, 2, 2, 2, 2, 3], 2, 2, 2, "new value  →  v[1] = 2"),
        ([1, 2, 2, 2, 2, 3], 2, 3, 2, "v[3] == kept  →  skip"),
        ([1, 2, 2, 2, 2, 3], 2, 4, 2, "v[4] == kept  →  skip"),
        ([1, 2, 3, 2, 2, 3], 3, 5, 3, "new value  →  v[2] = 3"),
    ]
    for r, (vals, w, rd, keep, note) in enumerate(steps):
        y = y0 - r * 30
        kinds = ["ok" if i < keep else ("dim" if i >= keep else "") for i in range(6)]
        kinds[rd] = "hi"
        p.cells(x0, y, vals, cw=cw, ch=ch, kinds=kinds, index=False, size=7.8)
        p.text(x0 - 8, y + 5, "r=%d" % rd, 6.4, D.hi_bd, MONO, "r")
        p.text(x0 + 6 * cw + 8, y + 5, note, 6.7, D.muted, SANS, "l")
        if w < 6:
            p.text(x0 + w * cw + cw / 2, y - 9, "w", 6.4, D.ok_bd, MONO_B, "c")
    p.text(x0 - 30, y0 - 5 * 30 + 4,
           "the first w elements are the unique ones; everything past w is ignored",
           6.8, D.ok_bd, SANS_SB, "l")


@fig("op_move_zeroes")
def op_move_zeroes(p):
    """Compact, then pad."""
    cw, ch, x0 = 42, 20, 92
    y0 = p.h - 34
    p.text(x0, y0 + 22, "PASS 1  —  compact every non-zero to the front",
           7.3, D.ok_bd, SANS_SB, "l")
    steps = [
        ([0, 1, 0, 3, 12], 0, 0, 0, "v[0] is 0  →  skip"),
        ([1, 1, 0, 3, 12], 1, 1, 1, "v[1] = 1  →  write at w=0"),
        ([1, 1, 0, 3, 12], 1, 2, 1, "v[2] is 0  →  skip"),
        ([1, 3, 0, 3, 12], 2, 3, 2, "v[3] = 3  →  write at w=1"),
        ([1, 3, 12, 3, 12], 3, 4, 3, "v[4] = 12 →  write at w=2"),
    ]
    for r, (vals, w, rd, keep, note) in enumerate(steps):
        y = y0 - r * 27
        kinds = ["ok" if i < keep else "dim" for i in range(5)]
        kinds[rd] = "hi"
        p.cells(x0, y, vals, cw=cw, ch=ch, kinds=kinds, index=False, size=8)
        p.text(x0 - 8, y + 5, "r=%d" % rd, 6.4, D.hi_bd, MONO, "r")
        p.text(x0 + 5 * cw + 8, y + 5, note, 6.7, D.muted, SANS, "l")
    y2 = y0 - 5 * 27 - 20
    p.text(x0, y2 + 24, "PASS 2  —  fill the rest with zeroes", 7.3,
           D.node_bd, SANS_SB, "l")
    p.cells(x0, y2, [1, 3, 12, 0, 0], cw=cw, ch=ch,
            kinds=["ok", "ok", "ok", "teal", "teal"], index=False, size=8)
    p.text(x0 + 5 * cw + 8, y2 + 5, "order of 1, 3, 12 never changed", 6.7,
           D.muted, SANS_I, "l")


@fig("mat_grid")
def mat_grid(p):
    """A grid, and the same grid as one line."""
    cw, ch = 28, 20
    x0, y0 = 36, p.h - 40
    p.text(x0 - 30, y0 + 26, "HOW WE PICTURE IT", 7.2, D.node_bd, SANS_SB, "l")
    vals = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    kinds = ["", "teal", "hi"]
    for r in range(3):
        for c in range(4):
            p.box(x0 + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5,
                  str(vals[r][c]), kinds[r], size=7.6, radius=1.2,
                  font=MONO)
        p.text(x0 - 6, y0 - r * ch + 6, "row %d" % r, 6.2, D.faint, SANS, "r")

    x1 = 184
    p.text(x1, y0 + 26, "HOW IT REALLY SITS IN MEMORY", 7.2, D.hi_bd,
           SANS_SB, "l")
    flat = [v for row in vals for v in row]
    fk = [""] * 4 + ["teal"] * 4 + ["hi"] * 4
    cw2 = 18
    p.cells(x1, y0 - ch, flat, cw=cw2, ch=ch - 1.5, kinds=fk, index=False,
            size=6.8)
    for i, lab in enumerate(["row 0", "row 1", "row 2"]):
        p.brace(x1 + i * 4 * cw2, x1 + (i + 1) * 4 * cw2, y0 - ch - 3,
                lab, up=False)
    p.text(x1, y0 - ch - 26, "one block of 12 ints — there is no second dimension",
           6.8, D.muted, SANS_I, "l")
    p.text(x1, y0 + 6, "flat index:", 6.4, D.faint, SANS, "l")
    for i in range(12):
        p.text(x1 + i * cw2 + cw2 / 2, y0 - ch - 11, str(i), 5.6, D.faint,
               MONO, "c")


@fig("mat_address")
def mat_address(p):
    """Flat index of g[2][1]."""
    cw, ch = 34, 22
    x0, y0 = 60, p.h - 40
    vals = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    for r in range(3):
        for c in range(4):
            k = "hi" if (r, c) == (2, 1) else ("dim" if r < 2 else "")
            p.box(x0 + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5,
                  str(vals[r][c]), k, size=8, radius=1.2, font=MONO)
        p.text(x0 - 6, y0 - r * ch + 6, "r = %d" % r, 6.4, D.faint, SANS, "r")
    for c in range(4):
        p.text(x0 + c * cw + cw / 2, y0 + ch - 2, "c = %d" % c, 6.4, D.faint,
               SANS, "c")
    p.brace(x0, x0 + 4 * cw, y0 - 2 * ch - 4,
            "skip 2 whole rows of 4 = 8, then 1 more = 9", up=False)
    p.box(44, 10, p.w - 88, 26, None, "ok", radius=3)
    p.text(58, 20, "flat(2, 1) = 2 × C + 1 = 2 × 4 + 1 = 9", 8.6, D.ink,
           MONO_B, "l")
    p.text(58, 10, "the formula needs the COLUMN count — never the row count",
           6.6, D.muted, SANS_I, "l")


@fig("mat_cache")
def mat_cache(p):
    """Walking along memory versus jumping across it."""
    cw, ch = 15, 13
    R, C = 5, 10
    for col, (title, rowwise, kind) in enumerate([
            ("ROW-MAJOR  —  along memory", True, "ok"),
            ("COLUMN-MAJOR  —  across it", False, "bad")]):
        x0 = col * 212
        y0 = p.h - 34
        p.text(x0, y0 + 20, title, 7.2, D.ok_bd if rowwise else D.bad_bd,
               SANS_SB, "l")
        for r in range(R):
            for c in range(C):
                order = (r * C + c) if rowwise else (c * R + r)
                k = kind if order < 12 else "dim"
                p.box(x0 + c * cw, y0 - r * ch, cw - 1.2, ch - 1.2, None, k,
                      radius=0.6, lw=0.35)
        # the visiting path
        pts = []
        for step in range(12):
            r, c = (step // C, step % C) if rowwise else (step % R, step // R)
            pts.append((x0 + c * cw + cw / 2 - 0.6, y0 - r * ch + ch / 2 - 0.6))
        for a, b in zip(pts, pts[1:]):
            p.line(a[0], a[1], b[0], b[1],
                   D.ok_bd if rowwise else D.bad_bd, 0.8)
        note = ("16 ints arrive per fetch;" if rowwise
                else "each step lands in a")
        note2 = ("the next 15 are free" if rowwise
                 else "different cache line")
        p.text(x0, y0 - R * ch - 8, note, 6.7, D.muted, SANS, "l")
        p.text(x0, y0 - R * ch - 17, note2, 6.7, D.muted, SANS, "l")
    p.text(0, 4, "same O(R·C), same number of operations — commonly 3–6× "
           "difference in real time", 7.0, D.ink, SANS_SB, "l")


@fig("mat_diagonals")
def mat_diagonals(p):
    """r == c, and r + c == n - 1."""
    cw, ch, n = 30, 22, 4
    for col, (title, test, kind) in enumerate([
            ("MAIN DIAGONAL   r == c", lambda r, c: r == c, "teal"),
            ("ANTI-DIAGONAL   r + c == n-1", lambda r, c: r + c == n - 1,
             "violet")]):
        x0 = 34 + col * 212
        y0 = p.h - 42
        p.text(x0, y0 + 26, title, 7.2,
               D.teal_bd if col == 0 else D.violet_bd, SANS_SB, "l")
        for r in range(n):
            for c in range(n):
                p.box(x0 + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5,
                      "%d%d" % (r, c), kind if test(r, c) else "dim",
                      size=6.8, radius=1.2, font=MONO)
        p.text(x0, y0 - n * ch - 6,
               "indices are equal" if col == 0 else "indices add up to 3",
               6.7, D.muted, SANS_I, "l")


@fig("mat_transpose")
def mat_transpose(p):
    """Swap the upper triangle with the lower."""
    cw, ch, n = 32, 23, 3
    y0 = p.h - 46
    x0 = 44
    before = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    after = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    for col, (title, g) in enumerate([("BEFORE", before), ("AFTER", after)]):
        bx = x0 + col * 250
        p.text(bx, y0 + 28, title, 7.4, D.muted, SANS_SB, "l")
        for r in range(n):
            for c in range(n):
                k = "ok" if r == c else ("hi" if c > r else "teal")
                p.box(bx + c * cw, y0 - r * ch, cw - 1.5, ch - 1.5,
                      str(g[r][c]), k, size=8, radius=1.2, font=MONO)
    p.arrow(x0 + n * cw + 24, y0 - ch, x0 + 250 - 18, y0 - ch, D.arrow, 1.1,
            head=4)
    p.text(x0 + n * cw + 56, y0 - ch + 6, "swap", 6.8, D.muted, SANS_I, "c")
    legend(p, x0, 14, [("ok", "diagonal — never moves"),
                       ("hi", "upper: c > r — visited"),
                       ("teal", "lower — its partner")], gap=132)
    p.text(x0, 1, "the inner loop starts at c = r + 1, so each pair is swapped exactly once",
           6.9, D.hi_bd, SANS_SB, "l")
