---
name: extractor-questionnaire-filter-2026-06-12
description: "SHIPPED 2026-06-12 (d7f1160): rag/intake/extractor.py drops findings whose evidence quote is a question/checklist item rather than a statement of compliance. Catches vendor-assessment templates and similar Q&A documents that produce dozens of false-positive Comply findings via LLM extraction. Four marker patterns: (Y/N), (Yes/No), Proof Point:, and interrogative+? close. New dropped_questionnaire telemetry bucket."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The LLM extractor was fooled by vendor-assessment questionnaire
templates: a list of *questions to ask vendors* textually matches
the control criteria those questions probe, so the LLM
classified each question as a present/high finding of the
corresponding control. The grounded-quote check passed because
the questions really are in the document.

Surfaced 2026-06-12 by a "Vendor Security Assessment
Report.docx" upload (a blank questionnaire template, not a
populated assessment). The extractor produced **22 ISO findings
+ 25 GDPR xfw proposals = 47 findings**, almost all with
evidence quotes of the form:

    "Does the vendor have a formal information security
     policy? (Y/N) - Proof Point: Vendor security policy
     document."

Approving any of those would have falsely advanced Arion's
posture based on the questionnaire shape.

## The filter

Module-level constants + helper in `extractor.py`:

```python
_QUESTIONNAIRE_PATTERNS = [
    re.compile(r"\(\s*Y\s*/\s*N\s*\)",                          re.IGNORECASE),
    re.compile(r"\(\s*Yes\s*/\s*No\s*\)",                       re.IGNORECASE),
    re.compile(r"\b(?:Proof|Evidence)\s+Point\s*:",             re.IGNORECASE),
    re.compile(                                                                  # interrogative + ? close
        r"\b(?:Does|Has|Have|Is|Are|Will|Would|Can|Should)"
        r"\s+(?:the|your|a|an|you)\b[^?]{0,200}\?",
        re.IGNORECASE,
    ),
]

def _looks_like_questionnaire(quote: str) -> bool:
    return any(p.search(quote or "") for p in _QUESTIONNAIRE_PATTERNS)
```

Any one match → finding dropped at parse time (before bridging,
before persistence). New `dropped_questionnaire` counter
incremented, accumulated to `doc.extraction_metrics` so the
schema_v35 quality-telemetry surface picks it up.

## Why "drop" not "demote to OFI"

The referential-mention rule (similar shape) demotes
Comply → OFI because register-shape docs ARE partial evidence
of awareness — they prove the tenant tracks the control even
if they don't implement it inline. Questionnaires are
different: a list of questions a vendor must answer does NOT
prove Arion tracks anything about its own posture. It's
evidence the vendor will be assessed, not that Arion's controls
are in place. Dropping outright is honest; demoting would
overstate the evidence's relationship to Arion's posture.

(The doc IS legitimate evidence of A.5.19 supplier-assessment
program — the descriptive passage about "this document provides
a structured assessment of third-party vendors" passes the
filter and lands as a real finding. The filter targets the
per-question shape specifically.)

## Test on real today data

Smoke-tested against actual evidence quotes from the Vendor
Security Assessment Report upload:

| sample | drop |
|---|---|
| "Does the vendor have a formal information security policy? (Y/N) - Proof Point: …" | ✓ |
| "Are personal email, removable media, and public repositories prohibited?" | ✓ |
| "Has the vendor undergone recent security audits or penetration testing? (Y/N)" | ✓ |
| "Is the vendor obligated to notify the organization of personal data breaches within 72 hours?" | ✓ |
| **"This document provides a structured assessment of third-party vendors…"** | **keep ✓** |
| **"All data processors requiring GDPR compliance assessment per Article 28"** | **keep ✓** |
| **"Information security policy approved 2025-04-11 by ISMS Owner; reviewed annually."** | **keep ✓** |

47-finding flood → ~2-3 legitimate program-statement findings.

## The wider pattern (referential family)

The extractor now has three sibling content-level filters that
all share the same shape — "this evidence quote looks like a
specific kind of wrong-shape evidence":

  - [[extractor-grounding-rules]] (2026-06-09): drops quotes
    that don't appear verbatim in the source doc
  - [[extractor-referential-mention-demotion]] (2026-06-10):
    demotes Comply → OFI when the quote cites OTHER refs but
    not the bound one (register-shape docs)
  - **THIS** (2026-06-12): drops when quote is a question/
    checklist item (template-shape docs)

Each catches a specific shape of "the LLM was fooled by surface
similarity". The trio is the content-aware safety net for the
LLM extractor; combined with the
[[sample-row-anchor-confirmation-2026-06-12]] system for
workbook discovery, the intake pipeline now has deterministic
guards on both paths.

## What this doesn't solve

  - **Partially-populated questionnaires.** A vendor returned a
    questionnaire with answers filled in alongside the
    questions — the answer lines are real evidence but the
    question lines still drop. Acceptable: the extractor gets
    fewer findings, and the tenant can re-upload a
    questions-stripped version if they want full extraction.
  - **Non-English questionnaires.** Patterns are English-only.
    A French / German / Polish questionnaire wouldn't trigger.
    Acceptable until a tenant needs multilingual support;
    pattern is i18n-localizable.
  - **Disguised questionnaires.** Someone could rewrite "Does
    the vendor have X?" as "The vendor must demonstrate X" —
    no `?`, no `(Y/N)`, no `Proof Point:`. The filter is bypass-
    able by paraphrase but the surface form is the common
    template export.

## Related

- [[extractor-referential-mention-demotion]] — sibling content
  filter, same parse-time location
- [[extractor-grounding-rules]] — sibling content filter
- [[sample-row-anchor-confirmation-2026-06-12]] — workbook-side
  analog of content-level guards
- [[intake-quality-telemetry]] — the telemetry layer the new
  dropped_questionnaire bucket feeds
