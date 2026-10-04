# Prompting as Engineering
@short: Prompting
@subtitle: Turning a craft into something you can version, test and improve
@tier: core
@prereq: Chapter 29
@blurb: Prompting is treated as folklore and it does not have to be. A prompt is a program: it has inputs, a contract, versions, tests and a regression suite. This chapter covers the techniques that reliably work, the ones that do not, and --- more importantly --- how to tell the difference for your own task.
@objectives:
- Structure a prompt so each part does one job
- Use the techniques that are actually supported by evidence
- Treat prompts as versioned artefacts with a test suite
- Optimise prompts systematically rather than by intuition
- Know when prompting has run out and something else is needed

## Structure

```python title="A prompt with clear separation of concerns"
SYSTEM = """\
You are a support-ticket classifier for an e-commerce platform.

## Task
Assign exactly one category and a priority to each ticket.

## Categories
- billing: payments, refunds, invoices, subscriptions
- shipping: delivery, tracking, returns in transit
- product: defects, missing parts, usage questions
- account: login, password, personal data, deletion
- other: anything that fits none of the above

## Priority
- urgent: the customer cannot use the service at all, or money is at risk
- normal: everything else

## Rules
- If a ticket spans categories, choose the one the customer asks about first.
- If the text is not a support ticket, use category "other".
- Never invent an order number. If one is absent, use null.

## Output
A single JSON object matching the schema. No prose, no markdown fence.
"""

USER = """\
<ticket>
{ticket_text}
</ticket>
"""
```

:::checklist Six structural rules that hold up
1. **Role and task first**, in two sentences. The model conditions on the
   opening most strongly.
2. **Definitions before instructions.** Define the categories, then say what
   to do with them.
3. **Delimit the input** with tags (`<ticket>...</ticket>`). This separates
   data from instructions and is the first line of defence against prompt
   injection (Chapter 44).
4. **State the output contract exactly**, and validate against it
   (Chapter 32).
5. **Handle the edge cases explicitly.** Most production failures are inputs
   the prompt never considered: empty, wrong language, adversarial, spanning
   two categories.
6. **Put the variable content last.** It is easier to cache a long fixed
   prefix (Chapter 30) and the model attends well to the end.
:::

## Techniques that work

| Technique | Effect | Best for |
|---|---|---|
| Few-shot examples | large, reliable | format adherence, edge cases, tone |
| Explicit reasoning ("think step by step") | large on multi-step tasks | maths, logic, planning |
| Output schema | near-total on format errors | anything structured |
| Decomposition into sub-prompts | large on complex tasks | pipelines, long documents |
| Self-consistency (sample $k$, majority vote) | moderate, costs $k\times$ | verifiable answers |
| Negative examples | moderate | recurring specific mistakes |
| Pre-filling the assistant turn | strong format control | where the API allows it |

@tbl: Techniques ranked by how reliably they help. Few-shot examples and an output schema are the two that almost always pay; the rest depend on the task.

```python title="Few-shot examples chosen for coverage, not for typicality"
EXAMPLES = [
    # 1. The common case — establishes the format.
    ("My package says delivered but it is not here.",
     {"category": "shipping", "priority": "normal", "order_id": None}),
    # 2. A boundary case — the rule in action.
    ("I was charged twice and cannot log in to check.",
     {"category": "billing", "priority": "urgent", "order_id": None}),
    # 3. A hard negative — what NOT to do.
    ("hi", {"category": "other", "priority": "normal", "order_id": None}),
]
# Pick examples that disagree with the model's default behaviour.
# Three well-chosen examples beat twenty typical ones.
```

:::insight Choose examples by where the model is wrong
The instinct is to pick representative examples. That is close to useless: the
model already handles the representative case. Pick examples from your
**failure log** --- the inputs where the current prompt got it wrong. Each one
then buys a correction rather than a confirmation.

This is also why few-shot selection should be dynamic where you can afford it:
retrieve the $k$ examples most similar to the current input (Chapter 33) and
include those. It typically beats a fixed set by a wide margin.
:::

## Techniques that do not work

:::pitfall Five things people do that do not help
**Politeness and threats.** "Please" and "this is very important to my career"
have no reliable effect on modern models. Measure it on your task before
believing otherwise.

**Assigning expertise.** "You are a world-class expert" is mostly inert on
current models. Describing the *task* precisely works; describing an identity
does not.

**Emphatic capitals and repetition.** "You MUST ALWAYS output JSON" is weaker
than providing a schema and validating. If a rule matters, enforce it in code.

**Extremely long prompts.** Past a few thousand tokens, added instructions
compete for attention and often dilute the ones that mattered. When a prompt
grows past that, decompose the task.

