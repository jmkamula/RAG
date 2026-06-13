"""Leaf-driven scan: back-bind existing approved findings to specific
MUSTs they semantically satisfy but weren't tagged with at extraction time.

Pilot scope (2026-06-12): A.6.3 training_completion_register. See
[[backlog]] item; targets the false-negative case where evidence
exists in the workbook/doc corpus but the original mapping routed
it to a different leaf or left checklist_item_id NULL.

Constraints (from the false-positive risk discussion earlier this
session):
  - Only scans findings ALREADY attributed to the parent control —
    never cross-control. A "Score" column on a risk register can't
    accidentally satisfy A.6.3's reg_score.
  - Only proposes for MUSTs that are currently UNMET on this tenant
    (no duplicate bindings).
  - Writes `inference_source='leaf_scan'`, `confidence='medium'`,
    `status='partial'`, `review_status='pending'`. HITL approves.
  - Never auto-flips posture. Engine handles that downstream after
    the tenant accepts.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import yaml

logger = logging.getLogger(__name__)


_CATALOG_DIR = Path(__file__).resolve().parents[2] / "db" / "must_fingerprints"


@dataclass
class MustFingerprint:
    must_id:           str
    description:       str
    excerpt_keywords:  list[list[str]]   # list of token sets; ANY set fully present = match


@dataclass
class LeafCatalog:
    target_evidence_requirement: str
    target_control:               str
    target_standard:              str
    fingerprints:                 list[MustFingerprint]


@dataclass
class ScanProposal:
    """One proposed back-binding — a new finding row to write."""
    source_finding_id: str   # the existing finding whose excerpt matched
    must_id:           str
    control_ref:       str
    standard_id:       str
    document_id:       str
    excerpt:           str
    confidence:        str = "medium"
    # 'present' so the engine Phase-2 path counts the binding as
    # items_recognised. A back-binding refers to the same evidence
    # the source finding describes; if the source proves the column
    # exists with real data, the binding to the new MUST is just as
    # present. Confidence stays 'medium' to reflect the indirection.
    status:            str = "present"
    inference_source:  str = "leaf_scan"


def load_catalogs(target_leaf_id: Optional[str] = None) -> list[LeafCatalog]:
    """Load all leaf catalogs from db/must_fingerprints/. If
    target_leaf_id is given, returns only that leaf's catalog.
    """
    out: list[LeafCatalog] = []
    if not _CATALOG_DIR.exists():
        return out
    for path in sorted(_CATALOG_DIR.glob("*.yaml")):
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning("leaf_scan: failed to load %s: %s", path, e)
            continue
        if data.get("schema_version") != 1:
            continue
        leaf_id = data.get("target_evidence_requirement")
        if not leaf_id:
            continue
        if target_leaf_id and leaf_id != target_leaf_id:
            continue
        fps = []
        for entry in data.get("must_fingerprints", []) or []:
            must_id = entry.get("must_id")
            if not must_id:
                continue
            fps.append(MustFingerprint(
                must_id          = must_id,
                description      = entry.get("description", ""),
                excerpt_keywords = [list(s) for s in entry.get("excerpt_keywords", []) or []],
            ))
        out.append(LeafCatalog(
            target_evidence_requirement = leaf_id,
            target_control              = data.get("target_control", ""),
            target_standard             = data.get("target_standard", "ISO27001:2022"),
            fingerprints                = fps,
        ))
    return out


_NORM_RE = re.compile(r"[^\w\s]", re.UNICODE)


def _norm(text) -> str:
    """Lowercase + strip punctuation + collapse whitespace. Tolerates
    non-string inputs (YAML can parse bare digits as ints) by stringifying
    first."""
    t = str(text or "").lower()
    t = _NORM_RE.sub(" ", t)
    return " ".join(t.split())


def _excerpt_matches(excerpt: str, keyword_sets: list[list[str]]) -> bool:
    """True when at least one keyword set is fully present in the
    normalised excerpt (all tokens found as substrings)."""
    norm = _norm(excerpt)
    if not norm:
        return False
    for kw_set in keyword_sets:
        if all(_norm(tok) in norm for tok in kw_set):
            return True
    return False


def scan(
    pg_conn,
    tenant_id:      str,
    target_leaf_id: Optional[str] = None,
) -> list[ScanProposal]:
    """Run the leaf-driven scan; return list of proposals.

    For each loaded leaf catalog:
      1. Find currently-unmet MUSTs (no approved active finding bound to
         that checklist_item_id on this tenant)
      2. Pull all approved active findings on the same control_ref
      3. For each (unmet MUST × candidate finding), check if the
         finding's excerpt matches the MUST's fingerprint keyword sets
      4. If yes AND the same finding isn't already bound to this MUST,
         add a ScanProposal
    """
    catalogs = load_catalogs(target_leaf_id)
    if not catalogs:
        return []

    proposals: list[ScanProposal] = []
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))

        for cat in catalogs:
            # Currently-met MUSTs on this leaf for this tenant
            cur.execute(
                """
                SELECT DISTINCT checklist_item_id
                  FROM document_findings
                 WHERE tenant_id     = %s::uuid
                   AND control_ref   = %s
                   AND standard_id   = %s
                   AND is_active     = TRUE
                   AND review_status = 'approved'
                   AND status        IN ('present', 'partial')
                   AND checklist_item_id IS NOT NULL
                """,
                (tenant_id, cat.target_control, cat.target_standard),
            )
            already_met = {row[0] for row in cur.fetchall()}

            unmet = [fp for fp in cat.fingerprints if fp.must_id not in already_met]
            if not unmet:
                continue

            # Candidate findings on the same control
            cur.execute(
                """
                SELECT id, document_id, excerpt, checklist_item_id
                  FROM document_findings
                 WHERE tenant_id     = %s::uuid
                   AND control_ref   = %s
                   AND standard_id   = %s
                   AND is_active     = TRUE
                   AND review_status = 'approved'
                """,
                (tenant_id, cat.target_control, cat.target_standard),
            )
            candidates = cur.fetchall()

            for fid, doc_id, excerpt, bound_must in candidates:
                if not excerpt:
                    continue
                for fp in unmet:
                    if fp.must_id == bound_must:
                        # Already bound to this MUST on another row;
                        # skip (we already counted it as "met").
                        continue
                    if _excerpt_matches(excerpt, fp.excerpt_keywords):
                        proposals.append(ScanProposal(
                            source_finding_id = str(fid),
                            must_id           = fp.must_id,
                            control_ref       = cat.target_control,
                            standard_id       = cat.target_standard,
                            document_id       = str(doc_id),
                            excerpt           = excerpt,
                        ))

    # Deduplicate (must_id, source_finding_id) pairs — same source
    # shouldn't yield multiple proposals for the same MUST.
    seen: set[tuple[str, str]] = set()
    unique: list[ScanProposal] = []
    for p in proposals:
        key = (p.must_id, p.source_finding_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def persist(
    pg_conn,
    tenant_id: str,
    proposals: list[ScanProposal],
) -> int:
    """Write proposals as new document_findings rows (status=pending,
    inference_source=leaf_scan). Returns rows written.
    """
    if not proposals:
        return 0
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        for p in proposals:
            # Prepend a marker so tenant sees this is a leaf-scan back-bind,
            # not a fresh extraction.
            tagged_excerpt = f"[leaf-scan back-bind from finding {p.source_finding_id[:8]}] " + (p.excerpt or "")[:480]
            cur.execute(
                """
                INSERT INTO document_findings (
                    tenant_id, document_id,
                    control_ref, standard_id, checklist_item_id,
                    status, confidence, excerpt,
                    inference_source,
                    is_active, retention_class
                ) VALUES (
                    %s::uuid, %s::uuid,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s,
                    TRUE, 'compliance'
                )
                """,
                (
                    tenant_id, p.document_id,
                    p.control_ref, p.standard_id, p.must_id,
                    p.status, p.confidence, tagged_excerpt,
                    p.inference_source,
                ),
            )
    pg_conn.commit()
    return len(proposals)
