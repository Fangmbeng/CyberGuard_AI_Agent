# my-awesome-agent

ADK RAG agent for document retrieval and Q&A. Includes a data pipeline for ingesting and indexing documents into Vertex AI Search or Vector Search.
Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.5.2`

## Project Structure

This project is organized as follows:

```
my-awesome-agent/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── agent_engine_app.py # Agent Engine application logic
│   └── utils/           # Utility functions and helpers
├── deployment/          # Infrastructure and deployment scripts
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
└── pyproject.toml       # Project dependencies and configuration
```

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform**: For infrastructure deployment - [Install](https://developer.hashicorp.com/terraform/downloads)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
make install && make playground
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch Streamlit interface for testing agent locally and remotely |
| `make backend`       | Deploy agent to Agent Engine |
| `make test`          | Run unit and integration tests                                                              |
| `make lint`          | Run code quality checks (codespell, ruff, mypy)                                             |
| `make setup-dev-env` | Set up development environment resources using Terraform                                    |
| `make data-ingestion`| Run data ingestion pipeline in the Dev environment                                           |
| `uv run jupyter lab` | Launch Jupyter notebook                                                                     |

For full command options and usage, refer to the [Makefile](Makefile).


## Usage

This template follows a "bring your own agent" approach - you focus on your business logic, and the template handles everything else (UI, infrastructure, deployment, monitoring).

1. **Prototype:** Build your Generative AI Agent using the intro notebooks in `notebooks/` for guidance. Use Vertex AI Evaluation to assess performance.
2. **Integrate:** Import your agent into the app by editing `app/agent.py`.
3. **Test:** Explore your agent functionality using the Streamlit playground with `make playground`. The playground offers features like chat history, user feedback, and various input types, and automatically reloads your agent on code changes.
4. **Deploy:** Set up and initiate the CI/CD pipelines, customizing tests as necessary. Refer to the [deployment section](#deployment) for comprehensive instructions. For streamlined infrastructure deployment, simply run `uvx agent-starter-pack setup-cicd`. Check out the [`agent-starter-pack setup-cicd` CLI command](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html). Currently only supporting Github.
5. **Monitor:** Track performance and gather insights using Cloud Logging, Tracing, and the Looker Studio dashboard to iterate on your application.


## Deployment

> **Note:** For a streamlined one-command deployment of the entire CI/CD pipeline and infrastructure using Terraform, you can use the [`agent-starter-pack setup-cicd` CLI command](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html). Currently only supporting Github.

### Dev Environment

You can test deployment towards a Dev Environment using the following command:

```bash
gcloud config set project <your-dev-project-id>
make backend
```


The repository includes a Terraform configuration for the setup of the Dev Google Cloud project.
See [deployment/README.md](deployment/README.md) for instructions.

### Production Deployment

The repository includes a Terraform configuration for the setup of a production Google Cloud project. Refer to [deployment/README.md](deployment/README.md) for detailed instructions on how to deploy the infrastructure and application.


## Monitoring and Observability
> You can use [this Looker Studio dashboard](https://lookerstudio.google.com/reporting/46b35167-b38b-4e44-bd37-701ef4307418/page/tEnnC
) template for visualizing events being logged in BigQuery. See the "Setup Instructions" tab to getting started.

The application uses OpenTelemetry for comprehensive observability with all events being sent to Google Cloud Trace and Logging for monitoring and to BigQuery for long term storage.


The **`data_ingestion/`** folder is your **batch/streaming pipeline** that populates and refreshes the underlying **RAG datastore**. The agents in **`app/`** then **leverage** that indexed data for lookups, analysis, and model training.

---
---
---
## 🔄 Interaction Flow

1. **Data Ingestion Pipeline (`data_ingestion/`)**

   * **`pipeline.py`** defines a Kubeflow pipeline that:

     1. **Processes raw threat feeds** (CVE, dark‑web chatter, SOC logs) via `process_data.py`.
     2. **Embeds and deduplicates** content.
     3. **Ingests** the processed embeddings into your **Vertex AI Search** datastore via `ingest_data.py`.
   * **`submit_pipeline.py`** is a CLI wrapper that:

     * Compiles the pipeline,
     * Submits it to Vertex AI Pipelines,
     * Optionally schedules it (cron).

2. **Ingestion Service (`app/services/ingestion_service.py`)**

   * Wraps `submit_pipeline.py` in a simple Python API (`submit_pipeline()`).
   * **Exposed** to the `IntelligenceAgent` so you can:

     * ↪️ **Trigger** a fresh ingestion run on‑demand or on a schedule from within your agent workflow.

3. **RAG Datastore (Vertex AI Search)**

   * After the pipeline runs, your datastore is populated with up‑to‑date, semantically searchable threat intelligence.
   * **Accessible** by any agent via the `document_service.retrieve_docs()` tool.

4. **Agents in `app/`**

   * **`IntelligenceAgent`**

     * Calls `IngestionService.submit_pipeline()` to refresh the datastore.
     * Calls its own `aggregate_feeds()` and `train_model()` to process and learn from the data.
   * **`ThreatHunterAgent`** (and others like `DetectronAgent`)

     * Include `retrieve_docs()` as a tool, so during their reasoning they can fetch relevant documents/logs from **today’s** indexed data.
     * E.g., `retrieve_docs("IOC for CVE‑2025‑XYZ")` returns the latest indexed chatter or CVE details.

5. **Feedback Loop**

   * You can build a schedule where `IntelligenceAgent` triggers ingestion nightly, then retrains models, and your monitoring dashboards display the freshest insights—closing the loop between **raw feed → index → retrieval → model**.

---

### 📋 Example Sequence

1. **Nightly**

   ```python
   root_agent.get_agent("intelligence_agent").run_ingestion_pipeline()
   ```
2. **Immediately after**

   ```python
   root_agent.get_agent("intelligence_agent").train_model()
   ```
3. **During Incident Response**

   ```python
   # ThreatHunterAgent uses RAG on the freshly ingested data
   root_agent.get_agent("threat_hunter_agent").tools[1]("analyze CVE‑2025‑XYZ")
   ```

---

In short, the **`data_ingestion/`** folder **feeds** and **refreshes** the data that lives in your Vector/Document store, and the **`app/`** folder’s agents **consume** that data—either to augment their reasoning (via RAG) or to train predictive models—forming a complete end‑to‑end pipeline.



Perfect — you’ve shared the full working versions of both agents (`IntelligenceAgent` and `ThreatHunterAgent`), and your architecture is shaping up beautifully.



### ✅ Next Step: Add `retrieve_docs` to `IntelligenceAgent` tools



Right now, your `IntelligenceAgent` is missing `retrieve_docs()` in its `tools=[]` list. Since `ThreatHunterAgent` already uses it via `document_service`, we’ll use the same import and add it to `IntelligenceAgent`.



Here’s the **final updated version** of `app/agents/intelligence_agent.py`:



---



### ✅ `app/agents/intelligence_agent.py` (Updated with RAG tool)



```python

