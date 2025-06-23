from typing import List
from app.models.threat import Threat
from datetime import datetime

def hunt_threats(logs: list, indicators: list) -> List[Threat]:
    # Fake detection logic — simulate 1 threat
    return [
        Threat(
            id="threat-001",
            type="Credential Stuffing",
            description="Repeated failed logins detected from known malicious IP.",
            severity="critical",
            source_ip="192.0.2.10",
            target_resource="login-service",
            timestamp=datetime.utcnow()
        )
    ]
