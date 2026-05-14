"""
ArionComply — API Source Stub
Placeholder interface for future API-based compliance data sources.

Future adapters to implement:
  ServiceNowAdapter   — pull CMDB, incidents, change records
  JiraAdapter         — pull security tickets, risk items
  LansweeeperAdapter  — pull asset inventory
  CrowdStrikeAdapter  — pull endpoint compliance status
  QualysAdapter       — pull vulnerability scan results

Each adapter implements the BaseAPIAdapter interface and returns
a list of DocumentFinding objects — same output as the document extractor.
The pipeline treats API findings identically to document findings.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional

from .models import DocumentFinding, ParsedDocument, ExtractionPath

logger = logging.getLogger(__name__)


class BaseAPIAdapter(ABC):
    """
    Interface for API-based compliance data sources.
    Implement this for each external system integration.
    """

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Unique identifier for this adapter, e.g. 'servicenow'."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name, e.g. 'ServiceNow CMDB'."""
        ...

    @abstractmethod
    def connect(self, config: dict) -> bool:
        """
        Establish connection to the API.
        config: dict with credentials/endpoints from secrets manager.
        Returns True if connected successfully.
        """
        ...

    @abstractmethod
    def extract(
        self,
        tenant_id:   str,
        standard_id: str,
        controls:    list[dict],
    ) -> list[DocumentFinding]:
        """
        Extract compliance findings from the API source.
        Returns list of DocumentFinding objects.
        """
        ...

    def health_check(self) -> bool:
        """Optional: verify the connection is still alive."""
        return True


class StubAPIAdapter(BaseAPIAdapter):
    """
    Placeholder adapter — raises NotImplementedError.
    Replace with a real implementation when connecting to an external system.
    """

    def __init__(self, source_id: str, display_name: str):
        self._source_id    = source_id
        self._display_name = display_name

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def display_name(self) -> str:
        return self._display_name

    def connect(self, config: dict) -> bool:
        logger.warning(
            f"{self.display_name} adapter is a stub — not yet implemented. "
            f"Implement {self.__class__.__name__} to enable this integration."
        )
        return False

    def extract(
        self,
        tenant_id:   str,
        standard_id: str,
        controls:    list[dict],
    ) -> list[DocumentFinding]:
        raise NotImplementedError(
            f"{self.display_name} ({self.source_id}) API adapter is not yet implemented. "
            f"To add this integration:\n"
            f"  1. Create a class that extends BaseAPIAdapter in rag/intake/api_stub.py\n"
            f"  2. Implement connect() and extract() methods\n"
            f"  3. Register in ADAPTER_REGISTRY below\n"
            f"  4. Add connection config to tenant_source_registry table"
        )


# =============================================================================
# ADAPTER REGISTRY
# Register all available adapters here.
# Keys are source_id values stored in tenant_source_registry.source_id
# =============================================================================

ADAPTER_REGISTRY: dict[str, BaseAPIAdapter] = {
    "servicenow":   StubAPIAdapter("servicenow",   "ServiceNow CMDB"),
    "jira":         StubAPIAdapter("jira",          "Jira Security Tickets"),
    "lansweeper":   StubAPIAdapter("lansweeper",    "Lansweeper Asset Inventory"),
    "crowdstrike":  StubAPIAdapter("crowdstrike",   "CrowdStrike Endpoint Compliance"),
    "qualys":       StubAPIAdapter("qualys",        "Qualys Vulnerability Scans"),
    "azure_defender": StubAPIAdapter("azure_defender", "Microsoft Defender for Cloud"),
}


def get_adapter(source_id: str) -> Optional[BaseAPIAdapter]:
    """Look up an adapter by source_id. Returns None if not registered."""
    adapter = ADAPTER_REGISTRY.get(source_id)
    if adapter is None:
        logger.warning(f"No adapter registered for source_id: {source_id}")
    return adapter


def extract_from_api(
    source_id:   str,
    config:      dict,
    tenant_id:   str,
    standard_id: str,
    controls:    list[dict],
) -> list[DocumentFinding]:
    """
    Extract findings from a registered API adapter.
    Returns empty list and logs warning if adapter is a stub.
    """
    adapter = get_adapter(source_id)
    if adapter is None:
        return []

    if not adapter.connect(config):
        logger.warning(f"Could not connect to {adapter.display_name} — skipping")
        return []

    try:
        findings = adapter.extract(tenant_id, standard_id, controls)
        logger.info(f"{adapter.display_name}: extracted {len(findings)} findings")
        return findings
    except NotImplementedError as e:
        logger.warning(str(e))
        return []
    except Exception as e:
        logger.error(f"{adapter.display_name} extraction failed: {e}")
        return []
