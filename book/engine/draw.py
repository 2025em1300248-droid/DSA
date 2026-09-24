"""
A small vector-drawing layer for figures.

Diagrams are written as plain functions that receive a `Canvas` helper with
primitives (boxes, arrows, cells, trees, plots) in a bottom-left origin
coordinate system. They render directly onto the PDF canvas, so they stay
crisp at any zoom and cost almost nothing in file size.
"""
import math
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import Flowable, KeepTogether, Paragraph

from .style import (C, FRAME_W, MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB,
                    SERIF, SERIF_I, styles)
from .markup import plain

# Palette for figures
class D:
    node      = HexColor("#EAF0F6")
    node_bd   = HexColor("#16466E")
    hi        = HexColor("#FBF1E2")
    hi_bd     = HexColor("#9A5B06")
    ok        = HexColor("#E9F4EC")
    ok_bd     = HexColor("#1F6134")
    bad       = HexColor("#FBEAEE")
    bad_bd    = HexColor("#9C1B3B")
    dim       = HexColor("#F3F5F8")
    dim_bd    = HexColor("#C2CAD6")
    teal      = HexColor("#E6F3F1")
    teal_bd   = HexColor("#0E6E63")
    violet    = HexColor("#F1EBF9")
    violet_bd = HexColor("#5B2E90")
    ink       = HexColor("#14161A")
    muted     = HexColor("#6A7180")
    faint     = HexColor("#AEB6C2")
    arrow     = HexColor("#4A5260")
    white     = HexColor("#FFFFFF")

PAL = {
    "": (D.node, D.node_bd), "n": (D.node, D.node_bd),
    "hi": (D.hi, D.hi_bd), "ok": (D.ok, D.ok_bd), "bad": (D.bad, D.bad_bd),
    "dim": (D.dim, D.dim_bd), "teal": (D.teal, D.teal_bd),
    "violet": (D.violet, D.violet_bd), "white": (D.white, D.dim_bd),
    "solid": (D.node_bd, D.node_bd), "ink": (D.ink, D.ink),
}


