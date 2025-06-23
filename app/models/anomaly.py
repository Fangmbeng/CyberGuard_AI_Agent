from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Anomaly(BaseModel):
    id: str
    source: str
    severity: str  # "low", "medium", "high"
    timestamp: datetime
    description: str
    affected_system: Optional[str]
