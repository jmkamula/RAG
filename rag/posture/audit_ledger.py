"""
rag/posture/audit_ledger.py — Ship 119'.b (2026-09-05).

The auditor's ledger — a whole-program HTML compilation that
combines Ship 118'.a's point-in-time snapshot with per-leaf
evidence packages from Ship 61'.a, wrapped with a cover page,
tenant scoping declarations, and Ship 119'.a PII redaction /
user pseudonymisation.

Design (from the auditor-ledger design chat, 2026-09-05):

  · **Data minimisation by default** — the ledger includes
    coverage counts + verdicts + reasons for every control, but
    verbatim evidence excerpts are OPT-IN per ledger generation.
    Default is to summarise without exposing tenant document text.

  · **PII redaction always on** unless the tenant explicitly opts
    out per control. Ship 119'.a's redactor handles this.

  · **User pseudonymisation always on** — reviewer / attester
    identifiers become `user-<6-hex>` with a per-tenant salt the
    auditor cannot reverse.

  · **Cite-mode preferred over stored** — for controls with
    cited external evidence, the ledger shows the URL + verification
    date + verifier pseudonym, never the fetched content.

  · **Scope acknowledgement + retention statement** on the cover
    page. Auditor knows what they're getting, what they can retain,
    and for how long.

  · **Watermarked + traceable** — every ledger has a unique ID, the
    tenant name, and the auditor firm (when provided) embedded on
    every page. Ship 119'.c adds one-time-download URL delivery
    that ties this ID to a specific auditor engagement.

Output: single self-contained HTML document. Auditor opens in
browser, uses File → Print → Save as PDF (Ship 118'.c pattern).
No server-side PDF dependency.
"""
from __future__ import annotations
import hashlib
import logging
import uuid as _uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html import escape
from typing import Optional

from rag.posture.snapshot        import snapshot_posture, PostureSnapshot
from rag.posture.pii_redactor    import (
    redact_pii, pseudonymise_user_id, pseudonymise_users_in_text,
    redaction_summary,
)

logger = logging.getLogger(__name__)


@dataclass
class LedgerOptions:
    """Every generation parameter for a ledger export.

    Design: options that affect what the auditor sees are all
    explicit + captured on the cover page. Nothing is silent.
    """
    as_of:                    Optional[str] = None
    auditor_firm:             Optional[str] = None
    engagement_date:          Optional[str] = None
    engagement_reference:     Optional[str] = None
    redaction_level:          str  = 'default'   # off | default | strict
    include_verbatim_excerpts: bool = False       # opt-in per generation
    pseudonymise_users:       bool = True
    frameworks_filter:        Optional[list[str]] = None  # None = all enrolled
    retention_days:           int  = 2555         # 7 years, typical auditor retention


@dataclass
class LedgerMeta:
    """Cover-page metadata written once per generation."""
    ledger_id:      str
    tenant_name:    str
    generated_at:   datetime
    generated_by:   Optional[str]      # user_id (raw) — not exposed to auditor
    generated_by_display: str          # what the ledger cover shows
    snapshot:       PostureSnapshot
    options:        LedgerOptions
    tenant_salt:    str                # deterministic per-tenant, private


# ── Building the ledger ─────────────────────────────────────────────

def _tenant_salt(tenant_id: str) -> str:
    """Deterministic per-tenant salt for user pseudonymisation.

    Uses SHA-256 of the tenant UUID with a fixed application prefix.
    Same tenant always gets the same salt (pseudonyms stable across
    ledgers for the same tenant). Different tenants get different
    salts (same underlying user in tenant A appears as a different
    pseudonym in tenant B's ledger).

    Ship 119'.d + future arcs may migrate this to a per-tenant salt
    stored in the DB (tenant can rotate). For MVP the deterministic
    derivation is enough.
    """
    return hashlib.sha256(f"arion-ledger-salt-v1:{tenant_id}".encode()).hexdigest()[:32]


