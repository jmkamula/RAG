---
leaf_id: req:A.5.29:information_security_during_disruption
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: plan
trigger_type: universal
template_version: 3
must_count: 8
should_count: 3
---

# Information Security During Disruption Plan

## What this template gives you

The **plan** for how information security holds (or degrades
gracefully) when your normal operations are disrupted — outage,
attack, supplier failure, natural event, regulatory shutdown.
Auditors check that it (a) exists, (b) has been exercised, (c)
covers degraded-state controls (not just "we'll restore quickly").
Untested continuity plans fail when needed; this is why the test
schedule MUST is mandatory.

## When to use it

You're producing the plan required by **ISO/IEC 27001:2022 A.5.29**.
Distinct from **A.5.30 ICT Readiness for Business Continuity** —
A.5.29 is "how does security hold during disruption"; A.5.30 is
"can we restore ICT services". Co-produced; cross-referenced.

## Before you start

- [ ] **A.5.7 Threat Intelligence** — informs scenario list (MUST 1)
- [ ] **A.5.9 Asset Register** + dependencies — drives which
      controls must continue
- [ ] **A.5.21 ICT Supply Chain** — supplier-failure scenarios
- [ ] **A.5.24 IR Procedure** — incident-triggered activation
- [ ] **A.5.30 ICT Readiness Plan** — pair-control coherence

## Cross-references

- **A.5.30 ICT Readiness** (pair-control)
- **A.5.7 Threat Intelligence**
- **A.5.21 ICT Supply Chain Risk**
- **A.5.24 IR Procedure** (activation path)
- **A.5.26 Incident Response** (operational coordination)
- **6.1.2 Risk Assessment** (disruption scenarios in register)

## Estimated effort

**8-16 hours** for v1 (scenario work is the bulk); **2-3 days
annual exercise**; **plus** post-exercise refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Document the disruption scenarios considered

<<MUST item:A.5.29:scenarios>>

> _Standard text:_ Disruption scenarios considered (cyber attack [link to A.5.7 threat intel], natural event, supplier failure [link to A.5.21], regulatory action, key-personnel loss)

_Scenario list — disruption isn't a single event; planning is
scenario-specific._

State the scenarios. Each has different security implications.

**✓ Good** (scenario list):

| Scenario | Triggers | Key security impacts |
|---|---|---|
| Cyber attack (ransomware) | Detected encryption / wiper malware | Production data unavailable; integrity compromised; legitimate access disrupted |
| Cyber attack (data exfil) | DLP / IDS alert; supplier-disclosed | Confidentiality compromise; potential A.5.24 + GDPR Art.33 notification |
| Cloud provider major outage | Provider status page; multi-AZ failure | A.5.23 single-provider dependency; failover to DR region |
| Supplier failure (financial / insolvency) | Vendor announcement; service degradation | Identity provider, payment processor, etc. |
| Natural / utility event | Site / region affected | Premises (if any in scope); cloud-region impact |
| Regulatory action (shutdown / data-residency) | Regulator order / sanctions | Geographic re-architecture; data-flow re-route |
| Key personnel loss | Death / incapacity / sudden departure | Single-points-of-knowledge; access lapse |

(Scenarios should be cross-linked to risk-register row IDs.)

<<TEXT>>

## 2. Name security controls that must continue operating

<<MUST item:A.5.29:must_continue>>

> _Standard text:_ Security controls that must continue operating during disruption (named explicitly — encryption, access control, audit logging at minimum)

_Non-negotiable baseline — even during disruption, some controls
hold at full strength._

State the controls that don't degrade. Encryption + access control
+ audit logging is the typical floor.

**✓ Good**: "Controls that MUST continue at full strength during
ANY disruption: (a) Encryption-at-rest + in-transit (A.8.24). (b)
Access control (A.5.15-18) — no shared accounts, no bypass.
(c) Audit logging (A.8.15) — write-only sink ensures continuity
even if processing pipelines fail. (d) MFA on all production
access (A.5.17). (e) DPA + Art.28 processor protections for
personal data (Art.32). Any plan or scenario that compromises
these is escalated to ISMS Owner + DPO."

<<TEXT>>

## 3. State acceptable degradation levels per control

<<MUST item:A.5.29:degradation_levels>>

> _Standard text:_ Acceptable degradation levels stated (which controls can drop to compensating, which must hold at full — risk-tiered)

_Graceful degradation — risk-tiered controls that CAN drop to
compensating._

For each control that can degrade, state to what level and what
compensating measures replace it. Tiered by risk.

**✓ Good** (degradation map sample):

| Normal control | Acceptable degradation | Compensating |
|---|---|---|
| A.5.18 access-rights review cadence quarterly | Pause review during major incident | Auto-extension max 30 days + post-disruption catch-up review |
| A.8.32 change-management oversight | Emergency-change fast-track | Post-hoc reviewer attestation within 5 days |
| A.5.22 supplier-review cadence annual | Postpone non-critical-tier reviews | Maintain Tier-3 schedule; defer Tier-1 by max 6 months |
| A.8.7 anti-malware (full pattern updates) | Lag patterns by 24h max | Heuristic + anomaly detection compensates |
| A.5.7 threat-intel feed full breadth | Reduce to high-priority sources | SecOps daily review until restored |

<<TEXT>>

## 4. Define fallback / compensating security measures

<<MUST item:A.5.29:fallback>>

