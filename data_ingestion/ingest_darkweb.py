# data_ingestion/ingest_darkweb_fastapi.py

import os
import requests
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from google.cloud import bigquery

# Environment defaults
BQ_DATASET = os.getenv("BIGQUERY_DATASET", "cyber_data")
BQ_TABLE   = os.getenv("CVE_TABLE", "darkweb_chatter")
API_URL    = os.getenv("DARK_WEB_API", "https://api.example-darkweb.com/chatter")

app = FastAPI(title="DarkWeb Ingestion Service")

class IngestResponse(BaseModel):
    inserted: int

@app.get("/ingest_darkweb", response_model=IngestResponse)
def ingest_darkweb(limit: Optional[int] = Query(50, ge=1, le=1000, description="Number of entries to fetch")):
    """
    Pulls `limit` entries from the dark‑web API and appends them to BigQuery.
    """
    # Compose API URL with query parameter
    url = f"{API_URL}?limit={limit}"
    resp = requests.get(url)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Dark-web API error: {e}")

    data = resp.json().get("data", [])
    rows = []
    for entry in data:
        # Validate required fields
        try:
            rows.append({
                "id":           entry["id"],
                "chatter_text": entry.get("title", ""),
                "event_time":   entry.get("timestamp"),
            })
        except KeyError as e:
            # Skip malformed entry
            continue

    # Insert into BigQuery
    client = bigquery.Client()
    table_ref = f"{client.project}.{BQ_DATASET}.{BQ_TABLE}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise HTTPException(status_code=500, detail=f"BigQuery insert errors: {errors}")

    return IngestResponse(inserted=len(rows))
