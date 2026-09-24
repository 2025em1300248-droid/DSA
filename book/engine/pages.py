"""Cover, title page, part dividers and chapter openers."""
import math
import random

from reportlab.lib.colors import HexColor
from reportlab.platypus import (Flowable, KeepTogether, NextPageTemplate,
                                PageBreak, Paragraph, Spacer, Table, TableStyle)

from .draw import D, Figure, Pen
from .flowables import Anchor, HRule, RunningState, callout
from .markup import inline, plain
from .style import (C, FRAME_H, FRAME_W, MARGIN_B, MARGIN_L, MARGIN_R,
                    MARGIN_T, MONO, PAGE_H, PAGE_W, SANS, SANS_B, SANS_BLK,
                    SANS_LT, SANS_SB, SERIF, SERIF_I, SERIF_LT, styles)

NAVY = HexColor("#0E2338")
NAVY2 = HexColor("#16466E")
GOLD = HexColor("#E0A458")
MINT = HexColor("#6FD3C7")
LILAC = HexColor("#B49BE0")
PAPER = HexColor("#FFFFFF")


class FullBleed(Flowable):
    """A flowable that paints the entire page, ignoring the frame."""

    def __init__(self, fn):
        Flowable.__init__(self)
        self.fn = fn
        self.width, self.height = 1, 1

    def wrap(self, aw, ah):
        return (1, 1)

    def draw(self):
        c = self.canv
        c.saveState()
        x, y = self.canv.absolutePosition(0, 0)
        c.translate(-x, -y)
        self.fn(Pen(c, PAGE_W, PAGE_H))
        c.restoreState()


# --------------------------------------------------------------------------
# Cover
# --------------------------------------------------------------------------
def draw_cover(p, title_lines, subtitle, kicker, author, edition):
    c = p.c
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # A faint constellation: a graph whose nodes fall on a soft grid.
    rnd = random.Random(20260924)
    pts = []
    for i in range(34):
        x = rnd.uniform(24, PAGE_W - 24)
        y = rnd.uniform(PAGE_H * 0.46, PAGE_H - 30)
        pts.append((x, y))
    c.setLineWidth(0.4)
    for i, (x1, y1) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            x2, y2 = pts[j]
            d = math.hypot(x2 - x1, y2 - y1)
            if d < 96:
                c.setStrokeColor(HexColor("#1D4A72"))
                c.setLineWidth(0.35 * (1 - d / 96) + 0.12)
                c.line(x1, y1, x2, y2)
    for i, (x, y) in enumerate(pts):
        c.setFillColor(MINT if i % 7 == 0 else HexColor("#2B5F8C"))
        c.circle(x, y, 1.7 if i % 7 else 2.6, stroke=0, fill=1)

    # Binary-tree motif, bottom right, very faint.
    c.saveState()
    c.setStrokeColor(HexColor("#17395A"))
    c.setFillColor(HexColor("#17395A"))
    def tri(x, y, w, depth):
        if depth == 0:
            return
        c.setLineWidth(0.5)
        c.line(x, y, x - w, y - 26)
        c.line(x, y, x + w, y - 26)
        c.circle(x, y, 2.2, stroke=0, fill=1)
        tri(x - w, y - 26, w / 2, depth - 1)
        tri(x + w, y - 26, w / 2, depth - 1)
    tri(PAGE_W - 92, 176, 52, 4)
    c.restoreState()

    # Accent rule
    c.setFillColor(GOLD)
    c.rect(MARGIN_L - 30, PAGE_H - 150, 54, 3.2, stroke=0, fill=1)

    x0 = MARGIN_L - 30
    p.text(x0, PAGE_H - 178, kicker, 9.4, HexColor("#9DC0DC"), SANS_SB, "l")

    y = PAGE_H - 232
    for i, line in enumerate(title_lines):
        p.text(x0, y, line, 40 if i == 0 else 40, PAPER, SANS_BLK, "l")
        y -= 45
    y -= 6
    c.setFillColor(MINT)
    c.rect(x0, y + 16, 28, 2.4, stroke=0, fill=1)
    y -= 12
    for line in subtitle:
        p.text(x0, y, line, 13.6, HexColor("#BBD3E6"), SERIF_LT, "l")
        y -= 20

    # Complexity ladder motif
    yy = 232
    ladder = [("O(1)", 0.10), ("O(log n)", 0.22), ("O(n)", 0.42),
              ("O(n log n)", 0.60), ("O(n²)", 0.80), ("O(2ⁿ)", 1.0)]
    for i, (lab, f) in enumerate(ladder):
        w = 150 * f + 16
        c.setFillColor(HexColor("#1B4468"))
        c.roundRect(x0, yy, w, 11, 2, stroke=0, fill=1)
        c.setFillColor(GOLD if f >= 0.8 else MINT if f <= 0.25 else HexColor("#5E9AC6"))
        c.roundRect(x0, yy, min(w, 10 + 140 * f), 11, 2, stroke=0, fill=1)
        p.text(x0 + w + 8, yy + 2.6, lab, 7.6, HexColor("#8FB3CE"), MONO, "l")
        yy -= 16

    p.text(x0, 104, author, 11.4, PAPER, SANS_SB, "l")
    p.text(x0, 88, edition, 8.6, HexColor("#7EA4C2"), SANS, "l")
    c.setStrokeColor(HexColor("#2B5F8C"))
    c.setLineWidth(0.6)
    c.line(x0, 74, PAGE_W - MARGIN_R + 30, 74)


