# cite_columns criterion

*Reference doc for curators authoring or reviewing
`db/workbook_mappings/*.yaml`. Complements the required/optional
discipline (see Ship 89'.a curator guidance).*

---

## Purpose

`cite_columns:` declares which columns in a tenant workbook carry
**citations to external evidence** — hyperlinks or references to
documents living outside the workbook row itself (SharePoint
policies, external system records, regulator URLs, evidence PDFs).

The framing: **stored vs cited evidence** (product principle,
Ship 87). Stored = evidence lives in the workbook row. Cited =
row points at where evidence lives. Ship 3'-arc external cite
machinery (verification_log + `cite_verification_overdue`
notification) takes over the lifecycle.

## The core auditor test

**Would an auditor need to walk out of the workbook to verify this cell?**

- YES → the cell POINTS AT evidence living elsewhere → **cite column**
- NO — the cell contents ARE the evidence (ID, date, owner, status, description) → **required or optional column**

That's the primary test. Two supporting signals refine the binding.

## Column-shape signal (tenant workbook)

Tenants use predictable naming for citation columns. When authoring a
new register mapping, ask: "of the columns a tenant might add to this
register, which are likely to carry hyperlinks or doc references?"

Register-type → typical cite column names:

| Register type              | Typical cite column headers                       |
|----------------------------|---------------------------------------------------|
| Risk register              | Treatment Plan, Treatment Doc, SoA Ref            |
| DPIA register              | DPIA Report, Report Link, Assessment Doc          |
| Incident log               | Incident Report, Post-mortem, Report Ref          |
| DSAR / rights register     | Response Doc, Fulfillment Evidence                |
| Supplier register          | Contract Ref, DPA Doc, SLA Ref                    |
| Audit register             | Audit Report, Finding Reference                   |
| Legal / regulatory         | Requirement URL, Regulator Site                   |
| Access register            | Approval Ref, Ticket, Change Record               |
| Training log               | Certificate, Proof of Completion, Materials       |
| Review record              | Review Report, Meeting Minutes                    |
| SoA                        | Linked Policies, Reference                        |
| Change record              | Change Doc, Approval Ref                          |
| BCP / DR                   | Continuity Plan, Test Report                      |

Common cite-intent tokens in headers: `link`, `url`, `ref`, `reference`,
`doc`, `document`, `report`, `evidence`, `proof`, `attachment`,
`source`, `supporting`, `contract`, `agreement`, `certificate`, `plan`,
`manual`.

## MUST-shape preference (how to bind)

Once a column qualifies, pick the `binds_to` MUST via two-tier fallback:

### Tier 1 — tight (preferred)

Bind to a MUST whose name contains cite-shaped tokens: `_ref`, `_link`,
`_evidence`, `_certificate`, `_report`, `_plan`, `_doc`, `_source`,
`_trail`, `_reference`, `_authorisation`, `_permit`, `_attachment`.

**Examples (from Ship 89-90 catalog):**
- `Contract` column → `role_contract_link` MUST (MUST name literally `_link`)
- `Agreement Reference` column → `reg_agreement_reference`
- `Consent Link` column → `consent_link`
- `Linked Policies` on SoA → `soa_reference` (existing cite-shape MUST)

Curator confidence: **high**. Ship 90'.a sweep showed 7 of 10 sampled
bindings were tight — the MUST name literally aligns.

### Tier 2 — stretch (when catalog has no cite-shape MUST)

Some registers were authored before Ship 89'.b; their MUSTs are all
data-shaped (`reg_treatment_status`, `reg_dpia_id`, `reg_scope_check`).
When the register genuinely has a cite column but no cite-shape MUST
exists, bind to the **semantically closest data MUST** — the one the
cited document corroborates in practice.

**Examples (from Ship 90'.a sweep):**
- `Treatment Plan` column (risk register) → `reg_treatment_status`
  (cited plan corroborates the treatment activity)
- `DPIA Report` column → `reg_dpia_id`
  (cited report corroborates the DPIA identity/existence)
- `Meeting Minutes` on supplier review → `rev_reports`
  (cited minutes corroborate the reported review)

Curator confidence: **medium**. Semantically defensible but introduces
drift — auditor sees a cite bound to a data MUST. Not wrong; just
softer than Tier 1.

### Anti-pattern binds (Tier 2 stretch — DON'T)

**Never bind cite to a MUST whose name ends `_date`, `_at`, or
`_owner` (or is one of those bare tokens).**

- `_date` / `_at` — timestamps. A cite corroborates a document
  existing, not a date. The Ship 90'.a DSAR `response_date` case is
  the poster child (`Response Doc` column bound to
  `reg_response_date` — semantically wrong; the document
  corroborates the outcome, not the date).
- `_owner` — a name string. The person is the evidence, not a doc
  pointer.

**Deliberately allowed** (subtle but defensible):

- `_id` — identity MUSTs CAN be corroborated by external reports.
  `DPIA Report → reg_dpia_id` is auditor-defensible: the linked
  report proves the DPIA row exists. Ship 90'.a produced ~7
  cite bindings of this shape (audit_id, dpia_id, finding_id,
  incident_id, doc_id, change_id, audit_id).
- `_status` — status MUSTs CAN be corroborated by certificates or
  proof-of-completion docs. `Certificate → reg_status` (training,
  personnel attestation) is auditor-defensible: the cert proves
  the completion status. Ship 90'.a produced ~4 cite bindings of
  this shape.

The distinction: dates and owners are pure data attributes. IDs and
statuses are anchors whose existence CAN have external
corroboration. Tier 2 stretch is defensible for identity + status,
weak for dates + owners.

Ship 91'.h enforces this via post-LLM filter in both
`ship86a_workbook_curator.py` (new YAML authoring) and
`ship90a_cite_columns_sweep.py` (catalog sweep).

## When NOT to add cite_columns at all

Some register shapes have no cite column by design:

**A. Data-only registers.** Asset register — the ID + Name + Owner +
Location IS the evidence. No external doc to cite. LLM correctly
returned `no_cite_shape` on asset-shaped mappings during Ship 90'.a.

**B. Attestation-only registers.** Personnel Security Attestation,
Policy Acknowledgment — presence in the register IS the evidence.
Nothing external to cite.

**C. Matrices.** RACI, segregation of duties, access-to-PII matrix
— pure grid data. Cells are role assignments, not pointers.

**D. Single-topic logs where the log IS the evidence.** Credential
Revocation Log, DLP Alert Log, Capacity Monitoring Log — data columns
contain the evidence.

**E. GDPR data-subject rights registers (mostly).** DSAR rights columns
(scope, timing, outcome, requester) are data. Only the response
document is a cite candidate; other columns are stored evidence.

## cite_kind field

Set based on the URL type tenants will actually use:

| Value | When to use | Typical URL shape |
|---|---|---|
| `internal_document` (default) | SharePoint, internal DMS, drive links | `../../../:w:/...` (SharePoint) or `\\fileshare\...` |
| `url` | Public web URL (regulator, standard body) | `https://nukib.gov.cz`, `https://cloudsecurityalliance.org` |
| `external_system` | Okta, Odoo, ServiceNow, ticket ref | `https://<tenant>.okta.com/...`, `https://helpdesk/tickets/...` |

## verification_days field

Cadence for Ship 3'.g `cite_verification_overdue` notifications:

| Cadence | Use for |
|---|---|
| `90` | Volatile external references (threat feeds, vulnerability disclosures) |
| `180` | Regulatory URLs (regulations change), review cycles under 1 year |
| `365` (default) | Policy references, annual review cadence |
| `730` | Long-cycle references (5-year retention, stable framework docs) |

## Fingerprint hygiene

- Keep `fingerprint` at **1-3 tokens**. Workbook tokenizer requires ALL
  tokens to appear in the header (subset match). Longer fingerprints
  never match — enforced by Ship 90'.a validation (drops proposals
  with `len(fingerprint) > 3`).
- Add `alternative_fingerprints` for common naming variants:
  ```yaml
  - fingerprint: [policy, ref]
    alternative_fingerprints:
      - [policy, reference]
      - [reference, policy]
      - [policy, link]
      - [policy, doc]
    binds_to: "item:X:policy_ref"
  ```
- Lowercase, singular where possible. Tokenizer stems trailing `-s`
  and maps synonyms (`process → procedure`, `standard → policy` —
  see `_SHAPE_SYNONYMS` in `workbook_discovery.py`).

## Known edge cases (catalog debt)

### 1. Adjacent columns with empty headers

Some workbooks put multiple citations in adjacent columns without
headers. **Ship 91'.f audit found this on SoA**: column H has
"Linked Policies/Processes" (69 hyperlinks matched); columns I-N have
80 additional policy hyperlinks with no headers. Current fingerprint
matching only covers H.

**Workaround (interim)**: encourage tenants to consolidate cited
docs into a single delimited cell (comma-separated URLs) or use a
sub-table shape we can fingerprint.

**Longer-term (Ship 92'+)**: extend fingerprint semantics to allow
"primary column + N adjacent unnamed columns → same cite binding."
Requires reader-side change to preserve column-adjacency signal.

### 2. Duplicate cite columns across passes

Some mappings have multiple passes (e.g. attestation register + review
record). If both passes have `cite_columns:` for the same MUST +
sheet, dedup only happens via the `external_evidence_source
UNIQUE(tenant, must_id, system_id)` constraint. Curator should avoid
duplicate cite_columns entries across passes on the same file.

### 3. Non-URL text in cite columns

Tenant fills a "Policy Reference" cell with plain text like "See
Info Security Policy v3" (no hyperlink). The Ship 89'.b row-level
guard (`_column_has_real_cite_hyperlink`) requires a real hyperlink,
so this cell is skipped. Correct behavior — plain text without a
verifiable URL isn't a Ship 3'-style cite. But some tenants use this
pattern; they may want the row's `optional_columns` corroboration
credit instead.

## Ship 91'.f audit summary (ISO Arion, 250 hyperlinks)

| Disposition | Count | % |
|---|---|---|
| **A. matched cite_columns → cite emitted** | 131 | 52.4% |
| B. mailto: filtered (auditor emails) | 32 | 12.8% |
| C. header-row hyperlink (metadata) | 4 | 1.6% |
| **D. unmatched column in cite-enabled mapping** | 83 | 33.2% |
| E. no cite_columns in matched mapping | 0 | 0% |
| F. sheet doesn't fingerprint any mapping | 0 | 0% |

**Key insight**: catalog reach on Arion is solid (0% in E + F —
every hyperlink-carrying sheet fingerprints AND its mapping has
cite_columns declared). The main gap is **column-shape coverage
within already-cite-enabled mappings** — 33.2% land in undeclared
columns. Most of that (80 hyperlinks) is the SoA adjacent-columns
edge case; the rest (3) are truly-uncovered columns like ISMS
Schedule "PROGRESS NOTES", Legal Register "Comm. channels", SIG
"Findings".

## Curator checklist

Before adding `cite_columns:` to a mapping:

- [ ] Does the register semantic have external evidence (not
      data-only / attestation / matrix)?
- [ ] Does the target column carry citations (auditor test:
      "walk out to verify")?
- [ ] Does the catalog leaf have a cite-shape MUST (Tier 1)?
      - If yes: bind there
      - If no: pick closest-meaning data MUST (Tier 2) —
        NOT `_date`/`_at`/`_id`/`_owner`/`_status`
- [ ] `fingerprint` ≤ 3 tokens, lowercase, common register
      column-name variants added as `alternative_fingerprints`?
- [ ] `cite_kind` set to match tenant URL shape (internal_document
      / url / external_system)?
- [ ] `verification_days` matches cadence expectation for this
      evidence type (default 365, tighter for regulatory feeds)?

Run `scripts/validate_workbook_mappings.py` to enforce cite
discipline programmatically (Ship 91'.i extension).

## Related

- Ship 87'.a corroboration discipline (auditor lens on partial)
- Ship 89'.a required/optional discipline (three-way column model)
- Ship 89'.b cite-mode integration + row-level HL guard
- Ship 90'.a catalog sweep (5 → 89 files)
- Ship 91'.f hyperlink audit (data behind this doc)
- Ship 91'.h post-LLM filter (enforces Tier 2 anti-patterns)
- Ship 91'.i validator extension (catalog-time enforcement)
