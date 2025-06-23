from pydantic import BaseModel

class RemediationAction(BaseModel):
    action: str               # Action type: isolate_vm, patch_vm, recover_file
    resource: str             # Affected resource: VM ID, file path, etc.
    status: str               # executed / failed / pending
    message: str              # Human-readable summary of the result
