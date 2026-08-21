"""Ship 92'.a + Ship 92'.b — cite lifecycle close on document upload.

TWO paths run in sequence:

  Ship 92'.a — best-effort URL basename auto-verify
    (works only when cite URLs are clean file paths; misses
     SharePoint / Google Drive / OneDrive / Confluence / Notion)

  Ship 92'.b — MUST-overlap system attestation (SCALE-INVARIANT)
    For each active cite whose MUST has a `status='present'`
    finding from the uploaded doc, INSERT a
    `cite_attestation_prompt` row (status='pending'). Tenant
    reviews via dashboard drill-in and one-clicks Confirm /
    Dismiss. Confirm writes `external_evidence_verification_log`;
    tenant OWNS the match decision.

Ship 92'.a auto-verifies where URLs are clean paths (rare in real
workbooks). Ship 92'.b creates prompts where MUSTs overlap
(scale-invariant across every URL shape). Both hook into
`doc_pipeline` Stage 4.8.

Env gates:
  USE_CITE_AUTO_VERIFY ∈ {"0", "1"} — default "1" (Ship 92'.a auto-verify)
  USE_CITE_ATTESTATION ∈ {"0", "1"} — default "1" (Ship 92'.b prompts)

Best-effort — errors are logged and swallowed; never blocks upload.
"""
from __future__ import annotations

import logging
import os
from typing import Any
from urllib.parse import urlparse, unquote
from uuid import UUID

logger = logging.getLogger(__name__)


def _url_basename(url: str) -> str | None:
    """Extract the last path segment of a URL / file link (case-preserved).

    Returns None if no extractable filename. Handles:
      https://.../file.docx?ver=3               → 'file.docx'
      https://.../file.docx#page=2              → 'file.docx'
      \\\\fileshare\\file.docx                  → 'file.docx'
      file.docx (bare)                          → 'file.docx'
      https://landing.example.com/site          → None (no extension)
      mailto:foo@bar                            → None
      ''                                        → None
    """
    if not url:
        return None
    if url.lower().startswith("mailto:"):
        return None
    try:
        parsed = urlparse(url)
        path = parsed.path or url
    except Exception:
        path = url
    path = path.replace("\\", "/").split("?", 1)[0].split("#", 1)[0]
    if not path:
        return None
    last = path.rstrip("/").split("/")[-1]
    if not last:
        return None
    try:
        last = unquote(last)
    except Exception:
        pass
    if "." not in last:
        return None
    return last


