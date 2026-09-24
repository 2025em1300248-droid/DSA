"""
Inline markup: a compact author-facing syntax compiled to ReportLab's
paragraph mini-XML, plus a small TeX-like math renderer and an automatic
glyph-fallback pass for symbols the Source fonts do not carry.
"""
import re
from .style import C, SERIF, SERIF_I, SANS, MONO, FALLBACK, covers

# --------------------------------------------------------------------------
# Math
# --------------------------------------------------------------------------
GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι",
    "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π",
    "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
SYMBOLS = {
    "times": "×", "cdot": "·", "div": "÷", "pm": "±", "mp": "∓",
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠",
    "approx": "≈", "sim": "∼", "simeq": "≃", "equiv": "≡", "propto": "∝",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "mapsto": "↦",
    "Rightarrow": "⇒", "Leftrightarrow": "⇔", "implies": "⇒", "iff": "⇔",
    "uparrow": "↑", "downarrow": "↓", "leftrightarrow": "↔",
    "in": "∈", "notin": "∉", "subset": "⊂", "subseteq": "⊆",
    "supseteq": "⊇", "cup": "∪", "cap": "∩", "emptyset": "∅",
    "setminus": "∖", "forall": "∀", "exists": "∃", "neg": "¬",
    "land": "∧", "lor": "∨", "infty": "∞", "partial": "∂", "nabla": "∇",
    "sum": "Σ", "prod": "Π", "int": "∫", "sqrt": "√",
    "lfloor": "⌊", "rfloor": "⌋", "lceil": "⌈", "rceil": "⌉",
    "langle": "⟨", "rangle": "⟩", "ldots": "…", "cdots": "⋯", "dots": "…",
    "oplus": "⊕", "otimes": "⊗", "star": "⋆", "circ": "∘", "bullet": "•",
    "prime": "′", "degree": "°", "perp": "⊥", "parallel": "∥",
    "gg": "≫", "ll": "≪", "subsetneq": "⊊", "models": "⊨", "vdash": "⊢",
    "quad": "  ", "qquad": "    ", "colon": ":", "bmod": " mod ",
}
OPERATORS = {
    "log", "ln", "lg", "exp", "max", "min", "arg", "argmax", "argmin",
    "sin", "cos", "tan", "gcd", "lcm", "det", "dim", "deg", "mod",
    "sup", "inf", "lim", "Pr", "E", "Var", "Cov", "poly", "polylog",
    "text", "mathrm", "mathbf", "mathbb", "mathcal", "operatorname",
}
_BLACKBOARD = {"R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ", "C": "ℂ", "E": "𝔼",
               "P": "ℙ", "F": "𝔽"}
_CAL = {"O": "O", "N": "N", "T": "T", "L": "L", "S": "S", "D": "D",
        "A": "A", "B": "B", "C": "C", "M": "M", "P": "P", "F": "F",
        "G": "G", "H": "H", "V": "V", "E": "E", "R": "R", "X": "X"}


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class _MathLexer:
    def __init__(self, s):
        self.s, self.i, self.n = s, 0, len(s)

    def peek(self):
        return self.s[self.i] if self.i < self.n else ""

    def group(self):
        """Read one atom: a braced group, a command, or a single character."""
        self._ws()
        if self.i >= self.n:
            return ""
        ch = self.s[self.i]
        if ch == "{":
            depth, start = 0, self.i
            while self.i < self.n:
                if self.s[self.i] == "{":
                    depth += 1
                elif self.s[self.i] == "}":
                    depth -= 1
                    if depth == 0:
                        self.i += 1
                        return render_math(self.s[start + 1:self.i - 1])
                self.i += 1
            return render_math(self.s[start + 1:])
        return self._token()

    def _ws(self):
        while self.i < self.n and self.s[self.i] == " ":
            self.i += 1

    def _token(self):
        ch = self.s[self.i]
        if ch == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", self.s[self.i:])
            self.i += m.end()
            return _cmd(m.group(1), self)
        if ch.isalpha():
            m = re.match(r"[A-Za-z]+", self.s[self.i:])
            word = m.group(0)
            if len(word) > 1:
                self.i += len(word)
                if word in OPERATORS:
                    return '<font name="%s">%s</font>&#8201;' % (SERIF, word)
                return '<font name="%s">%s</font>' % (SERIF_I, word)
        self.i += 1
        return _atom(ch)


