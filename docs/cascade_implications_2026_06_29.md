# Cascade Implications — A Domain-by-Domain Meditation

**Date:** 2026-06-29
**Status:** Design pass — no edges authored yet
**Purpose:** Before adding ~40 operational event types and their TRIGGERS_OBLIGATION edges, walk slowly through each domain and surface the *non-obvious* cascade implications. Not all cascades are "event → list of controls". Some are:

- **Second-order events** (event A causes event B, which fires its own cascade)
- **Profile-fact updates** (the tenant's `ClientFact` set changes, changing applicability)
- **Latent enablement** (an obligation that *was* dormant becomes active)
- **De-application** (an obligation that *was* active becomes N/A)
- **Time-bounded windows** (deadlines, grace periods, retention clocks)
- **Cross-domain handoffs** (HR event becomes IAM event becomes Asset event)
- **Aggregation thresholds** (10 individual events trigger a different obligation than 1)

If we model only the direct fan-out, we'll miss most of these.

## Companion reading

- [Relationship model design](relationship_model_design_2026_06_29.md) §5 — the original 8-event proposal
- [Relationship model audit](relationship_model_audit_2026_06_29.md) §A — existing 11 compliance-lifecycle events in Neo4j
- [[product-concept-evidence-cascade-2026-06-27]] — original cascade memo
- [[product-principle-evidence-stored-vs-cited]] — the cite-mode substrate that emits events

---

## Domain 1: Personnel

The HR system is the canonical source-of-truth. Events emit from cite verifications attesting "changes since last verify".

### Events

| Event | Capture |
|---|---|
| `personnel_added` | new HR row |
| `personnel_offboarded` | HR row marked exit |
| `role_changed` | HR row role/title update |
| `contractor_engaged` | contractor onboarding (distinct from employee row) |
| `contractor_offboarded` | contractor termination |
| `manager_changed` | reporting-line change |
| `personnel_transferred_jurisdiction` | location change crossing data-residency boundary |
| `disciplinary_action_taken` | formal A.6.4 process initiated |

### Direct obligation fan-out (TRIGGERS_OBLIGATION)

`personnel_added`:
- A.6.1 screening_record needs a row (record of who was checked, what was checked, outcome)
- A.6.2 terms_of_employment signed (signed within 1 working day)
- A.6.3 awareness training assigned (commonly within 30 days)
- A.5.10 AUP acknowledgement signed (commonly within 1 week)
- A.5.16 identity created (within 1 day, often same-day)
- A.5.17 authentication info issued (same-day)
- A.5.18 access rights granted (per-role, within hire date)
- A.6.6 NDA signed (employee variant; often packaged with A.6.2)

`personnel_offboarded`:
- A.5.11 return of assets (BEFORE last working day)
- A.5.16 identity revoked (within 24h — the SLA-met-flag MUST)
- A.5.17 credentials revoked (paired with A.5.16 — the lifecycle pair)
- A.5.18 access rights revoked (within 24h)
- A.6.5 post-employment briefing (on or before last day)

`role_changed`:
- A.5.18 access rights review (within 1 week)
- A.6.3 role-specific training (if role triggers new training requirements)
- A.6.5 confidentiality scope check (if role accesses materially different data)

### Non-obvious cascades

**A. Profile-fact updates from personnel events.**

A growing-headcount tenant can cross 250-employee threshold → triggers `fact:employee_count_250_plus` → triggers `gdpr_universal` obligation expansion (RoPA derogation lost). The cascade isn't on a single obligation but on the *applicability set*.

This means cascade emission shouldn't ONLY trigger obligations — it should re-evaluate ClientFacts and propagate downstream.

**B. Second-order: personnel_offboarded → asset_returned cascade.**

A.5.11 return of assets is the *event* fired by `personnel_offboarded`. But each returned asset is itself an asset-domain event (`asset_ownership_changed` → unassigned pool). If we don't model this handoff, asset-domain MUSTs aren't re-evaluated.

**C. Disciplinary action → access escalation.**

`disciplinary_action_taken` doesn't add a control row; it triggers *suspension* of A.5.18 access (a transient state, not a revocation). And if the disciplinary case is upheld, it may escalate to `personnel_offboarded` (firing). Cascade is conditional on outcome.

**D. Jurisdiction transfers.**

`personnel_transferred_jurisdiction` may flip GDPR applicability (employee moves from EU to non-EU). May change the tenant's Art.27 representative obligation if proportion of EU-located staff drops. Profile-fact-level cascade, not control-level.

**E. Aggregation: phishing-test fail rate.**

Individual `phishing_test_failed` events are below threshold; 20+ in a quarter triggers `disciplinary_action_taken` policy (A.6.4) AND A.6.3 training-program-review (the program is failing). Aggregation isn't TRIGGERS_OBLIGATION; it's a *threshold* edge — new shape.

**F. Latent enablement: contractor_engaged.**

Contractors don't trigger A.6.2 terms-of-employment (that's employee-only) but DO trigger A.5.20 supplier-agreement clauses (the contractor-as-supplier framing) AND A.6.6 NDA (separate template). Same source-of-truth (HR system) but distinct obligation set. The `contractor` vs `employee` discriminator changes the entire downstream cascade.