def cover(title_lines, subtitle, kicker, author, edition):
    return [FullBleed(lambda p: draw_cover(p, title_lines, subtitle, kicker,
                                           author, edition))]


# --------------------------------------------------------------------------
# Part divider
# --------------------------------------------------------------------------
def draw_part(p, number, roman_num, title, blurb, chapters, motif):
    c = p.c
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(HexColor("#132D46"))
    c.rect(0, 0, PAGE_W, 250, stroke=0, fill=1)

    if motif:
        c.saveState()
        motif(p)
        c.restoreState()

    x0 = MARGIN_L - 30
    c.setFillColor(GOLD)
    c.rect(x0, PAGE_H - 214, 46, 3, stroke=0, fill=1)
    p.text(x0, PAGE_H - 244, "PART %s" % roman_num, 10.6, MINT, SANS_SB, "l")

    y = PAGE_H - 300
    for line in title:
        p.text(x0, y, line, 32, PAPER, SANS_BLK, "l")
        y -= 38

    y -= 4
    for line in blurb:
        p.text(x0, y, line, 11.2, HexColor("#B7D0E4"), SERIF_LT, "l")
        y -= 17

    y -= 26
    c.setStrokeColor(HexColor("#2B5F8C"))
    c.setLineWidth(0.6)
    c.line(x0, y + 12, PAGE_W - MARGIN_R + 30, y + 12)
    y -= 8
    for num, name in chapters:
        p.text(x0, y, "%02d" % num, 9.4, GOLD, MONO, "l")
        p.text(x0 + 26, y, name, 10.2, HexColor("#D6E5F1"), SANS, "l")
        y -= 17.5


def part_page(number, roman_num, title_lines, blurb_lines, chapters, motif=None):
    key = "part-%d" % number
    return [
        RunningState(part="PART %s · %s" % (roman_num, " ".join(title_lines)),
                     chapter="", short=""),
        Anchor(0, "Part %s — %s" % (roman_num, " ".join(title_lines)), key),
        FullBleed(lambda p: draw_part(p, number, roman_num, title_lines,
                                      blurb_lines, chapters, motif)),
    ]


# --------------------------------------------------------------------------
# Chapter opener
# --------------------------------------------------------------------------
class OpenerArt(Flowable):
    def __init__(self, number, tier):
        Flowable.__init__(self)
        self.number = number
        self.tier = tier
        self.width, self.height = FRAME_W, 86

    def wrap(self, aw, ah):
        return (FRAME_W, 86)

    def draw(self):
        c = self.canv
        p = Pen(c, FRAME_W, 86)
        c.saveState()
        c.setFillColor(C.primary_lt)
        c.roundRect(FRAME_W - 96, 6, 96, 74, 4, stroke=0, fill=1)
        c.setFillColor(C.primary)
        c.setFont(SANS_BLK, 46)
        c.drawCentredString(FRAME_W - 48, 28, "%02d" % self.number)
        c.setFont(SANS_SB, 7.2)
        c.setFillColor(C.primary)
        c.drawCentredString(FRAME_W - 48, 66, "CHAPTER")
        c.restoreState()


