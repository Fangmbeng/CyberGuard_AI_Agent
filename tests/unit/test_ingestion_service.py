import os
from app.services.ingestion_service import IngestionService
from app.utils.config import PlatformConfig

def test_submit_pipeline_dry_run(tmp_path, monkeypatch):
    # Arrange
    config = PlatformConfig.from_env()
    config.project_id = "proj-123"
    config.location = "us-central1"
    svc = IngestionService(config)

    # Intercept subprocess.run
    called = {}
    def fake_run(cmd, check, env):
        called["cmd"] = cmd
        called["env"] = env
    monkeypatch.setattr("subprocess.run", fake_run)

    # Act
    result = svc.submit_pipeline(cron_schedule="0 5 * * *")

    # Assert
    assert "submit_pipeline.py" in called["cmd"][-2]
    assert "0" in called["cmd"]
    assert called["env"]["PYTHONPATH"] == "."
    assert "Ingestion pipeline submitted" in result
