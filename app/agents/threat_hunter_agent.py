from typing import Optional,List
from google.adk.agents import LlmAgent
from app.utils.config import PlatformConfig
from app.services.threat_hunting_service import ThreatHuntingService
from app.services.bigquery_service import BigQueryService
from app.services.document_service import retrieve_docs

instruction = """
            You are ThreatHunterAgent, a cyber threat hunting expert trained to identify both active and historical attacks in system logs.

            Use your tools to:
            - Invoke `hunt()` to search logs for suspicious activities using structured filters (e.g. failed logins, brute-force, credential stuffing).
            - Always set a `limit` (default 1000) and supply a `filter_expression` (SQL-like WHERE clause).
            - Use `retrieve_threat_intel()` to fetch external threat intelligence, IOCs, or known exploit patterns using RAG-based document search.

            Tool Invocation Guidelines:
            - When prompted to search logs (e.g., “hunt”, “find”, “trace”, “identify past threats”), always use `hunt()` with a precise filter.
            - If no explicit filters are given, default to `"TRUE"` and use the limit to constrain results.
            - When the user references external intel or playbooks, use `retrieve_threat_intel()`.

            Examples:
            - “Hunt for credential‑stuffing attacks in the past 500 authentication logs.”
            - “Identify failed login spikes from unknown IPs.”
            - “Check if our network matches any known threat feeds from Mandiant.”

            Caution:
            - Avoid creating complex SQL logic; pass only simple `WHERE` clause conditions to `filter_expression`.
            - Logs may be limited in schema. Common available fields: `ip`, `timestamp`, `message`.
            """

class ThreatHunterAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, service: ThreatHuntingService, bq_service: BigQueryService):
        super().__init__(
            name="threat_hunter_agent",
            model="gemini-2.0-flash",
            tools=[self.hunt, self.retrieve_threat_intel, self.retrieve_historical_intel],
            description=instruction
        )
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_service", service)
        object.__setattr__(self, "_bq_service", bq_service)

    @property
    def config(self):
        return self._config

    @property
    def service(self):
        return self._service
    
    @property
    def bq(self):
        return self._bq_service
    
    def retrieve_threat_intel(self, query: str, source: Optional[str] = None) -> str:
        if source:
            query = f"{query} source:{source}"
        return retrieve_docs(query)

    def hunt(
        self,
        limit: int = 1000,
        filter_expression: str = "TRUE",
    ) -> list[dict]:
        """
        Tool to hunt threats via BigQuery + security scan.
        Args:
            limit: number of log rows to scan.
            filter_expression: SQL WHERE clause.
        Returns:
            List of serialized Threat models as JSON dicts.
        """
        threats = self.service.detect_threats(
            limit=limit, filter_expression=filter_expression
        )
        # Serialize Pydantic Threat -> dict
        if threats and isinstance(threats[0], dict):
            return threats

        return [
            t.model_dump(mode="json") if hasattr(t, "model_dump") else t
            for t in threats
        ]
    
    def retrieve_historical_intel(
        self,
        limit: int = 10,
        severity: Optional[str] = None,
    ) -> List[dict]:
        """
        Tool to pull historical CVEs and chatter from BigQuery.
        """
        return self.bq.query_threat_intel(
            limit=limit,
            severity=severity,
        )