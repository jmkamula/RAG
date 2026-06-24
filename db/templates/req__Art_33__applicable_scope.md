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

> The upstream — what security events constitute a 'personal data breach' under Art.4(12), boundary with Art.34 (subject notification), lead supervisory authority identification

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Operational definition of 'personal data breach' per Art.4(12) — breach of security leading to accidental/unlawful destruction/loss/alteration/unauthorised disclosure/access

<<MUST item:Art.33:scope_breach_definition>>
_Why: Art.4(12)_

<<TEXT>>

## 2. Lead supervisory authority identified per main-establishment rules (Art.56)

<<MUST item:Art.33:scope_lead_sa>>
_Why: Art.55 + Art.56_

<<TEXT>>

## 3. High-risk overlay (when Art.34 subject notification ALSO triggers — boundary to Art.34 leaf)

<<MUST item:Art.33:scope_high_risk_overlay>>
_Why: Art.34.1 — high risk_

<<TEXT>>

## 4. Excluded events (security events NOT involving personal data; minor near-misses)

<<MUST item:Art.33:scope_excluded_events>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new SA jurisdiction added, scope change affecting main establishment)

<<SHOULD item:Art.33:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
