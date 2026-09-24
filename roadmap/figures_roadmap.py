"""Diagrams for the skill-map companion volume."""
from engine.parser import fig
from engine.draw import D, Pen
from engine.style import MONO, MONO_B, SANS, SANS_B, SANS_I, SANS_SB, SERIF, SERIF_I


@fig("role_map")
def role_map(p):
    """Five jobs behind one job title, and what each one is mostly made of."""
    roles = [
        ("AI Engineer", "teal", [("Foundation models", .9), ("Data", .4),
                                 ("Infra", .4), ("Classical ML", .15)]),
        ("ML Engineer", "violet", [("Foundation models", .35), ("Data", .7),
                                   ("Infra", .6), ("Classical ML", .8)]),
        ("ML Platform", "hi", [("Foundation models", .3), ("Data", .6),
                               ("Infra", .95), ("Classical ML", .2)]),
        ("Research Engineer", "ok", [("Foundation models", .8), ("Data", .5),
                                     ("Infra", .7), ("Classical ML", .3)]),
        ("Data Scientist", "dim", [("Foundation models", .3), ("Data", .8),
                                   ("Infra", .2), ("Classical ML", .9)]),
    ]
    labels = ["Foundation models", "Data", "Infra", "Classical ML"]
    colw = 74
    x0 = 108
    y = p.h - 22
    for j, lab in enumerate(labels):
        p.text(x0 + j * colw + 26, y, lab.replace(" ", "\n").split("\n")[0],
               6.4, D.faint, SANS_SB, "c")
        if " " in lab:
            p.text(x0 + j * colw + 26, y - 8, lab.split(" ", 1)[1], 6.4,
                   D.faint, SANS_SB, "c")
    p.line(0, y - 14, p.w, y - 14, D.faint, 0.5)
    y -= 30
    for name, kind, bars in roles:
        p.text(0, y, name, 7.4, D.ink, SANS_SB, "l")
        for j, (_, frac) in enumerate(bars):
            p.bar(x0 + j * colw, y - 2, 52, 8, frac, kind)
        y -= 21
    p.text(0, y + 4, "Same title on the job board. Very different day jobs — "
           "decide which column you want to be strongest in.", 7.0, D.muted,
           SANS_I, "l")


@fig("skill_stack")
def skill_stack(p):
    """The stack, bottom-up: nothing above works if a layer below is missing."""
    layers = [
        ("PRODUCT & JUDGEMENT", "framing, cost/benefit, when not to use ML", "hi"),
        ("SAFETY, SECURITY, COMPLIANCE", "injection, PII, evals as gates, AI Act", "bad"),
        ("PRODUCTION", "serving, MLOps, observability, cost", "violet"),
        ("FOUNDATION MODELS", "RAG, post-training, agents, evaluation", "violet"),
        ("MODELLING", "classical ML, deep learning, training at scale", "ok"),
        ("DATA", "SQL, pipelines, curation, dedup, labelling", "teal"),
        ("FOUNDATIONS", "Python, engineering, maths, algorithms, systems", "teal"),
    ]
    h = 24
    y = p.h - h - 6
    for i, (name, sub, kind) in enumerate(layers):
        inset = i * 6
        p.box(inset, y, p.w - 2 * inset, h, None, kind, radius=3)
        p.text(inset + 12, y + h - 10, name, 7.2, D.ink, SANS_SB, "l")
        p.text(p.w - inset - 12, y + h - 10, sub, 6.6, D.muted, SANS, "r")
        y -= h + 3
    p.text(0, 4, "Read bottom-up. Every hiring loop probes the bottom two "
           "layers, and most candidates who fail, fail there.", 7.0, D.muted,
           SANS_I, "l")


