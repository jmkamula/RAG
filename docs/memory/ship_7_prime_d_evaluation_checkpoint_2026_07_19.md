---
name: ship-7-prime-d-evaluation-checkpoint-2026-07-19
description: "Ship 7'.d — evaluation checkpoint on post-gateway output; polish() skipped; strip_markdown_escapes added"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 7'.d (2026-07-19) — the pre-registered evaluation
checkpoint from Ship 7'.a. Sampled real outputs from each of
the 4 surfaces Ship 7'.c migrated, judged whether an LLM
`polish()` layer is warranted, and shipped a targeted
deterministic fix for the one real gap surfaced.

## Evaluation samples

### 1. Evidence Package (auditor-facing) — VERDICT: PASS

Rendered `req:A.5.15:access_control_policy` for the Arion
tenant via `/api/v1/dashboard/leaf/{leaf_id}/evidence-package`.

    # Access Control Policy — Coverage Summary
    _A.5.15 · ISO 27001:2022 · Generated 2026-07-19_
    **Status:** Fully covered — 7 of 7 required elements
    covered (100%).
    ## What this is about
    To ensure authorized access and to prevent unauthorized
    access to information and other associated assets...
    ## This particular artifact
    A.5.15 requires rules controlling physical and logical
    access based on business and information security
    requirements. The policy states the principles and decision
    rules; the provisioning procedure (lifecycle) lives at
    A.5.18. Approval, communication and periodic review are
    sibling leaves.

Reads exactly like an auditor's summary. Curator-authored
`business_description` + leaf `description` come through the
Ship 7'.c `evidence_prose` surface unchanged (nothing to
scrub). No polish() would improve this — an LLM might drift
factuality on the "sibling leaves" claim.

### 2. Posture detail — VERDICT: NEEDS DETERMINISTIC FIX (not polish)

Sampled `/api/external/v1/posture/{ref}` on real Arion data.

**Clean cases** (human-authored gap_description, e.g. A.7.14):
Reads naturally, no changes needed.

    "BYOD environment requires comprehensive secure disposal
    procedures including data backup verification, multiple
    technical deletion methods..."

**Broken cases** (extractor-produced, e.g. 7.2.8): backslash-
escaped markdown punctuation surviving the gateway.

    Before Ship 7'.d:
    "Verpex processes: \- Server log data \(IP addresses,
    browser information, timestamps\) \- Contact form
    submissions \(temporarily relayed to us\)\."

This is a NEW jargon pattern not identified in the 7'.a audit.
Source: mammoth-processed DOCX output writes markdown-escaped
punctuation into `document_findings.excerpt` →
`posture_controls.gap_description`. The Ship 7'.c gateway
chain doesn't touch backslash-escape sequences.

**The fix** (this arc): new `strip_markdown_escapes` transform
that strips `\<punct>` for markdown-special punctuation
(`- ( ) . + * _ [ ] ! | < > # { } \` ~`). Preserves `\n`,
`\t`, and other legitimate escapes.

Added to the `stage2_reason`, `evidence_prose`, and
`cascade_rationale` surface chains. Idempotent.

**After Ship 7'.d** (same input, same request):

    "Verpex processes: - Server log data (IP addresses,
    browser information, timestamps) - Contact form
    submissions (temporarily relayed to us)."

Reads naturally.

### 3. Notification body — VERDICT: FUNCTIONAL, POLISH BORDERLINE

Latest tenant notification:

    Title: Document processed: 4 findings across 1 control
    Body:  We extracted 4 findings from your document. 0
           postures updated, 0 created. Review the pending
           items in the Stage-1 queue.

Terse. Concrete. Factual. A tenant reads this and knows what
to do. An LLM might rephrase as "We processed your document
and found 4 items to review; none automatically updated your
posture yet — check the Stage-1 queue to promote them."
Warmer, longer, but risks factuality drift ("promote them" —
does that word actually reflect what tenants do next?).

Not worth an LLM polish layer for a ~30-word notification. If
tenants complain about tone, revisit as its own arc.

### 4. Cascade timeline — VERDICT: UNTESTABLE

Zero cascade events in the dev tenant across the last 365
days. Ship 7'.c's cascade migrations are unit-tested but no
live sample to judge. Deferred to a real customer engagement.

## Decision — skip polish(), close Ship 7'.d as targeted fix

Evidence from the 3 testable surfaces: the deterministic
gateway is producing output that meets the 7'.a bar — factual,
complete, jargon-free (with the markdown-escape fix). The
notification borderline isn't worth the polish() infrastructure
cost (LLM latency, cost, failure paths, `output_polish_log`
schema, per-surface prompt engineering).

The Ship 7'.a design predicted this branch: **"If [outputs
look natural after JUST the deterministic pass], skip to
7'.f."** That's the path taken.

Ship 7'.e (conditional second polish() surface) is now MOOT.
Next: Ship 7'.f arc retrospective.

## What shipped in 7'.d

- `rag/output/transforms.py::strip_markdown_escapes` — new
  idempotent transform + regex `_MD_ESCAPE_RE`
- Registered in `TRANSFORMS` dict + re-exported from
  `rag/output/__init__.py`
- Added to 3 surface chains in `rag/output/gateway.py`:
  `stage2_reason`, `evidence_prose`, `cascade_rationale`
- `tests/test_output_gateway.py` — 6 new assertions (positive
  case + preserved whitespace escapes + idempotence + 2
  gateway-integration cases)
- Total 57 assertions (was 51), all PASS

## Baseline

Full eval running. Change is additive-scrub: reduces stored
prose noise, doesn't remove information.

## Ship 7' progress

| Sub-arc | Status |
|---|---|
| 7'.a Output audit + gateway proposal | ✓ |
| 7'.b Gateway skeleton + 2 pilots | ✓ |
| 7'.c Migrate remaining MIXED sites | ✓ |
| **7'.d Evaluation checkpoint + markdown-escape fix** | **✓** |
| 7'.e (conditional) second polish() surface | SKIPPED |
| 7'.f Arc retrospective | next |

## Related

- [[ship-7-prime-a-output-audit-2026-07-19]] — the checkpoint
  design that this arc executes
- [[ship-7-prime-c-mixed-site-migration-2026-07-19]] — the
  four migrations this arc evaluates
