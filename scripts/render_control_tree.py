#!/usr/bin/env python3
"""Render a control's curation tree as a standalone HTML page.

Control → leaves → MUSTs + SHOULDs.  Pure Neo4j schema view, no tenant
posture / evidence overlay.  Output is a single file suitable for the
docs HTTP server (port 8001) or for scp back to a workstation.

Usage:
    python3 scripts/render_control_tree.py --control A.5.15 \
        --standard ISO27001:2022 --out docs/tree_A5_15.html

Serves via:
    http://localhost:8001/tree_A5_15.html
"""
from __future__ import annotations

import argparse
import html
import os
import sys
from typing import Any

import glob
import re
import yaml
from dotenv import load_dotenv
from neo4j import GraphDatabase


CSS = """
:root {
  --fg: #1a1a1a;
  --muted: #666;
  --accent: #1c76fc;
  --accent-soft: #eaf2ff;
  --leaf-fill: #f0f7ea;
  --leaf-border: #6aa84f;
  --must-fill: #fff;
  --must-border: #b0b0b0;
  --should-fill: #fafafa;
  --should-border: #d0d0d0;
  --should-fg: #555;
  --border: #d0d0d0;
  --line: #999;
  --code-bg: #f5f5f7;
  --mono: "SF Mono", Menlo, "Cascadia Code", monospace;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
* { box-sizing: border-box; }
body {
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.45;
  color: var(--fg);
  margin: 0;
  padding: 24px 32px;
  background: #fafafa;
}
h1 { font-size: 1.8em; margin: 0 0 8px; letter-spacing: -0.02em; }
.subtitle { color: var(--muted); font-size: 0.85em; margin-bottom: 24px; }
.legend {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--muted);
  margin: 16px 0 32px;
  padding: 10px 14px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 4px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.legend-swatch {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1.5px solid;
}

/* ── Control (root) ─────────────────────────────────────────────────── */
.tree { padding: 20px 0; }
.control-node {
  background: var(--accent);
  color: #fff;
  padding: 16px 22px;
  border-radius: 8px;
  margin: 0 auto 40px;
  max-width: 480px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(28, 118, 252, 0.15);
}
.control-node .ref {
  font-family: var(--mono);
  font-size: 1.3em;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.control-node .title {
  font-size: 1.05em;
  font-weight: 600;
  margin-top: 4px;
}
.control-node .std {
  font-size: 0.8em;
  opacity: 0.85;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 4px;
}
.control-node .obligation {
  font-size: 0.85em;
  font-weight: 400;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.25);
  text-align: left;
  color: rgba(255,255,255,0.95);
  font-style: italic;
}
.control-node .spec {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.72em;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(255,255,255,0.15);
  margin-top: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ── Connecting line control → leaves ───────────────────────────────── */
.control-to-leaves {
  position: relative;
  height: 30px;
  margin-top: -20px;
}
.control-to-leaves::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--line);
}

/* ── Leaves row ─────────────────────────────────────────────────────── */
.leaves {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 8px;
}
.leaf {
  background: var(--leaf-fill);
  border: 2px solid var(--leaf-border);
  border-radius: 6px;
  padding: 14px 16px;
  position: relative;
}
.leaf::before {
  /* connecting bar from control */
  content: "";
  position: absolute;
  left: 50%;
  top: -10px;
  width: 2px;
  height: 10px;
  background: var(--line);
}
.leaf-header {
  border-bottom: 1px dashed var(--leaf-border);
  padding-bottom: 8px;
  margin-bottom: 10px;
}
.leaf-id {
  font-family: var(--mono);
  font-size: 0.72em;
  color: #4a7f37;
  word-break: break-all;
}
.leaf-title {
  font-weight: 600;
  font-size: 1em;
  color: #2c5820;
  margin-top: 3px;
}
.leaf-meta {
  font-size: 0.72em;
  color: var(--muted);
  margin-top: 4px;
  font-family: var(--mono);
}

/* ── MUSTs + SHOULDs ────────────────────────────────────────────────── */
.checklist-group {
  margin-top: 10px;
}
.group-label {
  font-size: 0.7em;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  margin-bottom: 6px;
}
.ci {
  padding: 6px 10px;
  margin: 4px 0;
  border-radius: 3px;
  font-size: 0.85em;
  line-height: 1.35;
}
.ci-must {
  background: var(--must-fill);
  border-left: 3px solid var(--must-border);
}
.ci-should {
  background: var(--should-fill);
  border-left: 3px dashed var(--should-border);
  color: var(--should-fg);
}
.ci-id {
  font-family: var(--mono);
  font-size: 0.75em;
  color: var(--muted);
  display: block;
  margin-bottom: 2px;
}
.ci-text { display: block; }

/* ── Fingerprints ───────────────────────────────────────────────────── */
.fp-block {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--leaf-border);
}
.fp-group-label {
  font-size: 0.7em;
  color: #7a5e00;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  margin-bottom: 6px;
}
.fp-must {
  margin: 4px 0 8px;
  padding: 6px 10px;
  background: #fffbe6;
  border-left: 3px solid #e0b74c;
  border-radius: 3px;
  font-size: 0.82em;
}
.fp-must-id {
  font-family: var(--mono);
  font-size: 0.85em;
  color: #7a5e00;
  display: block;
  margin-bottom: 4px;
}
.fp-sets {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.fp-tokens {
  display: inline-flex;
  gap: 3px;
  padding: 2px 6px;
  background: #fff;
  border: 1px solid #e0b74c;
  border-radius: 3px;
  font-family: var(--mono);
  font-size: 0.75em;
  color: #5c4200;
}
.fp-token {
  padding: 0 2px;
}
.fp-token + .fp-token::before {
  content: "+";
  color: #b58a20;
  margin-right: 3px;
}
.fp-empty {
  font-size: 0.75em;
  color: var(--muted);
  font-style: italic;
  padding: 4px 10px;
}

/* ── Chat + Intake consensus panels ─────────────────────────────────── */
.consensus-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin: 0 auto 32px;
  max-width: 1000px;
}
.consensus-panel {
  border-radius: 6px;
  padding: 14px 18px;
  background: #fff;
}
.consensus-panel.chat {
  border: 2px solid #7a5cbe;
  background: #f4f0fa;
}
.consensus-panel.intake {
  border: 2px solid #cc7a1a;
  background: #fdf5eb;
}
.consensus-title {
  font-size: 0.85em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 0 0 4px;
}
.consensus-panel.chat .consensus-title { color: #5c3ea4; }
.consensus-panel.intake .consensus-title { color: #a05c15; }
.consensus-sub {
  font-size: 0.75em;
  color: var(--muted);
  margin-bottom: 10px;
}
.artifact {
  margin: 6px 0 10px;
  padding: 8px 10px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #d0d0d0;
}
.artifact-label {
  font-size: 0.68em;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
  margin-bottom: 4px;
}
.artifact code, .artifact .mono {
  font-size: 0.82em;
}
.pattern-row {
  display: flex;
  gap: 6px;
  align-items: baseline;
  flex-wrap: wrap;
  padding: 3px 0;
}
.qtype-badge {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.7em;
  padding: 1px 6px;
  border-radius: 3px;
  background: #efe6fa;
  color: #5c3ea4;
  font-weight: 600;
  letter-spacing: 0.03em;
}
.ref-badge {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.72em;
  padding: 1px 6px;
  border-radius: 3px;
  background: #eaf2ff;
  color: var(--accent);
  font-weight: 600;
}
.ref-badge.self {
  background: var(--accent);
  color: #fff;
}
.tokens-chip {
  display: inline-flex;
  gap: 3px;
  padding: 2px 6px;
  background: #fff;
  border: 1px solid #cc7a1a;
  border-radius: 3px;
  font-family: var(--mono);
  font-size: 0.75em;
  color: #6b3f0a;
  margin: 2px 3px 2px 0;
}
.tokens-chip .fp-token + .fp-token::before {
  color: #b58a20;
}
.target-leaf-chip {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.72em;
  padding: 2px 6px;
  background: #f0f7ea;
  border: 1px solid var(--leaf-border);
  border-radius: 3px;
  color: #2c5820;
  margin: 2px 3px 2px 0;
}
.target-leaf-chip.self {
  background: var(--leaf-border);
  color: #fff;
}
.empty-panel {
  font-size: 0.8em;
  color: var(--muted);
  font-style: italic;
  padding: 10px 4px;
}

/* ── Footer ─────────────────────────────────────────────────────────── */
.footer {
  margin-top: 60px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.82em;
  text-align: center;
}
code {
  background: var(--code-bg);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--mono);
  font-size: 0.85em;
}
a { color: var(--accent); }
"""


