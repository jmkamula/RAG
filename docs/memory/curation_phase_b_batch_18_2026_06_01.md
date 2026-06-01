---
name: curation-phase-b-batch-18-2026-06-01
description: Phase B records_program batch 18 — A.5.34 (Privacy/PII protection) promoted to 4-leaf; natural pair with A.5.33; partial-evidence shape (OFI 1/4); TWO DerivedSpecs reference A.5.34 items; eval 73/74 → 74/75 clean upper bound
metadata: 
  node_type: memory
  type: project
  originSessionId: cc746afe-8680-4e51-a963-96eb379653f8
---

Phase B batch 18 — single-control records_program promotion. A.5.34
(Privacy and PII protection) promoted from single-leaf to 4-leaf
records_program spine pairing with A.5.33 from batch 17
([[curation-phase-b-batch-17-2026-06-01]]). A.5.33 protects the
records; A.5.34 protects the PII subset with privacy-law overlays.

**Why:** Continues [[curation-program-full-multi-leaf]]. A.5.34 is the
natural next step after A.5.33 — records-protection family completion
before crossing into A.5.35 independent review + A.5.36 compliance
review (both already curated, single-leaf, candidates for future
alignment).

**How to apply:** Pattern to reuse for future PIMS-adjacent privacy
controls. The two-way DerivedSpec dependency check (next bullet) is
the key trap when curating a control that already serves GDPR
derivations.

**Shipped (commit pending — current session 2026-06-01):**
- 4 leaves: privacy_and_pii_protection_policy (procedure, preserves
  prior single-leaf id) + pii_processing_register + privacy_
  applicability_scope + privacy_program_review (freshness=365)
