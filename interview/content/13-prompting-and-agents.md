# Prompting, LangChain and Agents
@short: Prompting and Agents
@subtitle: Including the MCP and A2A questions you listed
@tier: core
@prereq: Chapter 12
@blurb: Your resume names LangChain, LangGraph, agents, MCP and A2A, so all five get asked. The one that matters most is why SafeSight needed a graph rather than a chain --- that is a design decision you made, and being able to defend it is worth more than any definition.
@objectives:
- Say what makes a prompt reliable rather than lucky
- Explain the difference between a chain and a graph, with your own example
- Define MCP and A2A in one line each
- Say when you would *not* use an agent

## Prompting

#### Q20.1 — What is prompt engineering?
Writing the instruction carefully so you get a reliable answer instead of a
lucky one. A clear task, the relevant context, explicit limits, and the format
you want back.

#### Q20.2 — Zero-shot vs one-shot vs few-shot?
How many worked examples you include. None, one, or several.

Few-shot is how you pin down the exact output format and show it how to handle
edge cases, without any training.

#### Q20.3 — What makes a good prompt?
A specific task, the context it needs, explicit constraints, a stated output
format, and an instruction for what to do when it doesn't know.

Vague prompts produce vague answers. That's not a model limitation.

#### Q20.4 — What is a system prompt?
Standing instructions that apply to the whole conversation — the role and the
rules — kept separate from what the user types each turn.

#### Q20.5 — What is chain-of-thought, and when does it hurt?
Asking it to reason step by step before answering. It helps on anything with
multiple steps.

It hurts when you want a short structured answer — it adds length, latency and
cost for no benefit, and on simple classification it can talk the model out of
a correct first instinct.

#### Q20.6 — What is self-consistency?
Ask the same question several times, let it reason differently each time, and
take the most common answer. More reliable, several times more expensive.

#### Q20.7 — How do you get reliable JSON out of an LLM?
Ask for JSON and nothing else. Give it the exact structure you want. Use the
provider's structured-output mode if there is one. Set temperature to zero.
Then **validate** what comes back and retry if it's malformed.

The validation step is the one people skip, and it's the one that takes you
from "usually works" to "always works."

#### Q20.8 — What is ReAct prompting?
Alternating between thinking and doing: think about what's needed, take an
action, look at the result, think again. It's the pattern underneath most
agents.

#### Q20.9 — How do you handle a prompt that works 90% of the time?
Collect the failures into a test set. Then change **one thing** and measure
against it.

Treat prompts like code — versioned, with tests. Changing things by feel is
how you fix one case and break three others without noticing.

#### Q20.10 — What is prompt chaining, and why decompose?
Splitting a complicated task into several simpler prompts in sequence.

Each step is simpler, each can be tested on its own, and when something goes
wrong you know which step did it. One prompt doing five jobs is impossible to
debug.

#### Q20.11 — How do you reduce token cost in production?
Trim the system prompt. Retrieve fewer but better passages. Cache the parts of
the prompt that never change. Summarise long conversation history rather than
resending it. And send easy requests to a smaller model.

## LangChain and LangGraph

#### Q21.1 — What is LangChain?
A toolkit that wraps the common pieces of an LLM application — talking to
models, prompt templates, retrievers, memory, tools — behind one consistent
interface, so you can swap pieces without rewriting everything.

#### Q21.2 — What is a chain?
A fixed sequence of steps: build the prompt, call the model, parse the result.
Straight through, no branching, no going back.

#### Q21.3 — What is LangChain's retrieval QA doing under the hood?
Turn the question into numbers, pull the closest chunks from the store, slot
them into a prompt template with the question, call the model, and hand back
the answer plus the sources.

Nothing magic — it's the pipeline you'd write yourself, just packaged.

#### Q21.4 — What are the "stuff", "map-reduce" and "refine" chain types?
**Stuff**: put all the chunks in one prompt. Simple, but limited by context
size.

**Map-reduce**: answer from each chunk separately, then combine the answers.
Works on more text, costs more calls.

**Refine**: answer from the first chunk, then improve that answer with each
subsequent chunk. Good for summaries, but it's sequential so it's slow.

#### Q21.5 — What is LangGraph, and how does it differ from a chain?
It lets you build the flow as a **graph** rather than a line — with branches,
loops, and shared state that every step can read and write.

A chain goes forward once. A graph can decide where to go next, and it can go
back.

