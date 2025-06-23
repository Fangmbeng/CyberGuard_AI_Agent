from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Threat(BaseModel):
    id: str
    type: str
    description: str
    severity: str
    source_ip: Optional[str]
    target_resource: Optional[str]
    timestamp: datetime
