"""
Design system for the book: fonts, palette, page geometry, paragraph styles.

Everything visual is defined here so the look of the whole book can be tuned
from one file.
"""
import os
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

# --------------------------------------------------------------------------
# Page geometry
# --------------------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN_L = 94.0
MARGIN_R = 94.0
MARGIN_T = 60.0
MARGIN_B = 64.0
FRAME_W = PAGE_W - MARGIN_L - MARGIN_R          # ~407 pt
FRAME_H = PAGE_H - MARGIN_T - MARGIN_B

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
class C:
    ink        = HexColor("#14161A")
    body       = HexColor("#22252B")
    muted      = HexColor("#6A7180")
    faint      = HexColor("#9AA1AE")
    rule       = HexColor("#D9DEE5")
    hairline   = HexColor("#E8ECF1")
    paper      = HexColor("#FFFFFF")

    primary    = HexColor("#16466E")   # deep navy - structure, headings
    primary_lt = HexColor("#EAF0F6")
    primary_md = HexColor("#B9CCDF")

    teal       = HexColor("#0E6E63")   # insight / intuition
    teal_lt    = HexColor("#E6F3F1")
    teal_md    = HexColor("#A8D5CE")

    violet     = HexColor("#5B2E90")   # ML connection
    violet_lt  = HexColor("#F1EBF9")
    violet_md  = HexColor("#C9B2E4")

    crimson    = HexColor("#9C1B3B")   # pitfall / warning
    crimson_lt = HexColor("#FBEAEE")
    crimson_md = HexColor("#E7B3C1")

    amber      = HexColor("#9A5B06")   # performance / hardware
    amber_lt   = HexColor("#FBF1E2")
    amber_md   = HexColor("#E8C894")

    slate      = HexColor("#3D4756")   # theorem / proof
    slate_lt   = HexColor("#EEF1F5")
    slate_md   = HexColor("#C2CAD6")

    green      = HexColor("#1F6134")   # exercises / practice
    green_lt   = HexColor("#E9F4EC")
    green_md   = HexColor("#AFD3BA")

    code_bg    = HexColor("#F7F8FA")
    code_bd    = HexColor("#E3E7ED")
    code_gut   = HexColor("#AEB6C2")

    tbl_head   = HexColor("#16466E")
    tbl_zebra  = HexColor("#F4F7FA")

# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------
SERIF      = "Serif"
SERIF_B    = "Serif-Bold"
SERIF_I    = "Serif-It"
SERIF_BI   = "Serif-BoldIt"
SERIF_SB   = "Serif-Semi"
SERIF_SBI  = "Serif-SemiIt"
SERIF_LT   = "Serif-Light"

SANS       = "Sans"
SANS_B     = "Sans-Bold"
SANS_I     = "Sans-It"
SANS_BI    = "Sans-BoldIt"
SANS_SB    = "Sans-Semi"
SANS_SBI   = "Sans-SemiIt"
SANS_LT    = "Sans-Light"
SANS_BLK   = "Sans-Black"

MONO       = "Mono"
MONO_B     = "Mono-Bold"
MONO_I     = "Mono-It"
MONO_BI    = "Mono-BoldIt"

FALLBACK   = "Fallback"
FALLBACK_B = "Fallback-Bold"

_REGISTERED = False


