"""Composite flowables: callouts, code blocks, tables, openers, figures."""
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import (Flowable, KeepTogether, Paragraph, Spacer, Table,
                                TableStyle, CondPageBreak)

from .style import (C, FRAME_W, MONO, MONO_B, MONO_I, SANS, SANS_B, SANS_BLK,
                    SANS_SB, SERIF, SERIF_I, styles)
from .markup import inline, plain

# --------------------------------------------------------------------------
# Callout taxonomy
# --------------------------------------------------------------------------
KINDS = {
    "definition": ("DEFINITION",        C.primary, C.primary_lt, C.primary_md),
    "insight":    ("KEY INSIGHT",       C.teal,    C.teal_lt,    C.teal_md),
    "intuition":  ("INTUITION",         C.teal,    C.teal_lt,    C.teal_md),
    "ml":         ("WHERE THIS SHOWS UP IN ML", C.violet, C.violet_lt, C.violet_md),
    "pitfall":    ("COMMON PITFALL",    C.crimson, C.crimson_lt, C.crimson_md),
    "warning":    ("WATCH OUT",         C.crimson, C.crimson_lt, C.crimson_md),
    "perf":       ("PERFORMANCE NOTE",  C.amber,   C.amber_lt,   C.amber_md),
    "hardware":   ("HARDWARE REALITY",  C.amber,   C.amber_lt,   C.amber_md),
    "theorem":    ("THEOREM",           C.slate,   C.slate_lt,   C.slate_md),
    "proof":      ("PROOF",             C.slate,   C.slate_lt,   C.slate_md),
    "math":       ("THE MATH",          C.slate,   C.slate_lt,   C.slate_md),
    "exercise":   ("EXERCISES",         C.green,   C.green_lt,   C.green_md),
    "practice":   ("PRACTICE",          C.green,   C.green_lt,   C.green_md),
    "solution":   ("SOLUTION",          C.green,   C.green_lt,   C.green_md),
    "interview":  ("INTERVIEW ANGLE",   C.primary, C.primary_lt, C.primary_md),
    "note":       ("NOTE",              C.slate,   C.slate_lt,   C.slate_md),
    "recap":      ("CHAPTER RECAP",     C.primary, C.primary_lt, C.primary_md),
    "checklist":  ("CHECKLIST",         C.primary, C.primary_lt, C.primary_md),
    "history":    ("HISTORY",           C.amber,   C.amber_lt,   C.amber_md),
    "objectives": ("WHAT YOU WILL LEARN", C.primary, C.primary_lt, C.primary_md),
}


def callout(kind, title, body_flowables, width=None):
    label, fg, bg, bd = KINDS.get(kind, KINDS["note"])
    ss = styles()
    head = title if title else label
    inner = []
    tstyle = ss["callout-title"].clone("ct-%s" % kind)
    tstyle.textColor = fg
    inner.append(Paragraph(_badge(label, head, fg), tstyle))
    inner.extend(body_flowables)
    w = width or FRAME_W
    t = Table([[inner]], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, fg),
        ("BOX", (0, 0), (-1, -1), 0.4, bd),
        ("ROUNDEDCORNERS", [0, 3, 3, 0]),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    t.splitInRow = 1
    return t


def _badge(label, head, fg):
    if head and head.strip().upper() == label.strip().upper():
        head = None
    if head and head != label:
        return "%s&nbsp;&nbsp;<font color='#9AA1AE'>|</font>&nbsp;&nbsp;<font color='#22252B'>%s</font>" % (
            label, inline(head))
    return label


# --------------------------------------------------------------------------
# Syntax highlighting
# --------------------------------------------------------------------------
from pygments import lex                                   # noqa: E402
from pygments.lexers import get_lexer_by_name, TextLexer   # noqa: E402
from pygments.token import Token                           # noqa: E402

THEME = {
    Token.Keyword:              ("#CF222E", False),
    Token.Keyword.Constant:     ("#0550AE", False),
    Token.Keyword.Namespace:    ("#CF222E", False),
    Token.Name.Builtin:         ("#0550AE", False),
    Token.Name.Builtin.Pseudo:  ("#CF222E", False),
    Token.Name.Function:        ("#6639BA", False),
    Token.Name.Function.Magic:  ("#6639BA", False),
    Token.Name.Class:           ("#953800", False),
    Token.Name.Decorator:       ("#6639BA", False),
    Token.Name.Exception:       ("#953800", False),
    Token.Name.Namespace:       ("#953800", False),
    Token.Name.Attribute:       ("#1F2328", False),
    Token.Literal.String:       ("#0A3069", False),
    Token.Literal.String.Doc:   ("#0A3069", True),
    Token.Literal.String.Escape:("#0550AE", False),
    Token.Literal.Number:       ("#0550AE", False),
    Token.Operator:             ("#CF222E", False),
    Token.Operator.Word:        ("#CF222E", False),
    Token.Punctuation:          ("#4A5260", False),
    Token.Comment:              ("#6E7781", True),
    Token.Comment.Preproc:      ("#CF222E", False),
    Token.Generic.Prompt:       ("#6E7781", False),
    Token.Generic.Output:       ("#3D4756", False),
    Token.Text:                 ("#1F2328", False),
    Token.Error:                ("#CF222E", False),
}


