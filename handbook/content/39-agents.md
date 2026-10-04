# Agents
@short: Agents
@subtitle: Reliability engineering for a loop that is not deterministic
@tier: advanced
@prereq: Chapter 32
@blurb: An agent is a loop in which a model decides what to do next. The hard part is not building the loop --- that was Chapter 32 --- but making it reliable enough to trust, because errors compound across steps and a 95%-reliable step is a 60%-reliable ten-step task. This chapter is about the engineering that closes that gap.
@objectives:
- Compute how per-step reliability compounds, and design around it
- Choose the right architecture: single call, chain, router, or loop
- Build a failure taxonomy and use it to direct effort
- Add verification, recovery and budgets so failures are bounded
- Evaluate trajectories, not just final answers

## The compounding problem

@fig: agent_reliability | 158 | Task success against step count at several per-step reliabilities. The curve is $r^n$: at 95% per step, a ten-step task succeeds 60% of the time; at 99%, it succeeds 90%. Nothing about the loop fixes this --- only raising $r$, lowering $n$, or adding verification does.

$$P(\text{success}) = r^n$$

| Per-step $r$ | 3 steps | 5 steps | 10 steps | 20 steps |
|---|---|---|---|---|
| 0.90 | 0.73 | 0.59 | 0.35 | 0.12 |
| 0.95 | 0.86 | 0.77 | 0.60 | 0.36 |
| 0.99 | 0.97 | 0.95 | 0.90 | 0.82 |
| 0.999 | 0.997 | 0.995 | 0.99 | 0.98 |

@tbl: Why long autonomous tasks are hard. The engineering consequence is blunt: either make steps nearly perfect, or make tasks short, or add checks that catch and repair errors so a failed step does not end the task.

:::insight The three levers, and their relative cost
**Reduce $n$.** Decompose into short, independently verifiable sub-tasks.
Cheapest lever by far and almost always available.

**Raise $r$.** Better tool descriptions, constrained arguments, fewer tools
per call, clearer instructions. Moderate cost, bounded upside --- you will not
reach 0.999 this way.

**Add verification and recovery.** Check the result of each step and retry or
repair on failure. This changes the *shape* of the curve rather than its
parameters, because a caught error is not a failure. The most valuable lever,
and the one teams skip.
:::

## Choosing an architecture

| Pattern | Model calls | Predictable? | Use when |
|---|---|---|---|
| Single call | 1 | fully | the task fits in one prompt |
| Chain (fixed sequence) | $k$ | fully | the steps are known in advance |
| Router + specialists | 2 | mostly | distinct task types, each handled differently |
| Loop with tools | unbounded | **no** | the steps depend on what is found |
| Plan then execute | 1 + $k$ | mostly | the plan is checkable before acting |
| Multi-agent | many | no | genuinely parallel sub-tasks |

@tbl: Architectures from most to least predictable. Pick the least agentic option that solves the problem --- predictability is worth a great deal, and most tasks labelled "agentic" are a fixed chain with a conditional.

:::warning Multi-agent is usually a mistake
Multiple agents talking to each other multiply the failure modes: errors
propagate, context is lost at every handoff, cost scales with the number of
participants, and debugging requires reconstructing a conversation between
systems that are each non-deterministic.

It pays in one case: genuinely independent sub-tasks that can run in parallel
and whose results combine mechanically --- searching ten sources at once,
analysing twenty files separately. If the sub-agents need to negotiate, you
have built a distributed system with a language model as its coordination
protocol, which is not a good distributed system.
:::

## Plan-then-execute

```python title="Checking the plan before acting is cheap and catches a lot"
class Plan(BaseModel):
    steps: list[Step] = Field(min_length=1, max_length=12)
    expected_outcome: str

class Step(BaseModel):
    tool: Literal["search", "read_file", "run_sql", "write_file"]
    args: dict
    why: str
    verify: str          # how we will know this step worked

def run(task):
    plan = model.generate(PLAN_PROMPT.format(task=task), schema=Plan)

    # Validate the plan BEFORE executing anything.
    for s in plan.steps:
        validate_args(s.tool, s.args)                 # schema check
        if requires_approval(s.tool, s.args):         # destructive?
            if not ask_human(s):
                return "declined"

    results = []
    for s in plan.steps:
        out = execute(s)
        if not check(s.verify, out):                  # per-step verification
            out = repair(s, out) or replan(task, results, s)
        results.append(out)
    return synthesise(task, results)
```

The `verify` field is the important one: asking the model to state *how it
will know the step worked*, at planning time, produces a checkable condition
and makes the plan's assumptions explicit.

## The failure taxonomy

:::checklist Read fifty failed trajectories by hand and classify them
**Wrong tool.** Picked `search` when it needed `run_sql`. → tool descriptions
with negative clauses (Chapter 32).

**Wrong arguments.** Right tool, malformed or wrong-valued arguments. →
tighter schemas, enums, patterns, examples in the description.

**Wrong order.** Acted before gathering the information it needed. → plan
first, or declare dependencies.

**Premature stop.** Answered from partial information. → an explicit
completion criterion in the prompt and a check before returning.

**Loop.** Repeated the same call. → detect repeats in the trajectory and
inject a message naming the repetition.

**Context overflow.** Tool outputs filled the window and early context was
lost. → truncate results, summarise, externalise to files.

**Hallucinated tool.** Called something that does not exist. → return a
clear error listing the available tools; it usually recovers.

**Correct trajectory, wrong synthesis.** Every step right, final answer wrong.
→ this is a generation problem, not an agent problem.
:::

