"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("segment_tree")
def segment_tree(p):
    """A segment tree: each node owns a range; a query touches O(log n) nodes."""
    vals = [5, 8, 6, 3, 2, 7, 9, 1]
    n = len(vals)
    cw = 30
    top = p.h - 36
    p.text(0, p.h - 10, "query sum(0..6) = 22 + 9 + 9 \u2014 three nodes, not "
           "seven cells", 7.4, D.ok_bd, SANS_SB, "l")
    levels = [
        [(0, 7, 41)],
        [(0, 3, 22), (4, 7, 19)],
        [(0, 1, 13), (2, 3, 9), (4, 5, 9), (6, 7, 10)],
    ]
    hot = {(0, 3), (4, 5)}
    y = top
    for level in levels:
        for lo, hi, total in level:
            x = lo * cw
            w = (hi - lo + 1) * cw - 4
            k = "ok" if (lo, hi) in hot else "dim"
            p.box(x, y, w, 17, str(total), k, size=7.0, radius=2)
        y -= 26
    p.cells(0, y - 4, vals, cw=cw, ch=18, size=7.0,
            kinds=["ok" if i == 6 else "" for i in range(n)])
    p.text(n * cw + 16, top + 4, "root covers 0..7", 6.8, D.muted, SANS, "l")
    p.text(n * cw + 16, top - 48, "leaves", 6.8, D.muted, SANS, "l")
    p.text(0, 4, "Every node stores the aggregate of its range. Update a leaf "
           "\u2192 fix \u0398(log n) ancestors.", 7.0, D.muted, SANS_I, "l")


@fig("fenwick")
def fenwick(p):
    """A Fenwick tree: index i covers a range whose length is its lowest set bit."""
    n = 8
    cw = 40
    y = p.h - 30
    cover = {1: (1, 1), 2: (1, 2), 3: (3, 3), 4: (1, 4), 5: (5, 5),
             6: (5, 6), 7: (7, 7), 8: (1, 8)}
    p.text(0, p.h - 12, "tree[i] stores the sum of a range ending at i", 7.2,
           D.muted, SANS_SB, "l")
    for i in range(1, n + 1):
        x = (i - 1) * cw
        p.box(x, y, cw - 3, 16, str(i), "teal", size=7.0, radius=1.5)
    rows = [8, 4, 2, 6, 1, 3, 5, 7]
    for slot, i in enumerate(rows):
        lo, hi = cover[i]
        yy = y - 13 - slot * 8
        p.c.saveState()
        p.c.setFillColor(D.hi)
        p.c.setStrokeColor(D.hi_bd)
        p.c.setLineWidth(0.45)
        p.c.roundRect((lo - 1) * cw + 1, yy, (hi - lo + 1) * cw - 5, 5.6, 1.6,
                      stroke=1, fill=1)
        p.c.restoreState()
        p.text(n * cw + 6, yy - 0.6, "tree[%d]" % i, 5.8, D.muted, MONO, "l")
    ylow = y - 13 - 8 * 8
    p.text(0, ylow - 12, "prefix_sum(i):  i -= i & -i          "
           "update(i):  i += i & -i", 7.4, D.ink, MONO, "l")
    p.text(0, ylow - 24, "Both walk \u0398(log n) indices. One flat array, no "
           "pointers, half the memory of a segment tree.", 7.0, D.muted,
           SANS_I, "l")


@fig("bloom_filter")
def bloom_filter(p):
    """Bloom filter: k hashes set k bits; absence is certain, presence is not."""
    m = 20
    cw = 17
    bits = [0] * m
    for i in (2, 5, 9, 11, 14, 17):
        bits[i] = 1
    y = p.h - 46
    p.text(0, y + 26, "BIT ARRAY (m bits)", 7.0, D.muted, SANS_SB, "l")
    for i in range(m):
        p.box(i * cw, y, cw - 1.4, 17, str(bits[i]), "teal" if bits[i] else "dim",
              size=6.6, radius=1, font=MONO)
    p.text(0, y - 20, "insert(‘cat’): set bits h₁, h₂, h₃",
           7.0, D.teal_bd, SANS, "l")
    for i in (2, 9, 14):
        p.arrow(i * cw + 8, y - 12, i * cw + 8, y - 2, D.teal_bd, 0.8, head=2.8)
    y2 = y - 52
    p.text(0, y2 + 14, "query(‘dog’): any 0 bit → definitely absent",
           7.0, D.ok_bd, SANS_SB, "l")
    p.text(0, y2 + 2, "query(‘emu’): all bits set → probably present "
           "(may be a false positive)", 7.0, D.bad_bd, SANS_SB, "l")
    p.text(0, y2 - 16, "false positive rate ≈ (1 − e^(−kn/m))^k, "
           "minimised at k = (m/n) ln 2", 7.2, D.ink, SANS, "l")
    p.text(0, y2 - 28, "→ about 10 bits per element for a 1% error rate, "
           "whatever the element size", 7.2, D.node_bd, SANS_SB, "l")