#### Q21.6 — Why did SafeSight need a graph rather than a chain?
Because the flow has a decision and a loop in it.

Work out what kind of violation it is. Look up candidate rules. **Check
whether those rules actually apply** — and if none of them do, go back and
search differently. Only then produce the answer.

A chain can't re-enter a step it's already passed. That's the whole reason.

#### Q21.7 — What is state in LangGraph?
A shared object passed between steps. Each step reads what's there and adds
its own findings.

It's what lets a later step see what an earlier one found — without it, each
step would be starting fresh.

#### Q21.8 — What is a conditional edge?
An arrow whose destination is decided by looking at the current state. It's how
you implement "if no rule matched, go back and try again."

#### Q21.9 — What is a checkpointer?
Something that saves the state as the graph runs, so a run can be paused,
resumed, or inspected. It's what makes human-in-the-loop review possible —
you can stop, let a person look, and carry on.

## Agents

#### Q21.10 — What is an AI agent?
A model that decides what to do next, uses tools, looks at what came back, and
keeps going until the job is done — rather than producing one fixed response.

#### Q21.11 — Agent vs chain — when would you NOT use an agent?
**When you already know the steps.**

Agents add latency, cost, and unpredictability. If you can draw the flowchart,
build the flowchart.

This is the senior answer, and most interviewers are specifically listening for
it. Reaching for an agent when a fixed sequence would do is the most common
mistake in this area.

#### Q21.12 — What is tool calling?
You describe the tools available — what each does and what arguments it takes.
The model produces a structured request to use one. **Your code** actually
runs it and hands back the result.

The model never executes anything itself. That distinction matters for
security.

#### Q21.13 — What is agent memory? Short vs long term?
Short-term is the conversation currently in the context window. Long-term is
saved somewhere and retrieved when relevant.

The distinction exists only because context windows are finite — otherwise
you'd just keep everything.

#### Q21.14 — What is a multi-agent system, and what's the usual failure?
Several specialised agents working together — one plans, one researches, one
checks.

The usual failure is compounding. Every handoff adds latency, cost, and
another chance for something to go wrong. Three agents at 90% reliability each
gives you about 73% overall.

#### Q21.15 — What is MCP?
Model Context Protocol — an agreed standard for how a model connects to tools
and data.

#### Q21.16 — What problem does MCP actually solve?
Without a standard, every tool needs custom wiring for every framework. Ten
tools and five frameworks means fifty separate integrations.

With it, each side implements the standard once. Think of it as a USB-C port
for model tooling — one shape that everything plugs into.

#### Q21.17 — What does an MCP server expose?
Three things: tools it can call, data it can read, and reusable prompt
templates.

#### Q21.18 — What is A2A?
Agent-to-Agent — a standard for agents built by **different teams or
companies** to find each other and work together, passing tasks and results
between them as peers.

#### Q21.19 — MCP vs A2A — the clean distinction?
**MCP connects an agent downward to tools and data. A2A connects an agent
sideways to other agents.**

They complement each other rather than compete. That one-liner is exactly what
they're listening for.

#### Q21.20 — What are the real risks of deploying agents?
Loops that never end and burn money. Tools being used in ways you didn't
intend, with real consequences. Hidden instructions in retrieved content
hijacking what it does. And no record of what happened afterwards.

Mitigate with hard step limits, giving each agent only the tools it genuinely
needs, requiring human approval before anything irreversible, and logging
every single call.

#### Q21.21 — How do you debug an agent that behaves unpredictably?
Trace every step — the prompt sent, the tool called, the result, and the state
at each point. LangSmith or equivalent.

Without tracing you are genuinely just guessing, because the same input can
produce a different path each time.

:::practice The three to have ready
Q21.6 — why SafeSight needed a graph, because that's a decision you made.
Q21.11 — when **not** to use an agent, because that's the senior answer.
Q21.19 — MCP down, A2A sideways, because it's one line and it's the question
you listed yourself.
:::

:::recap
- A good prompt is specific, bounded, and says what to do when it doesn't
  know.
- Validate structured output and retry — that's what makes it reliable.
- A chain goes forward once; a graph can branch and loop. SafeSight needed the
  loop.
- Don't use an agent when you already know the steps. Say this.
- The model requests a tool; your code runs it. Never the other way round.
- MCP connects downward to tools; A2A connects sideways to other agents.
- Without tracing, debugging an agent is guesswork.
:::
