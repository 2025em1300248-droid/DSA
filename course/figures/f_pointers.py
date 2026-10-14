"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


@fig("ptr_what_is")
def ptr_what_is(p):
    """A variable, and a pointer holding its address."""
    y = p.h - 72
    # x
    p.box(50, y, 86, 36, None, "ok", radius=3)
    p.text(93, y + 14, "42", 13, D.ok_bd, MONO_B, "c")
    p.text(93, y + 44, "int x", 8.6, D.ink, MONO_B, "c")
    p.text(93, y - 12, "at address 1000", 6.8, D.faint, MONO, "c")
    p.text(93, y - 22, "holds a NUMBER", 6.8, D.muted, SANS_I, "c")

    # p
    p.box(252, y, 110, 36, None, "violet", radius=3)
    p.text(307, y + 14, "1000", 12, D.violet_bd, MONO_B, "c")
    p.text(307, y + 44, "int* p", 8.6, D.ink, MONO_B, "c")
    p.text(307, y - 12, "at address 2048", 6.8, D.faint, MONO, "c")
    p.text(307, y - 22, "holds an ADDRESS", 6.8, D.muted, SANS_I, "c")

    p.curve(250, y + 10, 140, y + 10, bulge=26, color=D.violet_bd, lw=1.2)
    p.text(196, y + 40, "the value in p is the address of x", 7.0,
           D.violet_bd, SANS_SB, "c")
    p.text(50, 8, "every arrow in this book means exactly that — "
           "\"the value here is the address of there\"", 7.0, D.ink, SANS_SB, "l")


@fig("ptr_operators")
def ptr_operators(p):
    """& and * as a round trip."""
    y = p.h - 56
    p.box(34, y, 104, 34, None, "ok", radius=3)
    p.text(86, y + 12, "x = 42", 9.6, D.ok_bd, MONO_B, "c")
    p.text(86, y + 40, "the VARIABLE", 7.0, D.muted, SANS_SB, "c")

    p.box(268, y, 104, 34, None, "violet", radius=3)
    p.text(320, y + 12, "1000", 9.6, D.violet_bd, MONO_B, "c")
    p.text(320, y + 40, "the ADDRESS", 7.0, D.muted, SANS_SB, "c")

    p.arrow(142, y + 26, 264, y + 26, D.hi_bd, 1.2, head=4)
    p.text(203, y + 31, "&x", 10, D.hi_bd, MONO_B, "c")
    p.text(203, y + 46, "\"the address of x\"", 6.8, D.muted, SANS_I, "c")

    p.arrow(264, y + 8, 142, y + 8, D.ok_bd, 1.2, head=4)
    p.text(203, y - 6, "*p", 10, D.ok_bd, MONO_B, "c")
    p.text(203, y - 18, "\"the thing at p\"", 6.8, D.muted, SANS_I, "c")

    p.box(34, 10, p.w - 68, 22, None, "dim", radius=3)
    p.text(p.w / 2, 18, "they undo each other:    *(&x)   is just   x", 8.4,
           D.ink, MONO_B, "c")


@fig("ptr_arrow")
def ptr_arrow(p):
    """Dot versus arrow."""
    y = p.h - 64
    # object
    p.box(42, y, 100, 42, None, "ok", radius=3)
    p.text(92, y + 26, "x: 3", 8.2, D.ink, MONO, "c")
    p.text(92, y + 12, "y: 4", 8.2, D.ink, MONO, "c")
    p.text(92, y + 50, "Point a", 8.4, D.ok_bd, MONO_B, "c")
    p.text(92, y - 14, "a.x   ✓   the dot", 8.0, D.ok_bd, MONO, "c")
    p.text(92, y - 25, "you are holding the object", 6.6, D.muted, SANS_I, "c")

    # pointer
    p.box(258, y + 10, 92, 24, None, "violet", radius=3)
    p.text(304, y + 18, "1000", 9, D.violet_bd, MONO_B, "c")
    p.text(304, y + 40, "Point* ptr", 8.4, D.violet_bd, MONO_B, "c")
    p.curve(256, y + 22, 146, y + 22, bulge=22, color=D.violet_bd, lw=1.1)
    p.text(304, y - 14, "ptr->x   ✓   the arrow", 8.0, D.violet_bd, MONO, "c")
    p.text(304, y - 25, "walk the pointer, then read", 6.6, D.muted, SANS_I, "c")
    p.text(304, y - 38, "ptr.x    ✗   does not compile", 7.6, D.bad_bd,
           MONO, "c")

    p.text(42, 6, "ptr->x  is exactly shorthand for  (*ptr).x  —  "
           "dereference first, then take the member", 6.9, D.ink, SANS_SB, "l")