@fig("what_changed")
def what_changed(p):
    """What the job asked for, year by year."""
    cols = [
        ("2020", ["sklearn + XGBoost", "Airflow", "TF/Keras", "manual tuning",
                  "REST model server"], "dim"),
        ("2023", ["PyTorch default", "prompt engineering", "vector DB + RAG",
                  "LoRA fine-tuning", "W&B / MLflow"], "teal"),
        ("2026", ["evals as the core skill", "agents + tool use + MCP",
                  "post-training (DPO/GRPO)", "vLLM / SGLang serving",
                  "inference cost engineering"], "hi"),
    ]
    colw = p.w / 3
    for i, (year, items, kind) in enumerate(cols):
        x = i * colw
        p.box(x, p.h - 22, colw - 14, 17, year, kind, size=8.0, radius=3)
        y = p.h - 40
        for it in items:
            p.text(x + 3, y, "•", 7.0, D.faint, SANS, "l")
            words, line = it.split(), ""
            lines = []
            for w in words:
                if len(line) + len(w) > 22:
                    lines.append(line); line = w
                else:
                    line = (line + " " + w).strip()
            lines.append(line)
            for k, ln in enumerate(lines):
                p.text(x + 12, y - k * 9.5, ln, 7.0, D.ink, SANS, "l")
            y -= 9.5 * len(lines) + 6
        if i < 2:
            p.arrow(x + colw - 12, p.h - 14, x + colw - 2, p.h - 14, D.arrow,
                    0.9, head=3)
    p.text(0, 4, "The 2020 column has not disappeared — it is still half of "
           "most ML jobs. The 2026 column is what is newly scarce.", 7.0,
           D.muted, SANS_I, "l")


@fig("adaptation_ladder")
def adaptation_ladder(p):
    """Cheapest intervention first: most teams jump three rungs too far."""
    rungs = [
        ("Prompt + few-shot", "minutes", "$0", "ok", 0.18),
        ("Structured output + tools", "hours", "$0", "ok", 0.30),
        ("Retrieval (RAG)", "days", "$", "teal", 0.45),
        ("Prompt optimisation + routing", "days", "$", "teal", 0.55),
        ("LoRA / QLoRA fine-tune", "1–2 weeks", "$$", "hi", 0.70),
        ("Full SFT + preference tuning", "weeks", "$$$", "hi", 0.85),
        ("Continued pretraining", "months", "$$$$", "bad", 1.0),
    ]
    y = p.h - 22
    for name, t, cost, kind, frac in rungs:
        p.bar(112, y - 2, 150, 9, frac, kind)
        p.text(108, y, name, 7.2, D.ink, SANS_SB, "r")
        p.text(272, y, t, 7.0, D.muted, SANS, "l")
        p.text(p.w, y, cost, 7.4, D.muted, MONO, "r")
        y -= 17
    p.text(112, y + 2, "effort and cost →", 6.6, D.faint, SANS_I, "l")
    p.text(0, y - 14, "Climb one rung at a time and measure. The most common "
           "expensive mistake in applied AI is", 7.0, D.bad_bd, SANS_SB, "l")
    p.text(0, y - 25, "fine-tuning a model that a better prompt and a "
           "retrieval step would have fixed for nothing.", 7.0, D.bad_bd,
           SANS, "l")


@fig("eval_loop")
def eval_loop(p):
    """Eval-driven development: the loop that separates demos from products."""
    steps = [("Collect real\nfailures", "teal"), ("Write a\ngolden set", "teal"),
             ("Define graders\n(rule + judge)", "hi"),
             ("Change one\nthing", "violet"), ("Re-run the\nsuite", "violet"),
             ("Ship or\nrevert", "ok")]
    n = len(steps)
    gap = 8
    w = (p.w - gap * (n - 1)) / n
    y = p.h - 62
    for i, (name, kind) in enumerate(steps):
        x = i * (w + gap)
        p.box(x, y, w, 42, None, kind, radius=3)
        for j, ln in enumerate(name.split("\n")):
            p.text(x + w / 2, y + 26 - j * 10, ln, 7.0, D.ink, SANS_SB, "c")
        if i < n - 1:
            p.arrow(x + w + 1, y + 21, x + w + gap - 1, y + 21, D.arrow, 0.8,
                    head=3)
    p.curve(p.w - w / 2, y - 6, w / 2, y - 6, bulge=-16, color=D.hi_bd, lw=1.0)
    p.text(p.w / 2, y - 40, "every regression becomes a new test case", 7.0,
           D.hi_bd, SANS_SB, "c")
    p.text(0, 6, "Teams that do this ship steadily. Teams that judge output by "
           "eye plateau within a month and cannot tell", 7.0, D.muted, SANS_I, "l")
    p.text(0, -4, "whether a change helped.", 7.0, D.muted, SANS_I, "l")


