"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


BAL = (50, (30, (20, 10, 25), (40, 35, 45)), (70, (60, 55, 65), (80, 75, 90)))


@fig("bst_shapes")
def bst_shapes(p):
    """The same keys, two shapes: balance is the whole story."""
    p.text(0, p.h - 8, "BALANCED — depth 3, 15 nodes, Θ(log n) search",
           7.4, D.ok_bd, SANS_SB, "l")
    p.tree(BAL, 118, p.h - 28, level_h=28, gap=17, r=8.5, size=6.4,
           node_kind_fn=lambda v: "ok" if v in (50, 70, 80, 90) else "")
    p.text(0, p.h - 142, "search for 90: 4 comparisons", 6.8, D.muted, SANS_I, "l")

    x0 = 262
    p.text(x0 - 30, p.h - 8, "DEGENERATE \u2014 depth 7, \u0398(n) search", 7.4,
           D.bad_bd, SANS_SB, "l")
    node = 90
    for v in (80, 70, 60, 50, 40, 30, 20):
        node = (v, None, node)
    p.tree(node, x0 + 42, p.h - 28, level_h=13, gap=13, r=6.8, size=5.8,
           node_kind_fn=lambda v: "bad")
    p.text(p.w, 6, "insert 20, 30, 40, \u2026 in sorted order and you get a "
           "linked list with extra steps", 6.9, D.bad_bd, SANS_I, "r")


@fig("rotation")
def rotation(p):
    """A right rotation: O(1) pointers, and the in-order sequence is preserved."""
    left = ("y", ("x", "A", "B"), "C")
    right = ("x", "A", ("y", "B", "C"))
    p.text(60, p.h - 6, "before", 7.2, D.muted, SANS_SB, "c")
    p.tree(left, 60, p.h - 22, level_h=30, gap=26, r=10, size=7.4,
           node_kind_fn=lambda v: "hi" if v in ("x", "y") else "dim")
    p.arrow(140, p.h - 56, 196, p.h - 56, D.node_bd, 1.2, head=4.2)
    p.text(168, p.h - 50, "rotate right at y", 6.8, D.node_bd, SANS_SB, "c")
    p.text(272, p.h - 6, "after", 7.2, D.muted, SANS_SB, "c")
    p.tree(right, 272, p.h - 22, level_h=30, gap=26, r=10, size=7.4,
           node_kind_fn=lambda v: "hi" if v in ("x", "y") else "dim")
    p.text(0, 6, "In-order traversal is A x B y C on both sides — rotation "
           "changes the shape, never the order.", 7.2, D.muted, SANS_I, "l")


@fig("btree_node")
def btree_node(p):
    """A B-tree node is sized to a disk page, so depth stays at 3-4."""
    y = p.h - 40
    keys = ["17", "35", "61", "82"]
    kw, pw = 32, 13
    total = 5 * pw + 4 * kw
    x0 = 18
    p.text(0, y + 26, "ONE B-TREE NODE (order 5) \u2014 one disk page",
           7.2, D.muted, SANS_SB, "l")
    p.box(x0 - 4, y - 4, total + 8, 26, None, "white", radius=3, lw=0.9)
    x = x0
    ptr_x = []
    for i in range(5):
        p.box(x, y, pw, 18, None, "dim", radius=1.5, lw=0.5)
        ptr_x.append(x + pw / 2)
        x += pw
        if i < 4:
            p.box(x, y, kw, 18, keys[i], "teal", size=7.2, radius=1.5)
            x += kw
    ranges = ["< 17", "17\u201335", "35\u201361", "61\u201382", "> 82"]
    for cx, rg in zip(ptr_x, ranges):
        p.arrow(cx, y - 5, cx, y - 18, D.arrow, 0.7, head=2.8)
        p.text(cx, y - 28, rg, 6.4, D.muted, SANS, "c")
    p.text(x0 + total + 14, y + 4, "up to 5 children", 7.0, D.muted, SANS, "l")

    rows = [("binary search tree", "1", "~30", "30 disk reads"),
            ("B-tree, 4 KB pages", "~200", "3", "3 disk reads"),
            ("B-tree, 16 KB pages", "~800", "2\u20133", "2\u20133 disk reads")]
    y2 = 34
    p.text(0, y2 + 14, "structure", 6.6, D.faint, SANS_SB, "l")
    p.text(130, y2 + 14, "keys/node", 6.6, D.faint, SANS_SB, "l")
    p.text(200, y2 + 14, "depth at 10\u2079 keys", 6.6, D.faint, SANS_SB, "l")
    p.text(p.w, y2 + 14, "cost of one lookup", 6.6, D.faint, SANS_SB, "r")
    p.line(0, y2 + 9, p.w, y2 + 9, D.faint, 0.5)
    for i, (a, b, c, d) in enumerate(rows):
        yy = y2 - i * 13
        p.text(0, yy, a, 7.0, D.ink, SANS, "l")
        p.text(130, yy, b, 7.0, D.muted, MONO, "l")
        p.text(200, yy, c, 7.0, D.muted, MONO, "l")
        p.text(p.w, yy, d, 7.0, D.bad_bd if i == 0 else D.ok_bd, SANS_SB, "r")


