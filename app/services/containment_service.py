from typing import List
from app.tools.containment_tools import isolate_vm, disable_account, tag_vm
from app.models.containment_action import ContainmentAction
from app.models.containment_policy import ContainmentPolicy
from app.utils.config import PlatformConfig

class ContainmentService:
    def __init__(self, config: PlatformConfig):
        self.project_id = config.project_id

    def perform_vm_isolation(self, instance_name: str, zone: str) -> ContainmentAction:
        return isolate_vm(
            instance_name=instance_name,
            zone=zone,
            project_id=self.project_id,
        )
    
    def lock_user_account(self, account_id: str) -> ContainmentAction:
        return disable_account(account_id)

    def tag_vm_for_audit(self, resource_id: str, tags: dict[str,str]) -> ContainmentAction:
        return tag_vm(resource_id, tags)

    def apply_policy(self, policy: ContainmentPolicy) -> List[ContainmentAction]:
        """
        Apply a set of containment actions based on the policy.
        """
        results: List[ContainmentAction] = []
        for res in policy.target_resources:
            for action in policy.actions:
                if action == "isolate_vm":
                    results.append(isolate_vm(res))
                elif action == "disable_account":
                    results.append(disable_account(res))
                elif action == "tag_vm":
                    # tag with policy id for audit
                    results.append(tag_vm(res, {"policy": policy.id}))
        return results