def resolve_cites_on_document_upload(
    pg,
    tenant_id:          str | UUID,
    client_document_id: str | UUID,
    user_id:            str | UUID | None,
) -> dict:
    """Ship 92'.a.iii entry point — called after successful doc upload.

    Args:
      pg:                 open psycopg2 connection
      tenant_id:          tenant UUID
      client_document_id: the freshly-uploaded client_documents.id
      user_id:            uploading user's UUID (used as verified_by)

    Returns a stats dict:
      {
        "cites_scanned":       int,   # active cites with hyperlink_url
        "url_matches":         int,   # basename matched client_documents
        "must_matches":        int,   # url_matches + linked-doc has present
        "verified":            int,   # verification_log rows written
        "target_document":     str,
        "target_filename":     str,
      }

    Best-effort: on internal error, returns partial stats + logs
    warning. Never raises to caller.
    """
    result: dict[str, Any] = {
        "cites_scanned": 0, "url_matches": 0,
        "must_matches": 0, "verified": 0,
        "target_document": str(client_document_id),
        "target_filename": None,
        "error": None,
    }
    if (os.getenv("USE_CITE_AUTO_VERIFY") or "1") == "0":
        result["error"] = "USE_CITE_AUTO_VERIFY=0"
        return result

    tenant_str = str(tenant_id)
    doc_str    = str(client_document_id)

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            # 1. Get the uploaded document's filename.
            cur.execute(
                """
                SELECT filename FROM client_documents
                 WHERE id = %s::uuid AND tenant_id = %s::uuid
                   AND is_active = TRUE
                 LIMIT 1
                """,
                (doc_str, tenant_str),
            )
            row = cur.fetchone()
            if not row:
                result["error"] = "client_document not found or not active"
                return result
            target_filename = (row[0] or "").strip()
            result["target_filename"] = target_filename
            if not target_filename:
                return result

            # 2. Fetch active cites with a stored hyperlink_url.
            cur.execute(
                """
                SELECT ees.id::text, ees.must_id, ees.leaf_id,
                       ees.system_id::text, ees.hyperlink_url,
                       ees.cadence_days, ees.last_verified_at
                  FROM external_evidence_source ees
                 WHERE ees.tenant_id     = %s::uuid
                   AND ees.is_active     = TRUE
                   AND ees.hyperlink_url IS NOT NULL
                """,
                (tenant_str,),
            )
            cites = cur.fetchall()
            result["cites_scanned"] = len(cites)
            if not cites:
                return result

            target_lower = target_filename.lower()

            for cite_id, must_id, leaf_id, system_id, url, cadence_days, last_verified in cites:
                basename = _url_basename(url or "")
                if not basename:
                    continue
                if basename.lower() != target_lower:
                    continue
                result["url_matches"] += 1

                # 3. Require: uploaded doc has present findings on same MUST.
                cur.execute(
                    """
                    SELECT 1 FROM document_findings
                     WHERE tenant_id         = %s::uuid
                       AND document_id       = %s::uuid
                       AND checklist_item_id = %s
                       AND status            = 'present'
                       AND is_active         = TRUE
                     LIMIT 1
                    """,
                    (tenant_str, doc_str, must_id),
                )
                if cur.fetchone() is None:
                    continue
                result["must_matches"] += 1

                # 4. Write verification_log + update cite.
                # verified_by is NOT NULL — use uploading user; if
                # None (rare), fall back to a synthetic sentinel-uuid
                # constant. The upload path always has a user_id in
                # practice; this defence-in-depth handles admin CLI.
                _verified_by = str(user_id) if user_id else "00000000-0000-0000-0000-000000000000"
                cur.execute(
                    """
                    INSERT INTO external_evidence_verification_log (
                        tenant_id, system_id, leaf_id,
                        verified_by, changes_detected,
                        sample_upload_id, note,
                        musts_covered_count
                    ) VALUES (
                        %s::uuid, %s::uuid, %s,
                        %s::uuid, %s,
                        %s::uuid, %s,
                        1
                    )
                    """,
                    (
                        tenant_str, system_id, leaf_id,
                        _verified_by,
                        "auto-matched by URL basename",
                        doc_str,
                        (f"Ship 92'.a auto-verify — cite URL basename "
                         f"'{basename}' matched uploaded document "
                         f"'{target_filename}'; document has present "
                         f"finding on {must_id}"),
                    ),
                )
                # Update the cite row itself.
                cur.execute(
                    """
                    UPDATE external_evidence_source
                       SET last_verified_at = NOW(),
                           next_review_due  = NOW() + make_interval(days => %s),
                           updated_at       = NOW(),
                           updated_by       = %s::uuid
                     WHERE id = %s::uuid
                    """,
                    (cadence_days, _verified_by, cite_id),
                )
                result["verified"] += 1

        pg.commit()
    except Exception as e:
        pg.rollback()
        result["error"] = f"{type(e).__name__}: {e}"
        logger.warning("cite_resolver: resolve_cites failed: %s", e)

    return result


# ── Ship 92'.b — MUST-overlap candidate detection ────────────────────