```python title="Classify automatically, then read a sample by hand"
def classify(trajectory, outcome):
    calls = [s.tool_call for s in trajectory if s.tool_call]
    names = [c.name for c in calls]
    if any(n not in TOOLS for n in names):
        return "hallucinated_tool"
    if len(names) != len(set(map(str, calls))) and len(calls) > 2:
        return "loop"
    if trajectory.tokens > 0.9 * CONTEXT:
        return "context_overflow"
    if any(s.error and "validation" in s.error for s in trajectory):
        return "wrong_arguments"
    if outcome.failed and len(calls) < 2:
        return "premature_stop"
    if outcome.steps_all_succeeded and not outcome.correct:
        return "wrong_synthesis"
    return "other"
```

The automatic classifier is for triage and trend-tracking. The real
understanding comes from reading the "other" bucket by hand --- that is where
the failure mode you have not thought of lives.

## Verification and recovery

```python title="Verify cheaply, repair locally, replan rarely"
VERIFIERS = {
    "write_file":  lambda s, out: Path(s.args["path"]).exists(),
    "run_sql":     lambda s, out: out.rowcount is not None,
    "run_code":    lambda s, out: out.exit_code == 0,
    "search":      lambda s, out: len(out.results) > 0,
}

def execute_with_recovery(step, max_repairs=2):
    for attempt in range(max_repairs + 1):
        out = execute(step)
        verify = VERIFIERS.get(step.tool)
        if verify is None or verify(step, out):
            return out
        if attempt < max_repairs:
            step = model.repair(step, out.error)       # fix the arguments
    raise StepFailed(step)
```

The hierarchy matters for cost: a **programmatic verifier** is free and should
be used wherever one exists; a **model-based check** costs a call; a **replan**
costs the whole remaining trajectory. Try them in that order.

## Evaluating an agent

```python title="Trajectory metrics, not just the final answer"
def evaluate(agent, tasks):
    rows = []
    for t in tasks:
        traj = agent.run(t.input)
        rows.append(dict(
            success=grade(traj.final, t.expected),
            steps=len(traj.steps),
            tool_accuracy=sum(s.tool == e for s, e in
                              zip(traj.steps, t.expected_tools)) / len(t.expected_tools),
            arg_validity=sum(s.args_valid for s in traj.steps) / len(traj.steps),
            recoveries=sum(s.repaired for s in traj.steps),
            cost=traj.cost, latency=traj.latency,
            failure_class=classify(traj, t) if not traj.ok else None,
        ))
    return summarise(rows)
```

| Metric | What it tells you |
|---|---|
| Task success | the headline, and the least diagnostic number |
| Steps taken vs minimum | efficiency; a rising trend means confusion |
| Tool-selection accuracy | whether descriptions are working |
| Argument validity | whether schemas are tight enough |
| Recovery rate | how much your verifiers are earning |
| Cost and latency per task | whether it is deployable at all |
| Failure-class distribution | **where to spend your next week** |

@tbl: Seven metrics. The last row is the one that directs work: fixing the largest failure class is almost always a better use of a week than a general attempt to "improve the agent".

:::insight The discipline that distinguishes a working agent
Build a 50-task evaluation set. Run it. Categorise every failure. Fix the
largest category only. Re-run. Repeat.

This sounds obvious and is rare. The common alternative --- tweaking the
prompt and re-running a few examples by hand --- cannot tell improvement from
noise, and routinely trades one failure class for another while leaving the
total unchanged.
:::

:::practice The task
Build an agent for a multi-step task with at least three tools. (a) Measure
per-step reliability and predict task success from $r^n$; compare to measured.
(b) Run 50 tasks, classify every failure, and plot the distribution. (c) Fix
the largest class and re-run; report the before/after for every class, not
just the total. (d) Add programmatic verifiers for two tools and measure the
recovery rate. (e) Deliberately trigger each of the eight failure modes.
(f) Compare your loop against a fixed chain on the same tasks --- is the
agency earning its unpredictability?

**You have this skill when** you can name your agent's largest failure class
and its share, and show the number falling over successive weeks.
:::

:::exercise
1. Derive $r^n$ and compute the per-step reliability needed for 90% success on
   a 15-step task.
2. Implement step-level verification for one tool and measure how much task
   success rises.
3. † Build a task that a fixed chain solves and an agent loop fails. Explain
   the mechanism.
4. Instrument a loop detector and trigger it. What message best breaks the
   loop?
5. Fill the context with tool outputs and observe the failure. Implement
   truncation plus summarisation and re-measure.
6. † Compare plan-then-execute against a reactive loop on 50 tasks. Report
   success, cost and the failure-class distribution for each.
7. Build the failure classifier, run it on 50 failures, then read the "other"
   bucket by hand. What did the classifier miss?
:::

:::recap
- Success compounds as $r^n$: at 95% per step, ten steps succeed 60% of the
  time.
- Three levers: shorten the task (cheapest), raise per-step reliability
  (bounded), add verification and recovery (changes the shape of the curve).
- Choose the least agentic architecture that works; multi-agent pays only for
  genuinely parallel sub-tasks.
- Plan first and validate the plan before acting; ask the model how it will
  verify each step.
- Classify every failure into the eight-mode taxonomy and fix the largest
  class.
- Verify programmatically where possible, repair locally, replan rarely.
- Evaluate trajectories: tool accuracy, argument validity, steps, recovery
  rate, cost, and the failure distribution.
:::