@fig("ptr_ref_vs_ptr")
def ptr_ref_vs_ptr(p):
    """An alias versus a separate variable."""
    y = p.h - 70
    # reference
    p.text(22, y + 54, "REFERENCE   int& r = x;", 7.6, D.ok_bd, SANS_SB, "l")
    p.box(42, y, 96, 36, None, "ok", radius=3)
    p.text(90, y + 13, "42", 12, D.ok_bd, MONO_B, "c")
    p.text(70, y + 42, "x", 8.4, D.ink, MONO_B, "c")
    p.text(110, y + 42, "r", 8.4, D.ok_bd, MONO_B, "c")
    p.line(70, y + 39, 70, y + 36, D.faint, 0.7)
    p.line(110, y + 39, 110, y + 36, D.faint, 0.7)
    p.text(90, y - 13, "two labels, ONE set of bytes", 6.8, D.muted, SANS_I, "c")
    p.text(90, y - 23, "no extra storage, no arrow", 6.8, D.muted, SANS_I, "c")

    # pointer
    p.text(222, y + 54, "POINTER   int* q = &x;", 7.6, D.violet_bd, SANS_SB, "l")
    p.box(238, y, 70, 36, None, "ok", radius=3)
    p.text(273, y + 13, "42", 12, D.ok_bd, MONO_B, "c")
    p.text(273, y + 42, "x", 8.4, D.ink, MONO_B, "c")
    p.box(336, y, 70, 36, None, "violet", radius=3)
    p.text(371, y + 13, "1000", 9.6, D.violet_bd, MONO_B, "c")
    p.text(371, y + 42, "q", 8.4, D.violet_bd, MONO_B, "c")
    p.curve(334, y + 18, 310, y + 18, bulge=16, color=D.violet_bd, lw=1.1)
    p.text(322, y - 13, "TWO variables; one holds", 6.8, D.muted, SANS_I, "c")
    p.text(322, y - 23, "the address of the other", 6.8, D.muted, SANS_I, "c")

    p.text(22, 6, "a reference can never be null and can never be reseated — "
           "which is exactly why a list's next must be a pointer",
           6.8, D.ink, SANS_SB, "l")


@fig("ptr_passing")
def ptr_passing(p):
    """By value, by reference, by pointer."""
    rows = [("void f(int n)", "BY VALUE", "ok",
             "n is a COPY", "caller's variable unchanged"),
            ("void f(int& n)", "BY REFERENCE", "hi",
             "n IS the caller's variable", "changes stick"),
            ("void f(int* n)", "BY POINTER", "violet",
             "n holds its address", "changes stick, and may be nullptr")]
    y0 = p.h - 42
    for i, (sig, title, kind, what, effect) in enumerate(rows):
        y = y0 - i * 54
        p.box(14, y, 128, 26, None, kind, radius=3)
        p.text(78, y + 9, sig, 8.4, D.ink, MONO_B, "c")
        p.text(78, y + 30, title, 6.8, D.muted, SANS_SB, "c")
        # caller box
        p.box(186, y + 3, 62, 20, "a = 1", "dim", size=7.4, radius=2)
        p.text(217, y + 27, "caller", 6.2, D.faint, SANS, "c")
        if i == 0:
            p.box(272, y + 3, 62, 20, "n = 1", kind, size=7.4, radius=2)
            p.arrow(250, y + 13, 270, y + 13, D.faint, 0.9, head=3,
                    label=None)
            p.text(303, y + 27, "a separate copy", 6.2, D.faint, SANS, "c")
            p.text(348, y + 10, "✗ lost", 7.4, D.bad_bd, SANS_SB, "l")
        elif i == 1:
            p.box(272, y + 3, 62, 20, "n", kind, size=7.4, radius=2,
                  dashed=True)
            p.arrow(270, y + 13, 250, y + 13, D.ink, 1.0, head=3.2)
            p.text(303, y + 27, "another name for a", 6.2, D.faint, SANS, "c")
            p.text(338, y + 10, "✓ sticks", 7.4, D.ok_bd, SANS_SB, "l")
        else:
            p.box(272, y + 3, 62, 20, "n = &a", kind, size=7.0, radius=2)
            p.curve(270, y + 13, 250, y + 13, bulge=11, color=D.ink, lw=1.0)
            p.text(303, y + 27, "holds a's address", 6.2, D.faint, SANS, "c")
            p.text(338, y + 10, "✓ sticks", 7.4, D.ok_bd, SANS_SB, "l")
        p.text(14, y - 12, "%s — %s" % (what, effect), 6.7, D.muted,
               SANS_I, "l")


