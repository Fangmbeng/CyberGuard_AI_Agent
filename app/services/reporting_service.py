from typing import List, Dict
from google.cloud import storage
from app.tools.report_tools import generate_compliance_report, render_report_to_pdf
from app.models.report import Report
from app.services.bigquery_service import BigQueryService
from app.utils.client_manager import PickleSafeService
from app.utils.config import PlatformConfig
import logging

logger = logging.getLogger(__name__)

class ReportingService:
    def __init__(self, config: PlatformConfig):
        super().__init__(config.project_id)
        self.dataset = config.bigquery_dataset
        self.config = config
    
    @property
    def client(self):
        """Get BigQuery client."""
        return self.client_manager.get_bigquery_client()

    def create_report(self, sections: List[str]) -> Report:
        report = generate_compliance_report(sections)
        self._reports[report.id] = report
        return report

    def save_report(self, report_id: str) -> str:
        """
        Render the Report into PDF bytes, upload to GCS,
        and return the GCS URI.
        """
        report = self.get_report(report_id)
        pdf_bytes = render_report_to_pdf(report)
        blob = self.storage.bucket(self.bucket_name).blob(f"{report.id}.pdf")
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        return f"gs://{self.bucket_name}/{report.id}.pdf"

    def get_report(self, report_id: str) -> Report:
        """
        Retrieve a previously created Report by its ID.
        """
        if report_id not in self._reports:
            raise KeyError(f"Report ID {report_id} not found")
        return self._reports[report_id]

    def get_report_url(self, report_id: str, expiration: int = 900) -> str:
        """
        Generate a signed URL (v4, default 15 minutes) for the PDF in GCS.
        """
        bucket = self.storage.bucket(self.bucket_name)
        blob = bucket.blob(f"{report_id}.pdf")
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET",
        )
        return url
    
    def save_and_record(self, report: Report) -> str:
        # 1) Render & upload
        pdf_bytes = render_report_to_pdf(report)
        bucket = self.storage.bucket(self.bucket_name)

        if not bucket.exists():
            raise RuntimeError(f"GCS bucket '{self.bucket_name}' does not exist")

        blob_name = f"{report.id}.pdf"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        logger.info("Uploaded report PDF to gs://%s/%s", self.bucket_name, blob_name)

        # # 2) Verify upload
        # if not blob.exists():
        #     # Something went wrong; inspect what's actually in the bucket
        #     existing = [b.name for b in bucket.list_blobs()]
        #     raise RuntimeError(
        #         f"Upload reported success but '{blob_name}' is missing!\n"
        #         f"Bucket '{self.bucket_name}' contains: {existing}"
        #     )

        gcs_uri = f"gs://{self.bucket_name}/{blob_name}"

        # 3) Record metadata into BigQuery
        gen_at = report.generated_at
        gen_at_str = (
            gen_at.isoformat()
            if hasattr(gen_at, "isoformat")
            else str(gen_at)
        )

        # 2) Record metadata into BigQuery
        self.bq.insert_report_metadata(
            report_id=report.id,
            title=report.title,
            generated_at=gen_at_str,
            sections=report.sections,
            gcs_uri=gcs_uri,

        )
        return gcs_uri