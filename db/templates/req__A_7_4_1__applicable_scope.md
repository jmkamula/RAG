---
leaf_id: req:A.7.4.1:applicable_scope
control_ref: A.7.4.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Collection Contexts Scope

> The upstream — which collection surfaces are in scope (forms + cookies + APIs + logs + integrations + third-party enrichment).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Collection surfaces enumerated (customer forms / employee onboarding / marketing forms / cookies / weblogs / API webhooks / integrations)

<<MUST item:A.7.4.1:scope_surfaces>>
_Why: Coverage_

<<TEXT>>

## 2. Indirect-collection map (technical logs + inferred data + third-party enrichment)

<<MUST item:A.7.4.1:scope_indirect_map>>
_Why: §7.4.1 — indirect_

<<TEXT>>

## 3. Excluded surfaces with rationale (e.g. anonymous analytics)

<<MUST item:A.7.4.1:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product surface / new integration)

<<SHOULD item:A.7.4.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