**Chain-of-thought on trivial tasks.** It adds latency and cost, and on simple
classification it can *reduce* accuracy by talking the model out of a correct
first instinct.
:::

## Prompts as versioned artefacts

```python title="A prompt is code: version it, test it, review it"
from dataclasses import dataclass

@dataclass(frozen=True)
class Prompt:
    id: str
    version: int
    template: str
    model: str
    params: dict
    created: str
    notes: str

    def render(self, **kw) -> str:
        missing = set(self.required()) - set(kw)
        if missing:
            raise ValueError(f"missing variables: {missing}")
        return self.template.format(**kw)

    def required(self) -> set[str]:
        import string
        return {f for _, f, _, _ in string.Formatter().parse(self.template) if f}
```

```
prompts/
  classify_ticket/
    v1.txt          the original
    v2.txt          + explicit tie-break rule
    v3.txt          + three failure-log examples
    examples.jsonl  the few-shot set, versioned with the prompt
    eval.jsonl      the golden set (Chapter 37)
    CHANGELOG.md    what changed and what it measured
```

:::warning A prompt change is a code change
It alters behaviour in production and it can regress. Treat it accordingly:
version it, review it, run the evaluation suite before merging, and keep the
suite green. Teams that edit prompts directly in a dashboard, with no version
history and no tests, eventually cannot answer "why did the output change on
Tuesday?" --- and that question always gets asked.
:::

## Systematic optimisation

@fig: prompt_loop | 152 | The prompt development loop. The distinguishing feature is the failure log: every production error becomes an eval case, and every eval case becomes either a fix or an accepted limitation.

```python title="Automated prompt optimisation, in outline"
# 1. Build an evaluation set with a grader (Chapter 37). Without this,
#    every subsequent step is guesswork.
# 2. Generate candidate variations — by hand, or with a model asked to
#    rewrite the prompt given the failing cases.
# 3. Score every candidate on the eval set.
# 4. Keep the winner ONLY if the improvement exceeds the confidence
#    interval (Chapter 10). Most apparent gains do not.
# 5. Re-test on a held-out set you have not optimised against.
#
# Frameworks (DSPy, OPRO and relatives) automate 2 and 3. They cannot
# automate 1, which is the part that determines whether any of it works.
```

:::insight When prompting has run out
Stop prompting and change the approach when:
- The prompt exceeds ~2000 tokens of instructions and still fails.
- You are adding an example per failure with no generalisation --- you are
  fitting, not teaching.
- The task needs knowledge the model does not have → **retrieval**
  (Chapter 33).
- The task needs a format or style the model resists consistently →
  **fine-tuning** (Chapter 35).
- The task needs exactness (arithmetic, lookup, sorting) → **a tool**
  (Chapter 32).

Recognising this early saves weeks. The failure mode is a team spending a
month on prompt iterations for a problem that needed retrieval on day three.
:::

:::practice The task
Take a prompt you use in production. (a) Restructure it per the six rules and
measure the change on a golden set of at least 100 cases. (b) Build the
failure log and add three examples drawn from it; measure again. (c) Test the
"politeness", "expertise" and "capitals" techniques on your task and report
whether the effect exceeds the confidence interval. (d) Version it as files
with a changelog. (e) Run one automated optimisation loop and check whether
the winner survives on a held-out set.

**You have this skill when** every prompt change in your system arrives as a
diff with an evaluation attached.
:::

:::exercise
1. Take a failing prompt and improve it with structure alone --- no new
   instructions. Measure.
2. Compare three few-shot examples chosen from failures against twenty chosen
   at random. Report the difference.
3. † Implement dynamic few-shot selection by similarity and compare against a
   fixed set on 200 cases.
4. Measure the effect of chain-of-thought on a simple classification task. Is
   it positive?
5. Build the prompt-versioning layout and wire the evaluation into CI.
6. † Run an automated optimiser for 20 candidates, then check the winner on a
   held-out set. How much of the gain survives?
7. Find a task in your system where prompting has run out. State which of the
   four alternatives it needs and why.
:::

:::recap
- Structure a prompt as role, definitions, rules, delimited input, output
  contract --- with edge cases handled explicitly and variable content last.
- Few-shot examples and an output schema are the two techniques that almost
  always pay; choose examples from your failure log, not from typical cases.
- Politeness, expertise assignment, capitals, very long prompts and
  chain-of-thought on trivial tasks are not reliable improvements.
- A prompt is a versioned artefact with a test suite; a prompt change is a
  code change.
- Optimise against an evaluation set and keep a change only when it beats the
  confidence interval.
- Know when to stop: retrieval for missing knowledge, fine-tuning for
  resistant style, tools for exactness.
:::
