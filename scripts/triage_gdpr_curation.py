"""Triage uncurated GDPR RequirementNodes into curation buckets (v2).

Buckets:
  COVERED — sub-clause of an already-curated parent (mark explicit_empty,
            reason="captured by parent <ref>")
  B1 — direct-evidence article (curate as EvidenceRequirement)
  B2 — implementation-derived (needs DerivedSpec + derives_from)
  B3 — operational / data-subject rights (operational trigger)
  B4 — definitional / scope / recital / supervisory (explicit_empty)
  UNCLASSIFIED — needs human review (target: as small as possible)

v2 changes vs v1:
  - tightened 'means ' pattern → only "' means " / 'means any' so it no longer
    catches 'by means of' / 'purposes and means of'
  - added COVERED bucket — sub-clauses of any curated GDPR parent
  - added Art.5/6/7/9/10/11 art_num overrides for the principles, lawful basis,
    consent, special-category, criminal-data, and no-ID-scope articles
  - added text patterns for 'lawfulness of processing', 'shall be lawful only if',
    'processing of special categories', 'shall be carried out only',
    'principles relating to processing'
"""
import csv
import os
from datetime import datetime

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv('/data/arioncomply/.env')
driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')),
)

BUCKET_CASE = """
CASE
  // COVERED first: sub-clause of an already-curated GDPR parent
  WHEN any(parent IN curated_parents
           WHERE parent <> '' AND ref STARTS WITH (parent + '.'))      THEN 'COVERED'

  // B4: definitions, scope, supervisory authority, remedies
  WHEN ntype IN ['recital','definition','scope']                       THEN 'B4'
  WHEN art_num IS NOT NULL AND art_num <= 4                            THEN 'B4'
  WHEN art_num = 11                                                    THEN 'B4'
  WHEN art_num IS NOT NULL AND art_num >= 51 AND art_num <= 91         THEN 'B4'
  WHEN ot CONTAINS "' means " OR ot CONTAINS 'means any'
    OR ot CONTAINS 'is defined as'                                     THEN 'B4'
  WHEN ot STARTS WITH 'this regulation' OR ot CONTAINS 'subject matter' THEN 'B4'
  WHEN ot = '' AND tt = ''                                             THEN 'B4'

  // B2: implementation-derived (the derives_from candidates)
  WHEN ot CONTAINS 'appropriate technical and organisational measures'
    OR ot CONTAINS 'data protection by design'
    OR ot CONTAINS 'data protection by default'
    OR ot CONTAINS 'security of processing'
    OR ot CONTAINS 'integrity and confidentiality'
    OR ot CONTAINS 'ongoing confidentiality, integrity'
    OR ot CONTAINS 'responsibility of the controller'
    OR ot CONTAINS 'shall implement appropriate measures'
    OR ot CONTAINS 'principles relating to processing'
    OR ot CONTAINS 'lawfully, fairly and in a transparent manner'
    OR tt CONTAINS 'security of processing'
    OR tt CONTAINS 'data protection by design'
    OR tt CONTAINS 'responsibility of the controller'
    OR tt CONTAINS 'accountability'
    OR tt STARTS WITH 'principles relating to'                         THEN 'B2'

  // B3: operational / time-bound / data-subject rights
  WHEN ot CONTAINS 'without undue delay'
    OR ot CONTAINS '72 hours'
    OR ot CONTAINS 'within one month'
    OR ot CONTAINS 'data subject shall have the right'
    OR ot CONTAINS 'the right to'
    OR ot CONTAINS 'on request'
    OR tt STARTS WITH 'right to' OR tt STARTS WITH 'right of'
    OR (art_num IS NOT NULL AND art_num >= 15 AND art_num <= 22)
    OR art_num = 34                                                    THEN 'B3'

  // B1: direct-evidence artefacts
  WHEN ot CONTAINS 'shall maintain a record'
    OR ot CONTAINS 'records of processing'
    OR ot CONTAINS 'shall designate'
    OR ot CONTAINS 'shall provide'
    OR ot CONTAINS 'in writing'
    OR ot CONTAINS 'data protection impact assessment'
    OR ot CONTAINS 'prior consultation'
    OR ot CONTAINS 'demonstrate that the data subject has consented'
    OR ot CONTAINS 'code of conduct'
    OR ot CONTAINS 'certification'
    OR ot CONTAINS 'binding corporate rules'
    OR ot CONTAINS 'standard contractual clauses'
    OR ot CONTAINS 'lawfulness of processing'
    OR ot CONTAINS 'shall be lawful only if'
    OR ot CONTAINS 'processing of special categories'
    OR ot CONTAINS 'shall be carried out only'
    OR tt CONTAINS 'notice'
    OR tt CONTAINS 'designation'
    OR tt CONTAINS 'records of'
    OR tt CONTAINS 'impact assessment'
    OR tt CONTAINS 'prior consultation'
    OR tt CONTAINS 'code of conduct'
    OR tt CONTAINS 'lawfulness of processing'
    OR (art_num IS NOT NULL AND art_num >= 44 AND art_num <= 50)       THEN 'B1'

  // Article-number overrides for residue not caught by content patterns
  WHEN art_num = 5                                                     THEN 'B2'
  WHEN art_num = 6 OR art_num = 7                                      THEN 'B1'
  WHEN art_num = 9 OR art_num = 10                                     THEN 'B1'

  ELSE 'UNCLASSIFIED'
END
"""

