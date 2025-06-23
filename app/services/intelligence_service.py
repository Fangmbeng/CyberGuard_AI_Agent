from typing import List
from app.services.threat_feed_service import ThreatFeedService
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.models.threat_intel import ThreatIntel

class IntelligenceService:
    def __init__(
        self,
        feed_service: ThreatFeedService,
        bq_service: BigQueryService,
        vertex_service: VertexAIService,
    ):
        self.feed = feed_service
        self.bq = bq_service
        self.vertex = vertex_service

    def aggregate_feeds(self) -> List[ThreatIntel]:
        """
        Fetch the latest threat intel from all sources,
        persist to BigQuery for history, and return the list.
        """
        reddit = self.feed.fetch_reddit_posts(limit=20)
        cves   = self.feed.fetch_recent_cves(days=1)
        # dark = self.feed.get_darkweb_intel(limit=20)
        combined = reddit + cves

        # Persist aggregated intel to BigQuery
        self.bq.insert_threat_intel(combined)

        return combined

    def train_prediction_model(self) -> str:
        """
        Kick off a Vertex AI training job for threat prediction.
        """
        dataset = self.bq.config.bigquery_dataset
        job_id = self.vertex.train_threat_model(dataset=dataset)
        return f"Triggered training job {job_id}"