@fig("mem_two_regions")
def mem_two_regions(p):
    """Stack frames and the heap."""
    W = 150
    y0, H = 30, 108
    p.box(10, y0, W, H, None, "teal", radius=3, lw=1.0)
    p.text(10 + W / 2, y0 + H + 16, "THE STACK", 8.2, D.teal_bd, SANS_SB, "c")
    p.text(10 + W / 2, y0 + H + 6, "one frame per active call", 6.7, D.muted,
           SANS_I, "c")
    frames = [("main()", "head, curr"), ("insert()", "node, prev"),
              ("findNode()", "p")]
    for i, (fn, vars_) in enumerate(frames):
        yy = y0 + H - 30 - i * 32
        p.box(20, yy, W - 20, 26, None, "white", radius=2, lw=0.6)
        p.text(28, yy + 15, fn, 7.4, D.ink, MONO_B, "l")
        p.text(28, yy + 5, vars_, 6.4, D.muted, MONO, "l")
    p.text(10, y0 - 12, "popped automatically on return", 6.7, D.teal_bd,
           SANS, "l")
    p.text(10, y0 - 22, "small: 1–8 MB in total", 6.7, D.muted, SANS_I, "l")

    x1 = 232
    p.box(x1, y0, 164, H, None, "violet", radius=3, lw=1.0)
    p.text(x1 + 82, y0 + H + 16, "THE HEAP", 8.2, D.violet_bd, SANS_SB, "c")
    p.text(x1 + 82, y0 + H + 6, "whatever you asked for with new", 6.7,
           D.muted, SANS_I, "c")
    spots = [(14, 74), (84, 56), (44, 24), (104, 88), (118, 30)]
    for i, (dx, dy) in enumerate(spots):
        p.box(x1 + dx, y0 + dy, 44, 18, "Node", "white", size=6.4, radius=2,
              lw=0.6)
    p.text(x1, y0 - 12, "lives until you delete it", 6.7, D.violet_bd, SANS, "l")
    p.text(x1, y0 - 22, "large, scattered, and yours to manage", 6.7, D.muted,
           SANS_I, "l")

    p.arrow(28 + 38, y0 + H - 30 + 6, x1 + 16, y0 + 74 + 9, D.faint, 0.8,
            head=3, dashed=True)
    p.text(192, y0 + H - 4, "a pointer on the stack", 6.3, D.faint, SANS_I, "c")
    p.text(192, y0 + H - 13, "holding a heap address", 6.3, D.faint, SANS_I, "c")