> _Standard text:_ Fallback / compensating security measures when primary controls fail (per-control: what replaces it, what residual risk it accepts)

_When primary fails, what's the backup — and what residual risk
does it accept._

For each scenario, the fallback controls + the explicit residual
acceptance.

**✓ Good**: "Per-scenario fallbacks: (a) Cloud-provider outage:
DR-region failover; same controls activate in DR; residual risk
during failover window (5-15 min) accepted by CTO. (b) Identity-
provider outage: emergency-access procedure (single break-glass
account, two-person sign-off, time-limited to 4h, full audit);
residual risk accepted by CISO. (c) DLP / monitoring outage:
manual review of high-risk operations + enhanced audit; SecOps
on-call elevated coverage."

<<TEXT>>

## 5. Plan communication during disruption

<<MUST item:A.5.29:communication>>

> _Standard text:_ Communication during disruption (internal personnel, external customers, regulators, suppliers; out-of-band channels when corp comms compromised)

_Internal + external comms — out-of-band channels when corp comms
compromised._

State channels per stakeholder + out-of-band fallback.

**✓ Good**: "Communication during disruption: (a) Internal staff:
primary = Slack + corp email; OOB fallback = Signal group (IR
team) + SMS broadcast (all-hands). (b) Customers: primary =
status page + customer-success direct; OOB = secondary status
page hosted on different provider. (c) Regulators: primary =
SA portal + DPO email; OOB = recorded phone hotline if portal
down. (d) Suppliers: primary = supplier portal + procurement
contact; OOB = phone tree. OOB credentials + channel configs
stored offline in IR kit."

<<TEXT>>

## 6. Plan restoration of normal security controls

<<MUST item:A.5.29:restoration>>

> _Standard text:_ Restoration of normal security controls after disruption ends (sequenced, verified — re-encryption, audit-log replay, access-control reactivation)

_Stand-down sequence — restoring controls in the right order
prevents re-disruption._

State the sequence + verification.

**✓ Good**: "Restoration sequence: (1) Verify root cause addressed +
no active threat. (2) Re-activate encryption-key rotations if
paused. (3) Re-instate access-review cadences with catch-up
schedule. (4) Re-engage paused supplier-review cycles. (5) Validate
audit-log integrity (no gaps in coverage during disruption).
(6) Restore patterns / signatures to current. (7) Stand-down
declared by Incident Manager + ISMS Manager + (Sev 1) ISMS Owner.
Each step verified + recorded in stand-down log."

<<TEXT>>

## 7. Define activation authority

<<MUST item:A.5.29:activation_authority>>

> _Standard text:_ Activation authority defined (who declares the plan active; who declares it stood down; criteria for each)

_Who declares the plan active + who declares it stood down._

State criteria + named role.

**✓ Good**: "Activation: any Sev 1-2 incident (A.5.24) auto-engages
this plan's relevant scenarios. Explicit activation criteria: (a)
Cloud-provider major outage > 30 min, (b) Identity-provider outage
> 15 min, (c) Confirmed major data-confidentiality compromise,
(d) Regulator order, (e) Site-affecting natural event. Activation
authority: IR Manager declares (in-progress incidents); ISMS Owner
declares (proactive / regulator). Stand-down: IR Manager + ISMS
Manager joint decision; documented criteria met."

<<TEXT>>

## 8. State test schedule for the plan

<<MUST item:A.5.29:test_schedule>>

> _Standard text:_ Test schedule for the plan (cadence stated; promoted from SHOULD because untested continuity plans fail when actually needed)

_Untested continuity plans degrade — annual minimum, often quarterly
tabletop._

State exercise cadence + variety. Pairs with A.5.30.

**✓ Good**: "Test schedule: (a) Tabletop exercises quarterly — each
quarter covers one scenario from MUST 1; full coverage over
12 months. (b) Annual full-simulation exercise with DR-region
failover (coordinated with A.5.30 ICT readiness test). (c) Annual
supplier-failure simulation (Tier 3 supplier outage scenario).
(d) Annual out-of-band comms drill. Each exercise produces an
A.5.29 plan_activation_record (type=test). Findings feed A.5.27
lessons-learned + 10.1 improvement actions."

<<TEXT>>

---

## Recommended additions

### BCP integration

<<SHOULD item:A.5.29:bcp_integration>>

> _Standard text:_ Integration with the broader Business Continuity Plan (this is the security ANNEX to the BCP — BCP itself is out of scope)

_BCP cross-link — this plan is the security overlay on a broader
business continuity plan._

State the BCP that this is the security-controls overlay on.

<<TEXT>>

### Residual-risk register

<<SHOULD item:A.5.29:residual_risk>>

> _Standard text:_ Residual-risk register for disruption scenarios where degradation creates accepted exposure (named risk owner per scenario)

_Each fallback + degradation accepts residual risk — capture
explicitly._

Aggregate the residual acceptances from MUSTs 3 + 4 into a single
register entry for audit.

<<TEXT>>

### Third-party-service plans

<<SHOULD item:A.5.29:third_party>>

> _Standard text:_ Third-party-dependent controls flagged (where the plan relies on supplier action — cross-link to A.5.22 review)

_Supplier-side disruption affecting our delivery — pair with the
A.5.21 supply-chain risk procedure._

Cross-link to supplier-specific contingency plans where they exist.

<<TEXT>>
