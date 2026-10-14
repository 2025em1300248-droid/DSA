"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


@fig("cmp_navigate_modify")
def cmp_navigate_modify(p):
    """Every operation is navigate + modify."""
    W, H = 150, 44
    y = p.h - 56
    p.text(28 + W / 2, y + H + 14, "NAVIGATE", 7.8, D.ink, SANS_SB, "c")
    p.text(28 + W / 2, y + H + 4, "get to position i", 6.6, D.muted,
           SANS_I, "c")
    p.text(222 + W / 2, y + H + 14, "MODIFY", 7.8, D.ink, SANS_SB, "c")
    p.text(222 + W / 2, y + H + 4, "do the thing once there", 6.6, D.muted,
           SANS_I, "c")
    rows = [("ARRAY", "O(1)", "ok", "O(n)", "bad", "compute the address",
             "shift everything after"),
            ("LINKED LIST", "O(n)", "bad", "O(1)", "ok", "follow i pointers",
             "two pointer writes")]
    for i, (name, nav, nk, mod, mk, nnote, mnote) in enumerate(rows):
        yy = y - i * 56
        p.text(22, yy + H / 2 - 3, name, 7.4, D.ink, SANS_SB, "r")
        p.box(28, yy, W, H, None, nk, radius=3)
        p.text(28 + W / 2, yy + 24, nav, 13, D.ink, MONO_B, "c")
        p.text(28 + W / 2, yy + 10, nnote, 6.4, D.muted, SANS_I, "c")
        p.box(222, yy, W, H, None, mk, radius=3)
        p.text(222 + W / 2, yy + 24, mod, 13, D.ink, MONO_B, "c")
        p.text(222 + W / 2, yy + 10, mnote, 6.4, D.muted, SANS_I, "c")
    p.text(10, 8, "insert at index i needs BOTH, so both structures are O(n) — "
           "insert at a held pointer needs only the right column",
           6.9, D.ink, SANS_SB, "l")


@fig("cmp_why_o1")
def cmp_why_o1(p):
    """A calculation versus a walk."""
    cw = 40
    y = p.h - 48
    p.text(0, y + 26, "ARRAY  —  three guarantees give a formula", 7.2,
           D.ok_bd, SANS_SB, "l")
    p.cells(64, y, [10, 20, 30, 40], cw=cw, ch=22, index=True, size=8.4,
            kinds=["dim", "dim", "dim", "ok"])
    for i in range(4):
        p.text(64 + i * cw + cw / 2, y - 20, str(1000 + 4 * i), 6.0, D.faint,
               MONO, "c")
    p.text(64 + 4 * cw + 14, y + 6, "same size · contiguous · in order", 6.6,
           D.muted, SANS_I, "l")
    p.text(64 + 4 * cw + 14, y - 4, "→  B + i × S", 7.6, D.ok_bd, MONO_B, "l")

    y2 = y - 72
    p.text(0, y2 + 32, "LINKED LIST  —  none of the three holds", 7.2,
           D.bad_bd, SANS_SB, "l")
    xs = chain(p, 64, y2, [10, 20, 30, 40], w=40, h=22, gap=18, size=8.2,
               kinds=["bad", "bad", "bad", "ok"])
    head_arrow(p, 64, y2, 22, up=14, w=40)
    for i in range(3):
        p.text(xs[i] + 40 + 9, y2 + 26, str(i + 1), 6.2, D.bad_bd, SANS_SB, "c")
    p.text(xs[3] + 54, y2 + 6, "no formula exists", 6.6, D.bad_bd, SANS, "l")
    p.text(xs[3] + 54, y2 - 4, "→  follow i pointers", 7.6, D.bad_bd,
           MONO_B, "l")