@fig("heap_array")
def heap_array(p):
    """A heap is a complete tree, and a complete tree is an array."""
    vals = [2, 5, 4, 9, 7, 8, 6, 12, 10]
    heap = (2, (5, (9, 12, 10), 7), (4, 8, 6))
    p.tree(heap, 116, p.h - 18, level_h=27, gap=24, r=9, size=6.8,
           node_kind_fn=lambda v: "teal" if v == 2 else "")
    p.text(0, p.h - 8, "heap-ordered tree", 7.0, D.muted, SANS_SB, "l")

    y = 26
    cw = 30
    p.text(0, y + 32, "the same thing, as an array", 7.0, D.muted, SANS_SB, "l")
    p.cells(0, y, vals, cw=cw, ch=19, size=7.0,
            kinds=["teal"] + [""] * 8)
    p.text(0, y - 24, "parent(i) = (i−1)//2      left(i) = 2i+1      "
           "right(i) = 2i+2", 7.2, D.node_bd, MONO, "l")
    p.text(0, y - 36, "No pointers, perfect cache locality, and the root "
           "— the minimum — is always at index 0.", 7.0, D.muted,
           SANS_I, "l")


@fig("topk_stream")
def topk_stream(p):
    """Top-k over a stream with a bounded min-heap."""
    y = p.h - 30
    p.text(0, y + 22, "STREAM", 7.0, D.muted, SANS_SB, "l")
    stream = [0.31, 0.88, 0.12, 0.95, 0.44, 0.71, 0.09, 0.63]
    for i, v in enumerate(stream):
        p.box(i * 34, y, 32, 17, "%.2f" % v, "dim" if i > 3 else "teal",
              size=6.6, radius=1)
    p.arrow(4 * 34 + 14, y - 6, 4 * 34 + 14, y - 22, D.hi_bd, 0.9, head=3.2)

    x0 = 0
    y2 = y - 58
    p.text(x0, y2 + 26, "MIN-HEAP OF SIZE k = 3", 7.0, D.hi_bd, SANS_SB, "l")
    p.tree((0.44, 0.88, 0.95), 62, y2 + 14, level_h=26, gap=44, r=13, size=6.4,
           node_kind_fn=lambda v: "hi" if v == 0.44 else "")
    p.text(140, y2 + 6, "root = smallest kept score", 7.0, D.muted, SANS, "l")
    p.text(140, y2 - 6, "next item ≥ root ?  replace root, sift down "
           "— Θ(log k)", 7.0, D.ink, SANS, "l")
    p.text(140, y2 - 18, "next item < root ?  discard — Θ(1)", 7.0,
           D.ink, SANS, "l")
    p.text(0, 4, "Θ(n log k) time and Θ(k) memory, and it never needs "
           "the whole stream in memory.", 7.2, D.muted, SANS_I, "l")


@fig("trie_structure")
def trie_structure(p):
    """A trie shares prefixes; lookup cost depends on key length, not count."""
    col = 40
    top = p.h - 22
    bot = p.h - 74
    nodes = {
        "root": (16, (top + bot) / 2),
        "c": (16 + col, top), "ca": (16 + 2 * col, top),
        "cat": (16 + 3 * col, top), "cats": (16 + 4 * col, top),
        "d": (16 + col, bot), "do": (16 + 2 * col, bot),
        "dog": (16 + 3 * col, bot), "dogs": (16 + 4 * col, bot),
    }
    edges = [("root", "c"), ("c", "ca"), ("ca", "cat"), ("cat", "cats"),
             ("root", "d"), ("d", "do"), ("do", "dog"), ("dog", "dogs")]
    for a, b in edges:
        ax, ay = nodes[a]
        bx, by = nodes[b]
        p.arrow(ax, ay, bx, by, D.arrow, 0.7, head=2.8, shrink=9.5,
                label=b[-1], label_off=5.5)
    terminal = {"cat", "cats", "dog", "dogs"}
    for k, (x, y) in nodes.items():
        p.circle(x, y, 8.5, "" if k == "root" else k[-1],
                 "ok" if k in terminal else "", size=7.0)
    p.text(16, (top + bot) / 2 - 17, "root", 6.4, D.muted, SANS, "c")
    p.text(nodes["cat"][0], top + 14, "\u2018cat\u2019", 6.6, D.ok_bd, SANS_SB, "c")
    p.text(nodes["cats"][0], top + 14, "\u2018cats\u2019", 6.6, D.ok_bd, SANS_SB, "c")
    p.text(nodes["dog"][0], bot - 18, "\u2018dog\u2019", 6.6, D.ok_bd, SANS_SB, "c")
    p.text(nodes["dogs"][0], bot - 18, "\u2018dogs\u2019", 6.6, D.ok_bd, SANS_SB, "c")

    x0 = 232
    lines = [
        ("insert(word)", "\u0398(|word|)"),
        ("lookup(word)", "\u0398(|word|)"),
        ("all words with prefix P", "\u0398(|P| + output)"),
        ("longest prefix of S in the set", "\u0398(|S|)"),
        ("memory", "prefixes shared"),
    ]
    y = p.h - 12
    for a, b in lines:
        p.text(x0, y, a, 7.0, D.ink, SANS, "l")
        p.text(p.w, y, b, 6.9, D.node_bd, SANS_SB, "r")
        y -= 14
    p.text(x0, y - 4, "Nothing here depends on how many words the trie holds.",
           6.9, D.muted, SANS_I, "l")
    p.text(x0, y - 15, "That is the property a hash table cannot give you.",
           6.9, D.muted, SANS_I, "l")


