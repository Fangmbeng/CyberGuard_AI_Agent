from app.tools.anomaly_tools import detect_network_anomalies
from app.services.bigquery_service import BigQueryService
from app.services.cloud_security_service import CloudSecurityService

class DetectronService:
    def __init__(self, bq_service: BigQueryService, security_service: CloudSecurityService):
        self.bq = bq_service
        self.security = security_service

    def detect_anomalies(self, limit: int = 1000) -> list[dict]:
        logs = self.bq.query_logs(query_filter="TRUE", limit=limit)
        indicators = self.security.scan_network_activity(logs)
        anomalies = detect_network_anomalies(logs, indicators)

        # Convert Pydantic → dict with ISO timestamps
        json_ready = [
            {**a.model_dump(), "timestamp": a.timestamp.isoformat()}
            for a in anomalies
        ]
        # Persist to BigQuery
        if json_ready:
            self.bq.insert_anomalies(json_ready)

        return json_ready
