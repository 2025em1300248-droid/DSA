"""Book-level structure: metadata, parts, and the chapter running order."""

BOOK = {
    "title": "Arrays & Linked Lists",
    "subtitle": "A complete beginner's course in data structures, in C++",
    "cover_title": ["Arrays", "& Linked", "Lists"],
    "cover_sub": ["A complete beginner's course in C++",
                  "Forty chapters, from what a variable is",
                  "to the hardest interview questions asked."],
    "kicker": "FROM ABSOLUTE ZERO TO INTERVIEW-READY",
    "author": "Written for the beginner who wants to understand, not memorise",
    "edition": "First edition · 2026",
    "tagline": ("You do not need to be clever to be good at this. You need to see "
                "what is happening in memory, one small step at a time. Every "
                "concept in this book is drawn before it is coded, traced before "
                "it is trusted, and practised before it is assumed."),
    "frontmatter": ["fm-how-to-read.md"],
}

PARTS = [
    {"n": 1, "roman": "I", "title": ["Before", "Anything Else"],
     "blurb": ["Three ideas hold up everything that follows: what a data",
               "structure is, what a computer's memory actually looks like,",
               "and how we measure whether an idea is fast or slow."],
     "chapters": ["01-what-is-a-data-structure.md",
                  "02-memory-and-addresses.md",
                  "03-big-o.md"]},

    {"n": 2, "roman": "II", "title": ["Arrays From", "the Ground Up"],
     "blurb": ["An array is a row of boxes in a straight line. That single",
               "sentence explains every strength it has and every weakness",
               "it will ever show you. We take it apart completely."],
     "chapters": ["04-the-array.md", "05-vectors.md",
                  "06-array-operations.md", "07-2d-arrays.md"]},

    {"n": 3, "roman": "III", "title": ["The Array", "Patterns"],
     "blurb": ["Almost every array problem you will ever be asked is one of",
               "ten shapes wearing a costume. Learn to see the shape and the",
               "problem stops being a puzzle and becomes a recognition task."],
     "chapters": ["08-linear-traversal.md", "09-two-pointers.md",
                  "10-sliding-window.md", "11-prefix-sums.md",
                  "12-binary-search.md", "13-in-place.md",
                  "14-frequency-counting.md", "15-sorting-based.md",
                  "16-kadane.md", "17-matrix-patterns.md"]},

    {"n": 4, "roman": "IV", "title": ["The Array", "Problem Set"],
     "blurb": ["Twenty-five problems, graded from your first day to a Google",
               "on-site, each one solved the long way first so that you can",
               "watch the short way being discovered rather than recited."],
     "chapters": ["18-problems-foundational.md", "19-problems-intermediate.md",
                  "20-problems-advanced.md"]},

    {"n": 5, "roman": "V", "title": ["Pointers", "and Memory"],
     "blurb": ["Linked lists are impossible without pointers and trivial with",
               "them. So we stop, and we learn pointers properly — addresses,",
               "the heap, nullptr, ownership and leaks — before going on."],
     "chapters": ["21-pointers.md", "22-stack-heap.md"]},

    {"n": 6, "roman": "VI", "title": ["Linked Lists", "From Scratch"],
     "blurb": ["We build the structure one node at a time, draw every pointer",
               "before we write it, and handle every empty-list and one-node",
               "case that has ever broken somebody's interview."],
     "chapters": ["23-linked-list-idea.md", "24-building-a-list.md",
                  "25-insertion.md", "26-deletion.md",
                  "27-doubly-circular.md", "28-reversal.md"]},

    {"n": 7, "roman": "VII", "title": ["Linked List Patterns", "and Problems"],
     "blurb": ["Dummy nodes, two speeds, and the courage to reverse things.",
               "Sixteen interview problems that between them cover almost",
               "every linked list question in circulation."],
     "chapters": ["29-ll-patterns.md", "30-ll-problems-core.md",
                  "31-ll-problems-intermediate.md",
                  "32-ll-problems-advanced.md"]},

    {"n": 8, "roman": "VIII", "title": ["Thinking Like", "a Problem Solver"],
     "blurb": ["The complete cost comparison of the two structures, a",
               "seventeen-step method that works on problems you have never",
               "seen, and the C++ habits that keep your code correct."],
     "chapters": ["33-complexity-showdown.md", "34-the-method.md",
                  "35-cpp-standards.md"]},

    {"n": 9, "roman": "IX", "title": ["Practice,", "Revision, Mastery"],
     "blurb": ["A five-level roadmap, quizzes and bug hunts after every",
               "chapter, a full answer key that explains rather than asserts,",
               "a mock interview, and a thirty-day plan to tie it together."],
     "chapters": ["36-roadmap.md", "37-exercises.md", "38-answer-key.md",
                  "39-mock-interview.md", "40-reference.md"]},
]
