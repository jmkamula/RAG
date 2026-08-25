---
name: feedback-advisory-tone-not-authoritative
description: "Tenant-facing prose must sound advisory, not authoritative. Lay truth plainly — completeness + best practice — no auditor overtones, no rubberstamp language. ArionComply surfaces + tracks; it doesn't decide, verify, or certify."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

# Advisory tone, not authoritative tone

**The rule**: every tenant-facing surface — chat, dashboard, Evidence
Package, Fix Workload, notifications, attestation prompts, template
prose — should read like a knowledgeable advisor laying out truth
plainly. Never like an authority certifying, verifying, or approving.

**Why**: ArionComply is a compliance program ledger, not a compliance
authority. We surface what evidence exists + tracks freshness +
ownership + gaps. The tenant decides. Their auditor decides. We
never do. Language that sounds authoritative ("attested by
ArionComply", "audit-ready", "verified", "certified") over-promises
what the product does + creates legal + trust risk. Language that
sounds rubberstamp ("Complete ✓", "Pass") over-simplifies + makes
tenants stop reading the details that matter.

Related: [[human-in-the-loop-positioning]] +
[[product-principle-cite-expose-and-track]] — same underlying
positioning, applied to tone.

## How to apply

**Prefer** — plain truth + completeness framing + best-practice
guidance:
- "3 of 7 required elements have evidence on file"
- "Partial evidence — one column typically closes this"
- "Best practice would show X here; the standard doesn't require it"
- "Your workbook shows STATUS in the Improvement Actions sheet"
- "No workbook mapping in the catalog binds this — the only path
   is to upload a document"
- "Your last review record dates from 2026-05-01"

**Avoid** — authoritative claims about compliance state:
- ~~"You are compliant with A.5.9"~~ → "A.5.9 has direct evidence
   on file for every required element"
- ~~"ArionComply verified this cite"~~ → "You attested this cite
   on 2026-08-24"
- ~~"Audit-ready"~~ → "Auditor-visible" or drop the word
- ~~"Compliance attestation"~~ → "Tenant confirmation"
- ~~"Certified"~~ → drop; ArionComply doesn't certify anything

**Avoid** — rubberstamp language:
- ~~"✓ Complete"~~ → "Direct evidence on file"
- ~~"Pass"~~ → "Required elements covered"
- ~~"OK"~~ → be specific about what's OK
- ~~"Approved by ArionComply"~~ → "You approved this on 2026-08-24"

**Avoid** — auditor overtones outside auditor-specific surfaces:
- The **Evidence Package export** is the auditor deliverable — it's
  appropriate for THAT surface to use auditor-facing framing
  ("standard obligation", "verbatim excerpt", "source reference").
- Every OTHER surface (dashboard, chat, Fix Workload, Stage-1
  queue, notifications) speaks to the tenant. The tenant's frame
  is "am I complete + what should I work on next", not
  "will this pass an audit".

## Test — read it out loud

If it sounds like a compliance officer confidently telling their
auditor "yes we've done X", that's wrong. If it sounds like a
consultant walking their client through the current picture + best
next step, that's right.

## Codified 2026-08-25

Ship 93'.c review. Fix Workload initially framed as "auditor-ready"
narrative + reused Evidence Package tone. User flagged: "we need to
lay the truth as we know it plainly, not auditor overtones or
rubberstamp, just completeness and best practice. user gets the
sense that we are advisory not authoritative."
