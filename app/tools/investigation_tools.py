from app.models.investigation_result import InvestigationResult
from datetime import datetime

def run_attack_investigation(logs: list, assets: list) -> InvestigationResult:
    return InvestigationResult(
        timeline=[
            "2025-06-17T11:12:00Z - Suspicious login from new geo",
            "2025-06-17T11:13:32Z - Service account privilege escalation",
            "2025-06-17T11:15:04Z - Access to sensitive BigQuery dataset"
        ],
        attack_path=["IAM > ServiceAccount > BigQueryDataset"],
        compromised_resources=["bigquery.myproject.sensitive_dataset"],
        data_exfiltrated=True,
        estimated_risk_score=9.2,
        investigation_time=datetime.utcnow()
    )
