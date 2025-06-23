from google.adk.agents import LlmAgent
from typing import List, Optional
from app.utils.config import PlatformConfig
from app.services.intelligence_service import IntelligenceService
from app.services.ingestion_service import IngestionService
from app.services.document_service import retrieve_docs # RAG integration
from app.models.threat_intel import ThreatIntel


instruction = """
You are IntelligenceAgent, responsible for collecting, enriching, and modeling global threat intelligence.

Use your tools to:

1. `ingest_feeds()`:  
   - Fetch the latest raw feeds from CVE, dark web chatter, and SOC logs.  
   - Always run this first when asked to “ingest”, “aggregate”, or “update” threat feeds.

2. `train_model()`:  
   - Trigger a Vertex AI training job on historical threat data.  
   - Use it when asked to “train”, “build predictive model”, or “generate risk forecasts.”

3. `run_ingestion_pipeline(cron_schedule, pipeline_name)`:  
   - Submit or schedule the Kubeflow ingestion pipeline.  
   - Provide an optional cron or custom pipeline name when asked to “schedule” or “run ingestion.”

4. `retrieve_docs(query)`:  
   - Perform RAG lookups against your datastore for CVE details, threat advisories, or best practices.  
   - Use for ad hoc intelligence lookups (e.g., “summarize CVE-2025-1234”).

Guidelines:
- Always begin with `ingest_feeds()` for any “update” or “sync” operations.
- For “forecast” or “predict” prompts, call `train_model()`.
- For scheduling or running pipelines, use `run_ingestion_pipeline()`.
- For detailed background or playbooks, use `retrieve_docs()` with clear queries.
- Return JSON-serializable threat records when using `ingest_feeds()`.

Examples:
- “Ingest the latest CVEs and dark web feeds, then show new high-severity items.”
- “Run the ingestion pipeline now and schedule it hourly.”
- “Train a predictive threat model on our historical dataset.”
- “Retrieve details on CVE-2025-1234 from our threat encyclopedia.”

Caution:
- Do not call multiple tools simultaneously—pick the one matching the user’s intent.
- Ensure outputs are JSON-serializable dictionaries, not Pydantic models.
"""


class IntelligenceAgent(LlmAgent):
    def __init__(
        self,
        config: PlatformConfig,
        intel_service: IntelligenceService,
        ingestion_service: IngestionService,
    ):
        super().__init__(
            name="intelligence_agent",
            model="gemini-2.0-flash",
            tools=[
                self.ingest_feeds,
                self.train_model,
                self.run_ingestion_pipeline,
                retrieve_docs,  # ✅ Add RAG lookup tool
            ],
            description=instruction
        )
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_intel", intel_service)
        object.__setattr__(self, "_ingest", ingestion_service)

    @property
    def config(self) -> PlatformConfig:
        return self._config

    @property
    def intel(self) -> IntelligenceService:
        return self._intel

    @property
    def ingest(self) -> IngestionService:
        return self._ingest

    def ingest_feeds(self) -> List[dict]:
        threats: List[ThreatIntel] = self.intel.aggregate_feeds()
        return [t.model_dump(mode="json") for t in threats]

    def train_model(self) -> str:
        return self.intel.train_prediction_model()

    def run_ingestion_pipeline(self, cron_schedule: Optional[str] = None, pipeline_name: str = "cyber_intel_ingest") -> str:
        """
        Trigger the pipeline with an optional custom name.
        """
        return self.ingest.submit_pipeline(cron_schedule, pipeline_name=pipeline_name)
        

