# Deploying and Operating Models
@short: MLOps
@subtitle: Shipping safely, and knowing when it has gone wrong
@tier: core
@prereq: Chapter 37
@blurb: Training a model is a project; running one is a job. This chapter covers the operational layer --- registries, deployment strategies, monitoring that detects silent degradation, and the incident response that turns a 3am page into a ten-minute rollback instead of a four-hour investigation.
@objectives:
- Register models with enough lineage to answer "what produced this?"
- Deploy with shadow, canary and rollback rather than a cutover
- Monitor the four signals that matter, including the one with no labels
- Detect drift and distinguish it from a broken pipeline
- Write a runbook that someone else can follow at 3am

## The registry

```python title="What a registered model version must record"
{
  "name": "fraud-detector",
  "version": 47,
  "stage": "production",                 # none | staging | production | archived
  "artifact_uri": "s3://models/fraud/47/",
  "artifact_sha256": "9f2c...",

  "git_sha": "a3f9c21", "git_dirty": false,
  "training_data": {"snapshot": "2026-03-01", "rows": 4_812_339,
                    "hash": "7bd1..."},
  "features": ["f_amount_z", "f_velocity_7d", "..."],   # exact, ordered
  "feature_pipeline_version": "3.2.0",

  "metrics": {"auc": 0.912, "auc_ci": [0.905, 0.918],
              "pr_auc": 0.447, "ece": 0.013},
  "threshold": 0.029, "threshold_basis": "cost matrix v2, 2026-02",

  "env": {"python": "3.12.3", "lock_sha256": "1a2b...",
          "image": "registry/fraud@sha256:4c5d..."},
  "approved_by": "...", "approved_at": "2026-03-14T09:12:00Z"
}
```

:::insight The question a registry has to answer
Six months from now, someone asks: *why did the model decline this
transaction on 14 March?*

Answering it requires the exact weights, the exact feature pipeline, the exact
threshold, and the exact input. If any one is missing you cannot reconstruct
the decision --- and in regulated settings that is not merely inconvenient, it
is a compliance failure.

Log the model version with every prediction. It is four bytes and it is the
difference between an answer and an apology.
:::

## Deployment

@fig: deployment_stages | 164 | The deployment ladder. Each stage increases exposure and the evidence required to proceed. Shadow mode is the one most often skipped and the one that catches the most, because it compares the new model against the old on identical live traffic at zero user risk.

| Stage | Traffic | Catches | Duration |
|---|---|---|---|
| Offline evaluation | none | quality regressions | minutes |
| **Shadow** | 100% mirrored, no effect | skew, latency, crashes, disagreement | days |
| **Canary** | 1--5% | real-world quality, rare inputs | hours--days |
| Progressive | 5 → 25 → 50 → 100% | load-dependent problems | days |
| Full | 100% | — | — |

@tbl: Five stages. Shadow mode is where train--serve skew (Chapter 14) surfaces: the new model runs on live inputs, and you compare its features and predictions against the offline pipeline's. Any mismatch is a bug you would otherwise have shipped.

```python title="Shadow mode, which is cheap and catches the most"
async def handle(request):
    features = feature_pipeline(request)
    prediction = production_model.predict(features)

    asyncio.create_task(shadow(request, features, prediction))   # fire and forget
    return prediction                     # the user is never affected

async def shadow(request, features, prod_pred):
    try:
        offline_features = offline_pipeline(request)             # skew check
        log_skew(features, offline_features)
        cand = candidate_model.predict(features)
        log_shadow(request_id=request.id, prod=prod_pred, candidate=cand,
                   agree=(cand > T) == (prod_pred > T_prod))
    except Exception as e:
        log_shadow_error(e)               # NEVER let this affect the response
```

```python title="Canary with automatic rollback"
CANARY = dict(
    initial_pct=1, step_pct=[1, 5, 25, 50, 100], step_minutes=60,
    rollback_if=dict(
        error_rate_above=0.01,
        p95_latency_above_ms=800,
        prediction_rate_shift_above=0.20,     # distribution of OUTPUTS moved
        business_metric_drop_below=0.95,      # relative to control
    ),
)
```

The output-distribution check is the one that earns its place: it needs no
labels, it responds within minutes, and almost every serious model bug moves
the prediction distribution before anyone notices a business metric.

## Monitoring

:::checklist Four layers, in increasing order of lag
**1. System** (seconds). Error rate, p50/p95/p99 latency, throughput, memory,
queue depth, GPU utilisation. Ordinary service monitoring.

**2. Data** (minutes). Null rates, range violations, unseen categories, schema
mismatches, row counts, feature-staleness. Most model incidents begin here.

**3. Prediction** (minutes). The distribution of outputs, the mean score, the
positive rate at the threshold, the abstain rate. **No labels required**,
which is what makes it the workhorse.

**4. Outcome** (hours to months). Accuracy, calibration, business metrics ---
whatever you actually care about. The ground truth, and the slowest to arrive.
:::