def esc(s: Any) -> str:
    return html.escape(str(s or ""))


def _leaf_to_fingerprint_path(leaf_id: str) -> str:
    # req:A.5.15:access_control_policy → req_A_5_15_access_control_policy.yaml
    slug = leaf_id.replace(":", "_").replace(".", "_")
    return f"/data/arioncomply/db/must_fingerprints/{slug}.yaml"


def _chat_artifacts(control_ref: str) -> dict:
    """Introspect rag/classifier.py's CLEAR_INTENT_PHRASES + DOCUMENT_TOPIC_MAP
    and return whatever routes chat queries to this control_ref.

    Returns:
        {
          'intent_phrases': [{'pattern': str, 'question_type': str, 'refs': [...]}],
          'topic_phrases':  [{'phrase': str, 'ref': str}],
        }
    """
    # Add project root to sys.path so we can import the classifier module.
    sys.path.insert(0, "/data/arioncomply")
    try:
        from rag.classifier import CLEAR_INTENT_PHRASES, DOCUMENT_TOPIC_MAP
    except Exception:
        return {'intent_phrases': [], 'topic_phrases': []}

    intents = []
    for entry in CLEAR_INTENT_PHRASES:
        if len(entry) < 3:
            continue
        pat, qtype, refs = entry[0], entry[1], entry[2]
        if control_ref in (refs or []):
            intents.append({
                'pattern':       pat.pattern if hasattr(pat, 'pattern') else str(pat),
                'question_type': qtype,
                'refs':          list(refs or []),
            })

    topics = [
        {'phrase': phrase, 'ref': ref}
        for phrase, ref in (DOCUMENT_TOPIC_MAP or {}).items()
        if ref == control_ref
    ]

    return {'intent_phrases': intents, 'topic_phrases': topics}