def _tok_style(ttype):
    t = ttype
    while t is not None:
        if t in THEME:
            return THEME[t]
        t = t.parent
    return ("#1F2328", False)


def _esc_code(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace(" ", "&nbsp;"))


def highlight_lines(code, lang):
    """Return a list of marked-up lines ready for a mono Paragraph."""
    try:
        lexer = get_lexer_by_name(lang, stripnl=False, ensurenl=False)
    except Exception:
        lexer = TextLexer(stripnl=False, ensurenl=False)
    out, cur = [], []
    for ttype, value in lex(code, lexer):
        color, italic = _tok_style(ttype)
        for i, piece in enumerate(value.split("\n")):
            if i:
                out.append("".join(cur))
                cur = []
            if not piece:
                continue
            frag = _esc_code(piece)
            if italic:
                frag = '<font name="%s">%s</font>' % (MONO_I, frag)
            cur.append('<font color="%s">%s</font>' % (color, frag))
    out.append("".join(cur))
    while out and not out[-1].strip():
        out.pop()
    return out


def _wrap_source(code, limit):
    """Soft-wrap long source lines so nothing overflows the measure."""
    lines, cont = [], []
    for raw in code.split("\n"):
        if len(raw) <= limit:
            lines.append(raw)
            cont.append(False)
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        pad = " " * min(indent + 4, 20)
        first = True
        rest = raw
        while len(rest) > limit:
            cut = rest.rfind(" ", 0, limit)
            for sep in (", ", " + ", " = ", "("):
                p = rest.rfind(sep, int(limit * 0.45), limit)
                if p > cut:
                    cut = p + (len(sep) - 1 if sep != "(" else 1)
            if cut < int(limit * 0.4):
                cut = limit
            lines.append(rest[:cut].rstrip())
            cont.append(not first)
            first = False
            rest = pad + rest[cut:].lstrip()
        lines.append(rest)
        cont.append(not first)
    return lines, cont