def create_attestation_prompts_on_document_upload(
    pg,
    tenant_id:          str | UUID,
    client_document_id: str | UUID,
) -> dict:
    """Ship 92'.b.ii — scan for cite/doc MUST overlaps + insert prompts.

    For each active cite in this tenant whose `must_id` has a
    `status='present'` finding from the uploaded document, insert a
    `cite_attestation_prompt` row (status='pending'). Tenant reviews
    on dashboard drill-in and one-clicks Confirm / Dismiss.

    Dedup: UNIQUE(tenant, cite, candidate_doc) WHERE pending — the
    same upload against the same cite doesn't spam prompts.

    Scale-invariant: the signal is MUST overlap, not URL parsing.
    Works across every URL shape (SharePoint, Drive, OneDrive,
    Notion, bare paths, ...).

    Returns:
      {
        "cites_scanned":   int,
        "candidates_found": int,   # MUST overlap
        "prompts_created": int,   # after dedup
        "prompts_existing": int,  # already had pending prompt
      }
    """
    result: dict[str, Any] = {
        "cites_scanned":    0,
        "candidates_found": 0,
        "prompts_created":  0,
        "prompts_existing": 0,
        "error":            None,
    }
    if (os.getenv("USE_CITE_ATTESTATION") or "1") == "0":
        result["error"] = "USE_CITE_ATTESTATION=0"
        return result

    tenant_str = str(tenant_id)
    doc_str    = str(client_document_id)

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            # Find every (cite, must_id) pair where the uploaded doc
            # has a present finding on the same must_id.
            cur.execute(
                """
                SELECT ees.id::text, ees.must_id, ees.leaf_id
                  FROM external_evidence_source ees
                 WHERE ees.tenant_id = %s::uuid
                   AND ees.is_active = TRUE
                   AND EXISTS (
                     SELECT 1 FROM document_findings df
                      WHERE df.tenant_id         = %s::uuid
                        AND df.document_id       = %s::uuid
                        AND df.checklist_item_id = ees.must_id
                        AND df.status            = 'present'
                        AND df.is_active         = TRUE
                   )
                """,
                (tenant_str, tenant_str, doc_str),
            )
            candidates = cur.fetchall()
            result["cites_scanned"] = len(candidates)
            result["candidates_found"] = len(candidates)
            if not candidates:
                return result

            # For control_ref display, map MUST → control_ref via
            # the checklist_item_id shape 'item:CTRL:name' — CTRL is
            # the second segment.
            for cite_id, must_id, leaf_id in candidates:
                control_ref = must_id.split(":", 2)[1] if ":" in must_id else ""

                # ON CONFLICT DO NOTHING — the UNIQUE index catches
                # duplicate pending prompts by construction.
                cur.execute(
                    """
                    INSERT INTO cite_attestation_prompt (
                        tenant_id, cite_id,
                        candidate_document_id,
                        must_id, leaf_id, control_ref,
                        status
                    ) VALUES (
                        %s::uuid, %s::uuid,
                        %s::uuid,
                        %s, %s, %s,
                        'pending'
                    )
                    ON CONFLICT (tenant_id, cite_id, candidate_document_id)
                    WHERE status = 'pending'
                    DO NOTHING
                    RETURNING id::text
                    """,
                    (
                        tenant_str, cite_id, doc_str,
                        must_id, leaf_id, control_ref,
                    ),
                )
                if cur.fetchone() is not None:
                    result["prompts_created"] += 1
                else:
                    result["prompts_existing"] += 1

        pg.commit()
    except Exception as e:
        pg.rollback()
        result["error"] = f"{type(e).__name__}: {e}"
        logger.warning("cite_resolver: create_attestation_prompts failed: %s", e)

    return result


