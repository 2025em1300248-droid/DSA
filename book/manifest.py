"""Book-level structure: metadata, parts, and the chapter running order."""

BOOK = {
    "title": "Data Structures & Algorithms for AI/ML Engineers",
    "subtitle": "From first principles to production systems",
    "cover_title": ["Data Structures", "& Algorithms", "for AI/ML", "Engineers"],
    "cover_sub": ["From first principles to production systems",
                  "Forty-seven chapters, from counting operations",
                  "to serving a trillion-parameter model."],
    "kicker": "A COMPLETE, SELF-CONTAINED COURSE",
    "author": "Written for practitioners who train and serve models",
    "edition": "First edition · 2026",
    "tagline": ("Most algorithms books teach you to pass an interview. This one "
                "teaches you to make a training run finish, a retrieval index "
                "fit in memory, and a decoder answer in under a second — "
                "and, along the way, to pass the interview anyway."),
    "frontmatter": ["fm-how-to-read.md"],
}

PARTS = [
    {"n": 1, "roman": "I", "title": ["Foundations:", "The Cost of Everything"],
     "blurb": ["Before any data structure, a mental model of what a computer",
               "actually charges you for — operations, memory traffic,",
               "and the distance between a number and the arithmetic unit."],
     "chapters": ["01-why-algorithms.md", "02-complexity.md",
                  "03-memory-machine.md", "04-arrays-strides.md",
                  "05-strings-tokens.md"]},

    {"n": 2, "roman": "II", "title": ["The Core Toolkit"],
     "blurb": ["The seven structures and four techniques that appear in",
               "every pipeline you will ever write, taught properly:",
               "what they cost, when they break, and how they are really used."],
     "chapters": ["06-linked-stacks-queues.md", "07-hashing.md",
                  "08-recursion-memoization.md", "09-sorting.md",
                  "10-binary-search.md", "11-two-pointers-windows.md"]},

    {"n": 3, "roman": "III", "title": ["Hierarchies", "and Priorities"],
     "blurb": ["Trees give you ordered access in logarithmic time; heaps give",
               "you the best element now. Between them they power every",
               "index, every top-k, and every tokenizer in production."],
     "chapters": ["12-trees.md", "13-heaps-topk.md", "14-tries-automata.md",
                  "15-union-find.md"]},

    {"n": 4, "roman": "IV", "title": ["Algorithm", "Design Paradigms"],
     "blurb": ["Four ways to turn a problem you cannot solve into problems",
               "you can: split it, commit to the locally best move, remember",
               "subproblems, or search with the courage to undo."],
     "chapters": ["16-divide-conquer.md", "17-greedy.md", "18-dp-method.md",
                  "19-dp-sequences-ml.md", "20-backtracking.md",
                  "21-randomized.md"]},

    {"n": 5, "roman": "V", "title": ["Graphs"],
     "blurb": ["A graph is what you get when relationships matter more than",
               "order. Computation graphs, knowledge graphs, retrieval graphs,",
               "and the scheduler that runs your training job are all graphs."],
     "chapters": ["22-graph-basics.md", "23-shortest-paths.md",
                  "24-dags-autograd.md", "25-flows-matching.md",
                  "26-graphs-in-ml.md"]},

    {"n": 6, "roman": "VI", "title": ["Data Structures", "for Scale"],
     "blurb": ["When the data no longer fits — in cache, in RAM, on one",
               "machine — exactness becomes negotiable. These structures",
               "trade a little accuracy for orders of magnitude of capacity."],
     "chapters": ["27-segment-fenwick.md", "28-sketches.md", "29-lsh-dedup.md",
                  "30-suffix-structures.md", "31-disk-structures.md"]},

    {"n": 7, "roman": "VII", "title": ["Algorithms at the Heart", "of Modern ML"],
     "blurb": ["The algorithms that make embeddings searchable, samplers fast,",
               "decoders cheap and tree models accurate. This is the part",
               "no general algorithms textbook contains."],
     "chapters": ["32-nearest-neighbour.md", "33-vector-search.md",
                  "34-sampling.md", "35-decoding.md", "36-kv-cache.md",
                  "37-tree-learners.md", "38-streaming.md"]},

    {"n": 8, "roman": "VIII", "title": ["Parallel, Distributed", "and Hardware-Aware"],
     "blurb": ["One core is a special case. Modern ML runs on thousands of",
               "them, and the winning algorithm is the one that moves the",
               "least data, not the one that does the fewest operations."],
     "chapters": ["39-parallel-primitives.md", "40-gpu-algorithms.md",
                  "41-distributed.md", "42-external-memory.md"]},

    {"n": 9, "roman": "IX", "title": ["Mastery"],
     "blurb": ["A method for attacking unseen problems, a catalogue of the",
               "patterns that cover most of them, a graded problem set with",
               "full solutions, and a study plan that fits around a job."],
     "chapters": ["43-problem-solving.md", "44-pattern-catalogue.md",
                  "45-problems-foundations.md", "46-problems-advanced.md",
                  "47-study-plan-reference.md"]},
]