```python title="Drift detection on features and predictions"
from scipy import stats
import numpy as np

def psi(expected, actual, bins=10):
    """Population stability index. <0.1 stable, 0.1-0.25 watch, >0.25 act."""
    edges = np.percentile(expected, np.linspace(0, 100, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected) + 1e-6
    a = np.histogram(actual, edges)[0] / len(actual) + 1e-6
    return float(np.sum((a - e) * np.log(a / e)))

def drift_report(reference, current, features):
    out = {}
    for f in features:
        out[f] = dict(
            psi=psi(reference[f], current[f]),
            ks_p=stats.ks_2samp(reference[f], current[f]).pvalue,
            null_rate_delta=current[f].isna().mean() - reference[f].isna().mean(),
        )
    return out
```

:::warning Drift is a symptom, not a diagnosis
A PSI of 0.4 on one feature usually means an upstream pipeline changed ---
a unit, a default, a join that started dropping rows. Genuine distribution
shift in the world is slower and shows on *many* features at once.

So the first question on a drift alert is never "should we retrain?" but
"did something break?". Check the data layer first. Retraining on broken data
bakes the bug into the model, and that is much harder to undo.
:::

| Pattern | Likely cause |
|---|---|
| One feature's PSI spikes, others flat | upstream pipeline change |
| Many features drift slowly together | real distribution shift |
| Null rate jumps on one feature | a source system changed or failed |
| Prediction distribution shifts, features stable | the model or threshold changed |
| Accuracy falls, nothing else moved | label definition changed, or feedback delay |

@tbl: Reading drift signals. The last row catches a subtle one: if your labels arrive late, a "sudden" accuracy drop may be an artefact of incomplete recent labels rather than a real regression.

## Retraining

| Trigger | Suits |
|---|---|
| Scheduled (weekly / monthly) | stable domains; simple, predictable |
| Performance-based | you have timely labels |
| Drift-based | labels are slow; use with the caveat above |
| Volume-based | after $N$ new labelled examples |
| Event-based | a known change: new product, new market, new policy |

@tbl: Retraining triggers. A scheduled retrain with a quality gate is the right default; it is simple, it is testable, and the gate stops a bad retrain reaching production.

```python title="A retraining job that cannot ship a worse model"
def retrain_and_gate():
    model = train(data_up_to=today)
    new = evaluate(model, holdout)
    cur = registry.get("production").metrics

    if new["auc"] < cur["auc"] - 0.005:
        alert("retrain REGRESSED; not promoting"); return
    if new["ece"] > 0.05:
        alert("retrain is miscalibrated; not promoting"); return
    if not fairness_ok(model, holdout):
        alert("fairness gate failed"); return

    v = registry.register(model, metrics=new, stage="staging")
    start_shadow(v)                       # humans promote from here
```

## The runbook

:::checklist What a 3am responder needs, in this order
1. **How to tell it is the model.** The three dashboards, in order: system,
   prediction distribution, data quality.
2. **How to roll back.** The exact command, the expected duration, and what
   the rollback does *not* undo (writes already made).
3. **How to disable the model entirely.** The fallback --- rules, the previous
   model, or a safe default --- and how to switch to it.
4. **Who to wake**, with names, not team aliases.
5. **The five most recent incidents** and what each turned out to be. This is
   the highest-value section and the one people omit.
:::

```bash title="The rollback must be one command"
./deploy.sh rollback --model fraud-detector --to 46
#   - repoints the serving alias to version 46
#   - takes ~90 seconds
#   - does NOT revert the feature pipeline (see runbook §4 if that changed)
#   - does NOT undo decisions already made
```

If rolling back takes more than two minutes or requires a code change, that
is the first thing to fix --- before any model improvement. Incident duration
is dominated by how long it takes to stop the bleeding, not by how long it
takes to find the cause.

:::practice The task
For a model you run: (a) write the registry record with full lineage and
confirm you can answer "why this prediction, six months ago?"; (b) implement
shadow mode and run it for a week --- report the skew found; (c) implement
canary with automatic rollback on the four conditions and trigger each one
deliberately; (d) implement PSI monitoring and alert on a feature you break on
purpose; (e) write the runbook and have a colleague who has never touched the
system roll back using only the runbook. Time them.

**You have this skill when** a colleague can roll back your model in two
minutes using only the runbook, and when a broken upstream feature pages you
before a user notices.
:::

:::exercise
1. Reconstruct a prediction from six months ago using only your registry.
   What was missing?
2. Implement shadow mode and find one genuine train--serve skew.
3. † Build the canary controller with automatic rollback and trigger each
   condition. Measure the time from trigger to full rollback.
4. Implement PSI and validate it against a known shift of known magnitude.
5. Construct a case where drift is caused by a pipeline bug and one where it
   is real. Show the signal patterns differ.
6. † Simulate delayed labels and show that a naive accuracy monitor reports a
   false regression. Design the fix.
7. Run a rollback drill with someone unfamiliar with the system. Record where
   the runbook failed them.
:::

:::recap
- A registry must record weights, data snapshot, feature pipeline version,
  threshold, environment and metrics --- enough to reconstruct any past
  decision.
- Deploy through shadow, canary and progressive rollout; shadow is the cheapest
  and catches the most, because it compares on identical live traffic.
- Monitor four layers: system, data, prediction distribution and outcomes.
  The prediction distribution needs no labels and moves first.
- Drift is a symptom: check the data pipeline before concluding the world
  changed.
- Scheduled retraining with a quality gate is the right default.
- Rollback must be one command taking under two minutes; incident duration is
  dominated by time-to-stop, not time-to-diagnose.
- The runbook's most valuable section is the list of past incidents.
:::
