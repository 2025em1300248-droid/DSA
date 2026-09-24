"""Structure of the skill-map companion volume."""

BOOK = {
    "title": "The AI/ML Engineer Skill Map",
    "subtitle": "Every competency that matters, and the order to acquire them",
    "cover_title": ["The AI/ML", "Engineer", "Skill Map"],
    "cover_sub": ["Every competency that matters in 2026,",
                  "what changed, what is obsolete,",
                  "and the order to acquire them."],
    "kicker": "A COMPLETE, CURRENT COMPETENCY MAP",
    "author": "A companion to Data Structures & Algorithms for AI/ML Engineers",
    "edition": "First edition · 2026",
    "tagline": ("Most roadmaps list technologies. This one lists capabilities: "
                "what you must be able to *do*, how to tell whether you can do "
                "it, what each skill is worth on the job market, and which "
                "widely-taught skills have quietly stopped mattering."),
    "frontmatter": ["fm-how-to-use.md"],
}

PARTS = [
    {"n": 1, "roman": "I", "title": ["The Landscape"],
     "blurb": ["“AI/ML engineer” now covers five distinct jobs with",
               "different skill profiles. Before learning anything, work out",
               "which one you are aiming at — the answer changes everything."],
     "chapters": ["01-the-five-roles.md", "02-how-to-use-this-map.md"]},

    {"n": 2, "roman": "II", "title": ["Foundations"],
     "blurb": ["The layer nobody can skip. Weakness here caps you at",
               "“can follow a tutorial” forever, and it is the most",
               "common reason strong candidates fail technical screens."],
     "chapters": ["03-python-and-engineering.md", "04-mathematics.md",
                  "05-algorithms-and-systems.md"]},

    {"n": 3, "roman": "III", "title": ["Data"],
     "blurb": ["Models are commodities; data pipelines are not. This is",
               "where most of the hours go and where most of the",
               "irreproducible results come from."],
     "chapters": ["06-data-engineering.md", "07-dataset-curation.md"]},

    {"n": 4, "roman": "IV", "title": ["Modelling"],
     "blurb": ["Classical machine learning still wins on tabular data and",
               "still pays well. Deep learning is the other half. You need",
               "both, and you need to know which one a problem wants."],
     "chapters": ["08-classical-ml.md", "09-deep-learning.md",
                  "10-training-at-scale.md"]},

    {"n": 5, "roman": "V", "title": ["Foundation Models"],
     "blurb": ["The layer that did not exist in this form five years ago and",
               "now accounts for most new AI engineering roles: retrieval,",
               "post-training, agents, and the evaluation that governs them."],
     "chapters": ["11-llm-fundamentals.md", "12-retrieval-and-rag.md",
                  "13-post-training.md", "14-agents.md", "15-evaluation.md"]},

    {"n": 6, "roman": "VI", "title": ["Production"],
     "blurb": ["Getting a model to work is a fraction of the job. Serving it",
               "cheaply, observing it honestly, and keeping it correct after",
               "the world moves is the rest."],
     "chapters": ["16-inference-and-serving.md", "17-mlops.md",
                  "18-hardware-and-systems.md"]},

    {"n": 7, "roman": "VII", "title": ["Judgement"],
     "blurb": ["The skills that separate a senior engineer from a competent",
               "one: safety, security, cost, product sense, and knowing when",
               "the answer is “do not use machine learning”."],
     "chapters": ["19-safety-security-compliance.md",
                  "20-product-and-communication.md"]},

    {"n": 8, "roman": "VIII", "title": ["Getting There"],
     "blurb": ["What changed recently, what is now obsolete, four concrete",
               "learning tracks with week-by-week plans, portfolio projects",
               "that actually signal competence, and a self-assessment rubric."],
     "chapters": ["21-what-changed.md", "22-learning-tracks.md",
                  "23-portfolio.md", "24-self-assessment.md"]},
]
