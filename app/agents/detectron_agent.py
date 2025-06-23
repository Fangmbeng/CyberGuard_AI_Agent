from typing import List
from google.adk.agents import LlmAgent
from app.utils.config import PlatformConfig
from app.services.detectron_service import DetectronService
from app.services.document_service import retrieve_docs  # RAG tool
from app.tools.anomaly_tools import Anomaly

instruction = """
    You are DetectronAgent, an expert anomaly detection assistant for cybersecurity operations.
    Your primary responsibility is to analyze network logs, detect suspicious patterns, and flag anomalous activity in real time.

    Use the `detect()` tool to:
    - Scan recent logs (default: last 1,000) for behavioral anomalies, suspicious outbound IP traffic, and system irregularities.
    - Always invoke `detect()` when asked to identify, scan, analyze, or correlate anomalies or unusual behavior.

    Guidelines:
    - Avoid creating your own SQL or query logic; let `detect()` handle data retrieval.
    - Responses must focus on clear and actionable anomaly summaries.
    - Always return anomalies with their timestamp, severity, description, and affected system.

    Example prompts that should trigger `detect()`:
    - “Scan the last 1,000 logs for unusual outbound network traffic.”
    - “Find real-time infrastructure anomalies in us-central1.”
    - “Detect abnormal activity contacting our production systems.”
    """

class DetectronAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, service: DetectronService):
        super().__init__(
            name="detectron_agent",
            model="gemini-2.0-flash",
            tools=[
                self.detect,
                retrieve_docs,           #  Raw doc retrieval
            ],
            description=instruction

        )
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_service", service)

    @property
    def config(self) -> PlatformConfig:
        return self._config

    @property
    def service(self) -> DetectronService:
        return self._service

    def detect(self) -> list[dict]:
        """
        Pull logs, flag suspicious IP traffic, and correlate anomalies via the service.
        Returns a list of Anomaly models.
        """
        anomalies = self.service.detect_anomalies()
        
        # Check if already dicts or need conversion
        if anomalies and isinstance(anomalies[0], dict):
            return anomalies
        
        # Convert models to dicts if they have model_dump method
        return [a.model_dump(mode="json") if hasattr(a, 'model_dump') else a for a in anomalies]

