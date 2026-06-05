"""Generate workbook intake YAML scaffolds for the Tier 3 register sweep.

For each curated EvidenceRequirement with evidence_type='register' (and the
register-variant types: asset_register, contact_register, lawful_basis_
register, records_of_processing, data_flow_inventory), produce a single-
pass YAML that:

- Derives sheet_name_fingerprints from the leaf title
- Binds all MUSTs to fingerprint-tokens derived from item id suffix +
  item text keywords
- Uses freshness_days from the leaf if present and the leaf has a
  date-shaped MUST
- Marks the first 2 most-fundamental MUSTs as required_columns, rest
  as optional_columns with coverage:partial where the column ↔ MUST
  mapping is interpretive

Output: db/workbook_mappings/<slug>.yaml. Skips leaves already covered by
an existing YAML.

The generator is intentionally conservative — produces plausible
scaffolds that validate, match the sheet name well, and gracefully
degrade when a tenant sheet's columns don't perfectly fit. Per-leaf
manual tuning can refine specific cases later.
"""

import os, re, sys
sys.path.insert(0, "/data/arioncomply")
from pathlib import Path
from enrichment.documents.document_requirements import (
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
)

REGISTER_ETS = {
    'register', 'asset_register', 'contact_register', 'lawful_basis_register',
    'records_of_processing', 'data_flow_inventory',
}

OUT_DIR = Path("/data/arioncomply/db/workbook_mappings")

# Track existing YAMLs to skip already-covered leaves
EXISTING_TARGETS: set[str] = set()
import yaml as _yaml
for f in OUT_DIR.glob("*.yaml"):
    try:
        data = _yaml.safe_load(f.read_text())
        for p in (data.get("passes") or []):
            EXISTING_TARGETS.add(p.get("target_evidence_requirement", ""))
    except Exception:
        pass

# Build the leaf list
all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [er for s in ALL_DERIVED_SPECS for er in s.direct_evidence]
register_leaves = [er for er in all_ers if er.evidence_type in REGISTER_ETS
                                          and er.id not in EXISTING_TARGETS]

# Sort
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
register_leaves.sort(key=lambda er: (std_key(er.standard_id), ctrl_key(er.control_ref), er.id))


_STOP = {'per','row','record','captured','exists','named','flagged','linked','each','of','the','and',
         'a','to','for','with','in','on','at','every','any','all','one','two','three','must','should',
         'also','no','not','if','where','when','that','this','from','by','as','is','are','was','were',
         'an','it','its','their','our','your','my','be','been','being','have','has','had','do','does','did'}

def words_from(text: str) -> list[str]:
    """Lowercase + alphanumeric tokens minus stopwords + short tokens."""
    return [w for w in re.findall(r'[a-z]+', text.lower())
            if len(w) >= 3 and w not in _STOP]

def slug(s: str) -> str:
    """Filename-safe slug from a title."""
    s = re.sub(r'[^a-zA-Z0-9_]+', '_', s).strip('_').lower()
    return s

def fingerprint_for_item(item) -> list[str]:
    """Derive a 1-3 token fingerprint for a checklist item from its id suffix
    + text keywords. Prefer concrete tokens over generic ones."""
    # Suffix tokens — strip common prefix
    suf = item.id.rsplit(':', 1)[-1]
    suf_tokens = [t for t in suf.split('_')
                  if t and t not in {'reg','rec','rev','dec','disp','imp','act','off','disc','rea','rc',
                                     'eol','exit','chg','app','rea','pgm','soa','rtp','dev','dfi',
                                     'default','log','digit','flag'}]
    # If suffix gives 1-2 good tokens, prefer them
    if 1 <= len(suf_tokens) <= 3:
        return suf_tokens
    # Otherwise fall back to text keywords (first 2)
    text_words = words_from(item.text)[:2]
    if text_words:
        return text_words
    # Last resort: use the suffix as a single token
    return [suf[:20]]

def is_date_item(item) -> bool:
    suf = item.id.rsplit(':', 1)[-1]
    if 'date' in suf or 'time' in suf or 'verified' in suf:
        return True
    if re.search(r'\b(date|time|verified|last|next)\b', item.text.lower()):
        return True
    return False

def is_owner_item(item) -> bool:
    suf = item.id.rsplit(':', 1)[-1]
    return any(t in suf for t in ('owner','authoriser','authorizer','responsible','approver'))

def sheet_fingerprints(er) -> list[list[str]]:
    """Derive sheet fingerprints from the leaf title.

    Example: 'Information Security Risk Register' → [[risk, register],
                                                     [information, security, register]]
    """
    title_words = [w for w in words_from(er.title)]
    out = []
    # Primary: drop generic kind-word and use 2-token combo with the
    # most-specific preceding tokens. Never emit a single-token generic
    # fingerprint ([register] / [log] / [inventory]) — every register-
    # named sheet would then match every register YAML.
    for kind in ('register', 'log', 'inventory', 'matrix', 'record', 'scheme'):
        if kind in title_words:
            idx = title_words.index(kind)
            if idx >= 2:
                # Three-token fingerprint for higher specificity
                out.append([title_words[idx-2], title_words[idx-1], kind])
            if idx >= 1:
                out.append([title_words[idx-1], kind])
            break
    # Secondary: first two-three meaningful tokens of the title
    if len(title_words) >= 3:
        out.append(title_words[:3])
    if len(title_words) >= 2:
        out.append(title_words[:2])
    # Dedupe while preserving order
    seen = set()
    deduped = []
    for fp in out:
        t = tuple(fp)
        if t not in seen:
            seen.add(t)
            deduped.append(fp)
    # Always need at least one fingerprint — fall back to first 2 title words
    return deduped or [title_words[:2] or ['untitled']]

