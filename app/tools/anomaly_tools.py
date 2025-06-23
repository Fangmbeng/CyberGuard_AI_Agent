from typing import List, Dict, Any
from app.models.anomaly import Anomaly
from datetime import datetime

def detect_network_anomalies(
    logs: List[Dict[str, Any]],
    indicators: List[Dict[str, Any]],
) -> List[Anomaly]:
    """
    Simple anomaly correlation: for each indicator, produce an Anomaly record.
    """
    anomalies: List[Anomaly] = []
    for idx, indicator in enumerate(indicators, start=1):
        anomalies.append(
            Anomaly(
                id=f"anomaly-{idx:03d}",
                source="network-activity",
                severity="high",  # you could infer from indicator content
                timestamp=indicator.get("timestamp", datetime.utcnow()),
                description=indicator.get("note", "Suspicious network traffic"),
                affected_system=indicator.get("ip"),
            )
        )
    return anomalies
