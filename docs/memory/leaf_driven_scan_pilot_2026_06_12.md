---
name: leaf-driven-scan-pilot-2026-06-12
description: "SHIPPED 2026-06-12 (474882b): leaf-driven scan back-binds existing approved findings to specific MUSTs they semantically satisfy but weren't tagged with at extraction time. Pilot on A.6.3 training_completion_register found 2 false-negative bindings (reg_module_id + reg_score on 'Training & Awarnesse' columns). End-to-end: persist → Stage-1 approval → engine sweep → Stage-2 OFI → live NC→OFI."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

First implementation of the false-negative recovery direction
that came out of [[feedback-intake-label-unreliability]].
Targets cases where evidence exists in tenant uploads but the
original mapping bound the column to only one of several
semantically-applicable leaves.

## Why this works (and the earlier per-MUST-scan idea didn't)

Earlier in the session we discussed a pure per-MUST scan —
scanning all findings for evidence of each MUST. Rejected
because a fingerprint like `[score]` would catch Risk Register
scores and falsely satisfy A.6.3:reg_score across controls.

The constraint that fixes the false-positive risk: **scan only
findings already attributed to the parent control**. A "Score"
column on a Risk Register won't ever be considered for A.6.3
because the source finding isn't on A.6.3. The control_ref
binding from the original extraction provides the anchor that
makes per-MUST matching safe.

## The pilot's concrete win

Arion uploaded "ISO 27001 workbook Arion Networks.xlsm" weeks
ago. Its `Training & Awarnesse Record` sheet has columns
`Training Title` and `Evaluation Results`. The workbook YAML
routes those to:

  - `Training Title`      → `item:A.6.3:rev_curriculum_check`
    (awareness_programme_review leaf)
  - `Evaluation Results`  → `item:A.6.3:rev_effectiveness`
    (awareness_programme_review leaf)

Both are valid bindings. But the same column content ALSO
semantically satisfies:

  - `Training Title`      → `item:A.6.3:reg_module_id`
    (training_completion_register leaf)
  - `Evaluation Results`  → `item:A.6.3:reg_score`
    (training_completion_register leaf)

The original mapping picked one leaf per column; leaf-scan
found the other. After tenant approval + engine sweep:

  - `training_completion_register` leaf: 4/6 → 6/6 MUSTs
    satisfied
  - A.6.3 engine view: 0/4 children → 1/4 children satisfied
  - A.6.3 live posture: NC → OFI

This is the FIRST false-negative recovery shipped. Workbook
discovery, doc curation, anchor confirmation, and the various
content filters all reduce false POSITIVES. None of them
recovered evidence that was already in the system but
unbound. Leaf-scan does.

## Architecture

`rag/intake/leaf_driven_scan.py`:

  - `load_catalogs(target_leaf_id=None)` — reads YAML catalogs
    from `db/must_fingerprints/*.yaml`. Each catalog is keyed
    by `target_evidence_requirement` (the leaf id) and lists
    `must_fingerprints[]` of `{must_id, description,
    excerpt_keywords}`.
  - `scan(pg_conn, tenant_id, target_leaf_id=None)` — for each
    loaded catalog: identify currently-unmet MUSTs on that leaf
    for this tenant, pull all approved findings on the same
    control, run excerpt-keyword match per (unmet MUST × candidate
    finding). Returns list of `ScanProposal`.
  - `persist(pg_conn, tenant_id, proposals)` — writes
    proposals as new `document_findings` rows with
    `inference_source='leaf_scan'`, `confidence='medium'`,
    `status='present'`. Tagged excerpt prepends
    `"[leaf-scan back-bind from finding XXXX]"` so the source
    is visible in Stage-1.

Fingerprint catalog format: same shape as workbook YAML column
matching — `excerpt_keywords` is a list of token lists; ANY one
token list fully present (all tokens as substrings) is a match.
Tokens are normalised lowercase + punctuation stripped.

## Schema changes

`schema_v39_inference_source_leaf_scan.sql` extends the
`document_findings_inference_source_check` enum to allow
`'leaf_scan'` alongside the existing `extracted / xfw_bridge /
regex_explicit / llm_xfw / workbook`. Requires DBA password
(`arioncomply` superuser, not `arioncomply_app`).

## Critical design choice: status='present', not 'partial'

Initial draft persisted with `status='partial'` as a hedge —
"back-bind is less certain than fresh extraction". This was
WRONG: the engine's Phase-2 path at `leaf_evaluators.py:177`
only counts `status='present'` findings as items_recognised.
With `status='partial'`, the leaf-scan bindings exist in the
DB but are invisible to the engine — the entire scan is inert.

Fix: persist as `status='present'`. The hedge stays in
`confidence='medium'` (which doesn't gate Phase-2 visibility).
Semantically correct too: a back-binding refers to the SAME
evidence the source finding describes; if the source proves
the column exists with real data, the binding to the new MUST
is just as present.

## False-positive prevention layered

  - Control scope: only findings on the parent control are
    candidates (prevents cross-control noise — A.5.X score
    can't satisfy A.6.3 score)
  - Tenant scope: only unmet MUSTs on THIS tenant trigger
    (prevents proposals for already-bound MUSTs)
  - Source-finding deduplication: same (must_id,
    source_finding_id) pair doesn't yield multiple proposals
  - HITL gate: all proposals land at `review_status='pending'`
    in Stage-1 — never auto-approved, never auto-flip posture
  - inference_source='leaf_scan' tag: tenant sees it's a
    back-bind, not fresh extraction

## What still doesn't auto-fire

Leaf-scan is currently a CLI / library function — not wired
into any pipeline stage. Tenants don't get back-bindings on
upload; they need someone to run the scanner. Operational
options:

  - Post-Stage-1-approval trigger — when a tenant approves
    findings, run leaf-scan on the same control. Catches
    new MUSTs as evidence accumulates.
  - Nightly batch — sweep all controls for all tenants.
  - Admin endpoint — `POST /api/v1/admin/leaf-scan/{control_ref}`
    for manual scoping.

All deferred. Pilot was about validating the pattern, not
operationalising the trigger.

## Catalog curation cost

A.6.3 training_completion_register: 6 MUSTs × ~6 keyword sets
each ≈ ~40 lines of YAML, ~15 minutes to author. Across ~150
multi-leaf curated specs × ~6 MUSTs per leaf = ~900 MUST
entries. Estimated 25-30 hours of curation work for full
coverage. Heavy upfront, but it's a one-time investment that
pays dividends across all current and future tenants.

Cheap to start small — author catalogs for the controls where
false-negatives are most likely (multi-leaf controls where
columns commonly fit multiple MUSTs across leaves). A.5.18
access registers and A.5.16 identity registers are the next
two natural candidates.

## Related

- [[feedback-intake-label-unreliability]] — the strategic
  framing where leaf-driven scan was one of four deferred
  options
- [[sample-row-anchor-confirmation-2026-06-12]] — sibling
  pattern; same fingerprint shape, different scope
- [[posture-writer-drop-fuzzy-match-2026-06-12]] — sibling
  rule: deterministic matching with explicit scope, never
  fuzzy global search
- [[workbook-yaml-vocab-refresh-2026-06-11]] — the workbook
  intake arc where the same column shape pattern (multiple
  semantic MUSTs per column) was first noted
- [[stage1-engine-kick-after-batch]] — once leaf-scan is
  wired into a trigger, this same kick should fire to
  recompute posture