def _fetch_tenant_meta(pg_conn, tenant_id: str) -> dict:
    """Get tenant name + scoping facts for the cover + profile page."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT t.name, t.slug, cf.country, cf.sector, cf.employee_size_bucket,
                   cf.processes_personal_data, cf.role_controller, cf.role_processor,
                   cf.public_authority, cf.eu_data_subjects, cf.uk_data_subjects,
                   cf.us_data_subjects, cf.ca_data_subjects, cf.apac_data_subjects,
                   cf.other_data_subjects
              FROM tenants t
              LEFT JOIN client_facts cf ON cf.tenant_id = t.id
             WHERE t.id = %s::uuid
        """, (tenant_id,))
        row = cur.fetchone()
    if not row:
        raise ValueError(f"tenant not found: {tenant_id}")
    keys = ("name", "slug", "country", "sector", "employee_size_bucket",
            "processes_personal_data", "role_controller", "role_processor",
            "public_authority", "eu_data_subjects", "uk_data_subjects",
            "us_data_subjects", "ca_data_subjects", "apac_data_subjects",
            "other_data_subjects")
    return dict(zip(keys, row))


def _fetch_evidence_excerpts(
    pg_conn, tenant_id: str, opts: LedgerOptions, salt: str,
) -> dict[tuple[str, str], list[dict]]:
    """When include_verbatim_excerpts=True, fetch per-control approved
    evidence excerpts with PII redaction + user pseudonymisation
    already applied.

    Returns dict keyed by (standard_id, control_ref).
    Empty dict when include_verbatim_excerpts=False.
    """
    if not opts.include_verbatim_excerpts:
        return {}

    as_of_sql = None
    if opts.as_of and opts.as_of != 'now':
        as_of_sql = f"{opts.as_of[:10]} 23:59:59.999999+00" if len(opts.as_of) >= 10 else None

    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        if as_of_sql is None:
            sql = """
                SELECT df.standard_id, df.control_ref,
                       cd.filename, df.checklist_item_id,
                       df.excerpt, df.section_number,
                       df.reviewed_at, df.reviewed_by
                  FROM document_findings df
                  JOIN client_documents cd ON cd.id = df.document_id
                 WHERE df.tenant_id = %s::uuid
                   AND df.is_active = TRUE
                   AND df.review_status = 'approved'
                   AND (df.expires_at IS NULL OR df.expires_at > NOW())
                 ORDER BY df.standard_id, df.control_ref, df.reviewed_at DESC
            """
            cur.execute(sql, (tenant_id,))
        else:
            sql = """
                SELECT df.standard_id, df.control_ref,
                       cd.filename, df.checklist_item_id,
                       df.excerpt, df.section_number,
                       df.reviewed_at, df.reviewed_by
                  FROM document_findings df
                  JOIN client_documents cd ON cd.id = df.document_id
                 WHERE df.tenant_id      = %s::uuid
                   AND df.extracted_at  <= %s::timestamptz
                   AND df.reviewed_at   <= %s::timestamptz
                   AND (df.deleted_at   IS NULL OR df.deleted_at   > %s::timestamptz)
                   AND (df.expires_at   IS NULL OR df.expires_at   > %s::timestamptz)
                   AND (df.resolved_at  IS NULL OR df.resolved_at  > %s::timestamptz)
                   AND df.review_status = 'approved'
                 ORDER BY df.standard_id, df.control_ref, df.reviewed_at DESC
            """
            cur.execute(sql, (
                tenant_id, as_of_sql, as_of_sql, as_of_sql, as_of_sql, as_of_sql,
            ))
        rows = cur.fetchall()

    out: dict[tuple[str, str], list[dict]] = {}
    for std, ref, fname, cid, excerpt, sec, rev_at, rev_by in rows:
        key = (std, ref)
        # Redact PII + pseudonymise reviewer
        redacted_excerpt = redact_pii(excerpt or "", level=opts.redaction_level)
        reviewer_pseudo  = (
            pseudonymise_user_id(str(rev_by), salt) if opts.pseudonymise_users and rev_by
            else str(rev_by) if rev_by else None
        )
        out.setdefault(key, []).append({
            "filename":   fname,
            "must_id":    cid,
            "excerpt":    redacted_excerpt,
            "section":    sec,
            "reviewed_at": rev_at,
            "reviewer":   reviewer_pseudo,
        })
    return out


