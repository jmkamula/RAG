---
name: ship-90-prime-a-cite-columns-sweep
description: Ship 90'.a — extended workbook curator with cite_columns discipline; catalog sweep added cite bindings to 84 register mappings (5 → 89 files with cite_columns)
metadata:
  type: project
---

# Ship 90'.a — cite_columns catalog sweep (2026-08-20)

## Framing

Ship 89'.b introduced `cite_columns:` YAML field for cite-mode
integration; 5 mappings hand-backfilled during dogfood (all on the
ISO workbook's hyperlink-bearing sheets). The other 235 register
mappings had zero cite_columns — meaning tenants uploading their
own registers (DPIA log, risk register, supplier review, audit
execution, etc.) got stored evidence but no cite emission, even
when their sheets have obvious cite columns (Policy Reference,
Treatment Plan Doc, Evidence Link).

Ship 90'.a delivers the systematic extension.

Framing correction from user during Ship 89'.b review: **"workbook
work should apply to any user, Arion remains an example."** The
YAMLs are the product; the demo tenant is dogfood. This arc
extends the catalog reach so cite emission works out-of-the-box on
any tenant workbook that has one of the ~90 register shapes we now
recognise.

## Delivered

**Curator extension** (`scripts/ship86a_workbook_curator.py`):
- Pass 2 prompt teaches three-way discipline (required / optional /
  cite). Concrete examples for common register types (DSAR, asset,
  risk, DPIA) show which columns are anchors, corroboration, cites.
- Emission wired: cite_kind allowlist (`internal_document` / `url` /
  `external_system`), verification_days range (30-3650, default 365).
- Validation drops cite bindings whose MUST id isn't real for the
  target leaf (idempotent gate — same discipline as required/optional).

**Sweep script** (`scripts/ship90a_cite_columns_sweep.py`, ~380 LOC):
- Reads each YAML lacking cite_columns
- Skips by evidence_type shape (matrices, classification schemes)
- Per-pass LLM prompt asks: "does this register shape naturally have
  a citation column? if yes, propose fingerprint + MUST binding"
- Validates against Neo4j MUSTs (verbatim id match), cite_kind
  allowlist, verification_days sanity, fingerprint 1-3 tokens
- Text-based YAML insertion (preserves comments + formatting)
- Idempotent: skip if any pass already has cite_columns
- Modes: `--dry-run` (default) / `--apply` / `--only <file>` / `--limit N`

**Prompt evolution mid-arc.** Initial prompt looked for MUST names
containing `_ref` / `_link`. Result: only 5-10 files got proposals
(the catalog is written for stored evidence, MUSTs named
semantically not cite-shaped). User pointback: "not full scope."
Rewrote prompt to identify **workbook column shapes** tenants would
use (Policy Reference, Treatment Plan, Audit Report) and bind them
to the semantically-closest existing MUST. Result: 84 proposals
across 243 files (35% hit rate).

## Sweep results

Total sweep on 243 mappings:

| Outcome | Count | Meaning |
|---|---|---|
| **ok** | **84** | cite_columns proposal validated + applied |
| no_cite_shape | 148 | LLM correctly identified no external cite (data-only registers) |
| already_has_cite | 5 | Ship 89'.b files (idempotent skip) |
| skipped_by_shape | 4 | matrices + classification_scheme (no cite by design) |
| no_valid_cites | 2 | LLM proposed but validation rejected (bad MUST id) |

Catalog totals after Ship 90'.a:
- **89 files with cite_columns** (up from 5)
- **121 total cite entries** (some files bind 2-3 cites)
- **109 internal_document + 12 url + 0 external_system**

## User eyeball review (10 diverse samples)

| File | Cites | Semantic verdict |
|---|---|---|
| audit_execution_log | audit_report → rec_audit_id; finding_reference → rec_findings | tight |
| controller_processor_decision | contract → role_contract_link | perfect (MUST named `_link`) |
| b.8.2.1 customer_agreement_register | agreement_reference → reg_agreement_reference | perfect |
| b.8.4.2 end_of_service_register | certification_ref → reg_certification_ref | perfect |
| b.8.5.2 destinations_register | basis_link → reg_basis_link | perfect |
| b.8.5.7 subcontractor_engagement | contract_reference + customer_authorisation → same-named MUSTs | perfect |
| lawful_basis_register | consent_link → consent_link; lia_link → lia_link | perfect |
| supplier_review_log | review_report + meeting_minutes + audit_report → rev_reports / rev_audit | tight |
| gdpr Art.15 DSAR | response_doc → **reg_response_date** (weak); fulfillment_evidence → reg_outcome | 1 stretch |
| risk_register | treatment_plan → reg_treatment_status | Ship 89'.b stretch pattern |
| gdpr Art.35 DPIA | dpia_report → reg_dpia_id | acceptable stretch |

7 of 10 semantically tight (MUST name aligns); 3 Ship-89'.b-style
stretches (bind cite to closest-meaning MUST when catalog lacks a
cite-shaped MUST); 1 weakly wrong (DSAR response_date binding —
timestamp shouldn't hold cites). User called "apply all 84 as-is"
— the semantic stretches are auditor-defensible provenance; the
one weak case is 1/121 entries and low-impact.

## Dogfood measurement

Re-extraction on ISO workbook (upload `ebf724de-0629`) after
apply: **no delta** in cite emission — 5 cite rows same as Ship
89'.b close. Expected: the ISO workbook has 6 hyperlink-bearing
sheets, all already covered by Ship 89'.b's hand-backfilled 5
files. The 84 new mappings apply to OTHER register types (risk,
DPIA, supplier review, audit exec, DPA, transfer, etc.) not present
on this workbook.

**The arc value is on OTHER tenants.** A tenant uploading their
risk register with a "Treatment Plan" column pointing at SharePoint
URLs now gets a cite bound to `item:6.1.2:reg_treatment_status`
without any tenant-specific YAML — the catalog covers it.

## Codified lessons

**Lesson 100: Catalog reach ≠ dogfood coverage.** Ship 89'.b
measured on 6 hyperlink sheets, but the catalog serves 240+ register
shapes. Ship 90'.a extends CATALOG reach without changing DOGFOOD
numbers. Reach is proven by "any tenant with register X gets cite Y
by construction"; dogfood only exercises whichever registers happen
to live in the demo workbook. **Measure catalog changes against the
catalog, not the demo.**

**Lesson 101: LLM prompt semantics matter — look for workbook
columns, not MUST names.** Initial prompt asked LLM to find MUSTs
named like cites (`_ref`, `_link`). Result: 5-10 proposals because
the catalog wasn't authored with cite-shaped MUSTs. Rewrote prompt
to identify workbook COLUMN SHAPES and bind cites to
semantically-closest MUSTs. Result: 84 proposals. **When the LLM
is being conservative, check if the prompt is asking about the
wrong side of the mapping.**

**Lesson 102: Text-based YAML mutation preserves catalog craft.**
The 240 workbook mappings have hand-authored comments (rationale,
provenance, cross-references). Round-trip YAML parse+write would
strip them. Ship 90'.a sweep uses regex-based line insertion after
the last `optional_columns:` block — preserves every existing byte
except the inserted cite_columns lines. **For any catalog mutation
sweep, preserve authorial context by construction.**

## Files changed

- `scripts/ship86a_workbook_curator.py` — Pass 2 prompt teaches
  cite_columns discipline; validation + YAML emission handle third list
- `scripts/ship90a_cite_columns_sweep.py` (new, ~380 LOC) — sweep
  driver with dry-run / apply / only / limit modes
- `db/workbook_mappings/*.yaml` — 84 files gain cite_columns blocks

## Deferred to future arcs

- **Ship 90'.b (optional)**: reclassify the 8 anti-pattern files
  (partial on required_columns) from the Ship 89'.a audit — curator
  drift signal worth cleaning
- **Ship 91' (LLM-preformatting-for-extraction lane)**: the recall
  lifter discussed at length. LLM as scaffolded row-arbiter within
  fingerprint-matched sheets. Reads catalog's three-way discipline
  (required / optional / cite) as prompt context. Expected value:
  catch evidence in prose cells / Notes columns that structural
  extraction misses. See earlier discussion in-thread.
- **Ship 91'.b**: auto-verification of workbook cites via
  existing `external_evidence_verification_log` (Ship 3' cite-mode
  cadence machinery) — when a client_document uploaded matches the
  cited URL/filename AND has present findings on the same MUST,
  mark the cite verified. Bounded to cite-mode; does NOT feed engine
  posture (per Ship 89'.b Lesson 98).

## Related

- [[ship-89-prime-b-cite-columns]] — cite_columns YAML field + emission (prerequisite)
- [[ship-89-prime-a-curator-fix]] — Ship 86 curator required/optional discipline (prerequisite)
- [[curation-phase-b-retrospective]] — YAML catalog history
