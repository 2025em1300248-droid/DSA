# Preference Optimisation
@short: Preference Optimisation
@subtitle: RLHF, DPO, GRPO --- training on what is better, not what is correct
@tier: advanced
@prereq: Chapter 35
@blurb: Supervised fine-tuning teaches a model to imitate one correct answer. Many of the things we want --- helpfulness, tone, safety, taste --- have no single correct answer, only better and worse ones. This chapter covers the family of methods that train on comparisons, from classical RLHF through DPO to verifiable rewards, and the failure modes each brings.
@objectives:
- Explain why imitation is insufficient and comparison is the alternative
- Describe the RLHF pipeline and what each component does
- Derive DPO's insight and implement its loss
- Choose between DPO, its variants, and online RL methods
- Recognise reward hacking, length bias and over-refusal

## Why comparisons

For "write a polite rejection email" there is no single target to imitate.
SFT on one human-written example teaches the model to reproduce *that*
email's idiosyncrasies. But people can reliably say which of two emails is
better --- and a comparison is far cheaper and more consistent to collect than
an ideal answer is to write.

:::insight The asymmetry that the whole field rests on
Writing a good answer is hard; judging which of two answers is better is easy.
Annotators agree far more on comparisons than on absolute ratings, and the
labels are cheaper. Every method in this chapter exploits that asymmetry.

The same asymmetry is why LLM-as-judge works better for pairwise comparison
than for absolute scoring (Chapter 37), and why ranking metrics are more
robust than scoring ones.
:::

## Classical RLHF

@fig: rlhf_pipeline | 168 | The three stages. SFT produces a policy worth improving, the reward model learns human preferences, and PPO optimises against it with a KL leash back to the reference. Each stage has its own failure mode.

**Stage 1 --- SFT.** Fine-tune on demonstrations to get a model that at least
produces the right *kind* of output. Without this, later stages have nothing
useful to improve.

**Stage 2 --- Reward model.** Train a model $r_\phi$ to score responses, using
the Bradley--Terry likelihood of the observed preferences:

$$\mathcal{L} = -\log \sigma\big(r_\phi(x, y_w) - r_\phi(x, y_l)\big)$$

where $y_w$ is preferred over $y_l$. Note what this objective does: it only
constrains the *difference* of scores, so the absolute scale is arbitrary.

**Stage 3 --- PPO.** Optimise the policy to maximise reward, penalised by
divergence from the reference:

$$\max_\theta \;\; \mathbb{E}\big[r_\phi(x, y)\big] \;-\; \beta\, D_{KL}\big(\pi_\theta \,\|\, \pi_{\text{ref}}\big)$$

The KL term is a leash. Without it the policy drifts into whatever region of
output space scores highly under an imperfect reward model, which is usually
degenerate text.

:::pitfall RLHF's three practical problems
**Four models in memory.** Policy, reference, reward model and value model.
For a 7B policy that is a lot of GPU for one training run.

**Instability.** PPO has many hyperparameters --- clip range, GAE lambda,
value coefficient, batch composition --- and is genuinely sensitive to them.

**Reward hacking.** The policy finds inputs on which the reward model is
wrong and exploits them. Symptoms: responses become longer and longer; they
acquire formulaic flourishes; they hedge compulsively. The reward score rises
and human evaluation falls --- which is why you must evaluate with humans or a
held-out judge, never with the reward model you are optimising against.
:::

## DPO: skipping the reward model

The insight: for the KL-constrained objective above, the optimal policy has a
closed form,

$$\pi^*(y \mid x) \;\propto\; \pi_{\text{ref}}(y \mid x)\,\exp\!\big(r(x,y)/\beta\big)$$

Rearranging gives the reward *implied* by any policy:

$$r(x, y) = \beta \log \frac{\pi(y \mid x)}{\pi_{\text{ref}}(y \mid x)} + \text{const}$$

Substitute that into the Bradley--Terry loss and the reward model vanishes.
What remains is a supervised loss on preference pairs, trainable with ordinary
backpropagation:

```python title="DPO loss, complete"
import torch.nn.functional as F

def dpo_loss(policy_chosen_lp, policy_rejected_lp,
             ref_chosen_lp, ref_rejected_lp, beta=0.1):
    """All arguments are summed log-probabilities of the response tokens."""
    pi_logratio  = policy_chosen_lp - policy_rejected_lp
    ref_logratio = ref_chosen_lp    - ref_rejected_lp
    logits = beta * (pi_logratio - ref_logratio)
    loss = -F.logsigmoid(logits).mean()

    # Useful diagnostics: these are the implicit rewards.
    chosen_rw   = beta * (policy_chosen_lp   - ref_chosen_lp).detach()
    rejected_rw = beta * (policy_rejected_lp - ref_rejected_lp).detach()
    acc = (chosen_rw > rejected_rw).float().mean()
    return loss, dict(accuracy=acc, margin=(chosen_rw - rejected_rw).mean())
```

Two models instead of four, no sampling loop, no PPO hyperparameters, and
training that behaves like ordinary supervised learning.

| Method | Models in memory | Online? | Notes |
|---|---|---|---|
| PPO | 4 | yes | strongest ceiling, hardest to run |
| **DPO** | 2 | no | the practical default |
| IPO | 2 | no | fixes DPO's overfitting on deterministic preferences |
| KTO | 2 | no | needs only good/bad labels, not pairs |
| ORPO | 1 | no | merges SFT and preference in one stage |
| SimPO | 1 | no | reference-free, length-normalised |
| **GRPO** | 2 | yes | group-relative; no value model; used for reasoning |

