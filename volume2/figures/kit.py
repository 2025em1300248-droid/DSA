"""Shared drawing helpers for the two structures this book is about.

Every linked-list diagram in the book is built from `chain`, so the nodes,
the split data/next halves, the arrows and the NULL terminator look identical
on page 4 and on page 300.
"""
from engine.draw import D
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB

NW, NH = 54.0, 23.0          # node width / height
GAP = 30.0                   # gap between nodes
DATA_FRAC = 0.56             # how much of a node the data half takes


def node(p, x, y, value, kind="", w=NW, h=NH, size=8.4, ptr_kind="dim",
         value_font=MONO):
    """One linked-list node: a data half and a next half, drawn as one box.

    Returns (link_x, link_y), the centre of the little dot in the next half,
    which is where an outgoing arrow should start.
    """
    dw = w * DATA_FRAC
    p.box(x, y, dw, h, None, kind, radius=1.8)
    p.box(x + dw, y, w - dw, h, None, ptr_kind, radius=1.8)
    if value is not None and value != "":
        p.text(x + dw / 2, y + h / 2 - size * 0.35, str(value), size, D.ink,
               value_font, "c")
    lx, ly = x + dw + (w - dw) / 2, y + h / 2
    p.circle(lx, ly, 2.0, None, "solid", lw=0.0)
    return lx, ly


def null_cap(p, x, y, h=NH, label="nullptr", color=None):
    """The ground symbol that marks the end of a list."""
    color = color or D.muted
    cy = y + h / 2
    p.line(x, cy, x + 9, cy, color, 0.9)
    for i, half in enumerate((5.0, 3.2, 1.6)):
        p.line(x + 9 + i * 2.6, cy - half, x + 9 + i * 2.6, cy + half, color, 0.9)
    if label:
        p.text(x + 7, cy - h / 2 - 7.5, label, 6.6, color, SANS_I, "c")


def chain(p, x, y, values, kinds=None, w=NW, h=NH, gap=GAP, end="nullptr",
          labels=None, size=8.4, arrow_color=None, top_labels=None,
          addrs=None):
    """A run of linked-list nodes joined by arrows.

    `labels` puts a pointer arrow and a name above a node (head, curr, ...).
    `addrs` writes a fake memory address under each node.
    Returns the list of node left-edge x positions.
    """
    kinds = kinds or [""] * len(values)
    xs, link = [], None
    for i, v in enumerate(values):
        xi = x + i * (w + gap)
        xs.append(xi)
        if link is not None:
            p.arrow(link[0], link[1], xi - 1.5, y + h / 2,
                    arrow_color or D.arrow, 0.95, head=3.6)
        link = node(p, xi, y, v, kinds[i] if i < len(kinds) else "", w, h, size)
        if labels and i < len(labels) and labels[i]:
            p.pointer(xi + w * DATA_FRAC / 2, y + h, labels[i])
        if top_labels and i < len(top_labels) and top_labels[i]:
            p.text(xi + w / 2, y + h + 5.5, top_labels[i], 6.8, D.muted, SANS, "c")
        if addrs and i < len(addrs) and addrs[i]:
            p.text(xi + w / 2, y - 10.5, addrs[i], 6.4, D.faint, MONO, "c")
    if end == "nullptr" and values:
        null_cap(p, link[0] + 4, y, h)
    elif end == "open" and values:
        p.arrow(link[0], link[1], link[0] + 20, link[1], D.faint, 0.9, head=3.4,
                dashed=True)
    return xs


def head_arrow(p, x, y, h=NH, label="head", color=None, up=22, w=NW):
    """The labelled arrow that comes down into the first node."""
    color = color or D.node_bd
    cx = x + w * DATA_FRAC / 2
    p.arrow(cx, y + h + up, cx, y + h + 3, color, 1.0, head=3.4)
    p.text(cx, y + h + up + 3.5, label, 7.4, color, SANS_SB, "c")


def legend(p, x, y, items, size=6.8, gap=84):
    """A row of colour chips explaining what each shade means."""
    for i, (kind, text) in enumerate(items):
        px = x + i * gap
        p.box(px, y, 9, 9, None, kind, radius=1.5, lw=0.6)
        p.text(px + 13, y + 1.4, text, size, D.muted, SANS, "l")
