from app.tools.remediation_tools import isolate_vm, patch_vm, recover_file_from_backup
from app.models.remediation_action import RemediationAction
from app.utils.config import PlatformConfig

class RemediationService:
    def __init__(self, config: PlatformConfig):
        self.config = config

    def isolate_vm(self, instance_name: str, zone: str) -> RemediationAction:
        return isolate_vm(
            instance_name=instance_name,
            zone=zone,
            project_id=self.config.project_id,
        )

    def patch_vm(self, instance_id: str, patch_job_name: str) -> RemediationAction:
        return patch_vm(
            instance_id=instance_id,
            patch_job_name=patch_job_name,
            project_id=self.config.project_id,
        )

    def recover_file(self, file_path: str) -> RemediationAction:
        return recover_file_from_backup(
            file_path=file_path,
            backup_location=self.config.incident_bucket,
        )
