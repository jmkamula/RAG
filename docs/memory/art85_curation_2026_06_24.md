---
name: art85-curation-2026-06-24
description: "SHIPPED 2026-06-24: Art.85 (GDPR freedom of expression derogation) curated as profile_fact-gated op_process 4-leaf. Closes the last truly-uncurated GDPR article surfaced by xfw_bridge MUST binding work. Sector-applicability gate via ClientFacts.journalism_academic_artistic_processing → RULE_JOURNALISM_ACADEMIC_ARTISTIC. N/A for typical B2B/SaaS/financial tenants; operationally central for media/publishers/academic institutions. All xfw_bridge findings now bound (72/72)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

The xfw_bridge MUST binding work (134e4a6) left 1 unbound bridge on
Arion — A.5.31 → Art.85. Art.85 had no curated leaves and no
DerivedSpec entry, making it the only true uncuration in the
otherwise-complete GDPR coverage.

User's framing led to a meaningful distinction in curation patterns:

- **Direct curation**: spec has direct_evidence leaves with MUSTs.
  The operational pattern. Examples: Art.6, Art.32, Art.28.
- **Derived curation**: spec is a principle alias; derives_from
  resolves to an operational implementer. Examples: Art.5.1.f →
  Art.32, Art.5.2 → Art.24. Both are CURATED — just differently.

Art.85 fit neither well:
- Not operationally implemented by any other curated control
  (A.5.31 only TRACKS Art.85; doesn't IMPLEMENT it)
- Has substantive obligations of its own (classify activities,
  identify per-jurisdiction national-law derogations, apply
  consistently, document legal basis)

Right answer: curate Art.85 directly, but gate by sector
applicability so it resolves N/A for most tenants.

## Pattern: profile_fact-gated 4-leaf

Same shape as Art.8 (children's data), Art.9 (special category),
Art.10 (criminal convictions). Four leaves all marked
`trigger_type="profile_fact"`:

| Leaf | Role | Freshness | MUSTs |
|---|---|---|---|
| `req:Art.85:derogation_application_procedure` | procedure | — | 6 |
| `req:Art.85:national_law_derogation_register` | register | 365d | 6 |
| `req:Art.85:applicable_activities_scope` | scope_note | — | 3 |
| `req:Art.85:program_review` | review_record | 365d | 5 |

## Sector applicability gate

Added to `enrichment/obligations/client_facts.py`:

```python
journalism_academic_artistic_processing: bool = False  # Art.85 derogation eligibility
```

New obligation rule in `enrichment/obligations/obligation_rules.py`:

```python
RULE_JOURNALISM_ACADEMIC_ARTISTIC = ObligationRule(
    id="journalism_academic_artistic_processing",
    condition=lambda f: f.journalism_academic_artistic_processing and f.gdpr_in_scope,
    trigger_type="profile_fact",
    mandatory_controls=["GDPR:2016/679:Art.85"],
)
```

For Arion (B2B SaaS) → fact=False → rule doesn't fire → Art.85
resolves N/A. For media/publisher/academic tenants → fact=True →
Art.85 obligations apply.

## End state on Arion

All engine-actionable sources now have **0 unbound active**:

```
inference_source | unbound | bound
extracted        |       0 |   349
form             |       0 |     0
leaf_scan        |       0 |    51
workbook         |       0 |   204
xfw_bridge       |       0 |    72
```

The A.5.31 → Art.85 bridge now binds to
`item:Art.85:proc_owner` via the canonical-bindings lookup
(direct hit, no derives_from fallback needed). For Arion the
bridge will still be inert at engine level because Art.85 is
profile_fact-gated to N/A — but the binding is correct so a
media tenant uploading the same compliance register would get
proper Art.85 coverage signal.

## Substantive Art.85 obligations (captured in the curation)

Each leaf's MUSTs encode real Art.85 obligations:

- **Procedure**: activity classification rules, jurisdiction
  lookup process, derogation decision rules, legal-basis
  documentation, consistency check
- **Register**: per-(Member State × derogated provision × activity)
  rows with citation + currency dates + Commission notification
  references
- **Scope**: in-scope activities by Art.85 category (journalism /
  academic / artistic / literary), out-of-scope adjacent
  activities, jurisdiction list
- **Review**: annual law-currency check, scope coverage audit,
  subject-rights audit (derogations not over-applied)

References Recital 153 (reconcile both rights, not extinguish
data-subject rights) and Art.85.2 enumeration of derogable
chapters (II, III, IV, V, VI, VII, IX).

## Files touched

| File | Change |
|---|---|
| `enrichment/obligations/client_facts.py` | +1 ClientFacts field |
| `enrichment/obligations/obligation_rules.py` | +1 ObligationRule |
| `enrichment/documents/document_requirements.py` | +4 EvidenceRequirements + ALL_EVIDENCE_REQUIREMENTS registration |
| `enrichment/documents/load_to_neo4j.py` | (no change; loader picks up automatically) |

Neo4j reloaded: 645 EvidenceRequirement nodes (was 641), 4279
ChecklistItem nodes (+20).

## Related

- [[xfw-bridge-must-binding-2026-06-24]] — the prior commit that
  surfaced Art.85 as the lone uncurated target
- [[curation-phase-b-retrospective]] — the arc that curated ~50
  GDPR articles; Art.85 was the final hold-out
- ClientFacts pattern from Art.8/9/10 in batch 27 — direct
  template for this work
