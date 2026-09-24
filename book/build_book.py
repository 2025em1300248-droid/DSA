#!/usr/bin/env python3
"""Build the book PDF from the content directory."""
import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.platypus import (CondPageBreak, KeepTogether, NextPageTemplate,
                                PageBreak, Paragraph, Spacer)  # noqa: F401

from engine.doc import BookDoc, make_toc
from engine.flowables import Anchor, HRule, RunningState, callout
from engine.markup import MISSING, inline, plain
from engine.pages import (Chips, chapter_opener, cover, part_page, title_page)
from engine.parser import Ctx, collect_figures, parse_file, render, scan
from engine.style import C, FRAME_W, SANS, SANS_SB, SERIF, SERIF_I, styles
import figures  # noqa: F401  (registers all diagrams)
from manifest import BOOK, PARTS

CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")


def load_chapter(path):
    blocks = parse_file(path)
    meta, body = {}, []
    for b in blocks:
        if b["t"] == "h1":
            meta["title"] = b["text"]
        elif b["t"] == "meta":
            if b["body"]:
                meta[b["key"]] = b["body"]
            else:
                meta[b["key"]] = b["value"]
        else:
            body.append(b)
    return meta, body


def build(out_path, only=None, quick=False):
    ss = styles()
    doc = BookDoc(out_path, title=BOOK["title"], subtitle=BOOK["subtitle"],
                  author=BOOK["author"])

    chapters = []
    number = 0
    for part in PARTS:
        part_chaps = []
        for fname in part["chapters"]:
            number += 1
            path = os.path.join(CONTENT, fname)
            if not os.path.exists(path):
                print("  ! missing %s" % fname)
                continue
            meta, body = load_chapter(path)
            part_chaps.append((number, meta, body, fname))
        chapters.append((part, part_chaps))

    # Pass 0: figure numbering
    fig_numbers = {}
    for part, part_chaps in chapters:
        for num, meta, body, fname in part_chaps:
            ctx = Ctx(chapter=num, fig_numbers=fig_numbers)
            collect_figures(body, ctx)

    story = []
    story += cover(BOOK["cover_title"], BOOK["cover_sub"], BOOK["kicker"],
                   BOOK["author"], BOOK["edition"])
    story += [NextPageTemplate("cover"), PageBreak()]
    story += title_page(BOOK["cover_title"], BOOK["cover_sub"], BOOK["author"],
                        BOOK["edition"], BOOK["tagline"])
    story += [NextPageTemplate("front"), PageBreak()]

    for fm in BOOK["frontmatter"]:
        path = os.path.join(CONTENT, fm)
        if not os.path.exists(path):
            continue
        meta, body = load_chapter(path)
        story.append(RunningState(part=BOOK["title"],
                                  chapter=plain(meta.get("title", "")),
                                  short=plain(meta.get("title", ""))))
        story.append(Anchor(0, meta.get("title", ""), "fm-" + fm))
        st = ss["h1"].clone("fmh")
        st.fontSize = 21
        st.leading = 25
        story.append(Paragraph(inline(meta.get("title", "")), st))
        story.append(HRule(color=C.primary, thickness=1.6, space_before=8,
                           space_after=12, width=90))
        ctx = Ctx(chapter=0, fig_numbers=fig_numbers, toc=False)
        fm_story = render(body, ctx)
        while fm_story and isinstance(fm_story[-1], Spacer):
            fm_story.pop()
        story += fm_story
        story.append(PageBreak())

    # Contents at a glance, then the full table of contents
    story.append(RunningState(part=BOOK["title"], chapter="Contents",
                              short="Contents"))
    st = ss["h1"].clone("toch")
    st.fontSize = 21
    st.leading = 25
    story.append(Paragraph("Contents at a Glance", st))
    story.append(HRule(color=C.primary, thickness=1.6, space_before=8,
                       space_after=14, width=90))
    story.append(make_toc(doc, max_level=1, glance=True))
    story.append(PageBreak())
    story.append(Paragraph("Contents", st))
    story.append(HRule(color=C.primary, thickness=1.6, space_before=8,
                       space_after=14, width=90))
    story.append(make_toc(doc, max_level=2))
    story.append(NextPageTemplate("part"))
    story.append(PageBreak())

    from engine.flowables import Callback
    story.append(Callback(doc.mark_arabic_start))

    last_part = len(chapters) - 1
    for pi, (part, part_chaps) in enumerate(chapters):
        toc_list = [(n, plain(m.get("title", ""))) for n, m, _, _ in part_chaps]
        story += part_page(part["n"], part["roman"], part["title"],
                           part["blurb"], toc_list, part.get("motif"))
        story.append(NextPageTemplate("opener"))
        story.append(PageBreak())
        last_ch = len(part_chaps) - 1
        for ci, (num, meta, body, fname) in enumerate(part_chaps):
            story.append(RunningState(
                part="PART %s \u00b7 %s" % (part["roman"], " ".join(part["title"]))))
            story += chapter_opener(
                num, meta.get("title", ""), meta.get("subtitle"),
                meta.get("blurb"), meta.get("objectives"),
                meta.get("tier", "core"), meta.get("prereq"))
            ctx = Ctx(chapter=num, fig_numbers=fig_numbers)
            chapter_story = render(body, ctx)
            while chapter_story and isinstance(chapter_story[-1], Spacer):
                chapter_story.pop()          # no trailing glue before a break
            story += chapter_story
            if pi == last_part and ci == last_ch:
                break
            story.append(NextPageTemplate("part" if ci == last_ch else "opener"))
            story.append(PageBreak())

    t0 = time.time()
    doc.multiBuild(story)
    doc.finish_pass()
    print("  built %s in %.1fs" % (out_path, time.time() - t0))
    if MISSING:
        print("  ! glyphs with no font: %s" % "".join(sorted(MISSING)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="../build/DSA-for-AI-ML-Engineers.pdf")
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    out = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       args.out))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out, only=args.only)