- Eval 73/74 → 74/75 clean upper bound (only #25 known-stale; on this
  run #3 + #24 also stochastic-failed but documented as non-blocking).

**Two-way DerivedSpec item-id preservation (load-bearing):**
A.5.34 is referenced by TWO DerivedSpecs (vs A.5.33's one):

1. `SPEC_ART_25` (GDPR Art.25 Data protection by design and by default)
   at document_requirements.py:6015 — references 4 A.5.34 items:
   - `item:A.5.34:applicable_laws`
   - `item:A.5.34:pii_inventory`
   - `item:A.5.34:retention_minimisation`
   - `item:A.5.34:security_controls_ref`

2. `SPEC_ART_24` (GDPR Art.24 Responsibility of the controller) at
   document_requirements.py:6208 — references 5 A.5.34 items:
   - `item:A.5.34:applicable_laws`
   - `item:A.5.34:lawful_basis`
   - `item:A.5.34:data_subject_rights`
   - `item:A.5.34:security_controls_ref`
   - `item:A.5.34:breach_handling`

Combined set: 7 unique items (overlap on `:applicable_laws` and
`:security_controls_ref`). ALL 7 must be preserved as ChecklistItem
ids somewhere in the A.5.34 cluster. After batch 18: six stay on the
policy leaf (where the concepts naturally live — applicable_laws,
lawful_basis, data_subject_rights, retention_minimisation,
security_controls_ref, breach_handling), `pii_inventory` relocates
to the register leaf (its natural home — the catalog of processing
activities, not a policy clause).

Verify after any A.5.34 edit:
```python
needed = ['item:A.5.34:applicable_laws', 'item:A.5.34:pii_inventory',
         'item:A.5.34:lawful_basis', 'item:A.5.34:data_subject_rights',
         'item:A.5.34:retention_minimisation', 'item:A.5.34:security_controls_ref',
         'item:A.5.34:breach_handling']
all_items = [i.id for r in ALL_EVIDENCE_REQUIREMENTS
             if r.control_ref == 'A.5.34'
             for i in (r.must_contain + r.should_contain)]
assert all(n in all_items for n in needed)
```

**Partial-evidence shape (third such case):**
Engine sits at OFI 1/4 — Arion has an uploaded privacy policy that
the matcher recognises as satisfying ALL 8 MUST items of the policy
leaf via semantic matching (a useful confirmation that the matcher
is concept-level, not text-level). The three new leaves (register +
scope + review) carry no evidence yet. So:
- live posture: Comply (hand-entered, empty gap)
- engine posture: OFI (1/4 satisfied, 3 leaves unsatisfied)
- engine ≠ live → Stage-2 surfaces the OFI proposal

Third partial-evidence case in the suite:
- #55 — A.5.15 (Access control policy, policy_program 1/4)
- #60 — A.5.23 (Cloud services policy, op_process 1/4)
- #75 — A.5.34 (PII protection, records_program 1/4)

Each one is a different spine, which validates the partial-evidence
path across all spine families.

**Semantic matcher confirmation:**
The policy leaf carries 8 MUSTs in batch 18 (was 7 in the prior
single-leaf — added `transfer_restrictions` + `owner`). ALL 8 are
recognized in Arion's existing privacy policy evidence. This proves
the matcher is concept-level — adding new MUST items that the
existing evidence covers doesn't break recognition. (Watch for the
inverse: adding a MUST that's NOT in existing evidence would flip
the leaf from satisfied → unsatisfied and the engine verdict would
shift; review existing evidence-doc content before promoting any
already-Compliant control.)

**Freshness cadence — annual (365d):**
Matches the records-family default established by A.5.33 batch 17
and the existing A.5.35 (independent review) + A.5.36 (compliance
review) annual cadence. Privacy program review at annual is doctrine
— GDPR doesn't mandate a fixed cadence so the convention is annual,
with ad-hoc triggers (Schrems shifts, sectoral enforcement actions,
M&A) captured in `rev_ad_hoc_triggers` SHOULD.

**ISO × GDPR integration — fourth MUST family in Phase B:**
1. `pii_overlay` MUST on A.5.13 labelling (batch 10)
2. `legal_jurisdiction` MUST on A.5.14 information transfer (batch 11)
3. `proc_pii_overlay` SHOULD on A.5.33 (batch 17)
4. `transfer_restrictions` MUST on A.5.34 policy leaf (this batch) +
   `reg_transfers` MUST on register leaf — encodes GDPR Chap V
   (Art.44-49) explicitly at MUST level

The pattern is now established: when an ISO control extends naturally
into GDPR territory, encode the integration at spec level. Promoted
to MUST (not SHOULD) here because cross-border PII transfers are
unavoidable for any org touching EU/EEA data subjects — unlike
A.5.33's PII overlay which can be SHOULD because tax-records-only
orgs have zero PII to overlay.

**PIMS (ISO/IEC 27701) alignment SHOULD:**
New `pims_alignment` SHOULD on the policy leaf captures the ISO/IEC
27701 PIMS extension where in scope. Kept as SHOULD (not MUST)
because A.5.34 is universal — every ISO 27001 org should have a
privacy policy, but only orgs pursuing 27701 certification need to
explicitly align with PIMS controls. Marks A.5.34 as the natural
landing point for any future 27701 curation work.

**Cross-control links established:**
- A.5.34 transfer_restrictions → A.5.14 (transfer policy)
- A.5.34 retention_minimisation → A.5.33 (records schedule)
- A.5.34 security_controls_ref → A.8.x (encryption A.8.24, access
  A.5.15/A.8.3, logging A.8.15/A.8.16, pseudonymisation A.8.11)
- A.5.34 breach_handling → A.5.24/A.5.26 (incident family) + GDPR
  Art.33-34
- A.5.34 scope_obligations_link → A.5.31 (applicable obligations)
- A.5.34 reg_ropa_link → GDPR Art.30 RoPA (Art.30 already curated
  4-leaf in calibration #4)
- A.5.34 dpia_process → GDPR Art.35

**Next records-family candidates:**
With A.5.33 + A.5.34 promoted, the records-family is complete for
the A.5.3x block. Natural next steps:
- A.5.35 (Independent review of information security) — already
  curated single-leaf with freshness=365; candidate for alignment
  or promotion to multi-leaf
- A.5.36 (Compliance review records) — already curated single-leaf
  with freshness=365; candidate for alignment or promotion
- A.5.37 (Documented operating procedures) — natural end of A.5
  block; check current curation state

After A.5.3x is complete, the A.5 Organisational Controls block is
fully multi-leaf except for A.5.18 (Access rights) which was the
original gap that started this whole arc (case #1).
