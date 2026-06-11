---
name: feedback-workbook-yamls-semantic-class
description: "Workbook mapping YAMLs (db/workbook_mappings/) should fingerprint the SEMANTIC CLASS of each column (competence | metric | topic | etc.), not the specific phrasing one tenant uses. Author each new YAML against the general vocabulary that any reasonable tenant might use for that evidence shape; tenants validate, not specify."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When authoring or refreshing a workbook mapping YAML, design the
column `fingerprint` set as a SEMANTIC CLASS, not a tenant-
specific phrase.

**Why:** the system serves many tenants, not just the validation
case in front of us. A YAML tuned narrowly to one tenant's exact
column titles (`[required, competence]` matching only sheets
titled exactly "Required Competence") fails on the next tenant
who uses "Competency Area" or "Skill" or "Knowledge Area". The
fingerprint matcher is token-subset; multiple alternative
fingerprints binding to the same `item:X.Y:id` is the pattern.

**How to apply:** for each binding target item, list at least 3-5
fingerprints covering the realistic vocabulary classes a tenant
might use. Validation against one real workbook (e.g. Arion) is a
sanity check that the YAML still matches a sensible specific
case — not a directive to use that tenant's exact words. After
validation, the YAML should match any tenant whose column means
the same thing in plain English.

**Scar:** 2026-06-11 — I initially proposed YAML edits using
Arion-specific column phrases (`[risk, id]`, `[risk, description]`).
User pushback: "Arion should act as an example, the design should
be general." Rewrote the YAMLs with semantic-class vocabulary —
[[workbook-yaml-vocab-refresh-2026-06-11]] — and the same patterns
now cover any sensible tenant naming.

This applies equally to `db/doc_mappings/` (the document-side
analog) and any future YAML-driven matcher. Tenant data is a
validation lens, not a vocabulary specification.

## Related

- [[doc-mappings-no-tenant-specific]] — sibling rule: don't put
  tenant-specific abbreviations into the global mapping namespace.
  Same shape — these YAML stores are GLOBAL across tenants.
- [[workbook-yaml-vocab-refresh-2026-06-11]] — the project memory
  where this rule was applied.
- [[workbook-intake-corpus-v1-complete]] — the corpus this rule
  governs.