@fig("cmp_cache")
def cmp_cache(p):
    """Sequential versus dependent loads."""
    cw = 15
    y = p.h - 44
    p.text(0, y + 26, "ARRAY  —  sequential, prefetched", 7.2, D.ok_bd,
           SANS_SB, "l")
    p.cells(40, y, [""] * 24, cw=cw, ch=18, kinds=["ok"] * 24, index=False)
    for b in range(0, 24, 8):
        p.brace(40 + b * cw, 40 + (b + 8) * cw, y + 19, "one cache line",
                up=True)
    p.text(40, y - 12, "one fetch delivers 16 ints; the prefetcher loads the "
           "next line before you ask", 6.6, D.muted, SANS_I, "l")

    y2 = y - 76
    p.text(0, y2 + 42, "LINKED LIST  —  dependent jumps", 7.2, D.bad_bd,
           SANS_SB, "l")
    spots = [(50, 24), (190, 0), (96, 30), (300, 14), (140, 4), (250, 30)]
    prev = None
    for i, (dx, dy) in enumerate(spots):
        p.box(40 + dx, y2 + dy, 30, 16, str(i + 1), "bad", size=6.6, radius=1.5)
        if prev is not None:
            p.curve(prev[0], prev[1], 40 + dx, y2 + dy + 8, bulge=11,
                    color=D.bad_bd, lw=0.85)
        prev = (40 + dx + 30, y2 + dy + 8)
    p.text(40, y2 - 16, "the address of the NEXT fetch is unknown until this "
           "one returns — the loads cannot overlap", 6.6, D.bad_bd, SANS_SB, "l")
    p.text(40, y2 - 27, "a cache miss costs 100–300 cycles; the arithmetic "
           "waiting on it costs 1", 6.6, D.muted, SANS_I, "l")


@fig("method_flow")
def method_flow(p):
    """Four phases, seventeen steps."""
    phases = [("UNDERSTAND", "1–3", "teal",
               ["restate it", "input and output", "hand-work an example"]),
              ("GET IT WORKING", "4–7", "ok",
               ["simplest thing", "say it aloud", "its complexity",
                "name the bottleneck"]),
              ("IMPROVE IT", "8–11", "hi",
               ["match a pattern", "develop it", "trace it", "pseudocode"]),
              ("FINISH IT", "12–17", "violet",
               ["write the code", "explain it", "edge cases",
                "complexity", "what goes wrong", "a related problem"])]
    y = p.h - 30
    for i, (title, rng, kind, steps) in enumerate(phases):
        x = 6 + i * 100
        p.box(x, y, 94, 24, None, kind, radius=3)
        p.text(x + 47, y + 13, title, 7.0, D.ink, SANS_SB, "c")
        p.text(x + 47, y + 4, "steps " + rng, 6.2, D.muted, SANS, "c")
        for j, s in enumerate(steps):
            p.box(x + 4, y - 22 - j * 18, 86, 14, s, "white", size=6.3,
                  radius=2, lw=0.5)
        if i < 3:
            p.arrow(x + 96, y + 12, x + 100 + 2, y + 12, D.faint, 0.9, head=3)
    p.text(6, 20, "most candidates begin at step 12 and fail at step 14",
           7.0, D.bad_bd, SANS_SB, "l")
    p.text(6, 8, "the first four steps take two minutes and prevent most of "
           "the ways this goes wrong", 6.8, D.muted, SANS_I, "l")


@fig("method_worked")
def method_worked(p):
    """The worked problem's window."""
    cw = 46
    x0 = 96
    y0 = p.h - 34
    vals = [1, 5, 6, 7, 2]
    rows = [(0, 0, "1", "spread 0"),
            (1, 1, "5", "dropped 1 — spread was 4"),
            (1, 2, "5 6", "spread 1"),
            (1, 3, "5 6 7", "spread 2  ←  best"),
            (4, 4, "2", "dropped 5, 6, 7")]
    for r, (l, rt, win, note) in enumerate(rows):
        y = y0 - r * 28
        kinds = ["hi" if l <= i <= rt else "dim" for i in range(5)]
        p.cells(x0, y, vals, cw=cw, ch=19, kinds=kinds, index=False, size=8)
        p.text(x0 - 8, y + 5, "r=%d" % rt, 6.4, D.muted, MONO, "r")
        p.text(x0 + 5 * cw + 10, y + 5, note, 6.6,
               D.ok_bd if "best" in note else D.muted,
               SANS_SB if "best" in note else SANS, "l")
    p.box(20, 10, p.w - 40, 30, None, "hi", radius=3)
    p.text(34, 28, "the new difficulty: max and min of a window that SHRINKS",
           7.6, D.ink, SANS_SB, "l")
    p.text(34, 17, "a single running max cannot be undone — hence a multiset "
           "(O(n log n)) or two monotonic deques (O(n))",
           6.6, D.muted, SANS_I, "l")
