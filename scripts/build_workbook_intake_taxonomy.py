"""Build a canonical-sheet-shape taxonomy from the curated sheet-shaped leaves.

Three-tier output:
  1. Confirmed clusters — leaves that share a canonical shape (one YAML
     covers many controls via multi-pass).
  2. Small clusters — evidence_types with 2-10 instances, likely one YAML each.
  3. Unique shapes — singleton leaves with their own column conventions, each
     requiring its own YAML (or deferring to file-upload + LLM extraction).
"""

import os, sys
sys.path.insert(0, "/data/arioncomply")
from collections import defaultdict
from enrichment.documents.document_requirements import (
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
)

SHEET_ET = {
    'register','asset_register','contact_register','lawful_basis_register',
    'records_of_processing','data_flow_inventory',
    'revocation_record','monitoring_record','change_record',
    'approval_record','audit_record','publication_record','test_log',
    'configuration_record','decision_record','discovery_record',
    'responsibility_matrix','segregation_matrix','classification_scheme',
    'risk_assessment_record','risk_treatment_record',
    'statement_of_applicability','risk_assessment','risk_treatment_plan',
    'audit_programme','review_record',
}
DONE = {
    'req:A.5.9:asset_inventory':            ('asset_register.yaml',         'A.5.9'),
    'req:6.1.2:risk_register':              ('risk_register.yaml',          '6.1.2'),
    'req:A.5.18:access_rights_register':    ('access_register_pii.yaml',    'A.5.18'),
    'req:A.5.26:incident_register':         ('incident_log.yaml',           'A.5.26'),
}

ers = list(ALL_EVIDENCE_REQUIREMENTS) + [er for spec in ALL_DERIVED_SPECS for er in spec.direct_evidence]
pending = [er for er in ers if er.evidence_type in SHEET_ET and er.id not in DONE]

# Bucket by evidence_type
by_et = defaultdict(list)
for er in pending:
    by_et[er.evidence_type].append(er)

# Standard ordering for stable output
def std_key(s):
    if s.startswith('ISO'): return (0, s)
    if s.startswith('GDPR'): return (1, s)
    return (2, s)

def ctrl_key(c):
    parts, cur, cur_is_digit = [], '', None
    for ch in c:
        is_digit = ch.isdigit()
        if cur_is_digit is None or is_digit == cur_is_digit:
            cur += ch
            cur_is_digit = is_digit
        else:
            parts.append((0 if cur_is_digit else 1, int(cur) if cur_is_digit else cur))
            cur, cur_is_digit = ch, is_digit
    if cur:
        parts.append((0 if cur_is_digit else 1, int(cur) if cur_is_digit else cur))
    return parts

def sort_ers(lst):
    return sorted(lst, key=lambda e: (std_key(e.standard_id), ctrl_key(e.control_ref), e.id))

out = []
out.append("# Workbook intake canonical sheet shapes\n")
out.append(
    "Taxonomy of curated sheet-shaped leaves. Each entry is a candidate "
    "intake YAML; entries marked CLUSTER cover many controls via multi-pass.\n"
)
out.append(f"**Pending: {len(pending)} leaves** (after the 4 done YAMLs).\n")
out.append("---\n")

# ── Tier 1: confirmed CLUSTER (review_record + revocation_record) ─────────────
out.append("## Tier 1 — Confirmed clusters (one YAML covers many leaves)\n")