**G. Manager change ⇒ Approval chain rebuild.**

`manager_changed` triggers A.5.4 segregation review: does the new manager have an approval-authority conflict with their reportee's role? May require A.5.3 segregation-of-duties remediation. The cascade is conditional on the (role, role) pair.

### Source-of-truth + capture

HR system cite covers these via `personnel_register` evidence type. The tenant attests during verification with structured event counts. **Open question:** can a single verification report multiple distinct events of the same type? (5 added + 2 offboarded + 1 role change in one verify, yes — schema must handle it).

### Candidate new edge types from this domain

- `TRIGGERS_RESPONSE` (event → control, NOT obligation level — softer; "must consider" vs "must do") — example: phishing_fail → A.6.4 disciplinary consideration
- `UPDATES_FACT` (event → ClientFact) — example: cross-jurisdictional move → `transfers_data_outside_eu`
- `THRESHOLDED_BY` (event → aggregation rule) — example: phishing fail count ≥ N → A.6.4 action

### Time-window awareness

Several obligations carry deadlines:
- A.6.2: 1 working day
- A.5.10 AUP: 1 week
- A.6.3 training: 30 days (often)
- A.5.16/17/18 onboarding: same-day
- A.5.16/17/18 offboarding: 24h (the SLA-met flag)
- A.5.11 return of assets: BEFORE last working day

These should be `deadline` properties on TRIGGERS_OBLIGATION edges (already supported in the existing schema). Implication: the implications-tracking layer (S3 `triggered_implication`) needs per-target deadlines, not one-deadline-per-event.

---

## Domain 2: IAM / Identity

Source-of-truth: IAM system (Okta / Azure AD / ServiceNow CMDB identity store / native LDAP).

### Events

| Event | Capture |
|---|---|
| `identity_added` | new system-side identity (may be personnel-linked, service account, machine identity) |
| `identity_disabled` | identity flipped inactive (distinct from removed) |
| `identity_removed` | identity fully purged |
| `privilege_granted` | new role/permission added |
| `privilege_revoked` | role/permission removed |
| `mfa_method_changed` | enrolment/de-enrolment of MFA factors |

### Direct fan-out

`identity_added`:
- A.5.16 identity record (the IAM register row IS the evidence)
- A.5.17 authentication-info initialised (password set, MFA enrolled)
- If service account: A.8.2 privileged-access record + A.5.3 segregation review

`identity_disabled`:
- A.5.16 register updated (status flip)
- A.5.17 credentials suspended (paired)
- A.5.18 access rights frozen

