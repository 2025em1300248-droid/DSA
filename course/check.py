#!/usr/bin/env python3
"""Content linter: catches the authoring mistakes this engine renders badly."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "book"))
sys.path.insert(0, HERE)

from engine.parser import FIGURES, parse_file          # noqa: E402
import figures                                         # noqa: F401,E402
from manifest import BOOK, PARTS                       # noqa: E402

CONTENT = os.path.join(HERE, "content")
problems = []


def err(fname, msg):
    problems.append("%-34s %s" % (fname, msg))


def walk(blocks, fname, in_callout=False):
    """Recursively check parsed blocks."""
    for b in blocks:
        t = b["t"]
        if t == "callout":
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

        # raw-text checks the parser cannot see
        for n, line in enumerate(raw.split("\n"), 1):
            if re.match(r"^@fig\s+\w", line):
                err(f, "line %d: '@fig name' should be '@fig: name'" % n)
            if re.match(r"^@(tbl|cols|tsize)\s+\w", line):
                err(f, "line %d: missing colon after @%s"
                    % (n, line.split()[0][1:]))
            if "\t" in line:
                err(f, "line %d: literal tab character" % n)
        if raw.count("```") % 2:
            err(f, "odd number of ``` fences")

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
