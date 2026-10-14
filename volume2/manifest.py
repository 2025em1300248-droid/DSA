"""Volume 2: metadata, parts, and the chapter running order."""

BOOK = {
    "title": "Strings, Hashing & the Window Patterns",
    "subtitle": "Volume 2 of a complete DSA course, in C++17",
    "cover_title": ["Strings,", "Hashing &", "the Window", "Patterns"],
    "cover_sub": ["Volume 2 of a complete DSA course, in C++17",
                  "Twenty-five chapters: what a character really is,",
                  "how a hash table reaches O(1), and the four",
                  "window shapes that cover most of the rest."],
    "kicker": "VOLUME 2 · BEGINNER TO INTERVIEW COMPETENCE",
    "author": "Written for the beginner who wants to understand, not memorise",
    "edition": "First edition · 2026",
    "tagline": ("Volume 1 taught you to see memory. This one teaches you to see "
                "text, and to recognise the four shapes — hash, prefix, two "
                "pointers, window — that between them solve more interview "
                "problems than every other technique combined."),
    "frontmatter": ["fm-how-to-read.md", "fm-the-course.md"],
}

PARTS = [
    {"n": 1, "roman": "I", "title": ["Strings From", "the Ground Up"],
     "blurb": ["A string is an array of small integers with a cultural",
               "convention attached. Take that sentence apart and every",
               "surprising thing C++ strings do becomes predictable."],
     "chapters": ["01-what-is-a-string.md", "02-std-string.md",
                  "03-building-strings.md", "04-chars-as-numbers.md",
                  "05-beyond-ascii.md"]},

    {"n": 2, "roman": "II", "title": ["Hashing"],
     "blurb": ["A hash table turns “have I seen this?” from a search into a",
               "calculation. It is the single highest-leverage structure in",
               "interview work, and the one most often used without understanding."],
     "chapters": ["06-hash-table-idea.md", "07-unordered-containers.md",
                  "08-keys.md", "09-hashing-goes-wrong.md"]},

    {"n": 3, "roman": "III", "title": ["Prefix", "Techniques"],
     "blurb": ["Pay once, answer forever. Prefix structures precompute a",
               "running summary so that any range question afterwards is a",
               "subtraction — and they generalise far past sums."],
     "chapters": ["10-prefix-generalised.md", "11-difference-arrays.md",
                  "12-prefix-plus-hash.md"]},

    {"n": 4, "roman": "IV", "title": ["Two Pointers"],
     "blurb": ["Two indices moving with purpose. Volume 1 introduced the",
               "shape on integer arrays; here it is completed, proved, and",
               "applied to text, partitioning and in-place rewriting."],
     "chapters": ["13-two-pointers-complete.md", "14-in-place-strings.md"]},

    {"n": 5, "roman": "V", "title": ["The Sliding", "Window"],
     "blurb": ["Four window shapes — fixed, variable, at-most-K and minimum",
               "— cover an enormous share of string and array problems.",
               "Each is one template with one condition changed."],
     "chapters": ["15-fixed-window.md", "16-variable-window.md",
                  "17-at-most-k.md", "18-minimum-window.md"]},

    {"n": 6, "roman": "VI", "title": ["The Problem Set"],
     "blurb": ["Thirty problems, every one derived from its brute force.",
               "The eleven canonical strings-and-hashing questions, the six",
               "window questions, and the combinations that need both."],
     "chapters": ["19-problems-strings-hashing.md", "20-problems-windows.md",
                  "21-problems-combined.md"]},

    {"n": 7, "roman": "VII", "title": ["Practice", "and Reference"],
     "blurb": ["Pattern-recognition drills, five kinds of exercise, a full",
               "answer key that explains rather than asserts, and the",
               "sixteen-week plan for the whole course."],
     "chapters": ["22-pattern-drills.md", "23-exercises.md",
                  "24-answer-key.md", "25-reference.md"]},
]