`privilege_granted`:
- A.5.18 access-rights register row
- If privileged: A.8.2 privileged-access record + approval-chain artefact
- A.5.3 segregation re-check (does the new privilege conflict?)

`mfa_method_changed`:
- A.5.17 register update
- Potential A.5.25 incident triage if the change is unauthorised (compromise indicator)

### Non-obvious cascades

**A. Service accounts vs human identities — applicability fork.**

A.5.16 ITSELF has service_accounts → MUST since the batch-12 promotion. A `identity_added` for a service account triggers a different sub-set of obligations than for a human (no A.6.x training; yes A.5.3 segregation check for what the bot can do).

We may need an `identity_kind` property on the event (`human` / `service` / `machine`), or distinct events (`service_account_added`).

**B. Bulk MFA reset = compromise indicator.**

One `mfa_method_changed` is normal. 50 in a day is `event:information_security_incident`. The cascade depends on aggregation, just like the phishing example. Same `THRESHOLDED_BY` shape.

**C. Privilege drift detection.**

Comparing access-rights register (A.5.18) snapshots over time reveals privilege creep. This isn't a single event — it's a *derived* observation across snapshots. Needs an `ANOMALY_DETECTED` event class or a periodic synthetic event.

**D. Identity ↔ personnel binding gaps.**

If `identity_added` happens for a person not in HR (`personnel_added` not seen first), that's a control failure of A.5.16 record_personnel_binding. Cascade is "the absence of an event triggers an obligation review" — *missing-event* logic.

**E. Privilege revocation timing window.**

When `personnel_offboarded` fires but no `privilege_revoked` arrives within 24h, the SLA is breached. This is again a missing-event check — the cascade engine must know to LOOK for the expected counterpart event.

### Cross-domain handoff: personnel ↔ IAM

The cleanest cascade is `personnel_added` → emits `identity_added` (when IAM rules say "all new employees get an identity"). The system should TRACK that this handoff is expected. If a personnel event arrives but no IAM counterpart within N days, the implications-tracking layer flags it.

This is fundamentally different from "event → control" — it's "event → expected-future-event". A new edge type: `EXPECTS_FOLLOWUP_EVENT`? Or modeled as a special `triggered_implication` whose target is another event?

### Candidate new edge types

- `EXPECTS_FOLLOWUP_EVENT` (event A in domain X → expected event B in domain Y within window N)
- `ANOMALY_DETECTED_BY` (event class → detector control)

---

## Domain 3: Asset / Physical

Source-of-truth: asset register (ServiceNow / GLPI / native) + facilities mgmt.

### Events

| Event | Capture |
|---|---|
| `asset_acquired` | procurement event (purchase order closed) |
| `asset_added` | inventory entry (may precede acquisition or follow) |
| `asset_reclassified` | classification level changed |
| `asset_relocated` | physical move (cross-facility, same-facility) |
| `asset_ownership_changed` | accountable owner reassigned |
| `asset_retired` | end-of-life decision |
| `asset_disposed` | physical disposal completed (lifecycle-end vs `asset_retired` which is decision-point) |
| `asset_lost_stolen` | unintended loss of control |
| `facility_added` | new physical site |
| `facility_closed` | site decommissioned |

### Direct fan-out

`asset_acquired`:
- A.5.9 asset_register row (procurement → inventory entry)
- A.5.20 supplier_agreement updated (if procurement was via new supplier)
- A.5.21 ICT supply-chain risk check (for ICT assets)

`asset_added`:
- A.5.9 register completion
- A.5.12 classification assigned (mandatory before use)
- A.5.13 labelling applied
- A.7.10 media handling if media

`asset_reclassified`:
- A.5.13 labels updated
- A.5.18 access rights re-reviewed against new classification
- A.8.12 DLP rules updated (label match changes outcome)
- A.8.24 cryptographic requirements re-evaluated

