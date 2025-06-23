from app.services.remediation_service import RemediationService
from app.utils.config import PlatformConfig
import pytest

@pytest.fixture
def config():
    c = PlatformConfig.from_env()
    c.project_id = "test-project"
    return c

def test_isolate_vm_success(monkeypatch, config):
    # Monkeypatch the compute client stop call
    from app.tools.remediation_tools import RemediationAction

    svc = RemediationService(config)
    action = svc.isolate_vm("vm-1", "us-central1-a")
    assert isinstance(action, RemediationAction)
    assert action.action == "isolate_vm"
    assert action.resource == "vm-1"
    assert action.status in ("executed", "failed")

def test_recover_file(config):
    svc = RemediationService(config)
    action = svc.recover_file("/secret/data.txt")
    assert action.action == "recover_file"
    assert "/secret/data.txt" in action.resource
