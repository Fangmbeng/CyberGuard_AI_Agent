from app.services.containment_service import ContainmentService
from app.models.containment_policy import ContainmentPolicy

def test_apply_policy():
    svc = ContainmentService()
    policy = ContainmentPolicy(
        id="pol-123",
        name="IsolateAll",
        description="Test isolation",
        target_resources=["vm-1","vm-2"],
        actions=["isolate_vm","tag_vm"],
        justification="Test run"
    )
    results = svc.apply_policy(policy)
    assert len(results) == 4
    assert all(r.action_type in ["isolate_vm","tag_vm"] for r in results)