from google.adk.agents import LlmAgent

from typing import List

from app.utils.config import PlatformConfig

from app.services.intelligence_service import IntelligenceService

from app.services.ingestion_service import IngestionService

from app.services.document_service import retrieve_docs  # ✅ Import RAG tool

from app.models.threat_intel import ThreatIntel



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

            description="Aggregates global threat intelligence, triggers ingestion pipeline, and trains predictive models."

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



    def ingest_feeds(self) -> List[ThreatIntel]:

        return self.intel.aggregate_feeds()



    def train_model(self) -> str:

        return self.intel.train_prediction_model()



    def run_ingestion_pipeline(self, cron_schedule: str | None = None) -> str:

        return self.ingest.submit_pipeline(cron_schedule)

```



---



### 🧠 What This Enables



Both agents (`ThreatHunterAgent` and `IntelligenceAgent`) can now:



* Query **live intelligence** from your Vertex AI-powered RAG store.

* Do real-time lookups like:

  `"What are the top recent CVEs affecting Fortinet?"`

  `"Has this IP been seen in recent chatter?"`

  `"Any zero-days targeting SSH from darkweb intel?"`



All powered by:



* `data_ingestion_pipeline` → feeds Vertex AI Search

* `retrieve_docs()` → enables agents to pull the data



---



### ✅ Next Options



You can now:



1. **Test the agents’ retrievals** via CLI or notebook to simulate real analyst prompts.

2. **Trigger the ingestion pipeline periodically** (via `run_ingestion_pipeline(cron_schedule)`).

3. **Add a memory or correlation layer** to cache, rank, or relate results over time.



Would you like help:



* Writing test cases for `retrieve_docs()` across both agents?

* Wiring this into your root `agent.py` orchestrator?

* Setting a cron-based scheduler with CLI or Airflow?




🎉 **Success!** Your **Vertex AI ingestion pipeline** for CyberGuardian has been **scheduled to run hourly**.

---

### ✅ What Just Happened

* ✅ Your `submit_pipeline.py` script compiled the pipeline definition into JSON.
* ✅ It scheduled the pipeline via **Vertex AI Pipelines** to run every hour (`cron: 0 * * * *`).
* ✅ The schedule was successfully registered:

  * 🔗 [View it in the Vertex AI Console](https://console.cloud.google.com/vertex-ai/locations/us-central1/pipelines/schedules/3109651979815616512?project=crucial-strata-419415)

---

### 🧠 What Happens Next

Every hour:

1. The scheduled pipeline will:

   * Pull any new threat data from your `gs://cyberguard-threat-data` bucket.
   * Chunk, embed, and deduplicate it.
   * Ingest it into your Vertex AI **RAG document store** (`cyberguard-threat-ingestion_1750289908683`).