def _cmd(name, lex):
    if name in GREEK:
        return '<font name="%s">%s</font>' % (_fb_font(GREEK[name]), GREEK[name])
    if name in SYMBOLS:
        c = SYMBOLS[name]
        return '<font name="%s">%s</font>' % (_fb_font(c), _esc(c))
    if name == "frac":
        a, b = lex.group(), lex.group()
        return "%s&#8202;/&#8202;%s" % (a, b)
    if name == "binom":
        a, b = lex.group(), lex.group()
        return '(<font name="%s">%s</font>&#8202;<sub>/</sub>&#8202;%s)' % (SERIF_I, a, b)
    if name in ("text", "mathrm", "operatorname"):
        raw = _raw_group(lex)
        return '<font name="%s">%s</font>' % (SERIF, _esc(raw))
    if name == "mathbf":
        raw = _raw_group(lex)
        return "<b>%s</b>" % _esc(raw)
    if name == "mathbb":
        raw = _raw_group(lex).strip()
        out = "".join(_BLACKBOARD.get(c, c) for c in raw)
        return '<font name="%s">%s</font>' % (_fb_font(out or "R"), out)
    if name == "mathcal":
        raw = _raw_group(lex).strip()
        return '<font name="%s">%s</font>' % (SERIF_I, _esc("".join(_CAL.get(c, c) for c in raw)))
    if name in OPERATORS:
        return '<font name="%s">%s</font>&#8201;' % (SERIF, name)
    if name in ("big", "Big", "bigg", "Bigg", "left", "right", "middle",
                "displaystyle", "textstyle", "limits", "nolimits"):
        return ""
    if name in (",", ";", " "):
        return "&#8202;"
    if name == "!":
        return ""
    if name in ("{", "}", "%", "$", "#", "_", "^", "&"):
        return _esc(name)
    return '<font name="%s">%s</font>' % (SERIF, _esc(name))


def _raw_group(lex):
    lex._ws()
    if lex.peek() != "{":
        return lex.s[lex.i:lex.i + 1] if lex.i < lex.n else ""
    depth, start = 0, lex.i
    while lex.i < lex.n:
        if lex.s[lex.i] == "{":
            depth += 1
        elif lex.s[lex.i] == "}":
            depth -= 1
            if depth == 0:
                lex.i += 1
                return lex.s[start + 1:lex.i - 1]
        lex.i += 1
    return lex.s[start + 1:]


def _atom(ch):
    if ch.isalpha():
        return '<font name="%s">%s</font>' % (SERIF_I, ch)
    if ch in "+-=<>":
        sym = {"-": "−", "<": "&lt;", ">": "&gt;"}.get(ch, ch)
        return "&#8202;%s&#8202;" % sym
    if ch == "*":
        return "∗"
    if ch == "|":
        return "|"
    return _esc(ch)


def _fb_font(s):
    for ch in s:
        if not covers(SERIF, ch):
            return FALLBACK
    return SERIF


_CASES = re.compile(r"\\begin\{(cases|aligned|array)\}(.*?)\\end\{\1\}", re.S)


def _render_cases(body):
    rows = [r for r in re.split(r"\\\\", body) if r.strip()]
    out = []
    for r in rows:
        cells = [c.strip() for c in r.split("&")]
        lhs = render_math(cells[0])
        rhs = ""
        if len(cells) > 1 and cells[1].strip():
            rhs = ("&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#6A7180\">%s</font>"
                   % render_math(cells[1]))
        out.append("&nbsp;&nbsp;&nbsp;&nbsp;" + lhs + rhs)
    return "<br/>".join(out)


def render_math(src):
    """Render a TeX-ish fragment into ReportLab paragraph markup."""
    m = _CASES.search(src)
    if m:
        return (render_math(src[:m.start()]) + _render_cases(m.group(2))
                + render_math(src[m.end():]))
    lex = _MathLexer(src)
    out = []
    while lex.i < lex.n:
        ch = lex.peek()
        if ch == " ":
            lex.i += 1
            if out and not (out[-1].endswith("&#8202;")
                            or out[-1].endswith("&#8201;")):
                out.append("&#8202;")
            continue
        if ch == "_":
            lex.i += 1
            out.append("<sub>%s</sub>" % _strip_fonts(lex.group()))
            continue
        if ch == "^":
            lex.i += 1
            out.append("<super>%s</super>" % _strip_fonts(lex.group()))
            continue
        out.append(lex.group())
    return "".join(out)


def _strip_fonts(s):
    # Sub/superscripts read better upright and un-nested.
    return re.sub(r'<font name="Serif-It">([^<]*)</font>', r"\1", s)


# --------------------------------------------------------------------------
# Inline text markup
# --------------------------------------------------------------------------
_CODE_STYLE = ('<font name="%s" size="8.6" backColor="#F2F4F7" color="#8A2846">'
               '&#8202;%s&#8202;</font>')
_KBD_STYLE = '<font name="%s" size="8.6" color="#3D4756">%s</font>'

_ENTITIES = [
    ("(c)", "©"), ("(tm)", "™"), ("-->", "→"), ("<--", "←"),
    ("---", "\u2014"), ("--", "\u2013"), ("...", "…"),
]


def _protect(text, store, pattern, fn):
    def sub(m):
        store.append(fn(m))
        return "\x00%d\x00" % (len(store) - 1)
    return re.sub(pattern, sub, text)