TIERS = {
    "foundation": ("FOUNDATION", C.teal, C.teal_lt),
    "core": ("CORE", C.primary, C.primary_lt),
    "advanced": ("ADVANCED", C.violet, C.violet_lt),
    "expert": ("FRONTIER", C.crimson, C.crimson_lt),
    "practice": ("PRACTICE", C.green, C.green_lt),
    "reference": ("REFERENCE", C.slate, C.slate_lt),
}


class Chips(Flowable):
    def __init__(self, chips, width=None):
        Flowable.__init__(self)
        self.chips = chips
        self.width = width or FRAME_W
        self.height = 15

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        p = Pen(self.canv, self.width, self.height)
        x = 0
        for text, kind in self.chips:
            x += p.label_chip(x, 1.5, text, kind) + 5

    
def chapter_opener(number, title, subtitle=None, blurb=None, objectives=None,
                   tier="core", prereq=None, key=None):
    ss = styles()
    key = key or "ch-%d" % number
    label, fg, bg = TIERS.get(tier, TIERS["core"])
    out = [
        NextPageTemplate("body"),
        RunningState(chapter=plain(title),
                     short="%d · %s" % (number, plain(title))),
        Anchor(1, "%d. %s" % (number, plain(title)), key),
        Spacer(0, 4),
        OpenerArt(number, tier),
        Spacer(0, 4),
    ]
    tstyle = ss["h1"].clone("h1c")
    out.append(Paragraph(inline(title), tstyle))
    if subtitle:
        st = ss["lead"].clone("sublead")
        st.fontName = SERIF_I
        st.textColor = C.muted
        st.spaceBefore = 5
        out.append(Paragraph(inline(subtitle), st))
    out.append(Spacer(0, 10))
    chips = [(label, "teal" if tier == "foundation" else
              "violet" if tier == "advanced" else
              "bad" if tier == "expert" else
              "ok" if tier == "practice" else "")]
    if prereq:
        chips.append(("PREREQS: " + prereq, "dim"))
    out.append(Chips(chips))
    out.append(Spacer(0, 6))
    out.append(HRule(color=C.rule, thickness=0.8, space_before=2, space_after=10))
    if blurb:
        out.append(Paragraph(inline(blurb), ss["lead"]))
        out.append(Spacer(0, 10))
    if objectives:
        items = [Paragraph(inline(o), ss["callout-bullet"], bulletText="•")
                 for o in objectives]
        spaced = []
        for it in items:
            spaced.append(it)
        out.append(callout("objectives", None, spaced))
        out.append(Spacer(0, 8))
    return out


# --------------------------------------------------------------------------
# Simple front-matter pages
# --------------------------------------------------------------------------
def title_page(title_lines, subtitle, author, edition, tagline):
    ss = styles()
    out = [Spacer(0, 110)]
    st = ss["h1"].clone("tp")
    st.fontSize = 30
    st.leading = 35
    for line in title_lines:
        out.append(Paragraph(line, st))
    out.append(Spacer(0, 14))
    sub = ss["lead"].clone("tps")
    sub.fontSize = 13
    sub.leading = 19
    sub.textColor = C.muted
    for line in subtitle:
        out.append(Paragraph(line, sub))
    out.append(Spacer(0, 26))
    out.append(HRule(width=110, color=C.primary, thickness=2.2, space_after=0))
    out.append(Spacer(0, 26))
    tg = ss["body"].clone("tg")
    tg.fontName = SERIF_I
    tg.fontSize = 11
    tg.leading = 16.5
    tg.textColor = C.slate
    out.append(Paragraph(inline(tagline), tg))
    out.append(Spacer(0, 150))
    au = ss["body"].clone("au")
    au.fontName = SANS_SB
    au.fontSize = 11
    au.textColor = C.ink
    out.append(Paragraph(author, au))
    ed = ss["body"].clone("ed")
    ed.fontName = SANS
    ed.fontSize = 8.6
    ed.textColor = C.muted
    out.append(Paragraph(edition, ed))
    return out