# 1.1 — review_record cluster
rrs = sort_ers(by_et.get('review_record', []))
out.append(f"### CLUSTER: `program_review_log`  ({len(rrs)} leaves, one canonical YAML)\n")
out.append(
    "**Canonical column conventions** (from keyword profile, ≥98% of instances):\n"
    "- `review_date` — when the review happened (drives freshness vs `freshness_days`)\n"
    "- `planned_interval` — cadence the review_record claims to track (90/180/365 days)\n"
    "- `reviewer_identity` — named reviewer (not generic role)\n"
    "- `scope` — what was reviewed (the linked program / register / control area)\n"
    "- `findings` / `decisions` — outcome of the review\n\n"
    "**Cadence variation**: cadence_days is encoded on the leaf's `freshness_days` "
    "(90 for high-volume identity-style reviews, 180 for compliance/supplier, 365 for stable "
    "doctrine areas). The YAML's freshness pass uses `column_fingerprint=review_date` and "
    "the engine cross-references each leaf's curated freshness_days.\n\n"
    "**Naming patterns observed**: `<Domain> Program Review Log` / `<Domain> Annual Review Log`. "
    "Fingerprint tokens: `[program, review]`, `[annual, review]`, `[scope, review]`.\n\n"
    "**Sample leaves** (full list below):\n"
)
for er in rrs[:5]:
    out.append(f"- `{er.id}` — {er.title}\n")
out.append(f"- … ({len(rrs)-5} more, see appendix)\n\n")

# 1.2 — revocation_record cluster
revs = sort_ers(by_et.get('revocation_record', []))
out.append(f"### CLUSTER: `revocation_log`  ({len(revs)} leaves, one canonical YAML — possibly 2)\n")
out.append(
    "**Canonical column conventions** (≥60% of instances):\n"
    "- `record_identifier` — unique id per record\n"
    "- `linked_register` — back-pointer to the parent register (e.g. identity_register → "
    "revocation_record links via identity_id)\n"
    "- `revocation_date` — when the revocation/closure happened\n"
    "- `authoriser` — named role/person\n"
    "- `trigger_type` — what caused the revocation (leaver, role change, exit, closure)\n"
    "- `outcome` — risk-accepted vs returned vs lost\n\n"
    "**Variation**: some leaves are 'closure records' (A.5.26 incident-closure) with extra fields "
    "like sla_met, root_cause; others are 'asset return' records (A.5.11). May warrant two YAMLs.\n\n"
    "**Member leaves**:\n"
)
for er in revs:
    out.append(f"- `{er.id}` — {er.title}\n")
out.append("\n")

# ── Tier 2: small clusters (2-10 instances) ───────────────────────────────────
out.append("## Tier 2 — Small clusters (2-10 leaves, one YAML each)\n")
for et in sorted(by_et, key=lambda e: -len(by_et[e])):
    if et in ('review_record', 'revocation_record'): continue
    items = sort_ers(by_et[et])
    if not (2 <= len(items) <= 10): continue
    out.append(f"### `{et}`  ({len(items)} leaves)\n")
    for er in items:
        out.append(f"- `{er.id}` — {er.title}\n")
    out.append("\n")

# ── Tier 3: registers (124 — mostly unique shapes, but listed by category) ────
out.append("## Tier 3 — Registers (124 leaves, mostly unique sheet shapes)\n")
out.append(
    "Each register is a distinct real-world artefact with its own column conventions "
    "— **likely one YAML per leaf** rather than a shared canonical shape. "
    "Listed by standard / control for navigation; prioritise via the high-value tier (below).\n\n"
)

# Sub-categorise registers by control prefix area for navigation
regs = sort_ers(by_et.get('register', []))
by_section = defaultdict(list)
for er in regs:
    std = er.standard_id
    ref = er.control_ref
    if std.startswith('ISO27001'):
        if   ref.startswith('A.5.'): section = 'ISO27001 / A.5 (Organisational)'
        elif ref.startswith('A.6.'): section = 'ISO27001 / A.6 (People)'
        elif ref.startswith('A.7.'): section = 'ISO27001 / A.7 (Physical)'
        elif ref.startswith('A.8.'): section = 'ISO27001 / A.8 (Technological)'
        else:                        section = 'ISO27001 / ISMS clauses'
    elif std.startswith('GDPR'):
        section = 'GDPR'
    else:
        section = std
    by_section[section].append(er)

