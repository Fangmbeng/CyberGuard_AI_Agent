from datetime import datetime
from typing import Any

def to_json_safe(obj: Any) -> Any:
    """
    Recursively convert:
      - datetime → ISO string
      - dict → {k: to_json_safe(v)}
      - list/tuple → [to_json_safe(v)]
      - everything else → itself
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    return obj