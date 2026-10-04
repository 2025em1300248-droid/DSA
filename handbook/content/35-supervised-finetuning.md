# Supervised Fine-Tuning
@short: Fine-Tuning
@subtitle: LoRA, QLoRA, and the data work that decides the outcome
@tier: advanced
@prereq: Chapters 23, 26
@blurb: Fine-tuning became cheap enough that teams reach for it far too early, and powerful enough that when it is the right tool it is decisive. This chapter covers how to tell which case you are in, how LoRA actually works, how to prepare the data --- which is where the result is determined --- and how to evaluate a fine-tune honestly, including what it broke.
@objectives:
- Choose the cheapest intervention that could solve your problem
- Explain LoRA and QLoRA and choose rank, alpha and target modules
- Prepare SFT data, including the masking detail that ruins runs
- Evaluate a fine-tune against a properly tuned prompted baseline
- Detect and mitigate catastrophic forgetting

## The ladder, and where to stop

@fig: adaptation_ladder_hb | 166 | The adaptation ladder. Each rung costs roughly an order of magnitude more effort than the one below. Climb only when the rung below has been genuinely exhausted --- which means measured, not merely attempted.

| Rung | Effort | Needs | Fixes |
|---|---|---|---|
| Prompt + few-shot | hours | nothing | most format and tone problems |
| Structured output + tools | days | schemas | validity, exactness, actions |
| Retrieval | days--weeks | a corpus | missing or changing knowledge |
| **LoRA fine-tune** | 1--2 weeks | 1k--50k examples | persistent style, format, domain behaviour |
| Full fine-tune | weeks | 50k+ examples, many GPUs | deep behavioural change |
| Preference optimisation | weeks | preference pairs | subjective quality, safety |
| Pre-training | months | trillions of tokens | a new base capability |

@tbl: The ladder. The honest answer for most teams is rung 1, 2 or 3; the fourth is the first that requires real machine-learning work.

:::insight What fine-tuning does and does not do
**Does well:** teach a consistent output format; adopt a domain's vocabulary
and register; follow a long, complicated instruction set reliably without
spending the context on it; reduce the cost of a task by moving behaviour from
a long prompt into the weights; make a small model do one narrow job as well
as a large general one.

**Does badly:** add factual knowledge (retrieval does this better, is
auditable, and updates without retraining); fix reasoning (that is a base
model property); keep up with changing information.

The clearest signal that you need fine-tuning is: *the prompted model can do
it, but not consistently, and the prompt has stopped improving.*
:::

## LoRA

A weight update learned by full fine-tuning is empirically close to low-rank.
So instead of learning $\Delta W \in \mathbb{R}^{d\times k}$, learn
$BA$ with $B \in \mathbb{R}^{d\times r}$, $A \in \mathbb{R}^{r \times k}$ and
$r \ll \min(d, k)$:

$$W' = W + \frac{\alpha}{r} BA$$

```python title="LoRA, implemented"
import torch, torch.nn as nn, math

class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r=16, alpha=32, dropout=0.05):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad_(False)                    # the base stays frozen
        self.A = nn.Parameter(torch.empty(r, base.in_features))
        self.B = nn.Parameter(torch.zeros(base.out_features, r))
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))
        # B starts at ZERO, so BA = 0 and the model is unchanged at step 0.
        self.scale = alpha / r
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        return self.base(x) + self.drop(x) @ self.A.T @ self.B.T * self.scale
```

The zero initialisation of $B$ is essential: it means the adapted model starts
exactly equal to the base model, so training begins from a known-good point
rather than from a random perturbation.

```python title="Parameter accounting"
# d = 4096, r = 16:
#   full:  4096 * 4096       = 16.8M parameters per matrix
#   LoRA:  2 * 4096 * 16     = 131k parameters per matrix   (128x fewer)
#
# A 7B model with LoRA on q, k, v, o, gate, up, down at r=16:
#   ~40M trainable parameters out of 7B  -> 0.6%
#   Optimiser state: 40M * 8 bytes = 320 MB instead of 56 GB.
```

| Hyperparameter | Guidance |
|---|---|
| `r` | 8--16 for style and format; 32--64 for new domain behaviour; above 128 rarely helps |
| `alpha` | 2× `r` is the common default; it is a scale, so `alpha/r` is the real knob |
| Target modules | all linear layers beats attention-only, consistently |
| Learning rate | 1e-4 to 3e-4 --- about 10× a full fine-tune, because fewer parameters move |
| Dropout | 0.05--0.1 on small datasets, 0 on large ones |

@tbl: LoRA settings. The target-modules row is the one most often left at the library default (attention only); including the MLP projections is a consistent improvement for a small memory cost.

**QLoRA** quantises the frozen base model to 4-bit (NF4) and keeps the
adapters in bf16. Gradients flow through the quantised weights by
dequantising on the fly. The result is roughly a 4× memory reduction with
very little quality loss, and it is what makes fine-tuning a 70B model on a
single 80 GB device possible.

## The data, which is what actually decides it

```python title="The SFT format, and the masking detail"
example = {
    "messages": [
        {"role": "system",    "content": "You are a clinical coding assistant."},
        {"role": "user",      "content": "Patient presents with..."},
        {"role": "assistant", "content": '{"icd10": "J45.909", ...}'},
    ]
}

# CRITICAL: compute the loss on the ASSISTANT tokens only.
# Training on the prompt tokens teaches the model to generate questions,
# wastes capacity, and measurably degrades the behaviour you wanted.
labels = input_ids.clone()
labels[~assistant_mask] = -100          # -100 = ignored by cross_entropy
```

:::warning The three data mistakes that waste a fine-tuning run
**1. Loss on the prompt tokens.** Many quick scripts omit the mask. The run
completes, the loss looks fine, and the model is worse than the prompted
baseline. Verify by decoding the positions where `labels != -100`.

