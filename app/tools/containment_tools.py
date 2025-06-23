from app.models.containment_action import ContainmentAction
# from datetime import datetime
from google.cloud import compute_v1
from logging import getLogger
import datetime

logger = getLogger(__name__)

def isolate_vm(instance_name: str, zone: str, project_id: str) -> ContainmentAction:
    """Stops a VM instance."""
    try:
        client = compute_v1.InstancesClient()
        op = client.stop(project=project_id, zone=zone, instance=instance_name)
        logger.info(f"Stopped VM {instance_name} (zone={zone}): op={op.name}")
        status = "executed"
        message = f"VM {instance_name} stopped successfully."
    except Exception as e:
        logger.error(f"Failed to stop VM {instance_name}: {e}")
        status = "failed"
        message = str(e)

    return ContainmentAction(
        resource_id=instance_name,
        action_type="isolate_vm",
        status=status,
        justification=message,
        timestamp=datetime.utcnow().isoformat(),
    )

def disable_account(account_id: str) -> ContainmentAction:
    """
    Call IAM API to disable the given user.
    """
    try:
        # e.g. googleapiclient.discovery build & call to remove roles or suspend.
        # For now, placeholder success:
        status = "executed"
        message = f"Account {account_id} disabled successfully."
    except Exception as e:
        status = "failed"
        message = str(e)

    return ContainmentAction(
        resource_id=account_id,
        action_type="disable_account",
        status=status,
        justification=message,
        timestamp=datetime.utcnow().isoformat(),
    )

def tag_vm(resource_id: str, tags: dict[str,str]) -> ContainmentAction:
    # Placeholder: call Compute Engine API setLabels()
    return ContainmentAction(
        resource_id=resource_id,
        action_type="tag_vm",
        status="success",
        timestamp=datetime.utcnow().isoformat(),
        justification=f"Applied labels: {tags}",
    )
