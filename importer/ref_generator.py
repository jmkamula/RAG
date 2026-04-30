"""
ArionComply — Platform Reference Generator

Generates stable, human-readable references for all client entities.
Format: {PREFIX}-{TENANT_SHORT}-{SEQUENCE}

Examples:
  PC-ARN-0001   Posture Control
  CD-ARN-0003   Client Document
  INC-ARN-002   Incident
  AST-ARN-001   Asset
  RSK-ARN-001   Risk
  VND-ARN-001   Vendor
  AUD-ARN-001   Audit

Usage:
  gen = PlatformRefGenerator(pg_conn, tenant_id, tenant_short="ARN")
  ref = gen.next_ref("client_documents")
  # → "CD-ARN-0001"
"""
from __future__ import annotations


# Table → (prefix, sequence_padding)
TABLE_TO_PREFIX: dict[str, tuple[str, int]] = {
    'posture_controls':   ('PC',  4),
    'client_documents':   ('CD',  4),
    'incidents':          ('INC', 3),
    'assets':             ('AST', 3),
    'risks':              ('RSK', 3),
    'vendors':            ('VND', 3),
    'isms_audits':        ('AUD', 3),
    'document_findings':  ('FND', 4),
}

# Reverse map
PREFIX_TO_TABLE: dict[str, str] = {
    v[0]: k for k, v in TABLE_TO_PREFIX.items()
}


class PlatformRefGenerator:
    """
    Generates and assigns platform_ref values.
    Uses the ref_sequences table in Postgres for atomic counters.
    Thread-safe: sequence increment is a single SQL upsert.
    """

    def __init__(
        self,
        pg_conn,
        tenant_id:    str,
        tenant_short: str,    # e.g. "ARN" — must be 2-4 uppercase letters
    ):
        if not tenant_short or not tenant_short.isalpha():
            raise ValueError(f"tenant_short must be 2-4 letters, got: {tenant_short!r}")
        self._pg           = pg_conn
        self._tenant_id    = tenant_id
        self._tenant_short = tenant_short.upper()

    def next_ref(self, table: str) -> str:
        """
        Generate the next platform_ref for a given table.
        Does NOT write to the entity table — call assign() to do that.
        """
        config = TABLE_TO_PREFIX.get(table)
        if not config:
            raise ValueError(f"No prefix configured for table: {table!r}")

        prefix, padding = config

        with self._pg.cursor() as cur:
            cur.execute(
                "SELECT next_platform_ref(%s, %s, %s)",
                (self._tenant_id, prefix, self._tenant_short)
            )
            return cur.fetchone()[0]

    def assign(self, table: str, record_id: str) -> str:
        """
        Generate a platform_ref and assign it to an existing DB row.
        Returns the platform_ref.
        """
        ref = self.next_ref(table)
        with self._pg.cursor() as cur:
            cur.execute(
                f"UPDATE {table} SET platform_ref = %s WHERE id = %s",
                (ref, record_id)
            )
        return ref

    def lookup(self, platform_ref: str) -> dict | None:
        """
        Look up an entity by its platform_ref across all tables.
        Returns {table, id, external_ref, display_name} or None.
        """
        prefix = platform_ref.split('-')[0] if '-' in platform_ref else ''
        table  = PREFIX_TO_TABLE.get(prefix)
        if not table:
            return None

        # Each table has different display columns
        display_cols = {
            'posture_controls':  'control_ref',
            'client_documents':  'document_title',
            'incidents':         'title',
            'assets':            'name',
            'risks':             'external_ref',
            'vendors':           'name',
            'isms_audits':       'external_ref',
            'document_findings': 'checklist_item_id',
        }
        ext_ref_col = 'external_ref' if table != 'vendors' else 'name'
        disp_col    = display_cols.get(table, 'id')

        with self._pg.cursor() as cur:
            cur.execute(f"""
                SELECT id::text, {ext_ref_col} AS external_ref, {disp_col} AS display_name
                FROM {table}
                WHERE tenant_id = %s AND platform_ref = %s
            """, (self._tenant_id, platform_ref))
            row = cur.fetchone()

        if not row:
            return None
        return {
            'platform_ref': platform_ref,
            'table':        table,
            'id':           row[0],
            'external_ref': row[1],
            'display_name': row[2],
        }

    @staticmethod
    def parse(platform_ref: str) -> dict:
        """
        Parse a platform_ref string into its components.
        Does not require a DB connection.
        """
        parts = platform_ref.split('-')
        if len(parts) != 3:
            return {}
        prefix, tenant_short, sequence = parts
        return {
            'prefix':       prefix,
            'tenant_short': tenant_short,
            'sequence':     int(sequence),
            'entity_type':  PREFIX_TO_TABLE.get(prefix, 'unknown'),
        }
