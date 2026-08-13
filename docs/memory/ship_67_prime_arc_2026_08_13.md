---
name: ship-67-prime-arc-2026-08-13
description: "Ship 67' — resolve the H3.a 'numeric fabrication' dogfood finding. Root cause was terminology collision — engine's composite count (leaves + derived deps) and RelatedCard's leaves-only count both rendered as 'required items present' with different denominators. Rename one to 'fulfilment elements met' and the other to 'evidence artifacts present' so the LLM can quote either without contradiction."
metadata:
  type: project
  ship: "67'"
---

# Ship 67' — Numeric fabrication root cause: terminology collision

## The dogfood finding

Ship 65's Art.32 dogfood + user's second-pass paste flagged that the
LLM prose fabricated *"none of the 9 required items are fully
present"* while the structured card underneath correctly showed *"0
of 4 required items present."* The user asked: *"how is 40% false-
alarm possible?"* — kicking off the investigation.

## Investigation

First hypothesis: LLM hallucination. Trace the digest → wrong.

Root cause discovered by instrumenting the digest capture:
```
POSTURE (showing 10 of 212 assessed):
- Art.32 [NC] ALL: 0 of 9 required items present (3 with partial
  evidence); still needed: test log; ...
```

**The digest itself says "0 of 9 required items present."** Not a
hallucination — the LLM is faithfully quoting.

Where does "9" come from? The engine's fulfilment spec walks two
kinds of children when composing Art.32:
- **4 direct-evidence leaves** (`program_review`,
  `applicable_scope_note`, `risk_appropriate_measures_register`,
  `resilience_test`)
- **5 derived-dependency verdicts** (Art.32 derives from ISO 27001
  A.5.18, A.5.24, A.5.30, A.8.13, A.8.24 — the "IMPLEMENTS" chain)

Total: 4 + 5 = 9 children. Engine reason string:
`"ALL: 0/9 children satisfied (3 with partial evidence)"`.

## The terminology collision

The digest's `_JARGON_SUBS` regex (Ship 2'.i) rewrote the engine's
`"N/M children satisfied"` → `"N of M required items present"`. But
`rag/casefile/answer_augment.py::_evidence_summary` — which builds
the RelatedCard's post-response summary — uses:
```python
summary = f"{n_satisfied} of {n_leaves} required items present"
```
where `n_leaves` is the leaves-only count (from
`build_per_must_advisory_data`).

Three surfaces, one phrase, three different denominators:
1. Engine reason via digest jargon-sub → **composite** (leaves +
   derived): 9 for Art.32
2. RelatedCard evidence_summary → **leaves only**: 4 for Art.32
3. DocumentContext render → **MUSTs on the specific doc**: variable

The auditor / tenant sees "0 of 9 required items" in the prose and
"0 of 4 required items" in the sidebar card. Same words, different
numbers. The LLM's intro is *technically correct* (quoting the
digest); the structured card is *also technically correct*
(counting leaves). Neither is fabrication — they're just measuring
different things.

## The fix

Give each denominator its own noun:

- **Engine composite view** → *"N of M fulfilment elements met"*
  (Ship 67' — `rag/casefile/digest.py::_JARGON_SUBS`)
- **RelatedCard leaves view** → *"N of M evidence artifacts
  present"* (Ship 67' — `rag/casefile/answer_augment.py`)
- **DocumentContext MUSTs view** → *"N of M required items"*
  (unchanged — this really is MUSTs, auditor-natural)

Test assertions updated
(`tests/casefile/test_digest.py::test_sanitize_gap_text_children_satisfied`
+ `test_posture_line_uses_sanitized_gap`) to lock the new phrasing.

Answer schema docstring
(`rag/casefile/answer_schema.py::LeafState.evidence_summary`)
updated too.

SPA leaf-detail render at `static/arioncomply.html:3687` uses
`d.n_have / d.n_total` where `d` is a per-leaf record — MUST-level
count, auditor-natural "required items" phrase preserved.

## Verification

Post-Ship-67' Art.32 chat query:
```
GDPR Art.32 (Security of processing) requires ... Currently NC —
none of the 9 required fulfilment elements are fully met, with
only partial evidence for some items. Compliance is demonstrated
via ISO 27001 controls, notably A.5.23, which is currently NC.

## Complete and maintain the test log
Establish and maintain a comprehensive test log ... This is a
missing fulfilment element and must be documented ...
```

- **"9 required fulfilment elements"** — accurate composite count,
  no ambiguity.
- **"missing fulfilment element"** — LLM adopts the phrase
  naturally in remediation prose.
- Structured card section shows *"evidence artifacts present"*
  14× (leaves view).
- Zero occurrences of the old *"required items present"* phrase in
  the chat prose.

## Codified lesson

### 31. Same phrase, different denominator = fabrication signal

When two subsystems build the same output surface with different
denominators but the same phrase, downstream consumers (LLM,
human, auditor) will read one as ground truth for the other.
Looks like fabrication; is actually a naming collision.

Rule: when multiple surfaces render "N of M X" counts, X must
carry the denominator's semantics. If two surfaces render at
different granularities, they must use different nouns.

## Follow-ons deferred

- **Numeric-check preservation guard** — the Ship 2' preservation
  check catches missing refs / verdicts but not fabricated numbers.
  Ship 67' fixed the fabrication trigger; adding a guard against
  future fabrications remains latent scope.
- **Cross-surface number consistency audit** — DocumentContext still
  uses "required items"; SPA leaf-detail also. These are semantically
  the same (MUSTs), so no conflict — but a broader audit would
  confirm nothing else shares the phrase with a mismatched
  denominator.

## What Ship 67' costs

- Schema migrations: 0
- Wall clock: ~45 min (investigation + fix + tests)
- Files touched: 4 (digest.py + answer_augment.py + answer_schema.py +
  test_digest.py)
- Lines: ~20 net
- Eval regression: to be confirmed at commit
