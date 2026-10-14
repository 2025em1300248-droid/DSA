#!/usr/bin/env python3
"""Measure every figure and report drawing that falls outside its box.

Figures are drawn with absolute coordinates, so it is easy to put a label
past the right edge of the frame, where it silently runs into the margin.
This renders each figure onto a measuring canvas and reports the overflow.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "book"))
sys.path.insert(0, HERE)

import re                                              # noqa: E402
from reportlab.pdfbase.pdfmetrics import stringWidth   # noqa: E402

from engine.draw import Pen                            # noqa: E402
from engine.parser import FIGURES                      # noqa: E402
from engine.style import FRAME_W, styles               # noqa: E402
import figures                                         # noqa: F401,E402

CONTENT = os.path.join(HERE, "content")
TOL = 1.0          # horizontal slack: tight, this runs into the margin
VTOL = 14.0        # vertical slack: a little overshoot is harmless


class Probe:
    """Stands in for a reportlab canvas, recording the extents touched."""

    def __init__(self):
        self.minx = self.miny = 1e9
        self.maxx = self.maxy = -1e9
        self._font = ("Sans", 8)

    def _mark(self, x, y):
        self.minx = min(self.minx, x); self.maxx = max(self.maxx, x)
        self.miny = min(self.miny, y); self.maxy = max(self.maxy, y)

    # -- canvas surface used by Pen --------------------------------------
    def saveState(self): pass
    def restoreState(self): pass
    def setFillColor(self, *a): pass
    def setStrokeColor(self, *a): pass
    def setLineWidth(self, *a): pass
    def setDash(self, *a): pass
    def translate(self, *a): pass
    def rotate(self, *a): pass
    def setFont(self, name, size): self._font = (name, size)

    def drawString(self, x, y, s):
        self._mark(x, y)
        self._mark(x + stringWidth(s, *self._font), y + self._font[1])

    def drawCentredString(self, x, y, s):
        w = stringWidth(s, *self._font) / 2.0
        self._mark(x - w, y); self._mark(x + w, y + self._font[1])

    def drawRightString(self, x, y, s):
        self._mark(x - stringWidth(s, *self._font), y)
        self._mark(x, y + self._font[1])

    def rect(self, x, y, w, h, **k): self._mark(x, y); self._mark(x + w, y + h)
    def roundRect(self, x, y, w, h, r, **k): self.rect(x, y, w, h)
    def circle(self, cx, cy, r, **k):
        self._mark(cx - r, cy - r); self._mark(cx + r, cy + r)
    def line(self, x1, y1, x2, y2):
        self._mark(x1, y1); self._mark(x2, y2)

    def beginPath(self): return _Path(self)
    def drawPath(self, p, **k): pass


class _Path:
    def __init__(self, probe): self.p = probe
    def moveTo(self, x, y): self.p._mark(x, y)
    def lineTo(self, x, y): self.p._mark(x, y)
    def curveTo(self, *a):
        for i in range(0, len(a), 2):
            self.p._mark(a[i], a[i + 1])
    def close(self): pass


def heights_from_content():
    """The height each figure is given in the book."""
    out = {}
    for f in sorted(os.listdir(CONTENT)):
        if not f.endswith(".md"):
            continue
        for m in re.finditer(r"^@fig:\s*([\w-]+)\s*\|\s*([\d.]+)",
                             open(os.path.join(CONTENT, f)).read(), re.M):
            out[m.group(1)] = (float(m.group(2)), f)
    return out


def main():
    styles()                     # registers the TTF fonts
    heights = heights_from_content()
    problems = []
    for name, fn in sorted(FIGURES.items()):
        h, src = heights.get(name, (140.0, "(unused)"))
        probe = Probe()
        pen = Pen(probe, FRAME_W, h + 8)
        try:
            fn(pen)
        except Exception as exc:                      # a figure that throws
            problems.append((name, src, "raised %s: %s"
                             % (type(exc).__name__, exc)))
            continue
        if probe.maxx > FRAME_W + TOL:
            problems.append((name, src, "extends %.0f pt past the right edge "
                             "(x=%.0f, frame=%.0f)"
                             % (probe.maxx - FRAME_W, probe.maxx, FRAME_W)))
        if probe.minx < -TOL:
            problems.append((name, src, "starts %.0f pt left of the frame"
                             % -probe.minx))
        if probe.maxy > h + 8 + VTOL:
            problems.append((name, src, "extends %.0f pt above its box"
                             % (probe.maxy - h - 8)))
        if probe.miny < -VTOL:
            problems.append((name, src, "extends %.0f pt below its box"
                             % -probe.miny))

    if problems:
        print("%d figure problem(s):\n" % len(problems))
        for name, src, msg in problems:
            print("  %-22s %-32s %s" % (name, src, msg))
        return 1
    print("all %d figures fit their boxes" % len(FIGURES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
