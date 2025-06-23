# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="arg-type"
import os

import google
import google.auth
import vertexai
from google.adk.agents import LlmAgent
from langchain_google_vertexai import VertexAIEmbeddings


from app.utils.config import PlatformConfig
from app.services.bigquery_service import BigQueryService
from app.services.cloud_security_service import CloudSecurityService
from app.services.detectron_service import DetectronService
from app.services.threat_hunting_service import ThreatHuntingService
from app.services.investigation_service import InvestigationService
from app.services.containment_service import ContainmentService
from app.services.remediation_service import RemediationService
from app.services.threat_feed_service import ThreatFeedService
from app.services.intelligence_service import IntelligenceService
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.services.reporting_service import ReportingService
from app.services.ingestion_service import IngestionService
from app.services.document_service import retrieve_docs


from app.agents.reporter_agent import ReporterAgent
from app.agents.intelligence_agent import IntelligenceAgent
from app.agents.remediator_agent import RemediatorAgent
from app.agents.detectron_agent import DetectronAgent
from app.agents.threat_hunter_agent import ThreatHunterAgent
from app.agents.investigator_agent import InvestigatorAgent
from app.agents.containment_agent import ContainmentAgent



EMBEDDING_MODEL = "text-embedding-005"
LLM_LOCATION = "global"
LOCATION = "us-central1"
LLM = "gemini-2.0-flash-001"

credentials, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LLM_LOCATION)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

vertexai.init(project=project_id, location=LOCATION)
embedding = VertexAIEmbeddings(
    project=project_id, location=LOCATION, model_name=EMBEDDING_MODEL
)


EMBEDDING_COLUMN = "embedding"
TOP_K = 5

data_store_region = os.getenv("DATA_STORE_REGION", "us")
data_store_id = os.getenv("DATA_STORE_ID", "my-awesome-agent-datastore")



# Initialize config and services
config = PlatformConfig.from_env()
bq_service = BigQueryService(config)
security_service = CloudSecurityService(config)
detectron_service = DetectronService(bq_service, security_service)
threat_hunting_service = ThreatHuntingService(bq_service, security_service)
investigation_service = InvestigationService(bq_service, security_service)
containment_service = ContainmentService(config)
remediation_service = RemediationService(config)
feed_service = ThreatFeedService()
vertex_service = VertexAIService(config)
intelligence_service = IntelligenceService(feed_service, bq_service, vertex_service)
reporting_service = ReportingService(bucket_name=os.getenv("REPORTS_BUCKET"), bq_service=bq_service)
ingestion_service = IngestionService(config)


# Create DetectronAgent
threat_hunter_agent = ThreatHunterAgent(config, threat_hunting_service, bq_service)
detectron_agent = DetectronAgent(config, detectron_service)
investigator_agent = InvestigatorAgent(config, investigation_service)
containment_agent = ContainmentAgent(config, containment_service)
remediator_agent = RemediatorAgent(config, remediation_service)
intelligence_agent = IntelligenceAgent(config, intelligence_service, ingestion_service)
reporter_agent = ReporterAgent(config, reporting_service, bq_service)

# --- Root Agent Instruction ---
instruction = """
You are CyberGuardian, an autonomous multi‐agent AI assistant for cybersecurity defense. 
Your job is to coordinate specialized sub‐agents, orchestrate complex workflows, 
and deliver clear, actionable outputs for detection, investigation, containment, remediation, 
intelligence gathering, predictive modeling, and compliance reporting.

Available sub‐agents and their primary responsibilities:
  • DetectronAgent       → Real‐time anomaly detection (network + infra)
  • ThreatHunterAgent    → Advanced threat hunting & behavioral analysis
  • InvestigatorAgent    → Forensic reconstruction and breach impact analysis
  • ContainmentAgent     → Rapid VM isolation, account lockdown, and policy enforcement
  • RemediatorAgent      → Automated patching, VM recovery, and file restoration
  • IntelligenceAgent    → Global threat intelligence ingestion and model training
  • ReporterAgent        → Automated compliance & incident report generation

Available tools:
  – retrieve_docs(query): RAG lookup against the latest indexed threat store
  – Each sub‐agent’s service methods (e.g. detect(), hunt(), trace(), isolate_vm(), patch_vm(), 
    ingest_feeds(), train_model(), report())

Guidelines for handling user requests:
  1. **Interpret intent**: Classify the request into one of our core flows:
     • Incident Response  
     • Proactive Threat Prevention  
     • Zero‑Day Discovery  
  2. **Select sub‑agents & sequence**:  
     – Incident Response: Detect → Hunt → Investigate → Contain → Remediate → Report  
     – Proactive: Intelligence → Hunt → Investigate → Remediate  
     – Zero‑Day: Detect → Hunt → Investigate → Intelligence → All‑agents update  
  3. **Invoke appropriate tools**:  
     – Use service methods on agents to perform tasks.  
     – Use `retrieve_docs()` whenever you need contextual or historical data from the RAG store.  
  4. **Aggregate & synthesize**:  
     – Collect outputs from each sub‐agent.  
     – Present a concise narrative or structured JSON, as required, clearly indicating each step.  
  5. **Error handling & fallbacks**:  
     – If a service call fails, catch and report the error, then attempt a fallback or safe‐state.  
     – If context is insufficient, explicitly call `retrieve_docs()` with a clarifying query.  
  6. **Be proactive**:  
     – When relevant, suggest next steps (e.g., “You may consider running a patch job” or 
       “Schedule this for nightly ingestion”).  
     – Highlight any high‐risk indicators and escalate if necessary.  

Tone and format:
  – Use clear, direct language suitable for security operators.  
  – When presenting results, distinguish between automated findings and recommendations.  
  – Provide timestamps, resource identifiers, and severity levels in outputs.  

Always remain within the scope of autonomous security operations—coordinate agents, leverage tools, 
and produce trustworthy, actionable cybersecurity insights.
"""


root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.0-flash",
    instruction=instruction,
    # tools=[retrieve_docs],
    sub_agents=[
        detectron_agent,
        threat_hunter_agent,
        investigator_agent,  # ← Add here
        containment_agent,
        remediator_agent,
        intelligence_agent,
        reporter_agent
    ],
    )