@fig("count_min")
def count_min(p):
    """Count-Min sketch: d rows, take the minimum to cancel collisions."""
    d, w = 4, 10
    cw, ch = 24, 16
    x0 = 44
    y0 = p.h - 20
    counts = [[3, 0, 7, 1, 0, 4, 2, 0, 5, 1],
              [0, 6, 2, 0, 9, 1, 3, 0, 0, 4],
              [5, 1, 0, 3, 2, 0, 8, 1, 0, 6],
              [2, 0, 4, 0, 1, 7, 0, 3, 5, 0]]
    hit = [2, 4, 6, 5]
    for r in range(d):
        p.text(x0 - 6, y0 - (r + 1) * ch + 4, "h%d" % (r + 1), 6.6, D.muted,
               SANS, "r")
        for c in range(w):
            k = "hi" if hit[r] == c else "dim"
            p.box(x0 + c * cw, y0 - (r + 1) * ch, cw - 1.4, ch - 1.4,
                  str(counts[r][c]), k, size=6.4, radius=0.8)
    p.text(x0 + w * cw + 12, y0 - 2.5 * ch, "estimate = min(7, 9, 8, 7) = 7",
           7.2, D.ink, SANS_SB, "l")
    p.text(x0 + w * cw + 12, y0 - 3.5 * ch, "never underestimates;", 7.0,
           D.muted, SANS, "l")
    p.text(x0 + w * cw + 12, y0 - 4.2 * ch, "overestimates with prob. δ",
           7.0, D.muted, SANS, "l")
    p.text(0, 6, "w = ⌈e/ε⌉, d = ⌈ln(1/δ)⌉ gives "
           "error ≤ εN with probability 1 − δ, in Θ(wd) "
           "counters — independent of the number of distinct keys.",
           7.0, D.muted, SANS_I, "l")


@fig("minhash_lsh")
def minhash_lsh(p):
    """MinHash signatures, banded into buckets so similar docs collide."""
    y = p.h - 34
    p.text(0, y + 24, "SIGNATURE (one column per hash function)", 7.0, D.muted,
           SANS_SB, "l")
    sigs = {
        "doc A": [17, 3, 41, 8, 22, 9, 30, 12],
        "doc B": [17, 3, 41, 8, 91, 4, 30, 55],
        "doc C": [62, 77, 5, 19, 40, 2, 88, 6],
    }
    cw = 28
    for i, (name, sig) in enumerate(sigs.items()):
        yy = y - i * 20
        p.text(-4, yy + 4, name, 7.0, D.ink, SANS_SB, "r")
        for j, v in enumerate(sig):
            same = (name != "doc C" and j < 4)
            p.box(44 + j * cw, yy, cw - 2, 16, str(v),
                  "ok" if same else "dim", size=6.4, radius=1)
    for b in range(4):
        x = 44 + b * 2 * cw
        p.brace(x, x + 2 * cw - 4, y - 2 * 20 - 6, "band %d" % (b + 1))
    p.text(0, y - 86, "Two documents land in the same bucket if ANY band "
           "matches entirely.", 7.2, D.ink, SANS, "l")
    p.text(0, y - 98, "P(candidate) = 1 − (1 − s^r)^b  — an S-curve "
           "whose threshold is about (1/b)^(1/r).", 7.2, D.node_bd, SANS_SB, "l")