`asset_relocated`:
- A.7.8 siting controls re-applied at new site
- A.7.4 monitoring coverage adjusted
- A.7.5 environmental-threat assessment for new site
- If cross-jurisdiction: GDPR Art.30 transfer record updated

`asset_retired` (decision):
- A.7.14 disposal plan
- A.8.10 information deletion plan
- A.5.9 register updated to "pending disposal" state

`asset_disposed` (lifecycle-end):
- A.7.14 disposal record (the audit artifact)
- A.8.10 information-deletion attestation
- A.5.9 register updated to "disposed"
- A.5.28 evidence-handling chain preserved

`asset_lost_stolen`:
- IMMEDIATELY fires existing `event:information_security_incident` (cross-domain emission)
- A.5.26 incident register row
- If contains personal data: existing `event:personal_data_breach` (cascading Art.33 72h clock)

`facility_added`:
- Entire A.7.x cluster re-evaluated (each control's applicability rechecked for the new site)
- A.5.9 asset register scope extends
- A.5.23 cloud-vs-physical balance check

`facility_closed`:
- A.7.14 disposal scope spikes (all physical assets at that facility)
- Personnel relocation cascade (multiple `personnel_transferred_jurisdiction`)
- A.5.9 register entries for facility-bound assets all transition

### Non-obvious cascades

**A. Reclassification ripples through DLP + crypto + access.**

A single asset reclassified UP (Internal → Confidential) cascades:
- A.5.18 access list narrows (review)
- A.8.12 DLP rule additions
- A.8.24 crypto requirements (must encrypt at rest)
- A.5.13 label update (visible signage)
- A.6.3 training implications for handlers

Reclassification DOWN has different cascade — usually less restrictive, but A.5.13 labels must change to prevent over-handling.

**B. Facility-add explodes obligations.**

`facility_added` doesn't trigger ONE obligation — it makes 14 A.7.x controls become applicable per the new site (each previously evaluated for site N now must be evaluated for site N+1). This is *scope expansion*, not control addition. The cascade engine needs to handle "trigger re-evaluation against new scope element" as a distinct shape.

**C. Lost/stolen → cross-domain incident emission.**

`asset_lost_stolen` is itself an event but it ALSO emits `event:information_security_incident` (and possibly `event:personal_data_breach`) — the cascade chain becomes asset-domain → incident-domain → GDPR-cascade with 72h clock.

The system must support **event emission as a cascade outcome**. Today's TRIGGERS_OBLIGATION goes event→control. We need an `event → event` edge.

**D. Disposal chain coherence.**

`asset_retired` (decision) → must be followed by `asset_disposed` (execution) within a window. If not, the asset is in "pending disposal" purgatory — register inaccurate. Same missing-event pattern as IAM revocation.

**E. Asset ownership changes that cross departments trigger A.5.3 segregation re-check.**

Same shape as the personnel case but for asset stewardship.

### Candidate new edge types from this domain

- `EMITS_EVENT` (event → event — cross-domain handoff)
- `EXPANDS_SCOPE` (event → scope element — facility/jurisdiction-level expansion)

---

## Domain 4: Supplier / Processor

Source-of-truth: vendor management / procurement / processor register.

### Events

| Event | Capture |
|---|---|
| `supplier_engaged` | new vendor contract signed |
| `supplier_terminated` | contract ended |
| `supplier_audit_completed` | A.5.22 review event |
| `supplier_breach_reported` | supplier-side incident disclosure |
| `supplier_changed_subprocessor` | tier-2 vendor change in flow-down chain |

### Direct fan-out

`supplier_engaged`:
- A.5.19 policy applied
- A.5.20 agreement signed (with security clauses)
- A.5.21 ICT supply-chain entry (if ICT supplier)
- A.5.22 initial review scheduled
- A.5.23 cloud-specific clauses (if cloud)
- If processor: existing `event:new_processor_engaged` → Art.28 DPA + Art.30 RoPA + Art.32 measure flow-down

`supplier_terminated`:
- A.5.20 closure obligations (data return / deletion proof — A.8.10 attestation)
- A.5.21 register update
- A.5.22 final review

`supplier_audit_completed`:
- A.5.22 review record (the artifact)
- Findings may emit `corrective_action_opened` (cross-domain)
- A.5.20 agreement may need renegotiation

`supplier_breach_reported`:
- A.5.22 emergency review
- A.5.20 contract enforcement clauses
- If processor: existing `event:personal_data_breach` (if controller's data affected) — Art.33 72h clock starts FROM PROCESSOR NOTIFICATION
- A.5.26 incident register row
- A.5.27 lessons learned scoped

`supplier_changed_subprocessor`:
- Art.28 sub-processor notification check (DPA clause)
- A.5.22 review of sub-processor security
- Cross-border check (sub-processor in third country)

### Non-obvious cascades

**A. Processor breach starts MY 72h clock.**

When my processor reports a breach, GDPR Art.33's 72h clock starts when MY controller becomes aware — not when the processor first detected. This is a deadline-clock-attribution subtlety. The cascade implications layer must track WHO holds the clock.

**B. Supplier termination = data-return event.**

`supplier_terminated` must be followed by a `data_returned` or `data_deleted` attestation (A.8.10 destruction certificate). If missing within N days, supplier termination is incomplete. Missing-event pattern.

**C. Cascade through processor flow-down.**

If I'm a processor and my controller fires `supplier_engaged` (engaging ME), my own processors need flow-down — chain of Art.28 obligations. Multi-tenant relationship implications.

**D. Sub-processor cascade.**

`supplier_changed_subprocessor` is a tier-2 event but can trigger tier-1 controller obligations under Art.28.2 — notification of intended changes. The cascade crosses tenancy boundaries (controller is NOT the same tenant as processor).

In v1, scope to single-tenant: cascade only within the tenant. Cross-tenant cascade is deferred.

### Candidate new edge types

- `DEFERS_CLOCK_TO` (event → external party — for the controller/processor clock-attribution)
- `EXPECTS_ATTESTATION` (event → attestation type within window)

---

## Domain 5: Management-system lifecycle (the originally-missed domain)

Source-of-truth: the ISMS itself — policy authoring, risk register, SoA, audit calendar, corrective-action tracker.

### Events

| Event | Capture |
|---|---|
| `policy_published` | new top-level / topic-specific policy |
| `policy_revised` | existing policy versioned-up |
| `procedure_published` / `procedure_updated` | A.5.37 operating procedures |
| `aup_revised` | A.5.10 specifically (high-cascade variant of policy_revised) |
| `classification_scheme_revised` | A.5.12 (high-cascade variant) |
| `risk_assessment_completed` | 6.1.2 cycle |
| `risk_treatment_decision` | 6.1.3 |
| `soa_updated` | 6.1.3.d Statement of Applicability change |
| `internal_audit_scheduled` | 9.2 calendar event |
| `internal_audit_completed` | 9.2 closure |
| `internal_audit_finding_raised` | existing `event:audit_nonconformity` |
| `compliance_review_completed` | A.5.36 |
| `management_review_completed` | 9.3 |
| `corrective_action_opened` | 10.1 |
| `corrective_action_closed` | 10.1 |
| `objective_set` | 6.2 |
| `kpi_threshold_exceeded` | 9.1 measurement |
| `vulnerability_disclosed_critical` | A.8.8 CVE-class signal |
| `patch_applied_emergency` | A.8.32 expedited change |
| `production_deployment` | A.8.32 normal change |
| `retention_period_reached` | A.5.33 lifecycle |
| `consent_withdrawn` | GDPR Art.7.3 |

### Direct fan-out — selected high-leverage

`policy_revised`:
- A.6.3 awareness program updated (if material change)
- A.5.10 AUP re-acknowledgement (if AUP-touching)
- A.5.36 compliance review scoped to verify new policy is followed
- A.5.37 operating procedures may need cascade update
- 7.4 communication (notify affected personnel)
- 7.5 document control (version, supersedes, archive)

`aup_revised` (specialised — high cascade):
- All personnel re-acknowledge within N days (mass `personnel-side` event)
- A.6.3 training content refresh
- A.5.10 register update tracking re-acknowledgements
- Failure-to-acknowledge after window = `disciplinary_action_taken` candidate

`classification_scheme_revised` (specialised — high cascade):
- All A.5.12 labels reviewed
- A.5.13 labelling updates
- A.5.18 access rights recomputed against new scheme
- A.8.12 DLP rule updates
- A.8.24 crypto requirements re-evaluated
- A.6.3 retraining on new scheme

`risk_assessment_completed`:
- 6.1.3 risk treatment plan re-evaluated
- SoA review (control applicability may change)
- 9.3 management review input
- Risk-register entries updated

`soa_updated`:
- Controls newly in-scope require evidence chain instantiated
- Controls newly out-of-scope flip to N/A (existing schema_v43 tenant_must_overrides)
- 9.2 audit scope adjusted
- A.5.36 compliance review scope adjusted
- All downstream evidence requirements recalculated against new applicability

`management_review_completed`:
- Decisions become candidates for `corrective_action_opened`
- 6.2 objectives may be re-set
- Resource decisions (7.1) flow to budgeting

`corrective_action_opened`:
- Tracking obligation (no due date in standard, but tenant-policy enforces one)
- Implicit link back to the finding source
- 9.3 management review awareness

`vulnerability_disclosed_critical`:
- A.5.7 threat-intel signal recorded
- A.8.8 vuln-mgmt patch decision required (often 24-72h)
- A.5.25 triage if exploited in-the-wild
- A.8.32 emergency change consideration
- Existing `event:significant_system_change` may be emitted (if patch is significant)

`retention_period_reached`:
- A.5.33 retention review → A.8.10 deletion or extension decision
- A.5.34 PII subset → GDPR Art.5.1.e check (must delete unless extension justified)
- A.8.11 anonymisation as alternative
- Tracking artifact in retention register

`consent_withdrawn`:
- GDPR Art.7.3 acknowledgement (immediate)
- Existing `event:erasure_request` may be emitted (if withdrawal implies erasure under Art.17.1.b)
- A.5.18 access-rights review (was consent the lawful basis for that access?)
- Re-evaluation of processing activities relying on this consent

### Non-obvious cascades

**A. Policy hierarchies → cascade depth.**

`policy_revised` for the parent ISP cascades to *all* topic-specific policies (A.5.10 / 5.12 / 5.14 / 5.15 / 5.19) which then cascade to procedures (A.5.37). 3-deep cascade is normal here. Each layer has its own freshness clock + approval workflow.

**B. SoA change is a meta-event.**

`soa_updated` doesn't trigger a single control — it triggers a RE-EVALUATION of the entire control set against new applicability. It's not "do X"; it's "re-decide what applies and propagate". A different shape of cascade.

**C. Risk register threshold crossings.**

A risk in the register moves from "Medium" to "High" — that's not currently an event but should be. It triggers re-treatment (6.1.3) and may force a management review topic. Implies a `risk_score_changed` event.

**D. Objective achievement / miss creates implication.**

`objective_missed` (alternative to `kpi_threshold_exceeded`) triggers root-cause analysis (10.1) + remedial actions. This is a longer-cycle cascade (quarterly review tempo) but very real.

**E. Production deployment cascades change-management evidence.**

`production_deployment` requires:
- A.8.32 change record (with approval chain)
- A.8.29 security testing evidence pre-deployment
- A.8.31 dev/test/prod separation evidence
- A.5.26 incident-monitoring heightened post-deploy
- Rollback plan (procedure reference)

Five concurrent obligation surfaces from one event.

**F. Corrective-action closure is not just CLOSE.**

`corrective_action_closed` must include effectiveness verification (10.1 explicitly requires). Closure-without-effectiveness-evidence is itself a finding. The cascade must enforce closure-quality criteria.

**G. Retention-reached + legal-hold conflict.**

If A.5.33 retention period reached but A.5.31 legal register shows a hold (litigation / regulatory action), deletion is BLOCKED. This is a *negative cascade* — an event that would normally fire is suppressed by a higher-priority obligation. The implications layer must know to check for blockers.

### Candidate new edge types from this domain

- `CASCADES_REVIEW` (event → control set — "re-evaluate these against new state")
- `BLOCKS_WHEN` (obligation → ClientFact / hold-state — applicability suppression)
- `SUPERSEDES_CYCLE` (event → existing-due-cycle — restarts a freshness clock)
- `REQUIRES_EFFECTIVENESS_PROOF` (closure event → verification artifact)

---

## Cross-cutting patterns surfaced by the meditation

Walking all five domains, the following patterns recur and should shape the implementation:

### P1. Events emit events (cross-domain handoff)

`personnel_offboarded` → `privilege_revoked` (× N)
`asset_lost_stolen` → `event:information_security_incident` → `event:personal_data_breach`
`supplier_breach_reported` → `event:personal_data_breach`
`facility_closed` → multiple `personnel_transferred_jurisdiction`

Schema implication: **events can fire downstream events**, not just obligations. Need an `EMITS_EVENT` edge type (event → event).

### P2. Missing-event detection

`personnel_offboarded` expects `privilege_revoked` within 24h.
`asset_retired` expects `asset_disposed` within 30d.
`policy_revised` expects mass `aup_re-acknowledged` within 7d.

Schema implication: the cascade engine must do **negative checking** — flag implications when expected followup events DON'T arrive. This is a periodic sweep, not a per-event firing.

### P3. Profile-fact recomputation

`personnel_added` may flip `fact:employee_count_250_plus` true.
`personnel_transferred_jurisdiction` may flip `fact:transfers_data_outside_eu`.
`supplier_engaged` may flip `fact:uses_processors`.

Schema implication: events should be able to UPDATE ClientFacts, not just trigger obligations. ClientFact updates then trigger the existing applicability cascade. New edge type: `UPDATES_FACT`.

### P4. Scope expansion

`facility_added` doesn't add ONE control — it expands the *scope set* against which all A.7.x controls are evaluated. Same shape: new processing activity, new jurisdiction, new sub-processor, new asset class.

Schema implication: some events trigger **re-evaluation of existing controls against new scope**, not new control instances. New edge: `EXPANDS_SCOPE`.

### P5. Thresholded aggregation

20 phishing fails → `disciplinary_action_taken` policy review (NOT 20 separate cascades).
50 MFA resets/day → compromise indicator.
Mass classification reclassifications → scheme-review trigger.

Schema implication: some cascades fire on **aggregate** patterns, not single events. New edge: `THRESHOLDED_BY` or counter-event class.

### P6. Negative cascade (blockers)

A.5.33 retention expiry → A.8.10 deletion ONLY IF no A.5.31 legal hold.
`policy_revised` → A.6.3 retraining ONLY IF material change.
`supplier_engaged` → Art.28 DPA ONLY IF supplier processes personal data.

Schema implication: existing `applies_when` mechanism handles applicability gating. New addition: **blocker checks** that suppress would-fire cascades based on other obligations' state. Could be modeled as a special `applies_when` on the trigger edge.

### P7. Clock attribution

Art.33 72h clock starts when CONTROLLER becomes aware — but processor may have known earlier.
Internal audit finding response window starts at FINDING date, not at CAR closure target.

Schema implication: deadline computation may depend on *which actor* triggered the chain, not just when the event was recorded. The `triggered_implication` row needs to capture both event time AND awareness time.

### P8. Effectiveness verification (closure quality)

`corrective_action_closed` must include effectiveness proof.
`asset_disposed` must include the disposal certificate.
`supplier_terminated` must include the data-return attestation.

Schema implication: closure events have *required attestation payloads* — closure WITHOUT the proof is itself a control failure. May extend the existing `changes_detected` field with structured proof types.

### P9. Cascade depth budget

Some cascades are 3-deep (policy → procedure → training). Others are 1-deep (`role_changed` → A.5.18 review).

Schema implication: the cascade engine needs a **depth limit** + cycle detection to avoid infinite chains (policy → procedure → policy update via correction → ...). Practical cap: depth 4.

### P10. Implication grouping for the human surface

5 `personnel_added` events in one verify shouldn't surface 5 × 5 = 25 separate implication cards. The UI should group "5 new employees → 5 training rows + 5 NDAs + 5 identity rows + 5 access grants" as a single high-level item with breakdown.

UX implication: implications-tracking surface needs grouping by source-event-batch, not per-implication.

---

## Implementation impact for S2

The original §5 of the design memo proposed adding 8 Event nodes + their TRIGGERS_OBLIGATION edges + a `structured_events JSONB[]` column on `external_evidence_verification_log` + a verify-dialog UI extension.

After this meditation, S2 should be re-scoped:

### What S2 ships (vocabulary + scaffolding)

- **All ~40 Event nodes** authored (vocabulary stabilised)
- **Schema additions**:
  - `structured_events JSONB[]` on `external_evidence_verification_log` (original plan)
  - **NEW**: `event_emits_event_log` table (P1)
  - **NEW**: `expected_followup_event` table tracking outstanding `EXPECTS_FOLLOWUP_EVENT` chains (P2)
  - **NEW**: `client_fact_update_log` (P3)
- **New edge types added to MANAGED_EDGE_TYPES**:
  - `EMITS_EVENT` (P1)
  - `EXPECTS_FOLLOWUP_EVENT` (P2)
  - `UPDATES_FACT` (P3)
  - `EXPANDS_SCOPE` (P4)
  - `CASCADES_REVIEW` (P5 management-system domain pattern)
  - `BLOCKS_WHEN` (P6)
- **Loader extensions** for the new edge types
- **Verify-dialog UI extension** to capture structured events (original plan)

### What S2 does NOT ship (deferred to S3 / S2b / S3b)

- Per-event TRIGGERS_OBLIGATION edge authoring beyond a starter set of ~15 high-priority events
- Aggregation engine (P5) — requires its own state machine, defer
- Negative-cascade blocker enforcement (P6) — defer to after basic cascade works
- Implication grouping UI (P10) — comes with the S3 implications surface

### What this means schedule-wise

Original S2 estimate (design memo): ~1 session.
Post-meditation estimate: ~2-3 sessions.

Worth it. Shipping S2 with only 8 events would force a "we forgot X" cycle within weeks. Shipping with the full vocabulary + the 6 new edge types means S3 (implications surface) can be built against a stable foundation.

## Open questions for user

1. **Aggregation engine** — is thresholded aggregation in S2 or pushed to a later layer? My instinct: defer, but acknowledge the gap.
2. **Cross-tenancy cascade** (P4 sub-processor scenario) — defer to v2 or model now?
3. **Event-emits-event chains** — depth cap of 4 OK?
4. **Effectiveness proof requirement** (P8) — extend `changes_detected` schema in this session or leave for S3?

## Companion changes captured during the meditation

The audit doc lists 17 typed edges in Neo4j. The meditation suggests adding 6 more (EMITS_EVENT / EXPECTS_FOLLOWUP_EVENT / UPDATES_FACT / EXPANDS_SCOPE / CASCADES_REVIEW / BLOCKS_WHEN) — bringing total to 23.

The relationship_model_design memo's Section 12 "Open Questions" should be updated to absorb these.