@fig("rag_decisions")
def rag_decisions(p):
    """A retrieval pipeline is a chain of decisions, each with a failure mode."""
    stages = [("Chunk", "size, overlap,\nsemantic vs fixed", "teal"),
              ("Embed", "model, dimension,\nnormalise", "teal"),
              ("Index", "flat / IVF-PQ /\nHNSW, filters", "violet"),
              ("Retrieve", "hybrid BM25 +\ndense, top-k", "violet"),
              ("Rerank", "cross-encoder,\nk→k′", "hi"),
              ("Assemble", "order, dedupe,\ntoken budget", "hi")]
    n = len(stages)
    gap = 7
    w = (p.w - gap * (n - 1)) / n
    y = p.h - 56
    for i, (name, sub, kind) in enumerate(stages):
        x = i * (w + gap)
        p.box(x, y, w, 36, None, kind, radius=3)
        p.text(x + w / 2, y + 22, name, 7.4, D.ink, SANS_SB, "c")
        for j, ln in enumerate(sub.split("\n")):
            p.text(x + w / 2, y + 12 - j * 8, ln, 6.2, D.muted, SANS, "c")
        if i < n - 1:
            p.arrow(x + w + 1, y + 18, x + w + gap - 1, y + 18, D.arrow, 0.8,
                    head=2.8)
    p.text(0, p.h - 10, "EACH BOX IS A TUNABLE WITH ITS OWN EVAL", 7.0,
           D.muted, SANS_SB, "l")
    y2 = y - 20
    for i in (0, 3):
        x = i * (w + gap) + w / 2
        p.arrow(x, y2 - 2, x, y2 + 8, D.bad_bd, 0.9, head=3)
    p.text(0, y2 - 18, "Recall is lost at chunking and retrieval. Measure "
           "retrieval recall@k separately from answer quality:", 7.0,
           D.bad_bd, SANS_SB, "l")
    p.text(0, y2 - 29, "if recall is 60%, no amount of prompt work on the "
           "generator will fix the answers \u2014 and teams spend months", 7.0,
           D.muted, SANS_I, "l")
    p.text(0, y2 - 39, "not knowing which half is broken.", 7.0, D.muted,
           SANS_I, "l")


@fig("agent_loop")
def agent_loop(p):
    """The agent loop, and the four places it goes wrong."""
    import math
    cx, cy, r = 96, p.h / 2 - 6, 44
    nodes = [("Observe", 90), ("Plan", 10), ("Act (tool)", -70), ("Verify", 190)]
    pts = []
    for i, (name, _) in enumerate(nodes):
        a = math.pi / 2 - i * 2 * math.pi / 4
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        pts.append((x, y))
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 4]
        p.arrow(x1, y1, x2, y2, D.arrow, 0.9, head=3.2, shrink=21)
    for (x, y), (name, _) in zip(pts, nodes):
        p.circle(x, y, 20, "", "teal", size=6.4)
        p.text(x, y - 2.4, name, 6.6, D.ink, SANS_SB, "c")

    x0 = 172
    rows = [("Loops forever", "hard step budget + a cost ceiling"),
            ("Tool call malformed", "constrained decoding against the schema"),
            ("Wrong tool chosen", "fewer, better-described tools; eval per tool"),
            ("Context overflows", "summarise or externalise memory"),
            ("Silent wrong answer", "a verifier step, or human sign-off")]
    y = p.h - 14
    p.text(x0, y, "FAILS LIKE THIS", 6.6, D.faint, SANS_SB, "l")
    p.text(x0 + 116, y, "FIX", 6.6, D.faint, SANS_SB, "l")
    p.line(x0, y - 5, p.w, y - 5, D.faint, 0.5)
    y -= 17
    for bad, fix in rows:
        p.text(x0, y, bad, 6.9, D.bad_bd, SANS, "l")
        p.text(x0 + 116, y, fix, 6.9, D.ok_bd, SANS, "l")
        y -= 15
    p.text(0, 4, "An agent is a while-loop with a budget. Most production "
           "“agents” are three tools and a good verifier.", 7.0,
           D.muted, SANS_I, "l")


