---
name: feedback-confirm-before-destructive-db
description: "Never delete tenant DB rows (document_findings, document_uploads, posture_*, etc.) without explicit user confirmation, even mid-experiment. Surfaced 2026-06-11 when I cleared 5 approved Stage-1 findings during a verification sweep without checking — the user had clicked Approve."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Don't delete or truncate tenant data (`document_findings`,
`document_uploads`, `document_text`, `posture_controls`,
`posture_assertions`, `posture_history`) without explicit
user confirmation on each delete.

**Why:** approvals and reviews leave their primary audit trail
in the deleted rows themselves. `document_findings.review_status='approved'`
+ `reviewed_at` + `reviewed_by` are the *only* record that a
tenant confirmed a finding — there is no shadow log to recover
from. Stage-2 traces in `posture_status_log` only fire when a
posture transition actually happens; an approval that just
confirms an already-OFI leaf leaves no trace there.

**How to apply:** even when re-running an experiment that needs
fresh extraction state (re-upload), ask before deleting prior
findings. If the user said they approved, the right path is
**update in place / mark inactive / branch to a new upload**,
not delete. When the user has been actively interacting with
the UI between turns, assume there's been state change you
haven't observed and confirm before destructive ops.

**Scar:** 2026-06-11 — during the Security Test Report bridge
audit, I cleared 5 approved findings to "verify the re-upload
produces only 2 GDPR proposals". The user had already clicked
Approve on the previous batch. Recovery was a re-upload + manual
re-approval; the original `reviewed_at` timestamp is gone for
good.

The harness already has the CLAUDE.md rule "confirm with the
user before proceeding unless durably authorized" — this is the
specific shape of that rule for ArionComply's tenant data.

## Related

- [[bridge-curation-dsar-2026-06-11]] — the context in which
  this scar happened. The curation itself was correct; the
  delete-before-confirming was not.
- [[sql-dry-run-nested-transaction]] — sibling: another case
  where a destructive operation bypassed a safety mechanism.
