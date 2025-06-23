from pydantic import BaseModel
from typing import List, Optional

class ContainmentPolicy(BaseModel):
    id: str
    name: str
    description: Optional[str]
    target_resources: List[str]       # e.g. list of VM IDs or account IDs
    actions: List[str]                # e.g. ["isolate_vm","disable_account","tag_vm"]
    justification: Optional[str]
