from google.cloud import bigquery
from typing import List, Dict, Any, Optional
from app.utils.config import PlatformConfig
from app.utils.tracing import trace_log
from app.utils.client_manager import PickleSafeService
from app.utils.config import PlatformConfig
import logging
import json

logger = logging.getLogger(__name__)

_trace_logger = logging.getLogger("app.tracing")
_trace_logger.setLevel(logging.DEBUG)

class BigQueryService:
    def __init__(self, config: PlatformConfig):
        super().__init__(config.project_id)
        self.dataset = config.bigquery_dataset
        self.config = config
    
    @property
    def client(self):
        """Get BigQuery client."""
        return self.client_manager.get_bigquery_client()

    def query_logs(self, query_filter: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Generic log fetch for DetectronAgent & ThreatHunterAgent.
        """
        query = f"""
        SELECT *
        FROM `{self.client.project}.{self.dataset}.logs`
        WHERE {query_filter}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        logger.debug("BQ fetch_logs query: %s", query)
        rows = list(self.client.query(query).result())
        return [dict(row.items()) for row in rows]

    # def query_security_logs(self, limit: int = 1000) -> List[Dict[str, Any]]:
    #     """
    #     For InvestigatorAgent forensic reconstruction.
    #     """
    #     return self.fetch_logs("TRUE", limit)

    def query_audit_logs(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        For ComplianceAgent to scan audit trails.
        """
        return self.query_logs("log_type = 'AUDIT'", limit)

    def query_behavior_anomalies(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        query = f"""
        SELECT *
        FROM `{self.client.project}.{self.dataset}.anomaly_predictions`
        WHERE anomaly_score > {threshold}
        ORDER BY timestamp DESC
        LIMIT 10
        """
        trace_log("BQ anomaly query", query)
        rows = list(self.client.query(query).result())
        result = [dict(row.items()) for row in rows]
        trace_log("BQ anomaly results", result)
        return result
    
    def query_threat_intel(
        self,
        source_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve threat intel from the BigQuery table, optionally filtered by source or severity.
        Deserializes `raw_data` JSON strings back into dicts.
        """
        where_clauses = []
        if source_filter:
            where_clauses.append(f"source = '{source_filter}'")
        if severity_filter:
            where_clauses.append(f"severity = '{severity_filter}'")

        where_clause = " AND ".join(where_clauses) or "TRUE"

        query = f"""
        SELECT *
        FROM `{self.client.project}.{self.dataset}.threat_intel`
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """

        logger.debug("BQ query_threat_intel: %s", query)
        rows = list(self.client.query(query).result())

        results = []
        for row in rows:
            item = dict(row.items())
            if "raw_data" in item and isinstance(item["raw_data"], str):
                try:
                    item["raw_data"] = json.loads(item["raw_data"])
                except json.JSONDecodeError:
                    item["raw_data"] = {"error": "Failed to parse raw_data"}
            results.append(item)

        return results


    def insert_threat_intel(self, intel: List[Any]) -> None:
        """
        For IntelligenceService: store aggregated ThreatIntel into BigQuery.
        """
        table = f"{self.client.project}.{self.dataset}.threat_intel"

        records: List[Dict[str, Any]] = []
        for item in intel:
            # item.model_dump(mode="json") returns a dict of primitives + raw_data dict
            row = item.model_dump(mode="json")
            # Serialize raw_data to a JSON string
            raw = row.pop("raw_data", None)
            row["raw_data"] = json.dumps(raw) if raw is not None else None
            # Ensure timestamp is an ISO string
            if isinstance(row.get("timestamp"), (bytes, bytearray)):
                # if ever bytes, decode
                row["timestamp"] = row["timestamp"].decode()
            # Pydantic may already give timestamp as ISO str; otherwise:
            # if it's a datetime, convert
            if hasattr(row.get("timestamp"), "isoformat"):
                row["timestamp"] = row["timestamp"].isoformat()

            records.append(row)

        logger.debug("BQ insert_threat_intel records: %s", records)
        errors = self.client.insert_rows_json(table, records)
        if errors:
            trace_log("BQ insert_threat_intel errors", errors)
            raise RuntimeError(f"Failed to insert threat intel: {errors}")


    def insert_anomalies(self, anomalies: list[dict]) -> None:
        """
        Persist anomaly predictions into a dedicated table.
        """
        table = f"{self.client.project}.{self.dataset}.anomaly_predictions"
        errors = self.client.insert_rows_json(table, anomalies)
        if errors:
            logger.error("Failed to insert anomalies: %s", errors)
            raise RuntimeError(f"BigQuery insert_anomalies errors: {errors}")

    def insert_report_metadata(
        self,
        report_id: str,
        title: str,
        generated_at: str,
        sections: list[str],
        gcs_uri: str,
    ) -> None:
        """
        Persist report metadata so you can list/search past reports later.
        """
        table = f"{self.client.project}.{self.dataset}.reports"
        record = {
            "report_id": report_id,
            "title": title,
            "generated_at": generated_at,
            "sections": sections,
            "gcs_uri": gcs_uri,
        }
        errors = self.client.insert_rows_json(table, [record])
        if errors:
            logger.error("Failed to insert report metadata: %s", errors)
            raise RuntimeError(f"BigQuery insert_report_metadata errors: {errors}")
# from app.utils.config import PlatformConfig

# class BigQueryService:
#     def __init__(self, config: PlatformConfig):
#         self.config = config

#     def query_logs(self, limit: int = 1000):
#         # Placeholder
#         return [{"log": "example BQ log", "timestamp": "2025-06-17T00:00:00Z"}]