def inline(text, allow_math=True):
    """Compile author markup to ReportLab paragraph markup."""
    if text is None:
        return ""
    store = []

    # 1. protect verbatim spans
    text = _protect(text, store, r"``(.+?)``",
                    lambda m: _CODE_STYLE % (MONO, _esc(m.group(1)).replace(" ", "&nbsp;")))
    text = _protect(text, store, r"`([^`]+?)`",
                    lambda m: _CODE_STYLE % (MONO, _esc(m.group(1)).replace(" ", "&nbsp;")))
    if allow_math:
        text = _protect(text, store, r"\$\$(.+?)\$\$", lambda m: render_math(m.group(1)))
        text = _protect(text, store, r"\$([^$]+?)\$", lambda m: render_math(m.group(1)))
    text = _protect(text, store, r"\[([^\]]+)\]\((https?://[^)]+)\)",
                    lambda m: '<link href="%s" color="#16466E"><u>%s</u></link>'
                              % (m.group(2), _esc(m.group(1))))

    # 2. escape the rest
    text = _esc(text)
    for a, b in _ENTITIES:
        text = text.replace(_esc(a), b)

    text = _smart_quotes(text)

    # 3. emphasis
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text, flags=re.S)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text, flags=re.S)
    text = re.sub(r"(?<![\w_])__(.+?)__(?![\w_])", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"~~(.+?)~~", r"<strike>\1</strike>", text, flags=re.S)
    text = re.sub(r"\^\{([^}]*)\}", r"<super>\1</super>", text)
    text = re.sub(r"~\{([^}]*)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"\{\{(.+?)\}\}", r'<font color="#16466E"><b>\1</b></font>', text, flags=re.S)

    # 4. restore protected spans
    def unprotect(m):
        return store[int(m.group(1))]
    for _ in range(3):
        if "\x00" not in text:
            break
        text = re.sub(r"\x00(\d+)\x00", unprotect, text)

    return _tidy(fallback_fonts(text))


_THIN = "&#8202;"


def _tidy(m):
    """Collapse duplicated thin spaces and redundant nested fallback spans."""
    while _THIN + _THIN in m:
        m = m.replace(_THIN + _THIN, _THIN)
    m = m.replace("&#8201;" + _THIN, "&#8201;").replace(_THIN + "&#8201;", "&#8201;")
    # Source Serif has no thin-space glyph, so render spacing as sized gaps.
    m = m.replace("&#8201;", '<font size="5.4"> </font>')
    m = m.replace(_THIN, '<font size="3.2"> </font>')
    m = re.sub(r'<font name="Fallback">(<font name="Fallback">.*?</font>)</font>', r"\1", m)
    for opener in ("\u230a", "\u2308", "(", "\u27e8"):
        m = m.replace(opener + _THIN, opener)
        m = m.replace(opener + "</font>" + _THIN, opener + "</font>")
    for closer in ("\u230b", "\u2309", ")", "\u27e9", ",", "."):
        m = m.replace(_THIN + closer, closer)
        m = m.replace(_THIN + '<font name="Fallback">' + closer, '<font name="Fallback">' + closer)
    return m


def _smart_quotes(t):
    out, open_d = [], True
    for i, ch in enumerate(t):
        if ch == '"':
            out.append("\u201c" if open_d else "\u201d")
            open_d = not open_d
        else:
            out.append(ch)
    t = "".join(out)
    t = re.sub(r"(?<=\w)'(?=\w)", "\u2019", t)
    t = re.sub(r"(?<=\s)'(?=\S)", "\u2018", t)
    t = re.sub(r"(?<=\S)'(?=\s|$)", "\u2019", t)
    return t


_TAG = re.compile(r"(<[^>]*>|&[#A-Za-z0-9]+;)")
MISSING = set()


def fallback_fonts(markup):
    """Wrap glyphs the Source families lack in the DejaVu fallback font."""
    parts = _TAG.split(markup)
    out = []
    for part in parts:
        if not part or part.startswith("<") or part.startswith("&"):
            out.append(part)
            continue
        buf, run = [], []
        for ch in part:
            if ord(ch) < 128 or (covers(SERIF, ch) and covers(SANS, ch)):
                if run:
                    buf.append('<font name="%s">%s</font>' % (FALLBACK, "".join(run)))
                    run = []
                buf.append(ch)
            else:
                if not covers(FALLBACK, ch):
                    MISSING.add(ch)
                run.append(ch)
        if run:
            buf.append('<font name="%s">%s</font>' % (FALLBACK, "".join(run)))
        out.append("".join(buf))
    return "".join(out)


def plain(text):
    """Strip markup down to plain text (for bookmarks and the TOC)."""
    t = re.sub(r"\$\$?(.+?)\$\$?", r"\1", text or "")
    t = re.sub(r"`+", "", t)
    t = re.sub(r"\*+", "", t)
    t = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK.get(m.group(1), SYMBOLS.get(m.group(1), m.group(1))), t)
    t = re.sub(r"[{}]", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    for a, b in _ENTITIES:
        t = t.replace(a, b)
    t = _smart_quotes(t)
    return t.strip()
