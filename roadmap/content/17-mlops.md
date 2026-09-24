# MLOps and Production Practice
@short: MLOps
@subtitle: Everything between a working model and a system you can operate
@tier: core
@prereq: Chapters 3, 6
@blurb: MLOps is what happens when software operations meets a system whose behaviour depends on data that changes. The additional problems over ordinary software are reproducibility, drift, and the fact that a broken model produces plausible output rather than an error. This chapter covers the practices that address each.
@objectives:
- Make an experiment reproducible by construction rather than by discipline
- Version models, data and code together and roll back all three
- Deploy safely with shadow, canary and automatic rollback
- Monitor the things that actually detect a degrading system

## The capabilities

:::checklist ESSENTIAL --- experiment tracking and reproducibility
- Track every run: code commit, data version, config, environment,
  hyperparameters, metrics, artefacts. W&B and MLflow are the common choices
- Seed everything and record the seeds; know what remains non-deterministic
  on a GPU and decide whether you care
- Data versioning: DVC, LakeFS, Delta/Iceberg time travel, or content-hashed
  snapshots. "Trained on the data as of last Tuesday" must be a resolvable
  statement
- The reproducibility test: can you regenerate a model from three months ago
  and get the same metric? If not, you cannot debug a regression
:::

:::checklist ESSENTIAL --- CI/CD for ML
- Tests that run on every change: unit, data validation, a single-batch
  overfit test, a small end-to-end training smoke test, and the evaluation
  suite
- Model registry with stages (staging, production, archived) and a recorded
  lineage back to data and code
- Automated retraining pipelines where the data changes; a manual gate where
  the stakes are high
- Rollback that restores the model *and* the preprocessing *and* the config,
  because rolling back one of the three is how skew is introduced
:::

:::checklist ESSENTIAL --- deployment patterns
| Pattern | What it gives you |
|---|---|
| Shadow | Run the new model on real traffic, serve the old one, compare offline. Zero risk |
| Canary | Route 1--5%, watch metrics, expand or roll back automatically |
| Blue/green | Instant switch and instant rollback, at double the capacity |
| A/B | Measure the *business* effect, not just the model metric |
| Feature flag | Turn a model off without a deploy. Non-negotiable for LLM features |
:::

:::checklist CORE --- monitoring
- **Operational**: latency percentiles, error rate, throughput, saturation,
  cost per request
- **Data**: schema violations, null rates, range violations, freshness, volume
- **Drift**: input distribution (PSI, KS, or a simple binned divergence),
  prediction distribution, and --- when labels eventually arrive --- actual
  performance
- **Quality**: for LLM systems, continuous sampled grading against the rubric
  from Chapter 15
- **Business**: the metric the system exists to move
- Alert on the last two; dashboard the rest. Alerting on input drift produces
  noise, because features move constantly without performance changing
:::

:::checklist CORE --- the things that make it operable
- Runbooks: what to do when the alert fires, written before it fires
- On-call for ML systems, and accepting that "the model is worse" is a real
  incident class
- Postmortems that reach the data or process cause rather than stopping at
  "the model degraded"
- Cost attribution per feature, per team, per request. Without it, cost
  optimisation has no target
- Documentation: model cards, data sheets, decision records
:::

:::checklist CORE --- LLM-specific operations
- Prompt versioning as deployable artefacts, with an eval gate on change
- Model version pinning, and a plan for provider deprecations --- they happen
  with months of notice and break behaviour subtly
- Full request/response tracing with token counts and cost per span
- Semantic caching, with an invalidation story
- Spend limits and per-tenant quotas enforced in code
- Regression suites in CI on every prompt, model or retrieval change
:::

:::checklist AWARENESS
- Kubernetes for ML workloads: GPU scheduling, node selectors, operators
- Ray for distributed Python; KServe or BentoML for model serving
- Terraform and infrastructure as code
- Multi-region, data residency and failover
:::

:::insight The difference from ordinary software operations
A conventional service fails loudly: a 500, a timeout, a stack trace. A
machine learning system fails *quietly and plausibly* --- it returns a
confident, well-formatted, wrong answer, and every conventional monitor stays
green. This single difference justifies everything in this chapter that looks
like overhead: continuous quality sampling, drift monitoring, shadow
deployment, and treating "the output got worse" as a pageable incident.
:::

## How to tell you have it

:::practice The task
Take a model you have trained and put it into a state you could hand to an
on-call engineer.
1. Reproduce a three-month-old result from the tracked run. If you cannot,
   fix that first.
2. Register the model with a lineage to its data and code versions.
3. Deploy behind a feature flag, in shadow mode, and compare its outputs with
   the incumbent on real traffic for a day.
4. Canary to 5% with an automatic rollback on a latency or error threshold.
5. Wire monitoring for operations, data quality, drift and business metric.
6. Write the runbook for the two most likely alerts.
7. Roll it back. Confirm that the model, preprocessing and config all revert
   together.
:::

:::pitfall The five operational failures
1. **Silent degradation.** No quality monitor; users notice before you do.
2. **Skew after rollback.** Model reverted, preprocessing not.
3. **Unreproducible training.** A regression appears and cannot be bisected.
4. **Alerting on drift.** Features move constantly; you train the team to
   ignore alerts.
5. **No cost attribution.** Spend triples and nobody can say which feature
   did it.
:::

:::note Time to competence
**6--8 weeks** for ESSENTIAL and CORE if you have one system to practise on.
The reproducibility test in step 1 above is the fastest way to find out where
you actually stand.
:::

:::recap
- ML systems fail quietly and plausibly, which is why quality sampling, drift
  monitoring and shadow deployment are not overhead.
- Track every run with code, data, config and environment; the test is
  whether you can regenerate a three-month-old result.
- Version and roll back the model, preprocessing and config together.
- Shadow first, canary second, automatic rollback always; feature-flag every
  LLM feature.
- Monitor operations, data, drift, quality and business; alert on quality and
  business, dashboard the rest.
- LLM-specific: prompt versioning with an eval gate, tracing with cost per
  span, pinned model versions, spend limits.
:::
