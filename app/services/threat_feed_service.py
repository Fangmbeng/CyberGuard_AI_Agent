import requests
import datetime
import json
from typing import List
from app.models.threat_intel import ThreatIntel

class ThreatFeedService:
    def __init__(self):
        self.nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.reddit_url = "https://www.reddit.com/r/netsec/new.json"
        self.headers = {"User-Agent": "cyberguardian-agent"}

    def fetch_recent_cves(self, days=1) -> List[ThreatIntel]:
        """Fetch CVEs from NVD and normalize"""
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(days=days)
        params = {
            "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "resultsPerPage": 100,
        }
        r = requests.get(self.nvd_url, params=params, headers=self.headers)
        r.raise_for_status()

        return [
            ThreatIntel(
                source="cve",
                id=item["cve"]["id"],
                summary=item["cve"]["descriptions"][0]["value"],
                severity=item["cve"]["metrics"].get("cvssMetricV31", [{}])[0]
                         .get("cvssData", {}).get("baseSeverity", "unknown"),
                raw_data=item,
                timestamp=datetime.datetime.utcnow()
            )
            for item in r.json().get("vulnerabilities", [])
        ]

    def fetch_reddit_posts(self, limit=10) -> List[ThreatIntel]:
        """Fetch security Reddit posts and normalize"""
        r = requests.get(self.reddit_url, headers=self.headers)
        r.raise_for_status()
        posts = r.json().get("data", {}).get("children", [])[:limit]

        return [
            ThreatIntel(
                source="reddit",
                id=post["data"]["id"],
                summary=post["data"]["title"],
                severity=None,
                raw_data=post,
                timestamp=datetime.datetime.utcfromtimestamp(post["data"]["created_utc"])
            )
            for post in posts
        ]

    def write_to_jsonl(self, items: List[ThreatIntel], filepath: str):
        """Write threat items to JSONL"""
        with open(filepath, "w", encoding="utf-8") as f:
            for item in items:
                f.write(item.model_dump_json() + "\n")
