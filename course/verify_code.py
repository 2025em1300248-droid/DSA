#!/usr/bin/env python3
"""Compile — and where possible run — every C++ block in the book.

Conventions used in the content files, written in the fence options line:

    ```cpp                 a complete program (has int main) or a set of
                           function definitions; always compiled
    ```cpp frag            a bare statement fragment; wrapped in a harness
    ```cpp norun           compile only (output varies between runs)
    ```cpp skip            not checked (deliberately non-compiling examples)

A complete program whose next block is a ```text block is also RUN, and its
real output is diffed against the text block. That is what keeps the printed
outputs in this book honest.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
FENCE = re.compile(r"^```(\w*)(.*)$")

PRELUDE = """#include <algorithm>
#include <climits>
#include <cmath>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <deque>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <set>
#include <stack>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
"""

HARNESS_VARS = """
static void work() {}
static void doSomething(int, int) {}
static void process(int) {}
static void deleteAt(std::vector<int>&, int) {}
static void insertAt(std::vector<int>&, int, int) {}
static bool keep(int) { return true; }
"""

# Added only to blocks that do not define their own Node.
NODE_DEF = """
struct Node {
    int data;
    Node* next;
    Node(int value) { data = value; next = nullptr; }
};
static Node* findNode(Node*, int) { return nullptr; }
static Node* buildList(std::vector<int>) { return nullptr; }
static void printList(Node*) {}
static void freeList(Node*) {}
"""


def blocks_of(path):
    """Yield (lang, opts, source, line_number) for every fenced block."""
    out = []
    lines = open(path, encoding="utf-8").read().split("\n")
    i, n = 0, len(lines)
    while i < n:
        m = FENCE.match(lines[i])
        if m:
            lang, opts, start = m.group(1) or "text", m.group(2).strip(), i + 1
            body, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            out.append((lang, opts, "\n".join(body), start))
        i += 1
    return out


def wrap(src, opts):
    """Turn a block into a complete translation unit."""
    has_main = re.search(r"\bint\s+main\s*\(", src) is not None
    prelude = "" if "#include" in src else PRELUDE
    # a block that defines its own Node must not get the harness one
    stubs = HARNESS_VARS + ("" if "struct Node" in src else NODE_DEF)
    if has_main:
        return prelude + src + "\n"
    if "frag" in opts:
        body = "\n".join("    " + ln for ln in src.split("\n"))
        return (PRELUDE + stubs +
                "int main() {\n"
                "    std::vector<int> v{3, 1, 4, 1, 5, 9, 2, 6};\n"
                "    std::vector<int> nums = v, arr = v, in = v, out;\n"
                "    std::vector<std::vector<int>> g(4, std::vector<int>(4, 1));\n"
                "    std::vector<std::vector<int>> grid = g, tri = g;\n"
                "    int R = 4, C = 4; (void)R; (void)C;\n"
                "    std::vector<long long> prefix(9, 0); (void)prefix;\n"
                "    std::unordered_map<long long,int> seen; (void)seen;\n"
                "    std::unordered_map<int,int> freq{{4,3}}; (void)freq;\n"
                "    (void)g; (void)grid; (void)tri;\n"
                "    int n = (int)v.size(), target = 7, i = 0, j = 0;\n"
                "    int x = 0, total = 0, s = 0, l = 0, best = 0, k = 2;\n"
                "    int current = 0, count = 0, w = 0, r = 0, lo = 0, hi = 0;\n"
                "    (void)current; (void)count; (void)w; (void)r;\n"
                "    (void)lo; (void)hi;\n"
                "    (void)n; (void)target; (void)i; (void)j; (void)x;\n"
                "    (void)total; (void)s; (void)l; (void)best; (void)k;\n"
                "    (void)nums; (void)arr; (void)in; (void)out;\n"
                "    Node* head = nullptr; Node* curr = head;\n"
                "    Node* prev = nullptr; Node* tail = nullptr;\n"
                "    Node* node = nullptr; Node* temp = nullptr;\n"
                "    (void)head; (void)curr; (void)prev; (void)tail;\n"
                "    (void)node; (void)temp;\n"
                "    int* p = nullptr; int* q = nullptr; (void)p; (void)q;\n"
                "    {\n" + body + "\n    }\n"
                "    return 0;\n}\n")
    return prelude + stubs + src + "\nint main() { return 0; }\n"


def main():
    only = sys.argv[1:] or sorted(f for f in os.listdir(CONTENT)
                                  if f.endswith(".md"))
    fails, compiled, ran = [], 0, 0
    tmp = tempfile.mkdtemp(prefix="dsa-cpp-")

    for fname in only:
        path = os.path.join(CONTENT, fname)
        bs = blocks_of(path)
        for idx, (lang, opts, src, line) in enumerate(bs):
            if lang != "cpp" or "skip" in opts or not src.strip():
                continue
            where = "%s:%d" % (fname, line)
            unit = wrap(src, opts)
            cpp = os.path.join(tmp, "u%d.cpp" % (len(fails) + compiled))
            exe = cpp[:-4]
            open(cpp, "w").write(unit)
            r = subprocess.run(
                ["g++", "-std=c++17", "-O0", "-w", cpp, "-o", exe],
                capture_output=True, text=True)
            if r.returncode:
                fails.append((where, "compile error", r.stderr.strip()[:1400]))
                continue
            compiled += 1

            # Run it when an expected-output block follows.
            if "norun" in opts or not re.search(r"\bint\s+main\s*\(", src):
                continue
            nxt = bs[idx + 1] if idx + 1 < len(bs) else None
            if not nxt or nxt[0] != "text":
                continue
            rr = subprocess.run([exe], capture_output=True, text=True,
                                timeout=20)
            got = rr.stdout.rstrip("\n")
            want = nxt[2].rstrip("\n")
            ran += 1
            if got != want:
                fails.append((where, "output mismatch",
                              "--- expected ---\n%s\n--- actual ---\n%s"
                              % (want, got)))

    print("compiled %d block(s); ran and diffed %d program(s)" % (compiled, ran))
    if fails:
        print("\n%d FAILURE(S):" % len(fails))
        for where, kind, detail in fails:
            print("\n=== %s — %s ===\n%s" % (where, kind, detail))
        return 1
    print("all C++ in the book compiles, and every printed output matches.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
