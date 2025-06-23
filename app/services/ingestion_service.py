# app/services/ingestion_service.py
import os
import sys
import subprocess
from app.utils.config import PlatformConfig

class IngestionService:
    def __init__(self, config: PlatformConfig):
        self.config = config

    def submit_pipeline(self, cron_schedule=None, pipeline_name="cyber_intel_ingest") -> str:
        """
        Submits or schedules the Kubeflow pipeline that feeds RAG datastore.
        """

        cmd = [
            sys.executable,  # ✅ uses the current venv Python
            os.path.join("data_ingestion", "data_ingestion_pipeline", "submit_pipeline.py"),
            "--project-id", self.config.project_id,
            "--region", self.config.location,
            "--data-store-region", os.getenv("DATA_STORE_REGION", "us"),
            "--data-store-id", os.getenv("DATA_STORE_ID", "cyberguard-threat-ingestion_1750289908683"),
            "--service-account", os.getenv("SERVICE_ACCOUNT", "cyberguard-sa@crucial-strata-419415.iam.gserviceaccount.com"),
            "--pipeline-root", os.getenv("PIPELINE_ROOT", "gs://cyberguard-pipeline-root"),
            "--pipeline-name", "cyber_intel_ingest",
        ]

        if cron_schedule:
            cmd += ["--cron-schedule", cron_schedule, "--schedule-only", "true"]
            cmd += ["--pipeline-name", pipeline_name]

        print("🚀 Running:", " ".join(cmd))
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": "."})
        return "✅ Ingestion pipeline submitted"
