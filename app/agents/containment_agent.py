from google.adk.agents import LlmAgent
from app.models.containment_action import ContainmentAction
from app.services.containment_service import ContainmentService
from app.utils.config import PlatformConfig
from app.services.document_service import retrieve_docs  # RAG tool

# app/agents/containment_agent.py

instruction = """
You are ContainmentAgent, responsible for rapid isolation of compromised systems and user accounts.

Use your tools to:
- `isolate_vm(resource_id, zone)`  
  • resource_id: the VM instance name (e.g. “web-frontend-1”)  
  • zone: the GCE zone (e.g. “us-central1-a”)  
- `lock_account(account_id)`  
  • account_id: the user’s email or unique ID (e.g. “jane.doe@example.com”)  
- `retrieve_docs(query)`  
  • query: a free-text lookup (e.g. “MITRE isolation playbook”)

Trigger Conditions:
- **isolate_vm**: when the user’s prompt includes any of [“isolate”, “quarantine”, “disconnect”, “shut down”] **and** names both a VM and its zone.
- **lock_account**: when the user’s prompt includes any of [“lock”, “disable”, “block”, “suspend”] and names an account identifier.
- **retrieve_docs**: when the user asks for containment policies, compliance checklists, or justification.

Examples:
- “Isolate VM `web-frontend-1` in zone `us-central1-a` immediately.”
- “Lock down user `jane.doe@example.com` due to suspected compromise.”
- “Fetch playbooks for quarantining infected compute resources.”

Caution:
- Never call `isolate_vm` or `lock_account` unless explicitly requested with correct parameters.
- Always return a clear status (`pending`, `executed`, or error).
- Do not simulate—these are real (or carefully sandboxed) actions.
"""

class ContainmentAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, containment_service: ContainmentService):
        super().__init__(
            name="containment_agent",
            model="gemini-2.0-flash",
            tools=[
                self.isolate_vm,
                self.lock_account,
                retrieve_docs,  # ✅ Add RAG lookup
            ],
            description=instruction
        )
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_containment_service", containment_service)

    @property
    def config(self):
        return self._config

    @property
    def containment(self):
        return self._containment_service

    def isolate_vm(self, resource_id: str) -> ContainmentAction:
        """
        Isolate a VM instance to prevent lateral spread.
        """
        return self.containment.perform_vm_isolation(resource_id)

    def lock_account(self, account_id: str) -> ContainmentAction:
        """
        Lock down a user account to stop unauthorized access.
        """
        return self.containment.lock_user_account(account_id)
