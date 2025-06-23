import logging
from google.cloud import compute_v1, osconfig_v1
from app.models.remediation_action import RemediationAction

logger = logging.getLogger(__name__)

def isolate_vm(instance_name: str, zone: str, project_id: str) -> RemediationAction:
    """Stops a VM instance as part of containment/remediation."""
    try:
        instances_client = compute_v1.InstancesClient()
        operation = instances_client.stop(project=project_id, zone=zone, instance=instance_name)
        logger.info(f"Stopping VM {instance_name} in zone {zone}: {operation.name}")
        return RemediationAction(
            action="isolate_vm",
            resource=instance_name,
            status="executed",
            message="VM stopped successfully."
        )
    except Exception as e:
        logger.error(f"Failed to isolate VM: {e}")
        return RemediationAction(
            action="isolate_vm",
            resource=instance_name,
            status="failed",
            message=str(e)
        )

def patch_vm(instance_id: str, patch_job_name: str, project_id: str) -> RemediationAction:
    """Triggers a patch job using OS Config."""
    try:
        patch_client = osconfig_v1.OsConfigServiceClient()
        parent = f"projects/{project_id}"
        patch_job = osconfig_v1.PatchJob(
            display_name=patch_job_name,
            instance_filter=osconfig_v1.PatchInstanceFilter(
                instance_name_prefixes=[instance_id]
            ),
            description="Auto-triggered patch job from RemediatorAgent",
            duration={"seconds": 600}
        )
        response = patch_client.execute_patch_job(parent=parent, patch_job=patch_job)
        logger.info(f"Patch job triggered: {response.name}")
        return RemediationAction(
            action="patch_vm",
            resource=instance_id,
            status="executed",
            message=f"Patch job {response.name} triggered."
        )
    except Exception as e:
        logger.error(f"Failed to patch VM: {e}")
        return RemediationAction(
            action="patch_vm",
            resource=instance_id,
            status="failed",
            message=str(e)
        )

def recover_file_from_backup(file_path: str, backup_location: str) -> RemediationAction:
    """Simulates restoring a file from a known secure backup."""
    try:
        # TODO: Integrate with Cloud Storage / Filestore or backup system
        logger.info(f"Restoring {file_path} from {backup_location}")
        return RemediationAction(
            action="recover_file",
            resource=file_path,
            status="executed",
            message=f"File recovered from {backup_location}"
        )
    except Exception as e:
        logger.error(f"Failed to recover file: {e}")
        return RemediationAction(
            action="recover_file",
            resource=file_path,
            status="failed",
            message=str(e)
        )