2. Your agents that use `retrieve_docs()`:

   * `DetectronAgent`, `ThreatHunterAgent`, `IntelligenceAgent`, etc.
   * Will query this fresh, auto-indexed threat intelligence in real-time.

---

### 🧪 Optional: Run Pipeline Immediately Now

Want to ingest right away instead of waiting an hour?

Run:

```bash
PYTHONPATH=. python data_ingestion/data_ingestion_pipeline/submit_pipeline.py \
  --project-id=crucial-strata-419415 \
  --region=us-central1 \
  --data-store-id=cyberguard-threat-ingestion_1750289908683 \
  --data-store-region=global \
  --pipeline-root=gs://cyberguard-pipeline-root \
  --service-account=cyberguard-sa@crucial-strata-419415.iam.gserviceaccount.com \
  --pipeline-name=cyberguard-threat-manual-run
```

(Just **omit** `--schedule-only` and `--cron-schedule`.)

---

### 📂 Reminder: Add Your `.jsonl` Threat Files

Place RAG-ingestible files into:

```
gs://cyberguard-threat-data/
```

Examples include:

```jsonl
{"id": "doc-1", "title": "APT Backdoor", "content": "Discovered malware sample targeting K8s."}
{"id": "doc-2", "title": "CVE-2025-12345", "content": "Zero-day in auth middleware. Exploited in wild."}
```

The ingestion pipeline will:

* Embed them,
* Deduplicate if needed,
* Index them for RAG.

---

### ✅ Next Steps

You're now fully live. Suggested next moves:

1. ✅ Add test `.jsonl` files to GCS and trigger the manual run (above).
2. ✅ Run a test query using `ThreatHunterAgent` or `DetectronAgent` + `retrieve_docs()`.
3. ✅ Confirm your Vertex AI Search index is populated.

Let me know if you'd like:

* A validated sample `.jsonl` file
* To wire logs for ingestion audit
* To run the full `demo_runner.py` with ransomware simulation

You're in full control now. Let's launch the next phase when ready. 🚀