def code_block(code, lang="python", title=None, small=False, width=None,
               numbers=True, highlight=()):
    ss = styles()
    w = width or FRAME_W
    cstyle = ss["code-sm"] if small else ss["code"]
    gstyle = ss["gutter-sm"] if small else ss["gutter"]
    char_w = (7.5 if small else 8.2) * 0.60205
    gutter_w = 19 if numbers else 0
    avail = w - gutter_w - 20
    limit = max(30, int(avail / char_w))

    src_lines, cont = _wrap_source(code.rstrip("\n"), limit)
    marked = highlight_lines("\n".join(src_lines), lang)
    while len(marked) < len(src_lines):
        marked.append("")

    rows, style = [], []
    if title:
        rows.append([Paragraph(inline(title), ss["code-title"]), ""])
        style += [("SPAN", (0, 0), (1, 0)),
                  ("BACKGROUND", (0, 0), (-1, 0), HexColor("#EDF0F4")),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.4, C.code_bd),
                  ("TOPPADDING", (0, 0), (-1, 0), 4.5),
                  ("BOTTOMPADDING", (0, 0), (-1, 0), 4.5),
                  ("LEFTPADDING", (0, 0), (-1, 0), 10)]
    n = 0
    off = 1 if title else 0
    for i, line in enumerate(marked):
        if cont[i] if i < len(cont) else False:
            label = "&#8618;"
        else:
            n += 1
            label = str(n)
        rows.append([Paragraph(label, gstyle) if numbers else "",
                     Paragraph(line if line.strip() else "&nbsp;", cstyle)])
        if (i + 1) in highlight:
            style.append(("BACKGROUND", (0, i + off), (-1, i + off), HexColor("#FFF6DA")))

    t = Table(rows, colWidths=[gutter_w, w - gutter_w] if numbers else [0, w],
              splitByRow=1)
    base = [
        ("BACKGROUND", (0, off), (-1, -1), C.code_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, C.code_bd),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
        ("LINEAFTER", (0, off), (0, -1), 0.5, C.code_bd) if numbers else ("NOOP",),
        ("LEFTPADDING", (0, off), (0, -1), 2),
        ("RIGHTPADDING", (0, off), (0, -1), 5),
        ("LEFTPADDING", (1, 0), (1, -1), 8),
        ("RIGHTPADDING", (1, 0), (1, -1), 5),
        ("TOPPADDING", (0, off), (-1, -1), 0.6),
        ("BOTTOMPADDING", (0, off), (-1, -1), 0.6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    base = [b for b in base if b[0] != "NOOP"]
    if rows:
        base.append(("TOPPADDING", (0, off), (-1, off), 6))
        base.append(("BOTTOMPADDING", (0, -1), (-1, -1), 6))
    t.setStyle(TableStyle(base + style))
    return t


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------
def md_table(header, rows, aligns=None, widths=None, width=None, mono_cols=(),
             font_size=None):
    ss = styles()
    w = width or FRAME_W
    ncol = len(header) if header else (len(rows[0]) if rows else 1)
    aligns = aligns or ["l"] * ncol
    if widths:
        total = float(sum(widths))
        col_w = [w * x / total for x in widths]
    else:
        col_w = _auto_widths(header, rows, w, ncol)

    def cell(txt, i, head=False):
        if head:
            st = ss["th"]
        elif i in mono_cols:
            st = ss["td-mono"]
        else:
            st = ss["td-c"] if aligns[i] in ("c", "r") else ss["td"]
        if font_size and not head:
            st = st.clone("tds%d" % font_size)
            st.fontSize = font_size
            st.leading = font_size * 1.35
        return Paragraph(inline(str(txt)), st)

    data = []
    if header:
        data.append([cell(h, i, True) for i, h in enumerate(header)])
    for r in rows:
        data.append([cell(c, i) for i, c in enumerate(r)])

    t = Table(data, colWidths=col_w, repeatRows=1 if header else 0, splitByRow=1)
    st = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, C.hairline),
        ("BOX", (0, 0), (-1, -1), 0.5, C.rule),
    ]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), C.tbl_head),
               ("TOPPADDING", (0, 0), (-1, 0), 5.5),
               ("BOTTOMPADDING", (0, 0), (-1, 0), 5.5),
               ("LINEBELOW", (0, 0), (-1, 0), 0, C.tbl_head)]
        for i in range(2, len(data), 2):
            st.append(("BACKGROUND", (0, i), (-1, i), C.tbl_zebra))
    for i, a in enumerate(aligns):
        if a == "c":
            st.append(("ALIGN", (i, 0), (i, -1), "CENTER"))
        elif a == "r":
            st.append(("ALIGN", (i, 0), (i, -1), "RIGHT"))
    t.setStyle(TableStyle(st))
    return t


def _auto_widths(header, rows, w, ncol):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    weights = []
    for i in range(ncol):
        cells = [plain(str(header[i]))] if header else []
        cells += [plain(str(r[i])) for r in rows if i < len(r)]
        longest = max((stringWidth(c, SERIF, 8.9) for c in cells), default=40)
        typical = sum(stringWidth(c, SERIF, 8.9) for c in cells) / max(1, len(cells))
        weights.append(max(28.0, min(longest, typical * 2.4 + 26)))
    total = sum(weights)
    return [w * x / total for x in weights]


# --------------------------------------------------------------------------
# Decorative primitives
# --------------------------------------------------------------------------
class HRule(Flowable):
    def __init__(self, width=None, thickness=0.6, color=None, space_before=6,
                 space_after=6, dash=None):
        Flowable.__init__(self)
        self.width = width or FRAME_W
        self.thickness = thickness
        self.color = color or C.rule
        self.sb, self.sa = space_before, space_after
        self.dash = dash

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.thickness + self.sb + self.sa)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        if self.dash:
            c.setDash(self.dash)
        y = self.sa
        c.line(0, y, self.width, y)
        c.restoreState()


class Anchor(Flowable):
    """Zero-height marker carrying metadata for the TOC / outline builder."""
    def __init__(self, level, text, key, kind="section"):
        Flowable.__init__(self)
        self.level, self.text, self.key, self.kind = level, text, key, kind
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        self.canv.bookmarkPage(self.key)


class RunningState(Flowable):
    """Zero-height marker that updates the running head."""
    def __init__(self, **kw):
        Flowable.__init__(self)
        self.state = kw
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        doc = getattr(self.canv, "_doc_ref", None)
        if doc is not None:
            doc.running.update(self.state)


class Callback(Flowable):
    def __init__(self, fn):
        Flowable.__init__(self)
        self.fn = fn
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        self.fn(self.canv)
