---
leaf_id: req:Art.33:applicable_scope
control_ref: Art.33
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Art.33 Triggers Scope

<<DOC_CONTROL>>

> The upstream — what security events constitute a 'personal data breach' under Art.4(12), boundary with Art.34 (subject notification), lead supervisory authority identification

## What this template gives you

This template helps you clearly define which security incidents count as a personal data breach under GDPR, and guides you on when to notify affected individuals and identify the lead supervisory authority.

## When to use it

Use this whenever you need to clarify what qualifies as a personal data breach in your environment, especially when reviewing or updating your incident response procedures. Update it whenever your processes or legal obligations change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes roughly 10 to 15 minutes to draft thoughtfully.

## 1. Operational definition of 'personal data breach' per Art.4(12) — breach of security leading to accidental/unlawful destruction/loss/alteration/unauthorised disclosure/access

<<MUST item:Art.33:scope_breach_definition>>
_Why: Art.4(12)_

<<GUIDANCE>>

<<TEXT>>

## 2. Lead supervisory authority identified per main-establishment rules (Art.56)

<<MUST item:Art.33:scope_lead_sa>>
_Why: Art.55 + Art.56_

<<GUIDANCE>>

<<TEXT>>

## 3. High-risk overlay (when Art.34 subject notification ALSO triggers — boundary to Art.34 leaf)

<<MUST item:Art.33:scope_high_risk_overlay>>
_Why: Art.34.1 — high risk_

<<GUIDANCE>>

<<TEXT>>

## 4. Excluded events (security events NOT involving personal data; minor near-misses)

<<MUST item:Art.33:scope_excluded_events>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new SA jurisdiction added, scope change affecting main establishment)

<<SHOULD item:Art.33:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
