# Ship 86' arc retrospective (2026-08-19)

## Arc summary

Opened by Ship 85' close-out: extract-time LLM path on multi-sheet
XLSX regressed F1 (-4.89pp aggregate); the durable fix is build-time
LLM curator for `workbook_mappings/*.yaml` (Ship 80'.b/83'.b pattern
applied to a different catalog).

**Delivered**: working curator tool + 4 new mappings on ISO workbook.
Strict F1 nudged +0.25pp (essentially flat) because the ceiling now
lives in `workbook_persistence`'s `status='present'` vs `'partial'`
calibration, not in sheet discovery. Ship 87' opens with that.

## Sub-arcs

### Ship 86'.a — LLM curator for workbook_mappings YAMLs

`scripts/ship86a_workbook_curator.py` (~450 LOC).

**Pattern** (mirror of Ship 80'.b/83'.b fingerprint YAML curator):
1. Read structured_sheets from Ship 85'.a (via `read_document`)
2. Identify unmapped sheets by testing each against existing
   `sheet_name_fingerprints` in `db/workbook_mappings/*.yaml`
3. For each unmapped sheet: 2-pass LLM authoring
   - **Pass 1**: LLM picks target leaf from full catalog (~844 entries
     summarized as `leaf_id | control_ref | title`) + emits
     `sheet_name_fingerprints`
   - **Pass 2**: fetch real MUSTs for the chosen leaf from Neo4j;
     LLM binds columns to those MUSTs verbatim
4. Validate every emitted `must_id` against real MUST list; drop
   fabricated ones silently
