#!/usr/bin/env python3
import argparse
import os
import subprocess
from app.agent import root_agent
from app.services.intelligence_service import IntelligenceService
from app.services.threat_feed_service import ThreatFeedService
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.services.ingestion_service import IngestionService
from app.utils.config import PlatformConfig


def fetch_and_upload():
    from app.utils.gcs import upload_file_to_gcs

    svc = ThreatFeedService()
    items = svc.fetch_reddit_posts(limit=25) + svc.fetch_recent_cves(days=1)
    svc.write_to_jsonl(items, "threats.jsonl")
    bucket = os.environ["DATA_STORE_BUCKET"]
    remote_path = "threat_intel/threats.jsonl" 
    gcs_path = upload_file_to_gcs(local_file="threats.jsonl", bucket_name=bucket,remote_path=remote_path)
    print(f"[+] Uploaded feed to {gcs_path}")

def trigger_pipeline():
    config = PlatformConfig.from_env()
    ingest = IngestionService(config)
    result = ingest.submit_pipeline()
    print("[+] Pipeline trigger result:", result)

def run_scenario(name: str):
    if name == "ransomware":
        prompt = "Simulate a ransomware outbreak: detect, hunt, investigate, contain, remediate, report."
    elif name == "apt":
        prompt = "Simulate an APT: proactive threat prevention flow."
    elif name == "zero-day":
        prompt = "Simulate a zero-day discovery and global protection workflow."
    else:
        prompt = name  # treat any custom prompt

    print("=== Agent response ===")
    print(root_agent.invoke(prompt))

def main():
    parser = argparse.ArgumentParser("CyberGuardian Demo Runner")
    parser.add_argument("--fetch", action="store_true", help="Fetch & upload threat feeds")
    parser.add_argument("--pipeline", action="store_true", help="Trigger ingestion pipeline")
    parser.add_argument("--scenario", type=str, help="Scenario to run (ransomware|apt|zero-day|<custom>)")
    args = parser.parse_args()

    if args.fetch:
        fetch_and_upload()
    if args.pipeline:
        trigger_pipeline()
    if args.scenario:
        run_scenario(args.scenario)

if __name__ == "__main__":
    main()
