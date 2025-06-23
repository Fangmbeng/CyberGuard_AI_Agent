from app.agents.investigator_agent import InvestigatorAgent
from app.services.investigation_service import InvestigationService
from app.services.bigquery_service import BigQueryService
from app.services.cloud_security_service import CloudSecurityService
from app.utils.config import PlatformConfig

def test_investigator_trace():
    config = PlatformConfig.from_env()
    bq = BigQueryService(config)
    sec = CloudSecurityService(config)
    service = InvestigationService(bq, sec)
    agent = InvestigatorAgent(config, service)
    result = agent.trace()
    assert result.data_exfiltrated is True
    assert isinstance(result.estimated_risk_score, float)
    assert len(result.timeline) > 0