@tbl: The family. DPO is where to start. KTO is valuable when your data is thumbs-up/thumbs-down rather than pairs, which is what production feedback usually looks like.

## GRPO and verifiable rewards

For tasks with a checkable answer --- mathematics, code, structured extraction
--- you do not need a learned reward model at all. Run the code; check the
answer; that is the reward.

```python title="GRPO: group-relative advantage, no value model"
def grpo_step(prompts, policy, ref, reward_fn, group=8, beta=0.04):
    losses = []
    for prompt in prompts:
        # 1. Sample a GROUP of responses for the same prompt.
        responses = [policy.sample(prompt, temperature=1.0) for _ in range(group)]
        rewards = torch.tensor([reward_fn(prompt, r) for r in responses])

        # 2. The advantage is relative to the group's own mean.
        #    This replaces the value model entirely.
        adv = (rewards - rewards.mean()) / (rewards.std() + 1e-8)

        # 3. Policy-gradient term, with a KL leash to the reference.
        for r, a in zip(responses, adv):
            lp     = policy.logprob(prompt, r)
            ref_lp = ref.logprob(prompt, r).detach()
            kl = lp - ref_lp
            losses.append(-(a * lp - beta * kl))
    return torch.stack(losses).mean()
```

The group-relative baseline is the trick: PPO needs a learned value model to
estimate "how good is this state", and GRPO gets the same variance reduction
by comparing samples from the *same* prompt against each other. One fewer
model, and a much simpler training loop.

:::insight Why verifiable rewards changed what is trainable
A learned reward model is an approximation that can be gamed. A unit test
cannot be gamed by writing more eloquently --- the code either passes or it
does not.

So for any task where correctness is checkable, you can train with a reward
that is exactly right: mathematics with a known answer, code with tests, SQL
compared against a reference result set, structured output against a schema,
a game with a score. This is the mechanism behind the recent step change in
reasoning capability, and it is available to you for any task you can write a
checker for.

The limitation is equally clear: it only works where you can write the
checker. For helpfulness and tone you are back to learned rewards or human
comparison.
:::

## The failure modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Length bias** | responses grow steadily; quality does not | length-normalise the reward, or penalise length explicitly |
| **Reward hacking** | reward rises, human rating falls | evaluate with a held-out judge; cap training steps |
| **Over-refusal** | the model declines benign requests | include benign-but-sensitive prompts labelled as should-answer |
| **Mode collapse** | outputs become samey | raise $\beta$; measure output diversity |
| **Verbose hedging** | every answer caveats everything | include concise answers as *chosen* in the pairs |
| **Forgetting** | general capability drops | the Chapter 35 retention suite |

@tbl: Six failure modes. Length bias is near-universal: annotators mildly prefer longer answers, the reward model learns "longer is better", and the policy exploits it. Always report mean response length alongside the reward.

```python title="The diagnostics to log during any preference run"
#  reward / implicit margin   — should rise, then flatten
#  KL(policy || reference)    — should rise slowly; a jump means drift
#  mean response length       — should be FLAT; rising means length bias
#  pairwise accuracy          — fraction where chosen > rejected
#  held-out judge win rate    — the only number that actually matters
#  output diversity           — distinct n-grams; falling means collapse
```

:::practice The task
Starting from an SFT model: (a) collect or construct 1000 preference pairs for
a task you care about; (b) train with DPO and log all six diagnostics;
(c) plot mean response length over training and check for length bias;
(d) evaluate with a held-out pairwise judge (Chapter 37), not the training
signal; (e) for a verifiable sub-task, implement a checker and run a GRPO-style
loop, comparing the result to DPO; (f) measure over-refusal on a set of benign
but sensitive prompts.

**You have this skill when** you can run a preference optimisation and state
confidently whether the improvement is real or is length bias.
:::

:::exercise
1. Derive the closed-form optimal policy for the KL-constrained reward
   objective.
2. Show how substituting the implied reward into Bradley--Terry yields the DPO
   loss.
3. † Train DPO at $\beta \in \{0.01, 0.1, 0.5\}$ and plot KL divergence, output
   diversity and judge win rate against $\beta$.
4. Demonstrate length bias: plot reward against response length in your
   preference data, then correct for it and retrain.
5. Implement KTO and train on unpaired good/bad labels. Compare with DPO on
   the same underlying data.
6. † Build a verifiable reward for a task of yours and run a GRPO loop.
   Report pass rate against training step.
7. Measure over-refusal before and after a safety-oriented preference run, and
   construct the data that would fix an over-refusal you find.
:::

:::recap
- Judging which of two answers is better is far easier and cheaper than
  writing the best answer; every method here exploits that.
- RLHF is SFT, then a Bradley--Terry reward model, then PPO with a KL leash
  --- four models, unstable, and gameable.
- DPO derives the implied reward from the policy itself, eliminating the
  reward model and the sampling loop; it is the practical default.
- KTO takes unpaired thumbs-up/down labels, which is what production feedback
  actually looks like.
- GRPO replaces the value model with a group-relative baseline and pairs well
  with verifiable rewards.
- Verifiable rewards cannot be gamed by style, which is why they produced a
  step change in reasoning --- but they need a checker.
- Watch length bias, reward hacking, over-refusal and mode collapse; the only
  number that matters is a held-out judge's win rate.
:::