5. Write `db/workbook_mappings/ship86_<slug>.yaml` with LLM-authored
   header for audit trail (Ship 83' Lesson 72)

**Model**: gpt-4.1-mini (~$0.02 per sheet, no Claude lock).

**Result on ISO workbook (37 sheets)**:
- 29 sheets already had existing mappings that matched
- 8 sheets unmapped:
  - **4 real compliance mappings authored**:
    - Business Partners Assessment → `req:A.5.19:supplier_register`
    - Competence Records → `req:7.2:competence_record`
    - Risk Comms Matrix → `req:7.4:isms_communication_procedure`
    - This Doc Chng Control → `req:7.5:isms_document_register`
  - 4 correctly identified as non-artefacts (TOC, Formulas,
    Instructions and Definitions, Mapping) — LLM returned
    `target_control="not_applicable"`

**Bug caught mid-run**: v1 curator produced synthesized `must_id`
values (e.g. `item:7.2:competence_record:employee_id`) because the
Pass 1 prompt gave a catalog of LEAVES but not their MUSTs. v2 fix:
after Pass 1 picks a leaf, fetch real MUSTs from Neo4j, feed them to
Pass 2, validate every emitted binding against the real ID set. All
v2 bindings verified to use real MUST IDs (`item:7.2:owner`,
`item:7.2:required_competence`, etc.).

**Bug caught post-write**: initial not_applicable YAMLs (empty
`target_evidence_requirement`) failed
`scripts/validate_workbook_mappings.py` at persist time — one bad
YAML aborted the whole batch. Deleted the 4 not_applicable YAMLs;
kept only the 4 with real target leaves. Discovery ran clean after.

### Ship 86'.b — dogfood + measure

Re-extracted ISO workbook. Stage 4.6 log:
> workbook discovery wrote **48 proposals + 197 findings**

Confirmed the 4 new sheets discover via curator YAMLs; specific MUSTs
matched:
- `item:7.5:{reg_title, reg_owner, reg_version, reg_approval_date, reg_next_review}` — 5 MUSTs
- `item:7.4:{reg_event_id, reg_topic, reg_audience, reg_channel, reg_date}` — 5 MUSTs
- `item:7.2:{required_competence, basis_of_competence, effectiveness, documented, owner}` — 5 MUSTs
- `item:A.5.19:{reg_inventory, reg_access_type, reg_owner}` — 3 MUSTs

**F1 vs LLM GT** (all scoring on iso_workbook_expected.yaml):

| Path | Strict F1 | Lenient F1 | Strict TP | Findings |
|---|---|---|---|---|
| Ship 84 (workbook_persistence only) | 4.63% | 21.70% | 5 | 220 |
| Ship 85 (LLM path — regressed) | 2.42% | 12.62% | 5 | 427 |
| **Ship 86 (curator YAMLs added)** | **4.88%** | **20.61%** | **5** | **197** |

**Strict F1 improved +0.25pp**; lenient slightly down (-1.09pp).
The four new sheets DISCOVERED cleanly and populated their MUSTs —
but the workbook_persistence `status='partial'` default kept them
from being counted as strict TPs.

**Ceiling analysis**: the 5 strict TPs are identical across all three
paths. That's not a coincidence — those 5 correspond to MUSTs where
workbook_persistence marks `status='present'` (rare — happens only
when specific column presence + freshness rules pass). The remaining
~30 GT-satisfies MUSTs get marked `status='partial'`, so lenient F1
counts them but strict F1 doesn't. **Ship 87' opens with that
status-calibration issue.**

## Codified lessons

**Lesson 81: Ship 80'.b/83'.b curator pattern generalizes across
catalogs.**

The pattern used for fingerprint YAMLs (Ship 80'.b/83'.b) worked
essentially unchanged for workbook_mappings YAMLs. Same shape:
LLM authors curated YAML from Neo4j context + doc structure; MUST
IDs validated against catalog before write. Different catalog (240
files vs 606) but same authoring loop. **Curator tools are a
transferable primitive** — every new catalog benefits from the same
scaffold.

**Lesson 82: 2-pass MUST binding is the right shape for schema-rich
catalogs.**

v1 curator single-pass fabricated `must_id` values because the LLM
saw a catalog of leaves without MUSTs. v2 2-pass (leaf pick → MUST
list fetch → column bindings) produced 100% real IDs. Rule:
**when the LLM must reference IDs from a large hierarchical catalog,
show it the specific sub-catalog after the parent selection, not the
whole tree at once.**

**Lesson 83: F1 ceiling can move between arcs without measurement
regression.**

Ship 84 F1 4.63% → Ship 86 F1 4.88%. Structurally the arc worked
(discovery went from 40 → 48 proposals, 4 new sheets recognized, 18
new MUST-bindings populated). But the F1 ceiling didn't move because
another arc's problem now dominates. **Progress can be real without
being visible in the top-line number** — measurement needs to
distinguish "discovery ceiling" from "status-calibration ceiling"
from "GT-coverage ceiling."

**Lesson 84: Batch-validation failure aborts atomically.**

The 4 not_applicable YAMLs (empty `target_evidence_requirement`)
crashed `scripts/validate_workbook_mappings.py` at persist time and
prevented ANY workbook_persistence output. Discovered 30 min into
Ship 86'.b. Lesson: **curator scripts should skip authoring for
non-applicable candidates, not write empty-target YAMLs that fail
validation downstream.** The v2 curator will be updated in a
follow-on to skip `target_control == "not_applicable"` cases entirely.

## Files changed

- `scripts/ship86a_workbook_curator.py` (new, ~450 LOC, 2-pass)
- `db/workbook_mappings/ship86_business_partners_assessment.yaml` (new)
- `db/workbook_mappings/ship86_competence_records.yaml` (new)
- `db/workbook_mappings/ship86_risk_comms_matrix.yaml` (new)
- `db/workbook_mappings/ship86_this_doc_chng_control.yaml` (new)
- `docs/ground_truth/ship77d_measurement/run_xlsx_ship86.csv` (new)
- `docs/memory/ship_86_prime_arc_retrospective.md` (this)

## Deferred to Ship 87'

- **Ship 87'.a**: fix `workbook_persistence` `status='present'` vs
  `'partial'` calibration. Current default marks most bindings
  `partial` even when column data is filled. Investigate the marking
  rules in `rag/intake/workbook_persistence.py` + `workbook_discovery.py`.
  Target: strict F1 crosses 15% on ISO workbook.
- Curator script skip-on-not_applicable improvement (avoids the
  batch-validation gotcha)
- Extend curator sweep to non-ISO workbooks once available on tenants
- Templated single-control YAMLs on the ISO workbook aren't picked up
  by workbook_persistence (`ISMS Schedule`, `ISMS Objectives`, `Asset
  Register` etc. — 44 out of 48 discovered proposals) — audit their
  status marking behavior

## Baseline

Ship 86' close: no runtime code changes (curator is a script + adds
YAMLs). Eval baseline preserved from Ship 85' close (232 PASS + 1
WARN + 0 FAIL / 233).