def register_fonts():
    global _REGISTERED
    if _REGISTERED:
        return
    spec = [
        (SERIF,     "SourceSerifPro-Regular.ttf"),
        (SERIF_B,   "SourceSerifPro-Bold.ttf"),
        (SERIF_I,   "SourceSerifPro-It.ttf"),
        (SERIF_BI,  "SourceSerifPro-BoldIt.ttf"),
        (SERIF_SB,  "SourceSerifPro-Semibold.ttf"),
        (SERIF_SBI, "SourceSerifPro-SemiboldIt.ttf"),
        (SERIF_LT,  "SourceSerifPro-Light.ttf"),
        (SANS,      "SourceSansPro-Regular.ttf"),
        (SANS_B,    "SourceSansPro-Bold.ttf"),
        (SANS_I,    "SourceSansPro-It.ttf"),
        (SANS_BI,   "SourceSansPro-BoldIt.ttf"),
        (SANS_SB,   "SourceSansPro-Semibold.ttf"),
        (SANS_SBI,  "SourceSansPro-SemiboldIt.ttf"),
        (SANS_LT,   "SourceSansPro-Light.ttf"),
        (SANS_BLK,  "SourceSansPro-Black.ttf"),
        (MONO,      "DejaVuSansMono.ttf"),
        (MONO_B,    "DejaVuSansMono-Bold.ttf"),
        (MONO_I,    "DejaVuSansMono-Oblique.ttf"),
        (MONO_BI,   "DejaVuSansMono-BoldOblique.ttf"),
        (FALLBACK,  "DejaVuSans.ttf"),
        (FALLBACK_B,"DejaVuSans-Bold.ttf"),
    ]
    for name, fn in spec:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))

    for base, r, b, i, bi in [
        ("Serif", SERIF, SERIF_B, SERIF_I, SERIF_BI),
        ("Sans", SANS, SANS_B, SANS_I, SANS_BI),
        ("Mono", MONO, MONO_B, MONO_I, MONO_BI),
        ("Serif-Semi", SERIF_SB, SERIF_B, SERIF_SBI, SERIF_BI),
        ("Sans-Semi", SANS_SB, SANS_B, SANS_SBI, SANS_BI),
        ("Fallback", FALLBACK, FALLBACK_B, FALLBACK, FALLBACK_B),
    ]:
        pdfmetrics.registerFontFamily(base, normal=r, bold=b, italic=i, boldItalic=bi)
    _REGISTERED = True


# Glyph coverage, used by the inline-markup layer to patch in a fallback font
# for symbols the Source families do not carry (set theory, logic, arrows).
_COVERAGE = {}


def covers(font_name, ch):
    cov = _COVERAGE.get(font_name)
    if cov is None:
        register_fonts()
        face = pdfmetrics.getFont(font_name).face
        cov = set(getattr(face, "charToGlyph", {}).keys())
        _COVERAGE[font_name] = cov
    return ord(ch) in cov


# --------------------------------------------------------------------------
# Type scale
# --------------------------------------------------------------------------
BODY_SIZE = 10.3
BODY_LEAD = 15.4

def _p(name, **kw):
    kw.setdefault("fontName", SERIF)
    kw.setdefault("fontSize", BODY_SIZE)
    kw.setdefault("leading", BODY_LEAD)
    kw.setdefault("textColor", C.body)
    return ParagraphStyle(name, **kw)


