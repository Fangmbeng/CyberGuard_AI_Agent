# tests/unit/test_threat_hunting_service.py

import pytest
from unittest.mock import MagicMock
from app.services.threat_hunting_service import ThreatHuntingService
from app.models.threat import Threat

@pytest.fixture
def mock_bq():
    bq = MagicMock()
    # Fake two log entries
    bq.query_logs.return_value = [
        {"ip": "8.8.8.8", "timestamp": "2025-06-19T00:00:00Z"},
        {"ip": "192.168.1.5", "timestamp": "2025-06-19T00:01:00Z"},
    ]
    return bq

@pytest.fixture
def mock_security():
    sec = MagicMock()
    # Only the public IP should pass
    sec.scan_network_activity.return_value = [
        {"ip": "8.8.8.8", "timestamp": "2025-06-19T00:00:00Z", "note": "Test"},
    ]
    return sec

def test_detect_threats_invokes_tools(mock_bq, mock_security):
    svc = ThreatHuntingService(mock_bq, mock_security)
    threats = svc.detect_threats(limit=2)

    # Ensure BQ was called with correct filter and limit
    mock_bq.query_logs.assert_called_once_with(query_filter="TRUE", limit=2)
    # Ensure security scan was called with the logs
    mock_security.scan_network_activity.assert_called_once_with(mock_bq.query_logs.return_value)

    # hunt_threats should return a list of Threat
    assert isinstance(threats, list)
    assert all(isinstance(t, Threat) for t in threats)
