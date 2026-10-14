#!/usr/bin/env python3
"""Content linter: catches the authoring mistakes this engine renders badly."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "book"))
sys.path.insert(0, HERE)

from engine.markup import GREEK, SYMBOLS, OPERATORS    # noqa: E402
from engine.parser import FIGURES, parse_file          # noqa: E402
import figures                                         # noqa: F401,E402
from manifest import BOOK, PARTS                       # noqa: E402

CONTENT = os.path.join(HERE, "content")
MATH_OK = set(GREEK) | set(SYMBOLS) | set(OPERATORS) | {
    "frac", "binom", "sqrt", "left", "right", "begin", "end",
    "cases", "pmatrix", "hat", "bar", "vec", "tilde", "overline",
    "underline", "mathbb", "mathcal", "mathrm", "mathbf"}
problems = []


def _mono_cmap():
    """Code points the monospace font can actually render."""
    try:
        import os
        from reportlab.pdfbase.ttfonts import TTFont
        from engine import style
        face = TTFont("probe", os.path.join(style.FONT_DIR,
                                            "DejaVuSansMono.ttf")).face
        return set(face.charToGlyph)
    except Exception:
        return None


MONO_CMAP = _mono_cmap()
if MONO_CMAP is None:          # font unavailable: fall back to ASCII-only
    MONO_CMAP = set(range(128)) | {0x2192, 0x2190}


def err(fname, msg):
    problems.append("%-34s %s" % (fname, msg))


def walk(blocks, fname, in_callout=False):
    """Recursively check parsed blocks."""
    for b in blocks:
        t = b["t"]
        if t == "callout":
            seq = [x["t"] for x in b["body"]]
            for i, t in enumerate(seq):
                if t != "list" or not b["body"][i]["ordered"]:
                    continue
                # a code block or table between two numbered lists means one
                # list was interrupted; a paragraph between them is deliberate
                for j in range(i + 1, len(seq)):
                    if seq[j] in ("code", "table"):
                        continue
                    if seq[j] == "list" and b["body"][j]["ordered"] \
                            and any(seq[k] in ("code", "table")
                                    for k in range(i + 1, j)):
                        err(fname, "numbered list in :::%s is interrupted by a "
                                   "%s block — the numbering restarts at 1"
                            % (b["kind"], seq[i + 1]))
                    break
            for inner in b["body"]:
                if inner["t"] == "list":
                    levels = {lvl for lvl, _, _ in inner["items"]}
                    if len(levels) > 1:
                        err(fname, "nested list inside :::%s — the engine "
                                   "flattens it" % b["kind"])
                    kinds = {o for _, o, _ in inner["items"]}
                    if len(kinds) > 1:
                        err(fname, "mixed bullet/numbered list inside "
                                   ":::%s" % b["kind"])
            walk(b["body"], fname, True)
        elif t == "fig":
            name = b["spec"].split("|")[0].strip()
            if name not in FIGURES:
                err(fname, "figure '%s' is referenced but not defined" % name)
            parts = [x.strip() for x in b["spec"].split("|")]
            if len(parts) < 3:
                err(fname, "figure '%s' has no caption" % name)
        elif t == "code":
            if b["lang"] not in ("cpp", "text", "python", "bash", "c"):
                err(fname, "unusual code language '%s'" % b["lang"])
        elif t == "table":
            widths = {len(r.strip().strip("|").split("|")) for r in b["rows"]}
            if len(widths) > 1:
                err(fname, "table has rows of differing column counts: %s"
                    % sorted(widths))


def main():
    declared = []
    for part in PARTS:
        declared += part["chapters"]
    declared += BOOK["frontmatter"]

    on_disk = sorted(f for f in os.listdir(CONTENT) if f.endswith(".md"))
    for f in on_disk:
        if f not in declared:
            err(f, "file exists but is not listed in manifest.py")
    for f in declared:
        if f not in on_disk:
            err(f, "listed in manifest.py but missing from content/")

    used_figs = set()
    for f in on_disk:
        path = os.path.join(CONTENT, f)
        raw = open(path, encoding="utf-8").read()

        # raw-text checks the parser cannot see (skipping fenced code)
        in_fence = False
        for n, line in enumerate(raw.split("\n"), 1):
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if re.match(r"^@fig\s+\w", line):
                err(f, "line %d: '@fig name' should be '@fig: name'" % n)
            if re.match(r"^@(tbl|cols|tsize)\s+\w", line):
                err(f, "line %d: missing colon after @%s"
                    % (n, line.split()[0][1:]))
            if "\t" in line:
                err(f, "line %d: literal tab character" % n)
            # (c)/(tm) become symbols -- but inline code and math are
            # protected by the engine before entity substitution, so only
            # occurrences in plain prose matter.
            prose = re.sub(r"`[^`]*`", "", line)
            prose = re.sub(r"\$[^$]*\$", "", prose)
            if "(c)" in prose or "(tm)" in prose:
                err(f, "line %d: '(c)'/'(tm)' in prose renders as a "
                       "© / ™ symbol" % n)
        if raw.count("```") % 2:
            err(f, "odd number of ``` fences")

        # glyphs the monospace font cannot render, inside code blocks
        inf = False
        for n, line in enumerate(raw.split("\n"), 1):
            if line.startswith("```"):
                inf = not inf
                continue
            if inf:
                for ch in line:
                    if ord(ch) > 127 and ord(ch) not in MONO_CMAP:
                        err(f, "line %d: %r inside a code block — the mono "
                               "font has no glyph for it" % (n, ch))
                        break

        italic_open = {}
        # a bare arrow glyph inside an *italic* span collides with the
        # fallback font; it must sit inside backticks (mono) instead.
        # Bold and plain text are fine, so look only inside single-* spans.
        for n, line in enumerate(raw.split("\n"), 1):
            if not line.strip():
                italic_open[f] = False       # a blank line ends the span
                continue
            if "\u2192" not in line:
                bare0 = re.sub(r"`[^`]*`", "", line)
                bare0 = re.sub(r"\*\*[^*]*\*\*", "", bare0)
                italic_open[f] = (italic_open.get(f, False)
                                  ^ (bare0.count("*") % 2 == 1))
                continue
            bare = re.sub(r"`[^`]*`", "", line)        # drop code spans
            bare = re.sub(r"\*\*[^*]*\*\*", "", bare)   # drop bold
            # walk the line tracking whether we are inside a single-* span;
            # such spans can run across several lines, so carry the state
            inside = italic_open.get(f, False)
            flagged = False
            for ch in bare:
                if ch == "*":
                    inside = not inside
                elif ch == "\u2192" and inside and not flagged:
                    err(f, "line %d: a bare arrow inside an italic span — "
                           "wrap it in backticks" % n)
                    flagged = True
            italic_open[f] = inside

        # math commands the renderer does not know print as literal text
        stripped = re.sub(r"^```.*?^```", "", raw, flags=re.M | re.S)
        for m in re.finditer(r"\$\$?(.+?)\$\$?", stripped, re.S):
            for cmd in re.findall(r"\\([A-Za-z]+)", m.group(1)):
                if cmd not in MATH_OK:
                    err(f, "math command \\%s is not supported — it will "
                           "print as literal text" % cmd)

        blocks = parse_file(path)
        if not blocks or blocks[0]["t"] != "h1":
            err(f, "does not start with a '# Title' line")
        walk(blocks, f)
        for m in re.finditer(r"^@fig:\s*([\w-]+)", raw, re.M):
            used_figs.add(m.group(1))

    for name in sorted(set(FIGURES) - used_figs):
        err("(figures)", "figure '%s' is defined but never used" % name)

    if problems:
        print("%d problem(s):\n" % len(problems))
        for p in problems:
            print("  " + p)
        return 1
    print("content ok — %d files, %d figures" % (len(on_disk), len(used_figs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