for section in sorted(by_section, key=lambda s: (0 if s.startswith('ISO27001 / A.') else
                                                 1 if s.startswith('ISO27001 / ISMS') else
                                                 2 if s.startswith('GDPR') else 3, s)):
    items = by_section[section]
    out.append(f"### {section}  ({len(items)} register YAMLs)\n")
    for er in items:
        # Build a compact MUST signature: just count + a few keyword hints
        n_must = len(er.must_contain)
        n_should = len(er.should_contain)
        out.append(f"- `{er.id}` ({n_must} MUSTs, {n_should} SHOULDs) — {er.title}\n")
    out.append("\n")

# ── Tier 4: one-off shapes (singletons of non-register evidence_types) ────────
out.append("## Tier 4 — One-off shapes (distinct evidence_types, 1 leaf each)\n")
out.append(
    "Each is a unique sheet shape — author one bespoke YAML per leaf. "
    "Most are high-value (RoPA, SoA, audit programme, classification scheme).\n\n"
)
for et in sorted(by_et, key=lambda e: e):
    if et in ('review_record', 'revocation_record', 'register'): continue
    items = sort_ers(by_et[et])
    if len(items) > 10: continue  # already covered in Tier 2
    if len(items) < 2:
        for er in items:
            out.append(f"- **{et}** — `{er.id}` — {er.title}  ({len(er.must_contain)} MUSTs)\n")

out.append("\n")

# ── Final priority recommendation ─────────────────────────────────────────────
out.append("## Suggested authoring sequence\n")
out.append(
    "1. **Batch 1 (high leverage)** — the `program_review_log` cluster YAML "
    "(closes 163 leaves at once).\n"
    "2. **Batch 2 (high value)** — Tier 4 one-offs aligned to ISMS clauses 9 + 10 "
    "(audit_programme, statement_of_applicability, risk_treatment_plan, RoPA, etc.) "
    "and GDPR cross-framework artefacts (data_flow_inventory, lawful_basis_register).\n"
    "3. **Batch 3 (close the lifecycle-end family)** — revocation_record cluster (22 leaves) "
    "+ change_record (3) + monitoring_record (6) + small Tier 2 entries.\n"
    "4. **Batches 4-N (per-section register sweep)** — iterate registers section by section "
    "(A.5, A.6, A.7, A.8, ISMS, GDPR). Each batch ~10-20 register YAMLs.\n"
)

with open('/data/arioncomply/docs/workbook_intake_canonical_shapes.md', 'w') as f:
    f.write("".join(out))

print(f"Wrote taxonomy: {len(pending)} pending leaves classified")
print(f"  Tier 1 (review_record cluster):  {len(by_et.get('review_record', []))} leaves → 1 YAML")
print(f"  Tier 1 (revocation_record cluster): {len(by_et.get('revocation_record', []))} leaves → 1-2 YAMLs")
small = sum(len(v) for k,v in by_et.items() if k not in ('review_record','revocation_record','register') and 2 <= len(v) <= 10)
print(f"  Tier 2 (small clusters):  {small} leaves → ~{sum(1 for k,v in by_et.items() if k not in ('review_record','revocation_record','register') and 2 <= len(v) <= 10)} YAMLs")
print(f"  Tier 3 (registers):  {len(by_et.get('register', []))} leaves → ~{len(by_et.get('register', []))} YAMLs (mostly unique)")
single = sum(1 for k,v in by_et.items() if k not in ('review_record','revocation_record','register') and len(v) == 1)
print(f"  Tier 4 (one-off shapes):  {single} leaves → {single} YAMLs")
total_yamls = 1 + 2 + sum(1 for k,v in by_et.items() if k not in ('review_record','revocation_record','register') and 2 <= len(v) <= 10) + len(by_et.get('register', [])) + single
print(f"  Total YAMLs estimated:    ~{total_yamls}  (from {len(pending)} pending leaves)")