def _intake_artifacts(control_ref: str, leaf_ids: list[str]) -> dict:
    """Walk db/doc_mappings/*.yaml + db/workbook_mappings/*.yaml, return
    the mappings whose target_leaves land on this control's leaves.

    Returns:
        {
          'doc_mappings':      [{'mapping_id', 'filename_fingerprints', ...}],
          'workbook_mappings': [{'mapping_id', 'sheet_match', 'target_leaves'}],
        }
    """
    leaf_set = set(leaf_ids)
    doc_matches: list[dict] = []

    for fp in glob.glob("/data/arioncomply/db/doc_mappings/*.yaml"):
        try:
            with open(fp) as f:
                d = yaml.safe_load(f) or {}
        except Exception:
            continue
        # A mapping targets this control if ANY of its target_leaves' leaf_id
        # is in leaf_set, OR any target names the control_ref explicitly.
        targets = d.get("target_leaves") or []
        hit_leaves = [t for t in targets
                      if (t.get("leaf_id") in leaf_set) or (t.get("control_ref") == control_ref)]
        if not hit_leaves:
            continue
        doc_matches.append({
            'file':                  os.path.basename(fp),
            'mapping_id':            d.get('mapping_id', '?'),
            'filename_fingerprints': d.get('filename_fingerprints') or [],
            'body_fingerprints':     d.get('body_fingerprints') or [],
            'min_body_chars':        d.get('min_body_chars'),
            'target_leaves':         targets,  # full list — highlight ours
            'hit_leaves':            hit_leaves,
        })

    wb_matches: list[dict] = []
    for fp in glob.glob("/data/arioncomply/db/workbook_mappings/*.yaml"):
        try:
            with open(fp) as f:
                d = yaml.safe_load(f) or {}
        except Exception:
            continue
        # Workbook mappings vary in shape; scan for control_ref / leaf_id
        # references anywhere in the doc.
        raw = yaml.safe_dump(d)
        if not any(lid in raw for lid in leaf_ids) and control_ref not in raw:
            continue
        wb_matches.append({
            'file':          os.path.basename(fp),
            'mapping_id':    d.get('mapping_id') or d.get('id') or os.path.basename(fp),
            'sheet_match':   d.get('sheet_match') or d.get('sheet_name_fingerprints') or [],
            'target_leaves': d.get('target_leaves') or [],
            'row_mapping':   d.get('row_mapping') or {},
        })

    return {'doc_mappings': doc_matches, 'workbook_mappings': wb_matches}


