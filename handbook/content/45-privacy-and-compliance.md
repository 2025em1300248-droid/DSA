# Privacy, Fairness and Compliance
@short: Privacy and Compliance
@subtitle: The constraints that are not negotiable, and how to engineer within them
@tier: core
@prereq: none
@blurb: Most engineers meet this material as a list of things they are not allowed to do, arriving late and from a legal team. Understood earlier it is a design input like any other, and the systems that handle it well are not noticeably more expensive --- they were just architected with it in mind. This chapter covers what the rules require and how to build to them.
@objectives:
- Identify personal data and apply the minimisation principle
- Implement deletion, access and portability in an ML system
- Measure fairness with the right metric and know they conflict
- Understand the regulatory surface for AI systems
- Produce the documentation an audit will ask for

## Personal data

```python title="Classify every field before you design the pipeline"
CLASSIFICATION = {
    "user_id":        "pseudonymous",   # personal data if you hold the mapping
    "email":          "direct",
    "ip_address":     "direct",         # personal data in most jurisdictions
    "device_id":      "pseudonymous",
    "postcode":       "quasi-identifier",
    "date_of_birth":  "quasi-identifier",
    "health_status":  "special category",   # higher protection, explicit consent
    "transaction_amount": "non-personal",
}
```

:::warning Quasi-identifiers re-identify people
Postcode, date of birth and sex together identify a large majority of people
in most populations. "We removed the names" is not anonymisation; it is
pseudonymisation, and pseudonymous data is still personal data with all the
same obligations.

Genuine anonymisation means re-identification is not reasonably possible, and
it is harder than it sounds: aggregates leak, and a model trained on personal
data can memorise and emit it.
:::

| Principle | Engineering consequence |
|---|---|
| Minimisation | collect only fields with a stated purpose; justify each one |
| Purpose limitation | data collected for billing cannot silently train a model |
| Storage limitation | retention periods, enforced by a job, not by intention |
| Accuracy | correction must propagate to derived data |
| Integrity | encryption at rest and in transit, access logging |
| Accountability | you must be able to *demonstrate* compliance |

@tbl: The principles, as engineering requirements. The last is the one that changes architecture: being compliant is insufficient if you cannot produce evidence.

## Deletion, in a system with models

A deletion request must reach every copy, and ML systems have many.

```python title="A deletion that actually completes"
def handle_deletion(user_id: str):
    tasks = [
        ("primary_db",      lambda: db.delete_user(user_id)),
        ("event_log",       lambda: events.delete_by_user(user_id)),
        ("feature_store",   lambda: fs.delete_entity(user_id)),
        ("vector_index",    lambda: index.delete_by_metadata(user_id=user_id)),
        ("training_sets",   lambda: mark_excluded(user_id)),   # for next retrain
        ("backups",         lambda: schedule_backup_purge(user_id)),
        ("caches",          lambda: cache.invalidate_user(user_id)),
        ("llm_provider",    lambda: provider.delete_conversations(user_id)),
        ("analytics",       lambda: analytics.delete_subject(user_id)),
    ]
    record = {"user_id": user_id, "requested_at": now(), "steps": {}}
    for name, fn in tasks:
        try:
            fn(); record["steps"][name] = "done"
        except Exception as e:
            record["steps"][name] = f"failed: {e}"
            alert(f"deletion incomplete for {user_id} at {name}")
    audit_log.write(record)                 # the evidence you will need
    return record
```

:::pitfall The model itself may contain the data
A model trained on personal data can memorise it, and deleting the training
row does not remove it from the weights. The practical positions are:

- **Exclude and retrain on schedule.** Mark the subject excluded; the next
  scheduled retrain removes their influence. Document the lag and tell the
  user.
- **Reduce memorisation up front.** Deduplicate (Chapter 16) --- memorisation
  rises sharply with repetition --- and consider differential privacy for
  high-risk data.
- **Do not train on data you may have to remove.** The cheapest answer by a
  wide margin, and available more often than teams assume: retrieval over a
  deletable index rather than training on the content.

"Machine unlearning" methods exist but are not yet reliable enough to present
to a regulator as a guarantee.
:::

## Fairness

```python title="Four definitions, which do not agree"
def fairness_report(y_true, y_pred, y_score, group):
    out = {}
    for g in np.unique(group):
        m = group == g
        out[g] = dict(
            n=int(m.sum()),
            selection_rate=float(y_pred[m].mean()),                 # demographic parity
            tpr=float(y_pred[m][y_true[m] == 1].mean()),            # equal opportunity
            fpr=float(y_pred[m][y_true[m] == 0].mean()),            # equalised odds
            ppv=float(y_true[m][y_pred[m] == 1].mean()),            # predictive parity
            calibration_error=ece(y_true[m], y_score[m]),
        )
    return out
```

| Definition | Requires equal | Fails when |
|---|---|---|
| Demographic parity | selection rate | base rates genuinely differ |
| Equal opportunity | true positive rate | you also need equal false positives |
| Equalised odds | TPR **and** FPR | base rates differ |
| Predictive parity | precision | you also need equalised odds |
| Calibration within groups | reliability | combined with equalised odds |

