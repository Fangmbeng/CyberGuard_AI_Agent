# app/agents/reporter_agent.py

from google.adk.agents import LlmAgent
from typing import List, Any, Dict
import json
import logging
from datetime import datetime

from app.utils.config import PlatformConfig
from app.services.reporting_service import ReportingService
from app.services.bigquery_service import BigQueryService
from app.models.report import Report
from app.services.document_service import retrieve_docs  # RAG tool
from app.utils.tracing import trace_log 

logger = logging.getLogger(__name__)

instruction = """
You are ReporterAgent, an automated reporting assistant for cybersecurity incidents and compliance.

Tools:
  • report(sections: List[str]) → JSON string  
    - Fetch metrics from BigQuery (anomalies, logs).  
    - Retrieve best-practice summaries via RAG (`retrieve_docs`).  
    - Serialize datetimes to ISO strings.  
    - Return a JSON object with keys: id, title, generated_at, sections, output_uri.

  • save_report(report_id: str) → GCS URI  
    - Render the in-memory report to PDF.  
    - Upload to GCS and record the URI.  
    - Log the save action.

  • get_download_url(report_id: str) → Signed URL  
    - Generate a time-limited HTTPS URL for report download.

  • retrieve_docs(query: str) → str  
    - Perform a RAG lookup in the threat intelligence datastore.

Guidelines:
  1. Always call `report()` first to generate report content.  
  2. After `report()`, the user may call `save_report(report_id)` or `get_download_url(report_id)`.  
  3. For each section header, map to:
     – “Executive Summary”: semantic summary from RAG.  
     – “Findings”: JSON dumps of anomalies & logs.  
     – “Recommendations”: best-practice guidance via RAG.
  4. If an unknown section is requested, respond with “No content defined for '<section>'”.
  5. Ensure the final output of `report()` is strictly valid JSON (no Python objects).

Examples:
  – “Generate an incident report with sections ['Executive Summary', 'Findings', 'Recommendations'].”  
  – “Save report 12345-abcde to GCS.”  
  – “Get download URL for report 12345-abcde.”

Caution:
  – Do not embed raw datetime objects; always convert them via `.isoformat()`.  
  – Use `retrieve_docs` only for contextual playbooks and summaries, not for quantitative data.
"""


