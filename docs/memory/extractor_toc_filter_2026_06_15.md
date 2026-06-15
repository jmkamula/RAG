---
name: extractor-toc-filter-2026-06-15
description: "SHIPPED 2026-06-15 (5216168): rag/intake/extractor.py drops TOC / document-index docs at extract entry. Doc-level analog of the 2026-06-12 questionnaire filter. Two signals: filename token ('TOC' / 'Table of Contents' / 'Index of') OR ≥3 lines matching 'N.N Title — Purpose:' shape at ≥30% density. Surfaced by a TOC upload that produced 47 inert pending findings."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

A "TOC Information Security Documents.docx" upload during the
2026-06-15 session produced **47 spurious findings** (18 ISO +
29 GDPR xfw_bridge) by treating TOC purpose-blurbs as actual
policy evidence. The blurbs grounded against the doc body
because they really were in the file — but they describe what
OTHER documents do, not what controls are implemented.

## Excerpts that fooled the LLM

```
2.1 Information Security Policy — Purpose: Defines the
  overarching security objectives.
2.2 Access Control Policy — Purpose: Establishes guidelines
  for granting, modifying, and revoking access...
3.2 Access Management Process — Purpose: Defines how user
  access is provisioned, reviewed, and revoked...
```

Plus bare blurbs stripped of the section number:

```
Defines how personally identifiable information (PII) collected
during lead generation, sales, and client engagement operations
is securely processed...
```

All bound to A.5.x / Art.x controls as `partial` or `present`.

## Why existing filters didn't catch it

- Grounding check passed (text IS in the doc)
- Confidence was medium (not dropped)
- Length OK (>20 chars)
- No `(Y/N)`, no `Proof Point:`, no `?` close — not a questionnaire
- Referential demotion didn't fire — refs weren't in the quote

## The filter

Module-level in `rag/intake/extractor.py`:

```python
_TOC_FILENAME_TOKENS = ("toc", "table of contents", "index of")
_TOC_LINE_RE = re.compile(
    r"\b\d+\.\d+\s+[A-Z][\w &/-]{2,80}\s+[—\-–]\s+"
    r"(?:Purpose|Defines|Establishes|Provides|Describes|Outlines)\b",
)

def _looks_like_toc(doc) -> str:
    # filename signal
    name = (doc.original_name or "").lower()
    for tok in _TOC_FILENAME_TOKENS:
        if tok in name: return f"filename token '{tok}'"
    # content density signal
    text = (doc.full_text or doc.markdown or "")[:20_000]
    hits = _TOC_LINE_RE.findall(text)
    if len(hits) < 3: return ""
    nonblank = sum(1 for ln in text.splitlines() if ln.strip()) or 1
    if len(hits) / nonblank >= 0.30:
        return f"toc-shape density {len(hits)}/{nonblank}"
    return ""
```

Called at the **top of `extract()`** — before scoping, before LLM
calls. Returns `[]` with `extraction_metrics["skipped_as_toc"]`
populated. No LLM tokens spent on these docs.

## Why doc-level not quote-level

The questionnaire filter is quote-level: each evidence quote
checked independently. TOC blurbs include bare descriptive
sentences (no section number prefix) that look identical to
real policy prose at the quote level. The signal that they're
TOC content lives at the **document level**: the doc's body
density of TOC-shape lines OR its filename.

Doc-level skip is cheaper too — one regex pass vs N LLM calls.

## The two-signal design

Either signal suffices. Filename catches the common case
("TOC.docx", "Table of Contents.pdf") cheaply. Density catches
TOCs that don't self-label (e.g. "ISMS_Doc_Register.docx" whose
body is dense with `N.N Title — Purpose:` lines).

The 30% density threshold + min-3-hits avoids false-positives
on real policies that happen to cite TOC entries in their body
text (e.g. a "Related Documents" section in a longer policy).

## Operational cleanup

The 47 stranded pre-filter findings were swept to rejected via
a transactional UPDATE, identical pattern to the 2026-06-12
questionnaire cleanup:

```sql
UPDATE document_findings
SET review_status = 'rejected',
    rejection_reason = 'toc_extraction_bug_2026_06_15',
    is_active = FALSE,
    reviewed_at = COALESCE(reviewed_at, now())
WHERE document_id = '<the TOC upload id>'
  AND is_active = TRUE;
```

Note: A.5.1 had already been auto-approved at 10:08 (1 min
after upload) — `reviewed_by` was NULL, matching the chat-user
placeholder gap from `[[hitl-two-stage-rollout-gotchas]]`. The
COALESCE preserves the original timestamp for audit. Inert for
posture (no checklist_item_id post Phase-1 retirement) but
conceptually wrong; rejection backs it out.

## Doc-shape filters family

The extractor now has three sibling filters at parse + extract
time, each catching a specific shape of "the LLM was fooled by
surface similarity":

| filter | level | shape caught | shipped |
|---|---|---|---|
| `_evidence_grounded` | quote | hallucinated quote | 2026-06-09 |
| referential-mention demotion | quote | register-shape | 2026-06-10 |
| `_looks_like_questionnaire` | quote | Y/N templates | 2026-06-12 |
| **`_looks_like_toc`** | **doc** | TOC/index | **2026-06-15** |

The promotion from quote-level to doc-level is the new pattern
here. Worth applying again the next time a per-quote filter
proves too fine-grained for a whole-document failure shape.

## Test coverage

`tests/test_extractor_filters.py` (NEW 2026-06-15) — 13 cases
covering both the questionnaire and TOC filters with
positive + negative + edge cases. First unit test file for
extractor.py filter logic; the questionnaire filter previously
had no automated test, just smoke checks. Run via:
```
PYTHONPATH=/data/arioncomply python3 tests/test_extractor_filters.py
```

## What this doesn't solve

- **Mixed docs** — a real policy with a Table of Contents
  section at the top would NOT trigger (TOC density across the
  whole doc would be low). That's the intended behaviour; the
  policy body is real evidence.
- **Filename-only TOCs without 'TOC' in name** — relies on the
  content-density signal; if density is below 30% it slips. Add
  more filename tokens as new shapes emerge.
- **Non-English TOCs** — English keywords only ("Purpose",
  "Defines", "Establishes", etc.).

## Related

- [[extractor-questionnaire-filter-2026-06-12]] — the sibling
  doc-shape filter
- [[extractor-referential-mention-demotion]] — sibling
  content-level filter
- [[extractor-grounding-rules]] — sibling content-level filter
- [[feedback-eval-with-each-feature]] — the rule that drove
  the unit-test file alongside the fix
- [[hitl-two-stage-rollout-gotchas]] — chat-user placeholder
  gap surfaced by the A.5.1 auto-approval timing
