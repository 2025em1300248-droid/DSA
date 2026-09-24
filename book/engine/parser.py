"""
Content format: an extended Markdown compiled straight to flowables.

Blocks
------
  # Title / ## / ### / ####     headings (# only at the top of a chapter file)
  @key: value                   chapter metadata (short, subtitle, blurb, ...)
  paragraph text                prose, with inline markup
  - item / 1. item              lists, one level of nesting via indent
  > quote                       block quote ("> -- name" attributes it)
  ```lang title="..." small     fenced, syntax-highlighted code
  | a | b |                     pipe tables
  :::kind Optional title        callout, nests any of the above
  @fig name | h | caption       a registered diagram
  @tbl caption                  caption the table that follows
  ---                           horizontal rule
  @pagebreak / @needspace N     layout hints
"""
import re

from reportlab.platypus import (CondPageBreak, KeepTogether, PageBreak,
                                Paragraph, Spacer)

from .draw import figure as make_figure
from .flowables import Anchor, HRule, RunningState, callout, code_block, md_table
from .markup import inline, plain
from .style import C, FRAME_W, SANS, SANS_B, SERIF, styles

FIGURES = {}


def fig(name):
    def deco(fn):
        FIGURES[name] = fn
        return fn
    return deco


class Ctx:
    def __init__(self, chapter=0, fig_numbers=None, tbl_numbers=None, toc=True):
        self.chapter = chapter
        self.toc = toc
        self.fig_numbers = fig_numbers or {}
        self.tbl_numbers = tbl_numbers or {}
        self.fig_count = 0
        self.tbl_count = 0
        self.width = FRAME_W
        self.keys = []


