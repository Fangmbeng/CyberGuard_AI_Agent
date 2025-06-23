from app.tools.anomaly_tools import detect_network_anomalies
from app.models.anomaly import Anomaly
from datetime import datetime

def test_detect_network_anomalies_empty():
    # No logs or indicators → no anomalies
    result = detect_network_anomalies([], [])
    assert result == []

def test_detect_network_anomalies_basic():
    # A single indicator should yield one anomaly
    indicator = {
        "ip": "8.8.8.8",
        "timestamp": datetime(2025, 6, 19, 12, 0, 0),
        "note": "Test outbound IP",
    }
    result = detect_network_anomalies([], [indicator])
    assert len(result) == 1
    anomaly = result[0]
    assert isinstance(anomaly, Anomaly)
    assert anomaly.id == "anomaly-001"
    assert anomaly.source == "network-activity"
    assert anomaly.description == "Test outbound IP"
    assert anomaly.affected_system == "8.8.8.8"
    assert anomaly.timestamp == indicator["timestamp"]