class Pen:
    """Drawing helper bound to a live PDF canvas."""

    def __init__(self, canv, w, h):
        self.c = canv
        self.w = w
        self.h = h

    # -- primitives -------------------------------------------------------
    def text(self, x, y, s, size=8, color=D.ink, font=SANS, anchor="c",
             rotate=0):
        c = self.c
        c.saveState()
        c.setFillColor(color)
        c.setFont(font, size)
        if rotate:
            c.translate(x, y)
            c.rotate(rotate)
            x = y = 0
        if anchor == "c":
            c.drawCentredString(x, y, s)
        elif anchor == "r":
            c.drawRightString(x, y, s)
        else:
            c.drawString(x, y, s)
        c.restoreState()

    def rich(self, x, y, s, size=8, color=D.ink, anchor="c", font=SANS):
        """Text with a trailing subscript after '_'."""
        if "_" not in s:
            return self.text(x, y, s, size, color, font, anchor)
        base, sub = s.split("_", 1)
        from reportlab.pdfbase.pdfmetrics import stringWidth
        wb = stringWidth(base, font, size)
        ws = stringWidth(sub, font, size * 0.72)
        total = wb + ws
        x0 = x - total / 2 if anchor == "c" else (x - total if anchor == "r" else x)
        self.text(x0, y, base, size, color, font, "l")
        self.text(x0 + wb, y - size * 0.22, sub, size * 0.72, color, font, "l")

    def box(self, x, y, w, h, label=None, kind="", size=8.2, radius=2.5,
            lw=0.9, font=SANS, label_color=None, dashed=False, fill=None,
            stroke=None, sub=None):
        fc, sc = PAL.get(kind, PAL[""])
        fc = fill if fill is not None else fc
        sc = stroke if stroke is not None else sc
        c = self.c
        c.saveState()
        c.setLineWidth(lw)
        c.setStrokeColor(sc)
        c.setFillColor(fc)
        if dashed:
            c.setDash(2.4, 2.2)
        if radius:
            c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
        else:
            c.rect(x, y, w, h, stroke=1, fill=1)
        c.restoreState()
        if label is not None:
            lc = label_color or (D.white if kind in ("solid", "ink") else D.ink)
            dy = 0 if sub is None else size * 0.42
            self.rich(x + w / 2, y + h / 2 - size * 0.34 + dy, label, size, lc, font=font)
            if sub is not None:
                self.text(x + w / 2, y + h / 2 - size * 1.18 + dy, sub,
                          size * 0.78, D.muted, SANS, "c")
        return (x + w / 2, y + h / 2)

    def circle(self, cx, cy, r, label=None, kind="", size=8.2, lw=0.9,
               font=SANS, label_color=None, dashed=False):
        fc, sc = PAL.get(kind, PAL[""])
        c = self.c
        c.saveState()
        c.setLineWidth(lw)
        c.setStrokeColor(sc)
        c.setFillColor(fc)
        if dashed:
            c.setDash(2.4, 2.2)
        c.circle(cx, cy, r, stroke=1, fill=1)
        c.restoreState()
        if label is not None:
            lc = label_color or (D.white if kind in ("solid", "ink") else D.ink)
            self.rich(cx, cy - size * 0.34, label, size, lc, font=font)
        return (cx, cy)

    def line(self, x1, y1, x2, y2, color=None, lw=0.8, dashed=False):
        c = self.c
        c.saveState()
        c.setStrokeColor(color or D.arrow)
        c.setLineWidth(lw)
        if dashed:
            c.setDash(2.4, 2.2)
        c.line(x1, y1, x2, y2)
        c.restoreState()

    def arrow(self, x1, y1, x2, y2, color=None, lw=0.9, head=3.6, dashed=False,
              label=None, label_size=7.2, label_off=4.5, shrink=0.0,
              label_color=None, both=False):
        color = color or D.arrow
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        if shrink:
            x1 += ux * shrink; y1 += uy * shrink
            x2 -= ux * shrink; y2 -= uy * shrink
            L = max(1.0, L - 2 * shrink)
        c = self.c
        c.saveState()
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(lw)
        if dashed:
            c.setDash(2.4, 2.2)
        c.line(x1, y1, x2 - ux * head * 0.7, y2 - uy * head * 0.7)
        c.setDash()
        self._head(x2, y2, ux, uy, head)
        if both:
            self._head(x1, y1, -ux, -uy, head)
        c.restoreState()
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            px, py = -uy, ux
            self.text(mx + px * label_off, my + py * label_off - 2.4, label,
                      label_size, label_color or D.muted, SANS, "c")

    def _head(self, x, y, ux, uy, head):
        c = self.c
        px, py = -uy, ux
        p = c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x - ux * head - px * head * 0.42, y - uy * head - py * head * 0.42)
        p.lineTo(x - ux * head + px * head * 0.42, y - uy * head + py * head * 0.42)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    def curve(self, x1, y1, x2, y2, bulge=18, color=None, lw=0.9, label=None,
              dashed=False, arrow=True, label_size=7.2):
        color = color or D.arrow
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        px, py = -dy / L, dx / L
        cx, cy = mx + px * bulge, my + py * bulge
        c = self.c
        c.saveState()
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(lw)
        if dashed:
            c.setDash(2.4, 2.2)
        p = c.beginPath()
        p.moveTo(x1, y1)
        p.curveTo(x1 + (cx - x1) * 0.75, y1 + (cy - y1) * 0.75,
                  x2 + (cx - x2) * 0.75, y2 + (cy - y2) * 0.75, x2, y2)
        c.drawPath(p, stroke=1, fill=0)
        c.setDash()
        if arrow:
            tx, ty = x2 - (cx - x2) * 0.25 - x2, y2 - (cy - y2) * 0.25 - y2
            n = math.hypot(x2 - cx, y2 - cy) or 1.0
            self._head(x2, y2, (x2 - cx) / n, (y2 - cy) / n, 3.6)
        c.restoreState()
        if label:
            self.text(cx + px * 3, cy + py * 3 - 2, label, label_size, D.muted,
                      SANS, "c")

    def brace(self, x1, x2, y, label=None, up=False, color=None, size=7.2):
        color = color or D.faint
        d = 4.0 if up else -4.0
        c = self.c
        c.saveState()
        c.setStrokeColor(color)
        c.setLineWidth(0.7)
        c.line(x1, y, x1, y + d)
        c.line(x2, y, x2, y + d)
        c.line(x1, y + d, x2, y + d)
        c.restoreState()
        if label:
            self.text((x1 + x2) / 2, y + d + (2.5 if up else -8.0), label,
                      size, D.muted, SANS, "c")

    def bar(self, x, y, w, h, frac, kind="", label=None):
        fc, sc = PAL.get(kind, PAL[""])
        c = self.c
        c.saveState()
        c.setFillColor(D.dim)
        c.setStrokeColor(D.dim_bd)
        c.setLineWidth(0.5)
        c.roundRect(x, y, w, h, 1.6, stroke=1, fill=1)
        c.setFillColor(sc)
        c.setStrokeColor(sc)
        if frac > 0:
            c.roundRect(x, y, max(2.0, w * frac), h, 1.6, stroke=0, fill=1)
        c.restoreState()
        if label:
            self.text(x + w + 5, y + h / 2 - 2.5, label, 7.2, D.muted, SANS, "l")

    # -- composites -------------------------------------------------------
    def cells(self, x, y, values, cw=28, ch=20, kinds=None, index=True,
              index_from=0, size=8.0, font=MONO, gap=0.0, idx_labels=None,
              top_labels=None, bottom_labels=None, idx_color=None):
        """A horizontal run of array cells with optional index row."""
        kinds = kinds or [""] * len(values)
        centers = []
        for i, v in enumerate(values):
            cx = x + i * (cw + gap)
            self.box(cx, y, cw, ch, None, kinds[i] if i < len(kinds) else "",
                     radius=1.6)
            if v is not None and v != "":
                fc, sc = PAL.get(kinds[i] if i < len(kinds) else "", PAL[""])
                self.text(cx + cw / 2, y + ch / 2 - size * 0.35, str(v), size,
                          D.ink, font, "c")
            centers.append(cx + cw / 2)
            if index:
                lbl = idx_labels[i] if idx_labels else str(i + index_from)
                self.text(cx + cw / 2, y - 9.5, lbl, 6.8,
                          idx_color or D.faint, SANS, "c")
            if top_labels and i < len(top_labels) and top_labels[i]:
                self.text(cx + cw / 2, y + ch + 4.5, top_labels[i], 6.8,
                          D.muted, SANS, "c")
            if bottom_labels and i < len(bottom_labels) and bottom_labels[i]:
                self.text(cx + cw / 2, y - 19, bottom_labels[i], 6.8,
                          D.muted, SANS, "c")
        return centers

    def pointer(self, cx, y_top, label, color=None, size=6.9, height=11):
        color = color or D.hi_bd
        self.arrow(cx, y_top + height, cx, y_top + 2.4, color=color, lw=0.9,
                   head=3.2)
        self.text(cx, y_top + height + 2.6, label, size, color, SANS_SB, "c")

    def tree(self, root, x, y, level_h=34, leaf_w=26, r=9.5, kinds=None,
             edge_labels=False, size=7.8, node_kind_fn=None, draw_null=False):
        """Lay out and draw a binary tree given as nested (val, left, right)."""
        leaves = []

        def count(n):
            if n is None:
                return 0
            return max(1, count(n[1]) + count(n[2])) if (len(n) > 2 and (n[1] or n[2])) else 1

        pos = {}
        counter = [0]

        def assign(n, depth):
            if n is None:
                return None
            left = n[1] if len(n) > 1 else None
            right = n[2] if len(n) > 2 else None
            lx = assign(left, depth + 1)
            if lx is None and right is None:
                px = counter[0] * leaf_w
                counter[0] += 1
            rx = assign(right, depth + 1)
            if lx is not None and rx is not None:
                px = (lx + rx) / 2
            elif lx is not None:
                px = lx + leaf_w * 0.5
            elif rx is not None:
                px = rx - leaf_w * 0.5
            pos[id(n)] = (px, -depth * level_h, n)
            return px

        assign(root, 0)
        xs = [p[0] for p in pos.values()]
        span = (max(xs) - min(xs)) if xs else 0
        x0 = x - span / 2 - min(xs) if xs else x

        def draw_edges(n):
            if n is None:
                return
            px, py, _ = pos[id(n)]
            for child in (n[1] if len(n) > 1 else None, n[2] if len(n) > 2 else None):
                if child is not None:
                    cx, cy, _ = pos[id(child)]
                    self.line(x0 + px, y + py - r, x0 + cx, y + cy + r,
                              D.arrow, 0.75)
                    draw_edges(child)

        def draw_nodes(n):
            if n is None:
                return
            px, py, _ = pos[id(n)]
            k = node_kind_fn(n[0]) if node_kind_fn else (kinds or {}).get(n[0], "")
            self.circle(x0 + px, y + py, r, str(n[0]), k, size=size)
            for child in (n[1] if len(n) > 1 else None, n[2] if len(n) > 2 else None):
                draw_nodes(child)

        draw_edges(root)
        draw_nodes(root)
        return {n[2][0]: (x0 + n[0], y + n[1]) for n in pos.values()}

    def axes(self, x, y, w, h, xlabel=None, ylabel=None, color=None):
        color = color or D.faint
        self.line(x, y, x + w, y, color, 0.8)
        self.line(x, y, x, y + h, color, 0.8)
        if xlabel:
            self.text(x + w, y - 11, xlabel, 7.2, D.muted, SANS_I, "r")
        if ylabel:
            self.text(x - 6, y + h + 3, ylabel, 7.2, D.muted, SANS_I, "l")

    def plot(self, x, y, w, h, fn, xmax=1.0, ymax=1.0, color=None, lw=1.2,
             samples=120, dashed=False, label=None, label_at=0.92):
        color = color or D.node_bd
        c = self.c
        c.saveState()
        c.setStrokeColor(color)
        c.setLineWidth(lw)
        if dashed:
            c.setDash(2.6, 2.2)
        p = c.beginPath()
        started = False
        lastpt = None
        for i in range(samples + 1):
            t = i / samples
            xv = t * xmax
            yv = fn(xv)
            if yv is None:
                continue
            px = x + (xv / xmax) * w
            py = y + min(yv / ymax, 1.02) * h
            if py > y + h:
                py = y + h
            if not started:
                p.moveTo(px, py)
                started = True
            else:
                p.lineTo(px, py)
            if t <= label_at:
                lastpt = (px, py)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()
        if label and lastpt:
            self.text(lastpt[0] + 3, lastpt[1] - 2.4, label, 7.0, color, SANS_SB, "l")

    def grid_matrix(self, x, y, rows, cols, cw=17, ch=15, values=None,
                    kinds=None, size=6.8, labels_r=None, labels_c=None):
        for r in range(rows):
            for cc in range(cols):
                k = kinds(r, cc) if callable(kinds) else ""
                v = values(r, cc) if callable(values) else None
                px = x + cc * cw
                py = y - (r + 1) * ch
                self.box(px, py, cw, ch, None, k, radius=0.8, lw=0.45)
                if v not in (None, ""):
                    self.text(px + cw / 2, py + ch / 2 - size * 0.35, str(v),
                              size, D.ink, MONO, "c")
            if labels_r:
                self.text(x - 4, y - (r + 1) * ch + ch / 2 - 2.4, labels_r[r],
                          6.6, D.muted, SANS, "r")
        if labels_c:
            for cc in range(cols):
                self.text(x + cc * cw + cw / 2, y + 3.5, labels_c[cc], 6.6,
                          D.muted, SANS, "c")

    def label_chip(self, x, y, text, kind="dim", size=6.8, pad=4.5, h=11):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        w = stringWidth(text, SANS_SB, size) + pad * 2
        fc, sc = PAL.get(kind, PAL["dim"])
        c = self.c
        c.saveState()
        c.setFillColor(fc)
        c.setStrokeColor(sc)
        c.setLineWidth(0.5)
        c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
        c.restoreState()
        self.text(x + w / 2, y + h / 2 - size * 0.36, text, size,
                  D.white if kind in ("solid", "ink") else sc, SANS_SB, "c")
        return w


