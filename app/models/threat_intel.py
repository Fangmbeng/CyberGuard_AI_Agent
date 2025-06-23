from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ThreatIntel(BaseModel):
    source: str                 # e.g., "dark_web", "CVE", "threat_feed"
    id: str                     # Unique identifier from feed
    summary: str                # Text summary or title
    severity: Optional[str]     # e.g., "low", "medium", "high"
    raw_data: dict              # Original payload
    timestamp: datetime         # When the intel was published