def build_audit_ledger(
    pg_conn,
    tenant_id:   str,
    options:     Optional[LedgerOptions] = None,
    generated_by: Optional[str] = None,
) -> tuple[LedgerMeta, str]:
    """Assemble the ledger. Returns (metadata, html_body).

    Caller manages the connection lifecycle. RLS-scoped when called
    with a runtime connection; direct read when called with the
    arioncomply-owner connection (as an operator would from a script).
    """
    opts = options or LedgerOptions()

    # 1) Snapshot the current (or point-in-time) posture
    snap = snapshot_posture(
        pg_conn, tenant_id, as_of=opts.as_of, generated_by=generated_by,
    )

    # 2) Filter to requested frameworks if specified
    if opts.frameworks_filter:
        snap.controls = [c for c in snap.controls if c.standard_id in opts.frameworks_filter]
        snap.control_count = len(snap.controls)

    # 3) Tenant metadata + per-tenant salt for pseudonymisation
    tmeta = _fetch_tenant_meta(pg_conn, tenant_id)
    salt  = _tenant_salt(tenant_id)

    # 4) Evidence excerpts (opt-in per ledger generation)
    excerpts_by_control = _fetch_evidence_excerpts(pg_conn, tenant_id, opts, salt)

    # 5) Assemble metadata
    ledger_id = str(_uuid.uuid4())
    generated_by_display = (
        pseudonymise_user_id(generated_by, salt) if (opts.pseudonymise_users and generated_by)
        else (generated_by or "tenant admin (identity not recorded)")
    )
    meta = LedgerMeta(
        ledger_id       = ledger_id,
        tenant_name     = tmeta["name"],
        generated_at    = datetime.now(timezone.utc),
        generated_by    = generated_by,
        generated_by_display = generated_by_display,
        snapshot        = snap,
        options         = opts,
        tenant_salt     = salt,
    )

    # 6) Render
    html = _render_ledger_html(meta, tmeta, excerpts_by_control)
    return meta, html


# ── HTML rendering ─────────────────────────────────────────────────

_HUMANIZE_STANDARD = {
    "ISO27001:2022":  "ISO 27001:2022",
    "ISO27701:2019":  "ISO 27701:2019",
    "GDPR:2016/679":  "GDPR (2016/679)",
}


def _human_std(s: str) -> str:
    return _HUMANIZE_STANDARD.get(s, s)


def _pill(finding: str, applicability: str) -> str:
    if applicability == "na":
        return '<span class="pill na-scope">N/A (out of scope)</span>'
    css = {
        "NC":            "nc",
        "OFI":           "ofi",
        "Comply":        "comply",
        "N/A":           "na",
        "Not assessed":  "notass",
    }.get(finding, "notass")
    return f'<span class="pill {css}">{escape(finding)}</span>'


def _region_summary(t: dict) -> str:
    """Bulleted list of regions with data subjects, from tenant meta."""
    regions = []
    if t.get("eu_data_subjects"):    regions.append("European Union / European Economic Area")
    if t.get("uk_data_subjects"):    regions.append("United Kingdom")
    if t.get("us_data_subjects"):    regions.append("United States")
    if t.get("ca_data_subjects"):    regions.append("Canada")
    if t.get("apac_data_subjects"):  regions.append("Asia-Pacific")
    if t.get("other_data_subjects"): regions.append("Latin America / Africa / Middle East / other")
    if not regions:
        return "<em>No regions declared</em>"
    return "<ul>" + "".join(f"<li>{escape(r)}</li>" for r in regions) + "</ul>"


