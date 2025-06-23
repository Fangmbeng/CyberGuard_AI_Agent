import os
from app.services.reporting_service import ReportingService
from app.models.report import Report

def test_create_report():
    # Set REPORTS_BUCKET for the output_uri stub
    os.environ["REPORTS_BUCKET"] = "test-bucket"
    svc = ReportingService()
    sections = ["Summary", "Findings", "Recommendations"]
    report = svc.create_report(sections)
    assert isinstance(report, Report)
    assert report.sections == sections
    assert report.output_uri.startswith("gs://test-bucket/")
    assert report.generated_at.year >= 2025