@fig("lsm_vs_btree")
def lsm_vs_btree(p):
    """Write path: update in place versus append and compact."""
    rx = 244
    p.text(0, p.h - 9, "B-TREE \u2014 update in place", 7.4, D.node_bd,
           SANS_SB, "l")
    p.box(62, p.h - 42, 66, 17, "root", "", size=7.0, radius=2)
    for i in range(3):
        x = 10 + i * 78
        p.box(x, p.h - 74, 66, 17, "leaf page", "hi" if i == 1 else "dim",
              size=7.0, radius=2)
        p.line(95, p.h - 42, x + 33, p.h - 57, D.arrow, 0.6)
    p.text(rx, p.h - 24, "one random write per update", 7.0, D.bad_bd, SANS, "l")
    p.text(rx, p.h - 38, "reads: one page, \u0398(log_B n)", 7.0, D.ok_bd,
           SANS, "l")
    p.text(rx, p.h - 52, "space amplification: low", 7.0, D.muted, SANS, "l")
    p.line(0, p.h - 88, p.w, p.h - 88, D.dim_bd, 0.5)

    p.text(0, 76, "LSM TREE \u2014 append, then compact", 7.4, D.violet_bd,
           SANS_SB, "l")
    p.box(0, 50, 58, 17, "memtable", "violet", size=6.8, radius=2)
    p.arrow(29, 48, 29, 36, D.arrow, 0.8, head=3)
    x = 0
    for lab, w, k in [("L0", 42, "violet"), ("L1", 62, "dim"),
                      ("L2", 96, "dim")]:
        p.box(x, 18, w, 16, lab, k, size=6.8, radius=2)
        if x:
            p.arrow(x - 7, 26, x - 1, 26, D.arrow, 0.7, head=2.6)
        x += w + 9
    p.text(x + 2, 22, "compaction merges downward", 6.8, D.muted, SANS, "l")
    p.text(rx, 62, "sequential writes only", 7.0, D.ok_bd, SANS, "l")
    p.text(rx, 48, "reads may touch every level", 7.0, D.bad_bd, SANS, "l")
    p.text(rx, 34, "\u2192 a Bloom filter per SSTable", 7.0, D.node_bd,
           SANS_SB, "l")
    p.text(0, 2, "Write-heavy \u2192 LSM. Read-heavy with range scans "
           "\u2192 B-tree.", 7.0, D.muted, SANS_I, "l")


@fig("suffix_array")
def suffix_array(p):
    """The suffix array plus LCP array: substring search by binary search."""
    s = "banana$"
    sufs = sorted(range(len(s)), key=lambda i: s[i:])
    lcp = [0]
    for a, b in zip(sufs, sufs[1:]):
        k = 0
        while a + k < len(s) and b + k < len(s) and s[a + k] == s[b + k]:
            k += 1
        lcp.append(k)
    y = p.h - 22
    p.text(0, y + 12, "TEXT:  b a n a n a $", 7.4, D.ink, MONO, "l")
    p.text(150, y + 12, "i", 6.6, D.faint, SANS_SB, "l")
    p.text(176, y + 12, "suffix", 6.6, D.faint, SANS_SB, "l")
    p.text(272, y + 12, "SA[i]", 6.6, D.faint, SANS_SB, "l")
    p.text(320, y + 12, "LCP", 6.6, D.faint, SANS_SB, "l")
    p.line(146, y + 7, p.w, y + 7, D.faint, 0.5)
    for i, (suf, l) in enumerate(zip(sufs, lcp)):
        yy = y - i * 13
        hot = s[suf:].startswith("ana")
        p.text(152, yy, str(i), 6.6, D.muted, MONO, "l")
        p.text(176, yy, s[suf:], 6.8, D.ok_bd if hot else D.ink, MONO, "l")
        p.text(280, yy, str(suf), 6.6, D.muted, MONO, "l")
        p.text(326, yy, str(l), 6.6, D.muted, MONO, "l")
    p.text(0, y - 24, "Suffixes are sorted, so every", 7.0, D.ink, SANS, "l")
    p.text(0, y - 36, "occurrence of a pattern is a", 7.0, D.ink, SANS, "l")
    p.text(0, y - 48, "contiguous run: two binary", 7.0, D.ink, SANS, "l")
    p.text(0, y - 60, "searches, Θ(m log n).", 7.0, D.node_bd, SANS_SB, "l")
    p.text(0, y - 80, "LCP[i] = shared prefix with", 7.0, D.muted, SANS, "l")
    p.text(0, y - 92, "the previous suffix — gives", 7.0, D.muted, SANS, "l")
    p.text(0, y - 104, "longest repeats for free.", 7.0, D.muted, SANS, "l")