@fig("union_find")
def union_find(p):
    """Union by rank keeps trees shallow; path compression flattens them."""
    y = p.h - 22
    p.text(0, y + 14, "BEFORE find(7)", 7.2, D.muted, SANS_SB, "l")
    chain = [(1, 60), (3, 60), (5, 60), (7, 60)]
    for i, (v, _) in enumerate(chain):
        p.circle(28, y - i * 26, 9.5, str(v), "teal" if i == 0 else "", size=7.0)
        if i:
            p.arrow(28, y - i * 26 + 10, 28, y - (i - 1) * 26 - 10, D.arrow,
                    0.8, head=3)
    p.text(46, y - 3 * 26, "depth 3: find(7) walks 3 links", 6.8, D.muted,
           SANS, "l")

    x0 = 224
    p.text(x0 - 30, y + 14, "AFTER find(7) with path compression", 7.2,
           D.ok_bd, SANS_SB, "l")
    p.circle(x0, y, 10, "1", "ok", size=7.2)
    for i, v in enumerate([3, 5, 7]):
        cx = x0 - 34 + i * 34
        p.circle(cx, y - 34, 9.5, str(v), "ok", size=7.0)
        p.arrow(cx, y - 24, x0 - 3 + (i - 1) * 2, y - 11, D.ok_bd, 0.8, head=3)
    p.text(x0 - 34, y - 56, "every node on the path now points at the root",
           6.8, D.ok_bd, SANS, "l")
    p.text(x0 - 34, y - 68, "the next find is Θ(1)", 6.8, D.ok_bd, SANS_SB, "l")
    p.text(0, 4, "With union by rank and path compression, m operations cost "
           "Θ(m α(n)) — α(n) ≤ 4 for any n you will ever see.",
           7.2, D.muted, SANS_I, "l")


@fig("aho_corasick")
def aho_corasick(p):
    """Failure links turn a trie into an automaton that never backtracks."""
    nodes = {
        "root": (24, p.h - 46), "h": (74, p.h - 22), "he": (124, p.h - 22),
        "her": (174, p.h - 22), "s": (74, p.h - 70), "sh": (124, p.h - 70),
        "she": (174, p.h - 70),
    }
    edges = [("root", "h", "h"), ("h", "he", "e"), ("he", "her", "r"),
             ("root", "s", "s"), ("s", "sh", "h"), ("sh", "she", "e")]
    for a, b, lab in edges:
        ax, ay = nodes[a]
        bx, by = nodes[b]
        p.arrow(ax + 9, ay + (6 if by > ay else -6) * 0, bx - 9, by, D.arrow,
                0.8, head=3, label=lab, label_off=6)
    fails = [("sh", "h"), ("she", "he")]
    for a, b in fails:
        ax, ay = nodes[a]
        bx, by = nodes[b]
        p.curve(ax, ay + 9, bx, by - 9, bulge=-16, color=D.bad_bd, lw=0.8)
    for k, (x, y) in nodes.items():
        p.circle(x, y, 9, "" if k == "root" else k[-1],
                 "ok" if k in ("her", "she", "he") else "", size=7.0)
    p.text(24, p.h - 62, "root", 6.4, D.muted, SANS, "c")
    p.text(200, p.h - 22, "‘her’", 6.8, D.ok_bd, SANS_SB, "l")
    p.text(200, p.h - 70, "‘she’", 6.8, D.ok_bd, SANS_SB, "l")
    p.text(96, p.h - 96, "red = failure links", 6.8, D.bad_bd, SANS_SB, "l")

    x0 = 246
    y = p.h - 16
    for line in ["Build the trie of all patterns.",
                 "Add a failure link from each node to the",
                 "longest proper suffix that is also a node.",
                 "",
                 "Then one pass over the text finds every",
                 "occurrence of every pattern:",
                 "Θ(|text| + total pattern length + hits),",
                 "with no backtracking, ever."]:
        p.text(x0, y, line, 7.0, D.ink if not line.startswith("Θ") else D.node_bd,
               SANS if not line.startswith("Θ") else SANS_SB, "l")
        y -= 12
