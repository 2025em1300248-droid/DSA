"""Document template: page furniture, running heads, TOC and PDF outline."""
from reportlab.lib.colors import HexColor
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from .style import (C, FRAME_H, FRAME_W, MARGIN_B, MARGIN_L, MARGIN_R,
                    MARGIN_T, PAGE_H, PAGE_W, SANS, SANS_B, SANS_BLK, SANS_SB,
                    SERIF, SERIF_I, styles)
from .flowables import Anchor
from .markup import plain

ROMAN = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
         (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
         (5, "v"), (4, "iv"), (1, "i")]


def roman(n):
    out = []
    for v, s in ROMAN:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def track(s, size, spacing=1.0):
    return s


class BookDoc(BaseDocTemplate):
    def __init__(self, filename, title="", subtitle="", author="", **kw):
        self.book_title = title
        self.book_subtitle = subtitle
        self.book_author = author
        self.running = {"part": "", "chapter": "", "chapter_num": "",
                        "short": ""}
        self.arabic_start = kw.pop("arabic_start", 9)
        self._seen_arabic = None
        self.total_pages = None
        self.outline_stack = []
        BaseDocTemplate.__init__(self, filename, pagesize=(PAGE_W, PAGE_H),
                                 leftMargin=MARGIN_L, rightMargin=MARGIN_R,
                                 topMargin=MARGIN_T, bottomMargin=MARGIN_B,
                                 title=title, author=author,
                                 subject=subtitle, creator="dsa-for-ml book engine",
                                 **kw)
        def main(tag):
            return Frame(MARGIN_L, MARGIN_B, FRAME_W, FRAME_H, id=tag,
                         leftPadding=0, rightPadding=0, topPadding=0,
                         bottomPadding=0)

        def full(tag):
            return Frame(0, 0, PAGE_W, PAGE_H, id=tag, leftPadding=0,
                         rightPadding=0, topPadding=0, bottomPadding=0)

        self.addPageTemplates([
            PageTemplate(id="cover", frames=[full("c")], onPage=self._blank_page),
            PageTemplate(id="body", frames=[main("b")], onPage=self._body_page),
            PageTemplate(id="opener", frames=[main("o")], onPage=self._opener_page),
            PageTemplate(id="front", frames=[main("f")], onPage=self._front_page),
            PageTemplate(id="blank", frames=[full("z")], onPage=self._blank_page),
            PageTemplate(id="part", frames=[full("p")], onPage=self._part_page),
            PageTemplate(id="wide",
                         frames=[Frame(MARGIN_L - 6, MARGIN_B, FRAME_W + 12,
                                       FRAME_H, id="w", leftPadding=0,
                                       rightPadding=0, topPadding=0,
                                       bottomPadding=0)],
                         onPage=self._body_page),
        ])

    # -- page-number labels ----------------------------------------------
    def _label(self, physical):
        if physical < self.arabic_start:
            return roman(physical)
        return str(physical - self.arabic_start + 1)

    def mark_arabic_start(self, canv):
        self._seen_arabic = canv.getPageNumber()

    def finish_pass(self):
        if self._seen_arabic:
            self.arabic_start = self._seen_arabic
        self._seen_arabic = None

    # -- decoration -------------------------------------------------------
    def _prep(self, canv):
        canv._doc_ref = self

    def _folio(self, canv, muted=False):
        n = canv.getPageNumber()
        canv.saveState()
        canv.setFont(SANS, 8.4)
        canv.setFillColor(C.faint if muted else C.muted)
        canv.drawCentredString(PAGE_W / 2, MARGIN_B - 26, self._label(n))
        canv.restoreState()

    def _body_page(self, canv, doc):
        self._prep(canv)
        n = canv.getPageNumber()
        y = PAGE_H - MARGIN_T + 24
        canv.saveState()
        canv.setStrokeColor(C.hairline)
        canv.setLineWidth(0.5)
        canv.line(MARGIN_L, y - 5, PAGE_W - MARGIN_R, y - 5)
        canv.setFont(SANS, 7.4)
        canv.setFillColor(C.faint)
        left = self.running.get("part", "") or self.book_title
        right = self.running.get("short", "") or self.running.get("chapter", "")
        canv.drawString(MARGIN_L, y, _cap(left)[:64])
        canv.drawRightString(PAGE_W - MARGIN_R, y, _cap(right)[:70])
        canv.setFillColor(C.primary_md)
        canv.circle(MARGIN_L - 0.0, y - 5, 0, stroke=0, fill=1)
        canv.restoreState()
        self._folio(canv)

    def _opener_page(self, canv, doc):
        self._prep(canv)
        self._folio(canv, muted=True)

    def _front_page(self, canv, doc):
        self._prep(canv)
        self._folio(canv, muted=True)

    def _blank_page(self, canv, doc):
        self._prep(canv)

    def _part_page(self, canv, doc):
        self._prep(canv)

    def handle_documentBegin(self):
        self.running = {"part": "", "chapter": "", "chapter_num": "",
                        "short": ""}
        BaseDocTemplate.handle_documentBegin(self)

    # -- TOC / outline -----------------------------------------------------
    def afterFlowable(self, flowable):
        if isinstance(flowable, Anchor):
            txt = plain(flowable.text)
            key = flowable.key
            lvl = flowable.level
            if lvl >= 0:
                self.notify("TOCEntry", (lvl, txt, self.page, key))
            try:
                self.canv.addOutlineEntry(txt[:110], key.encode("utf-8"),
                                          max(0, lvl), 0)
            except Exception:
                pass


def _cap(s):
    return s


def make_toc(doc=None):
    ss = styles()
    toc = TableOfContents(formatter=(doc._label if doc else None))
    toc.levelStyles = [ss["toc0"], ss["toc1"], ss["toc2"], ss["toc3"]]
    toc.dotsMinLevel = 1
    return toc
