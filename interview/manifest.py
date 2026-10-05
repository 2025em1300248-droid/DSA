"""Structure of the plain-English interview answer book."""

BOOK = {
    "title": "Say It Simply",
    "subtitle": "627 interview answers in plain English",
    "cover_title": ["Say It", "Simply"],
    "cover_sub": ["627 AI/ML interview questions,",
                  "answered in words you can",
                  "actually say out loud."],
    "kicker": "THE PLAIN-ENGLISH ANSWER BOOK",
    "author": "Prepared for Ayush Poojari",
    "edition": "First edition · 2026",
    "tagline": ("Every answer here is written the way you would say it to a "
                "person, not the way a textbook would write it. Short "
                "sentences, ordinary words, and nothing you cannot defend "
                "in a follow-up question."),
    "frontmatter": ["fm-how-to-use.md"],
}

PARTS = [
    {"n": 1, "roman": "I", "title": ["The Conversation"],
     "blurb": ["The questions that are not about technology at all, and",
               "the ones that attack the numbers on your own resume.",
               "These decide more interviews than the technical rounds do."],
     "chapters": ["01-opening-questions.md", "02-your-resume.md"]},

    {"n": 2, "roman": "II", "title": ["The Programming", "Rounds"],
     "blurb": ["Python first, then the databases and the language you",
               "listed but have not shipped. Short answers. Say the",
               "sentence, then stop."],
     "chapters": ["03-python.md", "04-sql-cpp-mongo.md"]},

    {"n": 3, "roman": "III", "title": ["Data and", "Classical ML"],
     "blurb": ["Statistics, handling real data, the classic algorithms,",
               "and how you prove a model is any good. The most",
               "reliably asked block in the whole interview."],
     "chapters": ["05-statistics.md", "06-pandas-and-data.md",
                  "07-classical-ml.md", "08-imbalance-and-metrics.md"]},

    {"n": 4, "roman": "IV", "title": ["Deep Learning", "and Vision"],
     "blurb": ["Neural networks from the forward pass to the training",
               "loop, then the vision stack your strongest project is",
               "built on."],
     "chapters": ["09-deep-learning.md", "10-cnn-and-vision.md"]},

    {"n": 5, "roman": "V", "title": ["Language Models"],
     "blurb": ["How a transformer works, how retrieval works, and how",
               "to talk about agents without overclaiming. Two of your",
               "projects live here."],
     "chapters": ["11-nlp-and-transformers.md", "12-embeddings-and-rag.md",
                  "13-prompting-and-agents.md"]},

    {"n": 6, "roman": "VI", "title": ["Shipping It"],
     "blurb": ["Containers, pipelines, APIs, version control and system",
               "design. The half of the job that turns a notebook into",
               "something a company can run."],
     "chapters": ["14-mlops.md", "15-apis-and-git.md", "16-system-design.md"]},

    {"n": 7, "roman": "VII", "title": ["Your Work and", "the Last Mile"],
     "blurb": ["Your four projects, defended question by question; the",
               "coding screen; what to ask them; and the checklist for",
               "the morning of the interview."],
     "chapters": ["17-your-projects.md", "18-coding-round.md",
                  "19-asking-and-checklist.md"]},
]
