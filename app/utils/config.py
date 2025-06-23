import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class AgentConfig:
    name: str
    model: str
    max_iterations: int
    timeout_seconds: int
    tools: list[str]

@dataclass
class PlatformConfig:
    project_id: str
    location: str
    bigquery_dataset: str
    vertex_ai_location: str
    incident_bucket: str  # New: to store incident-related logs/actions
    crm_system: str
    erp_system: str
    financial_system: str
    agents: Dict[str, AgentConfig]
    reports_bucket: str

    @classmethod
    def from_env(cls):
        reports_bucket = os.getenv("REPORTS_BUCKET", "cyberguard-reports")
        return cls(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "crucial-strata-419415"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            bigquery_dataset=os.getenv("BIGQUERY_DATASET", "cyber_data"),
            vertex_ai_location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
            crm_system=os.getenv("CRM_SYSTEM", "Salesforce"),
            erp_system=os.getenv("ERP_SYSTEM", "SAP"),
            financial_system=os.getenv("FINANCIAL_SYSTEM", "QuickBooks"),
            incident_bucket = os.getenv("INCIDENT_BUCKET", "cyberguardian-incidents"),
            agents={},
            reports_bucket=reports_bucket,  # new
        )
