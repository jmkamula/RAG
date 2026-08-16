# FindingContract SSoT — evidence consolidation dogfood

_2026-08-16. Post Ship 72' (extractor-side SSoT) + Ship 73' (GDPR bridges). User ask: dogfood the FindingContract itself + close Ship 73' loose ends._

Three sections:
1. Ship 73' loose-end closure (sub-clause retargets, 27701 complement gap, bridge coverage propagation)
2. FindingContract dogfood on 3 real document paths
3. Real bug surfaced: `intake_trace_log` doesn't persist the contract counters

---

## 1. Ship 73' loose ends

### Sub-clause retargets

Re-running Ship 69'.a's `audit_bridge_rationale.py` against the post-73'.b catalog surfaced 3 candidates whose rationales cite sub-clauses:

| Retargeted edge                        | Sub-node needed |
|----------------------------------------|-----------------|
| A.5.33 IMPLEMENTS Art.89 → Art.89.1    | (existed)       |
| A.8.11 SUPPORTS Art.89 → Art.89.1      | (existed)       |
| A.5.33 SUPPORTS Art.82 → Art.82.3      | Created stub    |

Art.82.3 stub: *"A controller or processor shall be exempt from liability under paragraph 2 if it proves that it is not in any way responsible for the event giving rise to the damage."*

Ship 59'.e's stub roll-down handles the MUST inheritance from the parent Art.82. Ship 69'.b's parent-article union in `must_verdicts.py` means Art.82's Evidence Package still surfaces the A.5.33 SUPPORTS bridge — but the RATIONALE now explicitly names Art.82.3, which is more auditor-testable.

### ISO 27701 complement gap

Inbound-bridge counts across the 12 newly-73'.b-bridged GDPR articles:

| Article | ISO 27001 | ISO 27701 |
|---------|----------:|----------:|
| Art.11  | 2 | 0 |
| Art.23  | 0 | 0 |
| Art.27  | 1 | 0 |
| Art.31  | 2 | 0 |
| Art.39  | 2 | 0 |
| Art.40  | 1 | 0 |
| Art.42  | 1 | 0 |
| Art.82  | 1 | 0 |
| Art.87  | 1 | 0 |
| Art.88  | 2 | 0 |
| Art.89  | 0 | 0 |
| Art.90  | 1 | 0 |

**Zero 27701 complements** across all 12 articles. ~7 have plausible mirrors (Art.11 → 27701 A.7.4.5; Art.27 → 27701 B.8.5.x; Art.31 → 27701 A.7.2.7 breach coop; Art.39 → 27701 A.7.2.5 DPO designation; Art.87 → 27701 A.7.4.5; Art.88 → 27701 A.7.2.4; Art.89 → 27701 A.7.4.9; Art.90 → 27701 A.7.2.6). Not authored today — that's a follow-on curator arc (Ship 74'-ish, ~8 edges to draft + review).

### Bridge coverage propagation on Arion

After `load_posture`:

| Article | rows | distinct_sources | Notes |
|---------|-----:|-----------------:|-------|
| Art.31  | 380  | 2 | A.5.24 + A.5.26; heavily bridged, sources have many satisfied MUSTs |
| Art.40  | 153  | 1 | A.5.31; single source, well-satisfied |
| Art.39  | 72   | 2 | A.5.2 + A.5.4 |
| Art.42  | 72   | 1 | A.5.36 |
| Art.11  | 0    | 0 | A.8.11 + A.5.34 both NC on Arion — honest empty signal |
| Art.82 / Art.82.3 | 0 | 0 | A.5.28 + A.5.33 low satisfaction |
| Art.87 / Art.88 / Art.89 / Art.89.1 / Art.90 | 0 | 0 | source controls NC |

4 articles light up; 8 empty because source controls don't have satisfied MUSTs on Arion. **Empty rows are honest signal** (Ship 68'.b's frame): the bridge is authored + present in Neo4j; bridge_coverage populates only when evidence lands. Not a bug.

---

## 2. FindingContract dogfood

Ran 3 documents through the templated edit-zone extractor path with a real reader upstream:

**Case 1 — Templated markdown, unedited round-trip**
```
zones detected: 6
findings bound: 0
metrics:
  contract_skip_pure_scaffolding: 6
  templated_edit_zones_total:     6
  templated_edit_zones_bound:     0
  templated_zones_scaffolding:    6  ← backward-compat preserved
```

