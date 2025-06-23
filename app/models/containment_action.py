from pydantic import BaseModel
from typing import List, Optional

class ContainmentAction(BaseModel):
    resource_id: str
    action_type: str  # e.g., "isolate_vm", "disable_account"
    status: str = "pending"
    justification: Optional[str] = None
