# Four Learning Tracks
@short: Learning Tracks
@subtitle: Week-by-week plans from four realistic starting points
@tier: practice
@prereq: Chapter 1
@blurb: Generic roadmaps fail because they ignore where you are starting from. These four tracks assume different backgrounds, aim at different roles, and give week-by-week plans with a deliverable each week. Pick the one whose starting point matches yours, and do not mix them.
@objectives:
- Choose a track matched to your background and target role
- Follow a week-by-week plan with a concrete weekly deliverable
- Know what to skip, which is as important as what to study

## The tracks

@fig: tracks | 168 | Four paths. Durations assume roughly 12 hours a week and that you build something real throughout; none of them works by reading alone.

:::note The rule that applies to every track
Each week has a **deliverable**: something that runs, that you could show
somebody. A week without a deliverable did not happen. If you are behind,
cut the reading, never the building.
:::

## Track A --- Software engineer to AI engineer

**Assumes**: you write production software, use git and Docker daily, and
have written tests. **Target**: building LLM-powered products.
**Duration**: 12--16 weeks.

| Week | Focus | Deliverable |
|---|---|---|
| 1 | Ch 4 maths, the ESSENTIAL list only | Backprop by hand for a 2-layer MLP, matched to PyTorch |
| 2 | Ch 11 LLM fundamentals | Tokenisation and cost analysis of your own documents across three models |
| 3 | Ch 11 tool use, structured output | Extraction service hitting 95% schema validity |
| 4--5 | Ch 15 evaluation | A golden set, three graders, a validated judge, CI integration |
| 6--7 | Ch 12 retrieval | RAG pipeline with hybrid search and a reranker, plus per-stage metrics |
| 8 | Ch 5 algorithms, interview patterns | 25 problems, patterns named |
| 9--10 | Ch 14 agents | An agent with budgets, three tools, a trajectory eval and a failure taxonomy |
| 11 | Ch 19 security | Injection attack on your own agent, then an architectural fix |
| 12 | Ch 16 serving basics | Cost and latency model; routing rule with measured savings |
| 13--16 | Ch 8 classical ML, Ch 17 MLOps, portfolio | One tabular project end to end; deploy the agent with monitoring |

@tbl: Track A. You are skipping deep learning internals (Ch 9--10) deliberately; add them later if you move toward ML engineering.

## Track B --- Data scientist to ML engineer

**Assumes**: statistics, sklearn, pandas, SQL. **Target**: owning models in
production. **Duration**: 16--24 weeks.

| Week | Focus | Deliverable |
|---|---|---|
| 1--3 | Ch 3 engineering | A notebook converted into a tested, typed, containerised package with CI |
| 4--5 | Ch 5 algorithms | 30 problems; explain the row-versus-column traversal gap |
| 6--7 | Ch 6 data engineering | Point-in-time-correct feature pipeline with validation and a skew test |
| 8 | Ch 8 classical ML, the production half | Calibration, cost-matrix thresholds, SHAP explanation to a non-specialist |
| 9--12 | Ch 9 deep learning | Transformer from scratch; overfit a batch; induce and diagnose six bugs |
| 13--14 | Ch 17 MLOps | Registry, shadow deploy, canary with auto-rollback, monitoring, runbook |
| 15--16 | Ch 11--12 LLM and retrieval | RAG pipeline with per-stage evaluation |
| 17--18 | Ch 15 evaluation | Harness for both a classical and an LLM system |
| 19--24 | Ch 10, 16, 18 plus a capstone | Distributed fine-tune; serving with measured cost; one full system |

@tbl: Track B. The engineering weeks at the start are the ones people want to skip and the ones that matter most.

## Track C --- Student or career changer

**Assumes**: some programming, no production experience. **Target**: a first
role. **Duration**: 36--48 weeks. Be honest with yourself about this number.

| Weeks | Focus | Deliverable |
|---|---|---|
| 1--6 | Ch 3 Python and engineering | Three packaged, tested projects; git fluency |
| 7--12 | Ch 4 maths | Backprop by hand; bootstrap confidence intervals; a probability notebook |
| 13--18 | Ch 5 algorithms | 75 problems across all patterns; the DSA companion volume |
| 19--22 | Ch 6 data | SQL fluency; a pipeline with validation and backfill |
| 23--26 | Ch 8 classical ML | Two tabular projects, deployed, with honest evaluation |
| 27--32 | Ch 9 deep learning | Transformer from scratch; a fine-tune; the debugging playbook |
| 33--38 | Ch 11--15 foundation models | RAG system, agent, and an evaluation harness for both |
| 39--44 | Ch 16--17 production | Serve something; monitor it; write the runbook |
| 45--48 | Portfolio and applications | Three polished projects, written up; Ch 23 |

@tbl: Track C. The temptation is to start at week 33. Everybody who does so stalls, because the foundations weeks are what make the later weeks productive rather than imitative.

## Track D --- ML engineer to research engineer

**Assumes**: you train and deploy models. **Target**: implementing and
scaling research. **Duration**: 24--36 weeks.

| Weeks | Focus | Deliverable |
|---|---|---|
| 1--4 | Ch 4 maths, deeper | Derive attention gradients; read three papers' derivations |
| 5--10 | Ch 9 deep learning internals | Reimplement three papers from scratch and match reported numbers |
| 11--16 | Ch 10 training at scale | Multi-node FSDP run; profile; fix a communication bottleneck |
| 17--22 | Ch 18 hardware | Triton kernels; roofline analysis; beat a framework default |
| 23--28 | Ch 13 post-training | SFT, DPO and a GRPO-style run with verifiable rewards |
| 29--36 | Original work | Reproduce a recent result, then extend it; write it up |

@tbl: Track D. The reimplementation weeks are the whole track; reading papers without implementing them does not produce this skill.

:::pitfall The four ways tracks fail
1. **Mixing tracks.** Doing a bit of each produces breadth with no depth and
   no portfolio.
2. **Reading without building.** Recognition feels like knowledge and
   disappears.
3. **Starting in the middle.** Track C's weeks 1--18 are what make weeks
   33--48 productive rather than imitative.
4. **No deadline.** A track without dates becomes indefinite. Put the dates in
   a calendar and treat them as real.
:::

:::insight If you have less time than the track assumes
Halve the scope, not the rigour. Better to do half the weeks properly, with
deliverables, than all of them superficially. The deliverables are what you
show an employer and what you actually retain; the reading is the scaffolding.
:::

:::recap
- Four tracks from four starting points; pick one and do not mix.
- Every week has a deliverable; a week without one did not happen.
- Track A (SWE to AI engineer) is the shortest at 12--16 weeks; Track C
  (career change) is honestly 36--48.
- If you are behind, cut reading, never building.
- Put real dates in a calendar; a track without deadlines becomes indefinite.
:::