**2. Inconsistent formatting.** If some examples wrap the answer in a code
fence and others do not, the model learns a distribution over both and you get
each about half the time. Normalise ruthlessly; the model will reproduce your
inconsistencies faithfully.

**3. Training on your own model's outputs without filtering.** It amplifies
existing errors and narrows diversity. Filter by verification wherever the
task permits it (Chapter 16).
:::

| Dataset size | What it can achieve |
|---|---|
| 50--200 | format and tone only; high variance |
| 500--2,000 | reliable format, basic domain adaptation --- the usual sweet spot |
| 5,000--20,000 | solid domain behaviour, complex instruction following |
| 50,000+ | diminishing returns for LoRA; consider a full fine-tune |

@tbl: Data sizing. A thousand carefully constructed, consistent examples beat ten thousand scraped ones; this is the most reliable finding in applied fine-tuning.

## Training and evaluation

```python title="A fine-tuning run, with the settings that matter"
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig

peft_config = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)

args = SFTConfig(
    num_train_epochs=2,                 # 2-3; more overfits fast on small data
    learning_rate=2e-4,
    lr_scheduler_type="cosine", warmup_ratio=0.03,
    per_device_train_batch_size=4, gradient_accumulation_steps=4,
    bf16=True, gradient_checkpointing=True,
    max_seq_length=2048, packing=True,  # pack short examples for efficiency
    eval_strategy="steps", eval_steps=50,
    load_best_model_at_end=True,        # early stopping on validation loss
)
```

:::warning Evaluate against a *properly tuned* prompted baseline
The usual comparison is a fine-tune against a first-draft prompt, which the
fine-tune wins --- and tells you nothing. Spend a day on the prompt first,
with few-shot examples drawn from the same data (Chapter 31), and compare
against that.

A meaningful fine-tuning report has four numbers: the tuned prompted baseline,
the fine-tune, the cost of each per thousand requests, and the result on a
**held-out set from a different time period** than the training data. And it
reports what got worse --- see below.
:::

## Catastrophic forgetting

Fine-tuning on a narrow distribution degrades everything outside it. The
model gets better at your task and worse at following general instructions,
at other languages, at refusing unsafe requests, and at reasoning.

```python title="Measure what you broke, not just what you improved"
RETAIN = {
    "general_instructions": load("ifeval_subset"),    # instruction following
    "reasoning":            load("gsm8k_subset"),     # multi-step reasoning
    "safety":               load("refusal_set"),      # does it still refuse?
    "other_languages":      load("multilingual_subset"),
}

before = {k: evaluate(base_model, d) for k, d in RETAIN.items()}
after  = {k: evaluate(tuned_model, d) for k, d in RETAIN.items()}
for k in RETAIN:
    print(f"{k:<24} {before[k]:.3f} -> {after[k]:.3f}  "
          f"({after[k]-before[k]:+.3f})")
```

| Mitigation | Effect |
|---|---|
| Lower `r` and fewer target modules | less capacity to overwrite |
| Mix 5--20% general instruction data into the training set | the standard fix, and it works |
| Fewer epochs, early stopping on a retention set | prevents over-specialisation |
| Keep the adapter separate and merge only at serving | lets you A/B, and roll back instantly |
| Lower learning rate | smaller weight movement overall |

@tbl: Forgetting mitigations. The second row is the one to reach for first: a modest fraction of general data costs little and preserves most of the base behaviour.

:::practice The task
Choose a task where a prompted model is nearly good enough. (a) Spend a day
tuning the prompt properly and record the baseline on a 200-item golden set.
(b) Build 1000 consistent training examples; verify the assistant-only masking
by decoding the unmasked positions. (c) Run a LoRA fine-tune; compare against
the baseline on a held-out set from a *later* time period. (d) Measure
retention on four capability sets before and after. (e) Repeat with 10%
general instruction data mixed in and compare retention. (f) Compute the cost
per thousand requests for both approaches, including the fine-tune's
amortised training cost.

**You have this skill when** your fine-tuning report states what improved,
what degraded, what it cost, and whether the prompted baseline would have been
enough.
:::

:::exercise
1. Verify empirically that a full fine-tune's weight update is approximately
   low-rank, by taking the SVD of $\Delta W$ and plotting the singular values.
2. Show that LoRA with $B$ initialised randomly rather than at zero makes
   early training unstable.
3. † Sweep $r \in \{4, 8, 16, 64, 128\}$ at fixed $\alpha/r$ and plot quality
   against trainable parameters. Where does it saturate?
4. Train with and without the assistant-only mask and compare both the loss
   curve and the generated outputs.
5. Deliberately introduce formatting inconsistency into 30% of examples
   and measure the resulting output variance.
6. † Measure catastrophic forgetting across four capability sets, then repeat
   with 10% general data mixed in. Quantify the recovery.
7. Compute the break-even request volume at which a fine-tuned small model is
   cheaper than a prompted large one, including training cost.
:::

:::recap
- Climb the adaptation ladder one rung at a time; fine-tuning is the fourth,
  and most problems are solved by the first three.
- Fine-tuning teaches format, style and domain behaviour; it does not reliably
  add facts or fix reasoning.
- LoRA learns a low-rank update with $B$ initialised to zero, so the model
  starts unchanged; target all linear layers, not just attention.
- QLoRA quantises the frozen base to 4-bit for a ~4× memory reduction.
- Compute the loss on assistant tokens only; normalise formatting ruthlessly;
  a thousand consistent examples beat ten thousand scraped ones.
- Compare against a *properly tuned* prompt, on a held-out set from a later
  period.
- Measure what you broke; mix in 5--20% general data to retain it.
:::