def _load_fingerprints(leaf_id: str) -> dict:
    """Return {must_id: [token_set, ...]} for the leaf's fingerprint YAML.
    Empty dict if the file doesn't exist (auto-gen skipped, missing file, etc)."""
    path = _leaf_to_fingerprint_path(leaf_id)
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    out: dict[str, list[list[str]]] = {}
    for fp in (data.get("must_fingerprints") or []):
        mid = fp.get("must_id")
        kws = fp.get("excerpt_keywords") or []
        if mid:
            out[mid] = kws
    return out


def render(control_ref: str, standard_id: str, out_path: str) -> None:
    load_dotenv("/data/arioncomply/.env")
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    with driver.session() as s:
        ctrl = s.run(
            """
            MATCH (rn:RequirementNode {ref: $r, standard_id: $s})
            OPTIONAL MATCH (rn)-[:SATISFIED_BY]->(fs:FulfilmentSpec)
            RETURN rn.title AS title,
                   rn.business_description AS `desc`,
                   fs.op   AS op
            """,
            r=control_ref, s=standard_id,
        ).single()
        if not ctrl:
            raise SystemExit(f"control {control_ref} ({standard_id}) not found")

        leaves = s.run(
            """
            MATCH (rn:RequirementNode {ref: $r, standard_id: $s})
                  -[:SATISFIED_BY]->(:FulfilmentSpec)
                  -[:REQUIRES_EVIDENCE]->(er:EvidenceRequirement)
            RETURN er.id AS id, er.title AS title,
                   er.evidence_type AS et,
                   er.freshness_days AS fd
            ORDER BY er.id
            """,
            r=control_ref, s=standard_id,
        ).data()

        for leaf in leaves:
            leaf["musts"] = s.run(
                """
                MATCH (er:EvidenceRequirement {id: $id})-[:MUST_CONTAIN]->(ci:ChecklistItem)
                RETURN ci.id AS id, ci.text AS text
                ORDER BY ci.id
                """,
                id=leaf["id"],
            ).data()
            leaf["shoulds"] = s.run(
                """
                MATCH (er:EvidenceRequirement {id: $id})-[:SHOULD_CONTAIN]->(ci:ChecklistItem)
                RETURN ci.id AS id, ci.text AS text
                ORDER BY ci.id
                """,
                id=leaf["id"],
            ).data()

    driver.close()

    # ── Render ─────────────────────────────────────────────────────────
    display_std = {
        "ISO27001:2022":  "ISO 27001:2022",
        "ISO27701:2019":  "ISO 27701:2019",
        "GDPR:2016/679":  "GDPR (EU 2016/679)",
    }.get(standard_id, standard_id)

    obligation = (ctrl.get("desc") or "").strip()
    if len(obligation) > 400:
        obligation = obligation[:400].rsplit(" ", 1)[0] + "…"

    total_musts   = sum(len(L["musts"]) for L in leaves)
    total_shoulds = sum(len(L["shoulds"]) for L in leaves)

    def render_ci(items, cls):
        if not items:
            return ""
        rows = []
        for ci in items:
            rows.append(
                f'<div class="ci {cls}">'
                f'<span class="ci-id">{esc(ci["id"])}</span>'
                f'<span class="ci-text">{esc(ci["text"])}</span>'
                f'</div>'
            )
        return "\n".join(rows)

    def render_fingerprints(leaf_id: str, all_ci_ids: list[str]) -> str:
        fps = _load_fingerprints(leaf_id)
        if not fps and not all_ci_ids:
            return ""
        # Render in MUST/SHOULD order so operator can eyeball coverage
        rows = []
        for cid in all_ci_ids:
            token_sets = fps.get(cid)
            if not token_sets:
                # Show the missing-fingerprint gap explicitly so operators
                # can spot curation holes.
                rows.append(
                    f'<div class="fp-must">'
                    f'<span class="fp-must-id">{esc(cid)}</span>'
                    f'<span class="fp-empty">no fingerprint entry</span>'
                    f'</div>'
                )
                continue
            sets_html = "".join(
                '<span class="fp-tokens">' +
                "".join(f'<span class="fp-token">{esc(t)}</span>' for t in token_set) +
                '</span>'
                for token_set in token_sets
            )
            rows.append(
                f'<div class="fp-must">'
                f'<span class="fp-must-id">{esc(cid)}</span>'
                f'<div class="fp-sets">{sets_html}</div>'
                f'</div>'
            )
        n_covered = sum(1 for cid in all_ci_ids if fps.get(cid))
        if not rows:
            return ""
        exists_msg = "" if fps else " (no fingerprint YAML found — will fall back to leaf-scan / LLM at extract time)"
        return f'''
          <div class="fp-block">
            <div class="fp-group-label">FINGERPRINTS ({n_covered}/{len(all_ci_ids)} MUSTs+SHOULDs covered){exists_msg}</div>
            {"".join(rows)}
          </div>
        '''

    def render_leaf(L):
        musts_html   = render_ci(L["musts"],   "ci-must")
        shoulds_html = render_ci(L["shoulds"], "ci-should")
        fd = L.get("fd")
        fd_str = f"freshness={fd}d" if fd else "freshness=none"
        all_ci_ids = [ci["id"] for ci in L["musts"]] + [ci["id"] for ci in L["shoulds"]]
        fp_html = render_fingerprints(L["id"], all_ci_ids)
        return f"""
        <div class="leaf">
          <div class="leaf-header">
            <div class="leaf-id">{esc(L["id"])}</div>
            <div class="leaf-title">{esc(L["title"])}</div>
            <div class="leaf-meta">type={esc(L["et"])} · {esc(fd_str)}</div>
          </div>
          {'''<div class="checklist-group">
            <div class="group-label">MUSTs ({n})</div>
            {rows}
          </div>'''.format(n=len(L["musts"]), rows=musts_html) if L["musts"] else ""}
          {'''<div class="checklist-group">
            <div class="group-label">SHOULDs ({n})</div>
            {rows}
          </div>'''.format(n=len(L["shoulds"]), rows=shoulds_html) if L["shoulds"] else ""}
          {fp_html}
        </div>
        """

    leaves_html = "\n".join(render_leaf(L) for L in leaves)

    # ── Chat consensus panel ──────────────────────────────────────────
    chat = _chat_artifacts(control_ref)
    def render_chat_panel():
        n_intent = len(chat['intent_phrases'])
        n_topic = len(chat['topic_phrases'])
        if n_intent == 0 and n_topic == 0:
            body = '<div class="empty-panel">No CLEAR_INTENT_PHRASES or DOCUMENT_TOPIC_MAP entries route to this control. Chat falls back to Signal B (explicit ref) + Signal A (Chroma semantic) + LLM classifier.</div>'
        else:
            parts = []
            if n_intent:
                intent_rows = []
                for ip in chat['intent_phrases']:
                    ref_chips = "".join(
                        f'<span class="ref-badge{" self" if r == control_ref else ""}">{esc(r)}</span> '
                        for r in ip['refs']
                    )
                    intent_rows.append(
                        f'<div class="pattern-row">'
                        f'<span class="qtype-badge">{esc(ip["question_type"])}</span> '
                        f'<code>{esc(ip["pattern"])}</code> → {ref_chips}'
                        f'</div>'
                    )
                parts.append(
                    f'<div class="artifact">'
                    f'<div class="artifact-label">CLEAR_INTENT_PHRASES ({n_intent}) — Signal C, weight 1.00</div>'
                    f'{"".join(intent_rows)}'
                    f'</div>'
                )
            if n_topic:
                topic_rows = []
                for t in chat['topic_phrases']:
                    topic_rows.append(
                        f'<div class="pattern-row">'
                        f'"<strong>{esc(t["phrase"])}</strong>" → '
                        f'<span class="ref-badge self">{esc(t["ref"])}</span>'
                        f'</div>'
                    )
                parts.append(
                    f'<div class="artifact">'
                    f'<div class="artifact-label">DOCUMENT_TOPIC_MAP ({n_topic}) — Signal C, weight 1.00</div>'
                    f'{"".join(topic_rows)}'
                    f'</div>'
                )
            body = "".join(parts)
        return f'''
        <div class="consensus-panel chat">
          <div class="consensus-title">💬 Chat consensus — how queries route here</div>
          <div class="consensus-sub">Signal C (curator-authored lexicon). Top-tier weight 1.00 —
            these deterministically pin the resolved ref.</div>
          {body}
        </div>
        '''

    # ── Intake consensus panel ────────────────────────────────────────
    leaf_ids = [L['id'] for L in leaves]
    intake = _intake_artifacts(control_ref, leaf_ids)

    def render_intake_panel():
        n_doc = len(intake['doc_mappings'])
        n_wb = len(intake['workbook_mappings'])
        if n_doc == 0 and n_wb == 0:
            body = '<div class="empty-panel">No doc_mappings or workbook_mappings target this control. Intake falls back to fingerprint_keyword (per-MUST catalog, shown below) + must_semantic_topk (Chroma) + BM25 signals.</div>'
        else:
            parts = []
            for dm in intake['doc_mappings']:
                fn_chips = "".join(
                    '<span class="tokens-chip">' +
                    "".join(f'<span class="fp-token">{esc(t)}</span>' for t in (fp.get('tokens') or [])) +
                    '</span>'
                    for fp in dm['filename_fingerprints']
                )
                body_chips = "".join(
                    '<span class="tokens-chip">' +
                    "".join(f'<span class="fp-token">{esc(t)}</span>' for t in (fp.get('tokens') or [])) +
                    '</span>'
                    for fp in dm['body_fingerprints']
                )
                # Highlight target leaves that belong to THIS control
                leaf_set = set(leaf_ids)
                target_chips = "".join(
                    f'<span class="target-leaf-chip{" self" if t.get("leaf_id") in leaf_set else ""}">'
                    f'{esc(t.get("control_ref") or "?")} · {esc(t.get("role") or "")}'
                    f'</span>'
                    for t in dm['target_leaves']
                )
                min_body = (f' · min_body_chars={dm["min_body_chars"]}' if dm.get('min_body_chars') else '')
                parts.append(
                    f'<div class="artifact">'
                    f'<div class="artifact-label">doc_mapping · <code>{esc(dm["mapping_id"])}</code>{esc(min_body)}</div>'
                    f'{"<div><em style=\"font-size:0.72em;color:#666\">Filename fingerprints:</em><br>" + fn_chips + "</div>" if fn_chips else ""}'
                    f'{"<div style=\"margin-top:6px\"><em style=\"font-size:0.72em;color:#666\">Body fingerprints:</em><br>" + body_chips + "</div>" if body_chips else ""}'
                    f'{"<div style=\"margin-top:6px\"><em style=\"font-size:0.72em;color:#666\">Target leaves:</em><br>" + target_chips + "</div>" if target_chips else ""}'
                    f'</div>'
                )
            for wb in intake['workbook_mappings']:
                parts.append(
                    f'<div class="artifact">'
                    f'<div class="artifact-label">workbook_mapping · <code>{esc(wb["mapping_id"])}</code></div>'
                    f'<div class="mono" style="font-size:0.75em;color:#666">{esc(wb["file"])}</div>'
                    f'</div>'
                )
            body = "".join(parts)
        return f'''
        <div class="consensus-panel intake">
          <div class="consensus-title">📄 Intake consensus — how docs route here</div>
          <div class="consensus-sub">doc_mappings (filename + body fingerprints → target leaves) run BEFORE
            the 9-signal extractor kicks in, tightening scope.</div>
          {body}
        </div>
        '''

    consensus_row_html = f'''
      <div class="consensus-row">
        {render_chat_panel()}
        {render_intake_panel()}
      </div>
    '''

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{esc(control_ref)} — {esc(ctrl['title'] or 'control tree')}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{CSS}</style>
</head>
<body>

