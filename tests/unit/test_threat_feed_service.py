from app.services.threat_feed_service import ThreatFeedService

def test_fetch_cves_structure():
    service = ThreatFeedService()
    cves = service.fetch_recent_cves(days=1)
    assert isinstance(cves, list)
    assert cves and hasattr(cves[0], "id") and hasattr(cves[0], "summary")