class Figure(Flowable):
    """A diagram rendered by `fn(pen)` inside a fixed box."""

    def __init__(self, fn, height, width=None, pad_top=4, pad_bottom=4,
                 bg=None, border=False):
        Flowable.__init__(self)
        self.fn = fn
        self.height = height + pad_top + pad_bottom
        self.width = width or FRAME_W
        self.pad_bottom = pad_bottom
        self.bg = bg
        self.border = border

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        if self.bg or self.border:
            c.saveState()
            if self.bg:
                c.setFillColor(self.bg)
            c.setStrokeColor(D.dim_bd if self.border else self.bg)
            c.setLineWidth(0.5)
            c.roundRect(0, 0, self.width, self.height, 3,
                        stroke=1 if self.border else 0, fill=1 if self.bg else 0)
            c.restoreState()
        c.saveState()
        c.translate(0, self.pad_bottom)
        self.fn(Pen(c, self.width, self.height))
        c.restoreState()


def figure(fn, height, caption=None, number=None, width=None, bg=None,
           border=False, keep=True):
    """A figure plus its numbered caption, kept together on one page."""
    ss = styles()
    items = [Figure(fn, height, width=width, bg=bg, border=border)]
    if caption:
        from .markup import inline
        num = ("<b><font color='#16466E'>Figure %s</font></b>&nbsp;&nbsp;" % number) if number else ""
        items.append(Paragraph(num + inline(caption), ss["caption"]))
    return KeepTogether(items) if keep else items
