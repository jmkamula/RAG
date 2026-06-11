---
name: feedback-checklist-must-should-curation
description: "When deciding MUST_CONTAIN vs SHOULD_CONTAIN on an EvidenceRequirement ChecklistItem, ask: (1) is the item clause-mandated by the standard, and (2) does every reasonable shape of this evidence type carry it? If either answer is no, prefer SHOULD. MUSTs that don't meet both tests block leaves on legitimate evidence."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When authoring or reviewing ChecklistItems in
`enrichment/documents/document_requirements.py`, the MUST vs
SHOULD decision should pass two tests:

**1. Is it clause-mandated?** Look at the source_clause field on
the item. If it's a real clause reference ("Clause 7.2 a)",
"Art.32.1.b)") and the clause text unconditionally requires the
artefact, MUST is right. If the clause is conditional ("where
applicable") OR the rationale is soft ("Accountability",
"Audit defensibility", "Operational view"), prefer SHOULD.

**2. Does every reasonable shape of this evidence type carry it?**
Some leaves accept multiple shapes — e.g. a "register" leaf can
be a per-event log OR a per-risk matrix; an asset register can
be per-platform or per-department. If a MUST_CONTAIN item makes
sense in one shape but not another, the leaf can't be fully
satisfied on the alternative shape — and you'll get NC findings
on legitimate evidence. Items that depend on shape should be
SHOULDs.

**Why:** MUSTs that fail either test block leaves on legitimate
evidence. The engine treats a 5-of-6 MUST coverage as "leaf not
satisfied", which downstream means the spec's compose rule reads
0 satisfied children for the control, which means NC stays NC.
The org has the evidence; the curation just doesn't recognise it.

**How to apply:** before declaring a ChecklistItem as MUST, write
the source_clause field. If you can't fill it with a real
unconditional clause reference, write "should" instead. The
chat surface still surfaces SHOULDs to the user; they just don't
gate leaf satisfaction.

**Scar:** 2026-06-11 — `item:7.2:gap_actions` was MUST under
"Clause 7.2 c)" even though that clause is "where applicable".
`item:7.4:reg_sender` was MUST with no clause-ref, just
"Accountability". Both blocked Arion's workbook-evidenced leaves
from satisfying. After downgrading to SHOULDs, three controls
flipped NC→OFI on the back of register evidence the tenant had
been carrying all along — see
[[workbook-yaml-vocab-refresh-2026-06-11]].

## Related

- [[workbook-yaml-vocab-refresh-2026-06-11]] — the project
  arc where this principle was forged.
- [[feedback-workbook-yamls-semantic-class]] — sibling rule on
  the YAML-matching side (vocabulary, not status).
- [[loader-orphan-cleanup-followup]] — the declarative loader
  that cleanly handles MUST→SHOULD demotions (prunes the stale
  edge, adds the new one).
