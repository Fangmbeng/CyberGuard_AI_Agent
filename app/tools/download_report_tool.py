from google.cloud import storage
from typing import Dict
import os

def download_report(report_id: str) -> Dict[str, str]:
    """
    Given a report ID, generate a signed URL valid for 1 hour so the user can download the PDF.
    """
    bucket_name = os.getenv("REPORTS_BUCKET")
    if not bucket_name:
        raise RuntimeError("Environment variable REPORTS_BUCKET is not set")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"{report_id}.pdf")

    if not blob.exists():
        raise ValueError(f"Report '{report_id}' not found in bucket '{bucket_name}'")

    url = blob.generate_signed_url(
        version="v4",
        expiration=3600,  # 1 hour
        method="GET"
    )
    return {
        "report_id": report_id,
        "download_url": url
    }
