"""Generate workbook-style doc-mapping YAML scaffolds for the curated
policy / procedure / plan / template doc-shaped leaves.

Doc analog of scripts/generate_register_yamls.py — same per-leaf
approach, same tokenizer, same abbreviation strategy. Produces one
YAML per curated EvidenceRequirement whose evidence_type is doc-shaped
AND that isn't already covered by an existing hand-authored mapping.

Per-leaf scope (NOT umbrella): a tenant who uploads e.g. "Identity
Lifecycle Management Procedure.docx" as its own file will match the
generator-produced identity_management_procedure.yaml. The hand-
authored access_control_policy.yaml stays in place for tenants
who upload one umbrella "Access Control Policy.docx" — both YAML
shapes coexist; multiple proposals on one upload are union'd in the
discovery layer.

Idempotent — won't overwrite existing files. Validate the output with
scripts/validate_doc_mappings.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import yaml as _yaml  # noqa: E402
from enrichment.documents.document_requirements import (  # noqa: E402
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
)

# Doc-shaped evidence types the generator covers. Sheet-shaped types
# (register, log, record family) are handled by generate_register_yamls.
DOC_ETS = {
    "policy", "procedure", "plan", "scope_note", "scope_statement",
    "management_directive", "privacy_notice", "training_programme",
    "agreement_template", "audit_programme", "charter",
    "rectification_procedure", "erasure_procedure",
    "data_processing_agreement", "designation_document",
    "intake_process", "process_map", "communication_record",
    "communication_evidence", "configuration_baseline",
    "audit_report", "approval",
    "risk_assessment", "risk_treatment_plan",
    "breach_notification", "dsar_response", "arrangement",
}

# Ship 9'.c (2026-07-20): review_record leaves whose id-suffix
# matches one of these patterns are doc-shaped annual/periodic review
# reports (as opposed to per-event review records). Tenants upload
# them under identifiable filenames like "PIA Program Review 2026.docx"
# — the doc_mapping catches those filenames.
#
# Not lifted into DOC_ETS because review_record is a broad type: 214
# leaves total, only ~65 are annual/periodic doc-shaped. The rest are
# per-event log entries.
_REVIEW_ID_SUFFIXES = (
    "program_review", "periodic_review", "annual_review",
)


def _is_review_doc(er) -> bool:
    """True when the leaf represents an annual/periodic review REPORT
    (a doc-shaped artefact), not a per-event review record."""
    if er.evidence_type != "review_record":
        return False
    suffix = er.id.rsplit(":", 1)[-1]
    return any(suffix.endswith(s) for s in _REVIEW_ID_SUFFIXES)

OUT_DIR = _ROOT / "db" / "doc_mappings"

# Existing target leaves (skip these — already authored)
EXISTING_TARGETS: set[str] = set()
for f in OUT_DIR.glob("*.yaml"):
    try:
        data = _yaml.safe_load(f.read_text()) or {}
        for t in (data.get("target_leaves") or []):
            if t.get("leaf_id"):
                EXISTING_TARGETS.add(t["leaf_id"])
    except Exception:
        pass


# ─── Tokenization helpers (mirror workbook/register generator) ─────────────────
_STOP = {
    "per","row","captured","exists","named","flagged","linked","each","of","the","and",
    "a","to","for","with","in","on","at","every","any","all","one","two","three","must","should",
    "also","no","not","if","where","when","that","this","from","by","as","is","are","was","were",
    "an","it","its","their","our","your","my","be","been","being","have","has","had","do","does","did",
}
def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", (text or "").lower())
            if len(w) >= 3 and w not in _STOP]

def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", s).strip("_").lower()

def _yaml_quote(t: str) -> str:
    if t and t[0].isdigit():
        return f'"{t}"'
    return t


# ─── Filename fingerprints (mirror sheet_fingerprints for docs) ────────────────
# Kind-words for doc shapes. Same trick as workbook generator: the
# tokenizer strips off the kind-word, then we emit (qualifier, kind)
# and (qualifier-2, qualifier-1, kind) pairings to bias for specificity.
KINDS = ("policy", "procedure", "plan", "template", "directive",
         "notice", "programme", "scheme", "charter", "agreement",
         "report", "record", "baseline")

# Lightweight abbreviation pairs that real tenant filenames use that
# the tokenizer's stemmer doesn't auto-normalise.
ABBREV = {
    "policy":      "pol",
    "procedure":   "proc",
    "information": "info",
    "management":  "mgmt",
    "compliance":  "compl",
}


def _emit_variants(out: list[list[str]], fp: list[str]) -> None:
    """Emit all 2^N variants of full+abbreviated tokens for a fingerprint."""
    variants: list[list[str]] = [[]]
    for t in fp:
        forms = [t]
        if t in ABBREV and ABBREV[t] != t:
            forms.append(ABBREV[t])
        new = []
        for v in variants:
            for f in forms:
                new.append(v + [f])
                if len(new) >= 16:
                    break
            if len(new) >= 16:
                break
        variants = new
    for v in variants:
        out.append(v)


def filename_fingerprints(er) -> list[list[str]]:
    """Derive filename fingerprints from leaf title.

    Examples:
      "Access Control Policy"       → [[access, control, policy]] + abbrev
      "Identity Lifecycle Management Procedure" →
        [[identity, lifecycle, management, procedure], [lifecycle, management, procedure]]
    """
    title_words = _words(er.title)
    # Drop "ISMS" / "Information" / "Security" prefixes — same logic as
    # register generator. Tenant filenames often omit these.
    no_isms = [w for w in title_words if w != "isms"]
    no_iso  = [w for w in title_words if w not in {"isms", "information", "security"}]

    out: list[list[str]] = []
    for source in (title_words, no_isms, no_iso):
        for kind in KINDS:
            if kind in source:
                idx = source.index(kind)
                if idx >= 2:
                    _emit_variants(out, [source[idx-2], source[idx-1], kind])
                elif idx >= 1:
                    _emit_variants(out, [source[idx-1], kind])
                break

    # Secondary: first 2-3 meaningful tokens of the no_iso title (info+
    # security stripped). Using no_iso instead of no_isms is critical —
    # otherwise leaves starting with "Information Security X Procedure"
    # emit a [information, security] 2-token fingerprint that cross-
    # matches any "Information Security <Anything>.docx" filename,
    # exploding false-positive proposals on common doc names.
    #
    # Skip pure-generic fallbacks too: a 2-token fingerprint consisting
    # ONLY of {information, security, data, isms, info, sec} tokens is
    # blacklisted regardless of source list.
    GENERIC = {"information", "security", "data", "isms", "info", "sec"}
    def _emit_safe(fp: list[str]) -> None:
        if len(fp) < 2:
            return
        if all(t in GENERIC for t in fp):
            return
        _emit_variants(out, fp)
    if len(no_iso) >= 3:
        _emit_safe(no_iso[:3])
    if len(no_iso) >= 2:
        _emit_safe(no_iso[:2])

    # Dedupe preserving order
    seen = set()
    deduped: list[list[str]] = []
    for fp in out:
        if not fp:
            continue
        t = tuple(fp)
        if t not in seen:
            seen.add(t)
            deduped.append(fp)
    return deduped or [_words(er.title)[:2] or ["untitled"]]


# ─── Render ─────────────────────────────────────────────────────────────────────
def render(er) -> tuple[str, str]:
    std_part  = er.standard_id.replace(":", "_").replace("/", "_")
    ctrl_part = er.control_ref.replace(".", "_").replace(" ", "_")
    leaf_suf  = er.id.rsplit(":", 1)[-1]
    mapping_id = f"doc.{std_part}.{ctrl_part}.{leaf_suf}"
    fname = _slug(f"{std_part}_{ctrl_part}_{leaf_suf}") + ".yaml"

    fps = filename_fingerprints(er)
    fps_yaml = "".join(
        f"  - tokens: [{', '.join(_yaml_quote(t) for t in fp)}]\n" for fp in fps
    )

    out  = f"# Generated by scripts/generate_doc_mappings.py\n"
    out += f"# Per-leaf scaffold — covers the case where a tenant uploads a dedicated\n"
    out += f"# document for this specific leaf. Hand-authored umbrella YAMLs (e.g.\n"
    out += f"# access_control_policy.yaml covering A.5.15-18) coexist; both can match\n"
    out += f"# the same upload, and the discovery layer unions their target_leaves.\n\n"
    out += f"schema_version: 1\n"
    out += f"mapping_id: {mapping_id}\n\n"
    out += f"filename_fingerprints:\n{fps_yaml}\n"
    out += f"target_leaves:\n"
    out += f"  - leaf_id: \"{er.id}\"\n"
    out += f"    control_ref: \"{er.control_ref}\"\n"
    out += f"    role: {er.evidence_type}\n\n"
    out += f"confidence_weights:\n"
    out += f"  filename: 0.6\n"
    out += f"  body: 0.3\n"
    out += f"  explicit_refs: 0.1\n"

    return fname, out


# ─── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [er for s in ALL_DERIVED_SPECS for er in s.direct_evidence]
    candidates = [
        er for er in all_ers
        if (er.evidence_type in DOC_ETS or _is_review_doc(er))
        and er.id not in EXISTING_TARGETS
    ]

    # Stable ordering
    def std_key(s): return (0,s) if s.startswith("ISO") else (1,s) if s.startswith("GDPR") else (2,s)
    def ctrl_key(c):
        parts, cur, cur_is_digit = [], "", None
        for ch in c:
            d = ch.isdigit()
            if cur_is_digit is None or d == cur_is_digit:
                cur += ch
                cur_is_digit = d
            else:
                parts.append((0 if cur_is_digit else 1, int(cur) if cur_is_digit else cur))
                cur, cur_is_digit = ch, d
        if cur:
            parts.append((0 if cur_is_digit else 1, int(cur) if cur_is_digit else cur))
        return parts
    candidates.sort(key=lambda er: (std_key(er.standard_id), ctrl_key(er.control_ref), er.id))

    written = 0
    skipped_exists = 0
    fname_seen: set[str] = set()
    for er in candidates:
        fname, content = render(er)
        if fname in fname_seen:
            base = fname[:-5]
            for i in range(2, 99):
                cand = f"{base}_{i}.yaml"
                if cand not in fname_seen and not (OUT_DIR / cand).exists():
                    fname = cand
                    break
        fname_seen.add(fname)
        path = OUT_DIR / fname
        if path.exists():
            skipped_exists += 1
            continue
        path.write_text(content)
        written += 1

    print(f"Candidate leaves (doc-shaped, not already covered): {len(candidates)}")
    print(f"Generated YAMLs: {written}")
    print(f"Skipped (file already exists): {skipped_exists}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
