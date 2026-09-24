# Post-Training: Fine-Tuning and Alignment
@short: Post-Training
@subtitle: The rungs of the adaptation ladder, and why most teams climb too far
@tier: advanced
@prereq: Chapters 9, 11
@blurb: Fine-tuning has become accessible enough that teams reach for it far too early, and powerful enough that when it is the right tool it is decisive. This chapter covers the full adaptation ladder from prompting to preference optimisation, with an emphasis on the decision of where to stop.
@objectives:
- Choose the cheapest intervention that could solve the problem
- Run a LoRA or QLoRA fine-tune correctly, including the data work
- Understand SFT, reward models, and the modern preference-optimisation family
- Evaluate a fine-tune honestly, including what it broke

## The ladder

@fig: adaptation_ladder | 172 | Each rung costs roughly an order of magnitude more effort than the one below it. Climb one at a time and measure. The single most expensive mistake in applied AI is fine-tuning around a problem that better context would have solved.

## When fine-tuning is actually right

| Fine-tune when | Do not fine-tune when |
|---|---|
| You need a consistent format, tone or style | You need the model to know new facts |
| You need a narrow task done cheaply by a small model | The knowledge changes frequently |
| You need lower latency or cost at fixed quality | You have fewer than a few hundred good examples |
| The task is hard to specify but easy to demonstrate | A better prompt or retrieval step is untried |
| You need to distil a large model's behaviour into a small one | You cannot evaluate the result |

@tbl: The decision. The left column is about *behaviour*; the right column is mostly about *knowledge*, which retrieval serves better. Facts injected by fine-tuning are learned unreliably and cannot be updated.

## The capabilities

:::checklist CORE --- supervised fine-tuning
- Data format: instruction/response pairs, chat templates, and getting the
  template exactly right for the base model (a mismatched template silently
  destroys quality)
- Loss masking: train on the response tokens only, not on the prompt
- Data quality over quantity --- a thousand carefully curated examples
  routinely beat a hundred thousand scraped ones
- Packing sequences to avoid padding waste; attention masking across packed
  document boundaries
- Hyperparameters: a much lower learning rate than pretraining
  ($10^{-5}$ to $10^{-4}$ for full, $10^{-4}$ to $10^{-3}$ for LoRA),
  one to three epochs, and early stopping on a held-out set
- Catastrophic forgetting: measure general capability before and after, not
  only the target task
:::

:::checklist CORE --- parameter-efficient fine-tuning
- **LoRA**: freeze the base weights and learn a low-rank update
  $\Delta W = BA$. Rank 8--64 covers most cases; also choose which modules
  to adapt (attention projections at minimum, often the MLP too)
- **QLoRA**: quantise the frozen base to 4-bit and train LoRA adapters on
  top, which brings large models within reach of a single GPU
- The alpha/rank scaling relationship, and why people get it wrong
- Merging adapters back into base weights for serving, and serving multiple
  adapters against one base model
- Awareness of the wider PEFT family: prefix tuning, prompt tuning, IA³, DoRA
:::

:::checklist CORE --- preference optimisation
- Why SFT alone is insufficient: it teaches the model to imitate, not to
  prefer, and cannot express "this answer is better than that one"
- **RLHF**: train a reward model on pairwise preferences, then optimise the
  policy with PPO against it, with a KL penalty to the reference model.
  Powerful, complex, and unstable
- **DPO**: optimise directly on preference pairs with a closed-form objective
  and no separate reward model. Far simpler, now the default starting point
  for most teams
- The wider family and what each changes: IPO (regularisation), KTO (works
  from unpaired binary feedback), ORPO (folds preference into SFT), SimPO
- **GRPO** and group-relative methods: sample a group of completions, score
  them, and use the within-group relative advantage. Central to training
  reasoning models with verifiable rewards
- **RLVR** (reinforcement learning from verifiable rewards): when correctness
  is checkable --- maths, code that runs, format that parses --- the reward is
  a program rather than a model, which removes reward hacking at its source
- Reward hacking, and why a held-out qualitative review is not optional
:::

:::checklist CORE --- evaluation of a fine-tune
- A held-out set from the same distribution, built *before* training
- General capability benchmarks before and after, to measure what you broke
- Format and instruction-following compliance
- Safety behaviour, which fine-tuning frequently degrades even when the
  training data is benign
- A/B comparison against the pre-fine-tune model on real traffic where
  possible
:::

:::checklist AWARENESS
- Continued pretraining for a new domain or language
- Model merging and model soups
- Distillation: training a small student on a large teacher's outputs or
  logits --- often the highest-value production technique in this chapter
- Quantisation-aware fine-tuning
:::

:::insight The economic case that actually justifies fine-tuning
It is rarely "the big model cannot do this". It is usually: the big model can
do it, at $X$ per million tokens and $Y$ milliseconds, and a fine-tuned 3B
model can do it at $X/30$ and $Y/5$. At sufficient volume that difference
funds the entire project. Frame the decision as an economics question with
measured numbers, not as a capability question, and it becomes much easier to
answer.
:::

## How to tell you have it

:::practice The task
Pick a narrow task where you can measure correctness automatically.
1. Establish a prompted baseline on a frontier model and on a small model.
   Record quality, latency and cost.
2. Add retrieval or better context. Measure again. Frequently you stop here.
3. Build 500--2,000 high-quality training examples. This is most of the work.
4. LoRA fine-tune the small model. Measure quality, latency and cost.
5. Measure what you broke: general benchmarks, instruction-following, safety
   behaviour.
6. Compute the break-even volume at which the fine-tune pays for itself,
   including your time.
7. Write down, honestly, whether step 2 was already good enough.
:::

:::pitfall The five fine-tuning failures
1. **Wrong chat template.** The most common silent failure; quality collapses
   for no visible reason.
2. **Training on the prompt tokens.** Loss masking omitted; the model learns
   to generate prompts.
3. **Fine-tuning for knowledge.** Facts learned this way are unreliable and
   unpatchable. Use retrieval.
4. **No before/after on general capability.** You fixed one task and
   degraded ten.
5. **Too few, too low-quality examples.** A few hundred excellent examples
   beat tens of thousands of mediocre ones, and most teams have the ratio
   backwards.
:::

:::note Time to competence
**6--8 weeks** for SFT and LoRA including the data work; another **4--6
weeks** for preference optimisation. The data curation is the majority of the
time in both cases, which is itself the lesson.
:::

:::recap
- Climb the adaptation ladder one rung at a time: prompt, structure, retrieve,
  optimise, LoRA, full SFT, preference tuning.
- Fine-tune for behaviour, not for knowledge; facts belong in retrieval.
- LoRA and QLoRA cover most real needs; get the chat template and the loss
  masking right or nothing else matters.
- DPO is the practical default for preference optimisation; GRPO and
  verifiable rewards are how reasoning behaviour is trained.
- Always measure what the fine-tune broke, not only what it improved.
- The justification is usually economic --- cost and latency at volume --- not
  a capability the big model lacks.
:::
