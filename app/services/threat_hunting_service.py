from app.services.bigquery_service import BigQueryService
from app.services.cloud_security_service import CloudSecurityService
from app.tools.threat_tools import hunt_threats
from app.models.threat import Threat
from typing import List, Dict, Any

class ThreatHuntingService:
    def __init__(self, bq: BigQueryService, security: CloudSecurityService):
        self.bq = bq
        self.security = security

    def detect_threats(self, limit: int, filter_expression: str) -> List[Dict[str, Any]]:
        # Validate and rewrite invalid fields
        filter_expression = self._sanitize_filter(filter_expression)
        return self.bq.query_logs(query_filter=filter_expression, limit=limit)

    def _sanitize_filter(self, filter_expression: str) -> str:
        """
        Converts hallucinated field references into valid log message substrings.
        """
        import re

        mappings = {
            r"event_type\s*=\s*['\"]?authentication['\"]?":
                "LOWER(message) LIKE '%authentication%'",
            r"authentication\.type\s*=\s*['\"]?credential-stuffing['\"]?":
                "LOWER(message) LIKE '%credential%'",
            r"authentication\.failure_reason\s*=\s*['\"]?invalid_password['\"]?":
                "LOWER(message) LIKE '%invalid password%'",
            r"failed_login_count\s*>\s*\d+":
                "LOWER(message) LIKE '%failed login%'",
            r"source_ip\s*=\s*['\"]?([\d.]+)['\"]?":
                r"ip = '\1'",
        }

        for pattern, replacement in mappings.items():
            filter_expression = re.sub(pattern, replacement, filter_expression, flags=re.IGNORECASE)

        # Fallback to TRUE if the result is empty
        if not filter_expression.strip():
            filter_expression = "TRUE"

        return filter_expression


    
    # def detect_threats(self, limit: int = 1000, filter_expression: str = "TRUE") -> List[Threat]:
    #     """
    #     Fetch recent logs from BigQuery, flag external‑IP network activity,
    #     then run the core hunt_threats logic to produce Threat models.
    #     """
    #     # 1) Retrieve logs (no filter means TRUE)
    #     logs = self.bq.query_logs(query_filter=filter_expression, limit=limit)

    #     # 2) Identify suspicious network activity
    #     indicators = self.security.scan_network_activity(logs)

    #     # 3) Run the threat‑hunting logic
    #     threats = hunt_threats(logs, indicators)
    #     return threats