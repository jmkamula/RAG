---
name: extractor-referential-mention-demotion
description: "SHIPPED 2026-06-10 (03680db): when an LLM finding's evidence quote cites OTHER control refs but not the bound one, demote Comply → OFI. Register-shape docs (compliance requirements, control matrix, gap analysis) name controls without implementing them; this catches the failure mode."
metadata:
  node_type: memory
  type: project
---

Register-shape docs (a compliance requirements register, control
matrix, gap analysis, audit checklist) describe what controls
*are relevant* without actually implementing them. The LLM's
grounding filter sees "this doc mentions A.5.22" and binds the
finding because the quote IS in the source — but the doc is
*listing* the control, not *implementing* it. False positive
disguised as legitimate evidence.

## Trigger case (2026-06-10)

Compliance Requirements.docx upload:
  - A.5.19 bound with quote `"Relevant controls for third-party
    risks include: 5.22 – Addressing information security within
    supplier relationships"`
  - A.5.20 bound with quote `"5.22 – Addressing information..."`
  - A.5.21 bound with quote `"5.23 – Managing information..."`
  - A.5.23 bound with quote `"5.20 – Management of information..."`

In each case the EVIDENCE QUOTE references DIFFERENT controls
than the BINDING. The LLM was reading a register's content (a
list of relevant controls) and treating the mention as
implementation.

## What ships in `_parse_llm_response`

After grounding succeeds, scan the evidence quote for control
refs via `_REFERENTIAL_REF_RE`:
```
\b[Aa]\.\d+\.\d+(?:\.\d+)?\b      # A.5.31 form
| \b\d+\.\d+(?:\.\d+)?\b           # 5.31 / 6.1.2 form
| \bArt\.\s*\d+(?:\.\d+)?\b        # Art.32 form
```

Demotion rule: if `findall(evidence)` returns any refs AND
neither the canonical form ("A.5.31") nor the bare form
("5.31") of the bound ref appears anywhere in the evidence,
demote `Comply → OFI`. The finding still surfaces for HITL
review but doesn't claim "implemented".

Doesn't drop — register docs ARE partial evidence of
awareness/intent, just not full implementation. OFI is the
honest signal.

## Why not just drop?

Dropping would erase the data point entirely. Tenants who
maintain a compliance register DO have something. The
register being uploaded IS evidence that they're tracking
obligations — that's worth OFI on the controls referenced,
not nothing. The auditor wants to see "tenant is aware of X"
even when they can't claim "tenant implements X".

## Why not just downgrade confidence to low?

Low-confidence findings get dropped at the parse-side filter.
That's the same as dropping. OFI is the right signal because:
1. It surfaces to Stage-1 HITL queue
2. The tenant can re-classify if they have actual
   implementation evidence
3. The strict compose rule keeps the live verdict at NC unless
   leaves are fully satisfied — so OFI doesn't accidentally
   promote posture

## Companion fix

Same commit (03680db) also ships
`compliance_requirements_register.yaml` umbrella scoping
"Compliance Requirements" / "Legal Register" / "Obligations
Register" filename shapes to **only A.5.31**. Two-layer
defense:
  - Umbrella layer: narrow the LLM's candidate set so the
    confusion can't even attempt
  - Demotion layer: if a register-shape doc still slips
    through to a wider scope, the demotion catches it

The umbrella is preventative; the demotion is the safety net.

## How to identify a register-shape doc in the wild

- Filename contains "register", "requirements", "matrix",
  "list", "inventory", "catalogue"
- Body contains many references to ISO 27001 / GDPR clauses
  per 1000 chars (high density of `\b\d+\.\d+\b` matches)
- The evidence quotes WOULD bind to many controls based on
  mention, not implementation

The demotion is a per-finding check — it doesn't classify the
WHOLE doc as register-shape. Individual quotes that look
referential get demoted; quotes that look implementational
stay as-is. Surgical.

## When to consider lowering the rule

If we observe many false-NEGATIVE demotions (legitimate
implementation evidence demoted because the LLM happened to
name OTHER controls in the same quote), tighten the rule. The
current rule already exempts quotes that mention the bound
control anywhere — so the false-negative rate should be low.

If we observe many true-positives that the rule still misses
(register docs over-binding despite the demotion firing),
extend `_REFERENTIAL_REF_RE` to catch more ref shapes (e.g.
`Clause 9.3`, `Control A.8.32`).

## Related

- [[doc-mappings-no-tenant-specific]] — global mappings;
  register-shape filename umbrellas are the prevention layer.
- [[extractor-grounding-rules]] — grounding passes for
  register quotes (the text IS in the doc), so the demotion
  has to live one layer above grounding.
- [[compose-posture-any-progress-ofi]] — strict compose rule
  keeps OFI from promoting live posture, so demotion is safe.
