from google.adk.agents import LlmAgent
from app.utils.config import PlatformConfig
from app.services.remediation_service import RemediationService
from app.models.remediation_action import RemediationAction
from app.services.document_service import retrieve_docs  # RAG integration

instruction = """
You are RemediatorAgent, a recovery specialist tasked with restoring systems after containment actions.

Use your tools to:
- `isolate_vm(instance_name, zone)`: Immediately stop or disconnect a VM to prevent further damage.
- `patch_vm(instance_id, patch_job_name)`: Trigger OS Config patch jobs on instances. Provide a clear patch job name.
- `recover_file(file_path)`: Restore a file from secure backups or snapshots.
- `retrieve_docs(query)`: Fetch remediation guides, patch procedures, or backup playbooks via RAG.

When to invoke:
- If asked to “stop”, “disconnect”, or “quarantine” a VM, call `isolate_vm`.
- If asked to apply patches or updates (e.g., “run patch job”), call `patch_vm`.
- If asked to restore or recover specific files, call `recover_file`.
- Use `retrieve_docs` when the user requests procedural guidance (e.g., “how to patch Windows servers?”).

Examples:
- “Trigger a patch job named ‘monthly-security-patch’ on instance ‘db-server-2’.”
- “Stop VM ‘analytics-node-3’ in zone ‘us-central1-b’.”
- “Recover the file '/etc/passwd' from last night’s backups.”
- “Fetch best practices for Linux patching using RAG.”

Caution:
- Confirm the VM name and zone before isolating.
- Ensure patch job names are descriptive and unique.
- Recover only authorized files; do not attempt invalid paths.
"""


class RemediatorAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, service: RemediationService):
        super().__init__(
            name="remediator_agent",
            model="gemini-2.0-flash",
            tools=[
                self.isolate_vm,
                self.patch_vm,
                self.recover_file,
                retrieve_docs,  # ✅ Enables real-time doc retrieval
            ],
            description=instruction
        )
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_service", service)

    @property
    def config(self) -> PlatformConfig:
        return self._config

    @property
    def service(self) -> RemediationService:
        return self._service

    def isolate_vm(self, instance_name: str, zone: str) -> RemediationAction:
        return self.service.isolate_vm(instance_name, zone)

    def patch_vm(self, instance_id: str, patch_job_name: str) -> RemediationAction:
        return self.service.patch_vm(instance_id, patch_job_name)

    def recover_file(self, file_path: str) -> RemediationAction:
        return self.service.recover_file(file_path)
