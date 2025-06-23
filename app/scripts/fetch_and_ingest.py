# app/scripts/fetch_and_ingest.py

import os

def run():
    from app.services.threat_feed_service import ThreatFeedService
    from app.utils.gcs import upload_to_gcs

    feed = ThreatFeedService()
    cves = feed.fetch_recent_cves()
    reddit = feed.fetch_reddit_posts()

    feed.write_to_jsonl(cves, "cve_feed.jsonl")
    feed.write_to_jsonl(reddit, "reddit_feed.jsonl")

    upload_to_gcs("cyberguard-threat-data", "cve_feed.jsonl", "cve_feed.jsonl")
    upload_to_gcs("cyberguard-threat-data", "reddit_feed.jsonl", "reddit_feed.jsonl")

    print("✅ Threat feeds uploaded. Submitting ingestion pipeline...")

    from app.services.ingestion_service import IngestionService
    from app.utils.config import PlatformConfig

    config = PlatformConfig.from_env()
    ingest = IngestionService(config)
    ingest.submit_pipeline()

    print("✅ Ingestion pipeline triggered.")

if __name__ == "__main__":
    run()
