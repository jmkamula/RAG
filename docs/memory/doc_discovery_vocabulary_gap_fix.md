---
name: doc-discovery-vocabulary-gap-fix
description: "SHIPPED 2026-06-08 (fea79af): synonym layer (process↔procedure / SOP / standard → policy / log → register etc.) + always-on enricher topic_tokens close the gap where tenant filenames don't share vocabulary with curated leaf titles."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The doc_mappings discovery layer started life as filename-fingerprint
subset matching. Real tenant uploads broke against three vocabulary
gaps the matcher couldn't bridge:

1. **Shape-word synonyms** — tenant says "Process", "Standard", "SOP",
   "Programme"; curated leaves use "Procedure", "Policy", "Plan".
2. **Topic-word mismatch** — tenant filename says "Access Management
   Process"; curated leaf is "Access Rights Management Procedure" —
   "rights" is in the title but missing from filename.
3. **Filename-only matching** — body content isn't used to enrich the
   match signal.

## What shipped 2026-06-08 (commit fea79af)

**Synonym layer in `rag/intake/workbook_discovery.py:_SHAPE_SYNONYMS`** —
shape words canonicalise at tokenize time:
```
process / workflow / wi / sop → procedure
standard / directive / rule   → policy
programme / program / roadmap → plan
report / evaluation           → assessment
log / list / inventory / tracker / record → register
```

The synonym map is consulted in `_stem()` for FOUR token classes:
- post-stem tokens (e.g. "standards" → "standard" → "policy")
- ≤3-char tokens that skip stemming (e.g. "sop", "wi")
- `_STEM_KEEP`-listed tokens (e.g. "process" — without this branch,
  the KEEP early-return short-circuited the synonym map)
- tokens with no suffix match

**`review` is deliberately NOT mapped to `assessment`** — it's also a
topic word in leaf titles like "Compliance Review Schedule" and would
cause false-positive cross-matches (verified during smoke-testing).

**Enricher topic_tokens (`rag/intake/enricher.py`)** — the LLM
classifier call now ALWAYS runs when an api_key is available (was:
fallback only when keyword detection failed). The prompt asks for
5-10 single-word topic SUBJECT NOUNS from the doc body. They feed
`doc.topic_tokens` on `ParsedDocument`.

**Parser-side blocklist** — at JSON parse time, doc-shape words
(`policy`, `procedure`, `register`, `review`, `audit`, `report`, etc.)
are filtered out of topic_tokens. Without this filter, the LLM would
emit `review` as a topic word (the doc body says "review access
regularly") and the matcher would mis-route "Access Management
Process" to A.5.18 `[management, review, procedure]` then later to
9.3 management_review_procedure scaffold via union.

**Discovery union (`rag/intake/doc_discovery.discover_doc(topic_tokens=...)`)**
— filename tokens ∪ topic_tokens for FILENAME fingerprint matching.
Body fingerprints still scored separately against actual body text
(orthogonal signal).

**`extractor._scope_controls_via_doc_mappings`** passes
`doc.topic_tokens` through.

**Umbrella YAML extension (`db/doc_mappings/access_control_policy.yaml`)**
— added procedure variants alongside policy variants
(`[access, control, procedure]`, `[access, management, procedure]`,
etc.). Same 4 target leaves (A.5.15-18). Tenants uploading "Access
Management Process" / "Access Control Procedure" now match the
umbrella, not just per-leaf scaffolds.

## End-to-end verification

`Access Management Process.docx` + topic_tokens
`[access, rbac, mfa, rights, identity]`:
- umbrella `access_control_policy.yaml` matches at confidence 0.9 →
  A.5.15-18
- `A.8.2:privileged_access_procedure` scaffold matches at 0.6 (genuine
  secondary — privileged is an access-management subset)
- Union: 5 controls scoped to LLM
- Previously: 0 matches; fell back to legacy `DOC_TYPE_CLAUSE_MAP`
  broad path

Eval: 195/198 PASS — no regressions; only pre-existing LLM-stochastic
known-stale (#2 ranking, #25 anti-hallucination, #27 cross-framework
format).

## How to apply / when to extend

- **Adding a new shape synonym**: edit `_SHAPE_SYNONYMS` in
  `workbook_discovery.py`. Bidirectional in effect (any leaf title
  containing the canonical word matches uploads using the synonym and
  vice versa). Be conservative — don't add words that ALSO appear as
  topic vocabulary.
- **Adding a topic blocklist entry**: edit `_TOPIC_SHAPE_BLOCKLIST` in
  `enricher.py`. Only block words that are doc-shape vocabulary AND
  not legitimate topic subjects.
- **Topic-word vocabulary mismatches** (e.g. tenant "cryptographic"
  vs curated "cryptography"): not handled by the synonym layer.
  Either hand-tune the relevant YAML's fingerprints, or wait for the
  enricher's topic_tokens to provide both forms.
- **Workbook side** (shares the tokenizer): synonym layer also affects
  sheet-name + column-header matching. The doc-shape synonyms
  (`log → register`, etc.) help workbook discovery catch shape
  variants too. Tested clean.

## 2026-06-10 extension — chat title matcher

The same shape-canonical idea now lives in a THIRD place:
`arion_graph._title_match_against` uses `_SHAPE_CANONICAL` (a
local copy of the same synonym map) to disambiguate doc titles
in chat queries. Without it, "have we uploaded our business
continuity policy?" was matching a doc titled "Business
Continuity Plan" (2-word topic overlap was enough; the
distinguishing `policy` vs `plan` got stripped by `_STOP_WORDS`
before the matcher ran).

Fix (commit f693954): detect shape from the FULL tokenization
BEFORE stopword stripping. If both query and matched title name
a shape, they must canonicalise to the same shape.

**Shape canonicalization now exists in 3 places.** Keep them in
sync when adding new shape synonyms:
- `rag/intake/workbook_discovery.py:_SHAPE_SYNONYMS` (workbook intake)
- `rag/intake/doc_discovery.py` (uses the workbook tokenizer)
- `rag/arion_graph.py:_SHAPE_CANONICAL` (chat title matcher)

Future cleanup: pull these into a shared module if drift starts
mattering.

## Related

- [[doc-curation-engine-v1]] — the architecture this extends.
- [[workbook-intake-corpus-v1-complete]] — the shared tokenizer's other
  consumer.
- [[conversational-context-routing-followup]] — the same chat-side
  bug surfaced a separate routing follow-up.