**Case 2 — Templated docx, unedited round-trip**
```
zones detected: 6
findings bound: 0
metrics:
  contract_skip_empty_text:       6
  templated_edit_zones_total:     6
  templated_edit_zones_bound:     0
  templated_zones_scaffolding:    6
```

**Case 3 — Templated docx, 2 placeholders filled by tenant**
```
zones detected: 6
findings bound: 2
metrics:
  contract_skip_empty_text:       4
  templated_edit_zones_total:     6
  templated_edit_zones_bound:     2

    · item:A.5.15:logical_rules  → "Logical access: SSO via Okta + hardware MFA…"
    · item:A.5.15:rbac           → "RBAC bundles maintained in Okta per role register…"
```

### Observations

1. **Same contract, different SkipReason per reader shape.** Markdown reader leaves scaffolding text inside the edit-zone body → contract sees content, calls `is_scaffolding`, rejects as `PURE_SCAFFOLDING`. DOCX reader (post-Ship-72'.a) uses ▽/△ rails as tight zone boundaries → contract sees empty text, rejects as `EMPTY_TEXT`. Both outcomes are correct honest signal; the SSoT rule fires uniformly, the input shape determines which reason value applies.

2. **Zero false positives.** Both unedited docs produce 0 findings across every extractor path. The bug Ship 72'.a closed (docx round-trip false Comply) stays closed.

3. **Correct tenant-evidence binding.** Filled placeholders bind to the right `item:A.5.15:logical_rules` + `item:A.5.15:rbac` MUST ids; the tenant text passes through unchanged.

4. **Backward-compat metrics preserved.** Every extractor site still emits `templated_edit_zones_bound` / `templated_zones_scaffolding` / etc. for downstream consumers that haven't migrated to the contract-native counter names.

5. **New `contract_skip_<reason>` counters land alongside.** Both docs surface the contract-native counters in `doc.extraction_metrics`. That's the ONE consolidation point the SSoT needed.

### What NOT observed (also useful)

- No `contract_skip_mangled_item_id` fired (no mangled ids in these test docs). Task #606's dogfood covered that case; the contract inherits it.
- No `contract_skip_unresolvable_control_ref` fired (all item ids resolve cleanly).
- No cross-path contamination — MD reader zones rejected via `PURE_SCAFFOLDING`, DOCX zones via `EMPTY_TEXT`, no leaks either way.

---

## 3. Real bug — `intake_trace_log` doesn't persist the contract counters

Ship 72'.d's retro claimed the contract counters "surface in intake_trace_log automatically." That was wrong.

Verified: `intake_trace_log` has 55 columns, **none** of which include `contract_skip_*` (or the pre-existing `templated_zones_scaffolding` / `templated_zones_mangled` from Task #606). The `tracer.write()` call at `doc_pipeline.py:475` explicitly lists every column it persists — no auto-forwarding of `doc.extraction_metrics`.

**Impact today**: the contract-native counters land on the in-memory `ParsedDocument` object during extraction but never reach persistent storage. Silent-drop is invisible in production traces.

**Suggested fix (Ship 74'-ish)**:
1. `schema_v90.sql` — add columns `contract_skip_empty_text INT NULL`, `contract_skip_pure_scaffolding INT NULL`, `contract_skip_mangled_item_id INT NULL`, `contract_skip_unresolvable_control_ref INT NULL` to `intake_trace_log`.
2. `doc_pipeline.py:475` — pass them through: `contract_skip_empty_text = doc.extraction_metrics.get("contract_skip_empty_text")`, etc.
3. Also add `templated_zones_scaffolding` + `templated_zones_mangled` (pre-existing Task #606 counters that also weren't forwarded).

Small arc. Would close the observability gap the FindingContract was designed to open.

---

## Verdict

**Ship 72' SSoT works.** Uniform behavior across reader types confirmed. Backward-compat preserved. Zero false positives. Correct binding on filled placeholders.

**Ship 73' bridges land on posture correctly.** 4 of 12 articles light up on Arion (source controls have satisfied MUSTs); 8 empty (honest signal — source controls NC).

**One follow-on gap** — `intake_trace_log` persistence for contract counters. Small schema arc.

Not fixing that today — the user asked for a dogfood, not a schema PR. Noted as Ship 74' candidate.