def yaml_quote_token(t: str) -> str:
    """Quote tokens that look numeric or start with digit (YAML int trap)."""
    if t and t[0].isdigit():
        return f'"{t}"'
    return t

def render(er) -> str:
    """Render a single-pass YAML for one register leaf."""
    # Build mapping_id
    std_part = er.standard_id.replace(':', '_').replace('/', '_')
    ctrl_part = er.control_ref.replace('.', '_').replace(' ', '_')
    leaf_suf = er.id.rsplit(':', 1)[-1]
    mapping_id = f"workbook.{std_part}.{ctrl_part}.{leaf_suf}"
    # Filename
    fname = slug(f"{std_part}_{ctrl_part}_{leaf_suf}") + ".yaml"

    # Sheet fingerprints
    fps = sheet_fingerprints(er)
    fps_yaml = ''.join(
        f"  - tokens: [{', '.join(yaml_quote_token(t) for t in fp)}]\n" for fp in fps
    )

    # Identify a date-shaped MUST for freshness; fall back to first MUST
    date_must = next((it for it in er.must_contain if is_date_item(it)), None)
    owner_must = next((it for it in er.must_contain if is_owner_item(it)), None)
    musts = list(er.must_contain)
    # Place identifier-like MUSTs first
    musts.sort(key=lambda it: 0 if any(t in it.id.rsplit(':',1)[-1] for t in ('id','ref','identifier')) else 1)
    required = musts[:2]
    optional = musts[2:]

    # Freshness block (only if leaf has freshness_days AND a date-shaped MUST)
    freshness_block = ""
    if er.freshness_days and date_must:
        date_fp = fingerprint_for_item(date_must)
        freshness_block = (
            "    freshness:\n"
            f"      column_fingerprint: [{', '.join(yaml_quote_token(t) for t in date_fp)}]\n"
            f"      alternative_fingerprints:\n"
            f"        - [date]\n"
            f"      days: {er.freshness_days}\n"
        )

    # Build required + optional blocks
    def render_col(it, is_required: bool) -> str:
        fp = fingerprint_for_item(it)
        toks = ', '.join(yaml_quote_token(t) for t in fp)
        s  = f"      - fingerprint: [{toks}]\n"
        s += f"        binds_to: \"{it.id}\"\n"
        if not is_required:
            s += "        coverage: partial\n"
        return s

    required_block = "".join(render_col(it, True) for it in required)
    optional_block = "".join(render_col(it, False) for it in optional)

    pass_name = leaf_suf
    target_ctrl = f'"{er.control_ref}"'

    out  = f"# Generated by scripts/generate_register_yamls.py\n"
    out += f"# Tier 3 register sweep — bulk-generated scaffold. Per-leaf tuning may refine\n"
    out += f"# sheet fingerprints and column bindings as real tenant data lands.\n\n"
    out += f"schema_version: 1\n"
    out += f"mapping_id: {mapping_id}\n\n"
    out += f"sheet_name_fingerprints:\n{fps_yaml}\n"
    out += f"header_row_hints: [1, 2]\n"
    out += f"min_data_rows: 1\n\n"
    out += f"passes:\n\n"
    out += f"  - pass_name: {pass_name}\n"
    out += f"    target_control: {target_ctrl}\n"
    out += f"    target_evidence_requirement: \"{er.id}\"\n"
    out += f"    target_evidence_type: {er.evidence_type}\n"
    out += freshness_block
    out += f"    required_columns:\n{required_block}"
    if optional_block:
        out += f"    optional_columns:\n{optional_block}"
    out += f"\nconfidence_weights:\n"
    out += f"  sheet_name: 0.5\n"
    out += f"  required_columns: 0.4\n"
    out += f"  row_count: 0.1\n"

    return fname, out

# Generate
generated = 0
skipped_collision = 0
fname_seen = set()
for er in register_leaves:
    fname, content = render(er)
    if fname in fname_seen:
        skipped_collision += 1
        # Append suffix
        base = fname[:-5]
        for i in range(2, 99):
            cand = f"{base}_{i}.yaml"
            if cand not in fname_seen:
                fname = cand
                break
    fname_seen.add(fname)
    path = OUT_DIR / fname
    if path.exists():
        skipped_collision += 1
        continue
    path.write_text(content)
    generated += 1

print(f"Total register leaves (excluding already-covered): {len(register_leaves)}")
print(f"Generated YAMLs: {generated}")
print(f"Skipped (existing file): {skipped_collision}")
