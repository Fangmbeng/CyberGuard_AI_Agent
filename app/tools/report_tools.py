import uuid
import os
from datetime import datetime
from google.cloud import documentai_v1 as documentai
from typing import List
from app.models.report import Report
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from io import BytesIO

# Assumes DOCUMENT_AI_PROCESSOR_ID and PROJECT_ID are set in env
PROCESSOR_ID = "YOUR_PROCESSOR_ID"
LOCATION = "us-central1"

def generate_compliance_report(text_sections: List[str]) -> Report:
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(
        project=__import__("os").getenv("GOOGLE_CLOUD_PROJECT"),
        location=LOCATION,
        processor=PROCESSOR_ID,
    )
    # Here we'd normally call Document AI to process/generate, but for a report:
    report_id = str(uuid.uuid4())
    generated_at = datetime.utcnow().isoformat()  # ✅ Convert datetime to ISO string
    # Simulate uploading to GCS
    output_uri = f"gs://{os.getenv('REPORTS_BUCKET')}/{report_id}.pdf"

    return Report(
        id=report_id,
        title="CyberGuardian Incident Report",
        generated_at=generated_at,
        sections=text_sections,
        output_uri=output_uri,
    )

def render_report_to_pdf(report: Report) -> bytes:
    """
    Render the Report object into a PDF and return bytes.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, report.title)

    # Generated timestamp
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 90, f"Generated at: {report.generated_at}")

    # Sections
    y = height - 120
    for sec in report.sections:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, sec.split("\n")[0])  # section header
        y -= 16
        c.setFont("Helvetica", 10)
        for line in sec.split("\n")[1:]:
            c.drawString(72, y, line)
            y -= 12
            if y < 72:
                c.showPage()
                y = height - 72
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