WITH_CLAUSE = """
// First: collect refs of all curated GDPR parents (used by the COVERED bucket)
MATCH (m:RequirementNode)-[:SATISFIED_BY]->(fsCur:FulfilmentSpec)
WHERE m.standard_id = 'GDPR:2016/679' AND fsCur.curation_status = 'curated'
WITH collect(m.ref) AS curated_parents

MATCH (n:RequirementNode)-[:SATISFIED_BY]->(fs:FulfilmentSpec)
WHERE n.standard_id = 'GDPR:2016/679'
  AND fs.curation_status = 'uncurated'
WITH curated_parents, n,
     toLower(coalesce(n.obligation_text,'')) AS ot,
     toLower(coalesce(n.title,''))           AS tt,
     coalesce(n.ref,'')                      AS ref,
     coalesce(n.node_type,'')                AS ntype,
     CASE WHEN n.ref STARTS WITH 'Art.'
          THEN toInteger(split(replace(n.ref,'Art.',''),'.')[0])
          ELSE null END AS art_num
"""

SUMMARY = WITH_CLAUSE + f"""
WITH n, ref, {BUCKET_CASE} AS bucket
RETURN bucket, count(*) AS n, collect(ref)[0..10] AS sample_refs
ORDER BY bucket
"""

DETAIL = WITH_CLAUSE + f"""
WITH n, ot, ref, ntype, art_num, tt, {BUCKET_CASE} AS bucket
WHERE bucket = $bucket
RETURN n.ref AS ref,
       n.title AS title,
       left(coalesce(n.obligation_text,''),200) AS obligation_snippet
ORDER BY n.ref
"""

stamp = datetime.now().strftime('%Y%m%d_%H%M')
outdir = f'/data/arioncomply/results/triage_gdpr_{stamp}'
os.makedirs(outdir, exist_ok=True)

with driver.session() as s:
    print(f"{'Bucket':<14} {'Count':>6}  Sample refs")
    print('-' * 78)
    for r in s.run(SUMMARY):
        refs = ', '.join(r['sample_refs'])
        print(f"{r['bucket']:<14} {r['n']:>6}  {refs}")
    print()

    for bucket in ['COVERED', 'B1', 'B2', 'B3', 'B4', 'UNCLASSIFIED']:
        rows = list(s.run(DETAIL, bucket=bucket))
        path = f'{outdir}/{bucket.lower()}.csv'
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['ref', 'title', 'obligation_snippet'])
            for r in rows:
                w.writerow([r['ref'], r['title'], r['obligation_snippet']])
        print(f"  -> {path}  ({len(rows)} rows)")

driver.close()
