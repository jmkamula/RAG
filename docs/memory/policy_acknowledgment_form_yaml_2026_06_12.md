---
name: policy-acknowledgment-form-yaml-2026-06-12
description: "SHIPPED 2026-06-12 (fb0e3af): db/workbook_mappings/policy_acknowledgment_form.yaml for Microsoft Forms / Google Forms / Typeform exports. Two passes (A.6.3 training_completion + 7.4 communication_event), column-anchored fingerprints (sheet name 'Sheet1' is useless), acknowledgment-statement column gates the YAML against false-positive matches on any tenant's default Sheet1 tab."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

A new mapping for a previously-uncovered evidence shape:
Microsoft Forms / Google Forms exports collecting personnel
acknowledgments that policies were read. Common pattern across
tenants — Forms is the path of least resistance for "we need
proof people read the policy."

## Why this YAML needed special handling

Microsoft Forms exports default to sheet name **`Sheet1`** —
generic enough that every tenant's workbook has one, useless as
a sheet-shape signal. Standard YAMLs (e.g. `asset_register.yaml`)
weight sheet_name at 0.5 — too much for this case.

This YAML rebalances:

  | weight | this YAML | standard YAML |
  |---|---|---|
  | sheet_name | 0.1 | 0.5 |
  | required_columns | 0.8 | 0.4 |
  | row_count | 0.1 | 0.1 |

Column-level evidence dominates; sheet-name match is essentially
free credit when present. A "Sheet1" tab with unrelated columns
gets sheet_score 1.0 × 0.1 = 0.1 contribution — far below the
drop threshold.

## The gate column

The decisive signal that identifies this evidence shape is the
**acknowledgment-statement column**. Microsoft Forms exports
column headers verbatim from the form question, so the
acknowledgment column reads `"Acknowledgment Statement: I
acknowledge that I have read..."`. Tokens always include
`[acknowledgment]` + `[statement]`. No non-acknowledgment sheet
carries those words together.

Required_columns make this MUST-equivalent — without an
acknowledgment-shape column, the YAML can't score above the drop
threshold. Initial draft used generic `[name]` and `[date]`
fingerprints; verified against a fake "Sheet1 as asset list" —
matched at confidence 1.0 (FALSE POSITIVE). Tightening dropped
`[name]`/`[date]` and forced specifically-form-shape signals
(`[full, name]` / `[completion, time]` etc.). Re-verified: same
asset-list scenario now dropped before persistence.

## Anchors

Two per pass, layered defence:
  - `person_name` on `[full, name]` — anchors that rows are
    people, not assets/vendors/products
  - `iso_date` on `[completion, time]` — anchors that the date
    column has real timestamps (Forms gives ISO format)
  - `email` on the audience column (pass 2) — additional shape
    check

Anchors only fire when confidence falls in 0.30-0.70 band.
Strong column matches push above that band; the anchors are
the safety net for borderline cases.

## What it satisfies

Two leaves, multi-pass:
  - `req:A.6.3:training_completion_register` — 3 of 6 MUSTs
    (personnel_id, completion_date, status); module_id, score,
    next_due genuinely missing from form-export shape
  - `req:7.4:communication_event_register` — 4 of 5 MUSTs
    (event_id, topic, audience, date); channel implicit (online
    form, not a per-row column)

Partial coverage is honest. The form is real evidence of
awareness; it just doesn't carry the full per-event detail a
strict training-event log would have. Spec stays strict; the
register surfaces what it actually proves.

## Arion validation

Uploaded `ISMS Policy and Process Documents Acknowledgment.xlsx`
(6 rows: Petra Ziva, Zorko Petrusa, Matt Dillon, Libor Ballaty,
Mutua Kamula, Albert Zagrobskii × 3 policies):

  - Proposal: confidence 1.0 (column shape strong; anchor band
    not entered)
  - Findings: 7 (3 on A.6.3, 4 on 7.4), all `review_status='pending'`
  - Doc extractor had already run in parallel and produced 5
    independent findings (A.5.1 + A.6.2 + 3 GDPR xfw); both
    paths complementary, not duplicative

## Pipeline routing footnote

The auto-upload pipeline routed this `.xlsx` through the
**doc extractor path** (LLM-driven) not the **workbook
discovery path** (structured). The 2 LLM findings + 3 xfw
proposals landed via the doc path; the 7 structured findings
were produced by running `scripts/discover_workbook.py`
manually post-hoc.

This is a known architectural gap: workbook discovery doesn't
fire automatically on `.xlsx` uploads — only via CLI. Long-
term, the pipeline should run BOTH paths on `.xlsx` uploads
(they produce complementary evidence). Not fixed in this
session; tracked as future work.

## Related

- [[sample-row-anchor-confirmation-2026-06-12]] — anchors are
  part of the layered defence here; this YAML uses them.
- [[feedback-intake-label-unreliability]] — the strategic
  framing that motivated the column-gated approach.
- [[feedback-workbook-yamls-semantic-class]] — the rule this
  YAML embodies (generic patterns, not tenant-specific words).