@tbl: Five definitions. The impossibility result is the important part: when base rates differ between groups, calibration, equalised odds and predictive parity *cannot all hold simultaneously*. This is arithmetic, not a limitation of technique.

:::insight The choice is normative, and it is not yours alone
Because the definitions conflict, you must choose --- and the choice encodes a
value judgement about which errors matter.

- A false negative is worse than a false positive (medical screening) →
  equal opportunity.
- Both error types are costly and symmetric (criminal justice risk) →
  equalised odds.
- The score is used as a probability downstream (lending) → calibration.

Make the choice explicitly, with the people accountable for the decision,
and write down the reasoning. An engineer silently picking demographic parity
because a library defaulted to it has made a policy decision without
authority.
:::

```python title="Mitigations, at three points in the pipeline"
# Pre-processing: reweight or resample so the training data is balanced.
#   Transparent, model-agnostic. Can reduce overall accuracy.
# In-processing: add a fairness constraint to the objective.
#   Most effective. Requires model surgery.
# Post-processing: group-specific thresholds.
#   Simplest and often the most effective — but using a protected attribute
#   at decision time may itself be unlawful. Check before implementing.
```

## The regulatory surface

| Regime | Applies to | Core requirement |
|---|---|---|
| GDPR / UK GDPR | EU/UK personal data | lawful basis, rights, DPIA, Art. 22 on automated decisions |
| EU AI Act | AI systems in the EU | risk tiers; conformity assessment and documentation for high-risk |
| Sector rules (finance, health) | the sector | model risk management, validation, adverse-action notices |
| US state privacy laws | state residents | access, deletion, opt-out of sale |
| Copyright and licensing | training data, model weights | provenance; teacher-output restrictions |

@tbl: A map, not legal advice. The practical point for an engineer is that all of these demand the *same artefacts*: a record of what data was used, what the system does, how it was evaluated, and who approved it.

:::checklist The documentation that satisfies most of them at once
- **Purpose and scope.** What the system decides, for whom, and what it is
  explicitly not for.
- **Data provenance.** Sources, licences, consent basis, retention.
- **Evaluation.** Metrics overall and by subgroup, with intervals
  (Chapter 38), and the limitations you know about.
- **Fairness assessment.** The definition chosen, why, and the measured
  result.
- **Human oversight.** Who can override, how, and how often they do.
- **Monitoring.** What is watched, what triggers an alert, who responds.
- **Change log.** Every version, what changed, who approved it.

Produce these as you build. Reconstructing them six months later for an audit
costs several times as much and is usually incomplete.
:::

:::warning Automated decisions with legal effect
Where a decision has a legal or similarly significant effect on someone ---
credit, employment, insurance, housing --- there is usually a right to a
meaningful explanation and to human review. Engineering consequences:

- You must be able to **explain the decision** in terms the subject can act
  on; a counterfactual (Chapter 21) is the form that works.
- You must be able to **reconstruct it exactly**, which is why Chapter 42's
  registry logs the model version with every prediction.
- There must be a **real human review path**, not a nominal one.
:::

:::practice The task
For a system you run: (a) classify every field and remove the ones with no
stated purpose; (b) implement end-to-end deletion including the vector index
and the provider, with an audit record; (c) measure all five fairness
definitions by group and show that two of them conflict; (d) choose one with
the accountable decision-maker and document the reasoning; (e) write the
seven-section documentation pack; (f) trace one past decision end to end and
produce the explanation you would give its subject.

**You have this skill when** you can hand an auditor the documentation pack
and reconstruct any individual decision from the last year.
:::

:::exercise
1. Show that postcode, date of birth and sex jointly identify most individuals
   in a dataset you have.
2. Implement deletion and verify no trace remains in the vector index or
   caches. What took longest?
3. † Demonstrate that a model memorises a rare training string, and that
   deduplication reduces it.
4. Construct data where demographic parity and calibration cannot both hold.
   Show the arithmetic.
5. Apply all three mitigation points to one model and compare fairness and
   accuracy for each.
6. † Write a counterfactual explanation for a declined decision that a
   non-technical subject could act on. Test it on someone outside the field.
7. Assemble the documentation pack for an existing system. Which section was
   hardest, and why?
:::

:::recap
- Pseudonymous data is still personal data; quasi-identifiers re-identify
  people.
- Deletion must reach the database, logs, feature store, vector index,
  training sets, backups, caches and your providers --- with an audit record.
- A model can memorise training data; prefer retrieval over a deletable index
  to training on removable content.
- Fairness definitions conflict by arithmetic when base rates differ; choosing
  one is a normative decision that needs the accountable person.
- Mitigate pre-, in- or post-processing; group-specific thresholds are
  effective but may be unlawful.
- Every regime wants the same artefacts: purpose, provenance, evaluation,
  fairness, oversight, monitoring, change log --- produce them as you build.
- Decisions with legal effect need an actionable explanation, exact
  reconstruction, and a real human review path.
:::
