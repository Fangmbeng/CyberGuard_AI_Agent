from pydantic import BaseModel
from typing import List
from datetime import datetime

class InvestigationResult(BaseModel):
    timeline: List[str]
    attack_path: List[str]
    compromised_resources: List[str]
    data_exfiltrated: bool
    estimated_risk_score: float
    investigation_time: datetime