<h1>{esc(control_ref)} — {esc(ctrl['title'] or '')}</h1>
<p class="subtitle">{esc(display_std)} · curation-graph view · {len(leaves)} leaves · {total_musts} MUSTs · {total_shoulds} SHOULDs</p>

<div class="legend">
  <div class="legend-item"><span class="legend-swatch" style="background:var(--accent);border-color:var(--accent)"></span> Control (RequirementNode)</div>
  <div class="legend-item"><span class="legend-swatch" style="background:var(--leaf-fill);border-color:var(--leaf-border)"></span> Leaf (EvidenceRequirement)</div>
  <div class="legend-item"><span class="legend-swatch" style="background:var(--must-fill);border-color:var(--must-border);border-style:solid"></span> MUST (mandatory)</div>
  <div class="legend-item"><span class="legend-swatch" style="background:var(--should-fill);border-color:var(--should-border);border-style:dashed"></span> SHOULD (recommended)</div>
  <div class="legend-item"><span class="legend-swatch" style="background:#fffbe6;border-color:#e0b74c"></span> Fingerprint token-set (extraction keyword catalog)</div>
  <div class="legend-item"><span class="legend-swatch" style="background:#f4f0fa;border-color:#7a5cbe"></span> Chat consensus artifact</div>
  <div class="legend-item"><span class="legend-swatch" style="background:#fdf5eb;border-color:#cc7a1a"></span> Intake consensus artifact</div>
