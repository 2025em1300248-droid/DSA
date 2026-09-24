"""Figures."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("solving_flow")
def solving_flow(p):
    """The five-step loop, with the escape hatch that matters."""
    steps = [("1  RESTATE", "inputs, outputs,\nconstraints, edges"),
             ("2  EXAMPLE", "work one small case\nby hand"),
             ("3  BRUTE FORCE", "state it, give its\ncomplexity"),
             ("4  FIND THE WASTE", "what is recomputed?\nwhat is ordered?"),
             ("5  OPTIMISE", "pick the structure that\nremoves the waste")]
    n = len(steps)
    gap = 10
    w = (p.w - gap * (n - 1)) / n
    y = p.h - 62
    for i, (title, body) in enumerate(steps):
        x = i * (w + gap)
        p.box(x, y, w, 46, None, "teal" if i < 3 else "hi", radius=3)
        p.text(x + w / 2, y + 33, title, 7.2, D.ink, SANS_SB, "c")
        for j, ln in enumerate(body.split("\n")):
            p.text(x + w / 2, y + 20 - j * 9, ln, 6.5, D.muted, SANS, "c")
        if i < n - 1:
            p.arrow(x + w + 1, y + 23, x + w + gap - 1, y + 23, D.arrow, 0.8,
                    head=3)
    p.curve(p.w - w / 2, y - 3, w + gap + w / 2, y - 3, bulge=-15,
            color=D.bad_bd, lw=0.9)
    p.text(p.w / 2, y - 30, "stuck? go back to step 2 with a bigger example",
           6.9, D.bad_bd, SANS_SB, "c")
    p.text(0, 10, "Steps 1–3 are not optional warm-up. A stated brute force "
           "is a correct answer you can improve;", 7.0, D.muted, SANS_I, "l")
    p.text(0, 0, "a half-remembered clever answer is neither.", 7.0, D.muted,
           SANS_I, "l")


@fig("pattern_triggers")
def pattern_triggers(p):
    """From the words in the problem to the structure that solves it."""
    rows = [
        ("“top k”, “best so far”, “merge k streams”", "heap", "hi"),
        ("“contiguous” + “longest/shortest”", "sliding window", "teal"),
        ("“sorted” or “find the minimum x such that”", "binary search", "teal"),
        ("“all pairs” + “sorted”", "two pointers", "teal"),
        ("“how many ways”, “minimum cost to”", "dynamic programming", "violet"),
        ("“prefix”, “autocomplete”, “dictionary”", "trie", "hi"),
        ("“connected”, “groups”, “merge sets”", "union–find", "hi"),
        ("“shortest path” + weights", "Dijkstra / BFS", "violet"),
        ("“order with dependencies”", "topological sort", "violet"),
        ("“range sum” + updates", "Fenwick / segment tree", "ok"),
        ("“too big to store exactly”", "sketch (Bloom/CMS/HLL)", "ok"),
        ("“nearest” in high dimensions", "ANN index", "ok"),
    ]
    y = p.h - 12
    p.text(0, y, "PHRASE IN THE PROBLEM", 6.6, D.faint, SANS_SB, "l")
    p.text(228, y, "STRUCTURE TO REACH FOR", 6.6, D.faint, SANS_SB, "l")
    p.line(0, y - 5, p.w, y - 5, D.faint, 0.5)
    y -= 17
    for phrase, struct, kind in rows:
        fc = {"hi": D.hi, "teal": D.teal, "violet": D.violet, "ok": D.ok}[kind]
        sc = {"hi": D.hi_bd, "teal": D.teal_bd, "violet": D.violet_bd,
              "ok": D.ok_bd}[kind]
        p.c.saveState()
        p.c.setFillColor(fc)
        p.c.roundRect(-3, y - 4, p.w + 6, 14, 2, stroke=0, fill=1)
        p.c.restoreState()
        p.text(0, y, phrase, 7.0, D.ink, SANS, "l")
        p.text(228, y, struct, 7.0, sc, SANS_SB, "l")
        y -= 17


@fig("study_plan")
def study_plan(p):
    """Sixteen weeks, and what each block buys you."""
    blocks = [("Weeks 1–3", "Foundations", "Ch 1–5", 0.19, "teal"),
              ("Weeks 4–6", "Core toolkit", "Ch 6–11", 0.19, "teal"),
              ("Weeks 7–8", "Trees & heaps", "Ch 12–15", 0.12, "ok"),
              ("Weeks 9–11", "Paradigms", "Ch 16–21", 0.19, "hi"),
              ("Weeks 12–13", "Graphs", "Ch 22–26", 0.12, "hi"),
              ("Weeks 14–16", "ML-native + practice", "Ch 27–47", 0.19, "violet")]
    x = 0
    y = p.h - 48
    for label, name, chapters, frac, kind in blocks:
        w = (p.w - 5 * 6) * frac
        p.box(x, y, w, 34, None, kind, radius=3)
        p.text(x + w / 2, y + 22, name, 7.2, D.ink, SANS_SB, "c")
        p.text(x + w / 2, y + 12, chapters, 6.4, D.muted, SANS, "c")
        p.text(x + w / 2, y - 10, label, 6.6, D.muted, SANS_SB, "c")
        x += w + 6
    p.text(0, p.h - 10, "A 16-WEEK PLAN AT 4–6 HOURS PER WEEK", 7.2,
           D.muted, SANS_SB, "l")
    p.text(0, 22, "Half the time on the keyboard. Every chapter: read, "
           "implement one structure from memory, do three exercises.", 7.0,
           D.ink, SANS, "l")
    p.text(0, 10, "Interview sprint (6 weeks): Ch 2, 4, 6–13, 16–20, "
           "22–24, then Part IX.", 7.0, D.muted, SANS_I, "l")
    p.text(0, -2, "Reference use: Ch 2 and 3 once, properly; then jump to "
           "whatever you are fighting.", 7.0, D.muted, SANS_I, "l")