def confirm_attestation(
    pg,
    tenant_id: str | UUID,
    prompt_id: str | UUID,
    user_id:   str | UUID,
) -> dict:
    """Ship 92'.b.iii — tenant one-click confirmation.

    Writes `external_evidence_verification_log` + bumps cite +
    marks prompt as confirmed. Tenant's decision, not URL guess.
    """
    result = {"ok": False, "verification_log_id": None, "error": None}
    tenant_str = str(tenant_id)
    prompt_str = str(prompt_id)
    user_str   = str(user_id)

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            # Fetch prompt + cite context
            cur.execute(
                """
                SELECT cap.cite_id::text, cap.candidate_document_id::text,
                       cap.must_id, cap.leaf_id, cap.status,
                       ees.system_id::text, ees.cadence_days,
                       cd.filename
                  FROM cite_attestation_prompt cap
                  JOIN external_evidence_source ees ON ees.id = cap.cite_id
                  JOIN client_documents cd ON cd.id = cap.candidate_document_id
                 WHERE cap.id = %s::uuid
                   AND cap.tenant_id = %s::uuid
                """,
                (prompt_str, tenant_str),
            )
            row = cur.fetchone()
            if not row:
                result["error"] = "prompt not found"
                return result
            (cite_id, doc_id, must_id, leaf_id, status,
             system_id, cadence_days, doc_filename) = row
            if status != "pending":
                result["error"] = f"prompt is {status!r}, not pending"
                return result

            # Write verification_log
            cur.execute(
                """
                INSERT INTO external_evidence_verification_log (
                    tenant_id, system_id, leaf_id,
                    verified_by, changes_detected,
                    sample_upload_id, note,
                    musts_covered_count
                ) VALUES (
                    %s::uuid, %s::uuid, %s,
                    %s::uuid, %s,
                    %s::uuid, %s,
                    1
                )
                RETURNING id::text
                """,
                (
                    tenant_str, system_id, leaf_id,
                    user_str,
                    "tenant-confirmed attestation",
                    doc_id,
                    (f"Ship 92'.b tenant attestation — confirmed that "
                     f"uploaded document '{doc_filename}' is the target "
                     f"of cite on {must_id}"),
                ),
            )
            log_id = cur.fetchone()[0]

            # Bump cite freshness
            cur.execute(
                """
                UPDATE external_evidence_source
                   SET last_verified_at = NOW(),
                       next_review_due  = NOW() + make_interval(days => %s),
                       updated_at       = NOW(),
                       updated_by       = %s::uuid
                 WHERE id = %s::uuid
                """,
                (cadence_days, user_str, cite_id),
            )

            # Mark prompt confirmed
            cur.execute(
                """
                UPDATE cite_attestation_prompt
                   SET status              = 'confirmed',
                       resolved_at         = NOW(),
                       resolved_by         = %s::uuid,
                       verification_log_id = %s::uuid,
                       updated_at          = NOW()
                 WHERE id = %s::uuid
                """,
                (user_str, log_id, prompt_str),
            )

        pg.commit()
        result["ok"] = True
        result["verification_log_id"] = log_id
    except Exception as e:
        pg.rollback()
        result["error"] = f"{type(e).__name__}: {e}"
        logger.warning("cite_resolver: confirm_attestation failed: %s", e)

    return result


def dismiss_attestation(
    pg,
    tenant_id: str | UUID,
    prompt_id: str | UUID,
    user_id:   str | UUID,
    reason:    str = "not the same document",
) -> dict:
    """Tenant dismissal. No verification_log write; audit trail
    preserved via prompt.status='dismissed' + reason."""
    result = {"ok": False, "error": None}
    tenant_str = str(tenant_id)
    prompt_str = str(prompt_id)
    user_str   = str(user_id)
    _reason = (reason or "").strip() or "not the same document"

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            cur.execute(
                """
                UPDATE cite_attestation_prompt
                   SET status           = 'dismissed',
                       resolved_at      = NOW(),
                       resolved_by      = %s::uuid,
                       dismissed_reason = %s,
                       updated_at       = NOW()
                 WHERE id = %s::uuid
                   AND tenant_id = %s::uuid
                   AND status = 'pending'
                RETURNING id::text
                """,
                (user_str, _reason, prompt_str, tenant_str),
            )
            row = cur.fetchone()
            if row is None:
                result["error"] = "prompt not found or not pending"
                return result
        pg.commit()
        result["ok"] = True
    except Exception as e:
        pg.rollback()
        result["error"] = f"{type(e).__name__}: {e}"
        logger.warning("cite_resolver: dismiss_attestation failed: %s", e)

    return result


# ── Ship 92'.d — humanization helpers ────────────────────────────────


def _humanize_cite_url(url: str, display: str | None) -> str:
    """Pick the auditor-friendly display label for a cite URL.

    Prefer the cell's captured display text (openpyxl `Hyperlink.display`).
    Fall back to:
      1. SharePoint `file=` query-param filename (URL-decoded)
      2. URL basename with extension (if clean path)
      3. The host portion (e.g. 'nukib.gov.cz')
      4. '(no display text)' as last resort.
    """
    if display and display.strip():
        return display.strip()
    if not url:
        return "(no link)"
    try:
        parsed = urlparse(url)
        # SharePoint / SaaS `file=` query param
        qs = parsed.query or ""
        for pair in qs.split("&"):
            if pair.lower().startswith("file="):
                try:
                    return unquote(pair.split("=", 1)[1])
                except Exception:
                    pass
        # Clean basename
        path = (parsed.path or "").replace("\\", "/")
        last = path.rstrip("/").split("/")[-1]
        if last and "." in last:
            try:
                return unquote(last)
            except Exception:
                return last
        # Fall back to host
        if parsed.hostname:
            return parsed.hostname
    except Exception:
        pass
    return "(external link)"