</div>

<div class="tree">
  <div class="control-node">
    <div class="ref">{esc(control_ref)}</div>
    <div class="title">{esc(ctrl['title'] or '')}</div>
    <div class="std">{esc(display_std)}</div>
    {f'<div class="obligation">{esc(obligation)}</div>' if obligation else ''}
    {f'<div class="spec">Spec op={esc(ctrl["op"] or "?")} · requires ALL {len(leaves)} leaves</div>' if ctrl.get("op") else ''}
  </div>

  <div class="control-to-leaves"></div>

  {consensus_row_html}

  <div class="leaves">
    {leaves_html}
  </div>
</div>

<div class="footer">
Generated from Neo4j curation graph · <a href="architecture_brief.html">architecture brief</a> · <a href="demo_walkthrough.html">demo walkthrough</a>
</div>

</body>
</html>
"""
    with open(out_path, "w") as f:
        f.write(doc)
    print(f"wrote {out_path} — {len(leaves)} leaves, {total_musts} MUSTs, {total_shoulds} SHOULDs")


def main() -> None:
    p = argparse.ArgumentParser(description="Render a control's curation tree as HTML")
    p.add_argument("--control",  required=True, help="e.g. A.5.15")
    p.add_argument("--standard", default="ISO27001:2022", help="e.g. ISO27001:2022")
    p.add_argument("--out",      required=True, help="output HTML path")
    args = p.parse_args()
    render(args.control, args.standard, args.out)


if __name__ == "__main__":
    main()