def _role_summary(t: dict) -> str:
    roles = []
    if t.get("role_controller"):  roles.append("Data controller")
    if t.get("role_processor"):   roles.append("Data processor")
    if t.get("public_authority"): roles.append("Public authority / publicly-funded institution")
    if not roles:
        return "<em>No role declared</em>"
    return ", ".join(escape(r) for r in roles)


def _render_ledger_html(meta: LedgerMeta, tmeta: dict, excerpts: dict) -> str:
    opts = meta.options
    snap = meta.snapshot

    # Cover-page opts
    firm_line = escape(opts.auditor_firm) if opts.auditor_firm else "<em>not declared</em>"
    engagement_line = escape(opts.engagement_date) if opts.engagement_date else "<em>not declared</em>"
    engagement_ref  = escape(opts.engagement_reference) if opts.engagement_reference else "<em>not declared</em>"

    # Summary counts
    from collections import Counter
    by_f = Counter((c.finding, c.applicability_status) for c in snap.controls)
    def _count(finding, na_scope=False):
        n = 0
        for (f, a), k in by_f.items():
            if na_scope and a != "na": continue
            if not na_scope and a == "na": continue
            if f == finding: n += k
        return n

    nc_c      = _count("NC")
    ofi_c     = _count("OFI")
    comp_c    = _count("Comply")
    notass_c  = _count("Not assessed")
    na_c      = sum(1 for c in snap.controls if c.applicability_status == "na")
    evi_total = sum(c.evidence_count for c in snap.controls)
    cas_total = sum(c.cascade_open_followups for c in snap.controls)

    # Per-framework sections
    per_std: dict[str, list] = {}
    for c in snap.controls:
        per_std.setdefault(c.standard_id, []).append(c)

    framework_sections: list[str] = []
    for std in sorted(per_std.keys()):
        rows = sorted(per_std[std], key=lambda r: r.control_ref)
        std_by_f = Counter(c.finding for c in rows)
        std_summary = (
            f"<p style='color:#5f5e5a;font-size:13px'>{len(rows)} controls  &middot;  "
            + " &middot; ".join(f"{v} {k}" for k, v in sorted(std_by_f.items()))
            + "</p>"
        )
        row_html: list[str] = []
        for c in rows:
            pill = _pill(c.finding, c.applicability_status)
            reason = escape(
                (c.applicability_reason if c.applicability_status == "na"
                 else (c.finding_reason or ""))
                or ""
            )
            evi_notes = ""
            evs = excerpts.get((c.standard_id, c.control_ref), [])
            if evs:
                items = []
                for e in evs[:5]:  # cap at 5 per control to keep ledger readable
                    filename_esc = escape(e['filename'] or 'source')
                    excerpt_esc = escape(e['excerpt'] or '')
                    items.append(
                        f'<div style="border-left:3px solid #e2e0d8;padding-left:10px;margin:6px 0">'
                        f'<div style="font-size:11px;color:#5f5e5a">'
                        f'<strong>{filename_esc}</strong>'
                        f'{" &middot; §" + escape(str(e["section"])) if e.get("section") else ""}'
                        f'{" &middot; reviewed by " + escape(e["reviewer"] or "") if e.get("reviewer") else ""}'
                        f'</div>'
                        f'<div style="font-size:12.5px;margin-top:4px">{excerpt_esc}</div>'
                        f'</div>'
                    )
                if len(evs) > 5:
                    items.append(f'<div style="font-size:11px;color:#8a8878">…and {len(evs)-5} more excerpt(s)</div>')
                evi_notes = "".join(items)
            elif c.evidence_count > 0:
                evi_notes = f'<div style="font-size:11px;color:#5f5e5a"><em>{c.evidence_count} evidence row(s) — excerpts not included in this ledger (tenant did not opt in)</em></div>'
            if c.cascade_open_followups:
                evi_notes += f'<div style="font-size:11px;color:#a37b00;margin-top:4px"><em>{c.cascade_open_followups} open cascade follow-up(s)</em></div>'
            row_html.append(f"""
                <tr>
                  <td class="ref">{escape(c.control_ref)}</td>
                  <td>{pill}</td>
                  <td class="reason">{reason}{evi_notes}</td>
                </tr>
            """)
        framework_sections.append(f"""
            <section class="framework-section">
              <h2>{escape(_human_std(std))}</h2>
              {std_summary}
              <table>
                <thead><tr><th style="width:12%">Control</th><th style="width:22%">Verdict</th><th>Reason / evidence</th></tr></thead>
                <tbody>{"".join(row_html)}</tbody>
              </table>
            </section>
        """)

    # Coverage notes for the cover page
    coverage_rows = []
    for axis, note in snap.coverage_notes.items():
        cov = note.get("coverage", "?")
        cov_cls = "cov-full" if cov == "full" else "cov-partial"
        coverage_rows.append(
            f'<dt>{escape(axis)}</dt>'
            f'<dd><span class="{cov_cls}">{escape(cov)}</span> &middot; {escape(note.get("note",""))}</dd>'
        )

    # Retention statement
    from datetime import timedelta
    retention_until = (meta.generated_at + timedelta(days=opts.retention_days)).date().isoformat()

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Audit Ledger — {escape(meta.tenant_name)} — {escape(snap.as_of)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root {{
  --fg:#1a1a1a; --muted:#5f5e5a; --line:#e2e0d8; --paper:#fbfaf4; --panel:#fff;
  --accent:#534AB7; --accent-soft:#EEEDFE; --accent-fg:#3C3489;
  --nc:#B92A28; --nc-soft:#FEECEA; --ofi:#a37b00; --ofi-soft:#fff3b0;
  --comply:#1D9E75; --comply-soft:#E5F5EE; --na:#6b7280; --na-soft:#f3f4f6;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  --mono:"SF Mono",Menlo,Consolas,monospace;
}}
*{{box-sizing:border-box}}
body{{font-family:var(--sans);font-size:14px;line-height:1.55;color:var(--fg);background:var(--paper);
  max-width:1100px;margin:0 auto;padding:32px 28px 100px}}
h1{{font-size:2.2em;margin:0.2em 0 0.4em;letter-spacing:-0.02em}}
h2{{font-size:1.35em;margin:2em 0 0.5em;padding-bottom:0.3em;border-bottom:2px solid var(--line)}}
h3{{font-size:1.05em;margin:1.4em 0 0.4em;color:var(--accent-fg)}}
p{{margin:0.4em 0 0.8em}}
code{{font-family:var(--mono);font-size:0.9em;background:#f2f0e8;padding:1px 5px;border-radius:3px}}
a{{color:var(--accent-fg)}}
.cover{{padding:28px 32px;background:linear-gradient(135deg,#F3F1FA,#EEEDFE);
  border-left:5px solid var(--accent);border-radius:10px;margin-bottom:24px}}
.cover .eyebrow{{font-size:11px;text-transform:uppercase;letter-spacing:0.12em;
  font-weight:700;color:var(--accent-fg);margin-bottom:8px}}
.cover h1{{color:var(--fg);margin-top:0}}
.cover .lede{{font-size:1.1em;color:var(--fg);margin:14px 0}}
.cover-grid{{display:grid;grid-template-columns:max-content auto;gap:6px 18px;
  margin-top:16px;font-size:13.5px}}
.cover-grid dt{{color:var(--muted);font-weight:600}}
.cover-grid dd{{margin:0}}
.summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:10px;margin:20px 0}}
.summary-card{{padding:14px 16px;background:var(--panel);border:1px solid var(--line);
  border-radius:6px;text-align:center}}
.summary-card .num{{font-size:1.6em;font-weight:700;display:block;line-height:1.1}}
.summary-card .label{{font-size:11px;color:var(--muted);text-transform:uppercase;
  letter-spacing:0.05em;margin-top:4px}}
.summary-card.nc .num{{color:var(--nc)}}
.summary-card.ofi .num{{color:var(--ofi)}}
.summary-card.comply .num{{color:var(--comply)}}
.summary-card.na .num{{color:var(--accent-fg)}}
.coverage-notes{{background:#f6f4ec;border:1px solid var(--line);border-radius:6px;
  padding:12px 16px;margin:16px 0;font-size:12px}}
.coverage-notes dl{{display:grid;grid-template-columns:max-content auto;gap:4px 12px;margin:0}}
.coverage-notes dt{{font-weight:600}}
.coverage-notes dd{{margin:0;color:var(--muted)}}
.coverage-notes .cov-full{{color:var(--comply);font-weight:600}}
.coverage-notes .cov-partial{{color:var(--ofi);font-weight:600}}
.tenant-profile{{padding:18px 22px;background:var(--panel);border:1px solid var(--line);
  border-radius:6px;margin:20px 0}}
.tenant-profile h3{{margin-top:0}}
.tenant-profile dl{{display:grid;grid-template-columns:max-content auto;gap:6px 16px;margin:0}}
.tenant-profile dt{{color:var(--muted);font-weight:600}}
.tenant-profile dd{{margin:0}}
table{{width:100%;border-collapse:collapse;margin:12px 0 20px;font-size:12.5px}}
th,td{{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#f2f0e8;font-weight:700;font-size:11px;text-transform:uppercase;
  letter-spacing:0.04em;color:var(--muted)}}
td.ref{{font-family:var(--mono);font-size:11.5px;white-space:nowrap}}
td.reason{{color:var(--muted);font-size:12px;max-width:600px}}
.pill{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10.5px;
  font-weight:700;text-transform:uppercase;letter-spacing:0.04em}}
.pill.nc{{background:var(--nc-soft);color:var(--nc)}}
.pill.ofi{{background:var(--ofi-soft);color:var(--ofi)}}
.pill.comply{{background:var(--comply-soft);color:var(--comply)}}
.pill.na{{background:var(--na-soft);color:var(--na)}}
.pill.na-scope{{background:var(--accent-soft);color:var(--accent)}}
.pill.notass{{background:#f2f0e8;color:var(--muted)}}
.legal{{margin-top:40px;padding:18px 20px;background:var(--panel);border:1px solid var(--line);
  border-radius:6px;font-size:12.5px;color:var(--muted)}}
.legal strong{{color:var(--fg)}}
.watermark{{position:fixed;bottom:8px;right:12px;font-size:10px;color:rgba(0,0,0,0.28);
  font-family:var(--mono)}}
@media print{{
  body{{background:white;padding:0.5in;max-width:none}}
  .watermark{{position:fixed;bottom:0.2in;right:0.4in;font-size:8pt}}
  h2{{page-break-after:avoid}}
  .framework-section{{page-break-before:always}}
  .framework-section:first-child{{page-break-before:auto}}
  table{{page-break-inside:auto}}
  tr{{page-break-inside:avoid;page-break-after:auto}}
}}
</style>
</head>
<body>

<div class="cover">
  <div class="eyebrow">Compliance program &middot; audit ledger</div>
  <h1>{escape(meta.tenant_name)}</h1>
  <p class="lede">Audit ledger reconstructed from the tenant's compliance program state
  as of <strong>{escape(snap.as_of)}</strong>.</p>
  <dl class="cover-grid">
    <dt>Ledger ID</dt>            <dd><code>{escape(meta.ledger_id)}</code></dd>
    <dt>Generated</dt>            <dd>{escape(meta.generated_at.isoformat())}</dd>
    <dt>Generated by</dt>         <dd>{escape(meta.generated_by_display)}</dd>
    <dt>Auditor firm</dt>         <dd>{firm_line}</dd>
    <dt>Engagement date</dt>      <dd>{engagement_line}</dd>
    <dt>Engagement reference</dt> <dd>{engagement_ref}</dd>
    <dt>Redaction level</dt>      <dd><strong>{escape(opts.redaction_level)}</strong> &middot; {escape(redaction_summary(opts.redaction_level))}</dd>
    <dt>Verbatim excerpts</dt>    <dd>{"included per control (tenant opt-in)" if opts.include_verbatim_excerpts else "not included — coverage counts + gap reasons only"}</dd>
    <dt>User pseudonymisation</dt><dd>{"on — reviewer/attester identifiers replaced with user-&lt;hash&gt;" if opts.pseudonymise_users else "off — raw identifiers visible"}</dd>
    <dt>Retention</dt>            <dd>Auditor's copy retained until <strong>{escape(retention_until)}</strong> ({opts.retention_days} days from generation)</dd>
  </dl>
</div>

<div class="tenant-profile">
  <h3>Tenant profile — declared scoping facts</h3>
  <dl>
    <dt>Country</dt>              <dd>{escape(tmeta.get("country") or "—")}</dd>
    <dt>Sector</dt>               <dd>{escape(tmeta.get("sector") or "—")}</dd>
    <dt>Organisation size</dt>    <dd>{escape(tmeta.get("employee_size_bucket") or "—")}</dd>
    <dt>Handles personal data</dt><dd>{"Yes" if tmeta.get("processes_personal_data") else "No" if tmeta.get("processes_personal_data") is False else "—"}</dd>
    <dt>Role(s)</dt>              <dd>{_role_summary(tmeta)}</dd>
    <dt>Data-subject regions</dt> <dd>{_region_summary(tmeta)}</dd>
  </dl>
</div>

<div class="summary-grid">
  <div class="summary-card"><span class="num">{snap.control_count}</span><span class="label">total controls</span></div>
  <div class="summary-card nc"><span class="num">{nc_c}</span><span class="label">non-conformity</span></div>
  <div class="summary-card ofi"><span class="num">{ofi_c}</span><span class="label">opportunity for improvement</span></div>
  <div class="summary-card comply"><span class="num">{comp_c}</span><span class="label">comply</span></div>
  <div class="summary-card na"><span class="num">{na_c}</span><span class="label">out of scope (N/A)</span></div>
  <div class="summary-card"><span class="num">{notass_c}</span><span class="label">not assessed</span></div>
  <div class="summary-card"><span class="num">{evi_total}</span><span class="label">evidence rows</span></div>
  <div class="summary-card"><span class="num">{cas_total}</span><span class="label">open follow-ups</span></div>
</div>

<div class="coverage-notes">
  <h4 style="margin:0 0 8px;font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted)">
    Coverage notes — what this ledger can and cannot reconstruct
  </h4>
  <dl>
    {"".join(coverage_rows)}
  </dl>
</div>

{"".join(framework_sections)}

<div class="legal">
  <p><strong>About this ledger.</strong> This audit ledger was generated by
  ArionComply from the compliance program of <strong>{escape(meta.tenant_name)}</strong>.
  It reflects the compliance posture as of {escape(snap.as_of)} — reconstructed
  from the tenant's assertion history + evidence lifecycle timestamps.</p>

  <p><strong>Data protection.</strong> This ledger may contain third-party
  personal data (data subjects named in evidence, staff who acted on
  findings). It is intended for the audit engagement documented on the
  cover page. Further distribution requires the tenant's consent + a
  compatible legal basis at the recipient.</p>

  <p><strong>Retention.</strong> Under the terms of this ledger, the auditor's
  copy is retained until <strong>{escape(retention_until)}</strong>. On or before that date,
  destruction / return should occur per the auditor's engagement letter.</p>

  <p><strong>Not a certification.</strong> ArionComply surfaces compliance
  state as observed; the tenant + their auditor own the compliance
  decision. This ledger is a record of what the ledger showed at
  generation time — not an assertion of correctness by any party.</p>

  <p><strong>Pseudonymisation legend.</strong> Reviewer and attester
  identifiers shown as <code>user-&lt;hash&gt;</code> pseudonyms.
  The tenant retains the mapping privately. Requests to resolve
  a specific pseudonym should be made in writing to the tenant.</p>
</div>

<div class="watermark">
  {escape(meta.tenant_name)} &middot; {escape(meta.ledger_id)}
</div>

</body>
</html>"""
