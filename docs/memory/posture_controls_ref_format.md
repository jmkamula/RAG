---
name: posture-controls-ref-format
description: "ISMS management-system clauses stored WITHOUT 'A.' prefix (5.1/6.1.2/7.5 etc.); Annex A controls stored WITH 'A.' prefix (A.5.9/A.5.18 etc.). Annex A refs missing the prefix are orphans from a 2026-04-28 workbook intake bug."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

`posture_controls.control_ref` follows two patterns depending on what
kind of control the row represents:

- **ISMS management-system clauses** (ISO 27001 main body §4-§10):
  stored WITHOUT prefix. `5.1`, `5.2`, `5.3`, `6.1.1`, `6.1.2`, `6.1.3`,
  `6.2`, `6.3`, `7.1`-`7.5`, `8.1`-`8.3`, `9.1`-`9.3`, `10.1`, `10.2`.
- **Annex A controls**: stored WITH `A.` prefix. `A.5.1` (information
  security policy as a control), `A.5.9` (asset inventory), `A.5.34`
  (PII protection), `A.8.x`, `A.6.x`, `A.7.x`.

Important: `5.1` (ISMS clause: management commitment) and `A.5.1` (Annex
A control: information security policy) are DIFFERENT rows — both exist
on the Arion tenant. Code that handles control_refs must not strip the
`A.` prefix or it conflates the two namespaces.

## Orphan pattern (cleaned up 2026-06-08)

A 2026-04-28 workbook intake bug wrote Annex A controls as bare `5.x` /
`6.x` / `8.x` (missing the `A.` prefix). 14 such rows existed on Arion,
all `is_active=FALSE` (superseded by correctly-prefixed `A.` rows from a
later sweep):

  `5.9, 5.12, 5.15-5.20, 5.26, 5.31, 5.34, 5.36, 6.4, 8.19`

How to identify on any tenant:
```sql
SELECT control_ref
FROM posture_controls
WHERE standard_id='ISO27001:2022'
  AND control_ref NOT LIKE 'A.%'
  AND control_ref ~ '^[5-8]\.([5-9]|[1-3][0-9])';
-- These are Annex A controls missing the prefix.
-- ISMS clauses go up to 7.5 / 8.3 / 9.3 / 10.2 only, no 5.9 / 8.19 etc.
```

## How to apply

- **Reading the table**: filter by `is_active=TRUE` to skip historical
  snapshots. The dashboard does this; ad-hoc queries should too.
- **Deleting orphan rows**: requires CASCADE through `posture_history`
  first. FK constraint `posture_history_control_id_fkey` blocks direct
  DELETE on `posture_controls`. Pattern:
  ```sql
  DELETE FROM posture_history
   WHERE control_id IN (SELECT id FROM posture_controls WHERE ...);
  DELETE FROM posture_controls WHERE ...;
  ```
- **Writing new rows**: always use the canonical form. ISMS clauses
  bare, Annex A with `A.` prefix. See `db/canonical_control_refs.sql`
  (schema_v14) for the authoritative list.

## Related

- [[workbook-intake-corpus-v1-complete]] — workbook intake v1 corpus
  (post-bugfix). Current intake writes correctly-prefixed refs.
