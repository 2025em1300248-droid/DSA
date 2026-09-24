# Agents and Tool Use
@short: Agents
@subtitle: A while-loop with a budget, and the four places it goes wrong
@tier: advanced
@prereq: Chapters 11, 12
@blurb: "Agent" covers everything from a single tool call to an autonomous multi-step system. The engineering content is smaller and more mundane than the discourse suggests: tool design, state management, budgets, verification and failure handling. The hard parts are reliability and evaluation, not architecture.
@objectives:
- Build a reliable tool-using loop with explicit budgets and verification
- Design tools a model can actually use correctly
- Manage context and memory across long-running tasks
- Evaluate an agent, which is substantially harder than evaluating a single response

## The loop, and its failure modes

@fig: agent_loop | 155 | An agent is a loop with a budget. The right-hand column is where the engineering actually goes.

## The capabilities

:::checklist CORE --- the loop
- The basic pattern: observe, plan, act, verify, repeat until done or out of
  budget
- Hard budgets on steps, wall-clock time, tokens and money --- all four,
  enforced, with a defined behaviour on exhaustion
- Error handling that feeds the error back to the model in a form it can act
  on ("the file does not exist; here are the files that do") rather than a
  stack trace
- Termination conditions and detecting loops (repeated identical actions)
- Structured state so that a run can be inspected, resumed and replayed
- Streaming progress to the user, because a silent 40-second agent feels
  broken
:::

:::checklist CORE --- tool design
- Few tools with unambiguous boundaries. Model performance degrades
  noticeably as the tool count grows; twenty overlapping tools is a design
  smell
- Descriptions written for the model: what it does, when to use it, when
  *not* to, what the arguments mean, what errors look like
- Schema-constrained arguments, validated before execution
- Idempotency, so a retry is safe
- Confirmation gates for irreversible or costly actions
- Sandboxing anything that executes code or touches a network. This is a
  security boundary, not a nicety (Chapter 19)
- MCP for exposing tools in a standard, reusable way across clients
:::

:::checklist CORE --- context and memory
- Context is the scarce resource. Strategies, roughly in order of preference:
  summarise old turns, externalise state to a file or database the agent can
  read back, retrieve selectively rather than carrying everything, and start
  a fresh context with a handoff note
- Distinguish working memory (this task), episodic memory (what happened
  before) and semantic memory (learned facts); they have different storage
  and retrieval needs
- Compaction: when and what to summarise, and keeping the summary faithful
- Passing state between sub-agents explicitly rather than hoping it is in the
  transcript
:::

:::checklist CORE --- architecture patterns
| Pattern | Use when |
|---|---|
| Single tool call | The task is one lookup or one action. Most tasks. |
| ReAct loop (think, act, observe) | Multi-step, tools available, moderate ambiguity |
| Plan-then-execute | The plan is worth reviewing before acting |
| Reflection / self-critique | Quality matters more than latency; pair with a verifier |
| Router | Several specialised paths; classify then dispatch |
| Orchestrator with sub-agents | Genuinely separable sub-tasks, each with its own context |
| Human in the loop | Irreversible actions, or accuracy below the required bar |
:::

:::checklist CORE --- evaluation
- Trajectory evaluation, not just final-answer evaluation: did it take a
  sensible path, call the right tools, avoid unnecessary steps
- Per-tool accuracy: was each call well formed and appropriate
- Cost and step distributions, not just means --- the tail is what hurts
- Reproducible runs: fixed seeds, recorded tool responses, replayable
  transcripts
- Failure taxonomy: classify every failure into a small set of causes and
  track the mix over time. This is how you know what to fix next
:::

:::checklist AWARENESS
- Multi-agent debate, role-play and voting schemes --- occasionally useful,
  frequently an expensive way to get a small gain
- Computer use and browser automation
- Long-horizon autonomy and its safety implications
:::

:::insight The engineering opinion that holds up
Most production "agents" are: three or four well-described tools, a loop with
a step budget, structured output, a verifier, and extensive logging. The
elaborate multi-agent architectures that appear in diagrams are usually
slower, more expensive and harder to debug than a single well-instrumented
loop, and they very rarely win in an evaluation.

Start with a single loop and three tools. Add complexity only when a
measured failure mode demands it.
:::

## How to tell you have it

:::practice The task
Build an agent that answers questions requiring several steps over a real
data source --- a database and a document store, say.
1. Implement the loop with explicit step, token and cost budgets.
2. Give it three tools with schemas and validation.
3. Build 50 evaluation tasks with known correct answers *and* known correct
   tool-use paths.
4. Report: success rate, mean and p95 steps, mean and p95 cost, and the
   failure mix by category.
5. Add a verification step and re-measure. Report whether it paid for itself.
6. Deliberately break each tool (timeout, malformed response, empty result)
   and confirm the agent recovers or fails cleanly rather than looping.

Step 6 is what separates a demo from a service.
:::

:::pitfall The four agent failures
1. **No budget.** A loop with no step or cost ceiling will eventually find an
   input that makes it run until somebody notices the bill.
2. **Too many tools.** Selection accuracy falls; consolidate.
3. **Evaluating only the final answer.** You cannot improve what you cannot
   localise; evaluate the trajectory.
4. **No sandbox.** An agent with shell access and a prompt-injectable context
   is a remote code execution vulnerability with extra steps.
:::

:::note Time to competence
**4--6 weeks** to build reliable single-agent systems. Evaluation is the long
pole and the differentiating skill.
:::

:::recap
- An agent is a loop with a budget; enforce steps, time, tokens and money.
- Design few tools, described for the model, with validated schemas,
  idempotency, confirmation gates and a sandbox.
- Context is the scarce resource: summarise, externalise, retrieve
  selectively, hand off.
- Evaluate trajectories and per-tool accuracy, track a failure taxonomy, and
  look at tails rather than means.
- Start with one loop and three tools; add architecture only when a measured
  failure demands it.
:::
