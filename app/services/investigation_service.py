from app.services.bigquery_service import BigQueryService
from app.services.cloud_security_service import CloudSecurityService
from app.tools.investigation_tools import run_attack_investigation
from app.models.investigation_result import InvestigationResult

class InvestigationService:
    def __init__(self, bq: BigQueryService, security: CloudSecurityService):
        self.bq = bq
        self.security = security

    def investigate(self, limit: int = 1000) -> InvestigationResult:
        """
        1) Fetch recent security logs.
        2) List current cloud assets.
        3) Run the attack reconstruction logic.
        """
        # Use the generic query_logs under the hood with a security filter if desired
        logs = self.bq.query_logs(query_filter="TRUE", limit=limit)
        assets = self.security.list_assets()
        return run_attack_investigation(logs, assets)