@fig("mem_new_delete")
def mem_new_delete(p):
    """Allocate, construct, return; then destroy, free, and the pointer remains."""
    panels = [
        ("1. new int(42)", "ok", "ask for 4 bytes", "p = 3000"),
        ("2. construct", "ok", "write 42 there", "p = 3000"),
        ("3. delete p", "bad", "object destroyed", "p = 3000  ← unchanged!"),
        ("4. p = nullptr", "teal", "the habit", "p = nullptr"),
    ]
    W = 94
    y = p.h - 56
    for i, (title, kind, what, ptr) in enumerate(panels):
        x = 6 + i * 100
        p.text(x + W / 2, y + 44, title, 7.2, D.ink, SANS_SB, "c")
        if i < 3:
            p.box(x + 14, y + 14, 66, 24, "42" if i >= 1 else "?",
                  kind if i < 2 else "dim", size=9, radius=2, font=MONO_B)
        else:
            p.box(x + 14, y + 14, 66, 24, None, "dim", radius=2, dashed=True)
        p.text(x + W / 2, y + 4, what, 6.4, D.muted, SANS_I, "c")
        p.box(x + 8, y - 24, 78, 18, None, kind, radius=2)
        p.text(x + 47, y - 18, ptr.split("←")[0].strip(), 6.8, D.ink, MONO, "c")
        if i == 2:
            p.text(x + 47, y - 34, "dangling", 6.6, D.bad_bd, SANS_SB, "c")
    p.text(6, 8, "delete frees the OBJECT; it never touches the POINTER — "
           "which is why step 4 is worth the extra line", 6.9, D.ink,
           SANS_SB, "l")


@fig("mem_leak")
def mem_leak(p):
    """The pointer dies; the object does not."""
    y = p.h - 86
    p.box(18, y, 150, 72, None, "teal", radius=3)
    p.text(93, y + 78, "STACK — inside leak1()", 7.2, D.teal_bd, SANS_SB, "c")
    p.box(30, y + 42, 126, 22, "int* p = 3000", "white", size=7.2, radius=2,
          lw=0.6)
    p.text(93, y + 24, "…function returns…", 7.0, D.muted, SANS_I, "c")
    p.box(30, y + 4, 126, 22, None, "dim", radius=2, dashed=True)
    p.text(93, y + 10, "frame gone", 6.6, D.faint, SANS_I, "c")

    p.box(244, y, 150, 72, None, "violet", radius=3)
    p.text(319, y + 78, "HEAP", 7.2, D.violet_bd, SANS_SB, "c")
    p.box(268, y + 28, 100, 26, "42", "bad", size=10, radius=2, font=MONO_B)
    p.text(319, y + 16, "still allocated", 6.6, D.bad_bd, SANS_SB, "c")
    p.text(319, y + 6, "nothing knows where", 6.6, D.muted, SANS_I, "c")

    p.arrow(160, y + 53, 266, y + 41, D.faint, 0.9, head=3, dashed=True)
    p.text(205, y + 60, "the only pointer", 6.3, D.faint, SANS_I, "c")
    p.text(10, 8, "no crash · no exception · no compiler warning — "
           "which is exactly what makes leaks dangerous", 7.0, D.bad_bd,
           SANS_SB, "l")


@fig("mem_dangling")
def mem_dangling(p):
    """After delete, the pointer still holds the old address."""
    y = p.h - 50
    for col, (title, kind, label, note, colour) in enumerate([
            ("AFTER delete p;", "bad", "3000", "*p reads freed memory — "
             "often the old value, for a while", D.bad_bd),
            ("AFTER p = nullptr;", "ok", "nullptr", "*p crashes immediately — "
             "loud, obvious, fixable", D.ok_bd)]):
        x = 12 + col * 206
        p.text(x, y + 44, title, 7.4, colour, SANS_SB, "l")
        p.box(x, y + 14, 92, 26, label, kind, size=8.6, radius=2, font=MONO_B)
        p.text(x + 46, y + 6, "the pointer", 6.3, D.faint, SANS_I, "c")
        p.box(x + 110, y + 14, 76, 26, None, "dim", radius=2, dashed=True)
        p.text(x + 148, y + 22, "freed", 7.0, D.faint, SANS_I, "c")
        if col == 0:
            p.arrow(x + 94, y + 27, x + 108, y + 27, D.bad_bd, 0.9, head=3)
        p.text(x, y - 14, note, 6.7, D.muted, SANS_I, "l")
    p.text(12, 6, "delete p;  p = nullptr;   —  two words that turn a silent "
           "intermittent bug into an instant crash", 7.0, D.ink, SANS_SB, "l")