@fig("cost_ladder")
def cost_ladder(p):
    """Order-of-magnitude serving economics: the knobs that actually move cost."""
    rows = [("Frontier API, no caching", 1.00, "bad"),
            ("+ prompt / prefix caching", 0.45, "bad"),
            ("+ route easy traffic to a small model", 0.20, "hi"),
            ("Open weights, self-hosted, fp16", 0.12, "hi"),
            ("+ int8 / fp8 quantisation", 0.07, "teal"),
            ("+ continuous batching, high utilisation", 0.03, "ok"),
            ("+ distil to a task-specific small model", 0.01, "ok")]
    y = p.h - 20
    for name, frac, kind in rows:
        p.bar(238, y - 2, 118, 9, frac, kind)
        p.text(234, y, name, 7.2, D.ink, SANS, "r")
        p.text(p.w, y, ("%.2f×" % frac), 7.2, D.muted, MONO, "r")
        y -= 18
    p.text(0, y + 2, "Relative cost per million served tokens, same task, "
           "same quality bar. Two orders of magnitude sit between", 7.0,
           D.muted, SANS_I, "l")
    p.text(0, y - 8, "the top and the bottom row — and none of it is model "
           "quality work.", 7.0, D.muted, SANS_I, "l")


@fig("time_allocation")
def time_allocation(p):
    """Where the hours go, versus where courses spend their time."""
    rows = [("Data: collection, cleaning, labelling", 0.30, 0.10),
            ("Evaluation and error analysis", 0.20, 0.05),
            ("Infrastructure and deployment", 0.20, 0.10),
            ("Modelling and training", 0.15, 0.65),
            ("Stakeholders, docs, review", 0.15, 0.10)]
    y = p.h - 26
    p.text(212, p.h - 10, "REAL JOB", 6.6, D.teal_bd, SANS_SB, "c")
    p.text(320, p.h - 10, "TYPICAL COURSE", 6.6, D.bad_bd, SANS_SB, "c")
    for name, real, course in rows:
        p.text(196, y, name, 7.2, D.ink, SANS, "r")
        p.bar(206, y - 2, 84, 9, real, "teal")
        p.bar(300, y - 2, 84, 9, course, "bad")
        y -= 20
    p.text(0, y + 4, "Proportions are illustrative but the shape is not "
           "controversial: the two rows that dominate real work are",
           7.0, D.muted, SANS_I, "l")
    p.text(0, y - 6, "the two that almost no curriculum teaches.", 7.0,
           D.muted, SANS_I, "l")


@fig("tracks")
def tracks(p):
    """Four entry paths, with honest timelines."""
    tracks_ = [
        ("A. Software engineer → AI engineer", "3–4 months", 
         "Ch 3, 11–16, 19–20", "teal"),
        ("B. Data scientist → ML engineer", "4–6 months",
         "Ch 3, 5, 6, 9, 16–18", "violet"),
        ("C. Student / career changer", "9–12 months",
         "all of it, in order", "hi"),
        ("D. ML engineer → research engineer", "6–9 months",
         "Ch 4, 9, 10, 13, 18", "ok"),
    ]
    y = p.h - 30
    for name, dur, chapters, kind in tracks_:
        p.box(0, y, p.w, 26, None, kind, radius=3)
        p.text(12, y + 9, name, 7.6, D.ink, SANS_SB, "l")
        p.text(p.w - 140, y + 9, dur, 7.2, D.muted, MONO, "l")
        p.text(p.w - 12, y + 9, chapters, 7.0, D.muted, SANS, "r")
        y -= 33
    p.text(0, y + 12, "Elapsed time at roughly 12 hours a week. "
           "Every track assumes you build and ship something real;", 7.0,
           D.muted, SANS_I, "l")
    p.text(0, y + 2, "none of them works by reading alone.", 7.0, D.muted,
           SANS_I, "l")


@fig("maturity")
def maturity(p):
    """The five levels, applied to any single skill area."""
    levels = [("1", "Aware", "can define it, has read about it", "dim"),
              ("2", "Guided", "can do it following a tutorial", "teal"),
              ("3", "Independent", "can do it on a new problem, unaided", "violet"),
              ("4", "Fluent", "knows the failure modes and the trade-offs", "hi"),
              ("5", "Authoritative", "others ask you; you have changed the default", "ok")]
    y = p.h - 26
    for num, name, desc, kind in levels:
        p.circle(14, y + 4, 12, num, kind, size=8.4)
        p.text(34, y + 6, name, 7.8, D.ink, SANS_SB, "l")
        p.text(122, y + 6, desc, 7.2, D.muted, SANS, "l")
        y -= 26
    p.text(0, y + 12, "Hiring bars, roughly: junior wants 3s in the "
           "foundations; mid wants 3–4 across a whole column of the role", 7.0,
           D.muted, SANS_I, "l")
    p.text(0, y + 2, "map; senior wants a 5 somewhere and no 1s anywhere that "
           "touches production.", 7.0, D.muted, SANS_I, "l")
