"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I
from .kit import NW, NH, GAP, DATA_FRAC, chain, node, null_cap, head_arrow, legend


@fig("ds_drawer")
def ds_drawer(p):
    """The same cutlery, thrown in or laid out."""
    import random
    rnd = random.Random(7)
    y0, H, W = 16, 92, 182
    # --- messy drawer ---------------------------------------------------
    p.box(0, y0, W, H, None, "dim", radius=3, lw=1.1)
    p.text(W / 2, y0 + H + 8, "UNARRANGED", 7.6, D.bad_bd, SANS_SB, "c")
    items = [("fork", "hi"), ("knife", "teal"), ("spoon", "ok")] * 3
    rnd.shuffle(items)
    for i, (name, kind) in enumerate(items):
        bx = 10 + (i % 3) * 56 + rnd.randint(-5, 5)
        by = y0 + 10 + (i // 3) * 26 + rnd.randint(-3, 3)
        p.box(bx, by, 48, 17, name, kind, size=6.8, radius=1.6)
    p.text(W / 2, y0 - 11, "to find a fork: look at everything", 6.9,
           D.bad_bd, SANS, "c")

    # --- arranged drawer ------------------------------------------------
    x1 = 225
    p.box(x1, y0, W, H, None, "dim", radius=3, lw=1.1)
    p.text(x1 + W / 2, y0 + H + 8, "ARRANGED", 7.6, D.ok_bd, SANS_SB, "c")
    for s, (name, kind) in enumerate([("fork", "hi"), ("knife", "teal"),
                                      ("spoon", "ok")]):
        sy = y0 + H - 28 - s * 28
        p.box(x1 + 8, sy, W - 16, 24, None, "white", radius=2, lw=0.6)
        for k in range(3):
            p.box(x1 + 14 + k * 54, sy + 3.5, 50, 17, name, kind, size=6.8,
                  radius=1.6)
    p.text(x1 + W / 2, y0 - 11, "to find a fork: go to slot 1", 6.9,
           D.ok_bd, SANS, "c")


@fig("ds_memory_street")
def ds_memory_street(p):
    """Memory is a numbered street; the CPU can teleport to any house."""
    cw, n = 36, 10
    x0 = (p.w - n * cw) / 2
    y = 40
    vals = ["", "", "17", "4", "", "99", "", "", "23", ""]
    kinds = ["dim" if v == "" else "" for v in vals]
    p.cells(x0, y, vals, cw=cw, ch=22, kinds=kinds, index=False)
    for i in range(n):
        p.text(x0 + i * cw + cw / 2, y - 11, str(1000 + i * 4), 6.2,
               D.faint, MONO, "c")
    p.text(p.w / 2, y - 24, "every box has an address — a house number",
           7.0, D.muted, SANS_I, "c")
    cx = x0 + 5 * cw + cw / 2
    p.arrow(cx, y + 46, cx, y + 25, D.hi_bd, 1.1, head=3.8)
    p.text(cx, y + 50, '"go to address 1020"', 7.2, D.hi_bd, SANS_SB, "c")
    p.text(p.w / 2, y + 66, "one step, whatever the number", 6.9, D.muted,
           SANS_I, "c")


@fig("ds_two_shapes")
def ds_two_shapes(p):
    """One solid block versus scattered pieces joined by signposts."""
    # --- array ----------------------------------------------------------
    yA = p.h - 50
    cw = 40
    x0 = 56
    p.text(0, yA + 34, "ARRAY", 8.0, D.node_bd, SANS_SB, "l")
    p.text(0, yA + 23, "one block", 6.8, D.muted, SANS_I, "l")
    cs = p.cells(x0, yA, [10, 20, 30, 40, 50], cw=cw, ch=22, index=True,
                 kinds=["", "", "hi", "", ""])
    for i in range(5):
        p.text(x0 + i * cw + cw / 2, yA - 20, str(1000 + i * 4), 6.0,
               D.faint, MONO, "c")
    p.brace(x0, x0 + 5 * cw, yA + 24, "no gaps anywhere", up=True)
    p.text(x0 + 5 * cw + 14, yA + 11, "address of [3]", 6.8, D.ok_bd, SANS_SB, "l")
    p.text(x0 + 5 * cw + 14, yA + 2, "= 1000 + 3×4 = 1012", 6.8, D.muted, MONO, "l")
    p.text(x0 + 5 * cw + 14, yA - 8, "one calculation", 6.6, D.ok_bd, SANS_I, "l")

    # --- linked list ----------------------------------------------------
    yB = 30
    p.text(0, yB + 58, "LINKED LIST", 8.0, D.violet_bd, SANS_SB, "l")
    p.text(0, yB + 47, "scattered", 6.8, D.muted, SANS_I, "l")
    spots = [(62, yB + 38), (150, yB + 6), (240, yB + 40), (326, yB + 8)]
    vals = [10, 20, 30, 40]
    kinds = ["", "", "hi", ""]
    links = []
    for (bx, by), v, k in zip(spots, vals, kinds):
        links.append((node(p, bx, by, v, k, w=46, h=20, size=7.6), bx, by))
    for i in range(3):
        (lx, ly), _, _ = links[i]
        _, nx, ny = links[i + 1]
        p.arrow(lx, ly, nx - 1.5, ny + 10, D.violet_bd, 0.95, head=3.4)
    (lx, ly), _, _ = links[3]
    null_cap(p, lx + 4, yB + 10, 20)
    head_x = spots[0][0]
    p.arrow(head_x + 12, spots[0][1] + 40, head_x + 12, spots[0][1] + 22,
            D.node_bd, 1.0, head=3.4)
    p.text(head_x + 12, spots[0][1] + 43, "head", 7.2, D.node_bd, SANS_SB, "c")
    for (bx, by), a in zip(spots, ["1000", "2400", "1600", "3200"]):
        p.text(bx + 23, by - 9, a, 6.0, D.faint, MONO, "c")
    p.text(0, yB - 12, "to reach the 3rd value you must walk: 10 → 20 → 30",
           6.9, D.violet_bd, SANS_I, "l")


@fig("ds_roadmap")
def ds_roadmap(p):
    """The dependency order of the nine parts."""
    W, H = 118, 25
    rows = [
        [("I · Foundations\nmemory, Big O", "teal")],
        [("II · Arrays", ""), ("V · Pointers & memory", "violet")],
        [("III · Array patterns", ""), ("VI · Linked lists", "violet")],
        [("IV · Array problems", ""), ("VII · List problems", "violet")],
        [("VIII · Method & complexity", "hi")],
        [("IX · Practice, revision, mock interview", "ok")],
    ]
    y = p.h - 26
    centres = []
    for r, row in enumerate(rows):
        gap = 24
        total = len(row) * W + (len(row) - 1) * gap
        x = (p.w - total) / 2
        rowc = []
        for (label, kind) in row:
            lines = label.split("\n")
            p.box(x, y, W, H, None, kind, radius=3, lw=0.9)
            if len(lines) == 1:
                p.text(x + W / 2, y + H / 2 - 2.8, lines[0], 7.3, D.ink,
                       SANS_SB, "c")
            else:
                p.text(x + W / 2, y + H / 2 + 1.2, lines[0], 7.3, D.ink,
                       SANS_SB, "c")
                p.text(x + W / 2, y + H / 2 - 7.5, lines[1], 6.4, D.muted,
                       SANS, "c")
            rowc.append((x + W / 2, y))
            x += W + gap
        centres.append(rowc)
        y -= H + 14
    for r in range(len(rows) - 1):
        src, dst = centres[r], centres[r + 1]
        if len(src) == len(dst):
            pairs = list(zip(src, dst))            # straight down, no crossings
        elif len(src) == 1:
            pairs = [(src[0], d) for d in dst]     # one box feeds both columns
        else:
            pairs = [(s_, dst[0]) for s_ in src]   # both columns merge into one
        for (cx, cy), (tx, ty) in pairs:
            p.arrow(cx, cy - 1, tx, ty + H + 1.5, D.faint, 0.8, head=3.0)


@fig("mem_bit_byte")
def mem_bit_byte(p):
    """One switch, then eight of them."""
    y = p.h - 46
    p.text(0, y + 30, "ONE BIT", 7.6, D.teal_bd, SANS_SB, "l")
    p.box(0, y, 26, 22, "0", "dim", size=9, font=MONO_B)
    p.box(32, y, 26, 22, "1", "teal", size=9, font=MONO_B)
    p.text(29, y - 12, "off or on — that is all", 6.8, D.muted, SANS_I, "c")

    x0 = 128
    p.text(x0, y + 30, "ONE BYTE = 8 BITS", 7.6, D.node_bd, SANS_SB, "l")
    bits = "01010010"
    for i, b in enumerate(bits):
        p.box(x0 + i * 22, y, 20, 22, b, "" if b == "1" else "dim", size=8.4,
              font=MONO_B)
    p.brace(x0, x0 + 8 * 22 - 2, y - 3, "2^8 = 256 possible patterns", up=False)
    p.text(x0 + 8 * 22 + 14, y + 12, "= 82", 8.0, D.ok_bd, MONO_B, "l")
    p.text(x0 + 8 * 22 + 14, y + 2, "as a number", 6.6, D.muted, SANS_I, "l")


@fig("mem_street")
def mem_street(p):
    """Bytes with addresses; four of them make one int."""
    n, cw = 16, 23
    x0 = (p.w - n * cw) / 2
    y = 48
    kinds = ["dim"] * n
    for i in range(4, 8):
        kinds[i] = "hi"
    for i in range(10, 14):
        kinds[i] = "teal"
    p.cells(x0, y, [""] * n, cw=cw, ch=20, kinds=kinds, index=False)
    for i in range(n):
        if i % 2 == 0:
            p.text(x0 + i * cw + cw / 2, y - 10, str(1000 + i), 5.8, D.faint,
                   MONO, "c")
    p.text(p.w / 2, y - 23, "one box = one byte, each with its own address",
           6.9, D.muted, SANS_I, "c")
    p.brace(x0 + 4 * cw, x0 + 8 * cw, y + 21, "an int lives here — 4 bytes",
            up=True)
    p.text(x0 + 6 * cw, y + 42, 'we call it "the int at address 1004"', 6.8,
           D.hi_bd, SANS_SB, "c")
    p.brace(x0 + 10 * cw, x0 + 14 * cw, y + 21, "another int — 4 more bytes",
            up=True)


@fig("mem_variable")
def mem_variable(p):
    """Name, address and value are three different things."""
    y = p.h - 62
    # name column
    p.box(0, y, 112, 34, None, "violet", radius=3)
    p.text(56, y + 20, "x", 11, D.violet_bd, MONO_B, "c")
    p.text(56, y + 8, "the NAME", 6.6, D.muted, SANS_SB, "c")
    p.text(56, y - 12, "exists only in the", 6.6, D.muted, SANS_I, "c")
    p.text(56, y - 21, "compiler — not in memory", 6.6, D.muted, SANS_I, "c")

    # address column
    p.box(148, y, 112, 34, None, "hi", radius=3)
    p.text(204, y + 20, "1000", 10, D.hi_bd, MONO_B, "c")
    p.text(204, y + 8, "the ADDRESS", 6.6, D.muted, SANS_SB, "c")
    p.text(204, y - 12, "which byte the value", 6.6, D.muted, SANS_I, "c")
    p.text(204, y - 21, "starts at", 6.6, D.muted, SANS_I, "c")

    p.arrow(114, y + 17, 146, y + 17, D.faint, 0.9, head=3.4)
    p.text(130, y + 21, "names", 6.4, D.muted, SANS_I, "c")

    # value column: four bytes
    x2 = 296
    for i in range(4):
        p.box(x2 + i * 26, y, 24, 34, None, "ok", radius=2)
    p.text(x2 + 52, y + 20, "42", 10, D.ok_bd, MONO_B, "c")
    p.text(x2 + 52, y + 8, "the VALUE", 6.6, D.muted, SANS_SB, "c")
    for i in range(4):
        p.text(x2 + i * 26 + 12, y - 10, str(1000 + i), 5.8, D.faint, MONO, "c")
    p.text(x2 + 52, y - 21, "4 bytes, side by side", 6.6, D.muted, SANS_I, "c")
    p.arrow(262, y + 17, 294, y + 17, D.faint, 0.9, head=3.4)
    p.text(278, y + 21, "holds", 6.4, D.muted, SANS_I, "c")

    p.text(p.w / 2, 8, "int x = 42;", 9.2, D.ink, MONO_B, "c")


@fig("mem_three_vs_array")
def mem_three_vs_array(p):
    """No guarantee versus a guarantee."""
    cw = 15
    # --- three separate variables ---------------------------------------
    y = p.h - 54
    p.text(0, y + 30, "THREE SEPARATE int VARIABLES", 7.4, D.bad_bd, SANS_SB, "l")
    p.text(0, y + 20, "int a = 10;  int b = 20;  int c = 30;", 6.8, D.muted,
           MONO, "l")
    n = 24
    x0 = 10
    kinds = ["dim"] * n
    spots = {2: ("b", "bad"), 9: ("c", "bad"), 17: ("a", "bad")}
    for s, (nm, k) in spots.items():
        for j in range(4):
            kinds[s + j] = k
    p.cells(x0, y - 16, [""] * n, cw=cw, ch=16, kinds=kinds, index=False)
    for s, (nm, k) in spots.items():
        p.text(x0 + (s + 2) * cw, y - 26, nm, 7.2, D.bad_bd, MONO_B, "c")
    p.text(x0, y - 40, "any order, any gaps — the compiler decides", 6.8,
           D.bad_bd, SANS_I, "l")

    # --- an array --------------------------------------------------------
    y2 = 34
    p.text(0, y2 + 34, "ONE ARRAY OF THREE int", 7.4, D.ok_bd, SANS_SB, "l")
    p.text(0, y2 + 24, "int arr[3] = {10, 20, 30};", 6.8, D.muted, MONO, "l")
    kinds2 = ["dim"] * n
    for j in range(12):
        kinds2[4 + j] = "ok"
    p.cells(x0, y2, [""] * n, cw=cw, ch=16, kinds=kinds2, index=False)
    for i in range(3):
        p.text(x0 + (4 + i * 4 + 2) * cw, y2 - 10, "arr[%d]" % i, 6.6,
               D.ok_bd, MONO_B, "c")
    p.brace(x0 + 4 * cw, x0 + 16 * cw, y2 + 17, "guaranteed: one block, in order, no gaps",
            up=True)


@fig("mem_address_formula")
def mem_address_formula(p):
    """address(i) = B + i x S, drawn."""
    cw = 54
    x0 = 40
    y = p.h - 72
    vals = [10, 20, 30, 40, 50]
    p.cells(x0, y, vals, cw=cw, ch=24, kinds=["", "", "", "hi", ""], index=True,
            size=8.6)
    for i in range(5):
        p.text(x0 + i * cw + cw / 2, y - 20, str(1000 + 4 * i), 6.4, D.faint,
               MONO, "c")
    p.text(x0 - 6, y + 10, "B =", 7.0, D.node_bd, SANS_SB, "r")
    p.arrow(x0 - 4, y + 32, x0 + 2, y + 25, D.node_bd, 0.9, head=3.0)
    p.text(x0 + 6, y + 34, "B = 1000, the base address", 7.0, D.node_bd,
           SANS_SB, "l")
    p.brace(x0, x0 + cw, y - 28, "S = 4 bytes per element", up=False)

    bx, by = 30, 14
    p.box(bx, by, p.w - 60, 30, None, "hi", radius=3)
    p.text(bx + 14, by + 17, "address(3)  =  B + 3 x S  =  1000 + 3 x 4  =  1012",
           8.6, D.ink, MONO_B, "l")
    p.text(bx + 14, by + 6, "one multiplication, one addition — the same work for i = 3 or i = 3,000,000",
           6.6, D.muted, SANS_I, "l")


@fig("mem_stack_heap")
def mem_stack_heap(p):
    """Automatic memory versus memory you ask for."""
    W = 176
    y0, H = 28, 94
    # stack
    p.box(0, y0, W, H, None, "teal", radius=3, lw=1.0)
    p.text(W / 2, y0 + H + 16, "THE STACK", 8.0, D.teal_bd, SANS_SB, "c")
    p.text(W / 2, y0 + H + 6, "automatic, managed for you", 6.7, D.muted,
           SANS_I, "c")
    for i, (lab, sub) in enumerate([("int x = 42;", "a local variable"),
                                    ("int arr[5];", "a fixed-size array"),
                                    ("Node* head;", "the pointer, not the node")]):
        p.box(10, y0 + H - 26 - i * 28, W - 20, 22, None, "white", radius=2,
              lw=0.6)
        p.text(18, y0 + H - 26 - i * 28 + 12, lab, 7.4, D.ink, MONO, "l")
        p.text(18, y0 + H - 26 - i * 28 + 3, sub, 6.2, D.muted, SANS_I, "l")
    p.text(W / 2, y0 - 11, "freed the moment the function ends", 6.7,
           D.teal_bd, SANS, "c")

    # heap
    x1 = 231
    p.box(x1, y0, W, H, None, "violet", radius=3, lw=1.0)
    p.text(x1 + W / 2, y0 + H + 16, "THE HEAP", 8.0, D.violet_bd, SANS_SB, "c")
    p.text(x1 + W / 2, y0 + H + 6, "you ask for it, you give it back", 6.7,
           D.muted, SANS_I, "c")
    for i, (lab, sub) in enumerate([("new Node(10)", "a linked list node"),
                                    ("new Node(20)", "another one"),
                                    ("new int[n]", "size known at run time")]):
        p.box(x1 + 10, y0 + H - 26 - i * 28, W - 20, 22, None, "white",
              radius=2, lw=0.6)
        p.text(x1 + 18, y0 + H - 26 - i * 28 + 12, lab, 7.4, D.ink, MONO, "l")
        p.text(x1 + 18, y0 + H - 26 - i * 28 + 3, sub, 6.2, D.muted, SANS_I, "l")
    p.text(x1 + W / 2, y0 - 11, "lives until you delete it — or leaks", 6.7,
           D.violet_bd, SANS, "c")

    p.arrow(W + 12, y0 + H / 2, x1 - 12, y0 + H / 2, D.faint, 0.9, head=3.4,
            both=True)
    p.text((W + x1) / 2, y0 + H / 2 + 6, "a pointer", 6.4, D.muted, SANS_I, "c")
    p.text((W + x1) / 2, y0 + H / 2 - 13, "on the stack", 6.4, D.muted, SANS_I, "c")
    p.text((W + x1) / 2, y0 + H / 2 - 22, "points into", 6.4, D.muted, SANS_I, "c")
    p.text((W + x1) / 2, y0 + H / 2 - 31, "the heap", 6.4, D.muted, SANS_I, "c")


@fig("bigo_counting")
def bigo_counting(p):
    """Work proportional to n, versus work independent of n."""
    import math
    y = p.h - 34
    for col, (title, kind, sizes) in enumerate([
            ("sum(v)  —  touches every element", "hi", [3, 6, 12]),
            ("first(v)  —  touches one element", "ok", [3, 6, 12])]):
        x0 = col * 212
        p.text(x0, y + 16, title, 7.4, D.hi_bd if col == 0 else D.ok_bd,
               SANS_SB, "l")
        for r, n in enumerate(sizes):
            yy = y - 6 - r * 36
            cw = 11
            kinds = [kind if (col == 0 or i == 0) else "dim" for i in range(n)]
            p.cells(x0, yy, [""] * n, cw=cw, ch=13, kinds=kinds, index=False)
            p.text(x0 + 12 * cw + 6, yy + 3, "n = %d" % n, 6.6, D.muted,
                   SANS, "l")
            steps = n if col == 0 else 1
            p.text(x0 + 12 * cw + 46, yy + 3, "%d step%s" % (steps,
                   "" if steps == 1 else "s"), 6.8,
                   D.hi_bd if col == 0 else D.ok_bd, SANS_SB, "l")
        p.text(x0, y - 122, "O(n)" if col == 0 else "O(1)", 10,
               D.hi_bd if col == 0 else D.ok_bd, MONO_B, "l")
        p.text(x0 + 32, y - 121, "work grows with n" if col == 0
               else "work never grows", 6.8, D.muted, SANS_I, "l")


@fig("bigo_definition")
def bigo_definition(p):
    """c*g(n) is an upper envelope beyond n0."""
    import math
    x0, y0, W, H = 34, 26, 330, p.h - 60
    p.axes(x0, y0, W, H, "n", "work")
    f = lambda t: 0.55 * t * t + 6 * t + 14
    g = lambda t: t * t
    xmax, ymax = 10.0, 100.0
    p.plot(x0, y0, W, H, g, xmax, ymax, D.faint, 1.0, dashed=True,
           label="g(n) = n²")
    p.plot(x0, y0, W, H, lambda t: 1.6 * g(t), xmax, ymax, D.ok_bd, 1.4,
           label="c · g(n)")
    p.plot(x0, y0, W, H, f, xmax, ymax, D.node_bd, 1.4, label="f(n)")
    n0 = 2.6
    px = x0 + (n0 / xmax) * W
    p.line(px, y0, px, y0 + H, D.hi_bd, 0.9, dashed=True)
    p.text(px, y0 - 11, "n₀", 7.4, D.hi_bd, SANS_SB, "c")
    p.text(px + 6, y0 + H - 6, "beyond here, c·g(n) stays above f(n)", 6.9,
           D.hi_bd, SANS_SB, "l")
    p.box(px - 150, y0 + H - 3, 1, 1, None, "dim", lw=0)
    p.text(x0 + 2, y0 + H + 8, "before n₀ anything may happen — we do not care",
           6.8, D.muted, SANS_I, "l")


@fig("bigo_growth")
def bigo_growth(p):
    """The standard growth hierarchy."""
    import math
    x0, y0, W, H = 30, 26, 300, p.h - 52
    p.axes(x0, y0, W, H, "input size n", "work")
    xmax, ymax = 24.0, 60.0
    curves = [
        (lambda t: 1.0, D.ok_bd, "O(1)"),
        (lambda t: math.log2(t + 1) * 2.2, D.teal_bd, "O(log n)"),
        (lambda t: t * 1.4, D.node_bd, "O(n)"),
        (lambda t: t * math.log2(t + 1) * 0.55, D.violet_bd, "O(n log n)"),
        (lambda t: t * t * 0.14, D.hi_bd, "O(n²)"),
        (lambda t: min(2 ** (t * 0.42), 400), D.bad_bd, "O(2ⁿ)"),
    ]
    for fn, col, lab in curves:
        p.plot(x0, y0, W, H, fn, xmax, ymax, col, 1.25, label=None)
    ly = y0 + H - 4
    for fn, col, lab in reversed(curves):
        p.text(x0 + W + 14, ly, lab, 7.2, col, SANS_SB, "l")
        ly -= 13
    p.text(x0 + 4, y0 + H + 9, "all six start out close together — "
           "the differences only appear later", 6.8, D.muted, SANS_I, "l")


@fig("bigo_nested")
def bigo_nested(p):
    """n rows of n cells."""
    n, cw = 9, 17
    x0 = 44
    y = p.h - 24
    for i in range(n):
        for j in range(n):
            p.box(x0 + j * cw, y - (i + 1) * cw, cw - 2, cw - 2, None,
                  "hi" if i == 2 else "dim", radius=0.8, lw=0.4)
        p.text(x0 - 6, y - (i + 1) * cw + 4.5, "i=%d" % i, 6.0, D.faint,
               SANS, "r")
    p.brace(x0, x0 + n * cw - 2, y + 2, "the inner loop: n iterations", up=True)
    p.text(x0 + n * cw + 16, y - 3 * cw + 6,
           "for i = 2 the inner", 6.9, D.hi_bd, SANS_SB, "l")
    p.text(x0 + n * cw + 16, y - 3 * cw - 3,
           "loop runs all n times", 6.9, D.hi_bd, SANS, "l")
    p.text(x0 + n * cw + 16, y - 3 * cw - 14,
           "— and so does every", 6.9, D.muted, SANS_I, "l")
    p.text(x0 + n * cw + 16, y - 3 * cw - 23, "other row", 6.9, D.muted,
           SANS_I, "l")
    p.text(x0 + n * cw + 16, y - n * cw + 22, "n rows × n cells", 7.6, D.ink,
           SANS_SB, "l")
    p.text(x0 + n * cw + 16, y - n * cw + 10, "= n²  cells in all", 8.4,
           D.bad_bd, MONO_B, "l")


@fig("bigo_halving")
def bigo_halving(p):
    """Four halvings of sixteen."""
    rows = [16, 8, 4, 2, 1]
    cw = 18
    y = p.h - 22
    for r, n in enumerate(rows):
        total = n * cw
        x0 = 40
        for i in range(n):
            p.box(x0 + i * cw, y - r * 25, cw - 2, 15, None,
                  "teal" if r < len(rows) - 1 else "ok", radius=1, lw=0.5)
        p.text(x0 - 8, y - r * 25 + 4, "%d" % n, 7.0, D.muted, MONO, "r")
        if r:
            p.text(x0 + total + 12, y - r * 25 + 4,
                   "step %d — half thrown away" % r, 6.9, D.muted, SANS, "l")
        else:
            p.text(x0 + total + 12, y - r * 25 + 4, "start: 16 candidates",
                   6.9, D.muted, SANS, "l")
    p.text(40, y - 5 * 25 - 2, "4 steps to reach 1, and log₂16 = 4", 7.6,
           D.teal_bd, SANS_SB, "l")
    p.text(40, y - 5 * 25 - 14,
           "double the data to 32 and you need 5 steps — one more, not sixteen more",
           6.8, D.muted, SANS_I, "l")


@fig("bigo_cases")
def bigo_cases(p):
    """Best, worst and average for a linear scan."""
    cw, n = 26, 12
    x0 = (p.w - n * cw) / 2
    rows = [("BEST", 0, "ok", "found at once — 1 comparison → O(1)"),
            ("AVERAGE", 6, "hi", "found halfway — n/2 comparisons → O(n)"),
            ("WORST", 11, "bad", "last, or absent — n comparisons → O(n)")]
    y = p.h - 26
    for r, (lab, hit, kind, note) in enumerate(rows):
        yy = y - r * 36
        kinds = [kind if i <= hit else "dim" for i in range(n)]
        kinds[hit] = "solid"
        p.cells(x0, yy, [""] * n, cw=cw, ch=15, kinds=kinds, index=False)
        p.text(x0 - 8, yy + 4, lab, 6.8, D.muted, SANS_SB, "r")
        p.text(x0, yy - 10, note, 6.7, D.muted, SANS_I, "l")
    p.text(p.w / 2, 6, "we quote the worst case, because it is the only promise",
           7.2, D.bad_bd, SANS_SB, "c")


@fig("bigo_space")
def bigo_space(p):
    """Three shapes of memory usage."""
    y = p.h - 40
    # O(1)
    p.text(0, y + 22, "O(1) AUXILIARY", 7.4, D.ok_bd, SANS_SB, "l")
    p.cells(0, y, [""] * 10, cw=11, ch=13, kinds=["dim"] * 10, index=False)
    p.text(0, y - 11, "input, n elements", 6.3, D.faint, SANS_I, "l")
    p.box(0, y - 42, 24, 16, "best", "ok", size=6.4, radius=1.5)
    p.box(27, y - 42, 24, 16, "i", "ok", size=6.4, radius=1.5)
    p.text(0, y - 54, "2 variables, whatever n is", 6.5, D.ok_bd, SANS, "l")

    # O(n) array
    x1 = 148
    p.text(x1, y + 22, "O(n) AUXILIARY", 7.4, D.hi_bd, SANS_SB, "l")
    p.cells(x1, y, [""] * 10, cw=11, ch=13, kinds=["dim"] * 10, index=False)
    p.text(x1, y - 11, "input, n elements", 6.3, D.faint, SANS_I, "l")
    p.cells(x1, y - 42, [""] * 10, cw=11, ch=13, kinds=["hi"] * 10, index=False)
    p.text(x1, y - 54, "a second array of n", 6.5, D.hi_bd, SANS, "l")

    # O(n) recursion
    x2 = 290
    p.text(x2, y + 22, "O(n) FROM RECURSION", 7.4, D.violet_bd, SANS_SB, "l")
    for i in range(5):
        p.box(x2 + i * 3.5, y - 4 - i * 11, 72, 10, None, "violet", radius=1,
              lw=0.5)
        p.text(x2 + i * 3.5 + 5, y - 4 - i * 11 + 2.5,
               "sumTo(%d)" % (5 - i), 5.8, D.ink, MONO, "l")
    p.text(x2, y - 66, "n pending call frames,", 6.5, D.violet_bd, SANS, "l")
    p.text(x2, y - 75, "though no array exists", 6.5, D.violet_bd, SANS, "l")