def build_styles():
    register_fonts()
    ss = StyleSheet1()

    ss.add(_p("body", alignment=TA_JUSTIFY, spaceAfter=0, spaceBefore=0,
              firstLineIndent=0, hyphenationLang="en_US"))
    ss.add(_p("body-first", parent=ss["body"], alignment=TA_JUSTIFY, spaceBefore=0))
    ss.add(_p("body-cont", parent=ss["body"], alignment=TA_JUSTIFY, spaceBefore=7.5))
    ss.add(_p("lead", fontSize=11.6, leading=17.4, textColor=C.ink,
              alignment=TA_LEFT, spaceBefore=0, spaceAfter=0, fontName=SERIF_LT))

    ss.add(_p("h1", fontName=SANS_BLK, fontSize=25, leading=29, textColor=C.ink,
              alignment=TA_LEFT, spaceBefore=0, spaceAfter=0))
    ss.add(_p("h2", fontName=SANS_B, fontSize=15.2, leading=19, textColor=C.primary,
              alignment=TA_LEFT, spaceBefore=19, spaceAfter=5.5, keepWithNext=1))
    ss.add(_p("h3", fontName=SANS_SB, fontSize=11.9, leading=15.5, textColor=C.ink,
              alignment=TA_LEFT, spaceBefore=13, spaceAfter=3.5, keepWithNext=1))
    ss.add(_p("h4", fontName=SERIF_BI, fontSize=10.7, leading=14.5, textColor=C.slate,
              alignment=TA_LEFT, spaceBefore=10, spaceAfter=2, keepWithNext=1))

    ss.add(_p("bullet", alignment=TA_LEFT, spaceBefore=2.2, spaceAfter=0,
              leftIndent=15, bulletIndent=3, leading=15.0))
    ss.add(_p("bullet2", parent=ss["bullet"], leftIndent=30, bulletIndent=18,
              fontSize=BODY_SIZE - 0.2, leading=14.4))
    ss.add(_p("number", alignment=TA_LEFT, spaceBefore=2.2, spaceAfter=0,
              leftIndent=19, bulletIndent=3, leading=15.0))
    ss.add(_p("number2", parent=ss["number"], leftIndent=36, bulletIndent=20,
              fontSize=BODY_SIZE - 0.2, leading=14.4))

    ss.add(_p("quote", fontName=SERIF_I, fontSize=10.3, leading=15.2,
              textColor=C.slate, leftIndent=16, rightIndent=10,
              spaceBefore=8, spaceAfter=8))
    ss.add(_p("quote-attr", fontName=SANS, fontSize=8.8, leading=12,
              textColor=C.muted, leftIndent=16, alignment=TA_LEFT))

    ss.add(_p("callout-title", fontName=SANS_B, fontSize=8.6, leading=11.5,
              textColor=C.primary, spaceAfter=3.5))
    ss.add(_p("callout-body", fontSize=9.7, leading=14.1, alignment=TA_LEFT,
              textColor=C.body))
    ss.add(_p("callout-bullet", parent=ss["callout-body"], leftIndent=13,
              bulletIndent=2, spaceBefore=2))
    ss.add(_p("callout-number", parent=ss["callout-body"], leftIndent=17,
              bulletIndent=2, spaceBefore=2))

    ss.add(_p("code", fontName=MONO, fontSize=8.2, leading=11.4,
              textColor=C.ink, alignment=TA_LEFT))
    ss.add(_p("code-sm", parent=ss["code"], fontSize=7.5, leading=10.5))
    ss.add(_p("gutter", fontName=MONO, fontSize=7.0, leading=11.4,
              textColor=C.code_gut, alignment=TA_RIGHT))
    ss.add(_p("gutter-sm", parent=ss["gutter"], fontSize=6.5, leading=10.5))
    ss.add(_p("caption", fontName=SANS, fontSize=8.5, leading=11.8,
              textColor=C.muted, alignment=TA_LEFT, spaceBefore=5))
    ss.add(_p("code-title", fontName=SANS_SB, fontSize=8.3, leading=11,
              textColor=C.muted, alignment=TA_LEFT))

    ss.add(_p("th", fontName=SANS_SB, fontSize=8.6, leading=11.4,
              textColor=C.paper, alignment=TA_LEFT))
    ss.add(_p("td", fontName=SERIF, fontSize=8.9, leading=12.2,
              textColor=C.body, alignment=TA_LEFT))
    ss.add(_p("td-c", parent=ss["td"], alignment=TA_CENTER))
    ss.add(_p("td-mono", fontName=MONO, fontSize=7.8, leading=12.2,
              textColor=C.body, alignment=TA_LEFT))

    ss.add(_p("math", fontName=SERIF_I, fontSize=10.6, leading=16,
              textColor=C.ink, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8))

    ss.add(_p("toc1", fontName=SANS_B, fontSize=10.2, leading=15,
              textColor=C.ink, spaceBefore=9))
    ss.add(_p("toc2", fontName=SERIF, fontSize=9.5, leading=13.4,
              textColor=C.body, leftIndent=14, spaceBefore=1.2))
    ss.add(_p("toc3", fontName=SERIF, fontSize=8.8, leading=12.2,
              textColor=C.muted, leftIndent=30, spaceBefore=0.4))
    ss.add(_p("toc0", fontName=SANS_BLK, fontSize=11.5, leading=16,
              textColor=C.primary, spaceBefore=16, spaceAfter=2))

    ss.add(_p("chapnum", fontName=SANS_BLK, fontSize=9, leading=11,
              textColor=C.primary))
    ss.add(_p("running", fontName=SANS, fontSize=7.6, leading=9,
              textColor=C.faint))
    ss.add(_p("center", alignment=TA_CENTER))
    return ss


STYLES = None


def styles():
    global STYLES
    if STYLES is None:
        STYLES = build_styles()
    return STYLES