# --------------------------------------------------------------------------
# Block scanner
# --------------------------------------------------------------------------
FENCE = re.compile(r"^```(\w*)(.*)$")
CALL_OPEN = re.compile(r"^:::(\w[\w-]*)\s*(.*)$")
HEAD = re.compile(r"^(#{1,4})\s+(.*)$")
META = re.compile(r"^@([a-z_-]+):\s?(.*)$")
BULLET = re.compile(r"^(\s*)[-*]\s+(.*)$")
NUMBER = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def scan(lines):
    blocks, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue

        m = FENCE.match(line)
        if m:
            lang = m.group(1) or "text"
            opts = m.group(2).strip()
            body, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            blocks.append({"t": "code", "lang": lang, "opts": opts,
                           "src": "\n".join(body)})
            continue

        m = CALL_OPEN.match(line)
        if m and s != ":::":
            kind, title = m.group(1), m.group(2).strip()
            depth, body, i = 1, [], i + 1
            while i < n:
                ls = lines[i].strip()
                if CALL_OPEN.match(lines[i]) and ls != ":::":
                    depth += 1
                elif ls == ":::":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                body.append(lines[i])
                i += 1
            blocks.append({"t": "callout", "kind": kind, "title": title,
                           "body": scan(body)})
            continue

        m = HEAD.match(line)
        if m:
            blocks.append({"t": "h%d" % len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue

        m = META.match(line)
        if m:
            key, val = m.group(1), m.group(2)
            if key in ("fig", "figure"):
                blocks.append({"t": "fig", "spec": val})
            elif key == "tbl":
                blocks.append({"t": "tblcap", "text": val})
            elif key == "cols":
                blocks.append({"t": "cols", "w": [float(x) for x in
                                                 val.replace(" ", "").split(",")]})
            elif key == "tsize":
                blocks.append({"t": "tsize", "n": float(val)})
            elif key == "pagebreak":
                blocks.append({"t": "pagebreak"})
            elif key == "needspace":
                blocks.append({"t": "needspace", "n": float(val or 60)})
            elif key == "space":
                blocks.append({"t": "space", "n": float(val or 6)})
            else:
                body = []
                if not val.strip():
                    j = i + 1
                    while j < n and lines[j].startswith(("- ", "* ", "  ")):
                        body.append(lines[j].strip().lstrip("-* ").strip()
                                    if lines[j].strip().startswith(("-", "*"))
                                    else lines[j].strip())
                        j += 1
                    i = j - 1
                blocks.append({"t": "meta", "key": key, "value": val,
                               "body": body})
            i += 1
            continue

        if s in ("---", "***", "___"):
            blocks.append({"t": "hr"})
            i += 1
            continue

        if TABLE_ROW.match(line):
            rows = []
            while i < n and TABLE_ROW.match(lines[i]):
                rows.append(lines[i])
                i += 1
            blocks.append({"t": "table", "rows": rows})
            continue

        if BULLET.match(line) or NUMBER.match(line):
            items, ordered = [], bool(NUMBER.match(line))
            while i < n:
                ln = lines[i]
                mb, mn = BULLET.match(ln), NUMBER.match(ln)
                if mb:
                    items.append((len(mb.group(1)) // 2, False, mb.group(2)))
                elif mn:
                    items.append((len(mn.group(1)) // 2, True, mn.group(3)))
                elif ln.strip() and ln.startswith(("  ", "\t")) and items:
                    lvl, o, t = items[-1]
                    items[-1] = (lvl, o, t + " " + ln.strip())
                else:
                    break
                i += 1
            blocks.append({"t": "list", "items": items, "ordered": ordered})
            continue

        if s.startswith(">"):
            body = []
            while i < n and lines[i].strip().startswith(">"):
                body.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append({"t": "quote", "body": body})
            continue

        para = []
        while i < n and lines[i].strip() and not _starts_block(lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            blocks.append({"t": "p", "text": " ".join(para)})
        else:
            i += 1
    return blocks


def _starts_block(line):
    s = line.strip()
    return (HEAD.match(line) or META.match(line) or FENCE.match(line)
            or CALL_OPEN.match(line) or s == ":::" or TABLE_ROW.match(line)
            or BULLET.match(line) or NUMBER.match(line) or s.startswith(">")
            or s in ("---", "***", "___"))


# --------------------------------------------------------------------------
# Renderer
# --------------------------------------------------------------------------
def render(blocks, ctx, in_callout=False, width=None):
    ss = styles()
    out = []
    width = width or ctx.width
    prev = None
    pending_caption = None
    pending_cols = None
    pending_size = None

    for b in blocks:
        t = b["t"]
        if t == "p":
            st = ss["callout-body"] if in_callout else (
                ss["body"] if prev in (None, "h2", "h3", "h4", "h1") else ss["body-cont"])
            out.append(Paragraph(_xref(b["text"], ctx), st))
        elif t in ("h2", "h3", "h4"):
            key = "sec-%d-%d" % (ctx.chapter, len(ctx.keys))
            ctx.keys.append(key)
            lvl = {"h2": 2, "h3": 3}.get(t, -1)
            if not getattr(ctx, "toc", True):
                lvl = -1
            if t == "h2":
                out.append(CondPageBreak(76))
            if lvl > 0:
                out.append(Anchor(lvl, b["text"], key))
            out.append(Paragraph(_xref(b["text"], ctx), ss[t]))
        elif t == "code":
            opts = b.get("opts", "")
            m = re.search(r'title="([^"]*)"', opts)
            small = "small" in opts
            hl = re.search(r"hl=([\d,]+)", opts)
            hls = set(int(x) for x in hl.group(1).split(",")) if hl else ()
            blk = code_block(b["src"], b["lang"], title=m.group(1) if m else None,
                             small=small, width=width, highlight=hls,
                             numbers="nonum" not in opts)
            out.append(Spacer(0, 6.5))
            out.append(blk)
            out.append(Spacer(0, 3))
        elif t == "list":
            out.extend(_list(b, ctx, ss, in_callout))
        elif t == "quote":
            out.extend(_quote(b, ctx, ss))
        elif t == "table":
            hdr, rows, aligns = _parse_table(b["rows"])
            out.append(Spacer(0, 6))
            out.append(md_table(hdr, rows, aligns, width=width,
                                widths=pending_cols, font_size=pending_size))
            pending_cols = None
            pending_size = None
            if pending_caption:
                ctx.tbl_count += 1
                out.append(Paragraph(
                    "<b><font color='#16466E'>Table %d.%d</font></b>&nbsp;&nbsp;%s"
                    % (ctx.chapter, ctx.tbl_count, inline(pending_caption)),
                    ss["caption"]))
                pending_caption = None
            out.append(Spacer(0, 5))
        elif t == "tblcap":
            pending_caption = b["text"]
        elif t == "cols":
            pending_cols = b["w"]
        elif t == "tsize":
            pending_size = b["n"]
        elif t == "callout":
            inner = render(b["body"], ctx, in_callout=True, width=width - 24)
            out.append(Spacer(0, 7))
            out.append(KeepTogether(
                [callout(b["kind"], b["title"], inner, width=width)]))
            out.append(Spacer(0, 4))
        elif t == "fig":
            out.extend(_figure(b["spec"], ctx, width))
        elif t == "hr":
            out.append(HRule(width=width, color=C.hairline, space_before=8,
                             space_after=8))
        elif t == "pagebreak":
            out.append(PageBreak())
        elif t == "needspace":
            out.append(CondPageBreak(b["n"]))
        elif t == "space":
            out.append(Spacer(0, b["n"]))
        prev = t
    return out


def _xref(text, ctx):
    def sub(m):
        name = m.group(1)
        num = ctx.fig_numbers.get(name)
        return "Figure&nbsp;%s" % num if num else "Figure&nbsp;?"
    text = re.sub(r"@ref:([\w-]+)", sub, text)
    return inline(text)


def _list(b, ctx, ss, in_callout):
    out = []
    for lvl, ordered, text in b["items"]:
        if in_callout:
            st = ss["callout-number"] if ordered else ss["callout-bullet"]
        else:
            st = (ss["number"] if lvl == 0 else ss["number2"]) if ordered else \
                 (ss["bullet"] if lvl == 0 else ss["bullet2"])
        if ordered:
            bullet = None
        else:
            bullet = "•" if lvl == 0 else "–"
        if ordered:
            num = text.split("\x00")[0]
            out.append(Paragraph(_xref(text, ctx), st, bulletText=b.get("_n", "")))
        else:
            out.append(Paragraph(_xref(text, ctx), st, bulletText=bullet))
    if b["ordered"]:
        out = []
        counters = {}
        for lvl, ordered, text in b["items"]:
            counters[lvl] = counters.get(lvl, 0) + 1
            for k in list(counters):
                if k > lvl:
                    del counters[k]
            if in_callout:
                st = ss["callout-number"]
            else:
                st = ss["number"] if lvl == 0 else ss["number2"]
            mark = "%d." % counters[lvl] if lvl == 0 else "%s." % chr(96 + counters[lvl])
            out.append(Paragraph(_xref(text, ctx), st,
                                 bulletText=mark))
    out.append(Spacer(0, 4.5))
    return [Spacer(0, 3.2)] + out


def _quote(b, ctx, ss):
    out, attr = [], None
    body = list(b["body"])
    if body and body[-1].startswith("--"):
        attr = body.pop().lstrip("- ").strip()
    text = " ".join(x for x in body if x)
    out.append(Spacer(0, 5))
    out.append(Paragraph(inline(text), ss["quote"]))
    if attr:
        out.append(Paragraph("—&nbsp;" + inline(attr), ss["quote-attr"]))
    out.append(Spacer(0, 5))
    return out


def _parse_table(rows):
    cells = []
    aligns = None
    for r in rows:
        if TABLE_SEP.match(r):
            spec = [c.strip() for c in r.strip().strip("|").split("|")]
            aligns = []
            for sp in spec:
                if sp.startswith(":") and sp.endswith(":"):
                    aligns.append("c")
                elif sp.endswith(":"):
                    aligns.append("r")
                else:
                    aligns.append("l")
            continue
        cells.append([c.strip() for c in r.strip().strip("|").split("|")])
    if not cells:
        return None, [], None
    header, body = cells[0], cells[1:]
    ncol = len(header)
    body = [(r + [""] * ncol)[:ncol] for r in body]
    return header, body, aligns


def _figure(spec, ctx, width):
    parts = [p.strip() for p in spec.split("|")]
    name = parts[0]
    height = float(parts[1]) if len(parts) > 1 and parts[1] else 120.0
    caption = parts[2] if len(parts) > 2 else None
    fn = FIGURES.get(name)
    ctx.fig_count += 1
    number = "%d.%d" % (ctx.chapter, ctx.fig_count)
    if fn is None:
        from reportlab.platypus import Paragraph as P
        return [P("<i>[missing figure: %s]</i>" % name, styles()["caption"])]
    return [Spacer(0, 9), make_figure(fn, height, caption=caption,
                                      number=number, width=width),
            Spacer(0, 9)]


def collect_figures(blocks, ctx):
    """First pass: assign figure numbers so @ref works."""
    for b in blocks:
        if b["t"] == "fig":
            name = b["spec"].split("|")[0].strip()
            ctx.fig_count += 1
            ctx.fig_numbers[name] = "%d.%d" % (ctx.chapter, ctx.fig_count)
        elif b["t"] == "callout":
            collect_figures(b["body"], ctx)


def parse_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    return scan(lines)