def _humanize_must_label(must_id: str) -> str:
    """Slug-to-title on the tail of the MUST id.

    'item:6.1.3:soa_reference' → 'Soa Reference' → 'SoA reference'
    'item:A.5.18:reg_idmgmt_link' → 'Reg Idmgmt Link' → 'Identity management link'
    Kept small + heuristic. Reuses the same discipline as
    rag/posture/advisory._humanize_evidence_type.
    """
    if not must_id or ":" not in must_id:
        return must_id or ""
    tail = must_id.rsplit(":", 1)[-1]
    parts = tail.split("_")
    # Cheap acronym preserves + common expansions
    preserve = {"iso": "ISO", "gdpr": "GDPR", "dpia": "DPIA", "sla": "SLA",
                "kpi": "KPI", "cia": "CIA", "roi": "ROI",
                "soa": "SoA", "roi": "ROI", "sig": "SIG", "isms": "ISMS",
                "id":  "ID", "pii": "PII"}
    expand = {"reg": "", "rev": "review", "rec": "record", "proc": "procedure",
              "off": "offboarding", "idmgmt": "identity management",
              "url": "URL", "ref": "reference"}
    out: list[str] = []
    for p in parts:
        low = p.lower()
        if low in preserve:
            out.append(preserve[low])
        elif low in expand:
            e = expand[low]
            if e:
                out.append(e)
        else:
            out.append(p.replace("-", " "))
    label = " ".join(t for t in out if t).strip()
    if not label:
        return tail.replace("_", " ")
    # Capitalize first letter only
    return label[0].upper() + label[1:] if label else label


def _leaf_label_from_id(leaf_id: str) -> str:
    """Look up leaf title from the curated catalog; fall back to slug."""
    if not leaf_id or ":" not in leaf_id:
        return leaf_id or ""
    try:
        from enrichment.documents import document_requirements as DR
        for r in DR.ALL_EVIDENCE_REQUIREMENTS:
            if r.id == leaf_id and getattr(r, "title", None):
                # Strip trailing " (Annex A.X)" style parenthetical
                import re as _re
                t = _re.sub(r"\s*\((?:Annex\s+)?[A-Z]?\.?[\d.]+\)\s*$", "", r.title).strip()
                return t
        for name in dir(DR):
            obj = getattr(DR, name, None)
            if isinstance(obj, DR.DerivedSpec):
                for r in obj.direct_evidence or []:
                    if r.id == leaf_id and getattr(r, "title", None):
                        import re as _re
                        return _re.sub(r"\s*\((?:Annex\s+)?[A-Z]?\.?[\d.]+\)\s*$", "", r.title).strip()
    except Exception:
        pass
    # Fallback: slug → title
    tail = leaf_id.rsplit(":", 1)[-1]
    return tail.replace("_", " ").title()


def humanize_attestation_row(row: dict) -> dict:
    """Ship 92'.d — return the humanized fields for a cite attestation row.

    Merge these into the raw row before returning to the client.
    Adds:
      leaf_label:       'Statement of Applicability'
      must_label:       'SoA reference'
      cite_link_label:  'Information Security Policy' (from display, or extracted)
      primary_prose:    tenant-facing sentence
    """
    leaf_label = _leaf_label_from_id(row.get("leaf_id") or "")
    must_label = _humanize_must_label(row.get("must_id") or "")
    cite_link_label = _humanize_cite_url(
        row.get("cite_url") or "", row.get("cite_display"),
    )
    candidate = row.get("candidate_filename") or "the uploaded document"
    control_ref = row.get("control_ref") or ""
    prose_bits = [f"Your workbook cites <strong>{cite_link_label}</strong>"]
    if leaf_label:
        prose_bits[-1] += f" in your <strong>{leaf_label}</strong>"
    prose_bits[-1] += f" ({control_ref})."
    prose_bits.append(
        f"You uploaded <strong>{candidate}</strong>, which appears to cover the "
        f"same requirement ({must_label})."
    )
    prose_bits.append("Is this the version your workbook was referring to?")
    return {
        "leaf_label":      leaf_label,
        "must_label":      must_label,
        "cite_link_label": cite_link_label,
        "primary_prose":   " ".join(prose_bits),
    }