def _serialize_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert datetime values in BigQuery rows to ISO strings."""
    serialized = []
    for row in records:
        new_row = {}
        for k, v in row.items():
            if isinstance(v, datetime):
                new_row[k] = v.isoformat()
            else:
                new_row[k] = v
        serialized.append(new_row)
    return serialized


class ReporterAgent(LlmAgent):
    def __init__(
        self,
        config: PlatformConfig,
        reporting_service: ReportingService,
        bq_service: BigQueryService,
    ):
        super().__init__(
            name="reporter_agent",
            model="gemini-2.0-flash",
            tools=[
                self.report,
                self.save_report,
                self.get_download_url,
                retrieve_docs,
            ],
            description=instruction
        )
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_service", reporting_service)
        object.__setattr__(self, "_bq", bq_service)

    @property
    def config(self) -> PlatformConfig:
        return self._config

    @property
    def service(self) -> ReportingService:
        return self._service

    @property
    def bq(self) -> BigQueryService:
        return self._bq

    def report(self, sections: List[str]) -> str:
        """
        Returns a JSON string of the report, mapping each section header
        to live data (BigQuery + RAG) with datetimes serialized.
        """
        logger.info(f"🛠 Entered ReporterAgent.report(), sections={sections}")

        # 1. Fetch raw data
        raw_anomalies = self.bq.query_behavior_anomalies(threshold=0.8)
        raw_logs = self.bq.query_logs(query_filter="TRUE", limit=20)
        raw_threats = self.bq.query_threat_intel(limit=10)  # new intel query
        guidance = retrieve_docs(query="incident response checklist")
        summary = retrieve_docs(query="recent threat summary")

        # 2. Serialize records to remove datetime objects
        anomalies = _serialize_records(raw_anomalies)
        logs = _serialize_records(raw_logs)
        threats   = _serialize_records(raw_threats)

        # 3. Map section headers to content
        section_map = {
            "Executive Summary": summary or "No summary available.",
            "Threat Intelligence": (
                "Recent Threat Intel:\n" +
                (json.dumps(threats, indent=2) if threats else "None available.")
            ),
            "Findings": (
                "Anomalies:\n" +
                (json.dumps(anomalies, indent=2) if anomalies else "None detected.") +
                "\n\nLogs:\n" +
                (json.dumps(logs, indent=2) if logs else "No logs found.")
            ),
            "Recommendations": guidance or "No recommendations available.",
        }

        # 4. Assemble only the requested sections
        filled_sections = []
        for header in sections:
            content = section_map.get(header, f"No content defined for '{header}'")
            filled_sections.append(f"{header}\n\n{content}")

        trace_log("📄 Final Report Sections", filled_sections)

        # 5. Create the Pydantic Report
        report_obj: Report = self.service.create_report(filled_sections)
        gen_at = str(report_obj.generated_at)

        # 6. Serialize report metadata
        result = {
            "id":           report_obj.id,
            "title":        report_obj.title,
            "generated_at": gen_at,
            "sections":     report_obj.sections,
            "output_uri":   report_obj.output_uri or "",
        }
        logger.info(f" Created Report ID {result['id']} with {len(filled_sections)} sections")

        # 7. Return as JSON text
        return json.dumps(result)


    def save_report(self, report_id: str) -> str:
        """
        Fetch the in-memory Report by ID, render it to PDF, upload to GCS,
        and record the GCS URI in storage or a log table.
        Returns the GCS URI.
        """
        # Retrieve the Report model
        report = self.service.get_report(report_id)
        # Save to GCS and record (e.g., BigQuery audit table)
        uri = self.service.save_and_record(report)
        logger.info(f"Report {report_id} saved at {uri}")
        return uri
    
    # def save_report(self, report_id: str) -> str:
    #     """
    #     Render, upload, and return the GCS URI of the report PDF.
    #     """
    #     return self.service.save_report(report_id)

    def get_download_url(self, report_id: str) -> str:
        """
        Return a signed HTTPS URL to download the report PDF.
        """
        url = self.service.get_report_url(report_id)
        logger.info(f" Download URL for report {report_id}: {url}")
        return url


# from google.adk.agents import LlmAgent
# from typing import List, Dict
# from app.utils.config import PlatformConfig
# from app.services.reporting_service import ReportingService
# from app.tools.download_report_tool import download_report  # signed‑URL tool
# from app.services.document_service import retrieve_docs       # RAG tool

# class ReporterAgent(LlmAgent):
#     def __init__(self, config: PlatformConfig, service: ReportingService):
#         super().__init__(
#             name="reporter_agent",
#             model="gemini-2.0-flash",
#             tools=[
#                 self.report,
#                 self.save,
#                 download_report,    # returns {"report_id":..., "download_url":...}
#                 retrieve_docs,      # RAG lookup
#             ],
#             description="Generates, saves, and provides download links for compliance & incident audit reports."
#         )
#         object.__setattr__(self, "_config", config)
#         object.__setattr__(self, "_service", service)

#     @property
#     def config(self) -> PlatformConfig:
#         return self._config

#     @property
#     def service(self) -> ReportingService:
#         return self._service

#     def report(self, sections: List[str]) -> str:
#         """
#         Generate an in‑memory report, enriched via RAG, and return summary with report ID.
#         """
#         enriched = []
#         for sec in sections:
#             docs = retrieve_docs(f"context for {sec}")
#             enriched.append(f"{sec}\nSupporting info:\n{docs}")

#         report = self.service.create_report(enriched)
#         return (
#             f"📄 Report generated with ID: {report.id}\n"
#             f"  Title: {report.title}\n"
#             f"  Generated: {report.generated_at}\n\n"
#             f"Use 'save report {report.id}' to upload to GCS, "
#             f"or 'download_report {report.id}' to get a download link."
#         )

#     def save(self, report_id: str) -> str:
#         """
#         Upload the report PDF to GCS, returning its bucket URI.
#         """
#         report = self.service.get_report(report_id)
#         uri = self.service.save_report(report)
#         return f"✅ Report saved to {uri}"
